# 慧眼（huiyan）暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证 Agent — 完整执行方案

> **项目代号**：huiyan / 慧眼
> **方法学骨架来源**：TongYuan (FDI screening, *Nutrients* submission) — 80% 代码复用
> **创建日期**：2026-10-11
> **目标期刊**（一志愿）：*Ophthalmology（IF 8+ 档候选；Phase 2 期刊适配检查后最终锁定）*；备选：*JAMA Ophthalmology*, *British Journal of Ophthalmology*, *American Journal of Ophthalmology*
> **预计工作量**：24 周（含数据构建、验证、写作）
> **当前状态**：📋 规划中（PLAN.md 由 medical-agent-planner 生成，等待 coding agent 启动 Phase 0）

---

## 0. 文档使用说明

本文档是 **从零到投稿** 的执行蓝图。每个任务都给出：
- **执行内容**：做什么
- **验收标准（verify）**：怎样算完成
- **Subagent 策略**：是否并行、用哪类 subagent
- **依赖任务**：必须先完成哪些前置

> **执行入口**：按 §9 任务清单顺序执行。Phase 0 全部顺序执行（小任务），Phase 1 启动 3 个并行 Explore subagent（entities_a / entities_b / evidence），完成后 Claude 整合 → Phase 2 顺序 → Phase 3 单 Agent → Phase 4 并行启动 3 个 Explore subagent → Phase 5 由 Claude 主导 → Phase 6 单 Agent → Phase 7 由 Claude + 用户协作 → Phase 8 投稿。

---

## §X. Literature Landscape & Feasibility (Phase 2 输出 · 已定稿)

> 本节由 medical-agent-planner Phase 2 (online validation) 生成并于作者两轮审核后定稿（2026-10-11）。完整审计轨迹：`PHASE2_Literature_Landscape.md`（含四探针检索式与全标题清单 `PHASE2_probe_titles.txt`，529 行）。

### X.1 研究前景（Research Prospect）

- **方向**：暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证
- **PubMed 5 年趋势**：exposom\*×眼病 17 篇/5y（全时段 22）；逐年 2020:2→2021:1→2022:0→2023:2→2024:3→2025:6→2026:7。低基数、方向性上升（2024–2026 合计 16/21），不作加速推断
- **近年综述**：Prog Retin Eye Res 2026《Exposome for ocular diseases》（10.1016/j.preteyeres.2026.101524，顶刊认定方向）；Exposome 2025 oculomics×exposomics roadmap（10.1093/exposome/osaf013）；Int J Mol Sci 2022《Vitamin D and Ocular Diseases》SR
- **活跃课题组**：China Kadoorie Biobank 组（ACG×exposome-wide，APJO 2026）；NHANES 重金属×眼病 ML 组（Sci Rep 2024/2025 两篇）；LifeLines+UK Biobank 组（尿酸×青光眼，IOVS 2026）
- **基金/产业动态**：在 NEI 公开战略计划页面（2021–2026 版）未检出将环境/代谢暴露列为眼病优先方向的表述（检索时点 2026-10-11，属未检出而非否定）；未检索到"暴露组×眼病筛查系统"专项资助公告——学术前沿先行、专项资助尚缺的窗口期
- **判定**：**strong**

### X.2 数据可及性（Data Availability）

| 数据源 | 类型 | 覆盖实体 | 可访问性 | 国内镜像/备注 |
|---|---|---|---|---|
| NHANES 1999-2008 本地原始库 | 公共数据库 | A（生化/膳食/毒物）+ B（VIX 视力 5 周期 12-85 岁；OPXRET 2005-08 40+ 含 VCDR/DR 四级/ARM；VIQ） | **本地已实测**（文件级核验） | E:\...\16.NHANES，719 文件 |
| KNHANES 1998-2024 | 公共数据库 | A（生化+营养+空气污染）+ B（眼科 10 波：IOP/CDR/AMD 四型/DR 逐病灶/VA） | **本地已实测**（Rdata 五包 + 官方字典） | E:\...\11. KNHANES；2013-16 无眼科模块 |
| 9 大老龄队列（CHARLS/HRS/ELSA/SHARE/KLoSA/LASI/MHAS/CRELES/CLHLS） | 公共数据库 | A（生活方式 9/9 + 部分血清）+ B（自报层：cataract_any 6/9、glaucoma 4/9、amd 1/9、自评视力 9/9） | **本地已实测**（dta 变量级核验） | E:\...\01-09 目录 |
| GBD 视觉库（2023×2 + 2021 55+） | 公共数据库 | 负担/归因背景 | 本地 | E:\...\15/17/18 |
| PubMed E-utilities / AAO PPP / Crossref+OpenAlex | 检索/指南 | 证据源 | accessible（NCBI key 已配；AAO 三册全文代理通道已验证） | 见 network_and_proxy.md |

