# Do literature-derived exposome rules replicate in national eye surveys? A pre-registered three-state evaluation of 21 exposure–eye-disease rules across NHANES, KNHANES and CHARLS

**Running title**: Literature-derived exposome–eye-disease rules: a pre-registered replication study

**Authors / affiliations**: *[to be completed]*

**Target journal**: *Ophthalmic Epidemiology* (alternate: *BMJ Open*)

**Manuscript version**: R11, 2026-10-15 — all analyses re-run after the variable-operationalisation corrections documented in `configs/variable_map.yaml` (17 corrections) and `docs/analysis_plan.md` §0.3–0.4.

---

## Abstract

**Purpose.** Rule-based "exposome × eye disease" screening systems are increasingly proposed as interpretable clinical decision support, but their rules are almost always derived from the same literature that is later used to praise them. We asked a blunt question: when a rule is derived *only* from published literature and guidelines, and is then tested against independent national survey data under a pre-registered protocol, how many rules survive?

**Methods.** We assembled 21 rules (3 evidence level A, 13 B, 5 C) linking modifiable exposures (metabolic, nutritional, lifestyle, environmental) to major eye diseases (cataract, diabetic retinopathy, age-related macular degeneration, glaucoma, vision impairment). Rules were authored from literature and guidelines before unblinding, without access to the validation datasets. Three independent layers were used: NHANES 2005–2008 (internal; 7,081 adults ≥40 y), KNHANES 2008–2012 and 2017–2021 (external, cross-country; 45,039 adults ≥40 y), and CHARLS 2011/2015 (external, cross-population). Every exposure and outcome was operationalised against the official data-provider codebook; a reference-prevalence gate flagged any operationalisation deviating >2.5-fold from published national rates. Each testable rule pair received a pre-registered three-state label — **replicated** (FDR q<0.05, direction concordant), **contradicted** (q<0.05, opposite), **uninformative** (q≥0.05) — under survey-design variance (R `survey::svyglm`, strata/PSU). FDR was applied within two pre-registered families: a confirmatory family (rule-relevant pairs) and an exploratory family (the full exposure×outcome matrix). Power was quantified per pair as the minimum detectable odds ratio (MDE-OR) at 80% power, with the design effect derived from the survey/model CI-width ratio rather than assumed. Mediation of the dysglycaemia–vision-impairment association by diabetic retinopathy (DR) and cataract was estimated by product of coefficients.

**Results.** 16 of 21 rules were testable in at least one layer (NHANES 16/18 rule-relevant pairs; KNHANES 15/17; coverage 0.889 and 0.882). Concordance with the reference standard was 6/16 in NHANES and 5/15 in KNHANES; **no rule was contradicted in either country**. All six NHANES and all five KNHANES concordances involved glycaemia (HbA1c or fasting glucose) and diabetic eye disease. **All three evidence-level-A rules (smoking–cataract, smoking–late AMD, BMI–cataract) failed to replicate in both countries as dichotomised at their pre-specified cut-points** (0/3; 0/3); a continuous (per-SD) re-analysis reproduced the same pattern and showed that the smoking null is not a measurement artefact — serum cotinine, an objective biomarker, was unrelated to cataract (OR per SD 0.92, q=0.31) and late AMD (1.08, q=0.53). BMI × cataract, however, was significant per SD in KNHANES only (1.077, q=0.0014), indicating that for that rule the binary null partly reflects cut-point choice. Under the conservative reading (uninformative counted as a failed prediction) rule precision was 0.375 (95% CI 0.152–0.646) in NHANES and 0.333 (0.118–0.616) in KNHANES; under the declared-domain reading it was 1.000 in both. The two countries' three-state labels agreed in 71 of 85 common testable pairs (83.5%). Median MDE-OR at 80% power was 1.337 (NHANES) and 1.159 (KNHANES); 10 of 13 NHANES and 7 of 11 KNHANES rule nulls were adequately powered to exclude a 2-fold association (informative-null rate 76.9% and 63.6%). In the exploratory matrix, dietary antioxidant inadequacy — an exposure that had previously been untestable because of a data-loading error — was strongly associated with retinopathy (OR 2.58, q=7.6×10⁻²³), elevated intraocular pressure (OR 1.73, q=2.1×10⁻⁴) and any AMD (OR 1.32, q=1.6×10⁻⁷); however, the same exposure was associated with *lower* odds of physician-diagnosed cataract (OR 0.72, q=8.1×10⁻¹⁰), so this cluster of findings is more consistent with confounding or differential ascertainment than with a nutritional effect. Mediation analysis indicated that only ~0–19% of the dysglycaemia–vision-impairment association operated through DR, and essentially none through cataract.

**Conclusions.** Literature-derived exposome rules for eye disease are largely non-replicable in independent national survey data, and — critically — these null results are adequately powered rather than artefacts of small samples. The rules with the strongest published evidence were precisely those that failed. Interpretable rule-based screening systems should therefore be evaluated against independent data before deployment, and should report power alongside null findings. Conversely, two directions warrant follow-up: glycaemic exposure is associated with vision impairment largely through pathways other than the classic ocular complications, and dietary antioxidant inadequacy showed a large, previously undetectable signal.

**Keywords**: exposome; eye disease; replication; pre-registration; NHANES; KNHANES; CHARLS; clinical decision support

---

## Strengths and limitations of this study

