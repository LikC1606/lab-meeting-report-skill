# 论文阅读摘记：boundary-aware segmentation

> Synthetic example. The paper and notes are fictional.

论文暂记为 *Boundary-Aware Learning for Microscopy Segmentation*，作者与发表信息未核验。

## 与当前项目有关的内容

- 论文使用 boundary-aware auxiliary loss 强化细结构边界。
- 论文实验对象是 fluorescence microscopy，不是当前项目的 bright-field 数据。
- 方法需要为训练样本生成 boundary distance map。
- 当前项目还没有该方法的实现，也没有在相同数据划分上验证它。

## 可带到组会的问题

该方法可以作为后续消融候选，但论文笔记不足以证明它会改善当前项目。若要测试，应保留当前配置作为 comparator，并记录失败结果。
