# Ethics Narrative — 慧眼 (huiyan)

> **Purpose**: IRB cover narrative, grant application ethics section, source for manuscript Methods → Ethics subsection
> **Created**: 2026-10-11
> **Version**: v1.0 (scaffold-generated; PI review and signature required before submission)
> **Companion docs**: [IRB_Protocol_Summary.en.md](IRB_Protocol_Summary.en.md) | [Data_Management_Plan.en.md](Data_Management_Plan.en.md) | [Informed_Consent.en.md](Informed_Consent.en.md) | [Manuscript_Ethics_Statement.en.md](Manuscript_Ethics_Statement.en.md)

---

## 1. Study Overview

### 1.1 Title

慧眼: A rule-engine + knowledge-graph + LLM-arbiter decision support system for 暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证 screening

### 1.2 Study Design

- **Design**: Retrospective case series + literature evidence review + public database analysis
- **Data sources**:
  - Primary: NHANES 1999-2008 本地原始库（生化/膳食/毒物 + VIX 客观视力 / OPXRET 视网膜分级 / VIQ 眼病问卷）[local_confirmed], KNHANES 1998-2024 本地 Rdata 全集 + 官方变量字典（眼科检查模块，1,686 眼科变量）[local_confirmed], 9 大老龄队列原始库（CHARLS/HRS/ELSA/SHARE/KLoSA/LASI/MHAS/CRELES/CLHLS）[local_confirmed], GBD 视觉库（GBD 2023 近视力丧失 / 2023 盲与视力损害 / 2021 55+ 暴露-结局）[local_confirmed]...
  - Clinical: Retrospective cases from partner hospital (n = 60)
  - Public: NHANES 1999-2008 本地原始库（生化/膳食/毒物 + VIX 客观视力 / OPXRET 视网膜分级 / VIQ 眼病问卷）[local_confirmed], KNHANES 1998-2024 本地 Rdata 全集 + 官方变量字典（眼科检查模块，1,686 眼科变量）[local_confirmed], 9 大老龄队列原始库（CHARLS/HRS/ELSA/SHARE/KLoSA/LASI/MHAS/CRELES/CLHLS）[local_confirmed], GBD 视觉库（GBD 2023 近视力丧失 / 2023 盲与视力损害 / 2021 55+ 暴露-结局）[local_confirmed], PubMed E-utilities（NCBI_API_KEY 已配置，10 req/s）[confirmed_public_key_available], AAO PPP 免费全文 PDF（POAG/AMD/DR 三册，代理通道 2026-09-27 实测可下载）[confirmed_public_proxy_path], Crossref + OpenAlex（引用交叉验证双源）[confirmed_public], GBD 官方数据门户（burden 补充与更新）[confirmed_public]
- **Intervention**: **None** (modeling only; no prospective intervention)
- **Follow-up**: **None**

### 1.3 Research Question

在中老年人群中，代谢（尿酸/血糖/HbA1c/血脂/CRP）、营养（维生素D/抗氧化营养素/膳食模式）、生活方式（吸烟/饮酒/体力活动/BMI）与环境（重金属/空气污染）暴露及其组合，与主要眼科疾病之间存在哪些有临床意义的关联与交互？这些暴露-眼病关系能否被规则+知识图谱+LLM 混合系统以可解释、可溯源的方式筛查、分级，并在 NHANES / KNHANES / 9 国老龄队列上完成多层独立验证？

### 1.4 Expected Benefits

- **Individual**: Provides elderly with traceable, explainable decision support for 暴露组（代谢-营养-生活方式-环境） × 主要致盲眼病 interactions
- **Population**: Promotes 主要致盲眼病 risk management; reduces 暴露组（代谢-营养-生活方式-环境）-related adverse outcomes
- **Scientific**: First A×B matrix screening system combining rule engine + KG + LLM arbiter for this domain

---

## 2. IRB / Ethics Review Pathway

### 2.1 Review Type

- [x] **Expedited Review** (for minimal-risk retrospective studies)
- [ ] Exemption
- [ ] Full Board Review

### 2.2 Applicable Regulations

- **Declaration of Helsinki** (2013)
- **CIOMS International Ethical Guidelines** (2016)
- **Belmont Report** (1979)
- China: **Measures for Ethical Review of Biomedical Research Involving Humans** (2016); **PIPL** (2021); **Health Big Data Management Measures** (2018)
- US (if applicable): 45 CFR 46 (Common Rule); HIPAA Privacy Rule

### 2.3 IRB Committee Information

