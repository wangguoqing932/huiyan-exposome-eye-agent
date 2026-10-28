# Multimedia Appendix 1 (Supplementary Tables S1-S6, Figures S1-S2)

# Supplementary Tables and Figures

Numbering note: Supplementary Notes S0–S9 (in supplementary_material.md) are distinct from the Supplementary Tables S1–S6 and Figures S1–S2 below.

This file contains the tables and figures moved out of the main text to keep the main manuscript at four tables and six figures. The main text cites them as Supplementary Table S1–S6 and Supplementary Figure S1–S2.

## Supplementary Table S1. Descriptive characteristics of the eight ageing cohorts

Computed from the same cohort frames the analysis uses, so the table cannot drift from the analysis. The unit is the person-wave, which is the analysed unit; SHARE's five imputation replicates are collapsed to replicate 1, so neither denominators nor prevalences are inflated.

Percentages are of person-waves with the variable observed. Missingness is reported separately in the table below.

| Cohort | Person-waves | Age, years, mean (SD) | Female, % | Current smoking, % | Diabetes (self-reported), % | BMI above the cohort cut-point, % | Cataract, % | Moderate vision impairment, % |
|---|---|---|---|---|---|---|---|---|
| SHARE | 338,703 | 67.9 (10.3) | 56.7 | 17.1 | 13.6 | 22.8 | 8.4 | 14.0 |
| HRS | 42,946 | 65.7 (11.8) | 58.5 | 22.5 | 24.5 | not available | 13.5 | 19.1 |
| ELSA | 9,771 | 64.9 (10.6) | 56.4 | 23.8 | not available | not available | 22.2 | 11.8 |
| KLoSA | 40,406 | 65.7 (11.0) | 57.0 | 14.2 | 5.4 | 23.1 | 4.5 | 20.9 |
| LASI | 73,408 | 57.9 (11.7) | 57.6 | not available | 12.1 | not available | 11.2 | 12.1 |
| MHAS | 15,217 | 60.3 (10.8) | 57.2 | not available | not available | not available | not available | 34.8 |
| CLHLS | 72,744 | 92.0 (7.9) | 60.0 | 15.9 | 1.4 | not available | 17.1 | 13.5 |
| CRELES | 5,191 | 76.7 (10.0) | 54.4 | 11.0 | 19.1 | 20.0 | 38.5 | not available |

### Missingness (% of person-waves with the variable missing)

**Read this table with the caveat that follows.** A 100% cell here usually means the variable is not carried in this cohort's analysis frame, not that the survey failed to measure it or that the item went unanswered. The frames were built to hold only what the pre-specified rules need, so a cohort that contributes no BMI rule has no BMI column at all and reports 100%. This column therefore describes **frame coverage**, which is what decides which (rule x cohort) cells are testable -- it is not an item non-response rate.

| Cohort | Age, years, mean (SD) | Female, % | Current smoking, % | Diabetes (self-reported), % | BMI above the cohort cut-point, % | Cataract, % | Moderate vision impairment, % | Missing at least one, % |
|---|---|---|---|---|---|---|---|---|
| SHARE | 0.0 | 0.0 | 58.0 | 0.4 | 0.0 | 0.4 | 18.7 | 58.1 |
| HRS | 51.3 | 51.3 | 33.1 | 0.7 | 100.0 | 62.5 | 0.3 | 100.0 |
| ELSA | 20.5 | 19.8 | 51.8 | 100.0 | 100.0 | 17.2 | 3.4 | 100.0 |
| KLoSA | 0.0 | 0.0 | 0.0 | 24.6 | 2.3 | 0.4 | 0.4 | 26.7 |
| LASI | 0.0 | 0.0 | 100.0 | 0.3 | 100.0 | 0.0 | 0.3 | 100.0 |
| MHAS | 0.2 | 0.2 | 100.0 | 100.0 | 100.0 | 100.0 | 7.6 | 100.0 |
| CLHLS | 7.3 | 0.0 | 75.1 | 76.8 | 100.0 | 76.6 | 81.9 | 100.0 |
| CRELES | 0.0 | 0.0 | 31.2 | 0.5 | 4.4 | 1.7 | 100.0 | 100.0 |

