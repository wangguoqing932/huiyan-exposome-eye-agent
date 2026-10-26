# R28 全文按 skill 重写（2026-10-23）

## 触发

作者要求“全文都重写，按照 skill 的要求”。此前只重排了 Results；Introduction、
Methods、Discussion 仍是主题式写法，不符合
`medical-agent-writer/references/imrad_playbook.md` 的结构要求。

## 规范依据

- Results：dataset-centric 八段（architecture → development → internal →
  external + generalization gap → expert agreement → case → reasoning trace →
  sensitivity）。
- Methods：study design → data sources → validation datasets（逐库）→ rule
  engine → LightRAG → LLM arbiter → validation phases/baselines → statistical
  analysis → construct substitutions/deviations → ethics。
- Introduction：gap → prior art → approach → contribution → paper outline。
- Discussion：main finding → mechanism → comparison with prior art →
  limitations（逐层 independence axis + generalization gap）→ future work →
  Conclusion（3–4 句，不加新 claim）。
- 数字只能来自 outputs CSV；per-dataset 不报 pooled-only。

## 重写内容

### Introduction（667 词）

五段：视觉丢失与可改变暴露的临床价值；exposome 证据异质性；规则型 CDS 的
可检查性与“聚合性能下降”不足以定位失败组件；Huiyan 三层与五个验证目标/
四个独立性层级；三项贡献与全文 outline。保留 C016、C021–C023、C020、C018。

### Methods（1,574 词）

十段：研究设计与报告标准；数据来源与四个验证数据集（development、NHANES
internal、KNHANES/CHARLS external、八队列 population）；rule engine；LightRAG
（1,060 chunks、top-k = 5、6,000-char context、doubao-embedding-vision-251215、
2,048 维）；LLM arbiter（Qwen3.8-27B / GLM-5.3-flash、temperature 0、bounded、
可 abstain、provider 非确定性）；validation phases 与三条 baseline；统计
（三态、BY、Clopper-Pearson、survey variance、power/MDE、REML/Q/I²/PI、
E-value、positive control、construct validation）；construct substitutions 与
protocol deviations；ethics。保留 C001–C015、C031–C033 等引用。

### Results（2,890 词）

保持 R27 的 dataset-centric 结构；开头补“三态标准下 sensitivity/specificity
不可识别、κ 不适用”的方法学说明；四层逐库报告；external 段补
generalization gap（coverage 0.007、precision 0.000）；case 段用 Figure S1
（OR 1.60、q = 1.3 × 10⁻²、r04 + r03、B×2/C×1、risk low→medium）；trace 段用
Figure S2 七步；sensitivity/heterogeneity/power 收在最后。

### Discussion（2,065 词）

七段：Main finding（强 agent + 规则不转运）；Why the agent performs well
（架构而非模型规模；standalone stronger LLM precision 0.10）；Why the rules do
not transport（6/21、18 对 8/8/2、18/168 feasible、r02 替代、1.36–19.14%）；
direction reversal / pooled estimate / positive control 与 outcome construct
作为 mechanism 的子节；Comparison with prior art（TRIPOD+AI、DECIDE-AI、
rule-based CDS、KG/LLM agents）；Limitations（逐层 independence axis +
generalization gap，及 self-report、cross-sectional、power、construct
substitutions、single-cohort rules、usability、expert panel、CLHLS severe
vision）；Future work（fundus imaging +15、blood assays +13、geocoded +13；
prospective cohort；expert panel；usability trial）；Conclusion 四句，不加新
claim。

## 一致性修正

- “Four explanations remain”改为“Three explanations remain”：原文已把
  “one cohort, not a region”单列，后续只剩 selective survival、confounding、
  subtype 三种。
- “r11 and r13 rest on one and two cohorts respectively”改为“each rest on one
  cohort”：Results 明确 r13 只在 SHARE 复证，CRELES 未复证，原句与 Results
  矛盾。

## 验收

- `manuscript.md`：107,603 B。
- 正文 7,692 词（Intro 667 / Methods 1,574 / Results 2,890 / Discussion
  2,065）；abstract 402 词。
- Word/PDF：48 页，0 中文；摘要仍收在 page 2，Introduction 从 page 3 开始。
- `qc_english_manuscript.py`：20/20 PASS。
- `verify_results_numbers.py`：70/70 PASS。
- `polish_bilingual.py --check-only`：OK；`manuscript.md` 与 `.en.md`
  逐字节相同。
- References 27 条；10 表 + 8 图未变。

## 门与文件

- 7_5（Methods）、7_6（Introduction）、7_7（Discussion）、7_8（装配稿）因
  R28 全文重写按硬门重新提交，待作者确认；7_4 保持 R27 的 Results 状态。
- 当前只保留：`manuscript.md` / `.en.md`、`manuscript_agent_first.docx`、
  `manuscript_agent_first.pdf`。
- 未投稿；未向任何期刊发送材料。
