# Table 3. System-level and rule-level performance by validation dataset

| Dataset (role) | Full agent F1 (G2) | Rule layer F1 (G0) | LightRAG | Pure LLM | Naive RAG | Rule-relevant pairs (R/C/U) | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| NHANES, Qwen (internal, **in-sample**) | 0.571 | 0.522 | 0.392 | 0.335 | 0.080 | 16 (6/0/10) | 80 pairs; G1 0.545; recall 1.000 constructed by the v1.2 rule revision |
| NHANES, GLM-5.3-flash (internal, **in-sample**) | 0.522 | 0.480 | 0.186 | 0.178 | 0.069 | 16 (6/0/10) | 159 pairs; same in-sample caveat |
| KNHANES (external, site) | **0.312** | 0.360 | 0.145 | 0.135 | 0.094 | 15 (5/0/10) | 301 pairs; agent ran end to end; gates raise precision 0.281→0.357 and halve recall 0.500→0.278 |
| CHARLS (external, site) | not assessed | not assessed | not assessed | not assessed | not assessed | 4 (0/0/4) | 14 pairs; rule-level direction only |
| Eight ageing cohorts (external, population) | not assessed | not assessed | not assessed | not assessed | not assessed | 18 (8/2/8) | 6 of 21 rules testable; 18 of 168 cells feasible |
| Literature indexes (independent) | not applicable | not applicable | not applicable | not applicable | not applicable | — | 0.800–0.922 (4 indexes) |

**Notes.** System-level F1 was measured wherever the three baselines were run,
which is NHANES (two generations) and KNHANES. The NHANES matrix is labeled
in-sample because the rule set was revised after the first confirmatory run; its
recall of 1.000 is a property of that revision (the pre-revision v1.1 set scored
0.111 on the same scope under the earlier gold), so its F1 is not an
out-of-sample estimate. KNHANES is the only external matrix on which the full
agent ran end to end; there the agent beats all three baselines but not its own
deterministic rule layer. CHARLS and the eight cohorts were evaluated at the rule
level, so "not assessed" indicates a different validation target, not a missing
result. R/C/U order is replicated/contradicted/uninformative rule-relevant pairs.
The literature layer reports index-level precision, not F1: PubMed 0.889, Web of
Science 0.916, Europe PMC 0.922 and CNKI 0.800.
