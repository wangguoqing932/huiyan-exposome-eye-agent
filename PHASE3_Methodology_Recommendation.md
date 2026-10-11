# Phase 3 · 方法学推荐（v2 · 裁定后修订版：架构 / 规则机制 / 风险登记）

> huiyan 慧眼 · medical-agent-planner Phase 3（第一批，2026-10-11 作者裁定后修订）
> 本版落实《Phase 3 第一批裁定》全部四项：r19 立项、体力活动转明示空白、空白分两类、三处引用修正 + r04 补机制引用 + r16 pin 条目、嵌套去重语义定稿（方案二）、裁定 4 选 A。
> 下一批（放行后）：数据集构建配方 / 验证策略与 4 基线 / 图件合约映射 → Phase 4 scaffold。

---

## 1. 架构确认（裁定无异议，维持）

**规则引擎 + 知识图谱（LightRAG）+ LLM 仲裁 三层混合架构成立，不降级。** 5 处增量维持（pair 级分析单元 / 三库三层验证+泛化落差 / risk_type 与 A-flags 解耦 / 覆盖率感知 / 拒识安全行为）。4 基线沿用：pure_llm / naive_rag / lightrag / full_system。
**新增（依裁定 2）**：拒识（abstain）行为指标**只在类型 2 空白上评估**；类型 1 空白只报覆盖率（见 §2.5）。

---

## 2. 规则机制清单 v2（21 条：18 修正版 + r19 + r20/r21 视力障碍）

**构建纪律（含裁定新增）**：
1. 每条 risk_type ∈ 7 机制清单；
2. 每条 ≥1 引用，executor phase3 阶段**补第二源 DOI**（双源核验）；
3. 证据分级 A/B/C 如实标注，**结果按证据级分层报告**（A/B/C 分组出性能，C 级不与 A 级混合出数）；
4. **（裁定 3a 新增）证据类型匹配门**：引用须按 study design 分类（指南 / meta / 队列 / 机制 / 患病率 / 基因关联 / 手术管理），与规则 claim 类型匹配后才放行——写入 executor phase3 规格（verify_rule_citations 只验"真实+相关"，本门补其盲区；r02/r03/r06 三处即为该盲区实例）。

### 2.1 规则表（v2；⚠ = 本版修正处）