**综合判定**：**strong**

### X.5 验证数据集可及性（Dataset Availability, v3.0）

| 数据集 ID | 角色 | 来源 | 目标规模 | 金标准方式 | 独立性轴 | 可及性判定 |
|---|---|---|---|---|---|---|
| dev-exposure-disease-pairs | development | 21 条规则证据池 + AAO PPP + 系统综述池 | 400 | label_guideline | source | **feasible** |
| intval-nhanes | internal_validation | NHANES 1999-2008（VIX/OPXRET/VIQ × 生化/膳食/毒物） | 400 | database_outcome | source | **feasible** |
| extval-knhanes | external_validation | KNHANES 眼科 10 波 × 官方权重 | 300 | database_outcome | site | **feasible** |
| extval-cohorts-9 | external_validation | 9 队列自报层（3/15 条 B 可判；逐条声明跨人群强度） | **120（上限）** | database_outcome | population | **feasible_reduced** |

**硬性要求（v3.0）**：4 个启用数据集全部存活（4 ≥ 2）✓；15×3 覆盖矩阵与逐格变量证据见 PHASE2 文档 §X.5。

### X.3 同类工作对比（Prior Art）

| 系统/工作 | 年份 | 期刊 | 实体覆盖 | 机制覆盖 | 验证 | 本项目填补的空白 |
|---|---|---|---|---|---|---|
| ACG × exposome-wide（CKB） | 2026 | Asia Pac J Ophthalmol | 单病种 | 关联 | 单队列 | 无系统/规则/多库 |
| DR × EWAS（NHANES） | 2020 | J Clin Med | 单病种 | 关联 | 单库 | 同上；本项目同库升维 |
| EWAS→预测评分（AD） | 2026 | Alzheimers Dement | 单病种 | 评分 | 单库 | 非眼科、无规则引擎 |
| exposome-phenome 图谱 | 2026 | Nat Med | 全表型 | 描述 | 多库 | 描述性，无筛查输出 |
| 可解释 ML 眼病预测（近视性黄斑病变 10 年；吸烟×衰老白内障-AMD XAI） | 2024/2026 | IOVS / Front Public Health | 单病种/共病 | 可解释 ML | 单队列 | 无暴露组系统、无跨库泛化 |
| **huiyan 本项目** | — | — | **暴露组 40 × 眼病 15** | **7 机制规则+KG+LLM** | **NHANES→KNHANES→9 队列三层+泛化落差** | — |

**判定**：**clear_gap**（四探针空间全标题筛查：EWAS 228 篇中眼病仅 5；眼病系统类 505 篇均为影像 DL；EWAS×眼病全库 6 篇）

### X.4 期刊适配（Journal Fit）

| 期刊 | IF | 适配判定 | 近 24 月类似文章（DOI） |
|---|---|---|---|
| Ophthalmology | ~13 | fit | AAO 羟氯喹视网膜病变筛查建议 2025 修订 `10.1016/j.ophtha.2025.11.001`；血浆代谢组→DR 预测 `10.1016/j.ophtha.2024.07.004` |
| JAMA Ophthalmology | ~8 | fit | 视网膜图像 DL 预测早产儿心肺疾病 `10.1001/jamaophthalmol.2025.5814` |
| British Journal of Ophthalmology | ~4 | fit | 暴露广谱×AMD `10.1136/bjo-2025-328446`（2026 刊出） |

**投稿策略**：一志愿 Ophthalmology（78 篇筛查/AI 类/24 月），备选 JAMA Ophthalmology→BJO；同族 jingming 投 JAMA Ophthalmology，cover letter 明示区分。

---

## 1. 项目定位与差异化

### 1.1 一句话定位

**慧眼 是elderly的暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证决策支持系统**：通过oxidative_stress, glycation_metabolic, inflammation_immune, vascular_perfusion, endocrine_hormonal, heavy_metal_toxicity, photochemical_uv机制规则 + 图组织证据检索，在 40+ 暴露组（代谢-营养-生活方式-环境） × 15+ 主要致盲眼病 的声明的覆盖域内组合（20 条规则覆盖约 54/615 对）上，提供可追溯、可解释的安全性/推荐性分级报告。

### 1.2 与参考项目的差异（防 Salami-Slicing）

