# Phase 2 · 文献景观与可行性（PLAN.md §X 预稿）

> 产出：medical-agent-planner Phase 2（联网验证），2026-10-11。
> 说明：本文件在 scaffold（Phase 4）生成 PLAN.md 后并入其 `## §X. Literature Landscape & Feasibility` 节。
> 检索渠道：PubMed E-utilities（本地 NCBI key，10 req/s）+ 本地原始数据库实读（R 4.6.1 / Python）+ NEI 官网（代理通道）。
> 全部计数为 2026-10-11 实测；检索式与原始计数见文末附录。

## §X.1 研究前景（Check 1）

| 检索主题 | 5y（2021–2025 完整年 + 2026 部分年） | 全时段 |
|---|---|---|
| **exposom\* × 眼病** | **17** | **22** |
| environment-wide / exposome-wide × 眼病 | 3 | 6 |
| 尿酸 × 眼病 | 126 | — |
| 维生素 D × 眼病 | 295 | — |
| 重金属（查询修复后）× 眼病 | 49 | — |
| 空气污染/PM2.5 × 眼病 | 233 | — |
| 吸烟 × 白内障/青光眼/AMD | 529 | — |
| 体力活动 × 眼病 | 747 | — |
| 混合暴露/共暴露 × 眼病 | 283 | — |
| 筛查/AI × 眼病 × 风险因素 | 1342 | — |
| GBD × 眼病 × 风险因素/归因 | 70 | — |
| NHANES × 眼病 | 271 | — |
| KNHANES × 眼病 | 35 | — |

**趋势（exposome × 眼病 逐年）**：2020:2 → 2021:1 → 2022:0 → 2023:2 → 2024:3 → **2025:6 → 2026:7**
结论：低基数、方向性上升（2024–2026 合计 16/21），不宜作趋势或加速推断；结合"疾病 × EWAS"范式中眼科仅 5/228 的结构性偏低（§X.3），支持选题窗口判断——**空白的是筛查系统，不是领域本身**。

- **基金/产业动态**（本行替换 PLAN 模板中的 TBD）：在 NEI 公开战略计划页面（2021–2026 版；2027–2032 编制中）**未检出**将环境/代谢暴露列为眼病优先方向的表述（检索时点 2026-10-11，属未检出而非否定）；亦未检索到针对"暴露组×眼病筛查系统"的专项资助公告（渠道：NEI 官网 + PubMed）。本方向处于"学术前沿先行、专项资助尚缺"的窗口期。

## §X.2 数据可及性（Check 2，逐库实读）

### NHANES（本地 1999–2018，719 文件）
| 模块 | 周期 | 实读结果 |
|---|---|---|
| VIX 客观视力 | 1999-2000 / 2001-02 / 2003-04 / 2005-06 / 2007-08（5 周期） | n=6,758 / 7,445 / 6,990 / 6,980 / —；年龄 12–85；logMAR 制（含 88=盲编码） |
| OPXRET 视网膜分级 | 2005-06 / 2007-08（2 周期） | n=2,934 / 3,863；**年龄 40–80+**；VCDR 连续值（OPDDVCDR n=2403、OPDSVCDR n=2413）、DR 四级（OPDURL4：2145/244/57/13）、ARM 分级（OPDUARM / OPDULARM / OPDUPIGA / OPDUGA）、222 列病灶级字段 |
| VIQ 眼病问卷 | 1999–2008 | 自报白内障/青光眼/AMD 等 |
| 生化 | 1999–2008 | BIOPRO（含尿酸 LBXSUA、血糖、肌酐等） |
| 膳食 | 1999–2008 | DR1TOT / DR2TOT 等 |
| 重金属/环境毒物 | 2005-08（PAH 另含 2003-04） | PBCD_D/E（血铅镉）、UHM_D/E（尿重金属）、PAH_D/E（多环芳烃）、L31PAH_C |
| 备注 | 2011–2018 本地仅核心问卷（无眼科/RXQ 文件；如需可公开补下载） | |

