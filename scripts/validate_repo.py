from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import yaml

try:
    from scripts.eval_contract import ContractError, load_manifest
    from scripts.grade_report import extract_numbers
except ModuleNotFoundError:
    from eval_contract import ContractError, load_manifest
    from grade_report import extract_numbers


SKILL_NAME = "lab-meeting-report"
SKILL_DIR = Path(SKILL_NAME)
EXPECTED_SKILL_FILES = {
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/lark-integration.md"),
    Path("references/meeting-lifecycle.md"),
    Path("references/mixed-report.md"),
    Path("references/paper-review.md"),
    Path("references/progress-report.md"),
}
EXAMPLE_FILES = {
    Path("examples/research-progress/input-notes.md"),
    Path("examples/research-progress/report.md"),
    Path("examples/journal-club/input-notes.md"),
    Path("examples/journal-club/report.md"),
    Path("examples/mixed/input-notes.md"),
    Path("examples/mixed/report.md"),
}
EXAMPLE_SOURCE_FILES = {
    Path("examples/research-progress/results/baseline.csv"),
    Path("examples/research-progress/results/retrieval_reranker.csv"),
    Path("examples/research-progress/results/paraphrase_all_classes.csv"),
    Path("examples/journal-club/papers/synthetic-retrieval-notes.md"),
    Path("examples/mixed/results/current_experiment.csv"),
    Path("examples/mixed/papers/synthetic-balanced-retrieval.md"),
}
EXAMPLE_NUMERIC_SOURCES = {
    Path("examples/research-progress/report.md"): {
        Path("examples/research-progress/input-notes.md"),
        Path("examples/research-progress/results/baseline.csv"),
        Path("examples/research-progress/results/retrieval_reranker.csv"),
        Path("examples/research-progress/results/paraphrase_all_classes.csv"),
    },
    Path("examples/journal-club/report.md"): {
        Path("examples/journal-club/input-notes.md"),
        Path("examples/journal-club/papers/synthetic-retrieval-notes.md"),
    },
    Path("examples/mixed/report.md"): {
        Path("examples/mixed/input-notes.md"),
        Path("examples/mixed/results/current_experiment.csv"),
        Path("examples/mixed/papers/synthetic-balanced-retrieval.md"),
    },
}
COMMUNITY_FILES = {
    Path("CODE_OF_CONDUCT.md"),
    Path("CONTRIBUTING.md"),
    Path("SECURITY.md"),
    Path("SUPPORT.md"),
    Path(".github/PULL_REQUEST_TEMPLATE.md"),
}
README_TERMS = {
    "LikC1606/lab-meeting-report-skill@lab-meeting-report",
    "README.zh-CN.md",
    "https://skills.sh/LikC1606/lab-meeting-report-skill",
    "lab meeting report",
    "research progress report",
    "journal club",
    "Feishu",
    "Lark",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "## 中文说明",
}
LANGUAGE_TERMS = {
    "follow an explicit language request",
    "match the language of the user's request",
    "use English only when",
    "Translate headings and labels",
}
TEXT_SUFFIXES = {"", ".md", ".py", ".yaml", ".yml", ".txt"}
BLOCKED_PATTERNS = {
    "GitHub token": re.compile(r"\bgh[opsu]_[A-Za-z0-9]{20,}\b"),
    "API key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "Lark user ID": re.compile(r"\bou_[a-z0-9]{20,}\b"),
    "Lark app ID": re.compile(r"\bcli_[a-z0-9]{12,}\b"),
    "live Lark document URL": re.compile(
        r"https?://[^\s)]+\.(?:feishu|larksuite)\.cn/docx/[A-Za-z0-9]{10,}",
        re.IGNORECASE,
    ),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
}
ENCODING_GUARD_TERM = "Treat text encoding as protected content."
UNSUPPORTED_EXPLANATION_GUARD_TERM = (
    "Do not invent or brainstorm alternative causal explanations"
)
UNSUPPLIED_EXPECTATION_GUARD_TERM = (
    "Do not infer an experiment's intended outcome"
)
SPARSE_REPORT_GUARD_TERM = (
    "For sparse source material, target 1-2 rendered pages."
)
INPUT_CONTRACT_GUARD_TERM = (
    "Accept a natural-language request without forcing the user to fill a form."
)
OUTPUT_CONTRACT_GUARD_TERM = (
    "Make the first screen decision-useful: summarize the current state"
)
MISSING_SOURCE_GUARD_TERM = (
    "If no usable source or explicit source scope is available"
)
DECISION_SNAPSHOT_GUARD_TERM = (
    "begin the report body with a localized decision snapshot"
)
MEETING_LIFECYCLE_GUARD_TERMS = {
    "stage (`before`, `after`, or `both`)",
    "place `上次行动复盘` or its localized equivalent immediately after the snapshot",
    "Run an evidence-completeness check for every decision-critical empirical result",
    "add `会议决定与行动记录` using only decisions captured in the supplied meeting notes",
    "one message per slide, its evidence source, the spoken interpretation, and the discussion question",
}
DECISION_SNAPSHOT_FIELDS = {
    "**当前状态：**",
    "**需要决策：**",
    "**最强证据：**",
    "**下一步：**",
}
EXAMPLE_DECISION_SNAPSHOT_FIELDS = {
    "## Decision Snapshot",
    "**Current status:**",
    "**Decision needed:**",
    "**Strongest evidence:**",
    "**Next action:**",
}
LIFECYCLE_TEMPLATE_TERMS = {
    "上次行动复盘",
    "证据完整度与缺口",
    "当前阻塞与决策包",
    "会议决定与行动记录",
    "负责人",
    "截止时间",
}
MEETING_LIFECYCLE_REFERENCE_TERMS = {
    "| `before` |",
    "| `after` |",
    "| `both` |",
    "## Continuity inventory",
    "## Decision package",
    "## Post-meeting record",
    "## Evidence completeness",
    "## Presenter outline",
}
EXAMPLE_LIFECYCLE_TERMS = {
    "## Previous Action Review",
    "## Evidence Completeness And Gaps",
    "## Blocker And Decision Package",
    "| Action | Owner | Due date |",
}
DEFAULT_PRIORITY_PATTERN = re.compile(r"\|\s*P[0-9]+\s*\|")
PREVIEW_SOURCE = Path("scripts/render_preview.py")
PREVIEW_REQUIRED_TERMS = {
    "Expected outcome: not supplied",
    "The sources do not provide a priority rule.",
    "From scattered notes to an evidence-grounded decision",
}
PREVIEW_STALE_TERMS = {
    "Complete 75 manual reviews",
    "P0",
    "P1",
}
EVAL_CASE_IDS = {
    "clean-multiseed",
    "conflicting-results",
    "buried-negative-result",
    "missing-evidence-causal-lure",
    "duplicated-multilingual-notes",
    "scoped-directory-selection",
    "safe-existing-report-update",
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
CORRUPT_CSV = Path(
    "evals/research-progress/cases/partial-source-failure/"
    "inputs/results/secondary.csv"
)
CORRUPT_CSV_SHA256 = (
    "c90d4efb69ec99c28d449dbfb3e53a5aba0eb40b0ea686c3e58378067a9a5908"
)
EVAL_TEXT_SUFFIXES = {".md", ".txt", ".csv"}
CANDIDATE_SELECTION = Path(
    "benchmarks/v1.1-v1.2/candidate-selection.json"
)
CANDIDATE_BLOCKS = {
    "E1": (Path("lab-meeting-report/SKILL.md"), "<!-- E1 -->"),
    "E2": (Path("lab-meeting-report/SKILL.md"), "<!-- E2 -->"),
    "E3": (Path("lab-meeting-report/SKILL.md"), "<!-- E3 -->"),
    "E4": (Path("lab-meeting-report/SKILL.md"), "<!-- E4 -->"),
    "E5": (Path("lab-meeting-report/SKILL.md"), "<!-- E5 -->"),
    "P1": (
        Path("lab-meeting-report/references/progress-report.md"),
        "<!-- P1 -->",
    ),
    "P2": (
        Path("lab-meeting-report/references/progress-report.md"),
        "<!-- P2 -->",
    ),
}
FINAL_BENCHMARK_DIR = Path("benchmarks/v1.1-v1.2")
FINAL_BENCHMARK_FILES = {
    Path("benchmark.json"),
    Path("benchmark.md"),
    Path("semantic-review-final.json"),
}


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def load_yaml(path: Path, errors: list[str]) -> object | None:
    try:
        return yaml.safe_load(read_utf8(path))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"Invalid UTF-8 or YAML in {path}: {exc}")
        return None


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, object] | None:
    try:
        content = read_utf8(path)
    except UnicodeDecodeError as exc:
        errors.append(f"Invalid UTF-8 in {path}: {exc}")
        return None

    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", content, re.DOTALL)
    if not match:
        errors.append(f"Missing or malformed YAML frontmatter in {path}")
        return None

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.append(f"Invalid frontmatter YAML in {path}: {exc}")
        return None

    if not isinstance(data, dict):
        errors.append(f"Frontmatter must be a mapping in {path}")
        return None
    return data


