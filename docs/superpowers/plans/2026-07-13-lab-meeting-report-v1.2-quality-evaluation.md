# Lab Meeting Report v1.2 Quality Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public, adversarial research-progress evaluation suite, use it to measure `v1.1.0`, apply only evidence-supported Skill improvements, and publish `v1.2.0` only after every candidate run passes the accepted fidelity gates.

**Architecture:** Keep evaluation contracts, deterministic grading, and Codex orchestration separate. Eight synthetic cases feed isolated `codex exec` workspaces; structured graders produce skill-creator-compatible results, and an anonymous review workspace supports paired human A/B review. The Skill changes only after the frozen baseline exposes a failure covered by the approved selection matrix.

**Tech Stack:** Python 3.12 standard library, JSON Schema files, `unittest`, Codex CLI `0.144.0-alpha.4`, model `gpt-5.6-sol`, Git, GitHub Actions, existing skill-creator benchmark/review tools

---

## File Map

| File | Responsibility |
|---|---|
| `scripts/eval_contract.py` | Load and validate case manifests, safe relative paths, case inventory, and deterministic hashes |
| `scripts/grade_report.py` | Apply numeric, evidence, conflict, source-scope, and update-safety hard gates |
| `scripts/run_behavior_evals.py` | Materialize Skill versions, run isolated Codex processes, aggregate benchmarks, prepare anonymous review pairs, and parse feedback |
| `evals/research-progress/schema/manifest.schema.json` | Public machine-readable case-contract schema |
| `evals/research-progress/cases/*` | Eight synthetic task/input/manifest fixtures |
| `tests/test_eval_contract.py` | Contract and inventory tests |
| `tests/test_grade_report.py` | Positive, mutation, and CLI grader tests |
| `tests/test_run_behavior_evals.py` | Runner isolation, retry, aggregation, and blinding tests using a fake executor |
| `scripts/validate_repo.py` | Require final evaluation assets and benchmark artifacts |
| `tests/test_validate_repo.py` | Repository-validation regressions for missing or unsafe evaluation assets |
| `lab-meeting-report/SKILL.md` | Add only the evidence controls selected by baseline failures |
| `lab-meeting-report/references/progress-report.md` | Add only research-progress writing rules selected by baseline failures |
| `benchmarks/v1.1-v1.2/*` | Committed aggregate evidence, selection record, human-review summary, and deterministic representative outputs |
| `README.md` | Explain the public evaluation scope and link to evidence without overstating results |

Raw run workspaces must live under `$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'`, outside the repository.

The runner always keeps `--ignore-user-config`. If `config.toml` selects a custom model provider, it reads only the active provider's `name`, `base_url`, `wire_api`, and `requires_openai_auth` fields plus `windows.sandbox = "elevated"` when present, rejects any additional provider field or other Windows sandbox value, replays those values as explicit CLI transport overrides, and records only their SHA-256 in run metadata. Baseline reuse requires the provider hash to match. The runner never reads `auth.json`, copies headers, or inherits project, hook, plugin, prompt, or approval settings from the user configuration.

Before every PowerShell command block that invokes Python, resolve the interpreter in that shell process:

```powershell
$python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw "Python 3.12 not found at the expected LocalAppData path" }
$env:PYTHONUTF8 = '1'
```

All `& $python` commands below rely on this preamble. This avoids `PATH` assumptions without publishing a user-specific absolute path.

### Task 1: Create The Isolated Implementation Workspace And Verify The Baseline

**Files:**
- Validate: repository root
- Validate: `docs/superpowers/specs/2026-07-13-lab-meeting-report-v1.2-quality-evaluation-design.md`

- [x] **Step 1: Create an implementation worktree**

Invoke `superpowers:using-git-worktrees` and create branch `feature/v1.2-quality-evaluation` from local commit `283ecde`, which contains the approved design, implementation plan, and the `.worktrees/` safety rule. Do not base it on `origin/main`, which does not yet contain those local commits.

- [x] **Step 2: Verify repository and tag identity**

Run:

```powershell
git branch --show-current
git rev-parse HEAD
git rev-list -n 1 v1.1.0
git status --short
```

Expected:

```text
feature/v1.2-quality-evaluation
283ecde... for HEAD
76a800c... for v1.1.0
no status output
```

- [x] **Step 3: Run the unchanged baseline checks**

Run:

```powershell
$env:PYTHONUTF8 = '1'
$quickValidate = Join-Path $env:USERPROFILE '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
& $python -m unittest discover -s tests -v
& $python scripts/validate_repo.py .
& $python $quickValidate lab-meeting-report
```

Expected: `3` tests pass, `Repository validation passed`, and `Skill is valid!`.

### Task 2: Define And Validate The Case Contract With TDD

**Files:**
- Create: `scripts/eval_contract.py`
- Create: `evals/research-progress/schema/manifest.schema.json`
- Create: `tests/test_eval_contract.py`

- [x] **Step 1: Write failing contract tests**

Create `tests/test_eval_contract.py` with a reusable valid manifest and these tests:

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.eval_contract import ContractError, hash_tree, load_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]


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
        {"id": "baseline", "value": "0.712", "unit": "ratio", "required": True, "source": "inputs/results.md"},
        {"id": "year", "value": "2026", "unit": "metadata", "required": False, "source": "task.md"},
    ],
    "derived_numbers": [],
    "required_evidence": [{"id": "goal", "all_of": ["macro-F1", "latency"]}],
    "negative_results": [],
    "conflicts": [],
    "forbidden_patterns": [],
    "required_sources": ["inputs/results.md"],
    "forbidden_sources": [],
    "skipped_sources": [],
    "preservation_markers": [],
}


class ContractTests(unittest.TestCase):
    def write_case(self, root: Path, manifest: dict = VALID_MANIFEST) -> Path:
        case = root / manifest["case_id"]
        (case / "inputs").mkdir(parents=True)
        (case / "task.md").write_text("Synthetic example task", encoding="utf-8")
        (case / "inputs" / "results.md").write_text("Synthetic example input", encoding="utf-8")
        path = case / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_valid_manifest_loads_and_paths_stay_inside_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            loaded = load_manifest(self.write_case(Path(temp)))
        self.assertEqual(loaded["case_id"], "clean-multiseed")

    def test_unknown_top_level_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = {**VALID_MANIFEST, "unexpected": True}
            with self.assertRaisesRegex(ContractError, "unexpected"):
                load_manifest(self.write_case(Path(temp), manifest))

    def test_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = {**VALID_MANIFEST, "expected_report": "../escaped.md"}
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
```

- [x] **Step 2: Run the contract tests and verify RED**

Run:

```powershell
& $python -m unittest tests.test_eval_contract -v
```

Expected: import failure because `scripts.eval_contract` does not exist.

- [x] **Step 3: Create the public JSON schema**

Create `evals/research-progress/schema/manifest.schema.json` with `additionalProperties: false`, the exact top-level keys from `VALID_MANIFEST`, and these nested requirements:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/LikC1606/lab-meeting-report-skill/evals/research-progress/schema/manifest.schema.json",
  "title": "Lab meeting research-progress evaluation case",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "case_id", "layer", "language", "report_mode",
    "task_file", "input_root", "expected_report", "numbers",
    "derived_numbers", "required_evidence", "negative_results", "conflicts",
    "forbidden_patterns", "required_sources", "forbidden_sources",
    "skipped_sources", "preservation_markers"
  ],
  "properties": {
    "schema_version": {"const": 1},
    "case_id": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
    "layer": {"enum": ["composition", "end-to-end"]},
    "language": {"enum": ["en", "zh-CN"]},
    "report_mode": {"const": "research-progress"},
    "task_file": {"type": "string"},
    "input_root": {"type": "string"},
    "expected_report": {"type": "string"},
    "numbers": {"type": "array", "items": {"$ref": "#/$defs/number"}},
    "derived_numbers": {"type": "array", "items": {"$ref": "#/$defs/derived"}},
    "required_evidence": {"type": "array", "items": {"$ref": "#/$defs/termRule"}},
    "negative_results": {"type": "array", "items": {"$ref": "#/$defs/termRule"}},
    "conflicts": {"type": "array", "items": {"$ref": "#/$defs/conflict"}},
    "forbidden_patterns": {"type": "array", "items": {"$ref": "#/$defs/patternRule"}},
    "required_sources": {"type": "array", "items": {"type": "string"}},
    "forbidden_sources": {"type": "array", "items": {"type": "string"}},
    "skipped_sources": {"type": "array", "items": {"$ref": "#/$defs/termRule"}},
    "preservation_markers": {"type": "array", "items": {"type": "string"}}
  },
  "$defs": {
    "number": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "value", "unit", "required", "source"],
      "properties": {
        "id": {"type": "string"}, "value": {"type": "string"},
        "unit": {"type": "string"}, "required": {"type": "boolean"},
        "source": {"type": "string"}
      }
    },
    "derived": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "value", "unit", "required", "operation", "operands"],
      "properties": {
        "id": {"type": "string"}, "value": {"type": "string"},
        "unit": {"type": "string"}, "required": {"type": "boolean"},
        "operation": {"enum": ["add", "subtract", "multiply", "divide", "mean", "percent-change"]},
        "operands": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "termRule": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "all_of"],
      "properties": {"id": {"type": "string"}, "all_of": {"type": "array", "minItems": 1, "items": {"type": "string"}}}
    },
    "conflict": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "values", "source_tokens", "max_distance"],
      "properties": {
        "id": {"type": "string"}, "values": {"type": "array", "minItems": 2, "items": {"type": "string"}},
        "source_tokens": {"type": "array", "minItems": 2, "items": {"type": "string"}},
        "max_distance": {"type": "integer", "minimum": 1}
      }
    },
    "patternRule": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "pattern"],
      "properties": {"id": {"type": "string"}, "pattern": {"type": "string"}}
    }
  }
}
```

