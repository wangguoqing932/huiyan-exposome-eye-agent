# Figure & Table QC Report (writer phase 7_1, v3.0)

- Date: 2026-10-15
- Overall: PASS ✅

| Check | Result | Detail |
|---|---|---|
| F1 | ✅ | 8 figure contracts found (expected ≥5) |
| F3 | ✅ | figure1: 3 panels parsed |
| F2 | ✅ | figure1 source_data outputs/figures/source_data/figure1_data.csv OK |
| F4 | ✅ | figure1: 2 rendered file(s) |
| F3 | ✅ | figure2: 1 panels parsed |
| F5 | ✅ | figure2 source_data carries dataset_id + dataset_role |
| F2 | ✅ | figure2 source_data outputs/figures/source_data/figure2_performance.csv OK |
| F4 | ✅ | figure2: 2 rendered file(s) |
| F3 | ✅ | figure3: 1 panels parsed |
| F2 | ✅ | figure3 source_data outputs/figures/source_data/figure3_rule_evaluation.csv OK |
| F4 | ✅ | figure3: 2 rendered file(s) |
| F3 | ✅ | figure4: 4 panels parsed |
| F2 | ✅ | figure4 source_data outputs/figures/source_data/figure4_demo_case.csv OK |
| F4 | ✅ | figure4: 2 rendered file(s) |
| F3 | ✅ | figure5: 3 panels parsed |
| F2 | ✅ | figure5 source_data outputs/figures/source_data/figure5_reasoning_trace.csv OK |
| F4 | ✅ | figure5: 2 rendered file(s) |
| F3 | ✅ | figure6: 1 panels parsed |
| F2 | ✅ | figure6 source_data outputs/figures/source_data/figure6_dose_response.csv OK |
| F4 | ✅ | figure6: 2 rendered file(s) |
| F3 | ✅ | figure7: 1 panels parsed |
| F2 | ✅ | figure7 source_data outputs/figures/source_data/figure7_power_mde.csv OK |
| F4 | ✅ | figure7: 2 rendered file(s) |
| F3 | ✅ | figure8: 2 panels parsed |
| F2 | ✅ | figure8 source_data outputs/figures/source_data/figure8_cohort_transportability.csv OK |
| F4 | ✅ | figure8: 2 rendered file(s) |
| T1 | ✅ | registry_summary.csv OK |
| T1 | ✅ | rule_list.csv OK |
| T1 | ✅ | performance_matrix.csv OK |
| T1 | ✅ | validation_distribution.csv OK |
| T1 | ✅ | dataset_summary.csv OK |
| T1 | ✅ | performance_by_dataset.csv OK |
| T2 | ✅ | 4 publication markdown tables |
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

## 目视检查补充（人工，2026-10-15）— 自动 QC 未覆盖的部分

> 本文件应**追加**在 `figure_table_qc_report.md` 之后。注意：`verify_figures_tables.py`
> 每次运行都会**整份重写** QC 报告，因此该脚本复跑后**必须重新追加本节**。
> 原始内容同时保存在 `outputs/paper/figure_visual_inspection.md`。

`verify_figures_tables.py` 检查的是**结构性**条件（契约数量、source_data 存在、
渲染产物存在、面板可解析、表格量纲范围）。它**无法**判断渲染出来的图是否
表达了契约声称的结论。本节是对新图 **figure8** 实际渲染结果的目视核验
（原则：*看了渲染再判断*、*看门人不是制作者*）。

### figure8 的三次迭代

| 版本 | 目视发现 | 处置 |
|---|---|---|
| v1（热图 + 森林） | ① 森林行标签**重复**：`… · SHARE · SHARE`（渲染器自动追加 ` · <dataset>`，而 `method` 里已含队列）<br>② 热图用渲染器默认的 sequential `Blues` → `contradicted`(-1) 与 `uninformative`(0) **几乎同色**，恰是契约明令禁止的（把无信息涂成某一极端） | 重设计 |
| v2（构成条 + 森林） | 标签重复已修；三态改为 `method` 前导 token → 按状态分色。但发现 ③ | 见下 |
| v3 | **③ 森林图既无 log 轴、也无 OR=1 参考线**：读渲染器源码确认，其 forest 分支**从不设置 `xscale('log')`、也从不传 `ref`**，落到 `make_forest_plot` 默认 `ref=0.0`——该线在绘图范围之外、**不可见** | P1 |
| v4（当前） | 项目内渲染器：真 log 轴 + OR=1 虚线 + 三态按**明度**也可分 | **P1 已解决** |

### P1（**已解决**——保留记录以留痕）

**figure8 面板 B 缺少 log 轴与空值参考线。**

- **为什么重要**：odds ratio 森林图若无 OR=1 参考线，读者无法判断方向；线性轴会
  压缩 <1 一侧区间，使保护向效应看起来比实际更极端。
- **为什么不在共享渲染器里修**：它位于
  `~/.dsh/skills/medical-agent-writer/scripts/build_figures.py`，**在工作区之外、
  沙箱只读，且跨项目共享**——为一个项目改它会波及其他项目。
