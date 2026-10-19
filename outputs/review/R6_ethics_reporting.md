# R6 报告规范与出版伦理审查报告

**审查对象**：`outputs/paper/manuscript.md`（v1.2，2026-10-15 18:45 落盘）及其章节原稿、投稿包
**审查角色**：报告规范（STROBE / TRIPOD+AI / DECIDE-AI）与出版伦理（伦理声明 / 数据与代码可得性 / 利益冲突 / 资助 / CRediT / 预注册真实性）
**审查日期**：2026-10-15
**核心准则**：伦理缺失一票否决；预注册真实性为本次最高优先级核查项。

**本次实际读取的材料**：
`outputs/paper/manuscript.md`（1104 行）、`outputs/paper/sections/{abstract,introduction,methods,results,discussion}.md`、
`docs/analysis_plan.md`（602 行，含 §19）、`docs/cohort_variable_mapping.md`、
`outputs/paper/citation_pool.json`、`outputs/submission/package_manifest.json`、
`outputs/submission/journal_guidelines_snapshot.md`、`outputs/submission/supplementary_material.md`、
`outputs/cohorts/*`（`cohort_transportability.json`、`cohort_meta_summary.csv`、`cohort_influence.csv`、`cohort_power.csv`、`evidence_audit.json`、`RESULTS_COHORT.md`）、
`outputs/paper/manuscript_R11.md`（内部分析版本，仅用于核对声明是否被回退），以及 git 版本库状态。

---

## 总体评价

这是一篇方法学上有真东西、诚信建设意识明显强于同类稿件的研究（三层证据、双精度口径、三态标准、效能与中介齐备，评论区甚至主动把"标准过于宽松"当作结果报告），**但其对外声明层存在系统性塌陷**：现行稿件（`manuscript.md`）**完全没有伦理声明、没有数据可得性声明、没有代码可得性声明、没有资助声明**——而上一版内部稿 `manuscript_R11.md` 第 248–260 行原本是有一个 `## Declarations` 区块的（含伦理、数据、代码三项），本版在扩层时被整体丢弃且未补回。以本刊（Ophthalmology）与任何 ICMJE 期刊的送审门槛衡量，这属于**形式审查即退稿**的缺陷，与科学质量无关，但足以让稿子根本不进入学术评审。

第二处系统性问题在预注册。核查结论（详见专节）：§19 **确实**在运行前冻结了五项被声明的要素（可检验规则集 6 条/18 对、逐队列 BMI 主切点、协变量集、三态判定定义、可迁移性判据），文件级时序（§19 mtime 17:32:27 ← 队列运行 17:33:14 → 结果 17:34:19）与"先于运行"自洽；但**该声明在版本库中不可证**——`HEAD`（2026-10-12 提交）里的 `analysis_plan.md` 在第 11 节就结束了，§12–§19 全部是未提交的工作区内容，且 §12/§13/§15 都已**自行披露**"落盘先于运行的声明无独立可证证据（无预运行 git 快照）"并主动降格，**唯独 §19 没有这句披露，而稿件恰恰只依赖 §19 的"pre-registered"**。更关键的是，稿件摘要与结果中承担核心论证的四项分析（随机效应合并与预测区间、地区亚组检验、留一队列法、E 值）**在 §19 中完全不存在**，其产物时间戳（18:31–18:36）晚于结果（17:34）——它们是标准的**事后分析**，却被摘要写进了"a pre-registered three-state standard … but both had I² above 90% and prediction intervals spanning unity"这一句的同一逻辑层级里。

**投票：大修（Major Revision）。** 无致命项（无造假、无数据冲突、无伦理违规——本研究确实使用公开去标识化数据、确可豁免，问题在于**没写**而非**做了不该做的**），但有三项独立的"重大"（伦理/知情同意、数据可得性、代码可得性——均为一票制门槛项）与一项"重大"（预注册表述的事后分析越界），必须在送审前逐项补齐；补齐后本稿的核心结论（合并掩盖方向冲突、限制因素是测量而非样本量）是站得住的，且比多数"跨队列复现"稿件更有信息量。

---

## 伦理与声明审查（逐项）

### 1. 伦理声明 —— **重大（缺失）**

- **位置**：`manuscript.md:124–143`（Methods §Reporting and study design，全段）；全稿无独立 Declarations/Back matter 区块。
- **问题**：全稿**没有任何伦理声明**。唯一相关句为 `manuscript.md:130–131`："No participant was contacted and no intervention was administered; all analyses used de-identified public data."——这是**对研究性质的描述，不是伦理声明**：它既未说明**豁免依据**，也未说明**由谁判定**豁免，更未说明**各队列原始研究是否已获伦理批准**及是否取得原始知情同意。作为对照，被本版取代的 `manuscript_R11.md:250` 有一句合格的表述（"Each source obtained its own ethics approval and informed consent; no new data were collected, and no further ethical approval was required."），说明这不是能力问题而是**扩层时的区块丢失**。
- **为什么是问题**：（1）ICMJE 与 Elsevier/AJO/Ophthalmology 系均把 ethics statement 列为投稿必填项，缺失通常**在编辑初审阶段即被退回**，不进入同行评审，因此这条不是"审稿意见"而是"送不出去"；（2）稿件的研究范围在本版已从 3 个数据库扩至 **11 个数据库、8 个原始队列、2.0 million person-wave**（`manuscript.md:16–22`、`:157–168`），比 R11 版宽得多，数据使用条件也比 R11 版复杂得多（SHARE 有 `gv_*` 官方派生件、MHAS 有官方插补件、CLHLS 有 80+ 高龄人群的敏感信息），此时沿用旧声明尚且不够，何况没有；（3）本刊审稿人会直接问"SHARE 的访问需要签署数据使用协议，你们遵守了吗"——数据可得性声明（下一条）与伦理声明在方法学上是同一个问题的两面，两条同时缺失会让审稿人无法排除**数据来源合规性风险**，这是最重的一档怀疑。
- **具体修改建议**：在 Limitations 之后、References 之前新增 `## Declarations` 区块，逐条写入：
  1. **Ethics approval and consent to participate**：明确写出"本研究为对**已去标识化、公开可得**的既有队列数据的二次分析（secondary analysis of de-identified, publicly available data）；**未接触任何受试者，未采集任何新数据**；因此依据 [适用辖区，如 45 CFR 46.104(d)(4) 或本地伦理委员会规则] **不属于需伦理审查的人体受试者研究，豁免伦理审查（exempt）**；该豁免判定由【作者单位伦理委员会名称 / 作者本人并说明依据】作出"——**豁免依据与判定主体二者必须都写**（这是审稿人真正会核对的两处）。
  2. **各源队列的原始伦理批准**：逐队列一句话声明"each participating cohort obtained its own ethics approval and written informed consent from its participants; the present analysis used only the de-identified data releases distributed by each study"。11 个来源（SHARE/HRS/ELSA/KLoSA/LASI/MHAS/CLHLS/CRELES/NHANES/KNHANES/CHARLS）逐一列出，避免"等"字。
  3. **Consent for publication**：N/A 或 "Not applicable"。
  4. 若本刊（Ophthalmology）要求，同步在 cover letter 中重述豁免依据——编辑常先读 cover letter 判断是否送审。

### 2. 知情同意 —— **重大（缺失，与上条同源）**

