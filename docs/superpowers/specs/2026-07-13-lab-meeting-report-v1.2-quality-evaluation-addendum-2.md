# Lab Meeting Report v1.2 Quality Evaluation Addendum 2

**Date:** 2026-07-13

**Trigger:** Candidate iteration 2 reached four hard-pass cases after a grader correction, leaving four narrow failures before the maximum third development iteration.

## Grader correction

The numeric closed-world check incorrectly treated Markdown ordered-list markers such as `1.` and `2.` as experimental values. A test-first correction excludes only integers used as line-start ordered-list syntax. Inline numbers, including invented seed identifiers, remain checked. Regrading the unchanged baseline preserves its `0/24` hard-pass outcome while changing the expectation-level mean from `0.786` to `0.799` and numeric failures from 20 to 17.

## Remaining evidence

- `clean-multiseed` assigned seed identifiers `1`, `2`, and `3` even though the source supplied only three unlabeled scores.
- `duplicated-multilingual-notes` correctly described one run but omitted the complete repeated-provenance and non-replication boundary.
- `missing-evidence-causal-lure` removed strong causal wording but repeated `statistically significant` inside a negation and did not state the missing significance test as a direct boundary.
- `scoped-directory-selection` said the candidate met the criterion but omitted the required qualitative fact that it exceeds the criterion.

## Final development correction

1. Preserve source identifiers exactly and leave unlabeled observations unlabeled.
2. Express threshold relations qualitatively as exceeds, meets, or falls below without computing a margin.
3. Require the complete duplicate-provenance boundary in the report language.
4. State missing ablation and significance checks directly, and never repeat an unsupported strong claim merely to negate it.

The corpus and semantic rules remain unchanged. Candidate iteration 3 is the final allowed development run; any remaining failure stops prompt iteration and blocks release pending a new design decision.