- **Committee**: [TODO: irb_committee_name]
- **Institution**: [TODO: hospital_name]
- **Committee ID**: [TODO: irb_committee_id]
- **Contact**: [TODO: irb_contact_name] / [TODO: irb_contact_email] / [TODO: irb_contact_phone]
- **Submission date**: [TODO: submission_date]
- **Expected approval**: [TODO: expected_approval_date]

### 2.4 Investigators

- **PI**: [TODO: pi_name] ([TODO: pi_title], [TODO: pi_department])
- **Contact**: [TODO: pi_email] / [TODO: pi_phone]
- **Co-investigators**: [TODO: coinvestigator_names]
- **Data manager**: [TODO: data_manager_name]
- **Statistician**: [TODO: statistician_name]

---

## 3. Human Subjects Protection

### 3.1 Risk Classification

This study is **Minimal Risk** per 45 CFR 46.110:

- **Description**: Retrospective chart review only; no intervention, no invasive procedures, no prospective contact
- **Level**: No greater than daily life risk
- **Primary risk sources**:
  1. **Privacy breach (PHI)** — see §4 mitigations
  2. **Model misclassification** — see §6 mitigations
  3. **Stigmatization of subtypes** — see §5 mitigations

### 3.2 Risk Minimization

| Risk | Mitigation |
|---|---|
| PHI breach | See [Data_Management_Plan.en.md](Data_Management_Plan.en.md) §3 de-identification |
| Model misclassification | LLM is **decision support only**; clinical judgment remains with physician |
| Stigmatization | Limitations section notes "subtype labels are not identity markers" |
| Re-identification | Public datasets use aggregated stats only; individual-level data never published |

### 3.3 Benefit Maximization

- All A×B screening outputs **free and open-source** to clinical partners
- 4 report views (clinician / patient / research / policy) directly usable for patient education

---

## 4. Data Protection & Privacy

### 4.1 Data Flow

```
[Public databases] ─────┐
                        ├──→ [Huanyu server] ──→ [De-identified evidence store] ──→ [LightRAG index]
[Hospital EMR] ─────────┘
                        ↑
                        └─ De-identified (HIPAA Safe Harbor) before transfer
```

### 4.2 Data Types

- **PHI**: Processed within partner hospital; de-identified before transfer
- **De-identified data**: Uploaded to research server for modeling
- **Public data**: CTD, ToxCast, etc. (no PHI)

### 4.3 De-Identification Standard

HIPAA Safe Harbor 18 identifiers (45 CFR 164.514(b)(2)(i)) — see [Data_Management_Plan.en.md](Data_Management_Plan.en.md) §3.

### 4.4 Storage & Access

- **Location**: 本地工作站（原始库 E:\BaiduNetdiskDownload\所有数据库 只读；分析工程 D:\Desktop\眼科公共数据库agent搭建） (institution-controlled server or encrypted cloud)
- **Access**: RBAC, least-privilege principle
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Backup**: Daily incremental, weekly full, retained 6 months
- **Audit logs**: All data access logged, retained 5+ years

---

## 5. Vulnerable Populations

### 5.1 Potential Vulnerable Groups

| Group | Protections |
|---|---|
| **Pregnant women** | No direct intervention; ICH E8(R1) handling of pregnancy data |
| **Pediatric patients** (if any) | Age-stratified analysis; no individual < 18 identification |
| **Infertility patients** (sensitive identity) | Public reports use aggregated stats only |
| **Occupational exposure groups** | Data isolated from employer; not used for employment decisions |

### 5.2 Equity Considerations

- **Inclusion**: All eligible cases at partner hospital; no discrimination by sex / race / socioeconomic status
- **Subgroup analysis**: Stratified performance by sex, age band, geographic region
- **Generalizability**: Limitations section notes "training data may be biased toward Chinese Han population"

---

## 6. AI / Algorithmic Transparency

### 6.1 System Positioning

**Huanyu is a decision support system, not a diagnostic device**:
- Output: Graded risk report + evidence chain + recommendations
- **Final authority**: Clinical physician
- **Use**: Clinical consultation, patient education, research hypothesis generation; **not** autonomous diagnosis or automated decision-making

### 6.2 Explainability

| Layer | Explanation |
|---|---|
| Rules | YAML configuration public; each rule has rationale + citation |
| Retrieval | KG path visualizable; evidence chunks clickable to source |
| Arbiter | LLM output with prompt + response log; not black-box |

### 6.3 Model Version & Reproducibility

Locked models:
- `deepseek-v4-flash` (DeepSeek; knowledge graph construction)
- `doubao-embedding-vision-251215` (Volcengine Ark; vector indexing, dim=2048)
- `gpt-4-turbo-2024-04-09` (OpenAI; final report arbitration)

