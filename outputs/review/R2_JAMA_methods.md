# R2 · JAMA 方法学与统计学审稿报告（数字对账负责人）

> 审稿人立场：JAMA 资深审稿人，方法学/统计守门人，本轮承担**全量数字对账**。
> 审稿对象：`outputs/paper/manuscript.md`（含 `outputs/paper/sections/*.md`、图注、表 1–7）
> 对账源：`outputs/cohorts/*`、`outputs/tables/*`、`outputs/confirmatory/cohort_rule_coverage.json`、
> `outputs/confirmatory/power_summary.json`、`outputs/figures/source_data/*`、`data/frames/cohort_*.csv`、
> `scripts/cohort_confirmatory.py`、`cohort_heterogeneity.py`、`cohort_power.py`、`evidence_base_audit.py`
> 说明：所有数字均**逐个**回溯到落盘文件；对核心三组数字（主张 a/b/c）做了**独立重算**（未使用作者脚本）。
> 凡我无法在提供材料中核验的，一律标【出处不明】或【不可核验】，不作善意推定。

---

## 总体评价

这篇稿件的问题不在于统计工作量，而在于**分母与推断的诚实度**：标题、摘要与正文反复使用的
"2.0 million person-waves" 经核查是 SHARE 五个插补副本的行数（338,703 个真实 person-wave × 5）
再加上 MHAS 一个损坏的连接产物（78,537 行 vs 15,213 个唯一 person-wave）得到的，真实可分析的
独立 person-wave 约 **60 万**、参与者约 **28.6 万**——标题级别的分母被高估了 3 倍以上。
更严重的是，稿件三大定量主张中最核心的一条（"吸烟-白内障的地区性方向反转"）经独立重算不成立：
ELSA 是**欧洲**队列且为保护向（稿件称"三条保护向队列都不是欧洲的"，是事实错误），而亚组差异检验
用的是**组内固定效应权重**（在 I²=91% 下无效），改用组内随机效应后 Europe OR 由 1.08 变为 0.94、
Q_between 由 24.61 降为 1.59、**p 由 <0.0001 变为 0.45**——"地区亚组差异显著"这一论断是模型伪影。
第三，队列层全部分析**偏离了预注册方案 §19.7 的方差规定**（方案要求 SHARE/LASI 等用 survey 设计
strata/PSU/weights，实现是**无权重**的 cluster-robust GLM，且八个队列 frame 里根本没有任何权重变量），
方案 §19.9 明令偏离须记录于 §0，而 §0 中没有这条——所有队列层 CI、q 值与三态标签都建立在这个未披露的偏离上。
此外，"预测区间排除 1 且 I²<75%"这一新判据是**结果之后**提出的，75% 阈值既未预注册也无引用，作者自己的
脚本 docstring 写着 "upgrade for a **10+ IF target**"，而该事后判据却被写进摘要的 Results 与结论
——这是教科书式的 HARKing。方法学上有可修复的硬 bug（powered-null 实现与表头定义相反、E-value 把 OR
当 RR、k=2 仍报预测区间且用 z 而非 t），也有不可修复的表述（"地区反转"需重写为"跨国异质、且欧洲内部即冲突"）。

**投票：拒稿（Reject）。** 核心定量主张需重做、标题分母需更正、预注册判据需降格为探索性分析；
若编辑倾向给机会，上限是"大修"（Major revision），但需以新稿形态重投，因为摘要、标题与结论的
结论方向会实质改变。

**本轮发现：致命 3 项、重大 17 项、次要 14 项、需澄清 8 项；数字对账中"不一致"28 处、
另有 2 处数值可追但口径冲突、2 处出处不明，以及 5 项因材料不足不可核验（见文末附）。**

---

## 方法学审计

### 一、三连问逐条回答

**Q1. Primary outcome 是什么？**
**答：稿件没有声明单一 primary outcome，这是一个真实的设计缺陷。**

- 稿件实际给出了**三个平行的"主结果"**：(i) 内部层（NHANES/KNHANES/CHARLS）的
  declared-domain / conservative precision（Table 3、Figure 3）；(ii) 队列层的三态构成与
  "transportable" 判据（Table 4/5、Figure 8）；(iii) 系统性能 F1（Figure 2）。Methods 未指明
  哪一个是一级终点，也未说明多重性如何在**这三族之间**控制。
- 更具体的口径缺陷：队列层唯一的"规则级判定"是**三态标签**，而三态由 `q_primary < 0.05` 驱动；
  但三态的**分母**（"可检验规则对"）在稿件内部有 **四套**不同数字：Table 3/4 的 16/15、
  Figure 3 的 19/16、Figure 7 的 17/13、`power_summary.json` 的 19/16，且 Results 的 "17 of 30"
  分母 30 与上述任何一个都不吻合（Table 4 合计 31，power_summary 合计 35）。
  primary outcome 未定义 + 分母四套 = 读者无法复现任何 headline。
- 另外，队列层真正的 clinically interpretable 终点（"该规则能否在新人群使用"）在稿件中被两个
  **不一致**的判据同时定义（预注册判据 vs 事后判据），见"方法学质疑"一节。
- **建议**：明确声明 primary = 预注册的 transportability 判据（replicated with q<0.05 in ≥2 cohorts），
  其余全部标为 secondary/exploratory；并给出一个唯一的、跨图表一致的分母定义
  （建议 "assessable pre-registered (rule × cohort) pairs"，并单列 excluded/not-assessable 计数）。

**Q2. 样本量/效能怎么算的？**
**答：没有先验样本量计算；效能是事后逐对 MDE，且实现有两处硬错误。**

- 队列层没有 a priori sample size 或 power 计算（STROBE item 10 缺项）。`docs/analysis_plan.md` §19
  也未规定效能目标；`cohort_power.py` 是在结果之后（R11/§17 之后）补做的。
- 效能方法本身可接受：`MDE = exp((z_{0.975}+z_{0.80})·SE)`，p0 由未暴露者事件率给出。
  但：
  1. **分母错误**：`cohort_power.py` 直接从 `data/frames/cohort_*.csv` 取 `len(dropna())`。
     SHARE frame 每个 person-wave 有 5 个插补副本，因此 SHARE 的 n 是分析样本的 **5 倍**：
     `cohort_rule_results.csv` 的 SHARE r02 n = 337,274，而 Table 6 写 **1,686,370**（= 337,274×5）；
     r10 142,084→710,420；r12 123,478→617,390；r13 337,274→1,686,370；r20 142,229→711,145（均为精确 5×）。
     MDE 随 √n 缩小，故 SHARE 的 MDE 被系统性低估（如 r02：报 1.024，按真实 n≈1.055）。
  2. **"powered null" 的实现与定义相反**：`cohort_power.py` L84–85 写的是
     `powered = r.ci_high < m if r.odds_ratio < 1 else r.ci_low > m`。
     对 OR>1，要求 **CI 下限 > MDE**（即整个区间在 MDE 之上，是一个显著的阳性结果），
     与脚本 docstring（"the upper bound of its own CI excludes the MDE"）和 Table 6 表头
     （"A pair is a POWERED NULL when its confidence interval excludes its own MDE"）**相反**。
     直接后果：CLHLS r20（MDE 1.2127，CI 0.8736–1.2066，CI 上限 1.2066 < MDE）按表头定义
     **应为 powered_null = True**，落盘为 False；因此 "5 of 8 (62.5%)" 应为 **6 of 8 (75%)**。
     而稿件同一段紧接着写 "CLHLS r20 **was powered** for a 1.21-fold association and observed 1.03"
     —— 正文与其自己的 Table 6 标签自相矛盾。
- 另：MDE 公式在 p1 = p0 处求 SE，忽略备择假设下的方差，会低估 SE → 低估 MDE → 高估效能。
  这是常见近似，但既未声明也未做敏感性。
- **建议**：重跑效能（去重插补副本、按分析 n）、修正 powered-null 逻辑使其与定义一致、
  在 p1 取备择值下重算 MDE 并双呈、把 "5 of 8" 更正为 6 of 8，并删除与标签冲突的正文表述。

**Q3. 多重比较校正了吗？**
**答：校正了，但口径存疑且缺一处关键敏感性。**

- 实现为 `fdr_bhy`（Benjamini–Yekutieli，c(n)=Σ1/i，`cohort_confirmatory.py` L78–90），
  确证家族 = 18 个 (rule × cohort) 对（`q_rule`），探索家族 = 全部 tested 对（`q`）。
  这与 `analysis_plan.md` §19.7 的"双家族 BHY"一致。
- 问题一（**重大**）：BY 在 n=18 时 c(n)=3.495，把 q 抬到 p 的 3.5 倍。CRELES r02 的
  p = 0.008845、q_primary = 0.050585 —— **恰好卡在 0.05 之外**。若用 Benjamini–Hochberg，
  q ≈ 0.0145 < 0.05，CRELES r02 将判为 **replicated**，r02 由 "3 of 4 cohorts" 变为 **4 of 4**。
  稿件的 "CRELES ... falling just short (q = 0.051)" 与 "replicated in three of four" 因此
  完全取决于 BY vs BH 的选择。18 个检验按队列分组、彼此近似独立，BY 的"任意依赖"假设
  在这里是**过度保守**的（方案 §7"每库内做 BHY"本身也偏向按库分组）。**必须报 BH 敏感性。**
- 问题二（次要）：`analysis_plan.md` §19.7 规定探索家族为"**各队列内**所有对"，
  实现是把所有队列 68 个对合并做一次 BHY（L251–255）。这是未记录的实现偏离
  （不影响 headline，因为 q_primary 用 q_rule，但方案纪律要求记录）。
- 问题三（**重大**）：三族（内部层指标、队列层三态、系统 F1）之间**没有**任何跨族校正，
  而稿件把它们并列为三个 headline 结论。
- **建议**：报 BY 与 BH 双结果；说明确证家族为何跨队列合并而非按库；明确三族的 family 边界。

### 二、STROBE 逐条对照（缺项清单）

