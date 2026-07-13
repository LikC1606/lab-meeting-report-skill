# Lab Meeting Report Behavior Benchmark

- Executor model: `gpt-5.6-sol`
- Analyzer: `codex-inline-self-review`
- Runs per configuration: `3`
- Evaluations: `8`

## Configuration Summary

| Configuration | Pass rate | Time (s) | Tokens |
|---|---:|---:|---:|
| with_skill | 1.000 +/- 0.000 | 94.3 +/- 16.5 | 352134 +/- 86482 |
| without_skill | 0.818 +/- 0.149 | 181.8 +/- 188.8 | 416982 +/- 205404 |

## Analyzer Notes

- Expectation 'conflict:macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'evidence:robustness-status' passes in every configuration and may not differentiate Skill value.
- Expectation 'evidence:success-criteria' passes in every configuration and may not differentiate Skill value.
- Expectation 'evidence:success-decision' passes in every configuration and may not differentiate Skill value.
- Expectation 'evidence:supersession' passes in every configuration and may not differentiate Skill value.
- Expectation 'evidence:unresolved-authority' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden-source:inputs/cache/debug.txt' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden-source:inputs/generated/old-report.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden:double-sample-count' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden:missing-image-content-claim' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden:two-independent-runs' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden:unsupported-average' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden:unsupported-final-value' passes in every configuration and may not differentiate Skill value.
- Expectation 'forbidden:unsupported-significance-claim' passes in every configuration and may not differentiate Skill value.
- Expectation 'negative:augmentation-drop' passes in every configuration and may not differentiate Skill value.
- Expectation 'negative:collapsed-seed' passes in every configuration and may not differentiate Skill value.
- Expectation 'preserve:0.728' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:augmentation-macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:baseline-latency' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:candidate-latency' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:candidate-macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:candidate-mean' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:candidate-seed-a' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:candidate-seed-b' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:candidate-seed-c' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:corrected-candidate' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:failed-macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:failed-seed' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:latency' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:latency-threshold' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:log-macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:macro-f1-threshold' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:new-recall' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:old-candidate' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:old-recall' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:primary-macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:sample-count' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:success-threshold' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:summary-macro-f1' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-number:timeout' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/archive/note.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/main-results.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/negative.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/new-results.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/notes.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/notes/decision.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/observations.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/results.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/results/final.csv' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/results/primary.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/results/secondary.csv' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/run-log.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/summary.csv' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/weekly-notes.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'required-source:inputs/周报.md' passes in every configuration and may not differentiate Skill value.
- Expectation 'skipped:missing-error-map' passes in every configuration and may not differentiate Skill value.
- Expectation 'skipped:unreadable-secondary' passes in every configuration and may not differentiate Skill value.