**Footnotes.**
* **Frame coverage versus item non-response.** Where a variable is present, its missingness is genuine non-response, SHARE's smoking is 58.0% missing with the column present, while HRS's BMI is 100% missing because the frame carries no BMI column.
* **Age in CLHLS is a baseline value repeated across waves**, not a follow-up age: 92.74% of its participants have a single unique age across all their waves, so its mean is not comparable to the others and should not be read as an average age during follow-up. The frame defect is documented in `docs/GAP_ANALYSIS_20IF.md`.
* **Diabetes is self-reported** in every cohort, so its prevalence reflects diagnosis rates rather than disease prevalence, the mechanism the paper demonstrates with the NHANES comparison.
* **MHAS contributes no cataract item, and several rule-required exposure–outcome combinations are absent in HRS and KLoSA** (hence their single analysed rule, r20); the outcome items themselves are present in those cohorts.
* The BMI cut-point is 25 kg/m² for the Asian cohorts and 30 kg/m² otherwise, fixed by the prevalence gate before the confirmatory analysis.

---

## Supplementary Table S2. Rule-level performance against the NHANES, KNHANES and CHARLS gold standards

| dataset | pairs_tested | rule_pairs_tested | replicated | contradicted | uninformative | precision_rule | precision_rule_ci95 | precision_binary_uninf_as_fp | coverage | phase | methodology |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NHANES |  | 16 | 6 | 0 | 10 | 1.0 | [0.541, 1.0] | 0.375 | 0.889 | confirmatory_R5 | three-state gold + survey svyglm variance (plan §6; R5) + Clopper-Pearson CI |
| KNHANES |  | 15 | 5 | 0 | 10 | 1.0 | [0.478, 1.0] | 0.333 | 0.882 | confirmatory_R5 | three-state gold + survey svyglm variance (plan §6; R5) + Clopper-Pearson CI |
| CHARLS |  | 4 | 0 | 0 | 4 | n/a (0 informative) | [None, None] | 0.0 | 1.0 | confirmatory_R5 | point estimates + declared fallback (no PSU; plan §6); three-state gold, R5 |

---

**Sensitivity sub-table (headline set).** Level A: 1 pair, 0 replicated. Levels A+B: 13 pairs, 4 replicated (0.308). Excluding the negative control r01 and the post-hoc r22: 16 pairs, 6 replicated (0.375). Source: outputs/confirmatory/headline_sensitivity.json.

---

## Supplementary Table S3. Validation layers: pairs available, testable and informative

| Dataset | Total pairs | Tested | Underpowered | Rule-relevant tested | Replicated | Contradicted | Uninformative | Not estimable |
|---|---|---|---|---|---|---|---|---|
| NHANES | 180 | 159 | 21 | 16 | 6 | 0 | 10 | 0 |
| KNHANES | 352 | 301 | 50 | 15 | 5 | 0 | 10 | 1 |
| CHARLS | 14 | 14 | 0 | 4 | 0 | 0 | 4 | 0 |

**On the "not estimable" column.** Tested plus underpowered does not equal the total for KNHANES (301 + 50 = 351 of 352), and the residual is shown here rather than absorbed into either column. One pair failed to estimate (numerical overflow in the survey model, logged as fit_fail), so no odds ratio could be computed; it is neither a powered test nor a power failure.

**On the two denominators.** The rule-relevant counts (NHANES 16, KNHANES 15) are those used under the pre-registered three-state standard. Other figures in this paper quote 17 and 16, or 19 and 16, because they count the extended v1.2 rule set. The difference is stated here so that the denominators are not confused with one another.

---

## Supplementary Table S4. Participant-level interaction test for the two-cohort rules

| Rule | Cohorts | Person-waves | One-step interaction p | Two-stage heterogeneity (Q) p | Agreement |
|---|---|---|---|---|---|
| `r02_hyperglycemia_x_cataract` | 4 | 431,026 | 3.2e-08 | 6.94e-07 | both significant |
| `r10_smoking_x_cataract` | 4 | 165,365 | 0.00223 | 2.63e-07 | both significant |
| `r11_smoking_x_amd_late` | — | 3,991 | not estimable | — | not fittable after cleaning: x_nunique=2 y_nunique=2 cohort_nunique=1 n=3991 |
| `r12_alcohol_x_cataract` | 2 | 131,271 | 0.141 | 0.0273 | **DISAGREE** |
| `r13_bmi_x_cataract` | 2 | 342,157 | 0.149 | 0.0272 | **DISAGREE** |
| `r20_smoking_x_vi_mod_severe` | 5 | 212,705 | 2.38e-29 | 3.03e-13 | both significant |