- **实际处置（项目内渲染）**：新增 `scripts/render_manual_figures.py`，读取**同一份
  契约 source_data**，绘制真正的 **log 轴**、**OR=1 虚线空值线**，并以**明度也不同**
  的三色区分三态（灰度打印下仍可分辨）。导出规格与共享渲染器一致
  （180 mm、600 dpi、svg/pdf/tiff/png）。契约已加
  `renderer: scripts/render_manual_figures.py` 声明。
- **附带修复**：TIFF 改为 **LZW 无损压缩**，该图由 **57.5 MB → 1.03 MB**（−98%）。
  项目此前记录的"TIFF 合计约 590 MB"是同一问题，属投稿门户的实际障碍。
- **复验方式**：**目视检查渲染**并逐行核对数值——
  r02·CLHLS 3.59 [2.62,4.91]、r10·CLHLS 0.75 [0.64,0.87]、r13·SHARE 1.24 [1.20,1.29]，全部相符。

### 已核验通过（figure8）

- 18 对（6 规则 × 7 队列）全部出现，与 `cohort_rule_results.csv` 逐行一致
- 三态计数与来源一致：replicated 8 / uninformative 8 / contradicted 2
- 构成条计数逐条可核：r02 = 3+1、r10 = 1+2+1、r12 = 1+1、r13 = 1+1、r20 = 3+2
- r10 行同时出现 replicated（SHARE）与 contradicted（CLHLS）——**真实的方向翻转**，
  与契约预先声明一致，非渲染故障
- 无占位符、无编造数据；不可检验的 15 条规则**不出现**（而非以空值出现）

### 结论

**自动 QC：PASS。人工目视：PASS。P1 已解决。**

**未解决项：无。** 但保留一条**共享工具缺陷记录**（非本项目问题）：
`build_figures.py` 的 forest 分支缺少 `log_x` / `ref` 钩子，因此**任何**项目用它画
odds ratio 森林图都会缺失空值线。**F7（效能 / MDE 图）受同一缺陷影响**——
本轮的项目内渲染器已为其预留接入点，但尚未实现，记为后续项。
---

## figure7（效能/MDE 图）——同一缺陷，另加三处目视问题

figure7 与 figure8 受**同一个共享渲染器缺陷**影响，但需要的修复不同：它画的是
**最小可检出 OR（x）vs 观测 OR（y）**，因此**identity 线 y = x 是全部解释力的来源**
（点在线**上**方 = 该研究本可检出自己观测到的效应；在线**下**方 = 检不出）。
共享渲染器的 scatter 分支只支持**单条横/竖** 
eference_line，**无法画对角线**。

| 版本 | 目视发现 | 处置 |
|---|---|---|
| v1（共享渲染器） | 双线性轴、无 identity 线、无 OR=1 参考线。MDE 1.10–2.27 × OR 0.60–15.14 在线性轴上**全挤进一角** | 项目内渲染 |
| v2（项目内首版） | ① y = x 标签**飘在右上角空区**（我放在固定数据坐标 (9,11)，但可见斜线只到 x=2.6，标签指向空处）<br>② x 轴刻度为科学计数法 1.2 × 10⁰ | 见下 |
| v3 | ① 已修：标签**贴在斜线上**，并按**对数轴上的实际屏幕斜率**旋转（log-log 下该斜率**不是 45°**，不能用常数）<br>② **仍为科学计数法**——因为跨度不足一个数量级时，matplotlib 标注的是**次刻度**，只设 major formatter 压不住 | 见下 |
| v4（当前） | ② 已修：显式设刻度 + set_minor_formatter(NullFormatter()) | ✅ |

### 已核验通过（figure7）

- y = x 虚线正确（可见段自 (0.95,0.95) 至 (2.6,2.6)，在对数 y 轴上位于约 48% 高度）
- OR=1 双向点线参考线齐备
- x 刻度为普通小数（1, 1.2, …, 2.6）
- **科学模式可见且符合预期**：replicated 点（红）**聚在斜线上方**，
  uninformative 点（灰）**聚在斜线上或下方**——即在有检验力的地方才复现

### 契约修复过程中的一次自伤（已修）

给 figure7 契约插入渲染器声明时，**注释里的反引号被 PowerShell 当作转义符**，
` 
 ` 变成回车，把 
eference_line 断成 
eference_line，
导致 **YAML 不可解析、7_1 QC 整份 FAIL**。
已修正并用 yaml.safe_load 复验通过。
→ **教训：PowerShell here-string 中反引号是转义字符，不得用来排版反引号代码；
YAML/JSON 等结构化文件的写入应使用文件编辑工具，不要经 shell 引号层。**

### figure7 / figure8 的 TIFF（附带收益）

| 图 | 共享渲染器 | 项目内渲染器（LZW） |
|---|---|---|
| figure7 | 90.9 MB | **0.52 MB** |
| figure8 | 57.5 MB | **0.73 MB** |

其余 6 张仍为无压缩 TIFF（合计约 590 MB），修法与命令见
outputs/paper/KNOWN_ISSUES_figure_export.md。
