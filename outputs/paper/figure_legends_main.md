# Figure Legends

**Figure 1. System architecture of Huiyan.**

Huiyan integrates three layers, a deterministic rule engine, a knowledge-graph retrieval module (LightRAG), and an LLM arbiter, to produce explainable risk-graded reports for exposome (metabolic, nutritional, lifestyle and environmental) × major blinding eye disease interactions, with full traceability from output back to source evidence.

(**a**) End-to-end pipeline: input → entity normalisation → rule engine → LightRAG retrieval → LLM arbiter → report with trace.

(**b**) Three layers, one traceable path: rule layer (deterministic), KG layer (evidence-grounded), arbiter layer (bounded). Every step belongs to one layer, so an output can be followed back to its evidence.

(**c**) Four output views: clinician card / patient handout / research table / policy brief. All from single inference pass.

Statistics: Rule layer: 21 rules (A1/B15/C5); KG layer: 27,136 nodes and 1,060 evidence chunks; Arbiter: local Qwen3.8-27B at temperature 0 in the reported runs.

Abbreviations: LLM = large language model; KG = knowledge graph; YAML = YAML Ain't Markup Language; LightRAG = lightweight retrieval-augmented generation.

---

**Figure 2. External performance, decision mechanism, and provenance of the positives.**

(a) F1 on the 301 KNHANES pairs and on the 296 pairs whose rules the post-confirmatory revision did not touch: agent 0.375 / 0.211, rule layer 0.360 / 0.200, LightRAG 0.176 / 0.089, pure LLM 0.173 / 0.122 and naive RAG 0.120 / 0.086. Every method loses about two thirds of its F1 when the revised pairs are removed; the ordering is unchanged.

(b) Which layer decides each of the 474 pairs in the fused run: no rule fires 418, evidence at level B or above confirms 45, the LLM arbiter 6, negative-control abstention 3 and no relevant evidence 2. The language model touches six cells.

(c) Replicated pairs by provenance. In the development matrix (NHANES) all 6 replicated pairs are covered by a rule that the revision touched and none is contamination-free; in the external matrix (KNHANES) 5 of the 18 replicated pairs sit on revised rules and 13 on untouched ones.

(d) Three-state decomposition on the 301 pairs. The agent and the rule layer recall the same 0.50 of replicated pairs and flag the same 0.17 of contradicted pairs; they differ only on uninformative pairs (0.07 versus 0.08). The gate is therefore a precision instrument, not a recall instrument.

Statistics: unit = (exposure flag, outcome item) pair; gold = three-state label under survey variance; baselines recomputed with failed parses treated as missing rather than negative (R31 addendum P0); F1 for baselines is the mean over five seeds (11, 22, 33, 44, 55), agent and rule layer are deterministic; paired McNemar on accuracy, Benjamini-Hochberg corrected over the 15 tests per matrix (q < 0.001).

Abbreviations: F1 = F1 score; G0 = rule layer; G2 = deployable agent (rule layer + negative-control gate + evidence confirmation + arbiter); KNHANES = Korea National Health and Nutrition Examination Survey; NHANES = National Health and Nutrition Examination Survey; RAG = retrieval-augmented generation.

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