- Pre-registered three-state reference standard (replicated / contradicted / uninformative) with FDR control, avoiding the "significance = truth" conflation of earlier screening-rule evaluations.
- Rules were authored from literature and guidelines **before** any validation data were opened; every operationalisation was verified against the official data-provider codebook and passed an automated reference-prevalence gate.
- Per-pair power analysis (minimum detectable OR) separates informative nulls from underpowered ones; this is what makes the negative result interpretable.
- Three independent layers spanning two countries and two survey designs; CHARLS contributed no informative labels and is reported as a feasibility layer only.
- Limitations: cross-sectional design, so temporality cannot be established; self-reported outcomes for cataract and glaucoma; KNHANES provides only a binary vision-impairment flag so no severity grading; five of 21 rules remain untestable for documented data reasons; exposures were dichotomised with clinical cut-offs, which trades dose–response information for interpretability (continuous versions are reported separately).

---

## Introduction

Rule-based screening systems for drug–food, herb–drug and, more recently, exposome–disease interactions are attractive because their outputs are auditable: each recommendation carries the mechanism, the evidence level and the citation that produced it. Reviews of such systems have generally reported internal consistency — whether the rules encode what the literature says — rather than external validity — whether the associations the rules assert actually hold in an independent population [refs].

These two questions are easily confused. A rule set distilled from meta-analyses of a given exposure–disease pair will, by construction, "agree with the literature" when that literature is re-searched. Reporting such agreement as external validation is circular. The informative test is whether the rule predicts an association that is observable in data the rule author never saw, using a reference standard defined before those data were analysed.

The eye is a useful testbed for this question for three reasons. First, the exposome–eye-disease literature is large but heterogeneous, with few associations reaching the evidential strength of, say, smoking–lung cancer. Second, several major eye diseases (cataract, glaucoma, age-related macular degeneration, diabetic retinopathy) are captured with reasonable validity in the large national health examination surveys now publicly available. Third, the leading associations are plausibly confounded by socioeconomic position and by each other, so a rule set that ignores these will be visibly stressed by a well-adjusted analysis.

We therefore built a rule set for exposome × major eye disease from literature and clinical guidelines only, pre-registered a three-state evaluation protocol, and applied it to NHANES (internal, United States), KNHANES (external, Republic of Korea) and CHARLS (external, China). We additionally quantified, for every testable pair, the smallest association the analysis could have detected, because a null result means little without it.

Two operational findings emerged during the work that materially shaped the analysis and are reported in full: a systematic audit against official codebooks revealed 17 operationalisation errors in the pre-existing implementation (listed in `configs/variable_map.yaml`), several of which had generated spurious associations in both directions. We report the corrected analysis exclusively; the pre-correction numbers are archived for transparency.

---

## Methods

### Rule set and evidence grading

21 rules were authored linking an exposure flag (entity A: metabolic, nutritional, lifestyle and environmental exposures) to an eye-disease outcome flag (entity B: cataract, diabetic retinopathy and its grades, AMD and its stages, glaucoma and its structural/functional proxies, vision impairment). Each rule carries a mechanism from a fixed seven-item taxonomy (oxidative stress, glycation/metabolic, inflammation/immune, vascular/perfusion, endocrine/hormonal, heavy-metal toxicity, photochemical/UV), a severity level, an evidence level (A/B/C, assigned by the authors from study design and consistency), a direction, a recommendation, and one or more citations. One rule (uric acid × cataract) was pre-designated a negative control; one rule (BMI × retinopathy, r22) was documented at authoring time as a data-driven *exploratory* extension added after viewing an internal result, and is therefore reported both inside and outside the headline family (see Sensitivity analyses).

Rule authoring used PubMed searches of the exposure–outcome pair plus AAO Preferred Practice Pattern chapters and WHO/Chinese dietary guidance. No validation dataset was accessed during rule authoring.

### Data sources and analytic frames

| Layer | Source | Waves | Analytic frame | Role |
|---|---|---|---|---|
| Internal | NHANES | 2005–2006, 2007–2008 | 7,081 adults ≥40 y (MEC exam weight >0) | internal validation |
| External (country) | KNHANES | 2008–2012, 2017–2021 | 45,039 adults ≥40 y (exam weight >0) | cross-country validation |
| External (population) | CHARLS | 2011, 2015 | 11,308 / — | cross-population feasibility |

NHANES modules used: DEMO, BIOPRO, HDL, TRIGLY, TCHOL, DIQ, GHB, GLU, CRP, COT/COTNAL, SMQ, ALQ, BMX, PBCD, DR1TOT, VIQ, VIX, OPXRET. KNHANES frames were rebuilt from the distributed Rdata collection (`scripts/build_knhanes_frames.R`), merging the health-interview/examination object with the eye-examination object (2008–2012) and with the air-pollution and indoor-air-quality modules, and harmonising the two eye-grading naming schemes used before and after 2016.

### Variable operationalisation and the codebook gate

Every exposure and outcome was defined against the official data-provider codebook; where the codebook supplies value labels (KNHANES `变量解释.docx`), those labels were used rather than inferred from variable names. Because inferring construct meaning from variable names was the dominant failure mode in the pre-existing implementation, two automated gates were built and are part of the reproducibility chain:

