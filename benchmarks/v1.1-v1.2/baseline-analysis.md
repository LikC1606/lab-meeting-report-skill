# v1.1.0 Baseline Analysis

## Scope and method

- Baseline skill: Git tag `v1.1.0`, commit `76a800c3fdd843b2513ea7270086a05ff7f5c47e`.
- Executor: `gpt-5.6-sol` through Codex CLI `0.144.0-alpha.4`.
- Corpus: eight public synthetic research-progress cases, three runs per case.
- Infrastructure outcome: 24 valid runs, zero infrastructure-invalid runs.
- Review method: deterministic grading plus an inline Codex semantic and transcript audit. The user explicitly declined manual review, so this analysis is not independent human validation.

The benchmark's mean pass rate of `0.799` is an expectation-level average. It must not be read as a run pass rate: all 24 reports failed at least one deterministic hard gate.

## Failure inventory

| Case | Runs | Hard failures | Semantic finding | Root cause |
|---|---|---|---|---|
| `buried-negative-result` | `run-1`, `run-2`, `run-3` | `numeric-closed-world` in 3/3 | Every report retained seed 29 and the timeout, but all introduced undeclared differences; one also added an undeclared relative percentage. | E2, E5 |
| `clean-multiseed` | `run-1`, `run-2`, `run-3` | `numeric-closed-world` in 3/3 | The reports copied required source values but added undeclared margins, deviations, dispersion, and rounded percentages. | E2, E5 |
| `conflicting-results` | `run-1`, `run-2`, `run-3` | `numeric-closed-world` and `evidence:unresolved-authority` in 3/3 | Both source values were retained, yet the reports added an undeclared `0.018` difference and did not state that no authority rule was supplied. | E1, E2, E3 |
| `duplicated-multilingual-notes` | `run-1`, `run-2`, `run-3` | `evidence:duplicate-provenance` in 3/3; numeric and forbidden replication failures in `run-3` | The reports recognized related notes but did not consistently express that they were repeated provenance for one run; `run-3` used the independent-replication wording inside a negation. | E1, P1 |
| `missing-evidence-causal-lure` | `run-1`, `run-2`, `run-3` | causal claim in 3/3; numeric in 3/3; evidence-boundary in 2/3; significance wording in `run-2` | Labels such as “Hypothesis” did not neutralize the sentence “hard negatives caused”; the sentence itself still asserted causality before disclaiming it. Extra effect sizes were also introduced. | E2, E5, P2 |
| `partial-source-failure` | `run-1`, `run-2`, `run-3` | unavailable-source content claim in 3/3; numeric in `run-1` and `run-3` | No secondary result number was invented, but each report characterized internal content of the invalid UTF-8 source instead of keeping the unavailable content unknown. | E1, E5 |
| `safe-existing-report-update` | `run-1`, `run-2`, `run-3` | missing baseline, source, and two manual markers in 3/3; numeric in 2/3 | Transcripts show the agent checked only the destination, found it absent, and reconstructed from `new-results.md` instead of locating the supplied source report under `inputs/reports/`. | E1, E2, E4 |
| `scoped-directory-selection` | `run-1`, `run-2`, `run-3` | `numeric-closed-world` in 3/3 | File selection and provenance were correct, but every report added undeclared differences, margins, or percentages. | E2, E5 |

## Cross-run patterns

- `numeric-closed-world` failed in 17/24 runs after the grader was corrected to exclude Markdown ordered-list markers. The remaining failures contain substantive undeclared calculations or identifiers.
- All three conflict runs, duplicate-note runs, causal-lure runs, partial-source runs, and safe-update runs failed their case-specific boundary.
- The most consequential behavior is the safe-update failure because it removed user-authored content and a baseline value in every repetition.
- `partial-source-failure/run-1` took `1017.845 s` and required a second attempt, making it a resource outlier even though the final run was infrastructure-valid.
- Every inspected transcript read the copied `SKILL.md` and progress template. The failures therefore reflect missing or insufficiently operational instructions rather than skill non-use.

## Grader limitations

The deterministic rules are intentionally conservative. Regex checks do not fully understand negation or section labels, so phrases such as “not statistically significant” or “not two independent replications” can still match a forbidden pattern. Markdown ordered-list markers are excluded from numeric grading, while inline run, seed, priority, and measurement numbers remain checked. These limitations are recorded rather than reinterpreted as fabrication. Candidate reports must nevertheless avoid ambiguous strong wording and undeclared experimental arithmetic, while semantic review checks that a hard pass was not achieved by deleting decision-relevant content.

## Selection decision

The evidence supports all seven predefined blocks: E1-E5 and P1-P2. Each block addresses a distinct failure observed in at least three baseline runs or a release-blocking destructive-update pattern. No rule is selected solely to create a version difference.
