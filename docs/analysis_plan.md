# huiyan 分析计划（预注册）· Analysis Plan

> 版本 v1.2 · 制定日期 2026-10-12（v1.1 基础上记录协议偏离：规则修改 + 重冻结）；2026-10-14 更正记录见 §0.1（R4）与 §0.2（R5）
> **R5 口径注记（2026-10-14）**：headline 三态标签以 survey svyglm 方差（§6 预注册标准，更正 7）+ 按库 judgeable 集（更正 6）为准；数据管道修复见更正 4/5。规则集 v1.2 不变（sha 5aee851d…）。> **定位声明**：此前已运行的三库对级检验（nhanes/knhanes/charls_pair_results.csv，2026-10-11）一律定性为 **exploratory（探索性）**，其指标（P/R/F1）因口径缺陷（审核 C1/C2：金标准自证循环 + 非显著≠反证混标）**不进入论文正文**。本计划规定 confirmatory（确证性）重跑的全部口径；确证运行以本文件落盘之后为起点。

## 0. 协议偏离记录（v1.2 新增）

**偏离事件**：2026-10-12 07:12，在确证运行（2026-10-11 20:59）之后、基线运行之前，规则集被修改：
- r02 entity_a_flags += hba1c_elevated
- r03 entity_a_flags += hyperglycemia
- r04 entity_a_flags += hyperglycemia, entity_b_flags += dr_npdr
- 新增 r22 (bmi_high × retinopathy_any/dr_npdr)

**性质**：测试集拟合（test-set fitting）。修改依据来自确证运行的 gold-positive 结果，随后在同一测试集上评估 → R=1.000 是构造的，不是性能提升。

**处置**：
1. r22 与跨覆盖改动定性为**探索性规则扩展**（exploratory rule expansion），不作为确证结论的依据
2. v1.2 规则集（21 条，含扩展）在本文档落盘时冻结；此后不再修改
3. 确证重跑使用 v1.2 规则集；报告中同时呈现 v1.1（原始）与 v1.2（扩展）两版指标，明确标注 v1.2 含探索性扩展
4. r22 的 evidence_level 从 B 降为 C（引文来自单库确证结果，非 meta 分析），severity 同步降为 low

**时间线**：
| 时间 | 事件 | 规则集 |
|---|---|---|
| 2026-10-11 20:52 | analysis_plan v1.1 落盘 | v1.1 (20 rules) |
| 2026-10-11 20:59 | 确证运行（NHANES/KNHANES/CHARLS） | v1.1 |
| 2026-10-12 07:12 | 规则修改（r02/r03/r04 交叉覆盖 + r22 新增） | v1.2 (21 rules) |
| 2026-10-12 07:13 | 基线运行 | v1.2 |
| 2026-10-12 （本次）| analysis_plan v1.2 落盘，v1.2 冻结 | v1.2 |
| 2026-10-12 已执行 | 确证重跑（NHANES 7/14 复证、KNHANES 2/10、CHARLS 0/4，均 0 反证） | v1.2 |
| 2026-10-14 R5 | 五专家评审→P0 数据/口径修复+survey 方差主口径+基线协议重跑（更正 4-9，§0.2）；headline 更新为 NHANES 5/14、KNHANES 2/10、CHARLS 0/4 | v1.2（规则集不变） |

### 0.1 冻结后更正记录（2026-10-14，R4 复审后）

**更正 1 — r22 引文主题更正（元数据更正，规则逻辑与评级均未变）**
- 事实：r22 原引 DOI 10.1371/journal.pone.0089923 经核实为"BMI×白内障"meta 分析（与 r13 共用同一篇），与 r22 的视网膜病变命题不匹配；引用门 strict 判定 authentic_only（wrong eye disease outcome）。
- 处置：更换为题目匹配的前瞻队列 meta 分析（肥胖×糖尿病视网膜病变；总体 RR=1.20 [1.01,1.43]，T2DM 亚组 RR=1.40 [1.05,1.87]；DOI 10.1097/MD.0000000000011807）。r22 的 flags / severity(low) / evidence_level(C) / 探索性扩展定性均不变。
- 复验：verify_rule_citations strict 21/21 PASS（2026-10-14，连跑两次结果一致）。
- 说明：BMI×DR 方向在文献层存在异质性（另有 meta 报告 null，PMID 28562529, OR≈0.97）；r22 仍按探索性 C 级处理，不据此升级证据级别。**作者裁决（2026-10-14）：确认维持 C/low 保守处理。**

**更正 2 — headline CI 方法记录（bootstrap → Clopper-Pearson）**
- 背景：v1.2 实现中，对 rep/(rep+con) 的观测标签 bootstrap 在 7/0、2/0 等小 n 下退化（恒得 [1.0,1.0]），实现已改为 Clopper-Pearson 精确二项 CI：NHANES [0.590,1.000]、KNHANES [0.158,1.000]。
- 说明：本更正补齐方法学记录（实现先于本记录）；§3 中"bootstrap 1000 次"表述以本条为准；R4 复审发现交付物曾同时出现 Wilson 值，已统一为 CP。

**更正 3 — r04 引用门判定稳定性修复（校验基础设施，非规则变更）**
- 事实：R4 复审发现同一引文（r04）在两次相同运行中得到相反判定；根因是 skill 引用门缺少 huiyan 项目词表扩展，24 条引文中 21 条依赖 LLM 层的非确定性判定。
- 处置：按门既有的 append-only 扩展模式（jingming/mingmu 同模式）为 huiyan 补齐词表；修复后 24/24 条引文走确定性关键词层，连跑两次结果一致。不改变任何规则内容与评级。
- **已知语义局限（R5 诚信审计披露，2026-10-14）**：关键词层为标题级双侧匹配，r10/r11 唯一引文仅走单侧存在性检查（弱路径）；实测 r22 旧错误引文在该词表下同样 PASS。引用门绿灯证明力以"标题级匹配"为限，writer 阶段引用清单须以 citation_verification_report 的判定层级为准复核。

### 0.2 R5 修复批次更正记录（2026-10-14，五专家评审后）

**更正 4 — KNHANES 眼底结局编码 8/9 处置（数据管道缺陷）**
- 事实：KNHANES 眼底检查变量（E_DRP_*、E_AMD_*）编码为 0=无/1=有/8=未检查/9=不可分级；此前实现把 8/9 当"无病"阴性（占分析样本约 12.6%，且缺失与暴露相关：code 9 组高血糖患病 11.6% vs 真阴性 7.5%）。
- 处置：8/9 改按缺失处理；双眼结局改为"任一眼分级阳性"（原仅右眼）。外部复证对 OR 24.2→25.0（hyperglycemia×DR）、27.2→28.4（hba1c×DR），标签与结论方向不变（剔除未检查者后关联更强）。
- 归档：修复前输出存 outputs/confirmatory/archive_v1.2_preR5/。

**更正 5 — NHANES 视力损害变量误用（数据管道缺陷）**
- 事实：VI 分层误用 VIXPRS（屈光球镜度，仅屈光检查子样本 n≈2000）作为视力；正确变量为 VIDRVA/VIDLVA（presenting VA，Snellen 分母 20-666 编码，n≈6400/周期）。
- 处置：改为 VIDRVA/VIDLVA 较差眼 logMAR（log10(XX/20)：20/40→0.30、20/60→0.48、20/200→1.00，与预注册阈值精确对应；单眼缺失回退可用眼，Han 2021 presenting-VA 标准）。VI 对样本量恢复后 coverage 0.269→0.23（分母增大）。

**更正 6 — coverage 分母 judgeable 集硬编码（指标口径缺陷）**
- 事实：compute_metrics_v11 对三库均使用 nhanes_judgeable 集合；KNHANES/CHARLS 的可判集不同（knhanes 含 selfreport 项、cohort 仅 3 项）。
- 处置：按库取 judgeable 集。KNHANES coverage 0.263→0.233；CHARLS coverage 0.667→0.308（此前 glaucoma_selfreport 对被错误剔出分母）。precision 不受影响（被剔行均为 uninformative/NC）。

