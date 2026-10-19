# R5 生物统计评审报告（写作前最后一轮）

- 评审人角色：生物统计学家（诊断/预测研究指标、小样本推断、二项置信区间、bootstrap）
- 日期：2026-10-14
- 范围：docs/analysis_plan.md（v1.2 + §0.1 更正）、outputs/confirmatory/（3 库 CSV + metrics JSON + archive_v1.1/ + 泛化差距）、outputs/baseline_*（4 基线 + bootstrap CI）、outputs/tables/（交付表）、outputs/figures/（figure2 契约 + 源数据）、scripts/evaluate*.py、run_baselines.py
- 方法：只读评审 + 独立重算（pandas/scipy，全部数字可由随附命令复现）；未修改项目任何文件

---

## 一、总结论

**整体框架是健康的**：三态金标准、BHY FDR、Clopper-Pearson 区间、precision-first 定位、协议偏离的完整披露，这些在代码与文档层面基本一致，独立重算全部对得上（4 基线 P/R/F1 逐对比对通过、CP 区间数值验证通过、figure2 源数据与交付表数字一致）。

但**不能直接进入 writer 阶段**。存在 1 个 P0：`compute_metrics_v11` 把 NHANES 的可判 B 项集合硬编码用于全部数据集，导致 **CHARLS coverage=0.667 实为 0.308（2.2 倍虚高）**、KNHANES coverage=0.263 实为 0.233；该数字已流入 limitations §3 与交付口径。另有 6 项 P1：交付表 CI 方法标签错误（写 Wilson 实为 CP）、方差估计偏离预注册未声明（R survey svyglm 未用、Python freq_weights GLM 无设计效应，且 r22 的 2 个复证 q=0.0395 恰在阈值上）、基线差异除 lightrag 外均不显著（McNemar p=1.0，"优于 pure_llm"不能写）、bootstrap 脚本未入库（数值不可逐位复现且 recall CI 结构性退化为 [1,1]）、双 precision 口径（1.0 vs 0.412）需显式桥接、archive_v1.1 的 CI 仍是退化 bootstrap [1,1] 且 figure2 契约"v1.1 为主"与计划冲突。全部修法均为低成本（改 1 个函数参数 + 若干文案），预计半天内可清零 P0/P1。

---

## 二、P0（统计口径硬伤 / 阻塞投稿）

### P0-1 coverage 分母用错可判集合：CHARLS 0.667 应为 0.308，KNHANES 0.263 应为 0.233

**证据**：
- 根因：`scripts/evaluate.py` L384（`compute_metrics_v11` 内）`judgeable = get_judgeable_b_items("nhanes")` —— **数据集键硬编码为 "nhanes"**，对任何传入的 DataFrame 都用 NHANES 可判集合过滤。
- `scripts/evaluate_charls.py` L118 直接调用 `compute_metrics_v11(res)`，无任何本地预过滤 → CHARLS 指标用了 NHANES 可判集合。
- `scripts/evaluate_knhanes.py` L164-179 先用 `get_judgeable_b_items("knhanes")` 预过滤，随后 `compute_metrics_v11` 内又叠加 "nhanes" 过滤 → 实际生效的是两集合的**交集**。
- `data/seed/entities_b.csv` L4（glaucoma_selfreport 行）：`knhanes_judgeable=true, cohort_judgeable=true`，仅 `nhanes_judgeable=false`。即按注册表自身的定义，KNHANES/CHARLS 的 glaucoma_selfreport 是可判项，理应进 coverage 分母。
- 独立重算（详见附表 A）：

| 库 | 现报 t_main | 现报 rp | 现报 coverage | 正确 t_main（按本库 judgeable） | 正确 coverage | 差异 |
|---|---|---|---|---|---|---|
| NHANES | 52 | 14 | 0.269 | 52（无差） | 0.269 | 无 |
| KNHANES | 38 | 10 | 0.263 | 43 | **0.233** | 剔除了 5 条 tested 的 glaucoma_selfreport 对（含 smoking×glaucoma OR=4.30, q=0.073） |
| CHARLS | 6 | 4 | 0.667 | 13 | **0.308** | 剔除了全部 7 条 tested 的 glaucoma_selfreport 对（cohort_judgeable=true） |