- **位置**：同上；全稿无 "informed consent" 字样（`outputs/paper/` 下仅 `manuscript_R11.md:250` 出现过）。
- **问题**：二次分析通常**不需要新的知情同意**，但必须在文中**说明为什么不需要**（原始队列已获同意 / 已去标识化 / 数据以聚合形式使用）。现行稿件对此零表述。
- **为什么是问题**：老年队列（尤其 CLHLS 的 80+ 高龄、MHAS 的低教育人群）是可识别的敏感人群，审稿人对"谁同意了什么"的容忍度很低；"没说"会被读成"没想过"。
- **具体修改建议**：在伦理声明第 1 条内附一句 "No additional informed consent was required for this secondary analysis because the data were obtained de-identified from the original studies' approved data-access mechanisms, and the original studies obtained informed consent from all participants." 并在数据可得性声明中写明各数据使用协议（DUA）的签署情况。

### 3. 数据可得性 —— **重大（缺失且无路径）**

- **位置**：`manuscript.md:124–278`（Methods 全章）；`:272–278`（§Software and reproducibility）；`supplementary_material.md` 全篇。全稿**没有 Data availability 声明**。
- **问题**：稿件在 `:157–168` 列出 8 个队列、在 `:170–178` 说明"仅用原始文件、排除 harmonised 版本"，但**通篇没有一处告诉读者到哪里、以什么条件、如何取得这些数据**。最接近的是 `:276–278` "Rule definitions, cohort variable maps and every correction applied to them are version-controlled in the repository"——这是**代码与台账**的可得性，不是**数据**的，且连仓库地址都没给。`supplementary_material.md:5` 也只说"每件产物由某脚本生成"，同样回避数据入口。
- **为什么是问题**：（1）本研究的**全部**工作量与**全部**可复现性都建立在"从原始文件重建 8 个队列 frame"之上，而这 8 个队列中**没有一个是即时可下载的**——SHARE 须在 SHARE Research Data Center 注册并签署 DUA、HRS 须在 hrs.isr.umich.edu 注册、ELSA 须通过 UK Data Service 注册（且需 UK 机构或特殊许可）、KLoSA 须向韩国雇佣情报院（KEIS）申请、LASI 须经 IIPS/LASI 门户审批、MHAS 须在 MHAS 网站注册、CLHLS 须向北京大学 CLHLS 项目组申请、CRELES 须经 ICPSR 或哥斯达黎加大学（UCR）/CCP 申请。不写清这 8 条路径，"可复现"就只是**声明**而非**事实**，这是本稿最实质的可复现性缺口。（2）泛泛一句"数据可向原研究申请"同样是重大缺口（用户审查清单已明确这一点）；（3）稿件还刻意排除了 Gateway/easySHARE/RAND 派生版（`:170–178`，`analysis_plan.md:458–463`），审稿人必须知道**作者用的是哪一套文件命名与位置**，否则无法判断"raw source files only"到底指什么——这条纪律只有在数据声明里点名文件族（如 SHARE `gv_*`、MHAS `Constructed Data/_Creadas`、HRS `HXXC_R.dta`）才可执行。
- **具体修改建议**：新增独立 `## Data availability` 段，用**逐队列可执行表**取代散文，例如：

  | 来源 | 获取入口（可执行） | 访问条件 | 本分析使用的文件族 |
  |---|---|---|---|
  | SHARE | http://www.share-project.org/data-access.html（SHARE Research Data Center，注册 + DUA） | 免费注册；需机构邮箱 | release 版本原始模块 + 官方 `gv_*`；未用 easySHARE |
  | HRS | https://hrs.isr.umich.edu/data-products（注册后下载） | 免费注册 | `HXXC_R.dta` 等原始波文件；未用 RAND Fat File |
  | ELSA | https://beta.ukdataservice.ac.uk/datacatalogue/series/series?id=200011（UK Data Service，End User Licence） | 注册 + EUL | wave 3 原始模块 |
  | KLoSA | https://survey.keis.or.kr/（韩国雇佣情报院，申请制） | 申请审批 | 波 1–8 核心文件；未用 `_CN`/harmonised |
  | LASI | https://lasi.hsph.harvard.edu/ 与 IIPS 数据门户（申请制） | 申请审批 | wave 1 个体文件 |
  | MHAS | https://www.mhasweb.org/（注册后下载） | 免费注册 | `sect_*` 原始波文件 + 官方 Constructed/Imputation 件 |
  | CLHLS | 北京大学 CLHLS 项目组（http://opendata.pku.edu.cn 相关入口，申请制） | 申请审批 | 1998–2018 CSV + 官方码本 |
  | CRELES | ICPSR 研究 26681（DOI 10.3886/ICPSR26681.v2）与 UCR/CCP | 注册/申请 | `DS1*.dta`、`DS10_Recoded_Variables` |
  | NHANES / KNHANES / CHARLS | 公开下载入口（CDC / KDCA / 北大 CHARLS） | 完全公开 | 见 R11 版声明 |

  表后补一句 "No data are shared by the authors; all analytic frames are regenerated by the scripts in `scripts/` from the above releases, and the exclusion of harmonised/derived releases is documented in the supplement (S1)." 这既满足 FAIR，也把"仅用原始文件"这条纪律**变成可检验的**。
- **说明**：以上链接与访问条件需作者**逐一实测后**再写入（本人未联网核实，仅依据各队列公开的常规入口；写错入口比不写更糟）。

### 4. 代码可得性 —— **重大（缺失）**

- **位置**：`manuscript.md:272–278`。
- **问题**：`:272–278` 只说"Rule definitions, cohort variable maps and every correction applied to them are version-controlled in the repository, and each figure and table is generated from a single declared source file"，**从未声明"分析代码可得"，也从未给出仓库/DOI/链接**。`supplementary_material.md:7–16` 的 S1–S8 表列出了脚本名（`scripts/cohort_power.py` 等），这是全稿最接近代码可得性的地方，但（a）它在投稿包中是否随稿提交未知，（b）该表只覆盖 8 个脚本，**未覆盖重建 8 个队列 frame 的核心脚本**（`scripts/build_cohort_frames.py`、`scripts/cohort_confirmatory.py`、`scripts/detect_exposure_gates.py`、`configs/rules.yaml`、`configs/variable_map.yaml`、`scripts/cohort_heterogeneity.py`）。
- **为什么是问题**：本项目 `scripts/` 下确有全部脚本，代码可得性的实现成本**为零**，缺失纯属遗漏；但缺了它，审稿人无法验证本稿最关键的三件事——frame 是怎么建的、门槛审计是怎么过的、`cohort_heterogeneity.py` 的 REML 与预测区间是怎么算的（Table 5 自己承认"no external meta-analysis package was used"，那就更需要代码）。这是典型的"低成本高损失"缺陷。
- **具体修改建议**：新增 `## Code availability` 段，给出（i）代码归档（GitHub 公开仓库 + Zenodo DOI 永久归档，建议随文提交 `code_v1.2.zip` 作为附件），（ii）入口脚本清单（`scripts/build_cohort_frames.py` → `scripts/detect_exposure_gates.py` → `scripts/cohort_rule_coverage.py` → `scripts/cohort_confirmatory.py` → `scripts/cohort_heterogeneity.py`/`cohort_power.py`/`evidence_base_audit.py` → 图表脚本），（iii）运行环境（`manuscript.md:274` 只写 "Python 3.10 with pandas, statsmodels and SciPy, and R 4.6.1 with the survey package"——**缺版本号与锁定文件**，建议补 `requirements.txt`/`renv.lock` 哈希与 R survey 版本），（iv）`docs/analysis_plan.md` 的**冻结版本哈希**（本稿反复引用"§19 预注册"，冻结哈希是让该声明可核验的最低成本手段）。

### 5. 利益冲突 —— **重大（缺失）**