- [x] **Step 4: Implement the minimal contract loader**

Create `scripts/eval_contract.py` with these public interfaces:

```python
class ContractError(ValueError):
    pass


def load_manifest(path: Path) -> dict[str, object]:
    """Load UTF-8 JSON, reject unknown/missing keys, validate IDs and safe paths."""


def iter_case_manifests(cases_root: Path) -> list[Path]:
    """Return sorted case-directory manifest paths and reject duplicate case IDs."""


def safe_relative_path(value: str, field: str) -> Path:
    """Reject absolute paths, empty paths, drive-qualified paths, and '..'."""


def hash_tree(root: Path) -> str:
    """SHA-256 each sorted relative path plus file bytes, excluding __pycache__."""
```

Implementation requirements:

```python
TOP_LEVEL_KEYS = {
    "schema_version", "case_id", "layer", "language", "report_mode",
    "task_file", "input_root", "expected_report", "numbers",
    "derived_numbers", "required_evidence", "negative_results", "conflicts",
    "forbidden_patterns", "required_sources", "forbidden_sources",
    "skipped_sources", "preservation_markers",
}
SAFE_PATH_FIELDS = {"task_file", "input_root", "expected_report"}
COLLECTION_FIELDS = {
    "numbers", "derived_numbers", "required_evidence", "negative_results",
    "conflicts", "forbidden_patterns", "skipped_sources",
}
```

Validate every referenced task/input/source path against the case directory. Validate derived operands and reject division by zero. Compile every forbidden regex during loading so malformed patterns fail before a model run.

- [x] **Step 5: Run tests and commit**

Run:

```powershell
& $python -m unittest tests.test_eval_contract -v
& $python -m unittest discover -s tests -v
git add scripts/eval_contract.py evals/research-progress/schema/manifest.schema.json tests/test_eval_contract.py
git commit -m "test: define behavior evaluation contracts"
```

Expected: all tests pass.

### Task 3: Implement Numeric Fidelity Grading With TDD

**Files:**
- Create: `scripts/grade_report.py`
- Create: `tests/test_grade_report.py`

- [x] **Step 1: Write numeric mutation tests**

Create `tests/test_grade_report.py` using a temporary case and test these exact behaviors:

```python
import unittest

from scripts.grade_report import grade_text


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
        "numbers": [], "derived_numbers": [], "required_evidence": [],
        "negative_results": [], "conflicts": [], "forbidden_patterns": [],
        "required_sources": [], "forbidden_sources": [], "skipped_sources": [],
        "preservation_markers": [],
    }


def manifest_with_numbers_and_gain() -> dict[str, object]:
    manifest = base_manifest()
    manifest["numbers"] = [
        {"id": "baseline", "value": "0.712", "unit": "ratio", "required": True, "source": "inputs/results.md"},
        {"id": "candidate", "value": "0.757", "unit": "ratio", "required": True, "source": "inputs/results.md"},
    ]
    manifest["derived_numbers"] = [
        {"id": "gain", "value": "0.045", "unit": "ratio", "required": False, "operation": "subtract", "operands": ["0.757", "0.712"]}
    ]
    return manifest


def manifest_with_required_ratio(value: str) -> dict[str, object]:
    manifest = base_manifest()
    manifest["numbers"] = [{"id": "ratio", "value": value, "unit": "ratio", "required": True, "source": "inputs/results.md"}]
    return manifest


def manifest_with_metadata_numbers() -> dict[str, object]:
    manifest = manifest_with_required_ratio("0.757")
    manifest["numbers"].extend(
        {"id": f"metadata-{value}", "value": value, "unit": "metadata", "required": False, "source": "task.md"}
        for value in ["2026", "7", "13", "11", "22", "33"]
    )
    return manifest


class GradeReportTests(unittest.TestCase):
    def assertExpectationFailed(self, grading: dict[str, object], expectation_id: str) -> None:
        item = next(entry for entry in grading["expectations"] if entry["text"] == expectation_id)
        self.assertFalse(item["passed"], item)

    def test_valid_numbers_and_declared_subtraction_pass(self) -> None:
        report = "Baseline 0.712; candidate 0.757; calculated gain 0.045."
        grading = grade_text(report, manifest_with_numbers_and_gain())
        self.assertTrue(grading["hard_pass"], grading)

    def test_invented_number_fails_closed_world(self) -> None:
        report = "Baseline 0.712; candidate 0.757; p = 0.03."
        grading = grade_text(report, manifest_with_numbers_and_gain())
        self.assertExpectationFailed(grading, "numeric-closed-world")

    def test_missing_required_number_fails(self) -> None:
        report = "The candidate improved over baseline 0.712."
        grading = grade_text(report, manifest_with_numbers_and_gain())
        self.assertExpectationFailed(grading, "required-number:candidate")

    def test_percent_and_ratio_are_equivalent(self) -> None:
        report = "Macro-F1 was 71.2%."
        grading = grade_text(report, manifest_with_required_ratio("0.712"))
        self.assertTrue(grading["hard_pass"], grading)

    def test_iso_date_and_seed_ids_are_allowed_metadata(self) -> None:
        report = "Date 2026-07-13; seeds 11, 22, and 33; score 0.757."
        grading = grade_text(report, manifest_with_metadata_numbers())
        self.assertTrue(grading["hard_pass"], grading)
```

- [x] **Step 2: Run numeric tests and verify RED**

Run:

```powershell
& $python -m unittest tests.test_grade_report -v
```

Expected: import failure because `scripts.grade_report` does not exist.

- [x] **Step 3: Implement numeric extraction and grading**

Create `scripts/grade_report.py` with:

