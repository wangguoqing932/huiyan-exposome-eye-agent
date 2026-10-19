# R5 轮评审报告 — 临床流行病学与观察性研究方法学（写作前终审）

> 评审人角色：临床流行病学/观察性研究方法学专家（STROBE/TRIPOD、公共数据库分析、NHANES survey weights）
> 日期：2026-10-14 · 项目：慧眼 huiyan v1.2（21 规则冻结）· 评审对象：executor 全部确证产物 + 写作底稿
> 评审方式：只读核验。所有数字均直接从项目文件/代码复算，附文件与行号证据。
> 严重度：P0 = 科学性硬伤/阻塞投稿；P1 = 重大（审稿人大概率攻击）；P2 = 建议。

---

## 一、总结论

本项目的内部诚实度显著高于同类工作：协议偏离有日志（analysis_plan §0）、偏倚调查有专文、局限性有底稿、探索/确证产物分目录。**但以投稿标准衡量，当前确证层存在 3 个 P0 级问题**：(1) KNHANES 眼底结局把"未检查/不可分级"编码（8/9）当成"无病"阴性，占分析样本 12.6%，且全部外部复证证据建立在该结局上；(2) 指标函数硬编码 NHANES 的 judgeable 集合，导致 CHARLS/KNHANES 已交付的 coverage 等数字错误；(3) 预注册的 survey 设计方差标准（svyglm strata/PSU）未执行、未按声明的降级路径披露，三态标签的 p/q 全部来自忽略抽样设计的模型 SE。三者都可机械修复，且大概率不翻转标签方向，但**必须在 writer 阶段开始前修复重跑，否则论文里的关键数字是错的**。

在此之上，论文表述需要系统性降格：v1.2 规则集在同一批数据上的"确证 P=1.0"中，NHANES 7 条复证对有 5 条直接来自看到结果后新增/扩展的 flags，本质上不可作为确证证据；真正的确证信息只有 v1.1 原始规则（NHANES 1 条、KNHANES 1 条信息性对，均为"血糖标志×DR"同一构造）。建议把 NHANES 层改名为 **internal consistency check**、KNHANES 层为 **transportability check（方向级）**、CHARLS 层为 **feasibility check（无信息）**，全文避免"三层确证通过"的说法。

**对评审要点 9 问的简答**（详见对应条目）：

| # | 问题 | 简答 |
|---|---|---|
| 1 | test-set fitting 披露是否达标；P=1.0 能否叫确证 | 框架合格但论文级分解缺失；不能叫确证，5/7 复证对是构造的（P1-4） |
| 2 | survey weights 用没用；不加权的 2×2 是否成立 | 权重用于点估计（非 2×2 卡方，是加权 logistic），但方差完全忽略分层/PSU = P0-3 |
| 3 | 横断面因果限制；direction audit 定义 | 方向审计标准被静默放宽（P1-6）；"只计显著反向"本身可辩护但必须记录 |
| 4 | CHARLS 0/4 怎么解读 | precision 无定义 = 无信息，不是失败也不是通过（P1-10） |
| 5 | 偏倚调查 11% 均值法是否充分 | 不充分，"100% 年龄混杂解释"与其自身调整模型矛盾（P1-8） |
| 6 | 混杂处理与论文限定 | 确证层有 age/age²/sex（NHANES 更多但层间不一致，P1-7）；规则引擎本身无调整，须限定为"文献接地的筛查 flag"（P1-4/正文建议） |
| 7 | r01 是否合格负控 | 预期 null 来自课题组自己在重叠数据上的既往分析，循环；仅 1 条（P2-11/12） |
| 8 | 三库人群差异对复证判断的影响 | DR 效应量 8 倍差、白内障"手术 vs 诊断"构造错位，只能做方向级一致性（P1-9） |
| 9 | 伦理与数据使用声明 | scaffold 有 TODO 未填、范围与实际分析不符（P2-17） |

---

## 二、P0（阻塞投稿，writer 前必须修复）

