# Rule Rationale — 慧眼 huiyan v1.2（R5 评审后重写版，2026-10-14）

> **数据源声明**：本文件唯一事实源为 `configs/rules.yaml`（**v1.2，sha256 95ebf0a9…（2026-10-19 引用归一化后；此前的 5aee851d 为 2026-10-12 冻结版），规则语义自 2026-10-12 起冻结**）。凡本文件历史版本、analysis_plan、评审报告与 yaml 冲突之处，**一律以 yaml 为准**。每条规则的 flag、方向、证据等级、severity、引文 DOI 均自 yaml 原样转录；证据性质标注（设计类型、引文-命题错配、文献反证、确证状态）来自 R5 评审报告（outputs/expert_review/R5_ophthalmology_clinical_2026-10-14.md、R5_epidemiology_methods_2026-10-14.md）的联网核实结论。
> 旧版（2026-10-11）与本版的全部矛盾点见文末"与 v1.2 yaml 的差异审计"。

## 统计口径（自 yaml 逐条清点）

- **21 条规则 = A 3 / B 13 / C 5**（与 yaml 头注释一致；旧文档误写 A3/B15/C3）。
  - **A（3）**：r10、r11、r13
  - **B（13）**：r02、r03、r06、r07、r08、r09、r12、r14、r16、r17、r18、r20、r21
  - **C（5）**：r01、r04、r05、r19、r22
- severity 映射核验：A→high（r10/r11/r13 均 high）、B→medium（13 条均 medium）、C→low（5 条均 low），无例外。
- 方向：20 条 `risk_up`，1 条 `risk_down`（r09 地中海饮食，保护性）。
- `negative_control: true` 仅 r01 一条。
- 7 机制全覆盖（r15 已撤销，规则 ID 因此跳号）：oxidative_stress / glycation_metabolic / vascular_perfusion / inflammation_immune / endocrine_hormonal / heavy_metal_toxicity / photochemical_uv。
- 引文共 24 条，`source_type` **全部为 literature**（0 条指南）——论文不得声称"AAO PPP 为规则提供 Level A 证据"（R5 P1-12）。

## 通用纪律（转录自 yaml 头注释，2026-10-11 作者裁定）

1. risk_type 必须取自 7 机制清单；
2. 引文数量不是硬门，但每条命题须至少有一条**研究设计匹配**的来源（prevalence / surgery-mgmt / genetic-only 类引文被拒）；
3. 嵌套结局语义 = 方案二：允许多 flag 规则；报告取 max(severity)、最具体优先展示；指标层每个 (A,B) 对独立计分；
4. 拒识指标仅在类型 2 空白上评估（见"明示空白"节）。

## 逐条规则证据链

### r01 尿酸 × 白内障（`r01_uric_acid_x_cataract`）

- **yaml 事实**：`uric_acid_elevated` × `cataract_any`；机制 `inflammation_immune`；等级 **C**；severity **low**；方向 `risk_up`；**`negative_control: true`（21 条中唯一）**；引文 `10.1038/s41420-024-01900-z`。
- **证据与设计**：机制级（细胞实验）——尿酸驱动 NLRP3 炎症小体激活、诱发晶状体上皮细胞衰老（yaml rationale 原文）。无人群关联级引文，为 C 级理由之一。
- **阴性对照设计**：课题组既往双队列分析（CHARLS 2011 n≈11,473 + NHANES 1999-2008 n≈9,754）结论为"尿酸×白内障关联非独立（年龄混杂）"，r01 预期在数据库验证中为 gold-negative，保留为 C 级**管线假阳性检验用例**。
- **确证层**：NHANES OR=1.04、q=1.0；CHARLS OR=1.21、q=1.0——均如预期落入 uninformative。
- **如实标注（R5 流行病学 P2-11/P2-12）**：负控预期值来自课题组在**重叠数据**上的既往分析（CHARLS 同波次、NHANES 周期部分重叠），只能证明"管线能复现已知 null"，不构成假阳性率的独立标定；KNHANES 层未测（n=0）。规则文本仍含机制 rationale 与 recommendation——论文须注明该对仅为管线测试用途（负控），面向用户的建议输出属产品层待办，不改动冻结规则。

### r02 高血糖 × 白内障（`r02_hyperglycemia_x_cataract`）