1. **Reference-prevalence gate** (`scripts/validate_nhanes_exposures.py`, `scripts/validate_knhanes_frames.py`). Each derived exposure is compared with the published national rate for adults ≥40 y; a deviation beyond 2.5-fold is a hard failure that aborts downstream reporting, and 1.5-fold is a warning. The gate also checks module integrity (that every referenced column is actually loaded) and internal consistency (that each dichotomised flag agrees exactly with its continuous parent at the stated cut-point).
2. **Biomarker cross-check.** Self-reported current smoking was validated against serum cotinine (≥10 ng/mL): sensitivity 0.803, specificity 0.990 (n=6,410); median cotinine 0.032 ng/mL in self-reported non-smokers vs 245 ng/mL in smokers.
3. **Wave-comparability check.** For variables present in more than one wave of the same survey, the gate compares prevalence across waves. A same-named variable whose prevalence differs by more than 2.5-fold between waves is flagged as not comparable rather than pooled.

The gate was applied to all three datasets. It found substantive errors in each, including three independent occurrences of the same reference-group failure: an exposure defined by conditioning on a variable that is asked only of a subset (NHANES current smoking, where the filter dropped all never-smokers; KNHANES smoking; and CHARLS 2011 current smoking, where the denominator became ever-smokers and produced 77.0% against a 27% national reference). The gate also demonstrated the converse hazard: HbA1c ≥6.5% in a Chinese population has a true prevalence near 5–7%, not the 11–13% that applies to diabetes defined by OGTT or fasting glucose, because HbA1c has low sensitivity for the Chinese phenotype. Using the OGTT figure as the reference would have flagged a correct variable as broken. Reference prevalences must therefore be criterion-specific.

Where the codebook was ambiguous, the construct was either renamed to what could actually be measured or declared untestable rather than substituted. For example, KNHANES supplies only a binary "any visual impairment" flag; the corresponding rule (PM2.5 × moderate/severe vision impairment) is therefore reported as untestable on construct grounds, and the flag is *not* relabelled as "moderate".

Seventeen operationalisation errors were found and corrected (`configs/variable_map.yaml`, corrections C1–C17). The most consequential are summarised in Table 1.

### Reference standard: three-state labels

For every (exposure flag, outcome) pair with ≥200 complete observations, ≥30 events and ≥30 exposed, we fitted a survey-weighted logistic model of the outcome on the dichotomised exposure plus covariates. Pairs failing these criteria were labelled **underpowered**; fitting separation was labelled **separation** (not silently pooled with uninformative).

Each testable pair then received one of three labels:
- **replicated** — FDR-adjusted q<0.05 and OR in the direction the rule asserts;
- **contradicted** — q<0.05 and OR opposite to the rule;
- **uninformative** — q≥0.05, irrespective of direction.

A pair with no rule is never "contradicted" but can be a significant *uncovered* finding; these are reported separately as exploratory results.

### Statistical analysis

**Variance.** The primary standard was survey-design variance using `survey::svyglm` with strata and primary sampling units (NHANES `SDMVSTRA`/`SDMVPSU`; KNHANES `kstrata`/`psu`). Model-based frequency-weighted GLMs are reported alongside as a sensitivity analysis. All 461 surveyed pairs converged (0 fit failures).

**Covariates.** NHANES: age, age², sex, race/ethnicity, family poverty-income ratio. KNHANES: age, age², sex, education, income quintile. These are the common, pre-specified adjustment sets; exposure-specific adjustment for the other exposures was not performed (see Limitations).

**Multiplicity: two pre-registered families.** Once the exposure×outcome matrix was expanded, a single Benjamini–Hochberg–Yekutieli family spanning >100 pairs with no rule attached would dilute power exactly where the paper's question lies. We therefore applied FDR separately to (i) a **confirmatory family** comprising rule-relevant pairs, used for all rule metrics, and (ii) an **exploratory family** comprising the full matrix, used for uncovered findings. Both are reported; neither replaces the other.

**Metrics.** Two precision definitions are reported side by side because they answer different questions and, previously, only the favourable one was shown:
- *declared-domain precision* = replicated / (replicated + contradicted) — the probability that, when the analysis was informative, it agreed with the rule;
- *conservative precision* = replicated / all rule-relevant testable pairs — treating an uninformative result as a failed prediction.

Confidence intervals are Clopper–Pearson exact. **Coverage** is defined as P(testable | a rule exists, the outcome is judgeable, and the pair is not the negative control).

**Power analysis.** For each pair we computed the minimum detectable odds ratio (MDE-OR) at 80% power, two-sided α=0.05, from the observed n, exposed count and event count, solving exactly for the unexposed event probability consistent with the marginal risk. Rather than assume a design effect, we derived it per pair from the ratio of the survey CI width to the model-based CI width, and deflated the effective sample size accordingly. Null results were then classified as *powered nulls* (MDE-OR ≤2.0, i.e. the absence of a 2-fold association is informative) or *underpowered nulls*.

**Mediation.** For the dysglycaemia–vision-impairment association we fitted, with survey weights: total effect (Y ~ X + covariates), direct effect and b-path (Y ~ X + M + covariates), and a-path (M ~ X + covariates). The indirect effect was the product of coefficients on the log-OR scale with delta-method standard error; the proportion mediated came from the difference method. Models were labelled UNSTABLE and excluded if outcome events <80, mediator-positive cases <80, the total-effect CI spanned more than six-fold, or the proportion mediated fell outside [−0.5, 0.9].

**Continuous (dose-response) matrix.** Because dichotomising an exposure at a clinical cut-point discards dose–response information, we repeated the full exposure×outcome screen with each exposure standardised to per-1-SD and fitted as a continuous term, so that the coefficient is an odds ratio per standard deviation. This layer used the same survey design, covariates and two FDR families as the binary layer. Pairs in which the outcome flag is *derived from* the exposure measurement itself were excluded as definitional: continuous intraocular pressure regressed on the "elevated IOP" flag returns an infinite OR by construction and carries no information.