All LLM calls logged: `{input, output, model_version, timestamp, token_count}`, retained 5+ years.

### 6.4 Bias & Limitations

- **Training data bias**: DeepSeek / GPT-4 trained primarily on English-language / Western medical literature; may bias Chinese clinical context
- **Mitigation**: Rule engine as "grounding" constrains LLM; validation on Chinese retrospective cases (n=200) with sens/spec
- **Disclosure**: Methods + Limitations sections explicitly state

### 6.5 Reporting Frameworks

- [x] **TRIPOD-AI**: AI prediction model reporting
- [x] **DECIDE-AI**: Early-stage AI clinical evaluation
- [ ] CONSORT-AI (not RCT; n/a)
- [ ] SPIRIT-AI (not protocol; n/a)

---

## 7. Informed Consent (If Applicable)

### 7.1 Retrospective Study (Huanyu Default Pathway)

Per 45 CFR 46.116(f) / China Ethical Review Measures Article 32, **informed consent waiver is requested** for retrospective chart review, satisfying:

- [x] Research involves ≤ minimal risk
- [x] Waiver does not adversely affect subject rights/welfare
- [x] Research cannot be completed without PHI contact (after de-identification)
- [x] Subjects cannot reasonably be notified post hoc (records archived)

### 7.2 Prospective Extension

If project extends to prospective (e.g., new case follow-up, biospecimen collection), **written consent is mandatory** using [Informed_Consent.en.md](Informed_Consent.en.md).

---

## 8. Data Sharing & Publication

### 8.1 Sharing

- **Code**: GitHub open-source (MIT or Apache 2.0)
- **De-identified data**: Zenodo / OSF with DOI (after IRB approval)
- **PHI**: **Never publicly shared**; DUA-based access for replicators
- **LLM logs**: PI-controlled retention 5 years; then destroyed

### 8.2 Publication Ethics

- **Authorship**: ICMJE 4 criteria; contributions via CRediT (see [Manuscript_Ethics_Statement.en.md](Manuscript_Ethics_Statement.en.md))
- **AI use disclosure**: Per ICJME 2023, disclose LLM use in Methods (model + version + purpose)
- **Preprints**: medRxiv / bioRxiv allowed; does not affect journal submission
- **Misconduct**: COPE guidelines

---

## 9. Adverse Events / Security Incidents

### 9.1 Adverse Events (Prospective Only)

Not applicable (retrospective, no intervention).

### 9.2 Security Incidents

| Type | Response | Notification |
|---|---|---|
| PHI breach | Within 24h | IRB + Hospital InfoSec + Affected individuals |
| Unauthorized access | Within 48h | IRB + PI + Institutional DPO |
| Data corruption/loss | Within 72h | PI + Backup recovery |
| Algorithmic failure | Within 7d | IRB + Journal (if published) |

### 9.3 Contingency Plan

- Breach: Immediate access revocation, system isolation, forensics
- Severe LLM error: Pause system use, assess impact, notify clinical users

---

## 10. Conflict of Interest

### 10.1 Financial COI

- **Investigators**: 无
- **Funder**: 无 — **no role** in study design, data collection, analysis, publication decisions
- **LLM providers**: DeepSeek / OpenAI / Volcengine Ark — tool providers only, no research funding relationship

### 10.2 Non-Financial COI

Academic reputation, publication pressure, IP, etc.

### 10.3 Management

All COI **fully disclosed** in submission, IRB application, and public presentations.

---

## 11. Post-Approval Oversight

### 11.1 Amendments

Any protocol change (data sources, PI, scope, AI models) requires IRB amendment review.

### 11.2 Continuing Review

Per IRB requirements, typically annual progress report.

### 11.3 Closure Report

Within 90 days of study completion; data destruction/archival per DMP §6.

---

## 12. PI Signature

I have reviewed this ethics narrative, confirm all information is accurate, and will conduct the study in strict accordance with this protocol.

**PI signature**: ____________________  **Date**: ____________________

**IRB Chair signature** (post-approval): ____________________  **Date**: ____________________

---

## Appendix: References

1. World Medical Association. Declaration of Helsinki (2013). JAMA, 310(20), 2191-2194.
2. National Commission. The Belmont Report (1979).
3. CIOMS. International Ethical Guidelines for Health-related Research Involving Humans (2016).
4. China NHFPC. Measures for Ethical Review of Biomedical Research Involving Humans (2016).
5. NPC of China. Personal Information Protection Law (PIPL, 2021).
6. Collins GS, et al. TRIPOD+AI statement. BMJ (2024).
7. Sounderajah V, et al. CONSORT-AI. Nature Medicine (2020).
