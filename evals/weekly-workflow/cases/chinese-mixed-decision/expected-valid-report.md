# Synthetic example: 步态事件检测项目会前组会总结

> 日期：2026-08-11 | 模式：进展与文献混合 | 阶段：会前 | 时长：8 分钟 | 详细度：standard

## 本周速览

**本周进展：** 完成 `window_5` 的 seed-13、seed-29、seed-42，并修复时间戳缺口导致预处理重复上一帧的问题；现有 `window_9` 结果不支持继续扩大 smoothing window。[来源：`inputs/notes.md`；`inputs/results.csv`]

**关键证据：** seed-42 下，`window_5` 的 recall 为 0.84，`window_9` 为 0.71。该比较只有一个共同随机种子，不能外推为跨种子结论。[来源：`inputs/results.csv`]

**阻塞与需协助：** 医院数据没有导出权限，会推迟外部验证；2026-08-08 已提交申请。需组会在 synthetic perturbation stress test 和推动数据权限之间确定下周主线，材料没有优先级规则。[来源：`inputs/notes.md`]

**下一步：** Chen 在 2026-08-18 前完成误报分类表，累计覆盖 60 个误报，每条记录场景、预测位置和人工类别。[来源：`inputs/notes.md`]

## 上次行动复盘

| 行动 | 状态 | 证据 |
|---|---|---|
| 跑完 `window_5` 的 seed-13、seed-29、seed-42 | 完成 | 三个运行均为 `complete`。[来源：`inputs/notes.md`；`inputs/results.csv`] |

## 关键结果与解释边界

| 配置 | Seed | Precision | Recall | F1 | Latency | 状态 |
|---|---:|---:|---:|---:|---:|---|
| `window_5` | 13 | 0.88 | 0.83 | 0.85 | 18 ms | complete |
| `window_5` | 29 | 0.86 | 0.84 | 0.85 | 19 ms | complete |
| `window_5` | 42 | 0.87 | 0.84 | 0.85 | 18 ms | complete |
| `window_9` | 42 | 0.91 | 0.71 | 0.80 | 26 ms | complete |

现有材料没有数据集、split、完整配置或不确定性信息，因此这些值只作为本周观测结果，不支持显著性或泛化判断。[来源：`inputs/results.csv`]

- **负面结果：** `window_9` 在 seed-42 的 recall 为 0.71，低于同种子的 `window_5` 0.84；不继续扩大 smoothing window。材料没有提供 recall 下降的原因。[来源：`inputs/notes.md`；`inputs/results.csv`]
- **误报观察：** 已人工查看 24 个误报，楼梯转身和停步后重新起步经常被识别为 gait event；类别定义、抽样方法和分类计数尚未完成，不能量化模式。[来源：`inputs/notes.md`]
- **文献边界：** *Temporal Convolution for Wearable Event Detection* 的作者和发表信息未核验。笔记只涉及平地步行和跑步，可作为后续模型方向，但不能解释本周 `window_9` 的 recall 下降。[来源：`inputs/paper-notes.md`]

## 阻塞与组会决策

医院数据导出权限尚未批准，不影响本地误差分析，但会推迟外部验证。2026-08-08 已提交申请，批准时间未知。[来源：`inputs/notes.md`]

**需决定：** 下周主要精力放在 synthetic perturbation stress test，还是推动数据权限。两个方向均来自材料，且没有优先级规则，报告不预先选择。[来源：`inputs/notes.md`]

## 下周行动

| 行动 | 负责人 | 截止时间 | 产物与完成标准 |
|---|---|---|---|
| 完成误报分类 | Chen | 2026-08-18 | 误报分类表累计覆盖 60 个误报，每条包含场景、预测位置和人工类别。[来源：`inputs/notes.md`] |

## 来源

- `inputs/notes.md`
- `inputs/results.csv`
- `inputs/paper-notes.md`

本次使用全部来源；未检索外部资料，未发布到云平台。
