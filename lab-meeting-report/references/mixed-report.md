# Mixed Progress And Literature Report

Use this structure when current research progress and literature evidence both matter. Preserve separate attribution, then connect them through an explicit evidence map.

```markdown
# 组会汇报：<研究主题>

> 日期：<日期>｜汇报人：<姓名或待补充>｜报告类型：进展与文献混合｜项目/方向：<项目或方向>
> 会议阶段：<会前/会后/两者>｜听众：<组会/导师/归档>｜时长：<分钟或待补充>

## 决策快照

- **当前状态：** <当前研究与文献的关系及边界；核心数值放在最强证据中>
- **需要决策：** <需要决定的问题；来源未提出时明确说明>
- **最强证据：** <当前证据与文献证据中最影响决策的主张>（来源：<各自的路径及定位>）
- **下一步：** <验证动作>；产物：<结果或文件>；成功判据：<可判断标准>

## 上次行动复盘（有连续性材料时保留）

| 行动 | 状态 | 负责人 | 截止时间 | 预期产物 | 当前证据 | 缺口或变化 |
|---|---|---|---|---|---|---|
| <原行动> | <完成/进行中/受阻/未开始/待核验> | <姓名或待补充> | <日期或待补充> | <产物> | <来源和定位> | <未完成原因或相对上次变化> |

## 当前研究进展

| 当前问题 | 方法或实验 | 结果 | 来源 | 解释边界 |
|---|---|---|---|---|
| <问题> | <方法> | <数值或观察> | <文件、表格或图> | <限制> |

### 失败实验与负面结果

- <尝试、实际结果、可能原因及其证据状态>

## 相关论文与关键启发

| 论文 | 关键主张 | 支持证据 | 局限性 | 与当前问题的相关性 |
|---|---|---|---|---|
| <标题/引用> | <主张> | <图表或结果> | <边界> | <关联> |

## 论文证据与当前结果的对应关系

| 当前观察 | 文献证据 | 一致或冲突 | 解释边界 | 验证动作 |
|---|---|---|---|---|
| <观察及当前来源> | <论文证据及来源> | <一致/部分一致/冲突> | <不可直接比较之处> | <下一实验> |

Do not collapse a correlation in the paper and a causal claim in the current work into the same statement. Keep incompatible metrics, datasets, or conditions visible.

## 证据完整度与缺口

| 决策关键结果或主张 | 已核对项目 | 缺失项目 | 对当前决策的影响 | 来源 |
|---|---|---|---|---|
| <当前结果或文献主张> | <目标；数据/样本与划分；方法与配置；对照；样本量/重复；不确定性/统计；单位；图表定位；方法来源> | <逐项列出，或写无> | <是否影响可比性、迁移或实验选择> | <当前来源或文献定位> |

## 可迁移的方法或实验设计

| 候选方法 | 可迁移部分 | 必要调整 | 风险 | 采用条件 |
|---|---|---|---|---|
| <方法> | <部分> | <调整> | <风险> | <判据> |

## 假设更新与下一步验证

### 假设更新

- 原假设：<内容>
- 当前证据：<支持、反对及各自来源>
- 更新后假设：<内容，明确仍是待验证假设>

### 验证计划

| 验证动作 | 负责人 | 截止时间 | 预期产物 | 成功判据 | 依赖或风险 |
|---|---|---|---|---|---|
| <动作> | <姓名或待补充> | <日期或待补充> | <结果或文件> | <可判断标准> | <依赖或风险> |

## 当前阻塞与决策包（需要组内输入时保留）

| 问题 | 影响 | 已尝试措施 | 可选方案 | 需要的支持或决定 | 来源 |
|---|---|---|---|---|---|
| <具体问题> | <对解释、迁移或验证的影响> | <措施及结果> | <来源提供的选项；未提供则待补充> | <支持或选择> | <路径和定位> |

## 会议决定与行动记录（会后或两者阶段保留）

> 会议记录来源：<会议纪要、逐字稿或明确的会后笔记路径>

| 决定或行动 | 类型 | 负责人 | 截止时间 | 预期产物 | 完成判据 | 状态 | 来源定位 |
|---|---|---|---|---|---|---|---|
| <明确记录的决定或行动> | <决定/行动> | <姓名或待补充> | <日期或待补充> | <产物或待补充> | <判据或待补充> | <未开始/进行中/完成> | <章节、段落或时间戳> |

## 来源与附件

### 当前研究来源

- <实验记录、代码、表格或图片路径>

### 文献来源

- <已核验引用、DOI、URL 或本地 PDF 路径>
```

Writing rules:

- Keep the four decision-snapshot fields in their defined order and localize their labels to the report language.
- Keep current-work and literature provenance separate even when both appear in the strongest-evidence field.
- Keep a requested choice open unless the source or user supplies a decision; label any generated recommendation as a recommendation.
- Avoid repeating the same metric in the decision snapshot, evidence map, and hypothesis update unless each occurrence adds a distinct decision-relevant meaning.
- Attribute current-work evidence and literature evidence separately before synthesizing them.
- State whether conditions, datasets, metrics, and populations are comparable.
- Treat literature-inspired explanations as hypotheses until directly tested.
- Let contradictions drive a validation plan instead of hiding them in a smooth narrative.
- Omit priority labels unless the user or a source explicitly supplies them.
- Do not add alternative causal explanations from general knowledge unless the user explicitly requests hypothesis generation.
- Treat `上次行动复盘` and `会议决定与行动记录` as optional lifecycle sections; omit them when their source material is absent.
- Turn blockers into decision packages with attempted measures, supplied options, requested support, and separate current-work or literature provenance.
- Check evidence completeness before comparing current results with literature; missing design or statistical details must stay visible.
- Keep owner and due-date cells as `待补充` when the source does not provide them.
