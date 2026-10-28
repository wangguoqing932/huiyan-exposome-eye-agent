# R31 分析计划附录（预注册）· 2026-10-28

> 本附录在任何 R31 确证计算运行之前落盘并计算 sha256；落盘后的分析口径不得改动，
> 任何偏离按 `docs/analysis_plan.md` §0 模式记录。目的：把"内部矩阵是样本内"这一事实
> 转成可检验、可复核的分析，而不是靠措辞。

## 背景（事实陈述，不含推断）

1. 首次确证运行于 2026-10-11 20:59（v1.1，20 条规则）。2026-10-12 07:12 规则被修改
   （r02/r03/r04 暴露交叉覆盖；新增 r22），随后在同一批配对矩阵上重跑（v1.2，21 条规则）。
   `docs/analysis_plan.md` §0 将此事定性为 test-set fitting，并写明"R=1.000 是构造的，
   不是性能提升"。
2. 受修订影响的配对判定规则（本附录预先固定，不随结果调整）：
   `rule_ids` 字段包含 `r02_`、`r03_`、`r04_` 或 `r22_` 任一项的配对 = **touched**；
   其余 = **clean**。
3. 单元 =（暴露 flag × 结局条目）配对；gold = 三态（replicated / contradicted / uninformative）
   在 survey 方差口径下的现用版本；预测 = 部署配置 G2 的二值 flag。

## P1 · 内部矩阵的定位（描述性，无检验）

对 NHANES 矩阵逐条列出 replicated 配对，并统计其中被 touched 规则覆盖的比例。
**判据**：若全部 replicated 配对均为 touched，则内部 F1 不得作为任何外推性能的估计报告，
只能作为"系统在开发矩阵上的拟合程度"描述，且该描述必须与 touched 比例同时出现。

## P2 · 不受修订污染的估计（确证性，主）

范围：**KNHANES 301 对中的 clean 子集**（即排除 touched 配对）。
理由：KNHANES 从未参与规则修订，clean 子集同时满足"外部数据"与"与修订无关"两个条件，
是本项目唯一同时满足两者的估计面。

报告：G2、G1、G0 与三个基线（LightRAG / pure LLM / naive RAG）在 clean 子集上的
TP/FP/FN/TN、precision、recall、F1（5 seeds 各自计算后给均值与范围）。
**判据（先固定）**：以 G2 与 G0 的 F1 差值描述"agent 是否胜过自身规则层"；
不设显著性通过线，如实报告；若 n 过小（clean 子集 replicated < 5），只作描述并明示功效不足。

## P3 · 三态分解（替代"uninformative 当阴性"的单一折叠）

对 KNHANES 全 301 与 clean 子集，分别报告：
- **recall_replicated** = 被 flag 的 replicated / 全部 replicated
- **flag_rate_contradicted** = 被 flag 的 contradicted / 全部 contradicted（越低越好）
- **flag_rate_uninformative** = 被 flag 的 uninformative / 全部 uninformative（越低越好）
- 以及已声明的二值折叠 F1（保留，但降为次要）

理由：三态标准下 uninformative 既非阳性也非阴性；把它算作阴性会使 precision 无法解释。
分解式指标不需要把 uninformative 归入任一类。

## P4 · 多重比较

对每个数据集，把 G2 与三个基线 × 5 seeds 的准确性 McNemar 精确 p 视为一个家族（15 个检验），
用 Benjamini-Hochberg 校正，报告 q 值。原始 p 与 q 同时给出。

## P5 · 不变项

- 规则集（v1.2，21 条）、三态定义、survey 方差口径、阈值、seed 列表 [11,22,33,44,55] 均不变。
- 不新增规则、不调门控、不换 arbiter 后端、不重选阈值。
- 任何"更好看"的变体一律标 exploratory，不进主结果。

## 输出

- `outputs/confirmatory/r31_holdout.json`（P1/P2/P3/P4 全部数字）
- 论文侧：Results 增补 clean 子集结果与三态分解；Table 3 增列 clean 子集行或脚注；
  Abstract 只在 P2 有可报告数字时引用，否则不引用。

## 落盘记录

- 文件：`docs/analysis_plan_R31_addendum.md`
- 生成时间（本地）：2026-10-28
- sha256：见同目录 `analysis_plan_R31_addendum.sha256`（由 `sha256sum` 生成，先于运行）

## P0 · 运行前补充：基线解析失败的处置（2026-10-28 追加，仍先于任何 R31 确证计算）

`outputs/baseline_predictions_knhanes.jsonl` 中同一 `(baseline, seed, cell)` 可出现多条记录，
差异在 `valid` 字段（`parsed='yes_no'` 但模型输出无法解析时 `valid=false`）。

**规定**：
1. 只采用 `valid=true` 的记录作为该 cell 的预测；
2. 解析失败**不是阴性**，属缺失数据；若某 cell 在该 seed 下全部解析失败，则从该 seed 的指标中剔除，
   并报告剔除数量与占比；
3. 同一 `(baseline, seed, cell)` 若存在两条以上 `valid=true` 且互相矛盾，视为数据错误，停止分析并报告。

**说明**：论文此前报告的基线数字（LightRAG 0.145 / pure LLM 0.135 / naive RAG 0.094）
使用了"解析失败即阴性"的旧处置，属错误处置；本节更正后全部重算，旧值作废并在论文中更新。

## P0b · 运行前补充：G0 的单一来源（2026-10-28 追加，仍先于本轮确证计算）

**发现**：`scripts/run_fused_system.py` 自行调用 `match_rules`，用登记表实体键匹配
（`serum_uric_acid`、`cataract_any`…），而确证 CSV 的 `a_flag`/`b_item` 使用概念名与测量变体
（`hyperglycemia`、`bmi_high`、`cataract_dx`、`retinopathy_selfreport`…）。结果：
KNHANES 301 对中 16 对规则命中在 harness 内被漏判（G0 阳性 16 vs 确证 32），
G0 F1 由 0.360 掉到 0.294。NHANES 的 `a_flag` 恰为登记表兼容写法，故不受影响，
这正是此前只看到"外部不一致"的原因。

**规定**：
1. G0 一律取确证 CSV 的 `predicted` 列（与 headline 规则层同一实现、同一 gold）；
2. 规则 ID 与负对照标记取同表 `rule_ids`、`negative_control` 列；
3. 证据门（G1/G2）逻辑不变，只改为作用在同一批 G0 命中上；
4. 该修正为**实现缺陷更正**，不是分析口径变更；更正前所有 G2 数字作废并重算；
5. 重算后若 G2 仍低于 G0，如实报告；若高于，同样如实报告，且不得据此改主结论。