稿件 Methods 写 "the observational cohort analyses follow STROBE [C003]"，但仓库中
**不存在任何 STROBE 清单文件**（全库检索 `*STROBE*` 无命中），且以下条目实质缺失：

| STROBE 条目 | 状态 | 具体缺陷 |
|---|---|---|
| 4 设计 | ✅ | 声明为回顾性多队列评估 |
| 5 场所/时间/招募期 | ❌ **缺** | 未给各队列的**数据采集年份与波次日期**；SHARE 4/5/6/7/9、ELSA wave 3、CLHLS 1998–2018 等只在 `analysis_plan.md` §19.3 出现，稿件正文未列 |
| 6 纳入排除（参与者） | ❌ **缺** | 无纳入/排除标准；"older adults" 未定义（年龄下限？是否 age≥45/50）；无排除标准 |
| 7 变量（暴露/结局/混杂/效应修饰） | ⚠️ 部分 | 混杂仅 age/sex；未说明为何不调整 SES/教育/收入（而 Discussion 又主张欧洲/亚洲 SES 分布差异可解释反转）；**暴露构念置换未声明**（见 M9） |
| 8 数据来源/测量 | ⚠️ 部分 | 未给具体问卷题号/编码；"codebook-verified" 不可复核 |
| 9 偏倚 | ⚠️ 部分 | 只谈了 ascertainment；**未讨论队列 frame 构建本身的选择偏倚**（如 MHAS frame 损坏、SHARE 5 副本堆叠） |
| 10 研究样本量 | ❌ **缺** | 无先验样本量/效能论证（效能为事后） |
| 11 定量变量处理 | ⚠️ 部分 | age 连续；BMI 切点已声明；其余连续暴露未说明 |
| 12a 统计方法 | ⚠️ 部分 | **未披露方差口径偏离预注册方案**（见 M7）；未说明为何用 BY 而非 BH |
| 12b 亚组/交互 | ❌ **缺陷** | 报告了"地区亚组差异"，但未说明所用的组内合并模型；事后判据被当作预注册呈现 |
| 12d 失访 | ❌ **缺** | 未报失访/未应答；重复波次的参与模式未描述 |
| 12e 缺失数据 | ❌ **缺** | 实现是 **complete-case**（`fit_one` 直接 `dropna`），稿件从未说明缺失处理、缺失比例或缺失机制；SHARE 之外无插补 |
| 13 参与者流程图 | ❌ **缺** | **无流程图**；无"每阶段人数 + 排除原因"；全文从未给出**参与者人数**（只有 person-wave 行数），且该行数本身错误（见 F1） |
| 14 描述性资料 | ❌ **缺** | **无 Table 1**（各队列年龄/性别/暴露/结局分布）；无缺失数 |
| 15 结局事件数 | ⚠️ 部分 | 仅效能表给出未暴露者结局率；各分析的事件数未报 |
| 16a 每个分析的人数 | ⚠️ 部分 | Table 6 给了 n，但 SHARE 的 n 错误（5 副本之和） |
| 16 未调整与调整估计 | ⚠️ 部分 | 只报调整后；无未调整估计 |
| 17 其他分析 | ⚠️ 部分 | 事后判据未标为事后（见 H1） |
| 19 局限 | ⚠️ 部分 | **遗漏了本轮全部关键局限**：无权重方差、插补副本计入分母、自报糖尿病代替高血糖、any AMD 代替 late AMD、事后判据、BY/BH 敏感性 |
| 21 可推广性 | ⚠️ 部分 | 只谈测量可得性 |
| 22 资金 | ❌ **缺** | 无 funding、无 competing interests、无 data/code availability、无伦理声明（`manuscript_R11.md` 曾有，现行稿全部丢失） |
| 注册号 | ❌ **缺** | 声称预注册但无注册平台/编号/时间戳产物（见 H2） |

**暴露与结局的测量时点（用户特别关注）**：稿件只写 "Most contributing waves are cross-sectional for the exposure"。
实际问题更重：队列层的主模型是**同一波次的 exposure×outcome 横断面关联**，结局是**患病**而非**发病**；
稿件却在 Discussion 用 "incidence cannot be separated from prevalent disease" 一句带过，
且**没有任何**测量时点表（哪个队列、哪个波次、暴露与结局是否同波）。这对一个
以"可迁移性"为论题的论文是结构性缺口——建议补一张 (rule × cohort × wave × exposure/outcome 是否同波) 表。

---

## 致命 / 重大 / 次要 / 需澄清

### 致命（Fatal）

**F1. 标题/摘要/正文的分母 "2.0 million person-waves" 高估 3 倍以上。**
- 位置：标题（L1 "in 2.0 million person-waves"）；Abstract Methods（L22）；Abstract Results（L27 隐含）；
  Methods L166–168；Results L327–329；Results "The eight cohorts together hold two million person-wave records"（L436）；
  Discussion L26–27、L205；Conclusion L693。
- 问题：`data/frames/cohort_SHARE.csv` 共 1,693,515 行，但 `implicat` 有 5 个水平、
  每水平恰 338,703 行，`uniq(mergeid, wave) = 338,703` —— SHARE 的 1,693,515 是
  **338,703 个 person-wave × 5 个插补副本**，不是一个独立的 person-wave 计数；
  作者自己的模型 n 也只有 337,274（`cohort_rule_results.csv`），与 1,693,515 差 5 倍。
  另：`cohort_MHAS.csv` 78,537 行，但 `uniq(mergeid, wave) = 15,213`，且 `mergeid` 列里出现
  "4.Fair"、"Good 3"、"3.Good"、"Fair 4" 这类**标签字符串**（4,789 行 mergeid 为 NaN），
  说明 MHAS frame 存在多对多连接膨胀（单组最多 6,447 行重复）。
- 为什么是问题：这是标题级数字。真实独立 person-wave ≈ **598,382**（各队列 uniq(mergeid,wave) 之和），
  真实参与者 ≈ **285,879**（`analysis_plan.md` §19.3 "人数"列之和）。标题里的 2.0 million 是错的，
  而且它恰是 Conclusion 的核心修辞（"eight cohorts hold two million person-wave records and still cannot…"）。
  此外 MHAS 贡献了 78,537 行却**没有产生任何分析对**（`cohort_rule_results.csv` 无 MHAS 行），
  把它计入"分析样本"也不成立。
- 修改建议：标题与全文改为真实口径，例如 "across eight ageing cohorts (598,382 person-wave observations;
  285,879 participants)"；明细表同时给"行数 / 独立 person-wave / 参与者 / 插补副本数"四列；
  修复 MHAS frame 的 mergeid 污染并重新出具行数。

**F2. 队列层核心结果偏离预注册方案 §19.7 的方差规定，且未记录偏离。**
- 位置：`docs/analysis_plan.md` §19.7（L555–556）；`scripts/cohort_confirmatory.py` L103–122；
  稿件 Methods L121–127。
- 问题：方案 §19.7 明确 "**方差**：SHARE 与 LASI 等带设计权重者用 survey 设计（strata/PSU/weights）；
  其余队列用聚类稳健方差"。实现对**所有**队列使用 `sm.GLM(...).fit(cov_type="cluster", groups=mergeid)`，
  **无权重、无 strata、无 PSU**；而八个 frame 里**根本不存在任何权重/PSU/strata 变量**
  （我逐一检查了列名：仅 CLHLS 有 `weight_kg`，那是体重）。方案 §19.9 规定
  "修改切点、协变量或判定阈值 → 必须记为偏离"，`§0` 中有更正 10–18，但**没有** §19 方差偏离的记录。
- 为什么是问题：论文的全部队列层估计、CI、q 值、三态标签与 transportability 判据都建立在这个方差口径上。
  SHARE（占分析记录 56%）与 LASI 是有设计权重的复杂抽样，忽略权重会同时偏移点估计与方差；
  多层模型里这是 JAMA 会直接退稿级别的口径问题。且稿件 Methods 只写"clustered by participant"，
  读者无法知道预注册方案要求的 survey 设计被替换了。
- 修改建议：两种路径任选其一并明示——(a) 补权重/PSU/strata 重建 SHARE、LASI（及可得队列）frame，
  按 §19.7 用 survey 设计重跑并报设计效应；(b) 若不可得，在 §0 补记偏离、在 Methods 与 Limitations
  显式声明"队列层使用无权重 cluster-robust 方差，与 §19.7 预注册口径不同"，
  并给出按可得权重（若任何队列有）的敏感性分析。任何情况下都不能继续沉默。

**F3. 主张 (b) "地区亚组差异 p<0.0001" 与"方向随地区反转"经独立重算不成立。**
- 位置：Abstract L28–30；Results L349–354、L387–390；Discussion L16–23、L36–38；Conclusion L193–195。
- 问题一（事实错误）：Results L353–354 写 "the single positive cohort is European while
  **all three protective cohorts are not**"。但 `cohort_heterogeneity.py` L49–51 的 REGION 映射中
  **ELSA = Europe**，而 ELSA 的 r10 OR = 0.7675（保护向）。所以三个保护向队列中
  **有两个在欧洲之外、一个在欧洲之内（ELSA）**；"保护向队列都不是欧洲的"是明确的与数据相反的陈述。
- 问题二（模型伪影）：亚组检验 `subgroup_diff()`（L144–162）在组内用 **w = 1/v 的固定效应**合并，
  完全忽略它正在检验的异质性（r10 的 I² = 91%）。其后果：Europe 池被 SHARE 主导
  （w_SHARE = 958.5、w_ELSA = 69.7，SHARE 占 93% 权重），"Europe 1.0817" 实际上是
  **SHARE 的估计被贴上欧洲标签**，ELSA 的保护向被吸收消失。
- 独立重算（我自己实现 REML + 组内随机效应，未用作者脚本）：
  | 量 | 作者交付（组内固定效应） | 我的重算（组内随机效应） |
  |---|---|---|
  | 亚组 OR（Americas / Asia / Europe） | 0.702 / 0.748 / **1.0817** | 0.702 / 0.748 / **0.939** |
  | Q_between (df=2) | **24.61** | **1.59** |
  | p_between | **4.53 × 10⁻⁶** | **0.451** |
  同一重算下 r02 由 p=0.00041 变 p=0.011、r20 由 8.99e-13 变 2.86e-09 —— 只有 r10 **翻转为不显著**。
