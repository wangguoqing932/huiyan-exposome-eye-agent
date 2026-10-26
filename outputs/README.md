# outputs/ 索引

本目录只放**产物**；输入数据在 `data/`，代码在 `src/` 与 `scripts/`。

## 1. 当前有效的主产物

| 路径 | 内容 |
|---|---|
| `paper/manuscript.md` | **投稿主稿**（英文原生，96,235 B；与 `.en.md` 逐字节相同） |
| `paper/sections/` | 分节源：abstract / introduction / methods / results / discussion / declarations；主稿由 `scripts/assemble_manuscript.py` 从这里装配 |
| `paper/figure_legends_main.md` | 主图 Figure 1–6 的英文图例（主稿使用） |
| `paper/figure_legends_supp.md` | 补充图 S1/S2 的英文图例 |
| `paper/figure_legends.md` | 全量图例参考（图 1–6 + S1/S2） |
| `paper/manuscript_agent_first.docx` | **投稿用整篇 Word（R30 最终英文版）**——37 页，正文 5,988 词（Word 口径）、abstract 412 词，零中文，统一配色/纯白背景，含标题页 + 正文 + 声明 + 文献 + 图例 + 4 表 + 6 图 |
| `paper/manuscript_agent_first.pdf` | **投稿用 PDF（R30 最终版）**——37 页，零中文；与 Word 同源 |
| `paper/manuscript_agent_first_preview.pdf` | ZCode/预览用栅格 PDF（37 页，RGB，4.9 MB）；投稿请用上一行矢量 PDF |
| `paper/references.docx` | 27 条参考文献的单独 Word 版（编号列表 + 核验审计表；由 `scripts/build_references_docx.py` 生成） |
| `paper/figure_table_qc_report.md` | 7_1 图表 QC 报告（结构检查 + 目视核验节） |
| `figures/contracts/` | 8 份图件契约（figure1–figure8；figure4–8 在稿中对应 S1/S2/Figure 4–6） |
| `figures/source_data/` | 每张图的绘图数据；figure2 带 `dataset_id`/`dataset_role` |
| `figures/*.{png,pdf,svg,tiff}` | 6 主图 + S1/S2 的四格式成品（TIFF 为 LZW；统一由 `scripts/render_top_figures.py` 渲染） |
| `tables/` | 4 张主表（cohorts / rules / performance by dataset / transportability）+ `supplementary/` 6 张补充表 |
| `confirmatory/` | 三层确证与敏感性结果（NHANES / KNHANES / CHARLS / 文献层 / 方向审计） |
| `cohorts/` | 8 队列 individual-level 结果与异质性 |
| `submission/` | 7_9 投稿包（cover letter、supplementary、STROBE、data availability、graphical abstract）；`_superseded_20261019/` 为旧包 |
| `baseline_predictions_canonical.jsonl` | **推荐使用的基线矩阵**（10,800 行，去重、带 generation/dataset 字段；12/12 校验通过） |
| `README_baseline_predictions.md` | 基线读取规则（canonical 首选；原始日志仅审计） |

## 2. 原始日志与只读证据

- `baseline_predictions.jsonl`、`baseline_predictions_knhanes.jsonl` — **追加日志**，
  含历史 variant 与 `valid=False` 行；不要直接按 `(baseline, seed)` 求指标。
- `baseline_predictions_preR5_archive.jsonl`、`_R5_round1.jsonl`、
  `baseline_predictions_valid.jsonl` — 历史代归档。
- `baseline_summary_R5.json`、`baseline_summary_R11_corrected_gold.json`、
  `baseline_fullsystem_bootstrap_ci.json` — 各代汇总。
- `citation_verification_report.json`、`source_coverage_report.json` — 引用门产物。
- `logs/` — 运行日志（见其 README）。
- `_rerun_backup_20261015/` — R5 重跑前的预测备份。

## 3. 次级与历史目录

| 路径 | 说明 |
|---|---|
| `agent/` | agent 诊断与合成回归产物 |
| `review/` | R1–R6 内部评审与统计复算记录（历史） |
| `expert_review/` | R5 五专家评审 + Phase 4 尝试记录（专家盲评由作者裁定跳过） |
| `exploratory/` | R3 隔离的探索性 pair 结果（不作为确证证据） |
| `_archive/` | 明确过时/被取代的产物，按日期分目录；入口见 `_archive/2026-10-23/README.md` |

## 4. 一句话判据

**要投稿/复现，读 `paper/`、`tables/`、`figures/`、`confirmatory/`、canonical 基线矩阵；
要审计历史，读 `logs/`、`review/`、`exploratory/`、`_archive/`。**
