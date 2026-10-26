# Cover Letter

**Journal:** Journal of Medical Internet Research (J Med Internet Res)
**Article type:** Original Paper
**Title:** An explainable rule-knowledge-graph-LLM agent for exposome-eye risk stratification: strong benchmarks, operable reports, limited rule transportability
**Authors:** Guoqing Wang¹,², Xianglong Yi¹,²,* (*corresponding; yixianglong1010@163.com)

Dear Editors,

We submit our Original Paper "An explainable rule-knowledge-graph-LLM agent for exposome-eye risk stratification: strong benchmarks, operable reports, limited rule transportability" for consideration in J Med Internet Res.

Why this fits JMIR:

1. **A complete, deployable digital-health intervention was benchmarked as such.** Our explainable agent (deterministic rules + LightRAG knowledge graph + a constrained LLM arbiter) was evaluated with its full pipeline on an 80-pair NHANES benchmark (F1 = 0.571 vs LightRAG 0.392, pure LLM 0.335, naive RAG 0.080; accuracy McNemar significant against LightRAG and pure LLM), with the rule layer alone reported as an ablation, on external KNHANES (rule layer 0.360 vs 0.145/0.135/0.094), and with binary-collapsed discrimination metrics (internal sensitivity 1.00, specificity 0.878, PPV 0.400, κ 0.520).
2. **Validation used independent data not used for development**, per JMIR's ML policy: an internal national survey, an external national survey (KNHANES, 301 pairs), eight ageing cohorts (285,878 participants; 598,386 person-waves) for rule-level transportability under a pre-registered three-state standard, and four literature indexes for directional concordance.
3. **Written for clinicians, with open tooling.** Every output resolves to a rule, a knowledge-graph path and a source chunk; the same report is rendered in a working Streamlit interface, and the rule/variable definitions ship as machine-readable files with the code.
4. **Open tooling.** The full pipeline — rules, variable definitions, Streamlit interface and every analysis script — is publicly available at https://github.com/wangguoqing932/huiyan-exposome-eye-agent
5. **An honest, transferable lesson for digital-health validation.** Fifteen of 21 rules were untestable in the cohorts for measurement reasons and none was robustly transportable where testable; we therefore argue that agent validation must report system-level and rule-level results separately and state which exposures were measured.

All content is our own; generative AI assistance is disclosed in the Declarations. The study uses de-identified public data only (ethics statement in the Declarations). Suggested reviewers and any conflicts of interest are declared in the submission metadata.

Sincerely,
Xianglong Yi (corresponding author), on behalf of all authors