- CHARLS 的 0.667 只能复现为 4/6：分子 4 = 预测阳性的白内障对，分母 6 = 白内障对去掉 1 条阴控——**等于把 glaucoma_selfreport 从"testable pairs"里静默删掉**，与 analysis_plan §3 的 Coverage 定义（"rule-covered testable pairs / total testable pairs"）矛盾。
- 流毒范围：`charls_metrics_v11.json` L12、`performance_by_dataset.csv` L6（0.667）、`performance_matrix.csv` L4（0.667）、`docs/limitations.md` §3（"CHARLS 0.667"）。三库 coverage "0.269 / 0.263 / 0.667" 的口径**不可比**：CHARLS 的分母被换成了子集。KNHANES 泛化差距 `generalization_gap_v1.2_summary.json` 的 gap=0.006 也建立在 0.263 上（正确为 0.269−0.233=0.036）。
- 注意：replicated/contradicted/uninformative 计数**不受影响**（被错误剔除的 12 行全部是 predicted=False 或 NC，gold3 全为 uninformative），precision_rule 及其 CP CI 不变——只需修 coverage 及其下游。

**修法**：
1. `compute_metrics_v11` 增加参数 `dataset_key`（默认 "nhanes"），`evaluate_knhanes.py`/`evaluate_charls.py` 分别传 "knhanes"/"cohort"（或干脆去掉 KNHANES 的预过滤、只在 metrics 内过滤一次）。
2. 重跑三库 metrics JSON、`performance_by_dataset.csv`、`performance_matrix.csv`、`generalization_gap_v1.2_summary.json`、limitations §3 的数字（CHARLS 0.667→0.308，KNHANES 0.263→0.233，gap 0.006→0.036）。
3. 论文中如保留"三库 coverage 可比"的表述，必须确认三库分母定义一致后再写。

---

## 三、P1（重大）

### P1-1 交付表 CI 方法标签错误：写 "Wilson"，数值实为 Clopper-Pearson

**证据**：`outputs/tables/performance_matrix.csv` L2-L4 methodology 列 = "three-state gold + **Wilson CI** (analysis_plan v1.2)"，但同表 ci 值 [0.59,1.0]/[0.158,1.0] 经 scipy 验证为 CP（Wilson 应为 [0.646,1.0]/[0.342,1.0]）。`performance_by_dataset.csv` L3/L5 写的是 "Clopper-Pearson"，两表互相矛盾。这正是 §0.1-更正2 所说"交付物曾同时出现 Wilson 值"的残留——R4 只统一了数值，漏了这张表的标签。
**修法**：performance_matrix.csv methodology 列改为 "three-state gold + Clopper-Pearson exact CI (analysis_plan v1.2 §0.1)"。一行文字改动。

### P1-2 方差估计偏离预注册且未声明；r22 的 2 个复证恰在 FDR 阈值上

**证据**：
- analysis_plan §6（L88-91）预注册：NHANES/KNHANES 以 R survey `svyglm`（strata=SDMVSTRA、psu=SDMVPSU、weights=WTMEC2YR）为**确证标准**；降级路径须"显著标注"。全库 `grep svyglm|Rscript|survey` 仅命中 evaluate.py 文档字符串 L8，实际实现是 `sm.GLM(..., freq_weights=w)`（evaluate.py L317、evaluate_knhanes.py L143、evaluate_charls.py L100）：归一化权重当频数权重用，**无分层、无 PSU、无设计效应**。`docs/limitations.md` 七个小节均未声明此偏离。
- 后果不是点估计（权重归一化下 OR 不变），而是 **SE 系统性偏小 → p/q 偏小 → gold 标签偏"复证"**。NHANES 调查数据设计效应普遍 1.5-3 倍，而 `nhanes_confirmatory.csv` L56-57 的 r22 两条（bmi×retinopathy q=0.0395、bmi×dr_npdr q=0.0395）**恰好压在 0.05 线上**（原始 p=0.0009/0.0011 但 BHY 校正后 q=0.0395）——SE 放大 1.5 倍即翻成 uninformative。届时 NHANES 变 5 复证 0 反证，precision 仍 1.0 但 CP 下界从 0.59 降到 0.478。
**修法**（三选一，按成本）：
1. 最低成本：limitations 增加一条"方差估计偏离"——预注册 R survey 未用，Python 加权 GLM 未校正分层/聚类，q<0.05 的金标准判定在设计效应下偏宽松；正文金标准方法部分如实写实际实现。
2. 推荐：用 R survey（或 Python `statsmodels` Sandwich + 分层聚类稳健方差）对 7 个 replicated + 2 个 borderline 对做敏感性分析，报告哪些标签稳固。r22 本来就定性探索性，若其翻转不影响 headline（P 仍 1.0），写明即可。
3. 论文表述：gold 标签写 "survey-weighted logistic regression (weights normalized; design-based variance not applied — see Limitations)"，不得写 "design-based analysis"。

