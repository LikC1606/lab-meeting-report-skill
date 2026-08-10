# Synthetic example: lab meeting research progress report

> All names, data, paths, and results in this report are synthetic and exist only to demonstrate the skill workflow.

> Date: 2026-07-12 | Report type: Research progress | Project: Low-resource intent classification

## Summary

- **Validated progress:** class-aware retrieval plus a reranker increased mean macro-F1 from 0.712 to 0.757 across three seeds.
- **Cost:** median latency increased from 18.2 ms to 19.4 ms, a 6.6% increase that remains inside the 10% project limit.
- **Negative result:** class-wide paraphrase augmentation reduced macro-F1 to 0.691, with the largest precision loss on rare classes.
- **Next decision:** test retrieval without the reranker before attributing the gain to either component.

## Decision Requested

Prioritize the latency ablation first. It directly tests whether retrieval alone can retain most of the quality gain while meeting the stricter 19.0 ms next-step target. Manual error review should continue in parallel, but only 45 of 120 predictions are currently labeled, so it cannot yet support a failure taxonomy.

## Objective And Current Hypothesis

- **Objective:** improve macro-F1 without increasing median inference latency by more than 10%.
- **Fact:** the combined retrieval-reranker system reached mean macro-F1 0.757 over seeds 11, 22, and 33.
- **Interpretation:** the combined system improves class-balanced performance relative to the 0.712 baseline.
- **Hypothesis:** retrieval provides most of the gain, while the reranker contributes disproportionately to latency. This has not been tested.

## Method

| Component | Baseline | New experiment |
|---|---|---|
| Encoder | Frozen | Frozen |
| Classifier | Linear | Linear |
| Retrieval | None | Class-aware retrieval |
| Reranker | None | Lightweight reranker |
| Evaluation | Macro-F1, median latency | Macro-F1 over 3 seeds, median latency |

## Results And Evidence

| Experiment | Seeds | Macro-F1 | Median latency | Evidence |
|---|---:|---:|---:|---|
| Frozen encoder baseline | Not supplied | 0.712 | 18.2 ms | `results/baseline.csv` |
| Retrieval + reranker | 11, 22, 33 | **0.757 mean** | 19.4 ms | `results/retrieval_reranker.csv` |
| Paraphrase all classes | Not supplied | 0.691 | Not supplied | `results/paraphrase_all_classes.csv` |

Individual retrieval-reranker seed results were 0.758, 0.764, and 0.749. The supplied notes do not include variance estimates, significance tests, or repeated baseline seeds, so statistical significance is not claimed.

## Analysis And Confidence

- **Fact:** the combined system improved the supplied macro-F1 by 0.045 absolute.
- **Fact:** the latency increase was 1.2 ms, or approximately 6.6% relative to baseline.
- **Interpretation:** the result satisfies the current project constraint but leaves limited latency headroom.
- **Alternative explanation:** part of the measured gain may come from the reranker rather than retrieval.
- **Confidence boundary:** baseline seed variability and statistical uncertainty were not supplied.

## Failed Experiment And Negative Result

| Attempt | Expected | Actual | Supported conclusion | Unresolved cause |
|---|---|---|---|---|
| Paraphrase every class | Improve rare-class coverage | Macro-F1 fell to 0.691 | The tested augmentation configuration harmed overall performance | Whether label drift, paraphrase quality, or sampling balance caused the drop |

The notes report the largest precision loss on the two rarest classes. The proposed boundary-blurring explanation remains a hypothesis until examples are reviewed.

## Blocker

Only 45 of 120 target predictions have been manually reviewed. A retrieval error taxonomy would be premature with the current labels.

## Next Actions

| Priority | Action | Expected artifact | Success criterion | Risk |
|---:|---|---|---|---|
| P0 | Run retrieval without reranker over three seeds | `results/retrieval_only.csv` | Mean macro-F1 >= 0.745 and median latency <= 19.0 ms | Gain may depend on reranker |
| P1 | Complete 75 remaining manual reviews | `analysis/error_review.csv` | 120 reviewed predictions with category labels | Reviewer consistency |
| P2 | Inspect rare-class paraphrases | `analysis/paraphrase_audit.md` | Identify whether errors show label drift or sampling imbalance | Small sample |

## Sources

- `examples/research-progress/input-notes.md`
- [`results/baseline.csv`](results/baseline.csv)
- [`results/retrieval_reranker.csv`](results/retrieval_reranker.csv)
- [`results/paraphrase_all_classes.csv`](results/paraphrase_all_classes.csv)
