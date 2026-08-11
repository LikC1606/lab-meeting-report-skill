# Lab Meeting Report

[![Validate skill](https://github.com/LikC1606/lab-meeting-report-skill/actions/workflows/validate-skill.yml/badge.svg)](https://github.com/LikC1606/lab-meeting-report-skill/actions/workflows/validate-skill.yml)
[![skills.sh listing](https://skills.sh/b/LikC1606/lab-meeting-report-skill)](https://skills.sh/LikC1606/lab-meeting-report-skill)
[![GitHub release](https://img.shields.io/github/v/release/LikC1606/lab-meeting-report-skill)](https://github.com/LikC1606/lab-meeting-report-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

把博士生一周的实验记录、论文笔记、结果文件、图片和工作说明，整理成一份可以直接开组会、归档和继续追踪的 Markdown 周报。

默认只需要告诉 Agent “这一周的资料在哪里”。Skill 会自动提取本周进展、关键证据、失败尝试、当前阻塞和下周计划；需要时还可以发布到飞书/Lark 或 Notion，并生成 Markdown、Marp、Quarto 或可编辑 PPTX 适配内容。

![一周的散乱科研材料被整理为可汇报、可追溯的 Markdown 组会周报](assets/lab-meeting-report-preview.png)

[English](README.md) | [完整示例](#完整示例) | [质量评测](#质量评测) | [参与贡献](CONTRIBUTING.md)

如果它帮你节省了一次组会准备时间，可以给[这个仓库加 Star](https://github.com/LikC1606/lab-meeting-report-skill)，让更多研究者找到它。

## 快速开始

从公开 GitHub 仓库安装：

```bash
npx skills add https://github.com/LikC1606/lab-meeting-report-skill --skill lab-meeting-report
```

macOS 或 Linux 全局、非交互安装：

```bash
npx skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

Windows PowerShell 使用 `npx.cmd`：

```powershell
npx.cmd skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

安装后，最简单的用法是：

```text
使用 $lab-meeting-report 读取 ./weekly 和我上面补充的工作说明，
生成本周中文组会总结。
```

来源是唯一必填项。粘贴的文字、附件、目录、论文、结果和图片都可以作为来源；报告类型、语言、日期和保存路径可以自动判断。默认创建真实文件：

```text
reports/group-meeting/YYYY-MM-DD.md
```

## 默认会得到什么

报告第一屏固定回答四个问题：

1. 本周最重要的进展是什么；
2. 最能支持它的结果、图表或论文证据在哪里；
3. 当前卡在哪里，需要组内讨论或帮助什么；
4. 下一步做什么，产物和成功判据是什么。

后续内容根据材料自动选择，通常包括：

- 本周完成的工作及实际产物；
- 关键结果、图表和论文启发；
- 失败尝试、负面结果和可信度边界；
- 当前阻塞与具体的协助请求；
- 下周计划；
- 来源与附件。

不会为了填满模板而生成空洞章节。输入较少时自动使用简报；只有明确要求 `audit`、`审计` 或 `追溯` 时，才展开逐声明来源和完整证据检查表。

## 一句话完成更多事情

发布到飞书并准备演示稿：

```text
使用 $lab-meeting-report 读取本周实验、论文笔记和图片，
生成组会 Markdown，发布到飞书，并准备一个 10 分钟的 Marp 演示稿。
```

发布到 Notion：

```text
使用 $lab-meeting-report 读取 ./weekly，生成中文组会总结，
发布到这个 Notion 页面下面：<页面 URL>。
```

生成审计级报告：

```text
使用 $lab-meeting-report 读取 ./notes ./results/*.csv，
生成 audit 级科研进展报告，逐声明列出来源和可能改变结论的证据缺口。
```

## 报告模式

| 模式 | 适用场景 | 主要内容 |
|---|---|---|
| 科研进展 | 实验、实现和持续项目 | 本周工作、结果、失败尝试、阻塞、下周动作 |
| 论文阅读 | Journal Club、论文研读、文献讨论 | 研究问题、方法、关键证据、局限、与当前工作的关系 |
| 混合 | 用文献解释或规划当前研究 | 当前结果、文献对应关系、冲突边界、验证计划 |

支持粘贴笔记、Markdown、文本、PDF、CSV、Excel、图片、截图、代码变更，以及明确选定的飞书/Lark 或 Notion 资源。具体可读取类型取决于宿主 Agent 提供的工具。

## 飞书/Lark 与 Notion

本地 Markdown 生成功能不依赖任何云平台。远程发布始终遵循“本地生成 → 质量检查 → 用户授权写入 → 回读验证 → 写回链接”。

飞书/Lark 使用官方 [`lark-cli`](https://github.com/larksuite/cli) 及相应的 Lark Skills，以用户身份读取或创建文档。Skill 不会扫描整个飞书空间、静默切换机器人身份、整篇覆盖已有文档或删除远程内容。

Notion 优先使用官方 [Notion MCP](https://developers.notion.com/guides/mcp/overview) 和 OAuth。它可以通过 `notion-create-pages`、`notion-update-page` 与 `notion-fetch` 创建、更新并验证页面。Skill 不要求用户在聊天中提供 API Token，也不会在没有明确目标页面或发布请求时写入工作区。

任一云平台发布失败，都不会影响已经生成的本地 Markdown。

## 演示稿接口

演示稿是报告之后的可选出口，不是核心依赖：

| 需要 | 推荐接口 | 说明 |
|---|---|---|
| 口头提纲 | 纯 Markdown | 无需额外安装，始终可用 |
| 快速 HTML、PDF 或简单 PPTX | [Marp CLI](https://github.com/marp-team/marp-cli) | Markdown 路径最短；普通 PPTX 通常不是完全可编辑 |
| 公式、引用和学术演示 | [Quarto](https://quarto.org/docs/presentations/) | 支持 reveal.js、PPTX 和 Beamer |
| 原生可编辑 PowerPoint | [PptxGenJS](https://github.com/gitbrent/PptxGenJS) | 需要已有、经过测试的排版适配器 |
| 交互式网页演示 | [Slidev](https://github.com/slidevjs/slidev) | 仅在用户明确选择或项目已经使用时启用 |

Skill 不会静默安装这些项目。工具不存在时，会保留可直接使用的 Markdown 演示稿并说明缺少的适配器。

## 会前与会后

来源仍是唯一必填项；会议阶段、听众、时长和上次行动都可以省略。

| 阶段 | 行为 |
|---|---|
| `before` / 会前（默认） | 生成本周速览、结果、阻塞与下一步 |
| `after` / 会后 | 保留会前报告，只追加会议记录中明确存在的决定和行动 |
| `both` / 两者 | 先生成会前报告，再追加来源明确的会后记录 |

如果会前阻塞已被会议决定解决，报告会保留旧问题用于追溯，但明确标记为“会前问题，已由会议决定解决”，不会继续把它展示成当前阻塞。

## 证据保护

轻量输入不等于降低科研严谨性。Skill 在后台继续执行这些保护：

- 不编造结果、指标、引用、作者、期刊会议、DOI 或因果解释；
- 精确复制来源中的数值和单位；
- 保留失败实验、负面结果和冲突值；
- 区分事实、解释与假设；
- 更新已有报告时保护手写内容和 UTF-8 编码；
- 缺失信息只在影响结论或下一步时展示，完整表格留给 `audit` 模式。

完整工作流见 [`lab-meeting-report/SKILL.md`](lab-meeting-report/SKILL.md)。

## 完整示例

所有示例数据、论文笔记和结果都是合成内容。建议先看“默认周总结”，它展示简洁的 `standard` 周报和对应 Marp 演示稿；其余示例使用 `audit` 详细程度展示证据边界。

| 工作流 | 输入材料 | 生成报告 |
|---|---|---|
| 默认周总结 | [本周散记](examples/weekly-summary/weekly-notes.md)、[论文笔记](examples/weekly-summary/paper-notes.md)和[实验结果](examples/weekly-summary/results.csv) | [简洁周报](examples/weekly-summary/report.md)和[Marp 演示稿](examples/weekly-summary/slides.md) |
| 科研进展 | [实验笔记](examples/research-progress/input-notes.md)和[结果文件](examples/research-progress/results) | [报告](examples/research-progress/report.md) |
| Journal Club | [输入笔记](examples/journal-club/input-notes.md)和[论文笔记](examples/journal-club/papers/synthetic-retrieval-notes.md) | [报告](examples/journal-club/report.md) |
| 进展与文献混合 | [混合笔记](examples/mixed/input-notes.md)、[实验结果](examples/mixed/results/current_experiment.csv)和[论文笔记](examples/mixed/papers/synthetic-balanced-retrieval.md) | [报告](examples/mixed/report.md) |

## 质量评测

v1.2 的证据保护规则在 8 个公开合成科研进展场景上各运行 3 次，严格门槛通过 24/24；冻结的 v1.1 基线为 0/24。v1.3 保留这些已评测的防编造规则，并重新设计默认输入输出和可选适配层。现有基准尚未证明真实博士生偏好或云平台发布成功率。

可查看[评测设计](docs/superpowers/specs/2026-07-13-lab-meeting-report-v1.2-quality-evaluation-design.md)、[公开场景](evals/research-progress/cases)、[版本化基准](benchmarks/v1.1-v1.2/benchmark.md)和[逐声明自审](benchmarks/v1.1-v1.2/semantic-review-final.json)。

## 反馈与贡献

- 使用 [Bug 表单](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=bug_report.yml)提交可复现问题。
- 使用[功能建议表单](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=feature_request.yml)提出可复用改进。
- 使用[示例投稿表单](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=example_submission.yml)分享合成或匿名工作流。
- 在 [Discussions](https://github.com/LikC1606/lab-meeting-report-skill/discussions)讨论科研汇报流程。

开发与 PR 流程见 [CONTRIBUTING.md](CONTRIBUTING.md)，安全问题私下报告方式见 [SECURITY.md](SECURITY.md)。

## 许可证

[MIT](LICENSE)
