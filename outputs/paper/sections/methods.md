# Methods

## Study design and reporting

This was a retrospective, multi-cohort evaluation of a fixed rule-based
decision-support agent for ocular risk in older adults. Cohort analyses follow STROBE [C003]; the TRIPOD+AI [C038] and DECIDE-AI [C039] statements govern estimated prediction models and prospective deployment and were assessed as not applicable to fixed rules. No participant
was contacted and all analyses used de-identified public data.

The development, internal and external-survey tiers were fixed before the internal confirmatory analyses, and the eight-cohort and literature-index layers were pre-registered on 2026-10-15 before any model in those layers was fitted. The four tiers are defined by
independence from the development material: a 134-pair literature-only
development set used only to construct the rule base; internal validation in
NHANES, where the pair-level gold and development-era baselines were built
(independence axis: data source); external validation in KNHANES [C014] and
CHARLS [C013], which differ by country, sampling and examination design (axis:
site); and eight population-based ageing cohorts on three continents (axis:
population). A fifth, literature-index layer assessed rule direction against
PubMed, Web of Science, Europe PMC and CNKI; it is independent of the cohort
databases and of any single index, though not of the source literature.

The agent's five validation targets were system classification, a working
interface and evidence traceability, cross-cohort transportability, rule
direction under a pre-registered three-state standard, and independent
literature concordance. A pre-registered blinded expert panel was planned as a sixth target and was not conducted (Limitations). The eight-cohort layer was pre-registered before any cohort-layer model was fitted, including its testable rule set, per-cohort BMI cut-point,
covariate set and transportability criterion (analysis plan section 19).

## Data sources and validation datasets

### Development set

The 134-pair development set was assembled from the published literature and used
only to construct the 21 rules and the evidence base. It contributes no
independent performance estimate; every result reported below is out-of-sample
with respect to it.

### NHANES: internal validation

NHANES contributed 180 pair-level tests across its exposure-outcome combinations; 159 were testable and 21 were underpowered. For rule-level
precision under survey-design variance, 16 rule-relevant pairs were testable.
The independence axis is the data source: the pair-level gold and the
development-era baselines were built in this database, so this layer is internal
by construction, not a test of site transfer.

### KNHANES: external validation

KNHANES [C014] contributed 352 pair-level tests; 301 were testable, 50 were underpowered, and one pair could not be estimated (numerical overflow in the survey model, logged as fit_fail). Fifteen rule-relevant pairs were testable for
precision. The independence axis is site: the survey differs from NHANES in
country, sampling frame and examination design.

### CHARLS: external validation

CHARLS 2011 [C013] contributed 14 exposure-outcome pairs; all 14 were testable,
and 4 rule-relevant pairs were available for precision. The independence axis is
site. Because only four rule-relevant pairs were available, CHARLS is reported as
a direction check and no precision conclusion is drawn from it alone.

### Eight ageing cohorts: external validation

Eight population-based cohorts were analysed from raw provider files: SHARE
[C006], HRS [C007], ELSA [C008], KLoSA [C037], LASI [C009], MHAS [C010], CLHLS and
CRELES; CLHLS and CRELES are cited to their data deposits [C031-C033]. The layer
contains 598,386 unique person-wave records from 285,878 participants. SHARE distributes five imputation replicates as stacked rows; replicate 1 was used for descriptive and power calculations and the five were combined by Rubin's rules for model estimates. MHAS contributes no confirmatory rule × cohort cell because its
measured exposures and ocular outcomes do not co-occur with sufficient
non-missing data; Supplementary Table S6 records its cells as infeasible rather than omitting the
cohort. Third-party harmonised releases (Gateway, easySHARE, RAND HRS) were excluded by design, because another team's operationalisation would make the transportability question circular; provider-official derived modules (SHARE's gv_* variables and imputed BMI, MHAS constructed files) were used as documented in the analysis plan. The independence axis is population: the cohorts are separate surveys with no cross-cohort linkage, and none contributed to rule construction. Every variable was operationalised from the cohort's own codebook under blocking availability, gate and plausibility checks; the full quality-control log is Supplementary Note S1.

### Literature-index layer

The literature layer queried PubMed, Web of Science (100 papers, 2 rules), Europe
PMC (521 papers across 21 queries, 17 informative) and CNKI (7 rules, 5 informative). It is
independent of the four cohort databases and of any single index, but it cannot
remove the shared source literature from which the rules were derived.

## Rule engine

The system encodes 21 deterministic rules linking an exposome exposure
(metabolic, nutritional, lifestyle or environmental) to an ocular outcome, each
with a declared direction from the published literature (Table 2). Every rule
carries an evidence level (A, B or C); r01 (uric acid and cataract) is a negative
control because the underlying literature is contradictory. Rule-relevant pairs are the (exposure flag, outcome item) pairs a rule asserts something about; all other pairs are exploratory. Every flag has a codebook-derived operationalisation (for example intraocular pressure > 21 mmHg, cup-to-disc ratio ≥ 0.7), recorded in the machine-readable rules.yaml and variable_map.yaml shipped with the code. The rule engine is deterministic: given the same
flags it returns the same matched rules, and it can return no rule rather than
invent one.

## LightRAG knowledge graph

The evidence layer combines a LightRAG index [C034] over 1,060 evidence chunks with an evidence store. Retrieval uses hybrid entity-and-relation search; the arbiter
receives the top five evidence chunks within a 6,000-character context.
Embeddings use doubao-embedding-vision-251215 at 2,048 dimensions. The retrieved subgraph is returned with the report, tracing each rule through its intermediate entities to the source chunk.