**更正 7 — §6 方差标准的落实（预注册svyglm 此前未执行）**
- 事实：§6 预注册以 R survey svyglm（strata/PSU/权重）为确证方差标准；实现为 Python 归一权重 freq_weights GLM（无设计效应校正），且未按降级路径声明。
- 处置：R5 以 svyglm 为 headline 判定标准（scripts/survey_sensitivity_export.py + survey_sensitivity_R5.R，129 对全拟合成功，q 在与主分析相同的全部 tested 对集上做 BHY）；freq_weights GLM 降为敏感性口径双呈（metrics JSON 的 sensitivity_freq_weights 子段）。影响：r22 两对（freq q=0.034/0.037，临界）在 survey 方差下 BHY q=0.204/0.260 → uninformative，NHANES 复证 7→5、P=1.0 [CP 0.478,1.0]；其余 5 条复证与 KNHANES 2 条复证的 survey p 均在 1e-9 量级以下，稳健。CHARLS 无 PSU 信息，维持点估计+声明（§6 降级路径）。
- 结论变化：r22 的"NHANES 复证"表述不再成立，r22 维持探索性 C/low 定级（与更正 1 的保守处理一致）。

**更正 8 — 方向审计触发标准对齐 §4（实现曾静默收窄）**
- 事实：§4 规定"≥2 个 A 级对同库 OR<1 即 quarantine"；实现曾收窄为"显著反向（q<0.05 且 OR<1）≥2"且未记录偏离。
- 处置：恢复 §4 记录义务——任何 OR<1 的 A 级 predicted 对标记第四态 direction_review 并落盘（direction_review_<dataset>.csv）；自动隔离保留"≥2 显著反向"为记录在案的偏离（依据：偏倚调查 docs/bias_investigation_smoking_cataract.md 表明非显著 OR<1 多为效能不足或 null——r13 BMI×cataract OR=0.986 为 null，r10 smoking×cataract OR=0.698 q=0.80 年龄分层后消失）。

**更正 9 — 基线协议修复（评测公平性）**
- seed 此前仅记入元数据、未传入 API 请求体（无复现语义）→ 已传入（OpenAI 兼容 seed 字段）；
- naive_rag 此前误用系统 EvidenceStore（A 级加权 5.0×）→ 改用专用 NaiveRAG 纯词频检索器；
- LLM 基线 prompt 此前喂内部 flag id（dr_npdr 等）→ 改用注册表人类可读名；
- full_system provider 标签 deepseek:legacy 与事实不符 → 更正 rule_engine:deterministic（该路径零 LLM 调用）；
- lightrag 内部 LLM 综合调用此前吞错（"[llm error]" 文本当证据）→ raise_on_error + 4 次退避重试；
- LLM 温度 0.0→0.7（2026-10-12，c244af7）此前未入偏离记录，补记于此；
- **解析规则透明化（round 2，2026-10-14）**：首轮重跑中 naive_rag 全部 5 seeds、lightrag 3/5 seeds 因 1-3 条"unparsable"被判 invalid——检视发现全部为明确的"证据未提及"陈述（如 "the text does not mention serum uric acid"），语义上即 NO（证据不足⇒不支持为危险因素），并非管道故障。处置：prompt 明确"证据未提及→答 NO"；解析层对明确的 no-evidence 陈述映射为 NO 并落盘 parsed="no_evidence_inference"（透明可审计），空响应/乱码/真歧义仍计失败。首轮输出归档 baseline_predictions_R5_round1.jsonl，full_system（确定性、不受解析规则影响）原样沿用；
- 全部基线在新 gold（survey 方差口径，5 复证）上按预注册 5 seeds [11,22,33,44,55] 以本地 qwen3.8-27b（thinking disabled, temp=0.7）重跑；差异显著性以配对 McNemar 报告，"优于"表述仅限统计显著的对。



### 0.3 R11 更正记录（2026-10-15，全链复审后：变量操作化修复）

> 触发：R11 全链实跑复审发现 4 处变量层硬错误（证据经独立重算证实：暴露率体检
> 38.7%/68.5%/1.7%/3.8% 与官方字典/国别统计对照全部不符）。处置原则与 R5 相同：
> 数据正确性修复非规则变更；修复后全链重跑，旧数字按双呈纪律保留于 R5 记录。

**更正 10 — NHANES current_smoking 参照组错误（A1）**：SMQ040 仅对 SMQ020==1
（一生吸≥100 支）者提问，原 `.where(SMQ040∈{1,2,3})` 把全部从不吸烟者置缺失，
0 组实为已戒烟者（40+ 样本暴露率 38.7%，真实当前吸烟应≈20%）。修正：
current = SMQ020==1 & SMQ040∈{1,2}；参照 = never ∪ former。直接后果：
current_smoking×dr_npdr 的显著"保护"信号（OR 0.70，即 direction_review 中 r10 相关
反向入册行）系编码伪影，修正后 replicated→uninformative。

**更正 11 — NHANES alcohol_intake 用终生门槛题（A2）**：ALQ101 是"一生是否喝过
12 杯"（阳性≈62%），非当前饮酒。修正：drinker = ALQ120Q≥1（过去一年有饮酒天数）；
参照 = ALQ120Q==0 或终生不饮。

**更正 12 — KNHANES 吸烟/饮酒变量无效（A3/A4）**：官方字典证实 BS1_1=终生吸烟
分类（==1 仅 1.7%，非当前吸烟）、BA2_2_1=酒后骑自行车、BA2_22=乘坐酒驾车辆、
BA2_12/13=安全带；正确的 BS3_1（当前吸烟）与真实饮酒变量均不在现有帧内。
处置：两暴露在帧重建前置 NA（不可测），相关配对转 underpowered——宁缺勿假
（原操作化曾产出 alcohol×amd_late OR=0.542 进入金标准的假信号）。KNHANES
规则对 10→7（2 复证不变、0 反证不变）；另出现 1 个 uncovered 的 contradicted 对
（hyperglycemia×amd_late，非规则覆盖，不入 headline 反证计数但如实入册）。
HE_UAScr 为砷（A7 注记）：尿酸对在 KNHANES 全波不可测（原注释错误已更正）。

**更正 13 — 双 precision 口径并列（B1）**：声明域口径 precision_rule（分母=rep+con，
剔除 uninformative）与保守二元口径（uninformative 记 FP，与基线 P 同构）此前并存
于不同交付物且未标注。现两个口径在全部 metrics JSON 与 performance_matrix 并列
（新列 precision_binary_uninf_as_fp）：修正后 NHANES 1.000 [0.478,1.0] vs 0.333
[0.118,0.616]；KNHANES 1.000 [0.158,1.0] vs 0.286 [0.037,0.710]。主指标二选一
为作者决策项（见 R11 FIXLOG 决策点）。

**修正后 headline（survey 方差主口径，2026-10-15 重跑）**：NHANES 15 规则对
5 复证 0 反证（coverage 0.242）；KNHANES 7 规则对 2 复证 0 反证（0.241）；
CHARLS 两层不变（0 信息性对）。基线（冻结预测 × 修正 gold 双呈，
baseline_summary_R11_corrected_gold.json）：full_system F1 0.417→0.435、
pure_llm 0.347→0.301、lightrag 0.316→0.327、naive_rag 0.073→0.080；
McNemar 显著性结论不变（vs pure_llm/naive_rag 显著，vs lightrag 不显著）。
G2 融合系统 NHANES F1=0.500 维持、KNHANES 0.333→0.444。

**新增审计事实（C1，入册）**：21 规则中 8 条（r07/r08/r09/r16/r17/r18/r21 为 B 级、
r19 为 C 级）从未被任何层测到（rule_coverage_audit_R11.csv）；3 条 A 级规则
（r10/r11/r13）被测到但 0 复证。跨库同对标签一致率 48 对中 29→18（37.5%）。

### 0.4 R11 续：KNHANES 帧重建（2026-10-15，取代 §0.3 的"置 NA"处置）

> §0.3 对 KNHANES 吸烟/饮酒采取的是"帧重建前置 NA、声明不可测"的保守路线。
> 后续回溯到原始 Rdata 后确认：**正确的变量在源数据里是齐的，是当年的帧构建脚本
> 没有取**。因此改为重建帧，把"不可测"变成"可测"，本节数字**取代 §0.3 中
> KNHANES 相关的全部计数**。§0.3 的 A1/A2（NHANES 侧）仍然有效。

**根因**：`data/raw/knhanes_frames/*.csv` 没有对应的生成脚本（仓库内只有读它的代码），
且该脚本存在四类缺陷：① 未取 `BS3_1`（当前吸烟）、`edu`、`incm5`；② 只用了
2008–2012 的眼科命名（`E_DRP_*`/`E_AMD_ELY_*`），**2016–2021 的新命名
（`E_DM`/`E_AMD`/`E_GR`/`E_DME`）完全未合并**；③ 未加载 `hnYY_ap`（大气污染）模块；
④ 用 `BA2_2_1`（酒后骑自行车）当饮酒暴露。

