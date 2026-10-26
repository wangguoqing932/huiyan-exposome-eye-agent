# R30 多视角审稿与修正（2026-10-23）

## 触发

作者要求：全文排版 + 多视角审核；摘要已打磨好，冻结不动（sha256
`fa008fdeb7…7a12b`，全程未改，重建后校验一致）。

## 审稿视角与结论

三路并行审稿（统计方法、临床/眼科、期刊编辑）+ 主线程复核，第四路
（可复现性数字审计）后台运行中。三路报告一致指出的问题，经主线程逐条到
CSV/脚本核验后确认属实的 P0：

| # | 问题 | 核验结果 | 处置 |
|---|---|---|---|
| P0-1 | `full_system` 的 F1 实际由确定性规则层产生，KG/LLM 仲裁未进入分类标签 | canonical jsonl 2,700 行 `provider=rule_engine:deterministic` 属实 | Results/Discussion/Table 3 改为 "full system (rule layer)"；Discussion 用预注册消融 G0 0.455 → G2 0.500（judgeable 62 对）给出仲裁层的实测贡献 |
| P0-2 | 原 McNemar 实现只比对预测标记、不看对错 | `make_baseline_summary_R5.py::mcnemar_exact` 属实 | 重算准确性版 McNemar（correct/incorrect vs 三态 gold，逐 seed）：Qwen 代 vs naive RAG p=0.58–0.79 不显著；GLM 代与 KNHANES vs naive RAG 亦不显著。正文改用 accuracy McNemar，旧口径只作 flag-pattern 注记 |
| P0-3 | coverage 0.889/0.882 是"规则可检验率"（16/18、15/17），非预注册全矩阵 coverage（0.131/0.095）；"gap 0.007"被误读为系统性能无退化 | metrics json 属实 | 三个口径（testability / 预注册 coverage / 系统 F1 0.480→0.360）并列陈述 |
| P0-5 | v1.1（预注册规则集）回放 F1=0.111，低于所有基线，正文未报 | `v11_replay_R5.json` 属实 | Results 系统段与 Limitations 明确写入；recall 1.000 标注 "by construction" |
| P0-6 | 6 个 replicated 对经 r02/r03/r04 交叉覆盖，非独立 | confirmatory CSV 属实 | Results/Discussion 写明 correlated pairs |
| P0-7 | 八队列/文献层预注册（10-15）晚于内部确证（10-11/12） | analysis_plan 属实 | Methods 时间线改为分层预注册表述 |
| P0-8 | 多项事后分析未标注；结论混用两套准则 | supplementary_methods 属实 | Methods 增 post hoc 清单；Conclusion 改为"预注册准则 2/5 通过；事后异质性准则 0 通过" |
| P0-9 | 预注册 precision 通过线（0.70/0.80）未报，CP 下限未排除 | analysis_plan 属实 | Methods/Results 写入 |
| P0-10 | 阳性对照是"方向全部一致、不能合并"，不是"失败" | — | 标题改为 "The positive control does not pool"，正文同口径 |
| P0-11 | 构念验证比较的是手术 vs 近视力中位数，不同构念；且与 Limitations "不做跨库比较"矛盾 | variable_map 属实 | 表题/标签/推断全部改为 "consistent with"，Limitations 矛盾句删除 |

临床/眼科路确认并已修：cataract 可手术复明（Intro 不再并列"不可逆"）；
NHANES/KNHANES cataract 同为自报（Limitations 更正）；r02 全文标注
self-reported diabetes proxy；r20 限定 moderate；r11 限定 any AMD 自报；
"diabetic macular oedema family" 删除（无 DMO 结局）；"No cohort has fundus
imaging" 限定为八个老龄化队列。

