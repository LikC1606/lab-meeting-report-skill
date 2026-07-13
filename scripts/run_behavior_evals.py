from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from scripts.eval_contract import (
    ContractError,
    hash_tree,
    iter_case_manifests,
    load_manifest,
    safe_relative_path,
)
from scripts.grade_report import grade_text


SKILL_NAME = "lab-meeting-report"
SKILL_FILES = {
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/lark-integration.md"),
    Path("references/mixed-report.md"),
    Path("references/paper-review.md"),
    Path("references/progress-report.md"),
}
CONFIGURATION_SKILL_DIR = {
    "with_skill": "with_skill",
    "without_skill": "without_skill",
}


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
    eval_index: int = 1


@dataclass(frozen=True)
class ExecutionContext:
    command: list[str]
    sandbox: Path
    last_message: Path
    case_root: Path
    manifest: dict[str, object]
    timeout_seconds: int


@dataclass(frozen=True)
class RunResult:
    run_dir: Path
    infrastructure_status: str
    hard_pass: bool | None
    attempts: int


Executor = Callable[[ExecutionContext], subprocess.CompletedProcess[str]]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def hash_run_environment(
    *,
    case_root: Path,
    skill_root: Path,
    prompt: str,
    runner_path: Path,
    grader_path: Path,
) -> dict[str, str]:
    return {
        "case_hash": hash_tree(case_root),
        "skill_hash": hash_tree(skill_root),
        "prompt_hash": _sha256_bytes(prompt.encode("utf-8")),
        "runner_hash": _sha256_file(runner_path),
        "grader_hash": _sha256_file(grader_path),
    }


def _validate_skill(skill_root: Path) -> None:
    if not skill_root.is_dir() or skill_root.is_symlink():
        raise ContractError(f"skill directory not found or unsafe: {skill_root}")
    for path in skill_root.rglob("*"):
        if path.is_symlink():
            raise ContractError(f"skill bundle contains symlink: {path}")
    actual = {
        path.relative_to(skill_root)
        for path in skill_root.rglob("*")
        if path.is_file()
    }
    if actual != SKILL_FILES:
        missing = sorted(item.as_posix() for item in SKILL_FILES - actual)
        extra = sorted(item.as_posix() for item in actual - SKILL_FILES)
        raise ContractError(
            f"unexpected Skill inventory; missing={missing}, extra={extra}"
        )
    skill_text = (skill_root / "SKILL.md").read_text(
        encoding="utf-8", errors="strict"
    )
    frontmatter = re.match(
        r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", skill_text, re.DOTALL
    )
    if not frontmatter or not re.search(
        rf"(?m)^name:\s*{re.escape(SKILL_NAME)}\s*$",
        frontmatter.group(1),
    ):
        raise ContractError(f"Skill frontmatter name must be {SKILL_NAME}")


def materialize_git_skill(
    repo_root: Path, ref: str, destination: Path
) -> Path:
    if destination.exists():
        raise ContractError(f"materialization destination exists: {destination}")
    destination.mkdir(parents=True)
    archive = subprocess.run(
        ["git", "archive", "--format=tar", ref, SKILL_NAME],
        cwd=repo_root,
        capture_output=True,
        check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination, filter="data")
    skill_root = destination / SKILL_NAME
    _validate_skill(skill_root)
    return skill_root


def build_prompt(
    manifest: dict[str, object], skill_file: Path
) -> str:
    task_file = safe_relative_path(str(manifest["task_file"]), "task_file")
    expected_report = safe_relative_path(
        str(manifest["expected_report"]), "expected_report"
    )
    return "\n".join(
        [
            "Execute the synthetic lab-meeting report task in this isolated workspace.",
            f"Open and follow the Skill at `{skill_file.as_posix()}`.",
            f"Read the user task at `{task_file.as_posix()}` and only the sources it places in scope.",
            f"Create the final Markdown report at `{expected_report.as_posix()}`.",
            "Do not read or search for manifest.json, expected-valid-report.md, or files outside this workspace.",
            "Do not stop after describing the report; write the requested file and verify it exists.",
        ]
    )


