Synthetic example

# Existing Research Progress Report - 2026-07-13

> Date: 2026-07-13 | Report type: Research progress

## Summary

- **Corrected result:** The candidate macro-F1 is 0.741.
- **Supersession status:** `inputs/new-results.md` explicitly supersedes the earlier candidate value of 0.728. It does not invalidate the baseline or the manual note.
- **Evidence boundary:** The supplied sources provide metric values and the supersession statement, but no experimental setup, replication evidence, uncertainty estimate, ablation result, or significance test.

## Results and Evidence

| Item | Macro-F1 | Status | Source |
|---|---:|---|---|
| Baseline | 0.702 | Retained; not invalidated by the correction | `inputs/reports/group-meeting/2026-07-13.md`; `inputs/new-results.md` |
| Candidate | 0.741 | Corrected current value; explicitly supersedes 0.728 | `inputs/new-results.md` |

The corrected candidate result exceeds the baseline. No significance test was supplied, so statistical significance is untested.

## Superseded History

The following statement is retained verbatim from the existing report to preserve the earlier record:

Baseline macro-F1 was 0.702 and the old candidate macro-F1 was 0.728.

The candidate value of 0.728 is superseded by 0.741 according to `inputs/new-results.md`. The baseline value of 0.702 remains valid under the supplied correction.

## Interpretation and Confidence Limits

- **Source fact:** The corrected candidate macro-F1 is 0.741.
- **Source fact:** The correction supersedes only the earlier candidate value of 0.728; it does not invalidate the baseline or manual notes.
- **Interpretation:** The corrected candidate remains qualitatively better than the baseline on the supplied macro-F1 values.
- **Confidence limits:** No experimental setup, independent replication, uncertainty measure, ablation outcome, or significance test was supplied. No causal or mechanism claim can be evaluated from the scoped sources.

## Manual Content Preserved Verbatim

## 导师反馈（手写）

保留这个消融实验，不要删除。

The manual note is retained without modification. The scoped sources do not include the referenced ablation result, so its outcome remains unknown.

## Next Actions

| Priority | Action | Expected artifact | Success criterion | Dependency or risk |
|---:|---|---|---|---|
| P0 | Attach the evidence for the corrected candidate result | Run record or results file linked to the 0.741 value | The candidate value and its provenance can be checked directly | The run identifier and artifact location were not supplied |
| P0 | Add the ablation evidence referenced by the manual note | Ablation result with setup and metric | The retained ablation can be assessed without removing the manual note | The ablation source was not supplied |
| P1 | Document evaluation setup and uncertainty checks | Evaluation protocol plus replication or uncertainty output | The baseline and corrected candidate are comparable under a documented protocol | Setup and statistical evidence were not supplied |

## Sources Used

- `inputs/reports/group-meeting/2026-07-13.md` — authorized existing report and merge base.
- `inputs/new-results.md` — corrected candidate value and explicit supersession scope.