- **yaml 事实**：A 侧 `hyperglycemia` + `hba1c_elevated` × `cataract_any`；机制 `glycation_metabolic`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1002/dmrr.3073`。
- **证据与设计**：系统综述（2 型糖尿病人群内白内障风险因素；山梨醇通路与糖基化）。
- **定义性分层（R5 P1-2，见"数据库复证的分层口径"节）**：`hba1c_elevated` 切点 6.5%、`hyperglycemia` 切点 FG≥126 mg/dL（NHANES 另并入已诊断糖尿病）均为**糖尿病诊断线**；切点下"暴露≈糖尿病状态"，此类复证属定义性/教科书级关联。
- **确证层**：NHANES hba1c 侧 OR=1.80 replicated；KNHANES/CHARLS 全部 uninformative（OR 1.10–1.18）。解释（R5 P1-10/P2-10）：两外库白内障为治疗史/自报口径（错分稀释），且 KNHANES/CHARLS 的 hyperglycemia 仅 FG≥126（血糖已控的糖尿病患者被错分为非暴露）。
- **第二源待办**：一般人群"糖尿病→白内障发病"meta。

### r03 HbA1c × 视网膜病变（`r03_hba1c_x_retinopathy_any`）

- **yaml 事实**：A 侧 `hba1c_elevated` + `hyperglycemia` × `retinopathy_any`；机制 `glycation_metabolic`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1007/s13300-017-0345-5`。
- **证据与设计**：叙述综述（血糖控制与血糖变异；Chatziralli 2017）。
- **命题错位如实标注（R5 P1-2）**：引文与 DCCT/UKPDS 传统讲的是**糖尿病人群内**的 HbA1c 剂量-反应（"控制质量"），而 6.5% 切点下数据库实际检验的是"糖尿病状态 × DR"——DR 是糖尿病的定义性并发症，读片 DR 在非高血糖者中极罕见，OR 部分为结构使然（NHANES hba1c×retinopathy OR=6.07；KNHANES 27.2，hyperglycemia×retinopathy 24.2）。**KNHANES 仅有的 2 个复证对全部属此类定义性关联**，作为"外部确证"证据力接近重言；论文须按"教科书级对 vs 非平凡对"分层呈现。
- **第二源待办**：DCCT/UKPDS 试验级证据。

### r04 HbA1c × 增生性/非增生性 DR（`r04_hba1c_x_dr_pdr`）

- **yaml 事实**：A 侧 `hba1c_elevated` + `hyperglycemia` × B 侧 `dr_pdr` + `dr_npdr`；机制 `vascular_perfusion`；等级 **C**；severity **low**；方向 `risk_up`；引文 `10.1167/iovs.17-22804`（**单源**）。
- **引文性质如实标注（R5 P1-3，联网核实）**：唯一引文（IOVS 2017, Vanderbilt 队列）标题即"Mitochondrial Haplogroups **Modify** the Effect of Diabetes Duration and HbA1c on PDR Risk"——为**人群基因-环境交互/线粒体单倍群效应修饰研究**，既非机制综述，也非 HbA1c→PDR 主效应的常规关联研究；单倍群是效应修饰因子。该研究在交互模型中亦报告 HbA1c 与 PDR 的关联，故可作关联级支撑，但仅此一源。
- **C 级理由（如实）**：证据**单源**、人群关联级、且引文命题与规则命题仅部分重叠（效应修饰背景下的 HbA1c 关联），不满足 B 级（综述/meta 或双源）标准。定位："人群关联级单源证据的 C 级探索规则"。
- **旧文档更正**：旧版写引文 `10.3390/ijms26114992` + `10.1002/kjm2.70200` 且"二源已补"——**两条 DOI 均不在冻结 yaml 中，论文禁止引用**；yaml rationale 字段内"机制综述"表述与引文实态不符，以本节核实结论为准（yaml 不可改）。
- **附注（R5 P2-2/P2-4）**：同受 P1-2 定义性错位影响；NHANES `dr_pdr` 操作化实为 OPDURL4==4（"severe NPDR 或 PDR"合并级），论文结局描述按 codebook 原文写。

### r05 血脂异常 × 晚期 AMD（`r05_dyslipidemia_x_amd_late`）

- **yaml 事实**：`dyslipidemia` × `amd_late`；机制 `oxidative_stress`；等级 **C**；severity **low**；方向 `risk_up`；引文 `10.62347/QJPQ2923`。
- **证据与设计**：单中心病例对照研究（IJCEP 2025，Yao）。yaml rationale 记录裁定过程：B 侧由 amd_early **改绑 amd_late**（"现有证据不支持早期 AMD 特异性"）并降为 C。
- **文献层反证记录（R5 P1-6，本次补记——与 r22 的异质性记录同等透明）**：Babaker 2025 Medicine meta（PMID 39993131；即本项目 r11 的引文 `10.1097/MD.0000000000041599`）明确报告**胆固醇与甘油三酯与 AMD 无显著关联**（与 BMI、脑血管病同列非显著项）。血脂×AMD 本身是争议区（AREDS/CATT 时代证据不一致）。
- **方向保留理由**：新生血管性（晚期）AMD 的脂质氧化/脉络膜新生血管机制 + 病例对照设计对晚期表型的富集。论文 Discussion 须**双引**（case-control 阳性 vs meta null），维持 C 级不提级。
- **旧文档更正**：旧版写 B 级、引文 `10.1097/MD.0000000000041599`——该 DOI 实为 r11 的吸烟-AMD meta（张冠李戴）；以 yaml 为准（C、10.62347/QJPQ2923）。

