# Meeting Lifecycle Addendum

Use this reference when previous actions, post-meeting notes, or presentation preparation are in scope. Add continuity without making lifecycle fields mandatory for an ordinary weekly summary.

## Route the request

| Stage | Source role | Report behavior |
|---|---|---|
| `before` | Current notes, results, figures, paper notes, or other scoped weekly material | Prepare a meeting-ready weekly summary. Do not invent meeting outcomes. |
| `after` | Existing report plus explicit meeting notes, transcript, or action log | Preserve pre-meeting evidence and record only captured decisions and assignments. |
| `both` | Current evidence and explicit meeting notes when available | Prepare the weekly summary first, then add a separately attributed post-meeting record. |

If the stage is omitted, use `before` unless the material clearly contains a decision or assigned action. A positive result is not a meeting decision, and a proposed next step is not an assigned action.

## Continuity inventory

Inventory supplied previous actions before drafting. Keep source wording and provenance, then classify status as `完成`, `进行中`, `受阻`, `未开始`, or `待核验`. Do not infer completion from a related result.

```markdown
## 上次行动复盘

| 行动 | 状态 | 负责人 | 截止时间 | 当前产物或证据 | 缺口或变化 |
|---|---|---|---|---|---|
| <原行动> | <状态> | <姓名或待补充> | <日期或待补充> | <来源和定位> | <变化> |
```

Omit this section when no previous action was supplied. Keep missing owners and dates as `待补充`.

## Help request and decision package

Write a normal blocker as a concrete help request:

```markdown
## 当前阻塞与需协助

| 问题 | 影响 | 已尝试措施 | 希望获得的讨论、资源或决定 | 来源 |
|---|---|---|---|---|
| <问题> | <影响> | <措施及结果> | <具体请求> | <来源> |
```

Use a fuller decision package only when the source actually supplies competing options or the user asks the group to choose. Keep tested options distinct from suggestions. Do not manufacture alternatives merely to fill a table.

## Post-meeting record

Populate this section only from explicit meeting notes. Preserve unresolved questions and keep missing details visible.

```markdown
## 会议决定与行动记录

> 会议记录来源：<纪要、逐字稿或明确的会后笔记>

### 已记录的决定

| 决定 | 依据或讨论结论 | 来源定位 |
|---|---|---|
| <明确记录的决定> | <记录中的理由；没有则待补充> | <定位> |

### 新增行动

| 行动 | 负责人 | 截止时间 | 预期产物 | 完成判据 | 状态 | 来源定位 |
|---|---|---|---|---|---|---|
| <明确分配的行动> | <姓名或待补充> | <日期或待补充> | <产物或待补充> | <判据或待补充> | <未开始/进行中> | <定位> |

### 未决问题

- <仍未决定的问题及来源定位>
```

When a meeting decision resolves a pre-meeting blocker, retain the old blocker for traceability but label it `会前问题，已由会议决定解决` or an equivalent localized phrase. Do not leave it presented as current. Record any replacement action separately.

Never fill an owner, due date, artifact, or success criterion from convention.

## Evidence completeness

Run the evidence-completeness check in the background for every result that could change a conclusion or action. Check the objective, data or sample and split, method and configuration, comparator, repetitions, uncertainty or statistical test, units, figure or table locator, and method source.

- In `brief`, show only a missing item that changes the immediate interpretation or next action.
- In `standard`, mention consequential gaps beside the affected result or in a short limitations note.
- In `audit`, add the full claim-level completeness table.

A missing check is a gap, not evidence that a result failed. Do not claim significance, causality, or reproducibility when the corresponding evidence is absent.

## Presenter outline

When a presentation is requested, read `presentation-export.md` and create a separate companion from the validated report. The minimal plain-Markdown shape is:

```markdown
# Presenter Outline: <主题>

## 1. <一句话信息点>

- Evidence: <source path and locator>
- Say: <口头解释和不确定性边界>
- Discuss: <需要会议回答的问题>
```

Keep one message per slide and use the meeting duration to control scope. Generate an exported format only through the selected optional adapter.