### P0-1 KNHANES 眼底结局编码缺陷：8/9（未检查/不可分级）被计为"无病"，污染全部外部复证证据

**证据**：
- `scripts/evaluate_knhanes.py` L60-65：`bi()` 函数把候选列 `s.isin([1])` 为阳性、**其余所有非缺失值（含 8、9）一律为阴性 0**。
- 我在 `data/raw/knhanes_frames/knhanes_2008.csv` 实测：`E_DRP_R` 分布 {0: 3137, **8: 1185**, **9: 481**, 1: 43}；`E_AMD_ELY_R`/`E_AMD_LATE_R` 呈完全相同的 8/9 结构。`DH2_lt`（自报白内障）同批人为 NaN（1188 人）——即 E_* 列的 8/9 与 DH2 的 NaN 是同一批"未做眼科检查/不可分级"的人（1185 vs 1188），绝不是"无病"。
- 在复现分析样本（age≥40、权重>0、HE_glu/cov 完整，n=19,194）中：`E_DRP_R`=9 者 **2,415 人（12.6%）被计为 no-DR 阴性**；DR 患病率被稀释为 1.71%（可分级者中为 1.96%）。
- **缺失与暴露相关（非随机错分）**：高血糖患病率按 E_DRP_R 编码分层 = {0（真阴性）: 7.5%，1（DR 阳性）: 68.1%，**9（被当阴性）: 11.6%**}。
- 受影响对象包括**仅有的两条外部复证对**（hyperglycemia×retinopathy_any OR=24.2；hba1c_elevated×retinopathy_any OR=27.2，`knhanes_confirmatory.csv` 行 12/20）以及全部 amd_early/amd_late 对（含两条 contradicted 非规则对，行 13/29）。这些行的 n、n_pos、OR、p、q 全部建立在错误结局上。

**修法**：`bi()` 增加 `.isin([0,1])` 限定（8/9/其它→NaN 缺失）后重跑 KNHANES 确证；重跑后需同步更新 knhanes_confirmatory.csv、knhanes_metrics_v11.json、generalization_gap_v1.2.* 与 limitations.md 中引用的所有 KNHANES 数字。预判：两条复证对因 |log OR| 极大、p≈1e-70，标签方向大概率不变，但全部数值会变；论文方法节必须写明 8/9 的语义与处理。

### P0-2 指标函数硬编码 "nhanes" judgeable 集合：CHARLS/KNHANES 已交付的 coverage 等数字错误

**证据**：
- `scripts/evaluate.py` L384：`compute_metrics_v11()` 内部固定调用 `get_judgeable_b_items("nhanes")`——对任何数据集都套用 NHANES 的 judgeable 列（`data/seed/entities_b.csv` 中 `nhanes_judgeable`：glaucoma_selfreport=false、vision_impairment_moderate/severe=false 等）。
- `evaluate_charls.py` L118 直接调用该函数、无前置过滤 → CHARLS 的 glaucoma_selfreport 对（`cohort_judgeable=true`）被错误剔除。实测复算：CHARLS coverage 报 0.667=4/6；按注册表 cohort_judgeable 应为 **4/13=0.308**。`limitations.md` §3 与 `generalization_gap_v1.2_summary.json` 引用的 0.667 是错的。
- `evaluate_knhanes.py` L165-177 先按 "knhanes" 过滤、函数内再按 "nhanes" 过滤（双重交集）→ 5 条 glaucoma_selfreport 测试对被误删。复算：KNHANES coverage 报 0.263=10/38，按注册表 knhanes_judgeable 应为 **10/43=0.233**；uncovered_pairs 报 28，应含 glau_self 共 33（其中 5 条 uninformative）。gap 表的 coverage 对比继承此错。

**修法**：给 `compute_metrics_v11()` 加 dataset_key 参数并全链路传入；重跑 KNHANES/CHARLS 指标（precision_rule 不受影响，CHARLS 仍为 null；coverage/uncovered 计数更新）；limitations §3 数字同步。

### P0-3 预注册的方差估计标准未执行也未按降级路径披露：全部三态标签的 p/q 忽略复杂抽样设计

