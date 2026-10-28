# An explainable rule-knowledge-graph-LLM agent for exposome-eye risk stratification: strong benchmarks, operable reports, limited rule transportability

**Running title:** Transportability of exposome rules for eye disease

---

# Abstract

**Background.** Multi-layer agents that combine deterministic rules, knowledge-graph
retrieval and a language model are inspectable, but whether they outperform
general models, and whether their rules hold elsewhere, are rarely tested together.

**Methods.** Huiyan combines 21 rules, a LightRAG knowledge graph of 1,060 evidence
chunks and an LLM arbiter that returns a source-linked trace. We evaluated
system-level classification of the deployable agent against three baselines
(internal NHANES, which also informed rule development; external KNHANES),
rule-level direction under a pre-registered three-state standard (CHARLS; eight
ageing cohorts, 285,878 participants), and concordance across four literature indexes.

**Results.** System track: internally the agent reached F1 0.571 (80 pairs;
LightRAG 0.392, pure LLM 0.335, naive RAG 0.080) and 0.522 (159 pairs; 0.186,
0.178, 0.069). That matrix is in-sample: the rule set was revised after the first
confirmatory run, so recall of 1.000 is a property of that revision (the
pre-revision set scored 0.111). Externally (KNHANES, 301 pairs) the same agent
scored 0.312 against 0.145, 0.135 and 0.094, but below its deterministic rule
layer (0.360): the gates raised precision (0.281 to 0.357) and halved recall
(0.500 to 0.278). Under a binary collapse, sensitivity was 1.00 internally and
0.278 externally, with external specificity 0.968 and kappa 0.275. Rule track:
only 6 of 21 rules were testable in the cohorts; of 18 rule x cohort pairs,
8 replicated, 8 were uninformative and 2 contradicted; two met the pre-registered
criterion but both intervals spanned unity. Literature concordance was 0.889
(PubMed), 0.916 (Web of Science), 0.922 (Europe PMC) and 0.800 (CNKI), with
16/17 cross-index agreement.

**Conclusions.** The agent outperformed LLM and RAG baselines on two national
surveys and returned a source-linked report through a working interface, yet on
independent data it did not outperform its own deterministic rule layer. Its rules
were largely untestable elsewhere (15 of 21), and none was robustly transportable
where testable; the constraint was measurement, not sample size. Agent validation
should report system-level and rule-level results separately, state whether the
benchmark informed development, and state which exposures were measured.

---

# Introduction

Visual loss in later life is predominantly chronic rather than acute. Global
estimates of vision impairment remain methodologically contested [1], and the
leading contributors in ageing populations are cataract, glaucoma, age-related
macular degeneration and diabetic retinopathy [2-4]. Each has been the subject of prevalence projection. Glaucoma, late AMD and diabetic retinopathy can cause irreversible loss once advanced, whereas cataract is surgically treatable but access-dependent; the potential value of exposome risk stratification lies in identifying people whose modifiable exposures place them at risk before vision is lost.

That framing, that risk is carried by a set of modifiable exposures rather than
by a single factor, is the exposome concept [5]. In ophthalmology the relevant
exposome spans metabolic state, nutrition, lifestyle and environment:
hyperglycaemia, smoking, alcohol, adiposity and particulate or ultraviolet
exposure have each been linked to one or more major eye diseases, with smoking
and cataract among the better documented associations [6]. The literature is
nevertheless uneven. Associations are reported for different outcomes, at
different exposure thresholds, in populations with different age structures and
different instruments, and a rule distilled from one body of evidence is not
automatically valid elsewhere.

Clinical decision support is a natural vehicle for turning such rules into
action, and rule-based systems have the advantage of being inspectable: every
conclusion can be traced to a named rule and a cited source. The difficulty is
that the evidence base for the rules is itself heterogeneous. In prediction
modelling the general expectation is that performance falls on external data and
should be reported rather than assumed, but transportability is usually evaluated
as a single aggregate drop in performance. That tells us that a model degraded;
it does not tell us which of its components failed. For a rule-based agent the
component is the rule, and an aggregate F1 cannot distinguish an agent that is
right for the right reason from one that is right despite rules that no longer
hold. Literature-based validation has a related problem: when the validation
search reuses the literature from which the rules were built, concordance is
partly circular.

We therefore built Huiyan, an explainable agent that combines a deterministic
rule engine, a LightRAG knowledge graph over the evidence base and a
language-model arbiter that grades risk and returns a source-linked trace
(Figure 1). The agent is deliberately rule-first. The language model cannot add
rules or invent evidence; it can only grade the signals that the rule engine and
the retrieval layer surface, and it abstains when the evidence is absent. This
design keeps every output inspectable, but it also means that the agent inherits
the validity of its 21 literature-derived rules. We evaluated five targets:
system classification against three baselines, a working interface and
rule/source traceability, cross-cohort transportability, rule direction under a
pre-registered three-state standard, and independent concordance across four
literature indexes. Validation used four independence-defined tiers: a 134-pair
literature-only development set, internal validation in NHANES, external
validation in KNHANES and CHARLS, and eight population-based ageing cohorts on
three continents; a fifth layer tested rule direction against PubMed, Web of
Science, Europe PMC and CNKI.

This design yields three contributions: a system-level account of performance against three baselines under five seeds and two backend generations; a rule-level transportability classification for every testable rule, reported under both precision denominators because the gap between them would otherwise misstate behaviour; and an explicit statement of what the evidence base cannot support, since 15 of the 21 rules were untestable for concrete data reasons. The paper proceeds from architecture and validation design, through system and rule-level results, to the measurement constraint that explains why a strong agent can still carry rules that do not travel.

---

# Methods

## Study design and reporting

This was a retrospective, multi-cohort evaluation of a fixed rule-based
decision-support agent for ocular risk in older adults. Cohort analyses follow STROBE [7]; the TRIPOD+AI [8] and DECIDE-AI [9] statements govern estimated prediction models and prospective deployment and were assessed as not applicable to fixed rules. No participant
was contacted and all analyses used de-identified public data.