- **位置**：全稿无 Competing interests / Conflict of interest 字样（`manuscript_R11.md:258` 原有 "None declared."，本版丢失）。
- **问题**：完全没有声明。
- **为什么是问题**：ICMJE 统一要求把 COI 声明作为稿件组成部分，Elsevier 系在投稿系统中单独收集且**正文通常也要求出现**；缺失会被编辑当作"未披露"而非"无冲突"处理，性质完全不同。本稿还声明了系统组件涉及 LLM 供应商（`manuscript.md:711` DeepSeek 主客户端、本地 qwen3.8-27b 微调？——见 `analysis_plan.md:82`），且研究的核心命题是"LLM/RAG 架构在临床决策支持中的价值"（`:264–271`、`:478–485`），**厂商关系属于必须披露的类型**。
- **具体修改建议**：新增 `## Competing interests`，若有供应商资助/算力支持/API 免费额度必须写明（含金额无关的实物支持），否则写 "The authors declare no competing interests."；同时说明 LLM 供应商对研究设计、数据分析、结论与稿件撰写**无任何参与**（这是本领域审稿人必问）。

### 6. 资助 —— **重大（缺失）**

- **位置**：全稿无 Funding 字样（`manuscript_R11.md:256` 原有 `**Funding.** *[to be completed]*`——即**从未填过**，本版连占位符都不再出现）。
- **问题**：没有任何资助信息，包括"无资助"这一结论本身。
- **为什么是问题**：（1）资助声明一旦缺失，审稿人无法评估**数据访问成本**（8 个队列的申请与算力开销不小）与研究独立性；（2）本稿包含 LLM 推理实验（`analysis_plan.md:82`、`:328–330` 的 4 基线 × 5 seeds × 多轮重跑），若使用了机构算力或商业 API 额度，属于必须披露的资源支持；（3）**注意本版比 R11 版更糟**：R11 至少留下了一个会被编辑一眼看到的 `[to be completed]` 占位符，本版删除占位符后，缺失在形式上变成了"作者选择不声明"，风险更高。
- **具体修改建议**：`## Funding` 段写明基金编号与资助方角色；无资助则写 "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. Data access fees were covered by [机构/自筹]。" 若 LLM API/算力由机构或商业方提供，一并列入。

### 7. 作者贡献（CRediT） —— **重大（缺失）+ 需特别说明（agent 主导）**

- **位置**：全稿无 Author contributions / CRediT 字样（`manuscript_R11.md:260` 原有 `*[to be completed]*`，同样从未填写，本版丢失）。
- **问题**：没有作者名单、没有 CRediT 分工、没有通讯作者与责任声明。**并且本项目的特殊性使这一点不能按常规处理**：本研究的规则库提炼、队列 frame 重建、门槛审计、统计运行、图表生成、稿件撰写与修订，是由一个 agent 主导的流水线完成的（`outputs/submission/supplementary_material.md:7–16` 的 S1–S8 逐项标注"Produced by scripts/…"；`docs/analysis_plan.md` §0–§16 记录了大量由 agent 自查发现并更正的错误，如 C36/C41/C46/C51/C67/C69）。
- **为什么是问题**：（1）ICMJE 明确 **AI/LLM 不能作为作者**，也不能承担"对研究完整性负责"的义务（accountability），因此**必须有一个具名人类作者承担全文责任**，否则稿件在伦理上无法成立；（2）本项目实际发生过一类恰好需要人类责任兜底的错误——`analysis_plan.md:14` 承认 **test-set fitting**（确证运行后修改规则再在同一测试集评估）、`:667–673` 的 C67 与 `:724–732` 的 C69 是 agent 自己的批量正则操作造成的事故、`:564–572` 的 C64 是映射错误被门漏检 1,499 人。这些**都被如实记录并修正了**，是加分项；但也正是这些记录说明：**必须有一位人类作者确认"我审阅并认可全部修正"**，否则读者无从判断这些自查结论是否经过人类独立判断。（3）多数期刊现已**强制要求**披露生成式 AI 在写作/分析中的使用范围（Elsevier、Nature、JAMA、BMJ 系均有专门政策），不披露属于失范。
- **具体修改建议**（直接给出可用的三段式）：
  1. **Authorship**：列出具名作者（含 ORCID），通讯作者承担 "the corresponding author affirms that all authors meet ICMJE criteria and take public responsibility for the integrity of the data, the analysis, and the manuscript"。**禁止**把 agent、脚本或 LLM 列为作者。
  2. **CRediT authorship contribution statement**（逐人）：Conceptualization / Methodology / Software / Validation / Formal analysis / Investigation / Data curation / Writing – original draft / Writing – review & editing / Visualization / Supervision / Project administration / Funding acquisition。**特别建议**：由人类第一作者显式认领 **Validation**（独立复核 §0 记录的全部更正与偏离）、**Supervision**、**Writing – review & editing** 三项，这是"人类责任兜底"最直接的落点。
  3. **Use of AI / automated tools（必须新增的一段）**：写明（i）使用了什么（规则库构建、代码生成、统计运行、图表渲染、初稿起草的 agent 流水线；以及本地 qwen3.8-27b / DeepSeek 作为系统组件与文献抽取器）；（ii）人类做了什么（设计分析计划、批准协议偏离与更正处置、裁定争议方向判定、审阅全部输出）；（iii）**"All AI-assisted outputs were verified by the authors, who take full responsibility for the content."** 一句不可省。可附一行说明 agent 自查记录（`docs/analysis_plan.md` §0 的更正 1–18、`docs/cohort_variable_mapping.md` 的 C19–C69）已作为补充材料公开——**这实际上是把本项目最强的诚信资产转成了审稿人的信任来源，建议主动写**。

### 8. 附带：上一版声明区块的回归（次要但需处理）

- **位置**：`manuscript_R11.md:248–260` vs `manuscript.md`（全文）。
- **问题**：R11 版的 `## Declarations` 至少含 Ethics / Data availability / Code availability / Competing interests 四项（Funding 与 Author contributions 为占位符），本版**四条已写内容一并消失**，且 `outputs/paper/manuscript_assembly_manifest.json`（`:4–35`）把稿件拆成 abstract/introduction/methods/results/discussion/legends 六节——**没有任何一节的名称是 declarations**，说明这不是"漏粘贴"，而是**组装模板里根本没有声明槽位**。
- **修改建议**：在 `manuscript_assembly_manifest.json` 中新增 `declarations` 一节，并把 `outputs/submission/package_manifest.json` 的 `files` 里加 `declarations.md`；同时给 `journal_guidelines_snapshot.md:33–39` 的"To verify before submission"补第 6 项（伦理/数据/代码/COI/资助/CRediT 六项声明是否齐备）——目前该清单只关心字限、图表上限与参考文献格式，**完全没有把声明项纳入核查**，这正是本次塌陷能发生的原因。

---

## 报告规范逐条对照

### A. STROBE（22 条，观察性研究）

判定基准：以稿件正文（`manuscript.md` 及章节原稿）为唯一依据；"部分"= 有内容但规范要件不足。