### KNHANES（本地 Rdata 五包 + 官方变量字典 1,686 眼科变量）
| 波次 | 眼科模块（R 实读，含年龄） |
|---|---|
| 2008 / 2009 / 2010 | hn08_eye n=4,846（年龄 3–80，中位 39）/ 9,760 / 8,141 |
| 2011 / 2012 | n=7,791 / 7,444（3–80） |
| 2017–2020 | n=3,160 / 4,386 / 4,437 / 4,171（**40–80**，中位 59–61） |
| 2021 | n=3,603（10–59） |
| 变量（跨波稳定） | 眼压 E_Gr_p / E_Gl_p（2008-12）与 E_Pr_1 / E_Pl_1（2017+）；**视盘 CDR 垂直/水平 E_Grv / E_Grh / E_Glv / E_Glh + 视盘出血 E_Gr_b / E_Gl_b（2008-12）**；AMD 四型分眼 E_AMD_ELY / LATE / WET / DRY；DR E_DRP + 逐病灶 E_DR_1..11；双眼视力 E_Cr_1 / E_Cl_1 + 矫正视力；自动验光/屈光；空气污染模块（hnXX_ap） |
| 缺口 | **晶状体分级：字典全库 0 命中（수정체）→ 白内障仅自报（DH2/DH3）**；2013–2016 无独立眼科检查模块 |

### 9 大老龄队列 / CHARLS / GBD
- **CHARLS 2011 原始 dta 实读**：da033 / da034（远/近视力）、da035 / da036（白内障手术）、da037（青光眼）、biomarkers.dta；2011、2015 含血生化
- 其余队列自报眼病变量（白内障/手术史/青光眼/自评视力）在 HRS / ELSA / SHARE / KLoSA / LASI 等可用；各库覆盖不同，验证时按库分别计覆盖率
- **GBD 本地齐备**：15（2023 近视力丧失）/ 17（2023 盲与视力损害）/ 18（2021 55+ 暴露-结局）

## §X.3 竞品与差异化（Check 3）

**"首个可解释暴露组×眼病筛查 agent"的证明性检索（2026-10-11；两轮探针**全标题筛查**，完整清单落盘 `PHASE2_probe_titles.txt`）：**

*探针 D —— EWAS 全称（`"environment-wide association"[tiab] OR "exposome-wide association"[tiab]`，n=228，全标题筛查）*
- **眼病相关仅 5/228（2.2%）**；同期 EWAS 已覆盖阿尔茨海默病、心血管病、哮喘、SLE、高血压、自杀未遂、BMI、COVID、高尿酸血症等 10+ 疾病 → **眼科在"疾病 × EWAS"范式中是结构性空白**（分母证据，比单纯计数更有力）
- 眼病命中 5 篇分类：
  - 🔴 **必须区分**：**原发性房角关闭青光眼 × exposome-wide（China Kadoorie Biobank，Asia Pac J Ophthalmol 2026，`10.1016/j.apjo.2026.100378`）**——最直接先例：单病种、单队列、关联研究；无系统/规则/多库验证
  - 🔴 **必须区分**：**DR × EWAS in NHANES 2005-2008（J Clin Med 2020，`10.3390/jcm9113643`）**——同数据库（NHANES）单病种先例，无系统化筛查与多库验证
  - 🔵 必须引用：Oculomics meets exposomics 路线图（Exposome 2025，`10.1093/exposome/osaf013`）
  - 🔵 必须引用：ExWAS 方法学 heuristic（Environ Sci Technol 2026，`10.1021/acs.est.6c02553`）
  - 🔵 必须引用：AD × AMD 共享环境病因（npj Aging 2024，`10.1038/s41514-024-00162-4`）
- 另 45 篇"系统/预测"类**非眼病**论文（范式近邻）：🔵 **Nat Med 2026 exposome-phenome 图谱（`10.1038/s41591-026-04266-0`）**——图谱框架（描述性），无临床筛查输出；🔴 **AD 的 EWAS→预测风险评分（Alzheimers Dement 2026，`10.1002/alz.71842`）**——最近邻范式（EWAS 升级为评分，但单病种/单库/无规则引擎）；🔵 EWAS 计算标准（Environ Int 2026）；高血压风险因素图谱（Eur J Prev Cardiol 2025）