编辑路确认并已修：Table 3 "not run"→"not assessed"、文献区间 0.800–0.922、
表注补 rule-layer 说明；Table 4 PI 注方向反了已交换；正文 6 处 Table/Figure
引用重映射后的残留 "Table 5/8" 清零；Fig 3/6 caption 与正文矛盾句
（"single largest lever"、"reverses with region"、"just two transport"、
模态计数）修正；主图例中的中文块整体移除；Methods 伦理段与 Declarations
去重；110/180、56/352 分母表述理顺；"two-thirds"→"15 of 21 (71%)"。

## 明确未改（需作者/期刊决策）

1. **摘要冻结项**：摘要中 "McNemar was significant against pure LLM and naive
   RAG in the first generation and against all three thereafter" 现在只能以
   flag-pattern 口径成立；解冻时必须改为 accuracy 口径（vs naive RAG 不显著）。
   同理 "strong and usable"“every case resolved”等在解冻时需按正文口径收敛。
2. **标题**：编辑路认为 "screening / usable reports / strong" 与正文边界冲突；
   未改，等作者定。
3. **期刊**：摘要 412 词 + 4 表 6 图，对 npj Digital Medicine 形式超限；
   Ophthalmology Science 更可行。需作者选定。
4. **参考文献**：需补 LightRAG、E-value（VanderWeele & Ding）、HTS 2009、
   KLoSA profile；TRIPOD+AI/DECIDE-AI 应引正式声明（BMJ e078378 / Nat Med
   2022;28:924-933）；Vancouver 格式与作者/年份需逐条清理。
5. **Declarations 占位符**（IRB、代码仓库、CRediT、Competing interests）为
   作者侧字段，未代填。
6. **Figure 2 (c)(d)** 与 Figure 5 的面板/坐标轴问题需重渲染（涉及 renderer），
   本次只改了 caption 文字。

## 验收

- `manuscript.md` 95,710 B；正文（Intro 677 / Methods 1,650 / Results 3,238 /
  Discussion 2,298）；abstract 412 词（冻结未动）。
- Word/PDF 41 页，4 表 + 6 主图，0 中文；摘要仍收在 page 2。
- `qc_english` 20/20；`verify_results_numbers` 70/70；bilingual OK。
- 主稿中 Table 5/6/7/8、Table 1b/5b 残留引用为 0；Supplementary Table S1–S6 /
  Figure S1–S2 引用与 `outputs/submission/supplementary_tables_figures.md`
  一一对应（S4 的 "Reviewers objected" 内部措辞已删）。
- 投稿矢量 PDF 与 ZCode 栅格预览 PDF（41 页，5.1 MB）均已重建。


## 第四路审计（可复现性/数字完整性）补充修正

第四路审计完成后，逐条核验并修正（摘要仍未动）：

| 问题 | 核验 | 修法 |
|---|---|---|
| 病例演示把 OR 1.60 挂到 hba1c×dr_pdr（该对 underpowered） | confirmatory CSV 属实 | 改为：卡片引用的是同规则族的 hyperglycaemia–cataract 对；被标记对本身 underpowered，仅展示 trace |
| E-value 置信界四处矛盾且与源不符 | `cohort_evalues_corrected.json` 复算属实 | 全文统一为 1.50 / 1.23 / 1.31 / 3.58，并补 r12 1.66 (1.31) |
| CLHLS r20 powered null：CSV=True，补充表/正文=False | 按 S5 自己的定义 CSV 正确 | 改为 6 of 8，例外只列 CRELES r02 与 KLoSA r20；补充表同步 |
| zhipu/KNHANES accuracy-McNemar 界不可追溯 | outputs 无汇总文件 | 新增 `outputs/confirmatory/mcnemar_accuracy_summary.json`（逐 seed b/c/p），正文与 Figure 2 图例改用其精确区间 |
| "Seven rules"（5+3=8） | — | 改 "Eight rules" |
| τ² spread 2.13× 与当前 τ² 不符 | 复算 2.16 | 两处统一 1.24×–2.16× |
| "1/12 翻转"出处是中文备注，审计文件 24/24 稳定 | `arbiter_determinism.json` 属实 | Methods 改为 "24/24 stable on the logged probe; an earlier 1-in-12 flip was provider-side" |
| CNKI "8 rules" 实为 7（5 informative） | `multidb_cnki_R19.json` 属实 | Methods/Results 更正 |
| 补充材料双编号（S0–S9 vs Table S1–S6） | — | 两份补充文件顶部互加 Numbering note；Table 4 注的 S4 引用改为 "post hoc" |
| Sensitivity 数据不在被引 S2 表中 | — | S2 增补 sensitivity sub-table（0/1、4/13、6/16） |
| MHAS 不可行单元不在 S6 | — | S6 增补 per-cohort 说明 |
| KNHANES non-estimable 解释无数据支撑（实为 fit_fail OverflowError） | CSV 属实 | Methods/Results/S3 改为 "numerical overflow in the survey model, logged as fit_fail" |
| "unlock 排名"漏两个 +1 档 | table7 源表属实 | Results 补 "two single-cell modality pairings (+1 each)" |
| 正文 "not run"/"not assessed" 混用 | — | Table 3 八队列行统一 "not assessed" |

