# R5 统计复算报告（统计复算师）

**复算对象**：`outputs/paper/sections/methods.md`、`outputs/paper/sections/results.md`（任务指定材料），
并对照装配稿 `outputs/paper/manuscript.md`。
**复算数据**：`data/frames/cohort_*.csv`（8 队列原始帧），不读任何项目中间结果作为输入。
**复算脚本与输出**：`outputs/review/recalc/`（`r5_01`–`r5_09`，全部独立重写，未 import 任何项目脚本）。
**一句话结论**：**稿件列出的 29 个核心数字全部复现（max |ΔOR| = 0.000000，三态 18/18 一致）**；
但由这些数字推出的**若干定性结论不被数据支持**，其中一条是致命的方向归因错误，一条是稿件内部版本冲突。

---

## 复现环境

| 项 | 值 |
|---|---|
| 解释器 | `D:\Desktop\眼科公共数据库agent搭建\.venv\Scripts\python.exe`，Python 3.10.4 |
| pandas | 2.3.3 |
| numpy | 2.2.6 |
| scipy | 1.15.3 |
| statsmodels | 0.15.0 |
| 缺失包 | **无** |
| 降级项 | **无**（未使用 patsy；波次哑变量手工构造） |
| R | **未使用**。工作目录含中文，R 无法打开该路径；本层复算不需要 R（但由此暴露一项声明未落实，见"无法复现项"1） |