- 为什么是问题：r10 是全文两个"未迁移"例证之一，是 Abstract 的第二个 headline，
  是 Discussion 整节（"The direction reversal, and what could explain it"）的立足点，也是标题
  "Pooling conceals directional conflict" 的经验依据。现在：(i) 反转并非地区性的（欧洲内部即冲突：
  SHARE 1.11 vs ELSA 0.77）；(ii) 地区差异统计上不显著（p=0.45）。
  "the regional subgroups differ significantly (Europe 1.08 versus Asia 0.75 and the Americas 0.70, p<0.0001)"
  这一句必须删除或彻底重写。
- 修改建议：(a) 亚组检验改为组内随机效应（或直接报告各队列估计、放弃合并亚组）；(b) 删除所有
  "regional"/"by region" 的因果-地理框架，改为 "between-cohort heterogeneity including within-Europe
  disagreement"；(c) 明确报告 ELSA 的欧洲身份与保护向，并讨论"欧洲内部即冲突"对
  "选择存活/混杂/真实效应修饰"三种解释的含义（此时第三种解释的相对权重上升）；
  (d) 重写 Abstract、Discussion 第 1–2 节与 Conclusion。

### 重大（Major）

**M1. HARKing：事后提出的 "PI 排除 1 且 I²<75%" 判据被写进摘要与结论。**
- 位置：Abstract L26–27、L32–33；Results L394–399；Discussion L106–121、L188–197；
  `scripts/cohort_heterogeneity.py` L280–303。
- 问题：`analysis_plan.md` §19 **完全没有**异质性感知判据、没有预测区间判据、没有 I² 阈值
  （我通读 §19.1–19.10 确认）。75% 硬编码在 `cohort_heterogeneity.py` L299
  （`hi_i2 = rep["I2_percent"] >= 75.0`），无引用、无预注册。脚本自己的注释承认这是事后加的：
  "This adds a second, stricter reading, **because the pre-registered rule turns out to be too permissive**"；
  脚本 docstring 第一行更直白：**"Formal heterogeneity analysis of the cohort layer (upgrade for a 10+ IF target)."**
  该脚本还先读取结果文件 `cohort_transportability.json`（L189–192）再定义"预注册"一侧，
  时序上不可能先于结果。稿件 Discussion 说 "heterogeneity to be below **a declared threshold**"，
  但阈值从未被 declared（只在 Results/Discussion 出现"75%"），且它是**事后**阈值。
- 为什么是问题：Abstract 的 "so under a criterion also requiring tolerable heterogeneity **no rule was
  reliably transportable**" 与 Conclusion 的 "none was reliably transportable" 是论文最主要的"结论"，
  而这个结论由事后判据产生。这是 HARKing 的定义性特征，JAMA 会要求删除或彻底降格。
- 修改建议：(a) 预注册判据保持 primary、结论以其为准；(b) 事后判据明确标注
  "post hoc, not pre-specified, added after observing the results"，只放在 Sensitivity/Exploratory；
  (c) 75% 要么引用 Cochrane Handbook 的 "considerable heterogeneity" 惯例并声明为惯例而非预注册，
  要么在 v1.3 方案中前瞻性预注册并在新数据上检验；(d) Abstract/Conclusion 不得以事后判据下结论。

**M2. "powered null" 的计数与正文自相矛盾（5/8 vs 6/8）。**
- 位置：Results L465–474；Discussion Limitations L173；Table 6 表头与 CLHLS r20 行；
  `scripts/cohort_power.py` L84–85。
- 问题：见"三连问 Q2"。按 Table 6 自己的定义，CLHLS r20 应为 powered_null = True
  （CI 上限 1.2066 < MDE 1.2127），落盘为 False，故 "5 (62.5%)" 应为 **6 (75%)**；
  而正文同一段又写 "CLHLS r20 **was powered** for a 1.21-fold association"。
- 为什么是问题：这是作者为所有阴性结果辩护的核心论证（"负结果多数是有信息的"）。
  计数与定义不一致会让整个效能段落失去可信度。
- 修改建议：修正 `cohort_power.py` 的判据（对 OR<1 用 CI 上限 < MDE、对 OR>1 用 CI 上限 < MDE
  在 OR 尺度上等价于 CI 下限 > 1/MDE），重跑，并把 Results/Discussion/Table 6 统一为同一数字。

**M3. Table 6 的 n 列不是分析样本量（SHARE 为 5 个插补副本之和）。**
- 位置：Table 6（`outputs/tables/table6_power.md`）SHARE 五行。
- 问题：SHARE r02/r13 n=1,686,370、r10 710,420、r12 617,390、r20 711,145，均为
  `cohort_rule_results.csv` 中每副本分析 n 的**精确 5 倍**。表头写 "from the **analysed n** and observed
  margins"，与事实不符。
- 为什么是问题：读者会据此判断效能；同时它又把 F1 的"2.0M"讹误在表内复现一遍。
- 修改建议：n 改为分析样本量（每副本），另加 "n_imputation_replicates = 5" 列；MDE 相应重算。

**M4. E-value 把 OR 直接当 RR 代入 VanderWeele 公式，r02 的 E-value 高估约 47%。**
- 位置：Results L405–410；Discussion L56–63；Table 5 脚注 E-values；`cohort_heterogeneity.py` L165–175。
- 问题：`e_value()` 直接 `ev(est)` 其中 `est` 是 odds_ratio，公式 `rr + sqrt(rr(rr-1))` 是
  **风险比**的 E-value（VanderWeele & Ding, Ann Intern Med 2017）。该队列层的结局并不罕见
  （CLHLS 未暴露者白内障 17.8%、CRELES 39.9%、SHARE 8.8%），因此 OR 会放大与 1 的距离，
  E-value 被系统性高估。按精确 RR 换算 `RR = OR/(1-p0+p0·OR)`（p0 取 `cohort_power.csv`
  的 outcome_prevalence_unexposed）：

  | 估计 | 稿件 E-value | RR 换算后 | 偏差 |
  |---|---|---|---|
  | r10 @CLHLS（OR 0.748, p0=0.178） | 2.01 (1.57) | **1.87 (1.50)** | +7% |
  | r10 @SHARE（OR 1.109, p0=0.088） | 1.46 (1.25) | **1.43 (1.23)** | +2% |
  | r12 @CLHLS（OR 0.809, p0=0.211） | 1.78 (1.36) | **1.66 (1.31)** | +7% |
  | r02 @CLHLS（OR 3.589, p0=0.161） | 6.64 (4.69) | **4.51 (3.58)** | **+47%** |

  （若用 VanderWeele 对常见结局推荐的 `RR ≈ sqrt(OR)` 近似，数值更低：1.58 / 1.29 / 1.50 / 3.20。）
- 为什么是问题：Discussion 用 "a risk ratio of roughly **1.5 to 2** would suffice" 来描述脆弱性，
  真实门槛约 1.4–1.9；而 r02 "not fragile in the same way"（6.64）在正确换算后是 4.51，
  对比被夸大。E-value 是本文唯一的定量偏倚分析，口径错误不能留。
- 修改建议：显式声明所使用的 OR→RR 换算（并引用 VanderWeele & Ding 2017 / Mathur & VanderWeele 2020），
  重算四个 E-value，并同步修正 Discussion 的 "1.5 to 2" 与 "not fragile" 表述。

**M5. k=2–5 的 τ² 不可识别一事，只在脚本里说了，稿件里没说；且 k=2 仍报预测区间与"地区 p"。**
- 位置：Methods L22–23、L240–260；Results Table 5（r12、r13 行）；Discussion L91–99；
  `cohort_heterogeneity.py` L69–98 的 docstring。
- 问题：脚本 docstring 明确写 "With only 2-5 cohorts **tau^2 is poorly identified regardless of estimator**；
  the reported inference therefore leans on Cochran's Q and I^2"；稿件 Methods 只写
  "random-effects pooling (REML τ², Cochran's Q, I²)"，Table 5 脚注只写 "no external meta-analysis
  package was used"。**没有任何一句提示 τ² 在 k=2–5 下不可识别**，也没有提示 k=2 的
  prediction interval 在统计上几乎无信息（τ² 由 1 个自由度估计）。更糟的是 r12、r13（k=2）
  还被给出 "Regional subgroup difference p = 0.027" —— 而这与总 Q 检验**恒等**
  （Q_between = Q = 4.87 / 4.877，df=1，因为 2 个队列恰好 2 个"地区"），属重复计数，
  读者会误以为得到了一个独立的地区证据。
- 另一处口径问题：预测区间用 1.96（z）而非 t_{k−2}（`cohort_heterogeneity.py` L128）。
  k=2 时 t=12.71，正确 PI 近乎无界；用 z 使 r12/r13 的 PI（0.68–1.17、0.80–1.62）**严重偏窄**。
  对 k=4 也偏窄（我的重算：r02 PI 用 t₂ 为 0.30–12.63，而稿件报 0.84–4.57）。
- 为什么是问题：论文的核心论证之一是"所有预测区间都跨 1"。结论方向不受影响（t 更宽），
  但"预测区间"这一方法在 k=2–5 下的报告方式必须诚实；否则读者会以为得到一个精确的区间。
- 修改建议：(a) Methods 与 Table 5 脚注加一句"τ² 在 k≤5 下识别不良，PI 应视为粗略上界"；
  (b) 用 t_{k−2} 重算所有 PI 并双呈（z 与 t）；(c) 删掉 r12/r13 的"地区亚组差异"行，
  或明确注明"k=2 时该检验与总 Q 检验等价"；(d) 不应对 k=1 的 r11 讨论"可迁移性"。

