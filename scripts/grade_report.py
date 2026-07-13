from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from scripts.eval_contract import ContractError, load_manifest


@dataclass(frozen=True)
class Expectation:
    text: str
    passed: bool
    evidence: str


NUMBER_RE = re.compile(
    r"(?<![\w.])(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)\s*(%)?"
)


def canonical_decimal(value: str, percent: bool = False) -> Decimal:
    number = Decimal(value.replace(",", ""))
    return number / Decimal("100") if percent else number


def _is_markdown_ordered_list_marker(text: str, match: re.Match[str]) -> bool:
    line_start = text.rfind("\n", 0, match.start()) + 1
    prefix = text[line_start : match.start()]
    suffix = text[match.end() :]
    return not prefix.strip() and re.match(r"[.)]\s", suffix) is not None


def _is_hyphenated_technical_identifier(
    text: str, match: re.Match[str]
) -> bool:
    prefix = text[: match.start()]
    return re.search(r"[A-Za-z][A-Za-z0-9]*-$", prefix) is not None


def extract_numbers(text: str) -> list[tuple[str, Decimal]]:
    values: list[tuple[str, Decimal]] = []
    normalized = unicodedata.normalize("NFKC", text)
    for match in NUMBER_RE.finditer(normalized):
        if _is_markdown_ordered_list_marker(
            normalized, match
        ) or _is_hyphenated_technical_identifier(normalized, match):
            continue
        token = match.group(0).strip()
        raw_value = token.rstrip("% ")
        values.append(
            (token, canonical_decimal(raw_value, percent=bool(match.group(1))))
        )
    return values


def evaluate_derived(rule: dict[str, object]) -> Decimal:
    operands = [Decimal(str(value)) for value in rule["operands"]]
    operation = str(rule["operation"])
    with localcontext() as context:
        context.prec = 40
        if operation == "add":
            return sum(operands, Decimal("0"))
        if operation == "subtract":
            return operands[0] - operands[1]
        if operation == "multiply":
            return math.prod(operands)
        if operation == "divide":
            return operands[0] / operands[1]
        if operation == "mean":
            return sum(operands, Decimal("0")) / Decimal(len(operands))
        if operation == "percent-change":
            return (operands[0] - operands[1]) / operands[1]
    raise ContractError(f"unsupported derived operation: {operation}")


def _declared_value(rule: dict[str, object], field: str) -> Decimal:
    try:
        value = Decimal(str(rule["value"]))
    except (InvalidOperation, KeyError) as exc:
        raise ContractError(f"{field} has invalid decimal value") from exc
    if not value.is_finite():
        raise ContractError(f"{field} must be finite")
    return value


def numeric_expectations(
    text: str, manifest: dict[str, object]
) -> list[Expectation]:
    source_rules = list(manifest["numbers"])
    derived_rules = list(manifest["derived_numbers"])

    allowed: set[Decimal] = set()
    for index, rule in enumerate(source_rules):
        allowed.add(_declared_value(rule, f"numbers[{index}]"))
    for index, rule in enumerate(derived_rules):
        declared = _declared_value(rule, f"derived_numbers[{index}]")
        calculated = evaluate_derived(rule)
        quantum = Decimal(1).scaleb(declared.as_tuple().exponent)
        if calculated.quantize(quantum) != declared:
            raise ContractError(
                f"derived_numbers[{index}] declared {declared}, "
                f"calculated {calculated}"
            )
        allowed.add(declared)

    extracted = extract_numbers(text)
    unexpected = [(token, value) for token, value in extracted if value not in allowed]
    expectations = [
        Expectation(
            "numeric-closed-world",
            not unexpected,
            (
                "unexpected numeric tokens: "
                + ", ".join(token for token, _ in unexpected)
                if unexpected
                else "all numeric tokens are declared"
            ),
        )
    ]

    seen = {value for _, value in extracted}
    for index, rule in enumerate([*source_rules, *derived_rules]):
        if not isinstance(rule.get("required"), bool):
            raise ContractError(f"numeric rule {index} required must be boolean")
        if not rule["required"]:
            continue
        value = _declared_value(rule, f"numeric rule {index}")
        rule_id = str(rule["id"])
        expectations.append(
            Expectation(
                f"required-number:{rule_id}",
                value in seen,
                f"required canonical value: {value}",
            )
        )
    return expectations


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).replace("\\", "/")
    return re.sub(r"\s+", " ", normalized).casefold()