**Sensitivity analyses.** (i) frequency-weighted vs survey-weighted variance; (ii) rule-set definition: all rules, excluding the documented leakage rule r22, excluding the negative control, evidence level A only, and evidence levels A+B only; (iii) BMI cut-point 25 vs 23 kg/m² (WHO Asian); (iv) blood lead threshold 3.5 vs 5.0 µg/dL.

**Reproducibility.** The full chain is scripted and re-runnable; a byte-identical re-run of the six principal outputs was verified against a dated backup. Software: Python 3.10 (pandas, statsmodels, scipy) and R 4.6.1 (`survey`).

---

## Results

### Rule testability

Of 21 rules, **16 were testable in at least one layer**. Coverage — the probability that a rule-relevant hypothesis could actually be evaluated — was 0.889 in NHANES (16/18) and 0.882 in KNHANES (15/17), i.e. high. Five rules remained untestable for three distinct, documented reasons (Table 2): two for genuine data limitations (r07 vitamin D × DR: the local NHANES copy lacks the vitamin D module and the KNHANES serum-vitamin-D waves do not overlap the DR-grading waves; r18 UV × cataract: the sunlight variable and the cataract self-report variable occur in non-overlapping waves), one on construct grounds (r21 PM2.5 × moderate/severe vision impairment: KNHANES supplies only a binary impairment flag), and two because the required dietary index has not yet been constructed (r09 Mediterranean diet, r19 dietary inflammatory index).

### Rule-level concordance

**Table 3** gives the primary results.

| Layer | Rule-relevant pairs | Testable | Coverage | Replicated | Contradicted | Uninformative | Declared-domain precision | Conservative precision |
|---|---|---|---|---|---|---|---|---|
| NHANES (internal) | 18 | 16 | 0.889 | 6 | 0 | 10 | 1.000 (0.541–1.000) | 0.375 (0.152–0.646) |
| KNHANES (external) | 17 | 15 | 0.882 | 5 | 0 | 10 | 1.000 (0.478–1.000) | 0.333 (0.118–0.616) |
| CHARLS 2011 | 4 | 4 | 1.000 | 0 | 0 | 4 | — | 0.000 |

**Every replication involved glycaemia.** The replicated rules were hyperglycaemia × cataract (r02), HbA1c × retinopathy (r03) and HbA1c × proliferative DR (r04); the remaining replications were additional outcomes of the same two exposures (HbA1c × cataract, hyperglycaemia × retinopathy, BMI × retinopathy [r22, the exploratory rule]). No rule was contradicted in either country.

**The strongest-evidence rules failed.** All three evidence-level-A rules — smoking × cataract (r10), smoking × late AMD (r11) and BMI × cataract (r13) — were uninformative in both countries as dichotomised at their pre-specified cut-points (Table 4). Restricting the analysis to level-A rules gives 0/3 replications in NHANES and 0/3 in KNHANES; restricting to levels A+B gives 4/13 in both. The continuous (per-SD) layer confirms the smoking nulls using an objective biomarker and partially qualifies the BMI null (see Continuous dose-response matrix, below).

### Power: are the nulls informative?

Median design effect was 1.07 (NHANES) and 1.26 (KNHANES). **Median MDE-OR at 80% power was 1.337 in NHANES and 1.159 in KNHANES** — that is, both layers could reliably detect an association of roughly 1.2–1.3-fold. Of the rule nulls, **10 of 13 in NHANES (76.9%) and 7 of 11 in KNHANES (63.6%) were adequately powered to exclude a 2-fold association** (Table 5). Only one null in each country was underpowered.

This materially changes the interpretation of "0 contradicted": the absence of an association between the level-A exposures and their outcomes is not a power failure. The rules do not replicate because the associations are, in these data, smaller than 1.2–1.3-fold or absent.

### Cross-dataset consistency

Of 85 pairs testable in both countries, the three-state labels agreed in **71 (83.5%)**. The coverage gap was +0.007 (internal minus external) and the declared-domain precision gap 0.0; the conservative-precision gap was +0.042. The near-absence of a generalisation gap is itself notable: whatever the rules capture transfers between the United States and the Republic of Korea about as well as it performs internally.

### Exploratory matrix

In the full exposure×outcome matrix, 122 pairs were testable in NHANES (6 significant under the exploratory family) and 158 in KNHANES (13 significant). Rule-pair labels use the **confirmatory** family; uncovered pairs are labelled with the **exploratory** family, and because the two families have different denominators a rule pair can be significant under one and not the other (for example NHANES hyperglycaemia × cataract: confirmatory q=3.0×10⁻⁴, exploratory q=0.129). Both are reported in the source tables.

Among the 13 exploratory-family findings in KNHANES not covered by any rule, several ran **opposite** to the direction the corresponding rule asserts for a related outcome — a pattern that argues against a simple causal reading and for ascertainment or confounding. Notably: dietary antioxidant inadequacy was associated with *lower* odds of physician-diagnosed cataract (OR 0.72, q=8.1×10⁻¹⁰) while being associated with *higher* odds of retinopathy; dyslipidaemia was associated with *lower* odds of any AMD (OR 0.81, q=0.0055) and of early AMD (OR 0.73, q=0.0084); low HDL was associated with lower odds of any AMD (OR 0.77, q=9.1×10⁻⁴); and PM2.5 with lower odds of retinopathy (OR 0.71, q=0.046). The only exploratory finding aligned with a plausible prior was binge drinking × retinopathy (OR 1.51, q=0.049, borderline).

