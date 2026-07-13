from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