| # | STROBE 条目 | 判定 | 位置与缺口 |
|---|---|---|---|
| 1 | 标题与摘要：设计类型、可推广性 | **部分** | 标题 `:1` 有 "cross-cohort evaluation"；摘要 `:9–43` 结构完整（Background/Methods/Results/Conclusions），但**未提伦理豁免、未提注册信息**（注册号/落盘日期）。STROBE 明确要求摘要给出"注册信息"。→ 补一句 "The cohort-layer protocol was frozen before analysis (analysis plan §19, dated 2026-10-15); the study was exempt from ethics review (see Declarations)." |
| 2 | 背景/理由 | **符合** | `:49–86`，含 exposome 概念与规则迁移问题，文献引用与结论范围匹配。 |
| 3 | 目的/假设 | **符合** | `:88–96` 明确"which individual rules survive transport"。 |
| 4 | 研究设计 | **部分** | `:124–143` 说明"retrospective, multi-cohort evaluation"与四层结构；但**未说明各队列层的时间性质是横断面还是纵向混合**（实际 8 队列多数多波、暴露多为横断面，见 `:656–659` 的 Limitations 才提到）。→ 在 Methods 首段直接写明 "exposure was predominantly cross-sectional within wave"。 |
| 5 | 场所/时间/相关日期 | **部分** | `:157–168` 有队列名与合计 person-wave，但**未给各国队列的波次与年份**（这些信息在 `analysis_plan.md:471–480` 的表格里完整存在：SHARE 4/5/6/7/9、HRS 2010/2016、KLoSA 1/2/4/6/8、LASI 1、MHAS 1/3/4/5/6、CLHLS 1998–2018、ELSA 3、CRELES 1/2）。**建议把该表直接搬进正文 Methods**——这是 STROBE 第 5 条的核心内容，也是审稿人判断"暴露时序"的唯一依据。 |
| 6 | 参与者：合格标准、来源、纳入方法 | **部分** | `:180–212` 说明"codebook-verified operationalisation"、两级 prevalence gate、门槛审计；但**没有给出各队列自身的纳入/排除标准**（年龄下限？各波是否限制 50+？重复波次的个体如何贡献？）。`analysis_plan.md:377` 只对 CHARLS 写了 "age≥45"。→ 补简表：每队列 n、人数、年龄范围、波数。 |
| 7 | 变量：结局、暴露、混杂、效应修饰 | **符合** | `:215–227`（结局/暴露）、`:180–212`（操作化纪律）、`:242–248`（协变量 age/sex + wave FE）；效应修饰（地区、年龄）在 `:381–412`。 |
| 8 | 数据来源/测量 | **符合（较优）** | `:180–212` 的门槛审计、C1 类错误（条件题）处置、"矫正后视力"构念声明，质量高于一般观察性研究。 |
| 9 | 偏倚 | **部分** | Limitations `:651–655`（自报漏报、医疗可及性混杂）与 `:640–649`（与文献不独立）都有，质量高；但**缺"选择偏倚/幸存者偏倚"作为独立条目**——它是本稿核心解释之一（`:530–542`），却只出现在 Discussion 里，Methods 未声明如何评估。→ 在 Methods 加一句分析方法（本稿已有 meta-regression 与 LOO，见 `:401–412`，补个交叉引用即可）。 |
| 10 | 研究样本量的确定 | **部分** | `:253–260` 与 `:451–474` 是**效能**分析，规范且出色；但 STROBE 问的是**样本量如何确定**。本层样本量由数据可得性决定（非功效驱动），应**明说**："No a priori sample-size calculation was performed; the cohort layer includes all cohorts for which the pre-specified rule-relevant variables were reconstructible, and minimum detectable effects are reported per pair (Table 6)." 这句话一写，"样本量"这一条反而比多数稿件更强。 |
| 11 | 定量变量处理 | **符合** | 二分 flag 主分析（`:223–227` BMI 切点预声明 + 敏感性）+ 连续暴露剂量反应（`:775–781`、Figure 6）。 |
| 12 | 统计方法：主要分析 | **部分** | `:240–254` 完整（within-cohort logistic、wave FE、个体聚类、Rubin、BHY 双家族、Clopper–Pearson）。**但 meta 分析（REML τ²、Q、I²、预测区间）与 E 值在 Methods 中无对应方法段**——它们只出现在 Results（`:373–412`）与 Discussion（`:577–592`），且 Table 5 括注承认是自实现。→ 在 Methods 新增 `## Between-cohort synthesis` 子段，写明 REML 估计、预测区间构造、亚组检验与 E 值公式来源（并引 C026/C027）。**同时必须声明这些是事后分析**（见预注册专节）。 |
| 13 | 统计方法：亚组/交互 | **部分** | 地区亚组（`:381–394`）、年龄 meta-regression（`:401–404`）结果有，**方法学预声明没有**（§19 无此内容）。同 12。 |
| 14 | 统计方法：敏感性分析 | **符合** | 切点敏感性（`:226`）、BHY 双家族（`:250–254`）、LOO（`:411–412`）、连续暴露（Figure 6）。 |
| 15 | 统计方法：失访处理 | **部分/不适用** | 多波设计下"失访"实质存在（个体贡献 1–8 波不等），但稿件只写了"clustered by participant"（`:246`），**未说明各波个体的存活/退出如何影响估计**。→ 补一句"waves were analysed as repeated observations clustered by participant; no attrition weighting was applied, and the number of contributing waves per participant is reported in supplement S2/S6"。 |
| 16 | 统计方法：缺失数据 | **部分** | SHARE 五副本 Rubin（`:246–248`）说明清楚；但 **BMI 的插补（MHAS `bmi_imp`、SHARE/KLoSA 插补产物）在正文未提**（`analysis_plan.md:584` 明确"SHARE/KLoSA/MHAS 的 BMI 为插补产物"，`cohort_variable_mapping.md` C49 亦列明）。CLHLS 因无身高被排除也只在 `analysis_plan.md:584/588`。→ 在 `:223–227` 后补一段缺失数据与插补说明（含"仅实测值"敏感性是否执行）。 |
| 17 | 其他分析 | **部分** | 探索性扫描（`:439–449`）已明确标"exploratory only"，态度正确；但地区亚组与 E 值未标 post hoc。见预注册专节。 |
| 18 | 描述性数据 | **部分** | Table 6（`:1054–1073`）给了每对的 n、暴露率、结局率，质量好；**缺个体层面的基线特征表**（各队列 age/sex/结局分布的汇总表）。Table 1/4 只是注册表与计数。→ 建议补 Table S9 或正文表：逐队列 n、人数、平均年龄、女性比例、结局阳性率。 |
| 19 | 结局事件数 | **符合** | Table 6 的 `outcome_prevalence_unexposed` 与 n 可直接算事件数；Table 7 给出 modality 可行性。 |
| 20 | 主要结果：估计值与精度、混杂调整 | **部分** | 全部 OR 带 95% CI + q 值 + 三态，精度报告优秀；**缺未调整估计**（STROBE 建议同时给粗估与调整后估计，以便读者判断调整的影响）。→ 在补充材料加未调整 OR 列，成本极低。 |
| 21 | 其他分析 | **部分** | LOO / meta-regression / E 值都在，**但均未标 post hoc**；且 LOO 报告与源数据冲突（见后文"致命/重大"第 3 条）。 |
| 22 | 关键结果总结、局限、解释、可推广性 | **部分** | Limitations `:638–672` 分条完整、坦率（含"与文献不独立"这一最重要的局限），Discussion 解释克制、明确拒绝择优解释（`:568`）；**缺口**：（a）局限未涵盖"异质性感知判据为事后追加"；（b）未讨论**临床可推广性边界**（8 个老龄化队列 ≠ 眼科筛查人群，规则用于临床决策支持时的适用域未讨论）；（c）"Funding/COI/伦理"不属于 STROBE 第 22 条，但同属稿件完整性。

**STROBE 小结**：22 条中 **完全符合 7 条**（第 2、3、7、8、11、14、19 条）、**部分符合 15 条**、**完全缺失 0 条**（缺失项已归入声明类，不计入 STROBE 条目）。**没有 STROBE 特有内容的重大缺项**；最需要补的是第 5 条（波次/年份表）、第 12/13（meta 分析方法段与事后声明）、第 16（BMI 插补）、第 18（基线特征表）、第 20（未调整估计）。

