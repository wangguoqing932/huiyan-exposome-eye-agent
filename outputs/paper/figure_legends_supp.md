**Figure S1. Demo case: exposome (metabolic, nutritional, lifestyle and environmental) × major blinding eye disease risk evaluation.**

A worked demo case shows how Huiyan integrates rule signals, retrieved evidence, and LLM arbitration into an explainable risk report, enabling clinicians to trace each component of the recommendation back to its source.

(**a**) Input. Compact summary card: Entity A (subtype + key flags) | Entity B (exposure + key flags) | Patient factors (tags). No fancy graphics, just clear metadata.

(**b**) Triggered rules. Horizontal bar chart: each rule triggered, with severity color and mechanism category label. Bars ordered by severity (H → M → L).

(**c**) Evidence levels. Horizontal bars for levels A (regulatory) through E (mechanism), showing the number of retrieved evidence chunks at each level for this case.

(**d**) Traceability chain. Flow diagram showing how the LLM arbiter combined rule signals + top-k evidence chunks → final risk level. Each chunk numbered, source cited.

Statistics: Levels: A=regulatory, B=meta-analysis, C=original study, D=in vitro/animal, E=mechanism inference; Case selection: representative high-risk case from the internal validation set (intval-nhanes).

Abbreviations: OR = odds ratio; LLM = large language model; AMD = age-related macular degeneration; DR = diabetic retinopathy; IOP = intraocular pressure; CDR = cup-to-disc ratio.

---

**Figure S2. Step-by-step reasoning trace across the three architectural layers.**

Huiyan's three-layer architecture produces a fully traceable reasoning chain, each transition from rule signal to KG path to LLM arbitration is logged, enabling post-hoc audit of every output.

(**a**) Seven-step swim-lane trace. Rule Engine steps 1–4 (normalise A, normalise B, match r04, cross-cover r03), LightRAG KG step 5 (retrieval), LLM Arbiter / Report steps 6–7 (risk grade, report + trace). Step numbers are execution order; no duration is encoded.

(**b**) Knowledge-graph path: HbA1c → hyperglycaemia → retinal ischaemia → VEGF upregulation → neovascularisation → PDR. Rule r04 covers the full chain.

(**c**) Steps per layer: Rule 4, KG 1, Arbiter 2, the reasoning burden is concentrated in the rule layer.

Statistics: Seven logged steps; per-layer timings were not logged, so no latency panel is shown. Step labels are the logged trace, not a reconstruction.

Abbreviations: KG = knowledge graph; LLM = large language model; LightRAG = lightweight retrieval-augmented generation; VEGF = vascular endothelial growth factor; PDR = proliferative diabetic retinopathy; HbA1c = glycated haemoglobin.

---