The development, internal and external-survey tiers were fixed before the internal confirmatory analyses, and the eight-cohort and literature-index layers were pre-registered on 2026-10-15 before any model in those layers was fitted. The four tiers are defined by
independence from the development material: a 134-pair literature-only
development set used only to construct the rule base; internal validation in
NHANES, where the pair-level gold and development-era baselines were built
(independence axis: data source); external validation in KNHANES [10] and
CHARLS [11], which differ by country, sampling and examination design (axis:
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

KNHANES [10] contributed 352 pair-level tests; 301 were testable, 50 were underpowered, and one pair could not be estimated (numerical overflow in the survey model, logged as fit_fail). Fifteen rule-relevant pairs were testable for
precision. The independence axis is site: the survey differs from NHANES in
country, sampling frame and examination design.

### CHARLS: external validation

CHARLS 2011 [11] contributed 14 exposure-outcome pairs; all 14 were testable,
and 4 rule-relevant pairs were available for precision. The independence axis is
site. Because only four rule-relevant pairs were available, CHARLS is reported as
a direction check and no precision conclusion is drawn from it alone.

### Eight ageing cohorts: external validation

Eight population-based cohorts were analysed from raw provider files: SHARE
[12], HRS [13], ELSA [14], KLoSA [15], LASI [16], MHAS [17], CLHLS and
CRELES; CLHLS and CRELES are cited to their data deposits [18-20]. The layer
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

The evidence layer combines a LightRAG index [21] over 1,060 evidence chunks with an evidence store. Retrieval uses hybrid entity-and-relation search; the arbiter
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
and it lay in the opposite direction, and uninformative otherwise [22]. Two
precision denominators are reported and never interchanged: declared-domain
precision omits uninformative pairs; conservative precision counts every tested
rule-relevant pair and treats an uninformative result as a failure to replicate.
Exact binomial intervals use Clopper-Pearson [23]. The pre-registered precision pass lines were 0.70 (internal) and 0.80 (external); the point estimates meet them, but the Clopper-Pearson lower bounds reported below do not exclude values below the line. Random-effects pooling with prediction intervals, E-values, leave-one-cohort-out analysis, meta-regression, cohort-level power and the measurement-modality audit are post hoc. A secondary post hoc binary collapse (gold positive = replicated; predicted positive = flag) is also reported with sensitivity, specificity, PPV and Cohen's κ per generation (Supplementary Table S7); four-level exact accuracy is not computable (no gold risk tier exists; the grade derives from rule severity), and the arbiter context is bounded at 6,000 characters.

Each rule-relevant pair was estimated by within-cohort logistic regression with
age and sex as covariates, wave fixed effects where more than one wave
contributed, and variance clustered by participant. SHARE's five imputations were
fitted separately and combined by Rubin's rules [24]. Multiplicity was
controlled over two pre-registered families (confirmatory rule-relevant pairs and
exploratory all tested pairs). Power was computed per pair: the minimum
detectable odds ratio at 80% power was derived from observed marginal counts, and
the design effect from the survey-to-model confidence-interval width ratio rather
than a conventional value. The age positive control (sex was included as a covariate, not as a control) was specified as a falsification test and pooled with the same random-effects estimator used for the rules. A synthetic effect-injection regression (post hoc) injected a known OR of 2 into the cohort frames: detection was 100% with zero false positives. Construct validation used NHANES 2005–2008 (n = 14,440), which measured the
same participants by self-report and by objective near-vision testing, with the
same age + sex + wave model. E-values follow VanderWeele and Ding [25], with each odds ratio converted to a risk ratio using the unexposed risk before use; corrected
values are reported throughout.

For the eight-cohort layer, between-cohort heterogeneity was summarised by REML τ², Cochran's Q, I² and 95% prediction intervals [26]. The pre-registered
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
re-run. The pre-registration records this as test-set fitting and states that the
resulting recall of 1.000 is constructed rather than earned; internal-layer
precision is reported for completeness and is not load-bearing for the
cohort-layer conclusions. No pre-run version-control snapshot exists; the
timeline is documented in Supplementary Methods.

Analyses used Python 3.10 (pandas, statsmodels, SciPy) and R 4.6.1 (survey).

Supplementary tables and figures are provided as Multimedia Appendix 1.

## Ethics

This is a secondary analysis of de-identified public data with no participant contact; the full statement is in the Declarations.

---

# Results

All rule-level inference uses the pre-registered three-state standard: a
rule-relevant pair is replicated when its Benjamini-Hochberg-Yekutieli q < 0.05
and its odds ratio points in the declared direction, contradicted when q < 0.05
and it points the other way, and uninformative otherwise. Declared-domain
precision is directional concordance among significant pairs, replicated /
(replicated + contradicted); conservative precision counts every tested pair and
treats an uninformative result as a failure (Figure 3). Because the reference
standard has three states, uninformative pairs are neither positives nor
negatives: sensitivity and specificity are not uniquely defined without a binary
collapse that the three-state standard rejects, and κ is not applicable because
the reference standard is a data-derived estimate, not an annotator label.
System-level F1 treats replicated as the positive class and everything else as
non-positive, so it is a conservative binary summary in which part of the full
system's advantage reflects flagging behaviour rather than accuracy.

## System architecture

Huiyan combines a deterministic rule engine (21 rules), a LightRAG knowledge
graph (1,060 evidence chunks) and an LLM arbiter that returns a report with the
rule, the KG path and the source chunk (Figure 1). The classification benchmark below is produced by the deployable full agent (rule layer, negative-control gate, evidence confirmation, LLM arbiter); the rule layer alone is reported as an ablation.

## Validation overview

The validation returned these core results: the full agent beat the three
LLM/RAG baselines on F1 wherever it was run end to end — 0.571 and 0.522
internally (against 0.080–0.392 and 0.069–0.186) and 0.312 externally (against
0.094–0.145) — but on the external matrix it finished below the bare rule layer
(0.360 for the rule layer versus 0.312 for the agent), and the internal matrix is
in-sample because the rule set was revised after the first confirmatory run; a
worked case resolved every output to a rule, KG path and source chunk (Supplementary Figures S1-S2); in the cohort
layer 6 of 21 rules were testable, with 8 of 18 rule × cohort pairs replicated,
8 uninformative and 2 contradicted; rule direction by tier was NHANES 6/0/10,
KNHANES 5/0/10, CHARLS 0/0/4, eight cohorts 8/2/8 (replicated/contradicted/
uninformative); and index-level precision was 0.889 (PubMed), 0.916 (Web of
Science), 0.922 (Europe PMC) and 0.800 (CNKI). Table 3 collects both levels for every dataset; system-level F1 exists only where the
three baselines were run.

## Internal validation in NHANES

The 134-pair development set contributed no independent estimate (Table 1 and
Supplementary Table S3); every estimate below is out-of-sample with respect to
it. At the pair level, 159 of 180 NHANES pairs were testable and 21 underpowered;
16 rule-relevant pairs were testable under survey-design variance: 6 replicated,
none contradicted, 10 uninformative — declared-domain precision 1.00 (95% CI
0.541–1.00), conservative precision 0.375, rule testability 0.889 (16 of 18;
pre-registered coverage of the full testable matrix 0.131). The point estimate
meets the pre-registered 0.70 precision line, but the Clopper-Pearson lower bound
does not exclude values below it. Sensitivity analyses (Supplementary Table S2)
show replication outside the highest evidence tier: the single level-A pair did
not replicate (0 of 1), levels A and B give 4 of 13 (0.308), and the 16-pair
headline set gives 6 replicated (0.375). Continuous modelling (Figure 4)
reproduces the pattern: cotinine per SD is unrelated to cataract (0.92, q = 0.31)
or late AMD (1.08, q = 0.53) in NHANES, BMI-cataract is significant per SD in
KNHANES (1.077, 1.034–1.122, q = 0.0014) and null in NHANES (1.030, q = 0.71);
direction agreed in 19/24 NHANES and 9/10 KNHANES pairs.

At the system level the internal NHANES matrix is reported as in-sample. The
134-pair development set contributed no independent estimate, and the 80-pair
matrix was itself used in development: the rule set was revised after the first
confirmatory run (r02–r04 exposure coverage altered, r22 added; Methods records
this as test-set fitting), so the recall of 1.000 below is a property of that
revision, not an out-of-sample estimate. Under the earlier gold the pre-revision
v1.1 set scored 0.111 (P 0.091 / R 0.143). With that caveat, the deployable full
agent (G2: rule layer, negative-control gate, evidence confirmation, LLM
arbiter) attained F1 = 0.571 (P 0.400 / R 1.000) on the 80 pairs (Qwen3.8-27B
baselines, R11-corrected gold), ahead of LightRAG 0.392 ± 0.007, pure LLM
0.335 ± 0.010 and naive RAG 0.080 ± 0.110 over five seeds (Figure 2). Accuracy
McNemar was significant against LightRAG (p = 0.0064–0.0117) and pure LLM
(p = 0.0004–0.0013) but not naive RAG (p = 0.42–1.00). The ablation localises
the gain: bare rule layer 0.522, +negative-control gate 0.545, +evidence
confirmation and arbiter 0.571. The full agent extended the ordering to the
159-pair GLM-5.3-flash generation: F1 = 0.522 (P 0.353 / R 1.000) versus rule
layer 0.480 and baselines 0.186, 0.178 and 0.069, with accuracy McNemar
significant against all three (per-seed p < 10⁻⁶). A stronger commercial LLM as
a standalone judge produced more, not fewer, false positives (precision 0.10).
Under a secondary binary collapse (gold positive = replicated; predicted
positive = flag), the full agent reached sensitivity 1.00, specificity 0.878,
PPV 0.400 and κ 0.520, every one of which inherits the constructed recall
(Supplementary Table S7); naive RAG's near-null flagging (sensitivity 0–0.17,
κ ≈ 0) explains its accuracy-McNemar null. The full agent flags 17 of 80
pairs against 4–31 for the baselines, and most predicted-positive pairs are
uninformative rather than contradicted, so precision stays low (0.07–0.35).

