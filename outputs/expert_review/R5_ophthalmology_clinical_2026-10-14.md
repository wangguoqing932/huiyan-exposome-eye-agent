# R5 眼科临床专业评审（写作前最后一轮）· 2026-10-14

评审人：眼底病/糖尿病视网膜病变方向临床专家（兼眼科流行病学）
范围：configs/rules.yaml v1.2（21 条规则）、docs/rule_rationale.md、R4_FIXLOG_2026-10-14.txt 第 1 条、outputs/citation_verification_report.json、三层确证 CSV、docs/limitations.md、docs/analysis_plan.md、data/seed/entities_a.csv / entities_b.csv、scripts/evaluate.py / evaluate_knhanes.py / evaluate_charls.py、data/seed/evidence_chunks.jsonl（指南分级）。关键引文经 Crossref / Europe PMC / PMC 全文联网核实。只读评审，未修改任何项目文件。

---

## 一、总体结论

**不建议以当前状态直接进入论文写作。** 存在 1 个 P0 级数据硬伤（NHANES 视力损害分层把**屈光球镜度当 logMAR 视力**使用，全部 VI 行数据无效）与 14 个 P1 级问题（引文-命题错配、暴露阈值与引文定义错配、注册表与实现矛盾、指南分级站不住等）。规则集本身的**方向声明绝大多数与主流眼科证据一致**（21 条中 19 条方向正确、保守可辩护），r22 的引文更换（R4 更正 1）经全文核实**恰当且数值准确**；但"规则声明"与"数据库操作化"之间、以及"文档声明"与"代码实现"之间存在多处会被专科审稿人一眼识破的错位。P0 必须修复并重跑；P1 必须在写作前逐条处置（改文字、补声明或预置 Discussion），否则大概率在第一轮外审被攻击。

逐条统计：**P0 × 1，P1 × 14，P2 × 10**。

---

## 二、P0（科学性硬伤 / 阻塞投稿）

### P0-1 NHANES 视力损害（VI）分层使用了屈光球镜度数变量，全部 VI 结果数据无效

