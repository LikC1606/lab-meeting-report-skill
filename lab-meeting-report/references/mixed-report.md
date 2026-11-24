# Mixed Progress And Literature Report

Use this structure when current research progress and literature both matter. Keep their provenance separate, then show how the paper changes the interpretation or next experiment.

## Ordinary mixed report: connect without conflating

Lead with the current-work result and the question it leaves open. Show current measurements together. Explain the paper's relevant finding in prose, followed immediately by the differences in data, method, or conditions that prevent direct transfer. Avoid copying all literature metrics into the opening. If the user asks which experiment to run, label the proposed control and expected distinction as a recommendation; preserve supplied values and do not invent expected scores or claim the experiment was agreed.

```markdown
# <当前结果与尚未回答的核心问题>

> <日期或来源中的周期；合成材料必须明确标注>

## 本周速览

- **本周进展：** <一句话说明完成了什么，以及目前能得出什么判断>
- **关键证据：** <最有代表性的一条证据；不要只写“见下表”>
- **阻塞与需协助：** <需要解决的具体问题；没有则简短说明>
- **下一步：** <来源中的下一项动作；必要时说明产物与完成标准>

来源：<上述判断对应的文件或定位>

## 当前实验告诉了我们什么

<交代任务与比较条件，把关键指标放在一个表或短段落中。区分整体系统收益与单个组件的贡献。>

来源：<当前实验记录和结果定位>

<解释结果支持的判断，以及仍需保留的失败、冲突或不确定性。>

## 论文能提供什么，哪些不能直接迁移

<保留完整论文标题。说明与当前问题有关的方法或结果，随后解释数据、组件、指标或运行条件差异。不要把两组不可比数字放在一起排名。>

来源：<论文定位及当前实验定位，明确各自支持什么>

## 下一步要回答的问题

<记录来源中的问题与下一步。用户明确请求实验建议时，可以给出最小可行对照，解释它能区分什么、仍排除不了什么，标明是建议。不要编造预计分数、时间、资源或已达成的决定。>

来源：<提供该问题或计划的记录>

## 来源与附件

<列出未在正文链接的必要材料；已在正文完整链接时可省略本节>
```

## Optional continuity and audit

Use `meeting-lifecycle.md` for 上次行动复盘, 当前阻塞与需协助, and 会议决定与行动记录 when relevant. Include 负责人 and 截止时间 only in an action-tracking context; preserve them when supplied. If tracking requires an absent value, mark it unknown in the report language. Do not create columns of unknowns for an ordinary report.

For an explicitly requested audit, add claim-level provenance, evidence-completeness checks, conflicts, and unreadable inputs. Keep ordinary reports readable without dropping consequential uncertainty.


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
- Omit owner and due-date columns from ordinary reports unless action tracking needs them. Preserve supplied values; localize unknowns when required.
