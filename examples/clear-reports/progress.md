# 当前配置的三个运行已完成，大 batch 训练仍受显存限制

> 合成演示：项目细节与结果均为虚构。周期：2026-07-06 至 2026-07-12。

## 本周速览

**本周进展：** 当前 U-Net 配置的三个随机种子均完成训练；boundary dropout 分支的现有结果不支持保留。

**关键证据：** seed-23 上，boundary dropout 的 Dice 低于同种子的当前配置；具体数值见结果表。

**阻塞与需协助：** 16 GB GPU 无法完成物理 batch size 4；需要决定借用至少 24 GB GPU，还是使用 gradient accumulation。

**下一步：** 按选定路线完成 batch 配置实验；没有更大 GPU 时，先使用 gradient accumulation。

来源：[本周散记](../weekly-summary/weekly-notes.md)、[结果 CSV](../weekly-summary/results.csv)。

## 上次行动复盘

用当前配置完成 seed-11、seed-23、seed-37 的复现：**已完成**，产物为 `results.csv`。来源：[本周散记](../weekly-summary/weekly-notes.md)。

## 当前配置已跑完，boundary dropout 暂无保留依据

本周在训练流程中加入 stain normalization，并固定数据加载器随机状态。当前配置的三个运行全部完成；材料没有隔离这些调整的影响，因此不能把结果归因于某一项改动。

| 配置 | 随机种子 | Batch size | Dice | IoU | Peak GPU memory |
|---|---|---:|---:|---:|---:|
| current | seed-11 | 2 | 0.812 | 0.691 | 14.8 GB |
| current | seed-23 | 2 | 0.806 | 0.683 | 14.9 GB |
| current | seed-37 | 2 | 0.809 | 0.687 | 14.8 GB |
| boundary_dropout | seed-23 | 2 | 0.774 | 0.648 | 14.9 GB |

来源：[本周散记](../weekly-summary/weekly-notes.md)、[结果 CSV](../weekly-summary/results.csv)。

boundary dropout 在同一随机种子上的 Dice 低于当前配置，本周证据不支持保留这个分支。材料未提供统计检验，也没有更多数据划分信息，不能据此推广到其他种子或宣称显著差异。

## 需要组内决定的是资源路线

物理 batch size 4 在 16 GB GPU 上于第一次 optimizer step 出现 OOM；开启 AMP 和清理缓存仍未解决。物理 batch size 2 可以完成训练，因此接下来需要在借用更大 GPU 与 gradient accumulation 之间选择。来源：[本周散记](../weekly-summary/weekly-notes.md)、[结果 CSV](../weekly-summary/results.csv)。

论文中的 boundary-aware auxiliary loss 可以作为后续消融候选，但来自 fluorescence microscopy，当前项目是 bright-field 数据，且尚未实现。它不能作为当前数据上有效的证据；如果后续测试，应保留当前配置作为 comparator。来源：[论文笔记](../weekly-summary/paper-notes.md)。

## 下周交付

资源路线尚待组会讨论。若没有可用的 24 GB GPU，按笔记中的计划保持物理 batch size 2，以 gradient accumulation 得到 effective batch size 4。交付三个随机种子的训练日志和对比表；所有运行需无 OOM 结束，并记录 Dice、IoU 和 peak GPU memory，没有预设性能提升阈值。来源：[本周散记](../weekly-summary/weekly-notes.md)。