### r06 CRP × 晚期 AMD（`r06_crp_x_amd_late`）

- **yaml 事实**：`crp_elevated` × `amd_late`；机制 `inflammation_immune`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1016/j.survophthal.2010.08.007`。
- **证据与设计**：血清 CRP 与 AMD 的 meta 分析（Surv Ophthalmol 2011，Hong）——主题与分期（晚期）匹配、设计类型匹配（R5 通过项 4）。
- **第二源待办**：2011 年后新 meta。

### r07 维生素 D 缺乏 × NPDR（`r07_vitamind_x_dr_npdr`）

- **yaml 事实**：`vitamin_d_deficiency` × `dr_npdr`；机制 `endocrine_hormonal`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.3390/nu9030307` + `10.1016/j.jcjo.2017.09.026`（双源）。
- **证据与设计**：两个独立 meta（Luo 2017 Nutrients；Zhang 2017 CJO），方向一致支持 risk_up（R5 通过项 5）。
- **绑定特异性标注（R5 P2-3）**：两个 meta 报告的均是 **any DR**（部分含 PDR），不支持 NPDR 特异绑定；论文中该规则结局表述应对齐 any DR，或在局限中声明绑定宽于证据。yaml rationale 中"负相关"指维生素 D **水平**与 DR 呈负相关（暴露 flag 是"缺乏"，规则方向仍为 risk_up），勿误读为保护。
- **确证层**：三库无维生素 D 测量代理（NHANES 确证 CSV 无对应行，R5 P2-19）——未确证（not tested）。

### r08 抗氧化摄入不足 × 白内障（`r08_low_antioxidant_x_cataract`）