*探针 E —— exposome × 眼病（`exposome*[tiab] AND (eye OR ocular OR ophthalmic OR vision OR cataract* OR glaucoma* OR "macular degeneration" OR "diabetic retinopathy" OR "visual impairment" OR "eye disease*")`，n=44，全标题筛查）*
- 实质眼病相关约 10/44；🔵 **重磅必须引用：Prog Retin Eye Res 2026 综述 "Exposome for ocular diseases: From exposure evidence to causality and actionable prevention"（`10.1016/j.preteyeres.2026.101524`）**——顶刊已认定该方向，且其 "actionable prevention" 定位正是本项目筛查系统的生态位
- 其余相关：眼表 exposome 综述（IJMS 2023）、视网膜 × 衰老 exposome（GeroScience 2026）、AMD × exposome 代谢组（Metabolomics 2026）、教室灰尘微生物组 × 学生眼健康（Environ Pollut 2026）
- 查询卫生：`vision[tiab]` 含"愿景"义噪声（如 "A vision for exposome epidemiology"），已人工筛除
- 补充（眼病系统侧旧证据保留）：眼病 × 决策支持/筛查/专家系统/知识图谱（全时段 505 篇）人工核查 top 命中**均为影像 DL 或器械类**（Cell 2018 眼底 DL、OCT 术中定位、DR 影像筛查等），**未见暴露侧系统**——与探针 D 的结构性空白结论一致

*探针 F —— 暴露侧风险预测 × 眼病（`眼病组 AND (risk prediction[tiab] OR prediction model[tiab] OR risk score[tiab]) AND (exposure*[tiab] OR environmental[tiab] OR lifestyle[tiab] OR metabolic[tiab])`，n=211，**已全标题筛查**，清单见 `PHASE2_probe_titles.txt`）*
- 空间画像：211 篇以"单病种 × 单暴露/生化指标 × 预测模型"为主（AMD 进展模型数十篇、近视预测、重金属×青光眼/DR 机器学习、空气污染×青光眼/AMD、尿酸×青光眼等）；**未见暴露组 × 多眼病的系统化筛查工作**
- 🔴 必须区分（"暴露侧→眼病预测"最接近者）：
  - 重金属暴露 × 青光眼机器学习预测（**NHANES 2005-2008**，Sci Rep 2025，`10.1038/s41598-025-88698-7`）——同库、单病种、ML 无规则
  - 重金属 × DR 机器学习建模（Sci Rep 2024，`10.1038/s41598-024-63916-w`）
  - Exposure-wide 方法识别 AMD 可干预因素（Br J Ophthalmol 2026，`10.1136/bjo-2025-328446`）——单病种暴露广谱关联
  - 代谢指标可解释 ML 预测 DR（J Diabetes Res 2023，`10.1155/2023/3990035`）——"可解释"仅达单病种、单队列
  - 生化指标白内障风险模型（**NHANES 2005-2008**，Front Med 2024，`10.3389/fmed.2024.1452756`）
  - 代谢易感性 × 多年龄相关眼病（前瞻队列，Front Nutr 2026，`10.3389/fnut.2026.1840459`）——多眼病但单队列、无系统
  - 心血管代谢共病 × 视力障碍 ML 预测（**CHARLS**，BMC Ophthalmol 2025，`10.1186/s12886-025-04596-6`）——使用本项目队列臂同一数据源
- 🔵 必须引用：Gene-Lifestyle Synergy in DR（Ophthalmology 2026）；饮食/生活方式对晚期 AMD 进展的量化（Ophthalmology 2026）；EYE-RISK 遗传×生活方式×AMD（Ophthalmology 2021）

*探针 G —— 可解释/规则 × 暴露 × 眼病（`眼病组 AND (explainable[tiab] OR interpretable[tiab] OR rule-based[tiab] OR knowledge graph[tiab]) AND (exposure*[tiab] OR environmental[tiab] OR lifestyle[tiab])`，n=33，**已全标题筛查**）*
- 🔴 必须区分：吸烟 × 衰老对**白内障-AMD 共病**的非线性协同效应——可解释人工智能方法（Front Public Health 2026，`10.3389/fpubh.2026.1784189`，PMID 42052023）——比 ACG/CKB 与 DR/NHANES 先例更近：已触及多眼病共病 + 可解释 AI
- 🔴 必须区分：近视性黄斑病变 10 年风险预测——可解释机器学习算法的开发与验证（IOVS 2024，`10.1167/iovs.65.6.40`，PMID 38935031）——"可解释 + 有验证"的眼病风险预测，本项目差异化据此收窄
- **方法学记录**（重要）：探针 G 的相关命中位于 relevance 排序第 14–29 位，前 27 位混有自动驾驶、罗非鱼形态学、睡眠记忆巩固等噪声——**top-命中审法在此空间必然漏检，全标题筛查是必需而非偏好**

