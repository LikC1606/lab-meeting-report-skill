---
marp: true
theme: default
paginate: true
title: 显微图像分割项目组会周报
description: Synthetic example derived from the validated weekly report
---

# 显微图像分割项目组会周报

2026-07-12

**Evidence:** `report.md` 的本周速览与来源列表。

**Say:** 本次只汇报可复现结果、失败尝试和需要组内决定的资源路线。

**Discuss:** 今天需要形成哪项决定？

---

## 本周状态

- 当前 U-Net 配置的三个随机种子均完成训练。
- 训练流程加入 stain normalization，并固定数据加载器随机状态。
- 物理 batch size 4 仍受 GPU 内存限制。

**Evidence:** `report.md` 的“本周速览”和“上次行动复盘”。

**Say:** 上次行动已完成，现在的主要问题不是运行失败，而是下一轮 batch 配置受资源约束。

**Discuss:** 这个状态描述是否遗漏了会影响路线选择的背景？

---

## 三个随机种子的观测结果

| Seed | Dice | IoU | Peak GPU memory |
|---|---:|---:|---:|
| seed-11 | 0.812 | 0.691 | 14.8 GB |
| seed-23 | 0.806 | 0.683 | 14.9 GB |
| seed-37 | 0.809 | 0.687 | 14.8 GB |

**Evidence:** `report.md` 的“关键结果”，原始值来自 `results.csv`。

**Say:** 三个运行均完成；现有材料没有统计检验或预设提升阈值，因此不声称显著改善。

**Discuss:** 下一轮是否需要增加其他数据划分或统计检查？

---

## 必须保留的负面结果

- boundary dropout 在 seed-23 上的 Dice 为 0.774。
- 同一随机种子的当前配置 Dice 为 0.806。
- 本周证据不支持保留该分支。

**Evidence:** `report.md` 的“失败尝试与证据边界”，原始值来自 `results.csv`。

**Say:** 这是一次有决策价值的失败尝试，不能从周报中省略。

**Discuss:** 是否停止该分支，把资源转给 boundary-aware auxiliary loss 的小规模消融？

---

## 当前阻塞：物理 batch size 4

- 16 GB GPU 在第一次 optimizer step OOM。
- AMP 和清理缓存没有解决。
- batch size 2 可以完成训练。

**Evidence:** `report.md` 的“当前阻塞与需协助”。

**Say:** 阻塞会改变下周实验路线，需要组内明确资源选择。

**Discuss:** 借用至少 24 GB GPU，还是用 gradient accumulation 得到 effective batch size 4？

---

## 文献线索及边界

- boundary-aware auxiliary loss 可作为后续候选。
- 论文对象是 fluorescence microscopy，不是当前 bright-field 数据。
- 当前项目尚未实现，也没有本地验证。

**Evidence:** `report.md` 的“失败尝试与证据边界”，内容来自 `paper-notes.md`。

**Say:** 这是一条待验证线索，不是当前项目已经得到的结果。

**Discuss:** 是否值得排入下一轮消融，还是先完成 batch 配置实验？

---

## 下周交付

- 按组会决定执行 batch 配置实验。
- 交付三个随机种子的训练日志和对比表。
- 全部运行需无 OOM 结束，并记录 Dice、IoU、peak GPU memory。

**Evidence:** `report.md` 的“下周行动”。

**Say:** 没有预设提升阈值；先确保实验完成并完整记录。

**Discuss:** 请确认资源路线和 boundary-aware auxiliary loss 的优先顺序。