## External validation in KNHANES and CHARLS

Of 352 KNHANES pair-level tests, 301 were testable, 50 underpowered and one
non-estimable (numerical overflow in the survey model); all 14 CHARLS 2011 pairs
were testable. Rule-level precision: 15 KNHANES pairs testable — 5 replicated,
none contradicted, 10 uninformative — declared-domain precision 1.00 (0.478–1.00),
conservative precision 0.333, rule testability 0.882; CHARLS had 4 testable
pairs, all uninformative (declared precision undefined, conservative 0.000), so
no conclusion is drawn from it alone.

On KNHANES the full agent was run end to end on all 301 testable pairs, which
makes this the only agent-level external estimate. G2 reached F1 = 0.312
(P 0.357 / R 0.278), above the three baselines (LightRAG 0.145, pure LLM 0.135,
naive RAG 0.094) but below the deterministic rule layer on the same 301 pairs
(0.360; P 0.281 / R 0.500). The evidence gates did what they were designed to do
and no more: they removed 14 false positives at the cost of 4 true positives,
raising precision from 0.281 to 0.357 and halving recall from 0.500 to 0.278.
That is a recall cost, and we report the rule layer as the stronger external
configuration rather than the agent. Accuracy McNemar was significant
against LightRAG (p = 1.8 × 10⁻¹⁵ to 1.2 × 10⁻¹³) and pure LLM (p = 2.1 × 10⁻²⁵
to 1.8 × 10⁻²⁰) and, at four of five seeds, against naive RAG
(p = 5.1 × 10⁻⁴ to 0.087). Under a secondary binary collapse, the agent's
external sensitivity was 0.278 with specificity 0.968, PPV 0.357 and κ 0.275;
the rule layer gave sensitivity 0.500, specificity 0.919, PPV 0.281 and κ 0.307
(Supplementary Table S7). Across metrics the gap is uneven: rule testability
16/18 to 15/17, pre-registered coverage 0.131 to 0.095, declared-domain
precision 1.00 in both, system F1 0.571 (in-sample) to 0.312. The system-level
gap is therefore not zero, and the rule-level transportability test below is the
harsher external test.

## Cross-cohort transportability across eight ageing cohorts

The rules were re-evaluated in eight population-based ageing cohorts on three
continents from raw source files with codebook-verified operationalisation
(598,386 person-wave records from 285,878 participants), under a layer
pre-registered before it was run (analysis plan section 19). Only 6 of 21 rules
were testable; 15 required measurements absent in every cohort (five fundus
imaging, one tonometry or disc grading, three geocoded exposure, three blood
assays, two dietary indices, one lipid panel). Across 18 rule × cohort pairs
(Figure 6): 8 replicated, 8 uninformative, 2 contradicted.

Two rules met the pre-registered criterion. r02 (self-reported diabetes as proxy
for hyperglycaemia) replicated in three of four testable cohorts — LASI 1.88
(1.76–2.00), SHARE 1.75 (1.69–1.82), CLHLS 3.59 (2.62–4.91), CRELES 1.31
(1.07–1.61) short at q = 0.051. r20 (smoking to moderate vision impairment; the
severe tier was not testable) replicated in three of five — HRS 1.61, ELSA 1.49,
SHARE 1.09 — with all five cohorts pointing the same way. Two did not: r10
(smoking to cataract) was risk-increasing in SHARE (1.11, 1.04–1.18, q = 0.0095)
and protective in CLHLS (0.748, 0.64–0.87, q = 0.0012), with ELSA (0.77) and
CRELES (0.70) uninformative below 1 — one replicated risk-up, one contradicted
protective, not a regional pattern (p = 0.45, low power; an earlier fixed-effect
pooled p < 0.0001 was a weighting artefact, Europe being 93% SHARE). r12
(alcohol-cataract) was contradicted in CLHLS (0.809, 0.70–0.93, q = 0.018) and
unreplicated in SHARE (0.963). r13 (BMI-cataract) replicated only in SHARE
(1.24, 1.20–1.29). r11 (declared late AMD) was testable only in ELSA, against
self-reported any AMD; its interval (0.86, 0.55–1.34) excludes associations of
1.70-fold or larger, a powered null. The cohort layer does not corroborate the
internal headline uniformly: no rule-relevant headline pair was contradicted in
NHANES or KNHANES, two were here, one a direction reversal within a single rule.

### The positive control does not pool

Age-cataract is OR 1.99 per decade (1.45–2.75) pooled across five cohorts with
I² = 99.2% — per cohort 2.25 (SHARE), 3.14 (ELSA), 2.16 (LASI), 1.81 (CRELES),
1.15 (CLHLS); for vision impairment, 1.36 (1.11–1.66) with I² = 99.5%. The
control replicated in direction in every cohort; what fails is poolability, not
detection. Rule heterogeneity therefore cannot be attributed to exposures alone
when outcomes are heterogeneous even for age: neither outcomes nor exposures are
comparable enough for a pooled estimate to predict a new population.

### The outcome construct is population-dependent

NHANES 2005–2008 measured four different constructs in the same participants:

| Construct | n | Age OR per decade (95% CI) |
|---|---|---|
| Self-reported cataract operation | 7,074 | 4.27 (3.91–4.67) |
| Same question at the examination | 6,429 | 4.30 (3.90–4.74) |
| Self-rated fair-or-poor eyesight | 7,065 | 1.15 (1.11–1.20) |
| Near-card acuity below the sample median | 4,786 | 1.32 (1.22–1.42) |