**Definitions.** One-step: a single logistic model on stacked
participants with an exposure x cohort interaction and standard
errors clustered on the person; the p-value is the joint test of
all interaction terms. Two-stage: Cochran Q heterogeneity test on
the per-cohort estimates from random-effects pooling. At k = 2, Q
is statistically identical to the regional subgroup test in Table
5, so the two-stage p quoted in the text is the same number. For
k > 2 the two-stage subgroup test (main-text Table 4) is a post hoc regional contrast
with fewer degrees of freedom and is not the same null as a
cohort-level interaction; the two need not agree (r10: regional
p = 0.45, Q p = 2.6e-07).


## What this table is

Two caveats apply: at k = 2
the subgroup test and the heterogeneity test are the same number computed twice,
and pooling per-cohort estimates gives a cohort of 5,191 the same weight as one of
338,703. Both objections disappear if the cohorts are stacked and fitted once at
the level of the person with an exposure x cohort interaction.

Every person enters once, so cohort size sets its own weight, and the interaction
term asks the question directly. The two-stage comparator is the Cochran Q test of
between-cohort heterogeneity; for k > 2 it is not the same null as the post hoc
regional subgroup test in main-text Table 4 (see the definitions below).

## What it changes

**r13 (BMI to cataract) is the substantive change.** The two-stage Q test reports
p = 0.027 -- evidence of a difference at the conventional threshold -- while the
one-step test reports p = 0.149, i.e. no evidence of a difference. At k = 2 the
two-stage statistic gives each cohort one weight regardless of size, so pooling
SHARE (338,703 person-waves) and CRELES (5,191) on equal terms lets the small
cohort's noise dominate the heterogeneity statistic; the person-level model, which
weights by person, does not reproduce it.

**r12 (alcohol to cataract) shows the same k = 2 pattern.** Its two-stage Q p is
0.027 (at k = 2 identical to the regional subgroup statistic), while the one-step
test gives 0.141. The disagreement at k = 2 is about weighting, not about whether
the populations differ.

**For r02, r10 and r20 both tests detect heterogeneity** (one-step p = 3.2e-08,
0.00223 and 2.38e-29; Q p = 6.9e-07, 2.6e-07 and 3.0e-13), so no conclusion there
depends on the choice of test. The post hoc regional subgroup test is a coarser
null and does not reach significance for r10 (p = 0.45), consistent with the
leave-one-out result that r10's heterogeneity is driven by SHARE, not by region.

**r11 cannot be tested this way at all**: it is feasible in one cohort only, so
there is no interaction to estimate. That is consistent with what the manuscript
already reports for it.

## Limits

This re-fits the same frames the two-stage analysis used. It changes the inference,
not which cells are feasible, and it does not add cohorts. Exposure and outcome
columns come from the coverage matrix, so the two analyses are comparable.
Standard errors are clustered on the person identifier.

---

## Supplementary Table S5. Statistical power: minimum detectable odds ratios

Minimum detectable odds ratio at 80% power, two-sided alpha = 0.05, computed from the analysed n and
the observed margins. A pair is a POWERED NULL when its confidence interval excludes its own MDE.

SHARE appears once per pair, not five times: its five imputation replicates are stacked as rows in the
source release, and counting all five inflated n by exactly 5x, which shrank SE by sqrt(5) and made every
MDE look better than it is. Replicate 1 is used here, as it is for the prevalence gate.

