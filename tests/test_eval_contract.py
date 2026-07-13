from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.eval_contract import (
    ContractError,
    hash_tree,
    iter_case_manifests,
    load_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

COMPOSITION_CASES = {
    "clean-multiseed",
    "conflicting-results",
    "buried-negative-result",
    "missing-evidence-causal-lure",
    "duplicated-multilingual-notes",
}

VALID_MANIFEST = {
    "schema_version": 1,
    "case_id": "clean-multiseed",
    "layer": "composition",
    "language": "en",
    "report_mode": "research-progress",
    "task_file": "task.md",
    "input_root": "inputs",
    "expected_report": "reports/group-meeting/2026-07-13.md",
    "numbers": [
        {
            "id": "baseline",
            "value": "0.712",
            "unit": "ratio",
            "required": True,
            "source": "inputs/results.md",
        },
        {
            "id": "year",
            "value": "2026",
            "unit": "metadata",
            "required": False,
            "source": "task.md",
        },
    ],
    "derived_numbers": [],
    "required_evidence": [
        {"id": "goal", "all_of": ["macro-F1", "latency"]}
    ],
    "negative_results": [],
    "conflicts": [],
    "forbidden_patterns": [],
    "required_sources": ["inputs/results.md"],
    "forbidden_sources": [],
    "skipped_sources": [],
    "preservation_markers": [],
}


class ContractTests(unittest.TestCase):
    def write_case(self, root: Path, manifest: dict | None = None) -> Path:
        data = deepcopy(manifest if manifest is not None else VALID_MANIFEST)
        case = root / str(data["case_id"])
        (case / "inputs").mkdir(parents=True)
        (case / "task.md").write_text(
            "Synthetic example task", encoding="utf-8"
        )
        (case / "inputs" / "results.md").write_text(
            "Synthetic example input", encoding="utf-8"
        )
        path = case / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_valid_manifest_loads_and_paths_stay_inside_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            loaded = load_manifest(self.write_case(Path(temp)))

        self.assertEqual(loaded["case_id"], "clean-multiseed")

    def test_unknown_top_level_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = {**deepcopy(VALID_MANIFEST), "unexpected": True}

            with self.assertRaisesRegex(ContractError, "unexpected"):
                load_manifest(self.write_case(Path(temp), manifest))

    def test_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = {
                **deepcopy(VALID_MANIFEST),
                "expected_report": "../escaped.md",
            }

            with self.assertRaisesRegex(ContractError, "relative path"):
                load_manifest(self.write_case(Path(temp), manifest))

    def test_hash_tree_is_stable_and_content_sensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.txt").write_text("one", encoding="utf-8")
            first = hash_tree(root)

            self.assertEqual(first, hash_tree(root))
            (root / "a.txt").write_text("two", encoding="utf-8")
            self.assertNotEqual(first, hash_tree(root))

    def test_composition_case_inventory_loads(self) -> None:
        root = REPO_ROOT / "evals" / "research-progress" / "cases"
        manifests = [
            load_manifest(path) for path in iter_case_manifests(root)
        ]
        loaded = {
            item["case_id"]
            for item in manifests
            if item["layer"] == "composition"
        }

        self.assertEqual(loaded, COMPOSITION_CASES)


if __name__ == "__main__":
    unittest.main()