def repository_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts or "tmp" in relative.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name == ".gitignore":
            files.append(path)
    return files


def validate_png(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing preview PNG: {path.relative_to(path.parents[1])}")
        return
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        errors.append(f"Invalid PNG signature: {path}")
        return
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1440, 960):
        errors.append(
            f"Unexpected preview dimensions: {width}x{height}; expected 1440x960"
        )


def validate_preview_source(root: Path, errors: list[str]) -> None:
    path = root / PREVIEW_SOURCE
    if not path.is_file():
        errors.append(f"Missing preview source: {PREVIEW_SOURCE.as_posix()}")
        return
    text = read_utf8(path)
    for term in sorted(PREVIEW_REQUIRED_TERMS):
        if term not in text:
            errors.append(f"Preview source missing current evidence guard: {term}")
    for term in sorted(PREVIEW_STALE_TERMS):
        if term in text:
            errors.append(f"Preview source contains stale generated claim: {term}")


def validate_example_numbers(root: Path, errors: list[str]) -> None:
    metadata_values = {
        value for _, value in extract_numbers("2026 7 12")
    }
    for report_relative, source_relatives in EXAMPLE_NUMERIC_SOURCES.items():
        report_path = root / report_relative
        source_paths = [root / relative for relative in source_relatives]
        if not report_path.is_file() or any(
            not path.is_file() for path in source_paths
        ):
            continue
        allowed = set(metadata_values)
        for source_path in source_paths:
            allowed.update(
                value
                for _, value in extract_numbers(read_utf8(source_path))
            )
        unexpected = [
            token
            for token, value in extract_numbers(read_utf8(report_path))
            if value not in allowed
        ]
        if unexpected:
            errors.append(
                "Example report contains unexpected numeric values: "
                f"{report_relative.as_posix()}: {', '.join(unexpected)}"
            )


