# R4 审稿报告 · BMJ×Nature Medicine 双眼镜（证据等级与患者价值 × 创新与可复现）

**审稿人角色**：全场第二双眼睛。BMJ 眼镜看证据等级、患者重要结局与临床路径；Nature Medicine 眼镜看创新增量与别人能否复现。
**审稿日期**：2026-10-15
**送审材料**：manuscript.md（1104 行）、sections/{abstract,introduction,methods,results,discussion}.md、citation_pool.json、docs/analysis_plan.md（602 行）、outputs/cohorts/*（8 个文件）、figure_table_qc_report.md、figure_visual_inspection.md、package_manifest.json、supplementary_material.md（4104 行）、journal_guidelines_snapshot.md

**独立核验动作**：Crossref REST 实查 6 条 DOI（C002/C005/C018/C022/C027/C029）；DataCite 实查 CLHLS 数据沉积 DOI；逐行复算 cohort_rule_results.csv、cohort_power.csv、cohort_heterogeneity.json、cohort_influence.csv、evidence_audit.json、cohort_meta_summary.csv。

---

## 总体评价

这篇稿子的**队列层**（八队列、18 个预注册规则×队列单元、合并估计 + 预测区间 + E 值 + 效能表 + 测量可得性审计）是一个真实、可用的贡献：它用一个干净的实证案例说明了"数复现次数"作为可迁移性判据过于宽松，并且把"证据基础测不了什么"做成了 168 格的量化审计——后者是我在这次审稿中看到的最有原创性的一块。但**整篇稿子的包装与实现之间有一道明显裂缝**：作者自家的分析计划（§0、§13、§19.1）白纸黑字记载"规则集 v1.2 是在看过 NHANES 确证结果之后被修改的（测试集拟合）""NHANES 已被 v1.2 拟合污染"，而稿件把 NHANES 当作内部验证层、把 F1 = 0.435 当作系统性能来报告，且**通篇未披露这一时点事实**；这是我这副眼镜下唯一一条致命问题。此外，标题与摘要的"2.0 million person-waves"把插补副本当行数计入（真实唯一 person-wave ≈ 66 万），Table 6 中 SHARE 的 n 与同层另一份结果文件相差正好 5 倍，Discussion 的留一法结论与自家 `cohort_influence.csv` 直接矛盾。

**投票：大修（Major Revision）。**
补充条件：如果作者坚持保留 Figure 2 与 "System performance" 一节的原样表述（在被自家协议判定为污染的金标准上宣称"优于三个基线"），本刊应转为拒稿；把系统层整段撤下或改为独立技术报告后，本文的核心结论（表 5–7、图 6–8）是可修的。

---

## 领域贡献判定

**判定：递进（incremental）＋局部原创，但存在"包装大于内容"的结构性问题。不是重复，也谈不上突破。**

### 往前走的那一步（真贡献）

1. **测量模态可得性审计（Table 7 / evidence_audit.json）是真新的东西。** 把"不可检验"从一句 limitations 变成 21×8 = 168 格的可行性矩阵，并给出 83/41/26 的失败归因（双侧缺失／暴露缺失／结局缺失）与逐模态解锁数，这个"证据基础体检表"在其他疾病领域可直接复用，是本文最可能被引用的部分。换算正确：18/168 = 10.714%。
2. **"复现计数 vs 预测区间"的判据冲突被实证化了。** 预注册判据判 2/6 可迁移，异质性感知判据判 0/6，两判据在同一批数据上分道扬镳——这个"判据本身是结果"的写法是有价值的，且作者把两个裁决都报了出来（Discussion "A criterion that was too permissive"），态度诚实。
3. **一个方向翻转的干净案例**（r10 吸烟×白内障：SHARE 1.11 vs CLHLS 0.748），提示"合并会把真实分歧平均成一个谁都不描述的估计"。

### 包装大于内容的部分（必须点破）

1. **方法学内核是教科书内容，且未与真正的文献对话。** "I² 90–94% 时不要报合并值、要报预测区间" 是 2009 年 Higgins 与 2016 年 IntHout（BMJ Open，明确呼吁"常规报告预测区间"）的既有结论；稿件只引了 C026（I² 原始方法）与 C027（一篇口腔正畸杂志的统计方法短文），**没有引 IntHout 2016、也没有引任何把预测区间写进报告规范的文件**。把"规则基座"这个词套上去，属于重新命名而非推进。
2. **系统层（Figure 1–5、Table 1、"System performance"）不是贡献，是负债。** 一个确定性规则引擎 + LightRAG + LLM 仲裁在没有干净测试集的前提下比出 F1 0.435，分析计划 §13 已判定"三库 gold 不得用于策略调参（NHANES 已被 v1.2 拟合污染、dev 集金标准为 rule_defined 属循环结构不可用作调参集）"，§15 又结论"性能上限的三重约束…进一步提升非推理层工程"。也就是说作者自己已经证明了系统层无可评之处，稿件却把它作为 Methods 的一节和 Results 的一节保留，且摘要与标题完全不提它。**摘要不提、正文大篇幅写**，本身就说明作者知道它撑不住。
3. **"八队列、三大陆、200 万人"的叙事收益被数据打了折。** 真正贡献规则×队列单元的是 7 个队列（MHAS 贡献 0 格），MHAS 只进入 168 的分母；SHARE 贡献的 1,693,515 行里 5/6 是插补副本。

### 换个人能否复现

**目前不能。** 详见"透明度与可复现审查"：无 Data Availability、无 Code Availability、无机器可读变量映射、69 条操作化更正（C1–C69）只存在于一份中文手写台账，且八个队列全为需注册/申请的受控微观数据。这不是"复现门槛高"的程度问题，是"第三方拿到数据后仍无法重做"的可复现性缺口。

---

## 透明度与可复现审查

### 1. 数据与代码可得性：缺失（重大）

- 全文 **没有 Data Availability Statement，也没有 Code Availability Statement**（grep 全稿无 "data availability/repository/github/zenodo/OSF"）。Methods 只有一句 "Rule definitions, cohort variable maps and every correction applied to them are version-controlled in the repository"——**没有仓库地址、没有 DOI、没有哈希**。对一个把"可复现"写进标题气质的稿件（"pre-registered cross-cohort evaluation"），这是硬伤。
- 8 个队列的**获取门槛一个都没写**。实际门槛（据 supplementary S1 台账反推）：
  | 队列 | 获取方式 | 额外门槛 |
  |---|---|---|
  | SHARE | 官网注册、科研用途免费 | 官方 `gv_*` 派生模块的使用须声明（稿件只在 Methods 一处提到） |
  | HRS | 官网注册 | 需避开 RAND Fat File（稿件已声明） |
  | ELSA | UK Data Service，End User Licence | 眼科结局取自 `wave_2_derived_variables.dta` |
  | KLoSA | 韩国 KEIS 站点 | 韩文问卷/码本、cp949 编码 |
  | LASI | 需注册 | 多选字符串型结局需靠指示变量标签解码 |
  | MHAS | 官网注册 | 官方 constructed / imputation 派生文件 |
  | CLHLS | 北大开放数据（DOI 10.18170/DVN/MKB1LF 等） | 中文 docx 码本、逐波尺度不同 |
  | CRELES | ICPSR / Harvard Dataverse | 部分变量 1–7 尺度本地无法解码 |
- **具体修改建议**：新增 Data Availability（逐队列写清提供方、访问途径、注册要求、所用版本与访问日期、许可类型）与 Code Availability（frame 构建脚本、变量映射、三态判定、合并/异质性/效能脚本，打 tag 并给 Zenodo/OSF DOI）；把 `docs/cohort_variable_mapping.md` 的 69 条更正转为机器可读的 YAML/CSV 映射表（字段：cohort, flag, source_file, source_var, value_label_source, gate_var, missing_codes, wave, correction_id）。这是把"可复现负担"变成"可复现资产"的最低成本动作。

### 2. "仅用原始文件、排除 harmonized"：设计上是优势，交付上是不可复现的负担（重大）

**作为设计选择，我支持它，理由与作者一致**：harmonized 文件编码的是另一个团队的操作化，用它做"规则可迁移性"检验会把问题变成循环——你想知道的是"我的构念在别人的人群里成不成立"，而不是"两个团队的操作化一不一致"。作为审稿人我不会要求作者改用 harmonized 文件。

**但它现在是负担，原因有三，且第三条最致命：**

1. **门槛被抬到了"必须做一遍同等强度的码本考古"。** 台账记录了 69 条更正中至少 6 类真实错误（C1 类条件题错误在本项目出现 5 次；`to_numeric` 类别型陷阱出现 3 次并一度让 ELSA 整个眼科模块"消失"；CLHLS 2000 波 `g1` 少一级导致 1,499 人错分；KLoSA 官方值标签把饮酒标签贴到吸烟变量上）。这些都不是"读一遍码本"能避免的，而**任何第三方必须在取得 8 套受控微观数据后把这条路重走一遍**——审稿人做不到，因此本文的核心结果在评审阶段**原则上不可验证**。
2. **"raw only"把唯一的共同测量骨架拿掉了，而稿件没有为可比性提供替代证据。** 排除 harmonized 之后，"同一 flag 在不同队列来自完全不同的题项"这件事就没有任何量化陈述。CLHLS 的 `diabetes` 是"医生是否告知"（1.36%），SHARE/KNHANES 是测量或混合口径（13.6%）；白内障在 5 个队列分别是自报诊断/派生临床条目，AMD 只有 ELSA。**作者在正文里承认"自报 ≠ 测量"，但从未量化测量差异有多大**，于是 r10 的方向翻转既可以是真实效应修饰，也可以是暴露/结局分辨率差异——作者自己在 Discussion 里承认分不清，却没有把"测量不等价"作为第四个候选解释系统地摆出来。
3. **可复现的最佳实践是"双轨"而不是"单轨"。** 具体建议（不影响现有结论、成本可控）：(a) 保留 raw-only 为主分析；(b) 对 18 个可行单元中**能同时在 harmonized 版本里构造出来的那些**（我判断 r20 吸烟×视力、r13 BMI×白内障、r02 糖尿病×白内障至少部分可做）做一次 harmonized 平行分析，报告两次结果的标签一致率——这恰好把"raw-only 是否值得"变成可检验的经验问题；(c) 补一张**逐 flag 的题项对照表**（同 flag → 8 队列各自的问题原文/量表级数/缺失码/参考期）与一个简单的"构念距离"评分，作为 Table 2 的补充。

### 3. 方案预注册：存在但不能验证（重大）

- analysis_plan.md 是**项目内文件**，无 OSF/注册号、无时间戳、无版本哈希（§0 里只有"落盘"叙事）。作者在 §12/§13/§15 三处自己承认"落盘先于运行**无独立可证证据**，证据等级降格为叙事自洽"。也就是说本文标题里的 "pre-registered" 目前是一个**自称**，不是可核验事实。
- 更棘手的是 §0 的偏离记录本身：**规则集在确证运行（2026-10-11 20:59）之后、基线运行之前被修改**（2026-10-12 07:12），依据来自确证运行的 gold-positive 结果，作者自己定性为 **test-set fitting**，并写明 "R=1.000 是构造的，不是性能提升"。这条记录存在于内部文档，**稿件正文完全没有对应披露**。
- 具体修改建议：(1) 把 analysis_plan 全文（含全部更正）作为 Supplementary 一并投出，并补一个带日期的公开预注册（哪怕事后补登 OSF 并标注 "registered after data access"）；(2) Methods 增一节 "Rule-set version history and protocol deviations"，逐条列出 v1.1→v1.2 的 4 处改动、时点、依据、以及在哪些层产生了影响；(3) Results 的主报告改为 **v1.1 与 v1.2 双列**，并用同一金标准重放 v1.1（现在 v1.1 replay 只在 Figure 2 图例里出现，标 0.111，且被标注为"不同金标准不可比"——作者知道它不好看，就把它藏进了图例）。

### 4. 8 个队列的数据获取门槛（逐队列，供作者补写）

见上表 1。额外三点必须在稿件中写明：CLHLS 分析使用了 1998–2018 共 8 波，而公开沉积 DOI（10.18170/DVN/MKB1LF）题名覆盖 1998–2011，需补 2014/2018 波的来源与版本；KLoSA 无英文队列简介文章（这一点作者的判断是对的，见引文抽查）；CRELES 的 `c55/c56` 本地不可解码，作者按纪律弃用并只贡献 `c54='Is blind'`——这个处置是对的，但必须写进 Methods 而非只留在台账。

---

## 关键数字抽查表

复核方式：直接读取 `outputs/cohorts/*` 与 `outputs/paper/manuscript.md` 逐字段比对。✅=相符；⚠=数值相符但表述/方法有问题；❌=与原始值不符。

| # | 数字 | 稿件值 | 原始值（出处） | 判定 |
|---|---|---|---|---|
| 1 | 可检验规则数 | 6 / 21 | `evidence_audit.json`: `rules_testable_somewhere=6`, `rules_total=21` | ✅ |
| 2 | 可行单元数 | 18 / 168 = 10.7% | `evidence_audit.json`: `feasible_cells=18`, `possible_cells=168`, `0.1071`；blocked 83+41+26=150；`feasible_pairs` 18 条与 Table 6 的 18 行逐条相同 | ✅ |
| 3 | r10 合并 OR | 0.84 (0.67–1.05) | `cohort_heterogeneity.json`: 0.839 (0.6698–1.0511)；`cohort_meta_summary.csv` 0.839 | ✅ |
| 4 | r10 地区亚组 p 与分组 OR | p<0.0001；Europe 1.08 / Asia 0.75 / Americas 0.70 | `p_between=4.529e-06`；per_group 1.0817 / 0.748 / 0.7023 | ✅ 数值相符；⚠ **Europe 组是 SHARE(1.109) 与 ELSA(0.7675) 两个方向相反队列的合并值**，"地区差异"解释不成立 |
| 5 | r02 三队列 OR | LASI 1.88 (1.76–2.00)；SHARE 1.75 (1.69–1.82)；CLHLS 3.59 (2.62–4.91) | `cohort_rule_results.csv`: 1.8782 (1.7646–1.9991)；1.7539 (1.6908–1.8194)；3.5887 (2.6244–4.9074)；CRELES 1.3116 (1.0705–1.6069), q=0.05059 | ✅ |
| 6 | r02 合并 OR 的 95% CI | 摘要 1.33–2.88；Table 5 1.32–2.88 | 1.3245–2.8828 | ⚠ 摘要写错（1.3245 舍入为 1.32），且**摘要在这一行与 Table 5 自相矛盾** |
| 7 | E 值 | 2.01 (1.57)、1.46 (1.25)；另 r12 CLHLS 1.78 (1.36)、r02 CLHLS 6.64 (4.69) | `e_values`: 2.008 (1.566)、1.457 (1.248)、1.776 (1.361)、6.637 (4.689) | ✅ 数值相符；⚠ 方法未声明，且把 OR 直接当 RR 代入（CLHLS 未暴露患病率 17.8%，属常见结局）→ 换算后约 1.87 / 4.35，**方向上是高估稳健性** |
| 8 | 有检验力的零结果数 | 5 / 8 (62.5%) | `cohort_power.csv`：8 条 uninformative 中 `powered_null=True` 5 条（CRELES r10、CRELES r13、ELSA r10、ELSA r11、SHARE r12） | ✅ 复算相符；⚠ 该 5 用的是"CI 排除自身 MDE"这一定义，**预注册 §17 的定义是 MDE-OR ≤ 2.0，按预注册应为 8/8** |
| 9 | 样本量（标题/摘要） | 2.0 million person-waves | SHARE 行数 1,693,515 ÷ 5 个插补副本 = **338,703** 唯一 person-wave；八队列合计 **661,706**；唯一人数 **285,879** | ❌ 高估约 3 倍（把 5 个插补副本当独立 person-wave 计数） |
| 10 | SHARE 分析 n | Table 6：r02 = 1,686,370；r10 = 710,420；r20 = 711,145 | `cohort_rule_results.csv` 同层同对：r02 = **337,274**；r10 = **142,084**；r20 = 142,229。放大倍数精确为 5（`cohort_power.csv` 用了 ×5 的值） | ❌ **同层两份交付物相差正好 5 倍，进入稿件的是错的那一份**；且与正文"an imputation replicate is never counted as an independent person"直接矛盾 |
| 11 | 留一法结论 | "Leave-one-cohort-out analysis shows the r10 regional split is not produced by any single cohort" / "no single cohort drives the pattern" | `cohort_influence.csv`：r10 剔除 SHARE → 合并 OR **0.747 (0.6636–0.841)**、**I² = 0.0%**（原 91.0%）；剔除其他任一队列 I² 仍为 86.6–93.0% | ❌ **与自家结果文件直接矛盾**：SHARE 单独贡献了 r10 的全部异质性 |
| 12 | 无可检验条柱的规则数 | Figure 8 图例："13 rules have no bar at all: 5 fundus + 1 tonometry + 3 geocoded + 3 blood + 2 dietary"（分项合计 14） | 21 − 6 = **15**；正文 Methods 的清单为 15（含 r05 lipid panel） | ❌ 图例总数错（应为 15），分项也漏了 r05 |

### 抽查附带发现（未列入上表但必须改）

- **Table 4 / Results 文本**：KNHANES `total_pairs=352`，而 `tested=301`、`underpowered=50`，301+50 = 351 ≠ 352（差 1）。
- **Figure 7 图例**：NHANES n=17、KNHANES n=13（合计 30），但 Table 4 的规则对已检验数为 16 与 15（合计 31）。两处对"规则相关已检验对"的计数不一致。
- **Table 5 的 "Regional p"**：r12 与 r13 的 regional p（0.0273、0.0272）与同一行的 Q p **完全相同**。k=2、每地区各 1 队列时，组间 Q 恒等于总 Q（自由度都是 1），这是同一个检验被呈现为两条独立证据。
- **Table 6 vs 结果文件**：ELSA r10 n = 4050（Table 6）vs 4013（`cohort_rule_results.csv`）；ELSA r11 = 4028 vs 3991。同一行相差 37，说明效能分析与估计用了不同的分析样本。
- **r07 的不可检验归因非互斥**：正文把 r07 同时算作"需眼底影像"与"需血液指标"，因此"5+1+3+3+2(+1)=15"不是划分，只是计数；Table 7 的细胞级 blocked_by 才是正确的，规则级分类需注明可重叠。

---

## 引文抽查表

引用池 24 条标称 Crossref+OpenAlex 双源核验。我独立用 `api.crossref.org/works/<doi>` 实查 6 条（超过要求的 5 条），全部 HTTP 200、题名逐字相符：

| 池 ID | DOI | 池中题名 | 独立核验结果 | 判定 |
|---|---|---|---|---|
| C002 | 10.1038/s41591-021-01229-5 | DECIDE-AI: new reporting guidelines… | *Nat Med* 2021;27(2):186–187，题名逐字相符，作者 "The DECIDE-AI Steering Group" | ✅ DOI 真实、题名相符 |
| C005 | 10.1093/biomet/26.4.404 | THE USE OF CONFIDENCE OR FIDUCIAL LIMITS… | *Biometrika* 1934;26(4):404–413，CLOPPER C. J. / PEARSON E. S. | ✅ |
| C018 | 10.1167/iovs.12-9820 | Smoking and Risk of Age-Related Cataract: A Meta-Analysis | *IOVS* 2012;53(7):3885，Ye J. 等 | ✅ |
| C022 | 10.7189/jogh.08.010803 | Prevalence, risk factors and burden of diabetic retinopathy in China… | *J Glob Health* 2018;8(1):010803，Song P. 等 | ✅ |
| C027 | 10.1016/j.ajodo.2019.12.011 | Prediction interval in random-effects meta-analysis | *AJODO* 2020;157(4):586–588，Spineli & Pandis | ✅ 题名相符；⚠ 是口腔正畸刊的统计方法短文，作为"预测区间"的唯一依据偏弱，应补 IntHout 2016 (BMJ Open, 10.1136/bmjopen-2015-010247) 与 Higgins 2009 (10.1111/j.1467-985X.2008.00552.x) |
| C029 | 10.1093/eurheartj/ehae295 | Genetic predictors of traits in elderly subjects: risk of survival bias and reverse causation | *Eur Heart J* 2024;45(24):2155–2157，Burgess & Zhou | ✅ 题名相符；⚠ 内容是孟德尔随机化语境的存活偏倚评论，用来支持"横断面老年队列的选择性存活"属跨语境引用，建议补一篇老年流行病学直接文献 |

**未发现假 DOI、未发现题名错配、6/6 通过。** 抽查范围内引用池的核验声明是可信的。

### C011（CLHLS）与 C012（CRELES）"NOT FOUND 且不引用"的处置判断

**程序上诚实，实质上不成立。应当补引，而且必须补。**

1. **检索范围选错了库。** `not_found_detail` 写的是"not indexed in Crossref or OpenAlex under this title"——这两个都是**文章库**。而队列数据的规范引用对象是**数据沉积**，归 DataCite 管。我用 DataCite 实查确认：
   - **CLHLS**：`10.18170/DVN/MKB1LF`，北大开放数据 Dataverse，2015，题名 "The Chinese Longitudinal Healthy Longevity Survey (CLHLS)-Longitudinal Data（1998-2011）"，`state: findable`。
   - **CRELES**：Harvard Dataverse `10.7910/DVN/7AUOAO`，以及 ICPSR `10.3886/icpsr26681.v2`（作者自己在 `not_found_detail` 里已经看到了 ICPSR 那条，却因为"是数据沉积、不是可引用文章"而放弃——这个判断与 DataCite/Force11 的"数据集可引用"共识相反）。
2. **"没有文章可引"不等于"不引"。** 不编造引文是对的，但正确处置是引数据沉积 DOI + 访问途径与版本，而不是让三个队列在 Methods 里以裸名出现。当前写法使读者无法定位数据、无法核验版本，恰好落在本文自身最在意的可复现性上。
3. **第三个队列根本没进引文池。** 正文说的是"KLoSA, CLHLS and CRELES have no citable cohort-profile article"，但 `failed_claims` 里只有 C011/C012 两条，**KLoSA 没有任何登记**（我独立检索也确认 KLoSA 无英文队列简介文章，只有 KEIS 的韩文机构报告）——正文对三者的断言，池子只记录了两者，这是引文池自身的完整性缺口。
4. **版本覆盖还需说明。** CLHLS 沉积题名覆盖 1998–2011，而分析用了 1998–2018 共 8 波，需指明 2014/2018 波来自哪个发布版。

**具体修改建议**：把 C011/C012 改为"已核验的数据沉积引文"入池（CLHLS: 10.18170/DVN/MKB1LF；CRELES: 10.7910/DVN/7AUOAO 与/或 10.3886/icpsr26681.v2），KLoSA 补登一条数据来源条目（KEIS 官方数据页/报告 + 访问日期）；在 Data Availability 中逐队列给出这些标识符与版本。另外把 `failed_claims` 中 C017/C019/C024/C025 这 4 条的处置说明补齐（目前只有 C011/C012 有说明，其余 4 条既无条目也无理由，读者无法判断这些 claim 对应的正文表述是否被删除或改了措辞）。

---

## 致命 / 重大 / 次要 / 需澄清

### 致命（1 条）

**【致命-1】规则集 v1.2 的测试集拟合未披露，且系统性能（F1 = 0.435）与 NHANES"复证"建立在作者自家协议判定为污染的金标准上。**

- **位置**：manuscript.md L262–270（"System architecture and comparators"）、L476–485（"System performance"）、Figure 2 及其中英文图例（L717–725、L833–848）、L296–319（"The internal layers"）；对照 docs/analysis_plan.md §0（L6–31）、§13（L311、L313）、§19.1（L445–447）。
- **问题**：分析计划明确记录 2026-10-12 在确证运行之后修改规则集（r02/r03/r04 增补 `hyperglycemia`/`hba1c_elevated` flags、新增 r22），作者自己定性为 test-set fitting，并写明"R=1.000 是构造的，不是性能提升"；§13 进一步写明"NHANES 已被 v1.2 拟合污染"，§19.1 写明"在既有 NHANES/KNHANES 数据上不存在无偏调参集"。稿件却把 NHANES 作为内部验证层报告"16 个规则对，6 复现、0 反证、声明域精确率 1.00"，并把 F1 = 0.435 作为系统性能与"优于三个基线"的依据。稿件唯一的痕迹是 L317 的一句"excluding the test-set-leakage rule r22"，**只剔了 r22，没有剔 r02/r03/r04 的跨覆盖改动，也没有说明改动时点**。而 v1.1 重放的 0.111 被放在 Figure 2 图例里并标注"不同金标准、不可比"——读者无法看出 0.111→0.435 的"提升"主要来自测试集拟合。
- **为什么是问题**：这是完整性问题，不是统计问题。一个把"pre-registered"写进标题的稿件，读者会默认评价层是干净的；此处作者自己的协议文件否证了这一默认。被污染的又是稿件唯一一处对外宣称"系统有效"的地方。
- **具体修改建议**：(a) Methods 新增 "Rule-set version history and protocol deviations" 小节，逐条列出 v1.1→v1.2 的 4 处改动、时点、"依据来自确证运行的 gold-positive 结果"这一事实、以及受影响的层；(b) Results 对 NHANES/KNHANES 层一律 **v1.1 与 v1.2 双列**，并用**同一金标准**重放 v1.1（把 0.111 从图例移进正文表格）；(c) "System performance" 一节与 Figure 2 二选一：删除，或明确降格为"探索性、无干净测试集、不作为系统有效性证据"并与文章核心结论解耦；(d) 摘要与结论不得再出现任何来自该节的性能表述。

### 重大（9 条）

**【重大-1】留一法结论与自家结果文件直接矛盾。**
- **位置**：manuscript.md L411–412、L586–587；对照 outputs/cohorts/cohort_influence.csv。
- **问题**：正文两处写"no single cohort drives the pattern / the r10 regional split is not produced by any single cohort"。原始文件显示：r10 剔除 SHARE 后合并 OR = 0.747 (0.6636–0.841)、**I² = 0.0%**（原 91.0%）；剔除 CLHLS/ELSA/CRELES 任一，I² 仍为 86.6–93.0%。SHARE 单独贡献了 r10 的全部异质性。
- **为什么是问题**：这是稿件"合并掩盖方向冲突"这一核心叙事的支撑句，而它被自家输出否证。若异质性完全由一个队列（SHARE）产生，则"冲突"的主角是 SHARE 而非"地区"或"人群"。
- **修改建议**：改写成如实陈述——"r10 的异质性完全由 SHARE 一个队列贡献（剔除后 I² 91.0%→0.0%，合并 OR 0.747）"，并把这一事实并入对方向翻转的解释（SHARE 的吸烟测量为条件题构造、SHARE 是唯一带 5 副本插补的队列、SHARE 白内障自报率 8.4% 明显低于 CLHLS 17.1%），讨论"这是人群差异还是一个队列的测量/编码特征"。

**【重大-2】"方向随地区反转"的机制表述既与数据不符（ELSA 是欧洲且保护向），也把组内分歧包装成组间差异。**
- **位置**：manuscript.md L349–354（"the single positive cohort is European while all three protective cohorts are not"）、L382/Table 5 的 regional p、摘要 L34–36。
- **问题**：(a) ELSA = English Longitudinal Study of Ageing，OR 0.7675（保护向），因此"三个保护向队列都不是欧洲的"是事实错误；(b) Europe 亚组 1.0817 是 SHARE(1.109) 与 ELSA(0.7675) 两个**方向相反**队列的合并值，组内方向分歧被合并掉之后，p<0.0001 被解释为"地区差异"。
- **为什么是问题**：这是全文最醒目的机制主张（标题式表述"reversed by region"），也是 Discussion 三个解释的靶子。按现有数据，"地区"不是合法解释变量，真正成立的陈述只是"SHARE 与其他队列方向相反"（见重大-1）。
- **修改建议**：删去"by region"及一切地理归因；改为"r10 在 4 个队列中 1 个（SHARE）风险升高、3 个（CLHLS/ELSA/CRELES）方向保护"，并明确"亚组分析中 Europe 组内本身方向不一致，因此不支持地理修饰"；若要用亚组 p，须同时报告组内异质性。

**【重大-3】"powered null"的定义与预注册不一致、层间不一致，且正文对三条"not powered"的叙述自相矛盾。**
- **位置**：manuscript.md L463–474 与 Table 6 表头注释（L1051–1052）；对照 analysis_plan.md §17（L397–405）。
- **问题**：§17 预注册的判读是 `MDE-OR ≤ 2.0 → powered_null`。Table 6 改用"CI 排除其自身 MDE"。结果：CLHLS r20（MDE 1.2127，观测 1.0267）、CRELES r02（1.2281 vs 1.3116）、KLoSA r20（1.1023 vs 1.1002）被判为 **not powered**，而按预注册定义三者全部 ≤ 2.0，**应为 powered null（8/8 而非 5/8）**。同时正文却写"CLHLS r20 was powered for a 1.21-fold association and observed 1.03"——用"有 1.21 倍效能"来论证，却把它归入 not powered。另外 NHANES/KNHANES 层（L453–457）用的是 §17 的 ≤2.0 定义，同一篇文章两套定义。
- **为什么是问题**：这一段的目的是替阴性结果辩护（"多数阴性是有信息量的"），定义不一致会让审稿人无法判断作者到底主张什么；而 CLHLS r20 的 MDE 1.2127 与 CI 上限 1.2066 只差 0.5%，属于刀锋式分类，不应承载解释重量。
- **修改建议**：统一采用预注册定义并单列敏感性；Table 6 增列 `powered_null_preregistered (MDE≤2.0)` 与 `powered_null_ci_criterion` 两列；正文改为"按预注册定义 8/8 为有检验力零结果；按更严格的 CI-排除-MDE 定义 5/8"；把"三项未达更严定义"写成它们与阈值仅一步之遥，而不是"效能不足"。

**【重大-4】E 值与"modest confounding could explain it away"的定量基础未声明，且把 OR 当 RR 使用，方向上是高估稳健性。**
- **位置**：manuscript.md L404–410、L544–551、Table 5 注（L1043–1045）；对照 cohort_heterogeneity.json `e_values`。
- **问题**：方法节没有任何 E 值公式或 OR→RR 处理说明。E 值定义在风险比上；白内障在 CLHLS 未暴露患病率 17.8%、CRELES 39.9%，属常见结局。把 OR 直接当代入：OR 0.748 → E = 2.01；按 `RR ≈ OR/(1−p0+p0·OR)` 换算（RR ≈ 0.783）则 E ≈ 1.87；r02 CLHLS 的 6.64 换算后约 4.35（降 35%）。
- **为什么是问题**：E 值是本文用于"bound rather than assert"混杂的核心工具（BMJ 眼镜下这是加分项），但它现在系统性偏高，即**把脆弱的结果说得比实际更稳**。
- **修改建议**：Methods 写明公式与常见结局的 OR→RR 换算（或引用 VanderWeele & Ding 2017 并声明所用变体）；全部 E 值双报（OR 尺度 / RR 尺度），正文结论改用 RR 尺度的保守值。

**【重大-5】双 precision 口径的主指标未指定，而"声明域精确率 1.00"被前置为结果。**
- **位置**：manuscript.md L229–238（Methods 三态）、L303–319（Results）、L731–735（Figure 3 图例）；对照 analysis_plan.md §2（L225–231）与 §0.3 更正 13（L112–117）。
- **问题**：§2 明确定义 `uninformative` **不构成反证、不计 FP**；而表 3/图 3 的"保守精确率"又把 uninformative 全部当失败计（0.375 / 0.333）。分析计划 §0.3 更正 13 写明"主指标二选一为作者决策项"——**也就是作者至今没有决定**，稿件却把两个口径并列呈现并让 1.00 出现在 Results 的第一句和 Figure 3 的第一行。
- **为什么是问题**：在 18 个规则对里 contradicted = 0 的情况下，"声明域精确率 1.00"是分母近乎退化的产物（6/(6+0)），把它与 0.375 并列而不指定主指标，读者会取好看的那个。这正是审稿人最警惕的"denominator shopping"。
- **修改建议**：明确指定**保守口径为主指标**（或明确声明"两口径均不足以支持性能主张，因为 contradicted = 0 使声明域口径不可识别/退化"）；Figure 3 中把 1.00 标为"退化分母（0 反证）下的不可识别量"，不要以同等视觉权重呈现。

**【重大-6】标题与摘要的样本量被插补副本放大，且 Table 6 的 SHARE n 与同层结果文件相差正好 5 倍。**
- **位置**：标题（L1）、摘要 L20–25、Methods L166–168、Table 6（L1049–1073）、`cohort_power.csv` 对照 `cohort_rule_results.csv`。
- **问题**：(a) SHARE 1,693,515 行 = 5 个插补副本 × 338,703 唯一 person-wave；八队列唯一 person-wave 合计 **661,706**、唯一人数 **285,879**，标题的 "2.0 million person-waves" 高估约 3 倍；(b) Table 6 的 SHARE n（1,686,370 / 710,420 / 711,145）恰为结果文件 n（337,274 / 142,084 / 142,229）的 5 倍，而 Methods 亲口写"an imputation replicate is never counted as an independent person"；(c) 该 n 进入 MDE 计算，使 SHARE 各行的效能被高估。
- **为什么是问题**：标题里的数字是本文修辞的核心（"两百万条记录仍然答不了三分之二的问题"）。它被夸大 3 倍之后，这句话的说服力是借来的。而 Table 6 与同层另一份交付物相差 5 倍，说明交付物之间没有对账纪律。
- **修改建议**：标题与全文改用唯一 person-wave（≈66 万）或唯一人数（≈29 万）；Methods 定义一个量就报一个数——"1,693,515 rows = 5 imputation replicates × 338,703 person-waves；分析样本 = 副本内 n（如 r02 为 337,274），副本仅用于 Rubin 合并"；Table 6 的 n 全部改为副本内分析 n，并加一列 `n_person_wave_unique`；重算 SHARE 各行的 MDE 并核对 powered_null 分类。

**【重大-7】预注册的方差方法与稿件方法节不一致，且未记为偏离。**
- **位置**：manuscript.md L240–248（"Statistical analysis"）；对照 analysis_plan.md §19.7（L555–556）。
- **问题**：§19.7 预注册 "SHARE 与 LASI 等带设计权重者用 survey 设计（strata/PSU/weights）；其余队列用聚类稳健方差"。稿件方法节只写 "variance clustered by participant"，**完全没提 survey 设计/权重**；而 cohort 层唯一带 1.69M 行的队列正是 SHARE（其 `cci_w*` 校准权重在台账里已核验存在）。RESULTS_COHORT.md 又声称"本次运行未修改任何预注册项"。
- **为什么是问题**：本文（R11 层）把 survey svyglm 作为确证方差标准写进了预注册，并因此把 r22 从复现改判为无信息（§0.2 更正 7）。同一项目在队列层对最大的队列改用聚类稳健方差却不声明，读者会认为采用了同一标准；这直接影响 r10/r02/r13 各 SHARE 估计的 CI 宽度，而 SHARE 又是 r10 异质性的唯一来源（重大-1）。
- **修改建议**：在 Methods 明确逐队列方差方法（SHARE/LASI 是否用了 strata/PSU/weights、其余是否 cluster-robust、SHARE 插补副本如何与 survey 设计结合）；如实际未按 §19.7 执行，按 §19.9 记为协议偏离并同时报告原方案结果。

**【重大-8】MHAS 贡献 0 个规则×队列单元，但被计入"八队列 2.0M"与 168 格分母，稿件未披露。**
- **位置**：摘要 L19–21、Methods L157–168、Results L327–328、L415–420；对照 evidence_audit.json（`feasible_pairs` 无任何 MHAS）与 Figure 8 图例 L807（"across 6 rules and 7 cohorts"）。
- **问题**：八队列中 MHAS（78,537 行）没有贡献任何一条规则对，Table 6 无 MHAS 行，Figure 8 只有 7 个队列。但摘要、Methods、Table 7 的分母（21×8）都按八队列表述，读者会以为 2.0M 人里有 MHAS 的规则检验。
- **为什么是问题**："八队列三大陆"是本文的规模卖点；实际规则层证据来自 7 个队列，其中 MHAS 一格未出。这是容易被抽查发现的夸大。
- **修改建议**：摘要改为"在八个队列中评估、其中七个队列贡献了可检验的规则×队列单元"；Table 7 注明"MHAS 进入分母但未贡献可行单元（原因：…）"；Figure 8 图例与正文口径统一。

**【重大-9】ELSA 的眼科结局来自 wave 2 派生文件、底层题项未确认，而唯一的 AMD 结论依赖它。**
- **位置**：manuscript.md L217–221（"age-related macular degeneration (ELSA only)"）、L360–364（r11）、Table 6 ELSA 行；对照 supplementary_material.md L163–170（更正 C42）、analysis_plan.md §19.3（ELSA 记为 wave 3）。
- **问题**：台账 C42 记载 `heoptca`（白内障）/`heoptgl`（青光眼）/`heoptmd`（AMD）位于 **`wave_2_derived_variables.dta`（派生文件）**，并标注 "⚠️ 使用前须确认其底层原始题项，并在预注册中声明"。稿件未做此确认、未在 Methods 声明使用派生文件（Methods 的例外清单只列了 SHARE `gv_*` 与 MHAS constructed/imputation），且分析层被记为 wave 3，存在波次错配的可能。**r11（唯一 AMD 规则的全部证据）与 r10@ELSA 都建立在这些变量上。**
- **为什么是问题**：本文的说服力建立在"每个变量都凭官方码本核验"上（Methods 三条 blocking QC 规则）。唯一 AMD 结论用了一个作者自己标记为"待确认底层题项"的派生变量，且是跨波的。
- **修改建议**：确认并写出 `heoptca/heoptgl/heoptmd` 的底层题项与所属波次；若为 wave 2 派生变量而 frame 为 wave 3，说明合并逻辑；把 ELSA 派生文件写入 Methods 的官方派生文件例外清单；对 r11 的结论加一句"基于 provider-derived 变量，构念核验强度低于本层其他结局"。

### 次要（9 条）

1. **摘要 r02 合并 CI 与 Table 5 不一致**（L31 "1.33–2.88" vs L381/Table 5 "1.32–2.88"；原始 1.3245 → 1.32）。位置：摘要 vs Table 5。修改：统一为 1.32，并在一次性对账脚本中加"摘要数字必须来自 metrics JSON"的断言。
2. **摘要把 meta 回归 p 的范围写成 0.42–0.52**（L37），实际三个 p 为 0.4178／0.5169／0.3472 → 应为 0.35–0.52。修改：改为 0.35–0.52 或直接列三个值。
3. **Figure 8 图例的不可检验规则数错**（L807）：写"13 rules have no bar at all"，分项 5+1+3+3+2 = 14，实际 21−6 = 15，且漏掉 r05（lipid panel）。修改：改为 15 并补 r05 项。
4. **Table 4 / Results 的 KNHANES 计数不自洽**（L299–301、L1017–1023）：total 352 vs 301 tested + 50 underpowered = 351。修改：核对源文件后修正一个数。
5. **Figure 7 图例的规则对 n 与 Table 4 不一致**：图例 NHANES 17 / KNHANES 13（合 30），Table 4 为 16 / 15（合 31）。修改：以同一件事后口径重算并统一。
6. **Table 5 中 r12/r13 的 "Regional p" 与 "Q p" 是同一个检验**（k=2、每地区 1 队列时组间 Q 恒等于总 Q，df=1）。修改：删除这两行的 regional p 或注明"与异质性检验同一统计量"。
7. **Table 6 与 cohort_rule_results.csv 的 ELSA n 不一致**（4050 vs 4013；4028 vs 3991，各差 37）。修改：统一分析样本并在效能脚本中加断言。
8. **规则级"不可检验原因"分类不是划分**：r07 同时被算作需眼底影像与需血液指标，故 5+1+3+3+2 只是计数不是分类。修改：注明可重叠，或改为按"解锁该规则所需的最小新增模态"做互斥归类（细胞级的 Table 7 已正确）。
9. **模态解锁数被呈现为投资排序，但各模态互相重叠、不可相加**（L426–430、L516–518、Table 7 下半）：r07 需同时加眼底影像与血液检测，故 fundus +15 与 blood_assay +13 存在重复计数；分项合计 68 > 150。修改：加一句"各模态解锁数不互斥、不可相加"，并给出贪心排序下的**去重后**增量（例如"仅加眼底影像解锁 X 个此前完全不可行的单元"）。

### 需澄清（4 条）

1. **主要结局是否属于"患者重要结局"、临床路径是否真会用？** 队列层结局是自报医生诊断的白内障/青光眼与自评矫正视力。自评视力属功能性患者结局（这是优点）；但白内障自报诊断本质上是**就医可及性的代理**，稿件也承认"differential under-ascertainment where access to care differs, which is itself correlated with the exposures of interest"。请澄清：本文是否主张任何一条规则可用于临床路径？我的判断是**不能**（作者自己的结论是 0/6 可靠可迁移），因此建议在摘要与结论中把"临床决策支持"的定位明确降为"研究议程"，避免读者误以为已有可用规则。位置：摘要、Introduction L75–96、Discussion L611–625。
2. **预注册的可核验性**：analysis_plan.md 无注册号/时间戳/哈希，§12/§13/§15 三处作者自陈"落盘先于运行无独立可证证据"。请澄清"pre-registered"在本文中的确切含义（项目内先落盘 vs 第三方可查注册），并在 Methods 用一句话如实限定。
3. **测量不变性未被检验**：raw-only 排除了 harmonized 之后，同一 flag 在 8 个队列来自不同题项（CLHLS 糖尿病自报 1.36% vs 测量队列 12–14%）。请澄清是否做过任何跨队列测量等价性/阳性对照分析（例如用"年龄→白内障"这类近乎不随人群改变的关联作为管线校准）。若未做，这是解释 r10 翻转时缺失的第四个候选解释（测量不等价），应与三个既有解释并列。
4. **Table 6 的"CI 排除自身 MDE"判据的统计含义**：该判据与"MDE ≤ 2.0"的关系、以及为何 CLHLS r20（MDE 1.2127、CI 上限 1.2066）只差 0.5% 就被判为"未达效能"，需要一句话说明；否则读者会认为分类对阈值极度敏感。

---

## 升维建议（一条具体路径）

**把"18 格可迁移性"升级为带测量不变性层的个体参与者数据（IPD）元分析，并用一个阳性对照证明管线本身无偏——预注册、冻结代码、公开可查。**

理由：本文目前的最高层结论是"我们说不清 r10 为什么翻转"（三种解释并列、一种被 meta 回归否掉、一种只能给 E 值上界、一种自称设计上测不了）。这是**同级期刊的天花板**：一个诚实的负结果 + 一张体检表。要再上一层，必须把"说不清"变成一个能判定的设计。具体三步，按优先级：

1. **加一个管线阳性对照与一个测量不变性层（成本最低、收益最大，不需要新数据）。**
   在同一批 8 队列、同一套代码上，预先声明 2–3 条**已知跨人群稳定**的关联（例如"年龄↑→白内障↑""女性→白内障↑"），要求管线在所有队列都复现且效应量排序一致。若管线能稳定复现这些，r10 的翻转就只能是人群/测量差异而非管线缺陷；若某队列连阳性对照都失败，该队列的 r10 结果就不该进入"方向翻转"的论证。同时给出逐 flag 的题项对照表与"构念距离"评分（问题原文/等级数/参考期/自报 vs 测量），把测量不等价从 Discussion 的"承认"变成 Results 的一个数值。**这一步单独就能把 Discussion 从"三种解释都无法排除"变成"测量差异解释了 X%，剩余 Y% 需要机制解释"。**

2. **把 18 格改成真正的 IPD 元分析（数据已在手，只需重跑）。**
   现在是把 18 个 OR 拿来做随机效应合并；改成在 8 个队列的个体数据上做一步式 IPD 回归（规则 × 队列交互项），可以直接检验"队列间差异是效应修饰还是抽样波动"，并用 participant-level 交互项取代"地区亚组"这种 k=2/k=4 的粗糙分组。这一步同时能消掉本文两处最被诟病的地方：k=2 时"地区 p"与"Q p"重复（次要-6），以及 Europe 组内方向相反仍被当地区证据（重大-2）。

3. **补一个带镜片分级（LOCS 类）的检查队列，把"白内障不是一种病"从猜测变成检验。**
   本文最强的机制假设是"核性/皮质性/后囊下亚型的风险因素谱不同，队列间亚型构成不同 → 同一暴露产生不同的边际关联"，而作者承认"no cohort in the layer grades opacity subtype"。这是全文唯一一条**能一举解决核心谜题但被数据卡住**的路径。可行来源是已有的检查分级队列（NHANES 2005–2008 眼科检查含晶状体分级；如有条件再加一个带 LOCS 分级的亚洲队列）。只要在 ≥2 个队列中把白内障结局按亚型拆开重跑 r10，就能判定：若 SHARE 与 CLHLS 的亚型构成差异能解释符号翻转 → 这是一篇"暴露组规则必须在亚型层面重写"的正面方法学论文；若不能解释 → 把选择性存活/混杂的结论做实。无论哪个方向，都比现在的"我们不分伯仲地列了三种解释"高一个层级。

**执行顺序与可行性**：第 1 步 2–3 周（纯复用现有代码与数据，唯一的增量是阳性对照的预注册与逐 flag 题项对照表）；第 2 步 2–4 周（需把 8 队列个体数据统一到分析格式，但 frame 已建成）；第 3 步取决于能否取得检查分级队列的访问（NHANES 2005–2008 立即可得）。**建议至少完成第 1 步再投**——它同时补齐本文两个最大的可复现缺口中的"测量不变性"这一个，并把"仅用原始文件"从负担变成有校准的资产。

---

## 给编辑的一句话（保密意见）

队列层的实证与审计是扎实、可发表的；稿件当前的风险全部集中在**自我披露不足**（测试集拟合未披露、样本量被插补副本放大、留一法结论与自家输出矛盾、预注册不可核验、无数据/代码可得性声明）与**系统层的不必要存在**。这些问题不改变"6/21 可检验、0/6 可靠可迁移、测量而非样本量是瓶颈"这一核心结论——它们改变的是读者对作者自我审计能力的信任。建议给作者一次大修，条件是把系统层解耦、把版本历史与偏离记录全部摆到台面上、把 n 与"powered null"的定义统一到预注册口径、并把数据/代码可得性补齐。
