# 基线预测文件的读取说明（重要）

## 推荐读取（2026-10-23 起）

- **`baseline_predictions_canonical.jsonl`** —— 去重后的规范矩阵，共 10,800 行，
  带 `dataset_id` / `dataset_role` / `generation` 字段。它是唯一应当直接用于指标计算的
  文件；12 组 F1 由 `scripts/verify_canonical_predictions.py` 逐项校验（当前 12/12 PASS）。
  重建命令：`python scripts/build_canonical_predictions.py`。
- 原始 `baseline_predictions*.jsonl` 是**追加日志**（含历史 variant、`valid=False` 行与
  跨代重复），只在审计时使用；直接按 `(baseline, seed)` 分组会读错（例：NHANES
  full_system 会得到 0.385 而非 0.480）。

## R5 现状（2026-10-14，本节为准）

- `baseline_predictions.jsonl` — **R5 重跑结果（当前唯一有效数据源）**：
  - full_system：确定性规则引擎（provider=rule_engine:deterministic），5 seeds（结果相同），400 行；
  - pure_llm / naive_rag / lightrag：本地 qwen3.8-27b（thinking disabled，temp=0.7），预注册 5 seeds [11,22,33,44,55]，seed 传入 API 请求体，每 run 0 失败，各 400 行；
  - gold：`nhanes_confirmatory.csv` 的 gold3 列（R5 主口径 = survey svyglm 方差；80 tested 对层面 R5 运行时共 7 个 replicated 阳性，其中 5 个为规则覆盖——headline"5 复证"即后者；R11 变量修正后当前金标准为 **6 replicated / 2 contradicted**，见下节）；
  - 解析规则：YES/NO 首行；明确的"证据未提及"陈述映射为 NO 并标 `parsed="no_evidence_inference"`（透明可审计）。
- `baseline_predictions_valid.jsonl` — 与主文件相同的副本（R5 全部行 valid）。
- `baseline_predictions_R5_round1.jsonl` — round-1 归档（更严格解析器：no-evidence 回答被判失败），保留供 prompt 敏感性分析。
- `baseline_predictions_preR5_archive.jsonl` — R5 之前全部历史代归档（旧 gold、旧协议），**不得用于指标**。
- `baseline_summary_R5.json` — per-seed 指标 + 均值±std + McNemar（R5 记录，gold 为当时口径）。
- `baseline_summary_R11_corrected_gold.json` — **R11 修正 gold 双呈**（2026-10-15 变量修复后；同一批冻结预测在新旧 gold 两个口径下并列）。2026-10-19 用 canonical 链重新结算后的当前对外数字见下节；显著性结论不变。
- `baseline_fullsystem_bootstrap_ci.json` — R5 重算：F1=0.417 [0.118, 0.640]（B=2000）；R10 起由 `scripts/make_baseline_bootstrap_ci.py` 逐位可复现（gold=80 对层面 survey 三态标签共 7 个 replicated 阳性、其中 5 个规则覆盖；R=5/7）。

## R5 指标（80 tested 对，survey 方差 gold，5 seeds 均值±std）

| baseline | P | R | F1 | McNemar vs full_system |
|---|---|---|---|---|
| full_system | 0.294 | 0.714 | **0.417**±0.000 | — |
| pure_llm | 0.214±0.009 | 0.914±0.070 | 0.347±0.017 | p=0.004–0.012 显著 |
| lightrag | 0.203±0.004 | 0.714±0.000 | 0.317±0.005 | p=0.057–0.092（**qwen 代残血基线历史值**；R17 满血后见下节，vs lightrag 转显著） |
| naive_rag | 0.100±0.122 | 0.057±0.070 | 0.073±0.089 | p≤0.013 显著 |

v1.1（事前注册规则集）回放同一 gold：F1=0.111（TP1/FP10/FN6，见 confirmatory/v11_replay_R5.json）——论文必须与 v1.2 双呈。

## R17 zhipu 代（GLM-5.3-flash，基线公平修复后，2026-10-20/23）

- **lightrag 基线升级为 hybrid KG 图遍历**（qwen 代曾为 naive 纯向量残血——limitations §5 已改）；mix+rerank 实测更差（0.164）故定格 hybrid
- NHANES 159 对矩阵，5 seeds 全 0 失败，导出/判定数据在 baseline_predictions.jsonl（provider=zhipu:glm-5.3-flash 段）：

| baseline | F1 | P | R | McNemar vs full |
|---|---|---|---|---|
| **full_system** | **0.480±0.000** | 0.316 | 1.000 | — |
| lightrag | 0.186±0.006 | 0.103 | 0.833 | **p≈3×10⁻¹¹ 显著** |
| pure_llm | 0.178±0.015 | 0.098 | 1.000 | **p≈10⁻¹⁹ 显著** |
| naive_rag | 0.069±0.086 | — | 0.067 | p≤0.013 显著 |

- **KNHANES 301 对**（R15）：full 0.360 > lightrag 0.145 > pure 0.135 > naive 0.094，vs 全部基线显著
- **代际纪律**：qwen 代（80 对）与 zhipu 代（159 对）双呈，不做合并均值；论文主口径=zhipu 代满血基线


## R11 修正 gold 当前数字（2026-10-19 重算，对外引用以此为准）

金标准：`nhanes_confirmatory.csv` gold3（survey svyglm 主口径），80 对评分面内 6 个
replicated 阳性、2 个 contradicted；predictions 为 2026-10-14 冻结的运行（5 seeds）。

| baseline | P | R | F1 | 说明 |
|---|---|---|---|---|
| full_system | 0.353 | 1.000 | **0.522** | 确定性（5 seeds 完全相同），TP 6 / FP 11 / FN 0 |
| lightrag | 0.244 | 1.000 | 0.392 ± 0.007 | |
| pure_llm | 0.202 | 1.000 | 0.335 ± 0.010 | 本地 qwen3.8-27b，temp 0.7 |
| naive_rag | 0.100 | 0.067 | 0.080 ± 0.110 | 部分 seed 无预测，按 0 计入均值 |

McNemar（full_system vs）：pure_llm p = 0.0043–0.0118 显著；naive_rag p = 0.00024–0.0129
显著；lightrag p = 0.057–0.092 **不显著**。v1.1 回放 F1 = 0.111（必须双呈）。

> 与上表 R5 gold 的 0.417 不可直接比较：金标准不同（R5 为 7 阳性，R11 修正后为 6 阳性）。

## 读取规则
- 指标从 `baseline_predictions_canonical.jsonl` 按 `(dataset_id, generation, baseline, seed)` 分组计算；
- **原始日志的读取口径（2026-10-23 更正）**：该文件是多次运行追加写入的，含历史 variant（hybrid / mix / rerank）与 `valid=False` 行，同一 `(seed, a_flag, b_item)` 最多出现 4 次。计算指标前必须 **(a) 过滤 `valid == True`，(b) 按 `(seed, a_flag, b_item)` 去重并保留最后一行**（后追加的块才是修正后的重跑；保留首行会得到 0.385/0.345 等错误值）。
- `full_system` 两代共用 `provider=rule_engine:deterministic`，无法用 provider 区分代际；canonical 文件按 80 对（qwen）与 159 对（zhipu）显式拆分。
- F1 无定义的 seed（TP=FP=0，如部分 naive_rag seed）按 0 计入均值（排除会高估）；
- 旧 v1.2 数字（F1 0.583/0.421/0.270/0.182，71 对、freq 方差 gold、单 seed）已过时，见归档。