def validate_evaluation_assets(root: Path, errors: list[str]) -> None:
    for relative in sorted(EVAL_REQUIRED_CODE):
        if not (root / relative).is_file():
            errors.append(f"Missing evaluation code: {relative.as_posix()}")

    cases_root = root / "evals" / "research-progress" / "cases"
    if not cases_root.is_dir():
        errors.append("Missing evaluation cases directory")
        return
    actual_cases = {
        path.name for path in cases_root.iterdir() if path.is_dir()
    }
    for case_id in sorted(EVAL_CASE_IDS - actual_cases):
        errors.append(f"Missing evaluation case: {case_id}")
    for case_id in sorted(actual_cases - EVAL_CASE_IDS):
        errors.append(f"Unexpected evaluation case: {case_id}")

    for case_id in sorted(EVAL_CASE_IDS & actual_cases):
        case_root = cases_root / case_id
        manifest_path = case_root / "manifest.json"
        if not manifest_path.is_file():
            errors.append(
                f"Missing evaluation manifest: {case_id}/manifest.json"
            )
        else:
            try:
                load_manifest(manifest_path)
            except ContractError as exc:
                errors.append(f"Invalid evaluation manifest {case_id}: {exc}")
        for name, kind in (
            ("task.md", "file"),
            ("inputs", "directory"),
            ("expected-valid-report.md", "file"),
        ):
            path = case_root / name
            exists = path.is_file() if kind == "file" else path.is_dir()
            if not exists:
                errors.append(
                    f"Missing evaluation {kind}: {case_id}/{name}"
                )

        for path in sorted(case_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in EVAL_TEXT_SUFFIXES:
                continue
            relative = path.relative_to(root)
            if relative == CORRUPT_CSV:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != CORRUPT_CSV_SHA256:
                    errors.append(
                        "Corrupt CSV hash mismatch: "
                        f"{relative.as_posix()} expected "
                        f"{CORRUPT_CSV_SHA256}, got {digest}"
                    )
                continue
            try:
                text = read_utf8(path)
            except UnicodeDecodeError as exc:
                errors.append(
                    f"Invalid UTF-8 evaluation fixture {relative.as_posix()}: {exc}"
                )
                continue
            if "Synthetic example" not in text:
                errors.append(
                    "Evaluation fixture lacks Synthetic example label: "
                    f"{relative.as_posix()}"
                )

    corrupt_path = root / CORRUPT_CSV
    if not corrupt_path.is_file():
        errors.append(f"Missing corrupt CSV fixture: {CORRUPT_CSV.as_posix()}")


def validate_candidate_selection(root: Path, errors: list[str]) -> None:
    selection_path = root / CANDIDATE_SELECTION
    if not selection_path.is_file():
        return

    try:
        selection = json.loads(read_utf8(selection_path))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid candidate selection: {exc}")
        return

    selected_raw = (
        selection.get("selected_blocks")
        if isinstance(selection, dict)
        else None
    )
    if not isinstance(selected_raw, list) or not all(
        isinstance(block_id, str) for block_id in selected_raw
    ):
        errors.append("Candidate selection selected_blocks must be a string array")
        return

    selected = set(selected_raw)
    for block_id in sorted(selected - CANDIDATE_BLOCKS.keys()):
        errors.append(f"Unknown selected block {block_id}")

    for block_id, (relative, marker) in CANDIDATE_BLOCKS.items():
        path = root / relative
        count = read_utf8(path).count(marker) if path.is_file() else 0
        if block_id in selected and count == 0:
            errors.append(f"Selected block {block_id} is missing")
        elif block_id in selected and count > 1:
            errors.append(f"Selected block {block_id} appears more than once")
        elif block_id not in selected and count:
            errors.append(f"Unselected block {block_id} is present")


def load_json_object(
    path: Path, label: str, errors: list[str]
) -> dict[str, object] | None:
    try:
        value = json.loads(read_utf8(path))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid {label}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"Invalid {label}: expected a JSON object")
        return None
    return value