**更正 14 — KNHANES 眼科结局命名换代未 harmonize（C8）**：官方字典证实
`E_DM` = 糖尿病视网膜病变，而 **`E_DR` = "目前是否使用眼药水"，不是 DR**；
2016–2021 的 AMD/青光眼分别为 `E_AMD`/`E_GR`，IOP 为 `E_Pr_1`。
修正后 `retinopathy_any` 在 2008–2012（`E_DRP_R/L`）与 2016–2021
（`E_DM`/`E_DM_r/l`）两套命名下均可构造。**直接后果：此前被判"结构性不可测"的
14 个配对（尿酸/CRP × 眼结局）实际可测**，其中包含登记为阴性对照的 r01 与 B 级 r06。

**更正 15 — KNHANES 缺 SES 协变量（C9）**：`edu`/`incm5` 存在于全部 wave
（hn07_all…hn24_all），只是帧构建未取。修正后 KNHANES 协变量为
`age, age2, sex, edu, incm5`。

**更正 16 — 暴露 flag 名与注册表不一致**：帧内暴露键名（`pm25_high`、
`sun_exposure_high`、`vitamin_d_deficient`）与 `entities_a.csv` 的 flag 词汇
（`pm25_exposure`、`uv_exposure`、`vitamin_d_deficiency`）不一致，导致
`match_rules()` 永不命中，规则被误判为"不可测"。修正后 r16/r17（PM2.5）可测，
并补 `cadmium_exposure`/`mercury_exposure`。

**更正 17 — 指标口径三项**：
(a) **双家族 FDR**：单一家族跨 >100 个无规则配对会稀释规则配对效能。现分
**确证家族**（规则相关配对，主指标）与**探索家族**（全矩阵，未覆盖发现）并报；
(b) **`coverage` 定义修正**：原 `len(规则配对)/len(全部可测配对)` 在矩阵扩容后
退化为 0.08–0.23 的无意义小数，现改为 `P(可检验 | 存在规则, 可判, 非阴性对照)`；
(c) **效能分析与中介分析纳入主交付**（§17、§18）。

**修正后 headline（survey svyglm 主口径，2026-10-15 最终重跑）**：

| 层 | 规则相关配对 | 已检验 | coverage | 复证 | 反证 | 精度(声明域) | 精度(保守) |
|---|---|---|---|---|---|---|---|
| NHANES | 18 | 16 | 0.889 | 6 | 0 | 1.000 [0.541,1.0] | 0.375 [0.152,0.646] |
| KNHANES | 17 | 15 | 0.882 | 5 | 0 | 1.000 [0.478,1.0] | 0.333 [0.118,0.616] |
| CHARLS 2011 | 4 | 4 | 1.000 | 0 | 0 | — | 0.000 |

- 跨库同对标签一致率：85 对中 71 = **83.5%**（§0.3 的 37.5% 系帧缺陷所致）
- 从未被任何层检验的规则：**5 条**（r07/r09/r18/r19/r21），原因逐条见
  `configs/variable_map.yaml` 的 `rule_testability`
- **A 级规则 0/3 复证**，两个库一致（`outputs/tables/headline_sensitivity.csv`）

**§0.3 中以下数字作废**：KNHANES 规则对 10→7、2 复证、coverage 0.241、
跨库一致率 37.5%、"8 条从未被测到"。

### 0.5 R11 续：CHARLS 首次过码本门（2026-10-15）

> CHARLS 此前**从未过任何码本/参考率门**，是全项目最后一处未审的操作化。
> 补门后发现 1 个 C1 类错误 + 1 个错参考值 + 2 个未解决缺口。

**更正 18 — CHARLS 2011 current_smoking 参照组错误（C1 类第三次出现）**：
`da061`（"是否还在吸"）**只对 `da059==1`（曾经吸烟）者提问**。原实现把分母限制为
`da059` 与 `da061` 均非缺失，于是分母变成"曾经吸烟者"，得到 **77.0%** 的"当前吸烟率"
（中国参考值 27%）。修正为 分子 = `da059==1 & da061==1`、分母 = `da059` 非缺失，
得 **28.1%**，与参考值吻合（比值 1.04）。同时补 `ever_smoking`(40.1%)、`former_smoking`。
**这是同一错误类别在本项目中的第三次出现**（NHANES C1、KNHANES C6、CHARLS）。

**错参考值（记录以免重蹈）**：HbA1c≥6.5% 在中国人群中患病率约 **5–7%**，而非
OGTT/FPG 定义的糖尿病患病率 11–13%——HbA1c 对中国人群表型的敏感度低，约为 OGTT 的一半。
若用 11–13% 作参考，会把**正确的**变量判为坏。**参考值必须与判定标准同源。**

**未解决缺口（已在论文 Limitations 声明）**：
1. **CHARLS 2015 吸烟暴露门失败并排除**：当前吸烟 7.5%、曾吸烟 12.4%（参考 27%/40%）。
   与 2011 波（28.1%/40.1%）差 3.7 倍，说明 2015 问卷的吸烟题项编号或跳转逻辑不同。
   需 2015 问卷码本才能定位；在此之前 **CHARLS 不得产出任何吸烟结论**。
2. **CHARLS HbA1c 跨波不可比**：≥6.5% 患病率 2011 波 4.9% vs 2015 波 13.1%（差 2.7 倍），
   与 KNHANES HbA1c 的跨波问题同源。§16 记录的"CHARLS 2015 层 hba1c×cataract
   OR=1.71, p=0.0026 接近显著"因此**不能作为佐证**，只能作为 caveat 报告。

**修正后 CHARLS 连续矩阵**：两波各 16 对，共 32 对，**0 显著**（单家族 FDR）。
2011 波门：0 硬失败；2 项 warn（`crp_elevated` 0.180 vs 0.35、`uric_acid_elevated`
0.077 vs 0.14），保留但记录。

**§6 降级路径适用**：CHARLS 无 PSU/strata，用调查权重 + 模型方差（**非 svyglm**），
此降级为显式声明而非默认等同。

## 1. 分析单元与定义域（分母纪律）

- 单元 = (A-flag, B-item) 对。
- **规则声明域**：21→20 条规则（r15 镉×白内障撤销，A1 决策 2026-10-11：唯一证据报 OR≈0.97 无关联）。
- **B 侧修正**：r05 dyslipidemia 从 amd_early → amd_late（证据支持新生血管性 AMD，不支持早期特异）。
- B 侧剔除条目不变：vi_mild、glaucoma/amd_selfreport、optic_disc_abnormality（已声明剔除，只报覆盖率）。
- **FN 定义修订**：v1.0 的 recall_gap 因类型 2 空白在注册表中无对应实体（flags 为 physical_inactivity 而非 physical_activity）导致分母恒为 0，指标不可识别。v1.1 以 **coverage** 取代 recall 作为透明度指标（见 §3）。
- r01（尿酸×白内障）登记为**阴性对照规则**（negative_control），单列报告，不进 headline 指标。
- r14（铅×白内障）引文更换：IJHEH 2016（血铅 OR≈0.97）→ JAMA 2004（骨铅蓄积，阳性）。理由：骨铅是与白内障相关的终身蓄积测量；血铅为当前暴露，可能低估效应。

## 2. 金标准三态标签（取代二值 gold，审核 C1/C2）

对每个可测规则对（引擎输出的 predicted-positive 对）在库内估计加权关联后：
- **replicated**：q<0.05 且方向与规则声明一致；
- **contradicted**：q<0.05 且方向相反（唯一计入 FP 的状态）；
- **uninformative**：q≥0.05（无论方向——不构成反证，不计 FP，单列报告）。
- **separation**：拟合分离/准分离时标记该状态并剔除（不用 uninformative 掩盖）。

## 3. headline 指标（全部带 bootstrap 95% CI，1000 次重采样，审核 C7）（v1.2 更正：CI 方法为 Clopper-Pearson 精确二项，见 §0.1-更正2）

- **Precision_rule = replicated / (replicated + contradicted)**（引擎发言范围内的精确率；uninformative 单列）；
- **Coverage = rule-covered testable pairs / total testable pairs**（透明度指标，v1.1 新增，取代不可识别的 recall_gap）；
- ~~Recall_gap~~（**v1.1 撤除**：FN 分母结构为 0，指标不可识别。若需恢复须先扩大覆盖域并修订预注册）；
- 阴性对照（r01）与全量明细表单列；
- **分层**：证据级 × 数据集；
- **Δ 指标只在两层均可判的交集对上计算**（审核 C8）。
- **通过线修订**（v1.1）：**只考核 precision_rule**（≥0.70 内部 / ≥0.80 外部）；coverage 如实报告，不设通过线。原 sens/spec 等价性**不成立**（precision_rule 是单一指标，无法同时映射 sens 与 spec 两个维度），此声明予以撤回。

