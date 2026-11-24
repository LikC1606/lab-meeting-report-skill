# Paper Review Report

Use this structure for weekly paper reading, journal club, or literature-centered reports. Summarize what the paper changes for the user's understanding or work instead of restating the abstract.

## Ordinary journal club: tell the research story

Use the supplied paper title, then explain the question, why it matters to the stated task, and how the method addresses it. Present the key evidence together and distinguish the authors' explanation from what the experiment establishes. End with the most consequential limitation and a source-grounded discussion question. Do not add unknown author, venue, DOI, or owner cells just to fill the template. Do not claim relevance to a project the user has not described. Detailed metadata and audit tables below are optional.

```markdown
# <论文短标题或有证据支持的核心判断>

> 论文：<完整原始标题>。<只写已提供且有用的发表信息；合成论文必须明确标注>

## 本周速览

- **本周进展：** <一句话说明完成了什么，以及目前能得出什么判断>
- **关键证据：** <最有代表性的一条证据；不要只写“见下表”>
- **阻塞与需协助：** <需要解决的具体问题；没有则简短说明>
- **下一步：** <来源中的下一项动作；必要时说明产物与完成标准>

来源：<上述判断对应的文件或定位>

## 这篇论文解决什么问题

<用普通语言说明问题、来源支持的动机和方法如何对应这个问题。首次出现的关键术语作简短解释。不要把推断的动机写成作者事实。>

来源：<论文节号或笔记>

## 证据说明了什么

<概述对照设置。可比结果较多时才用结果表；只有一个观察时用短段落。保留会改变结论的负面结果。>

来源：<论文图表、章节或笔记>

<把作者主张、实验直接支持的结论与汇报者评价分清楚。关键限制紧跟结论；没有统计检验时不要写“不显著”。>

## 值得讨论什么

<围绕论文最重要的证据边界提出具体问题，明确它是汇报者的讨论问题。只有用户提供当前项目时才谈迁移关系；不默认承诺复现。后续行动仅记录来源内容或明确请求的建议。>

## 来源与附件

<列出未在正文链接的必要材料；已在正文完整链接时可省略本节>
```

## Optional continuity and audit

Use `meeting-lifecycle.md` for 上次行动复盘, 当前阻塞与需协助, and 会议决定与行动记录 when relevant. Include 负责人 and 截止时间 only in an action-tracking context; preserve them when supplied. If tracking requires an absent value, mark it unknown in the report language. Do not create columns of unknowns for an ordinary report.

For an explicitly requested audit, add claim-level provenance, evidence-completeness checks, conflicts, and unreadable inputs. Keep ordinary reports readable without dropping consequential uncertainty.


Writing rules:

- Keep the weekly snapshot first and the four fields in order.
- Put the paper's most important limitation near its core contribution.
- Tie major claims to figures, tables, sections, or supplied notes.
- Separate authors' claims from the reporter's evaluation.
- Do not establish novelty without a supported prior-work comparison.
- Label incomplete bibliographic details as `未核验`.
- Do not imply that reproduction or adoption was requested when it was not.
- Do not create alternative explanations or hypotheses unless requested.
- Keep full evidence-completeness tables for `audit`; surface only decision-changing gaps otherwise.
- Omit owner and due-date columns from ordinary reports unless action tracking needs them. Preserve supplied values; localize unknowns when required.