| # | 规则（A × B） | risk_type | 方向 | 证据级 | 代表引用（DOI） |
|---|---|---|---|---|---|
| r01 | 尿酸升高 × cataract_any | oxidative_stress | ↑ | C | Cell Death Discov 2024 `10.1038/s41420-024-01900-z` |
| r02 ⚠ | 高血糖 × cataract_any | glycation_metabolic | ↑ | **B**（原 A 降） | Diabetes Metab Res Rev 2019 T2D 白内障风险因素系统综述 `10.1002/dmrr.3073`（原 IJO 手术管理综述弃用；人群限定 T2D，executor 补一般人群发病 meta 二源） |
| r03 ⚠ | HbA1c 升高 × retinopathy_any | glycation_metabolic | ↑ | **B**（原 A 降） | Diabetes Ther 2018 血糖控制与 DR `10.1007/s13300-017-0345-5`（原患病率/负担文弃用；executor 补 DCCT/UKPDS 二源） |
| r04 ⚠ | HbA1c 升高 × dr_pdr | vascular_perfusion | ↑ | **C**（不再借 r03 的 A） | Int J Mol Sci 2025 VEGF 与 DR/AMD 机制综述 `10.3390/ijms26114992`（新生血管/缺血机制；executor 补增生性病变关联级二源） |
| r05 | 血脂异常 × amd_early | oxidative_stress | ↑ | B | Medicine 2025 `10.1097/MD.0000000000041599` |
| r06 ⚠ | CRP 升高 × amd_late | inflammation_immune | ↑ | B | Surv Ophthalmol 2011 **血清 CRP-AMD meta** `10.1016/j.survophthal.2010.08.007`（原基因多态性文弃用；flag 维持 crp_elevated 血清口径不改名；2011 较旧，executor 补新源） |
| r07 | 维 D 缺乏 × dr_npdr | endocrine_hormonal | ↑ | B | Int J Mol Sci 2023 `10.3390/ijms241512014` |
| r08 | 抗氧化摄入不足 × cataract_any | oxidative_stress | ↑ | B | Free Radic Res 2013 `10.3109/10715762.2013.777155` |
| r09 | 地中海饮食 × amd_late | oxidative_stress | ↓保护 | B | Ophthalmology 2019 `10.1016/j.ophtha.2018.09.032` |
| r10 | 当前吸烟 × cataract_any | oxidative_stress | ↑ | A | EBioMedicine 2022 `10.1016/j.ebiom.2022.104154` |
| r11 | 当前吸烟 × amd_late | oxidative_stress | ↑ | A | Medicine 2025 `10.1097/MD.0000000000041599` |
| r12 | 饮酒 × cataract_any | oxidative_stress | ↑ | B | Clin Exp Ophthalmol 2021 `10.1111/ceo.13892` |
| r13 | BMI 升高 × cataract_any | glycation_metabolic | ↑ | A | PLoS One 2014 `10.1371/journal.pone.0089923` |
| r14 | 铅暴露 × cataract_any | heavy_metal_toxicity | ↑ | B | Int J Hyg Environ Health 2016 `10.1016/j.ijheh.2016.07.012` |
| r15 | 镉暴露 × cataract_any | heavy_metal_toxicity | ↑ | B | 同 r14（同文覆盖镉，正当共用） |
| r16 ⚠ | PM2.5 × **[glaucoma_iop_elevated, glaucoma_suspect_cdr]** | vascular_perfusion | ↑ | B | Part Fibre Toxicol 2021 `10.1186/s12989-021-00403-4`（pin 到两个客观青光眼条目；引文结局即"ocular hypertension"；两条目在 NHANES VCDR + KNHANES IOP/CDR 均客观可得） |
| r17 | PM2.5 × amd_early | inflammation_immune | ↑ | B | BMC Ophthalmol 2024 `10.1186/s12886-024-03465-y` |
| r18 | UV 暴露 × cataract_any | photochemical_uv | ↑ | A | JAMA 2025 `10.1001/jama.2025.1597` |
| r19 ★ | 促炎饮食 × dr_npdr | inflammation_immune | ↑ | **C**（如实，不升格） | J Nutr Health Aging 2025 `10.1016/j.jnha.2025.100694`（条件①③ 已纳入纪律 2/3；条件② 见纪律 3） |
| r20 ★ | 当前吸烟 × **[vision_impairment_moderate, vision_impairment_severe]** | oxidative_stress | ↑ | B | Sci Rep 2021 吸烟/尿可替宁与 VI 发病 `10.1038/s41598-020-79865-z` |
| r21 ★ | PM2.5 × **[vision_impairment_moderate, vision_impairment_severe]** | vascular_perfusion | ↑ | B | BMC Public Health 2024 绿地/空气污染与 VI 前瞻队列 `10.1186/s12889-024-20853-7` |

（★ = 裁定新增；⚠ = 裁定修正。r20/r21 引用中 VI 定义对应中度及以上阈值，severity 映射在 executor 阶段按各文定义逐条核对。）

**机制覆盖**：oxidative 7（r01/05/08/09/10/11/12+20→8）· glycation 3 · vascular 3（r04/16/21）· inflammation 3（r06/17/19）· metal 2 · photochemical 1 · endocrine 1 —— 7 类全覆盖。

**证据级分布（修正后）**：**A 4 / B 14 / C 3**（共 21 条）。
注：比裁定预告的"A 7→6"更保守——r02、r03 换用证据类型匹配的引用后，现有单源仅支持 B 级（宁低勿虚）；A 级 = r10、r11、r13、r18。Phase 3 第二批报证据级分布时以此为准。

### 2.2 明示空白（裁定 1b + 2）

| 类型 | 定义 | 条目 | 指标口径 |
|---|---|---|---|
| 类型 1 结构性空白 | 从未为其写规则（A 旗标级） | **mercury_exposure × 全部 B**；**physical_inactivity × 全部 B** | 只报覆盖率，**不计入拒识/行为指标** |
| 类型 2 证据性空白 | 有规则意图但证据不足/方向混合（对级） | **physical_activity × glaucoma_***（急性 Valsalva 分支在 NHANES/KNHANES/队列均无测量，违反"数据集真能判定"纪律；候选引文标题本身在问方向） | **拒识/abstain 指标只在此类上评估** |

### 2.3 嵌套结局去重语义（裁定 3d · **定稿方案二**）

