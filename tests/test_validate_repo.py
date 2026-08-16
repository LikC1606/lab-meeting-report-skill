from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_repo.py"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def copy_fixture(destination: Path) -> None:
    shutil.copytree(
        REPO_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "tmp"),
    )


def write_candidate_selection(root: Path, selected_blocks: list[str]) -> None:
    path = root / "benchmarks" / "v1.1-v1.2" / "candidate-selection.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "baseline_commit": "76a800c3fdd843b2513ea7270086a05ff7f5c47e",
                "baseline_benchmark_sha256": "0" * 64,
                "selected_blocks": selected_blocks,
                "evidence": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class ValidateRepoTests(unittest.TestCase):
    def test_current_repository_is_valid(self) -> None:
        result = run_validator(REPO_ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Repository validation passed", result.stdout)

    def test_old_skill_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            old_name = "lab-meeting-report" + "-md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace("name: lab-meeting-report", f"name: {old_name}", 1),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("old skill name", (result.stdout + result.stderr).lower())

    def test_missing_skill_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            missing = (
                fixture
                / "lab-meeting-report"
                / "references"
                / "progress-report.md"
            )
            missing.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing skill file", (result.stdout + result.stderr).lower())

    def test_missing_meeting_lifecycle_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            lifecycle = (
                fixture
                / "lab-meeting-report"
                / "references"
                / "meeting-lifecycle.md"
            )
            lifecycle.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing skill file",
                (result.stdout + result.stderr).lower(),
            )

    def test_missing_optional_adapter_references_are_rejected(self) -> None:
        for filename in ("notion-integration.md", "presentation-export.md"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp_dir:
                fixture = Path(temp_dir) / "repo"
                copy_fixture(fixture)
                (fixture / "lab-meeting-report" / "references" / filename).unlink()

                result = run_validator(fixture)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "missing skill file",
                    (result.stdout + result.stderr).lower(),
                )

    def test_missing_community_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            (fixture / "SECURITY.md").unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing community file",
                (result.stdout + result.stderr).lower(),
            )

    def test_stale_preview_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            preview = fixture / "scripts" / "render_preview.py"
            content = preview.read_text(encoding="utf-8")
            preview.write_text(
                content.replace(
                    "The sources do not provide a priority rule.",
                    "Complete 75 manual reviews",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "stale generated claim",
                (result.stdout + result.stderr).lower(),
            )

    def test_missing_social_preview_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            preview = (
                fixture
                / "assets"
                / "lab-meeting-report-social-preview.png"
            )
            preview.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing preview png",
                (result.stdout + result.stderr).lower(),
            )

    def test_missing_example_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            source = (
                fixture
                / "examples"
                / "research-progress"
                / "results"
                / "baseline.csv"
            )
            source.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing example source",
                (result.stdout + result.stderr).lower(),
            )

    def test_invented_example_number_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            report = fixture / "examples" / "mixed" / "report.md"
            content = report.read_text(encoding="utf-8")
            report.write_text(
                content + "\nInvented acceptance threshold: 0.59.\n",
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "unexpected numeric values",
                (result.stdout + result.stderr).lower(),
            )

    def test_missing_eval_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            manifest = (
                fixture
                / "evals"
                / "research-progress"
                / "cases"
                / "clean-multiseed"
                / "manifest.json"
            )
            manifest.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing evaluation manifest",
                (result.stdout + result.stderr).lower(),
            )

    def test_missing_safe_update_source_fixture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            existing_report = (
                fixture
                / "evals"
                / "research-progress"
                / "cases"
                / "safe-existing-report-update"
                / "inputs"
                / "reports"
                / "group-meeting"
                / "2026-07-13.md"
            )
            existing_report.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "source not found",
                (result.stdout + result.stderr).lower(),
            )

    def test_non_synthetic_eval_text_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            task = (
                fixture
                / "evals"
                / "research-progress"
                / "cases"
                / "clean-multiseed"
                / "task.md"
            )
            task.write_text("Create a report.", encoding="utf-8")

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "synthetic example", (result.stdout + result.stderr).lower()
            )

    def test_corrupt_eval_fixture_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            corrupt = (
                fixture
                / "evals"
                / "research-progress"
                / "cases"
                / "partial-source-failure"
                / "inputs"
                / "results"
                / "secondary.csv"
            )
            corrupt.write_bytes(corrupt.read_bytes() + b"changed")

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "corrupt csv hash", (result.stdout + result.stderr).lower()
            )

    def test_selected_candidate_block_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            write_candidate_selection(
                fixture, ["E1", "E2", "E3", "E4", "E5", "P1", "P2"]
            )
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace("<!-- E1 -->\n", "", 1),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "selected block e1 is missing",
                (result.stdout + result.stderr).lower(),
            )

    def test_unselected_candidate_block_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            write_candidate_selection(fixture, [])
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "### 3. Select one report mode",
                    "<!-- E1 -->\n\n### 3. Select one report mode",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "unselected block e1 is present",
                (result.stdout + result.stderr).lower(),
            )

    def test_unknown_candidate_block_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            write_candidate_selection(fixture, ["E9"])

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "unknown selected block e9",
                (result.stdout + result.stderr).lower(),
            )

    def test_existing_report_encoding_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "Treat text encoding as protected content.", "", 1
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "encoding guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_unsupported_explanation_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "Do not invent or brainstorm alternative causal explanations",
                    "Do not add unsupported explanations",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "unsupported-explanation guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_sparse_report_length_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "For sparse source material, target 1-2 rendered pages.",
                    "Keep sparse reports concise.",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "sparse-report length guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_input_contract_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "Accept a natural-language request without forcing the user to fill a form.",
                    "Accept a request without forcing a form.",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "input-contract guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_output_contract_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "Make the first screen decision-useful: summarize the current state",
                    "Make the report useful:",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "output-contract guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_source_required_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "If no usable source or explicit source scope is available",
                    "If source material is unavailable",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "source-required guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_meeting_lifecycle_contract_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "Run an internal evidence-completeness check for every empirical result",
                    "Review the available evidence before drafting",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "meeting-lifecycle guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_meeting_lifecycle_template_terms_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            template = (
                fixture
                / "lab-meeting-report"
                / "references"
                / "mixed-report.md"
            )
            content = template.read_text(encoding="utf-8")
            template.write_text(
                content.replace(
                    "## 当前阻塞与需协助（存在时保留）",
                    "## 当前问题（需要组内输入时保留）",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "meeting-lifecycle template term",
                (result.stdout + result.stderr).lower(),
            )

    def test_research_example_lifecycle_terms_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            report = fixture / "examples" / "research-progress" / "report.md"
            content = report.read_text(encoding="utf-8")
            report.write_text(
                content.replace(
                    "## Previous Action Review",
                    "## Previous Work",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "example missing meeting-lifecycle term",
                (result.stdout + result.stderr).lower(),
            )

    def test_weekly_snapshot_template_fields_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            template = (
                fixture
                / "lab-meeting-report"
                / "references"
                / "paper-review.md"
            )
            content = template.read_text(encoding="utf-8")
            template.write_text(
                content.replace("**关键证据：**", "**关键结果：**", 1),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "weekly-snapshot field",
                (result.stdout + result.stderr).lower(),
            )

    def test_weekly_snapshot_example_fields_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            report = fixture / "examples" / "mixed" / "report.md"
            content = report.read_text(encoding="utf-8")
            report.write_text(
                content.replace(
                    "**Blocker or help needed:**", "**Open question:**", 1
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "example report missing weekly-snapshot field",
                (result.stdout + result.stderr).lower(),
            )

    def test_default_weekly_report_rejects_audit_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            report = fixture / "examples" / "weekly-summary" / "report.md"
            content = report.read_text(encoding="utf-8")
            report.write_text(
                content + "\n## Audit Appendix\n\nUnexpected audit content.\n",
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "audit-only section",
                (result.stdout + result.stderr).lower(),
            )

    def test_default_weekly_slides_require_presenter_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            slides = fixture / "examples" / "weekly-summary" / "slides.md"
            content = slides.read_text(encoding="utf-8")
            slides.write_text(
                content.replace("**Discuss:**", "**Question:**", 1),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "slide missing presenter field",
                (result.stdout + result.stderr).lower(),
            )

    def test_default_weekly_slides_must_enable_marp(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            slides = fixture / "examples" / "weekly-summary" / "slides.md"
            content = slides.read_text(encoding="utf-8")
            slides.write_text(
                content.replace("marp: true", "marp: false", 1),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "must enable marp",
                (result.stdout + result.stderr).lower(),
            )

    def test_unsupplied_expectation_guard_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            skill_file = fixture / "lab-meeting-report" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(
                content.replace(
                    "Do not infer an experiment's intended outcome",
                    "Do not invent an experiment expectation",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "unsupplied-expectation guard",
                (result.stdout + result.stderr).lower(),
            )

    def test_default_priority_rank_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            template = (
                fixture
                / "lab-meeting-report"
                / "references"
                / "mixed-report.md"
            )
            content = template.read_text(encoding="utf-8")
            template.write_text(
                content.replace(
                    "| <动作> | <姓名或待补充> | <日期或待补充> | <结果或文件> | <判据> | <风险> |",
                    "| P0 | <动作> | <姓名或待补充> | <日期或待补充> | <结果或文件> | <判据> | <风险> |",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "default priority rank",
                (result.stdout + result.stderr).lower(),
            )

    def test_missing_final_benchmark_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            benchmark = (
                fixture / "benchmarks" / "v1.1-v1.2" / "benchmark.json"
            )
            benchmark.unlink()

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing final benchmark",
                (result.stdout + result.stderr).lower(),
            )

    def test_candidate_final_benchmark_failure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            benchmark_path = (
                fixture / "benchmarks" / "v1.1-v1.2" / "benchmark.json"
            )
            benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
            candidate = next(
                run
                for run in benchmark["runs"]
                if run["configuration"] == "with_skill"
            )
            candidate["result"]["pass_rate"] = 0.9
            candidate["result"]["failed"] = 1
            benchmark_path.write_text(
                json.dumps(benchmark, indent=2) + "\n", encoding="utf-8"
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "candidate benchmark run failed",
                (result.stdout + result.stderr).lower(),
            )

    def test_final_benchmark_requires_codex_self_review_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "repo"
            copy_fixture(fixture)
            benchmark_path = (
                fixture / "benchmarks" / "v1.1-v1.2" / "benchmark.json"
            )
            benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
            benchmark["metadata"]["analyzer_model"] = "human-blind-review"
            benchmark_path.write_text(
                json.dumps(benchmark, indent=2) + "\n", encoding="utf-8"
            )

            result = run_validator(fixture)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "analyzer model",
                (result.stdout + result.stderr).lower(),
            )


if __name__ == "__main__":
    unittest.main()