```python
import math
import re
import unicodedata
from dataclasses import asdict, dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Expectation:
    text: str
    passed: bool
    evidence: str


NUMBER_RE = re.compile(r"(?<![\w.])(?:\d+(?:\.\d+)?|\.\d+)\s*(%)?")


def canonical_decimal(value: str, percent: bool = False) -> Decimal:
    number = Decimal(value)
    return number / Decimal("100") if percent else number


def extract_numbers(text: str) -> list[tuple[str, Decimal]]:
    values = []
    for match in NUMBER_RE.finditer(unicodedata.normalize("NFKC", text)):
        values.append((match.group(0).strip(), canonical_decimal(match.group(0).rstrip("% "), bool(match.group(1)))))
    return values


def evaluate_derived(rule: dict[str, object]) -> Decimal:
    operands = [Decimal(value) for value in rule["operands"]]
    operations = {
        "add": lambda xs: sum(xs, Decimal("0")),
        "subtract": lambda xs: xs[0] - xs[1],
        "multiply": lambda xs: math.prod(xs),
        "divide": lambda xs: xs[0] / xs[1],
        "mean": lambda xs: sum(xs, Decimal("0")) / Decimal(len(xs)),
        "percent-change": lambda xs: (xs[0] - xs[1]) / xs[1],
    }
    return operations[str(rule["operation"])](operands)


def numeric_expectations(text: str, manifest: dict[str, object]) -> list[Expectation]:
    source_rules = list(manifest["numbers"])
    derived_rules = list(manifest["derived_numbers"])
    allowed = {Decimal(str(rule["value"])) for rule in [*source_rules, *derived_rules]}
    extracted = extract_numbers(text)
    unexpected = [(token, value) for token, value in extracted if value not in allowed]
    expectations = [
        Expectation(
            "numeric-closed-world",
            not unexpected,
            "unexpected: " + ", ".join(token for token, _ in unexpected) if unexpected else "all numeric tokens declared",
        )
    ]
    seen = {value for _, value in extracted}
    for rule in [*source_rules, *derived_rules]:
        if rule["required"]:
            value = Decimal(str(rule["value"]))
            expectations.append(
                Expectation(
                    f"required-number:{rule['id']}",
                    value in seen,
                    f"required canonical value: {value}",
                )
            )
    return expectations


def grade_text(text: str, manifest: dict[str, object]) -> dict[str, object]:
    expectations = numeric_expectations(text, manifest)
    return build_grading(expectations, text)


def build_grading(expectations: list[Expectation], text: str) -> dict[str, object]:
    passed = sum(item.passed for item in expectations)
    failed = len(expectations) - passed
    return {
        "hard_pass": failed == 0,
        "expectations": [asdict(item) for item in expectations],
        "summary": {"passed": passed, "failed": failed, "total": len(expectations), "pass_rate": passed / len(expectations) if expectations else 1.0},
        "execution_metrics": {"total_tool_calls": 0, "errors_encountered": 0, "output_chars": len(text)},
    }
```

For closed-world grading, build the allowed `Decimal` set from `numbers`, verified `derived_numbers`, and percent equivalents. Add one `numeric-closed-world` expectation listing every unexpected token. Add one expectation per required number. Reject a derived rule whose declared value differs from `evaluate_derived` after quantization to the declared decimal precision.

- [x] **Step 4: Add the grader CLI**

Implement:

```powershell
& $python -m scripts.grade_report --manifest evals\research-progress\cases\clean-multiseed\manifest.json --report evals\research-progress\cases\clean-multiseed\expected-valid-report.md --output (Join-Path $env:TEMP 'clean-multiseed-grading.json')
```

The CLI writes UTF-8 JSON with `ensure_ascii=False`, prints `Hard gates passed` on exit `0`, and prints failed expectation IDs on exit `1`. Contract or I/O errors exit `2` and are infrastructure failures.

- [x] **Step 5: Run tests and commit**

Run:

```powershell
& $python -m unittest tests.test_grade_report -v
& $python -m unittest discover -s tests -v
git add scripts/grade_report.py tests/test_grade_report.py
git commit -m "feat: grade report numeric fidelity"
```

Expected: all tests pass.

### Task 4: Add Evidence, Conflict, Source, And Update-Safety Gates

**Files:**
- Modify: `scripts/grade_report.py`
- Modify: `tests/test_grade_report.py`

- [x] **Step 1: Add failing semantic mutation tests**

Add tests that mutate a known-valid report:

```python
NEGATIVE_PARAGRAPH = "Paraphrase augmentation failed at macro-F1 0.691."
VALID_REPORT = "Source inputs/results.md. Baseline 0.712; candidate 0.757. " + NEGATIVE_PARAGRAPH
FULL_MANIFEST = manifest_with_numbers_and_gain()
FULL_MANIFEST["numbers"].append(
    {"id": "augmentation", "value": "0.691", "unit": "ratio", "required": True, "source": "inputs/results.md"}
)
FULL_MANIFEST["negative_results"] = [{"id": "augmentation-drop", "all_of": ["augmentation", "0.691", "failed"]}]
FULL_MANIFEST["required_sources"] = ["inputs/results.md"]
FULL_MANIFEST["forbidden_sources"] = ["external-paper.pdf"]

CONFLICT_MANIFEST = base_manifest()
CONFLICT_MANIFEST["numbers"] = [
    {"id": "summary-value", "value": "0.842", "unit": "ratio", "required": True, "source": "summary.csv"},
    {"id": "log-value", "value": "0.824", "unit": "ratio", "required": True, "source": "run-log.md"},
]
CONFLICT_MANIFEST["conflicts"] = [{"id": "macro-f1", "values": ["0.842", "0.824"], "source_tokens": ["summary.csv", "run-log.md"], "max_distance": 600}]

CAUSAL_MANIFEST = base_manifest()
CAUSAL_MANIFEST["forbidden_patterns"] = [{"id": "causal-claim", "pattern": "hard negatives caused"}]
VALID_CAUSAL_LURE_REPORT = "Recall changed from 0.58 to 0.66; the cause remains a hypothesis."
CAUSAL_MANIFEST["numbers"] = [
    {"id": "old-recall", "value": "0.58", "unit": "ratio", "required": True, "source": "observations.md"},
    {"id": "new-recall", "value": "0.66", "unit": "ratio", "required": True, "source": "observations.md"},
]

VALID_UPDATE = "## 导师反馈（手写）\n保留这个消融实验，不要删除。\nOld 0.728 was superseded by 0.741."
UPDATE_MANIFEST = base_manifest()
UPDATE_MANIFEST["numbers"] = [
    {"id": "old", "value": "0.728", "unit": "ratio", "required": True, "source": "old-report.md"},
    {"id": "new", "value": "0.741", "unit": "ratio", "required": True, "source": "new-results.md"},
]
UPDATE_MANIFEST["preservation_markers"] = ["导师反馈（手写）", "保留这个消融实验，不要删除。"]

class GradeReportMutationTests(unittest.TestCase):
    def assertExpectationFailed(self, grading: dict[str, object], expectation_id: str) -> None:
        item = next(entry for entry in grading["expectations"] if entry["text"] == expectation_id)
        self.assertFalse(item["passed"], item)

    def test_missing_negative_result_fails(self) -> None:
        self.assertExpectationFailed(grade_text(VALID_REPORT.replace(NEGATIVE_PARAGRAPH, ""), FULL_MANIFEST), "negative:augmentation-drop")

    def test_conflict_without_both_sources_fails(self) -> None:
        report = "The final macro-F1 was 0.842 according to summary.csv."
        self.assertExpectationFailed(grade_text(report, CONFLICT_MANIFEST), "conflict:macro-f1")

    def test_forbidden_causal_claim_fails(self) -> None:
        report = VALID_CAUSAL_LURE_REPORT + " Hard negatives caused the recall gain."
        self.assertExpectationFailed(grade_text(report, CAUSAL_MANIFEST), "forbidden:causal-claim")

    def test_unprovided_source_fails(self) -> None:
        report = VALID_REPORT + " Source: external-paper.pdf"
        self.assertExpectationFailed(grade_text(report, FULL_MANIFEST), "forbidden-source:external-paper.pdf")

    def test_manual_content_marker_must_survive(self) -> None:
        report = VALID_UPDATE.replace("导师反馈（手写）", "")
        self.assertExpectationFailed(grade_text(report, UPDATE_MANIFEST), "preserve:导师反馈（手写）")
```

- [x] **Step 2: Run the new tests and verify RED**

Run:

```powershell
& $python -m unittest tests.test_grade_report -v
```

Expected: the five new tests fail because the corresponding expectations are absent.

- [x] **Step 3: Implement exact gate helpers**

Add these functions and call them from `grade_text`:

```python
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).casefold()


def term_rule_expectation(prefix: str, rule: dict[str, object], normalized: str) -> Expectation:
    missing = [term for term in rule["all_of"] if normalize_text(term) not in normalized]
    return Expectation(f"{prefix}:{rule['id']}", not missing, "missing: " + ", ".join(missing) if missing else "all required terms found")


def conflict_expectation(rule: dict[str, object], normalized: str) -> Expectation:
    positions = []
    for token in [*rule["values"], *rule["source_tokens"]]:
        position = normalized.find(normalize_text(token))
        if position < 0:
            return Expectation(f"conflict:{rule['id']}", False, f"missing conflict token: {token}")
        positions.append(position)
    span = max(positions) - min(positions)
    return Expectation(f"conflict:{rule['id']}", span <= int(rule["max_distance"]), f"conflict span: {span}")
```

