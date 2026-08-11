# Research Progress Report

Use this structure for experiment, implementation, or project-centered weekly reports. Adapt it to the available material; omit empty sections instead of making the report look like a form.

```markdown
# 组会周报：<主题>

> 日期：<日期>｜汇报人：<姓名或待补充>｜范围：<本周或用户指定周期>
> 会议阶段：<会前/会后/两者>｜来源：<主要目录、笔记或结果文件>

## 本周速览

- **本周进展：** <最重要的结果、变化或阶段状态>
- **关键证据：** <最能支持本周进展的结果、图表或产物>（来源：<路径和定位>）
- **阻塞与需协助：** <卡点、已尝试措施和希望讨论或获得的支持；没有则简短说明>
- **下一步：** <动作>；产物：<文件、结果或实验>；成功判据：<可判断标准>

## 上次行动复盘（有来源时保留）

| 行动 | 状态 | 负责人 | 截止时间 | 当前产物或证据 | 缺口或变化 |
|---|---|---|---|---|---|
| <原行动> | <完成/进行中/受阻/未开始/待核验> | <姓名或待补充> | <日期或待补充> | <来源和定位> | <变化> |

## 本周完成的工作

| 工作或问题 | 本周产物 | 结果或变化 | 来源 |
|---|---|---|---|
| <做了什么及目的> | <代码、数据、实验或笔记> | <支持的结果，不只写活动> | <路径和定位> |

## 关键结果与图表

| 实验或对照 | 指标或观察 | 结果 | 解释边界 | 来源 |
|---|---|---|---|---|
| <名称> | <指标> | <数值或观察> | <重复、统计、对照或外推限制> | <文件、表格或图> |

![<图题>](<相对路径>)

*图：<图题>。来源：<来源>。说明：<该图直接支持什么，以及不能支持什么。>*

## 方法或方案变化（有实质变化时保留）

- **原方案：** <内容>
- **本周变化：** <方法、数据、参数或实现变化>
- **变化原因：** <来源明确提供的原因；未提供则省略>
- **可能影响：** <有证据的解释，或标为待验证假设>

## 失败尝试与负面结果

| 尝试 | 来源提供的预期 | 实际结果 | 已知边界或原因 | 后续处理 | 来源 |
|---|---|---|---|---|---|
| <尝试> | <预期或未提供> | <结果> | <仅写来源支持的原因或待验证解释> | <重试、停止或调整> | <路径和定位> |

## 当前阻塞与需协助（存在时保留）

| 问题 | 影响 | 已尝试措施 | 希望获得的讨论、资源或决定 | 来源 |
|---|---|---|---|---|
| <具体问题> | <对结果或进度的影响> | <措施及结果> | <具体请求；来源未说明则待补充> | <路径和定位> |

## 下周计划

| 动作 | 负责人 | 截止时间 | 预期产物 | 成功判据 | 依赖或风险 |
|---|---|---|---|---|---|
| <动作> | <姓名或待补充> | <日期或待补充> | <文件、结果或实验> | <可判断标准> | <依赖或风险> |

## 会议决定与行动记录（会后或两者阶段保留）

> 会议记录来源：<会议纪要、逐字稿或明确的会后笔记路径>

| 决定或行动 | 类型 | 负责人 | 截止时间 | 预期产物 | 完成判据 | 状态 | 来源定位 |
|---|---|---|---|---|---|---|---|
| <明确记录的决定或行动> | <决定/行动> | <姓名或待补充> | <日期或待补充> | <产物或待补充> | <判据或待补充> | <未开始/进行中/完成> | <定位> |

## 来源与附件

- <本地相对路径、仓库链接或已核验引用>

## 审计附录（仅 audit）

| 关键主张 | 证据类型 | 已核对项目 | 缺失项目及影响 | 来源 |
|---|---|---|---|---|
| <主张> | <事实/计算/解释/假设> | <数据、方法、对照、重复、统计、单位、定位> | <缺失及其决策影响> | <路径和定位> |
```

Writing rules:

- Lead with outcomes rather than chronological activity.
- Keep the four weekly-snapshot fields in order and localize their labels.
- State directly when no blocker or help request was supplied; do not create a false decision.
- Keep a requested choice open unless a source records the decision. Label generated advice as a recommendation.
- Avoid repeating the same metric in the snapshot, table, and analysis unless each use adds distinct meaning.
- Preserve negative results because they constrain the next experiment.
- Compare with a baseline or prior state only when the sources permit it.
- Do not imply statistical significance without supplied evidence.
- Keep evidence-completeness checking internal in `brief` and `standard`; surface only gaps that could change the conclusion or next action.
- Include the audit appendix only for `audit` or a materially conflicting evidence set.
- Omit priority labels unless the user or source supplies them.
- Do not generate alternative causal explanations from general knowledge.
- Do not infer an expected outcome from an experiment name or method. Write `未提供` when the missing expectation matters.
- Treat previous-action review and post-meeting records as optional lifecycle sections.
- Turn blockers into specific help requests. Add options only when supplied.
- Keep owner and due-date cells as `待补充` when absent.

<!-- P1 -->
- Treat duplicated or translated notes about the same run as repeated provenance for one run, not independent replication or additional sample count. State the full boundary directly without calculating a counterfactual count. In Chinese, use the unambiguous form `同一次运行的重复来源，并非独立复现`; translate that complete meaning in other report languages.

<!-- P2 -->
- A source author's causal wording is still an attributed claim when no isolating test is supplied. Put uncertainty inside the sentence, for example, “the source suggests X may explain Y.” State each missing check directly. Do not say a result is “not statistically significant” when no test was performed; significance is untested.