| 维度 | 参考项目 | 本项目 |
|---|---|---|
| 实体 A | food | 暴露组（代谢-营养-生活方式-环境） |
| 实体 B | drug | 主要致盲眼病 |
| 相互作用类型 | FDI | oxidative_stress, glycation_metabolic, inflammation_immune, vascular_perfusion, endocrine_hormonal, heavy_metal_toxicity, photochemical_uv |
| 规则数 | 15 | 12 |
| 数据源 | 本项目不使用（FDA/USDA/LiverTox 为 TongYuan 遗留） | NHANES 1999-2008 本地原始库（生化/膳食/毒物 + VIX 客观视力 / OPXRET 视网膜分级 / VIQ 眼病问卷）[local_confirmed], KNHANES 1998-2024 本地 Rdata 全集 + 官方变量字典（眼科检查模块，1,686 眼科变量）[local_confirmed], 9 大老龄队列原始库（CHARLS/HRS/ELSA/SHARE/KLoSA/LASI/MHAS/CRELES/CLHLS）[local_confirmed], GBD 视觉库（GBD 2023 近视力丧失 / 2023 盲与视力损害 / 2021 55+ 暴露-结局）[local_confirmed] |
| 文化/临床故事 | 药食同源 + 全球化营养学 | 多库跨文化验证：规则仅由文献/指南构建，性能在 NHANES（内部）→ KNHANES（独立国家）→ 9 国老龄队列（跨人群）三层独立验证并报告泛化落差；可解释的暴露组×眼病风险筛查 agent（暴露→机制→眼病→证据等级 链路溯源；全链溯源声明因 G10 证据过滤缺陷暂时撤回） |
| 目标期刊 | Nutrients | Ophthalmology（IF 8+ 档候选；Phase 2 期刊适配检查后最终锁定） |
| 患者人群 | general + high-risk subgroups | diabetic, hypertensive, rural_china, multi_country |

**审稿人最可能问的差异化问题**：与已有暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证工作有何不同？ → 答案：多库跨文化验证：规则仅由文献/指南构建，性能在 NHANES（内部）→ KNHANES（独立国家）→ 9 国老龄队列（跨人群）三层独立验证并报告泛化落差；可解释的暴露组×眼病风险筛查 agent（暴露→机制→眼病→证据等级 链路溯源；全链溯源声明因 G10 证据过滤缺陷暂时撤回）

### 1.3 核心创新点（Highlights 草案）

1. 首个针对该 A×B 组合的系统化筛查工具
2. 12+ 条确定性规则，覆盖多类机制
3. 规则 + 图检索的混合架构，可解释、非黑箱
4. 多库跨文化验证：规则仅由文献/指南构建，性能在 NHANES（内部）→ KNHANES（独立国家）→ 9 国老龄队列（跨人群）三层独立验证并报告泛化落差；可解释的暴露组×眼病风险筛查 agent（暴露→机制→眼病→证据等级 链路溯源；全链溯源声明因 G10 证据过滤缺陷暂时撤回）
5. 多数据集验证（开发 → 内部验证 → 外部验证 + 泛化落差，v3.0）

---

## 2. 方法学设计

### 2.1 整体架构（复用 TongYuan 流水线）

```
用户输入（暴露组（代谢-营养-生活方式-环境） + 主要致盲眼病 + 患者因素）
  → 实体归一化（normalize.py）
  → 规则引擎风险评估（risk_rules.py + rules.yaml）
  → LightRAG 图组织证据检索（lightrag_adapter.py）
  → 证据压缩（top-k + 字符上限）
  → 结构化安全报告生成（report.py）
  → 验证 / 专家盲评导出
```

### 2.2 与 TongYuan 代码复用率

| 模块 | TongYuan 源文件 | 复用程度 | 修改要点 |
|---|---|---|---|
| 数据模型 | `schemas.py` | 90% | `Food` → `Exposure`；字段定制 |
| 归一化 | `normalize.py` | 80% | 扩展别名表 |
| 规则引擎 | `risk_rules.py` | 95% | YAML 配置不同，逻辑零改动 |
| Evidence Store | `evidence_store.py` | 85% | 同 TongYuan |
| LightRAG Adapter | `lightrag_adapter.py` | 95% | 仅索引内容不同 |
| Naive RAG | `naive_rag.py` | 95% | 同上 |
| Safety Agent | `safety_agent.py` | 85% | 入口字段重命名 |
| 报告生成 | `report.py` | 80% | 提示词模板改写 |
| Streamlit | `streamlit_app.py` | 70% | UI 文案、导航 |

**总复用率：约 80%。新增工作集中在：数据构建、规则 YAML、UI 调整、论文写作。**

---

## 3. 知识库构建计划

### 3.1 EntityA 实体注册表（目标 40+ 条）

**结构**（`data/seed/entities_a.csv`）：

```csv
exposure_id,exposure_name,aliases,category,active_mechanisms,flags,evidence_sources


```

**实体来源**：

| 类别 | 数量 | 数据源 |
|---|---:|---|
| 主名录 | 40 | 各库原始变量字典（NHANES 生化 BIOPRO / 膳食 DR1TOT-DR2TOT / 毒物检测模块；KNHANES 官方变量字典 3.4 血液-3.10 眼科-4.x 营养 / 空气污染模块；CHARLS biomarkers.dta；HRS VBS 静脉血）+ GBD 2021 55+ 暴露-结局数据 + 暴露组（exposome）文献框架 |
| 补充名录 | 按需 | executor phase1 依据各库可用性补录（血清维D/血汞按周期核对表、PM2.5 外部监测链接方案）；主名录已录 40 项（2026-10-11） |
| **合计目标** | **≥ 40** | — |

