# Discussion

## Main finding

Huiyan, benchmarked as a complete deployable agent, ranked first on F1 against
three LLM/RAG baselines in both NHANES backend generations and in the independent
KNHANES survey, and returns source-linked, operable reports. It also edged past
its own deterministic rule layer on independent data (0.375 versus 0.360), which
is the comparison that matters if the claim is about the agent rather than about
rules. Three qualifications belong with that statement. The internal NHANES
matrix is development, not validation: all 6 of its replicated pairs are covered
by rules the revision touched, so it holds zero contamination-free positives and
its recall of 1.000 measures the revision. The external margin is precision, not
recall: agent and rule layer both recall 0.500, and the gate removes 2 of 23 false
positives. And when the 5 revised pairs are removed every method loses about two
thirds of its F1; the agent keeps the lead (0.211 versus 0.200, 0.122, 0.089 and
0.086) but at a level that no longer supports a deployment claim.
Its rules also did not transport: only 6 of 21 were testable in eight ageing
cohorts, and of the two that met the pre-registered criterion, neither interval
excluded unity. Together these change how agent validation should be reported.

## Where the performance comes from

The gain over LLM baselines is architectural, not scale. On the NHANES matrices
the deployable full agent scored 0.571 (80 pairs) and 0.522 (159 pairs, versus
rule layer 0.480); the ablation localises the gain: rule layer 0.522,
+negative-control gate 0.545, +evidence confirmation and arbiter 0.571. A
stronger commercial model as a standalone judge produced more, not fewer, false
positives, and swapping the arbiter itself for GLM-5.3-flash left every one of the
474 predictions unchanged: the arbiter decides 3 cells, the remaining 471 being
settled by the rule layer, the negative-control gate or the evidence-B+ gate. The
measured gain therefore belongs to the rule and gate layers, not to the language
model. On external data the same structure holds with a smaller amplitude: the
gate removes 2 of 23 false positives and loses no true positive, so precision
rises from 0.281 to 0.300 while recall stays at 0.500. That is a precision
instrument, not a recall instrument, and a system meant to decide which pairs
deserve review should be judged on both. Every output still resolves to a rule, a
KG path and a source chunk; that demonstrates operability, not clinical usability
or deployment.

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
Selective survival is plausible at CLHLS's mean age of 92.0 years [C028, C029],
but the meta-regression slope on mean age does not support it. Unmeasured
confounding is plausible: E-values are 1.87 (1.50) for CLHLS and 1.43 (1.23) for
SHARE. Genuine effect modification across cataract subtypes [C018] cannot be
excluded, as no cohort grades opacity. The design cannot distinguish these, and
we do not prefer one. The same caution applies to alcohol, where abstainers are
not a comparable exposure category [C030].

### The pooled estimate is the wrong summary

With I² of 79.5–93.8% across the multi-cohort rules [C026], the pooled average
estimates a quantity no population in the analysis has; the three computable
prediction intervals all include the null (r02 0.30–12.63, r10 0.30–2.31, r20
0.62–2.46) [C027]. Leave-one-out qualifies this: removing SHARE collapses I² to
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
validation: reporting standards such as TRIPOD+AI [C038] and DECIDE-AI [C039]
organise validation around estimated models, whereas a fixed-rule agent's
components are its rules. We therefore report rule-level transportability
alongside system F1, add a literature-index layer that is independent of the
cohort databases and of any single index, and note that the internal layers'
clean headline reflects fewer, narrower and correlated pairs — adding populations
adds disagreement, and a protocol that cannot represent it reports a clean
result.

## Limitations

Independence is tier-specific and the gap differs by metric: the development set
contributes no independent estimate (and, on the audit above, no
contamination-free positives either); internal-to-external change was 0.007 for
rule testability, 0.522 to 0.360 for the rule layer and 0.571 to 0.375 for the
agent, falling to 0.211 on the 296 revision-free pairs; the eight cohorts are
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
holds against general models and, narrowly, against the agent's own deterministic
rule layer (0.375 versus 0.360); the margin is precision and disappears when the
pairs that informed development are removed (0.211, still ahead of 0.200 and of
0.086-0.122 for the baselines), while the internal benchmark that produced its
best score contains no contamination-free positive. Its rules, moreover, did not
transport: of 21, six were testable in eight ageing cohorts, and on the
pre-registered criterion two passed while on a heterogeneity-aware post hoc
criterion none did. The lesson is not that the agent is weak; it is that an agent
can beat general LLMs and its own rules and still owe most of its external F1 to
pairs its development had already seen. Agent validation should therefore report
the rule layer and the full system separately, name the pairs that informed
development, and state which exposures were actually measured.