def term_rule_expectation(
    prefix: str, rule: dict[str, object], normalized: str
) -> Expectation:
    missing = [
        str(term)
        for term in rule["all_of"]
        if normalize_text(str(term)) not in normalized
    ]
    return Expectation(
        f"{prefix}:{rule['id']}",
        not missing,
        "missing: " + ", ".join(missing)
        if missing
        else "all required terms found",
    )


def _token_positions(normalized: str, token: str) -> list[int]:
    target = normalize_text(token)
    return [match.start() for match in re.finditer(re.escape(target), normalized)]


def conflict_expectation(
    rule: dict[str, object], normalized: str
) -> Expectation:
    tokens = [
        *[str(value) for value in rule["values"]],
        *[str(value) for value in rule["source_tokens"]],
    ]
    position_groups = [_token_positions(normalized, token) for token in tokens]
    for token, positions in zip(tokens, position_groups, strict=True):
        if not positions:
            return Expectation(
                f"conflict:{rule['id']}",
                False,
                f"missing conflict token: {token}",
            )
    minimum_span = min(
        max(combination) - min(combination)
        for combination in itertools.product(*position_groups)
    )
    maximum = int(rule["max_distance"])
    return Expectation(
        f"conflict:{rule['id']}",
        minimum_span <= maximum,
        f"minimum conflict span: {minimum_span}; maximum: {maximum}",
    )


def semantic_expectations(
    text: str, manifest: dict[str, object]
) -> list[Expectation]:
    normalized = normalize_text(text)
    nfkc_text = unicodedata.normalize("NFKC", text)
    expectations: list[Expectation] = []

    for rule in manifest["required_evidence"]:
        expectations.append(term_rule_expectation("evidence", rule, normalized))
    for rule in manifest["negative_results"]:
        expectations.append(term_rule_expectation("negative", rule, normalized))
    for rule in manifest["skipped_sources"]:
        expectations.append(term_rule_expectation("skipped", rule, normalized))
    for rule in manifest["conflicts"]:
        expectations.append(conflict_expectation(rule, normalized))

    for rule in manifest["forbidden_patterns"]:
        pattern = re.compile(str(rule["pattern"]), re.IGNORECASE)
        match = pattern.search(normalized)
        expectations.append(
            Expectation(
                f"forbidden:{rule['id']}",
                match is None,
                f"forbidden pattern found: {match.group(0)}"
                if match
                else "forbidden pattern absent",
            )
        )

    for source in manifest["required_sources"]:
        target = normalize_text(str(source))
        expectations.append(
            Expectation(
                f"required-source:{source}",
                target in normalized,
                "source found" if target in normalized else "source missing",
            )
        )
    for source in manifest["forbidden_sources"]:
        target = normalize_text(str(source))
        expectations.append(
            Expectation(
                f"forbidden-source:{source}",
                target not in normalized,
                "forbidden source absent"
                if target not in normalized
                else "forbidden source cited",
            )
        )
    for marker in manifest["preservation_markers"]:
        target = unicodedata.normalize("NFKC", str(marker))
        expectations.append(
            Expectation(
                f"preserve:{marker}",
                target in nfkc_text,
                "preservation marker found"
                if target in nfkc_text
                else "preservation marker missing",
            )
        )
    return expectations


def build_grading(
    expectations: list[Expectation], text: str
) -> dict[str, object]:
    passed = sum(item.passed for item in expectations)
    failed = len(expectations) - passed
    return {
        "hard_pass": failed == 0,
        "expectations": [asdict(item) for item in expectations],
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": len(expectations),
            "pass_rate": passed / len(expectations) if expectations else 1.0,
        },
        "execution_metrics": {
            "total_tool_calls": 0,
            "errors_encountered": 0,
            "output_chars": len(text),
        },
    }


def grade_text(text: str, manifest: dict[str, object]) -> dict[str, object]:
    expectations = numeric_expectations(text, manifest)
    expectations.extend(semantic_expectations(text, manifest))
    return build_grading(expectations, text)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade a generated lab report")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        manifest = load_manifest(args.manifest)
        report = args.report.read_text(encoding="utf-8", errors="strict")
        grading = grade_text(report, manifest)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(grading, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (ContractError, OSError, UnicodeDecodeError) as exc:
        print(f"Grading infrastructure error: {exc}", file=sys.stderr)
        return 2

    if grading["hard_pass"]:
        print("Hard gates passed")
        return 0
    failed = [
        item["text"] for item in grading["expectations"] if not item["passed"]
    ]
    print("Hard gates failed: " + ", ".join(failed), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
