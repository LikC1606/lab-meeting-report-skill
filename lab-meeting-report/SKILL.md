---
name: lab-meeting-report
description: Create or update evidence-grounded Markdown documents for lab meetings from pasted notes, local research files, papers, experiment results, directories, or explicitly scoped Lark/Feishu documents, chats, Minutes, and meeting artifacts. Use for lab meeting reports, research progress reports, journal club notes, experiment retrospectives, mixed progress-and-literature reports, or publishing and synchronizing a verified Markdown report to a Lark cloud document rather than creating slides.
---

# Research Group Meeting Markdown Reports

Create a real Markdown report grounded in the user's source material. Choose the output language in this order: follow an explicit language request, otherwise match the language of the user's request, and use English only when a genuinely mixed-language request is ambiguous. Preserve precise technical terms, model names, abbreviations, metric names, equations, citations, and identifiers in their source form.

## Workflow

### 1. Collect sources

- Combine pasted context with user-specified files or directories.
- Prioritize `.md`, `.txt`, `.pdf`, `.csv`, `.xlsx`, and common raster images.
- For a large directory, list candidate files first and read only files relevant to the report. Exclude caches, archives, dependencies, and unrelated generated outputs.
- Use structured parsers for structured files when available. Inspect images when they carry experimental evidence.
- Record every source used. Record unreadable or skipped sources and continue with the remaining material.
- Do not search for additional literature unless the user explicitly requests it.

### 2. Build an evidence inventory

Extract only supported information:

- research objective and current hypothesis;
- experimental or implementation setup;
- results, metrics, figures, and observations;
- failed attempts, negative results, uncertainty, and blockers;
- paper metadata, question, method, findings, and limitations;
- decisions needed and next actions.

Keep facts, interpretations, and hypotheses distinct. When sources conflict, retain each value with its source and describe the conflict. Do not silently reconcile it.

Never invent a result, value, citation, author, venue, DOI, URL, method, or causal explanation. Mark an essential unsupported field as `待补充`. Mark unverified citation details as `未核验`.

### Optional Lark/Feishu sources

Read `references/lark-integration.md` whenever the user supplies a Lark/Feishu URL, token, chat, meeting, or Minute source, or asks to publish or synchronize the finished report to Lark. Read only resources the user explicitly places in scope. Keep identifiers and source provenance intact, and use user identity for all Lark operations.

### 3. Select one report mode

- **Research progress:** Use when the material primarily concerns the user's experiments, implementation, or project results. Read `references/progress-report.md`.
- **Paper review:** Use when the material primarily concerns one or more papers. Read `references/paper-review.md`.
- **Mixed:** Use when both evidence types are substantial or literature is used to interpret or plan current research. Read `references/mixed-report.md`.

If routing remains ambiguous, prefer mixed mode and keep current-work evidence separate from literature evidence. Ask one focused question only when the answer would materially change the report's conclusions or structure.

### 4. Draft the report

- Use the selected reference as the structure, not as text to copy mechanically.
- Treat Chinese headings in the reference templates as structural examples. Translate headings and labels into the selected report language while preserving their semantic order and evidence rules.
- Target roughly 3-5 rendered pages, shortening sparse reports and expanding only when evidence requires it.
- Put each conclusion next to its supporting evidence.
- Use Markdown tables for useful numeric comparisons.
- Use relative paths for figures. Add a figure caption, source, and one-sentence interpretation.
- If a referenced figure is missing, retain the intended caption and source note and flag the missing asset.
- Omit unsupported optional sections. Keep essential missing sections and label their gaps.
- Make next actions concrete: include the action, expected artifact, success criterion, and relevant dependency or risk.
- Avoid decorative filler, generic praise, and activity lists that imply unsupported conclusions.

### 5. Write safely to disk

Resolve the active project as the user's explicit project root when provided; otherwise use the current working directory. Create:

```text
<active-project>/reports/group-meeting/YYYY-MM-DD.md
```

Use the current local date unless the user specifies a reporting date.

If the same-date file exists:

1. Read it before editing.
2. Merge new evidence into matching sections.
3. Preserve unrecognized headings and manually written content.
4. Do not remove an earlier claim unless the new source explicitly supersedes it; record the change when it does.
5. If a safe merge is ambiguous, write `YYYY-MM-DD-revised.md` and leave the original unchanged.

Create or edit the Markdown file with the platform's normal file-editing tool. Do not stop after printing an outline in chat.

### 6. Run the quality gate

Before finishing, verify:

- every key conclusion is traceable to an input source;
- facts, interpretations, and hypotheses are visibly distinct;
- failed experiments and negative results remain present;
- numeric values and citations match their sources;
- heading levels, tables, and relative image links are internally consistent;
- next actions include expected artifacts and success criteria;
- the report is understandable without the preceding chat;
- unresolved essential gaps are summarized for the user.

### 7. Publish to Lark when requested

Finish and validate the local Markdown file before any Lark write. Then follow `references/lark-integration.md` to create or safely append to a Lark cloud document, embed local images, verify the remote result, and write the verified URL back into the local report. A Lark failure must not invalidate the local file.

### 8. Report completion

Tell the user:

- the output file path;
- the selected report mode;
- the sources used;
- any skipped or unreadable sources;
- any essential gaps or conflicts that remain.
- when Lark was used, the verified remote URL and any partial synchronization failures.

## Scope Boundaries

Do not generate PPTX, DOCX, or HTML through this skill. Do not recompute statistics by default, copy external assets automatically, maintain a long-term tracking database, scan all Lark resources, publish silently, switch to bot identity as a fallback, delete remote resources, or publish to services outside the explicit Lark integration request.