## 4. 方向合理性前置审计（审核 C4）

指标产出前必须先过：对**证据级 A 的确立危险因素对**（r10/r11/r13）逐对核对库内方向；若 ≥2 个 A 级对在同库呈反向（OR<1），该库标签进入 **quarantine**（隔离）：先查暴露编码、结局口径、选择偏倚（存活/患病）、反向因果（现吸烟 vs 曾吸烟），出具书面归因后方可解除；未解除前该库不产出 headline 指标。

## 5. 协变量统一（审核 C3）

- **主模型（全层统一）**：age、age²/100、sex。
- **敏感性（仅 NHANES 可得层）**：+race、education、PIR、BMI、smoking（暴露为该变量时移除自身）。
- 层间比较只用主模型口径；敏感性结果单列附录。

## 6. 方差估计（审核 C5）

- NHANES：以 R `survey` 包 svyglm（strata=SDMVSTRA, psu=SDMVPSU, weights=WTMEC2YR）为确证标准；Python 归一化权重的 GLM 仅作开发近似并声明。
- KNHANES：同法（kstrata/psu，wt_itvex）。
- CHARLS：个体权重 svydesign（无分层信息时声明）。
- R survey 不可用时的降级路径：报告 design-effect 无法校正的局限，headline 只报点估计+bootstrap CI（对权重不敏感），并显著标注。

## 7. 多重检验

每库内对全部进入检验的对做 BHY FDR；报告 q 与 p 双列；α=0.05。

## 8. 数据集交付口径（审核 B4/B5/B6）

- 目标维持 config 值：dev 400 / intval 400 / extval-K 300 / extval-C 120（**上限**）；
- 每集产出 per-dataset `cases.jsonl`（含 provenance：变量映射、纳入排除、每步 N）后，验证脚本必须**从 cases.jsonl 读取**（脚本内即时造对不再允许，审核 B5/B8）；
- 引擎与验证脚本分离：验证只消费 `huiyan_agent.risk_rules` 的输出（审核 B8）。

## 9. 基线与 seeds

4 基线（pure_llm / naive_rag / lightrag / full_system）× ≥5 seeds；seed 列表预注册 [11, 22, 33, 44, 55]。

## 10. 预注册阈值（不变项）

内部 sens≥0.70 / spec≥0.60；外部 sens≥0.70 / spec≥0.80（按新三态口径换算后评估：precision_rule≥0.70 内部 /≥0.80 外部对应原 spec 语义——换算关系在确证报告中显式给出）；未达标 → state `blocked[]` 记录，不得标 complete。

## 11. 版本与变更

- 本计划一经确证运行开始不得修改；任何修订以 v1.1+ 记录变更理由。
- 探索性结果与确证性结果在 outputs/ 下分目录存放：`outputs/exploratory/`（移入现有三库产物）与 `outputs/confirmatory/`。

## 12. 文献层外部验证（R5.1 预注册，2026-10-15 落盘——先于任何文献验证运行）

**动机**：三库验证均为横断面/自报测量；作者裁决（2026-10-15）增加独立于全部四个数据库的**文献层外部验证**（literature-based external validation）：以公开发表文献的方向一致性为金标准，覆盖所有研究类型（RCT/队列/病例对照/横断面/meta/系统综述/case report/机制研究）。

**预注册协议（本节落盘后判定阈值不得改动；任何偏离按 §0 模式记录）**：

1. **验证单位**：21 条规则（v1.2 冻结集）。每规则构造检索式 = 暴露人类名（含同义词 OR 展开）AND 眼病名（含同义词 OR 展开）。
   - **检索同义词表披露（2026-10-15）**：注册表 primary_name 含操作化后缀（如 "Cataract (self-report or surgery)"、"Late AMD (graded)"），在文献中从不逐字出现；故检索词采用逐 flag 的标准文献词表，全文落盘于 scripts/literature_validation.py 顶部 A_FLAG_TERMS/B_FLAG_TERMS（如 cataract_any→["cataract"]、amd_*→["age-related macular degeneration","macular degeneration"]、vision_impairment_*→["visual impairment","vision loss"]）。term 以非短语 [tiab] 匹配（PubMed 自动分词，宁宽勿漏——相关性由抽取层把关）。
2. **检索**：PubMed E-utilities esearch（`english[lang] AND human[filter]`），默认 relevance 排序，每规则取前 40 条；efetch 取 title/abstract/pubtype/year。检索失败重试 3 次，仍失败该规则标 `search_fail`（不得静默补）。
3. **独立性排除（防循环验证）**：剔除规则自身引文（citation_verification_report 中该规则的 DOI/PMID）；与证据池（evidence_chunks 901 unique PMIDs）的重叠**不剔除但逐篇标记**，并做敏感性分析（剔除重叠后重判）。
4. **抽取协议**：本地 qwen3.8-27b（thinking disabled，temp=0.0，seed=20261015），逐篇输入 title+abstract，输出 JSON：`relevant`（是否研究/报告该暴露×该结局的关联）、`direction`（concordant=与规则声明方向一致 / discordant=相反 / null=明确无关联 / unclear）、`study_type`（RCT/cohort/case_control/cross_sectional/meta_systematic/case_report/mechanistic/review_other）、`note`。JSON 解析失败计数落盘（fail-loud）；随机 15% 复跑第二次做稳定性检查。
   - **Round-2 修订（2026-10-15，全量重抽，非选择性）**：Round-1（750 篇，0 解析失败）暴露措辞陷阱——"低暴露→风险升"类声明（r07/r08）被 LLM 判为与"高暴露→风险降/治疗有效"文献 discordant（r08 的 10/12 discordant 全为抗氧化剂保护/治疗研究，即同一关联的相反措辞）。处置：prompt 增加方向等价说明（"LOW raises risk 与 HIGH lowers risk/treats 为同一关联，判 concordant"），**全部 750 篇统一重抽**（不做规则选择性重抽，避免协议不一致）；Round-1 归档 `lit_validation_extracts_round1.jsonl` 留作抽取误差的实证材料。
   - **Round-3 修订（2026-10-15，全量重抽）**：Round-2 中 framing note 对 r07 生效（mixed→replicated）但 r08 恶化（conc=2/disc=16）——检视为治疗/干预类文献（纳米制剂抗氧化治疗白内障等）的方向映射不稳（同类文献同轮内一次 concordant 一次 discordant，qwen 3bit 语义判定能力限制）。处置：改**两步判定协议**——Step1 分类 etiological（暴露水平 vs 风险）/interventional（给予/去除暴露的干预）；Step2 按类别映射（etiological 按"高暴露⟺低风险为同一关联的反向措辞"；interventional 补充有效=concordant、无效=null、恶化=discordant），输出增 study_class 字段；仍全量重抽。Round-2 归档 `lit_validation_extracts_round2.jsonl`。三轮全量重抽的 r08 分歧本身作为"LLM 抽取层对治疗类文献敏感"的实证，写入 limitations。
   - **Round-4 人工复核修正（2026-10-15，R7 复审后）**：R7 独立抽查 12 篇确认 4 处方向判定错误（r08 三篇治疗有效误判 discordant：PMID 42193946/42636787/41864488；r17 一篇 PM2.5 未报告却判 concordant：PMID 34454934）。按抽查证据裁定修正这 4 篇（`adjudication` 字段落盘理由，round3 归档 `lit_validation_extracts_round3.jsonl`）；**未被抽查覆盖的同类文献不作臆改**（保守原则）——r08 修正后 14 conc/5 disc 仍为 mixed；precision_lit 不变（16/18=0.889 [0.653,0.986]）；S3 双跑一致率如实降为 97.1%（68 对中 2 对因裁定修正而与复跑不一致）。
   - **协议-实现差异披露（R7 复审发现，记录在案不重跑）**：① §12-2 声明含 `human[filter]`，实际 0/21 条检索式未加该 filter——影响为可能纳入动物/机制研究，但抽取层已标 study_type=mechanistic 且 S2 敏感性仅保留人群研究，结论不受影响；② §12-2 声明"默认 relevance 排序"，实际 PubMed 默认排序为近因序（750 篇中 2025-2026 年占约 77%）——治疗学新文献挤占 top-40 的检索偏倚已在 limitations §7.5 声明；③ 预注册时序对 round-3 可证（§12 mtime 先于 round-3 运行），round-1/2 的协议先行性无 git 快照可证，如实降格为"round-1/2 属协议形成期的探索性运行，正式结果以 round-3+round-4 为准"。