| cohort | rule_id | n | exposure_prevalence | outcome_prevalence_unexposed | mde_or_80 | observed_or | ci_low | ci_high | three_state | powered_null | null_interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CLHLS | r02_hyperglycemia_x_cataract | 16650 | 0.0129 | 0.1607 | 1.6882 | 3.5887 | 2.6244 | 4.9074 | replicated | False | replicated |
| CLHLS | r10_smoking_x_cataract | 16961 | 0.1572 | 0.1782 | 1.167 | 0.748 | 0.6435 | 0.8694 | contradicted | False | contradicted |
| CLHLS | r12_alcohol_x_cataract | 8414 | 0.2369 | 0.2107 | 1.1926 | 0.809 | 0.704 | 0.9297 | contradicted | False | contradicted |
| CLHLS | r20_smoking_x_vi_mod_severe | 13115 | 0.1595 | 0.1394 | 1.2127 | 1.0267 | 0.8736 | 1.2066 | uninformative | True | powered_null |
| CRELES | r02_hyperglycemia_x_cataract | 5086 | 0.1917 | 0.3809 | 1.2281 | 1.3116 | 1.0705 | 1.6069 | uninformative | False | underpowered_or_indeterminate |
| CRELES | r10_smoking_x_cataract | 3511 | 0.1105 | 0.3987 | 1.3607 | 0.7023 | 0.5021 | 0.9822 | uninformative | True | powered_null |
| CRELES | r13_bmi_x_cataract | 4883 | 0.2011 | 0.3986 | 1.2267 | 0.9911 | 0.8126 | 1.2087 | uninformative | True | powered_null |
| ELSA | r10_smoking_x_cataract | 4050 | 0.2138 | 0.2337 | 1.2888 | 0.7675 | 0.6069 | 0.9705 | uninformative | True | powered_null |
| ELSA | r11_smoking_x_amd_late | 4028 | 0.2133 | 0.0435 | 1.6956 | 0.8586 | 0.5483 | 1.3444 | uninformative | True | powered_null |
| ELSA | r20_smoking_x_vi_mod_severe | 4546 | 0.2352 | 0.1171 | 1.3563 | 1.4883 | 1.2128 | 1.8263 | replicated | False | replicated |
| HRS | r20_smoking_x_vi_mod_severe | 28654 | 0.2256 | 0.1808 | 1.1084 | 1.6144 | 1.4682 | 1.7752 | replicated | False | replicated |
| KLoSA | r20_smoking_x_vi_mod_severe | 40260 | 0.1418 | 0.215 | 1.1023 | 1.1002 | 1.0004 | 1.21 | uninformative | False | underpowered_or_indeterminate |
| LASI | r02_hyperglycemia_x_cataract | 73204 | 0.121 | 0.1012 | 1.111 | 1.8782 | 1.7646 | 1.9991 | replicated | False | replicated |
| SHARE | r02_hyperglycemia_x_cataract | 337274 | 0.1364 | 0.0747 | 1.0549 | 1.7539 | 1.6908 | 1.8194 | replicated | False | replicated |
| SHARE | r10_smoking_x_cataract | 142084 | 0.1715 | 0.0882 | 1.072 | 1.109 | 1.041 | 1.1815 | replicated | False | replicated |
| SHARE | r12_alcohol_x_cataract | 123478 | 0.167 | 0.0919 | 1.0768 | 0.9628 | 0.8999 | 1.0301 | uninformative | True | powered_null |
| SHARE | r13_bmi_x_cataract | 337274 | 0.2282 | 0.0822 | 1.0427 | 1.2439 | 1.2008 | 1.2886 | replicated | False | replicated |
| SHARE | r20_smoking_x_vi_mod_severe | 142229 | 0.1715 | 0.1443 | 1.0577 | 1.0875 | 1.0429 | 1.1339 | replicated | False | replicated |

---

## Supplementary Table S6. Measurement-modality evidence audit

Of 168 possible (rule × cohort) cells, **18 (10.7%)** are feasible. A cell is feasible only when both the exposure and the outcome exist in that cohort with at least 200 non-missing observations.

| Blocked by | Cells | Share of infeasible |
|---|---|---|
| both_sides | 83 | 55.3% |
| exposure_missing | 41 | 27.3% |
| outcome_missing | 26 | 17.3% |
## Marginal value of adding one measurement modality
| Modality added | Additional rule × cohort cells unlocked |
|---|---|
| OUTCOME:fundus_imaging | +15 |
| blood_assay | +13 |
| geocoded_environment | +13 |
| dietary_index | +6 |
| questionnaire_behaviour | +6 |
| OUTCOME:fundus_imaging_or_grading | +5 |
| OUTCOME:selfreport_ocular_diagnosis | +5 |
| anthropometry | +3 |
| selfreport_or_assay_metabolic | +1 |
| OUTCOME:vision_rating | +1 |

