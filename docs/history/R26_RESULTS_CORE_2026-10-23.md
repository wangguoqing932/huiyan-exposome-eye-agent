# R26 Results 核心结果补全（2026-10-23）

## 触发

作者指出：摘要 Methods 列了五个验证目标（系统分类、工作界面与可追溯性、八队列可转运性、预注册三态标准下的规则方向、四库独立一致性）和四个独立性层级（134 对开发集、NHANES 内部、KNHANES/CHARLS 外部、八队列），但 Results 没有逐项给出核心结果，读起来像一堆 “uninformative”。

## 诊断

1. Results 开头直接进入 “The internal layers”，没有一个把五个目标与核心数字对上的总览。
2. 四个层级混在 “four waves” 里，开发集只写 “used only for rule construction”，没有明确说它不产生独立性能估计；KNHANES 的 301/352 与 “50 underpowered” 差 1，未解释那 1 对是 non-estimable。
3. 界面/可追溯性只有最后一句 “Every reported case resolved…”，没有界面结果和七步案例。
4. 文献段把四个精度写成 “(0.889, 0.916, 0.922 and 0.800)”，没有逐库点名 PubMed/WoS/EPMC/CNKI。
5. 规则方向散在内部层和八队列两节，没有一个跨层级的合计。

## 改动

### 1. 新增 `## Core results by validation target`

在 Results 开头、三态标准说明之后，用一段把五个目标的核心结果逐项写出：

- **系统分类**：full agent 在三个矩阵均排第一，F1 = 0.522（NHANES Qwen）、0.480（NHANES GLM-5.3-flash）、0.360（KNHANES）；基线区间分别为 0.080–0.392、0.069–0.186、0.094–0.145。
- **界面与可追溯性**：一个七步工作案例，三层记录，所有输出落到 rule/KG/source chunk；同一报告在 Streamlit 界面呈现。
- **八队列可转运性**：21 条规则中 6 条可测；18 个 rule × cohort 对中 8 复证、8 无信息、2 反证；两条过预注册标准的规则 PI 均跨 null。
- **规则方向**：三个调查层级合计 11 复证 / 0 反证 / 24 无信息；八队列 8 复证 / 2 反证 / 8 无信息。
- **四库独立一致性**：0.889（PubMed）、0.916（WoS）、0.922（Europe PMC）、0.800（CNKI）。

### 2. 四层级显式标注

`## The internal layers` 改为 `## Development, internal and external validation`，并把四层写全：

- 134 对开发集：只用于规则构建，因此不提供独立性能估计；
- 110 对 NHANES：内部验证；
- 56 对 KNHANES + 14 对 CHARLS 2011：外部验证；
- 八队列：外部验证，下一节详述。

同时把 “Testable pairs were 159/180…” 改为 pair-level 表述，并补 “301 + 50 + 1 non-estimable = 352” 的分母说明，避免 301/352 与 50 对不上。

### 3. 系统性能与文献段补核心句

- System performance 末补 “The full agent ranked first in all three matrices.”
- Literature-index validation 改为逐库点名：PubMed 0.889；WoS 100 篇/2 规则，0.916；Europe PMC 521 篇/21 查询/17 informative，0.922；CNKI 8 规则，0.800。

### 4. 界面与可追溯性扩写

`## Evidence traceability` 改为 `## Interface and evidence traceability`，写入七步案例的实际内容：规则层 4 步（两次规范化、match r04、cross-cover r03）、LightRAG 1 步、arbiter/report 2 步；最终报告同时给出两条命中规则和各自证据 chunk；同一报告在 Streamlit 界面呈现 clinician card / patient handout / research table / policy brief。明确这是 operability，不是 clinical usability 或 deployment。

## 数字与验收

- `manuscript.md`：102,963 B。
- 正文 7,102 词（Intro 608 / Methods 1,616 / Results 2,556 / Discussion 1,879）；abstract 406 词。
- Word/PDF：46 页，0 中文；摘要仍收在 page 2，Introduction 从 page 3 开始。
- `qc_english_manuscript.py`：20/20 PASS。
- `verify_results_numbers.py`：70/70 PASS。
- `polish_bilingual.py --check-only`：OK；`manuscript.md` 与 `.en.md` 逐字节相同。
- 9 表 + 8 图未变；Figure 2 双代分组柱与 80 对 R11 gold panel b 未动。

## 门与文件

- 7_4（Results）与 7_8（装配稿）因 R26 变化按硬门重新提交，待作者确认；7_7 仍为 R25 后的待确认状态。
- `manuscript_agent_first.pdf` 曾被 WPS PDF（PID 20516）占用；已关闭该查看器进程并重建 canonical PDF，`manuscript_agent_first_R25*` 等重复文件已删除。
- 当前只保留：`manuscript.md` / `.en.md`、`manuscript_agent_first.docx`、`manuscript_agent_first.pdf`。
