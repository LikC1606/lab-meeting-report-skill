# Synthetic example: lab meeting research progress report

> All names, data, paths, and results in this report are synthetic and exist only to demonstrate the skill workflow.

> Date: 2026-07-12 | Report type: Research progress | Project: Low-resource intent classification
> Meeting stage: Before | Audience: Lab group | Duration: 12 minutes

## Decision Snapshot

- **Current status:** The combined retrieval-plus-reranker system reached mean macro-F1 0.757 across three seeds with 19.4 ms median latency (sources: `results/retrieval_reranker.csv`, `examples/research-progress/input-notes.md`).
- **Decision needed:** Choose between the latency ablation and completing the manual error review. Batching by intent did not resolve the missing category definitions; the group needs to choose the order and clarify who can approve those definitions (source: `examples/research-progress/input-notes.md`, Current blocker).
- **Strongest evidence:** The combined result is above the supplied 0.712 baseline, but retrieval and reranking were changed together, so attribution remains unresolved (sources: `results/baseline.csv`, `results/retrieval_reranker.csv`).
- **Next action:** Run retrieval without the reranker over three seeds; artifact: `results/retrieval_only.csv`; success criterion: mean macro-F1 at least 0.745 and median latency no more than 19.0 ms.

## Previous Action Review

| Action | Status | Owner | Due date | Expected artifact | Current evidence | Gap or change |
|---|---|---|---|---|---|---|
| Run retrieval plus reranker over three seeds | Completed | Lin | 2026-07-12 | Multi-seed result file | `results/retrieval_reranker.csv` | The source explicitly links the completed action to this result |
| Review 120 predictions and create a traceable error taxonomy | In progress | Lin | 2026-07-15 | `analysis/error_review.csv` | 45 reviewed predictions in `examples/research-progress/input-notes.md` | Category definitions have not been supplied |

## Objective And Current Hypothesis

- **Objective:** improve macro-F1 without increasing median inference latency by more than 10%.
- **Fact:** the combined retrieval-reranker system reached mean macro-F1 0.757 over seeds 11, 22, and 33.
- **Interpretation:** the combined system improves class-balanced performance relative to the 0.712 baseline.
- **Source hypothesis:** noisy paraphrases may have blurred boundaries between rare intents in the failed augmentation experiment. The contribution of retrieval versus the reranker remains unresolved.

## Method

| Component | Baseline | New experiment |
|---|---|---|
| Encoder | Frozen | Frozen |
| Classifier | Linear | Linear |
| Retrieval | None | Class-aware retrieval |
| Reranker | None | Lightweight reranker |
| Evaluation | Macro-F1, median latency | Macro-F1 over three seeds, median latency |

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
- **Alternative explanation:** the sources provide no alternative causal explanation for the combined-system result; the missing component ablation leaves attribution unresolved.
- **Confidence boundary:** baseline seed variability and statistical uncertainty were not supplied.

## Evidence Completeness And Gaps

| Decision-critical result | Checks present | Missing checks | Decision impact | Source |
|---|---|---|---|---|
| Retrieval plus reranker result | Objective, synthetic dataset scope, method change, baseline comparator, three seeds, metric units, and source path | Data split, full configuration, dispersion, significance test, and a figure or table locator | The result can guide an ablation, but the missing checks limit attribution and a stronger readiness claim | `examples/research-progress/input-notes.md`; `results/retrieval_reranker.csv` |
| Paraphrase augmentation result | Tested change, observed macro-F1, baseline context, and source path | Repetitions, uncertainty, full configuration, and reviewed examples supporting the proposed explanation | The negative result should constrain the next experiment, while its cause remains unverified | `examples/research-progress/input-notes.md`; `results/paraphrase_all_classes.csv` |

## Failed Experiment And Negative Result

| Attempt | Expected | Actual | Supported conclusion | Unresolved cause |
|---|---|---|---|---|
| Paraphrase every class | Not supplied | Macro-F1 fell to 0.691 | The tested augmentation configuration harmed overall performance | The source hypothesis about boundary blurring remains unverified; no other cause was supplied |

The notes report the largest precision loss on the two rarest classes. The proposed boundary-blurring explanation remains a hypothesis until examples are reviewed.

## Blocker And Decision Package

| Problem | Impact | Attempted measure | Supplied options | Support or decision requested | Source |
|---|---|---|---|---|---|
| Manual review is incomplete and category definitions are unavailable | A retrieval error taxonomy would be premature with the current labels | Batch predictions by intent before review; category definitions remain unavailable | Prioritize the latency ablation, or finish the manual review first | Choose the order and clarify who can approve the category definitions | `examples/research-progress/input-notes.md`, Current blocker |

## Next Actions

| Action | Owner | Due date | Expected artifact | Success criterion | Dependency or risk |
|---|---|---|---|---|---|
| Run retrieval without reranker over three seeds | Lin | 2026-07-14 | `results/retrieval_only.csv` | Mean macro-F1 >= 0.745 and median latency <= 19.0 ms | Keep the remaining setup and latency protocol comparable |
| Complete the manual review | Lin | 2026-07-15 | `analysis/error_review.csv` | 120 reviewed predictions with traceable category labels | Current state is 45 reviewed predictions; category definitions are not supplied |

## Sources

- `examples/research-progress/input-notes.md`
- [`results/baseline.csv`](results/baseline.csv)
- [`results/retrieval_reranker.csv`](results/retrieval_reranker.csv)
- [`results/paraphrase_all_classes.csv`](results/paraphrase_all_classes.csv)
