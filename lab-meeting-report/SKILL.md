---
name: lab-meeting-report
description: Turn a PhD student's weekly notes, papers, experiment results, figures, code changes, and explicitly scoped cloud sources into a concise, source-grounded Markdown lab-meeting summary. Use for weekly research summaries, progress reports, journal club notes, experiment retrospectives, meeting follow-up, optional Feishu/Lark or Notion publishing, and optional Markdown or PPT presentation preparation. Preserve negative results and manual edits, accept natural-language input without a form, and never publish without an explicit request.
---

# Weekly Research Meeting Summaries

Turn the user's scattered weekly research material into a report they can present, discuss, and archive. Keep the default interaction lightweight: the user supplies the material; infer the structure. Apply evidence safeguards in the background instead of making the user complete an audit form.

Choose the output language in this order: follow an explicit language request, otherwise match the language of the user's request, and use English only when a genuinely mixed-language request is ambiguous. Preserve technical terms, model names, abbreviations, metric names, equations, citations, and identifiers in their source form.

## Input contract

Accept a natural-language request without forcing the user to fill a form. Treat the source scope as the only required input. Pasted notes, a description of this week's work, and attached material count as sources. Resolve relative paths and globs against the active project.

Extract these optional preferences when supplied:

- **Sources:** pasted updates, notes, papers, results, figures, screenshots, code changes, or explicitly scoped Feishu/Lark and Notion resources;
- **Focus:** the message, question, or problem the user wants the group to understand;
- **Mode:** research progress, paper review, or mixed;
- **Meeting context:** stage (`before`, `after`, or `both`), audience, duration, previous actions, and meeting notes;
- **Output:** language, date, detail (`brief`, `standard`, or `audit`), and destination path;
- **Publishing:** local only, Feishu/Lark, Notion, or both;
- **Presentation:** plain Markdown outline, Marp, Quarto, or editable PPTX when a compatible adapter is available.

Use these defaults when preferences are absent: infer the mode, use the current local date, match the request language, use `before`, write `reports/group-meeting/YYYY-MM-DD.md`, and use `standard`. For sparse input, use `brief` automatically. Infer `after` only when the sources clearly contain meeting decisions or assigned actions. Ask at most one focused clarification question, and only when the answer changes the report's conclusions, source boundary, or remote write target; otherwise mark the gap as `待补充` and continue.

If no usable source or explicit source scope is available, ask one focused question requesting the weekly material and do not draft evidence claims. A stated goal is not evidence.

A sufficient request is:

```text
读取本周的笔记、实验结果、论文和图片，生成中文组会总结。
```

Optional destinations can be added naturally:

```text
读取 ./weekly 和我上面的补充说明，生成本周组会 Markdown，
发布到飞书，并准备一个 10 分钟的 Marp 演示稿。
```

## Output contract

Create and validate a local Markdown file before any cloud publication or slide export. The local report is the source of truth.

Begin the report body with a localized weekly snapshot containing these fields in order:

1. **Progress this week:** the most important supported outcome, not an activity list;
2. **Key evidence:** the strongest result, figure, paper finding, or artifact with its source;
3. **Blocker or help needed:** what is stuck and the concrete discussion, resource, or decision needed; if none was supplied, say so briefly;
4. **Next step:** the next action, expected artifact, and success criterion.

Use localized labels such as `本周进展`, `关键证据`, `阻塞与需协助`, and `下一步`. If the sources cannot support a progress judgment, mark it `待补充` and state what is missing.

For `standard`, organize the remaining material around what a researcher normally needs to present and retain:

- completed work and material changes since the previous report;
- key results, figures, and relevant paper insights;
- failed attempts, negative results, uncertainty, and limitations;
- blockers and the specific help or discussion needed;
- next-week actions;
- sources and attachments.

Omit empty or duplicative sections. Do not make the user-facing report resemble a completed questionnaire.

