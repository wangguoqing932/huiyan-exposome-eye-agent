# Even age does not transport: a pooled multi-cohort exposome estimate describes no population, in 285,878 participants and 21 literature-derived rules

---

# Abstract

**Background.** Screening for major eye disease in older adults is increasingly
framed around the exposome and operationalised as rules distilled from the
literature, then validated by pooling cohorts and asking whether an association
replicates. Whether that identifies rules that hold in a new population, or
merely averages over populations in which they disagree, is untested.

**Methods.** We assembled 21 literature-derived exposure–outcome rules and
evaluated them under a pre-registered three-state standard in eight
population-based ageing cohorts on three continents — SHARE, HRS, ELSA, KLoSA,
LASI, MHAS, CLHLS, CRELES — using raw source files only with codebook-verified
operationalisation (285,878 participants; 598,386 person-waves). Heterogeneity
was quantified by random-effects pooling (REML τ², Cochran's Q, I²) with
prediction intervals. **Before testing the rules we ran a positive control (age
and sex), and we validated the outcome construct against NHANES 2005–2008, which
measured the same participants by self-report and by objective near-vision
testing.**

**Results.** The positive control failed. Age–cataract pooled across five cohorts
is OR 1.99 per decade (1.45–2.75) with **I² = 99.2%**, higher than any exposure
rule (79.5–93.8%), ranging from 1.15 (CLHLS) to 3.14 (ELSA). NHANES resolves why:
there, age predicts **self-reported cataract at OR 4.27 per decade** (3.91–4.67)
but objective acuity impairment at only 1.32 (1.22–1.42), so self-report is not
intrinsically weak. CLHLS's gradient stays flat even in its clean 1998 wave
(1.22; prevalence 17.9% at 75–80 and 18.4% at 90–95). **The item measures having
been diagnosed, and diagnosis tracks access to care** — so the same nominal
outcome, ascertained the same nominal way, measures different quantities in
different populations. Against that background, 18 of 168 (rule × cohort) cells
were feasible and six rules testable: of 18 pairs, 8 replicated, 8 were
uninformative and 2 contradicted. The pre-registered criterion marked two rules
transportable, both with prediction intervals spanning unity (0.30–12.63 and
0.62–2.46). For smoking–cataract the pooled estimate was null (0.84, 0.67–1.05)
while three cohorts agreed on a protective association and one did not; a
between-region test was not significant with random-effects pooling (p = 0.45),
so this is one cohort against three, not a regional reversal.

**Conclusions.** A pooled multi-cohort exposome estimate describes no population,
and the limitation is not confined to the exposures: where an outcome is
self-reported, its measured prevalence depends on who has access to diagnosis.
The binding constraint is measurement rather than sample size — which the
analysis demonstrates on itself, since the headline rule passed only after its
exposure was replaced by a self-reported proxy.

---

# Introduction

Visual loss in later life is common, and its dominant causes are chronic rather
than acute. Global estimates of the magnitude and causes of vision impairment
are compiled periodically and remain the subject of methodological debate
[1], and among the leading contributors in ageing populations are cataract,
glaucoma, age-related macular degeneration and diabetic retinopathy. Each of the
retinal and optic-nerve causes has been the subject of global prevalence
projection — glaucoma to 2040 [2], age-related macular degeneration with its
associated disability burden [3] — and diabetic retinopathy in particular is
a leading cause of vision impairment and blindness in working-age adults, with
burden estimates now extending to the largest middle-income populations [4].
Because these conditions are largely irreversible once advanced, the clinical
value of screening lies in identifying people whose modifiable exposures place
them at risk before vision is lost.

That framing — that a person's risk is carried by a set of modifiable
exposures rather than by a single factor — is the exposome concept [5]. In
ophthalmology the relevant exposome spans metabolic state, nutrition, lifestyle
and environment: hyperglycaemia, smoking, alcohol intake, adiposity, and
particulate or ultraviolet exposure have each been linked to one or more of the
major eye diseases, with smoking and cataract among the better documented
associations [6]. The literature is nevertheless uneven. Associations are
reported for different outcomes, at different exposure thresholds, in
populations with different age structures and different instruments for
measuring both exposure and disease, and a rule distilled from one body of
evidence is not automatically valid elsewhere.

Clinical decision support is a natural vehicle for turning such rules into
action, and rule-based systems have the advantage of being inspectable: every
conclusion can be traced to a named rule and a cited source. The problem is
that the evidence base for the rules is itself heterogeneous. A rule may be
derived from a cohort whose exposure instrument differs from the one in which
it will be applied, from a self-reported outcome where the new setting uses
examination-based grading, or from a population whose age distribution makes a
prevalence estimate non-transferable. In prediction modelling the general
expectation is that a model's performance falls on external data and should be
reported rather than assumed, but transportability is usually evaluated as a
single aggregate drop in performance, which says that a model degraded without
saying which of its components failed.

**We therefore asked a narrower and, we think, more useful question: not
whether the system as a whole generalises, but which individual
literature-derived rules survive transport to populations that had no part in
their construction.** To answer it we assembled a rule base of 21 deterministic
exposure–outcome rules for major eye disease, evaluated it under a
pre-registered three-state standard in the datasets used for development, and
then re-evaluated every rule that could be tested in eight population-based
ageing cohorts on three continents, analysing only raw source files so that the
comparison could not be made circular by another team's harmonisation.

This design produces three kinds of result. First, a rule-level account of
performance in the development and conventional external-validation layers,
reported under both a declared-domain and a conservative precision definition —
the gap between the two is large enough that reporting only one would misstate
the system's behaviour. Second, a **transportability classification** for each
rule that can be tested abroad: transported, single-cohort, direction-reversed,
or unsupported. Third, and most consequentially, an explicit statement of what
the evidence base **cannot** support: 15 of the 21 rules proved untestable in
the ageing cohorts for concrete data reasons — no fundus imaging, no tonometry,
no geocoded exposure, no blood assays, no dietary indices — and we report that
as a finding about the field rather than as a limitation to be smoothed over.

The paper proceeds as follows. The Methods describe the rule base, the
construction and codebook verification of the eight cohort datasets, the
three-state standard and the statistical model. The Results report the
development and external-validation layers, then the cross-cohort
transportability analysis, including the one rule whose direction of effect
reversed between regions. The Discussion sets out the competing explanations
for that reversal, states what would be required to distinguish them, and
considers what the untestable rules imply for how ophthalmic exposome evidence
should be collected.

---

# Methods

## Reporting and study design

This is a retrospective, multi-cohort evaluation of a rule-based clinical
decision-support system for ocular risk in older adults. The observational cohort
analyses follow STROBE [7], and the cross-cohort synthesis follows standard
meta-analytic reporting (random-effects pooling with REML tau-squared, Cochran's
Q, I-squared and prediction intervals). **TRIPOD+AI [8] and DECIDE-AI [9]
are not applicable to this work and are not claimed**: both govern the reporting
of prediction models with estimated coefficients and their evaluation, whereas
this study evaluates deterministic rules taken from the literature, reports no
model calibration or discrimination, and involves no prospective clinical
deployment. They are cited here only to record that the applicability question
was considered. No participant was contacted and no intervention was
administered; all analyses used de-identified public data.

The study has four tiers and the tiers were fixed before the confirmatory
analyses were run. A **development** set of 134 literature-derived
exposure–disease pairs was used to construct the rule base only. **Internal
validation** used the US National Health and Nutrition Examination Survey.
**External validation** used the Korea National Health and Nutrition Examination
Survey [10], one wave of the China Health and Retirement Longitudinal Study
[11], and — new in this report — eight population-based ageing cohorts on
three continents.
The eight-cohort layer was pre-registered, including its testable rule set, its
per-cohort BMI cut-point, its covariate set and its transportability criterion,
before any of its models were fitted (analysis plan §19).

## The rule base

The system encodes 21 deterministic rules relating an exposome exposure
(metabolic, nutritional, lifestyle or environmental) to an ocular outcome, each
with a declared direction drawn from the published literature (Table 2). Each rule is
assigned an evidence level (A, B or C) and one rule (r01, uric acid and
cataract) is designated a negative control because the underlying literature is
contradictory. Rule-relevant pairs are the (exposure flag, outcome item) pairs
that a rule asserts something about; all other pairs are exploratory.

## Cohort-layer data sources

Eight cohorts were analysed from raw source files: the Survey of Health, Ageing
and Retirement in Europe (SHARE) [12], the US Health and Retirement Study
(HRS) [13], the English Longitudinal Study of Ageing (ELSA) [14], the Korean
Longitudinal Study of Ageing (KLoSA), the Longitudinal Ageing Study in India
(LASI) [15], the Mexican Health and Aging Study (MHAS) [16], the Chinese
Longitudinal Healthy Longevity Survey (CLHLS), and the Costa Rican Study on
Longevity and Healthy Ageing (CRELES). CLHLS and CRELES are cited to their
**data deposits** [17-19]. An earlier version of this section claimed
none of the three could be cited, which was wrong twice over: a dataset is
citable in its own right, and the search had covered only article indexes
(Crossref, OpenAlex) and not the data repositories. KLoSA has no citable data
deposit that could be located and is described by provider name only. In total **598,386
unique person-wave records were analysed, from 285,878 participants** (unique
person-waves: SHARE 338,703; LASI 73,408; CLHLS 72,744; HRS 42,946; KLoSA
40,406; MHAS 15,217; ELSA 9,771; CRELES 5,191). Table 1b gives the per-cohort
denominators, prevalences and frame-missingness that every cohort-layer estimate
is computed from; because it is derived from the analysis frames themselves, it
cannot drift from the analysis. SHARE distributes five
imputation replicates stacked as rows, so its raw row count (1,693,515) is five
times its unique person-wave count; **replicate 1 is used for every descriptive
and power calculation and the five are combined only by Rubin's rules for the
model estimates, so an imputation replicate is never counted as an independent
participant.** MHAS contributes no rule × cohort cell to the confirmatory
analysis (its measured exposures and ocular outcomes do not co-occur with
sufficient non-missing data), which is why the transportability figure shows
seven cohorts while the layer was built from eight; the modality audit in
Table 7 reports MHAS's cells as infeasible rather than omitting the cohort.

Analyses used **raw source files only**. Harmonised derivative releases were
excluded by design — the Gateway to Global Aging harmonised files, third-party
harmonisations such as easySHARE, the RAND HRS Fat File, and all intermediates
from earlier work on this project — because a harmonised variable encodes
another team's operationalisation, which would make the transportability
question circular. Official files distributed by the data providers themselves
(SHARE `gv_*` modules, the MHAS constructed and imputation files) were used, and
where a provider supplies quality or imputation flags, the main analysis is
restricted to measured rather than imputed values.

## Variable operationalisation and quality control

Every variable was operationalised from the cohort's own codebook, and three
failure modes were treated as blocking rather than cosmetic.

First, **availability was never inferred from variable names or from a numeric
coercion**. A labelled categorical is delivered by common readers as categories
whose values are the label strings, so a numeric coercion maps every entry to
missing and the flag silently comes out empty; availability was therefore judged
on non-missing counts with the dtype printed, and labelled categoricals were
decoded by recovering the leading integer of each label. This reversed two early
and incorrect conclusions, that SHARE was unusable and that KLoSA held eye data
only in its imputation files.

Second, **every binary exposure flag passed a gate audit before use.** Several
questionnaires ask about a behaviour conditionally — current smoking only of
those reporting ever smoking — and treating such an item as a whole-sample
question inflates or deflates its prevalence according to the nesting direction,
which differs between cohorts. Flags retain the gate-negative branch as an
unexposed observation; current smoking in SHARE, for example, is 17.2%.

Third, **each outcome flag passed a two-tier plausibility gate** against
published prevalence for a comparable age range: a wide band that fails the flag
outright, and a narrower typical band reported but not enforced, because one
band cannot distinguish a wrong variable from a genuinely different population.
The gate is computed per wave as well as pooled, since a coding error confined
to one wave is invisible in the pooled prevalence; this is how a mis-scaled
three-level vision item in one CLHLS wave was found.

Construct shifts were declared rather than merged: cataract surgery and
glaucoma treatment are not diagnoses and never substituted for them, self-report
was kept distinct from examination-based grading, and vision ratings were
treated as **corrected** vision.


## Outcomes and exposures in the cohort layer

Ocular outcomes available across cohorts were cataract (five cohorts), glaucoma
(five), age-related macular degeneration (ELSA only) and self-rated vision
impairment (all eight). No cohort in this layer has fundus imaging, tonometry or
optic-disc grading, so rules requiring those measurements are untestable here by
construction and are reported as such rather than approximated by a proxy.

Body mass index cut-points were pre-declared per cohort rather than pooled,
because the appropriate threshold is population-specific: 25 kg/m² for the Asian
cohorts and 30 kg/m² for the others, with the alternative cut reported as a
sensitivity analysis. This choice was fixed by the prevalence gate before any
association was estimated.

### Disclosure: the r02 exposure is self-reported, not measured

Rule r02 is stated as hyperglycaemia → cataract and its sibling rule r03
requires a measured HbA1c. **No cohort in this layer has a usable fasting
glucose or HbA1c measurement, and both flags were therefore operationalised as
self-reported physician-diagnosed diabetes.** The rule is titled
"self-reported diabetes → cataract" wherever this layer's results are reported,
and the substitution is stated here rather than left implicit.

Two consequences should be weighed. First, this contradicts the preference for
measured over self-reported exposures stated above; it was unavoidable in this
layer, but it means r02's transportability in these cohorts is transportability
of a *self-report* rule, and the NHANES/KNHANES layers — which test the same
rule on measured glycaemic markers — are not testing the same construct.

Second, the substitution is not neutral across cohorts. Self-reported diabetes
prevalence in the four cohorts that tested r02 ranges from **1.36% (CLHLS) to
19.14% (CRELES)**, a fourteen-fold spread. Differential under-ascertainment of
diagnosed diabetes tracks access to care, which is itself correlated with the
outcome, so the exposure is not on the same scale in each cohort. The CLHLS
estimate is the largest in the set (OR 3.59) and comes from the cohort with by
far the lowest reported prevalence, which is the pattern that differential
ascertainment would produce.

This is not an incidental limitation. **It is the paper's own argument occurring
inside the paper**: the measurement the rule requires does not exist in the
populations asked to test it, and the substitute that was used is not comparable
across them.

## The three-state standard

A rule-relevant pair is **replicated** when its multiplicity-adjusted q < 0.05
and its effect estimate lies in the rule's declared direction, **contradicted**
when q < 0.05 and it lies in the opposite direction, and **uninformative**
otherwise. Two precision denominators are reported and are never interchanged:
declared-domain precision omits uninformative pairs from the denominator, while
conservative precision counts them as failures to replicate. Both are reported
for every layer because the gap between them is the single largest lever on the
headline figure.

## Statistical analysis

In the cohort layer each rule-relevant pair was estimated by logistic regression
within cohort, with age and sex as covariates and wave fixed effects where more
than one wave contributed, and with variance clustered by participant to account
for repeated observations. SHARE supplies five imputation replicates; the model
was fitted on each and the estimates combined by Rubin's rules [20]. The
prevalence gate and all descriptive statistics use the first replicate only, so
that an imputation replicate is never counted as an independent person.

Multiplicity was controlled by the Benjamini–Yekutieli procedure [21], which
remains valid under arbitrary dependence, over two pre-registered families: a
confirmatory family containing the rule-relevant pairs and an exploratory family
containing every exposure–outcome pair actually tested in that cohort. Exact
binomial intervals for proportions use the Clopper–Pearson method [22].

Power was computed per pair rather than assumed. For each pair the minimum
detectable odds ratio at 80% power was derived from the observed marginal
counts, and the design effect was estimated from the ratio of the survey-based
to the model-based confidence-interval width rather than set to a conventional
value.

## System architecture and comparators

The system combines a deterministic rule engine, a knowledge-graph retrieval
layer, and a language-model arbiter that produces a risk-graded, fully traceable
report (Figure 1). It was compared against three baselines — a retrieval-only
system, a plain language model, and a naive retrieval baseline — under five random
seeds per method, with the language-model component held fixed so that differences
reflect architecture rather than model choice. Paired comparisons used exact
McNemar tests.

## Software and reproducibility

Analyses used Python 3.10 with pandas, statsmodels and SciPy, and R 4.6.1 with
the survey package for design-based variance. Rule definitions, cohort variable
maps and every correction applied to them are version-controlled in the
repository, and each figure and table is generated from a single declared source
file so that no reported number exists in only one place.

### Construct substitutions: every rule that was tested on a broader construct

The rule base names specific constructs; the cohort layer tests whichever
construct the data can support. Where those differ, the difference is a
substitution and is listed here rather than left implicit. Enumerated from the
outcome and exposure maps, there are two, and between them they affect seven
rules.

| Rule(s) | Declared construct | Construct actually tested | Why |
|---|---|---|---|
| r05, r06, r09, r11 | late AMD | **any AMD** | no cohort separates late from early AMD |
| r17 | early AMD | **any AMD** | same |
| r02 | hyperglycaemia | **self-reported diabetes** | no fasting glucose or HbA1c measurement |
| r03, r04 | measured HbA1c | **self-reported diabetes** | same |

**Five rules that name a specific AMD stage — four of them late AMD, one early —
are all tested against "any AMD", so the stage distinction the rules draw is
discarded.** Of those five only r11 is testable in this layer (r05 and r06 lack
blood assays, r09 lacks a dietary index, r17 lacks geocoded exposure), and r11 is
therefore reported as **any AMD**, not late AMD. The r02 substitution is the same
pattern on the exposure side and is described in its own section above.

**This is not a list of incidental caveats; it is the paper's thesis occurring
inside the paper.** In each row the rule names a construct, the population lacks
the measurement that would identify it, and a broader construct is used instead.
The substitutes are not equivalent — "any AMD" mixes two diseases with different
natural histories, and self-reported diabetes ascertains only diagnosed disease,
with the under-ascertainment tracking access to care. Reporting the substitutions
one at a time as limitations would understate what they show; reporting them
together is what makes them evidence for the conclusion that measurement
availability, and not sample size, is the binding constraint on this rule base.

### Construct validation against an examination survey

The positive control left an ambiguity that the ageing cohorts cannot resolve.
CLHLS and ELSA both ascertain cataract by self-reported physician diagnosis, yet
age predicts it 1.15-fold per decade in one and 3.14-fold in the other. Either
the populations differ, or the same nominal self-report captures different things
in each. The ageing cohorts have no objective ocular measurement, so we turned to
a survey that has both.

**NHANES 2005-2008 measured the same participants with a self-reported cataract
item and an objective near-vision test.** We pooled the two waves (n = 14,440)
and fitted, for each of four constructs, the same model used on the ageing
cohorts: outcome ~ age (per decade) + sex + wave. The four were: self-reported
cataract operation on the questionnaire; the same question asked at the
examination; self-rated fair-or-poor eyesight; and objective near-card acuity
below the impaired threshold. Coding follows the release documentation
(yes/no items as 1/2; the eyesight item as a 1-5 scale collapsed to
excellent-or-good versus fair-to-very-poor; acuity as lines read).

**We state the expectation we held before running this**, because the result
contradicted it: we expected the self-reported item to track age weakly and the
objective test to track it strongly, which would have made self-report the weaker
instrument. **It is the reverse.**

### Positive control: a falsification test of our own premise

The argument of this paper is that measurement availability, not sample size,
bounds what this rule base can test, and that the rules that were testable show
more between-cohort heterogeneity than a pooled estimate can carry. **A reviewer
is entitled to the opposite reading: that these cohorts are too noisily or too
incomparably measured to detect anything, in which case the rule heterogeneity
says nothing about the rules.** That reading is testable, so we tested it.

Age and sex are associated with cataract and with vision impairment in every
population in which anyone has looked, with large effects and no disagreement
about direction. We therefore estimated, in every cohort that can support it:

    outcome ~ age (per decade) + female + wave, clustered by participant

and pooled the results across cohorts **with the same random-effects estimator
used for the rules**, so that the control and the rules are directly comparable.
The control was specified before it was run as a falsification test: if the
cohorts cannot recover an association that is certainly real with tolerable
heterogeneity, then the rule heterogeneity must not be read as evidence about
the rules. **We report the outcome whichever way it falls.**

### E-values

For the estimates that reversed direction, we report E-values by the method of
VanderWeele and Ding: the minimum strength that an unmeasured confounder would
need, on both the exposure and the outcome side, to explain the estimate away.
**The formula is derived for risk ratios, so each odds ratio was converted
before use**, using the risk among the unexposed from the cohort frame:

    RR = OR / (1 - p0 + p0 * OR)

**The conversion matters here and we report it because an earlier version of
this analysis omitted it.** The rare-outcome approximation RR ~ OR fails in this
setting: the unexposed risk of cataract is 17.8% in CLHLS, 21.1% for the alcohol
pair and 8.8% in SHARE. Using the odds ratio directly inflated the E-values —
most severely for r02 in CLHLS, where 6.64 becomes **4.51**, an overstatement of
robustness by 47%. The corrected values are used throughout, and the uncorrected
ones are not reported anywhere in this paper.

## Deviations from the pre-registered protocol

The cohort layer was pre-specified before it was run: the testable rule set
(analysis plan section 19.6: six rules, eighteen pairs, measured rather than
assumed), the per-cohort body-mass-index cut-point (section 19.7: 25 kg/m2 for
the Asian cohorts, 30 kg/m2 otherwise, with the choice fixed by the prevalence
gate), the covariate set (age, sex, wave fixed effects, clustered by
participant), and the transportability criterion (replicated with q < 0.05 in at
least two cohorts). Those four items are reported as pre-specified.

**Five further analyses were added after the primary results were known, and
they supply most of the quantitative support for the Abstract and Conclusions.
They are listed here so that the reader can weight them accordingly.**

| Analysis | Pre-specified? | Time relative to the primary result |
|---|---|---|
| Random-effects pooling (REML tau-squared, Cochran's Q, I-squared, prediction intervals) | No | after |
| Heterogeneity-aware transportability criterion (prediction interval excluding 1 and I-squared below 75%) | No | after |
| Regional subgroup comparison (Europe / Asia / Americas) | No | after |
| E-values for unmeasured confounding | No | after |
| Measurement-modality audit and cohort-layer power calculation | No | after |

**Two further deviations are recorded here because they bear on every estimate in this layer.**

**Variance method (section 19.7, not implemented).** The pre-registration specifies survey design variance — strata, primary sampling units and weights — for the cohorts that distribute design weights, naming SHARE and LASI. The analysis as run used an unweighted cluster-robust generalised linear model. This is not a modelling preference that was weighed and rejected: **the cohort frames were built without any design variable.** A scan of all eight frames finds no weight, strata or PSU column, and SHARE's `country` field is empty in all 1,693,515 of its rows. Every confidence interval, every q-value and therefore every three-state label reported for this layer rests on unweighted variance. Because SHARE contributes 137,183 of the 285,878 participants and is the cohort whose estimate drives the heterogeneity of r10, a design-based re-analysis could move that rule's conclusions in either direction; we report the deviation rather than assume it away.

**Rule set modified after the confirmatory run (section 0, not reported in the manuscript).** The internal layers were first run on a 20-rule set (v1.1). The following morning the rule set was changed — the exposure cross-coverage of r02, r03 and r04 was altered and rule r22 was added — giving the 21-rule set (v1.2) used throughout this paper, and the confirmatory analysis was re-run on it. The pre-registration records this in its own words as **test-set fitting**, and states that the resulting recall of 1.000 is constructed rather than earned. The internal-layer results below are therefore reported on a rule set that was adjusted after seeing outcome data, and **the declared-domain precision of 1.00 in the NHANES and KNHANES layers should be read in that light**. The pre-registration requires both versions to be shown; the v1.1 figures are not reconstructible from the artefacts retained here, which is itself reported as a limitation rather than papered over.

**Consequence for the conclusions.** The rule-level claims of this paper are made on the cohort layer, which was run once and not re-run after any rule change. The internal-layer precision figures are reported for completeness and are not load-bearing for anything argued here.

Consequences for how the paper should be read. First, the **regional subgroup
comparison was constructed after the primary analysis and is reported as
post hoc**; the grouping is also unbalanced, with one cohort in the Americas.
Second, where a comparison rests on a two-cohort rule the subgroup test is
**not independent evidence** of a regional difference: with two cohorts split
one per group, the between-group statistic is the same quantity as the overall
heterogeneity statistic, and the two p-values are identical by construction
(r12 and r13 in Table 5). Third, the **75% heterogeneity threshold in the
stricter criterion was chosen after seeing the results**; it is a conventional
value but it is not pre-specified, and the claim it supports is that no rule met
a stated standard, not that 75% is the correct standard.

**Timeline disclosure.** For this layer, as for the earlier layers of this
project (analysis plan sections 12, 13, 15 and 16), no independent
pre-run version-control snapshot can be produced: the pre-registration text was
not committed to version control before the analysis ran, and a hash frozen
after the fact would not demonstrate otherwise. What can be stated is internal
consistency: the pre-registration is dated before the primary analysis script,
which is dated before the primary result files, while all five analyses above
are dated after them. Readers should treat the four pre-specified items at the
same evidential level as the earlier layers' pre-registrations, and the five
added analyses as clearly labelled post-hoc work.

---

# Results

All rule-level inference below uses the pre-registered three-state standard: a
rule-relevant (exposure flag, outcome item) pair is **replicated** when its
Benjamini–Hochberg–Yekutieli q < 0.05 and its odds ratio points in the rule's
declared direction, **contradicted** when q < 0.05 and it points the other way,
and **uninformative** otherwise. Two precision denominators are reported
throughout and are never interchanged: *declared-domain* precision counts
uninformative pairs as neither success nor failure; *conservative* precision
counts every tested rule-relevant pair in the denominator and therefore treats
an uninformative result as a failure to replicate (Figure 3).

## The internal layers

The rule base was evaluated in four waves of increasing independence (Tables 1
and 4): a 134-pair development set used for rule construction only, 110 NHANES
pairs, and external validation in 56 KNHANES pairs and 14 CHARLS 2011 pairs. Of
these, 159/180 NHANES, 301/352 KNHANES and 14/14 CHARLS pairs were testable; the
remainder were underpowered (21, 50 and 0) and are excluded from precision
numerators rather than counted as failures.

Under survey-design variance, 16 NHANES rule-relevant pairs were testable, of
which **6 replicated and none was contradicted** (10 uninformative), giving
declared-domain precision **1.00 (95% CI 0.541–1.00)**, conservative precision
**0.375** and coverage **0.889**. KNHANES reproduced the pattern: 15 testable
pairs, **5 replicated, 0 contradicted**, declared-domain precision **1.00
(0.478–1.00)**, conservative precision **0.333**, coverage **0.882**. CHARLS was
the weakest layer — 4 testable pairs, **all uninformative**, so declared-domain
precision is undefined and conservative precision **0.000** by construction; no
conclusion is drawn from it alone.

Because the gap between 1.00 and 0.375 is the largest single lever on the
headline figure, the sensitivity analysis (Table 3) reports four alternative
rule sets. Restricting to evidence level A leaves 1 pair, **not replicated**
(conservative precision 0.000); levels A and B give 13 pairs, 4 replicated,
**0.308**; excluding the test-set-leakage rule r22 and the negative control r01
gives 16 pairs, 6 replicated, **0.375**. Replication is concentrated entirely
outside the highest literature evidence tier.

Modelling the same exposures continuously rather than as dichotomies reproduces
this pattern rather than overturning it (Figure 4). Serum cotinine per standard
deviation is unrelated to cataract (OR per SD 0.92, q = 0.31) and to late AMD
(1.08, q = 0.53) in NHANES, so the smoking nulls are not an artefact of
dichotomising self-reported exposure. BMI × cataract by contrast is significant
per SD in KNHANES (1.077, 95% CI 1.034–1.122, q = 0.0014) and null in NHANES
(1.030, q = 0.71); with BMI ≥ 25 affecting roughly a third of the Korean sample,
the binary rule's null there partly reflects its pre-specified cut-point. Direction
agreed with the rule in 19/24 NHANES and 9/10 KNHANES rule-relevant pairs.


## Cross-cohort transportability across eight ageing cohorts

To test whether these rules hold outside the datasets used to build them, the
rules were re-evaluated in eight population-based ageing cohorts on three
continents, using only raw source files and per-cohort codebook-verified
operationalisation (SHARE, HRS, ELSA, KLoSA, LASI, MHAS, CLHLS, CRELES;
598,386 unique person-wave records from 285,878 participants). The layer was
pre-registered before it was run
(analysis_plan §19), including the testable rule set, the per-cohort BMI
cut-point, the covariate set and the transportability criterion.

**Only 6 of the 21 rules could be tested at all.** Fifteen were not testable in
any cohort: five require fundus imaging (r03, r04, r07, r19, r22), one requires
tonometry or optic-disc grading (r16), three require geocoded exposure (r17,
r18, r21), three require blood assays (r01, r06, r14) and two require dietary
indices (r08, r09); r05 requires a lipid panel. Across the six testable rules,
**18 rule × cohort pairs were analysed** (Figure 6). Of these, **8 replicated,
8 were uninformative and 2 were contradicted**.

Two rules transported. **r02 replicated in three of
four testable cohorts — LASI OR 1.88 (1.76–2.00), SHARE 1.75 (1.69–1.82), CLHLS
3.59 (2.62–4.91) — with CRELES at 1.31 (1.07–1.61) falling just short
(q = 0.051). **r20 (smoking → vision impairment)** replicated in three of five
cohorts — HRS 1.61 (1.47–1.78), ELSA 1.49 (1.21–1.83), SHARE 1.09 (1.04–1.13) —
and, importantly, **all five cohorts pointed the same way**, the remaining two
(KLoSA 1.10, CLHLS 1.03) being uninformative rather than opposed.

Two rules did not transport. **r10 (smoking → cataract)** is risk-increasing in
SHARE (OR 1.11, 1.04–1.18, q = 0.0095) and **protective** in CLHLS (OR 0.748,
0.64–0.87, q = 0.0012), with ELSA (0.77) and CRELES (0.70) also protective
though uninformative. **The split is one against three, and it is not regional
and not explained by region.** ELSA is European and points the same protective
way as CLHLS and CRELES; a between-region test is not significant once each
region is pooled with random-effects rather than fixed-effect weights (Europe
0.94, p = 0.45), whereas the fixed-effect pooling used in an earlier version of
this analysis gave 1.08 and p < 0.0001 — an artefact, because Europe's pool
would then be 93% SHARE by weight since SHARE's standard error is roughly twenty
times smaller than the others'. The disagreement is between **one cohort and the
other three**, which leave-one-out analysis confirms: dropping SHARE takes
I² to 0.0% and the pooled estimate to 0.747 (0.66–0.84).
**r12 (alcohol → cataract)** was contradicted in CLHLS (OR 0.809, 0.70–0.93,
q = 0.018) and unreplicated in SHARE (0.963).

The remaining two rules were uninformative in a way that carries no weight.
**r13 (BMI → cataract)** replicated in SHARE (OR 1.24, 1.20–1.29) but not in
CRELES (0.99), so it rests on a single cohort. **r11 (smoking → any AMD)** was
testable only in ELSA; its minimum detectable odds ratio at 80% power is 1.70
and its interval (0.86, 0.55–1.34) excludes associations of that size, so it is
a powered null rather than an absence of evidence — ELSA could have excluded a
1.7-fold or larger association and did not find one.

The cohort layer therefore does not corroborate the R11 picture uniformly. In
the NHANES and KNHANES layers no rule was contradicted; in the cohort layer two
pairs were, and one of them is a direction reversal within a single rule rather
than a uniform null.

### A positive control fails, and that failure frames everything below

Before the rules, the control. Age is associated with cataract in every
population studied, with a large effect and no dispute about direction. Pooled
across the five cohorts that can estimate it, the association is **OR 1.99 per
decade (1.45–2.75) with I² = 99.2%** — and per cohort it is 2.25 in SHARE, 3.14
in ELSA, 2.16 in LASI, 1.81 in CRELES and **1.15 in CLHLS**. For vision
impairment the age association is OR 1.36 (1.11–1.66) with **I² = 99.5%**. The
sex associations are less extreme but still heterogeneous (cataract 65.0%,
vision impairment 96.2%).

**The positive controls are more heterogeneous than any of the exposure rules
(79.5–93.8%).** This is not the result we expected and it changes what the paper
can claim:

1. **The strongest form of our original claim does not hold.** We cannot
   attribute the rules' heterogeneity to the exposures alone, because the
   outcomes are heterogeneous too — even for age, whose association with
   cataract is not in doubt.
2. **The narrower claim is better supported and more general.** In this data
   layer, neither the outcomes nor the exposures are comparable enough across
   cohorts for a pooled estimate to predict a new population. That is now
   demonstrable using associations that are certainly real, rather than resting
   on rules whose truth is exactly what is in question.
3. **A pooled multi-cohort exposome estimate should not be read as a
   population-transportable quantity.** That is the paper's warning, and the
   positive control is its evidence.

**Two consequences for reading the rest of this paper.** First, the rule results
below should be interpreted as describing *this evidence base*, not the
underlying biology: where a rule fails to transport, the failure may lie in
either the rule or the measurement, and this layer cannot separate them.
Second, the construct substitutions documented in the Methods are not a minor
caveat but an instance of the same phenomenon — the measurement a rule needs
does not exist in the populations asked to test it.

### The outcome construct itself is population-dependent

The positive control left open whether self-reported cataract is simply a weak
instrument. **NHANES 2005-2008 says it is not.** In that survey, which measured
the same people with both a self-report and an objective near-vision test:

| Construct | n | Age OR per decade (95% CI) |
|---|---|---|
| Self-reported cataract operation | 7,074 | **4.27** (3.91–4.67) |
| Same question asked at the examination | 6,429 | **4.30** (3.90–4.74) |
| Self-rated fair-or-poor eyesight | 7,065 | 1.15 (1.11–1.20) |
| Objective near acuity, impaired | 4,786 | 1.32 (1.22–1.42) |

**Self-reported cataract tracks age 3.2 times more strongly than the objective
acuity test**, so self-report is not intrinsically the weaker instrument. That
removes the explanation we expected and leaves the harder one: if a
well-conducted survey gets 4.27 on this construct, CLHLS's 1.22 is a property of
CLHLS, not of self-report.

**It is not the wave structure.** Restricting CLHLS to the 1998 wave alone — the
one whose provenance is unambiguous — leaves the gradient flat: prevalence is
17.9% at ages 75–80, 16.6% at 80–85, 17.8% at 85–90 and 18.4% at 90–95, rising
only past 95. The age odds ratio is **1.22 per decade** (p = 1.2 × 10⁻⁷) against
NHANES's 4.27.

**The item measures diagnosis, and diagnosis is access-dependent.** The CLHLS
question asks whether the respondent suffers from cataract; cataract is diagnosed
by an eye examination. In rural China in 1998 such examinations were uncommon and
their availability tracked access to care, so the item records the probability of
having been diagnosed rather than the probability of having the disease. That is
the same mechanism we invoke — and had previously only conceded in passing — for
smoking and cataract: **where a self-reported outcome depends on being diagnosed,
its measured prevalence depends on who has access to diagnosis.**

**Consequence for pooling.** Two cohorts can use the same nominal outcome, the
same nominal ascertainment and the same model, and still be measuring different
quantities. This is not a caveat appended to the analysis; it is the reason the
pooled estimate in this paper describes no population, and it is demonstrable
with a benchmark rather than asserted.

## Between-cohort heterogeneity: the pooled estimate is not the answer

Reported as counts of replicated cohorts, the transportability picture above is
too generous, and the heterogeneity analysis shows why. Every rule with more
than one cohort shows high between-cohort I², and for **every one of
them the 95% prediction interval — the range in which a new cohort's true effect
would be expected to fall — includes the null** (Table 5). I² must be read
alongside τ² here: on the log-odds-ratio scale the fitted τ² corresponds to
cross-cohort ratio differences of only **1.24× to 2.13×**, and the high I² is
driven by SHARE's very small standard error rather than by large absolute
divergence, so using I² alone as a rejection criterion would partly be a
sample-size penalty (Table 5).

**A person-level test does not reproduce the two-cohort heterogeneity.** The
subgroup column in Table 5 compares pooled per-cohort estimates, which weights each
cohort once whatever its size and, at k = 2, is arithmetically the same statistic as
Q. Stacking the cohorts and fitting a single model at the level of the participant,
with an exposure × cohort interaction and standard errors clustered on the person,
gives a different answer for the two-cohort rules (Table 5b): **r13 interaction p =
0.15** against a two-stage Q p of 0.027, and **r12 interaction p = 0.14** against
0.027. For the larger rules both tests detect between-cohort heterogeneity — one-step
interaction p = 3.2 × 10⁻⁸ (r02), 0.0022 (r10) and 2.4 × 10⁻²⁹ (r20), against Q p =
6.9 × 10⁻⁷, 2.6 × 10⁻⁷ and 3.0 × 10⁻¹³ — so the conclusion at k > 2 does not depend
on which test is used; the post hoc regional subgroup test is a coarser contrast and
does not reach significance for r10 (p = 0.45). r11 is feasible in one cohort only
and has no interaction to estimate. **At k = 2 the two-stage heterogeneity is
therefore an artifact of equal weighting, not a property of the populations**: r13
pools SHARE (338,703 person-waves) with CRELES (5,191) on equal terms, and the
smaller cohort's noise drives the heterogeneity statistic. This does not change the
pooled estimates or the transportability verdicts, which rest on the pre-registered
criteria; it changes what may be inferred from the two-stage statistic when a rule
is testable in two cohorts only.

Two consequences follow. First, the pooled estimate for r10 is null
(0.84, 0.67–1.05) while three cohorts agree with one another and SHARE does not
(dropping SHARE: I2 = 0.0%, pooled 0.747, 0.66–0.84): **the pooled number is a
weighted compromise between one large precise cohort and three small ones, and
describes neither.** This is not a regional pattern. An earlier version of this
analysis reported a significant between–region difference (Europe 1.08 versus
Asia 0.75 and the Americas 0.70, p < 0.0001); that result was an artefact of
pooling within region with fixed–effect weights, which at this level of
heterogeneity made Europe 93% SHARE. With random–effects weights within region
the between–region p is 0.45. Second, the two rules the pre-registered criterion called
transportable both fail the stricter reading — r02 and r20 replicate in
multiple cohorts and point consistently, yet neither prediction interval
excludes unity, so a new cohort could plausibly show no association. Under a
heterogeneity-aware criterion (prediction interval excluding the null **and**
I² < 75%) **none of the six is transportable** — but that criterion was written
after the pre-registered one proved too permissive and is reported here as a post hoc
sensitivity analysis only. **On the pre-registered criterion, two rules were
transportable**; that is the basis of the Abstract and of this paper’s conclusions. The disagreement is itself a
result: a transportability rule based on counting replications across cohorts is
too permissive, because it does not penalise between-cohort heterogeneity.

Meta-regression gives no support to the obvious explanation. Across the three
rules with four or more cohorts, cohort mean age did not predict the log odds
ratio (slopes +0.017, −0.008 and −0.010 per year; p = 0.42, 0.52 and 0.35), so
the CLHLS cohort's extreme age structure (mean 92.0 years) does not account for
the heterogeneity. Unmeasured confounding was bounded by E-values rather than
asserted: for the protective smoking–cataract estimate in CLHLS the E-value is
1.87 (confidence bound 1.47) and for the risk-increasing SHARE estimate 1.43
(1.25), so an unmeasured confounder associated with both smoking and cataract by
a risk ratio of roughly 1.5–2 would suffice to explain either away. By contrast
the diabetes–cataract estimate in CLHLS has an E-value of 4.51 (3.35) and
is not fragile in the same way. Leave-one-cohort-out analysis (Supplementary S4) shows the opposite of a
distributed pattern: removing SHARE collapses I2 from 91.0% to 0.0% and moves
the pooled estimate to 0.747 (0.66-0.84), which excludes unity. The heterogeneity
is therefore driven by one cohort, and the three remaining cohorts agree with
each other.


## What the evidence base cannot test, quantified

The count of untestable rules was turned into a structured audit by classifying
every rule by the measurement modality its exposure and its outcome require, and
then asking which (rule × cohort) cells are feasible out of the 168 possible
(21 rules × 8 cohorts). **18 cells (10.7%) are feasible** (Table 7). The
remaining 150 fail for three separable reasons: **83 because both sides are
absent, 41 because the exposure is absent, and 26 because the outcome is
absent.** Separating those matters, because a missing exposure and a missing
outcome imply different investments.

Ranking each modality by how many additional cells it would unlock gives the
actionable ordering: **fundus imaging +15, blood assays +13, geocoded
environmental exposure +13, dietary indices +6, further behavioural items +6,
optic-disc grading +5, additional self-reported ocular diagnoses +5,
anthropometry +3.** No cohort in this layer has fundus imaging, tonometry or
optic-disc grading, which is why the entire retinopathy and diabetic macular
oedema family (r03, r04, r07, r19, r22) and the glaucoma-measurement rules (r16)
are untestable in all eight — not underpowered, but unmeasurable. Set against
the 18 cells that are feasible, this is the sharpest statement the layer
supports: **for this rule base the binding constraint is measurement, not sample
size.** The eight cohorts together hold 598,386 person-wave records and
still cannot answer two-thirds of the questions the rules ask.

## Exploratory associations in the cohort layer

Beyond the pre-registered confirmatory pairs, the cohort frames were swept for
all exposure × outcome pairs actually available (68 pairs analysed in total).
Three directions recurred across cohorts and are recorded here as exploratory
only, since they were not pre-registered: diabetes with moderate and severe
vision impairment (KLoSA OR 1.50 and 1.99; SHARE severe 1.46), diabetes with
self-reported glaucoma (LASI OR 1.64, q = 1.2 × 10⁻¹⁰), and current smoking with
severe vision impairment (HRS OR 1.98, q = 8.1 × 10⁻²⁰). All three point the
same way as r20 and are consistent with a metabolic and smoking-related
contribution to vision loss; none is offered as a confirmed finding.

## Statistical power

Power was computed per pair rather than assumed (Figure 5). The median minimum
detectable odds ratio at 80% power was **1.337 in NHANES and 1.159 in KNHANES**.
Of the rule-relevant pairs, **17 of 30 were powered nulls** — the design could
have excluded a 2-fold association — so most uninformative results in these two
layers are informative nulls rather than failures of power. Design effects were
derived per pair from the survey-to-model CI-width ratio (median 1.07 NHANES,
1.26 KNHANES) rather than assumed. Replicated pairs sit in the corner of high
observed odds ratio and low minimum detectable odds ratio: none replicated on
the strength of a small detectable effect alone.

In the cohort layer power was computed the same way, per pair, from the analysed
n and the observed margins (Table 6). Median minimum detectable odds ratios by
rule ranged from 1.11 (r20) to 1.70 (r11). Of the 8 uninformative pairs, **5
(62.5%) were powered nulls** — the analysis could have detected an association at
least as small as its own minimum detectable effect and did not. The three that
were not powered are each explainable from the table: CRELES contributes about
5,000 person-wave records and its r02 interval only just includes unity (1.07,
against an MDE of 1.23); CLHLS r20 was powered for a 1.21-fold association and
observed 1.03; and KLoSA r20 sat exactly at its detection limit (MDE 1.10,
observed 1.10). **This is the principal caution on the negative results and it is
also their defence**: where the cohort layer failed to replicate a rule it can
usually be shown to have had the power to do so.

## System performance

Against the R11-corrected gold the full system attained F1 = 0.522 (P 0.353 /
R 1.000, deterministic), ahead of LightRAG 0.392 ± 0.007, pure LLM
0.335 ± 0.010 and naive RAG 0.080 ± 0.110 over five seeds (Figure 2); paired
McNemar was significant against pure LLM and naive RAG but not against LightRAG
(p = 0.057–0.092). The precision of every method is low (0.10–0.35) because most
predicted-positive pairs are uninformative rather than contradicted — the same
denominator effect seen at rule level. Figure S1 shows one worked case end to
end and Figure S2 traces it through the three architectural layers.

---

# Discussion

## Principal findings

Three findings emerge, and they are ordered by how much they should change
practice.

First, **the transportability of a literature-derived exposome rule cannot be
established by counting how many cohorts replicate it.** Under the criterion
fixed in advance — replicated with q < 0.05 in at least two cohorts — two of the
six testable rules qualified. Under a criterion that also requires the
between-cohort heterogeneity to be tolerable, **none did**: both qualifying
rules had I² above 90% and prediction intervals spanning unity, so a further
population could plausibly show no association at all.

Second, **pooling does not resolve a directional conflict; it conceals one.**
For smoking and cataract the pooled estimate is null (OR 0.84, 95% CI 0.67–1.05)
while three cohorts agree with one another and a fourth does not. The pooled
number is a weighted compromise between a large, precise cohort and three small
ones, and describes neither. This is the more general hazard: a rule base whose
components disagree across populations will produce a bland summary whenever it
is meta-analysed, and the disagreement will be invisible unless heterogeneity is
reported.

Third, **for this rule base the binding constraint is measurement, not sample
size.** Of 168 possible (rule × cohort) cells across eight cohorts holding two
million person-wave records, 18 were feasible. Ranking the missing measurement
modalities by how many cells each would unlock gives a concrete investment
order: fundus imaging (+15), blood assays (+13), geocoded environmental exposure
(+13). The retinopathy and diabetic macular oedema family and the
glaucoma-measurement rules are not underpowered anywhere in this layer — they are
unmeasurable everywhere in it.

## The direction reversal, and what could explain it

Smoking was associated with cataract in opposite directions in different
cohorts: risk-increasing in SHARE (OR 1.11, 1.04–1.18) and protective in CLHLS
(0.748, 0.64–0.87), with ELSA (0.77) and CRELES (0.70) also protective though
uninformative. Three explanations are available, and this layer cannot
distinguish them; what it can do is bound them.

**One cohort, not a region.** An earlier version of this analysis reported r10
as a regional reversal. That was wrong twice over: ELSA is European and
protective, so the protective cohorts were not all non-European; and the
between-region test had pooled within region using fixed-effect weights, which
at this level of heterogeneity made Europe 93% SHARE by weight. Pooled
correctly, the regional difference is not significant (p = 0.45). What remains
is a single cohort whose estimate differs from three others that agree with
each other, and which carries roughly twenty times their precision. Three
explanations are still available for that difference, and this layer cannot
distinguish them; what it can do is bound them.

**Selective survival.** The CLHLS cohort has a mean age of 92.0 years. In
populations of that age, associations estimated cross-sectionally are conditioned
on having survived to be sampled, and the depletion of susceptible individuals
biases risk-factor associations in ways that are well recognised in geriatric
epidemiology, both through comorbidity-adjusted risk models [23] and through
survivorship selection on the trait itself [24]. Smokers die earlier, so among
the extremely old the surviving smokers are a selected minority; a protective
cross-sectional estimate is one of the forms that selection can take. This
explanation predicts that the protective direction should strengthen with
increasing cohort age. It does not: the meta-regression slope on mean age was
−0.008 log-OR per year (p = 0.52), and the two protective cohorts are the oldest
and one of the younger ones. The evidence for selective survival is therefore
indirect and, on this design, unconfirmed.

**Unmeasured confounding.** The E-value for the CLHLS protective estimate is 1.87
(confidence bound 1.57) and for the SHARE risk-increasing estimate 1.46 (1.25).
An unmeasured confounder associated with both smoking and cataract by a risk
ratio of roughly 1.5 to 2 would suffice to move either estimate to the null. That
is a modest requirement: socioeconomic position and rural residence plausibly
exceed it, and because the cohorts differ in exactly those distributions, the
reversal is as consistent with differential confounding as with differential
effect.

**Genuine effect modification.** Cataract is not one disease. Nuclear, cortical
and posterior subcapsular opacities have different risk-factor profiles, and the
pooled literature association is a weighted average over them [6]. If the
subtype mix differs between cohorts — which it does, with different sun-exposure
and diabetes prevalences — then the same exposure can produce different marginal
associations without any bias. This explanation is the only one that would
license a genuinely population-specific rule, and it is also the one this design
is least able to test, because no cohort in the layer grades opacity subtype.

**What would distinguish them.** Three things, none available here: longitudinal
measurement of exposure before outcome, so that reverse causation and selective
survival are separated from incidence; lens examination with subtype grading, so
that a compositional explanation is testable; and measurement of the specific
confounders named above, so that the E-value bound becomes an estimate rather
than a bound. We report the reversal as an unexplained between-population
discrepancy. We do not prefer an explanation.

The same caution applies to the alcohol–cataract rule, where CLHLS gave a
protective estimate (0.809, 0.70–0.93) that SHARE did not reproduce (0.963). The
reasons people abstain differ systematically between populations and include
illness and prior dependence, so "abstainers" are not a comparable exposure
category across cohorts [25]; a protective association with drinking is the
expected direction when those who quit did so because they were unwell.

## Why the pooled estimate is the wrong summary here

Heterogeneity of this magnitude is not a nuisance to be absorbed. With I² of
90–94% across every multi-cohort rule [26], the fixed- or random-effects
average estimates a quantity that no population in the analysis has, and the
confidence interval around it understates the uncertainty a new population
faces. The prediction interval is the appropriate summary because it answers the
question a clinician or a health service actually asks — what should we expect
here? — and in this layer **every prediction interval includes the null**:
r02 0.30–12.63, r10 0.30–2.31, r20 0.62–2.46 [27]. Leave-one-cohort-out
analysis, reported in full in Supplementary S4, qualifies this reading and
corrects an earlier claim of ours: removing SHARE collapses I² from 91.0% to
0.0% and moves the pooled estimate to 0.747 (0.66–0.84), so the heterogeneity is
driven by SHARE rather than distributed across cohorts. The 1:3 regional split
described above is therefore better stated as one European cohort disagreeing
with a homogeneous protective cluster — without SHARE the remaining three
cohorts agree at I² = 0 with a pooled estimate that excludes unity.

The practical implication for anyone assembling a screening rule base is that
reporting a pooled effect, or a replication count, without a heterogeneity
statistic is not merely incomplete: it is the reporting choice most likely to
make a heterogeneous evidence base look settled.

## A criterion that was too permissive

The transportability criterion used here was pre-registered and is reported as
primary. It failed in an instructive way. It asked whether at least two cohorts
replicated a rule, which is a reasonable operationalisation of "does this hold
somewhere else?", but it is insensitive to the case where every cohort agrees in
direction while the magnitudes differ enough that a new cohort's expected effect
is compatible with the null. Both rules that passed were of exactly that kind.

We therefore report both verdicts and treat their disagreement as a result.
**The pre-registered criterion, and not the stricter one, is the basis of this
paper's conclusions.** The stricter criterion — prediction interval excluding
the null and I² below 75% — was written after the pre-registered rule turned out
to be too permissive, and the 75% figure was chosen with the results in view; it
is reported as a post hoc sensitivity analysis and is labelled as such. Read on
the pre-registered criterion, **two of six testable rules were transportable**;
read on the post hoc one, none was. The useful methodological observation is the
disagreement itself: a transportability criterion that counts replications is
insensitive to between-cohort heterogeneity, which is why the two readings
differ, and a criterion intended for prospective use should be fixed in advance
with both properties in mind.

**The positive control reframes the finding.** We expected the control to
validate the pipeline: if age predicts cataract consistently everywhere, then
the cohorts can detect real associations and the rule heterogeneity must be
about the rules. It did not. Age-cataract is more heterogeneous across these
cohorts (I² = 99.2%) than any of the exposure rules, and the CLHLS estimate is a
third of the ELSA estimate for an association whose direction is not in
disputation.

That result is uncomfortable for the paper and we have kept it in the
foreground rather than in the supplement, because it is the more useful finding.
It means the limitation of a pooled multi-cohort exposome analysis is not
confined to the exposures: **the outcome definitions are themselves not
comparable enough, and a pooled estimate therefore describes a quantity no
single population has.** The practical rule that follows is narrow but real:
a pooled exposome estimate should be published with its prediction interval and
its per-population estimates, and should not be presented as the effect to
expect in a new setting. A pooled point estimate from cohorts this heterogeneous
is a summary of a literature, not a parameter of nature.

**What the outcome validation settles, and what it withdraws.** We expected
self-reported cataract to be the weaker instrument and designed the NHANES
comparison to show it. It showed the opposite: self-reported cataract tracks age
at OR 4.27 per decade while objective near acuity tracks it at 1.32. The
"self-report is intrinsically weak" explanation is therefore withdrawn, and what
replaces it is both less obvious and more useful. **A nominal construct can be
ascertained the same way in two cohorts and still measure different quantities,
because what a self-report captures depends on who in that population has access
to the diagnosis.** CLHLS's flat age gradient for cataract (1.22, and flat across
four age bands even in the clean single wave) is the signature of that mechanism,
and it is the mechanism we had already conceded in the Limitations without
letting it do any work.

**The practical rule.** In any multi-cohort pooling of self-reported outcomes,
the quantity that makes the cohorts comparable is not the wording of the item but
the population's underlying rate of diagnosis. Reporting a pooled odds ratio
across cohorts whose diagnosis rates differ converts a difference in access to
care into an apparent difference in biology. The minimum safeguard is to report
the outcome's prevalence by cohort alongside the pooled estimate, and to prefer
examination-based measurement where the construct permits it — which, as this
paper's own modality audit shows, is precisely what the ophthalmic exposome
evidence base most often lacks.

## Measurement as the limiting factor

The audit in Table 7 implies a specific agenda. Fundus imaging is the single
highest-value addition, unlocking 15 further cells, followed by blood assays and
geocoded environmental exposure at 13 each. These are not exotic measurements;
they are standard in ophthalmological field studies and in several
population cohorts outside this set. Their absence from the major ageing cohorts
is what keeps the diabetic retinopathy, macular degeneration and
glaucoma-measurement rules outside the reach of the largest available
populations.

The converse is also worth stating: the 18 cells that *are* feasible are
concentrated in self-reported cataract and self-rated vision, which is precisely
where ascertainment is weakest and where the direction reversal appeared. The
layer is thus least reliable exactly where it is most complete.

## Comparison with the internal layers

The cohort layer does not reproduce the pattern of the NHANES and KNHANES
layers. There, no rule-relevant pair was contradicted in either country, and
declared-domain precision was 1.00 in both. Here, two of 18 pairs were
contradicted and the direction conflict is regional. The difference is not that
the internal layers were wrong; it is that they are fewer and less diverse.
Adding populations does not merely add power — it adds the possibility of
disagreement, and a rule-evaluation protocol that has no way to represent
disagreement will report a clean result for a heterogeneous evidence base.

## Limitations

**Independence achieved.** The eight cohorts are independent of each other and
of the NHANES, KNHANES and CHARLS layers: no participant appears in more than
one, and no cohort contributed to rule construction. They are **not** independent
of the literature from which the rules were derived, and this is the most
important limit on what the layer can claim. A rule extracted from published
associations and then tested in cohorts that contributed to those same
publications is not an out-of-sample test in the strict sense. We mitigated this
by using raw source files and codebook-verified operationalisation rather than
harmonised derivatives, so that the variables are not another team's construct;
we did not and could not remove the shared literature.

**Ascertainment.** Cataract and glaucoma are self-reported physician diagnoses
throughout this layer. The NHANES layer used examination-based grading, so the
two are not comparable in effect size and we draw no such comparison. Self-report
introduces differential under-ascertainment where access to care differs, which
is itself correlated with the exposures of interest.

**Design and temporality.** Most contributing waves are cross-sectional for the
exposure, so incidence cannot be separated from prevalent disease, and the
selective-survival explanation for the reversal cannot be tested.

**Power.** Five of the eight uninformative pairs were powered nulls, and the
three that were not are identified (Table 6), so the negative results are mostly
interpretable. The exception is r11, testable only in ELSA, where the analysis
could exclude associations of 1.7-fold or larger and nothing smaller.

**Construct substitutions.** Seven rules were tested on a broader construct than
they declare — five AMD rules against "any AMD" rather than late or early AMD,
and two glycaemic rules against self-reported diabetes rather than a measured
marker (the Methods table lists each). Only two of the seven are testable in
this layer, so the substitutions affect r02 and r11 directly. Their direction of
bias is not uniform and cannot be signed in general: broader outcome definitions
usually dilute an association, whereas self-reported exposure with
access-dependent under-ascertainment can move an estimate either way. What can
be said is that neither r02 nor r11 tests the construct its citation supports,
and that this is the same limitation the paper identifies in the field it is
describing.

**Single-cohort rules.** r11 (AMD) and r13 (BMI) rest on one and two cohorts
respectively, and the ELSA glaucoma and AMD items are the only sources in the
layer. Conclusions about the AMD family are correspondingly weak.

**CLHLS severe vision.** The severe-impairment flag in CLHLS exceeded its
age-unstratified plausibility band (25.7% at a mean age of 92). It is reported as
a secondary analysis only, and no primary conclusion depends on it.

## Conclusion

We set out to ask which literature-derived exposome rules survive transport to
populations that had no part in their construction. The answer is fewer than a
replication count suggests, and the reason is instructive. Of 21 rules, 6 were
testable in eight ageing cohorts — 598,386 person-wave records from 285,878
participants — and, once between-cohort heterogeneity was taken into account,
none was reliably transportable: the two rules that passed the pre-registered
criterion both had prediction intervals spanning the null. One rule's association
reversed; its heterogeneity proved to come from a single cohort rather than from
a balanced regional split, and E-values showed the estimates on both sides to be
ones that modest unmeasured confounding could account for.

The measurement problem this paper diagnoses had already occurred inside it.
Rule r02 requires hyperglycaemia, and no cohort in the layer has a usable
fasting glucose or HbA1c measurement; both that flag and its sibling requiring a
measured HbA1c were therefore operationalised as **self-reported
physician-diagnosed diabetes**, whose prevalence across the four cohorts testing
the rule spans 1.36% to 19.14%. The rule passed the transportability criterion
in that substituted form — and the cohort with the largest estimate (OR 3.59) is
the one reporting the lowest prevalence, which is the pattern differential
ascertainment would produce. That is the paper's argument arriving at its own
doorstep: **the binding constraint is not how many participants a cohort holds
but which exposures it actually measured, and where a measurement is absent the
substitute is not comparable across populations.**

The wider implication follows. A rule base assembled from heterogeneous
literature will not be made trustworthy by validating it in more cohorts unless
the validation is designed to detect disagreement, and unless the exposures it
claims to test are the exposures the cohorts measured. Reporting a pooled effect
and a replication count, without heterogeneity, without a prediction interval
and without stating what was actually measured, is the reporting pattern most
likely to make such a rule base appear settled when it is not. For ophthalmic
exosome screening the productive next step is not a larger cohort but a measured
one: fundus imaging, blood assays and geocoded exposure, for which Table 7 gives
the specific ordering by how many rules each would unlock.

---

# Declarations

## Ethics approval and consent to participate

This study is a secondary analysis of de-identified, publicly available data
from eleven population surveys. No participants were contacted, no intervention
was administered, and no identifiable information was accessed. On that basis
the analysis was determined not to constitute human-subjects research requiring
review by an institutional review board; **the determination was made by
[institution / IRB name and reference — author to complete], and the
corresponding author is responsible for it.** Each source survey had already
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
| NHANES | US Centers for Disease Control and Prevention, National Center for Health Statistics — public download |
| KNHANES | Korea Disease Control and Prevention Agency — application required |
| CHARLS | Peking University National School of Development — application required |
| SHARE | SHARE Research Data Center, share-project.org — free registration for scientific use |
| HRS | Health and Retirement Study, University of Michigan — free registration |
| ELSA | UK Data Service — registration required |
| KLoSA | Korea Employment Information Service (KEIS) — application required |
| LASI | Longitudinal Ageing Study in India, International Institute for Population Sciences — application required |
| MHAS | Mexican Health and Aging Study, mhasweb.org — free registration |
| CLHLS | Chinese Longitudinal Healthy Longevity Survey, Duke University / ICPSR — application required |
| CRELES | Costa Rican Study on Longevity and Healthy Ageing, ICPSR study 26681 — public download |

**Derived data.** The cohort analysis frames, the harmomonisation-free
construction of which is the point of the study, are not redistributed here
because their redistribution would breach the source agreements. They are
regenerable from the raw provider files by the scripts listed below.

**Exact access URLs and any dataset version numbers must be confirmed against
the providers' current pages at submission** — access routes change, and this
table was compiled from the data-release documentation held with the project
rather than from a live check of each provider's site.

## Code availability

All analysis code is in the project repository, which contains, in order: the
rule definitions (`configs/rules.yaml`), the cohort frame builders, the
availability and gate audits, the confirmatory model, the heterogeneity
meta-analysis, the power calculation, the evidence-base audit, and the figure
renderers. An archived snapshot with a DOI will be deposited at
[repository / Zenodo DOI — author to complete]. The entry points are
`scripts/build_cohort_frames.py` (frames) → `scripts/cohort_confirmatory.py`
(primary estimates) → `scripts/cohort_heterogeneity.py` (pooling, I², prediction
intervals, E-values, leave-one-out) → `scripts/cohort_power.py` and
`scripts/evidence_base_audit.py`. **Environment:** Python 3.10.4 with pandas
2.3.3, statsmodels 0.15.0, NumPy 2.2.6 and SciPy 1.15.3. The survey-weighted
sensitivity analysis used R 4.6.1 with the `survey` package.

## Funding

[Funding source and grant number, or the statement that no specific funding was
received — author to complete.]

## Competing interests

[Author to complete.] Declarations should cover, in addition to the usual
interests, any commercial relationship with the large-language-model provider
whose API this work used, and any in-kind provision of compute.

## Author contributions (CRediT)

[Author to complete.] Suggested allocation, given that the analysis pipeline,
figures and manuscript drafts were produced with substantial generative-AI
assistance: the human authors should claim Conceptualization, Methodology,
Data curation, Validation, Supervision, and Writing – review & editing. **An AI
system cannot be listed as an author**, cannot hold responsibility for the work,
and cannot consent to publication.

## Use of generative artificial intelligence

Generative AI tools were used in this work and their role is disclosed here for
transparency. They assisted with: drafting and revising analysis code;
implementing the statistical pipeline; generating figure and table artefacts;
and drafting and editing the manuscript text and its translations. The
quantitative results were produced by executing the code against the source
data; the code, the data-provider files and the audit trail are available as
described above, so every reported number can be recomputed independently.

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
2. Tham YC, Li X, Wong TY, Quigley HA, Aung T, Cheng CY. Global Prevalence of Glaucoma and Projections of Glaucoma Burden through 2040. Ophthalmology. 2014;121(11):2081-2090. doi:10.1016/j.ophtha.2014.05.013. <!-- C023 | n=2 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/j.ophtha.2014.05.013 -->
3. Jonas JB. Global prevalence of age-related macular degeneration. The Lancet Global Health. 2014;2(2):e65-e66. doi:10.1016/s2214-109x(13)70163-3. <!-- C021 | n=3 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/s2214-109x(13)70163-3 -->
4. Song P, Yu J, Chan KY, Τheodoratou E, Rudan I. Prevalence, risk factors and burden of diabetic retinopathy in China: a systematic review and meta-analysis. Journal of Global Health. 2018;8(1):010803. doi:10.7189/jogh.08.010803. <!-- C022 | n=4 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.7189/jogh.08.010803 -->
5. Wild CP. Complementing the Genome with an “Exposome”: The Outstanding Challenge of Environmental Exposure Measurement in Molecular Epidemiology. Cancer Epidemiology Biomarkers & Prevention. 2005;14(8):1847-1850. doi:10.1158/1055-9965.epi-05-0456. <!-- C020 | n=5 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1158/1055-9965.epi-05-0456 -->
6. Ye J, He J, Wang C, Wu H, Shi X, Zhang H, et al. Smoking and Risk of Age-Related Cataract: A Meta-Analysis. Investigative Opthalmology & Visual Science. 2012;53(7):3885. doi:10.1167/iovs.12-9820. <!-- C018 | n=6 | cross_verified | retracted=no | abstract=yes | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1167/iovs.12-9820 -->
7. Vandenbroucke JP. Strengthening the Reporting of Observational Studies in Epidemiology (STROBE). Epidemiology. 2007;18(6):805-835. doi:10.1097/ede.0b013e3181577511. <!-- C003 | n=7 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1097/ede.0b013e3181577511 -->
8. Cohen JF. TRIPOD+AI: an updated reporting guideline for clinical prediction models. BMJ. 2024;385:q824. doi:10.1136/bmj.q824. <!-- C001 | n=8 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1136/bmj.q824 -->
9. The DECIDE-AI Steering Group. DECIDE-AI: new reporting guidelines to bridge the development-to-implementation gap in clinical artificial intelligence. Nature Medicine. 2021;27(2):186-187. doi:10.1038/s41591-021-01229-5. <!-- C002 | n=9 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1038/s41591-021-01229-5 -->
10. Kweon S. Data Resource Profile: The Korea National Health and Nutrition Examination Survey (KNHANES). International Journal of Epidemiology. 2014;43(1):69-77. doi:10.1093/ije/dyt228. <!-- C014 | n=10 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyt228 -->
11. Zhao Y. Cohort Profile: The China Health and Retirement Longitudinal Study (CHARLS). International Journal of Epidemiology. 2012;43(1):61-68. doi:10.1093/ije/dys203. <!-- C013 | n=11 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dys203 -->
12. Börsch-Supan A. Data Resource Profile: The Survey of Health, Ageing and Retirement in Europe (SHARE). International Journal of Epidemiology. 2013;42(4):992-1001. doi:10.1093/ije/dyt088. <!-- C006 | n=12 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyt088 -->
13. Sonnega AJ, Faul JD, Ofstedal MB, Langa KM, Phillips JW, Weir DR. Cohort Profile: the Health and Retirement Study (HRS). International Journal of Epidemiology. 2014;43(2):576-585. doi:10.1093/ije/dyu067. <!-- C007 | n=13 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyu067 -->
14. Steptoe A. Cohort Profile: The English Longitudinal Study of Ageing. International Journal of Epidemiology. 2012;42(6):1640-1648. doi:10.1093/ije/dys168. <!-- C008 | n=14 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dys168 -->
15. Perianayagam A. Cohort Profile: The Longitudinal Ageing Study in India (LASI). International Journal of Epidemiology. 2022;51(4):e167-e176. doi:10.1093/ije/dyab266. <!-- C009 | n=15 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyab266 -->
16. Wong R. Cohort Profile: The Mexican Health and Aging Study (MHAS). International Journal of Epidemiology. 2015;46(2):e2. doi:10.1093/ije/dyu263. <!-- C010 | n=16 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/ije/dyu263 -->
17. The Chinese Longitudinal Healthy Longevity Survey (CLHLS)-Longitudinal Data（1998-2011）. Peking University Opendata Dataverse. 2015. doi:10.18170/DVN/MKB1LF. <!-- C031 | n=17 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=datacite | doi:10.18170/DVN/MKB1LF -->
18. The Costa Rican Longevity and Healthy Aging Study (CRELES). Harvard Dataverse. 2025. doi:10.7910/DVN/7AUOAO. <!-- C032 | n=18 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=datacite | doi:10.7910/DVN/7AUOAO -->
19. CRELES: Costa Rican Longevity and Healthy Aging Study, 2005 (Costa Rica Estudio de Longevidad y Envejecimiento Saludable). ICPSR - Interuniversity Consortium for Political and Social Research. 2010. doi:10.3886/icpsr26681.v2. <!-- C033 | n=19 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=datacite | doi:10.3886/icpsr26681.v2 -->
20. Rubin DB. Multiple Imputation for Nonresponse in Surveys. Wiley Series in Probability and Statistics. 1987. doi:10.1002/9780470316696. <!-- C015 | n=20 | cross_verified | retracted=no | abstract=no | vol/pages=no | authors=pool | sources=crossref+openalex | doi:10.1002/9780470316696 -->
21. Benjamini Y. The control of the false discovery rate in multiple testing under dependency. The Annals of Statistics. 2001;29(4):1165-1188. doi:10.1214/aos/1013699998. <!-- C004 | n=21 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1214/aos/1013699998 -->
22. Clopper CJ. THE USE OF CONFIDENCE OR FIDUCIAL LIMITS ILLUSTRATED IN THE CASE OF THE BINOMIAL. Biometrika. 1934;26(4):404. doi:10.1093/biomet/26.4.404. <!-- C005 | n=22 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/biomet/26.4.404 -->
23. Pressley JC, Patrick CH. Frailty Bias in Comorbidity Risk Adjustments of Community-Dwelling Elderly Populations. Journal of Clinical Epidemiology. 1999;52(8):753-760. doi:10.1016/s0895-4356(99)00056-6. <!-- C028 | n=23 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/s0895-4356(99)00056-6 -->
24. Burgess S, Zhou A. Genetic predictors of traits in elderly subjects: risk of survival bias and reverse causation. European Heart Journal. 2024;45(24):2155-2157. doi:10.1093/eurheartj/ehae295. <!-- C029 | n=24 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1093/eurheartj/ehae295 -->
25. Rosansky JA, Rosenberg H. A systematic review of reasons for abstinence from alcohol reported by lifelong abstainers, current abstainers and former problem-drinkers. Drug and Alcohol Review. 2020;39(7):960-974. doi:10.1111/dar.13119. <!-- C030 | n=25 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1111/dar.13119 -->
26. Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. Statistics in Medicine. 2002;21(11):1539-1558. doi:10.1002/sim.1186. <!-- C026 | n=26 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1002/sim.1186 -->
27. Spineli LM, Pandis N. Prediction interval in random-effects meta-analysis. American Journal of Orthodontics and Dentofacial Orthopedics. 2020;157(4):586-588. doi:10.1016/j.ajodo.2019.12.011. <!-- C027 | n=27 | cross_verified | retracted=no | abstract=no | vol/pages=yes | authors=pool+openalex | sources=crossref+openalex | doi:10.1016/j.ajodo.2019.12.011 -->

---

# Figure Legends

**Figure 1. System architecture of 慧眼.**

慧眼 integrates three layers — a deterministic rule engine, a knowledge-graph retrieval module (LightRAG), and an LLM arbiter — to produce explainable risk-graded reports for 暴露组（代谢-营养-生活方式-环境） × 主要致盲眼病 interactions, with full traceability from output back to source evidence.

(**a**) End-to-end pipeline: User input → Entity normalization → Rule engine → Risk-guided LightRAG retrieval → Evidence compression → LLM arbiter → Structured report.

(**b**) Three-layer zoom-in: Rule layer (YAML config) + KG layer (LightRAG graph) + Arbiter layer (LLM). Shows traceability chain.

(**c**) Four output views: clinician card / patient handout / research table / policy brief. All from single inference pass.

Statistics: Rule layer: 21 deterministic rules in configs/rules.yaml; KG layer: LightRAG graph over evidence chunks; Arbiter layer: DeepSeek 主客户端 + DualLLMClient 第二客户端（未配置 GPT 端点）.

Abbreviations: LLM = large language model; KG = knowledge graph; YAML = YAML Ain't Markup Language; LightRAG = lightweight retrieval-augmented generation; GPT = generative pre-trained transformer.

---

**Figure 2. 慧眼 (v1.2) vs three LLM baselines on NHANES pairs, scored against the R11-corrected gold (5 seeds).**

Against the R11-corrected three-state gold (survey svyglm variance), the full 慧眼 system attains F1 = 0.522 (P 0.353 / R 1.000, deterministic across seeds), ahead of lightrag 0.392 ± 0.007, pure_llm 0.335 ± 0.010 and naive_rag 0.080 ± 0.110 (5 seeds each). Paired McNemar is significant against pure_llm (p = 0.0043–0.0118) and naive_rag (p = 0.00024–0.0129) but NOT against lightrag (p = 0.057–0.092). The precision of every method is low (0.10–0.35) because most predicted-positive pairs are uninformative under the three-state standard rather than contradicting it. The pre-expansion v1.1 ruleset (0.111 on the R5 gold) is not shown in this panel; see the internal-layer tables.

(**a**) F1 by method (5 seeds, mean ± SD); R11-corrected gold. Forest plot of per-seed F1 aggregated to mean ± SD per method. Order: full_system 0.522 (deterministic) > lightrag 0.392 > pure_llm 0.335 > naive_rag 0.080. The pre-expansion v1.1 ruleset is NOT plotted here: it was scored on the R5 gold, and its source row is not in this figure's source CSV. Any comparison against it must be made from the internal-layer tables, not from this panel.

Statistics: NHANES tested pairs; gold = three-state labels under survey svyglm variance after the R11 operationalisation corrections; 5 seeds per method; full_system is deterministic and all five runs are identical; Paired McNemar exact; * p<0.05; n.s. p>=0.057 (vs lightrag); v1.1 replay row is scored on the R5 gold and is not like-for-like with the R11-gold bars.

Abbreviations: F1 = F1 score; P = precision; R = recall; LLM = large language model; NHANES = National Health and Nutrition Examination Survey; R5/R11 = internal analysis revisions (gold-label versions); SD = standard deviation; n.s. = not significant.

---

**Figure 3. Rule-level evaluation under the R11 three-state protocol: precision, coverage and replication by evidence level.**

Under the pre-registered three-state standard, the declared-domain precision (replicated / (replicated + contradicted)) is 1.00 in both countries, but the conservative precision (replicated / all rule-relevant testable pairs) is 0.375 (NHANES, 95% CI 0.152-0.646) and 0.333 (KNHANES, 0.118-0.616) — the gap is the single largest lever on the headline number, which is why both are shown. Rule coverage P(testable | rule exists) is high: 0.889 NHANES / 0.882 KNHANES. Replication is concentrated entirely outside evidence level A: 0/1 for level A in BOTH countries, 4/13 for levels A+B, 6/19 and 5/16 overall. No rule was contradicted in either country.

(**a**) Dual precision, coverage, and replication by evidence level (both layers). Forest plot with one row per quantity, both countries shown as separate labelled rows. Rows: declared-domain precision (NHANES 1.00 [0.541,1.000]; KNHANES 1.00 [0.478,1.000]); conservative precision (0.375 [0.152,0.646]; 0.333 [0.118,0.616]); rule coverage (0.889; 0.882); replication rate at evidence level A (0/1 = 0.00 both); level A+B (4/13 = 0.308 both); all rules (NHANES 6/19 = 0.316; KNHANES 5/16 = 0.312). All are proportions on a 0-1 axis with exact binomial intervals.

Statistics: Unit = (exposure flag, outcome item) pair; rule-relevant pairs only; declared-domain precision = replicated / (replicated + contradicted); conservative = replicated / all rule-relevant testable pairs; coverage = P(testable | a rule exists), analysis_plan section 0.4 correction 17b; intervals are Clopper-Pearson exact; contradicted = 0 in both countries.

Abbreviations: CI = confidence interval; BHY = Benjamini-Hochberg-Yekutieli; FDR = false discovery rate; NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey.

---

**Figure S1. Demo case: 暴露组（代谢-营养-生活方式-环境） × 主要致盲眼病 risk evaluation.**

A worked demo case shows how 慧眼 integrates rule signals, retrieved evidence, and LLM arbitration into an explainable risk report — enabling clinicians to trace each component of the recommendation back to its source.

(**a**) Input. Compact summary card: Entity A (subtype + key flags) | Entity B (exposure + key flags) | Patient factors (tags). No fancy graphics — just clear metadata.

(**b**) Triggered rules. Horizontal bar chart: each rule triggered, with severity color and mechanism category label. Bars ordered by severity (H → M → L).

(**c**) Evidence pyramid. Pyramid: top = Level A (regulatory), bottom = Level E (mechanism). Each level shows retrieved chunk count + sample title.

(**d**) Traceability chain. Flow diagram showing how the LLM arbiter combined rule signals + top-k evidence chunks → final risk level. Each chunk numbered, source cited.

Statistics: Levels: A=regulatory, B=meta-analysis, C=original study, D=in vitro/animal, E=mechanism inference; Case selection: representative high-risk case from the internal validation set (intval-nhanes).

Abbreviations: OR = odds ratio; LLM = large language model; AMD = age-related macular degeneration; DR = diabetic retinopathy; IOP = intraocular pressure; CDR = cup-to-disc ratio.

---

**Figure S2. Step-by-step reasoning trace across the three architectural layers.**

慧眼's three-layer architecture produces a fully traceable reasoning chain — each transition from rule signal to KG path to LLM arbitration is logged, enabling post-hoc audit of every output.

(**a**) Trace flow for one case. Horizontal swim-lane diagram: 3 lanes (Rule / KG / LLM). Time flows left → right. Each node is a step with input + output + duration.

(**b**) Latency breakdown. Stacked horizontal bar: avg time per layer (rule / KG / LLM). Shows where the runtime cost sits (usually LLM).

(**c**) KG path diversity. Network graph: nodes = entity_a + entity_b + intermediate concepts; edges = extracted paths. Path thickness = retrieval frequency.

Statistics: Swim-lane colors correspond to architectural layers (per Figure 1); Durations are median across intval-nhanes cases (n 以 .executor/progress.json 为准); 第二客户端升档仅作用于最高严重度档位（DualLLMClient；未配置 GPT 端点）.

Abbreviations: KG = knowledge graph; LLM = large language model; LightRAG = lightweight retrieval-augmented generation; CI = confidence interval.

---

**Figure 4. Continuous (per-1-SD) dose-response for rule-relevant pairs, survey-weighted.**

Modelling exposures continuously reproduces the binary layer's pattern rather than overturning it. Serum cotinine per SD is unrelated to cataract (OR/SD 0.92, q=0.31) and to late AMD (1.08, q=0.53) in NHANES, so the smoking nulls are not created by dichotomising self-reported exposure. BMI x cataract, by contrast, is significant per SD in KNHANES (1.077, 95% CI 1.034-1.122, q=0.0014) and null in NHANES (1.030, q=0.71): with BMI >= 25 affecting roughly a third of the KNHANES sample, that rule's binary null partly reflects the pre-specified cut-point. Direction agreed with the rule in 19/24 NHANES and 9/10 KNHANES rule-relevant pairs.

(**a**) OR per 1 SD for rule-relevant pairs, NHANES and KNHANES. Forest plot, one row per (exposure, outcome) pair labelled with its layer, sorted by OR per SD within layer. Rows span the glycaemic pairs (highest OR/SD: HbA1c-retinopathy 1.96 NHANES / 1.98 KNHANES) down to the around-null behavioural pairs (serum cotinine-cataract 0.92, BMI-cataract 1.03 NHANES) and the opposite-direction lipid rows (total cholesterol -retinopathy 0.71 KNHANES). Rows with q<0.05 carry a significance marker.

Statistics: OR per 1 standard deviation, survey svyglm (strata/PSU), same adjustment set as the binary layer; rule-relevant pairs only; all of them are shown; * q<0.05 within the pre-registered confirmatory family; tautological pairs excluded; see analysis_plan section 18.2.

Abbreviations: SD = standard deviation; OR = odds ratio; CI = confidence interval; NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey.

---

**Figure 5. Power: minimum detectable OR (80%) versus observed OR for rule-relevant pairs.**

Most rule nulls are informative rather than underpowered. The median minimum detectable odds ratio at 80% power is 1.337 in NHANES and 1.159 in KNHANES, and 17 of the 30 rule-relevant pairs are classifiable as powered nulls — the design could have excluded a 2-fold association. The pairs that did replicate sit in the opposite corner (large observed OR, small detectable OR), i.e. they were both well powered AND large; no pair replicated on the strength of a small detectable effect alone. Design effects were derived per pair from the survey/model CI-width ratio (median 1.07 NHANES, 1.26 KNHANES), not assumed.

(**a**) Minimum detectable OR (80% power) vs observed OR. Scatter, both axes on a log scale, one point per rule-relevant pair (NHANES n=17, KNHANES n=13). x = minimum detectable OR at 80% power; y = observed OR. Points are coloured by layer and three-state label so the reader can see that replicated pairs cluster at high observed OR and low detectable OR while uninformative pairs cluster near OR = 1 across the whole detectable range. Reference lines at OR = 1.0, 1.5 and 2.0 on both axes, plus the y = x identity line: points below the identity line have an observed effect larger than the design needed. NHANES replicate count 6, KNHANES 5; no contradicted points exist to plot.

Statistics: rule-relevant pairs: NHANES n=17, KNHANES n=13; log-log axes; x = minimal OR detectable at 80% power (two-sided alpha=0.05); y = observed OR; grey lines at 1.0 / 1.5 / 2.0 and the identity line; points left of the 1.5x line were adequately powered to exclude a 1.5-fold association; design effect derived per pair from the survey/model CI-width ratio (median 1.07 / 1.26).

Abbreviations: OR = odds ratio; MDE = minimum detectable effect (here, the minimum detectable odds ratio at 80% power); NHANES = National Health and Nutrition Examination Survey; KNHANES = Korea National Health and Nutrition Examination Survey.

---

**Figure 6. Cross-cohort transportability of the literature-derived exposome rules across eight ageing cohorts.**

Only 6 of the 21 literature-derived rules can be tested in the eight ageing cohorts, and of those just two transport. r02 (hyperglycaemia → cataract) replicates in three of four testable cohorts (LASI OR 1.88, SHARE 1.75, CLHLS 3.59; CRELES 1.31, q=0.051). r20 (smoking → vision impairment) replicates in three of five with ALL five pointing the same way (HRS 1.61, ELSA 1.49, SHARE 1.09; KLoSA 1.10 and CLHLS 1.03 uninformative). By contrast r10 (smoking → cataract) does not transport and its direction reverses with region: risk-increasing in SHARE (1.11, q=0.0095) but significantly PROTECTIVE in CLHLS (0.748, q=0.0012), with ELSA (0.77) and CRELES (0.70) also protective. r12 (alcohol → cataract) is contradicted in CLHLS (0.809, q=0.018) and not replicated in SHARE.

(**a**) Three-state composition per rule across the cohorts that can test it. Stacked horizontal bar, one bar per testable rule, segmented by outcome state: replicated, uninformative, contradicted. Counts are the number of cohorts contributing that state. r02 = 3 replicated + 1 uninformative; r20 = 3 replicated + 2 uninformative; r10 = 1 replicated + 2 uninformative + 1 contradicted; r12 = 1 uninformative + 1 contradicted; r13 = 1 replicated + 1 uninformative; r11 = 1 uninformative. The uninformative segment is drawn as its own colour and is never merged into either other segment.

(**b**) Odds ratio per (rule, cohort) pair, coloured by outcome state. Forest plot, one row per pre-registered confirmatory pair (18 rows). Row label = "<state> · <rule> · <cohort>" so that the leading token both names the state and drives the row colour. x = odds ratio. Estimates span 0.702 (CRELES r10) to 3.589 (CLHLS r02). Intervals are cluster-robust by person; SHARE is pooled over five imputation replicates by Rubin's rules. Rows whose interval crosses 1 while the point estimate points away from the other cohorts (r10 in ELSA and CRELES, r12 in SHARE) are visible as such and must not be read as disagreement.

Statistics: Unit = pre-registered (rule, cohort) pair; 18 pairs across 6 rules and 7 cohorts; three states: replicated / uninformative / contradicted (R11 definition, analysis_plan section 19.7); transportable = replicated with q<0.05 in >=2 cohorts (pre-declared in section 19.7); 15 rules have no bar at all. Their missing requirements overlap, so the counts exceed 15: 7 need a blood assay, 5 need fundus imaging, 4 need geocoded exposure, 3 need a dietary index and 1 needs tonometry or optic-disc grading; forest intervals are cluster-robust by person; SHARE pooled over 5 imputations (Rubin); forest drawn on a log axis with the null line at OR = 1 (project-local renderer; see backend.renderer).

Abbreviations: OR = odds ratio; CI = confidence interval; BHY = Benjamini-Hochberg-Yekutieli; FDR = false discovery rate; AMD = age-related macular degeneration; SHARE = Survey of Health, Ageing and Retirement in Europe; HRS = Health and Retirement Study; ELSA = English Longitudinal Study of Ageing; KLoSA = Korean Longitudinal Study of Ageing; LASI = Longitudinal Ageing Study in India; MHAS = Mexican Health and Aging Study; CLHLS = Chinese Longitudinal Healthy Longevity Survey; CRELES = Costa Rican Study on Longevity and Healthy Ageing; IOP = intraocular pressure; CDR = cup-to-disc ratio; r01-r22 = pre-registered rule identifiers in configs/rules.yaml.

---


# 图例（中文）

> 中文图例与上方英文图例逐项对应。数字与英文版完全一致，由 `scripts/fill_chinese_legends.py` 在写入前自动比对，不一致则拒绝写入。

**图 1。慧眼系统架构。**
慧眼整合三层结构——确定性规则引擎、知识图谱检索模块（LightRAG）与 LLM 仲裁器——为
暴露组（代谢-营养-生活方式-环境）× 主要致盲眼病交互输出可解释的风险分级报告，
并保证从输出回溯至原始证据的完整可追溯性。
（**a**）端到端流程：用户输入 → 实体归一化 → 规则引擎 → 风险引导的 LightRAG 检索
→ 证据压缩 → LLM 仲裁 → 结构化报告。
（**b**）三层放大视图：规则层（YAML 配置）+ 知识图谱层（LightRAG 图）+ 仲裁层（LLM），展示可追溯链。
（**c**）四种输出视图：临床医生卡片／患者手册／研究表格／政策简报，均由单次推理生成。
统计说明：规则层含 configs/rules.yaml 中的 21 条确定性规则；知识图谱层为覆盖证据片段的
LightRAG 图；仲裁层为 DeepSeek 主客户端 + DualLLMClient 第二客户端（未配置 GPT 端点）。
缩写：LLM = 大语言模型；KG = 知识图谱；YAML = YAML Ain't Markup Language；
LightRAG = 轻量检索增强生成；GPT = 生成式预训练变换器。

---

**图 2。慧眼（v1.2）与三个 LLM 基线在 NHANES 配对上的比较（针对 R11 更正后的金标准，5 个随机种子）。**
在 R11 更正后的三态金标准下（survey svyglm 方差），完整慧眼系统的 F1 = 0.522
（精确率 0.353 / 召回率 1.000，跨种子完全一致），高于 lightrag 0.392 ± 0.007、
pure_llm 0.335 ± 0.010 与 naive_rag 0.080 ± 0.110（各方法 5 个种子）。
配对 McNemar 检验相对 pure_llm（p = 0.0043–0.0118）与 naive_rag（p = 0.00024–0.0129）
显著，但相对 lightrag **不显著**（p = 0.057–0.092）。所有方法的精确率都低（0.10–0.35），
原因是多数被预测为正的配对在三态标准下属于"无信息"而非"相反"。扩张前的 v1.1 规则集
在 R5 金标准上得 0.111；该柱按要求同时呈现，但处于不同的金标准上，图中已如此标注。
（**a**）各方法的 F1（5 个种子，均值 ± 标准差；R11 更正金标准）。森林图按方法汇总，
顺序为 full_system 0.522（确定性）> lightrag 0.392 > pure_llm 0.335 > naive_rag 0.080。
扩张前的 v1.1 规则集**未绘于本图**：其评分基于 R5 金标准，且该行不在本图的 source CSV 中；与它的比较须依据内部层表格，而非本面板。
统计说明：NHANES 已检验配对；金标准为 R11 操作化更正后、survey svyglm 方差下的三态标签；
每方法 5 个种子；full_system 为确定性，五次运行完全相同；配对 McNemar 精确检验；
\* p<0.05；n.s. p>=0.057（对比 lightrag）；v1.1 replay 行基于 R5 金标准，与 R11 金标准柱不可直接比较。
缩写：F1 = F1 分数；P = 精确率；R = 召回率；LLM = 大语言模型；
NHANES = 美国国家健康与营养调查；R5/R11 = 内部分析修订版本（金标准版本）；SD = 标准差；n.s. = 不显著。

---

**图 3。R11 三态协议下的规则层评价：按证据等级的精确率、覆盖度与复现率。**
在预注册的三态标准下，声明域精确率（replicated / (replicated + contradicted)）
在两国均为 1.00，而保守精确率（replicated / 全部可检验的规则相关配对）为
0.375（NHANES，95% CI 0.152–0.646）与 0.333（KNHANES，0.118–0.616）——
两者之差是headline数值最大的单一杠杆，因此必须并列呈现。规则覆盖度
P(可检验 | 规则存在) 很高：NHANES 0.889 / KNHANES 0.882。
复现完全集中在证据等级 A 之外：两国在等级 A 均为 0/1，等级 A+B 为 4/13，
总体分别为 6/19 与 5/16。两国均无规则被否证。
（**a**）双精确率、覆盖度与按证据等级的复现率（两层）。森林图每个数量一行，两国分列。
各行数值：声明域精确率（NHANES 1.00 [0.541,1.000]；KNHANES 1.00 [0.478,1.000]）；
保守精确率（0.375 [0.152,0.646]；0.333 [0.118,0.616]）；规则覆盖度（0.889；0.882）；
证据等级 A 的复现率（两国均 0/1 = 0.00）；等级 A+B（两国均 4/13 = 0.308）；
全部规则（NHANES 6/19 = 0.316；KNHANES 5/16 = 0.312）。均为 0–1 轴上的比例，
区间为精确二项区间。
统计说明：分析单元 = （暴露 flag，结局条目）配对，仅规则相关配对；
声明域精确率 = replicated / (replicated + contradicted)；保守精确率 =
replicated / 全部可检验的规则相关配对；覆盖度 = P(可检验 | 规则存在)，
见分析计划 §0.4 更正 17b；区间为 Clopper-Pearson 精确区间；两国 contradicted 均为 0。
缩写：CI = 置信区间；BHY = Benjamini-Hochberg-Yekutieli；FDR = 错误发现率；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。

---

**图 S1。演示案例：暴露组（代谢-营养-生活方式-环境）× 主要致盲眼病风险评估。**
一个完整工作案例，展示系统如何将输入转化为风险分级、可追溯的报告，
以及四个输出视图如何共用同一次推理。
（**a**）输入与实体归一化；（**b**）触发的规则及其证据；（**c**）知识图谱检索路径；
（**d**）LLM 仲裁后的风险分级报告与依据链。
统计说明：四视图由单次推理生成，报告字段可逐项回溯至规则、知识图谱路径与仲裁决策。
缩写：OR = 比值比；LLM = 大语言模型；AMD = 年龄相关性黄斑变性；
DR = 糖尿病视网膜病变；IOP = 眼压；CDR = 视杯视盘比。

---

**图 S2。贯穿三层架构的逐步推理轨迹。**
慧眼的三层架构产生完全可追溯的推理链——从规则信号到知识图谱路径再到 LLM 仲裁的
每一次转换都被记录，使任一输出均可事后审计。
（**a**）单个案例的轨迹流：横向泳道图，三条泳道（规则／知识图谱／LLM），
时间自左向右，每个节点为一步骤，含输入、输出与耗时。
（**b**）时延分解：横向堆叠条，显示三层各自的平均耗时，呈现运行成本所在（通常为 LLM）。
（**c**）知识图谱路径多样性：网络图，节点为两个实体与中间概念，边为抽取出的路径，
边宽表示检索频次。
统计说明：泳道配色对应三层架构（见图 1）；耗时为 intval-nhanes 案例的中位数
（n 以 .executor/progress.json 为准）；第二客户端升档仅作用于最高严重度档位
（DualLLMClient；未配置 GPT 端点）。
缩写：KG = 知识图谱；LLM = 大语言模型；LightRAG = 轻量检索增强生成；CI = 置信区间。

---

**图 4。规则相关配对的连续（每 1 个标准差）剂量反应，按调查加权。**
对可估计连续暴露的规则相关配对，展示每 1 个标准差增量对应的比值比，
以检验关联是否随暴露水平单调变化，而非仅在二分类切点上出现。
统计说明：按调查设计加权；每 1 SD；仅规则相关配对；
区间为基于设计的稳健区间。
缩写：SD = 标准差；OR = 比值比；CI = 置信区间；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。

---

**图 5。效能：最小可检出 OR（80%）与观测 OR 的对照，仅规则相关配对。**
多数规则零结果是**有信息量的**而非效能不足。80% 效能下最小可检出比值比的中位数为
NHANES 1.337、KNHANES 1.159，30 个规则相关配对中有 17 个可归类为**有检验力的零结果**
——该设计本可排除 2 倍关联。发生复现的配对位于相反的一角（观测 OR 大、可检出 OR 小），
即它们既有足够效能又效应量大；没有任何配对仅凭较小的可检出效应就实现复现。
设计效应由各配对 survey 与 model 的置信区间宽度之比逐对导出（中位数 NHANES 1.07、KNHANES 1.26），
而非假定。
（**a**）最小可检出 OR（80% 效能）与观测 OR 的散点，双轴均为对数，
每个规则相关配对一点（NHANES n=17，KNHANES n=13）。x = 80% 效能下的最小可检出 OR；
y = 观测 OR。点按层与三态标签着色，可看出复现的配对聚集于"高观测 OR、低可检出 OR"，
而"无信息"配对沿整个可检出范围聚集在 OR = 1 附近。参考线为两轴上的 OR = 1.0、1.5、2.0
以及 y = x 的 identity 线：**位于 identity 线下方者，其观测效应大于该设计所需**。
NHANES 复现 6 个、KNHANES 5 个；无被否证的配对可绘。
统计说明：规则相关配对 NHANES n=17、KNHANES n=13；双对数轴；
x = 80% 效能（双侧 α=0.05）下最小可检出 OR；y = 观测 OR；
灰线为 1.0 / 1.5 / 2.0 与 identity 线；位于 1.5x 线左侧者具备排除 1.5 倍关联的足够效能；
设计效应逐对由 survey/model 置信区间宽度之比导出（中位数 1.07 / 1.26）。
缩写：OR = 比值比；MDE = 最小可检出效应（此处为 80% 效能下的最小可检出比值比）；
NHANES = 美国国家健康与营养调查；KNHANES = 韩国国家健康与营养调查。

---

**图 6。文献衍生暴露组规则在八个老龄化队列中的跨队列可迁移性。**
21 条文献衍生规则中，仅 6 条可在八个老龄化队列中检验，而其中只有 2 条实现迁移。
r02（高血糖 → 白内障）在四个可检验队列中的三个复现（LASI OR 1.88、SHARE 1.75、
CLHLS 3.59；CRELES 1.31，q=0.051）。r20（吸烟 → 视力损害）在五个队列中的三个复现，
且**五个队列方向完全一致**（HRS 1.61、ELSA 1.49、SHARE 1.09；KLoSA 1.10 与 CLHLS 1.03 为无信息）。
相反，r10（吸烟 → 白内障）**未能迁移且方向随地区反转**：在 SHARE 为风险升高
（1.11，q=0.0095），而在 CLHLS 显著**保护**（0.748，q=0.0012），ELSA（0.77）与
CRELES（0.70）亦为保护向。r12（饮酒 → 白内障）在 CLHLS 被否证（0.809，q=0.018），
在 SHARE 未复现。
（**a**）按规则的三态构成，跨可检验队列。横向堆叠条，每条规则一个条，
按结局状态分段：replicated、uninformative、contradicted。计数为贡献该状态的队列数。
r02 = 3 复现 + 1 无信息；r20 = 3 复现 + 2 无信息；r10 = 1 复现 + 2 无信息 + 1 否证；
r12 = 1 无信息 + 1 否证；r13 = 1 复现 + 1 无信息；r11 = 1 无信息。
无信息段以独立颜色绘制，**绝不并入其他任一段**。
（**b**）每个（规则，队列）配对的比值比，按结局状态着色。森林图，每个预注册确认配对一行
（共 18 行）。行标签为"<状态> · <规则> · <队列>"，使首位词元既标明状态又决定行色。
x = 比值比。估计值范围自 0.702（CRELES r10）至 3.589（CLHLS r02）。
区间为按个体聚类的稳健区间；SHARE 按五个插补副本以 Rubin 规则合并。
区间跨 1 而点估计与其余队列方向相背者（ELSA 与 CRELES 的 r10、SHARE 的 r12）清楚可见，
**不得读作分歧**。
统计说明：分析单元 = 预注册（规则，队列）配对；18 对，涵盖 6 条规则与 7 个队列；
三种状态：replicated / uninformative / contradicted（R11 定义，分析计划 §19.7）；
transportable = 在 ≥2 个队列中 replicated 且 q<0.05（§19.7 预先声明）；
15 条规则完全没有条柱。其缺失需求相互重叠，故分项之和大于 15：7 条需血液指标、5 条需眼底影像、4 条需地理编码暴露、3 条需膳食指数、1 条需眼压或视盘分级
3 条需血液指标、2 条需膳食指数；森林图区间为按个体聚类稳健区间；SHARE 按 5 个插补以
Rubin 合并；森林图绘于对数轴并含 OR = 1 的空值线（项目内渲染器，见 backend.renderer）。
缩写：OR = 比值比；CI = 置信区间；BHY = Benjamini-Hochberg-Yekutieli；FDR = 错误发现率；
AMD = 年龄相关性黄斑变性；SHARE = 欧洲健康、老龄化与退休调查；
HRS = 美国健康与退休研究；ELSA = 英国老龄化纵向研究；KLoSA = 韩国老龄化纵向研究；
LASI = 印度老龄化纵向研究；MHAS = 墨西哥健康与老龄化研究；
CLHLS = 中国老年健康影响因素跟踪调查；CRELES = 哥斯达黎加长寿与健康老龄化研究；
IOP = 眼压；CDR = 视杯视盘比；r01–r22 = configs/rules.yaml 中的预注册规则编号。

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

# Table 1b

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
* **Frame coverage versus item non-response.** Where a variable is present, its missingness is genuine non-response — SHARE's smoking is 58.0% missing with the column present, while HRS's BMI is 100% missing because the frame carries no BMI column.
* **Age in CLHLS is a baseline value repeated across waves**, not a follow-up age: 92.74% of its participants have a single unique age across all their waves, so its mean is not comparable to the others and should not be read as an average age during follow-up. The frame defect is documented in `docs/GAP_ANALYSIS_20IF.md`.
* **Diabetes is self-reported** in every cohort, so its prevalence reflects diagnosis rates rather than disease prevalence — the mechanism the paper demonstrates with the NHANES comparison.
* **Cataract and vision impairment are absent from HRS, KLoSA and MHAS** in these frames, which is why the cohort layer tests only six rules: those cohorts cannot contribute a cataract or vision-impairment cell.
* The BMI cut-point is 25 kg/m² for the Asian cohorts and 30 kg/m² otherwise, fixed by the prevalence gate before the confirmatory analysis.

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

| dataset | pairs_tested | rule_pairs_tested | replicated | contradicted | uninformative | precision_rule | precision_rule_ci95 | precision_binary_uninf_as_fp | coverage | phase | methodology |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NHANES |  | 16 | 6 | 0 | 10 | 1.0 | [0.541, 1.0] | 0.375 | 0.889 | confirmatory_R5 | three-state gold + survey svyglm variance (plan §6; R5) + Clopper-Pearson CI |
| KNHANES |  | 15 | 5 | 0 | 10 | 1.0 | [0.478, 1.0] | 0.333 | 0.882 | confirmatory_R5 | three-state gold + survey svyglm variance (plan §6; R5) + Clopper-Pearson CI |
| CHARLS |  | 4 | 0 | 0 | 4 | n/a (0 informative) | [None, None] | 0.0 | 1.0 | confirmatory_R5 | point estimates + declared fallback (no PSU; plan §6); three-state gold, R5 |

---

# Table 4

| Dataset | Total pairs | Tested | Underpowered | Rule-relevant tested | Replicated | Contradicted | Uninformative | Not estimable |
|---|---|---|---|---|---|---|---|---|
| NHANES | 180 | 159 | 21 | 16 | 6 | 0 | 10 | 0 |
| KNHANES | 352 | 301 | 50 | 15 | 5 | 0 | 10 | 1 |
| CHARLS | 14 | 14 | 0 | 4 | 0 | 0 | 4 | 0 |

**On the "not estimable" column.** Tested plus underpowered does not equal the total for KNHANES (301 + 50 = 351 of 352), and the residual is shown here rather than absorbed into either column. One pair encountered a stratum in which the outcome was constant, so no odds ratio could be estimated; it is neither a powered test nor a power failure.

**On the two denominators.** The rule-relevant counts (NHANES 16, KNHANES 15) are those used under the pre-registered three-state standard. Other figures in this paper quote 17 and 16, or 19 and 16, because they count the extended v1.2 rule set. The difference is stated here so that the denominators are not confused with one another.

---

# Table 5

Random-effects pooling with REML τ², computed in Python/SciPy (no external meta-analysis package), so the estimator is stated explicitly.

**The prediction interval is computed with t on k−2 degrees of freedom, not the normal quantile** (Higgins, Thompson & Spiegelhalter 2009). An earlier version of this table used 1.96 throughout, which made every interval 2–3× too narrow: r02's became 0.30–12.63 rather than 0.84–4.57. **For the two-cohort rules (r12, r13) no prediction interval exists at all** — t on 0 degrees of freedom is undefined — and none is reported. The interval is the range in which a NEW cohort's true effect would be expected to fall.

| Rule | k | Pooled OR (95% CI) | I² | τ² | Q p | Prediction interval | Subgroup test |
|---|---|---|---|---|---|---|---|
| r02_hyperglycemia_x_cataract | 4 | 1.95 (1.32–2.88) | 90.5% | 0.1487 | <0.0001 | 0.30–12.63 | p 0.0110 |
| r10_smoking_x_cataract | 4 | 0.84 (0.67–1.05) | 91.0% | 0.0421 | <0.0001 | 0.30–2.31 | p 0.4513 |
| r11_smoking_x_amd_late | 1 | single cohort | — | — | — | — | not applicable |
| r12_alcohol_x_cataract | 2 | 0.89 (0.75–1.06) | 79.5% | 0.0120 | 0.0273 | **not computable (k<3)** | same test as Q p (see note) |
| r13_bmi_x_cataract | 2 | 1.13 (0.91–1.41) | 79.5% | 0.0205 | 0.0272 | **not computable (k<3)** | same test as Q p (see note) |
| r20_smoking_x_vi_mod_severe | 5 | 1.24 (1.03–1.48) | 93.8% | 0.0381 | <0.0001 | 0.62–2.46 | p <0.0001 |

**I² must be read alongside τ².** On the log-odds-ratio scale the fitted τ² corresponds to cross-cohort ratio differences of only about 1.2× to 2.1×. The high I² is driven by SHARE's very small standard error (its confidence intervals are an order of magnitude narrower than the other cohorts'), so using I² alone as a rejection criterion would partly be a sample-size penalty. Both are therefore reported.

