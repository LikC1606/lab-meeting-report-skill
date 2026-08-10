# Lab Meeting Report

[![Validate skill](https://github.com/LikC1606/lab-meeting-report-skill/actions/workflows/validate-skill.yml/badge.svg)](https://github.com/LikC1606/lab-meeting-report-skill/actions/workflows/validate-skill.yml)
[![skills.sh installs](https://skills.sh/b/LikC1606/lab-meeting-report-skill)](https://skills.sh/LikC1606/lab-meeting-report-skill)
[![GitHub release](https://img.shields.io/github/v/release/LikC1606/lab-meeting-report-skill)](https://github.com/LikC1606/lab-meeting-report-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

Turn scattered experiment notes, results, and papers into a dated Markdown report that keeps negative results, uncertainty, and source paths visible.

Use `lab-meeting-report` for research progress reports, journal club notes, experiment retrospectives, or a combined progress-and-literature report. Optional Feishu/Lark intake and publishing are available when the host environment provides the required tools.

![Rendered research progress report example](assets/lab-meeting-report-preview.png)

[中文文档](README.zh-CN.md) | [Complete examples](#complete-examples) | [Measured quality](#measured-quality) | [Contributing](CONTRIBUTING.md)

## Start Here

Install the skill from its public GitHub source:

```bash
npx skills add https://github.com/LikC1606/lab-meeting-report-skill --skill lab-meeting-report
```

For a global, non-interactive installation on macOS or Linux:

```bash
npx skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

On Windows PowerShell, use `npx.cmd`:

```powershell
npx.cmd skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

The installer requires Node.js and `npx`. You can also inspect the skill, install count, and security audits on [skills.sh](https://skills.sh/LikC1606/lab-meeting-report-skill/lab-meeting-report).

Then give your agent a concrete source and outcome:

```text
Use $lab-meeting-report to read this week's experiment notes and results,
then create a lab meeting report with failures, blockers, and next steps.
```

The default output is a real file, not a chat-only outline:

```text
reports/group-meeting/YYYY-MM-DD.md
```

## Why This Skill

Most report generators optimize for a smooth summary. Research reporting also needs to preserve evidence that makes the story less smooth.

This skill is designed to:

- retain failed experiments, negative results, blockers, and conflicting values;
- keep observed facts, interpretations, and hypotheses visibly separate;
- copy supplied measurements and citations without silently filling gaps;
- update an existing dated report without deleting manual content;
- turn next steps into actions with artifacts and success criteria;
- read only the files or Feishu/Lark resources explicitly placed in scope.

## Complete Examples

All example data, paper notes, and results are synthetic. Each workflow includes its source material and generated report so you can audit the transformation end to end.

| Workflow | Source material | Generated report |
|---|---|---|
| Research progress | [Notes](examples/research-progress/input-notes.md) and [result files](examples/research-progress/results) | [Report](examples/research-progress/report.md) |
| Journal club | [Input notes](examples/journal-club/input-notes.md) and [paper notes](examples/journal-club/papers/synthetic-retrieval-notes.md) | [Report](examples/journal-club/report.md) |
| Progress plus literature | [Combined notes](examples/mixed/input-notes.md), [results](examples/mixed/results/current_experiment.csv), and [paper notes](examples/mixed/papers/synthetic-balanced-retrieval.md) | [Report](examples/mixed/report.md) |

Additional prompts:

```text
Use $lab-meeting-report to read paper.pdf and create a journal club report
focused on the method, key evidence, limitations, and relevance to my work.
```

```text
Use $lab-meeting-report to combine my latest results with these paper notes,
explain agreements and conflicts, and propose the next validation experiment.
```

## Report Modes

| Mode | Best for | Core sections |
|---|---|---|
| Research progress | Experiments, implementations, ongoing projects | Goal, method, evidence, negative results, blockers, next actions |
| Paper review | Journal clubs, paper reading, literature discussions | Research gap, method, evidence, novelty, limitations, reproducibility |
| Mixed | Connecting current work to literature | Current results, literature mapping, hypothesis update, validation plan |

Supported inputs include pasted notes, Markdown, text, PDF, CSV, Excel, figures, screenshots, and explicitly selected Feishu/Lark resources. Availability depends on the parsing tools provided by the host agent.

## Evidence Rules

- Never invent results, metrics, citations, authors, venues, DOI values, or causal explanations.
- Preserve source identifiers and copy experimental measurements exactly.
- Do not introduce new calculations unless the user requests them or a supplied source defines them.
- Retain conflicting values when no authority rule is supplied.
- Mark essential missing information as `待补充` and unverified citation data as `未核验`.
- Preserve manually written content when updating an existing report.

Read the complete workflow in [`lab-meeting-report/SKILL.md`](lab-meeting-report/SKILL.md).

## Measured Quality

The v1.2 candidate was evaluated three times on each of eight public synthetic research-progress cases. The cases cover numeric fidelity, conflicting sources, buried negative results, unsupported causal language, duplicated notes, scoped directory reading, safe report updates, and unavailable sources.

| Configuration | Strict hard passes | Mean expectation pass rate |
|---|---:|---:|
| v1.2 candidate | 24/24 | 1.000 |
| Frozen v1.1 baseline | 0/24 | 0.818 |

The hard gate requires every deterministic expectation in a report to pass. Codex also audited the 24 candidate reports claim by claim and found no unsupported critical claim. That audit used the same authoring agent, so it was neither independent nor blinded. The results apply only to this synthetic corpus and do not establish universal hallucination prevention or reviewer preference.

Review the [evaluation design](docs/superpowers/specs/2026-07-13-lab-meeting-report-v1.2-quality-evaluation-design.md), [public cases](evals/research-progress/cases), [versioned benchmark](benchmarks/v1.1-v1.2/benchmark.md), and [claim-level self-audit](benchmarks/v1.1-v1.2/semantic-review-final.json).

## Optional Feishu/Lark Integration

Local Markdown generation does not require Feishu/Lark. Reading or publishing Feishu/Lark content additionally requires:

- [`lark-cli`](https://github.com/larksuite/cli);
- the official `lark-shared`, `lark-doc`, `lark-im`, `lark-minutes`, and `lark-vc` skills needed for the requested operation;
- a user-authorized Lark identity with the minimum required scopes.

The workflow reads only explicitly selected resources, validates the local Markdown first, uses user identity, and verifies the remote document before recording its URL. It does not silently switch to bot identity, overwrite an entire existing document, or delete remote resources.

## Scope And Compatibility

The repository follows the portable Agent Skills folder format and includes Codex interface metadata. Core output is Markdown; this skill does not generate PPTX, DOCX, or HTML. It does not search for additional literature unless the user explicitly requests it.

File parsing and Feishu/Lark operations depend on the tools available in the host environment. Review the skill before installation and keep sensitive research data within an environment you trust.

## Feedback And Contributions

- Report a reproducible problem with the [bug form](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=bug_report.yml).
- Propose a reusable improvement with the [feature form](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=feature_request.yml).
- Share a synthetic or anonymized workflow with the [example form](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=example_submission.yml).
- Ask questions and compare workflows in [Discussions](https://github.com/LikC1606/lab-meeting-report-skill/discussions).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development and pull-request workflow and [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## 中文说明

完整中文安装、示例、能力边界和贡献说明见 [README.zh-CN.md](README.zh-CN.md)。

## License

[MIT](LICENSE)
