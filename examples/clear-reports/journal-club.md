# 难负例检索训练值得讨论，但跨域迁移证据仍有限

> 合成演示：论文及结果均为虚构，不可作为真实研究引用。
> 论文：Contrastive Retrieval for Low-Resource Intent Classification

## 本周速览

**本周进展：** 梳理了利用难负例训练改善低资源意图检索的方法，以及现有结果支持到哪里。

**关键证据：** 提议方法在域内和跨域 macro-F1 上均高于标准 bi-encoder；去掉 hard-negative mining 后，域内结果低于完整方法。

**阻塞与需协助：** 笔记未提供数据和代码，复现条件不完整；没有记录具体的组内资源请求。

**下一步：** 材料未给出后续行动。本次可讨论：现有对照是否足以支持“难负例负责大部分提升”和“跨域泛化”这两项作者主张？

来源：[输入笔记](../journal-club/input-notes.md)、[论文笔记](../journal-club/papers/synthetic-retrieval-notes.md)。讨论问题为本报告提出的问题，不是已记录的会议决定。

## 方法在解决什么问题

论文问的是：在标注较少的意图分类任务中，用容易混淆的错误意图训练检索模型，能否改善域内及跨域表现？模型采用 bi-encoder，hard-negative mining 从最接近的两个错误意图中选择负例。实验覆盖六个合成领域，每个领域有 500 个标注样本，并使用五个随机种子。来源：[论文笔记](../journal-club/papers/synthetic-retrieval-notes.md)。

## 结果支持更好的表现，归因还需谨慎

| 比较 | 标准 bi-encoder | 提议方法 | 去掉 hard-negative mining |
|---|---:|---:|---:|
| 平均域内 macro-F1 | 0.68 | 0.74 | 0.70 |
| 跨域 macro-F1 | 0.61 | 0.65 | 未提供 |

来源：[论文笔记](../journal-club/papers/synthetic-retrieval-notes.md)。

域内消融与“hard-negative mining 有帮助”的解释一致。不过，“负责大部分提升”是输入笔记记录的作者主张；当前笔记没有给出充分的隔离设计和不确定性信息，不能把它直接升级为确定的机制结论。跨域结果说明方法在已报告条件下表现更好，不证明对任意新领域都有效。来源：[输入笔记](../journal-club/input-notes.md)、[论文笔记](../journal-club/papers/synthetic-retrieval-notes.md)。

## 讨论前需要记住的边界

词法检索基线虽然被提及，但分数未提供，因此无法比较。数据和代码不可获取、超参数不完整；计算成本和领域类别平衡情况也未报告。笔记没有统计检验，显著性尚未验证。作者、发表信息和 DOI 未提供，且本例本身为虚构论文。来源：[输入笔记](../journal-club/input-notes.md)、[论文笔记](../journal-club/papers/synthetic-retrieval-notes.md)。

**本次讨论问题：** 在缺少完整复现条件的情况下，哪些作者主张可以保留为当前证据支持的结论，哪些仍应作为待验证判断？这是汇报者提出的问题；材料没有安排复现或迁移任务。