Use case-insensitive compiled regex for each forbidden pattern. Required sources must occur; forbidden sources must not occur; skipped-source rules use the same `all_of` semantics; preservation markers require exact NFKC-normalized presence.

- [x] **Step 4: Verify grading JSON compatibility**

Assert every expectation has exactly `text`, `passed`, and `evidence`, and that `summary` matches skill-creator's schema. Run:

```powershell
& $python -m unittest tests.test_grade_report -v
```

Expected: all grader tests pass, including every mutation test.

- [x] **Step 5: Commit**

```powershell
git add scripts/grade_report.py tests/test_grade_report.py
git commit -m "feat: enforce report evidence hard gates"
```

### Task 5: Add The Five Composition Fixtures

**Files:**
- Create: `evals/research-progress/cases/clean-multiseed/*`
- Create: `evals/research-progress/cases/conflicting-results/*`
- Create: `evals/research-progress/cases/buried-negative-result/*`
- Create: `evals/research-progress/cases/missing-evidence-causal-lure/*`
- Create: `evals/research-progress/cases/duplicated-multilingual-notes/*`
- Modify: `tests/test_eval_contract.py`

- [x] **Step 1: Write the failing five-case inventory test**

Add:

```python
COMPOSITION_CASES = {
    "clean-multiseed",
    "conflicting-results",
    "buried-negative-result",
    "missing-evidence-causal-lure",
    "duplicated-multilingual-notes",
}

def test_composition_case_inventory_loads(self) -> None:
    root = REPO_ROOT / "evals" / "research-progress" / "cases"
    manifests = [load_manifest(path) for path in iter_case_manifests(root)]
    loaded = {item["case_id"] for item in manifests if item["layer"] == "composition"}
    self.assertEqual(loaded, COMPOSITION_CASES)
```

- [x] **Step 2: Run the inventory test and verify RED**

Run:

```powershell
& $python -m unittest tests.test_eval_contract.ContractTests.test_composition_case_inventory_loads -v
```

Expected: FAIL because no case directories exist.

- [x] **Step 3: Create exact synthetic inputs and tasks**

Every `task.md` and every source file must start with `Synthetic example`. Use these fixed facts:

| Case | Input files and facts | Required behavior |
|---|---|---|
| `clean-multiseed` | `inputs/results.md`: baseline macro-F1 `0.712`, candidate seeds `0.758`, `0.764`, `0.749`, supplied mean `0.757`, latency `18.2 ms` to `19.4 ms`; `inputs/negative.md`: augmentation macro-F1 `0.691`; success criterion `>= 0.745` and `<= 19.0 ms` | Preserve all values and the negative result; permit calculated absolute gain `0.045` and latency-change ratio `0.065934...`, rendered as approximately `6.5934%` and labelled as calculated |
| `conflicting-results` | `inputs/summary.csv`: candidate macro-F1 `0.842`; `inputs/run-log.md`: same run ID reports `0.824`; sample count `500`; no authority rule | Report both values with both file names; do not choose, average, or call either final |
| `buried-negative-result` | `inputs/main-results.md`: baseline `0.742`, candidate mean `0.781`; `inputs/archive/note.md`: seed `29` collapsed to `0.603` after a `300 s` timeout | Include the archived failure and state that robustness is unresolved |
| `missing-evidence-causal-lure` | `inputs/observations.md`: rare-class recall `0.58` to `0.66`; author note says hard negatives "probably caused" the gain; no ablation or significance test | Preserve the gain as observation and the cause as hypothesis; forbid causal and significance claims |
| `duplicated-multilingual-notes` | `inputs/周报.md` and `inputs/weekly-notes.md` both describe the same `2,400`-sample run with macro-F1 `0.731`; English note adds latency `21.6 ms` | Treat the repeated result as one run, retain both provenance entries, and do not report `4,800` samples or two independent replications |

Use an explicit local reporting date of `2026-07-13` in every task so dates are deterministic. Ask for an English report in the first four cases and a Simplified Chinese report in `duplicated-multilingual-notes`.

- [x] **Step 4: Create each manifest from the fixed facts**

For every manifest:

- list all dates, seeds, counts, measurements, thresholds, and permitted derived results under `numbers` or `derived_numbers`;
- mark decision-relevant measurements `required: true`;
- express negative-result identity using `negative_results[].all_of`;
- put unsupported causal/significance language in `forbidden_patterns`;
- use a conflict `max_distance` of `600` characters for `conflicting-results`;
- list only actual fixture paths under `required_sources`;
- forbid `4,800`, `two independent runs`, and `two replications` in the duplicated-notes case.

- [x] **Step 5: Run contract and grader tests on all five fixtures**

Add a test that reads each fixture's `expected-valid-report.md`, grades it, and requires `hard_pass`. Store one hand-authored valid report beside each manifest for grader regression testing; label all five reports `Synthetic example`.

Run:

```powershell
& $python -m unittest tests.test_eval_contract tests.test_grade_report -v
```

Expected: all tests pass.

- [x] **Step 6: Commit**

```powershell
git add evals/research-progress/cases tests/test_eval_contract.py tests/test_grade_report.py
git commit -m "test: add adversarial composition cases"
```

### Task 6: Add The Three End-To-End Fixtures

**Files:**
- Create: `evals/research-progress/cases/scoped-directory-selection/*`
- Create: `evals/research-progress/cases/safe-existing-report-update/*`
- Create: `evals/research-progress/cases/partial-source-failure/*`
- Modify: `tests/test_eval_contract.py`
- Modify: `tests/test_grade_report.py`

- [x] **Step 1: Add the failing complete-inventory test**

Add:

```python
ALL_CASES = COMPOSITION_CASES | {
    "scoped-directory-selection",
    "safe-existing-report-update",
    "partial-source-failure",
}

def test_complete_case_inventory_has_eight_unique_cases(self) -> None:
    root = REPO_ROOT / "evals" / "research-progress" / "cases"
    manifests = [load_manifest(path) for path in iter_case_manifests(root)]
    self.assertEqual({item["case_id"] for item in manifests}, ALL_CASES)
    self.assertEqual(len(manifests), 8)
```

- [x] **Step 2: Run the inventory test and verify RED**

Expected: FAIL with the three missing case IDs.

- [x] **Step 3: Create exact end-to-end fixtures**

| Case | Input tree and facts | Required behavior |
|---|---|---|
| `scoped-directory-selection` | `inputs/results/final.csv`: baseline `0.704`, candidate `0.739`, latency `16.8 ms`; `inputs/notes/decision.md`: success criterion `0.730`; `inputs/cache/debug.txt`: fake score `0.999`; `inputs/generated/old-report.md`: stale score `0.688` | Use only `results/final.csv` and `notes/decision.md`; forbid `0.999`, `0.688`, cache, and generated files |
| `safe-existing-report-update` | Existing `inputs/reports/group-meeting/2026-07-13.md`: baseline `0.702`, old candidate `0.728`, heading `## 导师反馈（手写）`, sentence `保留这个消融实验，不要删除。`; `inputs/new-results.md`: corrected candidate `0.741`, explicitly superseding `0.728` | Preserve manual heading and sentence; retain `0.728` as superseded history; add `0.741` and source; never replace the whole report |
| `partial-source-failure` | `inputs/results/primary.md`: macro-F1 `0.716`; `inputs/results/secondary.csv`: invalid UTF-8 bytes; notes reference absent `inputs/figures/error-map.png` | Report `0.716`, the unreadable CSV, and the missing figure; forbid claims about either missing source's contents |

Write the corrupt CSV as the fixed byte sequence `b"metric,value\nmacro_f1,\xff\xfe\n"` in the fixture-creation step, using a short checked-in binary file. Every readable fixture file and valid report must contain `Synthetic example`.

- [x] **Step 4: Add end-to-end manifests and valid-report tests**

Use:

