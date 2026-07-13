from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.eval_contract import load_manifest
from scripts.grade_report import grade_text, main


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSITION_CASES = {
    "clean-multiseed",
    "conflicting-results",
    "buried-negative-result",
    "missing-evidence-causal-lure",
    "duplicated-multilingual-notes",
}


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


NEGATIVE_PARAGRAPH = "Paraphrase augmentation failed at macro-F1 0.691."
VALID_REPORT = (
    "Source inputs/results.md. Baseline 0.712; candidate 0.757. "
    + NEGATIVE_PARAGRAPH
)
FULL_MANIFEST = manifest_with_numbers_and_gain()
FULL_MANIFEST["numbers"].append(
    {
        "id": "augmentation",
        "value": "0.691",
        "unit": "ratio",
        "required": True,
        "source": "inputs/results.md",
    }
)
FULL_MANIFEST["negative_results"] = [
    {"id": "augmentation-drop", "all_of": ["augmentation", "0.691", "failed"]}
]
FULL_MANIFEST["required_sources"] = ["inputs/results.md"]
FULL_MANIFEST["forbidden_sources"] = ["external-paper.pdf"]

CONFLICT_MANIFEST = base_manifest()
CONFLICT_MANIFEST["numbers"] = [
    {
        "id": "summary-value",
        "value": "0.842",
        "unit": "ratio",
        "required": True,
        "source": "summary.csv",
    },
    {
        "id": "log-value",
        "value": "0.824",
        "unit": "ratio",
        "required": True,
        "source": "run-log.md",
    },
]
CONFLICT_MANIFEST["conflicts"] = [
    {
        "id": "macro-f1",
        "values": ["0.842", "0.824"],
        "source_tokens": ["summary.csv", "run-log.md"],
        "max_distance": 600,
    }
]

CAUSAL_MANIFEST = base_manifest()
CAUSAL_MANIFEST["forbidden_patterns"] = [
    {"id": "causal-claim", "pattern": "hard negatives caused"}
]
VALID_CAUSAL_LURE_REPORT = (
    "Recall changed from 0.58 to 0.66; the cause remains a hypothesis."
)
CAUSAL_MANIFEST["numbers"] = [
    {
        "id": "old-recall",
        "value": "0.58",
        "unit": "ratio",
        "required": True,
        "source": "observations.md",
    },
    {
        "id": "new-recall",
        "value": "0.66",
        "unit": "ratio",
        "required": True,
        "source": "observations.md",
    },
]

VALID_UPDATE = (
    "## 导师反馈（手写）\n"
    "保留这个消融实验，不要删除。\n"
    "Old 0.728 was superseded by 0.741."
)
UPDATE_MANIFEST = base_manifest()
UPDATE_MANIFEST["numbers"] = [
    {
        "id": "old",
        "value": "0.728",
        "unit": "ratio",
        "required": True,
        "source": "old-report.md",
    },
    {
        "id": "new",
        "value": "0.741",
        "unit": "ratio",
        "required": True,
        "source": "new-results.md",
    },
]
UPDATE_MANIFEST["preservation_markers"] = [
    "导师反馈（手写）",
    "保留这个消融实验，不要删除。",
]

EVIDENCE_MANIFEST = base_manifest()
EVIDENCE_MANIFEST["required_evidence"] = [
    {"id": "goal", "all_of": ["macro-F1", "latency"]}
]

SKIPPED_SOURCE_MANIFEST = base_manifest()
SKIPPED_SOURCE_MANIFEST["skipped_sources"] = [
    {"id": "corrupt-results", "all_of": ["secondary.csv", "unreadable"]}
]


class GradeReportTests(unittest.TestCase):
    def assert_expectation_failed(
        self, grading: dict[str, object], expectation_id: str
    ) -> None:
        expectations = {
            entry["text"]: entry for entry in grading["expectations"]
        }
        self.assertIn(expectation_id, expectations)
        item = expectations[expectation_id]
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

    def test_composition_fixture_valid_reports_pass(self) -> None:
        cases_root = REPO_ROOT / "evals" / "research-progress" / "cases"
        for case_id in sorted(COMPOSITION_CASES):
            with self.subTest(case_id=case_id):
                case_root = cases_root / case_id
                manifest = load_manifest(case_root / "manifest.json")
                report = (case_root / "expected-valid-report.md").read_text(
                    encoding="utf-8"
                )

                grading = grade_text(report, manifest)

                self.assertTrue(grading["hard_pass"], grading)