### B. TRIPOD+AI / DECIDE-AI 适用性判断 —— **重大（报告规范误用）**

- **位置**：`manuscript.md:126–130` / `sections/methods.md:5–10`（"Model development and the system-level comparison are reported against TRIPOD+AI [C001] and the early-stage evaluation against DECIDE-AI [C002]"）；引用池 `citation_pool.json` C001（TRIPOD+AI, BMJ 2024）、C002（DECIDE-AI, Nat Med 2021）**均只被 methods 引用**；`journal_guidelines_snapshot.md:39` 还据此认为"任何 TRIPOD+AI/DECIDE-AI 要求已满足"。

- **判断：本文不属于 TRIPOD+AI 的适用范围；声称遵循它是报告规范误用，应删除或实质降级。** 理由分四点：
  1. **TRIPOD+AI 的对象是"预测模型"**（diagnostic/prognostic prediction model development, validation, or both），其条目围绕**模型规格**展开：结局定义、预测因子选择与测量时点、**模型构建方法（回归类型/超参/惩罚项）**、**模型性能（区分度与校准，如 C 统计量、校准斜率/截距、校准图）**、**模型更新**、**模型可获取性（完整模型公式/系数/代码）**。本稿的核心对象是 **21 条"文献衍生的确定性规则"**（`:145–153`、Table 2），在 8 个队列中被当作**规则级命题**做关联检验（logistic 回归 OR），**既没有预测模型的开发（无系数、无训练目标、无超参搜索）**，**也没有任何模型性能指标（无 AUROC/AUPRC/校准/决策曲线/NRI）**。稿件 Results 中的 F1/P/R（`:478–485`）评价的是 **LLM+规则系统的规则命中分类性能**，不是预测模型的临床预测性能——两者不可互换。因此 TRIPOD+AI 的**主体条目（模型规格、性能、校准）无对象可对**。
  2. **TRIPOD+AI 确实包含"外部验证"主题**，若作者想保留部分对齐，只能落在 TRIPOD 的**外部验证条目**（第 3b/4b/10b/11b/12b/13b/16b/17b/19b/20b 系列），而**这些条目本文大部分不满足**：无 prespecified model（规则是"文献声明"而非"拟合模型"）、无校准、无序贯性能比较（只有 OR 与三态）、无模型可获取性声明（规则在 `configs/rules.yaml`，但稿件未给公式/条件）。**声称遵循而未提供对应内容，是比不声称更糟的状态**——审稿人一旦索要 TRIPOD+AI checklist，会发现大面积不适用（"Not applicable"占多数），反而暴露"声称与实际不符"。
  3. **DECIDE-AI 更不适用**：DECIDE-AI 面向 **AI 系统在临床现场的早期活体评估（early-stage live clinical evaluation）**，其条目要求**真实临床工作流中的前瞻性使用、使用者（医护/患者）交互、人因评估、临床结局与系统结局双层报告、现场数据漂移、伦理与治理（含是否影响患者决策）**。本文**无受试者接触、无临床部署、无前瞻使用**（`:130–131` 自己声明），因此 DECIDE-AI 的绝大多数条目在本研究中**在定义上不可能满足**。
  4. **讽刺的是，本稿的方法学远不止"能用 STROBE 描述"**：它做的是**规则/生物标志物式命题的跨队列可迁移性评估**，与以下框架或方法学更匹配——（i）**STROBE**（观察性关联研究，本稿已用且大部分满足）；（ii）若要强调"某个已发表的明确规则在不同人群中是否成立"，应显式采用 **PROBAST / QUIPS 的偏倚评估语言**（研究层面而非模型层面）并在 Discussion 中限定适用域；（iii）若要强调"同一条规则在 8 个队列的效应分布"，**系统综述/meta 分析的报告规范（PRISMA 2020 + 它关于异质性与预测区间的条目）**才是对口规范，因为本稿实际执行的就是"跨研究随机效应合并 + 异质性 + 预测区间 + 亚组 + LOO"，与 meta 分析同构（Table 5 的 REML/Q/I²/预测区间即是证据）。**这一点建议明确写进 Methods：本稿的合成层按 meta 分析规范报告（PRISMA 2020 相关条目），而非 TRIPOD+AI。**

- **为什么是问题**：报告规范声称具有"编辑与审稿人据以核查"的契约性质。声称遵循不适用的规范，会让（a）审稿人按错误的清单检查并发现大量空白，（b）编辑认为作者对方法学定位不清（把"规则验证"误称为"预测模型验证"），（c）掩盖真正应该声明的**事后分析性质**（见预注册专节——真正的风险不在"遵循了错的规范"，而在"用规范术语把事后分析包装成确证流程"）。
- **具体修改建议**：
  1. **删除** TRIPOD+AI 与 DECIDE-AI 的"reported against"表述，以及 `citation_pool.json` C001/C002 在 Methods 的引用（若删除后引用池变为 22 条，需同步更新 `package_manifest.json` 的 `references_cited: 24`）。
  2. 改为一句准确的定位：*"The cohort-layer analyses are reported according to STROBE [C003]; the between-cohort synthesis of rule-specific effects follows the reporting principles for meta-analysis of observational estimates (random-effects pooling, heterogeneity, prediction intervals) [C026, C027]. The rule- and system-level evaluation is not a prediction-model development or validation study, and therefore TRIPOD+AI is not applicable."* —— **主动说明"不适用"，比声称"遵循"更显专业。**
  3. 若作者坚持保留 AI 相关规范，唯一站得住的做法是**只保留条目标注 + 提交完整 checklist**：在补充材料中附 DECIDE-AI / TRIPOD+AI 清单，**如实把绝大多数条目标为 "Not applicable" 并逐条给理由**，同时把系统性能评估的局限（F1 on 规则命中、无校准、无前瞻、无临床结局影响）在 Limitations 中明写。**我不推荐这条路线**，因为它会把大量篇幅用于解释"为什么不适用"。
  4. 同步修正 `journal_guidelines_snapshot.md:39` 的判断（"any requirement for them is met"）——该判断基于错误的适用范围假设，且**自相矛盾**：同文件 `:16` 明确说无法取得本刊要求，`package_manifest.json:4` 也记 `journal_limits_verified: false`，却在 `:39` 断言"要求已满足"。这是投稿包内部的逻辑不一致，应改为"pending author verification"。

### C. 其他规范与格式（次要）

| 项 | 判定 | 说明 |
|---|---|---|
| 结构化摘要 | 符合 | Background/Methods/Results/Conclusions（`:9–43`），362 词。 |
| 图例自足性 | 部分 | Figure 1 图例 `:701–703`/`:818–829` 含中文（"慧眼"、"暴露组"），**英文投稿的图注中残留中文需清理或统一解释**；`analysis_plan §19.10` 亦为中文。稿件正文本身无中文（已核）。 |
| 图/表与源数据一致性 | **需澄清** | Table 3 `cohorts` 列在 `:1036` 为 `1.32-2.88`，正文 `:30`、`:381`、Table 5 为 `1.33–2.88`；Table 5 `:1039–1040` 的 Q p 为 4 位小数（0.0273/0.0272）而正文 `:384–385` 为 0.027。属舍入不一致，但审稿人会逐个核对，建议统一。 |
| 注册/预注册标识 | 缺失 | 见下节。 |
| 数据/代码/伦理/COI/资助/CRediT 六项 | **全缺** | 见"伦理与声明审查"。 |

---

## 预注册真实性核查（本次最重要一项）

### 核实方法

