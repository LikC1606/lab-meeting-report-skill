# Research Progress Report

Use this structure for experiment, implementation, or project-centered group-meeting reports. Include only sections supported by the sources, except essential gaps, which must remain visible as `待补充`.

```markdown
# 组会汇报：<主题>

> 日期：<日期>｜汇报人：<姓名或待补充>｜报告类型：科研进展｜项目/方向：<项目或方向>

## 本次摘要

- 核心进展：<最重要的已验证变化>
- 当前判断：<解释或假设，并明确其性质>
- 下一步：<关键验证动作>

## 需要讨论或决策的事项

1. <问题、已知选项、希望获得的决定>

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

## 失败实验与负面结果

| 尝试 | 来源提供的预期 | 实际结果 | 来源提出的可能原因 | 已排除原因 | 后续处理 |
|---|---|---|---|---|---|
| <尝试> | <预期> | <结果> | <来源提出的待验证解释；未提供则写待补充> | <证据> | <重试、停止或改进> |

## 当前阻塞

| 阻塞项 | 影响 | 已尝试措施 | 需要的支持或决策 |
|---|---|---|---|
| <阻塞> | <范围或延期> | <措施> | <支持> |

## 下一步计划

| 动作 | 预期产物 | 成功判据 | 依赖或风险 |
|---|---|---|---|
| <动作> | <文件、结果或实验> | <可判断标准> | <依赖或风险> |

## 相关文件、代码与参考资料

- <本地相对路径、仓库链接或已核验引用>
```

Writing rules:

- Report outcomes rather than activity alone.
- Preserve negative results because they constrain the next decision.
- Compare results with a baseline or prior state when the source permits it.
- Do not imply statistical significance without supplied evidence.
- Omit priority labels unless the user or a source explicitly supplies them.
- Do not generate alternative causal explanations from general knowledge. If the sources provide none, state that directly or omit the field.
- Do not infer an expected outcome from an experiment name or method. If the source does not state the expectation, write `未提供`.

<!-- P1 -->
- Treat duplicated or translated notes about the same run as repeated provenance for one run, not independent replication or additional sample count. State the full boundary directly without calculating a counterfactual count. In Chinese, use the unambiguous form `同一次运行的重复来源，并非独立复现`; translate that complete meaning in other report languages.

<!-- P2 -->
- A source author's causal wording is still an attributed claim when no isolating test is supplied. Put the uncertainty inside the sentence, for example, “the source suggests X may explain Y”; a `Hypothesis` label does not make “X caused Y” evidence-safe. State each missing check directly and separately, for example, `No ablation was supplied. No significance test was supplied.` Do not say a result is “not statistically significant” when no test was performed; significance is untested.