### P1-3 基线差异的显著性：只对 lightrag 成立，"优于 pure_llm/naive_rag"不能写

**证据**（本评审独立计算，71 对配对 McNemar 精确检验，按"判对/判错"配对）：
- full_system vs pure_llm：discordant 8/7，**p=1.000**
- full_system vs naive_rag：discordant 8/9，**p=1.000**
- full_system vs lightrag：discordant 19/2，**p=0.0002**
- 机理：71 对里 61 对 uninformative 是"容易的 TN"，四系统 accuracy 85.9%/84.5%/87.3%/62.0% 几乎无差；F1 的差距全部由 7 个 positive 驱动。full_system F1 bootstrap CI [0.286,0.800]（自报）与各基线点估计全部重叠。
- 叠加：LLM 基线仅 1 个 seed（temp=0.7），违反预注册 §9 的 ≥5 seeds [11,22,33,44,55]（`run_multiseed.py` 为未实现 stub，退出码 1）；跨后端（本地 qwen3.8-27b 3bit vs 确定性引擎）。
**修法（写作纪律）**：
- 可写："full system 达到最高 F1（0.583）"（描述性）；"与 lightrag 的逐对判对率差异显著（McNemar exact p=0.0002）"。
- 不可写："significantly outperforms pure_llm/naive_rag"、"F1 提升 38%"之类因果/显著性表述；vs pure_llm 只能写 "higher F1 (0.583 vs 0.421, descriptive; paired difference not significant)"。
- 建议把本评审的 3 个 McNemar p 值算入论文（脚注或附表），这是审稿人一定会问的。
- ≥5 seeds 复跑列入 limitations 承诺（已有），或投稿前用现有额度补跑。

### P1-4 bootstrap CI 产物不可复现，且 recall CI 结构性退化未标注

**证据**：
- `outputs/baseline_fullsystem_bootstrap_ci.json` 自报 B=2000、seed=42、percentile。**scripts/ 下没有任何生成它的代码**（grep "bootstrap" 仅命中 evaluate.py 的 CP 注释）。本人按同一口径（71 对行级重抽、B=2000、分别用 `default_rng(42)` 与 legacy `np.random.seed(42)`）复现：precision [0.176,0.667]、F1 [0.300,0.800]，与自报 [0.167,0.667]/[0.286,0.800] 接近但不逐位一致——说明实现细节（RNG、抽样方式）与任何自然重写不同，审稿人/复现者无法验证。
- recall CI [1.0,1.0]：full_system 对全部 7 个 gold-positive 都预测 YES，行级 bootstrap 中 FN 恒为 0，**任何重抽 recall 都=1**——区间不携带信息，属于构造性退化（JSON note 只说了"finite-test-set sampling"，没说 recall 区间无信息量）。
- 另注意 B=2000 与计划 §3 的"1000 次"不一致（§3 的 1000 指 headline bootstrap，已被 CP 取代，但正文如引用 B 值需统一说法）。
**修法**：
1. 把 bootstrap 脚本入库（如 `scripts/bootstrap_baseline_ci.py`），JSON 里记录脚本路径；或
2. 更稳妥：baseline precision 改报 CP（7/17 → **[0.184, 0.671]**，本评审计算），F1 报 bootstrap 并附脚本；recall 标注 "CI degenerate by construction (engine answers YES on all gold positives)"。
3. limitations §2 中引用 F1 CI 时同步注明方法与 B。