1. 逐条比对 `manuscript.md`（及 `sections/`）中的 "pre-registered" 声称与 `docs/analysis_plan.md` §19 的实际文本。
2. 用**文件系统时间戳**建立时序（§19 mtime、frame 构建时间、结果产物时间、异质性/效能/审计产物时间、稿件落盘时间）。
3. 用**版本库**检查 §19 是否存在于任何已提交快照中（**这一项是判定"是否可证"的关键**）。

### 核查结果 1：§19 是否真的包含所声称的预注册内容 —— **是，五项声称全部落在 §19 文本内**

| 稿件声称（行号） | §19 对应内容 | 判定 |
|---|---|---|
| "its testable rule set"（`:141–143`、`:329–331`、`RESULTS_COHORT.md` 首段） | `analysis_plan.md:523–549` §19.6"可检验规则集（**实测**，非推测）"：6/21 条规则、18 个（规则×队列）对，逐规则列出可检验队列 | **实质符合，但有一处需修正**：§19.6 表只列了 6 条**可检验**规则及其队列，**没有像稿件那样给出"15 条不可检验规则"的结构化清单**；15 条的原因表（`:539–546`）存在**分类重叠与计数不符**（r07 同时归入"需血液指标"，但稿件归入眼底影像；r19 同时出现在"需眼底影像"与"需膳食指数"；血液指标类实际列了 r01/r06/r07/r14 四条而稿件写"three require blood assays"；r05 的"需血脂"未计入稿件分类）。**这正是稿件 `:333–338` 与 Table 7 括注 `:1102`（"the two glaucoma-measurement rules (r16)"，实为一条）出现分类不一致的根源。** |
| "its per-cohort BMI cut-point"（`:143`、`:330`） | `analysis_plan.md:560–563` §19.7："逐队列**主切点预先声明**——KLoSA/MHAS/LASI/CLHLS 用亚洲切点 25；SHARE/HRS/ELSA/CRELES 用国际切点 30"，并给出参考率门实测依据（KLoSA 25→23.06% PASS / 30→1.45% FAIL；SHARE 25→63.83% FAIL / 30→22.81% PASS），另一作为敏感性 | **完全符合**（这是 §19 中最"像预注册"的一条：有切点、有依据、有敏感性安排）。 |
| "its covariate set"（`:143`、`:330–331`） | `analysis_plan.md:553–556` §19.7："协变量 = **age（连续或样条）+ sex**，队列内按波次固定效应"；`§19.7` 另定方差策略（survey 设计 / 聚类稳健）与 SHARE Rubin 合并（`:557–559`） | **基本符合，但两处松动**：（a）"age（**连续或样条**）"——**未冻结**具体形式，而稿件 `:242–247` 实际用 "age and sex as covariates"，两者措辞不同；建模选择（样条 vs 线性）会影响 meta-regression 结论，应冻结。（b）**协变量集与稳健方差/聚类、Rubin 合并写在同一段**，与"三态判定来自 R11 定义"混排，审稿人会问"§19.7 是预注册还是运行说明"。 |
| "its transportability criterion"（`:143`、`:330–331`） | `analysis_plan.md:570–572` §19.7："某规则在 ≥2 个队列中同向且 q<0.05 记 `transportable`；仅 1 个队列记 `single_cohort`；全部方向相反记 `non_transportable`" | **完全符合**，且与稿件 `:497–499`"the criterion fixed in advance — replicated with q < 0.05 in at least two cohorts"一致。 |
| "three-state standard … pre-registered"（`:16–19`、`:229–238`、`:284–292`） | `analysis_plan.md:564–566` §19.7："三态判定：**沿用 R11 定义**（replicated/contradicted/uninformative），基于 q 值与方向" | **符合（但属"沿用"而非"新定"）**：定义本身在 §2（`:225–231`）早已存在，§19 只是沿用。稿件的表述"pre-registered three-state standard"在**层间**层面成立于 §2，但读者会以为是本层新注册。建议改为 "the three-state standard fixed in the analysis plan before any layer was run (§2, §19.7)"。 |

**结论 1**：稿件所声称的四项（可检验规则集、BMI 切点、协变量集、可迁移性判据）**确实存在于 §19，且 §19 文本的详实程度足以支撑"运行前已确定"的内部一致性**。这一条对作者有利，应当承认。

### 核查结果 2：是否有内容明显是事后追加 —— **有，且是稿件结论的核心；共五项，其中两项已被稿件部分披露、三项未披露**

时间戳证据（同一天，逐分秒）：

| 时间 | 事件 / 产物 |
|---|---|
| 17:29:43–17:31:41 | 8 个 `data/frames/cohort_*.csv` 建成 |
| 17:31:08 | `scripts/cohort_rule_coverage.py`（生成 §19.6 的实测可检验集） |
| **17:32:27** | **`docs/analysis_plan.md` 最后写入（含 §19）** |
| 17:33:14–17:33:18 | `scripts/cohort_confirmatory.py`（主分析） |
| **17:34:19** | `outputs/cohorts/cohort_rule_results.csv`、`cohort_transportability.json`（**主结果**） |
| 17:34:53 | `outputs/cohorts/RESULTS_COHORT.md`（运行记录） |
| **18:28:16–18:31:06** | `scripts/cohort_heterogeneity.py` → `cohort_meta_summary.csv`、`cohort_influence.csv`、`cohort_heterogeneity.json` |
| **18:32:01–18:33:39** | `scripts/cohort_power.py` → `cohort_power.csv` |
| **18:36:58** | `evidence_audit.json`（Table 7 的 modality 审计） |
| 18:40–18:45 | `manuscript.md` 落盘 |

由此得出：

| # | 事后追加内容 | 证据 | 稿件是否披露 |
|---|---|---|---|
| 1 | **随机效应合并、REML τ²、Cochran Q、I²、95% 预测区间**（Table 5、`:373–399`、`:577–592`） | §19 **全文无"异质性""预测区间""随机效应""I²"任何字样**（已逐节确认）；产物 `cohort_meta_summary.csv`/`cohort_heterogeneity.json` **18:31** 生成，晚于主结果 57 分钟 | **未披露**。稿件把它当作 Methods 既定做法（`:22–24` 摘要 "Heterogeneity was quantified by random-effects pooling (REML τ², Cochrane's Q, I²) and summarised by prediction intervals"），Methods 章 `:240–260` **也无对应方法段**。这是最严重的一处。 |
| 2 | **异质性感知判据（预测区间排除 1 且 I²<75%）** | §19.7 的判据（`:570–572`）只有 "≥2 队列同向 q<0.05"；**无 I²、无 75% 阈值、无预测区间**。稿件 `:394–399` 自述 "Under a heterogeneity-aware criterion (prediction interval excluding the null **and** I² < 75%) … whereas the pre-registered criterion marked two as such" | **部分披露（好）但呈现在摘要中越界（不好）**：Discussion `:594–609` 明确说 "The transportability criterion used here was pre-registered and is reported as primary. It failed in an instructive way"，态度正确；**但摘要 `:29–33` 把两种判据写在同一句里**（"The pre-registered criterion marked two rules transportable … but both had I² above 90% and prediction intervals spanning unity …, so under a criterion also requiring tolerable heterogeneity no rule was reliably transportable"），**读者极易把 I²<75% 也当预注册**。→ 摘要须显式写 "in a **post hoc** heterogeneity-aware re-reading"。 |
| 3 | **地区亚组检验（Europe vs Asia vs Americas，p<0.0001）** —— 这是稿件标题与结论的支点（"directional conflict"、"pooling conceals"） | §19 **无"地区""regional""subgroup"任何字样**；亚组 p 值来自 `cohort_heterogeneity.py`（18:28–18:31）。§19.7 只声明了单队列模型与 ≥2 队列判据 | **未披露**。稿件 `:387–391`、`:504–511` 把地区冲突写成核心发现，却从未说明"region 作为分组变量"是**分析后引入**的（`analysis_plan.md` 里连"按大洲分层"这一构思都没有）。→ 必须补一句 post hoc 声明，并给出分组定义（欧洲=SHARE/ELSA/CRELES？亚洲=CLHLS/LASI/KLoSA？美洲=MHAS？——`cohort_meta_summary.csv` 与 `cohort_influence.csv` 的分组口径需在正文或补充材料写明，否则不可复现）。 |
| 4 | **E 值（E-values）** | §19 无 "E 值/E-value" 字样（§17/§18 亦无）；Table 5 括注与 `:406–412` 的 E 值由 `cohort_heterogeneity.py` 一并产出 | **未披露**（属于"事后加入的稳健性手段"，方向上是**加固**而非削弱结论，但仍是事后）。 |
| 5 | **Table 7 的测量模态审计（168 格中 18 格可行、各模态解锁计数）与效能分析（Table 6）** | §19 **无**"168""模态""modality""效能/MDE"任何字样；(§17 只在三库层预注册了效能方法，**未声明用于队列层**)；`evidence_audit.json` 18:36、`cohort_power.csv` 18:33 | **未披露**。Table 6 的 MDE 方法可援引 §17（三库层预注册），但 §17 未声明"同样用于队列层"；Table 7/modality 审计**完全无预先声明**。 |

