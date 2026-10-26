# Figure Legends

**Figure 1. System architecture of Huiyan.**

Huiyan integrates three layers, a deterministic rule engine, a knowledge-graph retrieval module (LightRAG), and an LLM arbiter, to produce explainable risk-graded reports for exposome (metabolic, nutritional, lifestyle and environmental) × major blinding eye disease interactions, with full traceability from output back to source evidence.

(**a**) End-to-end pipeline: input → entity normalisation → rule engine → LightRAG retrieval → LLM arbiter → report with trace.

(**b**) Three layers, one traceable path: rule layer (deterministic), KG layer (evidence-grounded), arbiter layer (bounded). Every step belongs to one layer, so an output can be followed back to its evidence.

(**c**) Four output views: clinician card / patient handout / research table / policy brief. All from single inference pass.

Statistics: Rule layer: 21 rules (A1/B15/C5); KG layer: 27,136 nodes and 1,060 evidence chunks; Arbiter: local Qwen3.8-27B at temperature 0 in the reported runs.

Abbreviations: LLM = large language model; KG = knowledge graph; YAML = YAML Ain't Markup Language; LightRAG = lightweight retrieval-augmented generation.

---

**Figure 2. Huiyan (v1.2) vs three LLM baselines on NHANES pairs, in two baseline generations.**

In the primary generation (80 development-era pairs, local Qwen3.8-27B baselines, R11-corrected three-state gold under survey svyglm variance), the full Huiyan system attains F1 = 0.522 (P 0.353 / R 1.000, deterministic across seeds), ahead of lightrag 0.392 ± 0.007, pure_llm 0.335 ± 0.010 and naive_rag 0.080 ± 0.110 (5 seeds each). Accuracy McNemar is significant against pure_llm (p = 0.0043–0.0118) but not lightrag (p = 0.057–0.092, then vector-only) or naive_rag (p = 0.58–0.79); a flag-pattern McNemar on predicted positives is significant against pure_llm and naive_rag. After the LightRAG baseline was upgraded to full hybrid knowledge-graph traversal and all baselines were re-run on GLM-5.3-flash over 159 pairs, the ordering holds and the LightRAG comparison resolves: full 0.480 (P 0.316 / R 1.000) > lightrag 0.186 ± 0.006 > pure_llm 0.178 ± 0.015 > naive_rag 0.069 ± 0.086, with accuracy McNemar significant against lightrag (p = 1.0×10⁻⁸ to 7.7×10⁻⁷) and pure_llm (p = 1.2×10⁻¹² to 5.4×10⁻⁹) but not naive_rag (p = 0.30–1.00). Precision is low for every method (0.07–0.35) because most predicted-positive pairs are uninformative under the three-state standard rather than contradicting it.

(**a**) F1 by method (5 seeds; bars show the mean, whiskers are ±1 SD across seeds), two generations shown side by side. Grouped bars: blue = qwen generation (80 pairs), yellow = zhipu generation (159 pairs). qwen: full_system 0.522 (deterministic) > lightrag 0.392 > pure_llm 0.335 > naive_rag 0.080. zhipu: full_system 0.480 (deterministic) > lightrag 0.186 > pure_llm 0.178 > naive_rag 0.069. The two generations are not averaged: they differ in gold size and backend. The pre-expansion v1.1 ruleset (0.111 on the R5 gold) is not plotted here; see the internal-layer tables. (**b**) Confusion matrix of the deterministic full system against the R11-corrected three-state gold on the primary 80-pair generation: predict YES 6 replicated / 0 contradicted / 11 uninformative; predict NO 0 replicated / 2 contradicted / 61 uninformative (TP 6, FP 11, FN 0, TN 63). Cell shading in (**b**) is a visual aid only; every count is printed in its cell. (**c**) Rule-layer coverage and declared-domain precision in NHANES (internal) versus KNHANES (external), shown as grouped bars: coverage 0.889 versus 0.882, precision_rule 1.00 versus 1.00. (**d**) Distribution of retrieved KG context size for the qwen-generation LightRAG baseline (5 seeds × 80 pairs, characters); it documents how much context the retrieval baseline received and is not a performance claim.

Statistics: NHANES tested pairs; gold = three-state labels under survey svyglm variance after the R11 operationalisation corrections; 5 seeds per method; full_system is deterministic and all five runs are identical; paired McNemar exact; * p<0.05; n.s. p>=0.057 in the qwen generation versus lightrag.

Abbreviations: F1 = F1 score; P = precision; R = recall; KG = knowledge graph; LLM = large language model; NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey; R5/R11 = internal analysis revisions (gold-label versions); SD = standard deviation; n.s. = not significant.

---

**Figure 3. Rule-level evaluation under the R11 three-state protocol: precision, coverage and replication by evidence level.**