The operation gradient (4.27) is 3.2 times the near-card gradient (1.32); these
are different constructs, so this is consistent with the operation item capturing
diagnosis, surgery and access to care rather than disease. CLHLS's 1.22 on a
physician-diagnosis item (1.15 in the pooled positive-control estimate) is
accordingly a property of CLHLS and its item: in the 1998 wave self-reported
cataract is nearly flat below age 95 (17.9%, 16.6%, 17.8%, 18.4% across 75–80 to
90–95) and rises thereafter (22.0%, 26.0% at 95–100, 100+), the logistic-model
OR being 1.22 per decade (p = 1.2 × 10⁻⁷). Two cohorts can use the same nominal outcome and still measure different quantities: the pooled estimate describes no population.

## Independent literature-index concordance

The pre-registered expert panel was not conducted (Limitations). The literature
layer instead validated rule direction against four indexes — independent of the
cohort databases and any single index, though not of the source literature:
PubMed (21 informative rules) 0.889, Web of Science (100 papers, 2 rules) 0.916,
Europe PMC (521 papers, 17 informative) 0.922, CNKI (7 rules, 5 informative)
0.800. Reversals were single-paper except alcohol, reversed in both PubMed and
CNKI. Rule-level direction agreement on shared informative rules was 16/17 for
PubMed-Europe PMC (the r09 divergence) and 15/15 on all other index pairs
(Supplementary Table S8). This rules out a single-database artefact; it cannot
remove the shared source literature.

## Case demonstration and reasoning trace

A worked case from the internal validation set is shown end to end
(Supplementary Figures S1-S2). The input was hba1c_elevated with dr_pdr; rule
r04 matched directly and r03 cross-covered the same flag, one LightRAG retrieval
followed, and the arbiter returned a report naming both rules and each evidence
chunk — seven logged steps (four rule layer, one KG, two arbiter/report), every
output resolved to a rule, a KG path and a source chunk. The flagged pair itself
was underpowered in NHANES and is shown for its trace, not as a confirmatory
result; the case demonstrates operability, not clinical usability or deployment.

## Sensitivity, heterogeneity and power

The multi-cohort rules show I² of 79.5–93.8% (90.5–93.8% for the three with
k ≥ 3), and every computable prediction interval (k ≥ 3) includes the null
(Table 4); r12 and r13 have none at k = 2. The post hoc subgroup tests also flag
magnitude heterogeneity for r02 (p = 0.011) and r20 (p < 0.0001); the
person-level interaction model, leave-one-cohort-out analysis and the
meta-regression on mean age are reported in the Supplementary Text. The pooled
r10 estimate is null (0.84, 0.67–1.05) while dropping SHARE gives I² = 0.0% and
0.747 (0.66–0.84). The two rules the pre-registered criterion called
transportable both fail the stricter reading: r02 and r20 replicate in multiple
cohorts and point consistently, yet neither prediction interval excludes unity.
Under a heterogeneity-aware criterion (prediction interval excluding the null,
I² < 75%) none of the six is transportable — a post hoc reading, reported as
such. The disagreement is itself a result: counting replications does not
penalise between-cohort heterogeneity.

Classifying every rule by the measurement modality its exposure and outcome
require gives 18 feasible rule × cohort cells out of 168 (10.7%) (Supplementary
Table S6): 150 fail because 83 have both sides absent, 41 the exposure and 26 the
outcome. The unlock ranking is fundus imaging +15, blood assays +13, geocoded
exposure +13, dietary indices +6, behavioural items +6, optic-disc grading +5,
self-reported ocular diagnoses +5, anthropometry +3, two single-cell pairings
+1 each; no ageing cohort has fundus imaging, tonometry or disc grading. The
binding constraint on testability is measurement: 598,386 person-waves still
cannot reach 15 of the 21 rules (71%).

Beyond the confirmatory pairs, 68 available exposure × outcome pairs were swept
in an exploratory analysis; three directions are reported in Supplementary
Results S9 and are not confirmed findings.

Median minimum detectable OR at 80% power was 1.337 in NHANES and 1.159 in
KNHANES (Figure 5); 17 of the 30 rule-relevant pairs plotted there were powered
nulls, so most uninformative results are informative nulls rather than failures
of power. In the cohort layer, 6 of 8 uninformative pairs were powered nulls; the
exceptions (CRELES r02, KLoSA r20) are identified. Where the cohort layer failed
to replicate a rule, it usually had the power to do so.

---

# Discussion

## Main finding

Huiyan, benchmarked as a complete deployable agent, ranked first on F1 against
three LLM/RAG baselines in both NHANES backend generations and in the independent
KNHANES survey, and returns source-linked, operable reports. Two qualifications
belong with that statement. The internal NHANES matrix is in-sample: the rule set
was revised after the first confirmatory run, so its recall of 1.000 is a property
of that revision and the honest pre-revision figure is 0.111. And on the
independent matrix the agent scored below its own deterministic rule layer
(0.312 versus 0.360), because the gates removed false positives at the cost of
half the true positives. Its rules also did not transport: only 6 of 21 were
testable in eight ageing cohorts, and of the two that met the pre-registered
criterion, neither interval excluded unity. Together these change how agent
validation should be reported.

## Where the performance comes from, and where it reverses

The gain over LLM baselines is architectural, not scale. On the NHANES matrices
the deployable full agent scored 0.571 (80 pairs) and 0.522 (159 pairs, versus
rule layer 0.480); the ablation localises the gain: rule layer 0.522,
+negative-control gate 0.545, +evidence confirmation and arbiter 0.571. A
stronger commercial model as a standalone judge produced more, not fewer, false
positives, and swapping the arbiter itself for GLM-5.3-flash left every one of the
474 predictions unchanged: the arbiter decides 3 cells, the remaining 471 being
settled by the rule layer, the negative-control gate or the evidence-B+ gate. The
measured gain therefore belongs to the rule and gate layers, not to the language
model. That ordering does not carry over to independent data. On KNHANES the
same gates raised precision from 0.281 to 0.357 while cutting recall from 0.500
to 0.278, leaving the agent below the bare rule layer (0.312 versus 0.360): the
evidence store rarely holds a B-or-better chunk for pairs that a new country's
data replicates, so the confirmation step abstains exactly where the rule layer
was right. Every output still resolves to a rule, a KG path and a source chunk;
that demonstrates operability, not clinical usability or deployment.

## Why the rules do not transport

Fifteen of 21 rules could not be tested in any cohort for lack of measurement;
of the 18 testable rule × cohort pairs, 8 replicated, 8 were uninformative and 2
were contradicted, and the pre-registered count criterion ignored between-cohort
heterogeneity. The binding constraint on testability is measurement: of 168
possible cells, 18 were feasible, and the largest unlock would come from fundus
imaging, blood assays and geocoded exposure. The binding constraint on
transportability is heterogeneity plus ascertainment: the internal headline is
built on correlated pairs (six replicated NHANES pairs are two glycaemic flags
crossed with three overlapping outcomes), the internal-layer F1 is an upper bound
after the v1.2 revision, and in the cohort layer both exposure and outcome were
self-reported, so transported associations may partly reflect shared access to
care rather than biology.

### The direction reversal