5. **判定阈值（预注册，先落盘）**——按该规则 relevant 文献计数（n_conc/n_disc/n_null，不加权为主分析）：
   - `replicated_lit`：n_conc ≥ 2 且 n_conc > n_disc 且 n_conc ≥ n_null；
   - `contradicted_lit`：n_disc ≥ 2 且 n_disc > n_conc；
   - `mixed_lit`：n_conc ≥ 2 且 n_disc ≥ 2；
   - `null_dominant_lit`：n_null ≥ 2 且 n_null > max(n_conc, n_disc)；
   - `uninformative_lit`：relevant 总数 < 2（证据不足）。
   - 负控规则 r01 不参与 headline 汇总，单列。
6. **敏感性分析（预注册三组）**：S1 剔除证据池重叠 PMID 后重判；S2 仅人群研究（RCT/cohort/case_control/cross_sectional/meta_systematic）后重判；S3 复跑稳定性（15% 双跑不一致率）。
7. **汇总指标**：`precision_lit` = replicated_lit 规则数 / (replicated_lit + contradicted_lit + mixed_lit)，Clopper-Pearson 95% CI；逐规则文献构成表（各研究类型计数）随明细落盘。
8. **定位声明**：文献层是**外部一致性验证**，不是因果确证；与三库层结果并列呈报，不合并计算；检索窗口、发表偏倚、LLM 抽取误差在 limitations 声明。产出物：`outputs/confirmatory/literature_validation_R5.csv`（逐篇明细）+ `literature_validation_summary.json` + 敏感性三组。

## 13. 系统性能优化：证据门控融合推理（R5.2 预注册，2026-10-15 落盘——先于任何融合系统运行）

**动机与约束**（作者指令"系统性能还需要优化"）：v1.2 规则集冻结不得修改（改则确证失效并重蹈 §0 test-set fitting）；三库 gold 不得用于策略调参（NHANES 已被 v1.2 拟合污染、KNHANES/CHARLS 为外确证）；dev 集金标准为 `rule_defined`（provenance=rules.yaml）属循环结构**不可用作调参集**（R5.2 查明）。因此本优化采用**先验门控策略 + 预注册消融**框架：策略基于领域先验与系统构建时可得信息（规则元数据、证据池检索）设定，不做数据驱动调参；评估一次性跑完，无论升降分如实报告。

**基线口径统一（先行修复）**：基线评估分母改为与确证层 metrics 相同的 judgeable 口径（NHANES 62 tested 对；此前基线用全量 80 对，与非 judgeable 结局（vi_moderate/severe 等）混计，口径不一致）。重算基于既有 5-seed jsonl，不重跑 LLM。

**门控策略（三档消融，先验设定）**：
- **G0（裸规则）**= 现状：规则命中即发言 YES（含负控）；无规则命中 UNKNOWN。
- **G1（负控门控）**= G0 + 负控规则（negative_control）命中不发言（UNKNOWN）。理由：负控在评估协议中本就单列，系统发言语义上不应包含预期为 null 的对。
- **G2（证据门控+仲裁融合）**= G1 + 对每个非负控命中对做证据池检索确认（EvidenceStore，query=暴露名+结局名，top_k=5）：
  - 存在等级 ≥B 且实体匹配（块实体含该暴露或该结局）的相关块 → 发言 YES；
  - 仅有 C/D/E 级相关块 → **LLM 仲裁**（本地 qwen3.8-27b，thinking disabled，temp=0.0，seed=20261015；输入=检索块文本，输出 YES/UNKNOWN 严格二值）；
  - 无相关块 → UNKNOWN。
  理由：系统架构声称"规则+证据+LLM"三件套，G2 使其名副其实；仲裁仅作用于证据不足的边界命中（C 级证据），且为确定性温度保证可复现。

**评估协议**：主评估=NHANES judgeable 62 对（survey 方差 gold）；外层=KNHANES judgeable（43 对）/CHARLS；文献层按规则级发言重算 precision_lit（被门控弃权的规则不计入分母，双呈）。对比：G0/G1/G2 互比 + G2 vs 三个 LLM 基线（公平协议：同后端同温度纪律；G2 的 LLM 组件 temp=0 属仲裁确定性设定，与基线生成任务 temp=0.7 的差异如实披露）。显著性：G2 vs G0 配对 McNemar（精确）。产出：`outputs/confirmatory/fused_system_R5.jsonl` + `fused_system_summary.json`。

**运行记录（2026-10-15，含一次实现修正）**：
- 实现修正（bug fix，非策略调整）：首次运行的证据检索词源误用注册表操作化名（如 "Any retinopathy (graded)"），与证据池文献语言不匹配，导致 4 个 TP 被误判"无相关证据"弃权（G2 F1 一度 0.143）；修正为 §12 文献词表后重跑。检索词源问题与文献层检索（§12-1）同源，已两处一致修正。**时序披露（R8 复审指出）**：§13 落盘先于融合系统运行的声明无独立可证证据（无预运行 git 快照、首跑产物被覆盖），证据等级为"叙事自洽+内部一致"；与 §12 同样降格披露，正式结果以修正后重跑为准。相关块判据以实现为准：主判据=块 entities_a（规则关联标记）含命中规则 id，辅判据=块文本双词命中（文献词首词），括注先前表述与此不一致处以本句为准。
- 结果（judgeable 口径，survey 方差 gold）：NHANES **G0 F1=0.455 → G1 0.476（负控门控）→ G2 0.500（P 0.333→0.385，R 0.714 不变，TP 5 全保住）**；KNHANES G0 0.308 → G2 0.333；CHARLS 0 TP 不变（FP 5→4）。门控构成：evidence_Bplus 26、arbiter_yes 3、nc_abstain 2、no_relevant_evidence 2。
- 显著性：G2 vs G0 McNemar p=0.50（仅 2 对 discordant——改善方向一致但小样本下未达显著，如实报告）；**G2 vs 三个 LLM 基线全部显著**（pure_llm p=0.001-0.012、naive_rag p=0.012-0.023、lightrag p=0.012-0.022——G0 对 lightrag 此前不显著 p=0.057-0.092）。
- **归因红线（R8 复审指出）**：G2 相对 G0 的 FP 下降（10→8）全部来自负控弃权（r01，G1 已实现）与 r05 无证据弃权；**LLM 仲裁 3 次全部 YES、未拒绝任何规则命中**——论文不得将 F1 提升归因于"LLM 仲裁把关"，提升应归因于负控门控与证据存在性门控；仲裁组件当前价值是架构完整性（边界证据路径存在且可复现），非判别增益。

## 14. 系统性能优化 II：文献共识门控 + 证据直推（R5.3 预注册，2026-10-15 落盘——先于任何 R5.3 运行）

**动机**（作者指令"再次优化"）：G2 后 FN=2（hyperglycemia×vi_mild、current_smoking×dr_npdr——均无规则覆盖）；剩余 FP 中含文献共识分歧规则（r08 smoking×cataract，文献层 mixed）。两项先验扩展均不触碰冻结规则集、不经 gold 驱动调参。

**G3 = G2 + 文献共识门控（先验）**：命中规则的文献层判定（§12，独立 PubMed 750 篇共识）为 `contradicted_lit` 或 `mixed_lit` 时该次发言降为 UNKNOWN（文献共识分歧的规则不发言）；`uninformative_lit` 保持发言（证据不足≠反对）。**双重角色披露**：文献层判定既作外部验证报告（§12）又作 G3 门控先验——三库指标与文献层指标须分别解读，论文显式披露；去循环敏感性：G3 仅影响 r08 在 NHANES 的一对发言（r07 三库无暴露测量），单看 G4-无G3 的结果一并报告。

**G4 = G3 + 证据直推路径（先验，严门槛）**：无规则命中时，若证据池检索存在 **≥2 个等级 ≥B 且双实体匹配**（暴露文献词与结局文献词均命中块文本/实体）的块 → LLM 严格仲裁（prompt 要求"明确报告该暴露与该结局的阳性关联才答 YES，否则 UNKNOWN"；本地 qwen temp=0.0 seed=20261015）→ YES/UNKNOWN；不满足门槛 → UNKNOWN。理由：系统架构本含 RAG 组件，证据池强支持时发言是"规则+证据"融合的自然延伸；45 个 no_rule·非 replicated 对的 FP 风险由双块 B 级门槛+严格仲裁控制。