- 模型按 [methods.md:121-127](outputs/paper/sections/methods.md#L121-L127) 重写：
  `logit(P(结局)) = β0 + β1·暴露 + β2·age + β3·sex + 波次固定效应`，`cov_type="cluster"`，`groups=mergeid`。
- SHARE 按 `implicat` 5 个副本分别拟合后 Rubin 合并（within + (1+1/m)·between）。
- BMI 切点：KLoSA/MHAS/LASI/CLHLS = 25；SHARE/HRS/ELSA/CRELES = 30（[analysis_plan.md:560-563](docs/analysis_plan.md#L560-L563)）。
- 与项目实现唯一刻意的差异：我用 `maxiter=200, tol=1e-10`（项目默认 `tol=1e-8`）。
  这只让 p 值在第 4–5 位有效数字上相差 ~1e-4 相对值（例：CLHLS r02 p = 1.216418e-15 vs 1.214239e-15），
  **OR 与 95%CI 到 4 位小数完全一致**。此差异未用于"凑数"。

---

## 数据体检

### 1. n 对账（第一项）

| 队列 | 帧行数（实测） | 稿件/计划行数 | 差 | 唯一人数（实测） | 计划人数 | 差 |
|---|---|---|---|---|---|---|
| SHARE | 1,693,515 | 1,693,515 | 0 | 137,183 | 137,183 | 0 |
| HRS | 42,946 | 42,946 | 0 | 27,261 | 27,261 | 0 |
| ELSA | 9,771 | 9,771 | 0 | 9,771 | 9,771 | 0 |
| KLoSA | 40,406 | 40,406 | 0 | 11,137 | 11,137 | 0 |
| LASI | 73,408 | 73,408 | 0 | 73,408 | 73,408 | 0 |
| MHAS | 78,537 | 78,537 | 0 | **15,198** | **15,199** | **−1** |
| CLHLS | 72,744 | 72,744 | 0 | 9,093 | 9,093 | 0 |
| CRELES | 5,191 | 5,191 | 0 | 2,827 | 2,827 | 0 |
| **合计** | **2,016,518** | **2,016,518** | **0** | **285,878** | — | — |

行数与 [analysis_plan.md:471-480](docs/analysis_plan.md#L471-L480) 的 person-wave 表**逐队完全一致**；
唯一人数除 MHAS 差 1 人外完全一致。`manuscript.md` 报的 285,878 人、598,386 person-wave 我**独立算出并完全吻合**。

### 2. person-wave 口径核对（稿件内部不一致的来源）

| 口径 | 值 | 说明 |
|---|---|---|
| 帧行数合计 | 2,016,518 | = `outputs/paper/sections/methods.md` 的"2.0 million person-wave records" |
| 唯一 (mergeid, wave) 合计 | **598,386** | = `outputs/paper/manuscript.md:172-175` 的报数 |
| 膨胀倍数 | **3.37×** | 由 SHARE 5 份插补副本 + MHAS 重复行造成 |

- **SHARE 是 5 个完全平衡的副本**：每个 `implicat` 都是 338,703 行 / 137,183 人 / 5 个波次。
  故 1,693,515 = 5 × 338,703，唯一 person-wave = 338,703。复现无误。
- **MHAS 帧不完整**：78,537 行中 **63,320 行完全重复**（占 80.6%）；
  波次 3/4/5/6（合计 63,355 行）的 `age` 与 `sex` **100% 缺失**，且这些行塌缩到约 16 个退化 `mergeid`
  （单个 mergeid 吞掉 5,071–6,447 行）。唯一 person-wave 只有 **15,217**。
  MHAS 在本层不贡献任何可检验单元（[analysis_plan.md:526](docs/analysis_plan.md#L526)），故未污染任何已报估计。
- `sections/methods.md:45-47` 的 "In total 2.0 million person-wave records were analysed" 只有在
  **"CSV 行数"**意义上成立；作为"观测数"高估 3.37×，且违反同一稿件"插补副本绝不算作独立个体"的纪律
  （[methods.md:126-127](outputs/paper/sections/methods.md#L126-L127)）。`manuscript.md` 已改为 598,386。

### 3. 协变量缺失（直接影响可分析样本）

| 队列 | age 缺失% | sex 缺失% | 后果 |
|---|---|---|---|
| HRS | **51.31** | **51.31** | 2010 波（22,034 行）age/sex 全缺 → 整波被完整案例剔除 |
| MHAS | **80.67** | **80.67** | 波次 3–6 全缺 |
| ELSA | **20.49** | 19.83 | 单波（wave 3），r11/r10/r20 各损失约 1% |
| CLHLS | 7.26 | 0 | r02/r10/r12/r20 各损失约 7–8% |
| 其余 4 队 | 0 | 0 | — |

### 4. 关键 flag 流行率（与稿件声明互检）

| 检查 | 稿件 | 复算 | 判定 |
|---|---|---|---|
| SHARE `current_smoking` | 17.2%（[methods.md:78](outputs/paper/sections/methods.md#L78)） | **17.15%** | 一致 |
| CLHLS `diabetes`（医生告知口径） | 1.36%（[analysis_plan.md:493](docs/analysis_plan.md#L493)） | **1.36%** | 一致 |
| CLHLS 均龄 | 92.0（[analysis_plan.md:483](docs/analysis_plan.md#L483)） | **91.98** | 一致 |
| SHARE `bmi_high_30` | 22.81%（[analysis_plan.md:563](docs/analysis_plan.md#L563)） | **22.81%** | 一致 |
| 帧中 dtype | 全部 float64（无"标签字符串被数值化"陷阱） | — | 一致 |
| SHARE `country` 列 | 未声明 | **0 个非缺失值（整列空）** | 需澄清 |

### 5. 完整案例后仍被分析的波次

SHARE 5/5 波、KLoSA 5/5、CLHLS 8/8、CRELES 2/2、ELSA 1/1、LASI 1/1 全部存活；
**HRS 只剩 2016 波**（2010 波 age 全缺）、**MHAS 只剩 1 波**（其余 4 波 age 全缺）。见表 M2。

---

## 逐检验复现总表

`Δ` 为绝对差（OR / CI 限定 0.005，I² 限定 0.06，p 按数量级）。全部数值来自
`outputs/review/recalc/recalc_verdicts.csv`。

### A. 队列内 logistic 回归（点估计与 95%CI）

| 检验 | 稿件值 | 复算值 | 差异 | 判定 |
|---|---|---|---|---|
| r10 吸烟→白内障 **SHARE** | 1.11 [1.04, 1.18] | 1.1090 [1.0410, 1.1815] | <0.003 | **一致** |
| r10 吸烟→白内障 **CLHLS** | 0.748 [0.64, 0.87] | 0.7480 [0.6435, 0.8694] | <0.005 | **一致** |
| r02 高血糖→白内障 **CLHLS** | 3.59 [2.62, 4.91] | 3.5887 [2.6244, 4.9074] | <0.003 | **一致** |
| r02 高血糖→白内障 **SHARE** | 1.75 [1.69, 1.82] | 1.7539 [1.6908, 1.8194] | <0.002 | **一致** |
| r02 高血糖→白内障 **LASI** | 1.88 [1.76, 2.00] | 1.8782 [1.7646, 1.9991] | <0.002 | **一致** |
| r02 高血糖→白内障 **CRELES** | 1.31 [1.07, 1.61] | 1.3116 [1.0706, 1.6069] | <0.002 | **一致** |
| r20 吸烟→视力损害 **HRS** | 1.61 [1.47, 1.78] | 1.6144 [1.4682, 1.7752] | <0.005 | **一致** |
| r20 吸烟→视力损害 **ELSA** | 1.49 [1.21, 1.83] | 1.4883 [1.2128, 1.8263] | <0.004 | **一致** |
| r20 吸烟→视力损害 **SHARE** | 1.09 [1.04, 1.13] | 1.0875 [1.0429, 1.1339] | <0.004 | **一致** |
| r11 吸烟→AMD **ELSA** | 0.86 [0.55, 1.34] | 0.8586 [0.5483, 1.3444] | <0.005 | **一致** |
| r12 饮酒→白内障 **CLHLS** | 0.809 [0.70, 0.93] | 0.8090 [0.7040, 0.9297] | <0.002 | **一致** |
| r12 饮酒→白内障 **SHARE** | 0.963 | 0.9628 [0.8999, 1.0301] | 0.0002 | **一致** |
| r13 BMI→白内障 **SHARE** | 1.24 [1.20, 1.29] | 1.2439 [1.2008, 1.2886] | <0.002 | **一致** |
| r13 BMI→白内障 **CRELES** | 0.99 | 0.9911 [0.8126, 1.2087] | 0.0011 | **一致** |
| **18 个确认单元整体** | — | — | **max\|ΔOR\| = 0.000000** | **一致 18/18** |
| q 值（BY，确认家族）| 例 CRELES r02 q = 0.051 | 0.050584 | <0.001 | **一致** |
| 三态计数 | 8 replicated / 8 uninformative / 2 contradicted | 8 / 8 / 2（逐单元一致） | 0 | **一致** |

### B. 随机效应合并（REML τ²，与稿件一致）

| 检验 | 稿件值 | 复算值 | 差异 | 判定 |
|---|---|---|---|---|
| r10 合并 OR | 0.84 [0.67, 1.05] | 0.8390 [0.6698, 1.0511] | <0.002 | **一致** |
| r10 I² | 91.0% | 91.02%（τ²=0.042141） | 0.02 | **一致** |
| r10 地区亚组 Q_between p | <0.0001 | **4.53 × 10⁻⁶** | — | **一致** |
| r10 地区各组 OR | Europe 1.08 / Asia 0.75 / Americas 0.70 | 1.0817 / 0.7480 / 0.7023 | <0.002 | **一致** |
| r02 合并 OR | 1.95 [1.33, 2.88] | 1.9540 [1.3245, 2.8828] | <0.004 | **一致** |
| r02 I² | 90.5% | 90.45%（τ²=0.148689） | 0.05 | **一致** |
| r02 预测区间 | 0.84–4.57 | **0.8352–4.5716** | <0.005 | **一致** |
| r02 地区亚组 p | 0.0004 | **0.000409** | <0.001 | **一致** |
| r20 合并 OR | 1.24 [1.03, 1.48] | 1.2367 [1.0325, 1.4812] | <0.003 | **一致** |
| r20 I² | 93.8% | 93.81%（τ²=0.038137） | 0.01 | **一致** |
| r20 预测区间 | 0.81–1.89 | **0.8100–1.8881** | <0.002 | **一致** |
| r12 合并 OR / I² / PI | 0.89 (0.75–1.06) / 79.5% / 0.68–1.17 | 0.8924 (0.7535–1.0569) / 79.46% / 0.6788–1.1732 | <0.004 | **一致** |
| r13 合并 OR / I² / PI | 1.14 (0.91–1.41) / 79.5% / 0.80–1.62 | 1.1349 (0.9121–1.4120) / 79.50% / 0.7952–1.6197 | <0.005 | **一致** |
| Q p（r02/r10/r20） | <0.0001 | 6.94e-7 / 2.63e-7 / 3.03e-13 | — | **一致** |
| 元回归 平均年龄斜率 p | +0.017 / −0.008 / −0.010, p = 0.42 / 0.52 / 0.35 | +0.01676 (p=0.419) / −0.00831 (p=0.515) / −0.00979 (p=0.346) | <0.001 | **一致** |
| E 值（table5） | CLHLS r10 2.01 (1.57)；SHARE r10 1.46 (1.25)；CLHLS r12 1.78 (1.36)；CLHLS r02 6.64 (4.69) | 2.008 (1.566) / 1.457 (1.248) / 1.776 (1.361) / 6.637 (4.689) | <0.005 | **一致** |

### C. 逐对 MDE-OR

| 检验 | 稿件值 | 复算值（发表口径） | 复算值（分析 n 口径） | 判定 |
|---|---|---|---|---|
| SHARE r13 | 1.0189 | **1.0189** | 1.0427 | **一致**（见 M3） |
| ELSA r11 | 1.6956 | **1.6956** | 1.7017 | **一致** |
| CRELES r02 | 1.2281 | **1.2281** | 1.2281 | **一致** |
| r02 中位 MDE | — | 1.1696 | 1.1696 | — |
| r10 中位 MDE | — | 1.2279 | 1.2332 | — |
| r20 中位 MDE | 1.11（下界） | **1.1084 → 1.11** | 1.1590 | **一致** |
| r11 中位 MDE | 1.70（上界） | **1.6956 → 1.70** | 1.7017 | **一致** |
| 8 个 uninformative 中 powered null | 5（62.5%） | 5（62.5%） | **5（62.5%）** | **一致（修正后不变）** |

### D. 证据审计计数

| 检验 | 稿件值 | 复算值 | 判定 |
|---|---|---|---|
| 可能单元 | 168（21 规则 × 8 队列） | **168** | **一致** |
| 可行单元 | 18（10.7%） | **18（10.7%）** | **一致** |
| 可检验规则数 | 6 / 21 | **6 / 21** | **一致** |
| 阻塞分解 双侧缺/仅暴露缺/仅结局缺 | 83 / 41 / 26（和 150） | **83 / 41 / 26（和 150）** | **一致** |
| 解锁排序 | fundus imaging +15, blood assays +13, geocoded +13, dietary +6, behavioural +6, optic-disc grading +5, self-report ocular dx +5, anthropometry +3 | **同序同值**（`OUTCOME:fundus_imaging` 15, `blood_assay` 13, `geocoded_environment` 13, `dietary_index` 6, `questionnaire_behaviour` 6, `OUTCOME:fundus_imaging_or_grading` 5, `OUTCOME:selfreport_ocular_diagnosis` 5, `anthropometry` 3） | **一致** |
| 可行单元清单 | 18 个 (规则×队列) | **18 个逐一相同**，与 coverage 矩阵 `identical: true` | **一致** |

---

## 不一致清单

**所有 29 项数值检验均为"一致"（差异全在舍入范围内）**。以下不一致全部是**由这些数字推出的文字结论与数据不符**，
或**稿件内部两版文字互相矛盾**。每条给出差值与可能原因。

### 1【致命】r10 的"地区方向分裂"归因错误，欧洲内部即分裂

- 稿件（[results.md:68-73](outputs/paper/sections/results.md#L68-L73)，`manuscript.md:410-415` 同）：
  "Four cohorts therefore split 1:3 on the sign of the association, and the single positive cohort is
  European while **all three protective cohorts are not**."
- 复算：SHARE（欧洲）1.1090 为危险方向；CLHLS（亚洲）0.7480、CRELES（美洲）0.7023 **以及 ELSA（欧洲）0.7675** 为保护方向。
- **差值/方向**：该句被 **ELSA** 直接证伪——保护方向的三个队列中有一个就是欧洲队列。
  因此"欧洲 vs 非欧洲"的对照不成立，"reversed by region"是把 SHARE 一队的偏离写成了洲际差异（生态学谬误）。
- **可能原因**：方法不符 / 选择性报告。表 5 报的 "Europe 1.08" 是 SHARE 与 ELSA 的加权平均，
  权重被 SHARE 的极小标准误（se=0.0323 vs ELSA se=0.1198）压倒，把一队内的方向对立平均掉了。
  稿件正文从未展示这两个欧洲队列的点估计。
- **对论文的影响**：摘要 34-36 行与标题（"Pooling conceals directional conflict"）把该洲际对照当作核心叙事。

### 2【致命】r10 leave-one-out 的两种相反表述并存（版本冲突）

- [results.md:130-131](outputs/paper/sections/results.md#L130-L131)：
  "Leave-one-cohort-out analysis shows the r10 regional split **is not produced by any single cohort**."
- [table5_heterogeneity.md:29-31](outputs/tables/table5_heterogeneity.md#L29-L31) 与
  [manuscript.md:472-476](outputs/paper/manuscript.md#L472-L476)：
  "Removing SHARE reduces I-squared from 91.0% to 0.0% … **the heterogeneity of r10 is driven by one cohort**".
- **复算（裁决）**：
  | 剔除 | 合并 OR [95%CI] | I² | 地区 Q_between p |
  |---|---|---|---|
  | 不剔 | 0.8390 [0.6698, 1.0511] | 91.02% | 4.53e-6 |
  | **剔 SHARE** | **0.7470 [0.6636, 0.8410]** | **0.00%** | **0.913** |
  | 剔 CLHLS | 0.8701 [0.6493, 1.1660] | 86.6% | 0.0131 |
  | 剔 CRELES | 0.8722 [0.6700, 1.1354] | 93.0% | 8.47e-6 |
  | 剔 ELSA | 0.8563 [0.6378, 1.1496] | 92.8% | 1.01e-6 |
- 项目自己的 [cohort_influence.csv:6](outputs/cohorts/cohort_influence.csv#L6) 写着 `r10, SHARE, 0.747, 0.6636, 0.841, 0.0, 0.0`。
- **差值/方向**：`results.md` 的陈述与项目自己的输出、自己的表 5、自己的装配稿**全部相反**。
- **可能原因**：`sections/results.md` 是**旧版残留**；结论未随分析更新。属流程性错误，但若以该节投稿即发出错误陈述。
  我在 `manuscript.md`（应为准稿）中未发现该错误句，故判定为**版本冲突**而非已投出的错误。

### 3【重大】HRS r20 实为单波（2016）估计，稿件按两波呈现

- 稿件：HRS 列为两波（[analysis_plan.md:474](docs/analysis_plan.md#L474) "2010/2016"），
  方法称"波次固定效应（多于一波贡献时）"（[methods.md:122-123](outputs/paper/sections/methods.md#L122-L123)），
  HRS 计 42,946 person-wave。
- 复算：HRS 帧 2010 波 22,034 行的 `age`/`sex` **100% 缺失**（0/22,034）。age、sex 是完整案例协变量，
  故 **2010 波被整体静默剔除**。r20 的分析 n = **13,511**（≈ 2016 波），不是 28,654 也不是 42,946；
  该单元**没有可估的波次固定效应**（只有一个波次）。
- **差值/方向**：OR 1.6144 复现无误（无舍入差），但样本口径与稿件描述不符；
  稿件全文未报告该单元的可分析 n。同一原因使 Table 6 的 HRS n = 28,654（未调整分母）而非 13,511。
- **可能原因**：数据可用性缺陷未进入质量门；`scripts/detect_exposure_gates.py` 审的是暴露条件题的门槛，
  没有审协变量在波次维度的可得性。§19.4/§19.5 未覆盖此类失败模式。

### 4【重大】Table 6 的 n 不是"analysed n"，SHARE 被放大 5 倍

- 稿件（[table6_power.md:3-4](outputs/tables/table6_power.md#L3-L4) / `manuscript.md:1255`）：
  "computed from **the analysed n** and observed margins"；
  `manuscript.md:177-179`："replicate 1 is used for every descriptive **and power** calculation …
  so an imputation replicate is never counted as an independent participant."
- 复算：
  | 单元 | 表 6 的 n | 分析 n | 比值 | 表 6 MDE | 修正 MDE |
  |---|---|---|---|---|---|
  | SHARE r02 | 1,686,370 | 337,274 | **5.000** | 1.0242 | **1.0549** |
  | SHARE r10 | 710,420 | 142,084 | **5.000** | 1.0316 | **1.0720** |
  | SHARE r12 | 617,390 | 123,478 | **5.000** | 1.0336 | **1.0768** |
  | SHARE r13 | 1,686,370 | 337,274 | **5.000** | 1.0189 | **1.0427** |
  | SHARE r20 | 711,145 | 142,229 | **5.000** | 1.0254 | **1.0577** |
  | HRS r20 | 28,654 | 13,511 | **2.121** | 1.1084 | **1.1590** |
  | CLHLS 4 单元 | — | — | 1.076–1.080 | 例 1.6882 | 1.7208 |
- **差值/方向**：18 个单元中 **6 个 MDE 报错**（SHARE 5 个 + HRS 1 个），误差方向一致地**低估 MDE（高估效能）**，
  且与同一稿件"power 只用副本 1"的明文声明冲突。
- **对结论的影响**：**不改变**。修正后 rule 中位 MDE 仍为 r20 最小（1.1590）、r11 最大（1.7017），
  "8 个 uninformative 中 5 个是 powered null（62.5%）"仍为 **5/8**。属数值报错而非结论错误，但必须更正。
- **可能原因**：`scripts/cohort_power.py:71` 对 `d[[xcol,ycol]]` 直接 dropna，未按 `implicat` 取副本 1。

### 5【重大】§19.7 声明的 survey 设计方差从未实施，且未记为偏离

- 稿件（[analysis_plan.md:555](docs/analysis_plan.md#L555)）：
  "SHARE 与 LASI 等带设计权重者用 **survey 设计（strata/PSU/weights）**"。
- 复算：SHARE 帧 19 列、LASI 帧 19 列中**均无任何权重 / strata / PSU 列**
  （SHARE 的 `country` 列 0 个非缺失值）。实际实现的方差全部是 `mergeid` 聚类稳健方差；
  LASI 单波且每人一行，`mergeid` 聚类退化为无异质性调整（近似 HC0）。
- **差值/方向**：报告出的 LASI r02 CI [1.7646, 1.9991] 正是这个模型方差，复现无误；
  但**声明的设计效应校正从未计算**，且 §0 偏离记录中**没有**这一条。属"未实施的预注册设定"。
- **可能原因**：帧构建阶段未携带设计变量；§6 的降级路径只对 CHARLS 声明过，未延伸到 §19。

### 6【次要】命名错误：Benjamini–Hochberg–Yekutieli

- [results.md:5](outputs/paper/sections/results.md#L5) 与 `manuscript.md:347` 写作
  "Benjamini–Hochberg–Yekutieli q < 0.05"，[methods.md:129](outputs/paper/sections/methods.md#L129) 写作
  "Benjamini–Yekutieli procedure"。二者是同一族的两个名字混用（BHY ≠ BH），正确名为 **Benjamini–Yekutieli**。
- 复算：实现是 BY（`c(n) = Σ 1/i`）无误，q 值复现（例 CRELES r02 q = 0.050584，稿件 0.051）。属笔误。

### 7【次要】探索性/确认性两家族重叠

- §19.7 定义 exploratory 家族为"各队列内**所有**暴露 flag × 结局 flag 对"
  （[analysis_plan.md:569](docs/analysis_plan.md#L569)）；`scripts/cohort_confirmatory.py:255` 在**全部 68 对**
  （含 18 个确认对）上做一次 BHY，另在 18 对上做 `q_rule`。
- 复算：68 对（18 确认 + 50 探索）与稿件"68 pairs analysed in total"一致；三态用 `q_rule` 复现。
  两家族重叠是可接受的读法，但应写明以免读者以为分母互斥。

### 8【次要】其他未披露的缺失

- ELSA `age` 缺失 20.49%、`sex` 缺失 19.83%，[methods.md:59-91](outputs/paper/sections/methods.md#L59-L91)
  的质量控制只写了"可用性以非缺失计数判定"，未报任何逐队列协变量缺失表。
  对 ELSA r11（AMD，n=3,991）影响最大。
- MHAS 被描述为 "78,537 person-wave"，而实际唯一 person-wave = 15,217、80.6% 行重复。
  `manuscript.md:174` 已改为 15,217，`sections/methods.md:46` 仍是 78,537。

---

## 敏感性抽查（按任务要求）

### r10 的地区方向分裂是否会翻转？

| 敏感性 | 合并 OR [95%CI] | I² | 地区各组 OR | Q_between p | 方向分裂 |
|---|---|---|---|---|---|
| 主分析（4 队） | 0.839 [0.670, 1.051] | 91.02% | Eur 1.082 / Asia 0.748 / Am 0.702 | 4.53e-6 | 存在 |
| 剔 SHARE（"异常值"） | 0.747 [0.664, 0.841] | **0.00%** | Eur 0.768 / Asia 0.748 / Am 0.702 | **0.913** | **消失**（三队同向保护） |
| 剔 CLHLS | 0.870 [0.649, 1.166] | 86.6% | Eur 1.082 / Am 0.702 | 0.0131 | 保持 |
| 剔 CRELES | 0.872 [0.670, 1.135] | 93.0% | Eur 1.082 / Asia 0.748 | 8.47e-6 | 保持 |
| 剔 ELSA | 0.856 [0.638, 1.150] | 92.8% | Eur 1.109 / Asia 0.748 / Am 0.702 | 1.01e-6 | 保持（欧洲内部仍对立） |
| age ≤ 85（截掉最老层） | 0.856 [0.669, 1.095] | 87.8% | Eur 1.118 / Asia 0.732 / Am 0.721 | 0.000585 | 保持但减弱 |
| age ≤ 80 | 0.933 [0.736, 1.183] | 77.9% | Eur 1.145 / Asia 0.858 / Am 0.790 | **0.0875** | 方向不翻转，**显著性消失** |
| age 60–85 | 0.852 [0.666, 1.090] | 86.6% | Eur 1.111 / Asia 0.732 / Am 0.721 | 0.000799 | 保持 |

**答**：分裂**不会因剔除某一队而"翻转"**，但会**因剔除 SHARE 而整体消失**（I² → 0.0%，地区 p → 0.913，三队同向）；
把最老年龄层截到 age ≤ 80 后地区差异不再显著（p = 0.088），方向仍不翻转。
即：**"地区分裂"实际上是"SHARE 一队 vs 其余三队"**，并且一部分是年龄结构差异。

### BMI 切点

- **对 r10 定义上不适用**（暴露是 `current_smoking`，与 BMI 无关）；任务把 BMI 切点与 r10 并列，此处需澄清。
  我对 r10 做的等价"异常值"检查是 leave-one-cohort-out 与年龄截尾（上表）。
- 对唯一受 BMI 切点影响的规则 r13：

| 切点 | SHARE OR | CRELES OR | 合并 OR [95%CI] | I² | 方向 |
|---|---|---|---|---|---|
| 预注册（SHARE/CRELES = 30） | 1.2439 | 0.9911 | 1.135 [0.912, 1.412] | 79.50% | 不显著 |
|  swapped（= 25） | 1.1473 | 1.0772 | **1.1448 [1.1099, 1.1808]** | **0.00%** | **变为显著且同质** |

**答**：方向不翻转（两种切点下合并 OR 均 > 1），但**显著性与异质性结论完全反转**：
用 25 切点 r13 变成"两队列一致且显著"（I²=0%）。这正好落回
[results.md:78-80](outputs/paper/sections/results.md#L78-L80) 所说的"r13 只靠一个队列"的对立面，
说明 r13 的结论对预注册切点高度敏感，应在敏感性分析中显式报告。亚洲队列（KLoSA/MHAS/LASI/CLHLS）
帧内无 BMI 列或无 `cataract_any`，无法做对称检验。

---

## 无法复现项

1. **§19.7 声明的 SHARE/LASI survey 设计方差（strata/PSU/weights）**。
   *缺什么*：帧内没有任何设计变量列（SHARE 19 列、LASI 19 列均无 weight/strata/PSU；SHARE `country` 全空）。
   *后果*：只能复现模型型聚类稳健方差；设计效应校正后的 CI 不可计算。
   （对照：NHANES/KNHANES 层有 `survey_sensitivity_R5.R` 与 svyglm 实现，本层没有。）
2. **队列层 design effect（"从 survey/model CI 宽度比导出"）**。
   *缺什么*：本层既无 survey CI（见 1），结果表中也无 deff 列；`cohort_power.py` 未计算 deff。
   [methods.md:137-139](outputs/paper/sections/methods.md#L137-L139) 的这句在队列层无实现。
3. **§19.3 的 MHAS 行（78,537 person-wave / 15,199 人 / 5 波）**。
   *缺什么*：帧内 MHAS 唯一 person-wave 15,217、人 15,198、波次 3–6 的 age/sex 全缺、63,320 行完全重复，
   且约 16 个 `mergeid` 吞掉数千行。要复现计划表需要 MHAS 构建脚本的中间日志与原始构造文件。
4. **`sections/methods.md:45-47` 的 "2.0 million person-wave records were analysed"**。
   *缺什么*：作为观测数无法复现（真值 598,386）；只有当"person-wave record"被定义为"CSV 行"时才成立，
   而这与同一稿件"插补副本不算独立个体"的纪律冲突。`manuscript.md` 已是 598,386。
5. **ELSA 20.5% 年龄缺失 / HRS 51.3% 年龄缺失 / MHAS 80.7% 的成因**。
   *缺什么*：帧内无质量/来源标志列，无法判断是真实缺失、跳转缺失还是映射失败。
   需要 `scripts/build_cohort_frames.py` 的逐队映射日志。
6. **r11（吸烟→AMD）与 r16（眼压/视盘）族的可迁移性**。
   *缺什么*：8 队列均无眼底影像、眼压、视盘分级；r11 仅 ELSA 可检验（复算一致），其余按构造不可检验。
   这部分**不是复现失败，而是稿件已正确声明**，列此仅为界定结论域。

---

## 致命 / 重大 / 次要 / 需澄清

### 致命（Fatal）——结论层，必须在投稿前修正

- **F1 洲际方向分裂的归因被自己的数据证伪**（不一致清单 1）。
  ELSA（欧洲）与 CLHLS、CRELES 同为保护方向，SHARE（欧洲）为危险方向 → 欧洲内部即分裂。
  "the single positive cohort is European while all three protective cohorts are not" 是**事实错误**，
  且该对照正是标题、摘要与"pooling conceals directional conflict"结论的承载句。
  另外复算证明这类"地区差异"完全由 SHARE 一队承担（剔 SHARE → I² 91.0%→0.0%，地区 p→0.913）。
  **建议**：把叙述从"by region"改为"SHARE（欧洲）与其他三个队列（含另一欧洲队列 ELSA）方向相反"，
  并同时报告 ELSA 的点估计（0.7675）与 SHARE 的点估计（1.1090），否则读者会认为欧洲整体指向危险。
- **F2 r10 leave-one-out 存在两种相反表述并存**（不一致清单 2）。
  `sections/results.md` 与 `manuscript.md`／`table5` 互相矛盾；项目自己的 `cohort_influence.csv` 支持后者。
  若投稿版本取自 `sections/`，则发出与自身补充材料相反的陈述。
  **建议**：以 `manuscript.md:472-476` 为准，删除 `sections/results.md:130-131` 的句子，并核对 section 文件与装配稿的一致性。

### 重大（Major）——可复现性与口径，需更正 + 在稿件中披露

- **M1 HRS r20 实为单波（2016）估计**（不一致清单 3）。分析 n = 13,511，2010 波（22,034 行）因 age/sex 全缺被静默丢弃；
  该单元无波次固定效应可估。稿件按两波 42,946 person-wave 呈现。**必须报告逐单元可分析 n 与逐队协变量缺失。**
- **M2 Table 6 的 n 不是 analysed n**（不一致清单 4）。SHARE 5 个单元 n 恰为分析 n 的 5.000 倍（插补副本被当独立观测），
  HRS 为 2.121 倍；6/18 个 MDE 因此报错且系统性地高估效能。
  修正后 MDE：SHARE r13 1.0427、r10 1.0720、r12 1.0768、r02 1.0549、r20 1.0577、HRS r20 1.1590。
  **结论不翻转（5/8 powered nulls 不变）**，但与 `manuscript.md:177-179` 的明文声明冲突。
- **M3 §19.7 的 survey 设计方差从未实施且未记偏离**（不一致清单 5）。属未执行的预注册设定，
  须走 §19.9 偏离记录并单列报告，或明确声明 SHARE/LASI 的设计变量在本层不可得。

### 次要（Minor）——笔误与披露完整性

- **m1** "Benjamini–Hochberg–Yekutieli" 命名错误（应为 Benjamini–Yekutieli；两处）。
- **m2** 逐队协变量缺失（ELSA 20.5%、CLHLS 7.3%、SHARE `country` 整列空）未披露。
- **m3** MHAS 行数：`sections/methods.md:46` 仍为 78,537，`manuscript.md:174` 已为 15,217；同一稿件两个数。
- **m4** §19.7 提到 "MHAS 的 BMI 用其官方 bmi_imp（10 次插补均值）"，但 MHAS 帧内**没有 BMI 列**，
  该句在本层不可执行（结果上无害，因为 MHAS 无任何可检验单元）。

### 需澄清（Clarification）

- **Q1 审稿/投稿版本到底是哪一份？** `sections/methods.md` 与 `sections/results.md` 至少在
  三处结论性内容上与 `manuscript.md` 不一致：person-wave 总数（2.0M vs 598,386）、
  leave-one-out 结论（相反）、MHAS 计数（78,537 vs 15,217）。本报告已对两版分别标注。
- **Q2 探索性/确认性两家族重叠**（不一致清单 7）：是否刻意让 exploratory 家族含那 18 个确认对？应写明。
- **Q3 r20 的地区亚组检验同属单队效应**：剔 HRS → I² 93.8%→67.9%、Q_between p 8.97e-13→0.688。
  Table 5 对 r20 也给了同一 post hoc 检验，读者会重现 F1 的误读。建议对 r20 一并给 leave-one-out。
- **Q4 ELSA/HRS/MHAS 的年龄缺失是设计使然（不同问卷模块）还是映射失败？** 影响 ELSA r11 这一"powered null"的可信度。
- **Q5 稳健性**：我以 `tol=1e-10` 重拟合（项目 `tol=1e-8`）得到完全相同的 OR/CI；p 值差在第 4–5 位有效数字。
  这项差异不改变任何判定，仅供方法学透明度。

---

## 附：复算产物清单（`outputs/review/recalc/`）

| 文件 | 内容 |
|---|---|
| `r5_01_datahealth.py` / `recalc_datahealth.csv` / `.json` | 数据体检、逐队 flag 流行率与 dtype |
| `r5_02_confirm.py` / `recalc_fit_<COHORT>.json` | 18 个确认单元的独立 logistic 拟合（Rubin 合并 SHARE） |
| `r5_03_meta.py` / `recalc_meta.json` / `recalc_confirmed_18.csv` | REML/DL 合并、I²、Q、预测区间、地区亚组 |
| `r5_04_power.py` / `recalc_power.csv` | 逐对 MDE-OR（发表口径 + 分析 n 口径双呈） |
| `r5_05_audit.py` / `recalc_evidence_audit.json` | 168/18、83/41/26、解锁排序 |
| `r5_06_sens.py` / `recalc_sensitivity.json` | leave-one-out、年龄截尾、BMI 切点互换 |
| `r5_07_denominators.py` / `recalc_personwave.csv`、`recalc_waves.csv`、`recalc_three_state.csv`、`recalc_vs_project.csv` | person-wave 对账、波次存活、BY、与项目表逐单元比对 |
| `r5_08_evalues.py` / `recalc_evalues.csv` | E 值复算 |
| `r5_09_verdicts.py` / `recalc_verdicts.csv` | 29 项主张逐条判定表 |