**字段标准**：`flags` 命名遵循 snake_case，从 `domain_playbooks.md` 对应 playbook 的 flag catalog 选取。

### 3.2 EntityB 实体注册表（目标 15+ 条）

（同上结构，`data/seed/entities_b.csv`）

### 3.3 Evidence Base（目标 250+ 条）

**结构**（`data/seed/evidence_chunks.jsonl`）：复用 TongYuan `EvidenceChunk` schema。

**来源优先级**：
1. **Level A**（最高）：监管标签 / 指南（FDA / NMPA / AAO PPP 等）
2. **Level B**：系统综述与 meta 分析
3. **Level C**：原创研究（队列 / RCT / 机制研究）
4. **Level D**：体外 / 动物研究
5. **Level E**：机制推断与竞品文献

> 审核 102：以上为 `src/huiyan_agent/evidence_store.py:21` **实际使用**的定义（检索权重 A5/B4/C3/D2/E1）。
> 截至本版：`configs/rules.yaml` 的 25 条引用中**没有一条是指南**——Level A 的 3 条规则
> （r10/r11/r13）实际都由系统综述 / meta 分析支撑；Level D 从未使用。修订前正文的定义与此不一致。

**PubMed 检索词模板**：
- `(exposom* OR "risk factor*") AND (cataract OR glaucoma OR "macular degeneration" OR retinopathy)`（本项目检索式）
- 中文文献：CNKI / 万方（手工补 20–30 篇）

---

## 4. 规则引擎设计（21 条规则，见 `configs/rules.yaml`）

> 风格沿用 TongYuan `configs/rules.yaml`；但**引擎并非零改动**：暴露×眼病域需要
> `direction`（保护性关联）、`negative_control`（阴性对照）与 `evidence_level`（加载期校验）
> 三个字段，均在 `src/huiyan_agent/risk_rules.py` 中新增。

### 4.1 规则列表（草稿，需 Phase 2 后最终确定）

| # | 规则 ID | 严重度 | 机制 | 触发条件 |
|---:|---|---|---|---|
| 1 | r10_smoking_x_cataract | high | oxidative_stress | entity_a: current_smoking × entity_b: cataract_any |
| ... | | | | |

（完整规则见 `configs/rules.yaml` 与 `docs/rule_rationale.md`）

### 4.2 患者因素规则

- `diabetes` / `hypertension` / `chronic_kidney_disease`：命中即上调一级（见 `configs/rules.yaml` 的 `patient_factor_rules`）
- `elderly`：≥ 65 岁，high 风险信号维持
- ...

### 4.3 规则 YAML 示例

见 `configs/rules.yaml`（scaffold 后生成骨架）。

---

## 5. 基线对比设计

完全复用 TongYuan `run_baselines.py` 的四档对照：

| 方法 ID | 描述 |
|---|---|
| `pure_llm` | 无检索，直接问 LLM |
| `naive_rag` | 关键词检索 + LLM |
| `lightrag` | LightRAG 图索引（无规则） |
| `huiyan` | **完整系统**：规则 + LightRAG + 报告 |

**核心对比指标**（5 项）：
1. High-risk sensitivity
2. High-risk specificity
3. F1
4. Exact 4-level accuracy
5. Cohen's κ

加上检索效率指标：context char count、evidence chunks retrieved、expert Likert。

---

## 6. 验证设计（数据集中心，v3.0 · 四阶段）

详见 medical-agent-planner `references/validation_design.md`。

### 6.0 验证数据集（作者已勾选，≥2）

| 数据集 ID | 角色 | 来源类型 | 来源 | 目标规模 | 金标准方式 | 独立性轴 |
|---|---|---|---|---|---|---|
| dev-exposure-disease-pairs | development | literature | 暴露-眼病机制/流行病学文献池（系统综述+Meta 分析，PubMed 检索式 Phase 2 定稿）+ AAO PPP 风险因素章节 + WHO 视力保护与中国膳食指南 — 与规则库同步构建，仅此集参与规则生成 | 400 | label_guideline | source |
| intval-nhanes | internal_validation | public_database | NHANES 1999-2008 本地原始库（5 周期；暴露：生化+膳食+毒物；结局：VIX 客观视力 / OPXRET 视网膜分级 / VIQ 自报白内障-青光眼-AMD） | 400 | database_outcome | source |
| extval-knhanes | external_validation | public_database | KNHANES 1998-2024 本地全集（独立国家、独立抽样与检查设计；眼科检查 + 生化 + 营养 + 环境模块） | 300 | database_outcome | site |
| extval-cohorts-9 | external_validation | public_database | 9 大老龄队列原始库（CHARLS/HRS/ELSA/SHARE/KLoSA/LASI/MHAS/CRELES/CLHLS；自报眼病结局 + 统一暴露口径；跨国人群） | 120 | database_outcome | population |

