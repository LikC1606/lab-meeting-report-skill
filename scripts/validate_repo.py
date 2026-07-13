from __future__ import annotations

import hashlib
import re
import struct
import sys
from pathlib import Path

import yaml

try:
    from scripts.eval_contract import ContractError, load_manifest
except ModuleNotFoundError:
    from eval_contract import ContractError, load_manifest


SKILL_NAME = "lab-meeting-report"
SKILL_DIR = Path(SKILL_NAME)
EXPECTED_SKILL_FILES = {
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/lark-integration.md"),
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
README_TERMS = {
    "LikC1606/lab-meeting-report-skill@lab-meeting-report",
    "lab meeting report",
    "research progress report",
    "journal club",
    "Feishu",
    "Lark",
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

    validate_png(root / "assets" / "lab-meeting-report-preview.png", errors)
    validate_evaluation_assets(root, errors)

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
