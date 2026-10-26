# Figure & Table QC Report (writer phase 7_1, v3.0)

- Date: 2026-10-23
- Overall: PASS ✅

| Check | Result | Detail |
|---|---|---|
| F1 | ✅ | 8 figure contracts found (expected ≥5) |
| F3 | ✅ | figure1: 3 panels parsed |
| F2 | ✅ | figure1 source_data outputs/figures/source_data/figure1_data.csv OK |
| F4 | ✅ | figure1: 2 rendered file(s) |
| F3 | ✅ | figure2: 4 panels parsed |
| F5 | ✅ | figure2 source_data carries dataset_id + dataset_role |
| F2 | ✅ | figure2 source_data outputs/figures/source_data/figure2_performance.csv OK |
| F4 | ✅ | figure2: 2 rendered file(s) |
| F3 | ✅ | figure3: 1 panels parsed |
| F2 | ✅ | figure3 source_data outputs/figures/source_data/figure3_rule_evaluation.csv OK |
| F4 | ✅ | figure3: 2 rendered file(s) |
| F3 | ✅ | figureS1: 4 panels parsed |
| F2 | ✅ | figureS1 source_data outputs/figures/source_data/figure4_demo_case.csv OK |
| F4 | ✅ | figureS1: 1 rendered file(s) |
| F3 | ✅ | figureS2: 3 panels parsed |
| F2 | ✅ | figureS2 source_data outputs/figures/source_data/figure5_reasoning_trace.csv OK |
| F4 | ✅ | figureS2: 1 rendered file(s) |
| F3 | ✅ | figure4: 1 panels parsed |
| F2 | ✅ | figure4 source_data outputs/figures/source_data/figure6_dose_response.csv OK |
| F4 | ✅ | figure4: 2 rendered file(s) |
| F3 | ✅ | figure5: 1 panels parsed |
| F2 | ✅ | figure5 source_data outputs/figures/source_data/figure7_power_mde.csv OK |
| F4 | ✅ | figure5: 2 rendered file(s) |
| F3 | ✅ | figure6: 2 panels parsed |
| F2 | ✅ | figure6 source_data outputs/figures/source_data/figure8_cohort_transportability.csv OK |
| F4 | ✅ | figure6: 2 rendered file(s) |
| T1 | ✅ | registry_summary.csv OK |
| T1 | ✅ | rule_list.csv OK |
| T1 | ✅ | performance_matrix.csv OK |
| T1 | ✅ | validation_distribution.csv OK |
| T1 | ✅ | dataset_summary.csv OK |
| T1 | ✅ | performance_by_dataset.csv OK |
| T2 | ✅ | 9 publication markdown tables |
| T3 | ✅ | dev-exposure-disease-pairs: declared n_cases=134 vs cases.jsonl=134 |
| T3 | ✅ | intval-nhanes: declared n_cases=110 vs cases.jsonl=110 |
| T3 | ✅ | extval-knhanes: declared n_cases=56 vs cases.jsonl=56 |
| T3 | ✅ | extval-cohorts-9: declared n_cases=14 vs cases.jsonl=14 |
| T4 | ✅ | all proportion metrics within [0,1] |
| T4 | ✅ | gap_<metric> rows present (internal vs external) |

---

**Author action required.** Review the figures and tables yourself.
If correct: `author_gate.py confirm --phase 7_1`.
If not: `author_gate.py reject --phase 7_1 --note "<what to fix>"`.

---

## 目视检查补充 — R21 图表重制（2026-10-23）

`verify_figures_tables.py` 每次整份重写本报告，故本节在每次重跑后重新追加。

### 重制范围

8 张图统一由 `scripts/render_top_figures.py` + `scripts/figure_style_top.py` 重绘：
统一 navy/teal/amber 语义色、Arial 7.5–9 pt 字阶、面板字母与标题分离、三线表式坐标轴、
去除旧版 4.6 pt 微型标签与页脚元数据条。旧 renderer 现仅转发到新 renderer，防止误跑回退。

### 数据完整性修复

- **Figure 2**：qwen 代 full_system 0.522；panel b 只用 80 对 R11 gold（6/0/11 与 0/2/61）。
- **Figure 3**：旧版只画 4 个指标并把"等级 A 复现率 0.00"误标为总体复现率；现画全部 6 个指标
  （declared、conservative、coverage、replication A / A+B / all），数值取自
  `figure3_rule_evaluation.csv`。
- **Figure 6**：r02·CLHLS 的 95% CI 上界 4.91 此前被 x 轴 4.0 截断；现轴延至 5.0，
  上界完整可见。
- **Figure 6 / S2 / Figure 1**：图例与契约同步到实际面板（per-rule composition、
  KG path、steps per layer、qwen 仲裁后端）。

### 验收

- 结构 QC：PASS（8 契约 / 9 表 / 源数据齐）。
- 美学视觉评审（独立 agent，顶级期刊标准）：**8/8 pass，评分 8–9**（Figure 1/3/4/5/6 为 9 分，Figure 2/S1/S2 为 8 分）；
  评审确认下列缺陷已修复：document glyph、矩阵填色可辨性、图 3 脚注、图 6 轴截断、
  S1 整数刻度、S2 死区与曲线箭头、单面板字母一致性。
- 投稿 Word 中 8 个图页（48–55）逐页视觉检查：**8/8 pass**，图像无裁切/变形，图注完整。

### 作者美术方向（第二轮）

按作者要求统一到 Figure 2 的四色（navy/teal/amber/brick + 单一中性灰），移除所有浅色
背景板与卡片边框，全部图背景改为纯白；进程框圆角降至 0.15，层标题改为色点 + 粗体文字。
图 2 配色保持不变。作者第二轮反馈后：Figure 3 增加四色指标族图例、赭色压暗、右面板提高对比度；
Figure 5 改为深蓝实心/浅灰空心以同时用填充与颜色编码状态；Figure 6 画布 112→132 mm；
稿件去中文（组稿仅保留英文，中文图例镜像不进入 manuscript）。

### 遗留的次要项（不影响投稿）

- Figure 2 矩阵填色仅作视觉辅助，计数已逐格标注；图注不依赖色阶。
- Figure 3 panel b 仅 4 个点，留白偏多，但它是两库 declared vs conservative 的对照，保留。
- Figure 7 两枚灰色空值点仍轻微相邻；已缩小标记，不遮挡读数。
