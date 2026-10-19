# Methods

## Reporting and study design

This is a retrospective, multi-cohort evaluation of a rule-based clinical
decision-support system for ocular risk in older adults. The observational cohort
analyses follow STROBE [C003], and the cross-cohort synthesis follows standard
meta-analytic reporting (random-effects pooling with REML tau-squared, Cochran's
Q, I-squared and prediction intervals). **TRIPOD+AI [C001] and DECIDE-AI [C002]
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
Survey [C014], one wave of the China Health and Retirement Longitudinal Study
[C013], and — new in this report — eight population-based ageing cohorts on
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
and Retirement in Europe (SHARE) [C006], the US Health and Retirement Study
(HRS) [C007], the English Longitudinal Study of Ageing (ELSA) [C008], the Korean
Longitudinal Study of Ageing (KLoSA), the Longitudinal Ageing Study in India
(LASI) [C009], the Mexican Health and Aging Study (MHAS) [C010], the Chinese
Longitudinal Healthy Longevity Survey (CLHLS), and the Costa Rican Study on
Longevity and Healthy Ageing (CRELES). CLHLS and CRELES are cited to their
**data deposits** [C031, C032, C033]. An earlier version of this section claimed
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
was fitted on each and the estimates combined by Rubin's rules [C015]. The
prevalence gate and all descriptive statistics use the first replicate only, so
that an imputation replicate is never counted as an independent person.

Multiplicity was controlled by the Benjamini–Yekutieli procedure [C004], which
remains valid under arbitrary dependence, over two pre-registered families: a
confirmatory family containing the rule-relevant pairs and an exploratory family
containing every exposure–outcome pair actually tested in that cohort. Exact
binomial intervals for proportions use the Clopper–Pearson method [C005].

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