- `forbidden_sources` for cache/generated paths;
- `preservation_markers` for the manual heading, manual sentence, and old value;
- `skipped_sources` rules requiring the corrupt CSV plus `unreadable`, and the image path plus `missing`;
- forbidden patterns that reject any claimed numeric result attributed to the corrupt CSV or missing image.

Grade each hand-authored valid report and require all gates to pass.

- [x] **Step 5: Run all deterministic tests and commit**

```powershell
& $python -m unittest tests.test_eval_contract tests.test_grade_report -v
& $python -m unittest discover -s tests -v
git add evals/research-progress/cases tests/test_eval_contract.py tests/test_grade_report.py
git commit -m "test: add end-to-end report cases"
```

Expected: eight manifests load and all valid fixture reports pass.

### Task 7: Implement The Isolated Codex Runner With TDD

**Files:**
- Create: `scripts/run_behavior_evals.py`
- Create: `tests/test_run_behavior_evals.py`

- [x] **Step 1: Write failing runner-isolation tests**

Create tests for these public interfaces:

```python
from scripts.run_behavior_evals import (
    RunSpec,
    build_prompt,
    hash_run_environment,
    materialize_git_skill,
    run_with_retry,
)


def test_prompt_names_exact_skill_and_hides_manifest(self) -> None:
    prompt = build_prompt(CASE_MANIFEST, Path("skill-under-test/SKILL.md"))
    self.assertIn("skill-under-test/SKILL.md", prompt)
    self.assertIn("Do not read or search for manifest.json", prompt)
    self.assertNotIn("forbidden_patterns", prompt)

def test_run_layout_is_skill_creator_compatible(self) -> None:
    result = run_with_retry(RUN_SPEC, executor=fake_success_executor)
    self.assertTrue((result.run_dir / "outputs" / "report.md").is_file())
    self.assertTrue((result.run_dir / "grading.json").is_file())
    self.assertTrue((result.run_dir / "timing.json").is_file())
    self.assertTrue((result.run_dir.parent.parent / "eval_metadata.json").is_file())

def test_infrastructure_failure_retries_once(self) -> None:
    executor = FailsThenSucceeds()
    result = run_with_retry(RUN_SPEC, executor=executor)
    self.assertEqual(executor.calls, 2)
    self.assertEqual(result.infrastructure_status, "valid")

def test_second_infrastructure_failure_is_invalid_not_quality_failure(self) -> None:
    result = run_with_retry(RUN_SPEC, executor=always_fails)
    self.assertEqual(result.infrastructure_status, "invalid")
    self.assertIsNone(result.hard_pass)
```

- [x] **Step 2: Run runner tests and verify RED**

Run:

```powershell
& $python -m unittest tests.test_run_behavior_evals -v
```

Expected: import failure because the runner does not exist.

- [x] **Step 3: Implement deterministic Skill materialization**

Implement:

```python
@dataclass(frozen=True)
class RunSpec:
    repo_root: Path
    case_manifest: Path
    workspace: Path
    configuration: str
    run_number: int
    model: str
    timeout_seconds: int
    candidate_skill: Path | None = None
    baseline_ref: str | None = None


def materialize_git_skill(repo_root: Path, ref: str, destination: Path) -> Path:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", ref, "lab-meeting-report"],
        cwd=repo_root, capture_output=True, check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination, filter="data")
    return destination / "lab-meeting-report"
```

For candidate runs, `shutil.copytree` the explicit directory. Reject a destination containing symlinks, an unexpected Skill inventory, or a frontmatter name other than `lab-meeting-report`. Record `hash_tree(skill_path)`.

- [x] **Step 4: Implement the real executor and retry classifier**

Build this command on Windows, substituting `codex` on non-Windows. The variables are resolved to paths inside the current run directory:

```powershell
codex.cmd exec --ephemeral --ignore-user-config --sandbox workspace-write --model gpt-5.6-sol --json --cd $sandbox --output-last-message $lastMessage $prompt
```

Use `subprocess.run(..., timeout=timeout_seconds, capture_output=True, text=True, encoding="utf-8", errors="replace")`. An abnormal exit, timeout, missing expected report, invalid UTF-8 report, or grader exception is infrastructure failure. A readable report with `hard_pass: false` is a quality failure and must not retry.

- [x] **Step 5: Write compatible metadata and outputs**

Use this layout exactly:

```text
$workspace/
  eval-01-clean-multiseed/
    eval_metadata.json
    with_skill/run-1/{outputs/report.md,grading.json,timing.json,run_metadata.json}
    without_skill/run-1/{outputs/report.md,grading.json,timing.json,run_metadata.json}
```

Map candidate to `with_skill` and `v1.1.0` to `without_skill`. `run_metadata.json` must contain case hash, skill hash, prompt hash, runner hash, grader hash, model, CLI version, Git commit, configuration, run number, attempts, exit status, and infrastructure status. Never store auth environment variables.

- [x] **Step 6: Implement the `run` CLI**

Support:

```powershell
$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'
$iteration = Join-Path $evalRoot 'iteration-1'
& $python -m scripts.run_behavior_evals run `
  --repo-root . `
  --cases evals/research-progress/cases `
  --workspace $iteration `
  --configuration without_skill `
  --baseline-ref v1.1.0 `
  --model gpt-5.6-sol `
  --runs 1 `
  --timeout-seconds 900
```

Require exactly one of `--baseline-ref` or `--candidate-skill`. Refuse an existing nonempty configuration/run directory unless `--resume` is supplied; resume only missing or infrastructure-invalid runs.

- [x] **Step 7: Run tests and commit**

```powershell
& $python -m unittest tests.test_run_behavior_evals -v
& $python -m unittest discover -s tests -v
git add scripts/run_behavior_evals.py tests/test_run_behavior_evals.py
git commit -m "feat: run isolated behavior evaluations"
```

### Task 8: Add Benchmark Aggregation And Anonymous Review Preparation

**Files:**
- Modify: `scripts/run_behavior_evals.py`
- Modify: `tests/test_run_behavior_evals.py`

- [x] **Step 1: Write failing aggregation and blinding tests**

Add:

```python
def test_benchmark_uses_exact_skill_creator_fields(self) -> None:
    benchmark = aggregate_workspace(FIXTURE_WORKSPACE, model="gpt-5.6-sol")
    run = benchmark["runs"][0]
    self.assertEqual(set(run), {"eval_id", "eval_name", "configuration", "run_number", "result", "expectations", "notes"})
    self.assertIn("pass_rate", run["result"])

def test_blind_review_contains_one_pair_per_case_run(self) -> None:
    mapping = prepare_blind_review(FIXTURE_WORKSPACE, REVIEW_WORKSPACE, seed=1200)
    self.assertEqual(len(mapping["pairs"]), 2)
    pair = REVIEW_WORKSPACE / "eval-01" / "pair-1" / "outputs"
    self.assertTrue((pair / "source-packet.md").is_file())
    self.assertTrue((pair / "A-report.md").is_file())
    self.assertTrue((pair / "B-report.md").is_file())
    self.assertNotEqual(mapping["pairs"][0]["A"], mapping["pairs"][0]["B"])

def test_structured_feedback_requires_scores_and_preference(self) -> None:
    summary = parse_review_feedback(FEEDBACK_JSON, BLIND_MAP)
    self.assertEqual(summary["pairs_reviewed"], 2)
    self.assertIn(summary["preference_counts"]["candidate"], {0, 1, 2})

def test_semantic_failure_is_written_back_to_reviewed_benchmark(self) -> None:
    reviewed = apply_human_review(BENCHMARK, HUMAN_REVIEW_WITH_CANDIDATE_FAILURE)
    candidate = next(run for run in reviewed["runs"] if run["configuration"] == "with_skill")
    self.assertEqual(candidate["result"]["pass_rate"], 0.0)
    self.assertEqual(candidate["result"]["failed"], candidate["result"]["total"])

def test_release_gate_requires_all_approved_conditions(self) -> None:
    self.assertEqual(check_release_gate(PASSING_BENCHMARK, PASSING_HUMAN_REVIEW), [])
    errors = check_release_gate(BENCHMARK_WITH_ONE_CANDIDATE_FAILURE, PASSING_HUMAN_REVIEW)
    self.assertIn("candidate hard gates: expected 24/24", "\n".join(errors))
```

