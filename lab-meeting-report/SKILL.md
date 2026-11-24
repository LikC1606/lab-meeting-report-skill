---
name: lab-meeting-report
description: Turn research notes, papers, and experiment results into a clear lab meeting report. Use for weekly research updates, journal club, or updating a report after a meeting.
---

# Lab Meeting Report

Help the user explain what changed, what supports it, what is stuck, and what happens next. Create a concise local Markdown report from the material they provide.

## Start with the material

Accept a natural-language request without forcing the user to fill a form. Pasted notes, attachments, and a named folder are all enough to start. Do not ask the user to select a report mode, detail level, cloud service, or slide tool.

Example requests:

```text
Use $lab-meeting-report to turn these notes into this week's lab meeting report.
```

```text
使用 $lab-meeting-report，把 ./weekly 里的笔记、结果和图片整理成中文组会周报。
```

If no usable source or explicit source scope is available, ask one short question in the user's language requesting pasted notes, attachments, or a folder to read. Do not draft evidence claims from a goal alone.

Read only supplied material or the explicitly scoped files, directories, and cloud resources. For a large folder, choose relevant notes, results, figures, papers, and code changes; skip caches and dependencies. Do not search for more literature unless requested. Unreadable files remain unknown: name them and continue with usable sources.

For language, follow an explicit language request; otherwise match the language of the user's request; use English only when a genuinely mixed-language request is ambiguous. Translate headings and labels into that language. Use localized wording for unknowns, rather than Chinese placeholders in an English report.

## Make the report easy to present

Begin the report body with a localized weekly snapshot:

1. **Progress this week:** the most important supported outcome.
2. **Key evidence:** one concrete supporting comparison, observation, figure, or paper finding and its source. A pointer such as "see the table" is not evidence by itself.
3. **Blocker or help needed:** the supplied problem and requested help; briefly state when none was supplied.
4. **Next step:** the supplied action, artifact, and success criterion. Do not invent missing commitments.

Make the first screen decision-useful: summarize the current state, the strongest evidence, any help needed, and the next action.

After the snapshot, include only useful sections: results, paper insights, failed attempts, blockers, next actions, and sources. Prefer short prose; use a table when it makes several results easier to compare. Do not fill a template with empty sections or repeated missing-information cells.

For sparse source material, target 1-2 rendered pages. Normally use no more than four non-empty content sections after the snapshot and any previous-action review. Keep a shared limitation beside the affected results once. Do not repeat the same missing dataset, split, configuration, repetition, uncertainty, or statistical-test inventory in every row and again later.

### Write a useful explanation, not a source inventory

Choose the main message from the supplied evidence before drafting: what the group should understand or decide. Use an informative title such as "Current configuration completes; larger batch remains blocked" rather than "Weekly report." If no clear outcome is supported, say what was done and what remains unknown without manufacturing progress.

Use the snapshot as a short opening, not a second copy of the full result table. Keep exact measurements in one evidence table when useful; the opening can describe the supported comparison qualitatively. A failed branch deserves enough detail to explain why it changes the next action, not just a "negative results" label.

For each result cluster, connect the observation to its practical meaning and boundary: what happened, what it supports, and what it does not yet establish. Do not invent a mechanism to make the narrative feel complete. For a paper, explain the question and method in ordinary language before presenting its evidence; distinguish the authors' claims from the supplied evidence and the reporter's assessment.

Use short descriptive headings. Prefer prose for methods, implications, limitations, and discussion; tables work best for comparable measurements or several concrete actions. Do not create a bibliography-status table full of unknown values in an ordinary paper discussion. State consequential missing information once. Preserve earlier manual sections when updating an existing report.

Keep sources easy to inspect: attach one source line to a paragraph or table sharing the same evidence, or cite a paper's figure/section beside the claim. Do not add a source column repeating the same file on every row. Split source attribution when claims come from different files or conflict. A final source list alone is insufficient for decision-relevant claims.

Close with supplied next actions or the question the group needs to resolve. When the user explicitly asks for an experiment or decision proposal, provide a concrete recommendation, label it as proposed, and state what evidence it would distinguish; do not report it as an agreed commitment. Otherwise do not add speculative experiments, owners, deadlines, priorities, or success thresholds.

Infer the report type and read only its relevant reference. Treat the structures as examples, not mandatory forms:

- Experiments or project work: [progress-report.md](references/progress-report.md).
- Paper discussion: [paper-review.md](references/paper-review.md).
- Substantial project work and literature together: [mixed-report.md](references/mixed-report.md).

Default to a concise standard report, and shorten it for sparse input. If the user asks for a detailed audit, add claim-level provenance, conflicts, and the full evidence-completeness table. Keep those checks internal for ordinary reports; surface gaps only when they change a conclusion or next action.

## Edit the draft for the listener

Before saving, read the report as someone who has not seen the input. Check that the task, comparison, result, and remaining question are understandable without reopening every source. Briefly explain a specialist term only when it is necessary for the stated audience; do not turn the report into a tutorial.

- Make the snapshot compact. Use a representative comparison or observation there; keep the full measurements in the body. Repetition is justified only when it lets the opening stand alone or adds a new implication.
- Replace empty claims such as "significant progress," "promising results," and "further optimization needed" with the supported outcome or specific unresolved question.
- Use an informative, evidence-bounded heading rather than overstating success. "Current runs completed" does not mean "reproducibility established" or "performance improved."
- Include a limitation where it changes interpretation or a decision. Avoid a disclaimer after every sentence; never remove a consequential caveat just to shorten the report.
- Use one result table for a related comparison, with units in the headers and identifiers preserved. Add columns only when they support understanding or the meeting decision; retain other important supplied measurements in a linked appendix if needed.
- Keep the next-action section concrete and short. Do not repeat the full blocker narrative or add artificial owners, dates, priorities, or completion criteria.