**结论 2**：**存在明确的事后追加，且追加的不是边角料，而是稿件摘要与结论所依赖的全部量化论证（异质性 → 预测区间 → "合并掩盖冲突"）。** 判据层面尚可信：§19 冻结的四项预注册内容确实冻结了，主分析也按 §19 执行（`RESULTS_COHORT.md` 首段声明"本次运行未修改任何预注册项"，与 `cohort_transportability.json` 的 18 对/6 规则一致）。**但上文 5 项事后分析没有一项在正文被系统披露**（仅第 2 项以"criterion … also requiring"的措辞部分流露），这与本稿自称的"预注册纪律"不匹配。

### 核查结果 3：预注册"先于运行"的可证性 —— **在版本库中不可证，且 §19 缺少其他节都有的降格披露**

- **版本库事实**：`git log` 最后提交为 **2026-10-12**（`d04b0e0`/`568bf8a`/`c244af7`…）；`git show HEAD:docs/analysis_plan.md` **只到 `## 11.` 结束**，**没有 §12–§19**；`docs/analysis_plan.md` 当前为 **未提交的工作区修改（`git status` 显示 ` M docs/analysis_plan.md`）**。因此 **§19 在任何提交快照中都不存在**，"§19 落盘先于队列层运行"这一声明**无独立可证证据**。
- **作者自己的先例**：`analysis_plan.md:297`（§12）写明 "预注册时序对 round-3 可证（§12 mtime 先于 round-3 运行），round-1/2 的协议先行性无 git 快照可证，如实降格为'round-1/2 属协议形成期的探索性运行'"；`:327`（§13）"§13 落盘先于融合系统运行的声明无独立可证证据（无预运行 git 快照、首跑产物被覆盖），证据等级为'叙事自洽+内部一致'"；`:362`（§15）同款披露；`:372–379`（§16）亦声明时序。**§19 是唯一一个没有任何此类披露的层**，而它恰恰是稿件唯一声称"pre-registered"并写进标题的层。
- **文件级时序自洽性（对作者有利，应一并承认）**：§19 mtime 17:32:27 **早于**主分析脚本 17:33:14 与主结果 17:34:19，且 `cohort_rule_coverage.py`（17:31:08）先于 §19 落盘、其结果正是写进 §19.6 的"实测可检验集"——**内部故事在分钟级上自洽**。因此合理的定性是：**§19 很可能是真实运行前写下的，但这一点在客观上只能达到"叙事自洽+内部一致"的证据等级，与作者为 §12/§13/§15 自定的降格标准完全相同。**

- **修改建议（三条，按成本递增）**：
  1. **最低成本（必做）**：把 §19 及全部未提交的计划/台账**提交并打 tag**（如 `git tag prereg-cohort-layer`），在稿件中给出版本哈希；同时在 §19 开头补一句与 §12/§13/§15 同款的时序披露：*"本节落盘先于队列层运行；但本仓库在 §12–§19 期间无提交快照，该时序的证据等级为叙事自洽+内部一致（与 §12/§13/§15 同款披露）。"* —— **一致性本身就能挽回大部分信任**：目前的状态是"对前四层严格自曝、对最关键的层沉默"，审稿人一旦发现这个不对称，会往最坏处想。
  2. **必做（正文）**：在 Methods 增设 `## Deviations from the pre-registered protocol` 子段，逐条列出上文表 1–5 的五项事后分析，每条写明"**post hoc, not pre-specified in §19**"与理由；摘要对应句加 "post hoc" 限定词；标题中的 "pre-registered" 建议改为 **"pre-specified"**（或保留 pre-registered 但把适用范围明确限定为"§19 冻结的可检验规则集、BMI 切点、协变量集与可迁移性判据"四项）。
  3. **推荐（成本低、回报高）**：把补充材料 S3/S4/S5/S2 的脚本执行时间戳与 `docs/analysis_plan.md` 的 mtime 一并作为**审计材料**提交（本项目已在 `analysis_plan.md` 中大量使用这种"时序披露 + 降格自评"，审稿人会很买账；反之，若被审稿人自行发现 §19 未提交且时序不可证，性质会从"方法学局限"变成"诚信问题"）。

---

## 致命 / 重大 / 次要 / 需澄清

### 致命（0 项）

无。理由：本次核查未发现数据捏造、结果与源数据不符、未授权使用数据或伦理违规的证据；研究为公开去标识化数据的二次分析，豁免伦理审查在实质上是成立的（问题在于未声明）。`docs/analysis_plan.md` §0 记录的 test-set fitting（`:14`）发生在**内部分析层的早期版本**，且已按纪律降格处理（r22 定性为探索性扩展、逐版记录偏离、三态口径重跑），**不构成本稿的致命缺陷**，但**必须确保本稿不再出现类似的"结果已知后调整判据"而未披露的情形——这正是上文预注册核查结果 2 的五项**。

### 重大（4 项，均为送审/接收门槛项）

