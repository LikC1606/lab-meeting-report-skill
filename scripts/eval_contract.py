from __future__ import annotations

import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path


class ContractError(ValueError):
    pass


TOP_LEVEL_KEYS = {
    "schema_version",
    "case_id",
    "layer",
    "language",
    "report_mode",
    "task_file",
    "input_root",
    "expected_report",
    "numbers",
    "derived_numbers",
    "required_evidence",
    "negative_results",
    "conflicts",
    "forbidden_patterns",
    "required_sources",
    "forbidden_sources",
    "skipped_sources",
    "preservation_markers",
}
COLLECTION_FIELDS = {
    "numbers",
    "derived_numbers",
    "required_evidence",
    "negative_results",
    "conflicts",
    "forbidden_patterns",
    "skipped_sources",
}
NUMBER_KEYS = {"id", "value", "unit", "required", "source"}
DERIVED_KEYS = {
    "id",
    "value",
    "unit",
    "required",
    "operation",
    "operands",
}
TERM_RULE_KEYS = {"id", "all_of"}
CONFLICT_KEYS = {"id", "values", "source_tokens", "max_distance"}
PATTERN_KEYS = {"id", "pattern"}
CASE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DERIVED_OPERAND_COUNTS = {
    "add": (1, None),
    "subtract": (2, 2),
    "multiply": (1, None),
    "divide": (2, 2),
    "mean": (1, None),
    "percent-change": (2, 2),
}


def _require_mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    return value


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value


def _validate_exact_keys(
    value: dict[str, object], expected: set[str], field: str
) -> None:
    missing = expected - set(value)
    unexpected = set(value) - expected
    if missing:
        raise ContractError(f"{field} missing fields: {', '.join(sorted(missing))}")
    if unexpected:
        raise ContractError(
            f"{field} has unexpected fields: {', '.join(sorted(unexpected))}"
        )


def safe_relative_path(value: str, field: str) -> Path:
    path = Path(_require_string(value, field))
    if path.is_absolute() or path.drive or ".." in path.parts:
        raise ContractError(f"{field} must be a safe relative path: {value}")
    if path == Path("."):
        raise ContractError(f"{field} must be a non-empty relative path")
    return path


def _validate_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ContractError(f"{field} must be an array")
    return value


def _validate_unique_ids(items: list[object], field: str) -> None:
    ids: list[str] = []
    for index, raw in enumerate(items):
        item = _require_mapping(raw, f"{field}[{index}]")
        ids.append(_require_string(item.get("id"), f"{field}[{index}].id"))
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise ContractError(f"{field} has duplicate IDs: {', '.join(duplicates)}")


def _decimal(value: object, field: str) -> Decimal:
    try:
        number = Decimal(_require_string(value, field))
    except InvalidOperation as exc:
        raise ContractError(f"{field} must be a decimal string") from exc
    if not number.is_finite():
        raise ContractError(f"{field} must be finite")
    return number


def _calculate_derived(operation: str, operands: list[Decimal]) -> Decimal:
    if operation == "add":
        return sum(operands, Decimal("0"))
    if operation == "subtract":
        return operands[0] - operands[1]
    if operation == "multiply":
        return math.prod(operands)
    if operation == "divide":
        if operands[1] == 0:
            raise ContractError("derived divide operand cannot be zero")
        return operands[0] / operands[1]
    if operation == "mean":
        return sum(operands, Decimal("0")) / Decimal(len(operands))
    if operation == "percent-change":
        if operands[1] == 0:
            raise ContractError("percent-change baseline cannot be zero")
        return (operands[0] - operands[1]) / operands[1]
    raise ContractError(f"unsupported derived operation: {operation}")


def _validate_number_rules(
    data: dict[str, object], case_root: Path
) -> None:
    numbers = _validate_list(data["numbers"], "numbers")
    _validate_unique_ids(numbers, "numbers")
    for index, raw in enumerate(numbers):
        item = _require_mapping(raw, f"numbers[{index}]")
        _validate_exact_keys(item, NUMBER_KEYS, f"numbers[{index}]")
        _decimal(item["value"], f"numbers[{index}].value")
        _require_string(item["unit"], f"numbers[{index}].unit")
        if not isinstance(item["required"], bool):
            raise ContractError(f"numbers[{index}].required must be boolean")
        source = safe_relative_path(str(item["source"]), f"numbers[{index}].source")
        if not (case_root / source).is_file():
            raise ContractError(f"numbers[{index}].source not found: {source.as_posix()}")

    derived = _validate_list(data["derived_numbers"], "derived_numbers")
    _validate_unique_ids(derived, "derived_numbers")
    number_ids = {str(_require_mapping(item, "number")["id"]) for item in numbers}
    derived_ids = {
        str(_require_mapping(item, "derived number")["id"]) for item in derived
    }
    overlap = sorted(number_ids & derived_ids)
    if overlap:
        raise ContractError(f"numeric rule IDs must be unique: {', '.join(overlap)}")

    for index, raw in enumerate(derived):
        item = _require_mapping(raw, f"derived_numbers[{index}]")
        _validate_exact_keys(item, DERIVED_KEYS, f"derived_numbers[{index}]")
        declared = _decimal(item["value"], f"derived_numbers[{index}].value")
        _require_string(item["unit"], f"derived_numbers[{index}].unit")
        if not isinstance(item["required"], bool):
            raise ContractError(
                f"derived_numbers[{index}].required must be boolean"
            )
        operation = _require_string(
            item["operation"], f"derived_numbers[{index}].operation"
        )
        if operation not in DERIVED_OPERAND_COUNTS:
            raise ContractError(f"unsupported derived operation: {operation}")
        raw_operands = _validate_list(
            item["operands"], f"derived_numbers[{index}].operands"
        )
        minimum, maximum = DERIVED_OPERAND_COUNTS[operation]
        if len(raw_operands) < minimum or (
            maximum is not None and len(raw_operands) > maximum
        ):
            raise ContractError(
                f"derived_numbers[{index}].operands has invalid length for {operation}"
            )
        operands = [
            _decimal(value, f"derived_numbers[{index}].operands")
            for value in raw_operands
        ]
        with localcontext() as context:
            context.prec = 40
            calculated = _calculate_derived(operation, operands)
        quantum = Decimal(1).scaleb(declared.as_tuple().exponent)
        if calculated.quantize(quantum) != declared:
            raise ContractError(
                f"derived_numbers[{index}].value does not match {operation}: "
                f"declared {declared}, calculated {calculated}"
            )