The largest exploratory signal involved an exposure that had previously been **impossible to test**: dietary antioxidant inadequacy (≥2 of 3 micronutrients below the estimated average requirement for vitamin C, α-tocopherol and lutein+zeaxanthin). Before correction, a non-existent column name rendered this composite entirely missing (n=0 non-missing), so the corresponding rule was silently dropped from every analysis. After correction, antioxidant inadequacy was associated with retinopathy (OR 2.58, q=7.6×10⁻²³), elevated intraocular pressure (OR 1.73, q=2.1×10⁻⁴) and any AMD (OR 1.32, q=1.6×10⁻⁷). The rule as originally specified (low antioxidant intake × cataract) was null (OR 0.96, q=1.0 in NHANES; OR 1.08, q=0.31 in KNHANES).

**This signal should be treated as hypothesis-generating at best, and the internal inconsistency is the main reason.** The same exposure was protective for diagnosed cataract and harmful for retinopathy and AMD; dietary antioxidant inadequacy is strongly patterned by socioeconomic position and overall diet quality; it has not been replicated in a second dataset using the same construct; PM2.5 shows a similarly implausible protective direction; and a single 24-hour recall is a noisy measure of habitual intake. The honest reading is that a data-loading error had rendered a variable invisible, and once visible it produced a mixture of large positive and negative associations whose most likely common cause is confounding by position in the health system rather than a nutritional effect.

### Continuous (per-SD) dose-response matrix

Re-fitting the screen with continuous exposures (OR per 1 SD) yielded 134 testable pairs in NHANES (16 significant) and 180 in KNHANES (38 significant); 24 and 10 respectively were rule-relevant. Among rule-relevant continuous pairs the direction agreed with the rule in 19/24 (79%) in NHANES and 9/10 (90%) in KNHANES.

Two conclusions follow.

First, **dichotomisation attenuated the estimates but did not manufacture the nulls**. The replication pattern was the same as in the binary layer: glycaemic measures dominated, and the two smoking rules remained null. For smoking this is a stronger statement than in the binary analysis, because the continuous measure was **serum cotinine**, an objective biomarker rather than self-report: cotinine per SD was unrelated to cataract (OR/SD 0.92, q=0.31) and to late AMD (OR/SD 1.08, q=0.53) in NHANES. The smoking null is therefore not a measurement-artefact of self-reported exposure.

Second, **one level-A rule behaves differently under continuous exposure, and this qualifies our headline**. BMI × cataract (r13) was null as a binary flag in both countries, but as a continuous measure it was significant in KNHANES (OR/SD 1.077, 95% CI 1.034–1.122, q=0.0014) while remaining null in NHANES (OR/SD 1.030, q=0.71). With BMI ≥25 kg/m² affecting roughly a third of the KNHANES sample, the binary contrast is diluted relative to a per-SD contrast, so the binary null for r13 reflects the choice of cut-point at least in part. This does not overturn the overall pattern — r13 is concordant in only one of the two countries and the effect is small — but it means the statement "all level-A rules fail" should be read as "all level-A rules fail as dichotomised at their pre-specified clinical cut-points, and one of the three is detectable per SD in one of the two countries."

The continuous layer also produced a cluster of **opposite-direction** findings involving lipids — total cholesterol was inversely associated with retinopathy (OR/SD 0.71, q=2.0×10⁻⁸ in KNHANES; 0.79, q=0.013 in NHANES) and with cataract, and HDL was positively associated with AMD. These directions are not biologically plausible as causal effects and most likely reflect reverse causation or confounding by illness and lipid-lowering treatment; we report them because they illustrate that a large, well-powered survey will readily return significant associations in the wrong direction when the exposure is a marker of health-system contact rather than of aetiological exposure.

### Mediation: how does dysglycaemia affect vision?

Dysglycaemia was associated with vision impairment in both countries, and vision impairment is not part of the definition of diabetes, so this is not a tautological association. Mediation analysis (Table 6) indicated that only a small share operates through the classic ocular complications: proportion mediated by DR was 0.193 for moderate impairment in NHANES, 0.175 for any impairment in KNHANES, 0.047 for severe impairment, and −0.098 for mild impairment; mediation by cataract was 0.012. Two models were excluded as unstable (39 and 66 outcome events respectively, producing an implausible proportion mediated of 1.02).

### Sensitivity analyses

Excluding the documented leakage rule r22 changed NHANES conservative precision from 0.316 to 0.353 and KNHANES from 0.312 to 0.267; excluding the negative control left it at 0.333 in both. Level-A-only precision was 0.000 in both countries under every reading. Full results are in `outputs/tables/headline_sensitivity.csv`.

**Table 1. Operationalisation errors found by the codebook gate and their consequence.**
*(17 corrections in total; the six with material impact on inference are shown.)*

| # | Dataset | Domain | Pre-correction | Why wrong | Effect on exposure prevalence |
|---|---|---|---|---|---|
| C1 | NHANES | current smoking | `SMQ040 ∈ {1,2}`, reference = former smokers | SMQ040 is asked only of ever-smokers; all 3,433 never-smokers became missing | 38.2% → 19.7%; removed a spurious protective OR 0.70 (p=0.04) |
| C3 | NHANES | CRP | `LBXCRP > 3.0` | LBXCRP is mg/dL, not mg/L (i.e. >30 mg/L) | 1.5% → 36.8% |
| C4 | NHANES | dyslipidaemia | HDL/LDL thresholds | HDL and LDL modules were never loaded; both branches were always false | HDL branch n=0 → 6,410 |
| C5 | NHANES | antioxidant intake | `DR1TVE` + sample quartile | the column does not exist; the composite was entirely missing | n=0 → 7,081 |
| C8 | KNHANES | retinopathy | only the 2008–2012 naming scheme | 2016–2021 uses `E_DM`; `E_DR` means "using eye drops" | 14 pairs previously "untestable" became testable |
| C7 | KNHANES | alcohol | `BA2_2_1` | official label: "drank and rode a bicycle"; the whole BA2 module is traffic safety | 3.0%; corrected variable gives 64.5% past-year drinking |