构建位置：`data/datasets/<id>/cases.jsonl`（schema 见 `assets/directory_scaffold.md`，provenance 必填）。

### Phase 1：规则一致性测试（数据集：dev-exposure-disease-pairs，n = 400）

**验收**：完整系统在 cases 上达成 100% 一致。

### Phase 2：内部验证（数据集：intval-nhanes，n = 200）

**分配**：High 80 / Medium 60 / Low 50 / Unknown 10

**验收**：sens ≥ 0.70，spec ≥ 0.60，4-level ≥ 0.50。

### Phase 3：外部验证（数据集：extval-knhanes，n = 300）（若无临床合作，跳过并在论文 Limitations 披露）

**关键协作/来源**：需启动新合作（异步）

**验收**：sens ≥ 0.70，spec ≥ 0.80；**并报告泛化落差 generalization gap = 内部指标 − 外部指标**（高危敏感度 gap ≤ 0.10 为优，> 0.10 触发 triage）。

### Phase 4：盲法专家评估（n = 8 cases × 3 experts）—— **未进行**

**原验收标准**：系统-专家 κ ≥ 0.6；Fleiss κ ≥ 0.6。

**实际状态（2026-10-16 据实补记）：该阶段从未开展。**

- 未招募专家、未收集任何评分，**因此没有任何 κ 值**
- `outputs/figures/source_data/figure3_expert_agreement.csv` 中留有明确记录：
  `NOT_COLLECTABLE: 4-expert blind panel was never conducted in this project.
  Fabricating expert ratings would constitute research fraud.`
- 原 figure3 契约（专家一致性）已被 `figure3_rule_evaluation` 取代，
  图 3 改为呈现确证三态结果
- **稿件全文不含 expert / kappa / blinded panel 任何表述**（已 grep 确认），
  故不影响已报告的结论

**对本项目的影响**：四阶段验证中 Phase 1–3 已完成，
Phase 4 缺失意味着**系统输出未经人类专家盲法核验**，
"与专家判断一致性"这一主张**在本项目中无证据支持，不得写入论文**。

**若日后要补做**：需 8 个案例 × 3 位眼科专家、盲法、预先注册评分表与 κ 阈值；
在此之前任何 κ 数值都不得出现在任何产物中。

---

## 7. 项目结构

```
<project_root>/
├── README.md
├── PLAN.md                         # 本文档
├── pyproject.toml
├── .gitignore
├── .env.example
├── .planner.config.json            # Phase 1 调研输出（scaffold 已生成）
│
├── src/huiyan_agent/           # 核心包
│   ├── __init__.py
│   ├── schemas.py
│   ├── normalize.py
│   ├── risk_rules.py
│   ├── evidence_store.py
│   ├── lightrag_adapter.py
│   ├── naive_rag.py
│   ├── llm_client.py
│   ├── safety_agent.py
│   └── report.py
│
├── configs/
│   ├── rules.yaml                  # 规则配置
│   ├── prompts.yaml
│   └── settings.example.yaml
│
├── data/
│   ├── raw/
│   ├── seed/
│   │   ├── entities_a.csv
│   │   ├── entities_b.csv
│   │   ├── evidence_chunks.jsonl
│   │   ├── interactions_gold.jsonl
│   │   └── interactions_layer1_literature.jsonl
│   └── processed/lightrag_index/
│
├── scripts/
│   ├── build_entity_a_registry.py
│   ├── build_entity_b_registry.py
│   ├── fetch_pubmed.py
│   ├── build_evidence_base.py
│   ├── build_lightrag_index.py
│   ├── generate_cases.py
│   ├── run_baselines.py
│   ├── run_multiseed.py
│   ├── evaluate.py
│   ├── generate_paper_figures.py
│   ├── generate_paper_tables.py
│   └── run_demo_cases.py
│
├── app/streamlit_app.py
│
├── tests/
│   ├── test_normalize.py
│   ├── test_risk_rules.py
│   ├── test_evidence_store.py
│   └── test_integration.py
│
├── outputs/
│   ├── figures/
│   ├── tables/
│   ├── paper/
│   └── baseline_predictions.jsonl
│
└── docs/
    ├── data_sources.md
    └── rule_rationale.md
```

---

## 8. 数据源清单（带访问方法）

> 详见 §X.2 数据可及性表的填充版本。每条数据源记录：类型、用途、访问方式、国内镜像、备选。