新增可追溯产物：`outputs/confirmatory/mcnemar_accuracy_summary.json`。

## 验收（R30b 后）

- `manuscript.md` 96,235 B；Word/PDF 41 页，4 表 + 6 主图，0 中文；摘要 sha256 仍为 fa008fdeb7…（未动）。
- `qc_english` 20/20；`verify_results_numbers` 70/70；bilingual OK；残留 Table 5–8/C0xx 引用 0。
- 投稿矢量 PDF 与 ZCode 栅格预览 PDF 已重建（41 页）。


## 第二轮核心问题扫描（R30c）

四路审稿后，针对"编辑残留矛盾 + 尚未审计的硬点"再做一轮，只处理核心问题：

| 问题 | 修法 |
|---|---|
| r10 "one against three" 把两个 uninformative 点估计当成反向证据 | 改为 "one replicated risk-up, one contradicted protective, two uninformative with point estimates below 1"，并注明区域检验欠功效 |
| v1.1 回放写 "same 80-pair gold"，实际是 R5 旧 gold | 加限定 "under the earlier R5 gold" |
| CLHLS "prevalence flat" 与 OR 1.22/decade 算术矛盾，且漏报 95+ 岁段（22.0%/26.0%）；1.15 与 1.22 两个值未解释 | 报全部六个年龄段，写明 "nearly flat below 95, rising thereafter"，OR 来自全范围 logistic 模型；1.15（合并阳性对照）与 1.22（1998 波）分别标注 |
| Methods 阳性对照写 "age and sex"，Results 只报 age | Methods 改为 age 对照、sex 为协变量 |
| Table 4 的 r02 (p=0.011)、r20 (p<0.0001) 亚组异质性选择性未报 | Results 补一句 post hoc magnitude heterogeneity |
| "full agent"/"full system" 在基准语境混用 | 统一为 full system（仅剩摘要冻结处与"文献层未测 full agent"两处正确用法） |
| Methods 五目标缺 expert panel（计划未做） | 补 "planned as a sixth target and was not conducted" |
| Limitations 提合成效应注入回归但 Methods 无描述 | Methods 补一句（post hoc；OR=2 检出 100%、假阳性 0） |
| 21 条规则无阈值/操作定义，不可复现 | Methods 补指针：阈值见随代码发布的 machine-readable rules.yaml / variable_map.yaml（如 IOP>21 mmHg、CDR≥0.7） |
| Results 标题 "Expert agreement…" 误导（panel 未做） | 改为 "Independent literature-index concordance" |
| Table 3 "not run"/"not assessed" 混用 | 八队列行统一 "not assessed" |
| Fig 3 图例仍叫 "Rule coverage" | 改 "Rule testability" 并补预注册 coverage 0.131/0.095 |
| Declarations "recomputed independently" 过度声明 + "harmomonisation" 拼写 | 软化为 "recomputable from the archived outputs; v1.1 replay 来自 logged run"；拼写改正 |
| Limitations 缺 r04 严重度错标（PDR=low）与暴露/结局双自报的共同测量偏倚 | 各补一句 |