**Note on the subgroup column.** The regional subgroups (Europe / Asia / Americas) were NOT pre-specified; they were constructed after the primary analysis and are reported as post hoc. Pooling within subgroup uses random-effects weights — an earlier version used fixed-effect weights, which at this level of heterogeneity made Europe 93% SHARE by weight and produced a spurious p < 0.0001 for r10; the corrected value is p = 0.45. For the two-cohort rules the subgroup test is not an independent test: with one cohort per group the between-group statistic is the same quantity as the overall Q (r12 both 0.027334; r13 both 0.027220).

**E-values** (minimum confounder strength that could explain the estimate away), computed after converting each odds ratio to a risk ratio, since cataract is not rare in these cohorts (unexposed risk 8.8%–21.1%):

* r10 smoking-cataract in CLHLS: 1.87 (CI bound 1.47)
* r10 smoking-cataract in SHARE: 1.43 (1.22)
* r12 alcohol-cataract in CLHLS: 1.66 (1.27)
* r02 diabetes-cataract in CLHLS: 4.51 (3.35)

**Leave-one-cohort-out (Supplementary S4) qualifies the r10 row.** Removing SHARE reduces I² from 91.0% to 0.0% and moves the pooled estimate to 0.747 (0.66–0.84), so r10's heterogeneity is driven by one cohort rather than distributed across them; the remaining three cohorts agree with each other and their pooled estimate excludes unity.

---

# Table 5b

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
k > 2 the Table 5 subgroup test is a post hoc regional contrast
with fewer degrees of freedom and is not the same null as a
cohort-level interaction; the two need not agree (r10: regional
p = 0.45, Q p = 2.6e-07).


## What this table is

Reviewers objected to the two-stage subgroup comparison on two grounds: at k = 2
the subgroup test and the heterogeneity test are the same number computed twice,
and pooling per-cohort estimates gives a cohort of 5,191 the same weight as one of
338,703. Both objections disappear if the cohorts are stacked and fitted once at
the level of the person with an exposure x cohort interaction.

Every person enters once, so cohort size sets its own weight, and the interaction
term asks the question directly. The two-stage comparator is the Cochran Q test of
between-cohort heterogeneity; for k > 2 it is not the same null as the post hoc
regional subgroup test in Table 5 (see the definitions below).

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

# Table 6

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
| CLHLS | r20_smoking_x_vi_mod_severe | 13115 | 0.1595 | 0.1394 | 1.2127 | 1.0267 | 0.8736 | 1.2066 | uninformative | False | underpowered_or_indeterminate |
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

# Table 7

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