**评估**：口径同 §13（judgeable、survey 方差 gold、三库+McNemar 全对比 G0/G2/G3/G4 与三基线）；无论升降分如实报告。产出：`outputs/confirmatory/fused_system_R53.jsonl` + `fused_system_R53_summary.json`。

**运行记录（2026-10-15）——两项扩展均为无增益路径，正式系统定格 G2**：
- **G3（文献共识门控）= 空操作**：三库全部指标与 G2 完全相同（NHANES F1 0.500、KNHANES 0.333）。原因：文献层判 mixed 的两条规则（r07 维D×DR、r08 抗氧化×白内障）在三库 tested/judgeable 集中没有发言对（r07 的暴露 NHANES 未测量、r08 命中对未达 tested）——门控对象不存在。G3 无害亦无增益；双重角色担忧随之消解（文献层判定实际未进入任何三库预测路径），论文可如实表述"文献门控经预注册评估为无操作路径"。
- **G4（证据直推）= 有害路径**：NHANES FP 8→12（直推 4 次发言全为 uninformative 对：crp/smoking/alcohol × amd_early、alcohol×amd_late——AMD 块在证据池中占比高使双块门槛易过，但 NHANES AMD 对功效不足全为 uninformative）；两个目标 FN（hyperglycemia×vi_mild、smoking×dr_npdr）连 ≥2 B 级双实体块门槛均未过（vi/smoking-DR 语境块稀少）——门槛与目标错位。F1 0.500→0.417；KNHANES 同向变差（0.333→0.250）。**负结果如实报告**：证据直推在当前证据池分布（检索特异度不足）下不可行；未来需 per-对检索式或语义检索升级后方可重试。
- **正式系统 = G2**（§13），R5.3 消融证明其边界。G3/G4 数字保留于 fused_system_R53_summary.json 供论文消融表使用。

## 15. 系统性能优化 III：语义检索层（R6.0 预注册，2026-10-15 落盘——先于任何 R6.0 运行）

**动机**（作者指令"不要在乎工程量大小，对整个工程优化性能"）：§14 已证明瓶颈=关键词检索特异度（G4 失败根因）。本节启用既有语义资产：LightRAG 向量库（1054 条向量全量 embedding，Ark Doubao 2048 维，与索引同模型查询）替代关键词检索作为证据确认/直推的检索层。

**语义检索定义**：查询向量=文献标准词（§12 词表）"暴露词+结局词"的 embedding；候选=vdb_chunks 全库余弦相似度 top-8；**相关块**=相似度 ≥τ 且（块首实体注记 `[exposure:…|outcome:…]` 命中该暴露或结局 flag 名 **或** 块文本含双文献词）。

**先验阈值与敏感性**：τ 主值 **0.55**（先验，非搜索）；敏感性 τ∈{0.45, 0.65} 全报告不择优。等级门槛沿用 §13/§14（B 级）。

**两档系统**：
- **G5a（语义确认）**：规则命中（非负控）→ 语义检索 → 相关块最高等级 ≥B → YES；否则 LLM 仲裁（§13 同款，temp=0 seed 固定）。
- **G5b（语义确认+语义直推）**：G5a + 无规则命中时，若相关块中等级 ≥B 者 **≥2 个且注记双命中（exposure 与 outcome 都在注记中）** → 严格仲裁（§14 同款）→ YES/UNKNOWN；否则 UNKNOWN。双命中注记要求是 §14 失败后的先验收紧（语义相似+双侧实体注记，比"文本双词"更特异）。

**评估**：口径同 §13/§14（judgeable、survey 方差 gold、三库、McNemar vs G0/G2 与三基线）；τ 敏感性三档全报告；无论升降分如实报告。产出：`outputs/confirmatory/fused_system_R6.jsonl` + `fused_system_R6_summary.json`。若 G5b 仍为负结果，则语义直推结论=需 per-对检索式训练，正式系统维持 G2/G5a 中较优者（以主 τ 值为准，敏感性仅佐证稳健性）。

**运行记录（2026-10-15）——语义层无净增益，正式系统定格 G2（F1=0.500）**：
- **时序披露（R9 复审要求，与 §12/§13 同款）**：本节落盘先于 R6.0 运行的声明无独立可证证据（无预运行 git 快照），证据等级为叙事自洽+实现一致；正式结论以运行记录与落盘产物为准。
- **G5a（语义确认）NHANES F1=0.476 vs G2 0.500**：唯一差异对 dyslipidemia×amd_late——关键词版（规则关联判据）判无相关证据弃权，语义版 top1 相似度 0.756 召回成功并过 B 级门槛而发言，但该对 gold=uninformative（NHANES AMD 功效不足）→ +1 FP；KNHANES 因同一对退化（G2 0.333→G5a 0.308）。**根因洞察：B3 实体注记（548/1054=52% 覆盖）已把规则-证据对应编码进块首，关键词的 linked_rules 匹配在注记化证据池上与语义检索近似等价——检索层不是当前瓶颈**；
- **G5b（语义直推）零触发**：110 个无规则对的门槛计数全部为 0——双注记命中要求存在逻辑自锁（注记按规则 flag 打标，无规则命中对天然缺乏双注记块），负结果如实报告；与 §14 G4（门槛太松 FP 爆炸）合并构成实证：**无规则发言的先验阈值空间中不存在可用中间点**（松则 FP 灾难、严则自锁零触发）；
- **τ 敏感性**：judgeable 口径下 0.45/0.55/0.65 三档结果恒等（相关性判定由注记/双词命中主导；3 个非 judgeable 对在 τ=0.65 有翻转，不影响任何指标分母）——预注册阈值设了但被数据证明与判别无关，稳健性的正面解读；
- **G5a 分支歧义括注**："否则 LLM 仲裁"的完整语义以实现为准（run_fused_system_v3.py 镜像 §13 G2 三分支：≥B 发言 / 有相关块但低级→仲裁 / 无相关块→UNKNOWN）；
- **正式系统 = G2**（§13）。R6.0 大工程结论：性能上限的三重约束=规则集冻结（科学纪律）、gold 层功效（FP 多为 uninformative 而非方向错误）、无规则发言缺乏独立可信依据；进一步提升需新数据扩容（如 NHANES 新周期结局测量）或预注册 v1.3+全新盲测，非推理层工程。
- 文献层不变（文献层验证规则声明本身；门控为对级发言策略，不改变规则声明的文献共识判定）。

## 16. 时间外验证层：CHARLS 2015 波（R6.1 预注册，2026-10-15 落盘——先于任何 2015 层运行）

**动机**（作者指令"继续优化性能"，R6.0 证明推理层已到上限后的数据侧扩展）：NHANES 2011-2018 后续周期本地不可用（2013-2018 目录空、2011-2012 缺实验室/检查文件）；**CHARLS 2015 波数据齐全**（Blood.dta n=13,420 / Health_Status n=20,967 / Biomarker / Weights），且 **v1.2 规则集（2026-10-12 冻结）从未接触过 2015 数据**——该波构成干净的时间外验证层（temporal external validation，半盲：暴露/结局操作化沿用 2011 定义，但规则迭代期间从未见过 2015 的任何对级结果）。

**预注册协议**：
1. **暴露**（操作化与 2011 层/临床阈值一致）：uric_acid_elevated=bl_ua（性别阈值 6.8/5.7 mg/dL，µmol/L 自动换算沿用）、hyperglycemia=bl_glu≥126、hba1c_elevated=bl_hbalc≥6.5、dyslipidemia=bl_cho≥240|bl_tg≥200|bl_hdl<40|bl_ldl≥160、crp_elevated=bl_crp>3、bmi_high=qi002/(qi003/100)²≥25、current_smoking=da059&da061、alcohol_intake=da067；
2. **结局**：cataract_any=da035==1、glaucoma_selfreport=da037==1（自报，与 2011 层同源局限）；
3. **样本**：age≥45（ba002_1 出生年推算，回退 ba004）、INDV_weight>0；模型=age/age²/sex 主模型+INDV_weight 加权 GLM（CHARLS 无 PSU→§6 降级路径，点估计+声明）；检验门槛与三态判定（BHY q、方向）与主管道一致；
4. **系统评估**：G0/G2 在 2015 层 judgeable（cohort 集）上的 P/R/F1；与 2011 层并呈（2011=feasibility 0 信息对；2015 若产生信息性对即构成 CHARLS 层首个真实验证信号）；
5. **判读纪律**：新层结果无论方向如实报告；contradicted 出现 ≥2 条 A 级对则触发 §4 方向审计；该层不得反哺任何系统组件（与三库/文献层同样的只评不调约束）。

