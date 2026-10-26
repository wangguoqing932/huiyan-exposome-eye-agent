# STROBE checklist

Reporting checklist for the observational cohort analyses. The cross-cohort synthesis additionally follows standard meta-analytic reporting (REML τ², Cochran's Q, I², prediction intervals), which STROBE does not cover.

**TRIPOD+AI and DECIDE-AI are not applicable to this work** and are not claimed: both govern prediction models with estimated coefficients, whereas this study evaluates deterministic rules taken from the literature, reports no calibration or discrimination, and involves no prospective deployment.

| # | Item | Status | Where | Note |
|---|---|---|---|---|
| 1a | Indicate the study's design in the title or abstract | **MET** | Title; Abstract Methods | "pre-specified cross-cohort evaluation"; the design is a multi-cohort analysis of existing survey data |
| 1b | Summarise in an informative and balanced abstract | **MET** | Abstract | structured Background/Methods/Results/Conclusions; the positive control's failure is reported, not omitted |
| 2 | Explain the scientific background and rationale | **MET** | Introduction | 21 literature-derived rules and the pooling practice being questioned |
| 3 | State specific objectives, including pre-specified hypotheses | **MET** | Introduction; Methods | the four pre-specified items are named and separated from five analyses added later |
| 4 | Present key elements of study design early | **MET** | Methods | cross-cohort external validation of a rule base |
| 5 | Describe setting, locations, relevant dates | **PARTIAL** | Table 1; Methods | cohorts and their provenance are given; **survey fieldwork dates per cohort and recruitment periods are not tabulated** — reviewers asked for these |
| 6 | Eligibility criteria, sources and methods of selection | **PARTIAL** | Methods; Table 1 | cohorts named and frames described; **participant-level inclusion and exclusion flow is not reported** |
| 7 | Define all outcomes, exposures, predictors, confounders | **MET** | Methods; Table 2; construct-substitution table | including the seven rules tested on broader constructs than they declare |
| 8 | For each variable, give sources of data and measurement detail | **MET** | Methods; Table 1; construct-substitution table | codebook-verified operationalisation is the study's method |
| 9 | Describe efforts to address bias | **PARTIAL** | Methods; Discussion | E-values, prediction intervals, leave-one-out, positive control; **the survey-design variance deviation (section 19.7 not implemented) is disclosed but not remedied** |
| 10 | Explain how the study size was arrived at | **PARTIAL** | Methods; Supplementary Table S5 | no a priori sample-size calculation; per-pair minimum detectable odds ratios are reported post hoc, which is weaker |
| 11 | Explain how quantitative variables were handled | **MET** | Methods | per-cohort BMI cut-points; continuous exposures standardised; per-decade age in the control |
| 12a | Describe all statistical methods | **MET** | Methods | REML tau-squared, Cochran's Q, I-squared, t-based prediction intervals, E-values with the odds-ratio to risk-ratio conversion |
| 12b | Describe methods to examine subgroups and interactions | **MET** | Methods; Results | regional subgroups are reported as post hoc, with the k=2 non-independence stated |
| 12c | Explain how missing data were addressed | **PARTIAL** | Methods | **complete-case analysis; covariate missingness is disclosed in the Limitations (HRS 51.31%, ELSA 20.49%, MHAS 80.7%) but no imputation or sensitivity analysis for it is reported** |
| 12d | If applicable, sampling strategy (complex survey design) | **NOT MET** | Methods; deviations | **section 19.7 required survey strata/PSU/weights for SHARE and LASI; the frames contain no design variable at all and an unweighted cluster-robust model was used. Disclosed, not remedied.** |
| 12e | Describe sensitivity analyses | **MET** | Results; Supplementary Table S4 | leave-one-cohort-out, E-values, CLHLS single-wave sensitivity, meta-regression on mean age |
| 13 | Report numbers of individuals at each stage | **NOT MET** | Table 1 | **participant counts per cohort are now reported (285,878 participants; 598,386 person-waves), but there is no flow diagram and no accounting of who was excluded at each step from source file to analysed set** |
| 14a | Give characteristics of study participants | **MET** | Table 1b | age, sex, smoking, diabetes, BMI above the cohort cut-point and the two outcome prevalences, by cohort, on 598,386 person-waves. Constructs that differ are footnoted rather than merged: HRS and KLoSA record cataract as surgery, CLHLS age is a baseline value repeated across waves. |
| 14b | Indicate number of participants with missing data | **PARTIAL** | Table 1b | missingness tabulated per variable and cohort. **Partial because most 100% cells reflect frame coverage, not item non-response** — the frames carry only what the rules need, so the table is annotated to that effect rather than presented as a response rate. |
| 15 | Report numbers of outcome events | **MET** | Results; Table 4 | per-pair counts and three-state outcomes |
| 16a | Give unadjusted estimates and confounder-adjusted estimates | **PARTIAL** | Results | **adjusted estimates only; unadjusted estimates are not reported** (author check this) |
| 16b | Report category boundaries for continuous variables | **MET** | Methods; Table 1 | BMI 25/30 by cohort; age per decade |
| 16c | Translate relative risk into absolute risk | **NOT MET** | — | **no absolute risks or risk differences are reported; all estimates are odds ratios** |
| 17 | Report other analyses done | **MET** | Results; Supplementary | positive control, NHANES construct validation, evidence-base audit |
| 18 | Summarise key results with reference to objectives | **MET** | Discussion | including the positive control's failure |
| 19 | Discuss limitations | **MET** | Discussion | construct substitutions, ascertainment, measurement, positive control, survey variance deviation |
| 20 | Give a cautious overall interpretation considering limitations | **MET** | Discussion; Conclusions | the strongest form of the original claim is explicitly withdrawn |
| 21 | Discuss generalisability (external validity) | **PARTIAL** | Discussion | **generalizability is discussed for the measurement mechanism, but the equity and resource-setting implications of access-dependent ascertainment are not developed** (author check this) |
| 22 | Give the source of funding and role of funders | **NOT MET** | Declarations | **funding statement is a placeholder to be completed by the authors** |

## Summary of gaps

| Status | Count |
|---|---|
| MET | 18 |
| PARTIAL | 8 |
| NOT MET | 4 |

**The 4 unmet items are the honest state, not an oversight in this
checklist.** Four of them (12d, 13, 14a, 14b) are methodological and were raised
independently by the mock reviewers; 12d in particular is a disclosed deviation
from the pre-registered protocol rather than a reporting omission, and it cannot
be fixed by writing — it would require rebuilding the cohort frames with survey
design variables and re-running the layer.

**Recommended before submission, in order of how likely an editor is to ask:**
1. Item 14a — a descriptive table of the analysed populations by cohort
2. Item 13 — a participant flow from source file to analysed set
3. Item 22 — the funding statement
4. Item 12c/14b — missingness tabulated and a sensitivity analysis for it
5. Item 12d — either rebuild frames with survey design or state the deviation in
   the Methods as prominently as it is stated here
6. Item 16c — absolute risks alongside the odds ratios