**证据**：
- `scripts/evaluate.py` L161：`va = q("VIXPRS").where(q("VIXPRS") < 50).where(q("VIXPRS") > -5)`；L163-165 按注释声称的 logMAR 阈值分层（severe >1.00、modate 0.48–1.00、mild 0.30–0.48），注释称 "presenting VA, right eye"（L73）。
- 本地实测（E:\BaiduNetdiskDownload\所有数据库\16.NHANES\2005-2006\VIX_D.XPT 与 2007-2008\VIX_E.XPT，本次评审只读验证）：VIXPRS 取值呈 **0.25 步进的屈光球镜度分布**——大量负值（-0.5 至 -3.0 为主，另有 -14.25 等极端值）与特殊码 88；2005-06 周期 n=1992 中 >1.00 者 394、(0.48,1.00] 者 168、**(0.30,0.48] 者 0**；2007-08 周期 n=2224 中为 519/201/**0**。负值占比过半（近视屈光），绝无可能是 logMAR 视力（正常人群 logMAR 集中在 0±0.3）。NHANES VIX 文件中真正的右眼呈现视力变量是 **VIDRVA**（"Right visual acuity, presenting"，logMAR，文件内已存在），代码未使用。
- 后果链完整印证：`outputs/confirmatory/nhanes_confirmatory.csv` 中所有暴露的 vision_impairment_mild 均 n_pos=0（球镜 0.25 步进在 (0.30,0.48] 区间无刻度值），VI_moderate（实为 +0.5~+1.0D 轻中度远视）n_pos=314/2435≈12.9%，VI_severe（实为 ≥+1.25D 中高度远视+部分特殊值）n_pos=665/2435≈**27.3%**——美国 40+ 人群重度视力障碍/盲的真实患病率 <1%，27% 在临床上不可能；且"重度多于中度"违反视力分布的单调性。NHANES 眼病结局中 cataract(14%)/早期 AMD(8.2%)/晚期 AMD(1.0%)/DR(12%)/PDR(0.5%) 患病率全部合理，唯独 VI 三层全部反常，指向该单一变量用错。

**影响面**：nhanes_confirmatory.csv 约 30 行（VI_mild/moderate/severe）数据无效；r20（吸烟×VI）、r21（PM2.5×VI）在 NHANES 的检验行无效；"KNHANES hba1c_elevated×VI_severe contradicted（OR 0.57）"等结论不可引用；generalization_gap_v1.2 中含 VI 行的共同对受污染。因 VI_moderate/severe 在 entities_b.csv 中被判 non-judgeable（L14-15），headline precision_rule 分母未含 VI 行——**headline 指标幸免**，但任何交付表/附表/图若含 NHANES VI 行即为硬伤。

**修法**：(1) 数据管线 bug 修复不属于规则修改（R4 已有"实现修复不动规则"先例）：VIXPRS → VIDRVA（右眼）并按 r20 引文（Han 2021 为**双眼**标准）取 min(VIDRVA, VIDLVA)（较好眼）或双眼同时判定，需在 analysis_plan §0.1 追加"更正 4"记录后重跑 NHANES 确证与下游四张交付表/泛化落差表；(2) 重跑后按新数据更新 r20/r21 相关行；(3) 若不重跑，则论文中 NHANES 一切 VI 行与 r20/r21 的 NHANES 结果必须整体删除并声明变量不可用（不推荐，KNHANES 侧 r20/r21 也另有问题，见 P1-9/P1-10）。

---

## 三、P1（审稿人大概率攻击的重大问题）

### P1-1 r22/r13 引文的暴露定义是"肥胖"（≥30 / 最高 vs 最低 BMI 组），而 bmi_high 阈值为 ≥25，复证结论受阈值稀释

**证据**：`scripts/evaluate.py` L60、L132：bmi_high = BMXBMI ≥ 25（超重+肥胖）。PMC6133614 全文核实（Zhu 2018, Medicine 97(32):e11807）：该 meta 为 13 项前瞻队列、DR **发病**（incidence）、暴露为各研究**最高 vs 最低 BMI 分类**（多数为 BMI>30 vs 正常），总体 RR=1.20 (1.01–1.43)、T2DM 亚组 1.40 (1.05–1.87)、I²=59.6%——与 R4_FIXLOG 第 1 条所写数值完全一致（引文更换本身**恰当**，见通过项）。r13 引文（PLoS ONE 2014 meta, PMID 24587127）同为肥胖 vs 正常体重的对比。**NHANES 复证中 r13（A 级）OR=0.986 uninformative（nhanes_confirmatory.csv L52）**，用 ≥25 合并超重稀释效应是最可能的原因之一；r22 在 NHANES OR=1.47 replicated 而在 KNHANES OR=1.06 uninformative（knhanes_confirmatory.csv L44），同样的阈值两库结论相反，审稿人会追问阈值来源。
**修法**：规则已冻结不动；论文方法节明示 bmi_high=≥25 为"超重或肥胖"的宽定义，与引文"肥胖"定义存在暴露错分（趋向稀释，即复证阳性结果偏保守）；Discussion 用 ≥25 vs ≥30 的差异解释 r13 NHANES 未复证；敏感性分析（≥30 切点重算两库）如可行则一并提供，否则明确列为局限。

### P1-2 hba1c_elevated/hyperglycemia 的切点（6.5%/126 mg/dL）是糖尿病诊断线，检验的是"糖尿病状态×DR"，与 r03/r04 的"血糖控制差"命题错位；KNHANES 全部 2 个复证对均为此类定义性关联

**证据**：`scripts/evaluate.py` L54-55、L121-123（hba1c≥6.5%、FG≥126 或 DIQ010=1）。r03 引文（Chatziralli 2017，血糖控制与变异综述）与 DCCT/UKPDS 传统讲的是**糖尿病人群内**的 HbA1c 剂量-反应，而 6.5% 切点下"暴露组≈糖尿病、非暴露组≈非糖尿病"，实际检验的是糖尿病状态效应。NHANES hba1c×retinopathy OR=6.07、KNHANES OR=27.2（knhanes_confirmatory.csv L12-13, L20）——DR 是糖尿病的定义性并发症，读片 DR 在非高血糖者中极罕见，此类 OR 部分是结构使然。**KNHANES precision_rule=2/2 的两个复证对全部是血糖×DR**（hyperglycemia×retinopathy 24.2、hba1c×retinopathy 27.2），作为"外部确证"的证据力接近重言（tautology）。NHANES 7 个复证对中 5 个是血糖类对。
**修法**：论文不得把 precision_rule 表述为"系统性能"而不加注释；按"教科书级对（血糖×DR）vs 非平凡对（BMI×DR 等）"分层呈现各库复证构成；方法节明示 hba1c_elevated 的 6.5% 切点含义（糖尿病水平而非控制不佳水平），并声明该切点下复证结论的外推边界。KNHANES 章节如实写明 2 复证均为血糖-DR 对、证据力有限。

### P1-3 r04 唯一引文是"线粒体单倍群修饰 HbA1c 效应"的基因-环境交互研究，与规则命题（HbA1c→PDR 主效应/机制）错配；rationale 文档声称的"二源已补"在 rules.yaml 中不存在

**证据**：`configs/rules.yaml` L66-81：r04 引文仅 10.1167/iovs.17-22804；Crossref 核实该文（IOVS 2017;58(14):6481, Vanderbilt 队列）标题即"Mitochondrial Haplogroups **Modify** the Effect of Diabetes Duration and HbA1c on PDR Risk"——单倍群是效应修饰因子，非 HbA1c→PDR 主效应或机制综述证据；而 yaml 的 rationale 文字声称"（机制综述；关联级二源待补）"自相矛盾（引文既非机制综述，也未"待补"成功）。`docs/rule_rationale.md` L13 写 r04 引文为 10.3390/ijms26114992 + 10.1002/kjm2.70200 且"二源已补"——与冻结的 yaml 不一致（文档过期或引文在裁定后被撤）。
**修法**：写作前核实 r04 的证据链实态；若确只有 IOVS 一条，论文中 r04 定位为"人群关联级单源证据的 C 级探索规则"，rationale 措辞改为"效应修饰研究亦报告 HbA1c 与 PDR 关联"；文档层将 rationale.md 与 yaml 对齐（见 P1-4）。不得在论文中引用 rationale.md 里那两条未出现在规则里的 DOI。

### P1-4 rule_rationale.md 与 rules.yaml v1.2 多处矛盾（证据级总数、r05 等级与引文、r12/r18 引文、r19 设计类型、r22 缺行），照抄进论文必出错误

**证据**（逐处）：
- rules.yaml L2 头注释"A3/B13/C5"；rule_rationale.md L3"A 3 / B 15 / C 3"。实测 yaml：A=r10/r11/r13，C=r01/r04/r05/r19/r22，B=13 → yaml 自洽，rationale.md 过期（未反映 r15 撤销、r22 新增、r05 B→C）。
- r05：yaml L88 evidence_level: C、引文 10.62347/QJPQ2923（case-control）；rationale.md L14 写 B 级、引文 10.1097/MD.0000000000041599。
- r12：yaml 引文仅 Ophthalmology 2007；rationale.md L21 另有 10.1111/ceo.13892 且标"二源已补"。
- r18：yaml 引文为 Epidemiology 2003 + OEM 2006（Saadat）；rationale.md L27 写 JAMA 2025 (10.1001/jama.2025.1597) + Epidemiology 2003。
- r19：rationale.md L28 设计类型标"横断面研究"；Europe PMC 核实 10.1016/j.jnha.2025.100694 为**前瞻队列**（标题即 prospective cohort study）。
- r22 在 rationale.md 表格中完全缺失；analysis_plan §0 处置 4 写 r22 降 C 的理由是"引文来自单库确证结果，非 meta 分析"，但 §0.1 更正 1 后 r22 引文已是 meta——降级理由陈述与新引文矛盾（真实理由应是测试集拟合+文献异质性）。
**修法**：以 rules.yaml（sha 5aee851d…）为唯一事实源重写 rule_rationale.md 的对应行；论文证据表直接从 yaml 生成，不手工转录；r22 降级理由改写为"探索性规则扩展（测试集拟合）+ 文献异质性（Zhou 2017 null）"。

### P1-5 r17 绑定 amd_early，但其 meta 引文报告的是"任何 AMD"（PM2.5 仅并入 4 项研究），与 r05 被裁定改绑 amd_late 的逻辑自相矛盾

**证据**：rules.yaml L242-255（r17 B 侧 amd_early）；Europe PMC 核实 BMC Ophthalmology 2024 meta（PMID 38684968）：汇总结局为 **AMD 总体**（未按早期/晚期分层），PM2.5 仅 4 项研究、OR=1.16 (1.11–1.21)，另含 NO2/O3。而 r05 曾因"现有证据不支持早期 AMD 特异性"（rules.yaml L91-92 rationale 原文）从 amd_early 改绑 amd_late——同一审核逻辑未施加于 r17。审稿人并排看两条规则的裁定理由即可发难。
**修法**：规则冻结不动；论文中 r17 的结局表述改为"AMD（含早期）"，并诚实说明 meta 证据为不分期 AMD、数据库侧以早期 AMD 判定是因为 NHANES/KNHANES 分期变量可得；或在局限性中写明"r17 的分期绑定宽于其引文证据"。

### P1-6 r05（血脂异常×晚期 AMD）文献层存在直接反证且未记录，处理与 r22 不对称

**证据**：r05 现引 IJCEP 2025 单中心 case-control（Yao，10.62347/QJPQ2923，C 级）；Europe PMC 核实 Babaker 2025 Medicine meta（PMID 39993131，即本项目 r11 的引文）明确报告**胆固醇与甘油三酯与 AMD 无显著关联**（与 BMI、脑血管病同列非显著项）。血脂×AMD 本身是争议区（AREDS/CATT 时代证据不一致）。r22 在 FIXLOG/analysis_plan 中完整记录了反方 meta（Zhou 2017, OR≈0.97，本次核实确认：27 项研究、肥胖 OR=0.97 [0.73–1.30]、超重 OR=0.89 [0.75–1.07]），r05 却没有任何异质性记录。
**修法**：论文 Discussion 对 r05 必须双引（case-control 阳性 vs meta null）并给出方向保留理由（新生血管性 AMD 的脂质氧化机制+病例对照对晚期表型的富集）；limitations 增补 r05 文献异质性条目，与 r22 同等透明。

### P1-7 r16（PM2.5×IOP/CDR）B 级唯一引文为动物/细胞机制研究，违背项目自己声明的"研究设计匹配门"

**证据**：rules.yaml L227-241；引文 10.1186/s12989-021-00403-4（Particle Fibre Toxicol 2021）标题即"PM2.5 triggers ocular hypertension and glaucoma through pyroptosis"——小鼠/细胞机制证据。rules.yaml 头注释 L8-9 声明"研究设计门：prevalence/surgery-mgmt/genetic-only 引文被拒，必须与规则命题类型匹配"；r16 是人群级关联命题（B 侧为客观 IOP/CDR 条目）却仅由机制证据支撑。rule_rationale.md L25 自认待办"补 PM2.5-青光眼流行病学"未补。人群证据客观存在（如 UK Biobank PM2.5×IOP/青光眼研究，Chua et al. IOVS 2020）。
**修法**：规则不动；论文正文为 r16 补引人群流行病学文献（正文引用不受规则引文冻结约束），并把 r16 在结果呈现中标注"机制引文支撑、人群证据由论文正文补充"；或将 r16 的确证缺席（KNHANES 无 PM2.5 行、NHANES 无 PM2.5 数据）合并进覆盖局限讨论。

### P1-8 r20/r21 的结局阶段与引文定义错配，且两条规则在三层库中从未被有效确证

**证据**：
- r20 引文 Han 2021（Sci Rep，PMID 33432008）Europe PMC 核实：VI 定义为**双眼 VA 差于 0.5（decimal）= 双眼 logMAR>0.3（约 20/40 水平）**，而 r20 绑定 vision_impairment_moderate（20/60+）+ severe（20/200+）——引文结局宽于规则绑定，规则绑定的"中/重度"未经引文直接支持。yaml L312 rationale 自己写"severity 映射按原文 VI 定义核对"（待办语气，未核对）。
- r21 引文 Yan 2024（BMC Public Health，PMID 39614249）核实：VI 为 **CHARLS 自报**（远/近视困难，DVI/NVI），非客观 VA 分层；PM2.5 HR=1.60 (1.56–1.65)/10µg/m³、NDVI HR=0.68/0.1——效应量之大在该领域罕见，提示残余混杂，作为 B 级规则依据偏弱。
- 确证侧：VI_moderate/severe 在 entities_b.csv（L14-15）三库全部 non-judgeable → r20/r21 的 (A,B) 对被 D5 过滤出三库 metrics 分母——**两条 B 级规则实际从未进入任何一层确证**；KNHANES 明细中 current_smoking×VI_moderate OR=0.32 uninformative（且该行实测的是自报 E_VS_DS，见 P1-10）。
**修法**：论文按"规则声明域 vs 确证域"明示 r20/r21 属"未确证规则"（与 type-1/2 gap 同类呈现）；r20 的 severity 表述对齐引文（双眼 20/40 标准，介于 mild-moderate）；r21 声明引文结局为自报 VI、效应量解释需谨慎。

### P1-9 注册表（entities_b.csv）与实现代码双向矛盾：KNHANES VI 源变量、dr_npdr/dr_pdr judgeable 标志、vi_mild 剔除声明

**证据**：
- entities_b.csv L14 vision_impairment_moderate 的 judged_in 写"KNHANES: E_Cr_1/E_Cl_1"（视力检查），而 evaluate_knhanes.py L72 实际用 `bi("E_VS_DS")  # any VI`——代码注释自认是"any VI"（自报视觉困难），却挂名 vision_impairment_moderate。同名 flag 在 KNHANES 实测语义与注册表声明、与 NHANES 定义（presenting VA 分层）三者互不相同。
- entities_b.csv L11-12 将 dr_npdr/dr_pdr 标 knhanes_judgeable=true（"E_DR_1..7 病灶级重建"），但 evaluate_knhanes.py 的 build_knhanes_outcomes 根本未构建 dr_npdr/dr_pdr（KNHANES csv 中亦无此二行）——judgeable=true 的条目无实现。
- analysis_plan §1 声明"B 侧剔除条目：vi_mild、glaucoma/amd_selfreport、optic_disc_abnormality"，但 entities_b.csv L13 vi_mild 的 nhanes_judgeable=**true**（计入 coverage 分母），未声明剔除的 vi_moderate/severe 反而 false——剔除声明与 judgeable 标志交叉错乱。
**修法**：以实现为准修正注册表三处（VI 的 KNHANES 源与语义、dr_npdr/dr_pdr 标 false 或补实现、vi_mild 标 false 对齐剔除声明）；论文方法节的"结局可判定矩阵"必须与代码一致，逐库列明每个 B 侧 flag 的实际源变量与语义。

### P1-10 同名暴露/结局 flag 跨库语义漂移（alcohol 三库三定义、cataract 治疗史 vs 诊断、hyperglycemia 是否并诊断、DR 判定眼别）

**证据**（全部来自 evaluate*.py）：
- alcohol_intake：NHANES=ALQ101==1（**ever** 饮酒者，L146-147）；KNHANES=BA2_2_1==1（每月>1 次，L50-52）；CHARLS=da067==1（过去一年，L56-57）。三库暴露窗完全不同，而 r12 引文（Ejdervik Lindblad 2007，Europe PMC 核实：current drinkers vs never RR=1.11 [1.02–1.21]，每 13g/日 RR=1.07，方向 risk_up **成立**）用的是当前饮酒。
- cataract_any：NHANES=VIQ071==1（自报诊断，L159，未并入白内障手术条目）；KNHANES=DH2_lt==1（**治疗史**，evaluate_knhanes.py L67；注册表写 DH2_lt/DH2_dg 但代码只用 lt）；CHARLS=da035==1（自报诊断，evaluate_charls.py L60-61，da036 手术变量已加载却未并入）。诊断口径 vs 治疗口径的患病率与错分方向不同。
- hyperglycemia：NHANES=FG≥126 **或 DIQ010==1**（含已治疗糖尿病，L121）；KNHANES/CHARLS 仅 FG≥126（evaluate_knhanes.py L36、evaluate_charls.py L48）——后两库把血糖已控的糖尿病患者错分为非暴露（稀释效应）。
- retinopathy_any：NHANES=OPDURL4 2-4 级（any DR，L171）；KNHANES=bi("E_DRP_R","E_DRP_L") 实现上只取第一个命中列 **E_DRP_R（仅右眼）**（evaluate_knhanes.py L69 + bi() 定义 L60-65），与 NHANES 的（较差眼汇总）分级口径不同，单眼 DR 病例漏检。
**修法**：论文方法节必须逐库给出每个 flag 的操作化对照表（变量名+切点+暴露窗/眼别），并把跨库定义差异写入 limitations；r12/r02/r03 等复证解释按各库定义差异讨论（如 CHARLS 0 复证与自报+暴露窗差异的关系）。

### P1-11 统计实现违反预注册：analysis_plan §6 规定 R survey svyglm（strata/PSU）为确证标准，实际为 Python GLM + 归一化连续权重作 freq_weights，无设计效应校正，且 limitations 未声明

**证据**：analysis_plan.md L88-91（"以 R survey 包 svyglm（strata=SDMVSTRA, psu=SDMVPSU）为确证标准；Python 归一化权重的 GLM 仅作开发近似并声明"）；evaluate.py L315-317、evaluate_knhanes.py L141-143、evaluate_charls.py L98-100 实际全部用 `freq_weights=归一化权重` 的 statsmodels GLM（无分层、无 PSU、非整数频数权重）。三份确证 CSV 的 CI/p/q 均由此产生。NHANES 复证中 r22 的 bmi×retinopathy q=0.0396（nhanes_confirmatory.csv L56）为临界值——设计效应校正（DEFF 通常 1.3–2）后 SE 增大，该对存在翻转为 uninformative 的现实风险，届时 NHANES precision 由 7/7 变 6/6（不影响点结论方向但影响"7 复证"的叙述）。limitations.md 无 survey/权重条目。
**修法**：按 §6 的降级路径补声明（"R survey 不可用，headline 为点估计+CP 精确 CI，SE 未校正分层/聚类，q 值偏小"），或投稿前用 R survey 重跑确证层核对 q 值稳健性（重点复核临界复证对 bmi×retinopathy）；论文中所有 CI 注明估计口径。

### P1-12 AAO PPP"34A 危险因素 / 125D 背景"的分级在专科审稿人眼里站不住；且规则层 24 条引文全部为 literature，"PPP 提供 Level A 证据"的设计声明与实态不符

**证据**：data/seed/evidence_chunks.jsonl 中 guideline 块 159 个（34A+125D，tags=guideline_XXX_riskfactor 赋 A）。抽检 A 级指南块：ev_ppp_DR_059 是 **GLOSSARY（词汇表）**、ev_ppp_AMD_032 是 **ICG 血管造影**段、ev_ppp_DR_018/019/021 是随访问程与 OCT 局限、ev_ppp_DR_050 是 DRCR 研究列表、ev_ppp_AMD_042 是 anti-VEGF 失访风险因素、ev_ppp_POAG_021/027/055 是病史复查与手术告知——按段落标题关键词粗分，大量非危险因素内容被标为"riskfactor/A"。另：rules.yaml 21 条规则 24 条引文 source_type 全为 literature（0 条指南），而 docs/data_sources.md L19 写"AAO PPP (POAG/AMD/DR) | **Level A evidence**"。
**修法**：论文不得声称"34 块 A 级指南危险因素证据"；如实表述为"PPP 指南全文入 KG 作为检索背景（按章节关键词粗分），规则证据级仅由研究设计匹配的文献引文决定"；如需展示指南分级，先人工复核 34 个 A 块或改称"指南章节块（未分级）"。

### P1-13 证据池块级 A–E 分级与规则级 A–C 分级同名不同义，且 max_* 补充池含主题漂移与噪声块

**证据**：evidence_chunks.jsonl 块级分布 A47/B125/C129/D125/E634。抽检 A 级块：ev_m005_0087（菲律宾糖尿病管理现状综述）linked_rules=r03 且标 A——与 r03 命题无关；ev_m005_0093（**住院医师白内障手术并发症**综述）tags=max_cataract_rf 标 A——属于项目自己声明要拒绝的 surgery-mgmt 类；ev_m005_0084（**臭氧**×AMD，Sci Total Environ）linked r17——污染物不同（O3≠PM2.5）。这些块经 LightRAG 进入检索上下文，可能被 LLM 层当作支持证据在报告中引用。
**修法**：论文方法节显式区分两套分级体系（"检索池块级 A–E（排序用途）"vs"规则证据级 A–C（设计匹配）"）；对 linked_rules 非空的 max_* 块做一次主题复核（O3→r17、菲律宾综述→r03 应解除关联）；报告中引用证据时标明 chunk 来源类型，防止指南/背景块被表述为规则依据。

### P1-14 用户端文案将横断面关联翻译为个体风险等级与干预指令；论文展示 demo 输出时必被攻击

**证据**：src/huiyan_agent/report.py L13-16：HIGH="高风险——建议**优先干预该暴露**并转诊眼科评估"、MEDIUM="中等风险——建议加强监测，并在眼科随访时一并评估"。规则的证据基础是文献关联+横断面确证，且 21 条中 5 条为 C 级探索规则；命中即输出"高风险/优先干预"是因果化、指令化表述（虽有 L25 免责声明缓解）。论文若含系统截图或示例输出（figure 计划中有报告示例），专科审稿人会对照 r22（C 级、文献异质、测试集拟合扩展）也能触发同档文案的落差发难。
**修法**：报告文案分层显示证据级（如"高风险（文献证据级 A）"vs"低风险（C 级探索性关联）"），"优先干预"仅限 A 级因果确立对（r10/r11）；论文展示的 demo 案例选择 A 级对（吸烟×AMD），并在图注声明文案分级逻辑。

### P1-15 临床覆盖缺口：高血压无规则（仅 patient_factor 升档）、糖尿病病程未建模、青光眼仅 1 条弱证据规则——DR 方向审稿人必问

**证据**：rules.yaml 21 条按 B 侧计数：白内障 8、DR 5、AMD 5、青光眼 1（r16，且为动物机制证据，P1-7）、VI 2。AAO PPP 指南块自身（evidence_chunks.jsonl）即含"diabetes mellitus is an important risk factor for POAG"（ev_ppp_POAG_017）、DR PPP 的血压管理内容（ev_ppp_DR_013）——即项目自己的证据池声明了这些关联，但规则集未覆盖。NHANES（BPX）/KNHANES/CHARLS 均可测血压，糖尿病病程在 NHANES（诊断年龄）可得。"高血压只作为 patient_factor 升档器"（rules.yaml L344-353）而非独立暴露，缺乏预注册的排除理由。糖尿病病程是 DR 最强预测因子之一（r04 自己的引文即 duration×HbA1c 交互），完全缺席。
**修法**：论文在暴露选择协议节明确"暴露入组标准"（可测性+文献证据等级+机制覆盖），把高血压×DR/青光眼、糖尿病病程列为"证据池内已知但未建规则的缺口"，并解释原因（如横断面库病程测量的回顾偏差）；这比让审稿人先发现要有利得多。

---

## 四、P2（改进建议）

### P2-1 r11（A 级）唯一引文为 Medicine 2025 meta，期刊层级与"最高证据级"不匹配
Babaker 2025（PMID 39993131）核实：吸烟 OR=1.86 (1.33–2.6)，方向正确，但该 meta 未按晚期 AMD 分层（r11 绑 amd_late），且 Medicine 期刊声誉一般。建议：论文正文为 r11 补引权威 meta（如 Buttenschøn 2018 BMJ / Ye 2015 等 AMD 危险因素 meta）作为正文引用（不违反规则冻结）；规则内引文不动。

### P2-2 BMI×DR 文献异质性（Zhou 2017 null vs Zhu 2018 positive）应进入论文正文而非仅 FIXLOG
Zhou 2017（PMID 28562529）核实：27 项研究，肥胖 OR=0.97 (0.73–1.30)、超重 OR=0.89 (0.75–1.07)、连续 BMI OR=0.99，结论"超重/肥胖与 DR 风险升高无关"。Zhu 2018 为 13 项前瞻队列（incidence）。两 meta 分歧主要在研究设计与结局类型（患病率 vs 发病）。r22 的 NHANES 复证（incidence 样本的横断面 OR 1.47）站在 Zhu 一侧。论文应双引并以"发病型前瞻证据支持、患病率型混合证据 null"解释 C 级保守定级——这反而是 Discussion 的亮点素材。

### P2-3 r07 绑定 dr_npdr 特异性过强、rationale 措辞"负相关"易误读
两个 meta（Luo 2017 Nutrients、Zhang 2017 CJO）报告的均是 any DR（部分含 PDR），不支持 NPDR 特异绑定；rationale 文字"呈 meta 分析级负相关"（rules.yaml L120）指维生素 D **水平**与 DR 负相关，但暴露 flag 是"缺乏"（risk_up），建议措辞改为"维生素 D 缺乏与 DR 风险升高相关（OR/RR 方向为正）"，避免"负相关"被误读为保护。

### P2-4 dr_pdr 的 NHANES 操作化实为"severe NPDR+PDR 合并级"
evaluate.py L173：dr_pdr=OPDURL4==4。NHANES 视网膜读片的 4 级为"severe NPDR/PDR"合并层，并非纯 PDR。论文结局描述按 NHANES codebook 原文写（"severe NPDR 或 PDR"），勿写"增生性 DR"单义。

### P2-5 r18 第二源证据偏弱、r14 的暴露代理局限可再强化
r18 第二源 Saadat 2006（OEM，职业日晒×GSTM1×老年性白内障，伊朗小样本基因交互病例对照）作为 B 级二源偏弱，可在正文补 Salisbury Eye Evaluation/Poli 等经典 UV-白内障证据。r14 的 rationale（rules.yaml L222）已诚实注明 NHANES 血铅≠骨铅终身蓄积，建议论文中进一步给出 NHANES OR=0.90 uninformative 与该局限的对应解释。

### P2-6 KNHANES 混周期无周期效应校正、IOP 混合不同周期设备
evaluate_knhanes.py L91-95：2008–2021 全周期 concat，无周期固定效应；IOP 侧混合 2008-12（E_Gr_p）与 2017-19（E_Pr_1）不同设备。建议敏感性分析按周期分层或加周期项；论文方法节注明。

### P2-7 CHARLS 白内障定义未并入手术史（da036 加载未用）
evaluate_charls.py L30 加载 da036（白内障手术）但 L60-61 仅用 da035（诊断）。做过手术而 da035 答"否/已治"者被漏。修改会违反冻结吗——这是结局操作化而非规则，可与 P0-1 修复一并作为"实现更正"处理，或在论文中声明该定义（自报诊断，不含单纯手术史）。

### P2-8 cases.jsonl 管线与 B2/B5/B8 声明不符
scripts/generate_cases.py 为未实现占位（运行即报"尚未实现"并 return 1）；evaluate.py L235 load_cases 后 cases 变量从未使用（分析矩阵为 E×B 全组合 inline 生成，cases.jsonl 为 2026-10-11 旧探索脚本产物）。论文方法节按实态描述（"以注册表全交叉对为分析单元"），不要写"按 cases.jsonl 评估"；或补齐 B2 管线。

### P2-9 patient_factor diabetes 升档与 hba1c_elevated/hyperglycemia 暴露重叠时双重放大
rules.yaml L333-343：diabetes 升档器的 matching a flags 含 hyperglycemia/hba1c_elevated——当规则暴露本身就是 6.5% 切点的"糖尿病状态"时（P1-2），升档机制将同一信号计两次（暴露 flag 命中 + 糖尿病因素升档）。论文示例计算中应展示该边界情形的处理（或声明升档仅在暴露为非血糖类时生效）。

### P2-10 r02 的 KNHANES/CHARLS 未复证应预置解释
r02（B 级）在 NHANES hba1c 侧 replicated（OR=1.80）但 KNHANES/CHARLS 全 uninformative（1.16/1.18/1.10/1.13）。白内障在两外库为治疗史/自报口径（P1-10），错分稀释是首要解释；建议 Discussion 预写该段，避免审稿人以"A→B 级规则零外部复证"发难（KNHANES 仅有的 2 复证均为血糖×DR 对，见 P1-2）。

---

## 五、通过项（明确无问题，不需修改）

1. **r22 引文更换（R4 更正 1）恰当且数值准确**：Zhu 2018 Medicine 97(32):e11807 经 PMC 全文核实——13 项前瞻队列、DR 发病、总体 RR=1.20 (1.01–1.43)、T2DM 亚组 1.40 (1.05–1.87)，与 FIXLOG/analysis_plan §0.1 所写完全一致；risk_up 方向匹配；维持 C/low 并在 FIXLOG 记录反方 meta，处置保守且透明。该引文为 Medicine 期刊，作为 C 级探索规则的支撑够格。
2. **r10（吸烟×白内障，A 级）**：eBioMedicine 2022 MR 综述核实确认报告吸烟 liability 与 senile cataract 因果关联；A 级定级与"MR 确认因果"的 rationale 表述一致；SMQ040∈{1,2} 的现在吸烟操作化正确。
3. **r13（BMI×白内障）方向与证据**：PLoS ONE 2014 前瞻队列 meta 主题匹配、方向正确（阈值问题见 P1-1，与证据本身无关）。
4. **r06（CRP×晚期 AMD）**：Surv Ophthalmology 2011 meta（Hong），主题与阶段（晚期）匹配，方向正确，B 级恰当。
5. **r07（维 D 缺乏×DR）方向**：两个独立 meta 支持 risk_up（绑定特异性问题见 P2-3）。
6. **r09（地中海饮食×晚期 AMD，risk_down）**：Ophthalmology 2019（incidence）+ AJCN 2015（progression）双队列，是 21 条规则中证据链最干净的一条；protective 信号处理（schemas.py protective 标志）正确。
7. **r12（酒精×白内障）方向核实通过**：Europe PMC 核实 Ophthalmology 2007（瑞典女性前瞻队列 34,713 人）：current drinkers vs never RR=1.11 (1.02–1.21)、每 13g/日 RR=1.07，risk_up 成立（此前曾有"适度饮酒保护"的疑虑，经查证排除）。
8. **r14（铅×白内障）**：JAMA 2004 骨铅队列主题匹配；rationale 主动披露血铅代理低估终身蓄积，处理诚实。
9. **r01 阴性对照设计**：NHANES uninformative（OR=1.04, q=1.0）如预期，且 rationale.md 记录了课题组双队列反证与"gold-negative 预期"，作为管线假阳性检验的负控设计合理。
10. **临床切点本身**：尿酸 6.8/5.7 mg/dL（性别特异高尿酸血症切点）、CRP>3 mg/L（AHA/CDC 临床升高切点）、血脂复合切点（TC≥240/TG≥200/HDL<40/LDL≥160，NCEP ATP III 式）、IOP>21 mmHg（人群+2SD 传统高眼压切点）、CDR≥0.70（青光眼可疑标准切点）——除 P1-1/P1-2 所述 hba1c/bmi 的命题错位外，其余切点在眼科流行病学上成立。
11. **NHANES AMD 读片操作化**：早期 AMD 8.2%、晚期 1.0%（40+），患病率符合美国人群流行病学；KNHANES AMD 分级（4.7%/0.4%）亦合理。
12. **金标准三态设计**（replicated/contradicted/uninformative）避免"非显著=反证"的经典错误；方向审计 quarantine 只计显著反转并强制偏倚调查（吸烟×白内障反向的 bias_investigation 文档完整）；BHY FDR、分离检测、underpowered 前置规则实现正确。
13. **limitations.md 的协议偏离记录**（测试集拟合、v1.1/v1.2 双版本呈现、recall=1.000 不得单独引述）诚实到位，是本项目方法学上的强项，论文应保留该透明度。
14. **recommendation 字段文案**（rules.yaml 各规则）：为筛查/随访建议级表述，无因果断言，与证据等级相称（区别于 report.py 的等级标签，见 P1-14）。
15. **r17/r05 之外的 PM2.5×VI（r21）方向**、**r20 方向**：文献方向本身（吸烟→VI、PM2.5→VI）与主流证据一致，问题仅在结局阶段绑定与引文定义（P1-8）。

---

## 六、处置优先级建议（给 writer 阶段的顺序）

1. 【P0-1】修复 VIXPRS→VIDRVA，按 §0.1 更正记录重跑 NHANES 及下游表（预计 headline 不变，VI 明细全变）。
2. 【P1-4】以 rules.yaml 为准重写 rule_rationale.md 冲突行，防止论文证据表转录错误。
3. 【P1-9/P1-10】出一张"flag×库操作化对照表"（变量、切点、暴露窗、眼别、判定方式），作为论文方法节主表之一，同时化解两批矛盾。
4. 【P1-2/P1-1】结果呈现按"教科书对 vs 非平凡对"分层；方法节明示 hba1c 6.5%/BMI 25 切点与引文定义的关系。
5. 【P1-5/P1-6/P1-7/P1-8】四条规则的引文-命题错配在 Discussion 预置答辩段（r17 分期、r05 反证、r16 人群证据补引、r20/r21 未确证声明）。
6. 【P1-11】补统计口径声明或 R survey 敏感性重跑（重点 bmi×retinopathy q=0.04 的稳健性）。
7. 【P1-12/P1-13】方法节重写指南使用与两套分级的表述。
8. 【P1-14】report.py 文案分级化（工程小改，不动规则）。
9. 【P1-15】暴露选择协议节预置高血压/病程缺口。
10. 【P2 各条】随写作顺带处理。

—— 评审完 —— 
（本文件为 R5 轮评审交付物；评审过程未修改项目任何文件，本地仅对 NHANES VIX 原始数据做了只读验证。）
