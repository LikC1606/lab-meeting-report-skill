# Research Progress Report

Use this structure for experiment, implementation, or project-centered weekly reports. Adapt it to the available material; omit empty sections instead of making the report look like a form.

## Ordinary report: explain the result

For brief and standard reports, lead with the supported outcome and show the main comparisons in one table. Follow with a short explanation of what the results permit the group to conclude, the failed attempt or boundary that changes that conclusion, and the supplied next action or help request. Do not turn the full template below into an obligatory list of sections. Use action tables only when several actions actually need tracking.

```markdown
# <本周最重要的研究进展或待解决问题>

> <日期或来源中的周期；仅保留有用的元信息>

## 本周速览

- **本周进展：** <一句话说明完成了什么，以及目前能得出什么判断>
- **关键证据：** <最有代表性的一条证据；不要只写“见下表”>
- **阻塞与需协助：** <需要解决的具体问题；没有则简短说明>
- **下一步：** <来源中的下一项动作；必要时说明产物与完成标准>

来源：<上述判断对应的文件或定位>

## <主要实验回答了什么>

<先说明这个实验想检验的问题和比较条件，再展示结果。方法变化只保留影响理解的内容。>

| 配置或实验 | <关键指标及单位> | <必要的另一指标及单位> |
|---|---:|---:|
| <来源中的对照> | <原始数值> | <原始数值> |
| <来源中的方法> | <原始数值> | <原始数值> |

来源：<结果文件及定位>

<解释比较能支持什么。把影响解释的限制放在这里，不在每行重复写。>

## <失败尝试或阻塞为什么影响下一步>

<尝试了什么、实际发生了什么、已做哪些处理、仍需要什么帮助。只有来源提供原因时才写原因。多个无关阻塞可以用短列表。>

来源：<对应记录>

## 接下来做什么

<来源中的行动，以及提供的产物和完成标准。没有计划时明确说尚未提供；只有明确请求建议时才补充标为建议的方案。不要把待讨论选择写成已决定。>

来源：<对应记录>

## 来源与附件

<列出未在正文链接的必要材料；已在正文完整链接时可省略本节>
```

## Optional continuity and audit

Use `meeting-lifecycle.md` for 上次行动复盘, 当前阻塞与需协助, and 会议决定与行动记录 when relevant. Include 负责人 and 截止时间 only in an action-tracking context; preserve them when supplied. If tracking requires an absent value, mark it unknown in the report language. Do not create columns of unknowns for an ordinary report.

For an explicitly requested audit, add claim-level provenance, evidence-completeness checks, conflicts, and unreadable inputs. Keep ordinary reports readable without dropping consequential uncertainty.


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
- Omit owner and due-date columns from ordinary reports unless action tracking needs them. Preserve supplied values; localize unknowns when required.

<!-- P1 -->
- Treat duplicated or translated notes about the same run as repeated provenance for one run, not independent replication or additional sample count. State the full boundary directly without calculating a counterfactual count. In Chinese, use the unambiguous form `同一次运行的重复来源，并非独立复现`; translate that complete meaning in other report languages.

<!-- P2 -->
- A source author's causal wording is still an attributed claim when no isolating test is supplied. Put uncertainty inside the sentence, for example, “the source suggests X may explain Y.” State each missing check directly. Do not say a result is “not statistically significant” when no test was performed; significance is untested.