**M6. 预测区间跨 1 → "不可迁移"的推论过强（用户特别关注）。**
- 位置：Results L376–377、L391–399；Discussion L500–502、L603–609；Abstract L26–27；Conclusion L191–193。
- 问题（推理层面）：PI 跨 1 的严格含义是"在抽取新人群时，其**平均效应**落在包含 1 的区间内"，
  即**不能排除无效**，而不是"该规则在新人群无效/不可迁移"。稿件从 "a new cohort could plausibly
  show no association"（这一句是对的）跳到 "**none of the six testable rules was reliably
  transportable**"（结论过强）。理由：
  1. r20 在 5/5 队列方向一致（1.0267–1.6144），方向一致性本身是关于"是否存在关联"的证据，
     而 PI 只谈效应量的分布；稿件把"效应量可预测性不足"等同于"关联不可迁移"。
  2. 对 k=2（r12、r13）PI 跨越 1 是**必然**的（τ² 只有 1 df，t 区间近乎无界）——这没有证据力，
     却被计入 "every prediction interval includes the null"。
  3. 判据 (PI 排除 1 **且** I²<75%) 在 k≤5 且真实异质时几乎不可能通过，属**不可证伪的严格性**；
     "0/6 通过"部分是判据构造的结果，而不是关于世界的发现。
  4. r11 只有 1 个队列，谈不上"可迁移性"判定，却被计入"六条规则无一条可靠可迁移"。
- 修改建议：把结论改为分级表述，例如"在预注册判据下 2/6 可迁移；加入事后异质性判据后 0/6，
  但 PI 在 k≤5 下只能给出粗略上界，且该判据在 k=2 时不具区分度"；删去把 PI 结果等同于
  "不可迁移"的句子；在 Abstract 中明确 r11 不可判。

**M7. 暴露/结局构念置换未在稿件中声明（hyperglycaemia←自报 diabetes；late AMD←any AMD）。**
- 位置：Methods L209–212（"Construct shifts were declared"）；Results L341–347（称 r02 为
  "hyperglycaemia → cataract"）；Results L360–364、Table 5（称 r11 为 "smoking → late AMD"）；
  出处：`cohort_rule_coverage.json`（r02 的 `exposure_col = "diabetes"`；r11 的
  `outcome_flag="amd_late"` 但 `outcome_col="amd_any"`）；`cohort_confirmatory.py` L62–75
  （`"amd_late": ["amd_any"]`、`"hyperglycemia": ["diabetes"]`）。
- 问题：r02 的预注册暴露 flag 是 `hyperglycemia` / `hba1c_elevated`，队列层实际用**自报医生诊断糖尿病**
  代替。CLHLS 该暴露患病率 1.29%（`cohort_power.csv`），而 `analysis_plan.md` §19.4.2 自己写
  该变量实测 1.36%，远低于以测量为主的参考带——即暴露被严重低报。而 r02 恰是 CLHLS 给出最大
  OR（3.59）的规则，也是两条"可迁移"规则之一。r11 的规则声明是 late AMD，实际检验的是
  **any AMD**（含早期），这直接影响"powered null"的解释（对 late AMD 的效应会被早期 AMD 稀释）。
- 为什么是问题：论文的卖点之一是"构念纪律"（cataract surgery ≠ cataract、self-report ≠ measured）。
  但在**暴露侧与 AMD 侧**恰恰做了它自己禁止的构念替换，且未声明。这是选择性的构念纪律。
- 修改建议：在 Methods 与 Results 显式声明这两处操作化及理由；r02 全文改称
  "self-reported diabetes → cataract"并在 Limitations 讨论低报偏倚方向；
  r11 的结局改为 "any AMD (ELSA)",或说明为何可作为 late AMD 的替代并给出方向性偏倚预期。

**M8. 摘要与正文/表格的数字不一致（用户特别要求点名）。**
- (a) r02 合并 CI：Abstract L24 与 Results 表 L381 写 **1.33–2.88**；Table 5（L1036）与
  `cohort_heterogeneity.json`（pooled_ci [1.3245, 2.8828]）为 **1.32**。（本节另见"数字修正清单"）
- (b) r13 合并 OR：Results 表 L385 写 **1.14**；Table 5（L1040）与源文件（pooled_OR 1.1349）为 **1.13**。
- (c) 年龄 meta-regression 的 p 范围：Abstract L31 写 "p = 0.42–0.52"；正文 L403 写
  "p = 0.42, 0.52 and 0.35"，源文件为 0.4178 / 0.5169 / **0.3472**。摘要遗漏了 0.35，
  使区间看起来比实际更好。
- 为什么是问题：JAMA 会逐字核对摘要与正文；摘要数字与主表冲突是可直接退稿的编辑问题。
- 修改建议：以落盘源文件为准统一三处（1.32、1.13、0.35–0.52）。

**M9. 系统性能的 ±SD 取自另一套金标准（R5 而非 R11）。**
- 位置：Results L478–482；Figure 2 图注 L719；中文图注 L834–836。
- 问题：稿件写 "pure LLM **0.301 ± 0.017** and naive RAG **0.080 ± 0.089**"。
  `baseline_summary_R11_corrected_gold.json` 的 R11 金标准逐种子 F1 为
  pure_llm [0.324,0.286,0.286,0.324,0.286]（均值 0.301 ✓，总体 SD = **0.019**）、
  naive_rag [0.2,0,0,0.2,0]（均值 0.080 ✓，总体 SD = **0.098**）。
  0.017 与 0.089 分别是 **R5 金标准**下 [0.368/0.333…] 与 [0.182/0…] 的 SD（0.01715、0.0892）。
  即均值取 R11 口径、SD 取 R5 口径。
- 为什么是问题：Methods 明确写 "v1.1 replay ... on the R5 gold and is **labelled as such**"，
  说明作者知道两套金标准不可混用；这里却混用了，且混在同一句里。
- 修改建议：统一为 R11 口径（0.301 ± 0.019、0.080 ± 0.098），或在表中同时列出两套金标准。

**M10. Figure 2 图注声称源 CSV 含 v1.1 replay 行；实际不含。**
- 位置：Figure 2 图注 L719（"that bar is **shown** for the mandatory dual report"）、
  L721（"A separately labelled row for full_system_v1.1_replay (0.111) **is present in the source CSV**"）、
  中文图注 L840/L843。
- 问题：`outputs/figures/source_data/figure2_performance.csv` 仅 21 行（4 方法 × 5 种子 −1），
  **没有任何 v1.1 replay 行**。而 `outputs/paper/figure_legends.md`（同项目另一份图注）
  写的是相反的、正确的内容："The pre-expansion v1.1 ruleset is **NOT plotted here** ...
  its source row **is not** in this figure's source CSV."
- 为什么是问题：图注描述与图的实际内容不一致，且项目内两份图注互相矛盾（见"需澄清"）。
- 修改建议：以 `figure_legends.md` 的表述为准，删除"shown / present in the source CSV"。

**M11. Figure 8 图注的 "13 rules" 与自身分解式矛盾（应为 15）。**
- 位置：Figure 8 统计说明 L807（英文）与 L956（中文）。
- 问题：图注写 "**13** rules have no bar at all: 5 need fundus imaging, 1 needs tonometry/optic-disc
  grading, 3 need geocoded exposure, 3 need blood assays, 2 need **dietary indices**"。
  5+1+3+3+2 = **14** ≠ 13；而实际不可检验规则数 = 21 − 6 = **15**（Results 正文 L333–337 正确列为 15，
  含 r05 需血脂）。原因是 r07、r19 同时属 fundus 与 blood/dietary，被重复计入分类而漏计 r05。
- 修改建议：改为 "15 rules have no bar"，并给出互斥分解（例如把 r05 单列为脂质面板需求）。

**M12. "self-rated vision impairment (all eight)" 与实测不符（实为 7/8）。**
- 位置：Methods L217–219。
- 问题：`cohort_rule_coverage.json` 的 CRELES `flags_present` **不含** `vision_impairment_moderate/severe`
  （只有 `blindness_selfreport`、`uses_glasses`），与 `analysis_plan.md` §19.4.5 一致（CRELES 视力不可用）。
  因此"八个队列都有自评视力损害"是错的，应为七个；CRELES 的 `r20` 也确实不可测（
  `cohort_rule_coverage.json` r20@CRELES `testable: false`）。
- 修改建议：改为"(seven cohorts; CRELES contributed no vision outcome)"。

**M13. Discussion "With I² of 90–94% across every multi-cohort rule" 与 Table 5 冲突。**
- 位置：Discussion L91–92（`sections/discussion.md` L91）。
- 问题：r12 与 r13 的 I² = **79.5%**（`cohort_heterogeneity.json`、Table 5）。"every multi-cohort rule"
  与数据不符，且这里是用于支撑"异质性大到不能合并"的论证。
- 修改建议：改为 "79.5–93.8%（median …）"或明确"the three rules with k≥4 had I²>90%"。

**M14. "Leave-one-cohort-out ... not produced by any single cohort" 与影响分析结果冲突。**
- 位置：Results L411–412；Discussion L98–99、L587。
- 问题：`cohort_influence.csv` 显示 r10 去掉 **SHARE** 后合并 OR = **0.747**、**I² = 0.0**、tau² = 0
  ——即去掉 SHARE 后 r10 变成"一致的保护向、无异质性"；去掉其他任一个队列则 pooled ≈ 0.856–0.872、I² 86.6–93.0%。
  也就是说 r10 的"混合/冲突"结论**正是由 SHARE 单库驱动的**。稿件却写"没有任何单一队列造成这个模式"。
- 为什么是问题：这是对自家影响分析的误读，且方向恰好相反（该分析其实支持"SHARE 是异质性的来源"）。
- 修改建议：如实报告"removing SHARE removes the heterogeneity entirely (pooled OR 0.75, I² = 0%)"，
  并讨论其对"欧洲内部冲突"解读的含义（与 F3 相互印证）。