def validate_final_benchmark(root: Path, errors: list[str]) -> None:
    benchmark_root = root / FINAL_BENCHMARK_DIR
    for relative in sorted(FINAL_BENCHMARK_FILES):
        if not (benchmark_root / relative).is_file():
            errors.append(
                "Missing final benchmark asset: "
                f"{(FINAL_BENCHMARK_DIR / relative).as_posix()}"
            )

    benchmark_path = benchmark_root / "benchmark.json"
    if not benchmark_path.is_file():
        errors.append("Missing final benchmark: benchmark.json")
        return
    benchmark = load_json_object(
        benchmark_path, "final benchmark", errors
    )
    if benchmark is None:
        return

    metadata = benchmark.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("Final benchmark metadata must be an object")
    else:
        if metadata.get("executor_model") != "gpt-5.6-sol":
            errors.append("Final benchmark executor model must be gpt-5.6-sol")
        if metadata.get("analyzer_model") != "codex-inline-self-review":
            errors.append(
                "Final benchmark analyzer model must be "
                "codex-inline-self-review"
            )
        if metadata.get("evals_run") != list(range(1, 9)):
            errors.append("Final benchmark must contain eval IDs 1 through 8")
        if metadata.get("runs_per_configuration") != 3:
            errors.append(
                "Final benchmark must contain three runs per configuration"
            )

    runs = benchmark.get("runs")
    if not isinstance(runs, list):
        errors.append("Final benchmark runs must be an array")
        runs = []
    candidate = [
        run
        for run in runs
        if isinstance(run, dict) and run.get("configuration") == "with_skill"
    ]
    baseline = [
        run
        for run in runs
        if isinstance(run, dict)
        and run.get("configuration") == "without_skill"
    ]
    if len(candidate) != 24 or len(baseline) != 24 or len(runs) != 48:
        errors.append(
            "Final benchmark must contain 24 candidate and 24 baseline runs"
        )
    for run in candidate:
        result = run.get("result")
        passed = (
            isinstance(result, dict)
            and result.get("pass_rate") == 1.0
            and result.get("failed") == 0
        )
        if not passed:
            errors.append(
                "Candidate benchmark run failed: "
                f"{run.get('eval_name')}/run-{run.get('run_number')}"
            )
    if baseline and all(
        isinstance(run.get("result"), dict)
        and run["result"].get("pass_rate") == 1.0
        and run["result"].get("failed") == 0
        for run in baseline
    ):
        errors.append("Final benchmark does not demonstrate baseline failure")

    markdown_path = benchmark_root / "benchmark.md"
    if markdown_path.is_file() and (
        "Analyzer: `codex-inline-self-review`"
        not in read_utf8(markdown_path)
    ):
        errors.append("Final benchmark Markdown lacks Codex self-review label")

    review_path = benchmark_root / "semantic-review-final.json"
    if review_path.is_file():
        review = load_json_object(review_path, "final semantic review", errors)
        if review is not None:
            reviewer = review.get("reviewer")
            if not isinstance(reviewer, dict) or reviewer.get("kind") != (
                "codex-inline-self-review"
            ):
                errors.append("Final semantic review has an invalid reviewer")
            elif (
                reviewer.get("independent") is not False
                or reviewer.get("manual_user_review") is not False
            ):
                errors.append(
                    "Final semantic review must disclose non-independent "
                    "Codex self-review"
                )
            reports = review.get("reports")
            if not isinstance(reports, list) or len(reports) != 24:
                errors.append("Final semantic review must contain 24 reports")
            else:
                keys = {
                    (item.get("case_id"), item.get("run_id"))
                    for item in reports
                    if isinstance(item, dict)
                }
                if len(keys) != 24:
                    errors.append(
                        "Final semantic review report IDs must be unique"
                    )
                if any(
                    not isinstance(item, dict)
                    or item.get("deterministic_hard_pass") is not True
                    or item.get("unsupported_critical_claim") is not False
                    for item in reports
                ):
                    errors.append(
                        "Final semantic review contains a failed report"
                    )
            summary = review.get("summary")
            if not isinstance(summary, dict) or any(
                (
                    summary.get("reports_reviewed") != 24,
                    summary.get("deterministic_hard_passes") != 24,
                    summary.get("unsupported_critical_claims") != 0,
                    summary.get("semantic_gate_passed") is not True,
                )
            ):
                errors.append("Final semantic review summary does not pass")

    expected_reports = {f"{case_id}.md" for case_id in EVAL_CASE_IDS}
    for version in ("v1.1", "v1.2"):
        report_root = benchmark_root / "representative-outputs" / version
        actual = (
            {path.name for path in report_root.glob("*.md")}
            if report_root.is_dir()
            else set()
        )
        if actual != expected_reports:
            errors.append(
                f"Final benchmark representative outputs for {version} "
                "must contain all eight cases"
            )


