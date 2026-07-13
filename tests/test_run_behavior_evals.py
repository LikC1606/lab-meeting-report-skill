from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from scripts.eval_contract import ContractError, load_manifest
from scripts.run_behavior_evals import (
    ExecutionContext,
    RunSpec,
    aggregate_workspace,
    apply_human_review,
    build_prompt,
    check_release_gate,
    execute_codex,
    hash_run_environment,
    load_network_provider,
    parse_review_feedback,
    prepare_blind_review,
    run_with_retry,
    write_benchmark_markdown,
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


class CapturingSuccessExecutor:
    def __init__(self) -> None:
        self.command: list[str] = []

    def __call__(self, context: object) -> subprocess.CompletedProcess[str]:
        self.command = list(context.command)
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

    def build_paired_workspace(self) -> None:
        for run_number in (1, 2):
            candidate = replace(self.make_spec(), run_number=run_number)
            baseline = replace(
                self.make_spec(),
                configuration="without_skill",
                run_number=run_number,
                candidate_skill=None,
                baseline_ref="v1.1.0",
            )
            run_with_retry(candidate, executor=fake_success_executor)
            run_with_retry(baseline, executor=fake_success_executor)

    def test_prompt_names_exact_skill_and_hides_manifest(self) -> None:
        prompt = build_prompt(
            CASE_MANIFEST, Path("skill-under-test/SKILL.md")
        )

        self.assertIn("skill-under-test/SKILL.md", prompt)
        self.assertIn("Do not read or search for manifest.json", prompt)
        self.assertNotIn("forbidden_patterns", prompt)

    def test_command_allows_an_isolated_non_git_sandbox(self) -> None:
        executor = CapturingSuccessExecutor()

        result = run_with_retry(self.make_spec(), executor=executor)

        self.assertEqual(result.infrastructure_status, "valid")
        self.assertIn("--skip-git-repo-check", executor.command)

    def test_real_executor_closes_inherited_stdin(self) -> None:
        context = ExecutionContext(
            command=["codex", "exec", "synthetic"],
            sandbox=Path(self.temp_dir.name),
            last_message=Path(self.temp_dir.name) / "last-message.txt",
            case_root=CASE_ROOT,
            manifest=CASE_MANIFEST,
            timeout_seconds=30,
        )
        completed = subprocess.CompletedProcess(
            context.command, 0, stdout="", stderr=""
        )

        with patch(
            "scripts.run_behavior_evals.subprocess.run",
            return_value=completed,
        ) as run:
            execute_codex(context)

        self.assertIs(run.call_args.kwargs["stdin"], subprocess.DEVNULL)

    def test_provider_config_is_replayed_under_ignore_user_config(self) -> None:
        config = Path(self.temp_dir.name) / "config.toml"
        config.write_text(
            """
model_provider = "test_provider"

[model_providers.test_provider]
name = "Synthetic provider"
base_url = "https://example.invalid/v1"
wire_api = "responses"
requires_openai_auth = true

[windows]
sandbox = "elevated"

[projects.'ignored-project']
trust_level = "trusted"
""".strip(),
            encoding="utf-8",
        )
        provider = load_network_provider(config)
        executor = CapturingSuccessExecutor()
        spec = replace(self.make_spec(), network_provider=provider)

        result = run_with_retry(spec, executor=executor)

        self.assertEqual(result.infrastructure_status, "valid")
        self.assertIn("--ignore-user-config", executor.command)
        command = " ".join(executor.command)
        self.assertIn("model_provider", command)
        self.assertIn("example.invalid", command)
        self.assertIn('windows.sandbox="elevated"', command)
        self.assertNotIn("ignored-project", command)
        metadata = json.loads(
            (result.run_dir / "run_metadata.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertRegex(metadata["provider_hash"], r"^[0-9a-f]{64}$")

    def test_provider_config_rejects_unsafe_extra_fields(self) -> None:
        config = Path(self.temp_dir.name) / "config.toml"
        config.write_text(
            """
model_provider = "unsafe"

[model_providers.unsafe]
name = "Unsafe"
base_url = "https://example.invalid/v1"
wire_api = "responses"
requires_openai_auth = true
http_headers = { Authorization = "must-not-load" }
""".strip(),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ContractError, "unsupported fields"):
            load_network_provider(config)

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
        first_attempt = result.run_dir / "attempts" / "attempt-1"
        second_attempt = result.run_dir / "attempts" / "attempt-2"
        self.assertIn(
            "synthetic failure",
            (first_attempt / "stderr.txt").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "turn.completed",
            (second_attempt / "stdout.jsonl").read_text(encoding="utf-8"),
        )

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

    def test_benchmark_uses_exact_skill_creator_fields(self) -> None:
        self.build_paired_workspace()

        benchmark = aggregate_workspace(
            self.workspace, model="gpt-5.6-sol"
        )

        run = benchmark["runs"][0]
        self.assertEqual(
            set(run),
            {
                "eval_id",
                "eval_name",
                "configuration",
                "run_number",
                "result",
                "expectations",
                "notes",
            },
        )
        self.assertIn("pass_rate", run["result"])
        self.assertEqual(benchmark["metadata"]["runs_per_configuration"], 2)
        self.assertEqual(
            set(benchmark["run_summary"]),
            {"with_skill", "without_skill", "delta"},
        )

    def test_benchmark_records_explicit_semantic_analyzer(self) -> None:
        self.build_paired_workspace()

        benchmark = aggregate_workspace(
            self.workspace,
            model="gpt-5.6-sol",
            analyzer_model="codex-inline-self-review",
        )

        self.assertEqual(
            benchmark["metadata"]["analyzer_model"],
            "codex-inline-self-review",
        )
        output = Path(self.temp_dir.name) / "benchmark.md"
        write_benchmark_markdown(benchmark, output)
        self.assertIn(
            "Analyzer: `codex-inline-self-review`",
            output.read_text(encoding="utf-8"),
        )

    def test_blind_review_contains_one_pair_per_case_run(self) -> None:
        self.build_paired_workspace()
        review_workspace = Path(self.temp_dir.name) / "review"

        mapping = prepare_blind_review(
            self.workspace, review_workspace, seed=1200
        )

        self.assertEqual(len(mapping["pairs"]), 2)
        pair = (
            review_workspace
            / "eval-01-clean-multiseed"
            / "pair-1"
            / "outputs"
        )
        self.assertTrue((pair / "source-packet.md").is_file())
        self.assertTrue((pair / "A-report.md").is_file())
        self.assertTrue((pair / "B-report.md").is_file())
        self.assertNotEqual(
            mapping["pairs"][0]["A"], mapping["pairs"][0]["B"]
        )
        anonymous = json.loads(
            (review_workspace / "benchmark.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            {run["configuration"] for run in anonymous["runs"]}, {"A", "B"}
        )
        self.assertNotIn("skill_hash", json.dumps(anonymous))

    def test_structured_feedback_requires_scores_and_preference(self) -> None:
        self.build_paired_workspace()
        review_workspace = Path(self.temp_dir.name) / "review"
        mapping = prepare_blind_review(
            self.workspace, review_workspace, seed=1200
        )
        reviews = []
        for pair in mapping["pairs"]:
            reviews.append(
                {
                    "run_id": pair["review_run_id"],
                    "feedback": json.dumps(
                        {
                            "semantic_failure": "none",
                            "A": {
                                "evidence_clarity": 4,
                                "information_selection": 4,
                                "decision_usefulness": 4,
                                "readability": 4,
                            },
                            "B": {
                                "evidence_clarity": 3,
                                "information_selection": 3,
                                "decision_usefulness": 3,
                                "readability": 3,
                            },
                            "preference": "A",
                            "notes": "Synthetic review",
                        }
                    ),
                }
            )

        summary = parse_review_feedback(
            {"reviews": reviews, "status": "complete"}, mapping
        )

        self.assertEqual(summary["pairs_reviewed"], 2)
        self.assertIn(
            summary["preference_counts"]["candidate"], {0, 1, 2}
        )

    def test_structured_feedback_rejects_out_of_range_scores(self) -> None:
        mapping = {
            "pairs": [
                {
                    "review_run_id": "eval-01-pair-1",
                    "eval_id": 1,
                    "eval_name": "clean-multiseed",
                    "run_number": 1,
                    "A": "with_skill",
                    "B": "without_skill",
                }
            ]
        }
        feedback = {
            "status": "complete",
            "reviews": [
                {
                    "run_id": "eval-01-pair-1",
                    "feedback": json.dumps(
                        {
                            "semantic_failure": "none",
                            "A": {
                                "evidence_clarity": 6,
                                "information_selection": 4,
                                "decision_usefulness": 4,
                                "readability": 4,
                            },
                            "B": {
                                "evidence_clarity": 3,
                                "information_selection": 3,
                                "decision_usefulness": 3,
                                "readability": 3,
                            },
                            "preference": "A",
                            "notes": "",
                        }
                    ),
                }
            ]
        }

        with self.assertRaisesRegex(ContractError, "between 1 and 5"):
            parse_review_feedback(feedback, mapping)

    def test_structured_feedback_requires_complete_submission(self) -> None:
        mapping = {"pairs": []}

        with self.assertRaisesRegex(ContractError, "status must be complete"):
            parse_review_feedback(
                {"reviews": [], "status": "in_progress"}, mapping
            )

    def test_semantic_failure_is_written_back_to_reviewed_benchmark(
        self,
    ) -> None:
        benchmark = make_release_benchmark()
        human_review = make_passing_human_review()
        human_review["semantic_failures"]["candidate"] = [
            {"eval_id": 1, "eval_name": "case-1", "run_number": 1}
        ]

        reviewed = apply_human_review(benchmark, human_review)

        candidate = next(
            run
            for run in reviewed["runs"]
            if run["configuration"] == "with_skill"
            and run["eval_id"] == 1
            and run["run_number"] == 1
        )
        self.assertEqual(candidate["result"]["pass_rate"], 0.0)
        self.assertEqual(
            candidate["result"]["failed"], candidate["result"]["total"]
        )

    def test_release_gate_requires_all_approved_conditions(self) -> None:
        passing_benchmark = make_release_benchmark()
        passing_human_review = make_passing_human_review()

        self.assertEqual(
            check_release_gate(passing_benchmark, passing_human_review), []
        )
        failing_benchmark = make_release_benchmark(candidate_failure=True)
        errors = check_release_gate(
            failing_benchmark, passing_human_review
        )
        self.assertIn(
            "candidate hard gates: expected 24/24", "\n".join(errors)
        )
        incomplete_review = make_passing_human_review()
        incomplete_review["pairs_reviewed"] = 23
        errors = check_release_gate(passing_benchmark, incomplete_review)
        self.assertIn("human review: expected 24/24", "\n".join(errors))

    def test_release_gate_accepts_complete_inline_semantic_review(self) -> None:
        benchmark = make_release_benchmark()
        semantic_review = make_passing_semantic_review()

        self.assertEqual(
            check_release_gate(
                benchmark, semantic_review, review_kind="semantic"
            ),
            [],
        )

        semantic_review["reports"][0]["unsupported_critical_claim"] = True
        semantic_review["summary"]["unsupported_critical_claims"] = 1
        semantic_review["summary"]["semantic_gate_passed"] = False
        errors = check_release_gate(
            benchmark, semantic_review, review_kind="semantic"
        )
        self.assertIn(
            "candidate semantic failures: expected 0, got 1",
            "\n".join(errors),
        )


def make_release_benchmark(
    *, candidate_failure: bool = False
) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    for eval_id in range(1, 9):
        for run_number in range(1, 4):
            for configuration in ("with_skill", "without_skill"):
                passed = not (
                    configuration == "without_skill"
                    and eval_id == 1
                    and run_number == 1
                )
                if (
                    candidate_failure
                    and configuration == "with_skill"
                    and eval_id == 1
                    and run_number == 1
                ):
                    passed = False
                runs.append(
                    {
                        "eval_id": eval_id,
                        "eval_name": f"case-{eval_id}",
                        "configuration": configuration,
                        "run_number": run_number,
                        "result": {
                            "pass_rate": 1.0 if passed else 0.0,
                            "passed": 1 if passed else 0,
                            "failed": 0 if passed else 1,
                            "total": 1,
                            "time_seconds": 1.0,
                            "tokens": 10,
                            "tool_calls": 0,
                            "errors": 0,
                        },
                        "expectations": [],
                        "notes": [],
                    }
                )
    return {
        "metadata": {
            "skill_name": "lab-meeting-report",
            "executor_model": "gpt-5.6-sol",
            "analyzer_model": "human-blind-review",
            "evals_run": list(range(1, 9)),
            "runs_per_configuration": 3,
        },
        "runs": runs,
        "run_summary": {},
        "notes": [],
    }


def make_passing_human_review() -> dict[str, object]:
    return {
        "pairs_reviewed": 24,
        "preference_counts": {"candidate": 2, "baseline": 0, "tie": 22},
        "semantic_failures": {"candidate": [], "baseline": []},
        "global_medians": {
            "candidate": {"overall": 4.0},
            "baseline": {"overall": 3.5},
        },
        "per_case": {
            f"case-{eval_id}": {
                "candidate": {"overall": 4.0},
                "baseline": {"overall": 3.5},
                "preference_counts": {
                    "candidate": 2 if eval_id == 1 else 0,
                    "baseline": 0,
                    "tie": 1 if eval_id == 1 else 3,
                },
            }
            for eval_id in range(1, 9)
        },
        "reviews": [],
    }


def make_passing_semantic_review() -> dict[str, object]:
    reports = [
        {
            "case_id": f"case-{eval_id}",
            "run_id": f"with_skill/run-{run_number}",
            "deterministic_hard_pass": True,
            "unsupported_critical_claim": False,
            "finding": "No unsupported critical claim found.",
        }
        for eval_id in range(1, 9)
        for run_number in range(1, 4)
    ]
    return {
        "reviewer": {
            "kind": "codex-inline-self-review",
            "independent": False,
            "manual_user_review": False,
        },
        "reports": reports,
        "summary": {
            "reports_reviewed": 24,
            "deterministic_hard_passes": 24,
            "unsupported_critical_claims": 0,
            "semantic_gate_passed": True,
        },
    }


if __name__ == "__main__":
    unittest.main()
