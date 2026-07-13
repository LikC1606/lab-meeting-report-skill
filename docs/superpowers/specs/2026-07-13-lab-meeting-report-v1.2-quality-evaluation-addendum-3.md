# Lab Meeting Report v1.2 Quality Evaluation Addendum 3

**Date:** 2026-07-13

**Trigger:** Candidate iteration 3 produced eight semantically acceptable reports, but the original deterministic result was five hard passes because three accepted expressions were classified incorrectly.

## Confirmed scoring defects

1. `No source-authority rule` is semantically equivalent to `no authority rule` in an unresolved two-source conflict.
2. The digit in technical identifiers such as `UTF-8` is not an experimental measurement.
3. `Superseded historical value` satisfies the requirement to retain a superseded value as history.

Each correction was implemented test-first. Numeric grading now excludes a digit only when it follows an alphabetic technical identifier and a hyphen; inline experimental numbers remain closed-world checked. Conflict evidence requires `unresolved`, `no`, and `authority rule` rather than one exact contiguous phrase. Supersession accepts the stable stem `histor` so both `history` and `historical` are valid.

## Regraded outcome

- Frozen v1.1 reports: `0/24` hard passes, expectation-level mean `0.812`.
- Candidate iteration 1: `0/8` hard passes.
- Candidate iteration 2: `4/8` hard passes.
- Candidate iteration 3: `8/8` hard passes.

No candidate report was regenerated after these scoring corrections. The iteration 3 claim-level Codex self-review found zero unsupported critical claims and confirmed that negative evidence, conflicts, unavailable-source boundaries, and protected manual content remained present.

## Review limitation

The user explicitly declined manual review. The semantic audit is therefore non-independent and not blinded. Final release communication must state this limitation and must not call the artifact a human review. Final repeated evaluation remains required before release.
