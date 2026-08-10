# Synthetic example: research progress input

> All names, data, paths, and results in this file are synthetic and exist only to demonstrate the skill workflow.

## Reporting context

- Project: low-resource support-ticket intent classifier
- Period: 2026-07-06 to 2026-07-12
- Goal: improve macro-F1 without increasing median inference latency by more than 10%
- Dataset: synthetic, 8 intent classes, imbalanced class distribution
- Meeting stage: before
- Audience and duration: lab group, 12 minutes

## Previous meeting actions

- Action: run retrieval plus reranker over three seeds.
  - Owner: Lin
  - Due date: 2026-07-12
  - Status: completed
  - Evidence: `results/retrieval_reranker.csv`
- Action: review 120 predictions and create a traceable error taxonomy.
  - Owner: Lin
  - Due date: 2026-07-15
  - Status: in progress; 45 predictions reviewed
  - Evidence: this note; the category definitions have not been supplied

## Previous baseline

- Model: frozen encoder + linear classifier
- Macro-F1: 0.712
- Median latency: 18.2 ms per request
- Source: `results/baseline.csv`

## New experiment

- Change: add class-aware retrieval and a lightweight reranker
- Seed 11 macro-F1: 0.758
- Seed 22 macro-F1: 0.764
- Seed 33 macro-F1: 0.749
- Mean macro-F1: 0.757
- Median latency: 19.4 ms per request
- Precomputed comparisons supplied for reporting: macro-F1 change 0.045 absolute; latency change 1.2 ms, approximately 6.6% relative to baseline
- Source: `results/retrieval_reranker.csv`

## Failed experiment

- Change: paraphrase augmentation applied to every class
- Macro-F1: 0.691
- Observation: precision dropped most on the two rarest classes
- Hypothesis: noisy paraphrases blurred boundaries between rare intents
- Source: `results/paraphrase_all_classes.csv`

## Current blocker

- Error analysis needs 120 manually reviewed predictions.
- Only 45 predictions have been reviewed.
- Attempted measure: batch predictions by intent before review; the category definitions remain unavailable.
- Supplied options: prioritize the latency ablation, or finish the manual review first.
- Requested support: the group should choose the order and clarify who can approve the category definitions.
- No conclusion about retrieval failure categories is supported yet.

## Proposed next steps

1. Remove the reranker while keeping retrieval.
2. Run three seeds.
3. Compare rare-class recall and median latency.
4. Success criterion: mean macro-F1 at least 0.745 and median latency no more than 19.0 ms.
5. Owner: Lin. Proposed due date: 2026-07-14.

Complete the manual review as a separate action. Owner: Lin. Due date: 2026-07-15. The artifact is `analysis/error_review.csv`; success requires 120 reviewed predictions with traceable category labels.

## Decision needed

Should the next cycle prioritize the latency ablation or completion of manual error review?