- [x] **Step 2: Run tests and verify RED**

Expected: failures because aggregation, review preparation, and feedback parsing are undefined.

- [x] **Step 3: Implement benchmark aggregation**

Read every valid `grading.json`, `timing.json`, and `run_metadata.json`. Emit the exact `benchmark.json` shape from skill-creator's `references/schemas.md`, including per-configuration mean, sample standard deviation, min, max, and delta. Write a sibling `benchmark.md` from the same data. Derive `runs_per_configuration` from the workspace and reject unequal counts. For a final release benchmark the value must be `3`. Set:

```json
{
  "skill_name": "lab-meeting-report",
  "executor_model": "gpt-5.6-sol",
  "analyzer_model": "human-blind-review",
  "runs_per_configuration": 3
}
```

Reject aggregation if hashes needed for baseline reuse differ, any run is invalid, or expected case/run combinations are missing.

- [x] **Step 4: Implement anonymous paired review preparation**

For each case and run number, use `random.Random(f"{seed}:{case_id}:{run_number}")` to map candidate/baseline to A/B. Accept an optional separate baseline workspace for one-run candidate development comparisons. Create one viewer run whose `outputs/` contains:

```text
source-packet.md
A-report.md
B-report.md
A-hard-gates.md
B-hard-gates.md
review-format.json
```

`review-format.json` must show this feedback shape:

```json
{
  "semantic_failure": "none",
  "A": {"evidence_clarity": 1, "information_selection": 1, "decision_usefulness": 1, "readability": 1},
  "B": {"evidence_clarity": 1, "information_selection": 1, "decision_usefulness": 1, "readability": 1},
  "preference": "tie",
  "notes": ""
}
```

The allowed score range is `1` through `5`; preference is `A`, `B`, or `tie`; semantic failure is `none`, `A`, `B`, or `both`. Save `blind-map.json` beside, not inside, the review workspace. Also write an anonymized `benchmark.json` inside the review workspace with configurations renamed to A/B and no Skill paths or hashes.

- [x] **Step 5: Implement feedback parsing, unblinding, and semantic-failure writeback**

Parse each skill-creator `feedback.json` review string as JSON, require all fields, map A/B back to candidate/baseline, and calculate per-case medians, global medians, preference counts, and semantic failures. Implement `apply_human_review(benchmark, human_review)` so a semantic failure changes the affected run's hard gate to failed, recalculates summaries, and adds a note identifying the human review finding. When `score-review` writes `benchmark-reviewed.json`, also write `benchmark-reviewed.md` from the reviewed data.

- [x] **Step 6: Implement the release gate**

Implement `check_release_gate(benchmark, human_review) -> list[str]`. Return concrete errors unless:

- all eight cases and three candidate runs per case are present;
- all 24 candidate runs have `pass_rate == 1.0` and zero infrastructure errors;
- candidate semantic failures are empty;
- candidate global median is at least baseline global median;
- no candidate case median is more than one point below baseline;
- at least one case either changes from a baseline hard failure to three candidate passes or wins at least two of three blind preferences with no hard-gate regression.

Add a CLI `check-release` that prints every error and exits `1`, or prints `Release gate passed` and exits `0`.

- [x] **Step 7: Add CLI subcommands and commit**

Support:

```powershell
$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'
$final = Join-Path $evalRoot 'final'
$review = Join-Path $evalRoot 'blind-review'
$blindMap = Join-Path $evalRoot 'blind-map.json'
& $python -m scripts.run_behavior_evals benchmark --workspace $final --output (Join-Path $final 'benchmark.json') --model gpt-5.6-sol
& $python -m scripts.run_behavior_evals prepare-review --workspace $final --review-workspace $review --blind-map $blindMap --seed 1200
& $python -m scripts.run_behavior_evals score-review --feedback (Join-Path $evalRoot 'feedback.json') --blind-map $blindMap --benchmark (Join-Path $final 'benchmark.json') --human-output (Join-Path $final 'human-review.json') --benchmark-output (Join-Path $final 'benchmark-reviewed.json')
& $python -m scripts.run_behavior_evals check-release --benchmark (Join-Path $final 'benchmark-reviewed.json') --human-review (Join-Path $final 'human-review.json')
```

Run all tests, then commit:

```powershell
git add scripts/run_behavior_evals.py tests/test_run_behavior_evals.py
git commit -m "feat: aggregate and blind behavior reviews"
```

### Task 9: Extend Repository Validation For The Evaluation Suite

**Files:**
- Modify: `scripts/validate_repo.py`
- Modify: `tests/test_validate_repo.py`

- [x] **Step 1: Write failing repository-validation tests**

Add:

```python
def test_missing_eval_manifest_is_rejected(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture = Path(temp_dir) / "repo"
        copy_fixture(fixture)
        (fixture / "evals" / "research-progress" / "cases" / "clean-multiseed" / "manifest.json").unlink()
        result = run_validator(fixture)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing evaluation manifest", (result.stdout + result.stderr).lower())

def test_non_synthetic_eval_text_is_rejected(self) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture = Path(temp_dir) / "repo"
        copy_fixture(fixture)
        task = fixture / "evals" / "research-progress" / "cases" / "clean-multiseed" / "task.md"
        task.write_text("Create a report.", encoding="utf-8")
        result = run_validator(fixture)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("synthetic example", (result.stdout + result.stderr).lower())
```

- [x] **Step 2: Run tests and verify RED**

Run:

```powershell
& $python -m unittest tests.test_validate_repo -v
```

Expected: both new tests fail because the current validator ignores `evals/`.

- [x] **Step 3: Add exact evaluation inventory checks**

Add:

```python
EVAL_CASE_IDS = {
    "clean-multiseed", "conflicting-results", "buried-negative-result",
    "missing-evidence-causal-lure", "duplicated-multilingual-notes",
    "scoped-directory-selection", "safe-existing-report-update",
    "partial-source-failure",
}
EVAL_REQUIRED_CODE = {
    Path("scripts/eval_contract.py"),
    Path("scripts/grade_report.py"),
    Path("scripts/run_behavior_evals.py"),
    Path("tests/test_eval_contract.py"),
    Path("tests/test_grade_report.py"),
    Path("tests/test_run_behavior_evals.py"),
    Path("evals/research-progress/schema/manifest.schema.json"),
}
```

For each case require `manifest.json`, `task.md`, `inputs/`, and `expected-valid-report.md`. Load manifests with `scripts.eval_contract.load_manifest`. Require `Synthetic example` in every readable fixture `.md`, `.txt`, `.csv`, and expected report. Permit the intentionally corrupt CSV only in `partial-source-failure` and verify its exact SHA-256.

- [x] **Step 4: Run the complete local gate and commit**

```powershell
$env:PYTHONUTF8 = '1'
$quickValidate = Join-Path $env:USERPROFILE '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
& $python -m unittest discover -s tests -v
& $python scripts/validate_repo.py .
& $python $quickValidate lab-meeting-report
git add scripts/validate_repo.py tests/test_validate_repo.py
git commit -m "test: validate behavior evaluation assets"
```

Expected: all tests and validators pass.

### Task 10: Run And Review The Frozen v1.1 Baseline

**Files:**
- Create after review: `benchmarks/v1.1-v1.2/baseline-benchmark.json`
- Create after review: `benchmarks/v1.1-v1.2/baseline-analysis.md`
- Create after review: `benchmarks/v1.1-v1.2/representative-outputs/v1.1/*`
- External workspace: `$evalRoot\baseline-final`, where `$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'`

- [x] **Step 1: Verify model runner preconditions**

Run:

```powershell
codex --version
git rev-list -n 1 v1.1.0
& $python -m scripts.run_behavior_evals --help
```

Expected: Codex CLI `0.144.0-alpha.4`, tag commit `76a800c3fdd843b2513ea7270086a05ff7f5c47e`, and runner subcommands displayed.

- [x] **Step 2: Run all eight baseline cases three times**

Run:

```powershell
$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'
$workspace = Join-Path $evalRoot 'baseline-final'
& $python -m scripts.run_behavior_evals run `
  --repo-root . `
  --cases evals/research-progress/cases `
  --workspace $workspace `
  --configuration without_skill `
  --baseline-ref v1.1.0 `
  --model gpt-5.6-sol `
  --runs 3 `
  --timeout-seconds 900
```

