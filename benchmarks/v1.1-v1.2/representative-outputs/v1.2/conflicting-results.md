# Lab Meeting Report: `run-alpha` Candidate Evaluation

> Date: 2026-07-13 | Presenter: To be supplied | Report type: Research progress | Project/direction: Candidate evaluation

## Summary

- **Core result:** Two supplied sources describe `run-alpha` with `500 samples`, but they report different candidate macro-F1 values: `0.824` in `inputs/run-log.md` and `0.842` in `inputs/summary.csv`.
- **Current assessment:** The candidate result is unresolved because the sources conflict and no source-authority rule was supplied.
- **Next step:** Trace both values to their generating artifacts and produce a reconciled record that preserves the original provenance.

## Decision Needed

Decide which evidence rule should govern the canonical value for `run-alpha` after the generating artifacts are inspected. The current inputs provide no authority or precedence rule, so neither value can be selected from the supplied evidence alone.

## Objective and Current Hypothesis

- **Objective:** Establish the supported candidate macro-F1 result for `run-alpha`.
- **Source facts:** `run-alpha` used `500 samples`. The Markdown run log reports candidate macro-F1 `0.824`; the CSV summary reports `macro_f1` `0.842`.
- **Interpretation:** The supplied record is internally inconsistent for the decision-relevant metric.
- **Hypothesis:** One value may reflect a transcription, export, or evaluation-version difference, but no evidence identifying the cause was supplied.
- **Success criterion:** A reconciled record identifies the supported value and documents an explicit provenance or authority rule.

## Experimental Setup

| Item | Supplied detail | Source |
|---|---|---|
| Run identifier | `run-alpha` | `inputs/run-log.md`; `inputs/summary.csv` |
| Samples | `500` | `inputs/run-log.md`; `inputs/summary.csv` |
| Metric | candidate macro-F1 / `macro_f1` | `inputs/run-log.md`; `inputs/summary.csv` |
| Model, dataset, split, seed, code version, and evaluation procedure | To be supplied | Not present in the supplied sources |

The two files are repeated provenance for the same run, not an independent replication. No additional run identifier, seed label, or repetition was supplied.

## Results and Evidence

| Run | Samples | Metric | Reported result | Source | Evidence status |
|---|---:|---|---:|---|---|
| `run-alpha` | `500` | candidate macro-F1 | `0.824` | `inputs/run-log.md` | Source fact; conflicts with the CSV summary |
| `run-alpha` | `500` | `macro_f1` | `0.842` | `inputs/summary.csv` | Source fact; conflicts with the Markdown run log |

These values remain unresolved. No authority rule was supplied, and the report does not average, choose between, or otherwise reconcile them.

## Reliability and Limitations

- **Fact:** Both sources agree on the run identifier and sample count.
- **Fact:** The decision-relevant metric values conflict.
- **Interpretation:** The conflict prevents a supported canonical macro-F1 claim for `run-alpha`.
- **Uncertainty:** The supplied evidence does not establish why the values differ or which should take precedence.
- No independent replication was supplied.
- No significance test was supplied; significance is untested.
- No ablation or isolating check was supplied.
- No variance, confidence interval, baseline, acceptance threshold, or evaluation configuration was supplied.

## Failed Experiments and Negative Evidence

No failed experiment was documented in the supplied sources. The unresolved `0.824` versus `0.842` conflict is retained as negative evidence because it blocks selection of a canonical result.

## Current Blocker

| Blocker | Impact | Evidence available | Support or decision needed |
|---|---|---|---|
| Conflicting macro-F1 values for `run-alpha` | A single supported candidate result cannot be reported | Both source records, with no authority rule | Generating artifacts and an explicit precedence rule |

## Next Actions

| Priority | Action | Expected artifact | Success criterion | Dependency or risk |
|---:|---|---|---|---|
| P0 | Trace `0.824` and `0.842` to their generating evaluation outputs and configurations | Provenance note linking each value to its origin | Each value has a documented origin; discrepancies are identified without overwriting either source record | Original evaluation outputs and configurations may be unavailable |
| P0 | Define and apply a source-authority rule | Reconciled `run-alpha` result record | The canonical value is supported by an explicit rule and the conflicting value remains documented | Requires project-owner decision if provenance is inconclusive |
| P1 | Record the missing evaluation metadata | Run metadata record | Model, dataset, split, seed, code version, and evaluation procedure are present or explicitly marked unavailable | Historical metadata may be incomplete |
| P1 | Repeat the evaluation under a fixed, recorded configuration | New evaluation output with a distinct run identifier | The output contains the run identifier, sample count, metric definition, value, and configuration | A new run would be new evidence, not retroactive resolution of the original conflict |

## Sources

- `inputs/run-log.md`
- `inputs/summary.csv`

No source was skipped or unreadable.
