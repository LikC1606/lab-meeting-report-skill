# Lab Meeting Report v1.2 Quality Evaluation Addendum 1

**Date:** 2026-07-13

**Trigger:** Candidate iteration 1 retained all seven selected control blocks but produced eight valid quality failures and zero hard-pass cases.

## Evidence

Candidate iteration 1 improved the mean expectation pass rate from the three-repeat v1.1 baseline's `0.786` to `0.842`, but this aggregate concealed release-blocking failures:

- seven of eight reports introduced undeclared experimental arithmetic;
- the conflict report expressed the absence of source precedence indirectly rather than as the stable no-authority boundary;
- the duplicate-note report printed an invalid combined sample count while warning readers not to use it;
- the causal-lure report repeated strong causal clauses under a hypothesis label;
- the partial-source report described bytes and fields from a source classified as unreadable;
- the safe-update report preserved the baseline, superseded value, source path, and both manual markers, demonstrating that E4 fixed the destructive-update behavior.

## Design correction

The initial blocks explained evidence principles but left too much freedom in their execution. Revise only the blocks whose first implementation failed:

1. E2 defaults to no proactive experimental arithmetic. Qualitative comparisons are sufficient unless the user or a source explicitly requests a calculation.
2. E3 requires an explicit no-authority statement when conflicting sources have no precedence rule.
3. E5 audits the sentence body rather than trusting a heading, and treats reliably unreadable source contents as unknown.
4. P1 prohibits printing counterfactual combined counts while explaining duplicate provenance.
5. P2 requires attribution and modal uncertainty inside the causal sentence.

E1 and E4 remain unchanged. The corpus, manifests, grader, model, runner, and frozen baseline remain unchanged, preventing the candidate from passing through a weakened benchmark.

## Acceptance

Run all eight cases again once. Continue to final repeated evaluation only if every case passes deterministic hard gates and a direct semantic audit confirms that evidence was retained rather than omitted to satisfy lexical checks.
