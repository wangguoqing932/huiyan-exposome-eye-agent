# Table 5. Between-cohort heterogeneity and prediction intervals (cohort external-validation layer)

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