**修正后的 novelty 表述（建议采用）：**
> 首个面向**暴露组 × 多眼病**的**可解释筛查系统**（规则引擎 + 知识图谱 + LLM 仲裁），并首次在**三个独立人群库族**（NHANES → KNHANES → 9 国老龄队列）上对暴露-眼病关系做**三层独立验证并报告泛化落差**。与最近先例明确划界：① 单病种 EWAS 关联研究（ACG/CKB；DR/NHANES）——无系统与多库验证；② EWAS→预测评分（AD，2026）——单病种、单库、非暴露组×多眼病系统；③ exposome-phenome 图谱（Nat Med 2026）——描述性、无临床筛查输出；④ 单队列/单模型的（含可解释）ML 眼病预测（近视性黄斑病变 10 年风险，IOVS 2024；吸烟×衰老白内障-AMD 协同，2026；NHANES 重金属×青光眼 ML，2025）——单病种/单库、无跨库泛化验证、非系统化暴露组筛查。

**结论：声明成立（且经全标题筛查加固）。**（同族旁证：药物性眼病"AI/系统"方向全库仅 32 篇亦为空；本项目走暴露路线后差异化更纯。）

> 口径说明：本文件含四个探针，覆盖四个不同检索空间——D/E 为 EWAS/exposome 关键词空间（228 / 44），F/G 为功能空间（211 / 33）。四者互补而非等价，不可互相折算，计数差异不属语法或时点差异。四个空间的全标题清单均已落盘 PHASE2_probe_titles.txt；眼病相关子集均极小，结论在所有空间一致收敛。

**与课题组前作的方法学差异（mingmu / jingming）：**

| 维度 | mingmu 明目（2026-10） | jingming 睛明（前作） | **huiyan 慧眼（本项目）** |
|---|---|---|---|
| 实体对 | 食物 133 × 青光眼药物 62 | 手术 40 × 患者因素 200 | **暴露组 40 × 眼病 15** |
| 领域 | 食物-药物相互作用 | 围手术期禁忌 | **暴露组-眼病关联/易感性** |
| 验证数据 | 文献病例 + 自编题库 + 专家盲评（单源为主） | 医生决策影响实验（decision impact） | **本地 4 库三层独立验证（NHANES→KNHANES→9 国队列）** |
| 金标准 | 指南/说明书标注 | 临床结局 | **数据库对级关联（预注册 + FDR）** |
| 特色指标 | 拒识安全行为 / 特异度 | 决策改变率 | **跨库/跨国/跨人群泛化落差（前两作均无）** |
| 技术骨架 | 规则 + KG + LLM（共享同族骨架） | 同族 | 同族复用；实体对 / 领域 / 验证设计全新 |

## §X.4 期刊适配（Check 4，近 24 个月真实范例）

| 期刊 | 2023-26 "筛查/AI/预测"类计数 | 已核 DOI 范例 |
|---|---|---|
| Ophthalmology | 78 | ① AAO 羟氯喹视网膜病变筛查建议（2025 修订版）`10.1016/j.ophtha.2025.11.001`（**暴露性眼病筛查同形态先例**）；② 血浆代谢组→DR 预测 `10.1016/j.ophtha.2024.07.004` |
| JAMA Ophthalmology | 121 | 视网膜图像 DL 预测早产儿心肺疾病 `10.1001/jamaophthalmol.2025.5814`（2026） |
| British Journal of Ophthalmology | 136 | 暴露广谱方法识别 AMD 可干预因素（2026 刊出；与探针 F 命中同一篇）`10.1136/bjo-2025-328446` |

判定：**strong**（两大目标刊持续发表筛查/预测系统类工作；且暴露性眼病筛查在目标刊有 AAO 级先例）。

> 投刊提示：课题组前作睛明（jingming，已核实：手术 40 × 患者因素 200、decision impact 验证）为 submission-ready 且一志愿 JAMA Ophthalmology；本项目一志愿 Ophthalmology、备选含 JAMA Ophthalmology——主题不同（围术期禁忌 vs 暴露组-眼病筛查），同族同刊投稿时建议在 cover letter 明示区分。

## §X.5 验证数据集可及性（Check 5，逐条裁决）