def validate_repo(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    skill_root = root / SKILL_DIR

    if not skill_root.is_dir():
        return [f"Missing skill directory: {SKILL_DIR.as_posix()}"]

    actual_skill_files = {
        path.relative_to(skill_root)
        for path in skill_root.rglob("*")
        if path.is_file()
    }
    for missing in sorted(EXPECTED_SKILL_FILES - actual_skill_files):
        errors.append(f"Missing skill file: {(SKILL_DIR / missing).as_posix()}")
    for extra in sorted(actual_skill_files - EXPECTED_SKILL_FILES):
        errors.append(f"Unexpected skill file: {(SKILL_DIR / extra).as_posix()}")

    for relative in sorted(EXPECTED_SKILL_FILES & actual_skill_files):
        path = skill_root / relative
        try:
            read_utf8(path)
        except UnicodeDecodeError as exc:
            errors.append(f"Invalid UTF-8 in {path.relative_to(root)}: {exc}")

    skill_file = skill_root / "SKILL.md"
    if skill_file.is_file():
        frontmatter = parse_frontmatter(skill_file, errors)
        if frontmatter is not None:
            if set(frontmatter) != {"name", "description"}:
                errors.append("SKILL.md frontmatter must contain only name and description")
            if frontmatter.get("name") != SKILL_NAME:
                errors.append(f"SKILL.md name must be {SKILL_NAME}")
        skill_text = read_utf8(skill_file)
        for term in sorted(LANGUAGE_TERMS):
            if term not in skill_text:
                errors.append(f"Missing adaptive language instruction: {term}")
        if ENCODING_GUARD_TERM not in skill_text:
            errors.append(
                "Missing existing-report encoding guard: "
                f"{ENCODING_GUARD_TERM}"
            )
        if UNSUPPORTED_EXPLANATION_GUARD_TERM not in skill_text:
            errors.append(
                "Missing unsupported-explanation guard: "
                f"{UNSUPPORTED_EXPLANATION_GUARD_TERM}"
            )
        if UNSUPPLIED_EXPECTATION_GUARD_TERM not in skill_text:
            errors.append(
                "Missing unsupplied-expectation guard: "
                f"{UNSUPPLIED_EXPECTATION_GUARD_TERM}"
            )
        if SPARSE_REPORT_GUARD_TERM not in skill_text:
            errors.append(
                "Missing sparse-report length guard: "
                f"{SPARSE_REPORT_GUARD_TERM}"
            )
        if INPUT_CONTRACT_GUARD_TERM not in skill_text:
            errors.append(
                "Missing input-contract guard: "
                f"{INPUT_CONTRACT_GUARD_TERM}"
            )
        if OUTPUT_CONTRACT_GUARD_TERM not in skill_text:
            errors.append(
                "Missing output-contract guard: "
                f"{OUTPUT_CONTRACT_GUARD_TERM}"
            )
        if MISSING_SOURCE_GUARD_TERM not in skill_text:
            errors.append(
                "Missing source-required guard: "
                f"{MISSING_SOURCE_GUARD_TERM}"
            )
        if DECISION_SNAPSHOT_GUARD_TERM not in skill_text:
            errors.append(
                "Missing decision-snapshot guard: "
                f"{DECISION_SNAPSHOT_GUARD_TERM}"
            )
        for term in sorted(MEETING_LIFECYCLE_GUARD_TERMS):
            if term not in skill_text:
                errors.append(f"Missing meeting-lifecycle guard: {term}")

    for path in (
        skill_root / "references" / "progress-report.md",
        skill_root / "references" / "paper-review.md",
        skill_root / "references" / "mixed-report.md",
    ):
        if not path.is_file():
            continue
        template_text = read_utf8(path)
        for field in sorted(DECISION_SNAPSHOT_FIELDS):
            if field not in template_text:
                errors.append(
                    "Missing decision-snapshot field in "
                    f"{path.relative_to(root).as_posix()}: {field}"
                )
        for term in sorted(LIFECYCLE_TEMPLATE_TERMS):
            if term not in template_text:
                errors.append(
                    "Missing meeting-lifecycle template term in "
                    f"{path.relative_to(root).as_posix()}: {term}"
                )

    lifecycle_reference = skill_root / "references" / "meeting-lifecycle.md"
    if lifecycle_reference.is_file():
        lifecycle_text = read_utf8(lifecycle_reference)
        for term in sorted(MEETING_LIFECYCLE_REFERENCE_TERMS):
            if term not in lifecycle_text:
                errors.append(
                    "Missing meeting-lifecycle reference term: " f"{term}"
                )

    for path in (
        skill_root / "references" / "progress-report.md",
        skill_root / "references" / "mixed-report.md",
        root / "examples" / "research-progress" / "report.md",
        root / "examples" / "mixed" / "report.md",
    ):
        if path.is_file() and DEFAULT_PRIORITY_PATTERN.search(read_utf8(path)):
            errors.append(
                "Default priority rank detected in skill template: "
                f"{path.relative_to(root).as_posix()}"
            )

    metadata_file = skill_root / "agents" / "openai.yaml"
    if metadata_file.is_file():
        metadata = load_yaml(metadata_file, errors)
        interface = metadata.get("interface") if isinstance(metadata, dict) else None
        if not isinstance(interface, dict):
            errors.append("agents/openai.yaml must contain an interface mapping")
        else:
            required = {"display_name", "short_description", "default_prompt"}
            if set(interface) != required:
                errors.append(
                    "agents/openai.yaml interface must contain display_name, "
                    "short_description, and default_prompt"
                )
            if "$lab-meeting-report" not in str(interface.get("default_prompt", "")):
                errors.append("agents/openai.yaml default_prompt must invoke $lab-meeting-report")

    readme_path = root / "README.md"
    if not readme_path.is_file():
        errors.append("Missing README.md")
    else:
        readme = read_utf8(readme_path)
        for term in sorted(README_TERMS):
            if term not in readme:
                errors.append(f"README.md missing required term: {term}")

    for relative in sorted(COMMUNITY_FILES):
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing community file: {relative.as_posix()}")
            continue
        try:
            read_utf8(path)
        except UnicodeDecodeError as exc:
            errors.append(f"Invalid UTF-8 in {relative.as_posix()}: {exc}")

    for relative in sorted(EXAMPLE_FILES):
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing example file: {relative.as_posix()}")
            continue
        try:
            text = read_utf8(path)
        except UnicodeDecodeError as exc:
            errors.append(f"Invalid UTF-8 in {relative.as_posix()}: {exc}")
            continue
        if "Synthetic example" not in text:
            errors.append(f"Example lacks Synthetic example label: {relative.as_posix()}")
        if path.name == "report.md":
            for field in sorted(EXAMPLE_DECISION_SNAPSHOT_FIELDS):
                if field not in text:
                    errors.append(
                        "Example report missing decision-snapshot field in "
                        f"{relative.as_posix()}: {field}"
                    )
        if relative == Path("examples/research-progress/report.md"):
            for term in sorted(EXAMPLE_LIFECYCLE_TERMS):
                if term not in text:
                    errors.append(
                        "Research-progress example missing meeting-lifecycle "
                        f"term: {term}"
                    )

    for relative in sorted(EXAMPLE_SOURCE_FILES):
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing example source: {relative.as_posix()}")
            continue
        try:
            text = read_utf8(path)
        except UnicodeDecodeError as exc:
            errors.append(f"Invalid UTF-8 in {relative.as_posix()}: {exc}")
            continue
        if path.suffix == ".md" and "Synthetic example" not in text:
            errors.append(
                f"Example source lacks Synthetic example label: {relative.as_posix()}"
            )

    validate_example_numbers(root, errors)

    validate_preview_source(root, errors)
    validate_png(root / "assets" / "lab-meeting-report-preview.png", errors)
    validate_evaluation_assets(root, errors)
    validate_candidate_selection(root, errors)
    validate_final_benchmark(root, errors)

    old_name = SKILL_NAME + "-md"
    scaffold_pattern = re.compile(r"\b(?:T[O]DO|T[B]D|F[I]XME)\b")
    for path in repository_text_files(root):
        try:
            text = read_utf8(path)
        except UnicodeDecodeError as exc:
            errors.append(f"Invalid UTF-8 in {path.relative_to(root)}: {exc}")
            continue
        relative = path.relative_to(root).as_posix()
        if old_name in text:
            errors.append(f"Old skill name detected in {relative}")
        if path.is_relative_to(skill_root) and scaffold_pattern.search(text):
            errors.append(f"Scaffold marker detected in {relative}")
        for label, pattern in BLOCKED_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} detected in {relative}")

    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    errors = validate_repo(root)
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