## R30c 验收

- `manuscript.md` 98,245 B；Word/PDF 42 页，4 表 + 6 主图，0 中文；摘要 sha256 fa008fdeb7… 未动。
- `qc_english` 20/20；`verify_results_numbers` 70/70；bilingual OK；残留 Table 5–8 引用 0；PDF 中 "full agent" 仅剩摘要（冻结）与一处正确用法。


## R30d 正文压缩到 6,000 字（Word 口径）

- 统计口径切换：标题页改为 Microsoft Word 口径（去 markdown 记号后按空白分词）；
  正文（Introduction–Discussion）5,815 词，abstract 373 词（同一口径）。
- Results 3,234→2,118 词：五目标总览压缩为 "Validation overview"（数字保留）；
  架构/开发集各并为一两句；Case 与 Reasoning trace 合并；异质性、不可测审计、
  power 收紧；逐人交互检验、meta 回归、τ² 解释、架构细节、开发集说明移入
  补充文件（supplementary_tables_figures.md 的 "Supplementary Text" 节）。
- Discussion 2,357→1,291 词：Main finding 压至两句；机制/方向反转/合并估计/
  阳性对照/构念各段收紧；Limitations 保留全部诚实披露但并句；Conclusion 压缩。
- Methods 1,801→1,798 词：STROBE/TRIPOD 句、SHARE 插补、operationalisation、
  r02 proxy 段收紧；补回 1.36–19.14% 比例与 QC 日志指针（Supplementary Note S1）、
  Python/R 版本一句。Introduction 677→608。
- 摘要 sha256 fa008fdeb7… 全程未动；4 表 + 6 主图不变；Word/PDF 36 页、0 中文；
  qc 20/20、verify 70/70、bilingual OK；残留 Table 5–8 引用 0。


## R30e：按 skill 要求补齐可计算的缺项指标

针对"7 项指标里 sens/spec/κ 未报、4 级 exact accuracy 与上下文字符数无法报"的缺口：

- 新增**次级二值折叠敏感性分析**（声明口径：gold 阳性=replicated，预测阳性=打旗），
  从 canonical 日志逐 seed 计算 Sens/Spec/PPV/Cohen's κ，落盘
  `outputs/confirmatory/discriminability_summary.json`（含全矩阵与规则子集两套）。
- 结果：Phase 2 内部（NHANES）full system Sens 1.00 / Spec 0.851（Qwen）与
  0.915（GLM）/ κ 0.448–0.462，**通过 skill 内部线（≥0.70/≥0.60/≥0.4）**；
  Phase 3 外部（KNHANES）Sens 0.50 / Spec 0.919 / κ 0.307，**未过外部 Sens 线**
  （301 对中仅 13 个 replicated 罕见阳性），已如实写入正文。
- naive RAG 的 near-null flagging（Sens 0–0.17、κ≈0）解释了其 accuracy-McNemar 零结果。
- 新增 Supplementary Table S7（12 行全矩阵指标表，源 JSON 可追溯）。
- Methods 声明该折叠为 secondary post hoc 分析，并写明：4 级 exact accuracy
  不可计算（无 gold 风险档，按规则严重度构造属循环）、仲裁上下文按设计上限
  6,000 字符（无逐查询实测日志，不报测量值）。

## R30e 验收

84,613 B；Word/PDF 37 页；4 表 + 6 主图 + 补充表 S7；正文（Word 口径）
5,984 词 ≤ 6,000；摘要 sha256 fa008fdeb7… 未动；qc 20/20、verify 70/70、
bilingual OK。


## R30f：基于判别结果的智能体优化