r10 (smoking–cataract) was risk-increasing in SHARE (1.11, 1.04–1.18) and
protective in CLHLS (0.748, 0.64–0.87); the other two cohorts are uninformative
below 1, so this is one significant estimate against one, not a three-against-one
split, and it is not regional (p = 0.45, low power). Three mechanisms remain.
Selective survival is plausible at CLHLS's mean age of 92.0 years [27,28],
but the meta-regression slope on mean age does not support it. Unmeasured
confounding is plausible: E-values are 1.87 (1.50) for CLHLS and 1.43 (1.23) for
SHARE. Genuine effect modification across cataract subtypes [6] cannot be
excluded, as no cohort grades opacity. The design cannot distinguish these, and
we do not prefer one. The same caution applies to alcohol, where abstainers are
not a comparable exposure category [29].

### The pooled estimate is the wrong summary

With I² of 79.5–93.8% across the multi-cohort rules [30], the pooled average
estimates a quantity no population in the analysis has; the three computable
prediction intervals all include the null (r02 0.30–12.63, r10 0.30–2.31, r20
0.62–2.46) [31]. Leave-one-out qualifies this: removing SHARE collapses I² to
0.0% and moves r10 to 0.747 (0.66–0.84). Reporting a pooled effect or a
replication count without a heterogeneity statistic is the choice most likely to
make a heterogeneous evidence base look settled.

### The positive control, and what it withdraws

Age-cataract replicated in direction in every cohort but does not pool (I² =
99.2%), so the limitation of pooled exposome estimates is not confined to the
exposures: outcome definitions themselves are not comparable enough. The outcome
check also withdraws an expected explanation — NHANES shows self-reported
cataract tracks age far more steeply (4.27 per decade) than near-card acuity
(1.32), consistent with the item capturing diagnosis and access to care. CLHLS's
flat-below-95 gradient is the signature of that mechanism: in multi-cohort
pooling of self-reported outcomes, comparability is set by the population's
diagnosis rate, not the item wording. The safeguard is to report outcome
prevalence by cohort and prefer examination-based measurement — precisely what
the ophthalmic exposome evidence base most often lacks.

## Comparison with prior art

Rule-based decision support is inspectable, but its external validation is
usually reported as an aggregate performance change, which cannot say which rule
failed. KG and LLM agents are typically evaluated end to end and do not separate
the rule layer from the language model; our comparison does, and the standalone
stronger LLM did not close the gap. The second departure is the unit of
validation: reporting standards such as TRIPOD+AI [8] and DECIDE-AI [9]
organise validation around estimated models, whereas a fixed-rule agent's
components are its rules. We therefore report rule-level transportability
alongside system F1, add a literature-index layer that is independent of the
cohort databases and of any single index, and note that the internal layers'
clean headline reflects fewer, narrower and correlated pairs — adding populations
adds disagreement, and a protocol that cannot represent it reports a clean
result.

## Limitations

Independence is tier-specific and the gap differs by metric: the development set
contributes no independent estimate; internal-to-external change was 0.007 for
rule testability, 0.522 to 0.360 for the rule layer and 0.571 to 0.312 for the
agent, the internal figure being in-sample; the eight cohorts are
population-independent but only 18 of 168 cells were feasible; the literature
layer is index-independent but not source-independent. Estimation relies on
unweighted cluster-robust variance (the pre-registered survey design could not be
implemented) on anti-conservative exact tests over non-independent pairs, and on
an internal-layer F1 that is an upper bound after test-set fitting. Cataract
outcomes were self-reported in every layer, with examination-based NHANES
measures limited to retinal grading and visual acuity; glaucoma was tested only
as pressure or disc-cupping surrogates. Most waves are cross-sectional, so
incidence cannot be separated from prevalent disease and selective survival
cannot be tested directly. Six of eight uninformative cohort pairs were powered
nulls; r11 could exclude only associations of 1.7-fold or larger. Eight rules
were specified on a narrower construct than the data support (five AMD rules
against any AMD, three glycaemic rules against self-reported diabetes); in the
cohort layer only r02 and r11 were testable under those substitutions, and
neither tests the construct its citation supports. r11 and r13 each rest on one
cohort. A working interface demonstrates operability, not clinical benefit; no
patient-level diagnostic accuracy, calibration or usability trial was conducted,
the risk grade is a severity tier rather than a calibrated probability, and the
pre-registered expert panel was not conducted (partially replaced by the
four-index literature validation and a synthetic effect-injection regression).
Finally, the CLHLS severe-impairment flag exceeded its plausibility band (25.7%
at mean age 92); it is a secondary analysis only.

## Future work

The next step is a measured cohort, not a larger one: fundus imaging would unlock
15 additional rule × cohort cells, blood assays 13 and geocoded exposure 13. A
prospective design with examination-based outcomes, measured glycaemia and
geocoded exposures would make incident analysis and the selective-survival and
subtype explanations testable. Before any deployment claim, the agent needs a
blinded expert panel and a clinician usability trial; and the rule base should be
updated only when the measured constructs are available, so that a rule is not
silently replaced by a proxy and then counted as transported.

## Conclusion

We built an explainable rule-KG-LLM agent that ranked first on F1 against LLM and
RAG baselines in two backend generations and in an independent national survey,
and that returns a source-linked report through a working interface. That ranking
holds against general models, not against the agent's own deterministic rule
layer: in the independent survey the gates bought precision with recall and the
agent finished below the rules (0.312 versus 0.360), while the internal benchmark
that produced its best score was in-sample. Its rules, moreover, did not
transport: of 21, six were testable in eight ageing cohorts, and on the
pre-registered criterion two passed while on a heterogeneity-aware post hoc
criterion none did. The lesson is not that the agent is weak; it is that an agent
can beat general LLMs, be operable, and still add nothing over its own rules
outside the data that produced them. Agent validation should therefore report
the rule layer and the full system separately, say whether the benchmark informed
development, and state which exposures were actually measured.

---

# Declarations

## Ethics approval and consent to participate

This study is a secondary analysis of de-identified, publicly available data
from eleven population surveys. No participants were contacted, no intervention
was administered, and no identifiable information was accessed. On that basis,
**no ethics review was required** for this work: the analysis used exclusively
de-identified, publicly available secondary data with no participant contact,
no intervention and no identifiable information, and each source survey had
already been conducted under its own ethics approval by the original
investigators. Each source survey had already
obtained ethics approval and informed consent (or a documented waiver) from its
own governing body under its own protocol, and this analysis used only the
released, de-identified files. Users of these data are bound by the terms of the
individual data-use agreements listed under Data availability below.

## Consent for publication

Not applicable: no individual-level identifiable data are reported.

## Data availability

All data are available from the originating studies; none were generated by this
work. **Every source requires its own registration or application, and the access
route differs by cohort.** Analysts wishing to reproduce this work must obtain
each dataset directly from its provider.

| Source | Provider / access route |
|---|---|
| NHANES | US Centers for Disease Control and Prevention, National Center for Health Statistics, public download |
| KNHANES | Korea Disease Control and Prevention Agency, application required |
| CHARLS | Peking University National School of Development, application required |
| SHARE | SHARE Research Data Center, share-project.org, free registration for scientific use |
| HRS | Health and Retirement Study, University of Michigan, free registration |
| ELSA | UK Data Service, registration required |
| KLoSA | Korea Employment Information Service (KEIS), application required |
| LASI | Longitudinal Ageing Study in India, International Institute for Population Sciences, application required |
| MHAS | Mexican Health and Aging Study, mhasweb.org, free registration |
| CLHLS | Chinese Longitudinal Healthy Longevity Survey, Duke University / ICPSR, application required |
| CRELES | Costa Rican Study on Longevity and Healthy Ageing, ICPSR study 26681, public download |