| # | 项 | 位置 | 为什么是问题 | 修改建议 |
|---|---|---|---|---|
| M1 | **完全缺失伦理声明、豁免依据与各队列原始伦理批准说明、知情同意说明** | `manuscript.md:124–143`（全稿无 Declarations 区块） | ICMJE/Elsevier 必填项；缺失通常在编辑初审即退回；8 个队列的数据使用条件复杂，缺失使审稿人无法排除数据合规风险 | 见"伦理与声明审查"第 1–2 条：新增 `## Declarations`，写明豁免依据 + 判定主体 + 11 个来源各自已获伦理批准与知情同意 |
| M2 | **完全缺失数据可得性声明，且未给出任何可执行的获取路径** | `manuscript.md:124–278`；`supplementary_material.md` 全篇 | 全部可复现性建立在"从原始文件重建 8 队列"之上，而这 8 个队列均需注册/申请；无路径 = 不可复现（复现性前提缺失） | 见"伦理与声明审查"第 3 条：新增逐队列"入口—条件—所用文件族"表（须实测链接后写入） |
| M3 | **完全缺失代码可得性声明（虽有全部脚本）、资助声明、利益冲突声明、CRediT 作者贡献** | 全稿；对照 `manuscript_R11.md:248–260`（原有四项声明区块被整体丢弃，且 `manuscript_assembly_manifest.json` 无 declarations 槽位） | 四项均为期刊必填；本稿还涉及 LLM 供应商与机构算力，属必须披露类型；缺失会被判定为"未披露"而非"无" | 见"伦理与声明审查"第 4–7 条：补 Code/Funding/Competing interests/CRediT 四段，并在组装模板中增设 declarations 槽位 |
| M4 | **预注册表述越界：摘要与结论所依赖的异质性/预测区间/地区亚组/LOO/E 值/模态审计均为 §19 未声明的"事后追加"，正文未系统披露；且 §19 的"先于运行"在版本库中不可证，而 §12/§13/§15 都有同款降格披露、唯独 §19 没有** | `manuscript.md:16–24`（摘要）、`:329–331`、`:373–412`、`:496–511`、`:594–609`；`analysis_plan.md:570–572`（判据）vs `:441–602`（§19 全文无异质性/亚组内容）；`git show HEAD:docs/analysis_plan.md`（§19 未提交） | 稿件以 "pre-registered" 为标题卖点，而量化的核心论证是事后选择的分析路径；不披露会从"方法学局限"升级为"诚信质疑"；且版本库事实使"先于运行"不可证，审稿人若自行核查会发现披露不对称 | 见预注册专节的三条建议：提交并 tag §19 + 补同款时序披露；Methods 增 `## Deviations` 表列五项事后分析；摘要加 "post hoc" 限定词、标题可改 "pre-specified" |

### 次要（7 项）

1. **Figure 1 图例含中文**（`:701–703`、`:818–829`："慧眼"、"暴露组（代谢-营养-生活方式-环境）"）。英文投稿的图注应清理或统一英文命名（系统名可保留拼音 Huiyan 并首次出现给全称）。**另**：`analysis_plan.md` §19 全为中文，若作为补充材料提交给英文期刊，需附英文版或双语版。
2. **Table 5 与正文数值舍入不一致**：`cohort_meta_summary.csv` 给出 r02 合并 OR 1.954、CI 由正文 `:30/:381` 为 1.33–2.88 而 Table 5 `:1036` 为 1.32–2.88；r12/r13 的 Q p 为 0.0273/0.0272（Table 5）vs 0.027（正文 `:384–385`）。**建议**：全稿统一到同一精度来源（并注明"pooled with Python/scipy；REML"这一自实现事实，Table 5 括注已有，建议提至 Methods）。
3. **Table 7 括注规则计数错误**："the two glaucoma-measurement rules (r16)"（`:1102`）——实为**一条**（r16）；`analysis_plan.md:542` 明确只列 r16。同段 `:1102` 的另一处分类（r03/r04/r07/r19/r22 全为"眼底影像"）与 `:333–338` 正文分类（r07 归入前者、r19 属后者）不一致。
4. **`manuscript.md:333–338` 的不可检验原因分类与 §19.6 不一致**：稿件写"three require blood assays (r01, r06, r14)"，§19.6 `:544` 列为 r01/r06/r07/r14（四条），且 r07 在稿件中同时属眼底影像族；r05"requires a lipid panel"在稿件中单列但未计入分类体系。**建议**：以 §19.6 的原因表为唯一口径重写该段（并同时修正 §19.6 自身的 r07/r19 重叠与计数）。
5. **LOO 结果与正文声明冲突（建议澄清后按 M 处理，见下"需澄清"）**：`manuscript.md:411–412`/`:586–587` 称 "Leave-one-cohort-out analysis shows the r10 regional split is not produced by any single cohort"，但 `cohort_influence.csv` 显示剔除 SHARE 后 r10 的 **I² 由 91.0% 降至 0.0%**、合并 OR 0.747 (0.66–0.84)。**该声明需要限定**：稳健的是"合并后不显著为阳性"，不稳健的是"异质性不由单一队列驱动"。建议改写为 "leave-one-cohort-out shows the pooled estimate remains non-null-positive (and becomes clearly protective, 0.75, 0.66–0.84, I² 0%) only when SHARE is removed — i.e. the European/Asian split is itself carried substantially by the SHARE cohort"。
6. **STROBE 第 5/16/18/20 条的要素缺项**（波次年份表、BMI 插补说明、基线特征表、未调整估计）：均属补表/补段即可，成本低。
7. **投稿包自相矛盾**：`journal_guidelines_snapshot.md:16` 与 `package_manifest.json:4` 均声明无法取得本刊要求/未核实，但同文件 `:39` 断言"TRIPOD+AI/DECIDE-AI 已引用即满足任何要求"；`package_manifest.json` 的 `references_cited: 24` 在删除 C001/C002 后需同步更新。

### 需澄清（4 项，作者答复即可）

1. **豁免判定的主体与依据是什么？**（作者单位伦理委员会？自行判定？依据哪条法规/机构政策？）必须在伦理声明中写明——这是审稿人唯一会逐字核对的一句话。
2. **各队列的数据使用协议（DUA）是否允许本稿的分析与（可能的）代码/派生数据公开？** 尤其 SHARE 与 KLoSA/CLHLS 的条款常限制再分发；若不限制，建议在数据声明中说明"作者不再分发任何原始数据，仅公开可再生的派生 frame 生成脚本"。**另需澄清**：本地是否存在派生 frame（`data/frames/cohort_*.csv`，含 SHARE 1.69M 行）被随包提交或含可识别信息，请在数据声明中明确不提交。
3. **LLM 供应商与算力的性质**：`manuscript.md:711` 记 "DeepSeek 主客户端 + DualLLMClient 第二客户端"，`analysis_plan.md:82` 记本地 qwen3.8-27b——这些模型是自建、开源本地部署还是商业 API（是否含免费额度/机构协议）？关系到 COI 与 Funding 的写法。
4. **作者名单与顺序、通讯作者、是否有外部合作者/数据提供方人员参与**；本项目的 agent 流水线是否有第二位人类复核者（关系到 CRediT 中 Validation 与 Supervision 的落点）。

---

## 送审前最小必修清单（按执行顺序）

1. **[M1/M2/M3] 新增 `## Declarations` 区块**（Ethics + Consent + Data availability 逐队列表 + Code availability + Funding + Competing interests + CRediT + Use of AI 声明），并把它加入 `manuscript_assembly_manifest.json` 的 sections 与 `package_manifest.json` 的 files。
2. **[M4] 补 `## Deviations from the pre-registered protocol` 子段**（五项事后分析逐条列出）+ 摘要加 "post hoc" 限定 + `git tag` 冻结 §19 并给出哈希 + 在 §19 首补同款时序披露。
3. **[重大附带] Methods 新增 `## Between-cohort synthesis` 方法段**（REML/τ²/Q/I²/预测区间/亚组/E 值的具体做法与实现说明），使 Results 的方法来源有落点。
4. **[报告规范] 删除 TRIPOD+AI/DECIDE-AI 的 "reported against" 表述**，改为 STROBE + meta 分析规范的准确定位；同步修正 `journal_guidelines_snapshot.md:39`。**[必做否则审稿人会索要 TRIPOD+AI checklist 并发现大面积不适用]**
5. **[次要] 统一数值精度、修正 Table 7 的 r16 计数与 r07/r19 分类、改写 LOO 声明、补 STROBE 第 5/16/18/20 条要素。**
6. **[需澄清] 逐条答复"需澄清"4 项。**

---

*本报告基于对上述材料的实际读取；未联网核实各队列数据访问链接（数据声明表中的链接与条件须作者实测后再写入）；未接触原始数据文件，未复算任何统计量。*
