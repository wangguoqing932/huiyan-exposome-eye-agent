# Table 3. System-level and rule-level performance by validation dataset

| Dataset (role) | Full agent F1 (G2) | Rule layer F1 (G0) | LightRAG | Pure LLM | Naive RAG | Rule-relevant pairs (R/C/U) | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| NHANES, Qwen (development, **no contamination-free positives**) | 0.571 | 0.522 | 0.392 | 0.335 | 0.080 | 16 (6/0/10) | 80 pairs; all 6 replicated pairs are covered by rules revised after the first confirmatory run, so this is a development description, not an estimate |
| NHANES, GLM-5.3-flash (development) | 0.522 | 0.480 | 0.186 | 0.178 | 0.069 | 16 (6/0/10) | 159 pairs; same audit applies |
| KNHANES (external, site) | **0.375** | 0.360 | 0.176 | 0.173 | 0.120 | 15 (5/0/10) | 301 pairs; agent ran end to end; gate removes 2 of 23 false positives, recall unchanged at 0.500 |
| KNHANES, revision-free subset (external) | **0.211** | 0.200 | 0.089 | 0.122 | 0.086 | 13 replicated of 296 pairs | 5 pairs whose rules were revised are removed; every method loses about two thirds of its F1 |
| CHARLS (external, site) | not assessed | not assessed | not assessed | not assessed | not assessed | 4 (0/0/4) | 14 pairs; rule-level direction only |
| Eight ageing cohorts (external, population) | 0.000 (18 cells) | 0.615 (assume transport) | — | 0.667 (plain LLM) | — | 18 (8/2/8) | 6 of 21 rules testable; 18 of 168 cells feasible; cell-level task = will this rule replicate in this population; the population-conditioned gate found no population-specific evidence for any cell |
| Literature indexes (independent) | not applicable | not applicable | not applicable | not applicable | not applicable | — | 0.800–0.922 (4 indexes) |

**Notes.** Baselines were recomputed under the pre-registered rule that a failed
parse is missing data, never a negative (R31 addendum P0); the earlier values
(0.145/0.135/0.094) treated parse failures as negative responses and are void.
System-level F1 exists where the three baselines were run, which is NHANES (two
generations) and KNHANES. The NHANES matrix is labeled development because all 6
of its replicated pairs are covered by rules revised after the first confirmatory
run; with zero contamination-free positives it cannot support an out-of-sample
estimate. KNHANES is the only external matrix on which the full agent ran end to
end; there it edges past its own rule layer, and the ordering — but not the level
— survives removal of the 5 revised pairs. CHARLS was evaluated at the rule level only, so "not assessed" there
indicates a different validation target, not a missing result; the eight cohorts
are reported both at the rule level (Fig 6) and, for the 18 cells, at the agent
level. R/C/U order is replicated/contradicted/uninformative
rule-relevant pairs. The literature layer reports index-level precision, not F1:
PubMed 0.889, Web of Science 0.916, Europe PMC 0.922 and CNKI 0.800.