**证据**：
- analysis_plan §6（预注册）："NHANES：以 R survey 包 svyglm（strata=SDMVSTRA, psu=SDMVPSU, weights=WTMEC2YR）为**确证标准**；Python 归一化权重的 GLM 仅作开发近似并声明。" 全项目 grep 无任何 svyglm/R 脚本（无 .R 文件）；确证实际全部用 `sm.GLM(..., freq_weights=归一化权重)`（evaluate.py L315-317；evaluate_knhanes.py L141-143；evaluate_charls.py L98-100）。
- 设计变量在手而未用：KNHANES 帧含 `psu`、`kstrata` 列（实测 `knhanes_2008/2010/2017.csv` 均有），NHANES XPT 含 SDMVSTRA/SDMVPSU。
- §6 自己规定的降级路径（"headline 只报点估计+对权重不敏感的 bootstrap CI，并显著标注"）也未遵守：三态标签本质依赖 p/q，等于用忽略聚类/分层的模型 SE 决定 replicated/contradicted；`limitations.md` **通篇未提抽样设计**。
- 具体脆弱点：NHANES `current_smoking×cataract_any` 调整后 OR=0.698 [0.495, 0.983]、raw p=0.0396、q=0.80（nhanes_confirmatory.csv 行 72）——该对靠 FDR 才免于 contradicted，是设计效应最可能翻转标签的样本点之一；r02 hyper×cataract p=0.0135、q=0.29 同属边缘。大效应对（p≈1e-50）方向上稳健。

**修法**（二选一，推荐前者）：(a) 对全部 headline/边缘对用 R survey::svyglm（NHANES: SDMVSTRA/SDMVPSU/WTMEC4YR 或两周期合并权重；KNHANES: kstrata/psu/wt_itvex）重算 OR/CI/p，比较三态标签是否翻转，翻转处如实报告；(b) 若坚持现实现，必须在 §0 记录"确证未采用 §6 预注册方差标准"这一协议偏离，并在 limitations 增加专门段落（design-effect 未校正、SE 可能偏小、哪些标签对此敏感）。当前状态（既未执行又未披露）是审稿人一击即溃的点。

---

## 三、P1（重大，审稿人大概率攻击）

### P1-4 test-set fitting 的论文级披露不完整：必须给出 by-construction 分解，且 v1.2 NHANES 不能称"确证"

**证据**：
- NHANES v1.2 的 7 条复证对（nhanes_confirmatory.csv）逐条溯源：①hyper×retinopathy_any（r03，v1.2 新增 hyperglycemia flag）②hyper×dr_npdr（r04，v1.2 新增 flag）③hba1c×cataract_any（r02，v1.2 新增 flag）④bmi×retinopathy_any ⑤bmi×dr_npdr（r22，v1.2 新增规则）⑥hba1c×retinopathy_any ⑦hba1c×dr_npdr（v1.1 原始）。**5/7 来自看到 2026-10-11 确证结果后的规则修改**——这些对当时的 gold-positive 正是修改的依据，再在同一样本上"复证"为恒真式。⑥⑦又是同一构造（HbA1c×DR，嵌套结局）。
- 归档的 v1.1 三态指标（outputs/confirmatory/archive_v1.1/）：NHANES 8 对测试/1 复证/0 反证、KNHANES 7 对/1 复证、CHARLS 3 对/0——precision 均为平凡 1.0 或 null，且 CI 是退化 bootstrap **[1.0,1.0]**（CP 修正只应用到 v1.2，v1.1 归档未重算，1/1 的 CP CI 应为 [0.025,1.0]）。
- KNHANES 的 2 条复证对（hyper×retin、hba1c×retin）是**同一构造**（血糖×DR），暴露高度共线（DR 阳性者 68% 高血糖），等效信息量 ≈1 个构造。