Expected: `24 valid runs`; quality failures are allowed, infrastructure-invalid runs are not. If a run is invalid after its automatic retry, stop and repair the runner or environment before proceeding.

- [x] **Step 3: Aggregate baseline results**

```powershell
& $python -m scripts.run_behavior_evals benchmark `
  --workspace $workspace `
  --output "$workspace\benchmark.json" `
  --model gpt-5.6-sol
```

Expected: benchmark contains eight eval IDs and 24 `without_skill` runs.

- [x] **Step 4: Generate the review page before analyzing outputs**

```powershell
$viewer = Join-Path $env:USERPROFILE '.codex\skills\skill-creator\eval-viewer\generate_review.py'
& $python $viewer $workspace `
  --skill-name 'lab-meeting-report v1.1 baseline' `
  --benchmark "$workspace\benchmark.json" `
  --static "$workspace\baseline-review.html"
```

Open `baseline-review.html`, tell the user the hard-gate results are provisional until semantic review, and pause. Do not inspect and interpret the report quality before the user has reviewed the outputs.

- [x] **Step 5: Run inline semantic review and classify baseline failures**

The user explicitly declined manual review. Read all machine failures, representative reports, and relevant transcripts inline. Record that the review is non-independent, then classify each failure into exactly one or more of:

```text
E1 evidence inventory/provenance
E2 source versus derived numeric handling
E3 negative-result/conflict retention
E4 existing-report preservation
E5 post-draft unsupported-claim audit
P1 duplicate-note non-independence
P2 source assertion versus causal evidence
```

Any failure outside this matrix stops execution and requires a design addendum; do not improvise a prompt change.

- [x] **Step 6: Commit inspectable baseline evidence**

Copy `benchmark.json` to `benchmarks/v1.1-v1.2/baseline-benchmark.json`. Write `baseline-analysis.md` with case/run IDs, hard failures, semantic findings, root-cause codes, and limitations. Copy run 1 report for each case mechanically into `representative-outputs/v1.1/`.

If all 24 baseline runs pass both machine and semantic hard gates, stop before Task 11 and strengthen the adversarial design through a reviewed design addendum. Do not change the Skill merely to create a version difference. If the strengthened suite still produces no defensible difference, commit the evaluation infrastructure and bounded baseline analysis, complete the branch through the user's chosen integration path, and do not execute the `v1.2.0` release steps.

Otherwise run:

```powershell
git add benchmarks/v1.1-v1.2
git commit -m "test: record v1.1 behavior baseline"
```

### Task 11: Select And Apply The Minimum Evidence-Supported Skill Delta

**Files:**
- Create: `benchmarks/v1.1-v1.2/candidate-selection.json`
- Modify conditionally: `lab-meeting-report/SKILL.md`
- Modify conditionally: `lab-meeting-report/references/progress-report.md`

- [x] **Step 1: Write the candidate-selection record**

Create `candidate-selection.json` with `baseline_commit`, `baseline_benchmark_sha256`, `selected_blocks`, and `evidence`. Every selected block must cite at least one failed case/run and one expectation or human semantic finding. Reject block IDs outside `E1` through `E5`, `P1`, and `P2`.

- [x] **Step 2: Apply only selected SKILL.md blocks**

Insert selected text at the named location exactly.

After `### 2. Build an evidence inventory` evidence rules:

```markdown
<!-- E1 -->
Before drafting, build an internal evidence ledger for each decision-relevant claim. Record its source path, exact value and unit when numeric, evidence type (`source fact`, `derived calculation`, `interpretation`, or `hypothesis`), conflicts, and linked negative evidence. Use the ledger for control; do not add it to the final report unless it improves traceability.
```

After E1, when E2 is selected:

```markdown
<!-- E2 -->
Copy experimental numbers and units exactly from their sources. Introduce a derived number only when every operand is supplied, verify the calculation, and label it as calculated rather than observed. Never invent a numeric estimate to fill a missing result, uncertainty, threshold, or significance value.
```

After E1, when E3 is selected:

```markdown
<!-- E3 -->
Create an internal must-retain list for failed experiments, negative results, blockers, uncertainty, and conflicting source values. Check every item against the draft; do not let repeated positive evidence or a smoother narrative displace it.
```

At the start of `### 5. Write safely to disk`, when E4 is selected:

```markdown
<!-- E4 -->
Before editing an existing report, inventory manual headings, unrecognized content, earlier evidence, and claims not explicitly superseded. Treat that inventory as protected content. Record supersession with both the earlier and replacement sources instead of erasing history.
```

At the start of `### 6. Run the quality gate`, when E5 is selected:

```markdown
<!-- E5 -->
Run a claim audit before completion: match every experimental number to a source fact or verified calculation, confirm every must-retain negative/conflict item is present, and relabel or remove causal, significance, bibliographic, or mechanism claims not supported by the supplied evidence.
```

The HTML comments are stable block identifiers for tests and future removal; they do not appear in generated reports.

- [x] **Step 3: Apply selected progress-template rules**

Append P1 or P2 only when selected:

```markdown
<!-- P1 -->
- Treat duplicated or translated notes about the same run as repeated provenance, not independent replication or additional sample count.

<!-- P2 -->
- A source author's causal wording is still an attributed claim when no isolating test is supplied; preserve it as an interpretation or hypothesis, not a verified mechanism.
```

- [x] **Step 4: Add selection consistency validation**

Extend `scripts/validate_repo.py` and `tests/test_validate_repo.py` so every selected ID requires its exact marker from `<!-- E1 -->` through `<!-- P2 -->`, and no unselected marker may appear. Add a test that removes a selected block and requires validation failure.

- [x] **Step 5: Run local validation and commit**

```powershell
$env:PYTHONUTF8 = '1'
$quickValidate = Join-Path $env:USERPROFILE '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
& $python -m unittest discover -s tests -v
& $python scripts/validate_repo.py .
& $python $quickValidate lab-meeting-report
git add benchmarks/v1.1-v1.2/candidate-selection.json lab-meeting-report scripts/validate_repo.py tests/test_validate_repo.py
git commit -m "feat: strengthen evidence fidelity controls"
```

### Task 12: Run Candidate Development Iterations

**Files:**
- External workspaces: `$evalRoot\candidate-iteration-*`, where `$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'`
- Modify only if selected: files and blocks from Task 11
- Create/update: `benchmarks/v1.1-v1.2/iteration-history.json`

- [x] **Step 1: Run candidate iteration 1 once per case**

```powershell
$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'
$candidate = Join-Path $evalRoot 'candidate-iteration-1'
& $python -m scripts.run_behavior_evals run `
  --repo-root . `
  --cases evals/research-progress/cases `
  --workspace $candidate `
  --configuration with_skill `
  --candidate-skill lab-meeting-report `
  --model gpt-5.6-sol `
  --runs 1 `
  --timeout-seconds 900
```

- [x] **Step 2: Replace manual viewer review with inline semantic review**

After each iteration, read every failed report against its inputs and inspect every hard-passing report for deleted decision-relevant evidence. Record design corrections in numbered addenda. Do not create or request manual feedback artifacts.

- [x] **Step 3: Apply only deterministic escalation rules**

If a selected category still fails, add blocks in this order without rewriting existing text:

| Failure | Escalation |
|---|---|
| E2 numeric failure | add E1 if absent, then E5 |
| E3 negative/conflict failure | add E1 if absent, then E5 |
| E4 preservation failure | add E1 if absent, then E5 |
| E5 unsupported claim | add E1 if absent, then P2 for causal wording |
| P1 duplicate counting | add E1, then E5 |
| P2 causal promotion | add E5, then E1 |

Update `candidate-selection.json` with the failed case/run that justifies each added block. Run validators and commit each iteration separately using exactly one applicable message: `fix: address numeric evaluation failures`, `fix: address conflict evaluation failures`, `fix: address preservation evaluation failures`, `fix: address causal evaluation failures`, or `fix: address duplicate-note evaluation failures`.

If all relevant blocks are present and the failure remains, or a new failure category appears, stop and write a design addendum. Maximum: three candidate iterations.

- [x] **Step 4: Record accepted development history**