- **yaml 事实**：`low_antioxidant_intake` × `cataract_any`；机制 `oxidative_stress`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.3109/10715762.2013.777155`。
- **证据与设计**：叙述综述（维 C/维 E/类胡萝卜素摄入不足与晶体氧化损伤）。
- **确证层**：NHANES 抗氧化暴露 n=0（无测量代理，R5 P2-19）——未确证（not tested）。
- **第二源待办**：AREDS/类胡萝卜素 RCT 或 meta。

### r09 地中海饮食 × 晚期 AMD（`r09_mediterranean_diet_x_amd_late`）

- **yaml 事实**：`mediterranean_diet` × `amd_late`；机制 `oxidative_stress`；等级 **B**；severity **medium**；方向 **`risk_down`（21 条中唯一保护性方向）**；引文 `10.1016/j.ophtha.2018.08.006` + `10.3945/ajcn.115.111047`。
- **证据与设计**：双前瞻队列（Ophthalmology 队列=incidence；AJCN 2015=progression）——R5 通过项 6 评为"21 条规则中证据链最干净的一条"；protective 信号处理（schemas.py protective 标志）正确。
- **确证层**：三库无膳食依从性测量代理（P2-19）——未确证（not tested）。
- **旧文档更正**：旧版引文 DOI 误录为 `10.1016/j.ophtha.2018.09.032`，以 yaml 为准（…08.006）。

### r10 吸烟 × 白内障（`r10_smoking_x_cataract`）

- **yaml 事实**：`current_smoking` × `cataract_any`；机制 `oxidative_stress`；等级 **A**；severity **high**；方向 `risk_up`；引文 `10.1016/j.ebiom.2022.104154`。
- **证据与设计**：MR 系统综述（eBioMedicine 2022）确认吸烟→老年性白内障因果角色（R5 通过项 2）；SMQ040∈{1,2} 现在吸烟操作化正确。
- **方向审计与偏倚调查（结案记录）**：NHANES 调整后 **OR=0.698 [0.495, 0.983]**（raw p=0.0396、BHY q=0.80）——FDR 后为**非显著反向**，已按预注册触发偏倚调查并结案（`docs/bias_investigation_smoking_cataract.md`）：年龄混杂（现在吸烟者年轻）+ 反向因果（白内障确诊后戒烟，曾吸烟组患病率最高 19.7%）+ 存活偏倚（重度吸烟+白内障者早逝）。管线按 uninformative 处理，规则基于 A 级 MR 证据保留。
- **如实标注**：
  - **cross-sectional limitation**：受"疾病致戒烟/戒酒"影响的暴露在横断面库**原则上不可验证**，规则保留依据只引文献（MR/A 级），不引横断面数据；
  - R5 流行病学 P1-8：偏倚调查文档"crude 差异 100% 由年龄混杂解释"表述过强——多协变量调整后仍余名义显著 OR≈0.70（被 FDR 救回），与反向因果+存活偏倚一致；论文表述应为"年龄调整后关联大幅衰减且 FDR 后不显著"；
  - R5 P1-6：方向审计实现为"显著反向（q<0.05）才计数"（较预注册文本"OR<1"收紧），该标准修订依据即本偏倚调查，须记入协议偏离日志；
  - R5 P0-3：该对 q 值未校正抽样设计（strata/PSU），是设计效应可能翻转标签的样本点之一。

### r11 吸烟 × 晚期 AMD（`r11_smoking_x_amd_late`）

- **yaml 事实**：`current_smoking` × `amd_late`；机制 `oxidative_stress`；等级 **A**；severity **high**；方向 `risk_up`；引文 `10.1097/MD.0000000000041599`。
- **证据与设计**：AMD 风险因素 meta（Babaker 2025 Medicine，PMID 39993131；吸烟 OR=1.86 [1.33–2.6]，方向正确，R5 通过项）。
- **如实标注（R5 P2-1）**：该 meta **未按晚期 AMD 分层**（规则绑 amd_late 的分期特异性无引文直接支持），且 Medicine 期刊层级与"A 级"定级的匹配度一般。建议论文正文补引权威 meta（如 Buttenschøn 2018 BMJ 等 AMD 危险因素 meta）作正文引用——正文引用不受规则引文冻结约束，规则内引文不动。
- **关联事实**：此引文同时是 r05 文献层反证的来源（Babaker 2025 报告血脂项与 AMD null，见 r05 节）。

### r12 饮酒 × 白内障（`r12_alcohol_x_cataract`）

- **yaml 事实**：`alcohol_intake` × `cataract_any`；机制 `oxidative_stress`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1016/j.ophtha.2006.07.046`（**单引文**）。
- **证据与设计**：前瞻队列（Ophthalmology 2007，瑞典女性 34,713 人）：current drinkers vs never RR=1.11 [1.02–1.21]、每 13g/日 RR=1.07——risk_up 成立（R5 通过项 7，此前"适度饮酒保护"疑虑经查证排除）。
- **旧文档更正**：旧版另列 `10.1111/ceo.13892` 并标"二源已补"——不在 yaml 中，已移除。
- **跨库定义错位（R5 P1-10）**：`alcohol_intake` 三库三定义（NHANES=ever 饮酒；KNHANES=每月>1 次；CHARLS=过去一年），与引文"当前饮酒"口径不同；剂量-反应关系待验证库检验（yaml rationale 自述）。

### r13 BMI × 白内障（`r13_bmi_x_cataract`）

- **yaml 事实**：`bmi_high` × `cataract_any`；机制 `glycation_metabolic`；等级 **A**；severity **high**；方向 `risk_up`；引文 `10.1371/journal.pone.0089923`。
- **证据与设计**：前瞻队列 meta（PLoS ONE 2014，PMID 24587127）——主题匹配、方向正确（R5 通过项 3）。
- **切点错配声明（R5 P1-1）**：`bmi_high` 操作化 = BMXBMI **≥25**（超重+肥胖宽定义），引文暴露为**肥胖**（≥30 / 最高 vs 最低 BMI 组）——宽定义引入**向 null 的错分稀释**，即任何复证阳性结果偏保守；审稿人将追问阈值来源，论文方法节须明示该错配。
- **方向审计（结案记录）**：NHANES OR=0.986、q=1.0——**非显著反向**，偏倚调查认定实为 uninformative（非反向），隔离部分解除（bias_investigation §4.3）；规则基于 A 级 meta 保留，标注 cross-sectional limitation（同 r10：横断面口径+阈值稀释是未复现的最可能解释）。
- **待办**：≥30 切点敏感性分析（如可行），否则列为局限。

### r14 铅 × 白内障（`r14_lead_x_cataract`）