**修法**：论文中 (a) 以 v1.1 原始规则集为主结果（信息量如实陈述：每库 1 个信息性构造，方向一致、零反证）；(b) v1.2 扩展单列表标注 exploratory，7/7 分解为"2 clean + 5 by construction"；(c) NHANES 层改名 internal consistency check（post-freeze），KNHANES 层称 external transportability check 且只声称方向级一致；(d) v1.1 归档 CI 重算为 CP；(e) 未来工作保留"全新盲测试对"承诺（limitations §1 已有，保留）。

### P1-5 headline CI 的独立对假设被嵌套结局与多 flag 规则破坏

**证据**：precision_rule 的 CP CI 把 rep/(rep+con) 当作独立伯努利对。但 NHANES 的 14 测试对中：retinopathy_any ⊃ dr_npdr（B 侧嵌套，evaluate.py L174 注释自认）、hyperglycemia 与 hba1c_elevated 高度共线、r22 一条规则贡献 2 对。7 条"信息性对"实际只来自 3 个构造（血糖×DR×4 对、HbA1c×白内障、BMI×DR×2 对）。KNHANES 2 对 = 1 个构造。规则 yaml 头注也写明 "pair-level metrics count each (A,B) pair independently"（configs/rules.yaml L11）——注册了这个选择，但其推断后果（有效样本量远小于对数、CI 偏窄）未披露。

**修法**：增加 rule-level / construct-level 汇总敏感性（如按规则聚合：NHANES 有信息性证据的规则 r03/r04/r02/r22 → 4/4；按构造 3/3），在该层级给 CP CI；正文所有 "7/14""2/10" 表述旁注明"对间非独立（嵌套结局+共线暴露）"。

### P1-6 方向审计标准被静默放宽（未记入偏离日志），且 bias 文档承诺的第四态未实现

**证据**：
- analysis_plan §4（v1.1/v1.2 文本未改）："若 ≥2 个 A 级对在同库呈反向（**OR<1**），该库标签进入 quarantine"。`evaluate.py` L346-355 实现为 `(or<1) & (q<0.05)`（显著反向才计数）。NHANES 实际数据：r10 OR=0.698（q=0.80）、r13 OR=0.986（q=1.0）——按预注册文本触发隔离、headline 被压制；按代码不触发、headline 如常产出。**这是决定 headline 能否产出的标准，改了却没进 §0 偏离日志。**
- `bias_investigation_smoking_cataract.md` §4.4 提出的第四态 `cross_sectional_limitation` 未实现（`three_state()` 只有三态，吸烟×白内障在 CSV 中标 uninformative）；limitations.md §4 却写"方向审计（C4）已将该类信号隔离"——文档与实现不一致。

**修法**：把"审计标准从 OR<1 收紧为显著反向（q<0.05），依据偏倚调查结论"作为一条协议修订记入 §0（含日期与理由）；论文时间线如实呈现"隔离触发→调查→依据调查结论解除"的过程（这其实是加分项，比静默通过更有说服力）；limitations/正文措辞与实现对齐（不要说"已隔离"，说"经偏倚调查归因后按 uninformative 处理并单列"）。

### P1-7 协变量集跨层不一致且与预注册主模型不符

**证据**：plan §5 主模型 = age、age²/100、sex。实际：NHANES 用 age+age²+sex+**race+PIR+education**（evaluate.py L271-273、L313，即敏感性规格当了主模型）；KNHANES/CHARLS 仅 age+age²+sex（evaluate_knhanes.py L107-111、evaluate_charls.py L68）。plan §5 明言"层间比较只用主模型口径"——现状使 NHANES 1.80（hba1c×白内障，6 协变量）与 KNHANES 1.13（3 协变量）不可直接比较，§6 的泛化差距对比因此口径不齐。此偏离未在任何地方披露。

**修法**：以 age/age²/sex 重跑 NHANES 作为层间可比口径的 headline（现有 6 协变量版本降为敏感性，正好与 §5 的"敏感性单列附录"对应），或在 §0 记录偏离并放弃跨层效应量对比（只比方向）。

### P1-8 偏倚调查"100% 由年龄混杂解释"的结论过强，与其自身调整模型矛盾