| 数据源 | 类型 | 用途 | 访问方式 | 国内镜像 |
|---|---|---|---|---|
| NHANES 1999-2008 | 公共数据库 | 暴露（生化/膳食/毒物）+ 结局（VIX/OPXRET/VIQ） | 本地已实测 | E:\...\16.NHANES |
| KNHANES 1998-2024 | 公共数据库 | 暴露（生化/营养/AP）+ 结局（眼科 10 波客观） | 本地已实测（Rdata+字典） | E:\...\11. KNHANES |
| 9 大老龄队列 | 公共数据库 | 暴露（生活方式/部分血清）+ 结局（自报层） | 本地已实测（dta 核验） | E:\...\01-09 |
| GBD 视觉库 | 公共数据库 | 负担/归因背景 | 本地 | E:\...\15/17/18 |
| PubMed E-utilities | 检索 API | 证据池/引用核验 | NCBI key（10 req/s） | 直连+代理均通 |
| AAO PPP（POAG/AMD/DR） | 指南全文 | 规则证据（A 级） | 代理直链下载（已验证） | 见 network_and_proxy.md |
| Crossref + OpenAlex | 引用 API | DOI 双源交叉验证 | 公开 API | 直连 |

---

## 9. 详细任务清单（可执行块）

> 每个 Phase 内的任务尽可能并行；Phase 之间一般有依赖。

### Phase 0：项目初始化（预计 0.5 天）

- [ ] **T0.1** 在 `<project_root>` 初始化 git 仓库
  - verify: `git status` 显示 main 分支
- [ ] **T0.2** 编写 `pyproject.toml`、`.gitignore`、`.env.example`、`README.md`（scaffold 已生成骨架）
  - verify: `pip install -e .` 成功
- [ ] **T0.3** 复制 TongYuan `src/tongyuan_agent/*.py` → `src/huiyan_agent/*.py`，全局替换命名
  - verify: `python -c "import huiyan_agent"` 不报错
- [ ] **T0.4** 运行 `pytest` 确认基线测试通过
  - verify: 所有测试通过

### Phase 1：知识库构建（预计 1.5–2 周，**最大瓶颈**）

**并行 Subagent 任务**：

- [ ] **T1.1** 构建 `data/seed/entities_a.csv`（40+ 条）
  - **Subagent A1（Explore）**：调研 各库原始变量字典（NHANES 生化 BIOPRO / 膳食 DR1TOT-DR2TOT / 毒物检测模块；KNHANES 官方变量字典 3.4 血液-3.10 眼科-4.x 营养 / 空气污染模块；CHARLS biomarkers.dta；HRS VBS 静脉血）+ GBD 2021 55+ 暴露-结局数据 + 暴露组（exposome）文献框架
  - **Subagent A2（Explore）**：调研各暴露项在各库的实测变量名与周期覆盖（NHANES LBXSUA/LBXGL/PBCD 等；KNHANES 官方字典；CHARLS biomarkers/HRS VBS）——已完成（2026-10-11，结果写入 entities_a.csv 的 evidence_sources 列，40 项）
  - **Subagent A3（编码）**：合并为 CSV，手工标注 flags
  - verify: `wc -l data/seed/entities_a.csv ≥ 40`

- [ ] **T1.2** 构建 `data/seed/entities_b.csv`（15+ 条）
  - 同 T1.1 模式

- [ ] **T1.3** 构建 `data/seed/evidence_chunks.jsonl`（250+ 条证据）
  - **Subagent C1（Explore）**：PubMed E-utilities 检索
  - **Subagent C2（Explore）**：FDA DailyMed 抓取
  - **Subagent C3（Explore）**：证据库抓取（PubMed efetch 已落地；指南/监管源**尚未抓取**）
  - verify: 证据级别分布合理；至少 50 条 Level A/B

### Phase 2：规则引擎（预计 3 天）

- [ ] **T2.1** 编写 `configs/rules.yaml`（12 条规则 + 患者因素规则）
  - **Subagent D（Explore）**：为每条规则检索 2–3 篇 PubMed 支持文献
  - verify: YAML 合法；每条规则至少有 1 篇文献支持
- [ ] **T2.2** 运行规则引擎单元测试
  - verify: `pytest tests/test_risk_rules.py` 通过
- [ ] **T2.3** 编写 `docs/rule_rationale.md`
  - verify: 文档完整覆盖所有规则

### Phase 3：检索与基线（预计 1 周）

- [ ] **T3.1** 构建 LightRAG 索引
  - verify: `data/processed/lightrag_index/` 含完整 KV stores
- [ ] **T3.2** 实现四档基线
  - verify: 四种方法在 5 个示例 case 上都能输出报告
- [ ] **T3.3** Naive RAG 测试
  - verify: 经典 high-risk case 能召回关键证据

### Phase 4：验证集构建（预计 1 周）

- [ ] **T4.1** Phase 1 验证集：脚本枚举生成 cases
- [ ] **T4.2** Phase 2 验证集：文献派生 cases
- [ ] **T4.3** Phase 3 临床协作入组（**最早启动，异步进行**）
- [ ] **T4.4** Phase 4 专家盲评包导出