**产出**：outputs/confirmatory/charls2015_confirmatory.csv + charls2015_metrics.json + G0/G2 指标并入 fused 系列汇总。

**运行记录（2026-10-15）——2015 层仍为 feasibility 层级（0 信息性对），0 反证**：
- **实现修正（数据事实驱动，非结果驱动）**：2015 波原始 da035/da037 被问卷跳转逻辑切碎（da035 缺失 97.6%，仅 8 阳性），改用 CHARLS 官方清洗变量 zda035/zda037（白内障 275 阳/16,317 阴；青光眼 247 阳）；2015 Biomarker 无体重项（qi002 为身高），bmi_high 不可构造——2011 层亦未测 BMI，两 CHARLS 层保持一致（7 个暴露 flag）。
- **结果**：frame n=19,736；12 对 tested（cataract 6 + glaucoma 6），**全部 uninformative、0 contradicted**；rule pairs 3（负控 r01 单列剔除后；coverage 0.273），负控如预期 uninformative。系统 G0=4FP、G2=3FP、0TP（precision 无定义）。
- **关键临界对**：hba1c_elevated×cataract_any **OR=1.71 [1.21, 2.43]，p=0.0026，BHY q=0.0956**——方向与 r02 声明一致、效应量与 NHANES 同层（1.80）一致，因 12 对多重检验惩罚未达 0.05；论文可如实描述为"CHARLS 2015 层接近但未达显著的同向信号"。
- **根本限制确认**：自报白内障患病率 1.7%（275/16,592）——问卷自报漏报使 CHARLS 两波均无法产生足量阳性；**数据侧扩容至此穷尽**（NHANES 2011-2018 本地不可用、KNHANES 10 波已全用、CHARLS 2015 已入册），进一步提升只剩预注册 v1.3+全新盲测路径。

---

## 17. 效能分析（R11 预注册补充，2026-10-15 落盘）

> 动机：三态体系里 `uninformative` 同时容纳了"确实无关联"和"样本不足看不出"两类完全不同的
> 情形。只报 `contradicted=0` 而不报效能，等于把"没测出来"当成"测过了没问题"。
> 本节先于任何效能结果落盘。

**方法**：对每个已检验配对，用观测到的 n、暴露数、事件数计算**80% 效能、双侧 α=0.05 下的
最小可检出 OR（MDE-OR）**。p0（未暴露者事件概率）由边缘风险精确求解（单调，二分法），
不使用近似。
**设计效应不假设，而是逐对从数据导出**：`DEFF = (survey CI 宽度 / 模型 CI 宽度)²`，
有效样本量 `n_eff = n / DEFF`。
**判读**：MDE-OR ≤ 2.0 记为 `powered_null`（"排除 2 倍关联"是有信息量的阴性）；
否则记为 `underpowered_null`。`separation` 与 `not_assessable` 单列，不与前两者混同。

**预注册阈值**：效能目标 80%；临床关注效应 1.5×（主）与 2.0×（次）；严重效能不足界 3.0×。

**产出**：`outputs/confirmatory/power_analysis_<dataset>.csv` + `power_summary.json`。

## 18. 中介分析与连续暴露剂量反应矩阵（R11 预注册补充，2026-10-15 落盘）

**18.1 中介分析**（先于结果落盘）：针对血糖→视力损害这一跨库一致信号，估计经糖尿病
视网膜病变（DR）与白内障的中介比例。二元 X、二元 M、二元 Y；系数乘积法（a 路径 × b 路径，
log-OR 尺度）+ delta 法标准误；比例中介用差值法。
**稳定性筛查（预注册，用于防止退化模型被当作结论）**：事件数<80、或中介阳性<80、
或总效应 CI 跨度>6 倍、或比例中介落在 [−0.5, 0.9] 之外 → 标 `UNSTABLE` 并排除出结论。
产出：`outputs/confirmatory/mediation_analysis.csv` + `mediation_summary.json`。

**18.2 连续暴露剂量反应矩阵**：把二分暴露换成**按 1 个标准差标准化**的连续测量，
在同一 survey 设计、同一协变量、同一双家族 FDR 下重跑全矩阵，系数即 **OR per SD**。
目的是回答二分法是否人为制造了无效结果。
**恒等式配对必须剔除**：结局 flag 由该测量本身定义时（如 `glaucoma_iop_elevated` 就是
"眼压超阈值"，用连续眼压回归它得 OR=inf），拟合是恒等式而非关联，不得进入矩阵。
产出：`outputs/confirmatory/dose_response_matrix.csv` + `dose_response_summary.json`。

**双家族 FDR 在此同样适用**（§7 更正 17a）：确证家族=规则相关配对，探索家族=全矩阵。

**运行结果（2026-10-15）**：
- 效能：中位 DEFF NHANES 1.07 / KNHANES 1.26；**中位 MDE-OR 1.337 / 1.159**；
  规则阴性中 `powered_null` 占 NHANES 10/13（76.9%）、KNHANES 7/11（63.6%）。
  **结论：R11 审计时"`contradicted=0` 无信息量"的判断被此结果否定** —— 阴性大多有效能。
- 中介：5 个稳定模型中比例中介为 −0.098 至 0.193（DR）、0.012（白内障）；
  2 个模型判 UNSTABLE 并排除。**血糖→视力损害大部分不经经典眼部并发症**。
- 连续矩阵：NHANES 134 对（16 显著）、KNHANES 180 对（38 显著）；
  规则相关对方向一致率 NHANES 19/24（79%）、KNHANES 9/10（90%）。
  **A 级规则 r13（BMI×白内障）在二分类下无效、连续测量下 KNHANES 显著
  （OR/SD=1.077, q=0.0014）** —— 该规则的二分无效部分是切点选择所致，论文须如实限定。
  吸烟规则的无效在客观生物标志物（血清可替宁）下依然成立，**故非测量误差所致**。

---

## 19. 跨国老龄化队列外部验证层（R12 预注册，2026-10-15 落盘——先于任何队列层确认运行）

### 19.1 定位与与前序层的关系

R11 的性能瓶颈诊断（\outputs/confirmatory/performance_bottleneck_diagnosis.json\）证明：
在既有 NHANES/KNHANES 数据上**不存在无偏调参集**——验证金标准是唯一能指出
“哪几条规则有效”的信息源，用它调参即测试集拟合。
本层因此不追求提升既有指标，而是回答一个**独立的问题**：

> 文献衍生的暴露组规则，能否在**未参与规则构建的、不同国家与不同问卷工具的**人群中复现？

本层是**时间外/跨国外部验证层**，与 R11 的三态协议同构但**分层独立**：
规则集、切点、模型与判定阈值在**本节落盘时冻结**；本层结果**不得**用于回头修改
21 条规则或 R11 的主结果。

### 19.2 数据来源与排除（纪律）

**仅用原始文件**。明确排除：
- Gateway to Global Aging 官方 Harmonized 文件（\H_*.dta\、\h_*_g*.dta\）
- 既往项目的中间产物（\Working_data/\、\Temp_data/\、\*_CN.dta\）
- 第三方派生发布版：**easySHARE**（C55）
- RAND HRS Fat File（C43）

**例外并声明**：SHARE 的 \gv_*\ 与 MHAS 的 \Constructed Data/_Creadas\、
\Imputations of Weight & Height\ 是**数据提供方自己发布的官方派生文件**，
不是第三方 harmonize，因此使用；其插补/质量标志（SHARE \_f\）用于
**限定实测值做主分析**。

### 19.3 队列与波次（已建成并过参考率门）

| 队列 | 行数(person-wave) | 人数 | 波次 | 参考率门 |
|---|---|---|---|---|
| SHARE | 1,693,515 | 137,183 | 4/5/6/7/9 | 9/9 PASS |
| HRS | 42,946 | 27,261 | 2010/2016 | 5/5 PASS |
| KLoSA | 40,406 | 11,137 | 1/2/4/6/8 | 6/6 PASS |
| LASI | 73,408 | 73,408 | 1 | 5/5 PASS |
| MHAS | 78,537 | 15,199 | 1/3/4/5/6 | 2/2 PASS |
| CLHLS | 72,744 | 9,093 | 1998–2018(8) | 7/7\* |
| ELSA | 9,771 | 9,771 | 3 | 4/4 PASS |
| CRELES | 5,191 | 2,827 | 1/2 | 4/4 PASS |