**证据**：
- `bias_investigation_smoking_cataract.md` §2.2 仅用 **60-69 岁单一年龄层**的三组患病率目测（11.0/11.3/11.1%）即断言"crude 差异 100% 由年龄混杂解释"，无任何检验统计量、无其它年龄层、无标化。
- 而管线自身含 age+age²+sex+race+PIR+education 的模型给出 **OR=0.698 [0.495, 0.983]，raw p=0.0396**（nhanes_confirmatory.csv 行 72）——调整后仍有名义显著的"保护"信号，只是被 BHY q=0.80 救回 uninformative。这与"100% 年龄混杂"直接矛盾；残余信号更符合调查文档自己列的反向因果+存活偏倚机制。
- 两套分析样本不同（调查文档 n=7,072；管线 n=3,362 完整案例），未解释差异来源（协变量缺失的完整案例限制本身可能引入选择偏倚）。

**修法**：结论改为"年龄调整后关联大幅衰减且 FDR 后不显著；残余 OR≈0.70 与反向因果及存活者偏倚一致，横断面设计无法进一步区分"；补充逐年龄段（40-49/50-59/60-69/70+）分层 OR 或年龄标化 OR 一张小表；规则保留的依据只引文献（MR/A 级），不引横断面数据；把调整后 OR 如实写进论文（这是诚实性的展示点，不是弱点）。

### P1-9 三库结局构造不对齐，"复证"只能是方向级的

**证据**：
- DR 效应量 8 倍差：KNHANES hyper×retin OR=24.2 / hba1c×retin OR=27.2 vs NHANES 3.30 / 6.07。KNHANES 的 DR 几乎是糖尿病的标志物（DR 阳性者 68% 高血糖），且右眼单侧（`bi()` 只取第一个存在的列 E_DRP_R）；NHANES retinopathy_any=OPDURL4∈{2,3,4}（患病 12.4%，含轻度），dr_pdr=code 4。两库"retinopathy_any"不是一个构念。
- 白内障：NHANES cataract_any=VIQ071（**白内障手术史**，1=631/5,931，2007-2008 实测）vs KNHANES DH2_lt / CHARLS da035（**医生诊断自报**）——手术史受医疗可及性影响，诊断自报受知晓率影响，方向性偏倚不同。
- KNHANES amd_early 出现两条 contradicted 非规则对（hyper OR=0.59 q=0.013；dys OR=0.73 q=0.003）——横断面上高血糖"保护"早期 AMD，构造/存活问题同源，应在附录讨论。

**修法**：论文 Methods 加一张"结局构造映射表"（每库每结局：变量、编码、检出方式、单/双眼、患病率）；复证结论措辞统一为"方向一致（directionally concordant）"，明确排除效应量级可比性；讨论 OR 差异的构念来源（检出偏倚、严重度谱系、右眼单侧）。

### P1-10 CHARLS 层的解读与定位：0/4 是"无信息"，不是验证失败或成功

**证据**：charls_confirmatory.csv 全部 14 对均 uninformative（4 条主规则对：r02×2、r10、r12）；charls_metrics_v11.json：precision_rule=null（0 信息性对）、coverage 0.667（P0-2 修正后为 0.308）。自报白内障患病率仅 222/11,308=2.0%（45+ 人群显著低报）。CHARLS 2011 基线 biomarker 与自报结局同期测量 = 横断面，analysis_plan/data_sources 称 "Cohort layer" 具有误导性。gap 表只含 NHANES-KNHANES（35 共同对），未说明 CHARLS 缺席原因。

**修法**：论文将 CHARLS 层定位为 feasibility/measurement 层（自报结局+低事件数 → 无法产生信息性标签）；明确写"CHARLS 既不支持也不反驳规则集（precision 无定义）"；gap 表可补 CHARLS 列（限定 cataract_any 共同对）或在正文说明纳入标准（≥1 信息性对）。

---

## 四、P2（建议）

