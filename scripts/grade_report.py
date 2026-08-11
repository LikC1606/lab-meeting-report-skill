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

try:
    from scripts.eval_contract import ContractError, load_manifest
except ModuleNotFoundError:
    from eval_contract import ContractError, load_manifest


@dataclass(frozen=True)
class Expectation:
    text: str
    passed: bool
    evidence: str


NUMBER_RE = re.compile(
    r"(?<![\w.])(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)\s*(%)?"
)
MARP_FRONTMATTER_RE = re.compile(
    r"\A---\r?\n(?P<yaml>.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL
)
PRESENTATION_ROLE_PATTERNS = {
    "evidence": re.compile(
        r"(?:\*\*Evidence:\*\*|(?:Evidence|证据|来源)\s*[：:])",
        re.IGNORECASE,
    ),
    "say": re.compile(
        r"(?:\*\*Say:\*\*|(?:Say|讲述|讲述要点|演讲提示)\s*(?:[（(:：]|--?>))",
        re.IGNORECASE,
    ),
    "discuss": re.compile(
        r"(?:\*\*Discuss:\*\*|(?:Discuss|讨论|讨论问题|讨论入口|需组会决定|收束问题)\s*[：:])",
        re.IGNORECASE,
    ),
}
NEXT_STEP_PATTERN = re.compile(
    r"(?:next\s+steps?|next-week|下一步|下周|行动|交付)", re.IGNORECASE
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


def _markdown_reference_labels(text: str) -> set[str]:
    labels: set[str] = set()
    in_reference_section = False
    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading:
            title = heading.group(1)
            in_reference_section = (
                re.match(
                    r"(?:sources?|references?)(?:\s|$)",
                    title,
                    re.IGNORECASE,
                )
                is not None
                or any(
                    marker in title
                    for marker in ("来源", "参考文献", "参考资料")
                )
            )
            continue
        if not in_reference_section:
            continue
        item = re.match(r"^\s*(\d+)[.)]\s+", line)
        if item:
            labels.add(item.group(1))
    return labels


def _defined_markdown_citation_spans(text: str) -> list[tuple[int, int]]:
    labels = _markdown_reference_labels(text)
    if not labels:
        return []
    spans: list[tuple[int, int]] = []
    for citation in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", text):
        cited = set(re.findall(r"\d+", citation.group(1)))
        if cited <= labels:
            spans.append((citation.start(), citation.end()))
    return spans


def _source_locator_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    pattern = re.compile(
        r"(?:[\w./-]+\.(?:md|txt|csv|tsv|json|ya?ml|pdf|xlsx?))"
        r":(?P<locator>L?\d+(?:(?:-|,)L?\d+)*)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        spans.append(match.span("locator"))
    return spans


def extract_numbers(text: str) -> list[tuple[str, Decimal]]:
    values: list[tuple[str, Decimal]] = []
    normalized = unicodedata.normalize("NFKC", text)
    ignored_spans = [
        *_defined_markdown_citation_spans(normalized),
        *_source_locator_spans(normalized),
    ]
    for match in NUMBER_RE.finditer(normalized):
        if _is_markdown_ordered_list_marker(
            normalized, match
        ) or _is_hyphenated_technical_identifier(normalized, match):
            continue
        if any(
            start <= match.start() and match.end() <= end
            for start, end in ignored_spans
        ):
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
    normalized = (
        unicodedata.normalize("NFKC", text)
        .replace("\\", "/")
        .replace("`", "")
    )
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


def _forbidden_match_is_negated(text: str, match: re.Match[str]) -> bool:
    question_end = text.find("?", match.end())
    statement_ends = [
        position
        for boundary in (".", "!", ";", "\n")
        if (position := text.find(boundary, match.end())) != -1
    ]
    if question_end != -1 and (
        not statement_ends or question_end < min(statement_ends)
    ):
        return True
    clause_start = max(
        text.rfind(boundary, 0, match.start())
        for boundary in (".", "!", "?", ";")
    )
    prefix = text[clause_start + 1 : match.start()]
    contrasts = list(
        re.finditer(r"\b(?:but|however|yet|nevertheless)\b", prefix)
    )
    if contrasts:
        prefix = prefix[contrasts[-1].end() :]
    context = prefix[-160:]
    english_negation = re.search(
        r"\b(?:"
        r"(?:does|do|did|is|are|was|were|has|have|had|can|could|would|should)"
        r"\s+not|cannot|can't|neither|no evidence|without evidence|"
        r"fails? to|insufficient to"
        r")\b",
        context,
    )
    chinese_negation = re.search(
        r"(?:不(?:能|足以|支持|代表|表示|意味着|声称|主张|预设|排序)|"
        r"无(?:法|证据)|"
        r"没有(?:足够)?(?:证据)?|未(?:能|提供)?|缺(?:乏|少))"
        r"[^。！？；\n]{0,48}$",
        context,
    )
    return english_negation is not None or chinese_negation is not None


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
        match = next(
            (
                candidate
                for candidate in pattern.finditer(normalized)
                if not _forbidden_match_is_negated(normalized, candidate)
            ),
            None,
        )
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


def _presentation_slides(text: str) -> tuple[str | None, list[str]]:
    frontmatter = MARP_FRONTMATTER_RE.match(text)
    if frontmatter is None:
        return None, []
    slides = [
        slide.strip()
        for slide in re.split(r"(?m)^---\s*$", text[frontmatter.end() :])
        if slide.strip()
    ]
    return frontmatter.group("yaml"), slides


def _presentation_numeric_text(text: str) -> str:
    frontmatter = MARP_FRONTMATTER_RE.match(text)
    body = text[frontmatter.end() :] if frontmatter else text
    body = re.sub(r"#L\d+(?:-L?\d+)?", "", body)
    body = re.sub(r"第\s*\d+(?:\s*[-、至]\s*\d+)?\s*行", "", body)
    body = re.sub(r"第\s*\d+(?:\s*[-、至]\s*\d+)?\s*(?:页|张)", "", body)
    body = re.sub(
        r"\bslides?\s+\d+(?:\s*[-–]\s*\d+)?\b",
        "",
        body,
        flags=re.IGNORECASE,
    )
    body = re.sub(r"[（(]\s*\d+\s*:\s*\d+\s*[）)]", "", body)
    return body


def presentation_expectations(
    text: str,
    manifest: dict[str, object],
    report_text: str | None = None,
) -> list[Expectation]:
    frontmatter, slides = _presentation_slides(text)
    duration_source = report_text or text
    duration_match = re.search(
        r"(?:时长|汇报时间|duration)\D{0,20}(\d+)\s*(?:分钟|min(?:ute)?s?)",
        duration_source,
        re.IGNORECASE,
    )
    duration = int(duration_match.group(1)) if duration_match else None
    minimum_slides, maximum_slides = (
        (5, 7) if duration is not None and duration <= 10 else (2, 12)
    )
    expectations = [
        Expectation(
            "presentation:marp-frontmatter",
            frontmatter is not None
            and re.search(r"(?mi)^marp:\s*true\s*$", frontmatter) is not None,
            "Marp is enabled"
            if frontmatter is not None
            and re.search(r"(?mi)^marp:\s*true\s*$", frontmatter) is not None
            else "missing valid Marp frontmatter",
        ),
        Expectation(
            "presentation:slide-count",
            minimum_slides <= len(slides) <= maximum_slides,
            f"slide count: {len(slides)}; "
            f"expected {minimum_slides}-{maximum_slides}",
        ),
    ]

    for index, slide in enumerate(slides, start=1):
        for role, pattern in PRESENTATION_ROLE_PATTERNS.items():
            found = pattern.search(slide) is not None
            expectations.append(
                Expectation(
                    f"presentation:slide-{index}:{role}",
                    found,
                    f"{role} marker found" if found else f"{role} marker missing",
                )
            )

    final_has_next_step = bool(slides and NEXT_STEP_PATTERN.search(slides[-1]))
    expectations.append(
        Expectation(
            "presentation:final-next-step",
            final_has_next_step,
            "final slide contains a next-step or action marker"
            if final_has_next_step
            else "final slide lacks a next-step or action marker",
        )
    )

    allowed = {
        _declared_value(rule, f"numbers[{index}]")
        for index, rule in enumerate(manifest["numbers"])
    }
    for index, rule in enumerate(manifest["derived_numbers"]):
        allowed.add(_declared_value(rule, f"derived_numbers[{index}]"))
    unexpected = [
        token
        for token, value in extract_numbers(_presentation_numeric_text(text))
        if value not in allowed
    ]
    expectations.append(
        Expectation(
            "presentation:numeric-closed-world",
            not unexpected,
            "unexpected numeric tokens: " + ", ".join(unexpected)
            if unexpected
            else "all presentation numeric tokens are declared",
        )
    )

    normalized = normalize_text(text)
    for field, prefix in (
        ("required_evidence", "evidence"),
        ("negative_results", "negative"),
    ):
        for rule in manifest[field]:
            result = term_rule_expectation(prefix, rule, normalized)
            expectations.append(
                Expectation(
                    f"presentation:{result.text}", result.passed, result.evidence
                )
            )
    for source in manifest["required_sources"]:
        target = normalize_text(str(source))
        expectations.append(
            Expectation(
                f"presentation:required-source:{source}",
                target in normalized,
                "source found" if target in normalized else "source missing",
            )
        )
    for rule in manifest["forbidden_patterns"]:
        pattern = re.compile(str(rule["pattern"]), re.IGNORECASE)
        match = next(
            (
                candidate
                for candidate in pattern.finditer(normalized)
                if not _forbidden_match_is_negated(normalized, candidate)
            ),
            None,
        )
        expectations.append(
            Expectation(
                f"presentation:forbidden:{rule['id']}",
                match is None,
                f"forbidden pattern found: {match.group(0)}"
                if match
                else "forbidden pattern absent",
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


def grade_workflow(
    report_text: str,
    presentation_text: str | None,
    manifest: dict[str, object],
) -> dict[str, object]:
    expectations = numeric_expectations(report_text, manifest)
    expectations.extend(semantic_expectations(report_text, manifest))
    combined_text = report_text
    if presentation_text is not None:
        expectations.extend(
            presentation_expectations(
                presentation_text, manifest, report_text=report_text
            )
        )
        combined_text += "\n" + presentation_text
    return build_grading(expectations, combined_text)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade a generated lab report")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--presentation", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        manifest = load_manifest(args.manifest)
        report = args.report.read_text(encoding="utf-8", errors="strict")
        presentation = (
            args.presentation.read_text(encoding="utf-8", errors="strict")
            if args.presentation is not None
            else None
        )
        grading = grade_workflow(report, presentation, manifest)
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
