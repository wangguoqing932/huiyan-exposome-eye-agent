# Table 3. System-level and rule-level performance by validation dataset

| Dataset (role) | Full system F1 (rule layer) | LightRAG | Pure LLM | Naive RAG | Rule-relevant pairs (R/C/U) | Notes |
|---|---:|---:|---:|---:|---|---|
| NHANES, Qwen (internal) | 0.571 (full agent) | 0.392 | 0.335 | 0.080 | 16 (6/0/10) | 80 pairs; rule-layer ablation 0.522, NC-gated 0.545 |
| NHANES, GLM-5.3-flash (internal) | 0.522 (full agent) | 0.186 | 0.178 | 0.069 | 16 (6/0/10) | 159 pairs; rule-layer ablation 0.480 |
| KNHANES (external, site) | 0.360 | 0.145 | 0.135 | 0.094 | 15 (5/0/10) | 301 pairs |
| CHARLS (external, site) | not assessed | not assessed | not assessed | not assessed | 4 (0/0/4) | 14 pairs; direction check only |
| Eight ageing cohorts (external, population) | not assessed | not assessed | not assessed | not assessed | 18 (8/2/8) | 6 of 21 rules testable; 18 of 168 cells feasible |
| Literature indexes (independent) | not applicable | not applicable | not applicable | not applicable | — | 0.800–0.922 (4 indexes) |

**Notes.** System-level F1 was measured only where the three baselines were run (NHANES, two generations; KNHANES). CHARLS and the eight cohorts were evaluated at the rule level, so “not assessed” indicates a different validation target, not a missing result. R/C/U order is replicated/contradicted/uninformative rule-relevant pairs. Full-agent F1 is the deployable G2 configuration on the primary matrix; KNHANES reports the rule layer; on GLM-5.3-flash the full agent scored 0.522 versus rule layer 0.480. The arbiter affects the report and risk grade. The literature layer reports index-level precision, not F1: PubMed 0.889, Web of Science 0.916, Europe PMC 0.922 and CNKI 0.800.
