# Cover Letter

**Journal:** Journal of Medical Internet Research (J Med Internet Res)
**Article type:** Original Paper
**Title:** An explainable rule-knowledge-graph-LLM agent for exposome-eye risk stratification: external gains, a development-informed benchmark, and rules that do not transport
**Authors:** Guoqing Wang¹,², Xianglong Yi¹,²,* (*corresponding; yixianglong1010@163.com)

Dear Editors,

We submit our Original Paper "An explainable rule-knowledge-graph-LLM agent for exposome-eye risk stratification: external gains, a development-informed benchmark, and rules that do not transport" for consideration in J Med Internet Res.

This version corrects a methodological defect in our earlier submission. The internal benchmark had informed a post-confirmatory rule revision, which made its recall of 1.000 an artefact rather than a measurement; we have re-run the system, audited which evaluation pairs the revision touched, and now report the external matrix as primary. The earlier numbers are withdrawn.

Why this fits JMIR:

1. **A complete, deployable digital-health agent was benchmarked as such, and the comparison that matters is reported.** On the independent KNHANES matrix (301 pairs) the full agent reaches F1 = 0.375 against 0.360 for its own deterministic rule layer and 0.176 / 0.173 / 0.120 for LightRAG, a pure LLM and naive RAG. Removing the 5 pairs whose rules the revision touched leaves 296 pairs on which the ordering holds and every method loses about two thirds of its F1 (0.211 / 0.200 / 0.122 / 0.089 / 0.086). The agent's gain is precision, not recall.
2. **Validation is layered and disclosed, per JMIR's ML policy.** Four surfaces: the development matrix (NHANES, reported as development because all 6 of its replicated pairs sit on revised rules); the external national survey (KNHANES, 301 pairs); 18 pre-registered rule × cohort cells across eight ageing cohorts on three continents (285,878 participants; 598,386 person-waves), evaluated at the agent level as well as the rule level; and four bibliographic indexes for directional concordance.
3. **Written for clinicians, with open tooling.** Every output resolves to a rule, a knowledge-graph path and a source chunk; the same report is rendered in a working Streamlit interface, and the 21 rules and their variable definitions ship as machine-readable files.
4. **The full pipeline is public**: rules, variable definitions, interface and every analysis script at https://github.com/wangguoqing932/huiyan-exposome-eye-agent.
5. **A transferable lesson for digital-health validation.** Fifteen of 21 rules were untestable in the cohorts for measurement reasons and none was robustly transportable where testable; the agent's population-conditioned evidence gate found population-specific evidence for none of the 18 cohort cells, so it does not function as a transport predictor. We argue that agent validation must report system-level and rule-level results separately, name the pairs that informed development, and state which exposures were measured.

All content is our own; generative AI assistance is disclosed in the Declarations. The study uses de-identified public data only (ethics statement in the Declarations). Suggested reviewers and any conflicts of interest are declared in the submission metadata.

Sincerely,
Xianglong Yi (corresponding author), on behalf of all authors
