# Research Progress Report

Use this structure for experiment, implementation, or project-centered group-meeting reports. Include only sections supported by the sources, except essential gaps, which must remain visible as `待补充`.

```markdown
# 组会汇报：<主题>

> 日期：<日期>｜汇报人：<姓名或待补充>｜报告类型：科研进展｜项目/方向：<项目或方向>
> 会议阶段：<会前/会后/两者>｜听众：<组会/导师/归档>｜时长：<分钟或待补充>

## 决策快照

- **当前状态：** <阶段结论及关键边界；核心数值放在最强证据中>
- **需要决策：** <具体选择、阻塞或开放问题；来源未提出时明确说明>
- **最强证据：** <与决策直接相关的主张>（来源：<路径及章节、表格或行号>）
- **下一步：** <动作>；产物：<文件、结果或实验>；成功判据：<可判断标准>

## 上次行动复盘（有连续性材料时保留）

| 行动 | 状态 | 负责人 | 截止时间 | 预期产物 | 当前证据 | 缺口或变化 |
|---|---|---|---|---|---|---|
| <原行动> | <完成/进行中/受阻/未开始/待核验> | <姓名或待补充> | <日期或待补充> | <产物> | <来源和定位> | <未完成原因或相对上次变化> |

## 研究目标与当前假设

- **目标：** <当前阶段要回答的问题>
- **事实：** <输入材料直接支持的事实>
- **假设：** <尚需验证的解释>
- **成功判据：** <可观测、可判断的标准>

## 上次组会后的关键进展

| 事项 | 状态 | 产物或证据 | 相对上次的变化 | 来源 |
|---|---|---|---|---|
| <事项> | <完成/进行中/受阻> | <结果或路径> | <变化> | <文件或笔记> |

## 实验或实现方法

### 设置

- 数据、样本或任务：<内容>
- 方法、模型或系统：<内容>
- 对照或基线：<内容>
- 关键参数与环境：<内容>

### 与前次方案的变化

- <变化、原因及可能影响>

## 结果与证据

| 实验或对照 | 指标 | 结果 | 来源 | 可信度或注意事项 |
|---|---:|---:|---|---|
| <名称> | <指标> | <数值或观察> | <文件、表格或图> | <重复次数、方差或限制> |

![<图题>](<相对路径>)

*图：<图题>。来源：<来源>。解释：<该图直接支持的结论。>*

## 结果分析与可信度

- **事实：** <直接观察>
- **解释：** <当前最合理解释及证据>
- **假设：** <仍未验证的机制或原因>
- **替代解释：** <仅填写来源明确提出的解释；否则说明来源未提供或省略>
- **可信度边界：** <样本量、对照、统计或外推限制>

## 证据完整度与缺口

| 决策关键结果 | 已核对项目 | 缺失项目 | 对决策的影响 | 来源 |
|---|---|---|---|---|
| <结果或主张> | <目标；数据/样本与划分；方法与配置；对照；样本量/重复；不确定性/统计；单位；图表定位；方法来源> | <逐项列出，或写无> | <是否会改变选择、结论或复现判断> | <路径和定位> |

## 失败实验与负面结果

| 尝试 | 来源提供的预期 | 实际结果 | 来源提出的可能原因 | 已排除原因 | 后续处理 |
|---|---|---|---|---|---|
| <尝试> | <预期> | <结果> | <来源提出的待验证解释；未提供则写待补充> | <证据> | <重试、停止或改进> |

## 当前阻塞与决策包

| 问题 | 影响 | 已尝试措施 | 可选方案 | 需要的支持或决定 | 来源 |
|---|---|---|---|---|---|
| <具体问题> | <范围或延期> | <措施及结果> | <来源提供的选项；未提供则待补充> | <支持或选择> | <路径和定位> |

## 会议决定与行动记录（会后或两者阶段保留）

> 会议记录来源：<会议纪要、逐字稿或明确的会后笔记路径>

| 决定或行动 | 类型 | 负责人 | 截止时间 | 预期产物 | 完成判据 | 状态 | 来源定位 |
|---|---|---|---|---|---|---|---|
| <明确记录的决定或行动> | <决定/行动> | <姓名或待补充> | <日期或待补充> | <产物或待补充> | <判据或待补充> | <未开始/进行中/完成> | <章节、段落或时间戳> |

## 下一步计划

| 动作 | 负责人 | 截止时间 | 预期产物 | 成功判据 | 依赖或风险 |
|---|---|---|---|---|---|
| <动作> | <姓名或待补充> | <日期或待补充> | <文件、结果或实验> | <可判断标准> | <依赖或风险> |

## 相关文件、代码与参考资料

- <本地相对路径、仓库链接或已核验引用>
```

Writing rules:

- Report outcomes rather than activity alone.
- Keep the four decision-snapshot fields in their defined order and localize their labels to the report language.
- If no decision was supplied, state that directly and surface the strongest blocker or open question without creating a false choice.
- Keep a requested choice open unless the source or user supplies a decision; label any generated recommendation as a recommendation.
- Avoid repeating the same metric in the decision snapshot, evidence table, and analysis unless each occurrence adds a distinct decision-relevant meaning.
- Preserve negative results because they constrain the next decision.
- Compare results with a baseline or prior state when the source permits it.
- Do not imply statistical significance without supplied evidence.
- Omit priority labels unless the user or a source explicitly supplies them.
- Do not generate alternative causal explanations from general knowledge. If the sources provide none, state that directly or omit the field.
- Do not infer an expected outcome from an experiment name or method. If the source does not state the expectation, write `未提供`.
- Treat `上次行动复盘` and `会议决定与行动记录` as optional lifecycle sections; omit them when their source material is absent.
- Make every blocker a decision package with a problem, attempted measures, options, requested support, and source. Do not invent options or meeting outcomes.
- Check decision-critical results for evidence completeness and show missing checks that could change the decision.
- Keep owner and due-date cells as `待补充` when the source does not provide them.

<!-- P1 -->
- Treat duplicated or translated notes about the same run as repeated provenance for one run, not independent replication or additional sample count. State the full boundary directly without calculating a counterfactual count. In Chinese, use the unambiguous form `同一次运行的重复来源，并非独立复现`; translate that complete meaning in other report languages.

<!-- P2 -->
- A source author's causal wording is still an attributed claim when no isolating test is supplied. Put the uncertainty inside the sentence, for example, “the source suggests X may explain Y”; a `Hypothesis` label does not make “X caused Y” evidence-safe. State each missing check directly and separately, for example, `No ablation was supplied. No significance test was supplied.` Do not say a result is “not statistically significant” when no test was performed; significance is untested.