**M15. 探索性关联全部缺 CI。**
- 位置：Results L441–449。
- 问题：KLoSA OR 1.50 / 1.99、SHARE 1.46、LASI 1.64 (q=1.2e-10)、HRS 1.98 (q=8.1e-20) —— 均只给 OR 与 q，
  **无一给出 95% CI**（我已在 `cohort_rule_results.csv` 核到对应行，CI 均存在但未报）。
- 为什么是问题：用户/期刊对 effect size 的硬要求是必须带 CI；探索性结果也不例外。
- 修改建议：为这五处补 CI（源文件已有 `ci_low`/`ci_high`）。

**M16. "rule-relevant pairs" 的分母在稿内有四套值，且 "17 of 30" 的分母无出处。**
- 位置：Table 3/4（16 / 15）；Figure 3 图注 L731（19 / 16）；Figure 7 图注 L791/L919（17 / 13）；
  Results L455–457（"17 of 30"）；`power_summary.json`（19 / 16）。
- 问题：同一概念（rule-relevant testable pairs）取值 15/16/17/19。核到源头：
  `headline_sensitivity.csv` 的 "all_rules (current)" = 19（NHANES）/16（KNHANES）；
  `power_analysis_nhanes.csv` 中 `predicted=True` = 19、`power_analysis_knhanes.csv` = 16；
  `figure7_power_mde.csv` 只有 30 行（NHANES 17 + KNHANES 13），比 power 源文件**少 5 行**
  （= power_summary 的 `not_assessable` 2 + 3），图注未说明剔除；
  而 Table 3/4 的 16/15 又排除了 r01/r22（NHANES 19−3=16；KNHANES 16−1=15，
  但两库的排除规则并不一致：`headline_sensitivity.csv` 显示 NHANES 主表=exclude_both，
  KNHANES 主表=exclude_r01）。
- 为什么是问题：headline 计数无法复现；且 NHANES 的 "all_rules 19" 大于 `analysis_plan.md` §0.4
  声明的规则对总数 18，说明口径本身对不上。
- 修改建议：定义唯一分母并写进 Methods；图注列出被剔除的对（r01 阴控、r22 测试集泄漏、
  not_assessable）；说明两库排除规则不一致的原因。

**M17. 缺失全部声明性章节（伦理/数据可得性/资金/利益冲突/注册号/作者贡献）。**
- 位置：现行 `outputs/paper/manuscript.md` 全文（对比 `outputs/paper/manuscript_R11.md` L250–258 曾经有）。
- 问题：现行稿没有 Ethics、Data availability、Code availability、Funding、Competing interests、
  也没有预注册登记号或方案版本/日期。Methods 却断言 "pre-registered ... (analysis plan §19)"。
- 为什么是问题：STROBE item 22 与 JAMA 投稿硬要求；且"预注册"无编号不可核验（见 C2）。
- 修改建议：补齐全部声明；给出登记号或时间戳化产物（哈希/commit）以支撑预注册主张。

### 次要（Minor）

**m1. Figure 8 图注关于"区间跨 1"的描述错误。** L805 写 "Rows whose interval crosses 1 ...
(r10 in ELSA and CRELES, r12 in SHARE)"。实核：ELSA r10 CI 0.6069–0.9705、CRELES r10 CI 0.5021–0.9822，
**都排除 1**；它们被判 uninformative 是因为 BY 校正后 q ≥ 0.05，而非区间跨 1。仅 SHARE r12
（0.8999–1.0301）确实跨 1。建议更正并说明"uninformative 由 q 决定，不由 CI 决定"。

**m2. Table 3 的 `pairs_tested` 列为空。** `performance_matrix.csv` 该列即空，Table 3 原样复制。
建议填入 180/352/14 或删除该列。

**m3. "Benjamini–Hochberg–Yekutieli" 命名错误。** Results L286、Figure 3 缩写表 L737。
实现是 Benjamini–Yekutieli（`fdr_bhy` 用 c(n)=Σ1/i），Methods L250 写对了。建议全文统一为 BY。

**m4. "the sensitivity analysis (Table 3) reports four alternative rule sets"。** L312–314。
(i) 表号错（Table 3 是 performance matrix，不是敏感性表）；(ii) `headline_sensitivity.csv` 每库有
6 个备择规则集（exclude_r22 / exclude_r01 / exclude_both / A_only / A+B / exclude_C），非"四个"。

**m5. r12/r13 的"地区亚组差异"重复计数。** Table 5 的 "Regional p" 对 r12 (0.0273)、r13 (0.0272)
与同表 "Q p" 完全相同，因为 k=2 时两组 = 两队列。（与 M5 同源）

**m6. Discussion "the two protective cohorts" 实为三个。** L540（`sections/discussion.md` L52）：
CLHLS 92.0、CRELES 76.7、ELSA 64.9。

**m7. "the ELSA glaucoma and AMD items are the only sources in the layer"。** Discussion L667–668。
`cohort_rule_coverage.json` 显示 `glaucoma_selfreport` 存在于 CLHLS、CRELES、ELSA、HRS、LASI 五个队列，
并非只有 ELSA。建议改为 "ELSA is the only source of a graded AMD item"。

**m8. `performance_by_dataset.csv` 的 CI 注记与列值不符。** 该文件 NHANES 行 `ci_lo/ci_hi`=0.541/1.0，
  但 `ci_note` 写 "[0.478, 1.00]"（KNHANES 的数）；KNHANES 行 `ci_lo`=0.478 而 note 写 "[0.158, 1.00]"。
  交付数据自相矛盾，建议修正注记。

**m9. 探索性 FDR 家族实现为跨队列合并。** `cohort_confirmatory.py` L251–255 对全部 68 个对做一次 BHY，
  而 §19.7 规定"各队列内"。属未记录的实现偏离（不影响 headline）。建议补记于 §0。

**m10. Table 2 中 r22 的 `risk_type = inflammation_immune`。** BMI×视网膜病变应为代谢类
  （与 r13 的 `glycation_metabolic` 一致）；`table2_rules.md`/`registry_summary` 同错。

**m11. `analysis_plan.md` 内部不一致。** §0.2 更正 6 写 "CHARLS coverage 0.667→**0.308**"，
  §0.4 表写 CHARLS 2011 coverage **1.000**；稿件 Table 3 用 1.0。建议标注 §0.2 该数字已被 §0.4 取代。

**m12. "CRELES ... its r02 interval only just includes unity (1.07, against an MDE of 1.23)"。** L469–470。
  CRELES r02 的 CI 是 1.0705–1.6069，**不包含 1**；应改为"下限 1.07 与 1 的距离仅略大于 0"或直接说
  "q = 0.051 just misses the threshold"。

**m13. 稿件从未报告参与者人数（只报行数）。** 与 F1 同源；STROBE 13/14 要求。

**m14. "two precision denominators are reported and are never interchanged" 一句不成立。**
  Figure 3 图注同时给出"保守精确率 0.375 (分母 16)"与"all rules 6/19 = 0.316"，
  两者分子相同、分母不同，却并列呈现且未解释差异（0.375 vs 0.316 会被读成矛盾）。
  建议在图注中显式写出两套分母的构成。

### 需澄清（Clarification）

**C1. "110 NHANES pairs" 与 "56 KNHANES pairs" 的口径。** Results L296–298。
唯一出处是 `outputs/tables/dataset_summary.csv`（`n_cases` = 110 / 56），
但同稿 Table 4 写 NHANES 180 对、KNHANES 352 对，`nhanes_confirmatory.csv` 实为 180 行、
`knhanes_confirmatory.csv` 实为 352 行。请说明 110/56 是什么（legacy target？registry 子集？），
或删除。

**C2. 预注册不可核验。** 稿件断言 §19 在建模前落盘，但仓库内无 git 快照/登记号；
  `analysis_plan.md` 对 §12、§13、§15 都做了"时序无独立可证证据，降格披露"的诚实声明，
  **唯独 §19 没有**。请补同类披露或提供可验证锚点（方案文件哈希、commit、OSF 编号）。

**C3. r11 的 verdict 在两份交付物中冲突。** `cohort_transportability.json` 给 `r11 → "mixed"`；
  `cohort_heterogeneity.json` 给 `r11 → pre_registered: "single_cohort"`，且后者声称
  "pre_registered_verdict_source: cohort_transportability.json"（实际是 `cohort_heterogeneity.py` L293
  硬编码的）。同时 "mixed" 并非 §19.7 三态判据（transportable / single_cohort / non_transportable）之一
  ——它是 `cohort_confirmatory.py` L282 的 else 分支。请统一并说明新增第四态的依据。

**C4. CLHLS 均龄 92.0 的出处。** 只在 `cohort_heterogeneity.py` L55 的 `MEAN_AGE` 硬编码
  （注释称来自 `docs/cohort_variable_mapping` §0.14），没有任何结果文件承载；而它是 meta-regression
  唯一的 moderator。请提供由 frame 计算的、可复现的队列均龄表。

**C5. MHAS 的地位。** 摘要/正文把 MHAS 列为八个分析队列之一，但 `cohort_rule_results.csv`
  没有任何 MHAS 行（0 个分析对），且其 frame 的 mergeid 被标签字符串污染。请说明 MHAS 实际贡献了什么；
  若为零，应从"分析样本"叙述中移出（这同时减轻 F1）。

**C6. 两套图注文件相反。** `outputs/paper/manuscript.md` 的 Figure 2 图注 vs
  `outputs/paper/figure_legends.md`：前者说 v1.1 replay 柱"shown / present in source CSV"，
  后者说"NOT plotted / not in the source CSV"。请确认哪一份是投稿版并删除另一份。

**C7. BY 阈值稳健性。** CRELES r02 的 q = 0.0506 决定 "3 of 4"。请提供 BH 敏感性
  （q ≈ 0.0145）与"若 r02 为 4/4 则结论如何变化"的分析。

**C8. NHANES "all_rules 19" 与规则宇宙 18 的关系。** `analysis_plan.md` §0.4 写 NHANES
  rule pairs = 18、tested = 16；`headline_sensitivity.csv` 的 "all_rules (current)" = 19。
  19 > 18 需要解释（是否含阴控 r01？）。

