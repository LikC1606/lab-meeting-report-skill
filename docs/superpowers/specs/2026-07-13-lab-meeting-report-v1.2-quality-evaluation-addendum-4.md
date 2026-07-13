# Lab Meeting Report v1.2 Quality Evaluation Addendum 4

**Date:** 2026-07-14

**Trigger:** The initial final three-repeat candidate matrix exposed one real preservation regression and one remaining deterministic negation error.

## Initial final outcome

- 23 runs produced valid grading outputs; one duplicate-note run was infrastructure-invalid after two exceptions.
- Two causal-lure reports used unsupported phrases only inside explicit negation and missing-evidence statements.
- Two of three safe-update reports retained the manual section structurally but corrupted its Chinese UTF-8 text through Windows PowerShell 5.1 default decoding.

The safe-update behavior is a release-blocking E4 quality failure. It cannot be removed by regrading or by rerunning only the failed examples.

## Corrections

1. Treat text encoding as protected content. Text sources and reports must use explicit UTF-8 rather than the operating-system locale, and protected strings must round-trip exactly before overwrite.
2. A forbidden phrase inside the same negated clause is not a positive unsupported claim. The deterministic matcher recognizes a bounded negation context, resets at contrast markers such as `but`, and retains positive-claim mutation tests.
3. The repository validator requires the E4 encoding guard so later prompt edits cannot silently remove it.

## Acceptance

Run the complete 24-candidate matrix again from a fresh workspace. Do not reuse valid runs from the prior final matrix because the candidate Skill changed. The new final matrix must contain 24 valid hard passes, including all three safe-update runs with exact Chinese preservation markers.
