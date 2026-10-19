# Figure & Table QC Report (writer phase 7_1, v3.0)

- Date: 2026-10-19
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
| F3 | ✅ | figureS1: 4 panels parsed |
| F2 | ✅ | figureS1 source_data outputs/figures/source_data/figure4_demo_case.csv OK |
| F4 | ✅ | figureS1: 1 rendered file(s) |
| F3 | ✅ | figureS2: 3 panels parsed |
| F2 | ✅ | figureS2 source_data outputs/figures/source_data/figure5_reasoning_trace.csv OK |
| F4 | ✅ | figureS2: 1 rendered file(s) |
| F3 | ✅ | figure4: 1 panels parsed |
| F2 | ✅ | figure4 source_data outputs/figures/source_data/figure6_dose_response.csv OK |
| F4 | ✅ | figure4: 1 rendered file(s) |
| F3 | ✅ | figure5: 1 panels parsed |
| F2 | ✅ | figure5 source_data outputs/figures/source_data/figure7_power_mde.csv OK |
| F4 | ✅ | figure5: 1 rendered file(s) |
| F3 | ✅ | figure6: 2 panels parsed |
| F2 | ✅ | figure6 source_data outputs/figures/source_data/figure8_cohort_transportability.csv OK |
| F4 | ✅ | figure6: 2 rendered file(s) |
| T1 | ✅ | registry_summary.csv OK |
| T1 | ✅ | rule_list.csv OK |
| T1 | ✅ | performance_matrix.csv OK |
| T1 | ✅ | validation_distribution.csv OK |
| T1 | ✅ | dataset_summary.csv OK |
| T1 | ✅ | performance_by_dataset.csv OK |
| T2 | ✅ | 9 publication markdown tables |
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
