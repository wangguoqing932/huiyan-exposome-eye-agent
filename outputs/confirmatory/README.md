# outputs/confirmatory/ — 确证层结果

当前对外数字的来源。读取时先看 `outputs/README_baseline_predictions.md` 与
`docs/analysis_plan.md` 的口径说明。

| 文件 | 内容 |
|---|---|
| `nhanes_confirmatory.csv` | NHANES 全部 180 对的 OR/CI/q/gold3（R11 修正金标准；80 对评分面） |
| `knhanes_confirmatory.csv` | KNHANES 对应表（跨国层） |
| `charls_confirmatory.csv` | CHARLS 2011 波可行性层 |
| `charls2015_confirmatory.csv` | CHARLS 2015 时间外层（规则未见过的数据） |
| `nhanes_metrics_v11.json` / `knhanes_metrics_v11.json` | 规则层 coverage / precision / 复现计数 |
| `direction_review_*.csv` | 方向审计（第四态） |
| `literature_validation_R5.csv`、`*_R18/R19.json` | 文献层及四库交叉验证 |
| `survey_sensitivity_R5.csv` | survey 方差主口径 vs 频率权重敏感性 |
| `prevalence_gate_*.json` | 操作化患病率门（>50% 报警 / >2.5× 阻断） |

`archive_v1.1/`、`archive_v1.2_preR5/` 是历史口径，**不得用于当前指标**。