- **yaml 事实**：`lead_exposure` × `cataract_any`；机制 `heavy_metal_toxicity`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1001/jama.292.22.2750`。
- **证据与设计**：队列（JAMA 2004）——胫骨/髌骨**骨铅蓄积**与美国男性年龄相关性白内障风险升高相关。
- **代理局限（yaml rationale 已如实注明）**：NHANES 血铅为**当前暴露**标志物，可能低估终身蓄积效应；NHANES 确证 OR=0.90 uninformative 与该局限对应（R5 P2-5 建议论文给出此对应解释）。
- **旧文档更正**：旧版引文 `10.1016/j.ijheh.2016.07.012` 不在 yaml，已修正为 JAMA 2004。

### r16 PM2.5 × 高眼压/CDR 可疑（`r16_pm25_x_glaucoma_iop_cdr`）

- **yaml 事实**：`pm25_exposure` × B 侧 `glaucoma_iop_elevated` + `glaucoma_suspect_cdr`；机制 `vascular_perfusion`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1186/s12989-021-00403-4`。
- **引文性质如实标注（R5 P1-7）**：唯一引文（Particle Fibre Toxicol 2021）为**小鼠/细胞焦亡机制研究**（"PM2.5 经焦亡通路触发眼压升高与青光眼样改变"）——**机制证据、非人群关联**。规则是人群级关联命题（B 侧为客观 IOP/CDR 条目），仅由机制证据支撑，与项目自声明的"研究设计匹配门"不符；旧文档"补 PM2.5-青光眼流行病学"待办一直未补。
- **处置**：规则冻结不动；论文正文补引人群流行病学证据（如 UK Biobank PM2.5×IOP 研究，Chua et al. IOVS 2020——评审建议的正文补引，不受规则引文冻结约束）；结果呈现标注"机制引文支撑、人群证据由正文补充"。
- **确证层**：NHANES 无 PM2.5 数据、KNHANES 无 PM2.5 行——未确证（not tested）。

### r17 PM2.5 × 早期 AMD（`r17_pm25_x_amd_early`）

- **yaml 事实**：`pm25_exposure` × `amd_early`；机制 `inflammation_immune`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1186/s12886-024-03465-y`。
- **证据与设计**：meta 分析（BMC Ophthalmology 2024，PMID 38684968）。
- **结局错配如实标注（R5 P1-5）**：meta 汇总结局为**任何 AMD**（未按早期/晚期分层），PM2.5 仅并入 **4 项研究**（OR=1.16 [1.11–1.21]，另含 NO2/O3）；规则绑定 `amd_early` 的分期**窄于**引文证据。与 r05 的裁定逻辑（因"证据不支持早期特异性"而改绑 amd_late）存在**不对称**——如实记录，审稿人并排可见。
- **为何仍绑 early + 局限**：数据库侧绑定由**结局可测性**驱动（NHANES/KNHANES 均有早期 AMD 分期变量，而晚期 AMD 患病率 ~1% 事件数过小），并非引文分期证据支持。论文中 r17 结局表述应为"AMD（含早期）"，并在局限性写明"r17 的分期绑定宽于其引文证据"。

### r18 紫外线 × 白内障（`r18_uv_x_cataract`）

- **yaml 事实**：`uv_exposure` × `cataract_any`；机制 `photochemical_uv`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1097/01.ede.0000086881.84657.98` + `10.1136/oem.2005.022343`（双源）。
- **证据与设计**：队列（Epidemiology 2003，皮质性/核性白内障确立危险因素）+ 病例对照基因交互研究（Saadat 2006 OEM，职业日晒×GSTM1×老年性白内障，伊朗小样本）。
- **历史注记**：曾评 A，C12 裁定降 A→B（单篇叙述性综述不满足 A 级标准；现 yaml 引文为两条设计匹配来源）。
- **二源偏弱标注（R5 P2-5）**：Saadat 2006 为小样本基因交互病例对照，作为 B 级二源偏弱；正文可补 Salisbury Eye Evaluation/Poli 等经典 UV-白内障证据（评审建议）。
- **旧文档更正**：旧版引文含 `10.1001/jama.2025.1597`（JAMA 2025）——不在 yaml，已修正。

### r22 BMI × 视网膜病变（`r22_bmi_x_retinopathy`）【本次新增小节，旧文档缺行】

