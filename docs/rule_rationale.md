# Rule Rationale — huiyan（Phase 3 v2 · 作者裁定版，2026-10-11）

> 21 条规则：A 4 / B 14 / C 3；7 机制全覆盖。本文件 = 每条规则的证据链 + **研究设计类型标注**（作者裁定 3a 的证据类型门）+ 第二源待办。
> 纪律：risk_type ∈ 7 机制；severity 映射 A→high / B→medium / C→low；结果按证据级分层报告；C 级不与 A 级混合出数。

## 规则证据表

| 规则 | (A × B) | 机制 | 证据级 | 代表引用（DOI / PMID） | 设计类型 | 第二源待办（executor phase3） |
|---|---|---|---|---|---|---|
| r01 | 尿酸 × 白内障 | oxidative | C | 10.1038/s41420-024-01900-z / 38461179 | 机制（细胞实验） | 补流行病学队列（尿酸-晶体混浊）。**⚠ 课题组既往反证（2026-10-11 发现）**：本组双队列研究（CHARLS 2011 n=11,473 + NHANES 1999-2008 n=9,754，见 `E:\BaiduNetdiskDownload\所有数据库\01. CHARLS...\2011白内障\尿酸与白内障手术关联.docx`）结论为"尿酸×白内障关联非独立（年龄混杂）"——r01 预期在 DB 验证中为 gold-negative；保留为 C 级规则诚实测试用例，论文中须引用该工作并声明对已发表单对的让渡 |
| r02 | 高血糖 × 白内障 | glycation | B | 10.1002/dmrr.3073 / 30209868 | 系统综述（T2D 内风险因素） | 补一般人群"糖尿病→白内障发病"meta |
| r03 | HbA1c × 视网膜病变 | glycation | B | 10.1007/s13300-017-0345-5 / 29190012 | 叙述综述（血糖控制） | 补 DCCT/UKPDS 试验证据 |
| r04 | HbA1c × PDR | vascular | C | 10.3390/ijms26114992 / 40507802 | 机制综述（VEGF/缺血） | 补 PDR 进展关联级队列 |
| r05 | 血脂 × AMD 早期 | oxidative | B | 10.1097/MD.0000000000041599 / 39993131 | 更新 meta 分析 | 补血脂分项（LDL/TG）meta |
| r06 | CRP × AMD 晚期 | inflammation | B | 10.1016/j.survophthal.2010.08.007 / 21420705 | **血清 CRP meta**（类型匹配 ✓） | 补 2011 后新 meta |
| r07 | 维D × NPDR | endocrine | B | 10.3390/ijms241512014 / 37569392 | 叙述综述 | 补维D-DR 队列/meta |
| r08 | 抗氧化不足 × 白内障 | oxidative | B | 10.3109/10715762.2013.777155 / 23438873 | 叙述综述 | 补 AREDS/类胡萝卜素 RCT 或 meta |
| r09 | 地中海饮食 × AMD 晚期 | oxidative（保护） | B | 10.1016/j.ophtha.2018.09.032 / 30803514 | 队列证据综述 | 补 MedDiet-AMD 队列二源 |
| r10 | 吸烟 × 白内障 | oxidative | A | 10.1016/j.ebiom.2022.104154 / 35816897 | MR 系统综述（因果） | 可补经典队列（BMJ/BEH） |
| r11 | 吸烟 × AMD 晚期 | oxidative | A | 10.1097/MD.0000000000041599 / 39993131 | meta 分析 | 同 r05 共用正当（AMD 风险因素 meta 含吸烟） |
| r12 | 饮酒 × 白内障 | oxidative | B | 10.1111/ceo.13892 / 33426783 | 综述（白内障-全身病） | 补剂量-反应 meta |
| r13 | BMI × 白内障 | glycation | A | 10.1371/journal.pone.0089923 / 24587127 | 前瞻队列 meta | — |
| r14 | 铅 × 白内障 | metal | B | 10.1016/j.ijheh.2016.07.012 / 27460785 | 队列（NHANES 同库） | 补机制（晶体蛋白铅蓄积） |
| r15 | 镉 × 白内障 | metal | B | 同 r14（同文覆盖镉） | 队列 | 同 r14 |
| r16 | PM2.5 × IOP/CDR | vascular | B | 10.1186/s12989-021-00403-4 / 33663554 | 机制（动物/细胞） | 补 PM2.5-青光眼流行病学（F086/F060 池） |
| r17 | PM2.5 × AMD 早期 | inflammation | B | 10.1186/s12886-024-03465-y / 38684968 | meta 分析 | — |
| r18 | UV × 白内障 | photochemical | A | 10.1001/jama.2025.1597 / 40227658 | 临床综述 | 补经典流行病学（皮质性白内障-日照） |
| r19 | 促炎饮食 × NPDR | inflammation | C | 10.1016/j.jnha.2025.100694 / 41061592 | 横断面研究 | 补 DII-DR 第二源（新题量少，如实 C 级） |
| r20 | 吸烟 × VI（中/重） | oxidative | B | 10.1038/s41598-020-79865-z / 33432008 | 前瞻队列（尿可替宁客观） | severity 映射按原文 VI 定义核对 |
| r21 | PM2.5 × VI（中/重） | vascular | B | 10.1186/s12889-024-20853-7 / 39614249 | 前瞻队列 | 同上 |

## 明示空白（拒识指标口径）

- **类型 1（结构性，只报覆盖率）**：mercury_exposure × 任意 B；physical_inactivity × 任意 B
- **类型 2（证据性，abstain 只在此评估）**：physical_activity × glaucoma_*（方向混合 + 急性 Valsalva 分支三库无测量）

## 嵌套语义（方案二）

多规则命中 → 报告层 max(severity) + 最具体优先展示；指标层 (A,B) 对独立计分。r03⊃r04、r05/r06（early/late AMD）、r16/r20/r21（多 B flags）均按此实现。

## 患者因素升档规则（population subgroups）

diabetes / hypertension / chronic_kidney_disease / elderly——见 configs/rules.yaml `patient_factor_rules`。
