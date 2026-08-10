# Paper Review Report

Use this structure for paper-reading, journal-club, or literature-centered group-meeting reports. Evaluate the evidence instead of restating the abstract.

```markdown
# 组会汇报：<论文主题或标题>

> 日期：<日期>｜汇报人：<姓名或待补充>｜报告类型：论文阅读｜项目/方向：<相关方向>

## 决策快照

- **当前状态：** <论文的核心主张、证据强度及最重要边界；核心数值放在最强证据中>
- **需要决策：** <是否复用、复现或继续阅读；来源未提出时明确说明>
- **最强证据：** <支撑核心主张的结果>（来源：<图、表、章节或笔记路径>）
- **下一步：** <动作>；产物：<复现结果、评审记录或方案>；成功判据：<可判断标准>

## 论文信息与一句话贡献

| 字段 | 已核验信息 |
|---|---|
| 标题 | <标题> |
| 作者 | <作者> |
| 期刊或会议 | <venue 或未核验> |
| 年份 | <年份或未核验> |
| DOI/URL | <仅填写输入中存在或已核验的值> |
| 本地来源 | <PDF 或笔记路径> |

**一句话贡献：** <问题、方法、主要证据和适用范围>

## 研究背景与问题

- 已知背景：<内容>
- 关键缺口：<内容>
- 论文问题或假设：<内容>
- 该问题为何重要：<内容>

## 核心方法

| 组成 | 内容 | 评价时需关注的假设 |
|---|---|---|
| 数据/样本 | <内容> | <代表性、偏差或泄漏> |
| 方法/模型 | <内容> | <关键假设> |
| 对照/基线 | <内容> | <是否公平充分> |
| 评价指标 | <内容> | <是否匹配研究问题> |

## 关键结果与证据

| 主张 | 证据 | 定量结果 | 来源图表/章节 | 支持强度与边界 |
|---|---|---:|---|---|
| <主张> | <实验或分析> | <数值或待补充> | <Fig./Table/Section> | <判断> |

![<图题>](<相对路径>)

*图：<图题>。来源：<论文图号或文件>。解释：<图直接支持的主张。>*

## 创新点

1. <相对已有工作的实质变化及证据>

## 局限性与可信度

- 内部有效性：<对照、统计、消融、敏感性>
- 外部有效性：<数据、任务、人群或场景边界>
- 替代解释：<仅填写论文或用户明确提出的解释；否则说明未提供或省略>
- 作者声明的局限：<内容>
- 汇报者补充的局限：<内容，标明是评价>

## 可复现性

| 项目 | 状态 | 证据或缺口 |
|---|---|---|
| 数据 | <公开/受限/未说明> | <链接或说明> |
| 代码 | <公开/缺失/未核验> | <链接或说明> |
| 参数与环境 | <充分/部分/不足> | <说明> |
| 复现实验成本 | <低/中/高/待评估> | <依据> |

## 对当前研究的启发

- 可直接复用：<方法、指标、对照或工具>
- 需要验证后复用：<内容及验证条件>
- 不宜迁移：<边界与原因>
- 可形成的新假设：<仅在用户要求生成假设时填写，并明确标为待验证>

## 讨论问题与参考文献

1. <开放问题>

### 参考文献

- <已核验引用；保留 DOI、URL 或本地路径>
```

Writing rules:
- Keep the four decision-snapshot fields in their defined order and localize their labels to the report language.
- Include the paper's most important limitation in `当前状态`; do not imply that reuse or reproduction was requested when no such decision was supplied.
- Keep a requested relevance or reproduction choice open unless the source or user supplies a decision; label any generated recommendation as a recommendation.
- Avoid repeating the same result in the decision snapshot, key-results table, and limitations unless each occurrence adds a distinct evaluation.
- Tie every major claim to a figure, table, section, or quoted source note.
- Separate the authors' claim from the reporter's evaluation.
- Do not describe novelty as established without a supported comparison to prior work.
- Label incomplete bibliographic details as `未核验` rather than guessing.
- Do not generate alternative causal explanations or new hypotheses unless the user requests them; distinguish any requested hypothesis from paper evidence.