| 数据集 | 裁决 | 依据 |
|---|---|---|
| dev-exposure-disease-pairs（文献/指南） | **feasible** | 文献池充足（§X.1 各域 126–747 篇）；400 对可达成；AAO PPP 三册（POAG/AMD/DR）免费全文已验证可下载 |
| intval-nhanes | **feasible** | VIX 5 周期 + OPXRET 2 周期（40+）+ 生化/膳食/重金属（PBCD/UHM/PAH 2005-08，与视网膜分级同周期）+ VIQ |
| extval-knhanes | **feasible** | 眼科 10 波（2008-12 全龄 / 2017-20 40-80 / 2021 10-59）；IOP / CDR / AMD / DR / VA / 屈光齐全；暴露侧生化 + 营养 + 空气污染 |
| extval-cohorts-9 | **feasible_reduced** | 自报眼病 + 自评视力（无 VA / 分级）；暴露 = 生活方式 + 部分库血清；人群轴独立成立 |

**存活数 = 4 ≥ 2 ✓**（其中 1 条 feasible_reduced，按"各库覆盖率分别报告"处理）

**分级依赖项处置**：cataract_subtype_graded 全库无源可判（NHANES 无亚型 / KNHANES 无晶状体分级 / 队列无分级）→ 保留 15 条清单不动，验证时该条不计入覆盖率并在报告中注明。（其余 4 条分级依赖项 amd_early / amd_late / dr_npdr / dr_pdr 的可判性已包含在下表。）

**15 条 × 3 数据集族 覆盖矩阵（逐格实读证据；✓ = 可判，✗ = 不可判）**

| # | B 条目 | NHANES | KNHANES | 9 队列 |
|---|---|---|---|---|
| 1 | cataract_any | ✓ VIQ（1999–2008） | ✓ DH2_lt / DH2_dg + DH2_cd | ✓ 6/9：ELSA·SHARE·LASI（catracte）/ HRS·KLoSA（catrcte 手术）/ CHARLS（da035/36） |
| 2 | cataract_subtype_graded | ✗ | ✗ | ✗ |
| 3 | glaucoma_selfreport | ✓ VIQ | ✓ DH3_lt / DH3_dg | ✓ 4/9：HRS·KLoSA（glaucoma）/ LASI（glaucome+glaucoma）/ CHARLS（da037） |
| 4 | glaucoma_iop_elevated | ✗（无 IOP） | ✓ E_Gr_p / E_Gl_p（2008-12）、E_Pr_1 / E_Pl_1（2017-19） | ✗ |
| 5 | glaucoma_suspect_cdr | ✓ OPDDVCDR / OPDSVCDR（2005-08） | ✓ E_Grv / E_Grh / E_Glv / E_Glh | ✗ |
| 6 | amd_selfreport | ✓ VIQ | ✓ E_VS_ELY/LATE/WET/DRY | ✓ 1/9：HRS（ashamd） |
| 7 | amd_early | ✓ OPDUARM / OPDUPIGA | ✓ E_AMD_ELY | ✗ |
| 8 | amd_late | ✓ OPDULARM / OPDUGA / OPDUEXU | ✓ E_AMD_LATE / WET / DRY | ✗ |
| 9 | retinopathy_any | ✓ OPDURET（222 列病灶域） | ✓ E_DRP | ✗ |
| 10 | dr_npdr | ✓ OPDURL4 2–3 级 | ✓ E_DR_1..11 病灶级重建 | ✗ |
| 11 | dr_pdr | ✓ OPDURL4 4 级 | ✓ E_DR_8..11（NVD/NVE/玻璃体出血/纤维增殖） | ✗ |
| 12 | vision_impairment_mild | ✓ VIX logMAR | ✓ E_Cr_1 / E_Cl_1 | ✗★ |
| 13 | vision_impairment_moderate | ✓ VIX logMAR | ✓ E_Cr_1 / E_Cl_1 | ✗★ |
| 14 | vision_impairment_severe | ✓ VIX logMAR | ✓ E_Cr_1 / E_Cl_1 | ✗★ |
| 15 | optic_disc_abnormality | ✓ OPDUFOC / OPDUPHVH 等眼底异常域 | ✓ E_Gr_b / E_Gl_b（视盘出血）+ CDR 高值 | ✗ |

★ 队列层无 VA 测量（9/9 库有自评视力 `r*sight / sighta`，可作第 16 条"自评视力差"粗粒度补充，需作者批准，暂不计入）。