---

## 数据一致性核查总表

判定口径：【一致】= 稿件值与落盘源文件在该精度下相同；【不一致】= 数值或事实冲突；
【出处不明】= 提供的材料中无对应上游数字；【不一致-口径】= 数值可追但口径/分母与另一处冲突。

### A. 摘要

| 位置 | 稿件数值 | 原始出处 | 判定 | 备注 |
|---|---|---|---|---|
| Abstract L22 | 2.0 million person-wave records | `data/frames/*` 行数合计 2,016,518；但 SHARE 5×插补副本、MHAS 连接膨胀 | **不一致** | 真实独立 person-wave ≈598,382；参与者 ≈285,879 |
| Abstract L25 | 168 possible (rule × cohort) tests | `evidence_audit.json` possible_cells 168 | 一致 | 21×8 |
| Abstract L27 | 18/168 cells (10.7%) | `evidence_audit.json` 18 / 0.1071 | 一致 | |
| Abstract L27 | six of 21 rules testable | `evidence_audit.json` 6 / 21 | 一致 | |
| Abstract L28 | 18 analysed pairs, 8 rep / 8 uninf / 2 con | `cohort_rule_results.csv` rule_relevant=True 共 18 行 | 一致 | 逐行复核 |
| Abstract L30 | r02 pooled OR 1.95 | `cohort_heterogeneity.json` 1.954 | 一致 | |
| Abstract L30 | r02 95% CI **1.33**–2.88 | 源 1.3245–2.8828 → 1.32 | **不一致** | 与 Table 5 的 1.32 自相矛盾 |
| Abstract L31 | r20 1.24, 1.03–1.48 | 1.2367 [1.0325,1.4812] | 一致 | |
| Abstract L31 | both I² above 90% | 90.5% / 93.8% | 一致 | |
| Abstract L32 | PI 0.84–4.57；0.81–1.89 | [0.8352,4.5716]；[0.81,1.8881] | 一致 | |
| Abstract L33 | "Smoking–cataract reversed **by region**" | 固定效应亚组 p=4.5e-6；随机效应 p=0.45；ELSA=Europe 且保护向 | **不一致** | 表述与事实双重不成立（F3） |
| Abstract L34 | SHARE 1.11, 1.04–1.18 | 1.109 [1.041,1.1815] | 一致 | |
| Abstract L34 | CLHLS 0.748, 0.64–0.87 | 0.748 [0.6435,0.8694] | 一致 | |
| Abstract L35 | pooled null 0.84, 0.67–1.05 | 0.839 [0.6698,1.0511] | 一致 | |
| Abstract L36 | regional subgroups differed p<0.0001 | p_between 4.53e-06（固定效应） | **不一致-口径** | 随机效应 p=0.45 |
| Abstract L37 | mean age p = 0.42–0.52 | 0.4178 / 0.5169 / **0.3472** | **不一致** | 摘要遗漏 0.35 |
| Abstract L38 | E-values 2.01 (1.57) and 1.46 (1.25) | 2.008/1.566；1.457/1.248 | 一致 | 方法学错（OR 当 RR，M4） |
| Abstract L21 | 八个队列、三大洲 | REGION 映射 Europe(2)/Asia(3)/Americas(3) | 一致 | |

### B. Methods

| 位置 | 稿件数值 | 原始出处 | 判定 | 备注 |
|---|---|---|---|---|
| L134–135 | development 134 pairs | `dataset_summary.csv` dev 134 | 一致 | |
| L166–168 | SHARE 1,693,515; MHAS 78,537; LASI 73,408; CLHLS 72,744; HRS 42,946; KLoSA 40,406; ELSA 9,771; CRELES 5,191 | 各 frame 行数逐一核对 | 数值一致 | 但命名为"person-wave records"错误（F1） |
| L166 | "In total 2.0 million" | 合计 2,016,518 | **不一致** | 见 F1 |
| L199 | SHARE current smoking 17.2% | `cohort_rule_results.csv` r20 SHARE exposure_prevalence 0.1715 | 一致 | |
| L217–219 | cataract 5 / glaucoma 5 / AMD ELSA only / vision impairment **all eight** | `cohort_rule_coverage.json`：cataract 5 ✓、glaucoma 5 ✓、amd 仅 ELSA ✓、vision 仅 7（CRELES 无） | **不一致** | 应为 seven |
| L223–227 | BMI 25（亚洲）/30（其他） | `cohort_confirmatory.py` L54–59、`cohort_power.py` L38–40 | 一致 | 但 `cohort_rule_coverage.json` 记 SHARE/CRELES 的 exposure_col = bmi_high_**25**，与切点声明不符 |
| L231–238 | 三态 = q<0.05 + 方向 | `cohort_confirmatory.py` L93–100 | 一致 | |
| L242–248 | logistic + age/sex + wave FE + 聚类稳健；SHARE 5 副本 Rubin | `cohort_confirmatory.py` L103–137 | 一致 | **但缺 §19.7 要求的 survey 设计**（F2） |
| L250–254 | Benjamini–Yekutieli；双家族 | `fdr_bhy`（BY，c(n)=Σ1/i） | 一致 | 探索家族实现为跨队列合并（m9） |
| L254 | Clopper–Pearson 精确区间 | 0.541/0.478/0.152–0.646/0.118–0.616 均可由 CP 复现 | 一致 | |
| L256–260 | 每对 MDE(80%)；设计效应由 survey/model CI 宽比导出 | `cohort_power.py`（无 DEFF 计算；DEFF 仅存在于 R11 层 `power_summary.json`） | **不一致** | 队列层并未计算设计效应 |
| L274–278 | "each figure and table is generated from a single declared source file so that no reported number exists in only one place" | 反例：110/56 仅存在于 dataset_summary；0.33 级多处冲突 | **不一致** | 声明与事实不符 |

### C. Results — 内部层与系统

| 位置 | 稿件数值 | 原始出处 | 判定 | 备注 |
|---|---|---|---|---|
| L298–301 | 159/180、301/352、14/14；underpowered 21/50/0 | `validation_distribution.csv` | 一致 | |
| L298 | "110 NHANES pairs … 56 KNHANES pairs" | `dataset_summary.csv` n_cases 110/56 | 一致于该文件 | 与 Table 4 的 180/352 冲突（C1） |
| L303–306 | NHANES 16 / 6 rep / 0 con / 10 uninf / 1.00 [0.541,1.00] / 0.375 / 0.889 | `performance_matrix.csv` | 一致 | |
| L306–308 | KNHANES 15 / 5 / 0 / 10 / 1.00 [0.478,1.00] / 0.333 / 0.882 | 同上 | 一致 | |
| L308–311 | CHARLS 4 / 0 / 0 / 4 / undefined / 0.000 | 同上 | 一致 | |
| L312–314 | "sensitivity analysis (**Table 3**) reports **four** alternative rule sets" | `headline_sensitivity.csv` 有 6 个备择集；Table 3 非敏感性表 | **不一致** | 见 m4 |
| L315–317 | A level 3 pairs, none replicated, 0.000 | `headline_sensitivity.csv` A_level_only 3/0/0/3 | 一致 | |
| L316–318 | A+B 13 pairs, 4 replicated, 0.308 | A_and_B_level_only 13/4/0/9 | 一致 | |
| L317–319 | exclude r22+r01 → 16, 6 rep, 0.375 | exclude_both_r22_and_r01 16/6/0/10 | 一致 | |
| Table 3 | pairs_tested 列空白 | `performance_matrix.csv` 该列空 | **不一致** | 见 m2 |
| Fig 3 L731 | 保守精确率 0.375 [0.152,0.646]；0.333 [0.118,0.616] | CP 重算一致 | 一致 | |
| Fig 3 L731 | "all rules 6/19 = 0.316；5/16 = 0.312" | `headline_sensitivity.csv` all_rules 19/6、16/5 | 数值一致 | 分母与 Table 3/4 的 16/15 冲突（M16） |
| Fig 3 L731 | level A 0/3；A+B 4/13 | 同上 | 一致 | |
| L454–457 | median MDE 1.337 / 1.159 | `power_summary.json` 1.337 / 1.159 | 一致 | |
| L455–457 | 17 of **30** rule-relevant powered nulls | `figure7_power_mde.csv` 30 行 17 个 powered_null | 数值一致 | 分母 30 与 Table 4 的 31、power_summary 的 35 均冲突（M16） |
| L458–459 | DEFF median 1.07 / 1.26 | `power_summary.json` 1.069 / 1.262 | 一致 | |
| Fig 7 L791 | NHANES n=17, KNHANES n=13 | `figure7_power_mde.csv` 17/13 | 一致于该文件 | 与 power 源文件 19/16 冲突（M16） |
| L478–479 | F1 0.435 (P 0.294 / R 0.833) | `baseline_summary_R11_corrected_gold.json`、`figure2_performance.csv` | 一致 | |
| L479 | LightRAG 0.327 ± 0.005 | 逐种子 [0.333,0.323,0.323,0.333,0.323] → SD 0.0055 | 一致 | |
| L479–480 | pure LLM **0.301 ± 0.017** | R11 逐种子 SD = **0.019**；0.017 为 R5 金标准 SD | **不一致** | M9 |
| L480 | naive RAG **0.080 ± 0.089** | R11 逐种子 SD = **0.098**；0.089 为 R5 金标准 SD | **不一致** | M9 |
| L481–482 | McNemar vs LightRAG p = 0.057–0.092 | `mcnemar_R11_gold.lightrag` [0.05737, 0.09229] | 一致 | |
| Fig 2 L719 | vs pure_llm 0.0043–0.0118；naive_rag 0.00024–0.0129 | 同上 JSON | 一致 | |
| Fig 2 L719/L721 | v1.1 replay (0.111) 柱"shown / 在源 CSV 中" | `v11_replay_R5.json` F1=0.1111 ✓；`figure2_performance.csv` **无该行** | **不一致** | M10 |
| Fig 2 L719 | 各方法精确率 0.10–0.29 | 0.294 / 0.181 / 0.203 / 0.1 | 一致 | |

