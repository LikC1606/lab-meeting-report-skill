# Mixed Progress And Literature Report

Use this structure when current research progress and literature both matter. Keep their provenance separate, then show how the paper changes the interpretation or next experiment.

```markdown
# 组会周报：<研究主题>

> 日期：<日期>｜汇报人：<姓名或待补充>｜报告类型：进展与文献混合
> 会议阶段：<会前/会后/两者>｜来源：<当前工作与文献范围>

## 本周速览

- **本周进展：** <当前工作与文献阅读共同带来的核心进展>
- **关键证据：** <最重要的当前结果和相关论文证据，分别注明来源>
- **阻塞与需协助：** <当前解释、实验或迁移卡点，以及具体请求>
- **下一步：** <验证动作>；产物：<结果或文件>；成功判据：<判据>

## 上次行动复盘（有来源时保留）

| 行动 | 状态 | 负责人 | 截止时间 | 当前产物或证据 | 缺口或变化 |
|---|---|---|---|---|---|
| <原行动> | <状态> | <姓名或待补充> | <日期或待补充> | <来源> | <变化> |

## 当前研究进展

| 当前问题 | 本周方法或实验 | 结果 | 解释边界 | 来源 |
|---|---|---|---|---|
| <问题> | <方法> | <数值或观察> | <限制> | <文件、表格或图> |

### 失败尝试与负面结果

- <尝试、实际结果、来源支持的原因边界及后续处理>

## 本周论文与关键启发

| 论文 | 关键主张 | 支持证据 | 局限性 | 与当前问题的关系 |
|---|---|---|---|---|
| <标题或引用> | <主张> | <图表或结果> | <边界> | <关联> |

## 当前结果与文献的对应关系

| 当前观察 | 文献证据 | 一致、冲突或不可比 | 解释边界 | 下一验证动作 |
|---|---|---|---|---|
| <观察及来源> | <论文证据及来源> | <关系> | <条件、指标或人群差异> | <动作> |

Do not merge a correlation in the paper with a causal claim in current work. Keep incompatible metrics, datasets, and conditions visible.

## 当前阻塞与需协助（存在时保留）

| 问题 | 影响 | 已尝试措施 | 希望讨论或获得的支持 | 来源 |
|---|---|---|---|---|
| <问题> | <对解释、迁移或实验的影响> | <措施及结果> | <具体请求> | <当前来源或文献定位> |

## 下周验证计划

| 验证动作 | 负责人 | 截止时间 | 预期产物 | 成功判据 | 依赖或风险 |
|---|---|---|---|---|---|
| <动作> | <姓名或待补充> | <日期或待补充> | <结果或文件> | <判据> | <风险> |

## 会议决定与行动记录（会后或两者阶段保留）

| 决定或行动 | 负责人 | 截止时间 | 预期产物 | 完成判据 | 来源定位 |
|---|---|---|---|---|---|
| <明确记录的内容> | <姓名或待补充> | <日期或待补充> | <产物或待补充> | <判据或待补充> | <定位> |

## 来源与附件

### 当前研究来源

- <实验记录、代码、表格或图片路径>

### 文献来源

- <已核验引用、DOI、URL 或本地 PDF 路径>

## 审计附录（仅 audit）

| 关键结果或主张 | 证据类型 | 已核对项目 | 缺失项目及影响 | 来源 |
|---|---|---|---|---|
| <当前结果或文献主张> | <当前事实/文献事实/解释/假设> | <项目> | <缺失与影响> | <来源> |
```

Writing rules:

- Keep the weekly snapshot first and the four fields in order.
- Attribute current-work evidence and literature evidence separately before synthesis.
- State whether conditions, datasets, metrics, and populations are comparable.
- Treat literature-inspired explanations as hypotheses until tested.
- Let contradictions drive the next validation action instead of hiding them.
- Keep a requested choice open unless a source records the decision.
- Avoid repeating metrics without adding a new implication.
- Do not add alternative causal explanations from general knowledge unless requested.
- Keep full evidence-completeness tables for `audit`; surface only decision-changing gaps otherwise.
- Keep owner and due-date cells as `待补充` when absent.