**列合计**：NHANES **13/15**、KNHANES **14/15**、队列 **3/15**（条目级；另有自评视力补充位）。与上方四数据集裁决一致（feasible / feasible / feasible / feasible_reduced）。
**队列臂逐条覆盖声明（不得整体宣称"9 国"）**：cataract_any 6/9、glaucoma_selfreport 4/9、amd_selfreport 1/9（仅 HRS，列为探索性、不计入队列臂主结论）；后续 Results 按条目分别声明跨人群强度。据此，extval-cohorts-9 的 expected_size 已由 200 下调为 **120 对（上限）**（见 config datasets[].notes）。
**A 侧（暴露）覆盖**：NHANES = 生化 + 膳食 + 重金属 + 生活方式 ✓；KNHANES = 生化 + 营养 + 生活方式 + 空气污染 ✓；9 队列 = 生活方式（9/9）+ 部分库血清生化（CHARLS、HRS VBS 等）。MHAS / CRELES 仅自评视力（未检出白内障/青光眼/AMD 题项）；CLHLS 以视觉功能题项为主（待二次核）。

## §X.6 B 侧实体数 <30 的 mitigation 论证（P0）

- planner 硬规则要求任一侧 ≥30 实体（防组合空间平凡）。本项目 A=40 ✓，B=15 条眼病条目 <30。
- **Mitigation**：分析单元是 exposure×disease 的**对（pair）**而非 B 的条目数——40 暴露 × 15 眼病项 = **600 对**，组合空间非平凡；且 B 侧条目全部经"数据集真能判定"原则裁剪（见 §X.5 审计），硬凑到 30 会引入无数据支撑条目、反而破坏 Check 5。
- 结论：**以对为单位满足非平凡性要求**，本项按"通过 + 论证"处理。

---

## 附录：检索式与原始计数（2026-10-11，PubMed E-utilities）

| 代号 | 检索式（摘要） | 窗口 | 计数 |
|---|---|---|---|
| C1a | `exposom*[tiab] AND (eye OR ocular OR ophthalmic OR cataract* OR glaucoma* OR "macular degeneration" OR "diabetic retinopathy" OR "visual impairment")` | 2021-26 / 全 | 17 / 22 |
| C1b | `("exposome-wide" OR "exposome wide" OR "environment-wide") AND (眼病组)` | 2021-26 / 全 | 3 / 6 |
| C1c–C1l | 尿酸 / 维D / 重金属(修复后) / 空气污染 / 吸烟 / 体力活动 / 混合暴露 / 筛查AI×风险因素 / NHANES / KNHANES 各 × 眼病组 | 2021-26 | 126 / 295 / 49 / 233 / 529 / 747 / 283 / 1342 / 271 / 35 |
| P1b | `(眼病组) AND ("decision support system" OR "clinical decision support" OR "screening system" OR "expert system" OR "rule-based system" OR "knowledge graph")` | 全 | 505 |
| P2 | `("risk prediction" OR "prediction model" OR "risk score") AND (cataract* OR glaucoma* OR AMD OR DR)` | 全 | 740 |
| P3 | `("knowledge graph" OR "rule-based" OR explainable OR interpretable) AND (眼病组)` | 全 | 859 |
| P4 | `("environment-wide association" OR "exposome-wide association") AND (眼病组)` | 全 | 6 |
| P5 | `(GBD OR "Global Burden of Disease") AND (眼病组) AND ("risk factor*" OR attributable)` | 2021-26 | 70 |
| F | `眼病组 AND (risk prediction OR prediction model OR risk score) AND (exposure* OR environmental OR lifestyle OR metabolic)` | 全 | 211 |
| G | `眼病组 AND (explainable OR interpretable OR rule-based OR knowledge graph) AND (exposure* OR environmental OR lifestyle)` | 全 | 33 |
| 期刊 | `("Ophthalmology" / "JAMA ophthalmology" / "Br J Ophthalmol"[ta]) AND (AI/ML/DL/decision support/risk prediction/screening) AND 2023-26[pdat]` | 2023-26 | 78 / 121 / 136 |

> 查询卫生备注（已修复）：重金属检索初版含裸 `lead` 撞动词致 4980 虚高，修复版 49；BJO 初版 `"British Journal of Ophthalmology"[ta]` 返回 0，修复版（`"Br J Ophthalmol"[ta]`）136。C1a 口径已换 exposom*（覆盖 exposomics）；重计后计数不变（exposomics × 眼病仅 1 篇且同时命中 exposome，无净增——复核未复现出净增量）。

---
**注**：本文件为 scaffold 前预稿；Phase 4 生成 PLAN.md 时并入 §X，并在 §X.1 替换模板 TBD 行。
