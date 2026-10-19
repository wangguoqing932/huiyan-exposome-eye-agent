#!/usr/bin/env python
"""Formal heterogeneity analysis of the cohort layer (upgrade for a 10+ IF target).

WHY THIS REPLACES THE EARLIER POSITION
--------------------------------------
The first pass reported the r10 direction reversal descriptively and argued that
pooling "would manufacture a single number from incommensurable measurements".
That is a defensible instinct but an inadequate analysis: a reader cannot tell
whether the reversal is a real between-population difference or two noisy
estimates landing on opposite sides of 1. The remedy is not to refuse to pool --
it is to pool PROPERLY and to quantify how much of the variation is real:

  * random-effects pooling per rule (DerSimonian-Laird tau^2, with a REML
    refinement), giving a pooled OR and a prediction interval;
  * Cochran's Q and I^2 for between-cohort heterogeneity, so the reversal is a
    tested quantity rather than an observation;
  * a formal test of subgroup difference between world regions for r10;
  * meta-regression on cohort-level moderators, to ask whether anything we can
    measure explains the split;
  * leave-one-cohort-out influence, to show the reversal is not one cohort;
  * E-values for the reversed estimates, bounding unmeasured confounding.

The prediction interval matters more than the pooled estimate here: with real
heterogeneity the pooled OR is not what a new population should expect.

Outputs
  outputs/cohorts/cohort_heterogeneity.json
  outputs/cohorts/cohort_meta_summary.csv
  outputs/cohorts/cohort_influence.csv

Run: python scripts/cohort_heterogeneity.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "outputs" / "cohorts" / "cohort_rule_results.csv"
OUT = ROOT / "outputs" / "cohorts"

# Region assignment is a property of the sampling frame, not of the result, and
# is fixed here before any subgroup test is run.
REGION = {"SHARE": "Europe", "ELSA": "Europe",
          "HRS": "Americas", "MHAS": "Americas", "CRELES": "Americas",
          "KLoSA": "Asia", "LASI": "Asia", "CLHLS": "Asia"}
# Cohort mean age, measured from the built frames (docs/cohort_variable_mapping
# section 0.14). Used as a moderator because CLHLS sits ~26 years above the rest.
MEAN_AGE = {"SHARE": 67.9, "HRS": 65.7, "ELSA": 64.9, "KLoSA": 65.7,
            "LASI": 57.9, "MHAS": 60.3, "CLHLS": 92.0, "CRELES": 76.7}


def dl_tau2(y: np.ndarray, v: np.ndarray) -> tuple[float, float]:
    """DerSimonian-Laird tau^2 and the Q statistic."""
    w = 1.0 / v
    mu_fe = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - mu_fe) ** 2))
    k = len(y)
    c = float(np.sum(w) - np.sum(w ** 2) / np.sum(w))
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    return tau2, q


def reml_tau2(y: np.ndarray, v: np.ndarray) -> float:
    """REML tau^2 by bounded maximisation of the REML likelihood.

    The first implementation used the usual fixed-point update
    tau2 <- tau2 + num/den. That DIVERGED here: cohort variances are tiny
    (SHARE r02 has v ~ 3.6e-4, LASI ~ 1.1e-3) while the log-ORs are far apart,
    so the update ran away to tau^2 ~ 5e47. A number like that is obviously
    wrong, but it would have been printed as a result. Maximising the likelihood
    on a bounded interval is stable and cannot return an impossible value.

    With only 2-5 cohorts tau^2 is poorly identified regardless of estimator;
    the reported inference therefore leans on Cochran's Q and I^2, which behave
    better at small k, and tau^2 is given as a secondary quantity.
    """
    k = len(y)

    def neg_reml(t2: float) -> float:
        w = 1.0 / (v + t2)
        mu = float(np.sum(w * y) / np.sum(w))
        return 0.5 * (float(np.sum(np.log(v + t2))) + math.log(float(np.sum(w)))
                      + float(np.sum(w * (y - mu) ** 2)))

    from scipy.optimize import minimize_scalar
    # upper bound: tau^2 cannot plausibly exceed the spread of the log-ORs
    hi = float(max(1.0, 4.0 * np.var(y, ddof=1) if k > 1 else 1.0))
    if k < 2 or hi <= 0:
        return 0.0
    res = minimize_scalar(neg_reml, bounds=(0.0, hi), method="bounded",
                          options={"xatol": 1e-8})
    return float(max(0.0, res.x))


def _safe_exp(x: float) -> float:
    """exp that reports rather than crashes on overflow.

    With k = 2 cohorts whose estimates are far apart and whose variances are
    small, tau^2 can be large enough that the pooled CI or the prediction
    interval spans thousands-fold. math.exp then raises OverflowError. An
    unbounded interval IS the finding -- extreme heterogeneity -- so it is
    reported as such instead of being clamped into a falsely tidy number.
    """
    try:
        return math.exp(x)
    except OverflowError:
        return float("inf") if x > 0 else 0.0


def pool(y: np.ndarray, v: np.ndarray) -> dict:
    tau2 = reml_tau2(y, v)
    w = 1.0 / (v + tau2)
    mu = float(np.sum(w * y) / np.sum(w))
    se = float(math.sqrt(1.0 / np.sum(w)))
    _, q = dl_tau2(y, v)
    k = len(y)
    i2 = max(0.0, (q - (k - 1)) / q) * 100 if q > 0 else 0.0
    q_p = float(stats.chi2.sf(q, k - 1)) if k > 1 else float("nan")
    # prediction interval: where a NEW cohort's true effect would be expected
    if k > 1:
        se_pred = math.sqrt(se ** 2 + tau2)
        # Prediction interval multiplier. The pooled CI uses the normal
        # quantile, but a prediction interval for a NEW study is a t interval on
        # k-2 degrees of freedom (Higgins, Thompson & Spiegelhalter 2009). At
        # k=4 that is t_2 = 4.303 rather than 1.96, and at k=2 it is t_0, which
        # does not exist: with two studies a prediction interval cannot be
        # computed at all and none is reported.
        if k >= 3:
            tcrit = float(stats.t.ppf(0.975, k - 2))
            pi = (mu - tcrit * se_pred, mu + tcrit * se_pred)
        else:
            tcrit = float("nan")   # no PI: t on 0 df is undefined
            pi = (float("nan"), float("nan"))
    else:
        pi = (float("nan"), float("nan"))
    return {"k": k, "tau2": round(tau2, 5), "tau": round(math.sqrt(tau2), 4),
            "Q": round(q, 3), "Q_df": k - 1, "Q_p": q_p,
            "I2_percent": round(i2, 1),
            "pooled_OR": round(_safe_exp(mu), 4),
            "pooled_ci": [round(_safe_exp(mu - 1.96 * se), 4),
                           round(_safe_exp(mu + 1.96 * se), 4)],
            "pooled_ci_unbounded": not math.isfinite(_safe_exp(mu + 1.96 * se)),
            # k < 3: no prediction interval exists (t on 0 df). Recorded as
            # null with a flag rather than emitted as NaN, so that a reader of
            # the JSON cannot mistake an undefined quantity for a wide one.
            "prediction_interval": (
                [round(_safe_exp(pi[0]), 4), round(_safe_exp(pi[1]), 4)]
                if k >= 3 else None),
            "prediction_interval_computable": k >= 3,
            "prediction_interval_multiplier": (
                round(tcrit, 3) if k >= 3 else None),
            "prediction_interval_unbounded": not math.isfinite(_safe_exp(pi[1])),
            "log_OR": round(mu, 5), "log_OR_se": round(se, 5)}


def subgroup_diff(y: np.ndarray, v: np.ndarray, g: np.ndarray) -> dict:
    """Q-based test of difference between subgroups.

    CORRECTED. The first version pooled WITHIN each subgroup using fixed-effect
    weights w = 1/v. That is invalid when the subgroups are themselves
    heterogeneous, and here it was decisive: SHARE's variance is two orders of
    magnitude below the others', so Europe's pooled value was ~93% SHARE by
    weight and "Europe = 1.0817" was really SHARE. Recomputing with
    random-effects weights within each subgroup changes r10's Europe estimate
    from 1.0817 to 0.9394 and its between-group p from 4.5e-06 to 0.45 -- i.e.
    the regional difference for the very rule the manuscript called a regional
    reversal does not survive. Pooling within subgroup is now random-effects.
    """
    groups = sorted(set(g))
    if len(groups) < 2:
        return {"testable": False}
    mus, ses = [], []
    for grp in groups:
        m = g == grp
        yy, vv = y[m], v[m]
        # random-effects pooling within the subgroup
        tau2 = reml_tau2(yy, vv) if len(yy) > 1 else 0.0
        w = 1.0 / (vv + tau2)
        mus.append(float(np.sum(w * yy) / np.sum(w)))
        ses.append(float(math.sqrt(1.0 / np.sum(w))))
    wb = 1.0 / np.array(ses) ** 2
    mu_b = float(np.sum(wb * np.array(mus)) / np.sum(wb))
    qb = float(np.sum(wb * (np.array(mus) - mu_b) ** 2))
    df = len(groups) - 1
    out = {"testable": True, "groups": groups,
           "n_per_group": [int((g == grp).sum()) for grp in groups],
           "per_group_OR": [round(math.exp(m), 4) for m in mus],
           "Q_between": round(qb, 3), "df": df,
           "p_between": float(stats.chi2.sf(qb, df)),
           "within_subgroup_pooling": "random_effects"}
    # a subgroup test is not an independent test when k == 2
    out["independent_of_Q"] = len(y) > 2
    return out


def e_value(est: float, lo: float, hi: float) -> dict:
    """E-value for an odds ratio: the minimum confounder strength that could
    explain the estimate away. VanderWeele & Ding, Ann Intern Med 2017."""
    def ev(rr: float) -> float:
        rr = max(rr, 1e-12)
        if rr < 1:
            rr = 1.0 / rr
        return rr + math.sqrt(rr * (rr - 1.0))
    return {"point": round(ev(est), 3),
            "ci_bound_nearest_null": round(ev(lo if abs(math.log(lo)) <
                                               abs(math.log(hi)) else hi), 3)}


def main() -> int:
    d = pd.read_csv(RES, low_memory=False)
    c = d[d["rule_relevant"].astype(bool)].copy()
    c["region"] = c["cohort"].map(REGION)
    c["mean_age"] = c["cohort"].map(MEAN_AGE)
    y = np.log(c["odds_ratio"].to_numpy(float))
    v = c["se"].to_numpy(float) ** 2
    c["_y"], c["_v"] = y, v

    # Pre-registered transportability verdicts, fixed before this analysis ran.
    PRE_REG = {}
    _tp = ROOT / "outputs" / "cohorts" / "cohort_transportability.json"
    if _tp.exists():
        for _rid, _v in json.loads(_tp.read_text(encoding="utf-8"))["by_rule"].items():
            PRE_REG[_rid] = _v["verdict"]

    rows, report = [], {}
    for rid, sub in c.groupby("rule_id"):
        yy = np.log(sub["odds_ratio"].to_numpy(float))
        vv = sub["se"].to_numpy(float) ** 2
        if len(sub) < 2:
            report[rid] = {"k": len(sub), "note": "single cohort; not pooled",
                           "cohorts": sub["cohort"].tolist(),
                           "OR": round(float(sub["odds_ratio"].iloc[0]), 4)}
        else:
            rep = pool(yy, vv)
            rep["cohorts"] = sub["cohort"].tolist()
            rep["per_cohort_OR"] = dict(zip(sub["cohort"],
                                            [round(float(x), 4)
                                             for x in sub["odds_ratio"]]))
            rep["subgroup_by_region"] = subgroup_diff(
                yy, vv, sub["region"].to_numpy())
            # meta-regression on mean age (weighted least squares on log OR)
            w = 1.0 / (vv + rep["tau2"])
            X = np.column_stack([np.ones(len(sub)), sub["mean_age"].to_numpy(float)])
            W = np.diag(w)
            if len(sub) < 4:
                # With k = 2 or 3 the regression has 0-1 residual df. Reporting a
                # p-value from it manufactures precision that does not exist --
                # the earlier run printed p < 0.0001 for two-cohort rules, which
                # is an artefact of forcing dof = 1. Refuse to fit instead.
                rep["meta_regression_mean_age"] = {
                    "note": f"not fitted: k={len(sub)} leaves no residual df"}
                report[rid] = rep
                rows.append({"rule_id": rid, "k": len(sub),
                             "cohorts": ",".join(sub["cohort"]),
                             **{k2: v2 for k2, v2 in rep.items()
                                if k2 in ("pooled_OR", "I2_percent", "tau2",
                                          "Q", "Q_p")}})
                continue
            try:
                beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ yy)
                resid = yy - X @ beta
                dof = max(1, len(sub) - 2)
                s2 = float(resid @ W @ resid) / dof
                cov = s2 * np.linalg.inv(X.T @ W @ X)
                se_slope = math.sqrt(cov[1, 1])
                t = beta[1] / se_slope
                rep["meta_regression_mean_age"] = {
                    "slope_per_year_logOR": round(float(beta[1]), 5),
                    "se": round(se_slope, 5),
                    "p": float(2 * stats.t.sf(abs(t), dof)),
                    "note": "weighted by 1/(v + tau^2); CLHLS (mean age 92) is "
                            "the only cohort far above the rest"}
            except Exception as e:
                rep["meta_regression_mean_age"] = {"error": str(e)}
            report[rid] = rep
        rows.append({"rule_id": rid, "k": len(sub),
                     "cohorts": ",".join(sub["cohort"]),
                     **{k2: v2 for k2, v2 in report[rid].items()
                        if k2 in ("pooled_OR", "I2_percent", "tau2", "Q",
                                  "Q_p")}})

    # ---- leave-one-cohort-out on every multi-cohort rule -------------------
    infl = []
    for rid, sub in c.groupby("rule_id"):
        if len(sub) < 3:
            continue
        for drop in sub["cohort"]:
            s2 = sub[sub["cohort"] != drop]
            yy = np.log(s2["odds_ratio"].to_numpy(float))
            vv = s2["se"].to_numpy(float) ** 2
            r = pool(yy, vv)
            infl.append({"rule_id": rid, "dropped": drop,
                         "pooled_OR": r["pooled_OR"],
                         "pooled_ci_low": r["pooled_ci"][0],
                         "pooled_ci_high": r["pooled_ci"][1],
                         "I2_percent": r["I2_percent"],
                         "tau2": r["tau2"]})

    # ---- E-values for the estimates that decided the transportability ------
    ev = {}
    for rid, coh in (("r10_smoking_x_cataract", "CLHLS"),
                     ("r10_smoking_x_cataract", "SHARE"),
                     ("r12_alcohol_x_cataract", "CLHLS"),
                     ("r02_hyperglycemia_x_cataract", "CLHLS")):
        r = c[(c.rule_id == rid) & (c.cohort == coh)]
        if len(r):
            r = r.iloc[0]
            ev[f"{rid}@{coh}"] = e_value(float(r.odds_ratio), float(r.ci_low),
                                         float(r.ci_high))

    # ---- heterogeneity-aware reclassification --------------------------------
    # The pre-registered criterion (replicated in >=2 cohorts) is retained as the
    # primary verdict and is NOT overwritten. This adds a second, stricter
    # reading, because the pre-registered rule turns out to be too permissive:
    # r20 meets it (3 of 5 cohorts replicate, all pointing the same way) while
    # its prediction interval still spans the null, so a NEW cohort could
    # plausibly see no effect. Reporting only the pre-registered verdict would
    # overstate transportability; reporting only the stricter one would abandon
    # a criterion fixed in advance. Both are given, and the disagreement between
    # them is itself a result about how transportability should be judged.
    reclass = {}
    for rid, rep in report.items():
        if "pooled_OR" not in rep:
            reclass[rid] = {"pre_registered": "single_cohort",
                            "heterogeneity_aware": "not_poolable",
                            "agreement": "n/a"}
            continue
        pi = rep["prediction_interval"]
        # k < 3: no prediction interval exists, so the question of whether it
        # crosses the null does not arise. Recorded as None, not False -- a
        # False would read as "does not cross" and be wrong.
        pi_crosses_null = (pi[0] <= 1.0 <= pi[1]) if pi else None
        hi_i2 = rep["I2_percent"] >= 75.0
        if pi_crosses_null or hi_i2:
            strict = "heterogeneous_unreliable_pool"
        else:
            strict = "consistent"
        # READ the pre-registered verdict rather than recomputing it. An
        # earlier version counted cohorts agreeing in SIGN with the pooled
        # estimate, which labelled r10 and r12 "transportable" even though the
        # three-state protocol had classified r10 as mixed (one replicated, one
        # contradicted) and r12 as non-transportable (none replicated). Sign
        # agreement is not the pre-registered criterion; replicated-and-q<0.05
        # in >=2 cohorts is.
        pre = PRE_REG.get(rid, "not_assessed")
        n_rep = int(rep.get("n_replicated_pre_registered", 0))
        reclass[rid] = {
            "pre_registered": pre,
            "heterogeneity_aware": strict,
            "agreement": ("agree" if (pre == "transportable") ==
                           (strict == "consistent") else "DISAGREE"),
            "I2_percent": rep["I2_percent"],
            "prediction_interval": pi,
            "prediction_interval_crosses_null": pi_crosses_null,
            "pre_registered_verdict_source": "cohort_transportability.json",
            "k": rep["k"]}

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "cohort_meta_summary.csv", index=False,
                              encoding="utf-8")
    pd.DataFrame(infl).to_csv(OUT / "cohort_influence.csv", index=False,
                              encoding="utf-8")
    (OUT / "cohort_heterogeneity.json").write_text(json.dumps(
        {"note": ("random-effects pooling with REML tau^2; I^2 and Cochran Q "
                  "for heterogeneity; prediction interval = where a NEW "
                  "cohort's true effect would be expected"),
         "by_rule": report, "e_values": ev,
         "reclassification": reclass,
         "n_influence_rows": len(infl)}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print(f"{'rule':38s} {'k':>2s} {'pooled OR':>10s} {'95% CI':>18s} "
          f"{'I2%':>6s} {'tau2':>7s} {'Q_p':>8s}  PI")
    for rid, r in report.items():
        if "pooled_OR" not in r:
            print(f"{rid:38s} {r['k']:>2d}  single cohort ({r.get('OR')})")
            continue
        pi = r["prediction_interval"]
        print(f"{rid:38s} {r['k']:>2d} {r['pooled_OR']:>10.3f} "
              f"[{r['pooled_ci'][0]:.3f},{r['pooled_ci'][1]:.3f}]".ljust(62)
              + f"{r['I2_percent']:>6.1f} {r['tau2']:>7.4f} {r['Q_p']:>8.4f}  "
              + (f"[{pi[0]:.2f},{pi[1]:.2f}]" if pi else "not computable (k<3)"))
        sd = r.get("subgroup_by_region") or {}
        if sd.get("testable"):
            print(f"      region subgroups {dict(zip(sd['groups'], sd['per_group_OR']))}"
                  f"  Q_between={sd['Q_between']}  p={sd['p_between']:.4f}")
        mr = r.get("meta_regression_mean_age") or {}
        if "p" in mr:
            print(f"      meta-regression on mean age: slope="
                  f"{mr['slope_per_year_logOR']:+.5f}/yr  p={mr['p']:.4f}")
    print()
    for k, v2 in ev.items():
        print(f"  E-value {k:38s} point={v2['point']:.2f}  "
              f"CI-bound={v2['ci_bound_nearest_null']:.2f}")
    print()
    print("预注册判据 vs 异质性感知判据")
    for rid, r in reclass.items():
        print(f"  {rid:38s} {r['pre_registered']:14s} -> "
              f"{r['heterogeneity_aware']:32s} {r['agreement']}")
    print(f"\n-> {OUT/'cohort_heterogeneity.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