The default output is the report itself, without a long explanation of how it was generated. Add an oral script or deck only when requested.

## Keep evidence trustworthy

Before drafting, apply these checks internally. Do not ask the user to complete the ledger or audit.

<!-- E1 -->
Before drafting, build an internal evidence ledger for each decision-relevant claim. Record its source path, exact value and unit when numeric, evidence type (`source fact`, `derived calculation`, `interpretation`, or `hypothesis`), conflicts, and linked negative evidence. Preserve source identifiers exactly; do not assign sequence numbers, seed labels, run IDs, or priority ranks that the source did not supply. Use the ledger for control; include it only in `audit` or when it materially improves traceability.

Do not invent or brainstorm alternative causal explanations unless the user explicitly asks for hypothesis generation. When the sources supply no alternative explanation, state that boundary directly or omit the field. Do not infer an experiment's intended outcome from its method or name. Do not infer priority labels.

<!-- E2 -->
Copy experimental numbers and units exactly from their sources. By default, do not introduce new deltas, percentages, averages, dispersion values, threshold margins, or other experimental numbers; state comparisons qualitatively instead. Calculate a new number only when the user explicitly requests it or a supplied source defines that calculation, verify every operand, and label it as calculated rather than observed.

<!-- E3 -->
Create an internal must-retain list for failed experiments, negative results, blockers, uncertainty, and conflicting source values. Check every item against the draft. When conflicting sources provide no precedence rule, retain the conflict and state that no authority rule was supplied.

Never invent a result, value, citation, author, venue, DOI, URL, method, or causal explanation. Mark essential unsupported fields as `待补充` and unverified citation details as `未核验`.

A source author's causal explanation is an attributed claim unless an isolating test supports it. Duplicate or translated notes about one run are not independent repetitions. Missing statistical tests mean significance is untested, not that a result is statistically insignificant.

## Save and check

Use the user's destination when supplied; otherwise save to `reports/group-meeting/YYYY-MM-DD.md` using the current local date. If file writing is unavailable, deliver the complete Markdown in chat and say that no file was saved. Do not claim a file exists without verifying it.

<!-- E4 -->
Before editing an existing report, locate and read the authorized source report even when the requested destination does not yet exist. If the source copy is under the supplied input tree, use it as the merge base rather than reconstructing the report from only the new evidence. Inventory manual headings, unrecognized content, earlier evidence, and claims not explicitly superseded, and treat that inventory as protected content. Treat text encoding as protected content. Decode and encode Markdown and text sources with explicit UTF-8. Before overwriting, verify every protected string exactly; if protected text changed or became mojibake, leave the original unchanged and write a revised file. Record supersession with both the earlier and replacement sources instead of erasing history.

Resolve the active project from the user's explicit project root or the current working directory. Create `reports/group-meeting/YYYY-MM-DD.md` by default. If the same-date file exists, read and safely merge it; when a safe merge is ambiguous, write `YYYY-MM-DD-revised.md` and preserve the original.

Run an internal evidence-completeness check for every empirical result that could change a conclusion or action: objective, data and split, configuration, comparator, repetitions, uncertainty, units, figure/table locator, and method source. Show only consequential gaps unless a detailed audit was requested.

<!-- E5 -->
Run a claim audit before completion: match every experimental number to a source fact or explicitly requested calculation, confirm every must-retain negative or conflict item is present, and relabel or remove causal, significance, bibliographic, or mechanism claims not supported by the supplied evidence. State missing checks directly. For a source that cannot be decoded or parsed reliably, report only that it was unreadable and its contents remain unknown.

Verify that the report stands alone, has consistent headings and links, keeps manual content, preserves recorded meeting history, and contains no unsupported result or citation.

## Optional requests

Do not advertise or require these setup steps during an ordinary report request.

- **Previous actions or meeting notes:** read [meeting-lifecycle.md](references/meeting-lifecycle.md). Infer stage (`before`, `after`, or `both`); default to before. When continuity material is supplied, place `上次行动复盘` or its localized equivalent immediately after the snapshot. Preserve supplied status, owners, deadlines, and artifacts. For after/both, add `会议决定与行动记录` using only supplied meeting notes. Mark resolved pre-meeting blockers as resolved; a proposed action is not a recorded decision.
- **Slides:** read [presentation-export.md](references/presentation-export.md). Derive the deck from the checked report: one message per slide, its evidence source, the spoken interpretation, and the discussion question. For "make slides" without a format, create a Markdown slide outline. Choose export tooling only for an explicitly requested format. If unavailable, keep the outline and state what could not be exported. Never describe ordinary Marp PPTX as fully editable.
- **Feishu/Lark sources or publishing:** read [lark-integration.md](references/lark-integration.md).
- **Notion sources or publishing:** read [notion-integration.md](references/notion-integration.md).

Cloud publishing requires an explicit request and an authorized target. Validate the local report first, verify the remote result, then write back its URL. If a connector is unavailable, keep the local report and name the missing connection without claiming success. Do not scan a whole cloud workspace, silently overwrite or delete remote content, switch identities, or install tools silently. Do not generate DOCX; HTML, PDF, and PPTX require a requested presentation export.

## Finish briefly

Give the report link and a short description of what it covers. Mention unreadable inputs, consequential unresolved gaps, and any requested export or publication that failed. Include verified presentation paths and cloud URLs when created. Do not expose internal modes, adapter names, or audit mechanics unless they help the user use the output.
