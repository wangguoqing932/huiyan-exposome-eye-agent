# docs/ 索引

本目录存放方法学、伦理、审计与历史记录。**当前有效的合同性文档**是前两组；
其余是核查记录或前瞻计划，不应被当作现行口径。

## 1. 核心方法与口径（当前有效）

| 文件 | 用途 |
|---|---|
| [analysis_plan.md](analysis_plan.md) | 预注册分析计划 v1.2 + §0.1–0.3 更正记录；规则集、三态金标准、统计口径的最终依据 |
| [limitations.md](limitations.md) | 局限与诚实陈述（协议偏离、信息性对、后端、CHNS/数据扩容等） |
| [rule_rationale.md](rule_rationale.md) | 21 条规则的机制、证据等级与引文理由 |
| [cohort_variable_mapping.md](cohort_variable_mapping.md) | 8 队列变量操作化台账（也作为 supplementary S1） |
| [AGENT_AUDIT.md](AGENT_AUDIT.md) | agent 三层审计（R1–R30 的发现与处置，含 §三十六 Table 5b 更正） |

## 2. 伦理与投稿声明

公开数据、无人体受试者，IRB 走豁免路径；因此只保留以下文档：

- `ETHICS.md` / `ETHICS.en.md`
- `Data_Management_Plan.md` / `.en.md`
- `Manuscript_Ethics_Statement.md` / `.en.md`

`IRB_Protocol_Summary` 与 `Informed_Consent` 未生成（不适用）。
文件中的 TODO 标记是作者/医院侧字段，不影响公开数据豁免结论。

## 3. 核查与专项笔记

| 文件 | 内容 |
|---|---|
| [CHNS_feasibility_2026-10-20.md](CHNS_feasibility_2026-10-20.md) | CHNS 作为第 13 层被结构性否决（无眼科结局）；结论已并入 limitations §8 |
| [NHANES_CONSTRUCT_VALIDATION.md](NHANES_CONSTRUCT_VALIDATION.md) | NHANES 自报 vs 客观测量的构念验证 |
| [bias_investigation_smoking_cataract.md](bias_investigation_smoking_cataract.md) | 吸烟×白内障方向反转的偏倚调查 |
| [GAP_ANALYSIS_20IF.md](GAP_ANALYSIS_20IF.md) | 与 20+ IF 期刊要求的差距分析 |
| [data_sources.md](data_sources.md) | 数据源与获取路径 |

## 4. 前瞻计划

- [AGENT_V2_MUSTFIX_2026-10-16.md](AGENT_V2_MUSTFIX_2026-10-16.md) — 框架 V2 必改单
  （M1–M12；本稿是 V1 论文，V2 是后续工程，不是当前投稿的前置条件）。

## 5. 历史与归档

- [history/](history/) — R4–R30 逐轮审计 / 修复 / 阶段记录（含 R25 叙事重构、R26 结果补全、R27 dataset-centric 重排、R28 全文重写、R29 主稿 4 表/6 图与 R30 多视角审稿修正）。
- [archive_g3g4g5/](archive_g3g4g5/) — 推理层 G3/G4/G5 负结果归档。
- [audit_scripts_archive/](audit_scripts_archive/) — 早期审计脚本存档。

> 现行状态以 `.medical-agent/state.json` 与 `.writer/progress.json` 为准；
> 本目录的文档不驱动状态机。
