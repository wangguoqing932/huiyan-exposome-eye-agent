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
epidemiology, both through comorbidity-adjusted risk models [C028] and through
survivorship selection on the trait itself [C029]. Smokers die earlier, so among
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
pooled literature association is a weighted average over them [C018]. If the
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
category across cohorts [C030]; a protective association with drinking is the
expected direction when those who quit did so because they were unwell.

## Why the pooled estimate is the wrong summary here

Heterogeneity of this magnitude is not a nuisance to be absorbed. With I² of
90–94% across every multi-cohort rule [C026], the fixed- or random-effects
average estimates a quantity that no population in the analysis has, and the
confidence interval around it understates the uncertainty a new population
faces. The prediction interval is the appropriate summary because it answers the
question a clinician or a health service actually asks — what should we expect
here? — and in this layer **every prediction interval includes the null**:
r02 0.30–12.63, r10 0.30–2.31, r20 0.62–2.46 [C027]. Leave-one-cohort-out
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

Finally, the protocol's fourth validation phase — a blinded expert panel — was
not conducted. Its intended function, establishing that the system's outputs
agree with independent expert judgement, was partially replaced by two
non-human concordance checks: a four-index literature validation (PubMed, Web
of Science, Europe PMC and the Chinese-language CNKI index, spanning two
languages and distinct publication ecosystems, with concordant precision across
all four), and a synthetic effect-injection regression in which the statistical
pipeline recovered known planted effect sizes without false positives. Expert
agreement therefore remains untested, and the system should be understood as
validated against data and literature, not against clinical judgement.

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
