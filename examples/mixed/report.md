# Synthetic example: mixed research progress and literature report

> All project data and paper notes in this report are synthetic and exist only to demonstrate the skill workflow.

> Date: 2026-07-12 | Report type: Mixed | Topic: Retrieval for imbalanced intent classification

## Summary

- Current results improved macro-F1 from 0.712 to 0.757 and rare-class recall from 0.54 to 0.62.
- A fictional paper reports a similar macro-F1 direction, 0.70 to 0.77, but uses balanced classes and retrieval without a reranker.
- The two results are not directly comparable because class balance, model components, and latency reporting differ.
- The next experiment should isolate retrieval by removing the reranker and measuring rare-class recall over three seeds.

## Current Research Progress

| Metric | Baseline | Retrieval + reranker | Source |
|---|---:|---:|---|
| Macro-F1 | 0.712 | 0.757 mean over 3 seeds | `results/current_experiment.csv` |
| Rare-class recall | 0.54 | 0.62 | `results/current_experiment.csv` |
| Median latency | 18.2 ms | 19.4 ms | `results/current_experiment.csv` |

- **Fact:** the combined current system improved the supplied macro-F1 and rare-class recall.
- **Hypothesis:** retrieval caused the recall gain by exposing class-specific examples.
- **Unresolved alternative:** the reranker may account for some or all of the gain.

## Related Synthetic Paper

| Field | Supplied information |
|---|---|
| Title | Balanced Retrieval Memories for Intent Classification |
| Authors / venue / DOI / year | **Unverified / not supplied** |
| Data | Six domains with balanced classes |
| Main result | Macro-F1 0.70 -> 0.77 with retrieval |
| Latency | Not reported |
| Source | `papers/synthetic-balanced-retrieval.md` |

The fictional paper claims transfer across intent datasets. The supplied notes do not establish transfer to imbalanced data or systems with rerankers.

## Evidence Mapping

| Current observation | Literature evidence | Relationship | Boundary | Validation action |
|---|---|---|---|---|
| Macro-F1 improved by 0.045 | Fictional paper reports +0.07 | Directionally consistent | Different data balance and model components | Run retrieval-only ablation on current data |
| Rare-class recall improved by 0.08 | Rare-class recall not reported | Not comparable | Paper classes are balanced | Report per-class recall in retrieval-only run |
| Latency increased by 1.2 ms | Latency not reported | Missing evidence | Paper has no operational constraint | Measure retrieval-only median latency |

Agreement in macro-F1 direction does not prove a shared mechanism. The fictional paper cannot validate the current rare-class explanation because it reports no rare-class setting.

## Transferable Method

The retrieval-only configuration is transferable as an ablation, not yet as a production recommendation. Keep the current encoder and evaluation data fixed, remove the reranker, and run the same three-seed protocol.

## Updated Hypothesis

- **Original hypothesis:** retrieval improves rare-class recall through class-specific examples.
- **Current evidence:** the combined system improves recall, while the fictional paper reports retrieval gains under balanced conditions.
- **Updated hypothesis:** retrieval contributes to the current gain, but the magnitude depends on class imbalance and may interact with the reranker.

## Validation Plan

| Priority | Experiment | Expected artifact | Success criterion | Interpretation |
|---:|---|---|---|---|
| P0 | Retrieval without reranker, 3 seeds | `results/retrieval_only.csv` | Mean macro-F1 >= 0.745 and rare-class recall >= 0.59 | Supports a retrieval contribution if both thresholds hold |
| P1 | Compare per-class deltas | `analysis/per_class_recall.md` | Report all 8 classes without aggregation-only claims | Tests whether gain is concentrated in rare classes |
| P2 | Measure retrieval-only latency | Same result file | Median latency <= 19.0 ms | Tests operational viability |

## Sources

- `examples/mixed/input-notes.md`
- [`results/current_experiment.csv`](results/current_experiment.csv)
- [`papers/synthetic-balanced-retrieval.md`](papers/synthetic-balanced-retrieval.md)