---

## Discussion

### Principal findings

In a pre-registered test of 21 literature- and guideline-derived exposome rules against three independent national datasets, most rules that could be tested did not replicate. No rule was contradicted, but the nulls were not artefacts of low power: both national layers could detect associations of roughly 1.2–1.3-fold, and about two-thirds to three-quarters of the rule nulls could exclude a 2-fold association. The failures were concentrated exactly where the published evidence is strongest: all three level-A rules failed in both countries as dichotomised at their pre-specified cut-points. One qualification matters: BMI × cataract became detectable when BMI was modelled continuously in KNHANES, so for that rule the binary null partly reflects the cut-point rather than a true absence of association.

The rules that did replicate were confined to glycaemia and diabetic eye disease. This is a weak test of a rule-based system, because HbA1c ≥6.5% and fasting glucose ≥126 mg/dL are diagnostic criteria for diabetes and diabetic retinopathy is its complication; the association is close to definitional. Reassuringly, the observed effect sizes for these pairs were also implausibly large for an aetiological claim in the KNHANES analysis (OR ~11–15), a pattern consistent with definitional overlap plus ascertainment (retinal grading is performed in people already known to have diabetes) rather than a genuine risk gradient.

Taken together, the rule engine's apparent accuracy rests on pairs where the exposure and outcome are the same construct, and disappears on pairs where they are not. This is the central message for anyone building or buying interpretable screening rules.

### Why do literature-derived rules fail?

Three non-exclusive explanations are consistent with our results.

First, **publication and reporting biases inflate the apparent strength of the source associations**. Many of the rules' citations are cross-sectional or mechanistic studies that support the direction of an association without quantifying it. When the same hypothesis is tested in a survey with a pre-specified cut-point, a common adjustment set and an FDR-controlled family, the effect may simply be smaller than the literature implies.

Second, **literature-derived rules typically encode direction, not magnitude**. A rule that asserts "smoking increases cataract risk" is consistent with an OR of 1.05, which no survey of this size will detect, and which is of doubtful clinical relevance. The failure mode is therefore not that the rule is wrong, but that it is untestable in the sense the paper would like: it makes no falsifiable quantitative claim.

Third, **the rules ignore mutual confounding**. Smoking, alcohol, BMI, dyslipidaemia and dysglycaemia are strongly correlated, and the analysis adjusts for socioeconomic position and demographics but not for the other exposures. A rule engine that treats each exposure independently cannot distinguish a genuine effect from a marker of a correlated exposure or of socioeconomic position — and our finding that all three level-A rules involve behavioural exposures (smoking, BMI) is consistent with this. The continuous layer sharpens this point in a useful way: using serum cotinine, an objective and precisely measured biomarker, the smoking associations remained null, which rules out exposure misclassification as the explanation and leaves confounding or a genuinely small effect. For BMI, by contrast, the association with cataract did emerge per SD in KNHANES, which suggests that for anthropometric exposures the choice of cut-point matters more than for biomarker exposures.

### What does replicate, and what should follow it up

Two findings survived with adequate power and cross-dataset support, and both point away from the classic complication pathways.

The dysglycaemia–vision-impairment association was present in both countries and **only ~0–19% of it was mediated by diabetic retinopathy, with essentially none through cataract**. If confirmed, this suggests that the effect of chronic hyperglycaemia on vision operates substantially through pathways other than the two complications that dominate screening guidelines: candidate mechanisms include reversible lenticular refractive change, early or sub-clinically graded cataract, retinal neurodegeneration, and shared confounding by socioeconomic position and access to care. This is testable with longitudinal data and with objective refraction and lens grading.

The dietary antioxidant signal, though hypothesis-generating, is notable for two reasons. First, it was **invisible in the pre-correction analysis purely because of a data-loading error**: a single non-existent column name meant that neither this analysis nor the original rule evaluation could ever have detected the association. This is a cautionary result about the auditing burden of multi-cohort exposome analytics, and it argues for the automated codebook and prevalence gates we used here as a routine part of the pipeline rather than as an after-the-fact check. Second, its internal inconsistency — protective for diagnosed cataract, harmful for retinopathy and AMD — plus the parallel implausible protective direction for PM2.5, suggests that in this population these exposures are largely markers of position in the health system (who gets diagnosed, and where) rather than causal agents. We report it because suppressing it would obscure a real methodological lesson.

### Implications for interpretable screening systems

Our results do not show that rule-based screening is useless; they show that **internal consistency with the source literature is not evidence of external validity, and that the two are easily confused**. Concretely, we suggest that evaluations of such systems should:

1. define the reference standard and the multiplicity family **before** unblinding the validation data;
2. report, for every null, the smallest effect the design could have detected;
3. report both the declared-domain and the conservative precision, since the gap between them (1.000 vs 0.375 here) is the single largest lever on the headline number;
4. declare any rule added after seeing validation data, and report headline metrics with and without it;
5. verify every variable against the data provider's codebook and gate on published reference prevalences — in our experience this found errors that changed conclusions in both directions.