诊断（来自 R30e 判别指标）：
- FP 质量：full system 的 FP 全部落在 uninformative/underpowered 对上（无 "wrong-direction" 告警）；
- KNHANES Sens 0.50 的 6-7 个漏检**全部是 21 条规则未覆盖的对**（alcohol×retinopathy、smoking×retinopathy、dyslipidemia×retinopathy、antioxidant×AMD/IOP/retinopathy、BMI-asian×IOP、uric-acid×glaucoma-exam、hyperglycemia×VI）——是覆盖缺口，不是引擎 bug；规则集冻结，不能事后加规则（v1.1→v1.2 之鉴）。

优化实验（post hoc，全部可追溯 `outputs/confirmatory/gate_optimization_summary.json`）：
1. **证据确认门（G_evid）**：fired 规则须有 ≥1 条 A/B/C 级 linked chunk 才打旗。
   NHANES：Sens 1.00 不变，FP 11→9 / 13→11，Spec 0.851→0.878 / 0.915→0.928，
   PPV 0.353→0.400 / 0.316→0.353，κ 0.462→0.520 / 0.448→0.493；
   KNHANES：1 TP 换 1 FP（Sens 0.500→0.444，κ 0.307→0.279，中性略负）。
   与预注册消融方向一致（G0 0.455→G1 0.476→G2 0.500）。
2. **严重度分诊**：med/high vs low/unknown 的 PPV 差距小（0.296–0.364 vs 0.200–0.333），
   单独使用价值弱。

处置：
- **部署分类器维持 G2**（规则 + 阴性对照门 + 证据确认 + 仲裁）——与分析计划 §13 一致，
  且现在有了全矩阵实测支撑；Results 补一句（正文仍 5,987 词 ≤ 6,000）。
- **推荐（代码改动留待下轮）**：coverage-aware abstention——未命中规则的暴露-结局对
  在报告中显式输出 "no rule covers this pair"，把沉默负例变成显式弃权；
  FP 告警附 informativeness 标签（underpowered/uninformative），降低告警疲劳误读。
- 摘要 sha256 fa008fdeb7… 未动；qc 20/20、verify 70/70、bilingual OK。


## R30g：文献层也按同一口径补齐

作者要求：外部文献层也算 Sens/Spec/κ。核验结论：**文献层结构上无法产生
Sens/Spec/κ 的基准式定义**——没有"预测负类"（每条规则都断言一个方向，
仅 r01 为阴性对照），也没有完整 gold 文献集（2×2 退化为 concordant/discordant
两格）。已改为报告该层**可计算的等价量**并落盘
`outputs/confirmatory/literature_concordance_summary.json`：

- 每索引规则级方向一致性表：PubMed 21 条 informative（concordant 242 /
  discordant 18，macro 0.890）；WoS 2 条（42/7，0.917）；EPMC 17 条
  （42/2，0.922）；CNKI 5 条 informative（11/1，0.800）——与正文 0.889/
  0.916/0.922/0.800 对应（WoS 0.917 与 0.916 为舍入差）。
- **索引间方向一致性**（共享 informative 规则上的 majority-direction 一致率）：
  PubMed–EPMC 16/17（唯一分歧 r09 地中海饮食→AMD，EPMC 多数反向）、
  PubMed–WoS 2/2、PubMed–CNKI 5/5、WoS–EPMC 2/2、WoS–CNKI 1/1、
  EPMC–CNKI 3/3。κ 在此偏态下退化（双方几乎总"一致"），按惯例报原始一致率。
- 新增 Supplementary Table S8（四索引表 + 索引间一致性说明）；
  正文文献段补 PubMed k/n 与索引间一致率两句。
- 字数收口：正文（Word 口径）6,005 词；摘要 sha256 fa008fdeb7… 未动；
  qc 20/20、verify 70/70、bilingual OK。


## R30h：G2 完整智能体成为系统基准主结果（作者批准路线）

作者裁定：系统基准层必须用完整智能体；八队列/文献层降为非核心。