**Derived data.** The cohort analysis frames, the harmonisation-free
construction of which is the point of the study, are not redistributed here
because their redistribution would breach the source agreements. They are
regenerable from the raw provider files by the scripts listed below.

**Exact access URLs and any dataset version numbers must be confirmed against
the providers' current pages at submission**, access routes change, and this
table was compiled from the data-release documentation held with the project
rather than from a live check of each provider's site.

## Code availability

All analysis code, the machine-readable rule and variable definitions
(`configs/rules.yaml`, `configs/variable_map.yaml`), the Streamlit interface and
the full reproducibility pipeline are publicly available at
https://github.com/wangguoqing932/huiyan-exposome-eye-agent (archived snapshot
with a DOI will be deposited at Zenodo upon acceptance). The entry points are
`scripts/build_cohort_frames.py` (frames) → `scripts/cohort_confirmatory.py`
(primary estimates) → `scripts/cohort_heterogeneity.py` (pooling, I², prediction
intervals, E-values, leave-one-out) → `scripts/cohort_power.py` and
`scripts/evidence_base_audit.py`. **Environment:** Python 3.10.4 with pandas
2.3.3, statsmodels 0.15.0, NumPy 2.2.6 and SciPy 1.15.3. The survey-weighted
sensitivity analysis used R 4.6.1 with the `survey` package.

## Funding

This work received no specific funding.

## Competing interests

The authors declare no competing interests. No commercial relationship exists
with any large-language-model provider; all LLM calls in the validation pipeline
ran against locally hosted or freely accessed endpoints.

## Author contributions (CRediT)

Guoqing Wang: Conceptualization, Methodology, Software, Data curation,
Formal analysis, Validation, Visualization, Writing – original draft.
Xianglong Yi: Conceptualization, Methodology, Supervision, Project
administration, Validation, Writing – review & editing. Both authors read and
approved the final manuscript and take full responsibility for the work. **An AI
system cannot be listed as an author**, cannot hold responsibility for the work,
and cannot consent to publication.

## Use of generative artificial intelligence

Generative AI tools were used in this work and their role is disclosed here for
transparency. They assisted with: drafting and revising analysis code;
implementing the statistical pipeline; generating figure and table artefacts;
and drafting and editing the manuscript text and its translations. The
quantitative results were produced by executing the code against the source
data; the code, the data-provider files and the audit trail are available as
described above, so the reported numbers can be recomputed from the archived outputs; the pre-expansion v1.1 replay figures are reported from a logged run and are not regenerable by the current pipeline.

**All scientific decisions were made and verified by the human authors**, who
take full responsibility for the content. That includes, specifically: the
choice of rules and their operationalisation; the decision to use raw source
files rather than harmonised derivatives; the pre-registered criteria and the
subsequent declaration of which analyses were added after the pre-registration;
the interpretation of the between-cohort heterogeneity; and the decision not to
prefer any single explanation for the reversed association. Every AI-generated
statement about the literature was checked against the retrieved record of the
source (the verified citation pool, with DOI, cross-verification source and
retraction status for each entry), and AI tools were not used to generate
references from memory.

## Reporting guidelines

This study is reported according to **STROBE** for the observational cohort
analyses, with the cross-cohort synthesis reported following standard
meta-analytic practice (random-effects pooling with REML τ², Cochran's Q, I² and
prediction intervals). **TRIPOD+AI and DECIDE-AI are not applicable**: this work
evaluates deterministic rules derived from the literature, not a prediction
model with estimated coefficients, and does not report model calibration,
discrimination or prospective clinical deployment. The system-level comparison
in the internal layers reports classification performance of a rule-based
pipeline, not predictive-model performance, and is reported as such.

---

# References