The outcome-side entries are the actionable ones. No cohort in this layer has fundus imaging, tonometry or optic-disc grading, which is why the entire retinopathy and diabetic macular oedema family (r03, r04, r07, r19, r22) and the two glaucoma-measurement rules (r16) cannot be assessed in any of the eight.

---

**Per-cohort infeasibility.** MHAS contributes no feasible cell (23 infeasible combinations; outputs/confirmatory/cohort_rule_coverage.json).

## Supplementary Text: extended analyses (moved from the main text)

**Person-level heterogeneity tests.** At k = 2 the subgroup test is arithmetically the same statistic as Q; stacking cohorts and fitting one participant-level model with an exposure x cohort interaction gives r13 interaction p = 0.15 and r12 p = 0.14 against Q p = 0.027 for both. For the larger rules both tests detect heterogeneity (r02 3.2 × 10⁻⁸ vs 6.9 × 10⁻⁷; r10 0.0022 vs 2.6 × 10⁻⁷; r20 2.4 × 10⁻²⁹ vs 3.0 × 10⁻¹³). At k = 2 the two-stage statistic is consistent with equal weighting — r13 pools SHARE's 338,703 person-waves with CRELES's 5,191 — rather than a property of the populations; the pooled estimates and pre-registered verdicts are unchanged.

**Meta-regression on mean age.** Across the three larger rules the mean age did not predict the log OR (slopes +0.017 for r02, −0.008 for r10, −0.010 for r20 per year; p = 0.42, 0.52, 0.35; k = 4–5, low power).

**τ² interpretation.** On the log-OR scale the fitted τ² corresponds to cross-cohort ratio differences of only 1.24×–2.16×; high I² is driven by SHARE's very small standard error rather than large absolute divergence, so using I² alone as a rejection criterion would partly be a sample-size penalty.

**Architecture detail.** The rule layer fires first and can abstain; the knowledge graph retrieves supporting chunks; the arbiter grades risk within the rule's declared direction and cannot add rules or evidence. The same rule layer ran in every validation tier; the system-level classification benchmark is produced by this deterministic rule layer, while the KG and the arbiter shape the report and the risk grade. The literature-index layer tested rule direction, not the full agent.

**Development set.** The 134-pair development set was used only to construct the rule base and the evidence chunks; it contributes no independent performance estimate, and every in-text estimate is out-of-sample with respect to it.

## Supplementary Table S7. Binary-collapsed discrimination metrics (secondary analysis)

Gold positive = replicated; predicted positive = flag. Sensitivity/specificity/PPV and Cohen's κ on the full tested matrix, per-seed range across five seeds. Source: outputs/confirmatory/discriminability_summary.json (includes the rule-relevant headline subset), with the KNHANES full-agent row recomputed from fused_system_R5.jsonl. Caveat: uninformative pairs are treated as non-positive, which the three-state standard rejects; reported as a secondary collapse only. All NHANES rows are development descriptions: every replicated pair is covered by a rule the post-confirmatory revision touched, so their sensitivity of 1.00 is constructed, not earned. Baseline rows were recomputed with failed parses treated as missing, not negative (R31 addendum P0).

