# Synthetic example: mixed progress and literature input

> All project data and paper notes in this file are synthetic and exist only to demonstrate the skill workflow.

## Current experiment

- Task: 8-class imbalanced support-ticket intent classification
- Baseline macro-F1: 0.712
- Retrieval + reranker mean macro-F1: 0.757 over three seeds
- Rare-class recall: baseline 0.54; new system 0.62
- Median latency: baseline 18.2 ms; new system 19.4 ms
- Precomputed latency change supplied for reporting: 1.2 ms
- Current hypothesis: retrieval improves rare-class recall by exposing class-specific examples
- Source: `results/current_experiment.csv`

## Synthetic literature note

- Fictional title: Balanced Retrieval Memories for Intent Classification
- Authors, venue, DOI, and year: not supplied
- Data: 6 domains with balanced classes
- Reported baseline macro-F1: 0.70
- Reported retrieval macro-F1: 0.77
- Reported rare-class recall: not applicable because classes were balanced
- Latency: not reported
- Paper claim: retrieval gains transfer across intent datasets
- Source: `papers/synthetic-balanced-retrieval.md`

## Known condition mismatch

- Current data is imbalanced; fictional paper data is balanced.
- Current system adds a reranker; fictional paper evaluates retrieval alone.
- Current project has a latency constraint; fictional paper reports no latency.

## Decision needed

What experiment can test whether retrieval, rather than the reranker or class balance, explains the current rare-class recall gain?
