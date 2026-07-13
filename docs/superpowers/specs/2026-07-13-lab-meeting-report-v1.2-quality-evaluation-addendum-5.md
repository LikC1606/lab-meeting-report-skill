# Lab Meeting Report v1.2 Quality Evaluation Addendum 5

**Date:** 2026-07-14

**Trigger:** The complete `final-v2` candidate matrix produced 24 valid reports and zero infrastructure-invalid runs, but deterministic grading reported three lexical failures.

## Raw final-v2 outcome

- 21 of 24 reports received a raw deterministic hard pass.
- Buried-negative runs 1 and 2 retained seed `29`, macro-F1 `0.603`, the `300 s` timeout, the negative-result status, and unresolved robustness. The matcher nevertheless reported `missing: seed 29` because the reports used the semantically equivalent Markdown form `Seed \`29\``.
- Scoped-directory run 2 used `[1]` and `[2]` as citations linked to numbered entries under `## Sources`. The numeric closed-world gate incorrectly treated those source labels as experimental values.
- Direct inspection found no unsupported critical claim in these three reports. The failures are grader false positives, not candidate quality passes obtained by omission.

## Corrections

1. Semantic term normalization ignores Markdown backtick delimiters. This makes `Seed \`29\`` equivalent to `seed 29` while leaving the required words and number present.
2. Numeric extraction ignores a bracketed integer citation only when every cited label has a matching numbered definition under a Markdown `Sources` or `References` section.
3. An undefined bracketed number remains subject to the numeric closed-world gate. The regression suite proves that `[9]` still fails when only source label `1` is defined.
4. The generated candidate and baseline reports remain frozen. Regrading may update `grading.json` and the recorded grader hash, but it must not rerun generation or change report content.

## Frozen-baseline reconciliation

The candidate and baseline metadata match on model, Codex CLI version, provider hash, prompt hash, and every generation-visible task and input. Two recorded hash classes differ for bounded reasons:

- `conflicting-results` and `safe-existing-report-update` have different aggregate case hashes because commit `969750e` changed only their hidden manifests. Their task files and input trees, which are the material visible to the report generator, are unchanged.
- The runner hash changed from `885f51d...` to `9052a23...` because commit `98bb18e` added the `--semantic-review` release-gate path below `check_release_gate`. The isolated generation command, prompt construction, provider replay, workspace setup, and output capture are byte-for-byte unchanged by that diff.
- After report generation, the benchmark command gained an explicit analyzer label so published metadata says `codex-inline-self-review` instead of the former human-review default. This aggregation-only change is also outside the generation path.

These changes cannot influence generated report content. Reusing the frozen raw baseline reports is therefore allowed, while the mismatches and their commits remain disclosed here.

## Acceptance

The targeted red-green tests and the complete repository unit suite must pass. Regrade all 24 unchanged `final-v2` candidate reports and all 24 unchanged frozen `v1.1.0` baseline reports with the same corrected grader. Continue only if all candidate reports hard-pass, the baseline still contains a demonstrable hard failure, and the subsequent claim-level Codex self-audit finds no unsupported critical claim.
