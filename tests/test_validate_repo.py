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


if __name__ == "__main__":
    unittest.main()
