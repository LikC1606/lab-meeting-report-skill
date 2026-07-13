# Lab Meeting Report: Rare-Class Recall Change

> Date: 2026-07-13 | Reporter: [To be supplied] | Report type: Research progress | Project/direction: Rare-class recall evaluation

## Summary

- **Observed result:** Rare-class recall changed from 0.58 to 0.66, an absolute increase of 0.08 (approximately 13.8% relative to 0.58).
- **Interpretation status:** The author attributes the gain to hard negatives, but this is an unverified hypothesis rather than a supported causal conclusion.
- **Evidence gap:** No ablation or significance test was supplied, so neither the cause nor the statistical reliability of the change can be established.
- **Priority next step:** Run a controlled hard-negative ablation with repeated trials and uncertainty estimates.

## Research Objective and Current Hypothesis

- **Objective:** Determine whether the observed rare-class recall improvement is reproducible and attributable to hard negatives.
- **Fact:** Rare-class recall changed from 0.58 to 0.66 in the supplied observation.
- **Hypothesis:** Hard negatives caused the gain. This claim appears only in the author note and has not been tested by an ablation.
- **Success criterion:** A prespecified controlled comparison isolates hard-negative inclusion as the changed factor, reports repeated-run uncertainty, and shows a reproducible recall difference under the same evaluation protocol.

## Results and Evidence

| Comparison | Metric | Earlier value | Later value | Derived change | Source | Evidence boundary |
|---|---|---:|---:|---:|---|---|
| Earlier vs. later result | Rare-class recall | 0.58 | 0.66 | +0.08 absolute; +13.8% relative | `inputs/observations.md` | No sample size, run count, uncertainty, significance test, or experimental setup was supplied. |

The supplied values establish a descriptive increase in rare-class recall. They do not establish statistical significance or identify the intervention responsible for the change.

## Analysis and Confidence

- **Fact:** The reported rare-class recall is higher in the later value than in the earlier value.
- **Interpretation:** The observed difference is consistent with an improvement, conditional on both values having been obtained under a comparable evaluation protocol. Protocol comparability was not documented.
- **Hypothesis:** Hard negatives caused the gain.
- **Alternative explanations:** Other changes between the two evaluations, evaluation variance, data composition, or random variation could explain some or all of the difference. The supplied source does not allow these possibilities to be ranked.
- **Confidence boundary:** Causal attribution and statistical reliability are unresolved because no ablation, significance test, repeated-run results, sample size, or uncertainty estimates were supplied.

## Missing Evidence and Blockers

| Gap | Impact | Status | Needed evidence |
|---|---|---|---|
| Hard-negative ablation | Prevents causal attribution of the recall change | Not supplied | Matched runs with and without hard negatives, holding other factors fixed |
| Statistical or uncertainty analysis | Prevents assessment of whether the observed difference is robust | Not supplied | Repeated-run results or prediction-level data, plus an appropriate uncertainty interval or test |
| Experimental setup and evaluation protocol | Prevents verification that 0.58 and 0.66 are directly comparable | [To be supplied] | Dataset/split, model/configuration, seed policy, metric definition, and all changes between runs |

## Decisions Needed

1. Confirm whether hard-negative inclusion was the only intended difference between the evaluations. Until confirmed, the recall change should be reported as observational rather than causal.
2. Select the repeated-run or resampling procedure and the uncertainty criterion before examining the validation result.

## Next Actions

| Priority | Action | Expected artifact | Success criterion | Dependency or risk |
|---:|---|---|---|---|
| P0 | Document both evaluation configurations and enumerate every difference between them. | Configuration comparison table | All data, model, training, seed, and evaluation differences are recorded; comparability is explicitly resolved. | Original run metadata may be unavailable. |
| P0 | Run a controlled hard-negative ablation under the same evaluation protocol. | Per-run rare-class recall table for matched conditions | The hard-negative condition is the only controlled change, with enough repeated runs to report variability. | Compute/data availability; uncontrolled differences would invalidate attribution. |
| P1 | Quantify uncertainty using a prespecified method appropriate to the available prediction-level or repeated-run data. | Confidence interval and/or test result with method and sample size | The report states the estimate, uncertainty, assumptions, and prespecified decision rule. | The current source contains no raw predictions, sample size, or replicate values. |

## Source

- `inputs/observations.md` - supplied observation and embedded author note; used for the two recall values, the causal hypothesis, and the stated absence of ablation and significance testing.

No external literature or additional project sources were used.
