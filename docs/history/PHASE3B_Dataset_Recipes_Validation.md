# Phase 3 · 第二批：数据集构建配方 + 验证策略与基线 + 图件映射

> huiyan 慧眼 · medical-agent-planner Phase 3 第二批 · 2026-10-11（作者全速授权）
> 上游：PHASE3_Methodology_Recommendation.md v2（21 规则 / 两类空白 / 方案二去重 / A4-B14-C3）+ §X.5 覆盖矩阵

---

## 1. 数据集构建配方（4 集 · 每集含可人工抽查中间件）

### 1.1 dev-exposure-disease-pairs（development，~400 对）
- **来源**：21 条规则的证据文献池（每条 ≥2 源，executor phase3 补齐）+ AAO PPP（POAG/AMD/DR 三册，代理通道已验证）+ 系统综述池（§X.1 各域 126–747 篇）
- **提取**：文献 → (暴露 flag, 眼病条目, 方向, 证据级, 设计类型) 五元组；阳性对 = 有明确方向支持；阴性对照对 = 从 40×15 空间抽取"检索无支持"的对（预注册抽样规则：每条阳性对配 ~0.6 条同域阴性对）
- **金标准**：label_guideline（文献/指南明确方向）
- **规模**：~250 阳性 / ~150 阴性
- **中间件**：文献筛选表（PMID/标题/纳入理由/证据级/设计类型）、对清单 CSV、纳入排除流程图、每步 N 值
- **消费**：规则生成 + Phase 1 规则一致性（目标 100%）

### 1.2 intval-nhanes（internal_validation，~400 对）
- **提取**：逐对 survey-weighted logistic（暴露按四分位/临床切点；协变量 age/sex/race/education/PIR/BMI + 非暴露域混杂）；BHY FDR
- **可判层**：VIX 5 周期（12-85 岁，logMAR→WHO 三档）；OPXRET 2005-08（40+，DR 四级/ARM/VCDR）；VIQ 自报；暴露 = BIOPRO + DR1TOT/DR2TOT + PBCD/UHM/PAH + 问卷
- **金标准**：database_outcome（OR 显著且方向与规则一致 = 阳性）
- **中间件**：变量映射表（暴露→NHANES 变量名×周期）、纳入排除流程、每步 N、逐对结果 CSV
- **消费**：Phase 2 内部性能（pair 口径 sens≥0.70 / spec≥0.60 起步线）

### 1.3 extval-knhanes（external_validation，~300 对）
- 同 1.2 口径，按官方变量字典 + 权重（wt_itvex 等）；眼科 10 波（2008-12 全龄 / 2017-20 40-80 / 2021 10-59）；R→CSV 转换日志为中间件之一
- **消费**：Phase 3 外部验证（跨国），出相对 NHANES 的泛化落差

### 1.4 extval-cohorts-9（external_validation，≤120 对）
- 仅自报层：cataract_any（6/9 库）/ glaucoma_selfreport（4/9）/ 自评视力（对照层，不进主指标）；逐库复算后固定效应合并
- **中间件**：逐库变量映射表（已核验的 catracte/catrcte/glaucoma/ashamd/da033-037 清单）+ 逐库覆盖率表
- **消费**：Phase 3 外部验证（跨人群，第二层泛化落差；逐条声明跨人群强度）

## 2. 验证策略（4 阶段 × 数据集映射）

| 阶段 | 数据集 | 指标 | 通过线 |
|---|---|---|---|
| P1 规则一致性 | dev | 对级判定 vs 金标准 | 100%（规则同源，只查实现） |
| P2 内部性能 | NHANES | pair P/R/F1（证据级 A/B/C 分层 + 总体） | sens≥0.70, spec≥0.60 |
| P3 外部验证 | KNHANES → 9 队列 | 同口径 + **泛化落差**（ΔF1 逐层） | ΔF1≤0.15 可接受；>0.25 触发归因分析（预注册） |
| P4 专家盲评 | 60 份 agent 报告 × 3 名眼科专家 | 可接受率 + 一致性 κ | κ≥0.6；分歧仲裁记录 |

- **4 基线 × ≥5 seeds**：pure_llm / naive_rag / lightrag / full_system
- **拒识指标**：仅在类型 2 空白（physical_activity × glaucoma_*）上评估 abstain 正确率；类型 1（mercury / physical_inactivity）只报覆盖率
- **分母纪律**：pair 指标定义域 = 11/15 B 条目 × 各库可判性交集；4 条已声明剔除条目只报覆盖率
- **去重语义**：按 PHASE3 v2 §2.3（方案二）实现：报告层 max(severity) + 最具体优先；指标层按对独立计分
- **多重检验**：每库内 BHY FDR + 预注册分析计划（分析计划先于任何验证运行提交至 docs/analysis_plan.md）

## 3. 图件合约映射（5 图，对应 scaffold 的 figure contracts）

| 图 | 内容 | 数据源 |
|---|---|---|
| fig1 | 系统架构与三层验证流程（规则+KG+LLM；pair 级输出） | 架构图（示意） |
| fig2 | 注册表与覆盖：15×3 矩阵热图 + 各库可判对数 | 覆盖矩阵 + 变量映射表 |
| fig3 | 验证性能：4 基线 × 3 库 pair-F1 + 证据级分层 | phase5 输出 |
| fig4 | 泛化落差：NHANES→KNHANES→队列 ΔF1 逐层 + 逐条目跨人群强度 | phase5 输出 |
| fig5 | 规则-证据地图：21 规则 × 机制 × 证据级（A4/B14/C3）热图 | rules.yaml + 引用核验记录 |

## 4. Phase 4 前检查单

□ config 3/3 PASS ✓（已达成）· □ 规则表 v2 定稿 ✓ · □ 验证策略含预注册阈值 ✓ · □ 图件映射 ✓ · □ 本批作者放行 = 全速授权（2026-10-11"不要停下来"指令）