## LLM arbiter

The arbiter was a local Qwen3.8-27B model served by llama-server in the primary
generation and GLM-5.3-flash in the fairness generation, with temperature 0. It was bounded to the rule signals and retrieved evidence, could not add rules or override the rule layer, and the agent abstained when no rule fired and no evidence was retrieved. Provider-level nondeterminism was probed at temperature 0: 24 of 24 repeats were stable on the logged DeepSeek probe, and an earlier 1-in-12 flip was provider-side and predated the local Qwen arbiter; the deterministic rule layer is therefore the reproducible component.

## Validation phases and baselines

The validation targets were evaluated across the four tiers and the literature layer, each where the data supported it. System classification compared the full system with three baselines:
retrieval-only LightRAG, a plain language model, and naive retrieval. Each
baseline was run under five seeds with the language-model component held fixed,
so that differences reflect architecture rather than model choice. Paired comparisons used exact accuracy McNemar tests, computed per seed. Two baseline generations are reported side
by side and never pooled: an 80-pair generation with local Qwen3.8-27B baselines
and a 159-pair generation with GLM-5.3-flash baselines. The full system's performance was also evaluated on the independent KNHANES 301-pair matrix under the same three-state gold.

## Statistical analysis

A rule-relevant pair was replicated when its Benjamini-Hochberg-Yekutieli q < 0.05
and its estimate lay in the rule's declared direction, contradicted when q < 0.05
and it lay in the opposite direction, and uninformative otherwise [C004]. Two
precision denominators are reported and never interchanged: declared-domain
precision omits uninformative pairs; conservative precision counts every tested
rule-relevant pair and treats an uninformative result as a failure to replicate.
Exact binomial intervals use Clopper-Pearson [C005]. The pre-registered precision pass lines were 0.70 (internal) and 0.80 (external); the point estimates meet them, but the Clopper-Pearson lower bounds reported below do not exclude values below the line. Random-effects pooling with prediction intervals, E-values, leave-one-cohort-out analysis, meta-regression, cohort-level power and the measurement-modality audit are post hoc. A secondary post hoc binary collapse (gold positive = replicated; predicted positive = flag) is also reported with sensitivity, specificity, PPV and Cohen's κ per generation (Supplementary Table S7); four-level exact accuracy is not computable (no gold risk tier exists; the grade derives from rule severity), and the arbiter context is bounded at 6,000 characters.

Each rule-relevant pair was estimated by within-cohort logistic regression with
age and sex as covariates, wave fixed effects where more than one wave
contributed, and variance clustered by participant. SHARE's five imputations were
fitted separately and combined by Rubin's rules [C015]. Multiplicity was
controlled over two pre-registered families (confirmatory rule-relevant pairs and
exploratory all tested pairs). Power was computed per pair: the minimum
detectable odds ratio at 80% power was derived from observed marginal counts, and
the design effect from the survey-to-model confidence-interval width ratio rather
than a conventional value. The age positive control (sex was included as a covariate, not as a control) was specified as a falsification test and pooled with the same random-effects estimator used for the rules. A synthetic effect-injection regression (post hoc) injected a known OR of 2 into the cohort frames: detection was 100% with zero false positives. Construct validation used NHANES 2005–2008 (n = 14,440), which measured the
same participants by self-report and by objective near-vision testing, with the
same age + sex + wave model. E-values follow VanderWeele and Ding [C035], with each odds ratio converted to a risk ratio using the unexposed risk before use; corrected
values are reported throughout.

For the eight-cohort layer, between-cohort heterogeneity was summarised by REML τ², Cochran's Q, I² and 95% prediction intervals [C036]. The pre-registered
transportability criterion required replication with q < 0.05 in at least two
cohorts. A heterogeneity-aware criterion (prediction interval excluding the null
and I² below 75%) and a regional subgroup comparison were added after the primary
results were known and are reported as post hoc.

## Construct substitutions and protocol deviations

The rule base names specific constructs; the cohort layer tests whichever
construct the data can support. Five AMD rules (r05, r06, r09, r11, r17) were
tested against any AMD because no cohort separates late from early AMD. r02–r04 were specified against self-reported physician-diagnosed diabetes because no cohort has usable fasting glucose or HbA1c; self-reported diabetes prevalence across the four cohorts testing r02 ranges from 1.36% (CLHLS) to 19.14% (CRELES), so the proxy is not on one scale across cohorts.

Survey design variance was specified but not implemented: the cohort frames
contain no weight, strata or PSU variable (SHARE's country field is empty in all
1,693,515 rows), so every confidence interval, q-value and three-state label rests
on unweighted cluster-robust variance. The rule set was modified after the first
confirmatory run: the 20-rule v1.1 set became the 21-rule v1.2 set (exposure
cross-coverage of r02/r03/r04 altered; r22 added) and the confirmatory analysis was
re-run. The pre-registration records this as test-set fitting; the resulting recall of
1.000 is constructed, not earned. No pre-run version-control snapshot exists; the
timeline is documented in Supplementary Methods.

Analyses used Python 3.10 (pandas, statsmodels, SciPy) and R 4.6.1 (survey).

Supplementary tables and figures are provided as Multimedia Appendix 1.

## Ethics

This is a secondary analysis of de-identified public data with no participant contact; the full statement is in the Declarations.
