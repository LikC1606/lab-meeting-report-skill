# Lab Meeting Report Skill

Turn research notes, experiment results, papers, chats, and meeting transcripts into evidence-grounded Markdown reports for lab meetings and journal clubs. Optional Feishu/Lark publishing included.

[中文说明](#中文说明)

## What It Does

`lab-meeting-report` creates a real, dated Markdown document instead of stopping at an outline or chat response. It supports:

Use it as a lab meeting report generator, research progress report writer, or journal club reporting workflow without changing tools.

- **Research progress reports** with experiments, results, failed attempts, blockers, and next-step success criteria
- **Paper and journal club reports** with methods, evidence, novelty, limitations, and reproducibility checks
- **Mixed reports** that connect current results with literature evidence and turn conflicts into validation plans
- Evidence provenance, explicit uncertainty, and separation of facts, interpretations, and hypotheses
- Safe updates to existing dated reports without silently deleting manual content
- Optional, bounded Feishu/Lark source intake and cloud-document publishing

The default output language is Simplified Chinese. Technical terms, model names, metrics, and citations remain in their precise original form.

## Install

macOS and Linux:

```bash
npx skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

Windows PowerShell:

```powershell
npx.cmd skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

## Quick Start

```text
Use $lab-meeting-report to read this week's experiment notes and results,
then create a lab meeting report with failures, blockers, and next steps.
```

```text
Use $lab-meeting-report to read paper.pdf and create a journal club report
focused on the method, key evidence, limitations, and relevance to my work.
```

```text
Use $lab-meeting-report to combine my latest results with these paper notes,
explain agreements and conflicts, and propose the next validation experiment.
```

By default, the skill writes:

```text
reports/group-meeting/YYYY-MM-DD.md
```

## Report Modes

| Mode | Best for | Core sections |
|---|---|---|
| Research progress | Experiments, implementations, ongoing projects | Goal, method, evidence, negative results, blockers, next actions |
| Paper review | Journal clubs, paper reading, literature discussions | Research gap, method, key evidence, novelty, limitations, reproducibility |
| Mixed | Connecting current work to literature | Current results, literature mapping, hypothesis update, validation plan |

## Accepted Inputs

- Pasted notes and status updates
- Markdown and text files
- Research papers and reports in PDF
- CSV and Excel result tables
- Figures and screenshots
- Explicitly selected Feishu/Lark documents, chats, meetings, and Minutes artifacts

The skill reads only material placed in scope. It does not scan unrelated directories or all Lark resources by default.

## Evidence And Safety Rules

- Never invent results, metrics, citations, authors, venues, DOI values, or causal explanations.
- Keep observed facts, interpretations, and hypotheses visibly separate.
- Preserve failed experiments and negative results.
- Retain conflicting source values with provenance instead of silently reconciling them.
- Mark essential missing information as `待补充` and unverified citation data as `未核验`.
- Preserve manually written content when updating an existing report.

## Optional Feishu/Lark Integration

Local Markdown generation works without Feishu/Lark.

To read Lark sources or publish a report as a Lark cloud document, the host environment also needs:

- [`lark-cli`](https://github.com/larksuite/cli)
- The current official `lark-shared`, `lark-doc`, `lark-im`, `lark-minutes`, and `lark-vc` skills for the operations you use
- A user-authorized Lark identity with the minimum required scopes

The Lark workflow is local-first:

1. Read only explicitly selected Lark resources.
2. Generate and validate the local Markdown report.
3. Create or safely append to a Lark cloud document.
4. Upload local report images when requested.
5. Verify the remote document before writing its URL back to the local report.

It does not silently switch to bot identity, overwrite an entire existing document, or delete remote resources.

## Compatibility

The repository follows the portable Agent Skills folder format and includes Codex interface metadata. File parsing and Lark operations depend on the tools available in the host agent environment.

## 中文说明

`lab-meeting-report` 用于把实验记录、论文笔记、结果表格、图片、聊天和会议记录整理为可追溯的组会 Markdown 文档。

### 核心能力

- 科研进展汇报：目标、方法、结果、失败实验、阻塞和下一步判据
- 论文阅读汇报：研究问题、方法、关键证据、创新、局限和可复现性
- 混合型汇报：把当前研究结果与文献证据对应起来，形成下一步验证计划
- 明确区分事实、解释和假设
- 保留负面结果、冲突证据和来源信息
- 默认生成 `reports/group-meeting/YYYY-MM-DD.md`
- 可选读取飞书文档、指定聊天和妙记，并同步为飞书云文档

### 安装

Windows PowerShell：

```powershell
npx.cmd skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

macOS 或 Linux：

```bash
npx skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

### 使用示例

```text
使用 $lab-meeting-report 读取本周实验记录和结果，生成组会 Markdown，
保留失败实验、当前阻塞和下一步成功判据。
```

```text
使用 $lab-meeting-report 读取这篇论文，生成论文阅读组会报告，
重点分析方法、关键证据、局限性和对当前工作的启发。
```

### 飞书集成

本地 Markdown 功能不依赖飞书。启用飞书集成时，需要安装并授权 `lark-cli`，同时具备当前操作对应的官方 Lark skills。该流程只读取你明确指定的文档、聊天或会议范围，并先生成本地报告，再同步飞书。

### 可靠性原则

- 不编造数据、引用、DOI、作者或结论
- 不隐藏失败实验和负面结果
- 不把推测写成事实
- 不默认扫描全部飞书资源
- 不静默覆盖或删除远程文档

## License

MIT
