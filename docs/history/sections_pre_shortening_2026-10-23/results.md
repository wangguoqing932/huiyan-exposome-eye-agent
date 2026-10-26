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

Because the rules themselves were distilled from published literature, the
literature layer is reported as a multi-index concordance audit rather than an
independent validation. Rule directions were assessed against three further
literature indexes beyond the source index — Web of Science Core Collection
(100 papers across 2 rules), Europe PMC (521 papers across 21 rule queries, 17
of which had informative pairs) and the Chinese-language CNKI index (8 rules) —
under the same two-step
extraction protocol. Index-level precision was concordant across all four
(PubMed 0.889, Web of Science 0.916, Europe PMC 0.922, CNKI 0.800). Reversals
were confined to single-paper cells — one Europe PMC paper contradicted the
Mediterranean-diet/AMD rule that 17/17 PubMed papers supported, and one
contradicted the PM2.5/AMD rule (2/3 concordant in Europe PMC) — except for
alcohol and cataract, which was reversed in both PubMed and the
Chinese-language CNKI index and independently reproduces the reverse-causation
pattern seen in the prospective data layer. The concordance establishes that
the audit finding is not an artifact of a single database or its ranking
algorithm; it cannot establish independence, because the rules were derived
from the same body of published work.

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
four testable cohorts** — LASI OR 1.88 (1.76–2.00), SHARE 1.75 (1.69–1.82), CLHLS
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

System performance was assessed in two generations, reported side by side. In
the primary generation (80 development-era pairs, local Qwen3.8-27B baselines),
against the R11-corrected gold, the full system attained F1 = 0.522 (P 0.353 /
R 1.000, deterministic), ahead of LightRAG 0.392 ± 0.007, pure LLM
0.335 ± 0.010 and naive RAG 0.080 ± 0.110 over five seeds (Figure 2); paired
McNemar was significant against pure LLM and naive RAG but not against LightRAG
(p = 0.057–0.092) — a comparison compromised by the LightRAG baseline then
running in degraded vector-only mode.

After two fairness fixes — the LightRAG baseline upgraded to full hybrid
knowledge-graph traversal, and all baselines re-run on a stronger commercial
backend (GLM-5.3-flash) over the expanded 159-pair matrix — the ordering held
and the LightRAG comparison resolved: the full system attained F1 = 0.480
(P 0.316 / R 1.000), ahead of LightRAG 0.186 ± 0.006, pure LLM 0.178 ± 0.015
and naive RAG 0.069 ± 0.086, with paired McNemar significant against all three
baselines (LightRAG p = 3×10⁻¹¹ to 9×10⁻¹⁰; pure LLM p = 8×10⁻¹⁹ to 6×10⁻²⁴;
naive RAG p = 0.006–0.012). The stronger commercial LLM did not close the gap:
as a standalone judge it produced more, not fewer, false positives (precision
0.10 against the expanded gold). The precision of every method is low (0.07–0.35)
because most predicted-positive pairs are uninformative rather than contradicted
— the same denominator effect seen at rule level. Figure S1 shows one worked
case end to end and Figure S2 traces it through the three architectural layers.