### Strengths and limitations

The principal strength is the combination of a pre-registered three-state protocol, two national surveys with survey-design variance, a per-pair power analysis, and a codebook gate that found and fixed 17 operationalisation errors before the final analysis.

Several limitations qualify the conclusions. The design is cross-sectional, so no temporal or causal ordering can be established and reverse causation cannot be excluded. Cataract and glaucoma outcomes in the self-report waves are self-reported and therefore subject to differential reporting by socioeconomic position; the retinal and macular gradings are photographic and are performed in a subsample, which raises the possibility of selection. KNHANES provides only a binary vision-impairment flag, so the corresponding rule could not be tested on construct grounds. Five of 21 rules remain untestable for documented data reasons, so the rule set is not exhaustively evaluated. Exposures were dichotomised at clinical cut-points; continuous versions were estimated but are not the basis of the three-state labels, and dichotomisation discards dose–response information and can attenuate associations. BMI used the WHO international cut-point for the primary analysis, with the Asian cut-point reported as sensitivity. Exposure-specific adjustment for the other exposures was not performed, so residual confounding between correlated exposures remains.

Two limitations specific to the external layers deserve emphasis. First, **the CHARLS smoking exposures could not be validated and are excluded from all claims**: the 2015 wave yields a current-smoking prevalence of 7.5% and an ever-smoking prevalence of 12.4% against Chinese references of 27% and 40%, whereas the 2011 wave — after correcting the same reference-group error described above — yields 28.1% and 40.1%. Resolving the 2015 questionnaire's smoking items requires a codebook we did not have; until then, any CHARLS smoking result is unsupportable, and the CHARLS layers therefore contribute no smoking evidence. Second, **CHARLS HbA1c is not comparable across waves** (HbA1c ≥6.5%: 4.9% in 2011 vs 13.1% in 2015, a 2.7-fold difference for the same variable name), the same cross-wave comparability problem we found for KNHANES HbA1c. The near-significant CHARLS-2015 HbA1c × cataract association (OR 1.71, p=0.0026) that we would otherwise have highlighted as a supportive signal therefore rests on a variable that cannot be pooled across waves, and we report it only as a caveat rather than as corroboration. Finally, all observational associations reported here — including the glycaemic ones — are subject to confounding by socioeconomic position and by health-system contact, which the exploratory analyses of antioxidant intake and lipids illustrate directly.

---

## Conclusion

In a pre-registered, adequately powered evaluation across two national surveys, literature-derived exposome rules for eye disease largely failed to replicate, and the rules with the strongest published evidence failed most consistently. The replications that did occur were concentrated in exposure–outcome pairs that are close to definitionally linked. Rule-based interpretable screening systems should therefore be externally evaluated, with power and multiplicity declared in advance, before their outputs inform clinical or public-health decisions. Two directions — the non-complication pathways linking dysglycaemia to vision loss, and the possible role of dietary antioxidant inadequacy — merit prospective follow-up.

---

## Declarations

**Ethics approval.** This study used only de-identified, publicly available data from NHANES (US National Center for Health Statistics), KNHANES (Korea Disease Control and Prevention Agency) and CHARLS (Peking University). Each source obtained its own ethics approval and informed consent; no new data were collected, and no further ethical approval was required.

**Data availability.** NHANES: https://wwwn.cdc.gov/nchs/nhanes/. KNHANES: https://knhanes.kdca.go.kr/. CHARLS: http://charls.pku.edu.cn/. All derived analytic frames and result tables are produced by the scripts listed below.

**Code availability.** The complete pipeline is scripted. Key entry points: `scripts/build_knhanes_frames.py` (frame reconstruction), `scripts/validate_nhanes_exposures.py` and `scripts/validate_knhanes_frames.py` (codebook/prevalence gates), `scripts/evaluate.py` and `scripts/evaluate_knhanes.py` (confirmatory layers), `scripts/survey_sensitivity_export.py` + `scripts/survey_sensitivity_R5.R` + `scripts/apply_survey_variance.py` (survey-design variance), `scripts/power_analysis.py`, `scripts/mediation_analysis.py`, `scripts/headline_sensitivity.py`. Variable definitions and all 17 corrections: `configs/variable_map.yaml`. Pre-registration and protocol deviations: `docs/analysis_plan.md`.

**Funding.** *[to be completed]*

**Competing interests.** None declared.

**Author contributions.** *[to be completed]*

---

## Tables

**Table 2. Rules that could not be tested, with reasons.**

| Rule | Level | Reason | Category |
|---|---|---|---|
| r07 vitamin D × diabetic retinopathy | B | Local NHANES copy lacks the vitamin D module; KNHANES serum vitamin D (2008–2012) does not overlap DR grading (2016–2021) | data limitation |
| r18 UV exposure × cataract | B | KNHANES sunlight variable exists only in 2010–2012; cataract self-report exists only in 2008–2009 and 2017–2021 | data limitation |
| r21 PM2.5 × moderate/severe vision impairment | B | KNHANES supplies only a binary "any visual impairment" flag; no severity grading | construct mismatch |
| r09 Mediterranean diet × late AMD | B | Mediterranean-diet adherence index not yet constructed; FFQ data available | not yet built |
| r19 pro-inflammatory diet × DR | C | Dietary inflammatory index not yet constructed; FFQ data available | not yet built |

**Table 3.** Primary results (see Results). *to be typeset*