### P1-5 同一引擎的两个 precision（1.0 与 0.412）必须显式桥接；headline 与基线的评测集也不同（52 vs 71）

**证据**：
- headline precision_rule=1.0 [0.59,1.0]：分母 = 信息性对（rep+con）=7，评测集 = tested ∩ judgeable ∩ 非阴控 = 52 对中的 14 个规则对（evaluate.py L391-396）。
- 基线表里同一 full_system 的 precision=0.412：分母 = 全部预测 YES 的 17 对（含 10 个 uninformative 记 FP、含阴控 r01），评测集 = 全部 71 个 tested 对（run_baselines.py L73-89 无 judgeable/NC 过滤，`metrics()` L206-212 positive=replicated）。
- 评测集与分母双重不同 → "我们的系统 precision 是 1.0"（正文）与"precision 0.412"（基线表）若不解释，审稿人会当成矛盾或作弊。figure2 契约 panel_a 已写明 "both numbers must be reported"（好），但交付表 performance_by_dataset.csv 中两行共存且无脚注。
- 阴控 r01（uric×cataract，uninformative）在基线口径下被计为 full_system 的 FP——与计划 §1"阴控不进 headline"精神不一致，需一句话说明"基线口径为严格二分视图，阴控按普通对计入"。
**修法**：正文 Methods 用一小节或表格并列两个口径（declared-scope precision vs strict-view precision），明确各自分母；基线表脚注注明评测集 n=71（全部 tested 对，含阴控）而 headline n=52（judgeable、非阴控）；figure2 panel_a 的做法可作为模板。

### P1-6 archive_v1.1 的 CI 仍是退化 bootstrap [1,1]；figure2 契约"v1.1 为主要确证视图"与计划处置不一致

**证据**：
- `outputs/confirmatory/archive_v1.1/nhanes_metrics_v11.json`：rep=1/con=0，ci=[1.0,1.0]——这是 §0.1-更正2 明确废弃的"退化 bootstrap"旧值，R4 的"CI 统一为 CP"没有波及归档件。若 v1.1 数据以任何形式进论文（计划 §0 处置 3 要求"同时呈现 v1.1 与 v1.2 两版指标"），其 CI 必须重算：1/1 的 CP = **[0.025, 1.0]**（本评审计算），与 [1,1] 天壤之别。
- `figure2_performance.yaml` L164（review_risks.recall_inflation）写 "v1.1 metrics (archive_v1.1/) are the **primary confirmatory view**"，但 analysis_plan §0 处置只说两版并呈、v1.2 标注探索性扩展，并未规定 v1.1 为主；且交付表实际主打的是 v1.2 数字。表述需统一，否则 writer 会两头引。
**修法**：(a) 给 archive_v1.1 三份 metrics JSON 补算 CP CI（重算脚本同 evaluate.py 现有 CP 代码）；(b) figure2 契约该句改为与计划 §0 一致的措辞（"v1.1 presented alongside as the pre-expansion view; v1.2 flagged as containing exploratory extensions"）。

### P1-7 "通过预注册线"只在点估计意义上成立，必须带 CI 限定

**证据**：预注册通过线 precision_rule ≥0.70（内部）/≥0.80（外部）。NHANES 1.0≥0.70、KNHANES 1.0≥0.80 均以点估计通过；但 CP 下界 0.59/0.158 远低于线。以均匀先验后验计：P(真实 precision≥0.70 | 7/7)=0.7^7≈**0.082**；P(≥0.80 | 2/2)=0.8^2≈0.64（本评审计算）。即 **7/7 的证据实际上无法在统计上支持"真实精度≥0.70"**——这正是 n 极小时"完美点估计"的陷阱。
**修法**：结论写法固定为："point estimate meets the pre-registered threshold (1.00 ≥ 0.70/0.80); however, with only 7/2 informative pairs the 95% CI lower bounds (0.59/0.16) do not exclude precision below the threshold — the pass criterion is met on point estimates only"。禁止出现 "confirms precision ≥ 0.70" 这类话。同理，"P=1.0" 任何出现处必须伴随 "[CP 95% CI …, n=…]"——"precision=1.0" 裸写即误导（下界 0.59 的正确解读：真实精度最低也有约 59% 的把握（97.5% 单侧），但不足以排除低于预注册线的可能）。

