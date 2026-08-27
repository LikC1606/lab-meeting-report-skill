# Lab Meeting Report 传播素材

这份素材用于在没有真人测试渠道的情况下公开展示可复现工作流，而不是制造虚假的 Star 或用户证明。发布时可以改写语气，但不要删除合成案例和能力边界说明。

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

## GitHub 项目增长方法

### 从“高 Star”教程中提炼的原则

Star 是项目被看见后的信号，不应当单独作为目标。公开教程和 GitHub Open Source Guides 反复强调：

- **先解决一个具体问题**：明确目标用户、使用场景和可验证结果。
- **把仓库首页当成产品入口**：README 首屏回答“做什么、为什么有用、如何开始”，同时放 Demo、示例输入输出和许可证。
- **让第一次使用在几分钟内完成**：安装命令、最小示例、预期输出、常见问题都要可复制。
- **建立贡献者入口**：写清愿景、路线图、贡献方式、行为准则，并准备 `good first issue` 或文档类任务。
- **持续公开迭代**：用 Release、变更日志、教程文章和公开 issue 记录项目如何变好；不要只在发布日宣传。
- **选择开发者所在的分发渠道**：根据项目受众发布到相关社区、技术博客、目录或生态集成，针对每个平台改写内容。

参考：[GitHub Open Source Guides：启动项目](https://opensource.guide/starting-a-project/)、[构建社区](https://opensource.guide/building-community/)、[维护者最佳实践](https://opensource.guide/best-practices/)、[0 到 1000 Star 作者复盘](https://eke.hashnode.dev/how-my-open-source-project-got-1000-stars-on-github-in-4-months) 和 [Indie Hackers 项目复盘](https://www.indiehackers.com/post/0-1000-github-stars-for-your-open-source-projects-8f455f7d87)。这些是作者经验和社区建议，不是 Star 数量保证。

### 套用到 Lab Meeting Report

1. **定位**：面向博士生，把散记、实验结果和论文笔记整理成有来源的组会周报。
2. **首页首屏**：一句价值说明 + 输入/输出对比图 + 安装命令 + 60 秒最小示例。
3. **可复现证据**：公开合成输入、完整 Markdown/Marp 输出、评测命令和已知限制。
4. **增长入口**：发布“如何准备组会”的技术教程，提交相关 Skill/开源目录，并做飞书、Notion、PPT 等真实集成。
5. **社区循环**：维护公开路线图，优先处理安装问题和文档问题，把常见回答沉淀回 README。

先完成一个最小闭环：README 说清楚项目、Demo 可以复制运行、发布一个版本并附一篇技术说明。不要把合成案例写成真实用户证明，不购买 Star、不互赞、不批量私信，也不要把同一段广告复制到无关社区。

正文：

```text
组会前一晚，我把散记、实验 CSV 和论文笔记放在一起，最怕的不是写得不够漂亮，而是漏掉失败实验，或者把没有证据的数字写进汇报。

所以我做了一个开源 Agent Skill：Lab Meeting Report。

它解决的不是“把文字润色得像周报”，而是把一周散落的材料整理成可以讨论的组会内容：

- 做完了什么，证据在哪；
- 哪个实验失败了，为什么仍然值得保留；
- 现在卡在哪里，需要导师或组内决定什么；
- 下周做什么，交付物和完成标准是什么。

输入可以是周记、CSV、论文笔记、图片和代码变更。默认先生成本地 Markdown，需要时再做 Marp，或发布到飞书/Notion。

下面是完整的可复现流程：

1. 把散记、CSV、论文笔记和代码变更作为输入。
2. 让 Agent 只引用输入中的事实，标记来源，不补造数字。
3. 输出本周速览、结果表、失败实验、阻塞点和决策问题。
4. 需要演示时再生成 Marp；需要协作时发布到飞书或 Notion。
5. 用仓库里的自动评测检查数值、负面结果、来源和每页结构。

当前没有可以公开的真实博士生案例，因此仓库里明确放的是一个完全合成、可复现的显微图像分割案例，没有冒充用户反馈。

仓库已经公开全部合成输入、生成结果和自动评测，任何人都可以在自己的电脑和 Agent 中复现，不需要把未公开研究资料交给维护者。

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
6. 明确说明目前是合成演示，并链接完整输入、输出和自动评测。

## 短消息

```text
我开源了一个面向博士生组会的 Agent Skill：把散记、实验结果和论文笔记整理成有来源的 Markdown 周报和 Marp，保留失败实验，不补造数字。仓库包含完整的合成输入、输出和自动评测，可直接复现。https://github.com/LikC1606/lab-meeting-report-skill
```

## 无真人案例时的发布说明

```text
这个项目目前没有可以公开的真实用户案例，因此不引用虚构反馈。

仓库使用一套完整的合成科研材料展示工作流：
输入是本周散记、实验 CSV 和论文笔记；
输出是有来源的 Markdown 周报和 7 页 Marp；
自动评测检查数值、负面结果、来源和每页演讲结构。

所有材料都已公开，可以自行复现和检查，而不需要相信宣传文案。

项目：https://github.com/LikC1606/lab-meeting-report-skill
```

## 可自行完成的目录分发

- `skills.sh` 当前仍使用旧快照，可跟踪或补充 [`vercel-labs/skills#1918`](https://github.com/vercel-labs/skills/issues/1918)。
- `Awesome Claude Code` 接受已持续维护至少 14 天的项目，但要求作者本人通过网页表单推荐，不能使用 `gh` CLI 自动提交：[推荐表单](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml)。
- 推荐表单可使用这一句客观描述：`Creates source-grounded lab-meeting reports and presentation outlines from weekly research materials.`
- `VoltAgent/awesome-agent-skills` 明确要求已有社区使用，不把它作为当前阶段的渠道。

## 第一阶段目标

这些目标不依赖主动寻找真人测试：

1. 为 GitHub 仓库上传 Social preview 图片；
2. 在两个公开平台发布同一个可复现合成案例，而不是征集测试者；
3. 推动 `skills.sh` 更新快照和搜索索引；
4. 由仓库所有者提交 `Awesome Claude Code` 网页推荐表单；
5. 观察 14 天的 GitHub 独立访问量、`skills.sh` 安装数和自然获得的 Star。

不要购买 Star、参加互赞群、批量私信或把合成材料称为真实案例。这些行为不能证明产品有用，也会降低后续社区收录的可信度。