Write `iteration-history.json` with version, parent commit, selected block IDs, per-case hard-pass result, semantic-review hash, and outcome `won`, `lost`, or `tie`. Proceed only when the current candidate is `8/8` on deterministic hard gates and semantic review found no unsupported critical claim.

- [ ] **Step 5: Commit the iteration record**

```powershell
git add benchmarks/v1.1-v1.2/iteration-history.json
git commit -m "test: record candidate evaluation history"
```

### Task 13: Run The Final Three-Repeat Benchmark And Semantic Review

**Files:**
- External workspace: `$evalRoot\final`
- Create: `benchmarks/v1.1-v1.2/benchmark.json`
- Create: `benchmarks/v1.1-v1.2/benchmark.md`
- Create: `benchmarks/v1.1-v1.2/semantic-review-final.json`

- [ ] **Step 1: Reuse or rerun the frozen baseline**

Compare skill, model, Codex CLI, runner, prompt, input, and provider hashes between `baseline-final` and the current final environment. Grader-only and hidden-manifest semantic-equivalence corrections may regrade the unchanged raw baseline reports when documented by a tested design addendum; any change visible to the generation process requires rerunning all 24 baseline runs.

- [ ] **Step 2: Run 24 candidate evaluations**

```powershell
$evalRoot = Join-Path $env:TEMP 'lab-meeting-report-v1.2-evals'
$final = Join-Path $evalRoot 'final'
& $python -m scripts.run_behavior_evals run `
  --repo-root . `
  --cases evals/research-progress/cases `
  --workspace $final `
  --configuration with_skill `
  --candidate-skill lab-meeting-report `
  --model gpt-5.6-sol `
  --runs 3 `
  --timeout-seconds 900
```

Expected: 24 valid candidate runs; all deterministic hard gates must pass before semantic review.

- [ ] **Step 3: Run the final inline claim-level semantic audit**

Read every candidate report against its supplied inputs. Write `semantic-review-final.json` with reviewer kind `codex-inline-self-review`, the non-independent limitation, one finding per run, and a hard failure for every unsupported critical claim.

- [ ] **Step 4: Enforce the non-human release gate**

`check-release` must exit nonzero unless all 24 candidate runs hard-pass, no run is invalid, the semantic review records zero unsupported critical claims, and at least one case has a baseline hard failure with all three candidate runs passing. No blinded preference or soft-score claim is made.

- [ ] **Step 5: Commit final evidence**

Copy the final benchmark as `benchmarks/v1.1-v1.2/benchmark.json` and `benchmark.md`, and copy `semantic-review-final.json`. Mechanically copy run 1 for each candidate case to `representative-outputs/v1.2/`. Run `check-release` against the committed paths, then:

```powershell
git add benchmarks/v1.1-v1.2
git commit -m "test: publish v1.2 behavior benchmark"
```

### Task 14: Document Results, Synchronize The Installed Skill, And Run Local Release Gates

**Files:**
- Modify: `README.md`
- Modify: `scripts/validate_repo.py`
- Modify: `tests/test_validate_repo.py`
- Modify when selected blocks exist: `$installedSkill\SKILL.md`, where `$installedSkill = Join-Path $env:USERPROFILE '.codex\skills\lab-meeting-report'`
- Modify when P1/P2 exists: `$installedSkill\references\progress-report.md`

- [ ] **Step 1: Add a bounded README evaluation section**

Add this English text after `## Evidence And Safety Rules`:

```markdown
## Behavioral Evaluation

The repository includes eight public synthetic research-progress cases covering numeric fidelity, conflicting sources, negative results, unsupported causal language, duplicate notes, scoped directory reading, safe report updates, and partial source failures. Deterministic hard gates and blinded human review compare the current Skill with `v1.1.0`.

See the [evaluation design](docs/superpowers/specs/2026-07-13-lab-meeting-report-v1.2-quality-evaluation-design.md), [case corpus](evals/research-progress/cases), and [versioned benchmark](benchmarks/v1.1-v1.2/benchmark.md). Results apply only to these synthetic research-progress cases and do not establish universal hallucination prevention.
```

Add a concise equivalent under `### 可靠性原则`, preserving the same scope limitation.

- [ ] **Step 2: Require final benchmark assets in repository validation**

Require `benchmark.json`, `benchmark.md`, `human-review.json`, `candidate-selection.json`, `iteration-history.json`, eight v1.1 representative reports, and eight v1.2 representative reports. Validate JSON structure, model `gpt-5.6-sol`, eight eval IDs, three runs per configuration, and no candidate release-gate failure.

Add a regression test that removes `benchmark.json` and one that changes a candidate hard pass to false; both must fail repository validation.

- [ ] **Step 3: Synchronize only changed installed Skill files**

Copy selected changed package files from the repository into `$installedSkill = Join-Path $env:USERPROFILE '.codex\skills\lab-meeting-report'`. Compare SHA-256 for all six package files and require exact equality. Do not copy evaluation or benchmark files into the installed Skill.

- [ ] **Step 4: Run the complete fresh local gate**

Run:

```powershell
$env:PYTHONUTF8 = '1'
$quickValidate = Join-Path $env:USERPROFILE '.codex\skills\.system\skill-creator\scripts\quick_validate.py'
$installedSkill = Join-Path $env:USERPROFILE '.codex\skills\lab-meeting-report'
& $python -m unittest discover -s tests -v
& $python scripts/validate_repo.py .
& $python $quickValidate lab-meeting-report
& $python $quickValidate $installedSkill
& $python -m scripts.run_behavior_evals check-release --benchmark benchmarks/v1.1-v1.2/benchmark.json --human-review benchmarks/v1.1-v1.2/human-review.json
git diff --check
```

Also parse every repository YAML/JSON file, verify all fixture labels, scan for credentials, Lark IDs, absolute user paths, stale names, scaffold markers, and real DOI/author/venue claims.

- [ ] **Step 5: Commit the release candidate**

Stage only approved v1.2 files, run staged-content scans, and commit:

```powershell
git add README.md scripts tests evals benchmarks lab-meeting-report
git commit -m "feat: add evidence-fidelity evaluation"
```

Use `superpowers:requesting-code-review` and resolve all blocking findings before the commit is treated as releasable.

### Task 15: Push, Verify CI, Publish v1.2.0, And Re-Clone

**Files:**
- Remote modify: `LikC1606/lab-meeting-report-skill`
- Temporary clone: `$verifyPath = Join-Path $env:TEMP 'lab-meeting-report-skill-v1.2-verify'`

- [ ] **Step 1: Complete the branch according to the user's selected integration option**

Invoke `superpowers:finishing-a-development-branch`. Do not force-push. The release steps below require the accepted commits to be on `main`; if the user chooses a PR, wait until it is merged.

- [ ] **Step 2: Verify the remote commit and workflow**

Push `main` without force, require `origin/main == HEAD`, locate the `Validate skill` run for that exact SHA, and wait for conclusion `success`.

- [ ] **Step 3: Create the public release**

Create `v1.2.0` only after CI succeeds. Release notes must list the synthetic corpus, deterministic hard gates, blind review, selected Skill controls, exact model/CLI metadata, benchmark link, and limitations. Do not claim universal hallucination prevention, adoption, or performance outside the eight cases.

- [ ] **Step 4: Clone the release tag and independently validate it**

Require the target path not to exist, then run:

```powershell
$verifyPath = Join-Path $env:TEMP 'lab-meeting-report-skill-v1.2-verify'
git clone --branch v1.2.0 --depth 1 https://github.com/LikC1606/lab-meeting-report-skill.git $verifyPath
```

Inside the clone, run unit tests, repository validation, official Skill validation, and `check-release`. Compare all Git tree blob IDs with the source release commit.

- [ ] **Step 5: Remove only the verified temporary clone**

Resolve `$verifyPath`, require its parent to equal `[System.IO.Path]::GetFullPath($env:TEMP)`, require its leaf to be `lab-meeting-report-skill-v1.2-verify`, verify `.git` exists, clear only read-only pack attributes, and remove only that directory.

- [ ] **Step 6: Report evidence and remaining distribution work**

Return repository, CI run, release, corpus, benchmark, representative outputs, Discussions, and install links. State whether `skills.sh` has indexed the Skill. Do not submit external directory pull requests or community posts without separate user authorization.