- **yaml 事实**：`bmi_high` × B 侧 `retinopathy_any` + `dr_npdr`；机制 `inflammation_immune`；等级 **C**；severity **low**；方向 `risk_up`；引文 `10.1097/MD.0000000000011807`。
- **引文与数值（Zhu 2018, Medicine 97(32):e11807；R4 更正 1 更换，R5 全文核实数值一致）**：前瞻队列 meta，13 项队列、DR **发病**（incidence）、暴露为各研究最高 vs 最低 BMI 分类（多为 BMI>30 vs 正常）；总体 **RR=1.20 [1.01–1.43]**、T2DM 亚组 **RR=1.40 [1.05–1.87]**、I²=59.6%。方向 risk_up 与引文匹配。
- **文献异质性双引（如实记录）**：另有 meta 报 **null**——Zhou 2017（PMID 28562529）：27 项研究，肥胖 OR=0.97 [0.73–1.30]、超重 OR=0.89 [0.75–1.07]、连续 BMI OR=0.99，结论"超重/肥胖与 DR 风险升高无关"。两 meta 分歧主要在研究设计与结局类型（Zhu=发病型前瞻队列；Zhou=患病率混合）。NHANES 横断面 OR≈1.47 站在 Zhu（发病型）一侧。论文应双引并以"发病型前瞻证据支持、患病率型混合证据 null"解释保守定级。
- **定级与定位（真实理由，按 R5 P1-4 指正改写）**：r22 属**数据驱动的探索性扩展**——首轮确证结果（2026-10-12）之后新增的规则，构成 test-set fitting（analysis_plan v1.2 §0 协议偏离记录、limitations §1）。降 C/low 的真实理由 = **测试集拟合 + 文献异质性**（含 null meta），并非旧 analysis_plan 所写"引文非 meta"（§0.1 更正 1 更换引文后该理由已不成立）。2026-10-14 作者裁决维持 C 级不提级。
- **确证层如实**：NHANES 单库横断面 OR≈1.47、q=0.034/0.037（freq 口径，R5 重跑值）（临界）——观察方向与文献一致；但该 q 来自**忽略分层/PSU 抽样设计**的模型 SE（R5 方法学 P0-3/P1-11），设计效应校正后大概率 >0.05，**R5 之后不再将该行计为"复证"**，仅记"方向一致观察"。KNHANES OR=1.06 uninformative。
- **切点错配（R5 P1-1）**：同 r13——`bmi_high`≥25 宽定义 vs 引文肥胖（≥30/最高组）定义，向 null 稀释；且两库（NHANES 复现 / KNHANES 未复现）在同一阈值下结论相反，审稿人会追问阈值来源。

### r19 促炎饮食 × NPDR（`r19_proinflam_diet_x_dr_npdr`）

- **yaml 事实**：`pro_inflammatory_diet` × `dr_npdr`；机制 `inflammation_immune`；等级 **C**；severity **low**；方向 `risk_up`；引文 `10.1016/j.jnha.2025.100694`。
- **证据与设计**：**前瞻队列**（Europe PMC 核实标题即 prospective cohort study——R5 P1-4；旧版标"横断面研究"为误，已修正）。
- **定级理由**：新题、证据量少，如实 C 级；结果按证据级分层报告。
- **第二源待办**：膳食炎症指数（DII）×DR 第二源。
- **确证层**：三库无 DII 测量代理（P2-19）——未确证（not tested）。

### r20 吸烟 × 视力障碍中/重度（`r20_smoking_x_vi_mod_severe`）