Under the pre-registered three-state standard, the declared-domain precision (replicated / (replicated + contradicted)) is 1.00 in both countries, but the conservative precision (replicated / all rule-relevant testable pairs) is 0.375 (NHANES, 95% CI 0.152-0.646) and 0.333 (KNHANES, 0.118-0.616), both are shown. Rule testability P(testable | rule exists) is high: 0.889 NHANES / 0.882 KNHANES (pre-registered coverage of the full testable matrix is 0.131/0.095). Replication is concentrated entirely outside evidence level A: the single level-A pair did not replicate in either country, 4/13 for levels A+B, 6/19 and 5/16 overall (extended v1.2 set; the headline analysis in the text uses 16 and 15 testable pairs after excluding the negative control r01 and the post-hoc r22). No rule-relevant headline pair was contradicted in either country.

(**a**) Dual precision, coverage, and replication by evidence level (both layers). (**b**) Declared versus conservative precision as a slope chart; the shaded gap is the uninformative pairs counted as false positives. Forest plot with one row per quantity, both countries shown as separate labelled rows. Rows: declared-domain precision (NHANES 1.00 [0.541,1.000]; KNHANES 1.00 [0.478,1.000]); conservative precision (0.375 [0.152,0.646]; 0.333 [0.118,0.616]); rule coverage (0.889; 0.882); replication rate at evidence level A (0/1 = 0.00 both); level A+B (4/13 = 0.308 both); all rules (NHANES 6/19 = 0.316; KNHANES 5/16 = 0.312). Colours encode metric family: navy = declared precision, dark grey = conservative precision, teal = coverage, ochre = replication (level A, A+B, all). Value labels give the estimate and its k/n denominator. All are proportions on a 0-1 axis; precision and replication rows carry exact binomial intervals, while coverage is a census proportion with no interval.

Statistics: Unit = (exposure flag, outcome item) pair; rule-relevant pairs only; declared-domain precision = replicated / (replicated + contradicted); conservative = replicated / all rule-relevant testable pairs; coverage = P(testable | a rule exists), analysis_plan section 0.4 correction 17b; intervals are Clopper-Pearson exact; contradicted = 0 in both countries.

Abbreviations: CI = confidence interval; BHY = Benjamini-Hochberg-Yekutieli; FDR = false discovery rate; NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey.

---

---

**Figure 4. Continuous (per-1-SD) dose-response for rule-relevant pairs, survey-weighted.**

Modelling exposures continuously reproduces the binary layer's pattern rather than overturning it. Serum cotinine per SD is unrelated to cataract (OR/SD 0.92, q=0.31) and to late AMD (1.08, q=0.53) in NHANES, so the smoking nulls are not created by dichotomising self-reported exposure. BMI x cataract, by contrast, is significant per SD in KNHANES (1.077, 95% CI 1.034-1.122, q=0.0014) and null in NHANES (1.030, q=0.71): with BMI >= 25 affecting roughly a third of the KNHANES sample, that rule's binary null partly reflects the pre-specified cut-point. Direction agreed with the rule in 19/24 NHANES and 9/10 KNHANES rule-relevant pairs.

(**a**) OR per 1 SD for rule-relevant pairs, NHANES (US) and KNHANES (KR). Forest plot, one row per (exposure, outcome) pair. Rows are grouped by exposure family (glycaemia, adiposity, lipids, trace elements, smoking biomarker, micronutrients, inflammation) and sorted by OR within family. Point colour encodes the confirmatory result: brick = q<0.05 and OR>1, teal = q<0.05 and OR<1, grey = not significant. Rows span the glycaemic pairs (highest OR/SD: HbA1c-retinopathy 1.96 NHANES / 1.98 KNHANES) down to the around-null behavioural pairs (serum cotinine-cataract 0.92, BMI-cataract 1.03 NHANES) and the lowest lipid estimate (triglycerides x late AMD 0.717 in NHANES, not significant).

Statistics: OR per 1 standard deviation, survey svyglm (strata/PSU), same adjustment set as the binary layer; rule-relevant pairs only; all of them are shown; point colour encodes q<0.05 and direction; OR=1 dashed reference line; tautological pairs excluded; see analysis_plan section 18.2.

Abbreviations: SD = standard deviation; OR = odds ratio; CI = confidence interval; NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey.

---

**Figure 5. Power: minimum detectable OR (80%) versus observed OR for rule-relevant pairs.**

Most rule nulls are informative rather than underpowered. The median minimum detectable odds ratio at 80% power is 1.337 in NHANES and 1.159 in KNHANES, and 17 of the 30 rule-relevant pairs are classifiable as powered nulls, the design could have excluded a 2-fold association. The pairs that did replicate sit in the opposite corner (large observed OR, small detectable OR), i.e. they were both well powered AND large; no pair replicated on the strength of a small detectable effect alone. Design effects were derived per pair from the survey/model CI-width ratio (median 1.07 NHANES, 1.26 KNHANES), not assumed.