- For `brief`, keep the weekly snapshot, non-duplicative key evidence, failed attempts or blockers that affect interpretation, next actions, and sources.
- For `standard`, use the selected mode reference, target a readable meeting report, and surface only evidence gaps that could change the conclusion.
- For `audit`, add a claim-level provenance table, the full evidence-completeness table, unresolved conflicts, and skipped or unreadable sources.

Place a source path, identifier, or precise locator next to every decision-relevant claim. Avoid repeating the same metric unless a later occurrence adds comparison, uncertainty, or a new implication. Keep facts, interpretations, and hypotheses distinct. Label recommendations as recommendations; do not turn a requested choice into a decided outcome.

When continuity material is supplied, place `上次行动复盘` or its localized equivalent immediately after the snapshot. Preserve action wording, status, owner, due date, artifact, and source. Never infer completion from a related positive result.

For `after` or `both`, add `会议决定与行动记录` using only supplied meeting notes. When a pre-meeting blocker was resolved by a recorded meeting decision, label it as a pre-meeting issue resolved by that decision and retain it for traceability; do not present it as an active blocker. Keep missing owners or due dates as `待补充`.

## Workflow

### 1. Collect the weekly material

- Combine pasted context with user-scoped files, directories, and cloud resources.
- Prioritize `.md`, `.txt`, `.pdf`, `.csv`, `.xlsx`, common raster images, and relevant code diffs or logs.
- For a large directory, list candidate files and read only material relevant to the report. Exclude caches, dependencies, archives, and unrelated generated output.
- Inspect figures when they carry experimental evidence. Use structured parsers for tables when available.
- Record sources used, skipped, and unreadable.
- Do not search for additional literature unless the user explicitly requests it.

Read `references/lark-integration.md` when the user supplies a Feishu/Lark resource or requests Feishu/Lark publishing. Read `references/notion-integration.md` when the user supplies a Notion page or requests Notion publishing. Read only the resources the user places in scope.

### 2. Build the evidence inventory

Extract supported information:

- research objective and current hypothesis;
- work completed and artifacts created;
- experimental or implementation setup;
- results, figures, observations, and paper findings;
- failed attempts, negative results, uncertainty, and blockers;
- requested discussion, support, or decision;
- next actions and supplied success criteria.

<!-- E1 -->
Before drafting, build an internal evidence ledger for each decision-relevant claim. Record its source path, exact value and unit when numeric, evidence type (`source fact`, `derived calculation`, `interpretation`, or `hypothesis`), conflicts, and linked negative evidence. Preserve source identifiers exactly; do not assign sequence numbers, seed labels, run IDs, or priority ranks that the source did not supply. Use the ledger for control; include it only in `audit` or when it materially improves traceability.

Do not invent or brainstorm alternative causal explanations unless the user explicitly asks for hypothesis generation. When the sources supply no alternative explanation, state that boundary directly or omit the field. Do not infer an experiment's intended outcome from its method or name. Do not infer priority labels.

<!-- E2 -->
Copy experimental numbers and units exactly from their sources. By default, do not introduce new deltas, percentages, averages, dispersion values, threshold margins, or other experimental numbers; state comparisons qualitatively instead. Calculate a new number only when the user explicitly requests it or a supplied source defines that calculation, verify every operand, and label it as calculated rather than observed.

<!-- E3 -->
Create an internal must-retain list for failed experiments, negative results, blockers, uncertainty, and conflicting source values. Check every item against the draft. When conflicting sources provide no precedence rule, retain the conflict and state that no authority rule was supplied.

Never invent a result, value, citation, author, venue, DOI, URL, method, or causal explanation. Mark essential unsupported fields as `待补充` and unverified citation details as `未核验`.

### 3. Select the report mode

- **Research progress:** Use for experiments, implementation, or project progress. Read `references/progress-report.md`.
- **Paper review:** Use for paper reading or journal club. Read `references/paper-review.md`.
- **Mixed:** Use when current work and literature both matter. Read `references/mixed-report.md`.

Prefer mixed mode only when both evidence types are substantial. Read `references/meeting-lifecycle.md` when previous actions, post-meeting notes, or a presentation are in scope.