def _run_dir(spec: RunSpec, case_id: str) -> Path:
    configuration = CONFIGURATION_SKILL_DIR.get(spec.configuration)
    if configuration is None:
        raise ContractError(f"unsupported configuration: {spec.configuration}")
    eval_name = f"eval-{spec.eval_index:02d}-{case_id}"
    return spec.workspace / eval_name / configuration / f"run-{spec.run_number}"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _copy_case_to_sandbox(
    case_root: Path, manifest: dict[str, object], sandbox: Path
) -> None:
    task_file = safe_relative_path(str(manifest["task_file"]), "task_file")
    input_root = safe_relative_path(str(manifest["input_root"]), "input_root")
    task_destination = sandbox / task_file
    task_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(case_root / task_file, task_destination)
    shutil.copytree(case_root / input_root, sandbox / input_root)


def _materialize_skill(spec: RunSpec, sandbox: Path) -> Path:
    target = sandbox / "skill-under-test"
    if spec.candidate_skill is not None:
        shutil.copytree(spec.candidate_skill.resolve(), target)
        _validate_skill(target)
        return target
    if spec.baseline_ref is None:
        raise ContractError("a candidate Skill or baseline ref is required")
    materialized = materialize_git_skill(
        spec.repo_root.resolve(), spec.baseline_ref, sandbox / "_git-skill"
    )
    materialized.rename(target)
    (sandbox / "_git-skill").rmdir()
    _validate_skill(target)
    return target


def _codex_executable() -> str:
    if os.name == "nt":
        resolved = shutil.which("codex.cmd") or shutil.which("codex.exe")
        if resolved:
            return resolved
    return shutil.which("codex") or "codex"


def _build_command(
    spec: RunSpec, sandbox: Path, last_message: Path, prompt: str
) -> list[str]:
    return [
        _codex_executable(),
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
        "--model",
        spec.model,
        "--json",
        "--cd",
        str(sandbox),
        "--output-last-message",
        str(last_message),
        prompt,
    ]


