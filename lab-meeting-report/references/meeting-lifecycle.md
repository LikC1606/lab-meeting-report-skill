# Meeting Lifecycle Addendum

Use this reference when a report is being prepared before a meeting, updated after a meeting, or requested as both. It adds continuity and decision-tracking without changing the evidence rules of the selected progress, paper-review, or mixed template.

## Route the request

| Stage | Required source role | Report behavior |
|---|---|---|
| `before` | Current experiment notes, paper notes, results, figures, or other scoped evidence | Prepare a decision-ready report. Do not invent meeting outcomes. |
| `after` | The existing pre-meeting report plus explicit meeting notes, transcript, or action log | Preserve the pre-meeting evidence, record only captured decisions, and append accountable actions. |
| `both` | Current evidence and explicit meeting notes when available | Prepare the pre-meeting report first, then add a clearly attributed post-meeting record. |

If the stage is omitted, use `before` unless the scoped material clearly contains a decision or an assigned action. A positive result is not a meeting decision, and a proposed next step is not an assigned action.

## Continuity inventory

Before drafting, make an inventory of every previous action. Keep the source wording and provenance, then classify the status as `完成`, `进行中`, `受阻`, `未开始`, or `待核验`. Do not infer completion from a related result.

```markdown
## 上次行动复盘

| 行动 | 状态 | 负责人 | 截止时间 | 预期产物 | 当前证据 | 缺口或变化 |
|---|---|---|---|---|---|---|
| <原行动> | <状态> | <姓名或待补充> | <日期或待补充> | <产物> | <来源和定位> | <未完成原因或相对上次变化> |
```

If no previous action was supplied, omit the section rather than filling it with generic tasks. If an owner or due date is absent, write `待补充` in that cell.

## Decision package

Every blocker that needs group input should be written as a decision package. Keep the problem distinct from its impact and distinguish tested options from suggestions.

```markdown
## 当前阻塞与决策包

| 问题 | 影响 | 已尝试措施 | 可选方案 | 需要的支持或决定 | 来源 |
|---|---|---|---|---|---|
| <具体问题> | <对结论、进度或风险的影响> | <措施及结果> | <来源提供的选项；未提供则待补充> | <需要谁提供什么决定或资源> | <路径和定位> |
```

Do not manufacture options. When the source gives only one proposed action, keep it as a proposal and state that no alternative or priority rule was supplied. A decision package may be included in the first-screen `Decision needed` field when it changes the meeting outcome.

## Post-meeting record

Only explicit meeting notes can populate this section. Preserve unresolved questions and mark verbal statements without a source as `未记录` rather than converting them into facts.

```markdown
## 会议决定与行动记录

> 会议记录来源：<会议纪要、逐字稿或明确的会后笔记路径>

### 已记录的决定

| 决定 | 依据或讨论结论 | 来源定位 |
|---|---|---|
| <明确记录的决定> | <记录中的理由；没有则待补充> | <章节、段落或时间戳> |

### 新增行动

| 行动 | 负责人 | 截止时间 | 预期产物 | 完成判据 | 状态 | 来源定位 |
|---|---|---|---|---|---|---|
| <明确分配的行动> | <姓名或待补充> | <日期或待补充> | <产物或待补充> | <判据或待补充> | <未开始/进行中> | <章节、段落或时间戳> |

### 未决问题

- <仍未决定的问题及来源定位>
```

Never fill an owner, due date, artifact, or success criterion from convention. Keep `待补充` visible so the group can complete the record.

## Evidence completeness

Run this check on each result that could change a decision. A missing item is an evidence gap, not evidence that the result failed.

```markdown
## 证据完整度与缺口

| 决策关键结果 | 已核对项目 | 缺失项目 | 对决策的影响 | 来源 |
|---|---|---|---|---|
| <结果或主张> | <目标；数据/样本与划分；方法与配置；对照；样本量/重复；不确定性/统计；单位；图表定位；方法来源> | <逐项列出，或写无> | <是否会改变选择、结论或复现判断> | <路径和定位> |
```

At minimum, check the objective or hypothesis, data or sample and split, method and configuration, comparator or control, sample size or repetitions, uncertainty or statistical test, units, figure/table locator, and method source when one was used. In `brief`, show only gaps that could change the decision. Do not claim significance, causality, or reproducibility when the corresponding check is missing.

## Presenter outline

When requested, create a separate Markdown companion or append an explicitly labeled section. Keep one message per slide and make the spoken interpretation no stronger than the report.

```markdown
# Presenter Outline: <主题>

## 1. <一句话信息点>

- Evidence: <source path and locator>
- Say: <口头解释，包含不确定性边界>
- Discuss: <需要会议回答的问题>
```

Use the meeting duration and local format to choose the number of messages. The outline is Markdown only; this skill does not generate PPTX, DOCX, or HTML.
