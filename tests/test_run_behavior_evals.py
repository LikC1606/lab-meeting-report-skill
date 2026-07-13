from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from scripts.eval_contract import load_manifest
from scripts.run_behavior_evals import (
    RunSpec,
    build_prompt,
    hash_run_environment,
    run_with_retry,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = (
    REPO_ROOT
    / "evals"
    / "research-progress"
    / "cases"
    / "clean-multiseed"
)
CASE_MANIFEST = load_manifest(CASE_ROOT / "manifest.json")
SKILL_ROOT = REPO_ROOT / "lab-meeting-report"


def write_valid_report(context: object) -> None:
    report_path = context.sandbox / Path(context.manifest["expected_report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CASE_ROOT / "expected-valid-report.md", report_path)


def fake_success_executor(context: object) -> subprocess.CompletedProcess[str]:
    write_valid_report(context)
    return subprocess.CompletedProcess(
        context.command,
        0,
        stdout=(
            '{"type":"turn.completed","usage":'
            '{"input_tokens":10,"output_tokens":5}}\n'
        ),
        stderr="",
    )


def always_fails(context: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        context.command, 1, stdout="", stderr="synthetic failure"
    )


class FailsThenSucceeds:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, context: object) -> subprocess.CompletedProcess[str]:
        self.calls += 1
        if self.calls == 1:
            return always_fails(context)
        return fake_success_executor(context)


class RunBehaviorEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name) / "workspace"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def make_spec(self) -> RunSpec:
        return RunSpec(
            repo_root=REPO_ROOT,
            case_manifest=CASE_ROOT / "manifest.json",
            workspace=self.workspace,
            configuration="with_skill",
            run_number=1,
            model="gpt-5.6-sol",
            timeout_seconds=30,
            candidate_skill=SKILL_ROOT,
            eval_index=1,
        )

    def test_prompt_names_exact_skill_and_hides_manifest(self) -> None:
        prompt = build_prompt(
            CASE_MANIFEST, Path("skill-under-test/SKILL.md")
        )

        self.assertIn("skill-under-test/SKILL.md", prompt)
        self.assertIn("Do not read or search for manifest.json", prompt)
        self.assertNotIn("forbidden_patterns", prompt)

    def test_run_layout_is_skill_creator_compatible(self) -> None:
        result = run_with_retry(
            self.make_spec(), executor=fake_success_executor
        )

        self.assertEqual(result.infrastructure_status, "valid")
        self.assertTrue(result.hard_pass)
        self.assertTrue((result.run_dir / "outputs" / "report.md").is_file())
        self.assertTrue((result.run_dir / "grading.json").is_file())
        self.assertTrue((result.run_dir / "timing.json").is_file())
        self.assertTrue(
            (result.run_dir.parent.parent / "eval_metadata.json").is_file()
        )
        grading = json.loads(
            (result.run_dir / "grading.json").read_text(encoding="utf-8")
        )
        self.assertTrue(grading["hard_pass"])

    def test_infrastructure_failure_retries_once(self) -> None:
        executor = FailsThenSucceeds()

        result = run_with_retry(self.make_spec(), executor=executor)

        self.assertEqual(executor.calls, 2)
        self.assertEqual(result.infrastructure_status, "valid")
        metadata = json.loads(
            (result.run_dir / "run_metadata.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(metadata["attempts"], 2)

    def test_second_infrastructure_failure_is_invalid_not_quality_failure(
        self,
    ) -> None:
        result = run_with_retry(self.make_spec(), executor=always_fails)

        self.assertEqual(result.infrastructure_status, "invalid")
        self.assertIsNone(result.hard_pass)
        metadata = json.loads(
            (result.run_dir / "run_metadata.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(metadata["attempts"], 2)
        self.assertEqual(metadata["infrastructure_status"], "invalid")
        self.assertTrue(
            {
                "case_hash",
                "skill_hash",
                "prompt_hash",
                "runner_hash",
                "grader_hash",
                "model",
                "cli_version",
                "git_commit",
                "configuration",
                "run_number",
                "attempts",
                "exit_status",
                "infrastructure_status",
            }.issubset(metadata)
        )

    def test_environment_hashes_are_stable_and_content_sensitive(self) -> None:
        prompt = build_prompt(
            CASE_MANIFEST, Path("skill-under-test/SKILL.md")
        )
        first = hash_run_environment(
            case_root=CASE_ROOT,
            skill_root=SKILL_ROOT,
            prompt=prompt,
            runner_path=REPO_ROOT / "scripts" / "run_behavior_evals.py",
            grader_path=REPO_ROOT / "scripts" / "grade_report.py",
        )
        second = hash_run_environment(
            case_root=CASE_ROOT,
            skill_root=SKILL_ROOT,
            prompt=prompt,
            runner_path=REPO_ROOT / "scripts" / "run_behavior_evals.py",
            grader_path=REPO_ROOT / "scripts" / "grade_report.py",
        )

        self.assertEqual(first, second)
        changed = hash_run_environment(
            case_root=CASE_ROOT,
            skill_root=SKILL_ROOT,
            prompt=prompt + " changed",
            runner_path=REPO_ROOT / "scripts" / "run_behavior_evals.py",
            grader_path=REPO_ROOT / "scripts" / "grade_report.py",
        )
        self.assertNotEqual(first["prompt_hash"], changed["prompt_hash"])

    def test_invalid_skill_inventory_still_records_environment_hashes(
        self,
    ) -> None:
        invalid_skill = Path(self.temp_dir.name) / "invalid-skill"
        shutil.copytree(SKILL_ROOT, invalid_skill)
        (invalid_skill / "unexpected.txt").write_text(
            "Synthetic unexpected file", encoding="utf-8"
        )
        spec = replace(self.make_spec(), candidate_skill=invalid_skill)

        result = run_with_retry(spec, executor=fake_success_executor)

        self.assertEqual(result.infrastructure_status, "invalid")
        metadata = json.loads(
            (result.run_dir / "run_metadata.json").read_text(
                encoding="utf-8"
            )
        )
        for field in (
            "case_hash",
            "skill_hash",
            "prompt_hash",
            "runner_hash",
            "grader_hash",
        ):
            self.assertIn(field, metadata)


if __name__ == "__main__":
    unittest.main()