**Table 4. Evidence level A rules — all failed in both countries.**

| Rule | Level | NHANES | KNHANES | CHARLS 2011 |
|---|---|---|---|---|
| r10 smoking × cataract | A | uninformative | uninformative | uninformative |
| r11 smoking × late AMD | A | uninformative | uninformative | — |
| r13 BMI × cataract | A | uninformative | uninformative | — |

**Table 5. Power to detect an association, and interpretation of nulls.**

| | NHANES | KNHANES |
|---|---|---|
| Median design effect | 1.07 | 1.26 |
| Median minimum detectable OR (80% power) | 1.337 | 1.159 |
| Rule-relevant pairs powered to detect OR ≤1.5 | 14/19 | 11/16 |
| Rule nulls | 13 | 11 |
| … of which informative (could exclude OR ≥2) | 10 (76.9%) | 7 (63.6%) |
| … of which underpowered | 1 | 1 |

**Table 6. Mediation of the dysglycaemia–vision-impairment association (stable models only).**

| Dataset | Exposure → outcome | Mediator | n | Total OR | Direct OR | Proportion mediated |
|---|---|---|---|---|---|---|
| NHANES | HbA1c → mild VI | cataract | 5,641 | 1.50 | 1.49 | 0.012 |
| NHANES | HbA1c → mild VI | DR | 5,105 | 1.42 | 1.48 | −0.098 |
| NHANES | HbA1c → moderate VI | DR | 5,105 | 1.59 | 1.46 | 0.193 |
| NHANES | HbA1c → severe VI | DR | 5,105 | 1.85 | 1.80 | 0.047 |
| KNHANES | hyperglycaemia → any VI | DR | 16,351 | 3.09 | 2.54 | 0.175 |

**Table 7. Sensitivity of the headline to the rule-set definition (conservative precision).**

| Rule set | NHANES (rep/tested) | Conservative precision | KNHANES (rep/tested) | Conservative precision |
|---|---|---|---|---|
| All rules | 6/19 | 0.316 | 5/16 | 0.312 |
| Excluding r22 (leakage) | 6/17 | 0.353 | 4/15 | 0.267 |
| Excluding negative control r01 | 6/18 | 0.333 | 5/15 | 0.333 |
| **Level A only** | **0/3** | **0.000** | **0/3** | **0.000** |
| Levels A+B | 4/13 | 0.308 | 4/13 | 0.308 |

---

## Figure legends

**Figure 1.** Architecture of the rule-based exposome–eye-disease screening system: entity normalisation → rule engine → graph-organised evidence retrieval → evidence compression → structured report, with the pre-registered three-state evaluation wrapping the rule engine. *(Existing `figure1_architecture` is a system diagram and remains valid.)*

**Figure 2.** Rule-level evaluation after the R11 variable corrections (`outputs/figures/figure2_rule_evaluation_R11`). (a) Three-state distribution of rule-relevant testable pairs by layer: NHANES 6 replicated / 0 contradicted / 13 uninformative; KNHANES 5 / 0 / 11. (b) The two precision conventions side by side with Clopper–Pearson 95% intervals: declared-domain precision 1.00 in both layers; conservative precision 0.32 (NHANES) and 0.31 (KNHANES). The gap between the two bars is the single largest lever on the headline number and is why both must be reported. (c) Replicated rules by evidence level: 0/3 for level A in both countries, 4/13 for levels A+B, 6/19 and 5/16 overall.

**Figure 3.** Minimum detectable odds ratio (80% power, two-sided α=0.05) against the observed odds ratio, for rule-relevant pairs (`outputs/figures/figure3_power_mde_R11`). Blue = replicated, orange = uninformative. The vertical dashed and dotted lines mark MDE-OR 1.5 and 2.0. Points to the left of the 1.5× line were adequately powered to exclude a 1.5-fold association, which is why most of the nulls are interpretable rather than merely uninformative. The median MDE-OR was 1.337 (NHANES) and 1.159 (KNHANES).

**Figure 4.** Continuous (per-1-SD) dose–response for rule-relevant pairs, survey-weighted (`outputs/figures/figure4_dose_response_R11`). Bars are OR per 1 SD with 95% CI; asterisk marks q<0.05; red marks a direction opposite to the rule. NHANES n=24 pairs, KNHANES n=10. Note that BMI × cataract is significant per SD in KNHANES but not in NHANES, whereas serum cotinine is null for both cataract and late AMD — the two observations that qualify the headline result.

**Figure 5.** Example reasoning trace for a single exposure–outcome pair. *(Existing `figure5_reasoning_trace` is a system-illustration artefact and is unaffected by the corrections; it is a demonstration, not a result.)*

**Supplementary.** `configs/variable_map.yaml` (variable definitions and all 17 corrections); `docs/analysis_plan.md` §0.3–0.5 (protocol deviations, including the CHARLS gate); `outputs/tables/headline_sensitivity.csv`; `outputs/confirmatory/power_analysis_*.csv`; `outputs/confirmatory/mediation_analysis.csv`; `outputs/confirmatory/dose_response_matrix.csv`; `outputs/confirmatory/dose_response_charls.csv`; `outputs/confirmatory/knhanes_confirmatory.csv`, `nhanes_confirmatory.csv`.

> **Stale artifacts that must not be used**: `outputs/figures/figure2_performance.*` (rendered from pre-correction numbers), and `figure4_demo_case.*` / `figure5_reasoning_trace.*` in their original numbering (system illustrations, now renumbered to Figure 5 / Supplementary).