### Phase 5：评估与论文图（预计 1 周）

- [ ] **T5.1** 运行 `scripts/evaluate.py`，输出性能矩阵
- [ ] **T5.2** 生成论文图（架构、性能、检索效率、专家一致性、Demo、推理轨迹）
  - **调用 `nature-figure` skill**，按 **`outputs/figures/contracts/figure{1-5}_*.yaml`** 中的 contract 生成。Contract 由 scaffold 自动 emit（Python backend，NMI pastel palette，600 dpi，SVG+PDF+TIFF+PNG，可编辑文本）。
  - **5 张标准图**：
    - Figure 1 — 系统架构（`schematic_led_composite`）
    - Figure 2 — 性能多 seed（`quantitative_grid`，forest + 混淆矩阵 + metric bar + 效率散点）
    - Figure 3 — 专家一致性（`quantitative_grid`，Fleiss κ + system-vs-expert heatmap + Likert）
    - Figure 4 — Demo case 报告（`image_plate_plus_quant`，input + rules + evidence pyramid + traceability）
    - Figure 5 — 推理轨迹（`schematic_led_composite`，swim-lane + latency + KG path network）
  - 每张图必须附 `outputs/figures/source_data/figure{N}_*.csv`（YAML contract 中已声明 schema）
  - 后端锁定 **Python**（matplotlib + seaborn + networkx），不混用 R
  - 配色锁定 **NMI pastel**（色盲安全，CMYK 友好）
  - verify: `ls outputs/figures/figure{1-5}_*.{svg,pdf,tiff,png}` 共 20 个文件
- [ ] **T5.3** 生成论文表（注册表、规则、性能、验证分布）

### Phase 6：交互式界面（预计 2–3 天）

- [ ] **T6.1** 复用并改写 TongYuan `streamlit_app.py`
  - verify: `streamlit run app/streamlit_app.py` 启动；demo case 返回正确报告

### Phase 7：论文写作（预计 2–3 周）

> **Nature skill 编排**：本阶段大量调用 `nature-*` skill 完成 Nature 风格稿件生产。

- [ ] **T7.1** 论文大纲（IMRaD）—— 用 `nature-writing` 选定 article architecture
- [ ] **T7.2** Methods —— 用 `nature-writing` 起草，复用 TongYuan 方法节，按域改写
- [ ] **T7.3** Results（基于 Phase 5 数据）—— 用 `nature-writing` evidence ladder
- [ ] **T7.4** Introduction —— 用 `nature-citation` 给段落补 CNS 引用 backbone；用 `nature-reader` 深读 3–5 篇 cornerstone 引用做中英对照
- [ ] **T7.5** Discussion —— 用 `nature-writing` 中心贡献 + 证据意义 + 与前人关系 + 限制 + 未来
- [ ] **T7.6** 每节定稿后用 `nature-polishing` 润色（含中文初稿翻译）
- [ ] **T7.7** Data Availability 节用 `nature-data` 起草（GitHub + Zenodo + 数据源 + LLM provider）
- [ ] **T7.8** Highlights + Graphical Abstract + Cover Letter
- [ ] **T7.9** Supplementary

### Phase 8：投稿准备（预计 3–5 天）

- [ ] **T8.1** 按目标期刊格式调整
- [ ] **T8.2** 参考文献整理（Vancouver / Harvard / MDPI）—— 用 `nature-academic-search` 验证 DOI 和元数据
- [ ] **T8.3** GitHub 仓库整理 + Zenodo DOI
- [ ] **T8.4** Cover letter + CRediT + 数据可用性声明（T7.7 已起草）

### Phase 9：修回（投稿后，预计 1–4 周，按 major/minor revision 决定）

> **Nature skill 编排**：用 `nature-response` 处理 editor decision letter。

- [ ] **T9.1** 解析 editor decision letter + reviewer comments，建立 R1.1/R1.2/R2.1 编号
- [ ] **T9.2** 用 `nature-response` 起草逐点回复（response strategy + tracker table + draft letter）
- [ ] **T9.3** 按回复信承诺修改 manuscript，记录 line/figure/table 变更
- [ ] **T9.4** 补做 reviewer 要求的实验/分析（如适用）；不能做的标 `AUTHOR_INPUT_NEEDED`
- [ ] **T9.5** 重投 + 更新 cover letter

### Phase 10（可选）：会议汇报

- [ ] **T10.1** 用 `nature-paper2ppt` 把 manuscript 转成中文 PPTX（12–16 页，16:9）
- [ ] **T10.2** QA report + asset manifest

---

## 10. Subagent 并行策略

### 10.1 Subagent 类型选择