- **P2-11 负控 r01 的独立性**：rule_rationale.md r01 行自述预期 null 来自课题组既往双队列分析（CHARLS 2011 n≈11,473 —— 与本次 CHARLS 样本 n=11,308 同一波同一数据；NHANES 1999-2008 与本次 2005-2008 重叠）。负控的期望值来自被验证数据本身 → 只能证明"管线能复现已知 null"，不能作为假阳性率的独立标定。论文按此前者措辞；KNHANES 层 r01 未测（n=0），如实写。
- **P2-12 r01 规则文本自相矛盾**：作为阴性对照，rules.yaml L31-32 仍保留 NLRP3 机制 rationale 与临床 recommendation（"高尿酸血症人群建议评估晶状体状态…"）——引擎会对一个课题组自己认定 null 的对向用户输出风险建议。产品层面应让负控规则不产生面向用户的建议，或在论文注明该对仅为管线测试用途。
- **P2-13 FDR 敏感性**：NHANES headline 依赖 BHY 救回 smoking×cataract（raw p=0.0396 → q=0.80）。按 raw α 判定 precision=6/7=0.857 而非 1.0。建议单列该敏感性（恰好也回应 P0-3 的设计效应担忧）。
- **P2-14 权重技术细节**：(a) 连续归一权重传入 `freq_weights`（statsmodels 语义应为频数）——Binomial scale=1 下 SE 与 var_weights 等价，无实害但实现不严谨，若换 scale 估计会出错；(b) 两周期 WTMEC2YR 直接池化，规范做法是 WTMEC4YR 或除 2（归一化后近似等价，需一句话声明）；(c) CHARLS `wt.clip(lower=1)`（evaluate_charls.py L98）任意截断，应说明或去除。
- **P2-15 未覆盖的反向对应浮出**：`uncovered_significant` 只计 replicated（evaluate.py L412）。NHANES 存在 3 条 uncovered contradicted（alcohol×retin、alcohol×npdr OR≈0.65 q≈0.002；hba1c×vi_severe OR=0.57 q=0.040）——饮酒×DR 与吸烟×白内障同属反向因果家族，hba1c×重度 VI 提示矫正视力/就医可及混杂。附录单列，反而是"透明度指标"的好素材。
- **P2-16 gap 表口径**：coverage 之比（0.269 vs 0.263）跨不同可测全集（NHANES 52 对 vs KNHANES 38/43 对），非同口径比较；concordant 28/35 中 26 对是 uninformative-uninformative 的"功效性一致"，信息性对间一致仅 2/2。建议：coverage 只在共同对集合上比，另加 OR 符号一致列与按信息状态分层的一致率。
- **P2-17 文档漂移**：rule_rationale.md 与 rules.yaml 不一致（证据级合计 A3/B15/C3 vs A3/B13/C5；r04 引文 10.3390/ijms26114992+10.1002/kjm2.70200 vs yaml 10.1167/iovs.17-22804；r05 行引的 10.1097/MD.0000000000041599 实为 r11 的吸烟-AMD meta）；data_sources.md 写 "Rules 20"；ETHICS.md 范围（NHANES 1999-2008、KNHANES 1998-2024、9 队列）与实际分析（2005-2008、2008-2021、仅 CHARLS）不符，且 IRB/PI 字段全为 TODO——投稿前数据使用声明（三库均为公开授权数据、无需个体知情同意的规范表述）需定稿。
- **P2-18 §8 纪律偏离**：计划要求"验证脚本必须从 cases.jsonl 读取"，实际 evaluate.py L235 载入 cases 后从未使用，直接内联重算原始 XPT/CSV；KNHANES/CHARLS 脚本根本不载入 cases。实害低（flag 派生代码同一套），但属注册纪律偏离，应在 §0 备案一句。
- **P2-19 规则级可测性表**：r20/r21（VI 规则）在 NHANES 与 KNHANES 的指标分母中均被 judgeable 排除（entities_b.csv：vi_moderate/severe 两库均 false）；r07/r08/r09/r16-r19 无测量代理（NHANES 确证 CSV 中无对应暴露，r08 抗氧化 n=0）。**9/21 条规则在任何库都没有确证证据**。论文须给 per-rule 可测性/证据矩阵，避免"21 条规则经三库验证"的误读。
- **P2-20 通过线措辞**：§10 预注册阈值 precision≥0.70/0.80 在点估计 1.0 下"通过"，但 CI 下限 0.59/0.16。不得写"met the pre-specified criterion"而不带 CI；建议改为"点估计超过预注册阈值，但 CI 宽、信息性对少，不作把握度声明"。