---

## 四、P2（建议）

1. **limitations.md §5 数字过期**：写 "lightrag 0.263"（应为 F1 0.270；0.263 是 KNHANES coverage，串行了）、"P=0.161（31/71 YES）"（是 2026-10-14 重跑前的旧值；现 P=0.167、30/71 YES）。写作前统一。
2. **full_system 的 provider 标签**：baseline_summary_v12.json 与 figure2 源数据都标 "deepseek:legacy"，但 run_full_system（run_baselines.py L92-126）是纯规则查表、零 LLM 调用。标 provider 不仅无意义还会误导 provenance；应标 "deterministic rule engine (no LLM call)"。
3. **coverage 图例措辞**（figure2 yaml L179）"coverage = rule-covered testable pairs / testable pairs (0.269)" 不精确：实际分母是 tested∩judgeable∩非阴控（14/52），不是 71。修完 P0-1 后按新分母改写。
4. **uncovered_significant 只数 replicated**：evaluate.py L412。NHANES 库内另有 3 对显著**反向**关联（hba1c×VI_severe OR=0.57 q=0.04；alcohol×retinopathy OR=0.65 q=0.003；alcohol×dr_npdr OR=0.64 q=0.002）落在规则覆盖之外，metrics 里不可见。"coverage=透明度指标"的叙事下，建议双向都报（uncovered_sig_same_dir / uncovered_sig_inverse）。
5. **非规则对的 "contradicted" 标签语义**：three_state（evaluate.py L214-221）对 predicted=False 的对用默认 direction=risk_up，显著 OR<1 即标 contradicted——但对没有声明的对，"contradicted"（反证）无从谈起，实义是"显著反向关联"。figure2 panel_b 说 "contradicted pairs are all uncovered by rules" 与数据一致，但图注/正文应解释该标签对未覆盖对的含义，避免读者以为有 3 条规则被库内反证。
6. **泛化一致性建议补 κ**：28/35 原始一致率 80%，但主要由 uninformative 驱动，Cohen κ=0.273（本评审计算）。契约 panel_c 注记建议加 κ 并避免"标签高度泛化"的措辞；同理 generalization gap 0.006/0.0 是点估计层面，两库 CI 极宽，"gap≈0"不能引申为"泛化性好"。
7. **功效过滤器未预注册**：len≥200、n_pos≥30、暴露≥30、n_pos≤n−30（evaluate.py L303）决定了哪些对算 "tested"，从而决定 coverage 分母，但阈值不在 analysis_plan 中。Methods 里必须写明并给理由（建议也写进 limitations）。
8. **run_baselines.py L211 的 F1 边界 bug**：`f1 = ... if prec and rec else None`——P=0 或 R=0 时 F1 返回 None 而非 0（本批数据未触发；naive_rag 若 TP=0 即触发）。改为 `if prec is not None and rec is not None and (prec+rec)>0`。
9. **vi_mild 全部 n_pos=0**：NHANES 9 条 vi_mild 对全部 underpowered 且 n_pos=0，而更重的 vi_moderate 有 314 例阳性——(0.30,0.48] 区间 0 例在逻辑上几乎不可能，疑 VIXPRS 编码/单位问题。不影响现有指标（vi_mild 不进任何指标），但 "not_tested=29" 的构成里有 9 条可能是编码 bug 而非真缺功效，值得在正文或补充材料交代一句。
10. **指标文件名 _v11**：经全量重算确认，三份 *_metrics_v11.json 的数值与**当前 v1.2 规则的 CSV 完全一致**（见附表 A；v1.1 旧值在 archive_v1.1/ 且确实不同：NHANES 8 对 1 复证）。文件名后缀指"指标模式 v1.1（precision+coverage）"而非规则集 v1.1，建议在 README 或文件内 note 一句话说明，否则每个读者都会问一遍。
11. **performance_by_dataset.csv 的 n_cases 列语义**：coverage 行填 14（分子 rp 数）、precision 行填 7（rep 数），与列名 "n_cases" 不匹配。建议拆成 n_numerator/n_denominator 两列（coverage 行 14/52、14/43、4/13；precision 行 7/7、2/2）。