### 4. Draft for the meeting

- Lead with the weekly snapshot. Make the first screen decision-useful: summarize the current state, the strongest evidence, any help needed, and the next action.
- Report outcomes before method detail. Keep chronological activity only when it explains a change or failure.
- Use the selected mode reference as adaptable structure, not text to copy mechanically.
- Translate headings and labels into the selected report language while preserving their meaning and order.
- For sparse source material, target 1-2 rendered pages. Use 3-5 pages only when the evidence volume warrants it.
- Keep figures near their interpretations. Use relative image paths, captions, sources, and one-sentence evidence boundaries.
- Keep negative results visible because they constrain future work.
- Turn a blocker into a concrete help request: problem, impact, attempted measures, and requested discussion or resource. Include options only when the user or source supplied them.
- Make next actions concrete with an artifact and success criterion; include owners and dates only when supplied.
- In `brief` and `standard`, keep evidence-completeness auditing in the background and surface only missing checks that could change what the group concludes or does next.

### 5. Write safely to disk

<!-- E4 -->
Before editing an existing report, locate and read the authorized source report even when the requested destination does not yet exist. If the source copy is under the supplied input tree, use it as the merge base rather than reconstructing the report from only the new evidence. Inventory manual headings, unrecognized content, earlier evidence, and claims not explicitly superseded, and treat that inventory as protected content. Treat text encoding as protected content. Decode and encode Markdown and text sources with explicit UTF-8. Before overwriting, verify every protected string exactly; if protected text changed or became mojibake, leave the original unchanged and write a revised file. Record supersession with both the earlier and replacement sources instead of erasing history.

Resolve the active project from the user's explicit project root or the current working directory. Create `reports/group-meeting/YYYY-MM-DD.md` by default. If the same-date file exists, read and safely merge it; when a safe merge is ambiguous, write `YYYY-MM-DD-revised.md` and preserve the original.

### 6. Run the quality gate

Run an internal evidence-completeness check for every empirical result that could change a conclusion or action. Check the objective, data or sample and split, method and configuration, comparator, repetitions, uncertainty or statistical test, units, figure/table locator, and method source. In `brief` and `standard`, report only missing checks with decision impact; in `audit`, include the full table. A missing check is not a negative result.

<!-- E5 -->
Run a claim audit before completion: match every experimental number to a source fact or explicitly requested calculation, confirm every must-retain negative or conflict item is present, and relabel or remove causal, significance, bibliographic, or mechanism claims not supported by the supplied evidence. State missing checks directly. For a source that cannot be decoded or parsed reliably, report only that it was unreadable and its contents remain unknown.

Verify that the report stands alone, has consistent headings and links, keeps manual content, preserves recorded meeting history, and contains no unsupported result or citation.

### 7. Publish only when requested

Finish and validate the local report first.

- For Feishu/Lark, follow `references/lark-integration.md`.
- For Notion, follow `references/notion-integration.md`.
- When both are requested, publish and verify them independently; one platform's failure must not invalidate the local report or create a duplicate on the other platform.

Never publish silently. Use the user's authorized identity and requested scope. Write a remote URL back into the local report only after verification.

### 8. Prepare a presentation only when requested

Read `references/presentation-export.md`. Create a companion Markdown deck from the validated report rather than resynthesizing the raw sources. Keep one message per slide, its evidence source, the spoken interpretation, and the discussion question. Use an installed adapter only when the requested output needs it; do not install packages silently.

### 9. Report completion

Tell the user the local report path, selected mode and stage, sources used, skipped material, unresolved gaps, created presentation files, selected adapter, verified cloud URLs, and partial publishing failures.

## Scope boundaries

Keep Markdown as the canonical report. Do not scan whole cloud workspaces, publish without request, overwrite remote pages by default, delete remote content, switch identities as a fallback, install presentation tools silently, or search the web for new slide generators during an ordinary report run. Do not generate DOCX. Generate HTML, PDF, or PPTX only through an explicitly requested presentation adapter and clearly report editability limits.