1. 允许一条规则携带多个 B flags（severity 阶梯与 umbrella，如 r16/r20/r21；r03 与 r04 分别锚 umbrella 与最具体条目，共存）；
2. **报告层**：同一暴露档案多规则命中时，整体等级取 **max(severity)**，展示按**最具体 B 条目优先**（umbrella 仅在无 specific 命中时报出）；
3. **指标层**：分析单元 = 对，umbrella 对与 specific 对是**不同对**，pair-level P/R/F1 按对独立计分、天然去重；**报告级指标**（专家盲评、demo 案例）逐对去重，禁止重复计数。
（选方案二而非方案一的理由：severity 阶梯与 umbrella 条目各有可判定库——KNHANES 的 retinopathy_any（E_DRP）与 NPDR/PDR 分级并存——方案一会强迫人为拆分并丢失 umbrella 可判层。）

### 2.4 B 侧覆盖（裁定 4 · 选 A）与"已测量无规则"声明

裁定 4 选 **A**（补视力障碍规则 r20/r21）+ 对其余零规则条目按 B 式声明：

| B 条目 | 规则数 | 处置 |
|---|---|---|
| cataract_any | 9（r01/02/08/10/12/13/14/15/18） | — |
| amd_late | 3（r06/09/11） | — |
| amd_early | 2（r05/17） | — |
| dr_npdr | 2（r07/19） | — |
| vi_moderate / vi_severe | 各 2（r20/21） | 进入 pair 指标 |
| retinopathy_any | 1（r03） | — |
| dr_pdr | 1（r04） | — |
| glaucoma_iop_elevated / glaucoma_suspect_cdr | 各 1（r16） | — |
| **vi_mild** | 0 | **已测量无规则**：轻度 VI 主要由未矫正屈光不正驱动，非本暴露组规则域；从 pair P/R/F1 分母剔除，只报覆盖率 |
| **glaucoma_selfreport / amd_selfreport** | 0 | **已测量无规则**：自报条目作为客观条目的跨库对照层（队列臂验证用），不承载规则；从分母剔除、只报覆盖率 |
| **optic_disc_abnormality** | 0 | **已测量无规则**：作为 r16（CDR/IOP 客观链）的邻近对照结局；同上处置 |
| cataract_subtype_graded | 0 | 无源可判（已有处置） |

→ **11/15 条 B 进入 pair 指标定义域；4 条声明剔除**（写入验证策略，避免"定义域为空"或隐性虚大分母）。

---

## 3. 风险登记（Top 10，裁定无异议，维持）

R1 队列层覆盖率低（已量化 120 上限+逐条声明）· R2 横断面因果限制（预注册方向一致性+FDR+限制段）· R3 多重检验（BHY FDR+敏感性）· R4 口径异质（双口径交叉+覆盖率随结果报告）· R5 分级依赖无源（已处置）· R6 LLM 幻觉/引用（双源 DOI+**证据类型匹配门（本版新增至 executor 规格）**+人工抽查中间件）· R7 专家盲评（3 名×60 份+κ）· R8 KNHANES 复杂抽样（官权重复算+敏感性）· R9 GBD 版本漂移（锁定 2023）· R10 无代码团队（Claude 全包+中间件抽查）。附：同族投稿撞车提示（jingming→JAMA Ophthalmol，cover letter 区分）。

---

## 4. 放行条件对账

| 放行条件 | 状态 |
|---|---|
| 1a r19 立项（三条立项条件全收） | ✅ §2.1 r19 + 纪律 2/3 |
| 1b 体力活动不立项转明示空白 | ✅ §2.2 |
| 裁定 2 空白分两类，拒识只评类型 2 | ✅ §2.2 + §1 |
| 3a 三处引用修正 | ✅ r02/r03/r06 已换证据类型匹配引文；工具盲区门写入纪律 4 |
| 3b r04 补机制引用 + 自证证据级 | ✅ VEGF 机制引 + 降为 C（A 级 7→4，见 §2.1 注） |
| 3c r16 pin 条目 | ✅ pin 至 glaucoma_iop_elevated + glaucoma_suspect_cdr |
| 3d 嵌套去重语义定稿 | ✅ 方案二（§2.3，附选择理由） |
| 裁定 4 选 A/B | ✅ 选 A（r20/r21）+ 其余 4 条目 B 式声明（§2.4） |

---

## 5. 下一步

Phase 3 第二批（放行后即做）：**数据集构建配方**（4 数据集逐集：检索式/提取法/金标准流程/目标规模/中间件清单）+ **验证策略与 4 基线**（含证据级分层报告设计、拒识指标口径、去重语义实现）+ **图件合约映射** → 然后 Phase 4 scaffold。
