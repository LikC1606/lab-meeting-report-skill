# Lab Meeting Report 传播素材

这份素材用于寻找真实试用者，而不是制造虚假的 Star 或用户证明。发布时可以改写语气，但不要删除合成案例和能力边界说明。

## 可以公开使用的事实

- 项目是 MIT 许可的公开 Agent Skill。
- 输入可以是散记、实验结果、论文笔记、图片和代码变更。
- 默认输出是有来源标记的 Markdown 组会周报；可选生成 Marp，并衔接飞书/Lark 或 Notion。
- 仓库提供完整的合成显微图像分割案例、自动化测试和公开评测材料。
- 当前尚无经过许可公开的真实博士生案例，不应声称已有用户量、节省时间比例或真实满意度。

## 可用素材

| 素材 | 用途 |
|---|---|
| [`assets/lab-meeting-report-social-preview.png`](../assets/lab-meeting-report-social-preview.png) | GitHub Social preview、文章头图、帖子首图 |
| [`assets/lab-meeting-report-preview.png`](../assets/lab-meeting-report-preview.png) | 展示输入到报告的详细变化 |
| [`examples/weekly-summary/weekly-notes.md`](../examples/weekly-summary/weekly-notes.md) | 展示原始周记 |
| [`examples/weekly-summary/report.md`](../examples/weekly-summary/report.md) | 展示完整周报 |
| [`examples/weekly-summary/slides.md`](../examples/weekly-summary/slides.md) | 展示 7 页 Marp |

## 一句话介绍

把博士生一周的散记、实验结果和论文笔记，整理成有来源、保留失败实验、可直接开组会的 Markdown 周报和演示稿。

## 小红书帖子

可选标题：

1. 我把博士生每周最痛苦的组会整理做成了开源 Skill
2. 实验散记、CSV、论文笔记，能不能直接变成组会周报？
3. 不让 AI 编结果的组会周报 Agent，我先开源了

正文：

```text
我做了一个开源 Agent Skill：Lab Meeting Report。

它解决的不是“把文字润色得像周报”，而是把一周散落的材料真正整理成可以讨论的组会内容：

- 做完了什么，证据在哪；
- 哪个实验失败了，为什么仍然值得保留；
- 现在卡在哪里，需要导师或组内决定什么；
- 下周做什么，交付物和完成标准是什么。

输入可以是周记、CSV、论文笔记、图片和代码变更。默认先生成本地 Markdown，需要时再做 Marp，或发布到飞书/Notion。

目前我还没有可以公开的真实博士生案例，所以仓库里明确放的是一个完全合成、可复现的显微图像分割案例，没有冒充用户反馈。

我正在找 3 位愿意试用的博士生。未公开资料可以只在你自己的电脑和 Agent 里运行，不需要发给我；试完只反馈“哪里不好用”即可。愿意公开案例时，也只接受合成内容或得到许可的脱敏材料。

GitHub：
https://github.com/LikC1606/lab-meeting-report-skill

安装：
npx skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y

如果它真的帮你完成了一次组会准备，再考虑给它 Star。
```

## 知乎内容结构

建议回答“博士生如何高效准备组会汇报”一类真实问题，不要只发项目广告。

1. 先说明组会真正需要回答的四个问题：进展、证据、阻塞、下一步。
2. 展示未经整理的合成周记片段，包括失败实验和 OOM。
3. 展示生成周报的本周速览、结果表和决策问题。
4. 解释为什么不能让 Agent 补齐缺失数字、显著性或论文信息。
5. 给出可复制的安装命令和提示词。
6. 明确说明目前是合成演示，邀请真实试用者反馈。

## 短消息

```text
我开源了一个面向博士生组会的 Agent Skill：把散记、实验结果和论文笔记整理成有来源的 Markdown 周报和 Marp，保留失败实验，不补造数字。现在只有公开的合成案例，正在找 3 位真实试用者。https://github.com/LikC1606/lab-meeting-report-skill
```

## 首批试用邀请

```text
招募 3 位需要准备组会的博士生试用一个开源 Agent Skill。

你提供给自己的 Agent：本周散记、结果文件和论文笔记。
它输出：组会 Markdown；需要时附 10 分钟 Marp。

资料可以完全留在你的电脑上，不需要发给维护者。希望你试完后只回答三个问题：
1. 哪一步最省事？
2. 哪段输出最没用或最不可信？
3. 下次还会不会用？为什么？

项目：https://github.com/LikC1606/lab-meeting-report-skill
```

## 第一阶段目标

先衡量真实使用，不把 Star 当成唯一目标：

1. 找到 3 位完成安装并实际生成一次周报的人；
2. 收到至少 2 份可复现的问题或改进反馈；
3. 在得到许可后形成 1 个脱敏案例，或者继续公开标注为合成案例；
4. 有了真实使用证据后，再申请进入要求社区采用信号的 Awesome 列表。

不要购买 Star、参加互赞群、批量私信或把合成材料称为真实案例。这些行为不能证明产品有用，也会降低后续社区收录的可信度。
