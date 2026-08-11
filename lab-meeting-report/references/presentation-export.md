# Presentation Export

Use this reference only when the user asks for a presenter outline, slides, PDF, HTML presentation, or PPTX. Treat the validated Markdown report as the content source and presentation files as derived artifacts.

## Choose the lightest suitable output

| Request | Preferred output | Adapter |
|---|---|---|
| Talking points or no slide tool available | `YYYY-MM-DD-slides.md` | Plain Markdown |
| Fast Markdown presentation, PDF, HTML, or simple PPTX | Marp Markdown | Marp CLI |
| Academic slides with citations, equations, or multiple publishing formats | `.qmd` | Quarto |
| Natively editable PowerPoint with custom charts, tables, and templates | `.pptx` | Existing PptxGenJS adapter |
| Interactive web presentation explicitly requested | Slidev Markdown | Slidev |

Do not search for another slide project during an ordinary report run. Do not install or execute a network package silently. If the preferred adapter is unavailable, create plain Markdown slides and report the missing dependency.

## Build the deck

Create the companion next to the report by default:

```text
reports/group-meeting/YYYY-MM-DD-slides.md
```

Derive it from the validated report and keep:

- one message per slide;
- the related evidence source or figure;
- speaker notes that preserve uncertainty boundaries;
- a discussion question where group input is needed;
- a final next-step slide.

Every slide must retain three semantic roles: `Evidence`, `Say`, and `Discuss`. Localize their visible labels when appropriate. For an audience-facing deck, keep the evidence as a concise visible source footer, place `Say` in speaker notes when the format supports notes, and show `Discuss` only when the audience needs to act on it. A slide with no live discussion still needs a short presenter-note marker such as `Discuss: none` so the intent remains machine-checkable.

Use the meeting duration when supplied. As a default rhythm, prefer a title slide, one overview slide, a small number of evidence slides, one blocker or discussion slide, and one next-step slide. Reduce the number of slides before shrinking content.

For a presentation of 10 minutes or less, normally use 5-7 slides including the title. Exceed that range only when the supplied evidence requires a separate safety-critical or decision-critical slide. Do not turn every report section into a slide.

Do not invent a title, result, citation, image, or metric that is absent from the report. Keep relative asset paths valid from the deck file.
Preserve run IDs, seed labels, model names, and configuration identifiers exactly. Do not compress distinct identifiers into shorthand such as `seed-13/29/42`; write `seed-13`, `seed-29`, and `seed-42` so every claim remains searchable and traceable.
Preserve the operational scope of blockers and requests. For example, an export-permission blocker must remain `导出权限` or `export permission`; do not broaden it to generic data access or `数据权限`.
When a paper informs a slide, preserve its complete supplied title on that slide or in its speaker notes. Do not replace the title with a generic label such as "the paper."

## Marp

Choose Marp for the lowest-friction Markdown route. Add Marp frontmatter and slide separators to the companion Markdown. Use an already installed `marp` command to export only when the user requested an exported format.

Typical exports are:

```bash
marp slides.md --html
marp slides.md --pdf
marp slides.md --pptx
```

Standard Marp PPTX output normally contains pre-rendered slide pages and is not fully editable. Use `--pptx-editable` only when the user explicitly accepts its experimental status; verify text, equations, tables, and images after conversion. Never describe a standard Marp PPTX as natively editable.

Official project: [Marp CLI](https://github.com/marp-team/marp-cli)

## Quarto

Choose Quarto when citations, equations, code, or academic publishing formats are central. Write a `.qmd` companion and use an installed `quarto` command. Quarto supports `revealjs`, `pptx`, and `beamer` presentation formats.

Typical exports are:

```bash
quarto render slides.qmd --to revealjs
quarto render slides.qmd --to pptx
quarto render slides.qmd --to beamer
```

Verify citations, equations, code output, fonts, and image paths in the produced file. Do not assume a custom PowerPoint template exists unless the user supplies one.

Official documentation: [Quarto presentations](https://quarto.org/docs/presentations/)

## PptxGenJS

Choose PptxGenJS only when the user needs editable PowerPoint elements and the environment already contains a trusted generator or template adapter. PptxGenJS is a JavaScript library rather than a report-to-slide CLI, so do not improvise an untested layout generator inside a routine report run.

Pass structured slide content to the existing adapter, including the title, body, source, image path, speaker note, and layout hint. Verify the resulting `.pptx` opens and that text, tables, charts, and images remain editable where promised.

Official project: [PptxGenJS](https://github.com/gitbrent/PptxGenJS)

## Slidev

Use Slidev only when the user explicitly prefers an interactive web-first presentation or the project already uses Slidev. Keep it optional because its themes, Vue components, and browser export path add more dependencies than the default weekly-report workflow.

Official project: [Slidev](https://github.com/slidevjs/slidev)

## Verification

For every derived presentation:

- confirm all key claims match the validated report;
- confirm figures and captions point to the correct sources;
- preserve negative results and uncertainty that affect interpretation;
- open or render exported artifacts when the environment supports it;
- report the adapter, output path, unverified visual elements, and editability limits.
