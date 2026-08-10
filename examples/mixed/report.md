# Synthetic example: mixed research progress and literature report

> All project data and paper notes in this report are synthetic and exist only to demonstrate the skill workflow.

> Date: 2026-07-12 | Report type: Mixed | Topic: Retrieval for imbalanced intent classification

## Decision Snapshot

- **Current status:** The current retrieval-plus-reranker result improves the supplied macro-F1 and rare-class recall, while the paper uses balanced classes and retrieval without a reranker; the conditions are not directly comparable (sources: `results/current_experiment.csv`, `papers/synthetic-balanced-retrieval.md`).
- **Decision needed:** What experiment can test whether retrieval, rather than the reranker or class balance, explains the current rare-class recall gain?
- **Strongest evidence:** The current comparison changes retrieval and the reranker together, whereas the paper's result changes retrieval under balanced classes; neither source isolates the current mechanism (sources: `results/current_experiment.csv`, `papers/synthetic-balanced-retrieval.md`).
- **Next action:** Run retrieval without the reranker under the same seed protocol; artifact: `results/retrieval_only.csv`; success criterion: record macro-F1, rare-class recall, and median latency under controlled conditions.

## Current Research Progress

| Metric | Baseline | Retrieval + reranker | Source |
|---|---:|---:|---|
| Macro-F1 | 0.712 | 0.757 mean over three seeds | `results/current_experiment.csv` |
| Rare-class recall | 0.54 | 0.62 | `results/current_experiment.csv` |
| Median latency | 18.2 ms | 19.4 ms | `results/current_experiment.csv` |

- **Fact:** the combined current system improved the supplied macro-F1 and rare-class recall.
- **Source hypothesis:** retrieval improves rare-class recall by exposing class-specific examples.
- **Evidence boundary:** the current comparison changes retrieval and the reranker together, so it cannot attribute the observed result to either component.

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
| Macro-F1 is 0.712 for baseline and 0.757 for retrieval + reranker | Fictional paper reports baseline 0.70 and retrieval 0.77 | Directionally consistent | Different data balance and model components | Run retrieval-only ablation on current data |
| Rare-class recall is 0.54 for baseline and 0.62 for retrieval + reranker | Rare-class recall not reported | Not comparable | Paper classes are balanced | Report per-class recall in retrieval-only run |
| Latency increased by 1.2 ms | Latency not reported | Missing evidence | Paper has no operational constraint | Measure retrieval-only median latency |

Agreement in macro-F1 direction does not prove a shared mechanism. The fictional paper cannot validate the current rare-class explanation because it reports no rare-class setting.

## Transferable Method

The retrieval-only configuration is transferable as an ablation, not yet as a production recommendation. Keep the current encoder and evaluation data fixed, remove the reranker, and run the same three-seed protocol.

## Updated Hypothesis

- **Original hypothesis:** retrieval improves rare-class recall through class-specific examples.
- **Current evidence:** the combined system improves recall, while the fictional paper reports retrieval gains under balanced conditions.
- **Updated hypothesis:** the source hypothesis remains unverified because the current result combines retrieval with a reranker and the paper uses balanced classes.

## Validation Plan

| Experiment | Expected artifact | Success criterion | Interpretation |
|---|---|---|---|
| Retrieval without reranker under the same seed protocol | `results/retrieval_only.csv` | Record macro-F1, rare-class recall, and median latency under a controlled configuration; numeric acceptance thresholds are not supplied | Compares retrieval-only with baseline and the combined system |
| Compare all 8 per-class recall values | `analysis/per_class_recall.md` | Report every class without an aggregation-only claim | Tests whether the observed result is concentrated in rare classes |
| Measure retrieval-only latency | Same result file | Use the same measurement protocol as the current experiment; the project threshold is not supplied | Tests operational viability without importing a threshold from another workflow |

## Sources

- `examples/mixed/input-notes.md`
- [`results/current_experiment.csv`](results/current_experiment.csv)
- [`papers/synthetic-balanced-retrieval.md`](papers/synthetic-balanced-retrieval.md)
