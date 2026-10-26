# Introduction

Visual loss in later life is predominantly chronic rather than acute. Global
estimates of vision impairment remain methodologically contested [C016], and the
leading contributors in ageing populations are cataract, glaucoma, age-related
macular degeneration and diabetic retinopathy [C021-C023]. Each has been the subject of prevalence projection. Glaucoma, late AMD and diabetic retinopathy can cause irreversible loss once advanced, whereas cataract is surgically treatable but access-dependent; the potential value of exposome risk stratification lies in identifying people whose modifiable exposures place them at risk before vision is lost.

That framing, that risk is carried by a set of modifiable exposures rather than
by a single factor, is the exposome concept [C020]. In ophthalmology the relevant
exposome spans metabolic state, nutrition, lifestyle and environment:
hyperglycaemia, smoking, alcohol, adiposity and particulate or ultraviolet
exposure have each been linked to one or more major eye diseases, with smoking
and cataract among the better documented associations [C018]. The literature is
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