---

## 五、独立重算结果附表

### A. 三库确证指标（对 CSV 全量重算；"as-run" = 复现现有 JSON，"correct" = 按本库 judgeable 集合）

| 库 | rows | tested | underpowered | t_main (as-run) | rp | rep/con/uninf | precision (CP 95% CI) | coverage as-run | t_main correct | coverage correct |
|---|---|---|---|---|---|---|---|---|---|---|
| NHANES | 100 | 71 | 29 | 52 | 14 | 7/0/7 | 1.000 [0.590, 1.000] ✓ | 0.269 ✓ | 52 | 0.269（同） |
| KNHANES | 64 | 49 | 15 | 38 | 10 | 2/0/8 | 1.000 [0.158, 1.000] ✓ | 0.263 ✓ | 43 | **0.233** |
| CHARLS | 14 | 14 | 0 | 6 | 4 | 0/0/4 | n/a（0 信息性对）✓ | 0.667 ✓ | 13 | **0.308** |

- 与 `outputs/tables/validation_distribution.csv` 逐格一致 ✓；与三份 metrics JSON 逐格一致 ✓（即"v11 文件 vs v1.2 CSV 口径错位"的担忧**不成立**，数值同属 v1.2 规则口径）。
- CP 验证：7/7 → beta.ppf(0.025,7,1)=0.5904；2/2 → 0.025^0.5=0.1581 ✓。作为对照 Wilson 会给 [0.646,1.0]/[0.342,1.0]，证明现行数值确为 CP（即 P1-1 的标签错误）。

### B. 四基线 P/R/F1（从 baseline_predictions_valid.jsonl 284 条独立重算）

| 基线 | TP | FP | FN | TN | P | R | F1 | 与声明一致？ |
|---|---|---|---|---|---|---|---|---|
| full_system | 7 | 10 | 0 | 54 | 0.4118 | 1.0000 | 0.5833 | ✓ |
| pure_llm | 4 | 8 | 3 | 56 | 0.3333 | 0.5714 | 0.4211 | ✓ |
| naive_rag | 1 | 3 | 6 | 61 | 0.2500 | 0.1429 | 0.1818 | ✓ |
| lightrag | 5 | 25 | 2 | 39 | 0.1667 | 0.7143 | 0.2703 | ✓ |

- full_system 的 71 条预测与 nhanes_confirmatory.csv 的 predicted 列逐对一致（0 mismatch）；gold3 逐对一致（0 mismatch）✓。
- figure2_performance.csv 源数据与本表一致（lightrag F1 写 0.27 为 3 位舍入）✓。

### C. bootstrap 复现（行级 percentile，B=2000，seed=42，两种 RNG 均试）

| 指标 | 自报 | 复现 | 判定 |
|---|---|---|---|
| precision | [0.167, 0.667] | [0.176, 0.667] | 量级一致，不逐位复现（代码未入库） |
| recall | [1.0, 1.0] | 结构性恒为 1（FN 恒 0） | 退化，需标注 |
| F1 | [0.286, 0.800] | [0.300, 0.800] | 同 precision |

补充：baseline precision 的 CP 对照 = 7/17 → [0.184, 0.671]。

### D. 配对检验与一致性（新增计算）

| 比较 | discordant（full对/基线错 vs 基线对/full错） | McNemar exact p |
|---|---|---|
| full vs pure_llm | 8 / 7 | 1.000 |
| full vs naive_rag | 8 / 9 | 1.000 |
| full vs lightrag | 19 / 2 | **0.0002** |

| 一致性 | 数值 |
|---|---|
| NHANES×KNHANES gold3（35 共同 tested 对） | 28/35 一致（80.0%）✓（与 gap summary 相符）；Cohen κ=0.273 |
| P(真 precision≥0.70 \| 7/7, 均匀先验) | 0.082 |
| P(真 precision≥0.80 \| 2/2, 均匀先验) | 0.640 |

### E. figure2 契约数值断言核对

- "replicated 7 / contradicted 3 / uninformative 61（共 71）" ✓；"7 replicated predicted positive、10 uninformative predicted positive、3 contradicted 全部未被规则覆盖、FN=0" ✓；coverage 0.269/0.263 与 gap 0.006/0.0 ✓（但受 P0-1 影响，coverage 数字待更新）。