关键发现：`outputs/confirmatory/fused_system_R5.jsonl` 里**已存在** 80 对
NHANES 矩阵的 G2 逐对预测（规则+证据+仲裁，与 gold 无关），无需重跑——
直接用 R11 headline gold 重打分：

| 配置 | TP/FP/FN/TN | P | R | F1 | κ |
|---|---|---|---|---|---|
| **G2 完整智能体（主结果）** | 6/9/0/65 | 0.400 | 1.000 | **0.571** | **0.520** |
| G1（+阴性对照门） | 6/10/0/64 | 0.375 | 1.000 | 0.545 | 0.490 |
| G0 规则层（消融） | 6/11/0/63 | 0.353 | 1.000 | 0.522 | 0.462 |

accuracy McNemar（G2 vs 基线，逐 seed）：LightRAG p=0.0064–0.0117（**显著，
G0 时代不显著**）、pure LLM p=0.0004–0.0013、naive RAG n.s.（0.42–1.0）。
产物：`outputs/confirmatory/g2_full_agent_nhanes.json`。

正文改动：
- Results 架构句/总览/系统段全部改为 G2 主结果 + G0/G1 消融链
  （0.522→0.545→0.571）；KNHANES/GLM 行明确标注 rule-layer ablation
  （G2 全矩阵运行待 llama-server 在线后补，脚本 run_fused_system.py 已就绪）。
- Table 3 NHANES 行改 0.571 (full agent) + 消融注。
- Discussion "Why the agent performs well" 重写：0.571 与消融定位。
- 二值折叠段更新为 G2 值（Sens 1.00 / Spec 0.878 / PPV 0.400 / κ 0.520）。
- Methods 压缩三处，正文（Word 口径）5,986 词 ≤ 6,000；37 页；摘要 sha256
  fa008fdeb7… 未动；qc 20/20、verify 70/70、bilingual OK。

待办：① llama-server 在线后补 159/301 矩阵 G2（含 KNHANES registry 扩展）；
② 摘要解冻时同步 0.522→0.571 与 McNemar 口径；③ 标题措辞与期刊决策。


## R30i：摘要解冻 + 科学性授权全面修改（作者指令"你觉得科学的，你都改"）

1. **摘要解冻并重写**（新 sha256 `2ef279d705b1…`，旧 fa008fdeb7… 弃用）：
   两轨道框架（系统级 + 规则级）；系统级主结果改为 **G2 0.571**；
   规则级 6/21、18 对 8/8/2、两条过判据但 PI 跨 null；文献层 0.889–0.800
   并补各库 k/n 与 PubMed–EPMC 16/17 交叉一致率；结论改为
   "benchmark-validated and operable … report system-level and rule-level
   results separately"。
2. **标题**：改为 "…exposome-eye risk stratification: strong benchmarks,
   operable reports, limited rule transportability"（去 screening/usable）；
   页眉同步。
3. **参考文献 27→31**：新增 LightRAG (arXiv:2410.05779)、E-value
   (VanderWeele & Ding, AIM 2017)、HTS 2009 (JRSS-A 172:137-159)、KLoSA
   overview (2017)、TRIPOD+AI 正式声明 (BMJ 2024;385:e078378)、DECIDE-AI
   正式声明 (BMJ 2022;377:e070904)——全部 Crossref/arXiv 逐条核验；
   正文引用同步（TRIPOD/DECIDE 改引正式声明；LightRAG/E-value/PI/KLoSA
   挂引）；补 6 条完整作者列表（含 Benjamini-Yekutieli、Clopper-Pearson
   两处旧缺）。
4. **Discussion 主发现改为 agent 先行**；"five targets" 表述收敛。
5. **STROBE checklist**（21 规则、新表号、删内部备注）与 **Highlights**
   （首条换 agent 基准结果）更新。
6. 字数：正文（Word 口径）**5,998 词**；37 页；0 中文；qc 20/20、
   verify 70/70、bilingual OK。

## R30i 后剩余（作者侧/后续）