\* CLHLS 的 \ision_impairment_severe\ 超出 HARD 上限（25.7%），已判定为
**HARD 带未按年龄分层**所致（该队列均龄 **92.0 岁**）而非映射错误。
**处置：该 flag 在 CLHLS 仅作次要分析，主要分析排除**（见 19.8 局限 1）。

### 19.4 变量操作化的构念纪律（不可协商）

1. **白内障手术 ≠ 白内障患病**（C21/C29）。
   HRS \KC098/PC098\、KLoSA \C078\、CRELES \c58\ 只产出
   \cataract_surgery\，**不得**代入 \cataract_any\ 的规则检验。
   同理 KLoSA \C080\ = 青光眼**治疗** → \glaucoma_treated\。
2. **自报 ≠ 测量**。CLHLS 的 \hypertension\/\diabetes\ 是“医生是否告知”
   （实测 15.06% / 1.36%），低于以测量为主的 NHANES/KNHANES 参考带。
   这是**口径差异而非错误**（C64），分析中作为协变量/暴露时须声明。
3. **矫正后视力**。HRS \KC095/096/097\、MHAS \C45\、KLoSA \C075\、
   SHARE \eyesightr\、ELSA \heeye\ 的题面均限定“using glasses/corrective
   lenses as usual”（C27）→ 由此构造的 \ision_impairment_*\ 是
   **矫正后仍存在的损害**，**不是**未矫正屈光不正。论文必须显式声明。
4. **CLHLS \g1\ 的尺度逐波不同**（C65）：2000 波为 3 级（无“只能看见”类），
   其余为 4 级。已逐波分别映射；**2000 波不产出 \ision_impairment_moderate\**。
5. **CRELES 视力结局不可用**（C59）：\c55\/\c56\ 为未解码的 1–7 尺度，
   本地无任何可解码文档（harmonized 码本与 creation .do 均不含视力条目）。
   **按纪律不猜**，CRELES 只贡献自描述条项（\c54\ 的 \'Is blind'\）。

### 19.5 门槛审计（C54/C56，已执行且为前置条件）

C1 类错误（条件题当全样本题）在本项目**已发生五次**（NHANES \SMQ040\、
KNHANES \BS1_1\、CHARLS \da061\、SHARE \r002_\、\E_DR\ 语义错），
并经系统审计发现 **HRS / ELSA / MHAS / SHARE 四队列的“现吸”题均为条件问法**。
**全部二值暴露 flag 在进入 frame 前已过 \scripts/detect_exposure_gates.py\**，
命中者按下列规范构造：

`
flag = 1  若 现况 == Yes
flag = 0  若 门槛 == No  或  现况 == No
flag = NaN 仅当门槛缺失
`

已核验的构造实例：SHARE \current_smoking\（\r001_\ ∧ \r002_\）→ 17.15%；
HRS \current_smoking\（\PC116\/\PC117\）→ 全样本分母 14.6%。
**注意嵌套方向逐队列相反**：SHARE 先问“曾吸”再问“现吸”，HRS 相反。

### 19.6 可检验规则集（**实测**，非推测）

由 \scripts/cohort_rule_coverage.py\ 在已建成 frame 上实测
（两侧非缺失均 ≥ 200）：**6 / 21 条规则、合计 18 个（规则 × 队列）对**。

| 规则 | 可检验队列 | 对数 |
|---|---|---|
| r02 高血糖 × 白内障 | CLHLS, CRELES, LASI, SHARE | 4 |
| r10 吸烟 × 白内障 | CLHLS, CRELES, ELSA, SHARE | 4 |
| r11 吸烟 × AMD | ELSA | 1 |
| r12 饮酒 × 白内障 | CLHLS, SHARE | 2 |
| r13 BMI × 白内障 | CRELES, SHARE | 2 |
| r20 吸烟 × 视力损害 | CLHLS, ELSA, HRS, KLoSA, SHARE | 5 |

**15 条规则在本层不可检验**，原因分类（**明示，不作粉饰**）：

| 原因 | 规则 |
|---|---|
| 需眼底影像（视网膜/DR/DME） | r03, r04, r07, r19, r22 |
| 需眼压或视盘分级 | r16（\glaucoma_iop_elevated\/\glaucoma_suspect_cdr\） |
| 需地理编码暴露（PM2.5/UV） | r17, r21, r18 |
| 需血液指标（尿酸/CRP/维D/铅） | r01, r06, r07, r14 |
| 需膳食指数（未构建） | r08, r09, r19 |
| 需血脂 | r05 |

**本层的结论域因此严格限于**：白内障与视力的**吸烟/饮酒/BMI/高血糖**族。
**不得**由本层结果推断视网膜、AMD（ELSA 除外）、青光眼（需眼压）族的可迁移性。

### 19.7 主分析模型与判定

- **模型**：分层（按队列）logistic 回归，结局 = 对应 \*_any\/\ision_impairment_*\，
  暴露 = 对应 flag，协变量 = **age（连续或样条）+ sex**，队列内按波次固定效应。
- **方差**：SHARE 与 LASI 等带设计权重者用 survey 设计（strata/PSU/weights）；
  其余队列用聚类稳健方差（按个体聚类以处理重复波次）。
- **插补**：SHARE 的 \implicat\（1–5）**按副本分别拟合后以 Rubin 规则合并**；
  MHAS 的 BMI 用其官方 \mi_imp\（10 次插补均值）。
  **参考率门与描述性统计只用副本 1**（已实现）。
- **BMI 切点**（C58）：逐队列**主切点预先声明**——
  KLoSA/MHAS/LASI/CLHLS 用**亚洲切点 25**；SHARE/HRS/ELSA/CRELES 用**国际切点 30**。
  另一作为敏感性分析。依据是两层参考率门的实测判别
  （KLoSA：25 → 23.06% PASS / 30 → 1.45% FAIL；SHARE：25 → 63.83% FAIL / 30 → 22.81% PASS）。
- **三态判定**：沿用 R11 定义（\
eplicated\/\contradicted\/\uninformative\），
  基于 q 值与方向。
- **多重检验**：**双家族 BHY**，与本层“可检验规则集”一致：
  - **confirmatory 家族** = 19.6 表中 18 个（规则 × 队列）对
  - **exploratory 家族** = 各队列内所有“暴露 flag × 结局 flag”对
- **可迁移性判据**（预先声明）：某规则在 ≥2 个队列中同向且 q < 0.05 记
  \	ransportable\；仅 1 个队列记 \single_cohort\；全部方向相反记 \
on_transportable\。

### 19.8 已知局限（预先声明，不得事后淡化）

1. **CLHLS 重度视力**：实测 25.7%、均龄 92.0，超出未分层的 HARD 带。
   该 flag 在 CLHLS **仅作次要分析**；主要分析排除，并在论文中说明
   年龄分层参考率的缺失。
2. **CRELES 视力不可用**（C59）；其贡献限于白内障/青光眼/慢病与暴露。
3. **ELSA 单波**（wave 3），不能做纵向；且为本层唯一的 AMD 来源（r11）。
4. **视网膜/DR/DME 族全部不可检验** —— 8 个队列均无眼底影像。
5. **自报结局**：白内障/青光眼均为自报医生诊断，存在报告偏倚与医疗可及性混杂；
   与 NHANES 2005–2008 的**检查确诊**（OPXRET）不可直接比较，跨层比较须声明。
6. **CLHLS 无身高**，BMI 不可构造；**SHARE/KLoSA/MHAS 的 BMI 为插补产物**。
7. **饮酒仅在部分队列可得**（CLHLS 基线单波、SHARE）；KLoSA 的 \w01alc\
   因**无值标签**未使用（不猜），如需启用须先取得 KLoSA 变量说明文档。

### 19.9 协议偏离政策

本节落盘后：
- 新增队列或波次 → 记入 §0 偏离记录，并**单列报告**，不并入主要结果
- 修改切点、协变量或判定阈值 → 必须记为偏离并同时报告原方案结果
- 本层结果**不得**用于回溯修改 21 条规则或 R11 主结果
- 任何“因某队列结果不理想而排除该队列”的操作 → **禁止**；
  排除只能基于**运行前**已声明的数据可得性理由（本节 19.6/19.8 已列出）

### 19.10 交付物

\outputs/cohorts/cohort_rule_results.csv\（逐规则×队列：OR、CI、q、三态、可迁移性判据）、
\outputs/cohorts/cohort_transportability.json\、
以及图（队列×规则的三态热图 + OR 森林图）交由 writer 管线渲染。

