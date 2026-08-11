# 显微图像分割项目：本周散记

> Synthetic example. All project details and results are fictional.

- 周期：2026-07-06 至 2026-07-12
- 组会阶段：会前
- 汇报时长：10 分钟
- 当前目标：提高明场显微图像中细胞边界分割的复现稳定性。

## 上次行动

- 用当前 U-Net 配置完成 seed-11、seed-23、seed-37 三个随机种子的复现。
- 状态：已完成。
- 产物：`results.csv`。

## 本周工作

- 在现有训练流程中加入 stain normalization，并固定数据加载器的随机状态。
- 当前配置的三个随机种子均完成训练，结果记录在 `results.csv`。
- 尝试了 boundary dropout 分支。seed-23 的验证集 Dice 为 0.774；相同随机种子的当前配置为 0.806。这个结果不支持保留该分支。
- 尝试把物理 batch size 从 2 提高到 4。使用 16 GB GPU、已开启 AMP 并清理缓存后，训练仍在第一次 optimizer step 出现 OOM。batch size 2 可以完成训练。

## 需要组内帮助

请讨论下周优先采用哪条路线：

- 借用至少 24 GB 的 GPU，继续测试物理 batch size 4；或
- 保持物理 batch size 2，使用 gradient accumulation 得到 effective batch size 4。

## 下周计划

- 若组内没有可用的 24 GB GPU，先执行 gradient accumulation 路线。
- 产物：三个随机种子的训练日志和一张对比表。
- 完成标准：三个随机种子均无 OOM 地结束，并如实记录 Dice、IoU 和 peak GPU memory；没有预设提升阈值。
- 参考 `paper-notes.md` 评估 boundary-aware auxiliary loss 是否值得进入后续实验，但本周不据此宣称对当前数据有效。