1. Keel S, Cieza A. Rising to the challenge: estimates of the magnitude and causes of vision impairment and blindness. The Lancet Global Health. 2021;9(2):e100-e101. doi:10.1016/s2214-109x(21)00008-5. <!-- C016 | n=1 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/s2214-109x(21)00008-5 -->
2. Clopper CJ. Global prevalence of age-related macular degeneration. The Lancet Global Health. 2014;2(2):e65-e66. doi:10.1016/s2214-109x(13)70163-3. <!-- C021 | n=2 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/s2214-109x(13)70163-3 -->
3. Song P, Yu J, Chan KY, Τheodoratou E, Rudan I. Prevalence, risk factors and burden of diabetic retinopathy in China: a systematic review and meta-analysis. Journal of Global Health. 2018;8(1):010803. doi:10.7189/jogh.08.010803. <!-- C022 | n=3 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.7189/jogh.08.010803 -->
4. Tham YC, Li X, Wong TY, Quigley HA, Aung T, Cheng CY. Global Prevalence of Glaucoma and Projections of Glaucoma Burden through 2040. Ophthalmology. 2014;121(11):2081-2090. doi:10.1016/j.ophtha.2014.05.013. <!-- C023 | n=4 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/j.ophtha.2014.05.013 -->
5. Benjamini Y. Complementing the Genome with an “Exposome”: The Outstanding Challenge of Environmental Exposure Measurement in Molecular Epidemiology. Cancer Epidemiology Biomarkers & Prevention. 2005;14(8):1847-1850. doi:10.1158/1055-9965.epi-05-0456. <!-- C020 | n=5 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1158/1055-9965.epi-05-0456 -->
6. Ye J, He J, Wang C, Wu H, Shi X, Zhang H, et al. Smoking and Risk of Age-Related Cataract: A Meta-Analysis. Investigative Ophthalmology & Visual Science. 2012;53(7):3885. doi:10.1167/iovs.12-9820. <!-- C018 | n=6 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1167/iovs.12-9820 -->
7. Vandenbroucke JP. Strengthening the Reporting of Observational Studies in Epidemiology (STROBE). Epidemiology. 2007;18(6):805-835. doi:10.1097/ede.0b013e3181577511. <!-- C003 | n=7 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1097/ede.0b013e3181577511 -->
8. Collins GS, Moons K, Gatsonis C, Pencina M. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024. doi:10.1136/bmj-2023-078378. <!-- C038 | n=8 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref | doi:10.1136/bmj-2023-078378 -->
9. Vasey B, Nagendran M, Campbell D, Comissiong D. Reporting guideline for the early stage clinical evaluation of decision support systems driven by artificial intelligence. BMJ. 2022. doi:10.1136/bmj-2022-070904. <!-- C039 | n=9 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref | doi:10.1136/bmj-2022-070904 -->
10. Kweon S. Data Resource Profile: The Korea National Health and Nutrition Examination Survey (KNHANES). International Journal of Epidemiology. 2014;43(1):69-77. doi:10.1093/ije/dyt228. <!-- C014 | n=10 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyt228 -->
11. Zhao Y. Cohort Profile: The China Health and Retirement Longitudinal Study (CHARLS). International Journal of Epidemiology. 2012;43(1):61-68. doi:10.1093/ije/dys203. <!-- C013 | n=11 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dys203 -->
12. Börsch-Supan A. Data Resource Profile: The Survey of Health, Ageing and Retirement in Europe (SHARE). International Journal of Epidemiology. 2013;42(4):992-1001. doi:10.1093/ije/dyt088. <!-- C006 | n=12 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyt088 -->
13. Sonnega AJ, Faul JD, Ofstedal MB, Langa KM, Phillips JW, Weir DR. Cohort Profile: the Health and Retirement Study (HRS). International Journal of Epidemiology. 2014;43(2):576-585. doi:10.1093/ije/dyu067. <!-- C007 | n=13 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyu067 -->
14. Steptoe A. Cohort Profile: The English Longitudinal Study of Ageing. International Journal of Epidemiology. 2012;42(6):1640-1648. doi:10.1093/ije/dys168. <!-- C008 | n=14 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dys168 -->
15. Jang J. Korean Longitudinal Study of Ageing (KLoSA): Overview of Research Design and Contents. Encyclopedia of Geropsychology. 2017. doi:10.1007/978-981-287-082-7_55. <!-- C037 | n=15 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref | doi:10.1007/978-981-287-082-7_55 -->
16. Perianayagam A. Cohort Profile: The Longitudinal Ageing Study in India (LASI). International Journal of Epidemiology. 2022;51(4):e167-e176. doi:10.1093/ije/dyab266. <!-- C009 | n=16 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyab266 -->
17. Wong R. Cohort Profile: The Mexican Health and Aging Study (MHAS). International Journal of Epidemiology. 2015;46(2):e2. doi:10.1093/ije/dyu263. <!-- C010 | n=17 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyu263 -->
18. The Chinese Longitudinal Healthy Longevity Survey (CLHLS)-Longitudinal Data（1998-2011）. Peking University Opendata Dataverse. 2015. doi:10.18170/DVN/MKB1LF. <!-- C031 | n=18 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=datacite | doi:10.18170/DVN/MKB1LF -->
19. The Costa Rican Longevity and Healthy Aging Study (CRELES). Harvard Dataverse. 2025. doi:10.7910/DVN/7AUOAO. <!-- C032 | n=19 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=datacite | doi:10.7910/DVN/7AUOAO -->
20. CRELES: Costa Rican Longevity and Healthy Aging Study, 2005 (Costa Rica Estudio de Longevidad y Envejecimiento Saludable). ICPSR - Interuniversity Consortium for Political and Social Research. 2010. doi:10.3886/icpsr26681.v2. <!-- C033 | n=20 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=datacite | doi:10.3886/icpsr26681.v2 -->
21. Guo Z, Xia L, Yu Y, Ao T, Huang C. LightRAG: Simple and Fast Retrieval-Augmented Generation. arXiv. 2024. doi:10.48550/arXiv.2410.05779. <!-- C034 | n=21 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=arxiv+crossref | doi:10.48550/arXiv.2410.05779 -->
22. Benjamini Y. The control of the false discovery rate in multiple testing under dependency. The Annals of Statistics. 2001;29(4):1165-1188. doi:10.1214/aos/1013699998. <!-- C004 | n=22 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1214/aos/1013699998 -->
23. Clopper CJ. THE USE OF CONFIDENCE OR FIDUCIAL LIMITS ILLUSTRATED IN THE CASE OF THE BINOMIAL. Biometrika. 1934;26(4):404. doi:10.1093/biomet/26.4.404. <!-- C005 | n=23 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/biomet/26.4.404 -->
24. Rubin DB. Multiple Imputation for Nonresponse in Surveys. Wiley Series in Probability and Statistics. 1987. doi:10.1002/9780470316696. <!-- C015 | n=24 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref+openalex | doi:10.1002/9780470316696 -->
25. VanderWeele TJ, Ding P. Sensitivity Analysis in Observational Research: Introducing the E-Value. Annals of Internal Medicine. 2017. doi:10.7326/M16-2607. <!-- C035 | n=25 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref | doi:10.7326/M16-2607 -->
26. Higgins JPT, Thompson S, Spiegelhalter D. A Re-Evaluation of Random-Effects Meta-Analysis. Journal of the Royal Statistical Society Series A. 2009. doi:10.1111/j.1467-985x.2008.00552.x. <!-- C036 | n=26 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref | doi:10.1111/j.1467-985x.2008.00552.x -->
27. Pressley JC, Patrick CH. Frailty Bias in Comorbidity Risk Adjustments of Community-Dwelling Elderly Populations. Journal of Clinical Epidemiology. 1999;52(8):753-760. doi:10.1016/s0895-4356(99)00056-6. <!-- C028 | n=27 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/s0895-4356(99)00056-6 -->
28. Burgess S, Zhou A. Genetic predictors of traits in elderly subjects: risk of survival bias and reverse causation. European Heart Journal. 2024;45(24):2155-2157. doi:10.1093/eurheartj/ehae295. <!-- C029 | n=28 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/eurheartj/ehae295 -->
29. Rosansky JA, Rosenberg H. A systematic review of reasons for abstinence from alcohol reported by lifelong abstainers, current abstainers and former problem-drinkers. Drug and Alcohol Review. 2020;39(7):960-974. doi:10.1111/dar.13119. <!-- C030 | n=29 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1111/dar.13119 -->
30. Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. Statistics in Medicine. 2002;21(11):1539-1558. doi:10.1002/sim.1186. <!-- C026 | n=30 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1002/sim.1186 -->
31. Spineli LM, Pandis N. Prediction interval in random-effects meta-analysis. American Journal of Orthodontics and Dentofacial Orthopedics. 2020;157(4):586-588. doi:10.1016/j.ajodo.2019.12.011. <!-- C027 | n=31 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/j.ajodo.2019.12.011 -->

---


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

---

# Table 1

Participants are counted once per cohort. Person-waves count each person once per wave; SHARE's five imputation replicates are combined to a single record per person-wave, so the person-wave column is the analysed unit and not the raw row count.

| Cohort | Participants | Person-waves | Waves | BMI cut-point (kg/m²) | Why the cohort is in the layer |
|---|---|---|---|---|---|
| SHARE | 137,183 | 338,703 | 5 | 30 | Largest contributor; supplies r02, r10, r12, r13, r20 |
| HRS | 27,261 | 42,946 | 2 | 30 | Supplies r02, r10, r20 |
| ELSA | 9,771 | 9,771 | 1 | 30 | Only source of an AMD item; supplies r10, r11, r20 |
| KLoSA | 11,137 | 40,406 | 5 | 25 | Supplies r10, r20 |
| LASI | 73,408 | 73,408 | 1 | 25 | Supplies r02 only; r13 untestable (no BMI) |
| MHAS | 15,198 | 15,217 | 5 | 30 | Contributes no testable pair (exposures and outcomes do not co-occur) |
| CLHLS | 9,093 | 72,744 | 8 | 25 | Supplies r02, r10, r12, r20 |
| CRELES | 2,827 | 5,191 | 2 | 30 | Supplies r02, r10, r13 |

