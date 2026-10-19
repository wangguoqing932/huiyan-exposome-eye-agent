# 慧眼（huiyan）· 全链路实跑复审 R11
**日期**：2026-10-15　**方式**：从头实跑 + 数据溯源，非目录浏览
**范围**：configs/rules.yaml、src/huiyan_agent、data/raw（NHANES/KNHANES 原始库）、data/datasets、scripts/*、outputs/*

---

## 一句话结论

**工程骨架和流程可复现性是真的（我实跑 8 步全链，产物与你的备份逐字节一致）；
但"科学性"这版过不了同行评议 —— 有 4 个已被实算证明的变量层硬错误，
且"精度 1.0"来自把失败样本剔除出分母，21 条规则里只有 13 条被真正评到，
3 条 A 级规则在 4 个库里无一复证。**

下面每条结论都附可复现证据，不含推测。

---

## 0. 我实际跑了什么

| 动作 | 结果 |
|---|---|
| `pytest` 全量 | 未跑（本次以数据/统计链为主） |
| `scripts/evaluate.py --dataset intval-nhanes` | exit 0；**注意：这一步会静默把 headline 从 survey 方差改回 freq_weights，并删掉 or_svy/q_svy/gold3_svy 三列** |
| `evaluate_knhanes.py` | exit 0，3 s |
| `evaluate_charls.py` / `evaluate_charls2015.py` | exit 0，各 1 s |
| `survey_sensitivity_export.py` → `survey_sensitivity_R5.R`(svyglm) → `apply_survey_variance.py` | exit 0，14 s |
| `rebuild_deliverables_R5.py` → `generate_paper_tables.py` | exit 0 |
| `run_baselines.py --all --provider local --seed 11` | exit 0；本地 qwen3.8-27b（127.0.0.1:8082）在线；seed-11 数值与归档**完全一致** |
| KNHANES Rdata 溯源（R 4.6.1 载入 `KNHANES 2007-2010.Rdata` + 官方字典 + 官方清洗示例代码） | 完成 |
| NHANES XPT 变量跳转逻辑核验（SMQ/ALQ） | 完成 |

**可复现性是好消息**：8 步链重跑后，`nhanes_metrics_v11.json / knhanes_metrics_v11.json / charls_metrics_v11.json /
nhanes_confirmatory.csv / knhanes_confirmatory.csv / generalization_gap_v1.2.*`
的 sha256 前 12 位与 `outputs/_rerun_backup_20261015/` **全部相同**。这条可以写进论文的 Reproducibility。

**但是**：`README.md` 里写的入口（`python scripts/evaluate.py`）**不是** canonical 管道。
单独跑它会让 headline 指标口径回退（见 B1/B7）。缺一个 `make` / `run_all.py`。

---

## A. 硬错误：变量操作化错误（必须修，会直接改变结论）

### A1. NHANES `current_smoking` 的参照组是"已戒烟者"，且 100% 的非吸烟者被静默丢弃 ⛔

`scripts/evaluate.py:143-144`
```python
smk = q("SMQ040")
e["current_smoking"] = smk.isin([1, 2]).astype(float).where(smk.isin([1, 2, 3]))
```

**实测证据**（NHANES 2005-2008，age≥40，WTMEC2YR>0）：

```
SMQ020 x SMQ040
          1.0    2.0    3.0
SMQ020=1  1218   173   2248     <- 一生吸过≥100支
SMQ020=2     0     0      0  (3433 行 SMQ040 全为 NaN)
```
`SMQ040`（现在是否吸烟）**只在 `SMQ020==1` 时提问**。因此 `.where(smk.isin([1,2,3]))` 把 3433 名
从不吸烟者（占队列 48%）全部变成缺失，`current_smoking=0` 的实际含义是**已戒烟者**。

**后果实测**（同一协变量集，结局=VIQ071 自报白内障）：

| 定义 | n | 暴露率 | OR | p |
|---|---|---|---|---|
| **(a) 仓库现状**：SMQ040∈{1,2} vs 仅已戒烟者 | 3362 | **38.3%**（真实应≈20%） | **0.698** | **0.0396** |
| (b) 修正：current vs (never+former) | 6504 | 19.8% | 0.756 | 0.084 |
| (c) former vs never | 3362 | 61.7% | 1.434 | 0.0396 |
| (e) ever vs never | 6510 | 51.7% | 1.111 | 0.294 |

→ 仓库口径给出了一个**统计显著的"吸烟保护白内障"**结论（OR 0.70, p=0.04），
这正是 `direction_review_nhanes.csv` 里 r10 的那一行。**r10 是 3 条 A 级规则之一，
且是全项目机制证据最强的一条（MR 确认因果）**，现在它被一条编码错误变成了"反证"。

**修法**：`never = SMQ020==2`；`former = (SMQ020==1)&(SMQ040==3)`；`current = (SMQ020==1)&(SMQ040∈{1,2})`，
参照组取 never（或直接用三分类哑变量）。修完后 r10/r11/r20 全部要重算。

---

### A2. NHANES `alcohol_intake` 是"一生中是否喝过 12 杯酒"，不是现在饮酒

`scripts/evaluate.py:146-147` 用 `ALQ101==1`。我在 XPT 里核验了跳转：
`ALQ110`（过去一年是否喝够 12 杯）**只在 `ALQ101==2` 时才问**（实测 1355/1355 行），
说明 `ALQ101` 是**终生**门槛题。

**实测**：age≥40 中 `ALQ101==1` 占 **61.8%**。即所谓"饮酒暴露"= 终生曾饮酒，
暴露率 62%、参照组是终生滴酒不沾者。规则 r12 与它的文献主张（饮酒→白内障）指的是**当前饮酒量**。
正确做法是用 `ALQ120Q`/`ALQ120U`/`ALQ130`（当前频次/剂量）。

---

### A3. KNHANES `current_smoking` 用错变量，真正的变量根本没进 frame ⛔

`scripts/evaluate_knhanes.py:47-48`
```python
smk = q("BS1_1")  # 1=current, 2=former, 3=never   <- 注释是猜的
e["current_smoking"] = (smk == 1)...
```

**官方字典**（`11. KNHANES/KNHANES.xlsx` + `数据收集和清洗示例代码.R`，同一数据包）写的是：

```r
dat$BS1_1[(dat$BS1_1==8|dat$BS1_1==9)] <- NA      # 一生吸烟状况
dat$smoke[(dat$BS1_1==2) & (dat$BS3_1==3)] <- 2    # 戒烟
dat$smoke[(dat$BS1_1==2) & (BS3_1!=3)]     <- 3    # 正在吸烟
```
即**当前吸烟要由 `BS1_1==2`（一生吸过）+ `BS3_1`（当前吸烟状况）共同定义**。

**实测交叉表**（`hn08_all`，成人）：
```
BS1_1 x BS3_1        1     2     8
BS1_1=1             31   158     0
BS1_1=2           1510  1146     0
BS1_1=3              0     0  3952   <- 与 BS3_1==8 (비해당) 精确 1:1
```
`BS3_1∈{1,2}`（=正在吸烟）= 2845 人 / 9744 = **29.2%**，男性 53.6%、女性 9.4%
—— 与韩国 2008 年国民统计（约 28%/48%/10%）**吻合**。
仓库用的 `BS1_1==1` 在 40+ 分析样本里只有 **1.53%**（男 2.21% / 女 1.02%）。

**而且 `BS3_1` 根本不在 `data/raw/knhanes_frames/*.csv` 里**（我逐 wave 查过列清单），
所以这个错误**无法在不重建 frame 的前提下修**。

**后果**：KNHANES 层全部吸烟相关配对（r10、r11、r20）**在构造上就不可能出结果**，
必然落进 `uninformative`。这会系统性地制造"零反证"的假象。

---

### A4. KNHANES `alcohol_intake` = "过去一年是否酒后骑自行车"

`scripts/evaluate_knhanes.py:5,49-54` 用 `BA2_2_1`。官方字典原文：

| 变量 | 韩文标签 | 中文标签 |
|---|---|---|
| `BA2_2_1` | 1년간 음주운전여부 - **자전거** | 过去一年酒驾 - **自行车** |
| `BA2_2_3` | … - 오토바이 | … - 摩托车 |
| `BA2_2_5` | … - 자동차 | … - 汽车 |
| `BA2_22` | 1년간 음주차량 동승 횟수 | 过去一年饮酒频次 |

**实测暴露率**：3.01%（男 6.53% / 女 0.36%）—— 与"酒后骑车"完全吻合，与饮酒率（应约 50–60%）差 20 倍。

**更严重的是它产生了"结果"**：KNHANES `alcohol_intake × amd_early`
OR=0.542, 95%CI [0.346, 0.850], p=0.0077 —— 一个无意义暴露进入了 survey 加权金标准，
影响 `uncovered_significant` 与跨库一致性统计。

`BA2_22`（饮酒频次）其实就在 frame 里，代码也写了 fallback，但因为 `BA2_2_1` 存在而永不触发。

---

### A5. KNHANES `vision_impairment_moderate` 是二值"任意视力障碍"标志

`evaluate_knhanes.py:80`：`o["vision_impairment_moderate"] = bi("E_VS_DS")`。
实测 `E_VS_DS`（2008）：`0=4446, 1=22, NA=378` —— 是 0/1 二值变量，
`bi()` 只保留 {0,1}，所以没有严重度分级；KNHANES 侧**根本没有** `vision_impairment_severe`。

而 NHANES 侧是 logMAR 最差眼 + 累积分级 + worst-category 去嵌套（mild/moderate/severe）。
→ **同一"规则-结局"在两层是不同的构念**，r20 的跨层比较不成立。

---

### A6. KNHANES 暴露模块与结局模块落在互斥的 wave 上（结构性不可测）

逐 wave 变量可用性实测：

| wave | E_DRP/E_AMD/E_VS_DS/DH2_lt（眼） | HE_Uacid（尿酸） | HE_hsCRP |
|---|---|---|---|
| 2008–2012 | ✅ | ❌ | ❌ |
| 2017–2021 | ❌ | ✅ | 仅 2017–2018 |

**直接后果**（`knhanes_confirmatory.csv` 实测）：`underpowered` 的 15 对里，
**14 对恰好就是 `uric_acid_elevated × {全部眼结局}` 与 `crp_elevated × {全部眼结局}`**。
其中包含：

- **r01（尿酸×白内障）—— 被你自己指定为 negative_control 的那一条，在 KNHANES 层完全不可测**
- **r06（CRP×晚期AMD，B 级）—— 在 KNHANES 层完全不可测**

这些配对以 `underpowered` 被剔出所有分母，即**从未有机会成为"反证"**。

另外：README / `dataset.meta.json` 声称"KNHANES 1998–2024 全集"，实际 frame 只有
**10 个 wave（2008–2012 + 2017–2021），2013–2016 缺失**。

---

### A7. KNHANES 尿酸 fallback 指向"砷"（潜在雷）

官方字典：`HE_UAScr` = 비소(요네즈법 보정, ICPMS방법) = **砷（Yonezawa 校正，ICP-MS）**；
真正的尿酸 `HE_Uacid` 只有 2016+ 才有。

`evaluate_knhanes.py:31-34` 注释写"Uric: HE_UAScr (2008) or HE_Uacid (2017+)"，
且 fallback 顺序为 `first("HE_Uacid","HE_UAScr","HE_UAScr_AAS")`。
**这次的 concat 恰好让 `HE_Uacid` 列存在（2008–2012 全 NaN），所以砷没有真的被当成尿酸用**
—— 属于"侥幸正确"。但注释错误使这条链离"把砷按 mg/dL 尿酸切点 6.8 分类"只差一次改动。
实算 `HE_UAScr` 值域到 1478，绝不可能是 mg/dL 尿酸。

---

## B. 统计与指标口径问题

### B1. 同一个系统、同一份数据，有**两套互相矛盾的 precision** ⛔（评审致命）

| 出处 | 分母定义 | NHANES | KNHANES | CHARLS |
|---|---|---|---|---|
| `*_metrics_v11.json` / `performance_matrix.csv` | 仅 replicated+contradicted（**剔除 uninformative**） | **1.0** | **1.0** | n/a |
| `*_summary.json` / fused 表 | uninformative 记作 **FP** | **0.294** | **0.200** | 0.0 |

两者同时出现在 `outputs/tables/performance_by_dataset.csv`。
`scripts/run_baselines.py:271` 与 `run_fused_system_v3.py:127` 都把 `gold3 != "replicated"` 记 FP；
`scripts/evaluate.py:424` 的 `prec = rep/(rep+con)` 把 uninformative 排除。

→ 这不是"两种合理口径"，是**在评基线时把失败算失败、在报自己成绩时把失败算不存在**。
审稿人第一眼就会看到 1.0 与 0.294 并存。**必须选一个并预注册**，建议：
主指标用"uninformative 记 FP"的保守口径，另报一个 power-aware 版本（见 B2）。

### B2. `uninformative` 把"真无关联"和"效能不足"混为一谈，且从不做效能分析

NHANES 14 对规则配对里 9 对 uninformative；KNHANES 10 对里 8 对。
`detect_separation` + `n<200 / ny<30 / nx<30` 只是粗筛，**没有任何最小可检测 OR、
没有 post-hoc power、没有 equivalence/ROPE 检验**。
所以 headline 的"0 contradicted"几乎不携带信息 —— 它只说明"没测出反向"。

### B3. 跨库"金标准"自身只有 60% 一致，却被报成 gap = 0

`generalization_gap_v1.2_summary.json`：`n_common_tested_pairs: 48, gold3_concordant_pairs: 29`
→ **同一配对在 NHANES 与 KNHANES 的三态标签只有 60.4% 一致**。
而 headline 的 `precision_rule gap = 0.0`、`coverage gap = -0.003` 是在能算的子集上得出的。
**40% 的标签分歧才是真正该报的"泛化落差"**，现在被 0.0 掩盖了。

### B4. 两层的协变量集不同 → 估的不是同一个量

- NHANES：age, age², sex, RIDRETH1(种族), INDFMPIR(贫困收入比)（我核验了 `survey_pairs_R5/nhanes__*.csv` 列）
- KNHANES：**只有 age, age², sex**；`edu`/`incm` **在 frame 里根本不存在**

对吸烟、饮酒、膳食这类行为暴露，**SES 是首要混杂**。所以"NHANES 复证 / KNHANES 未复证"
不能解释为人群差异，只能说明两个模型在估不同东西。

### B5. 9 个暴露之间互不校正

每个配对单独建模。吸烟/饮酒/BMI/血脂/血糖彼此强相关，
行为类暴露的 `uninformative` 有很大一部分可以由互混杂解释。

### B6. BHY 的分母是被效能筛过的子集

`fdr_bhy` 只对 `status=="tested"` 的行做校正，即 q 值依赖于一个**任意的效能过滤**，
而不是实际考虑过的假设族。且三个数据集/四个层各自校正，跨层多重性未处理。

### B7. survey 方差口径的工程脆性

R5 改成 svyglm 作 headline 是对的。但：
1. 单跑 `evaluate.py` 会**静默回退**并删掉 svy 列（我实测复现），canonical 顺序没有任何保护；
2. NHANES 合并 2005-2006 + 2007-2008 两个 2 年周期，权重用的是 `WTMEC2YR`，
   4 年合并应使用 `WTMEC4YR` 或把 2 年权重除以 2；
3. CHARLS 没有 PSU/strata 变量，`performance_matrix.csv` 的 method 文案已诚实回避，
   但 fused 表里 CHARLS 的 F1=0.0 仍与其它层并列展示。

### B8. 文献层 `precision_lit = 0.889` 用的是同一套有利分母

`literature_validation.py:371`：`prec = rep/(rep+con+mix)` —— 排除 uninformative 与 null_dominant。
19 条主规则中有 4 条被排除在分母外。

---

## C. 设计层与声称层问题

### C1. 21 条规则里只有 13 条被真正评到；8 条从未进入任何一层 ⛔

实测规则覆盖（`status=="tested"` 的 `rule_ids`）：

| 从未被任何层测到的规则 | 级别 |
|---|---|
| r07 维生素D×DR | B |
| r08 低抗氧化物×白内障 | B |
| r09 地中海饮食×晚期AMD | B |
| r16 PM2.5×青光眼/IOP/CDR | B |
| r17 PM2.5×早期AMD | B |
| r18 紫外线×白内障 | B |
| r19 促炎饮食×DR | C |
| r21 PM2.5×视力障碍 | B |

**8/21 = 38% 的规则（其中 7 条 B 级）从未被验证过任何一层。**
而论文的主张是"规则仅由文献构建，性能在 NHANES→KNHANES→9 国队列三层独立验证"。
这个落差必须显式声明，否则等于漏报。

### C2. 3 条 A 级规则在全部 4 个层里无一复证

| 规则 | NHANES | KNHANES | CHARLS2011 | CHARLS2015 |
|---|---|---|---|---|
| r10 吸烟×白内障 (A) | uninformative | uninformative | uninformative | — |
| r11 吸烟×晚期AMD (A) | — | uninformative | — | — |
| r13 BMI×白内障 (A) | uninformative | uninformative | — | — |

**唯一复证的 3 条规则是 r02/r03/r04 —— 全部是"血糖 → 糖尿病眼病"。**

### C3. "复证"的配对高度同义反复

NHANES 的 5 个 replicated 配对 = hyperglycemia×cataract、hba1c×retinopathy、
hba1c×dr_npdr、以及它们的子集。
KNHANES 的对应 OR 是 **25.0（hyperglycemia×retinopathy）与 28.4（hba1c×retinopathy）**。

这个量级不是流行病学效应量，是**定义重叠**：HbA1c≥6.5% / FPG≥126 mg/dL 就是糖尿病的诊断标准，
DR 是糖尿病并发症。也就是说：**"精度 1.0"完全建立在暴露即疾病的配对上；
而机制证据最强的 A 级规则全部失败。**

这应该是 Discussion 的核心，而不是被 1.0 盖住。至少要做敏感性分析：
剔除"暴露-结局存在定义包含关系"的配对后重算。

### C4. r22 是测试集泄漏（你自己在 rationale 里写了）

`configs/rules.yaml:282` r22 rationale 原文：
> "NHANES 确证（单库横断面，OR≈1.47）方向一致。**规则纳入属数据驱动的探索性扩展**"

即在看到 NHANES 内部验证结果后新增的规则，然后它参与了 NHANES headline 指标。
必须二选一：① 从 headline 剔除、单独作为探索性发现报告；② 冻结规则集后重跑全部层。
R4 审计把它当成"引文张冠李戴"，但真正的问题是**它不该进 headline**。

### C5. `negative_control` 用法错误

r01（尿酸×白内障）被标 `negative_control: true` 并从 headline 分母剔除
（`compute_metrics_v11` 的 `t_main = t[~nc_mask]`）。但它是一条**带机制论证的"风险升高"主张**，
不是证伪终点；其自身文献层结论是 `mixed_lit`（8 一致/3 相反/3 零）。

阴性对照应是**先验不可能有关联的暴露-结局对**，期望结果是零。
把一条声称有关联的规则标成阴性对照再排除，等于**预先删掉一个潜在假阳性**。
在 fused G1/G2 里它进一步变成 `nc_abstain`（弃权），直接改善精度。

### C6. 文献层不是"外部验证"，是同义反复

`scripts/literature_validation.py` 的流程是：对每条规则用 `暴露词 AND 结局词` 检索 PubMed，
取前 40 条，让**同一个本地 qwen** 逐篇判方向，再按
`n_conc≥2 且 n_conc>n_disc 且 n_conc≥n_null` 判 `replicated_lit`。

问题：
1. 规则本来就来自这批文献；排除规则自引 DOI 并不能消除循环；
2. PubMed 相关性排序天然把最对题的（通常阳性）研究排在前 40；
3. 判定门槛极低（2 篇一致即可），且**没有任何系统检索策略/时间窗/偏倚评估/GRADE**；
4. **近零反证率**（r02 27:0、r03 10:0、r04 10:0、r05 16:0、r13 8:3、r06 6:1）
   强烈提示抽取提示词存在一致性偏置 —— 提示词把规则主张原文交给了模型；
5. `outputs/tables/performance_by_dataset.csv` 把这一行标为 `external_validation_lit`，
   读者会误认成独立验证（代码 note 里写对了，表格标签写错了）。

**建议**：改名为 "literature consistency audit"，并从"验证层"表格移到敏感性分析；
补一份真正的系统检索（PRISMA 式，预注册检索式 + 时间窗 + 双人核对）。

### C7. "9 国老龄队列"严重缩水

`dataset.meta.json` 声明 9 库 / 120 对；实测只有 **CHARLS 2011（14 对，4 对可判，0 informative）
+ CHARLS 2015（12 对，3 对可判，0 informative）**，precision 未定义，fused 系统在 CHARLS 上 **F1=0.0**。
所谓"三层独立验证"实际是：1 个内部横断面 + 1 个外部横断面 + 1 个部分队列，
第三层贡献 0 个有效标签。

### C8. 融合系统的增益不显著，且消融全是无效或有害

`fused_system_R6_summary.json`：G2 vs G0 的 McNemar **p=0.50**；
G3（文献共识门）与 G2 完全相同（no-op）；G4（证据直推）**有害**（F1 0.5→0.417）；
G5a/G5b 语义层在 tau 0.45/0.55/0.65 下结果完全相同，G5b 触发数为 0。
即：**"规则引擎+知识图谱+LLM 仲裁"的混合架构，相对裸规则引擎没有可检出的增益。**
这可以诚实写成阴性结果，但不能写成"混合系统优于基线"。

### C9. 基线被系统性削弱 + 依赖机器状态

- LLM 基线 `temp=0.7`，而系统仲裁器 `temp=0.0`；
- naive_rag / lightrag 只看到 **500 字符**证据（3 条 × 200 字），提示词还写着
  "If the evidence does not mention the relationship, answer NO"；
- 基线需要 `LOCAL_LLM_BASE_URL=http://127.0.0.1:8082/v1`（qwen3.8-27b）——**不在仓库里**；
- 我重跑 seed 11 时数值逐位一致，但日志显示 **LightRAG 查询大量命中
  `kv_store_llm_response_cache.json`（113 MB）**，"复现"实质是**缓存回放**。
  需要：模型/权重哈希、容器镜像、冷缓存重跑结果、cache 策略说明。

---

## D. 工程与交付物问题

| # | 问题 | 证据 |
|---|---|---|
| D1 | canonical 管道是 8 步手工链，README 写的入口会破坏 headline | 实测：单跑 `evaluate.py` 后 metrics 从 survey 版变 freq 版 |
| D2 | `run_baselines.py` 以 append 模式写 `baseline_predictions.jsonl`，代际混叠 | 我这次跑完从 1600 行涨到 1920 行，已还原；R4 也报过同一问题 |
| D3 | 原始数据路径硬编码在 `E:\BaiduNetdiskDownload\...` | `evaluate.py:244`（NHANES）、`evaluate_charls.py:27`、`evaluate_charls2015.py:27` |
| D4 | CHARLS svyglm 从未运行过（无 PSU/strata），但表格里与其它层并列 | `charls_metrics_v11.json` 无 `variance_standard`；`rebuild_deliverables_R5.py:84-87` 已注记 |
| D5 | `outputs/` 内混入 `_rerun_backup_*`、`lightrag_index_pre_r4_backup-*`（约 700 MB） | 会被当交付物一起提交 |
| D6 | 环境是 venv Python 3.10.4（skill 建议 3.11+）；`openpyxl` 未装 | 实测 ImportError |
| D7 | KNHANES frame 未包含 `BS3_1` / `edu` / `incm`，无法在不重建 frame 的前提下修 A3/B4 | 列清单实测 |
| D8 | README 说 12 条规则，rules.yaml 实际 21 条；README 说 NHANES 1999-2008（5 周期），代码只用 2005-2008（2 周期） | `evaluate.py:245` `CYCLES={"2005-2006":"_D","2007-2008":"_E"}` |

---

## E. 建议的修改顺序

### 第 1 优先级 —— 不修就无法投稿（改结论）
1. **修 A1**（NHANES 吸烟参照组）→ 重跑 r10/r11/r20 全部层。
2. **重建 KNHANES frame**，纳入 `BS3_1`、`edu`、`incm`；**修 A3**（吸烟）、**A4**（饮酒，
   改用 `BA2_22`/`BA2_12-14`）、**A5**（视力障碍，接受"无法分层"并降级 r20 的跨层主张）。
3. **统一 precision 口径（B1）**：写进 analysis_plan，预注册，重算所有交付表。
4. **把 uninformative 的两种语义分开（B2）**：报告 post-hoc power / 最小可检测 OR；
   主表用"uninformative=未复证"的保守口径。
5. **r22 出 headline（C4）**；**r01 不再是 negative control（C5）**，改为真正的证伪配对
   （例如某暴露 × 与机制无关的眼病）。

### 第 2 优先级 —— 改主张与表述
6. 显式声明 **8/21 规则从未被评估（C1）**、**A 级规则 0 复证（C2）**、
   **复证集中于血糖-糖尿病眼病同义反复（C3）**。
7. 文献层改名 + 移出"验证层"（C6）；补系统检索。
8. 队列层如实降级为"CHARLS 可行性层"（C7）。
9. 融合系统写成"相对裸规则引擎无可检出增益"的阴性结果（C8）。
10. 报 **40% 跨库标签分歧**（B3），并把 gap=0 的写法撤掉。

### 第 3 优先级 —— 工程与可复现
11. 写 `scripts/run_all.py` 或 Makefile，把 8 步链固化；给 `evaluate.py` 加"会破坏 headline"的守卫。
12. 数据获取脚本化（下载 + 校验和），去掉 `E:\` 硬编码。
13. 基线：模型哈希 + 冷缓存重跑 + 统一温度；补 5 seed 完整表。
14. 清理 `outputs/` 里的 backup / index 目录；`baseline_predictions.jsonl` 改为覆盖写或加代际字段。
15. 统一 README / meta / 代码的口径（规则数、周期数、队列数）。

---

## F. 这版做对的地方（建议保留并写进论文）

1. **全链可复现**：8 步链重跑与备份逐字节一致（本次实测）。
2. **svyglm 作 headline + freq_weights 作敏感性**：方法学正确，且注记清晰。
3. **诚实的 KNHANES 8/9 码处理**：把"未检查"与"阴性"分开，是 R5 的正确修复。
4. **阴性结果如实落盘**：G3 no-op、G4 harmful、G5b 零触发都写进了交付表 —— 很难得。
5. **direction_audit 双阈值设计**（记录任意反向 A 级配对 + 仅在 ≥2 显著反向时 quarantine）思路正确。
6. **`prec` 用 Clopper-Pearson 而非 bootstrap**：小 n 下选得对，理由也写清楚了。
7. **fail-loud 纪律**：`run_baselines.py` 的 canary + `valid=False` + error 落盘，比静默变 NO 好得多。

---

## 附：本次审计产生的可复现脚本

全部在 `.audit_tmp/`（可删）：
`smoke_refgroup.py`（A1 实算）、`knhanes_smoke_fix.py`（A3 实算）、
`knhanes_prevalence.py`（KNHANES 暴露/结局率体检）、`rule_coverage.py`（C1 规则覆盖）、
`cmp2.R` / `bs.R` / `knhanes_dict.R`（KNHANES 官方字典与 Rdata 溯源）、
`restore_chain.log`（8 步链重跑日志）。

**状态说明**：审计过程中的实跑覆盖了 `outputs/confirmatory/*` 与
`outputs/baseline_predictions.jsonl`，已全部恢复到审计前的 canonical 状态
（前者经 8 步链重跑、sha256 与 `outputs/_rerun_backup_20261015/` 一致；
后者从 `baseline_predictions_valid.jsonl` 还原至 1600 行）。
