---
marp: true
theme: default
paginate: true
lang: zh-CN
---

# Synthetic example: 步态事件检测

本周结论：停止扩大 smoothing window，转向误报分类与验证优先级决策

<small>证据：`report.md`；`inputs/notes.md`</small>

**讨论入口：** 下周主线选择什么？

<!-- 演讲提示：先给结论，说明今天需要带走一个优先级决定。 -->

---

## 本周状态

- `window_5` 的 seed-13、seed-29、seed-42 均已完成
- 时间戳缺口问题已修复
- 医院数据导出权限会推迟外部验证

<small>证据：`report.md`；`inputs/notes.md`；`inputs/results.csv`</small>

**讨论问题：** 当前状态是否遗漏会影响路线选择的信息？

<!-- 演讲提示：区分已经完成的实验和仍未直接验证的楼梯误报目标。 -->

---

## `window_5` 基线

| Seed | Precision | Recall | F1 | Latency |
|---:|---:|---:|---:|---:|
| 13 | 0.88 | 0.83 | 0.85 | 18 ms |
| 29 | 0.86 | 0.84 | 0.85 | 19 ms |
| 42 | 0.87 | 0.84 | 0.85 | 18 ms |

<small>证据：`report.md`；`inputs/results.csv`</small>

**讨论问题：** 下一轮比较前最需要补齐哪项实验记录？

<!-- 演讲提示：这些是本周观测值，不声称显著性、泛化性或统计稳定性。 -->

---

## 负面结果与文献边界

- seed-42：`window_9` recall 0.71；`window_5` recall 0.84
- `window_9` 同时记录 precision 0.91、F1 0.80、latency 26 ms
- 暂记论文 *Temporal Convolution for Wearable Event Detection* 的作者和发表信息未核验，且不能解释本周 recall 下降

<small>证据：`report.md`；`inputs/results.csv`；`inputs/paper-notes.md`</small>

**讨论问题：** 是否同意不再为 `window_9` 扩大实验？

<!-- 演讲提示：只陈述同种子观测，不补充材料之外的因果解释。 -->

---

## 阻塞需要组会决定

- 2026-08-08 已提交医院数据申请，批准时间未知
- 方向一：synthetic perturbation stress test
- 方向二：推动数据权限
- 材料没有优先级规则

<small>证据：`report.md`；`inputs/notes.md`</small>

**需组会决定：** 下周主要精力选哪一项？

<!-- 演讲提示：保留两个来源中的选择，不替组会作决定。 -->

---

## 下周行动与交付

- 已查看 24 个误报，目标累计覆盖 60 个
- 产物：误报分类表，记录场景、预测位置、人工类别
- 负责人：Chen
- 截止时间：2026-08-18

<small>证据：`report.md`；`inputs/notes.md`</small>

**收束问题：** 确认类别定义，并记录 stress test / 数据权限的主线选择。

<!-- 演讲提示：以可验收产物收尾。 -->