| Generation / matrix | Method | Sensitivity | Specificity | PPV | κ | n |
|---|---|---|---|---|---|---:|
| NHANES, Qwen (80) | full agent (G2) | 1.00 | 0.878 | 0.400 | 0.520 | 80 |
| NHANES, Qwen (80) | rule layer (G0) | 1.00 | 0.851 | 0.353 | 0.462 | 80 |
| NHANES, Qwen (80) | LightRAG | 1.00 | 0.743–0.757 | 0.24–0.25 | 0.303–0.318 | 80 |
| NHANES, Qwen (80) | pure LLM | 1.00 | 0.662–0.689 | 0.194–0.207 | 0.227–0.250 | 80 |
| NHANES, Qwen (80) | naive RAG | 0–0.167 | 0.905–0.959 | 0–0.250 | −0.088–0.149 | 80 |
| NHANES, GLM-5.3-flash (159) | full agent (G2) | 1.00 | 0.928 | 0.353 | 0.493 | 159 |
| NHANES, GLM-5.3-flash (159) | rule layer (G0) | 1.00 | 0.915 | 0.316 | 0.448 | 159 |
| NHANES, GLM-5.3-flash (159) | LightRAG | 0.833 | 0.706–0.739 | 0.10–0.111 | 0.119–0.139 | 159 |
| NHANES, GLM-5.3-flash (159) | pure LLM | 1.00 | 0.595–0.693 | 0.088–0.113 | 0.100–0.145 | 159 |
| NHANES, GLM-5.3-flash (159) | naive RAG | 0–0.167 | 0.954–0.980 | 0–0.250 | −0.042–0.175 | 159 |
| KNHANES (301) | full agent (G2) | 0.500 | 0.926 | 0.300 | 0.325 | 301 |
| KNHANES (301) | rule layer (G0) | 0.500 | 0.919 | 0.281 | 0.307 | 301 |
| KNHANES, revision-free (296) | full agent (G2) | 0.308 | 0.922 | 0.154 | 0.156 | 296 |
| KNHANES, revision-free (296) | rule layer (G0) | 0.308 | 0.919 | 0.148 | 0.150 | 296 |
| KNHANES (301) | LightRAG | 0.538–0.615 | 0.719–0.736 | 0.08–0.092 | 0.069–0.092 | 301 |
| KNHANES (301) | pure LLM | 0.692–0.769 | 0.576–0.622 | 0.069–0.079 | 0.050–0.071 | 301 |
| KNHANES (301) | naive RAG | 0.077–0.154 | 0.903–0.938 | 0.034–0.100 | −0.013–0.073 | 301 |

**Evidence-gated variant (post-hoc optimisation test; superseded by the pre-registered G0/G1/G2 ablation in Table 3 and by the R31 recomputation).** Requiring a fired rule to have at least one linked A/B/C evidence chunk keeps NHANES sensitivity at 1.00 while cutting false positives (Qwen: FP 11→9, spec 0.851→0.878, PPV 0.353→0.400, κ 0.462→0.520; GLM: FP 13→11, spec 0.915→0.928, PPV 0.316→0.353, κ 0.448→0.493); externally that particular variant traded one true positive for one false positive (sens 0.500→0.444, κ 0.307→0.279); the pre-registered G2 arm, recomputed under R31 with outcome variants resolved to canonical terms, keeps sensitivity at 0.500 and removes two false positives (κ 0.307→0.325, Table 3). This is consistent with the pre-registered G1/G2 ablation (0.455→0.476→0.500 on judgeable pairs); the deployable classifier is the evidence-gated configuration. Severity tiers alone are weak discriminators (PPV med/high 0.296–0.364 vs low/unknown 0.200–0.333). Source: outputs/confirmatory/gate_optimization_summary.json.

## Supplementary Table S8. Literature-layer directional concordance by index

Unit = rule-level directional concordance (concordant/discordant paper counts aggregated per rule; unclear judgments excluded). Macro precision = mean of per-rule precision. "Agree" = majority literature direction matches the rule's declared direction. Source: outputs/confirmatory/literature_concordance_summary.json (built from multidb_summary_R18.json and cnki_validation_R19.json).

| Index | Informative rules | Concordant papers | Discordant papers | Macro precision |
|---|---:|---:|---:|---:|
| PubMed | 21 | 242 | 18 | 0.890 |
| Web of Science | 2 | 42 | 7 | 0.917 |
| Europe PMC | 17 | 42 | 2 | 0.922 |
| CNKI | 5 | 11 | 1 | 0.800 |

**Inter-index agreement.** On shared informative rules, rule-level direction agreed in 16/17 for PubMed–Europe PMC (the exception is r09, Mediterranean diet–AMD, where Europe PMC's majority is discordant), and in 15/15 across all other index pairs (PubMed–WoS 2/2, PubMed–CNKI 5/5, WoS–Europe PMC 2/2, WoS–CNKI 1/1, Europe PMC–CNKI 3/3). Cohen's κ is degenerate at these prevalences (both raters almost always "agree") and is not reported; raw agreement is shown instead.

## Supplementary Figures

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