### D. Results / Discussion — 队列层

| 位置 | 稿件数值 | 原始出处 | 判定 | 备注 |
|---|---|---|---|---|
| L328–329 | 8 队列行数串 | 各 frame 行数 | 数值一致 | 命名与分母问题同 F1 |
| L333 | Only 6 of 21 rules testable | `evidence_audit.json` 6/21 | 一致 | |
| L334–337 | 15 untestable，按原因分解（5+1+3+3+2+1） | `analysis_plan.md` §19.6 | 一致 | |
| L338–339 | 18 rule × cohort pairs；8 rep / 8 uninf / 2 con | `cohort_rule_results.csv` | 一致 | 逐行复核 18 行 |
| L341–343 | LASI 1.88 (1.76–2.00)；SHARE 1.75 (1.69–1.82)；CLHLS 3.59 (2.62–4.91)；CRELES 1.31 (1.07–1.61) q=0.051 | 源 1.8782 [1.7646,1.9991]；1.7539 [1.6908,1.8194]；3.5887 [2.6244,4.9074]；1.3116 [1.0705,1.6069]，q 0.050585 | 一致 | |
| L345–347 | HRS 1.61 (1.47–1.78)；ELSA 1.49 (1.21–1.83)；SHARE 1.09 (1.04–1.13)；KLoSA 1.10；CLHLS 1.03 | 1.6144/1.4883/1.0875/1.1002/1.0267 | 一致 | |
| L346–347 | all five cohorts pointed the same way | 五个 OR 均 > 1 | 一致 | |
| L350–352 | SHARE 1.11 (1.04–1.18, q=0.0095)；CLHLS 0.748 (0.64–0.87, q=0.0012)；ELSA 0.77；CRELES 0.70 | 1.109/0.748/0.7675/0.7023；q 0.009507/0.001214 | 一致 | |
| L353–354 | "the single positive cohort is European while **all three protective cohorts are not**" | ELSA = Europe 且 OR 0.7675 | **不一致** | 事实错误（F3） |
| L355–356 | CLHLS 0.809 (0.70–0.93, q=0.018)；SHARE 0.963 | 0.809 [0.704,0.9297] q 0.01772；0.9628 | 一致 | |
| L359–360 | SHARE 1.24 (1.20–1.29)；CRELES 0.99 | 1.2439 [1.2008,1.2886]；0.9911 | 一致 | |
| L361–364 | r11 MDE 1.70；interval (0.86, 0.55–1.34) | `cohort_power.csv` 1.6956；0.8586 [0.5483,1.3444] | 一致 | 但结局实为 amd_any（M7） |
| Table 5 r02 | **1.95 (1.33–2.88)** | 1.9540 [1.3245,2.8828] | **不一致** | 与 Table 5 交付版（1.32）及同稿 L1036 冲突 |
| Table 5 r10 | 0.84 (0.67–1.05), 91.0%, <0.0001, 0.53–1.33, <0.0001 | 0.839 [0.6698,1.0511], 91.0, 2.63e-07, [0.5291,1.3306], 4.53e-06 | 一致 | |
| Table 5 r20 | 1.24 (1.03–1.48), 93.8%, 0.81–1.89, <0.0001 | 1.2367 [1.0325,1.4812], 93.8, [0.81,1.8881], 8.99e-13 | 一致 | |
| Table 5 r12 | 0.89 (0.75–1.06), 79.5%, 0.027, 0.68–1.17, 0.027 | 0.8924 [0.7535,1.0569], 79.5, 0.02733, [0.6788,1.1732] | 一致 | |
| Table 5 r13 | **1.14** (0.91–1.41), 79.5%, 0.027, 0.80–1.62, 0.027 | 1.1349 [0.9121,1.412], 79.5, 0.02722, [0.7952,1.6197] | **不一致** | 交付版 `table5_heterogeneity.md` 写 1.13（正确） |
| Table 5 脚注 | r10 CLHLS 2.01(1.57)；SHARE 1.46(1.25)；r12 CLHLS 1.78(1.36)；r02 CLHLS 6.64(4.69) | `cohort_heterogeneity.json` | 一致 | OR 当 RR（M4） |
| L387–390 | Europe 1.08 / Asia 0.75 / Americas 0.70, p<0.0001 | per_group_OR [0.7023,0.748,1.0817]（组内固定效应） | 数值一致 | 随机效应 Europe=0.939, p=0.451（F3） |
| L394–396 | "PI excludes null **and** I²<75%"，none reliably transportable | 无预注册出处；`cohort_heterogeneity.py` L299 硬编码 | **不一致** | HARKing（M1） |
| L402–404 | slopes +0.017/−0.008/−0.010；p 0.42/0.52/0.35 | 0.01679/−0.0083/−0.00977；0.4178/0.5169/0.3472 | 一致 | |
| L404 | CLHLS mean age 92.0 | `cohort_heterogeneity.py` L55 硬编码 | **出处不明** | 无 data-derived 文件（C4） |
| L406–410 | E-values（同 Table 5） | 同上 | 一致 | |
| L411–412 | LOO 显示"没有任何单一队列造成该模式" | `cohort_influence.csv`：去 SHARE 后 pooled 0.747、I²=0.0 | **不一致** | 与结论相反（M14） |
| L420 | 18 cells (10.7%) feasible | `evidence_audit.json` | 一致 | |
| L421–423 | 83 / 41 / 26（=150） | `evidence_audit.json` | 一致 | 加总正确 |
| L426–430 | +15 / +13 / +13 / +6 / +6 / +5 / +5 / +3 | `evidence_audit.json` unlock 字典 | 一致 | |
| L436–437 | "two million person-wave records" | 见 F1 | **不一致** | |
| L442 | 68 pairs analysed in total | `cohort_transportability.json` n_pairs 68 | 一致 | |
| L445–446 | KLoSA 1.50 / 1.99；SHARE severe 1.46 | 1.5027 / 1.9903 / 1.4614 | 一致 | 无 CI（M15） |
| L446–447 | LASI 1.64, q=1.2e-10；HRS 1.98, q=8.1e-20 | 1.6371 / 1.2152e-10；1.9806 / 8.149e-20 | 一致 | 无 CI（M15） |
| L465–466 | median MDE by rule 1.11 (r20) – 1.70 (r11) | 由 `cohort_power.csv` 重算 median | 一致 | |
| L466–467 | 5 (62.5%) powered nulls | `cohort_power.csv` True=5 | 数值一致 | 按表头定义应为 6（M2） |
| L468–470 | CRELES ~5,000；r02 CI 仅"刚好包含 1 (1.07)" vs MDE 1.23 | n 5,086；CI 1.0705–1.6069；MDE 1.2281 | 数值一致 | 措辞错：CI 不含 1（m12） |
| L470–471 | CLHLS r20 powered for 1.21, observed 1.03 | MDE 1.2127；OR 1.0267 | 数值一致 | 与 Table 6 标签自相矛盾（M2） |
| L471–472 | KLoSA r20 MDE 1.10, observed 1.10 | 1.1023 / 1.1002 | 一致 | |
| Table 6 SHARE 行 | n 1,686,370 / 710,420 / 617,390 / 711,145 | 分析 n 337,274 / 142,084 / 123,478 / 142,229 的精确保 5 倍 | **不一致** | 见 M3 |
| Table 6 CLHLS r20 | powered_null **False** | 按表头定义应为 True | **不一致** | 见 M2 |
| Fig 8 图注 L801 | LASI 1.88、SHARE 1.75、CLHLS 3.59；CRELES 1.31 q=0.051 | 源一致 | 一致 | |
| Fig 8 图注 L801 | r20 五库方向一致；KLoSA 1.10、CLHLS 1.03 | 源一致 | 一致 | |
| Fig 8 (a) | r02 3+1；r20 3+2；r10 1+2+1；r12 1+1；r13 1+1；r11 1 | `cohort_transportability.json` states | 一致 | |
| Fig 8 (b) L805 | 0.702 (CRELES r10) – 3.589 (CLHLS r02) | 源一致 | 一致 | |
| Fig 8 (b) L805 | "rows whose interval crosses 1 (r10 in ELSA and CRELES, r12 in SHARE)" | ELSA 0.6069–0.9705、CRELES 0.5021–0.9822 **均不跨 1** | **不一致** | 见 m1 |
| Fig 8 统计 L807 | 18 pairs / 6 rules / 7 cohorts | 源一致 | 一致 | |
| Fig 8 统计 L807 | "**13** rules have no bar at all：5+1+3+3+2" | 加总 14；实际 15（21−6） | **不一致** | 见 M11 |
| Disc L500–502 | 两条通过者 I²>90%、PI 跨 1 | 90.5% / 93.8% | 一致 | |
| Disc L505–507 | pooled 0.84 (0.67–1.05)；Europe 1.08 / Asia 0.75 / Americas 0.70；p<0.0001 | 同 F3 | **不一致-口径** | |
| Disc L514–515 | 18 of 168；two million person-wave | 见 F1 | **不一致** | |
| Disc L525–526 | SHARE 1.11 / CLHLS 0.748 / ELSA 0.77 / CRELES 0.70 | 源一致 | 一致 | |
| Disc L530 | CLHLS mean age 92.0 | 脚本硬编码 | **出处不明** | C4 |
| Disc L539–540 | slope −0.008，p=0.52；"the **two** protective cohorts" | −0.0083、0.5169；保护向队列 **3** 个 | **不一致** | 见 m6 |
| Disc L544–545 | E-value 2.01 (1.57)、1.46 (1.25) | 源一致 | 一致 | OR 当 RR（M4） |
| Disc L581 | "I² of **90–94%** across **every** multi-cohort rule" | r12/r13 = 79.5% | **不一致** | 见 M13 |
| Disc L586 | 所有 PI 都含 null：r02 0.84–4.57、r10 0.53–1.33、r20 0.81–1.89 | 源一致（未列 r12/r13） | 一致 | 列举不全 |
| Disc L606–609 | "none of the six testable rules was reliably transportable" | 事后判据；r11 k=1 | **不一致** | 推论过强（M6） |
| Disc L667–668 | "the ELSA glaucoma and AMD items are the only sources" | `cohort_rule_coverage.json`：glaucoma 见于 5 队列 | **不一致** | 见 m7 |
| Disc L670–672 | CLHLS severe vision 25.7%、均龄 92 | `analysis_plan.md` §19.3 | 一致 | 出处为方案而非结果文件 |
| Disc L678–685 | Conclusion：6 testable、none reliably transportable | 见 M6 | **不一致** | |
| Disc L693–695 | "two million person-wave records" | 见 F1 | **不一致** | |