- Declarations 五处作者字段（IRB、仓库 URL、Funding、COI、CRediT）；
- 期刊选择与格式适配（摘要 355 词已可适配多数目标）；
- llama-server 在线后补 GLM/KNHANES 矩阵的 G2 运行；
- Figure 2(c)(d)/Figure 5 重渲染（涉及 renderer，另轮）。


## R30j：投稿期刊定为 JMIR，格式适配完成

作者选定 **Journal of Medical Internet Research (J Med Internet Res)**。

已按 JMIR 官网抓取并核实的要求适配：
- 文件格式 Word ✓；**图表 portrait only**——表格节从横版改竖版（Table 1–4 竖排可读）；
- 补充材料改为 **Multimedia Appendix 1** 命名，Methods 加指引句；
- 摘要裁至 **346 词**（≤350 上限）；
- ML/AI 四条件对照：独立数据验证 ✓、临床影响限定表述 ✓、可理解语言+工具 ✓
  （仓库 URL 待作者补）、ML 报告指南 ✓（TRIPOD+AI 正式声明 C038 + STROBE）；
- 生成式 AI 使用披露 ✓（Declarations）；
- cover letter 重写为 JMIR 版（四点 fit + 诚实声明）；
- `journal_guidelines_snapshot.md` 重写为 JMIR 快照（含 Fast-Track 20 工作日
  付费加速选项、家族内携审稿转投政策）。

验收：85,989 B；正文 5,988 词（Word 口径）；37 页；4 表 + 6 主图；0 中文；
qc 20/20、verify 70/70、bilingual OK；摘要 sha 81549ba2…（本轮更新）。

## 投稿前剩余（全部作者侧）

1. Declarations 五处作者字段：IRB 判定落款、代码仓库 URL/Zenodo DOI、
   Funding、Competing interests、CRediT——**投稿系统必填，未代填**；
2. 确认 7_1–7_8 作者门；
3. （可选）llama-server 在线后补 GLM/KNHANES 矩阵 G2 运行；
4. （可选）JMIR Fast-Track（付费 20 工作日决定）是否使用。

完成后 7_9 打包（submission_pkg zip + cover_letter.docx），作者在
ScholarOne 提交。未投稿。


## R30k：G2 全矩阵实测完成（llama-server 在线）

作者起服务后重跑 `run_fused_system.py`，**本次覆盖全部矩阵**
（NHANES 159 + KNHANES 301 + CHARLS 14，门分布：no_rule 434 /
evidence_Bplus 32 / arbiter_yes 3 / nc_abstain 3 / no_relevant 2）。
正式计分（survey-variance gold，`g2_full_matrix_all.json`）：

| 矩阵 | G0 规则层 | G1 +NC 门 | **G2 完整智能体** |
|---|---:|---:|---:|
| NHANES Qwen 80（R11 gold） | 0.522 | 0.545 | **0.571** |
| NHANES GLM 159 | 0.480 | 0.500* | **0.522** |
| KNHANES 301 | 0.294（harness 口径） | 0.303 | **0.312** |

（*GLM 代 harness G0 0.500 与基准 full_system 0.480 的差异来自规则匹配子集；
正文 GLM 行升级为 full agent 0.522 vs 规则层 0.480。）

accuracy McNemar（NHANES-159，G2 vs 基线，逐 seed）：对 LightRAG / pure LLM /
naive RAG **全部 p < 10⁻⁶**——G2 完整智能体在 159 对 GLM 代上对三条基线全部显著。

KNHANES 如实披露：基准报告 rule layer 0.360（用 confirmatory rule_ids 含
~r02/~r03 反向规则）；registry 匹配的 G2 变体 0.312（Supplementary Table S7 注）。

正文/表/摘要同步：Table 3 NHANES 两行改 full agent（0.571/0.522）+ 消融注；
摘要 GLM 数字 0.480→0.522；Discussion 消融句加 159 对。产物
`outputs/confirmatory/g2_full_matrix_all.json`。正文（Word 口径）5,969 词。
