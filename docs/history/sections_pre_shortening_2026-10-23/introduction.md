# Introduction

Visual loss in later life is common, and its dominant causes are chronic rather
than acute. Global estimates of the magnitude and causes of vision impairment
are compiled periodically and remain the subject of methodological debate
[C016], and among the leading contributors in ageing populations are cataract,
glaucoma, age-related macular degeneration and diabetic retinopathy. Each of the
retinal and optic-nerve causes has been the subject of global prevalence
projection — glaucoma to 2040 [C023], age-related macular degeneration with its
associated disability burden [C021] — and diabetic retinopathy in particular is
a leading cause of vision impairment and blindness in working-age adults, with
burden estimates now extending to the largest middle-income populations [C022].
Because these conditions are largely irreversible once advanced, the clinical
value of screening lies in identifying people whose modifiable exposures place
them at risk before vision is lost.

That framing — that a person's risk is carried by a set of modifiable
exposures rather than by a single factor — is the exposome concept [C020]. In
ophthalmology the relevant exposome spans metabolic state, nutrition, lifestyle
and environment: hyperglycaemia, smoking, alcohol intake, adiposity, and
particulate or ultraviolet exposure have each been linked to one or more of the
major eye diseases, with smoking and cataract among the better documented
associations [C018]. The literature is nevertheless uneven. Associations are
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
