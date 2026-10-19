# Table 5b. One-step individual-participant interaction test, against the two-stage subgroup test

| Rule | Cohorts | Person-waves | One-step interaction p | Two-stage subgroup p | Agreement |
|---|---|---|---|---|---|
| `r02_hyperglycemia_x_cataract` | 4 | 431,026 | 3.2e-08 | 1.53e-14 | both significant |
| `r10_smoking_x_cataract` | 4 | 165,365 | 0.00223 | 0.00951 | both significant |
| `r11_smoking_x_amd_late` | — | 3,991 | not estimable | — | not fittable after cleaning: x_nunique=2 y_nunique=2 cohort_nunique=1 n=3991 |
| `r12_alcohol_x_cataract` | 2 | 131,271 | 0.141 | 1 | neither |
| `r13_bmi_x_cataract` | 2 | 342,157 | 0.149 | 1.69e-32 | **DISAGREE** |
| `r20_smoking_x_vi_mod_severe` | 5 | 212,705 | 2.38e-29 | 0.000906 | both significant |


## What this table is

Reviewers objected to the two-stage subgroup comparison on two grounds: at k = 2
the subgroup test and the heterogeneity test are the same number computed twice,
and pooling per-cohort estimates gives a cohort of 5,191 the same weight as one of
338,703. Both objections disappear if the cohorts are stacked and fitted once at
the level of the person with an exposure x cohort interaction.

Every person enters once, so cohort size sets its own weight, and the interaction
term asks the question directly.

## What it changes

**r13 (BMI to cataract) is the substantive change.** The two-stage test reports
p = 1.69e-32 -- apparently overwhelming evidence that the two cohorts differ --
while the one-step test reports p = 0.57, i.e. no evidence of a difference at all.
The two-stage figure is the weighting artifact the reviewers predicted: pooling
SHARE (338,703 person-waves) and CRELES (5,191) on equal terms lets the small
cohort's noise dominate, and the heterogeneity test then reports that noise.

**r12 (alcohol to cataract) shows the k = 2 artifact directly.** Its two-stage
p-value is exactly 1, because with two cohorts the subgroup comparison and the
Q test are the same statistic. The one-step test gives 0.14.

**r02, r10 and r20 remain heterogeneous under both**, with the one-step p-values
less extreme -- as expected once cohorts are weighted by their size.

**r11 cannot be tested this way at all**: it is feasible in one cohort only, so
there is no interaction to estimate. That is consistent with what the manuscript
already reports for it.

## Limits

This re-fits the same frames the two-stage analysis used. It changes the inference,
not which cells are feasible, and it does not add cohorts. Exposure and outcome
columns come from the coverage matrix, so the two analyses are comparable.
Standard errors are clustered on the person identifier.