def execute_codex(
    context: ExecutionContext,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        context.command,
        cwd=context.sandbox,
        timeout=context.timeout_seconds,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _extract_total_tokens(stdout: str) -> int:
    totals: list[int] = []

    def visit(value: object) -> None:
        if isinstance(value, dict):
            usage = value.get("usage")
            if isinstance(usage, dict):
                total = usage.get("total_tokens")
                if isinstance(total, int):
                    totals.append(total)
                else:
                    parts = [
                        item
                        for key, item in usage.items()
                        if key.endswith("_tokens") and isinstance(item, int)
                    ]
                    if parts:
                        totals.append(sum(parts))
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    for line in stdout.splitlines():
        try:
            visit(json.loads(line))
        except json.JSONDecodeError:
            continue
    return max(totals, default=0)


def _git_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _codex_version() -> str:
    result = subprocess.run(
        [_codex_executable(), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _validate_spec(spec: RunSpec) -> None:
    if spec.run_number < 1 or spec.eval_index < 1:
        raise ContractError("run_number and eval_index must be positive")
    if spec.timeout_seconds < 1:
        raise ContractError("timeout_seconds must be positive")
    has_candidate = spec.candidate_skill is not None
    has_baseline = spec.baseline_ref is not None
    if has_candidate == has_baseline:
        raise ContractError(
            "exactly one of candidate_skill and baseline_ref is required"
        )
    if has_candidate and spec.configuration != "with_skill":
        raise ContractError("candidate Skill requires with_skill configuration")
    if has_baseline and spec.configuration != "without_skill":
        raise ContractError("baseline ref requires without_skill configuration")


def _write_eval_metadata(
    run_dir: Path,
    spec: RunSpec,
    manifest: dict[str, object],
    prompt: str,
) -> None:
    _write_json(
        run_dir.parent.parent / "eval_metadata.json",
        {
            "eval_id": spec.eval_index,
            "eval_name": str(manifest["case_id"]),
            "prompt": prompt,
            "assertions": [],
        },
    )


def run_with_retry(
    spec: RunSpec, *, executor: Executor = execute_codex
) -> RunResult:
    _validate_spec(spec)
    manifest = load_manifest(spec.case_manifest)
    case_root = spec.case_manifest.resolve().parent
    case_id = str(manifest["case_id"])
    run_dir = _run_dir(spec, case_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(manifest, Path("skill-under-test/SKILL.md"))
    _write_eval_metadata(run_dir, spec, manifest, prompt)

    started = time.perf_counter()
    attempts = 0
    last_exit_status: int | str = "not-started"
    infrastructure_error = ""
    total_tokens = 0
    grading: dict[str, object] | None = None
    report_text: str | None = None
    runner_path = Path(__file__).resolve()
    grader_path = runner_path.with_name("grade_report.py")
    environment_hashes = {
        "case_hash": hash_tree(case_root),
        "skill_hash": "unavailable",
        "prompt_hash": _sha256_bytes(prompt.encode("utf-8")),
        "runner_hash": _sha256_file(runner_path),
        "grader_hash": _sha256_file(grader_path),
    }

    for attempts in range(1, 3):
        sandbox = run_dir / "sandbox"
        if sandbox.exists():
            shutil.rmtree(sandbox)
        sandbox.mkdir(parents=True)
        last_message = run_dir / "last-message.txt"
        if last_message.exists():
            last_message.unlink()
        try:
            _copy_case_to_sandbox(case_root, manifest, sandbox)
            skill_root = _materialize_skill(spec, sandbox)
            environment_hashes = hash_run_environment(
                case_root=case_root,
                skill_root=skill_root,
                prompt=prompt,
                runner_path=runner_path,
                grader_path=grader_path,
            )
            command = _build_command(
                spec, sandbox, last_message.resolve(), prompt
            )
            context = ExecutionContext(
                command=command,
                sandbox=sandbox,
                last_message=last_message,
                case_root=case_root,
                manifest=manifest,
                timeout_seconds=spec.timeout_seconds,
            )
            completed = executor(context)
            last_exit_status = completed.returncode
            total_tokens = max(
                total_tokens, _extract_total_tokens(completed.stdout or "")
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"Codex exit {completed.returncode}: "
                    f"{(completed.stderr or '').strip()[:500]}"
                )
            expected_report = sandbox / safe_relative_path(
                str(manifest["expected_report"]), "expected_report"
            )
            if not expected_report.is_file():
                raise RuntimeError(
                    f"expected report missing: {manifest['expected_report']}"
                )
            report_text = expected_report.read_text(
                encoding="utf-8", errors="strict"
            )
            grading = grade_text(report_text, manifest)
            infrastructure_error = ""
            break
        except subprocess.TimeoutExpired as exc:
            last_exit_status = "timeout"
            infrastructure_error = f"timeout after {exc.timeout} seconds"
        except (
            ContractError,
            OSError,
            RuntimeError,
            UnicodeDecodeError,
            subprocess.SubprocessError,
        ) as exc:
            last_exit_status = "exception"
            infrastructure_error = f"{type(exc).__name__}: {exc}"

    elapsed_ms = round((time.perf_counter() - started) * 1000)
    timing = {
        "total_tokens": total_tokens,
        "duration_ms": elapsed_ms,
        "total_duration_seconds": round(elapsed_ms / 1000, 3),
    }
    _write_json(run_dir / "timing.json", timing)

    valid = grading is not None and report_text is not None
    infrastructure_status = "valid" if valid else "invalid"
    metadata: dict[str, object] = {
        **environment_hashes,
        "model": spec.model,
        "cli_version": _codex_version(),
        "git_commit": _git_commit(spec.repo_root),
        "configuration": spec.configuration,
        "run_number": spec.run_number,
        "attempts": attempts,
        "exit_status": last_exit_status,
        "infrastructure_status": infrastructure_status,
    }
    if infrastructure_error:
        metadata["infrastructure_error"] = infrastructure_error
    _write_json(run_dir / "run_metadata.json", metadata)

    if not valid:
        return RunResult(run_dir, "invalid", None, attempts)

    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / "report.md").write_text(report_text, encoding="utf-8")
    _write_json(run_dir / "grading.json", grading)
    return RunResult(
        run_dir,
        "valid",
        bool(grading["hard_pass"]),
        attempts,
    )


def _require_eval_workspace(workspace: Path) -> Path:
    allowed_root = (
        Path(tempfile.gettempdir()) / "lab-meeting-report-v1.2-evals"
    ).resolve()
    resolved = workspace.resolve()
    if not resolved.is_relative_to(allowed_root):
        raise ContractError(
            f"workspace must be inside {allowed_root}, got {resolved}"
        )
    return resolved


def _existing_run_status(run_dir: Path) -> str | None:
    metadata = run_dir / "run_metadata.json"
    if not metadata.is_file():
        return None
    try:
        value = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    status = value.get("infrastructure_status")
    return status if isinstance(status, str) else None


def run_command(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    cases_root = Path(args.cases).resolve()
    workspace = _require_eval_workspace(Path(args.workspace))
    manifests = iter_case_manifests(cases_root)
    if not manifests:
        raise ContractError(f"no cases found under {cases_root}")
    candidate = (
        Path(args.candidate_skill).resolve()
        if args.candidate_skill is not None
        else None
    )
    valid_runs = 0
    invalid_runs = 0
    quality_failures = 0
    for index, manifest_path in enumerate(manifests, start=1):
        case_id = str(load_manifest(manifest_path)["case_id"])
        for run_number in range(1, args.runs + 1):
            spec = RunSpec(
                repo_root=repo_root,
                case_manifest=manifest_path,
                workspace=workspace,
                configuration=args.configuration,
                run_number=run_number,
                model=args.model,
                timeout_seconds=args.timeout_seconds,
                candidate_skill=candidate,
                baseline_ref=args.baseline_ref,
                eval_index=index,
            )
            run_dir = _run_dir(spec, case_id)
            if run_dir.exists() and any(run_dir.iterdir()):
                if not args.resume:
                    raise ContractError(
                        f"run directory already exists: {run_dir}"
                    )
                if _existing_run_status(run_dir) == "valid":
                    valid_runs += 1
                    continue
                shutil.rmtree(run_dir)
            result = run_with_retry(spec)
            if result.infrastructure_status == "invalid":
                invalid_runs += 1
            else:
                valid_runs += 1
                if not result.hard_pass:
                    quality_failures += 1
    print(
        f"{valid_runs} valid runs; {quality_failures} quality failures; "
        f"{invalid_runs} infrastructure-invalid runs"
    )
    return 2 if invalid_runs else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and review lab-meeting-report behavior evaluations"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser(
        "run", help="run isolated behavior evaluations"
    )
    run_parser.add_argument("--repo-root", required=True)
    run_parser.add_argument("--cases", required=True)
    run_parser.add_argument("--workspace", required=True)
    run_parser.add_argument(
        "--configuration", choices=sorted(CONFIGURATION_SKILL_DIR), required=True
    )
    source = run_parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--baseline-ref")
    source.add_argument("--candidate-skill")
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--runs", type=int, default=1)
    run_parser.add_argument("--timeout-seconds", type=int, default=900)
    run_parser.add_argument("--resume", action="store_true")
    run_parser.set_defaults(handler=run_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.runs < 1:
            raise ContractError("runs must be positive")
        return int(args.handler(args))
    except (
        ContractError,
        OSError,
        subprocess.SubprocessError,
        ValueError,
    ) as exc:
        print(f"Evaluation infrastructure error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
