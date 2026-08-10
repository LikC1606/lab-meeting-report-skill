# Lab Meeting Report

[![Validate skill](https://github.com/LikC1606/lab-meeting-report-skill/actions/workflows/validate-skill.yml/badge.svg)](https://github.com/LikC1606/lab-meeting-report-skill/actions/workflows/validate-skill.yml)
[![skills.sh listing](https://skills.sh/b/LikC1606/lab-meeting-report-skill)](https://skills.sh/LikC1606/lab-meeting-report-skill)
[![GitHub release](https://img.shields.io/github/v/release/LikC1606/lab-meeting-report-skill)](https://github.com/LikC1606/lab-meeting-report-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

把散落的实验记录、CSV 结果和论文笔记整理为可用于决策的 Markdown 组会报告，同时不隐藏失败实验，也不编造缺失证据。

`lab-meeting-report` 适用于科研进展汇报、Journal Club、实验复盘，以及把当前结果和文献证据放在一起分析的混合报告。宿主环境提供所需工具时，还可以按明确范围读取或发布飞书/Lark 内容。

![原始科研文件被整理为证据可追溯的组会报告，同时保留失败实验和明确的决策边界](assets/lab-meeting-report-preview.png)

[English](README.md) | [完整示例](#完整示例) | [质量评测](#质量评测) | [参与贡献](CONTRIBUTING.md)

如果它帮你节省了一次组会准备时间，可以给[这个仓库加 Star](https://github.com/LikC1606/lab-meeting-report-skill)，让更多研究者找到它。

## 快速开始

从公开 GitHub 仓库安装：

```bash
npx skills add https://github.com/LikC1606/lab-meeting-report-skill --skill lab-meeting-report
```

在 macOS 或 Linux 上全局、非交互安装：

```bash
npx skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

Windows PowerShell 使用 `npx.cmd`：

```powershell
npx.cmd skills add LikC1606/lab-meeting-report-skill@lab-meeting-report -g -y
```

安装命令需要 Node.js 和 `npx`。也可以先到 [skills.sh](https://skills.sh/LikC1606/lab-meeting-report-skill/lab-meeting-report) 检查已发布的 Skill 内容。

安装后，向 Agent 指定来源和目标：

```text
使用 $lab-meeting-report 读取本周实验记录和结果，生成组会 Markdown，
保留失败实验、当前阻塞和下一步成功判据。
```

默认会创建真实文件，而不是只在聊天中返回提纲：

```text
reports/group-meeting/YYYY-MM-DD.md
```

## 为什么需要这个 Skill

普通报告生成器倾向于把故事写得流畅，但科研汇报还需要保留那些让故事不那么流畅、却影响判断的证据。

这个 Skill 会：

- 保留失败实验、负面结果、阻塞和互相冲突的数值；
- 明确区分观察事实、解释和假设；
- 精确复制来源中的指标和引用，不静默填补缺失信息；
- 更新已有日期报告时保护手写内容；
- 把下一步写成包含产物和成功判据的具体行动；
- 只读取用户明确放入范围的文件或飞书/Lark 资源。

## 完整示例

所有示例数据、论文笔记和结果都是合成内容。每个工作流都包含完整输入和生成报告，可以端到端核对转换过程。

| 工作流 | 输入材料 | 生成报告 |
|---|---|---|
| 科研进展 | [实验笔记](examples/research-progress/input-notes.md)和[结果文件](examples/research-progress/results) | [报告](examples/research-progress/report.md) |
| Journal Club | [输入笔记](examples/journal-club/input-notes.md)和[论文笔记](examples/journal-club/papers/synthetic-retrieval-notes.md) | [报告](examples/journal-club/report.md) |
| 进展与文献混合 | [混合笔记](examples/mixed/input-notes.md)、[实验结果](examples/mixed/results/current_experiment.csv)和[论文笔记](examples/mixed/papers/synthetic-balanced-retrieval.md) | [报告](examples/mixed/report.md) |

更多调用示例：

```text
使用 $lab-meeting-report 读取 paper.pdf，生成论文阅读组会报告，
重点分析方法、关键证据、局限性和对当前工作的启发。
```

```text
使用 $lab-meeting-report 合并最新实验结果和论文笔记，
解释一致与冲突之处，并提出下一项验证实验。
```

## 报告模式

| 模式 | 适用场景 | 主要内容 |
|---|---|---|
| 科研进展 | 实验、实现和持续项目 | 目标、方法、证据、负面结果、阻塞、下一步 |
| 论文阅读 | Journal Club、论文研读、文献讨论 | 研究缺口、方法、证据、创新、局限、可复现性 |
| 混合 | 用文献解释或规划当前研究 | 当前结果、文献映射、假设更新、验证计划 |

支持粘贴笔记、Markdown、文本、PDF、CSV、Excel、图片、截图，以及明确选定的飞书/Lark 资源。实际可读取的文件类型取决于宿主 Agent 提供的工具。

## 证据规则

- 不编造结果、指标、引用、作者、期刊会议、DOI 或因果解释。
- 保留来源标识符，精确复制实验数值和单位。
- 除非用户明确要求或来源定义了计算方式，否则不引入新的计算结果。
- 来源冲突且没有优先级规则时，保留所有值并说明冲突。
- 必要信息缺失时标记 `待补充`，未核验的引用信息标记 `未核验`。
- 更新已有报告时保留手写内容和未被新证据明确替代的结论。

完整工作流见 [`lab-meeting-report/SKILL.md`](lab-meeting-report/SKILL.md)。

## 质量评测

v1.2 候选版本在 8 个公开合成科研进展场景上各运行 3 次。场景覆盖数值保真、来源冲突、被埋没的负面结果、无证据因果语言、重复笔记、目录范围控制、安全更新已有报告和来源不可用。

| 配置 | 严格门槛通过 | 平均期望项通过率 |
|---|---:|---:|
| v1.2 候选版本 | 24/24 | 1.000 |
| 冻结的 v1.1 基线 | 0/24 | 0.818 |

严格门槛要求报告中的所有确定性期望项全部通过。Codex 还对 24 份候选报告进行了逐声明自审，未发现无证据支撑的关键声明。该审阅使用同一编写 Agent，因此不独立、非盲评。结果只适用于当前合成语料，不能证明普遍消除幻觉，也不能代表真实审阅者偏好。

可查看[评测设计](docs/superpowers/specs/2026-07-13-lab-meeting-report-v1.2-quality-evaluation-design.md)、[公开场景](evals/research-progress/cases)、[版本化基准](benchmarks/v1.1-v1.2/benchmark.md)和[逐声明自审](benchmarks/v1.1-v1.2/semantic-review-final.json)。

## 可选飞书/Lark 集成

本地 Markdown 生成功能不依赖飞书/Lark。读取或发布飞书/Lark 内容还需要：

- [`lark-cli`](https://github.com/larksuite/cli)；
- 当前操作需要的官方 `lark-shared`、`lark-doc`、`lark-im`、`lark-minutes` 和 `lark-vc` Skills；
- 具有最小必要权限的用户授权身份。

流程只读取明确选定的资源，先验证本地 Markdown，再用用户身份执行远程操作，并在记录 URL 前核验云文档。它不会静默切换为机器人身份、整篇覆盖已有文档或删除远程资源。

## 能力边界与兼容性

仓库遵循可移植的 Agent Skills 目录格式，并包含 Codex 接口元数据。核心输出是 Markdown；该 Skill 不生成 PPTX、DOCX 或 HTML，也不会在用户没有明确要求时主动检索额外文献。

文件解析和飞书/Lark 操作取决于宿主环境中的工具。安装前应检查 Skill 内容，并只在可信环境中处理敏感研究数据。

## 反馈与贡献

- 使用 [Bug 表单](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=bug_report.yml)提交可复现问题。
- 使用[功能建议表单](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=feature_request.yml)提出可复用改进。
- 使用[示例投稿表单](https://github.com/LikC1606/lab-meeting-report-skill/issues/new?template=example_submission.yml)分享合成或匿名工作流。
- 在 [Discussions](https://github.com/LikC1606/lab-meeting-report-skill/discussions)讨论科研汇报流程。

开发与 PR 流程见 [CONTRIBUTING.md](CONTRIBUTING.md)，安全问题私下报告方式见 [SECURITY.md](SECURITY.md)。

## 许可证

[MIT](LICENSE)