def _validate_term_rules(data: dict[str, object], field: str) -> None:
    rules = _validate_list(data[field], field)
    _validate_unique_ids(rules, field)
    for index, raw in enumerate(rules):
        item = _require_mapping(raw, f"{field}[{index}]")
        _validate_exact_keys(item, TERM_RULE_KEYS, f"{field}[{index}]")
        terms = _validate_list(item["all_of"], f"{field}[{index}].all_of")
        if not terms:
            raise ContractError(f"{field}[{index}].all_of cannot be empty")
        for term_index, term in enumerate(terms):
            _require_string(term, f"{field}[{index}].all_of[{term_index}]")


def _validate_conflicts(data: dict[str, object]) -> None:
    conflicts = _validate_list(data["conflicts"], "conflicts")
    _validate_unique_ids(conflicts, "conflicts")
    for index, raw in enumerate(conflicts):
        item = _require_mapping(raw, f"conflicts[{index}]")
        _validate_exact_keys(item, CONFLICT_KEYS, f"conflicts[{index}]")
        for key in ("values", "source_tokens"):
            values = _validate_list(item[key], f"conflicts[{index}].{key}")
            if len(values) < 2:
                raise ContractError(f"conflicts[{index}].{key} needs at least two values")
            for value_index, value in enumerate(values):
                _require_string(
                    value, f"conflicts[{index}].{key}[{value_index}]"
                )
        if not isinstance(item["max_distance"], int) or item["max_distance"] < 1:
            raise ContractError(f"conflicts[{index}].max_distance must be positive")


def _validate_patterns(data: dict[str, object]) -> None:
    patterns = _validate_list(data["forbidden_patterns"], "forbidden_patterns")
    _validate_unique_ids(patterns, "forbidden_patterns")
    for index, raw in enumerate(patterns):
        item = _require_mapping(raw, f"forbidden_patterns[{index}]")
        _validate_exact_keys(item, PATTERN_KEYS, f"forbidden_patterns[{index}]")
        pattern = _require_string(
            item["pattern"], f"forbidden_patterns[{index}].pattern"
        )
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error as exc:
            raise ContractError(
                f"forbidden_patterns[{index}].pattern is invalid: {exc}"
            ) from exc


def _validate_string_list(data: dict[str, object], field: str) -> None:
    values = _validate_list(data[field], field)
    for index, value in enumerate(values):
        _require_string(value, f"{field}[{index}]")


def load_manifest(path: Path) -> dict[str, object]:
    path = path.resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read manifest {path}: {exc}") from exc
    data = _require_mapping(data, "manifest")
    _validate_exact_keys(data, TOP_LEVEL_KEYS, "manifest")
    if data["schema_version"] != 1:
        raise ContractError("schema_version must be 1")

    case_id = _require_string(data["case_id"], "case_id")
    if not CASE_ID_RE.fullmatch(case_id):
        raise ContractError("case_id must be lowercase kebab-case")
    if path.parent.name != case_id:
        raise ContractError(
            f"case_id {case_id} does not match directory {path.parent.name}"
        )
    if data["layer"] not in {"composition", "end-to-end"}:
        raise ContractError("layer must be composition or end-to-end")
    if data["language"] not in {"en", "zh-CN"}:
        raise ContractError("language must be en or zh-CN")
    if data["report_mode"] != "research-progress":
        raise ContractError("report_mode must be research-progress")

    task_file = safe_relative_path(str(data["task_file"]), "task_file")
    input_root = safe_relative_path(str(data["input_root"]), "input_root")
    safe_relative_path(str(data["expected_report"]), "expected_report")
    if not (path.parent / task_file).is_file():
        raise ContractError(f"task_file not found: {task_file.as_posix()}")
    if not (path.parent / input_root).is_dir():
        raise ContractError(f"input_root not found: {input_root.as_posix()}")

    for field in COLLECTION_FIELDS:
        _validate_list(data[field], field)
    _validate_number_rules(data, path.parent)
    _validate_term_rules(data, "required_evidence")
    _validate_term_rules(data, "negative_results")
    _validate_term_rules(data, "skipped_sources")
    _validate_conflicts(data)
    _validate_patterns(data)
    for field in ("required_sources", "forbidden_sources"):
        _validate_string_list(data, field)
        for index, value in enumerate(data[field]):
            safe_relative_path(str(value), f"{field}[{index}]")
    _validate_string_list(data, "preservation_markers")
    return data


def iter_case_manifests(cases_root: Path) -> list[Path]:
    manifests = sorted(cases_root.glob("*/manifest.json"))
    seen: set[str] = set()
    for path in manifests:
        case_id = str(load_manifest(path)["case_id"])
        if case_id in seen:
            raise ContractError(f"duplicate case ID: {case_id}")
        seen.add(case_id)
    return manifests


def hash_tree(root: Path) -> str:
    root = root.resolve()
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            raise ContractError(f"hash_tree rejects symlink: {path}")
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()
