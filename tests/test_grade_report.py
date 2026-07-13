from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.grade_report import grade_text, main


def base_manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "case_id": "unit-case",
        "layer": "composition",
        "language": "en",
        "report_mode": "research-progress",
        "task_file": "task.md",
        "input_root": "inputs",
        "expected_report": "reports/group-meeting/2026-07-13.md",
        "numbers": [],
        "derived_numbers": [],
        "required_evidence": [],
        "negative_results": [],
        "conflicts": [],
        "forbidden_patterns": [],
        "required_sources": [],
        "forbidden_sources": [],
        "skipped_sources": [],
        "preservation_markers": [],
    }


def manifest_with_numbers_and_gain() -> dict[str, object]:
    manifest = base_manifest()
    manifest["numbers"] = [
        {
            "id": "baseline",
            "value": "0.712",
            "unit": "ratio",
            "required": True,
            "source": "inputs/results.md",
        },
        {
            "id": "candidate",
            "value": "0.757",
            "unit": "ratio",
            "required": True,
            "source": "inputs/results.md",
        },
    ]
    manifest["derived_numbers"] = [
        {
            "id": "gain",
            "value": "0.045",
            "unit": "ratio",
            "required": False,
            "operation": "subtract",
            "operands": ["0.757", "0.712"],
        }
    ]
    return manifest


def manifest_with_required_ratio(value: str) -> dict[str, object]:
    manifest = base_manifest()
    manifest["numbers"] = [
        {
            "id": "ratio",
            "value": value,
            "unit": "ratio",
            "required": True,
            "source": "inputs/results.md",
        }
    ]
    return manifest


def manifest_with_metadata_numbers() -> dict[str, object]:
    manifest = manifest_with_required_ratio("0.757")
    manifest["numbers"].extend(
        {
            "id": f"metadata-{value}",
            "value": value,
            "unit": "metadata",
            "required": False,
            "source": "task.md",
        }
        for value in ["2026", "7", "13", "11", "22", "33"]
    )
    return manifest


class GradeReportTests(unittest.TestCase):
    def assert_expectation_failed(
        self, grading: dict[str, object], expectation_id: str
    ) -> None:
        item = next(
            entry
            for entry in grading["expectations"]
            if entry["text"] == expectation_id
        )
        self.assertFalse(item["passed"], item)

    def test_valid_numbers_and_declared_subtraction_pass(self) -> None:
        report = "Baseline 0.712; candidate 0.757; calculated gain 0.045."

        grading = grade_text(report, manifest_with_numbers_and_gain())

        self.assertTrue(grading["hard_pass"], grading)

    def test_invented_number_fails_closed_world(self) -> None:
        report = "Baseline 0.712; candidate 0.757; p = 0.03."

        grading = grade_text(report, manifest_with_numbers_and_gain())

        self.assert_expectation_failed(grading, "numeric-closed-world")

    def test_missing_required_number_fails(self) -> None:
        report = "The candidate improved over baseline 0.712."

        grading = grade_text(report, manifest_with_numbers_and_gain())

        self.assert_expectation_failed(grading, "required-number:candidate")

    def test_percent_and_ratio_are_equivalent(self) -> None:
        report = "Macro-F1 was 71.2%."

        grading = grade_text(report, manifest_with_required_ratio("0.712"))

        self.assertTrue(grading["hard_pass"], grading)

    def test_iso_date_and_seed_ids_are_allowed_metadata(self) -> None:
        report = "Date 2026-07-13; seeds 11, 22, and 33; score 0.757."

        grading = grade_text(report, manifest_with_metadata_numbers())

        self.assertTrue(grading["hard_pass"], grading)

    def test_cli_writes_grading_json_and_returns_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = root / "unit-case"
            (case / "inputs").mkdir(parents=True)
            (case / "task.md").write_text("Synthetic example", encoding="utf-8")
            (case / "inputs" / "results.md").write_text(
                "Synthetic example", encoding="utf-8"
            )
            manifest_path = case / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest_with_required_ratio("0.712")),
                encoding="utf-8",
            )
            report_path = root / "report.md"
            report_path.write_text("Macro-F1 was 71.2%.", encoding="utf-8")
            output_path = root / "grading.json"

            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = main(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--report",
                        str(report_path),
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            grading = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertTrue(grading["hard_pass"])


if __name__ == "__main__":
    unittest.main()