(**a**) Minimum detectable OR (80% power) vs observed OR. Scatter, both axes on a log scale, one point per rule-relevant pair (NHANES n=17, KNHANES n=13). x = minimum detectable OR at 80% power; y = observed OR. Points are coloured by three-state label (blue = replicated, grey = uninformative); replicated pairs cluster at high observed OR and low detectable OR, while uninformative pairs sit near OR = 1 across the detectable range. The dashed y = x identity line separates points whose observed effect is larger than the design could detect from those it could not; the y-axis spans 0.55–2.55 so protective estimates below 0.95 remain visible. NHANES replicate count 6, KNHANES 5; no contradicted points exist to plot.

Statistics: rule-relevant pairs: NHANES n=17, KNHANES n=13; log-log axes; x = minimal OR detectable at 80% power (two-sided alpha=0.05); y = observed OR; OR=1 lines on both axes and the y = x identity line; the shaded region above the identity line marks observed effects larger than the design could detect; design effect derived per pair from the survey/model CI-width ratio (median 1.07 / 1.26).

Abbreviations: OR = odds ratio; MDE = minimum detectable effect (here, the minimum detectable odds ratio at 80% power); NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey.

---

**Figure 6. Cross-cohort transportability of the literature-derived exposome rules across eight ageing cohorts.**

Only 6 of the 21 literature-derived rules can be tested in the eight ageing cohorts, and of those two met the pre-registered count criterion (neither prediction interval excluded unity). r02 (self-reported diabetes as proxy for hyperglycaemia → cataract) replicates in three of four testable cohorts (LASI OR 1.88, SHARE 1.75, CLHLS 3.59; CRELES 1.31, q=0.051). r20 (smoking → moderate vision impairment) replicates in three of five with ALL five pointing the same way (HRS 1.61, ELSA 1.49, SHARE 1.09; KLoSA 1.10 and CLHLS 1.03 uninformative). By contrast r10 (smoking → cataract) does not transport and one cohort reverses direction, not a regional pattern (p = 0.45): risk-increasing in SHARE (1.11, q=0.0095) but significantly PROTECTIVE in CLHLS (0.748, q=0.0012), with ELSA (0.77) and CRELES (0.70) also protective. r12 (alcohol → cataract) is contradicted in CLHLS (0.809, q=0.018) and not replicated in SHARE.

(**a**) Three-state composition per rule across the cohorts that can test it. Stacked horizontal bar, one bar per testable rule, segmented by outcome state: replicated, uninformative, contradicted. Counts are the number of cohorts contributing that state. r02 = 3 replicated + 1 uninformative; r20 = 3 replicated + 2 uninformative; r10 = 1 replicated + 2 uninformative + 1 contradicted; r12 = 1 uninformative + 1 contradicted; r13 = 1 replicated + 1 uninformative; r11 = 1 uninformative. The uninformative segment is drawn as its own colour and is never merged into either other segment.

(**b**) Odds ratio per (rule, cohort) pair, coloured by outcome state. Forest plot, one row per pre-registered confirmatory pair (18 rows). Rows are cohort labels grouped under a bold rule header; point colour drives the state encoding (blue = replicated, grey = uninformative, brick = contradicted). x = odds ratio. Estimates span 0.702 (CRELES r10) to 3.589 (CLHLS r02). Intervals are cluster-robust by person; SHARE is pooled over five imputation replicates by Rubin's rules. Rows whose interval crosses 1 while the point estimate points away from the other cohorts (r10 in ELSA and CRELES, r12 in SHARE) are visible as such and must not be read as disagreement.

Statistics: Unit = pre-registered (rule, cohort) pair; 18 pairs across 6 rules and 7 cohorts; three states: replicated / uninformative / contradicted (R11 definition, analysis_plan section 19.7); transportable = replicated with q<0.05 in >=2 cohorts (pre-declared in section 19.7); 15 rules have no bar at all. Their missing requirements overlap, so the counts exceed 15: 5 need fundus imaging, 3 a blood assay, 3 geocoded exposure, 2 a dietary index, 1 tonometry or optic-disc grading and 1 a lipid panel; forest intervals are cluster-robust by person; SHARE pooled over 5 imputations (Rubin); forest drawn on a log axis with the null line at OR = 1 (project-local renderer; see backend.renderer).

Abbreviations: OR = odds ratio; CI = confidence interval; BHY = Benjamini-Hochberg-Yekutieli; FDR = false discovery rate; AMD = age-related macular degeneration; SHARE = Survey of Health, Ageing and Retirement in Europe; HRS = Health and Retirement Study; ELSA = English Longitudinal Study of Ageing; KLoSA = Korean Longitudinal Study of Ageing; LASI = Longitudinal Ageing Study in India; MHAS = Mexican Health and Aging Study; CLHLS = Chinese Longitudinal Healthy Longevity Survey; CRELES = Costa Rican Study on Longevity and Healthy Ageing; IOP = intraocular pressure; CDR = cup-to-disc ratio; r01-r22 = pre-registered rule identifiers in configs/rules.yaml.

---
