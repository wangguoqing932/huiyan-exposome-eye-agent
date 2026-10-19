# 基线预测文件的读取说明（重要）

## R5 现状（2026-10-14，本节为准）

- `baseline_predictions.jsonl` — **R5 重跑结果（当前唯一有效数据源）**：
  - full_system：确定性规则引擎（provider=rule_engine:deterministic），5 seeds（结果相同），400 行；
  - pure_llm / naive_rag / lightrag：本地 qwen3.8-27b（thinking disabled，temp=0.7），预注册 5 seeds [11,22,33,44,55]，seed 传入 API 请求体，每 run 0 失败，各 400 行；
  - gold：`nhanes_confirmatory.csv` 的 gold3 列（R5 主口径 = survey svyglm 方差；80 tested 对层面共 7 个 replicated 阳性，其中 5 个为规则覆盖——headline"5 复证"即后者）；
  - 解析规则：YES/NO 首行；明确的"证据未提及"陈述映射为 NO 并标 `parsed="no_evidence_inference"`（透明可审计）。
- `baseline_predictions_valid.jsonl` — 与主文件相同的副本（R5 全部行 valid）。
- `baseline_predictions_R5_round1.jsonl` — round-1 归档（更严格解析器：no-evidence 回答被判失败），保留供 prompt 敏感性分析。
- `baseline_predictions_preR5_archive.jsonl` — R5 之前全部历史代归档（旧 gold、旧协议），**不得用于指标**。
- `baseline_summary_R5.json` — per-seed 指标 + 均值±std + McNemar（R5 记录，gold 为当时口径）。
- `baseline_summary_R11_corrected_gold.json` — **R11 修正 gold 双呈**（2026-10-15 变量修复后；同一批冻结预测在新旧 gold 两个口径下并列：full_system 0.417→0.435 等，显著性结论不变）。当前对外引用以修正口径为准。
- `baseline_fullsystem_bootstrap_ci.json` — R5 重算：F1=0.417 [0.118, 0.640]（B=2000）；R10 起由 `scripts/make_baseline_bootstrap_ci.py` 逐位可复现（gold=80 对层面 survey 三态标签共 7 个 replicated 阳性、其中 5 个规则覆盖；R=5/7）。

## R5 指标（80 tested 对，survey 方差 gold，5 seeds 均值±std）

| baseline | P | R | F1 | McNemar vs full_system |
|---|---|---|---|---|
| full_system | 0.294 | 0.714 | **0.417**±0.000 | — |
| pure_llm | 0.214±0.009 | 0.914±0.070 | 0.347±0.017 | p=0.004–0.012 显著 |
| lightrag | 0.203±0.004 | 0.714±0.000 | 0.317±0.005 | p=0.057–0.092 不显著 |
| naive_rag | 0.100±0.122 | 0.057±0.070 | 0.073±0.089 | p≤0.013 显著 |

v1.1（事前注册规则集）回放同一 gold：F1=0.111（TP1/FP10/FN6，见 confirmatory/v11_replay_R5.json）——论文必须与 v1.2 双呈。

## 读取规则
- 指标从 `baseline_predictions.jsonl` 按 `(baseline, seed)` 分组计算（80 行/组）；
- F1 无定义的 seed（TP=FP=0，如部分 naive_rag seed）按 0 计入均值（排除会高估）；
- 旧 v1.2 数字（F1 0.583/0.421/0.270/0.182，71 对、freq 方差 gold、单 seed）已过时，见归档。