- **yaml 事实**：`current_smoking` × B 侧 `vision_impairment_moderate` + `vision_impairment_severe`；机制 `oxidative_stress`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1038/s41598-020-79865-z`。
- **证据与设计**：前瞻队列（Han 2021 Sci Rep，PMID 33432008；尿可替宁客观吸烟标志）。
- **结局错配如实标注（R5 P1-8）**：引文 VI 定义为**双眼 VA 差于 0.5（decimal）= 双眼 logMAR>0.3（约 20/40 水平）**——引文结局**宽于**规则绑定（moderate 20/60+ / severe 20/200+），"中/重度"绑定未经引文直接支持；severity 表述应对齐引文（双眼 20/40 标准，介于 mild–moderate 之间）。yaml rationale 内"severity 映射按原文 VI 定义核对"为未完成的待办语气，以本节核实为准。
- **确证层如实**：VI_moderate/severe 在三库均 non-judgeable（被过滤出指标分母；NHANES VI 变量另有 P0-1 数据缺陷待修，修复前 NHANES 一切 VI 行无效）——**三库均未确证（uninformative / not tested）**。KNHANES 明细 current_smoking×VI_moderate OR=0.32 uninformative（且该行实测的是自报视觉困难，语义不同）。论文按"未确证规则"与 type-1/2 空白同类呈现。

### r21 PM2.5 × 视力障碍中/重度（`r21_pm25_x_vi_mod_severe`）

- **yaml 事实**：`pm25_exposure` × B 侧 `vision_impairment_moderate` + `vision_impairment_severe`；机制 `vascular_perfusion`；等级 **B**；severity **medium**；方向 `risk_up`；引文 `10.1186/s12889-024-20853-7`。
- **证据与设计**：前瞻队列（Yan 2024 BMC Public Health，PMID 39614249；PM2.5 **HR=1.60 [1.56–1.65]/10µg/m³**，同文报告绿地缓冲 NDVI HR=0.68/0.1）。
- **结局错配如实标注（R5 P1-8）**：引文 VI 为 **CHARLS 自报**（远/近视困难，DVI/NVI），**非客观 VA 分层**；效应量之大在该领域罕见（提示残余混杂），作为 B 级规则依据偏弱，效应量解释需谨慎。
- **确证层如实**：同 r20——三库均未确证（uninformative / not tested）。

## 数据库复证的分层口径（定义性 vs 非平凡关联）

`hba1c_elevated`（≥6.5%）与 `hyperglycemia`（FG≥126 mg/dL 或已诊断）的切点是**糖尿病诊断线**。该切点下"血糖类暴露 × DR/白内障"的复证属**定义性关联（教科书级对）**：DR 是糖尿病的定义性并发症，读片 DR 在非高血糖者中极罕见，OR 部分为结构使然（NHANES hba1c×retinopathy OR=6.07；KNHANES 27.2 / hyperglycemia 24.2）。**非平凡关联**指 BMI×DR、酒精×白内障等构造上不重言的对。

- NHANES 7 个复证对中 **5 个为血糖类（定义性）对**；KNHANES 仅有的 2 个复证对**全部**为血糖×DR 对——作为外部确证证据力接近重言（R5 P1-2/P1-4）。
- 论文规则：precision_rule 不得不加注释地表述为"系统性能"；复证构成按"教科书级对 vs 非平凡对"分层呈现；方法节明示 6.5%/126 切点含义（糖尿病水平，而非糖尿病人群内的"控制不佳"水平）及外推边界；KNHANES 章节如实写明 2 复证均为血糖-DR 对。

**规则可测性总览（R5 P2-19）**：r07/r08/r09/r16/r17/r18/r19 无测量代理，r20/r21 被 judgeable 排除——**9/21 条规则在任何库都没有确证证据**；论文须给 per-rule 可测性矩阵，避免"21 条规则经三库验证"的误读。

## 明示空白（拒识指标口径）

- **类型 1（结构性，只报覆盖率）**：`mercury_exposure` × 任意 B；`physical_inactivity` × 任意 B。
- **类型 2（证据性，abstain 只在此评估）**：`physical_activity` × `glaucoma_*`（方向混合 + 急性 Valsalva 分支三库无测量）。

## 嵌套语义（方案二）

多规则命中 → 报告层 max(severity) + 最具体优先展示；指标层 (A,B) 对独立计分。多 flag 实例：r02/r03（双 A 侧血糖 flags）、r04/r16/r20/r21/r22（多 B 侧 flags）、r03⊃r04 与 r22 内部（retinopathy_any ⊃ dr_npdr 嵌套结局）、AMD 分期并列（r05/r06→late；r17→early）。推断后果（对间非独立 → 有效样本量小于对数、CI 偏窄）论文须披露（R5 P1-5）。

## 患者因素升档规则（population subgroups）

diabetes / hypertension / chronic_kidney_disease / elderly 四组，定义见 configs/rules.yaml `patient_factor_rules`。边界情形（R5 P2-9）：diabetes 升档器的匹配暴露含 hyperglycemia/hba1c_elevated——当规则暴露本身就是 6.5% 切点的"糖尿病状态"时，同一信号将被计两次（暴露命中 + 因素升档）；论文示例计算须展示该情形的处理或声明升档仅在非血糖类暴露时生效。

---

## 与 v1.2 yaml 的差异审计（旧版 → 本版变更记录）

旧版 = docs/rule_rationale.md（2026-10-11，Phase 3 v2 作者裁定版）。R5 评审（P1-4 等）确认 yaml 自洽、旧文档过期。逐项矛盾与处置：

| # | 位置 | 旧文档内容 | yaml v1.2 实况 | 本次处置 |
|---|---|---|---|---|
| 1 | 证据级总数 | "A 3 / B 15 / C 3" | **A3 / B13 / C5**（自数核对：A=r10/r11/r13；C=r01/r04/r05/r19/r22） | 已修正；旧数未反映 r15 撤销、r22 新增、r05 B→C |
| 2 | r04 引文 | `10.3390/ijms26114992` + `10.1002/kjm2.70200`，"二源已补" | 唯一引文 `10.1167/iovs.17-22804` | 按 yaml 改单源；两条旧 DOI 不在冻结规则中，论文禁止引用；补记 R5 P1-3 引文性质核实（线粒体单倍群效应修饰研究） |
| 3 | r05 等级与引文 | B 级；引文 `10.1097/MD.0000000000041599`（实为 r11 的吸烟-AMD meta，张冠李戴）；B 侧写"AMD 早期" | **C 级**；引文 `10.62347/QJPQ2923`；B 侧 `amd_late` | 已修正；并补记文献层反证（Babaker 2025 meta，PMID 39993131，血脂项 null）与不对称处理说明（R5 P1-6） |
| 4 | r07 引文 | `10.3390/ijms241512014`（叙述综述） | `10.3390/nu9030307` + `10.1016/j.jcjo.2017.09.026`（双 meta） | 已修正；补 P2-3 绑定特异性标注 |
| 5 | r09 引文 | `10.1016/j.ophtha.2018.09.032` | `10.1016/j.ophtha.2018.08.006` | 已修正（DOI 转录错误） |
| 6 | r12 引文 | 含 `10.1111/ceo.13892`，"二源已补" | 仅 `10.1016/j.ophtha.2006.07.046` | 已修正（单引文） |
| 7 | r14 引文 | `10.1016/j.ijheh.2016.07.012` | `10.1001/jama.292.22.2750`（JAMA 2004 骨铅队列） | 已修正 |
| 8 | r18 引文 | `10.1001/jama.2025.1597`（JAMA 2025）+ Epidemiology 2003 | `10.1097/01.ede.0000086881.84657.98` + `10.1136/oem.2005.022343`（OEM 2006 Saadat） | 已修正；补 P2-5 二源偏弱标注 |
| 9 | r19 设计类型 | "横断面研究" | 引文 `10.1016/j.jnha.2025.100694` 经 Europe PMC 核实为**前瞻队列** | 已修正（R5 P1-4） |
| 10 | r22 行 | **表格完全缺行** | C/low、risk_up、`10.1097/MD.0000000000011807` | 新增小节：Zhu 2018 数值、Zhou 2017 null meta（PMID 28562529）双引、探索性扩展定位、NHANES 方向一致但 survey 方差下不再计为复证、切点错配 |
| 11 | r17 分期绑定 | 未标注 meta 结局实为 any AMD（PM2.5 仅 4 项研究） | 绑 `amd_early`，引文 meta 为不分期 AMD | 新增如实标注 + 与 r05 裁定逻辑的不对称记录 + 可测性驱动解释（R5 P1-5） |
| 12 | r16 引文性质 | 未标注唯一引文为动物/细胞机制研究；"补流行病学"待办未补 | 引文 `10.1186/s12989-021-00403-4` 为小鼠焦亡机制研究 | 新增"机制证据、非人群关联"标注与正文补引建议（R5 P1-7） |
| 13 | r20/r21 结局定义 | 未标注结局-引文错配与三库未确证 | 引文分别=双眼 20/40 标准 / CHARLS 自报 VI（HR=1.60） | 新增错配标注与"三库均未确证（uninformative/not tested）"（R5 P1-8） |
| 14 | r10/r13 方向审计 | 未记录 NHANES 非显著反向（OR=0.698 q=0.80 / OR=0.986 q=1.0）及偏倚调查结案 | 规则基于 A 级文献证据保留 | 新增结案记录（引用 bias_investigation_smoking_cataract.md）+ cross-sectional limitation + P1-8"100% 年龄混杂"表述修正 |
| 15 | r22 降级理由 | （旧文档无行；analysis_plan §0 旧理由"引文非 meta"已因引文更换失效） | R4 更正 1 后引文为前瞻队列 meta | 降级理由改写为真实理由：测试集拟合 + 文献异质性（R5 P1-4） |
| 16 | 定义性关联分层 | 无 | — | 新增"数据库复证的分层口径"节（hba1c/FG 切点=糖尿病诊断线；教科书级对 vs 非平凡对）（R5 P1-2） |
| 17 | bmi_high 切点错配 | 无 | `bmi_high`=≥25 vs 引文肥胖 ≥30 | r13/r22 节新增错配声明（宽定义→向 null 稀释）（R5 P1-1） |

*本文件为 R5 评审（2026-10-14）P1-4 处置产物；除本文件外未改动任何项目文件；configs/rules.yaml v1.2 的规则语义自 2026-10-12 起冻结（当前 sha 95ebf0a9…，仅 2026-10-19 的引用标识符归一化与分级注释更新，字段未变）。*