**合计：不一致 28 处；数值一致但口径/分母冲突 2 处；出处不明 2 处；另有 5 项因材料不足不可核验。**

---

## 数字修正清单（一处一行，错值 → 正确值）

1. 标题 L1：`2.0 million person-waves` → `598,382 person-wave observations (285,879 participants)`
2. Abstract L22：`comprising 2.0 million person-wave records` → `comprising 598,382 person-wave observations from 285,879 participants`
3. Abstract L30：r02 `95% CI 1.33–2.88` → `1.32–2.88`
4. Abstract L37：`p = 0.42–0.52` → `p = 0.35–0.52`
5. Abstract L33：`reversed by region` → `differed across cohorts, including within Europe`（并删除"地区"框架）
6. Abstract L36：`regional subgroups differed (p < 0.0001)` → `a fixed-effect subgroup test suggested regional variation (p < 0.0001) that did not survive random-effects subgroup pooling (p = 0.45)`
7. Abstract L32–33 / L27：删除"under a criterion also requiring tolerable heterogeneity no rule was reliably transportable"，或改为"in a post hoc sensitivity analysis"
8. Methods L166：`In total 2.0 million person-wave records were analysed` → `In total 2,016,518 frame rows were analysed, comprising 598,382 distinct person-wave observations (285,879 participants); the SHARE frame stacks five imputation replicates and the MHAS frame contains duplicated rows`
9. Methods L168：`SHARE 1,693,515` → `SHARE 1,693,515 rows = 338,703 person-waves × 5 imputation replicates`
10. Methods L168：`MHAS 78,537` → `MHAS 78,537 rows (15,213 distinct person-waves; frame contains a merge defect)`
11. Methods L217–219：`self-rated vision impairment (all eight)` → `self-rated vision impairment (seven; CRELES has no vision item)`
12. Methods L256–260（及 L121–127）：补一句方差口径声明——`variances were cluster-robust and unweighted; the pre-registered survey design specification of §19.7 could not be implemented because the frames contain no sampling weights or strata/PSU identifiers`
13. Methods L274–278：`so that no reported number exists in only one place` → 删除或改为"every table is generated from a declared source file; row-level provenance is listed in the supplement"（当前陈述与 110/56、0.33 系冲突相矛盾）
14. Methods L250 / Results L286 / Fig 3 缩写：`Benjamini–Hochberg–Yekutieli` → `Benjamini–Yekutieli`
15. Methods 结尾：补 Ethics / Data availability / Code availability / Funding / Competing interests / 预注册登记号
16. Results L297–298：`110 NHANES pairs ... 56 KNHANES pairs` → `180 NHANES pairs ... 352 KNHANES pairs`（或删除，或解释 110/56 口径）
17. Results L312：`the sensitivity analysis (Table 3)` → `(Table 4 / Supplementary Table Sx)`
18. Results L312：`four alternative rule sets` → `six alternative rule sets`
19. Results L354：`the single positive cohort is European while all three protective cohorts are not` → `SHARE (Europe) was risk-increasing while ELSA (also Europe), CLHLS and CRELES were protective`
20. Results L346（及 Fig 8）：`r11 (smoking → late AMD)` → `r11 (smoking → any AMD, ELSA)`
21. Results L342（及全稿）：`hyperglycaemia → cataract` → `self-reported diabetes → cataract`
22. Results 表 L381：r02 `1.95 (1.33–2.88)` → `1.95 (1.32–2.88)`
23. Results 表 L385：r13 `1.14 (0.91–1.41)` → `1.13 (0.91–1.41)`
24. Results L388–390：`regional subgroups differ significantly (Europe 1.08 versus Asia 0.75 and the Americas 0.70, p < 0.0001)` → 删除，或改为随机效应口径 `Europe 0.94 versus Asia 0.75 and the Americas 0.70, p = 0.45；ΕLSA remained protective within Europe`
25. Results L394–399：`heterogeneity-aware criterion (prediction interval excluding the null and I² < 75%)` → 明确加 `post hoc, not pre-specified`，并移入敏感性分析
26. Results L411–412：`Leave-one-cohort-out analysis shows the r10 regional split is not produced by any single cohort` → `removing SHARE removed the heterogeneity entirely (pooled OR 0.75, I² = 0%), whereas removing any other cohort left I² at 87–93%`
27. Results L455：`17 of 30 rule-relevant pairs` → `17 of 35 pre-registered rule-relevant pairs (35 = 19 NHANES + 16 KNHANES)`；或统一改为效能可评估的对 `17 of 30 assessable pairs`
28. Results L465–467：`5 (62.5%) were powered nulls` → `6 (75%) were powered nulls`
29. Results L468–470：`its r02 interval only just includes unity (1.07 ...)` → `its r02 lower bound (1.07) lay just above unity`
30. Results L470–471：`CLHLS r20 was powered for a 1.21-fold association and observed 1.03` → `CLHLS r20 could exclude 1.21 and observed 1.03, making it a powered null (Table 6 corrected)`
31. Results L479–480：`pure LLM 0.301 ± 0.017` → `0.301 ± 0.019`
32. Results L480：`naive RAG 0.080 ± 0.089` → `0.080 ± 0.098`
33. Results L436、Discussion L514、L693：`two million person-wave records` → `598,382 person-wave observations`
34. Table 3：`pairs_tested` 空白 → `180 / 352 / 14`
35. Table 5 脚注：补 `τ² is poorly identified with k = 2–5; prediction intervals use z and should be read as approximate`
36. Table 5 脚注：E-values → 声明 OR→RR 换算后重算：`r10 CLHLS 1.87 (1.50); r10 SHARE 1.43 (1.23); r12 CLHLS 1.66 (1.31); r02 CLHLS 4.51 (3.58)`
37. Table 6 表头：`from the analysed n` → `per-imputation analysed n (SHARE: 337,274 etc.; the frame stacks 5 replicates)`
38. Table 6 SHARE n：`1,686,370 / 710,420 / 617,390 / 711,145` → `337,274 / 142,084 / 123,478 / 142,229`
39. Table 6 SHARE MDE：`1.0242 / 1.0316 / 1.0336 / 1.0189 / 1.0254` → 按去重后 n 重算（≈1.055 / 1.071 / 1.077 / 1.043 / 1.057）
40. Table 6 CLHLS r20：`powered_null False` → `True`（`null_interpretation: powered_null`）
41. Discussion L505–507：`Europe 1.08 versus Asia 0.75 and the Americas 0.70; p < 0.0001` → 同第 24 条
42. Discussion L540：`the two protective cohorts` → `the three protective cohorts`
43. Discussion L581：`I² of 90–94% across every multi-cohort rule` → `I² of 79.5–93.8% across the five multi-cohort rules`
44. Discussion L606–609：`none of the six testable rules was reliably transportable` → `the pre-registered criterion classified two of six as transportable; a post hoc heterogeneity-aware criterion classified none, but the prediction interval is only weakly informative at k ≤ 5 and undefined for k = 1`
45. Discussion L667–668：`the ELSA glaucoma and AMD items are the only sources in the layer` → `ELSA provided the only graded AMD item; self-reported glaucoma was available in five cohorts`
46. Fig 2 图注 L719/L721：`that bar is shown` / `is present in the source CSV` → `is not plotted; its source row is not in this figure's source CSV`
47. Fig 2 图注 L719：`0.301 ± 0.017` / `0.080 ± 0.089` → `0.301 ± 0.019` / `0.080 ± 0.098`
48. Fig 8 图注 L805：`rows whose interval crosses 1 ... (r10 in ELSA and CRELES, r12 in SHARE)` → `the ELSA and CRELES r10 intervals exclude 1 but are uninformative after BY adjustment (q = 0.14 and 0.19); only SHARE r12 (0.90–1.03) crosses 1`
49. Fig 8 统计 L807：`13 rules have no bar at all` → `15 rules have no bar at all`（并把 r05 的脂质面板需求单列，使分解式加总为 15）
50. Fig 8 (a)/Table 5：删除 r12、r13 的 "Regional subgroup difference"（k=2 时该检验与总 Q 检验恒等）

---

## 附：本轮无法核验/未提供的事项（供编辑部参考）

1. §19 预注册的**时序**：仓库内无 git 快照、无外部登记号，`analysis_plan.md` 自身对 §12/§13/§15
   都做了"时序不可证"的降格披露，§19 没有。作为审稿人我**不能确认**队列层的预注册属性。
2. 队列均龄 92.0/67.9/… 的**数据来源**：仅存在于 `cohort_heterogeneity.py` 的常量表。
3. `110`/`56` 的口径：唯一出处 `dataset_summary.csv`，无生成脚本。
4. SHARE/KLoSA/MHAS 的**抽样权重是否存在**于原始数据：现有 frame 无权重列，
   因此我无法判断 §19.7 的 survey 设计是"未实现"还是"数据不可得导致降级"——两种情形的
   审稿结论不同，作者必须说明。
5. `Figure 7` 从 35 个 rule-relevant 对缩减到 30 行的**剔除规则**：图注未写，脚本未落盘。
6. MHAS frame 中 `mergeid` 出现 "4.Fair"/"Good 3" 等标签字符串的原因（连接键污染），
   需要作者给出 frame 构建脚本与修复。
7. NHANES "all_rules 19"（> 规则宇宙 18）的构成。
