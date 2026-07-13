# Group Meeting Report: Candidate Macro-F1 and Robustness

> Date: 2026-07-13 | Report type: Research progress | Project/direction: Synthetic example

## Summary

- **Verified result:** The reported candidate mean macro-F1 is `0.781`, compared with a baseline macro-F1 of `0.742` (absolute difference: `+0.039`). Source: `inputs/main-results.md`.
- **Decision-relevant failure:** Seed 29 collapsed to macro-F1 `0.603` after a `300 s` timeout. Source: `inputs/archive/note.md`.
- **Current interpretation:** The aggregate candidate result is higher than the reported baseline, but robustness remains unresolved because the supplied evidence contains a severe seed-level failure and does not document the aggregation or evaluation setup.
- **Immediate priority:** Reproduce seed 29 and obtain complete per-seed results before deciding whether the candidate is robust enough to advance.

## Decision Required

Do not treat the candidate's higher reported mean as sufficient evidence for promotion yet. Decide whether to continue evaluation only after a controlled seed 29 rerun and a complete per-seed comparison clarify whether the collapse is reproducible, timeout-induced, or isolated.

## Objective and Current Hypothesis

- **Objective:** Determine whether the candidate improves macro-F1 over the baseline without unacceptable seed-level instability.
- **Facts:** Baseline macro-F1 is `0.742`; candidate mean macro-F1 is `0.781`; seed 29 produced macro-F1 `0.603` after a `300 s` timeout.
- **Hypothesis:** The candidate may improve average macro-F1 but may be unstable for at least some seeds. This remains unverified.
- **Success criterion:** A complete, reproducible per-seed evaluation shows how often failures occur and whether the candidate's advantage persists under the same timeout and evaluation conditions as the baseline.

## Results and Evidence

| Evaluation | Metric | Result | Difference from baseline | Source | Confidence / limitation |
|---|---:|---:|---:|---|---|
| Baseline | macro-F1 | `0.742` | - | `inputs/main-results.md` | Number of runs, seeds, and dispersion are not supplied. |
| Candidate aggregate | mean macro-F1 | `0.781` | `+0.039` absolute | `inputs/main-results.md` | Seeds included, sample size, dispersion, and treatment of failed runs are not supplied. |
| Candidate, seed 29 | macro-F1 | `0.603` | `-0.139` vs. baseline | `inputs/archive/note.md` | Run followed a `300 s` timeout; the source does not establish causality between timeout and score collapse. |

No statistical significance claim can be made from the supplied evidence.

## Analysis and Confidence

- **Fact:** The reported candidate mean exceeds the reported baseline by `0.039` macro-F1.
- **Fact:** Seed 29 is `0.178` below the reported candidate mean and `0.139` below the baseline.
- **Interpretation:** The seed 29 result is large enough to affect the advancement decision even though the aggregate candidate value is higher.
- **Unverified explanations:** The collapse could reflect seed sensitivity, the timeout or its handling, or another undocumented run condition. The supplied sources do not distinguish these possibilities.
- **Confidence boundary:** The evaluation protocol, candidate configuration, baseline comparability, run count, seed list, variance, and aggregation treatment are not documented. Robustness therefore remains unresolved.

## Failed Experiment and Negative Result

| Attempt | Expected outcome | Actual result | Possible cause | Cause ruled out? | Follow-up |
|---|---|---|---|---|---|
| Candidate run with seed 29 | A valid candidate evaluation consistent enough to support a robustness assessment | macro-F1 `0.603` after a `300 s` timeout | Seed sensitivity, timeout behavior, or another undocumented condition | No | Reproduce seed 29 under instrumented, controlled conditions; retain this run in aggregate reporting rather than silently excluding it. |

## Current Blockers

| Blocker | Impact | Existing evidence | Decision/support needed |
|---|---|---|---|
| Missing per-seed results and dispersion | The candidate mean cannot establish robustness. | One failed seed is documented. | Require a complete seed-level result table. |
| Undocumented timeout semantics | It is unclear whether the timeout caused, followed, or merely coincided with the low score. | Seed 29 timed out at `300 s`. | Define timeout handling and record runtime/status consistently. |
| Missing evaluation setup | Baseline and candidate comparability cannot be independently checked. | Only summary metric values are supplied. | Record datasets, splits, configurations, seed set, and aggregation rule. |

## Next Actions

| Priority | Action | Expected artifact | Success criterion | Dependency / risk |
|---:|---|---|---|---|
| P0 | Rerun seed 29 with runtime and timeout instrumentation under the intended evaluation configuration. | Seed 29 run log and macro-F1 result | The run completes with an explicit status, reproducible configuration, runtime, and score. | A repeated timeout may require resource or configuration diagnosis. |
| P0 | Produce a per-seed baseline/candidate comparison, including failed and timed-out runs. | Per-seed results table with mean and dispersion | Every planned seed has a score or explicit failure status, and aggregation treatment is stated. | The planned seed set and baseline run records are not supplied. |
| P1 | Recompute the candidate summary only after defining failure and timeout handling. | Auditable aggregate metrics | The reported aggregate can be traced to the per-seed table and the candidate advantage can be reassessed without hiding seed 29. | The current `0.781` mean may or may not include seed 29; this is unspecified. |

## Sources

- `inputs/main-results.md` - baseline and candidate aggregate macro-F1 values.
- `inputs/archive/note.md` - seed 29 timeout and collapsed macro-F1 result.

## Essential Gaps

The reporter, experimental setup, run count, evaluated seed set, dispersion, timeout policy, aggregation rule, and whether seed 29 is included in the reported candidate mean are not supplied.
