from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean, median, stdev
from typing import Callable
from urllib.parse import urlsplit

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
PROVIDER_FIELDS = {
    "name",
    "base_url",
    "wire_api",
    "requires_openai_auth",
}


@dataclass(frozen=True)
class NetworkProvider:
    key: str
    name: str
    base_url: str
    wire_api: str
    requires_openai_auth: bool
    windows_sandbox: str | None


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
    network_provider: NetworkProvider | None = None


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


def load_network_provider(path: Path) -> NetworkProvider | None:
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractError(f"cannot read provider config {path}: {exc}") from exc
    key = data.get("model_provider")
    providers = data.get("model_providers")
    if not isinstance(key, str) or not isinstance(providers, dict):
        return None
    raw = providers.get(key)
    if raw is None:
        return None
    if not re.fullmatch(r"[A-Za-z0-9_]+", key):
        raise ContractError("model provider key must be alphanumeric or underscore")
    if not isinstance(raw, dict):
        raise ContractError(f"model provider {key} must be a table")
    extra = set(raw) - PROVIDER_FIELDS
    missing = PROVIDER_FIELDS - set(raw)
    if extra:
        raise ContractError(
            f"model provider {key} has unsupported fields: {sorted(extra)}"
        )
    if missing:
        raise ContractError(
            f"model provider {key} is missing fields: {sorted(missing)}"
        )
    name = raw["name"]
    base_url = raw["base_url"]
    wire_api = raw["wire_api"]
    requires_openai_auth = raw["requires_openai_auth"]
    if not isinstance(name, str) or not name.strip():
        raise ContractError("model provider name must be a non-empty string")
    if not isinstance(base_url, str):
        raise ContractError("model provider base_url must be a string")
    parsed = urlsplit(base_url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ContractError("model provider base_url is not a safe HTTP URL")
    if wire_api != "responses":
        raise ContractError("behavior evaluation requires responses wire_api")
    if not isinstance(requires_openai_auth, bool):
        raise ContractError("requires_openai_auth must be boolean")
    windows_sandbox: str | None = None
    windows = data.get("windows")
    if isinstance(windows, dict) and "sandbox" in windows:
        value = windows["sandbox"]
        if value != "elevated":
            raise ContractError(
                "behavior evaluation only permits windows.sandbox=elevated"
            )
        windows_sandbox = value
    return NetworkProvider(
        key=key,
        name=name,
        base_url=base_url,
        wire_api=wire_api,
        requires_openai_auth=requires_openai_auth,
        windows_sandbox=windows_sandbox,
    )


def _provider_hash(provider: NetworkProvider | None) -> str:
    if provider is None:
        return _sha256_bytes(b"builtin-default-provider")
    value = {
        "key": provider.key,
        "name": provider.name,
        "base_url": provider.base_url,
        "wire_api": provider.wire_api,
        "requires_openai_auth": provider.requires_openai_auth,
        "windows_sandbox": provider.windows_sandbox,
    }
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _provider_arguments(provider: NetworkProvider | None) -> list[str]:
    if provider is None:
        return []
    values = (
        ("model_provider", provider.key),
        (f"model_providers.{provider.key}.name", provider.name),
        (f"model_providers.{provider.key}.base_url", provider.base_url),
        (f"model_providers.{provider.key}.wire_api", provider.wire_api),
    )
    arguments: list[str] = []
    for key, value in values:
        arguments.extend(["--config", f"{key}={json.dumps(value)}"])
    auth = str(provider.requires_openai_auth).lower()
    arguments.extend(
        [
            "--config",
            f"model_providers.{provider.key}.requires_openai_auth={auth}",
        ]
    )
    if provider.windows_sandbox is not None:
        arguments.extend(
            [
                "--config",
                f"windows.sandbox={json.dumps(provider.windows_sandbox)}",
            ]
        )
    return arguments


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


def _subprocess_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _write_attempt_logs(
    run_dir: Path,
    attempt: int,
    *,
    stdout: str | bytes | None,
    stderr: str | bytes | None,
    status: str,
) -> None:
    attempt_dir = run_dir / "attempts" / f"attempt-{attempt}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "stdout.jsonl").write_text(
        _subprocess_text(stdout), encoding="utf-8"
    )
    (attempt_dir / "stderr.txt").write_text(
        _subprocess_text(stderr), encoding="utf-8"
    )
    _write_json(attempt_dir / "status.json", {"status": status})


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
        *_provider_arguments(spec.network_provider),
        "--skip-git-repo-check",
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
        stdin=subprocess.DEVNULL,
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
        "provider_hash": _provider_hash(spec.network_provider),
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
        attempt_stdout: str | bytes | None = None
        attempt_stderr: str | bytes | None = None
        try:
            _copy_case_to_sandbox(case_root, manifest, sandbox)
            skill_root = _materialize_skill(spec, sandbox)
            environment_hashes.update(
                hash_run_environment(
                    case_root=case_root,
                    skill_root=skill_root,
                    prompt=prompt,
                    runner_path=runner_path,
                    grader_path=grader_path,
                )
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
            attempt_stdout = completed.stdout
            attempt_stderr = completed.stderr
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
            _write_attempt_logs(
                run_dir,
                attempts,
                stdout=attempt_stdout,
                stderr=attempt_stderr,
                status="valid",
            )
            infrastructure_error = ""
            break
        except subprocess.TimeoutExpired as exc:
            last_exit_status = "timeout"
            infrastructure_error = f"timeout after {exc.timeout} seconds"
            _write_attempt_logs(
                run_dir,
                attempts,
                stdout=exc.stdout,
                stderr=exc.stderr,
                status="timeout",
            )
        except (
            ContractError,
            OSError,
            RuntimeError,
            UnicodeDecodeError,
            subprocess.SubprocessError,
        ) as exc:
            last_exit_status = "exception"
            infrastructure_error = f"{type(exc).__name__}: {exc}"
            diagnostic = _subprocess_text(attempt_stderr)
            if diagnostic and not diagnostic.endswith("\n"):
                diagnostic += "\n"
            diagnostic += infrastructure_error + "\n"
            _write_attempt_logs(
                run_dir,
                attempts,
                stdout=attempt_stdout,
                stderr=diagnostic,
                status="exception",
            )

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


def _load_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object: {path}")
    return value


def _discover_workspace_runs(workspace: Path) -> list[dict[str, object]]:
    workspace = workspace.resolve()
    records: list[dict[str, object]] = []
    seen: set[tuple[int, str, int]] = set()
    for eval_dir in sorted(workspace.glob("eval-*")):
        if not eval_dir.is_dir():
            continue
        eval_metadata = _load_json(
            eval_dir / "eval_metadata.json", "eval metadata"
        )
        eval_id = eval_metadata.get("eval_id")
        eval_name = eval_metadata.get("eval_name")
        if not isinstance(eval_id, int) or eval_id < 1:
            raise ContractError(f"invalid eval_id in {eval_dir}")
        if not isinstance(eval_name, str) or not eval_name:
            raise ContractError(f"invalid eval_name in {eval_dir}")
        for configuration in sorted(CONFIGURATION_SKILL_DIR):
            configuration_dir = eval_dir / configuration
            if not configuration_dir.is_dir():
                continue
            for run_dir in sorted(configuration_dir.glob("run-*")):
                if not run_dir.is_dir():
                    continue
                try:
                    run_number = int(run_dir.name.removeprefix("run-"))
                except ValueError as exc:
                    raise ContractError(
                        f"invalid run directory name: {run_dir}"
                    ) from exc
                key = (eval_id, configuration, run_number)
                if key in seen:
                    raise ContractError(f"duplicate workspace run: {key}")
                seen.add(key)
                grading = _load_json(run_dir / "grading.json", "grading")
                timing = _load_json(run_dir / "timing.json", "timing")
                run_metadata = _load_json(
                    run_dir / "run_metadata.json", "run metadata"
                )
                if run_metadata.get("infrastructure_status") != "valid":
                    raise ContractError(f"infrastructure-invalid run: {run_dir}")
                if run_metadata.get("configuration") != configuration:
                    raise ContractError(
                        f"configuration mismatch in {run_dir}"
                    )
                if run_metadata.get("run_number") != run_number:
                    raise ContractError(f"run number mismatch in {run_dir}")
                if not (run_dir / "outputs" / "report.md").is_file():
                    raise ContractError(f"missing report output: {run_dir}")
                records.append(
                    {
                        "eval_id": eval_id,
                        "eval_name": eval_name,
                        "configuration": configuration,
                        "run_number": run_number,
                        "run_dir": run_dir,
                        "eval_metadata": eval_metadata,
                        "grading": grading,
                        "timing": timing,
                        "run_metadata": run_metadata,
                    }
                )
    if not records:
        raise ContractError(f"no valid runs found in {workspace}")
    records.sort(
        key=lambda item: (
            int(item["eval_id"]),
            str(item["configuration"]),
            int(item["run_number"]),
        )
    )
    return records


def _validate_workspace_matrix(
    records: list[dict[str, object]], model: str
) -> int:
    configurations = {str(item["configuration"]) for item in records}
    evals = {
        (int(item["eval_id"]), str(item["eval_name"])) for item in records
    }
    counts: set[int] = set()
    for eval_id, eval_name in evals:
        eval_records = [
            item
            for item in records
            if item["eval_id"] == eval_id and item["eval_name"] == eval_name
        ]
        eval_configurations = {
            str(item["configuration"]) for item in eval_records
        }
        if eval_configurations != configurations:
            raise ContractError(
                f"missing configuration for eval {eval_id} {eval_name}"
            )
        for configuration in configurations:
            group = [
                item
                for item in eval_records
                if item["configuration"] == configuration
            ]
            numbers = sorted(int(item["run_number"]) for item in group)
            if numbers != list(range(1, len(numbers) + 1)):
                raise ContractError(
                    f"missing run combination for {eval_name} {configuration}"
                )
            counts.add(len(numbers))
            stable_fields = (
                "case_hash",
                "skill_hash",
                "provider_hash",
                "prompt_hash",
                "runner_hash",
                "grader_hash",
                "model",
                "cli_version",
            )
            for field in stable_fields:
                values = {
                    str(item["run_metadata"].get(field)) for item in group
                }
                if len(values) != 1:
                    raise ContractError(
                        f"run environment mismatch for {eval_name} "
                        f"{configuration}: {field}"
                    )
            if any(item["run_metadata"].get("model") != model for item in group):
                raise ContractError(
                    f"executor model mismatch for {eval_name} {configuration}"
                )
    if len(counts) != 1:
        raise ContractError(f"unequal runs per configuration: {sorted(counts)}")
    return counts.pop()


def _record_to_benchmark_run(
    record: dict[str, object], *, configuration: str | None = None
) -> dict[str, object]:
    grading = record["grading"]
    timing = record["timing"]
    summary = grading.get("summary")
    expectations = grading.get("expectations")
    metrics = grading.get("execution_metrics", {})
    if not isinstance(summary, dict) or not isinstance(expectations, list):
        raise ContractError(f"invalid grading summary: {record['run_dir']}")
    if not isinstance(metrics, dict):
        raise ContractError(
            f"invalid grading execution metrics: {record['run_dir']}"
        )
    required_summary = {"pass_rate", "passed", "failed", "total"}
    if not required_summary.issubset(summary):
        raise ContractError(f"incomplete grading summary: {record['run_dir']}")
    time_seconds = timing.get("total_duration_seconds")
    tokens = timing.get("total_tokens")
    if not isinstance(time_seconds, (int, float)) or isinstance(
        time_seconds, bool
    ):
        raise ContractError(f"invalid timing value: {record['run_dir']}")
    if not isinstance(tokens, int) or isinstance(tokens, bool):
        raise ContractError(f"invalid token count: {record['run_dir']}")
    notes: list[str] = []
    return {
        "eval_id": record["eval_id"],
        "eval_name": record["eval_name"],
        "configuration": configuration or record["configuration"],
        "run_number": record["run_number"],
        "result": {
            "pass_rate": float(summary["pass_rate"]),
            "passed": int(summary["passed"]),
            "failed": int(summary["failed"]),
            "total": int(summary["total"]),
            "time_seconds": float(time_seconds),
            "tokens": tokens,
            "tool_calls": int(metrics.get("total_tool_calls", 0)),
            "errors": int(metrics.get("errors_encountered", 0)),
        },
        "expectations": expectations,
        "notes": notes,
    }


def _metric_stats(values: list[float]) -> dict[str, float]:
    if not values:
        raise ContractError("cannot aggregate an empty metric")
    return {
        "mean": round(fmean(values), 6),
        "stddev": round(stdev(values), 6) if len(values) > 1 else 0.0,
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }


def _format_delta(value: float, digits: int) -> str:
    return f"{value:+.{digits}f}"


def _summarize_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    configurations = sorted({str(run["configuration"]) for run in runs})
    summary: dict[str, object] = {}
    for configuration in configurations:
        group = [run for run in runs if run["configuration"] == configuration]
        summary[configuration] = {
            metric: _metric_stats(
                [float(run["result"][metric]) for run in group]
            )
            for metric in ("pass_rate", "time_seconds", "tokens")
        }
    delta: dict[str, str] = {}
    preferred_pairs = [
        ("with_skill", "without_skill"),
        ("A", "B"),
    ]
    for first, second in preferred_pairs:
        if first in summary and second in summary:
            first_summary = summary[first]
            second_summary = summary[second]
            delta = {
                "pass_rate": _format_delta(
                    first_summary["pass_rate"]["mean"]
                    - second_summary["pass_rate"]["mean"],
                    2,
                ),
                "time_seconds": _format_delta(
                    first_summary["time_seconds"]["mean"]
                    - second_summary["time_seconds"]["mean"],
                    1,
                ),
                "tokens": _format_delta(
                    first_summary["tokens"]["mean"]
                    - second_summary["tokens"]["mean"],
                    0,
                ),
            }
            break
    summary["delta"] = delta
    return summary


def _benchmark_notes(runs: list[dict[str, object]]) -> list[str]:
    notes: list[str] = []
    by_expectation: dict[str, dict[str, list[bool]]] = {}
    for run in runs:
        configuration = str(run["configuration"])
        for expectation in run["expectations"]:
            if not isinstance(expectation, dict):
                continue
            text = expectation.get("text")
            passed = expectation.get("passed")
            if isinstance(text, str) and isinstance(passed, bool):
                by_expectation.setdefault(text, {}).setdefault(
                    configuration, []
                ).append(passed)
    for text, configurations in sorted(by_expectation.items()):
        if len(configurations) < 2:
            continue
        if all(all(values) for values in configurations.values()):
            notes.append(
                f"Expectation '{text}' passes in every configuration and may "
                "not differentiate Skill value."
            )
        elif all(
            not any(values) for values in configurations.values()
        ):
            notes.append(
                f"Expectation '{text}' fails in every configuration and may "
                "be beyond the tested capability."
            )
    by_eval: dict[tuple[str, str], list[float]] = {}
    for run in runs:
        key = (str(run["eval_name"]), str(run["configuration"]))
        by_eval.setdefault(key, []).append(float(run["result"]["pass_rate"]))
    for (eval_name, configuration), values in sorted(by_eval.items()):
        if len(values) > 1 and stdev(values) >= 0.25:
            notes.append(
                f"{eval_name} has high pass-rate variance under "
                f"{configuration}: stddev {stdev(values):.2f}."
            )
    return notes


def aggregate_workspace(
    workspace: Path, *, model: str
) -> dict[str, object]:
    records = _discover_workspace_runs(workspace)
    runs_per_configuration = _validate_workspace_matrix(records, model)
    runs = [_record_to_benchmark_run(record) for record in records]
    evals = sorted({int(run["eval_id"]) for run in runs})
    return {
        "metadata": {
            "skill_name": SKILL_NAME,
            "executor_model": model,
            "analyzer_model": "human-blind-review",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "evals_run": evals,
            "runs_per_configuration": runs_per_configuration,
        },
        "runs": runs,
        "run_summary": _summarize_runs(runs),
        "notes": _benchmark_notes(runs),
    }


def write_benchmark_markdown(
    benchmark: dict[str, object], output: Path
) -> None:
    metadata = benchmark["metadata"]
    lines = [
        "# Lab Meeting Report Behavior Benchmark",
        "",
        f"- Executor model: `{metadata['executor_model']}`",
        f"- Runs per configuration: `{metadata['runs_per_configuration']}`",
        f"- Evaluations: `{len(metadata['evals_run'])}`",
        "",
        "## Configuration Summary",
        "",
        "| Configuration | Pass rate | Time (s) | Tokens |",
        "|---|---:|---:|---:|",
    ]
    for configuration, values in benchmark["run_summary"].items():
        if configuration == "delta":
            continue
        lines.append(
            f"| {configuration} | {values['pass_rate']['mean']:.3f} "
            f"+/- {values['pass_rate']['stddev']:.3f} | "
            f"{values['time_seconds']['mean']:.1f} +/- "
            f"{values['time_seconds']['stddev']:.1f} | "
            f"{values['tokens']['mean']:.0f} +/- "
            f"{values['tokens']['stddev']:.0f} |"
        )
    lines.extend(["", "## Analyzer Notes", ""])
    notes = benchmark.get("notes", [])
    if notes:
        lines.extend(f"- {note}" for note in notes)
    else:
        lines.append("- No cross-run anomalies detected.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _source_packet(record: dict[str, object]) -> str:
    sandbox = Path(record["run_dir"]) / "sandbox"
    sections = ["# Synthetic Source Packet", ""]
    for path in sorted(sandbox.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(sandbox)
        if relative.parts[0] in {"skill-under-test", "reports"}:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            content = (
                "[Unreadable UTF-8 fixture; SHA-256 "
                f"{_sha256_file(path)}]"
            )
        sections.extend(
            [f"## `{relative.as_posix()}`", "", content.rstrip(), ""]
        )
    return "\n".join(sections).rstrip() + "\n"


def _hard_gates_markdown(record: dict[str, object]) -> str:
    grading = record["grading"]
    lines = [
        "# Deterministic Hard Gates",
        "",
        f"Hard pass: `{str(bool(grading.get('hard_pass'))).lower()}`",
        "",
    ]
    for expectation in grading.get("expectations", []):
        status = "PASS" if expectation.get("passed") else "FAIL"
        lines.append(
            f"- **{status}** `{expectation.get('text', 'unknown')}`: "
            f"{expectation.get('evidence', '')}"
        )
    return "\n".join(lines) + "\n"


REVIEW_DIMENSIONS = (
    "evidence_clarity",
    "information_selection",
    "decision_usefulness",
    "readability",
)


def _review_format() -> dict[str, object]:
    scores = {dimension: 1 for dimension in REVIEW_DIMENSIONS}
    return {
        "semantic_failure": "none",
        "A": dict(scores),
        "B": dict(scores),
        "preference": "tie",
        "notes": "",
    }


def prepare_blind_review(
    workspace: Path,
    review_workspace: Path,
    *,
    seed: int,
    baseline_workspace: Path | None = None,
    blind_map_path: Path | None = None,
) -> dict[str, object]:
    candidate_records = _discover_workspace_runs(workspace)
    if baseline_workspace is None:
        records = candidate_records
    else:
        records = [
            *candidate_records,
            *_discover_workspace_runs(baseline_workspace),
        ]
    review_workspace = review_workspace.resolve()
    if review_workspace.exists() and any(review_workspace.iterdir()):
        raise ContractError(
            f"review workspace must be empty: {review_workspace}"
        )
    review_workspace.mkdir(parents=True, exist_ok=True)

    grouped: dict[
        tuple[int, str, int], dict[str, dict[str, object]]
    ] = {}
    for record in records:
        key = (
            int(record["eval_id"]),
            str(record["eval_name"]),
            int(record["run_number"]),
        )
        configuration = str(record["configuration"])
        if configuration in grouped.setdefault(key, {}):
            raise ContractError(
                f"duplicate review source for {key} {configuration}"
            )
        grouped[key][configuration] = record

    pairs: list[dict[str, object]] = []
    anonymous_runs: list[dict[str, object]] = []
    for key in sorted(grouped):
        eval_id, eval_name, run_number = key
        configurations = grouped[key]
        if set(configurations) != {"with_skill", "without_skill"}:
            raise ContractError(f"review pair is incomplete: {key}")
        rng = random.Random(f"{seed}:{eval_name}:{run_number}")
        if rng.random() < 0.5:
            sides = {"A": "with_skill", "B": "without_skill"}
        else:
            sides = {"A": "without_skill", "B": "with_skill"}
        eval_dir = review_workspace / f"eval-{eval_id:02d}-{eval_name}"
        pair_dir = eval_dir / f"pair-{run_number}"
        outputs = pair_dir / "outputs"
        outputs.mkdir(parents=True)
        prompt = configurations["with_skill"]["eval_metadata"].get(
            "prompt", ""
        )
        _write_json(
            eval_dir / "eval_metadata.json",
            {
                "eval_id": eval_id,
                "eval_name": eval_name,
                "prompt": prompt,
                "assertions": [],
            },
        )
        (outputs / "source-packet.md").write_text(
            _source_packet(configurations["with_skill"]), encoding="utf-8"
        )
        for side in ("A", "B"):
            record = configurations[sides[side]]
            report = Path(record["run_dir"]) / "outputs" / "report.md"
            shutil.copy2(report, outputs / f"{side}-report.md")
            (outputs / f"{side}-hard-gates.md").write_text(
                _hard_gates_markdown(record), encoding="utf-8"
            )
            anonymous_runs.append(
                _record_to_benchmark_run(record, configuration=side)
            )
        _write_json(outputs / "review-format.json", _review_format())
        review_run_id = f"{eval_dir.name}-pair-{run_number}"
        pairs.append(
            {
                "review_run_id": review_run_id,
                "eval_id": eval_id,
                "eval_name": eval_name,
                "run_number": run_number,
                "A": sides["A"],
                "B": sides["B"],
            }
        )

    mapping: dict[str, object] = {"seed": seed, "pairs": pairs}
    if blind_map_path is not None:
        if blind_map_path.resolve().is_relative_to(review_workspace):
            raise ContractError("blind map must be outside review workspace")
        _write_json(blind_map_path, mapping)
    anonymous_benchmark = {
        "metadata": {
            "skill_name": "anonymous-A-B",
            "executor_model": "redacted-for-blind-review",
            "analyzer_model": "human-blind-review",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "evals_run": sorted({pair["eval_id"] for pair in pairs}),
            "runs_per_configuration": len(
                {pair["run_number"] for pair in pairs}
            ),
        },
        "runs": anonymous_runs,
        "run_summary": _summarize_runs(anonymous_runs),
        "notes": [],
    }
    _write_json(review_workspace / "benchmark.json", anonymous_benchmark)
    return mapping


def _json_object(value: Path | dict[str, object], label: str) -> dict[str, object]:
    if isinstance(value, Path):
        return _load_json(value, label)
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    return value


def _validate_review_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ContractError("review feedback must be a JSON object")
    expected = {"semantic_failure", "A", "B", "preference", "notes"}
    if set(payload) != expected:
        raise ContractError(
            f"review feedback fields must be {sorted(expected)}"
        )
    if payload["semantic_failure"] not in {"none", "A", "B", "both"}:
        raise ContractError("invalid semantic_failure value")
    if payload["preference"] not in {"A", "B", "tie"}:
        raise ContractError("invalid preference value")
    if not isinstance(payload["notes"], str):
        raise ContractError("review notes must be a string")
    for side in ("A", "B"):
        scores = payload[side]
        if not isinstance(scores, dict) or set(scores) != set(
            REVIEW_DIMENSIONS
        ):
            raise ContractError(f"{side} review scores have invalid fields")
        for dimension, score in scores.items():
            if (
                not isinstance(score, int)
                or isinstance(score, bool)
                or not 1 <= score <= 5
            ):
                raise ContractError(
                    f"{side}.{dimension} must be between 1 and 5"
                )
    return payload


def _median_scores(values: list[dict[str, int]]) -> dict[str, float]:
    if not values:
        raise ContractError("cannot calculate review medians without scores")
    result = {
        dimension: float(median([item[dimension] for item in values]))
        for dimension in REVIEW_DIMENSIONS
    }
    result["overall"] = float(
        median(
            [score for item in values for score in item.values()]
        )
    )
    return result


def parse_review_feedback(
    feedback: Path | dict[str, object],
    blind_map: Path | dict[str, object],
) -> dict[str, object]:
    feedback_data = _json_object(feedback, "feedback")
    mapping = _json_object(blind_map, "blind map")
    if feedback_data.get("status") != "complete":
        raise ContractError("feedback status must be complete")
    pairs = mapping.get("pairs")
    reviews = feedback_data.get("reviews")
    if not isinstance(pairs, list) or not isinstance(reviews, list):
        raise ContractError("feedback and blind map require arrays")
    pair_by_id = {
        str(pair["review_run_id"]): pair
        for pair in pairs
        if isinstance(pair, dict) and "review_run_id" in pair
    }
    if len(pair_by_id) != len(pairs):
        raise ContractError("blind map has duplicate or malformed pairs")
    reviewed_ids: set[str] = set()
    preference_counts = {"candidate": 0, "baseline": 0, "tie": 0}
    semantic_failures: dict[str, list[dict[str, object]]] = {
        "candidate": [],
        "baseline": [],
    }
    score_sets: dict[str, list[dict[str, int]]] = {
        "candidate": [],
        "baseline": [],
    }
    case_scores: dict[
        str, dict[str, list[dict[str, int]]]
    ] = {}
    case_preferences: dict[str, dict[str, int]] = {}
    parsed_reviews: list[dict[str, object]] = []

    for review in reviews:
        if not isinstance(review, dict):
            raise ContractError("feedback review must be an object")
        run_id = review.get("run_id")
        raw_feedback = review.get("feedback")
        if not isinstance(run_id, str) or run_id not in pair_by_id:
            raise ContractError(f"unknown review run_id: {run_id}")
        if run_id in reviewed_ids:
            raise ContractError(f"duplicate review run_id: {run_id}")
        if not isinstance(raw_feedback, str) or not raw_feedback.strip():
            raise ContractError(f"review feedback is empty: {run_id}")
        try:
            payload = _validate_review_payload(json.loads(raw_feedback))
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"review feedback is not valid JSON: {run_id}"
            ) from exc
        pair = pair_by_id[run_id]
        reviewed_ids.add(run_id)
        side_for = {
            "candidate": "A" if pair["A"] == "with_skill" else "B",
            "baseline": "A" if pair["A"] == "without_skill" else "B",
        }
        eval_name = str(pair["eval_name"])
        case_scores.setdefault(
            eval_name, {"candidate": [], "baseline": []}
        )
        case_preferences.setdefault(
            eval_name, {"candidate": 0, "baseline": 0, "tie": 0}
        )
        for configuration in ("candidate", "baseline"):
            side = side_for[configuration]
            scores = {
                dimension: int(payload[side][dimension])
                for dimension in REVIEW_DIMENSIONS
            }
            score_sets[configuration].append(scores)
            case_scores[eval_name][configuration].append(scores)

        preference = str(payload["preference"])
        if preference == "tie":
            winner = "tie"
        else:
            winner = (
                "candidate"
                if pair[preference] == "with_skill"
                else "baseline"
            )
        preference_counts[winner] += 1
        case_preferences[eval_name][winner] += 1

        failed_sides: list[str] = []
        if payload["semantic_failure"] == "both":
            failed_sides = ["A", "B"]
        elif payload["semantic_failure"] in {"A", "B"}:
            failed_sides = [str(payload["semantic_failure"])]
        for side in failed_sides:
            configuration = (
                "candidate" if pair[side] == "with_skill" else "baseline"
            )
            semantic_failures[configuration].append(
                {
                    "eval_id": pair["eval_id"],
                    "eval_name": eval_name,
                    "run_number": pair["run_number"],
                    "side": side,
                    "notes": payload["notes"],
                }
            )
        parsed_reviews.append(
            {
                "review_run_id": run_id,
                "eval_id": pair["eval_id"],
                "eval_name": eval_name,
                "run_number": pair["run_number"],
                "preference": winner,
                "semantic_failure": payload["semantic_failure"],
                "candidate_scores": payload[side_for["candidate"]],
                "baseline_scores": payload[side_for["baseline"]],
                "notes": payload["notes"],
            }
        )
    if reviewed_ids != set(pair_by_id):
        missing = sorted(set(pair_by_id) - reviewed_ids)
        raise ContractError(f"missing review feedback for: {missing}")

    per_case = {
        eval_name: {
            "candidate": _median_scores(values["candidate"]),
            "baseline": _median_scores(values["baseline"]),
            "preference_counts": case_preferences[eval_name],
        }
        for eval_name, values in sorted(case_scores.items())
    }
    return {
        "pairs_reviewed": len(parsed_reviews),
        "preference_counts": preference_counts,
        "semantic_failures": semantic_failures,
        "global_medians": {
            "candidate": _median_scores(score_sets["candidate"]),
            "baseline": _median_scores(score_sets["baseline"]),
        },
        "per_case": per_case,
        "reviews": parsed_reviews,
    }


def apply_human_review(
    benchmark: dict[str, object], human_review: dict[str, object]
) -> dict[str, object]:
    reviewed = copy.deepcopy(benchmark)
    runs = reviewed.get("runs")
    failures = human_review.get("semantic_failures")
    if not isinstance(runs, list) or not isinstance(failures, dict):
        raise ContractError("invalid benchmark or human review")
    for review_configuration, run_configuration in (
        ("candidate", "with_skill"),
        ("baseline", "without_skill"),
    ):
        findings = failures.get(review_configuration, [])
        if not isinstance(findings, list):
            raise ContractError("semantic failures must be arrays")
        for finding in findings:
            if not isinstance(finding, dict):
                raise ContractError("semantic failure must be an object")
            matches = [
                run
                for run in runs
                if run.get("configuration") == run_configuration
                and run.get("eval_id") == finding.get("eval_id")
                and run.get("run_number") == finding.get("run_number")
            ]
            if len(matches) != 1:
                raise ContractError(
                    f"semantic failure does not identify one run: {finding}"
                )
            run = matches[0]
            result = run.get("result")
            if not isinstance(result, dict):
                raise ContractError("benchmark run result must be an object")
            total = max(int(result.get("total", 0)), 1)
            result.update(
                {"pass_rate": 0.0, "passed": 0, "failed": total, "total": total}
            )
            notes = run.setdefault("notes", [])
            if not isinstance(notes, list):
                raise ContractError("benchmark run notes must be an array")
            notes.append(
                "Human semantic review failure: "
                + str(finding.get("notes", "unsupported critical claim"))
            )
    reviewed["run_summary"] = _summarize_runs(runs)
    return reviewed


def check_release_gate(
    benchmark: dict[str, object], human_review: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    runs = benchmark.get("runs")
    if not isinstance(runs, list):
        return ["benchmark runs must be an array"]
    if human_review.get("pairs_reviewed") != 24:
        errors.append(
            "human review: expected 24/24 pairs, got "
            f"{human_review.get('pairs_reviewed', 0)}/24"
        )
    candidate = [run for run in runs if run.get("configuration") == "with_skill"]
    baseline = [
        run for run in runs if run.get("configuration") == "without_skill"
    ]
    candidate_evals = {str(run.get("eval_name")) for run in candidate}
    if len(candidate_evals) != 8 or len(candidate) != 24:
        errors.append(
            "candidate matrix: expected 8 cases and 24 runs, got "
            f"{len(candidate_evals)} cases and {len(candidate)} runs"
        )
    matrix_ok = True
    for eval_name in candidate_evals:
        numbers = sorted(
            int(run.get("run_number", 0))
            for run in candidate
            if str(run.get("eval_name")) == eval_name
        )
        if numbers != [1, 2, 3]:
            matrix_ok = False
    if not matrix_ok:
        errors.append("candidate matrix: every case requires runs 1, 2, and 3")

    hard_passes = sum(
        1
        for run in candidate
        if float(run.get("result", {}).get("pass_rate", 0.0)) == 1.0
        and int(run.get("result", {}).get("errors", 0)) == 0
    )
    if hard_passes != 24:
        errors.append(
            f"candidate hard gates: expected 24/24, got {hard_passes}/24"
        )
    if len(baseline) != 24:
        errors.append(f"baseline matrix: expected 24 runs, got {len(baseline)}")

    semantic = human_review.get("semantic_failures", {})
    candidate_semantic = (
        semantic.get("candidate", []) if isinstance(semantic, dict) else []
    )
    if candidate_semantic:
        errors.append(
            f"candidate semantic failures: expected 0, got {len(candidate_semantic)}"
        )

    global_medians = human_review.get("global_medians", {})
    try:
        candidate_global = float(global_medians["candidate"]["overall"])
        baseline_global = float(global_medians["baseline"]["overall"])
    except (KeyError, TypeError, ValueError):
        errors.append("human review lacks global overall medians")
        candidate_global = baseline_global = 0.0
    if candidate_global < baseline_global:
        errors.append(
            "candidate global soft median is below baseline: "
            f"{candidate_global} < {baseline_global}"
        )

    per_case = human_review.get("per_case", {})
    if not isinstance(per_case, dict) or len(per_case) != 8:
        errors.append("human review requires medians for all 8 cases")
    else:
        for eval_name, values in per_case.items():
            try:
                candidate_median = float(values["candidate"]["overall"])
                baseline_median = float(values["baseline"]["overall"])
            except (KeyError, TypeError, ValueError):
                errors.append(f"case median missing for {eval_name}")
                continue
            if candidate_median < baseline_median - 1:
                errors.append(
                    f"case soft median drops by more than one point: {eval_name}"
                )

    measurable_improvement = False
    for eval_name in candidate_evals:
        candidate_case = [
            run for run in candidate if str(run.get("eval_name")) == eval_name
        ]
        baseline_case = [
            run for run in baseline if str(run.get("eval_name")) == eval_name
        ]
        candidate_all_pass = len(candidate_case) == 3 and all(
            float(run["result"].get("pass_rate", 0.0)) == 1.0
            for run in candidate_case
        )
        baseline_has_failure = any(
            float(run["result"].get("pass_rate", 0.0)) < 1.0
            for run in baseline_case
        )
        if candidate_all_pass and baseline_has_failure:
            measurable_improvement = True
            break
        case_review = per_case.get(eval_name, {}) if isinstance(per_case, dict) else {}
        preferences = (
            case_review.get("preference_counts", {})
            if isinstance(case_review, dict)
            else {}
        )
        baseline_passes = sum(
            float(run["result"].get("pass_rate", 0.0)) == 1.0
            for run in baseline_case
        )
        candidate_passes = sum(
            float(run["result"].get("pass_rate", 0.0)) == 1.0
            for run in candidate_case
        )
        if (
            int(preferences.get("candidate", 0)) >= 2
            and candidate_passes >= baseline_passes
            and candidate_all_pass
        ):
            measurable_improvement = True
            break
    if not measurable_improvement:
        errors.append("no case satisfies the measurable-improvement rule")
    return errors


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
    network_provider = load_network_provider(
        Path(args.provider_config).expanduser().resolve()
    )
    print(f"Network provider hash: {_provider_hash(network_provider)}")
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
                network_provider=network_provider,
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


def benchmark_command(args: argparse.Namespace) -> int:
    benchmark = aggregate_workspace(Path(args.workspace), model=args.model)
    output = Path(args.output)
    _write_json(output, benchmark)
    write_benchmark_markdown(benchmark, output.with_suffix(".md"))
    print(f"Benchmark written: {output}")
    return 0


def prepare_review_command(args: argparse.Namespace) -> int:
    mapping = prepare_blind_review(
        Path(args.workspace),
        Path(args.review_workspace),
        seed=args.seed,
        baseline_workspace=(
            Path(args.baseline_workspace)
            if args.baseline_workspace is not None
            else None
        ),
        blind_map_path=Path(args.blind_map),
    )
    print(f"Prepared {len(mapping['pairs'])} anonymous review pairs")
    return 0


def score_review_command(args: argparse.Namespace) -> int:
    benchmark = _load_json(Path(args.benchmark), "benchmark")
    human_review = parse_review_feedback(
        Path(args.feedback), Path(args.blind_map)
    )
    reviewed = apply_human_review(benchmark, human_review)
    human_output = Path(args.human_output)
    benchmark_output = Path(args.benchmark_output)
    _write_json(human_output, human_review)
    _write_json(benchmark_output, reviewed)
    write_benchmark_markdown(reviewed, benchmark_output.with_suffix(".md"))
    print(f"Scored {human_review['pairs_reviewed']} review pairs")
    return 0


def check_release_command(args: argparse.Namespace) -> int:
    benchmark = _load_json(Path(args.benchmark), "benchmark")
    human_review = _load_json(Path(args.human_review), "human review")
    errors = check_release_gate(benchmark, human_review)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Release gate passed")
    return 0


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
    run_parser.add_argument(
        "--provider-config",
        default=str(Path.home() / ".codex" / "config.toml"),
        help=(
            "Read only the active model provider's allowlisted transport "
            "fields from this TOML file"
        ),
    )
    run_parser.add_argument("--runs", type=int, default=1)
    run_parser.add_argument("--timeout-seconds", type=int, default=900)
    run_parser.add_argument("--resume", action="store_true")
    run_parser.set_defaults(handler=run_command)

    benchmark_parser = subparsers.add_parser(
        "benchmark", help="aggregate a behavior-evaluation workspace"
    )
    benchmark_parser.add_argument("--workspace", required=True)
    benchmark_parser.add_argument("--output", required=True)
    benchmark_parser.add_argument("--model", required=True)
    benchmark_parser.set_defaults(handler=benchmark_command)

    review_parser = subparsers.add_parser(
        "prepare-review", help="prepare anonymous paired review outputs"
    )
    review_parser.add_argument("--workspace", required=True)
    review_parser.add_argument("--baseline-workspace")
    review_parser.add_argument("--review-workspace", required=True)
    review_parser.add_argument("--blind-map", required=True)
    review_parser.add_argument("--seed", type=int, required=True)
    review_parser.set_defaults(handler=prepare_review_command)

    score_parser = subparsers.add_parser(
        "score-review", help="parse and apply anonymous review feedback"
    )
    score_parser.add_argument("--feedback", required=True)
    score_parser.add_argument("--blind-map", required=True)
    score_parser.add_argument("--benchmark", required=True)
    score_parser.add_argument("--human-output", required=True)
    score_parser.add_argument("--benchmark-output", required=True)
    score_parser.set_defaults(handler=score_review_command)

    release_parser = subparsers.add_parser(
        "check-release", help="enforce the v1.2 behavior release gate"
    )
    release_parser.add_argument("--benchmark", required=True)
    release_parser.add_argument("--human-review", required=True)
    release_parser.set_defaults(handler=check_release_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if getattr(args, "runs", 1) < 1:
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