---

## 五、通过项（未发现需要修改的问题）

1. **三态金标准设计**（replicated/contradicted/uninformative + separation 单列，§2）：正确解决了 C1/C2 的"非显著≠反证"混标问题；uninformative 不计 FP 的口径自洽。
2. **协议偏离日志的存在与时间线**（§0）：事件、性质（test-set fitting）、处置（冻结、降级、双版本呈现、盲测试对计划）记录完整——这是多数同类论文缺失的，框架合格（论文级细化要求见 P1-4）。
3. **暴露切点预注册**：三库统一固定临床阈值（尿酸性别特异 6.8/5.7、血糖 126、HbA1c 6.5、BMI 25、CRP 3.0、铅 5.0），非样本分位数——合格。
4. **权重用于点估计**：三库均归一使用 MEC/检查/个体权重（未忽略权重、也未退化成 2×2 卡方）；问题只在方差层（P0-3）。
5. **年龄/age²/性别调整**在所有确证层存在（NHANES 超出主模型规格的问题见 P1-7，属口径而非缺失）。
6. **多重检验**：库内全族 BHY FDR、p/q 双列、α=0.05，执行与注册一致。
7. **负控在可测层的表现**：NHANES OR=1.04 q=1.0、CHARLS OR=1.21 q=1.0，均为预期 uninformative（其独立性问题见 P2-11，属解释降格而非结果错误）。
8. **Clopper-Pearson 更正**（§0.1-更正2）：小 n 下弃退化 bootstrap 改 CP，方法学正确且已留痕。
9. **方向审计的触发-调查机制**（先查编码/结局/选择偏倚/反向因果再解除）与偏倚归因方向（年龄混杂+反向因果+存活偏倚）在机制学上正确；作为"横断面公共数据库验证文献规则的方法学边界"的讨论点是真贡献（表述修正见 P1-6/P1-8）。
10. **exploratory/confirmatory 分目录**与 v1.1 归档保留：可审计性良好。
11. **limitations.md 底稿**整体与落盘数据一致且罕见地坦诚（需按本报告补：抽样设计、指标硬编码修正后的数字、by-construction 分解、构造映射表）。

---

## 六、修复优先级清单（供 writer 排期）

| 序 | 动作 | 对应 |
|---|---|---|
| 1 | KNHANES bi() 修 8/9→缺失，重跑确证+指标+gap 表 | P0-1 |
| 2 | compute_metrics_v11 去 "nhanes" 硬编码，重算 CHARLS/KNHANES 指标 | P0-2 |
| 3 | R survey svyglm 重算（或按 §0 备案+limitations 补披露+边缘对敏感性） | P0-3 |
| 4 | 论文指标改用 v1.1 为主 + v1.2 分解（2 clean/5 by-construction），层级改名 | P1-4 |
| 5 | 方向审计标准修订记入 §0；cross_sectional_limitation 措辞对齐实现 | P1-6 |
| 6 | NHANES 主模型口径重跑（age/age²/sex）或放弃跨层效应量比较 | P1-7 |
| 7 | 偏倚调查补分层/标化表、软化"100%"结论 | P1-8 |
| 8 | 结局构造映射表 + 方向级"复证"措辞 + rule-level 敏感性 | P1-5/9 |
| 9 | CHARLS 定位为 feasibility；P2 各项（负控措辞、FDR 敏感性、未覆盖反向对附录、文档同步、ETHICS 定稿） | P1-10、P2-11~20 |

*本报告为只读评审，未修改项目任何文件（本报告文件除外）。文中所有 CSV 行号、代码行号、数字均可在对应文件复核。*