| 任务 | Subagent 类型 | 数量 | 并行度 |
|---|---|---:|---|
| 文献调研（数据库/监管源/政策） | `Explore` | 4–6 | 高 |
| 数据抓取与整合 | `Explore` + 编码 | 2–3 | 中 |
| 代码迁移与改写 | 默认（编码） | 1 | 低（顺序） |
| 规则依据文献检索 | `Explore` | 1 | 中 |
| 验证用例构建 | `Explore` | 3 | 高 |
| 论文章节撰写 | 默认 | 1（顺序） | 低 |

### 10.2 关键并行机会

**机会 1：知识库三件套同时构建**（Phase 1）
**机会 2：四档基线 + 评估流水线**（Phase 3 完成后）
**机会 3：论文章节并行初稿**（Phase 5 完成后）

---

## 11. 时间线（乐观估计）

| 周 | 主要工作 |
|---:|---|
| 1 | Phase 0 + Phase 1 启动 |
| 2 | Phase 1 完成 + Phase 2 规则 |
| 3 | Phase 3 检索与基线 |
| 4 | Phase 4 验证集构建 |
| 5–6 | Phase 5 评估 + Phase 6 Streamlit |
| 6 | **联系临床团队启动 Phase 3 临床病例收集**（异步） |
| 7–9 | Phase 7 论文写作 |
| 10 | Phase 8 投稿准备 |
| 11–25 | 内审 + 投稿 |

**关键路径**：Phase 1（数据）→ Phase 3（检索）→ Phase 5（评估）→ Phase 7（写作）。
**异步任务**：Phase 4.3 临床病例收集（最长，需 IRB + 临床团队配合，应最早启动）。

---

## 12. 目标期刊与投稿策略

### 12.1 一志愿：*Ophthalmology（IF 8+ 档候选；Phase 2 期刊适配检查后最终锁定）*

**适配理由**：
- 主题范围包含该研究方向
- 接受方法学 + 决策支持系统类稿件

**Special Issue 关注**：留意相关专刊征稿

### 12.2 备选

| 期刊 | IF | 适配点 | 风险 |
|---|---:|---|---|
| JAMA Ophthalmology | ~8 | 筛查/预测系统类持续发表（121 篇/24 月；视网膜图像 DL 预测全身病 2026） | 同族 jingming 同刊在投——cover letter 明示区分（围术期禁忌 vs 暴露组-眼病筛查） |

### 12.3 投稿顺序策略

1. 投 *Ophthalmology（IF 8+ 档候选；Phase 2 期刊适配检查后最终锁定）* → 若 reject 转 *JAMA Ophthalmology*
2. 若再 reject → *British Journal of Ophthalmology* 兜底

---

## 13. 风险与缓解

| 风险 | 概率 | 缓解 |
|---|---|---|
| 主名录数据获取难 | 中 | 多源核对（监管公告 + 已发表论文） |
| 临床病例收集周期长 | ... | ... |
| 临床病例收集周期长（IRB + 协调） | 高 | 尽早启动；先用文献验证支撑投稿 |
| 与已有工作重复 | 中 | Introduction 明确区分；规则、数据、目标人群全不同 |
| PubMed 检索召回率低 | 低 | 与文献管理员合作；中英文双查 |
| LightRAG 索引内存不足 | 低 | 复用 TongYuan 索引配置；分批构建 |
| 专家盲评协调难 | 低 | 复用既有专家网络 |

---

## 14. 执行入口

**Claude 开始执行时的标准流程**：

```
1. 读取本 PLAN.md（已完成）
2. 检查 git status & 当前文件树
3. 按 Phase 顺序执行（见 §0 与 §9）
4. 每完成一个 Phase 更新 TodoWrite
5. 关键节点（如数据构建完成、评估完成）通知用户确认
```

**Claude 启动命令**（用户在与 Claude 的下一轮对话时使用）：

> 请按 `<project_root>/PLAN.md` 执行 Phase 0，然后启动 Phase 1 的三个并行 subagent。

或更精细：

> 请执行 `<project_root>/PLAN.md` 的 T0.1–T0.4，verify 全部通过后停下来等我审查。

---

## 15. 附录：关键文件草稿

### 15.1 `pyproject.toml`

见 scaffold 生成的实际文件。

### 15.2 实体清单采样（写入 README）

（待 Phase 1 完成后填充）

### 15.3 论文标题（候选）

1. 慧眼: a rule-based decision support framework for 暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证 screening
2. Development and validation of a knowledge-graph-augmented 暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证 screening system
3. A pharmacological rule-based clinical decision support system for 暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证

---

**PLAN.md v1.0 — 2026-10-11**（由 medical-agent-planner skill 生成）

---

## 16. 执行日志 / Progress Log

| 日期 | 事件 | 操作者 |
|---|---|---|
| 2026-10-11 | PLAN.md v1.0 创建，项目立项 | medical-agent-planner skill |