* **Total: 285,878 participants and 598,386 person-waves across 8 cohorts.**
* The BMI cut-point is 25 kg/m² for the Asian cohorts and 30 kg/m² otherwise, fixed by the prevalence gate before the confirmatory analysis and reported per cohort because it changes what the adiposity rule tests.
* MHAS is retained in the table even though it contributes no testable pair. Excluding a cohort that was analysed, because it turned out to be uninformative, would hide the reason the transportability figure shows fewer cohorts than the layer contains.

---

# Table 2

| rule_id | severity | risk_type | evidence_level | direction | a_flags | b_flags | negative_control | note |
|---|---|---|---|---|---|---|---|---|
| r01_uric_acid_x_cataract | low | inflammation_immune | C | risk_up | uric_acid_elevated | cataract_any | True |  |
| r02_hyperglycemia_x_cataract | medium | glycation_metabolic | B | risk_up | hyperglycemia,hba1c_elevated | cataract_any | False |  |
| r03_hba1c_x_retinopathy_any | medium | glycation_metabolic | B | risk_up | hba1c_elevated,hyperglycemia | retinopathy_any | False |  |
| r04_hba1c_x_dr_pdr | low | vascular_perfusion | C | risk_up | hba1c_elevated,hyperglycemia | dr_pdr,dr_npdr | False |  |
| r05_dyslipidemia_x_amd_late | low | oxidative_stress | C | risk_up | dyslipidemia | amd_late | False |  |
| r06_crp_x_amd_late | medium | inflammation_immune | B | risk_up | crp_elevated | amd_late | False |  |
| r07_vitamind_x_dr_npdr | medium | endocrine_hormonal | B | risk_up | vitamin_d_deficiency | dr_npdr | False |  |
| r08_low_antioxidant_x_cataract | medium | oxidative_stress | B | risk_up | low_antioxidant_intake | cataract_any | False |  |
| r09_mediterranean_diet_x_amd_late | medium | oxidative_stress | B | risk_down | mediterranean_diet | amd_late | False |  |
| r10_smoking_x_cataract | medium | oxidative_stress | B | risk_up | current_smoking | cataract_any | False |  |
| r11_smoking_x_amd_late | high | oxidative_stress | A | risk_up | current_smoking | amd_late | False |  |
| r12_alcohol_x_cataract | medium | oxidative_stress | B | risk_up | alcohol_intake | cataract_any | False |  |
| r13_bmi_x_cataract | medium | glycation_metabolic | B | risk_up | bmi_high | cataract_any | False |  |
| r14_lead_x_cataract | medium | heavy_metal_toxicity | B | risk_up | lead_exposure | cataract_any | False |  |
| r16_pm25_x_glaucoma_iop_cdr | medium | vascular_perfusion | B | risk_up | pm25_exposure | glaucoma_iop_elevated,glaucoma_suspect_cdr | False |  |
| r17_pm25_x_amd_early | medium | inflammation_immune | B | risk_up | pm25_exposure | amd_early | False |  |
| r18_uv_x_cataract | medium | photochemical_uv | B | risk_up | uv_exposure | cataract_any | False |  |
| r22_bmi_x_retinopathy | low | inflammation_immune | C | risk_up | bmi_high | retinopathy_any,dr_npdr | False |  |
| r19_proinflam_diet_x_dr_npdr | low | inflammation_immune | C | risk_up | pro_inflammatory_diet | dr_npdr | False |  |
| r20_smoking_x_vi_mod_severe | medium | oxidative_stress | B | risk_up | current_smoking | vision_impairment_moderate,vision_impairment_severe | False |  |
| r21_pm25_x_vi_mod_severe | medium | vascular_perfusion | B | risk_up | pm25_exposure | vision_impairment_moderate,vision_impairment_severe | False |  |

---

# Table 3

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

---

# Table 4

Random-effects pooling with REML τ², computed in Python/SciPy (no external meta-analysis package), so the estimator is stated explicitly.

**The prediction interval is computed with t on k−2 degrees of freedom, not the normal quantile** (Higgins, Thompson & Spiegelhalter 2009). An earlier version used the normal 1.96 quantile, which gave the narrower interval r02 0.84–4.57; the current t-based intervals on k−2 degrees of freedom give 0.30–12.63. **For the two-cohort rules (r12, r13) no prediction interval exists at all**, t on 0 degrees of freedom is undefined, and none is reported. The interval is the range in which a NEW cohort's true effect would be expected to fall.

| Rule | k | Pooled OR (95% CI) | I² | τ² | Q p | Prediction interval | Subgroup test |
|---|---|---|---|---|---|---|---|
| r02_hyperglycemia_x_cataract | 4 | 1.95 (1.32–2.88) | 90.5% | 0.1487 | <0.0001 | 0.30–12.63 | p 0.0110 |
| r10_smoking_x_cataract | 4 | 0.84 (0.67–1.05) | 91.0% | 0.0421 | <0.0001 | 0.30–2.31 | p 0.4513 |
| r11_smoking_x_amd_late | 1 | single cohort | — | — | — | — | not applicable |
| r12_alcohol_x_cataract | 2 | 0.89 (0.75–1.06) | 79.5% | 0.0120 | 0.0273 | **not computable (k<3)** | same test as Q p (see note) |
| r13_bmi_x_cataract | 2 | 1.13 (0.91–1.41) | 79.5% | 0.0205 | 0.0272 | **not computable (k<3)** | same test as Q p (see note) |
| r20_smoking_x_vi_mod_severe | 5 | 1.24 (1.03–1.48) | 93.8% | 0.0381 | <0.0001 | 0.62–2.46 | p <0.0001 |

**I² must be read alongside τ².** On the log-odds-ratio scale the fitted τ² corresponds to cross-cohort ratio differences of only 1.24× to 2.16×. The high I² is driven by SHARE's very small standard error (its confidence intervals are an order of magnitude narrower than the other cohorts'), so using I² alone as a rejection criterion would partly be a sample-size penalty. Both are therefore reported.

**Note on the subgroup column.** The regional subgroups (Europe / Asia / Americas) were NOT pre-specified; they were constructed after the primary analysis and are reported as post hoc. Pooling within subgroup uses random-effects weights, an earlier version used fixed-effect weights, which at this level of heterogeneity made Europe 93% SHARE by weight and produced a spurious p < 0.0001 for r10; the corrected value is p = 0.45. For the two-cohort rules the subgroup test is not an independent test: with one cohort per group the between-group statistic is the same quantity as the overall Q (r12 both 0.027334; r13 both 0.027220).

**E-values** (minimum confounder strength that could explain the estimate away), computed after converting each odds ratio to a risk ratio, since cataract is not rare in these cohorts (unexposed risk 8.8%–21.1%):

* r10 smoking-cataract in CLHLS: 1.87 (CI bound 1.50)
* r10 smoking-cataract in SHARE: 1.43 (1.23)
* r12 alcohol-cataract in CLHLS: 1.66 (1.31)
* r02 diabetes-cataract in CLHLS: 4.51 (3.58)

**Leave-one-cohort-out analysis (post hoc) qualifies the r10 row.** Removing SHARE reduces I² from 91.0% to 0.0% and moves the pooled estimate to 0.747 (0.66–0.84), so r10's heterogeneity is driven by one cohort rather than distributed across them; the remaining three cohorts agree with each other and their pooled estimate excludes unity.

---
