# Table 5b. One-step individual-participant interaction test, against two-stage between-cohort heterogeneity (Cochran Q)

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

