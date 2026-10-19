#!/usr/bin/env python
"""Fix and extend outputs/paper/figure_prompts.md (writer 7_3).

Two defects in the generator's output, both found by reading it rather than
trusting the "written" message:

1. FIGURE 5 IS MISSING ENTIRELY. The generator hardcodes "Figure 1 architecture
   flowchart by default" and never scans the contracts for
   `archetype: schematic_led_composite`. Two contracts carry that archetype --
   figure1_architecture and figure5_reasoning_trace -- so the schematic set was
   one figure short. Prompts for figure5 are added below, built from its
   contract's three panels.

2. THE ENGLISH PROMPT CONTAINED CHINESE. Variant A is labelled "Main prompt
   (English)" and ends with "All labels in English", yet its body read
   "two entity types -- 暴露组（代谢-营养-生活方式-环境） and 主要致盲眼病".
   An image model given that instruction returns Chinese lettering, which then
   contradicts the same prompt's closing sentence. Fixed to English entity names.

Run: python scripts/fix_schematic_prompts.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FP = ROOT / "outputs" / "paper" / "figure_prompts.md"

CN_EXPOSOME = "暴露组（代谢-营养-生活方式-环境）"
EN_EXPOSOME = "exposome (metabolic, nutritional, lifestyle and environmental exposures)"
CN_DISEASES = "主要致盲眼病"
EN_DISEASES = "major blinding eye diseases"

FIG5 = """
## 2. Figure 5 — Three-layer reasoning trace

Figure 5 shows HOW a single conclusion is produced and audited, so its job is
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
"""


def main() -> int:
    text = FP.read_text(encoding="utf-8")

    fixed = 0
    for cn, en in ((CN_EXPOSOME, EN_EXPOSOME), (CN_DISEASES, EN_DISEASES)):
        if cn in text:
            # only inside the English variant; both occur there
            text = text.replace(cn, en)
            fixed += 1

    # keep the English variant's entity names English, and say so once
    text = text.replace(
        "two entity types — exposome (metabolic, nutritional, lifestyle and "
        "environmental exposures) and major blinding eye diseases —",
        "two entity types — the exposome (metabolic, nutritional, lifestyle and "
        "environmental exposures) and major blinding eye diseases —")

    if "Figure 5 — Three-layer reasoning trace" not in text:
        # insert before the iteration tips so the tips stay last
        marker = "## Iteration tips"
        text = (text.replace(marker, FIG5.strip() + "\n\n" + marker, 1)
                if marker in text else text.rstrip() + "\n" + FIG5)

    text = text.replace(
        "Customize bracketed slots before author submission.",
        "Customize bracketed slots before author submission.\n"
        "Figure 5 prompts added locally: the generator hardcodes Figure 1 and "
        "does not scan contracts for `archetype: schematic_led_composite`.")

    FP.write_text(text, encoding="utf-8")
    print(f"chinese terms anglicised in the English prompt: {fixed}")
    print(f"sections now present: "
          f"{text.count('## 1. Figure 1')}x fig1, "
          f"{text.count('## 2. Figure 5')}x fig5")
    print(f"-> {FP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