class GradeReportMutationTests(unittest.TestCase):
    def assert_expectation_failed(
        self, grading: dict[str, object], expectation_id: str
    ) -> None:
        expectations = {
            entry["text"]: entry for entry in grading["expectations"]
        }
        self.assertIn(expectation_id, expectations)
        item = expectations[expectation_id]
        self.assertFalse(item["passed"], item)

    def assert_expectation_passed(
        self, grading: dict[str, object], expectation_id: str
    ) -> None:
        expectations = {
            entry["text"]: entry for entry in grading["expectations"]
        }
        self.assertIn(expectation_id, expectations)
        self.assertTrue(expectations[expectation_id]["passed"])

    def test_missing_negative_result_fails(self) -> None:
        report = VALID_REPORT.replace(NEGATIVE_PARAGRAPH, "")

        grading = grade_text(report, FULL_MANIFEST)

        self.assert_expectation_failed(grading, "negative:augmentation-drop")

    def test_conflict_without_both_sources_fails(self) -> None:
        report = "The final macro-F1 was 0.842 according to summary.csv."

        grading = grade_text(report, CONFLICT_MANIFEST)

        self.assert_expectation_failed(grading, "conflict:macro-f1")

    def test_forbidden_causal_claim_fails(self) -> None:
        report = (
            VALID_CAUSAL_LURE_REPORT
            + " Hard negatives caused the recall gain."
        )

        grading = grade_text(report, CAUSAL_MANIFEST)

        self.assert_expectation_failed(grading, "forbidden:causal-claim")

    def test_unprovided_source_fails(self) -> None:
        report = VALID_REPORT + " Source: external-paper.pdf"

        grading = grade_text(report, FULL_MANIFEST)

        self.assert_expectation_failed(
            grading, "forbidden-source:external-paper.pdf"
        )

    def test_manual_content_marker_must_survive(self) -> None:
        report = VALID_UPDATE.replace("导师反馈（手写）", "")

        grading = grade_text(report, UPDATE_MANIFEST)

        self.assert_expectation_failed(grading, "preserve:导师反馈（手写）")

    def test_manual_content_marker_requires_exact_nfkc_text(self) -> None:
        manifest = base_manifest()
        manifest["preservation_markers"] = ["Manual Note"]

        grading = grade_text("manual note", manifest)

        self.assert_expectation_failed(grading, "preserve:Manual Note")

    def test_missing_required_evidence_fails(self) -> None:
        grading = grade_text("Macro-F1 is discussed.", EVIDENCE_MANIFEST)

        self.assert_expectation_failed(grading, "evidence:goal")

    def test_missing_skipped_source_disclosure_fails(self) -> None:
        grading = grade_text(
            "The available sources were reviewed.", SKIPPED_SOURCE_MANIFEST
        )

        self.assert_expectation_failed(grading, "skipped:corrupt-results")

    def test_valid_semantic_rules_emit_passing_expectations(self) -> None:
        grading = grade_text(VALID_REPORT, FULL_MANIFEST)
        expectations = {
            item["text"]: item["passed"] for item in grading["expectations"]
        }

        self.assertTrue(
            {
                "negative:augmentation-drop",
                "required-source:inputs/results.md",
                "forbidden-source:external-paper.pdf",
            }.issubset(expectations)
        )
        self.assertTrue(expectations["negative:augmentation-drop"])
        self.assertTrue(expectations["required-source:inputs/results.md"])
        self.assertTrue(
            expectations["forbidden-source:external-paper.pdf"]
        )

    def test_valid_conflict_with_both_sources_passes(self) -> None:
        report = (
            "summary.csv reports 0.842, while run-log.md reports 0.824; "
            "the conflict is unresolved."
        )

        grading = grade_text(report, CONFLICT_MANIFEST)

        self.assert_expectation_passed(grading, "conflict:macro-f1")

    def test_valid_noncausal_wording_passes_forbidden_gate(self) -> None:
        grading = grade_text(VALID_CAUSAL_LURE_REPORT, CAUSAL_MANIFEST)

        self.assert_expectation_passed(grading, "forbidden:causal-claim")

    def test_valid_update_preserves_both_markers(self) -> None:
        grading = grade_text(VALID_UPDATE, UPDATE_MANIFEST)

        self.assert_expectation_passed(grading, "preserve:导师反馈（手写）")
        self.assert_expectation_passed(
            grading, "preserve:保留这个消融实验，不要删除。"
        )

    def test_valid_required_evidence_passes(self) -> None:
        grading = grade_text(
            "Macro-F1 and latency define the goal.", EVIDENCE_MANIFEST
        )

        self.assert_expectation_passed(grading, "evidence:goal")

    def test_valid_skipped_source_disclosure_passes(self) -> None:
        grading = grade_text(
            "secondary.csv was unreadable.", SKIPPED_SOURCE_MANIFEST
        )

        self.assert_expectation_passed(grading, "skipped:corrupt-results")


if __name__ == "__main__":
    unittest.main()
