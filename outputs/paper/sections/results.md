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
LLM/RAG baselines on F1 wherever it was run end to end, and also beat its own
deterministic rule layer externally by a narrow margin (KNHANES 0.375 versus
0.360; baselines 0.176, 0.173 and 0.120); the internal NHANES matrix contained no
replicated pair untouched by the post-confirmatory rule revision, so it contributes
no out-of-sample estimate; on the 296 KNHANES pairs untouched by that revision
every method fell sharply and the agent kept the lead (0.211 versus 0.200, 0.122,
0.089 and 0.086); a worked case resolved every output to a rule, KG path and
source chunk (Supplementary Figures S1-S2); in the cohort
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

At the system level the internal NHANES matrix is reported as a development
description, not as performance. The 134-pair development set contributed no
independent estimate, and the 80-pair matrix was itself used in development: the
rule set was revised after the first confirmatory run (r02–r04 exposure coverage
altered, r22 added; Methods records this as test-set fitting). The audit is
decisive: of the 159-pair matrix's 6 replicated pairs, all 6 are covered by a
rule that the revision touched, leaving zero contamination-free positives. Its recall of 1.000 therefore measures the revision.
For completeness the numbers are: deployable full agent F1 = 0.571 (P 0.400 /
R 1.000) on the 80 pairs (Qwen3.8-27B baselines, R11-corrected gold), ahead of
LightRAG 0.392 ± 0.007, pure LLM 0.335 ± 0.010 and naive RAG 0.080 ± 0.110 over
five seeds; under the earlier gold the pre-revision v1.1 set scored 0.111
(P 0.091 / R 0.143). Accuracy
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
makes this the only agent-level external estimate, and it is also the only one
that can be split into pairs the rule revision touched and pairs it did not.
On all 301 pairs the agent reached F1 = 0.375 (P 0.300 / R 0.500), against its own
deterministic rule layer at 0.360 (P 0.281 / R 0.500) and the three baselines at
0.176 (LightRAG), 0.173 (pure LLM) and 0.120 (naive RAG; Figure 2a). Accuracy McNemar was significant against all three baselines before and after
Benjamini-Hochberg correction over the 15 tests per matrix (q < 0.001 in every
case), but that test is dominated by the 277 uninformative pairs, on which
abstention earns credit; F1 is the declared metric and accuracy is secondary.

The revision-free subset is the harsher test. Removing the 5 pairs whose rules
were modified after the first confirmatory run leaves 296 pairs carrying 13
replicated, 6 contradicted and 277 uninformative outcomes: the agent scores 0.211
(P 0.160 / R 0.308), the rule layer 0.200 (P 0.148 / R 0.308), the pure LLM 0.122,
LightRAG 0.089 and naive RAG 0.086. The ordering survives; the level does not.
Every method loses roughly two thirds of its F1 on the untouched pairs, because
the untouched pairs are the ones where no rule fires (9 of 13 replicated pairs
have no rule at all) and where the evidence store has least to say. The three-state decomposition makes the trade explicit: agent and rule layer
both flag 50% of replicated and 16.7% of contradicted pairs, and differ only on
uninformative pairs (7.2% versus 7.9%). The internal-to-external comparison therefore depends on the metric: rule
testability 16/18 to 15/17, pre-registered coverage 0.131 to 0.095,
declared-domain precision 1.00 in both, and system F1 0.571 (development, with
zero contamination-free positives) to 0.375 (external, 0.211 contamination-free).

## Cross-cohort transportability across eight ageing cohorts

The rules were re-evaluated in eight population-based ageing cohorts on three
continents from raw source files with codebook-verified operationalisation
(598,386 person-wave records from 285,878 participants), under a layer
pre-registered before it was run (analysis plan section 19). Only 6 of 21 rules
were testable; 15 required measurements absent in every cohort (five fundus
imaging, one tonometry or disc grading, three geocoded exposure, three blood
assays, two dietary indices, one lipid panel). Across 18 rule × cohort pairs
(Figure 6): 8 replicated, 8 uninformative, 2 contradicted.

The same 18 cells were then put to the agent, which makes this the second
external surface on which the full system is evaluated and the only one that asks
about transport rather than association. The question is whether a rule replicates
in a named population. Assuming transport — the rule layer's only available
answer, since it carries no cohort information — flags all 18 cells: recall 1.00
on the 8 replicated cells, but both contradicted and all 8 uninformative cells are
flagged too (precision 0.444, F1 0.615). The population-conditioned evidence gate
(query = exposure + outcome + country, requiring a chunk that names that
population) found such evidence for none of the 18 cells and flagged none: recall
0, precision undefined, accuracy 0.556 from abstention alone. A plain LLM asked
the same question in one sentence did better than either (F1 0.667; 6 of 8
replicated cells flagged, 4 false positives), but it endorsed 1 of the 2
contradicted cells — CLHLS smoking × cataract — which is exactly the failure the
rule layer was designed to prevent. The agent's evidence machinery is a
within-cohort retrieval tool and does not become a transport predictor by being
pointed at a population name.

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