---

## 六、通过项（明确无问题）

1. **Clopper-Pearson 用于 precision 二项 CI**：方法选择正确（7/0、2/0 这类边界情形 CP 是唯一非退化选项），scipy beta 实现（evaluate.py L400-404）数学正确，7/7→[0.590,1.0]、2/2→[0.158,1.0] 数值验证通过。§0.1-更正2 的方法学记录（bootstrap 退化→CP）理由成立且诚实。
2. **三态金标准的实现**：three_state（evaluate.py L214-221）与计划 §2 逐条对应（q<0.05 + 方向；非显著一律 uninformative 不冒充反证）；separation 独立状态而非混入 uninformative。
3. **BHY FDR 实现**（evaluate.py L199-211）：标准 Benjamini-Yekutieli step-up 调整 p（c(n)=Σ1/i，逆向累积最小化，clip [0,1]），逐库对全部 tested 对计算，符合计划 §7。（方差输入问题见 P1-2，FDR 机制本身无误。）
4. **"复证/反证"判定统计量**：规则引擎本身是确定性查表（risk_rules.match_rules，无统计量）；统计判定全部在库内金标准侧 = 加权 logistic 回归 OR 的方向 × BHY q<0.05。这个"引擎声明、数据库裁决"的架构清晰，判定统计量（方向×FDR 阈值）选择合理且可复现。阈值 q<0.05 与预注册一致。
5. **基线数值与明细**：4 基线 P/R/F1、TP/FP/FN 全部独立重算通过；预测与 gold 与 CSV 逐对一致；figure2 源数据一致。
6. **metrics JSON 与 CSV、交付表（数值）一致性**：三库 metrics、performance_by_dataset.csv、performance_matrix.csv（数值列）、validation_distribution.csv、generalization gap summary 数值全部与 CSV 重算一致（coverage 口径问题除外，见 P0-1；Wilson 标签问题见 P1-1）。
7. **诚实披露文化**：测试集拟合事件（§0）、recall=1.0 的构造性、单 seed 跨后端、负控仅 1 条等已入 limitations；figure2 契约的 review_risks 预判准确。这在同类工作里属于少见的透明度，保持。
8. **n=14 的选择偏差已正名**：precision_rule 明确限定"引擎发言范围内、信息性对内"，uninformative 单列而非并入分母或分子——该定义下 n=7（NHANES 信息性对）不是事后挑选，是三态设计的自然结果；需做的只是论文里把"信息性对"的成因（功效不足→q≥0.05）与 precision 的适用范围写透（limitations §7 已有雏形）。

---

## 七、修复优先级清单（供执行）

| # | 级别 | 动作 | 预估成本 |
|---|---|---|---|
| 1 | P0 | evaluate.py L384 增加 dataset_key 参数；重算 KNHANES/CHARLS coverage 及全部下游（tables、gap summary、limitations §3） | 2-3 小时 |
| 2 | P1-1 | performance_matrix.csv 方法标签 Wilson→Clopper-Pearson | 1 分钟 |
| 3 | P1-6 | archive_v1.1 三份 JSON 补 CP CI；figure2 契约 "primary confirmatory view" 措辞对齐计划 §0 | 30 分钟 |
| 4 | P1-5 | 论文/表格加双 precision 桥接脚注（52 vs 71 评测集、阴控处理） | 写作时 |
| 5 | P1-3 | 基线段落按"仅 lightrag 显著"的纪律表述；把 3 个 McNemar p 写入附注 | 写作时 |
| 6 | P1-7 | "通过预注册线"全部改为点估计达标+CI 限定句式 | 写作时 |
| 7 | P1-4 | bootstrap 脚本入库或 baseline precision 改报 CP [0.184,0.671]；recall CI 标退化 | 1 小时 |
| 8 | P1-2 | limitations 增方差估计偏离条目（最低）；建议对 7 复证+2 边缘对做 survey 方差敏感性 | 1 小时～1 天 |
| 9 | P2 | 按第四节逐条清理（limitations 旧数字、provider 标签、κ、功效阈值声明、F1 边界 bug 等） | 2 小时 |
