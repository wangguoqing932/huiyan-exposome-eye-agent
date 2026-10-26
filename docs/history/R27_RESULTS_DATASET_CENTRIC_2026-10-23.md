# R27 Results dataset-centric 重排（2026-10-23）

## 触发

作者要求先读 `medical-agent-writer` 的写作规范。重读
`references/imrad_playbook.md` 后确认，Results 的硬结构是 dataset-centric：

1. System architecture (Figure 1) — brief
2. Development-set consistency (Phase 1)
3. Internal validation (Figure 2) — per-dataset metrics vs baselines
4. External validation + generalization gap (Figure 2 gap panel) — headline
5. Expert agreement (Figure 3) — Fleiss κ + Likert
6. Case demonstration (Figure 4) — one worked example
7. Reasoning trace (Figure 5) — interpretability
8. Sensitivity / subgroup analyses

硬规则：Results 每个数字必须能回到 outputs CSV；per-dataset 指标逐库报告，
不能只报 pooled。当前稿子不符合：缺 architecture/development/case 段；
external 没写 generalization gap；expert panel 没交代；规则方向被汇总成
跨层合计；界面/追溯只有一句。

## 改动

### 结构

Results 现为：

1. `## System architecture`（Figure 1，简短）
2. `## Core results by validation target`（作者要求的五目标总览）
3. `## Development-set consistency`（134 对，仅构建规则，不产生独立估计）
4. `## Internal validation in NHANES`（rule-level 16 对 6/0/10；system-level
   qwen 0.522、zhipu 0.480；Figure 2/4）
5. `## External validation in KNHANES and CHARLS`（KNHANES 15 对 5/0/10；
   system 0.360；CHARLS 4 对全 uninformative；generalization gap 0.007/0.000）
6. `## Cross-cohort transportability across eight ageing cohorts`（6/21 可测；
   18 对 8/8/2；positive control；outcome construct）
7. `## Expert agreement and independent literature-index validation`
   （明确 expert panel 未做；四库 0.889/0.916/0.922/0.800）
8. `## Case demonstration`（Figure S1：hba1c_elevated × dr_pdr，OR 1.60，
   q = 1.3 × 10⁻²，r04 + r03，B×2/C×1，risk low→medium）
9. `## Reasoning trace and interface`（Figure S2：七步，Rule 4 / KG 1 /
   Arbiter 2；Streamlit；operability 非 clinical usability）
10. `## Sensitivity, heterogeneity and power`（异质性、不可测审计、探索性、
    power 全部收在最后）

### 关键修正

- 规则方向改为逐库：NHANES 6/0/10；KNHANES 5/0/10；CHARLS 0/0/4；八队列
  8/2/8。不再只报“三层合计 11/0/24”。
- 补 internal→external generalization gap：coverage 0.007（0.889 vs 0.882），
  declared-domain precision 0.000（1.00 vs 1.00），CI 均宽且重叠。
- 补 KNHANES 301 + 50 + 1 non-estimable = 352 的分母说明。
- 补“三态标准下 sensitivity/specificity 不可识别”的方法学说明；rule-level
  用 precision/coverage，system-level 用 F1。
- 补 Figure S1 病例与 Figure S2 七步 trace 的具体数字；所有数字来自
  `outputs/figures/source_data/figure4_demo_case.csv`、
  `figure5_reasoning_trace.csv`、`outputs/tables/performance_by_dataset.csv`
  与 `performance_matrix.csv`。

## 验收

- `manuscript.md`：104,933 B。
- 正文 7,433 词（Intro 608 / Methods 1,616 / Results 2,855 / Discussion
  1,879）；abstract 406 词。
- Word/PDF：47 页，0 中文；摘要仍收在 page 2，Introduction 从 page 3 开始。
- `qc_english_manuscript.py`：20/20 PASS。
- `verify_results_numbers.py`：70/70 PASS。
- `polish_bilingual.py --check-only`：OK；`manuscript.md` 与 `.en.md`
  逐字节相同。
- 9 表 + 8 图未变；Figure 2 双代分组柱与 80 对 R11 gold panel b 未动。

## 门与文件

- 7_4（Results）与 7_8（装配稿）因 R27 重排按硬门重新提交，待作者确认；
  7_7 仍为 R25 后的待确认状态。
- 当前只保留：`manuscript.md` / `.en.md`、`manuscript_agent_first.docx`、
  `manuscript_agent_first.pdf`。
- 未投稿；未向任何期刊发送材料。
