# 显微图像分割项目组会周报

> Synthetic example. All project details and results are fictional.  
> 日期：2026-07-12 | 模式：科研进展 | 阶段：会前 | 详细度：standard

## 本周速览

**本周进展：** 完成当前 U-Net 配置的三个随机种子复现，并在训练流程中加入 stain normalization、固定数据加载器随机状态。三个运行均完成训练。[来源：`weekly-notes.md`；`results.csv`]

**关键证据：** seed-11、seed-23、seed-37 的 Dice 分别为 0.812、0.806、0.809，IoU 分别为 0.691、0.683、0.687。[来源：`results.csv`]

**阻塞与需协助：** 物理 batch size 4 在 16 GB GPU 上 OOM；AMP 和清理缓存没有解决。需要组内决定是借用至少 24 GB GPU，还是先使用 gradient accumulation。[来源：`weekly-notes.md`；`results.csv`]

**下一步：** 若没有可用的 24 GB GPU，先用物理 batch size 2、effective batch size 4 完成三个随机种子，交付训练日志和对比表；完成标准是全部运行无 OOM 结束并记录 Dice、IoU 与 peak GPU memory。[来源：`weekly-notes.md`]

## 上次行动复盘

| 行动 | 状态 | 产物 | 来源 |
|---|---|---|---|
| 用当前配置完成三个随机种子的复现 | 已完成 | `results.csv` | `weekly-notes.md`；`results.csv` |

## 关键结果

| 实验 | 随机种子 | Batch size | Dice | IoU | Peak GPU memory | 状态 |
|---|---:|---:|---:|---:|---:|---|
| current | seed-11 | 2 | 0.812 | 0.691 | 14.8 GB | complete |
| current | seed-23 | 2 | 0.806 | 0.683 | 14.9 GB | complete |
| current | seed-37 | 2 | 0.809 | 0.687 | 14.8 GB | complete |

目前只能确认三个运行均完成并得到上述观测值；材料没有提供更多数据划分、统计检验或预设的性能提升阈值，因此不据此声称性能显著改善。[来源：`weekly-notes.md`；`results.csv`]

## 失败尝试与证据边界

- boundary dropout 在 seed-23 上的 Dice 为 0.774，低于同一随机种子当前配置的 0.806；本周证据不支持保留该分支。[来源：`weekly-notes.md`；`results.csv`]
- 物理 batch size 4 在 16 GB GPU 上于第一次 optimizer step OOM。已尝试 AMP 和清理缓存，仍未完成训练。[来源：`weekly-notes.md`；`results.csv`]
- 论文笔记中的 boundary-aware auxiliary loss 来自 fluorescence microscopy；它对当前 bright-field 数据的适用性未知，项目中也尚未实现。[来源：`paper-notes.md`]

## 当前阻塞与需协助

**问题：** 当前设备无法完成物理 batch size 4 的训练。[来源：`weekly-notes.md`]

**影响：** 下周的 batch 配置实验无法按物理 batch size 4 直接执行。[来源：`weekly-notes.md`]

**请求讨论：** 在“借用至少 24 GB GPU”和“使用 gradient accumulation 得到 effective batch size 4”之间确定路线。[来源：`weekly-notes.md`]

## 下周行动

| 行动 | 产物 | 完成标准 | 来源 |
|---|---|---|---|
| 按组会决定执行 batch 配置实验 | 三个随机种子的训练日志和对比表 | 所有运行无 OOM 结束，并记录 Dice、IoU、peak GPU memory | `weekly-notes.md` |
| 评估 boundary-aware auxiliary loss 是否进入后续消融 | 一条保留或暂缓的记录及理由 | 以当前配置为 comparator；不把论文结果当作当前数据的结果 | `weekly-notes.md`；`paper-notes.md` |

## 来源

- `weekly-notes.md`
- `paper-notes.md`
- `results.csv`
