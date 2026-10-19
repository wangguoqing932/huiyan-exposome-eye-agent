# Schematic Figure Prompts (writer phase 7_3, v3.0)

BioRender-style prompts for AI image generation of the project's schematic
figures (Figure 1 architecture flowchart, Figure S2 reasoning trace). Two model
variants are provided — pick per the author's available tools, iterate, and paste
final renders into `outputs/figures/manual/` for the figure-assembly step.

## 1. Figure 1 — System architecture flowchart

### Variant A — Nano Banana (Gemini image generation)

**Main prompt (English):**

> Create a horizontal scientific workflow flowchart in BioRender style for a clinical decision-support system named "huiyan". Left column: input panel showing two entity types — the exposome (metabolic, nutritional, lifestyle and environmental exposures) and major blinding eye diseases — entering the system. Center: three stacked processing layers connected by downward arrows: (1) a deterministic rule engine layer with a checklist icon, (2) a knowledge-graph retrieval layer (LightRAG) with a network-graph icon, (3) an LLM arbiter layer with a balanced-scale icon. Right column: output panel showing a color-coded 4-level risk report (high=red, medium=orange, low=green, unknown=gray) with a document icon. A small validation loop arrow returns from output to the rule engine, labeled 'expert feedback'. flat vector illustration, BioRender scientific figure style, soft medical color palette (muted blues, teals, warm grays), uniform rounded icons, clean sans-serif labels, generous white space, consistent stroke width, no gradients, no shadows, no 3D, no photorealism. All labels in English, large enough to read at single-column width.

**Negative prompt:**

> photorealistic, 3D render, gradient mesh, drop shadows, cluttered layout, tiny illegible text, watermarks, stock-photo look, cartoonish mascots, rainbow colors, inconsistent icon styles

**Suggested parameters:** aspect ratio 16:9 (or 3:2 for double-column);
highest available resolution; "style: flat illustration" if the UI offers it.

### Variant B — image2 (即梦 / Doubao Seedream-style)

**主提示词（中文）：**

> 请用 BioRender 科研插图风格绘制一张横向流程图，展示名为「慧眼」的临床决策支持系统。左侧：输入面板，两类实体——exposome (metabolic, nutritional, lifestyle and environmental exposures)与major blinding eye diseases——进入系统。中间：三层处理结构，用向下箭头连接：（1）确定性规则引擎层（清单图标），（2）知识图谱检索层（LightRAG，网络图图标），（3）LLM 仲裁层（天平图标）。右侧：输出面板，展示四级风险报告（高危=红、中危=橙、低危=绿、未知=灰）与文档图标。一条从输出回到规则引擎的回路箭头，标注「专家反馈」。扁平矢量插画、柔和医学配色（雾霾蓝、青绿、暖灰）、统一圆角图标、清晰无衬线标签、留白充分、描边一致；不要渐变、不要阴影、不要 3D、不要照片写实。所有标签使用中文，字号在单栏宽度下清晰可读。

**负面提示词：**

> photorealistic, 3D render, gradient mesh, drop shadows, cluttered layout, tiny illegible text, watermarks, stock-photo look, cartoonish mascots, rainbow colors, inconsistent icon styles

**建议参数：** 画幅 16:9（双栏图可用 3:2）；最高分辨率；风格选「扁平插画」。

## 2. Figure S2 — Three-layer reasoning trace

Figure S2 shows HOW a single conclusion is produced and audited, so its job is
traceability rather than architecture: three swim-lanes, one per layer, with the
hand-off between them visible.

### Variant A — Nano Banana (Gemini image generation)

**Main prompt (English):**

> Create a horizontal swim-lane diagram in BioRender style for a clinical
> decision-support system. Three stacked lanes labelled "Rule engine", "Knowledge
> graph (LightRAG)" and "LLM arbiter", arranged top to bottom. Time flows left to
> right within each lane. Each lane holds a row of rounded step nodes connected by
> right-pointing arrows; every node carries a short input and output label. A
> vertical hand-off arrow drops from the last node of one lane into the first node
> of the lane below, so the reader sees the chain rule signal to KG path to LLM
> arbitration. A thin side rail on the right collects a small numbered audit-tag
> badge from each node into a "trace log" document icon, making the audit trail
> explicit. Below the lanes, a compact horizontal stacked bar shows the relative
> time cost of the three layers with a legend reading "Rule / KG / LLM", the LLM
> segment visibly the largest. To the right of that, a small network graph: nodes
> for the two query entities plus intermediate concepts, edges for retrieved
> paths, and edge thickness varying with retrieval frequency. flat vector
> illustration, BioRender scientific figure style, soft medical palette (muted
> blues, teals, warm greys), uniform rounded icons, clean sans-serif labels,
> generous white space, consistent stroke width, no gradients, no shadows, no 3D,
> no photorealism. All labels in English, legible at single-column width.

**Negative prompt:**

> photorealistic, 3D render, gradient mesh, drop shadows, cluttered layout, tiny
> illegible text, watermarks, stock-photo look, cartoonish mascots, rainbow
> colors, inconsistent icon styles

**Suggested parameters:** aspect ratio 16:9; highest available resolution;
"style: flat illustration" if offered.

### Variant B — image2 (即梦 / Doubao Seedream-style)

**主提示词（中文）：**

> 请用 BioRender 科研插图风格绘制一张横向泳道图，展示一个临床决策支持系统如何得出并留痕一条结论。由上至下三条泳道，分别标注「规则引擎」「知识图谱（LightRAG）」「LLM 仲裁」。每条泳道内时间自左向右流动，依次排列圆角步骤节点，节点间以右向箭头连接，每个节点带简短的输入与输出标签。上下泳道之间用一条竖直交接箭头，从上一泳道末节点落入下一泳道首节点，使「规则信号 → 知识图谱路径 → LLM 仲裁」的链条可见。右侧设一条细窄的审计轨道，把每个节点的小型编号审计标签汇聚到一个「trace log」文档图标，显式呈现可追溯性。泳道下方并排两个小图：一个紧凑的横向堆叠条，显示三层的相对耗时（图例为「规则 / 知识图谱 / LLM」），LLM 段明显最长；其右侧一张小型网络图，节点为两个查询实体与中间概念，边为检索到的路径，边宽随检索频次变化。扁平矢量插画、柔和医学配色（雾霾蓝、青绿、暖灰）、统一圆角图标、清晰无衬线标签、留白充分、描边一致；不要渐变、不要阴影、不要 3D、不要照片写实。所有标签使用中文，字号在单栏宽度下清晰可读。

**负面提示词：**

> photorealistic, 3D render, gradient mesh, drop shadows, cluttered layout, tiny
> illegible text, watermarks, stock-photo look, cartoonish mascots, rainbow
> colors, inconsistent icon styles

**建议参数：** 画幅 16:9；最高分辨率；风格选「扁平插画」。

## Iteration tips

1. 第一版先确认**布局结构**（左输入 → 中间三层 → 右输出）再调配色。
2. 图中文字若出错，优先在提示词末尾加 "text labels must be spelled
   exactly as given" 或改用矢量工具手动替换文字层。
3. 保持与 Figure 1–6 及 S1–S2 的配色一致（见 figure contract `color_palette`）。
4. 最终图需导出 PNG ≥600 DPI 或 SVG，供组图使用。

---
Generated for project 「慧眼」 by build_schematic_prompts.py.
Customize bracketed slots before author submission.
Figure S2 prompts added locally: the generator hardcodes Figure 1 and does not scan contracts for `archetype: schematic_led_composite`.
