#!/usr/bin/env python
"""R5 independent recalculation -- step 3: random-effects pooling & heterogeneity.

INDEPENDENT REWRITE of scripts/cohort_heterogeneity.py. Consumes MY OWN fits
(outputs/review/recalc/recalc_fit_*.json), not the project's result CSV.

Reports, per rule:
  * DerSimonian-Laird and REML tau^2
  * pooled OR (random effects) with 95% CI
  * Cochran Q, Q p, I^2  (I^2 uses the conventional max(0,(Q-df)/Q))
  * 95% prediction interval (t_{k-2} and normal variants)
  * regional subgroup Q_between
Order of operations fixed before running.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(r"D:\Desktop\眼科公共数据库agent搭建\outputs\review\recalc")

REGION = {"SHARE": "Europe", "ELSA": "Europe", "HRS": "Americas",
          "MHAS": "Americas", "CRELES": "Americas", "KLoSA": "Asia",
          "LASI": "Asia", "CLHLS": "Asia"}
MEAN_AGE = {"SHARE": 67.85, "HRS": 65.67, "ELSA": 64.85, "KLoSA": 65.74,
            "LASI": 57.92, "MHAS": 60.26, "CLHLS": 91.98, "CRELES": 76.75}


def dl_tau2(y, v):
    w = 1.0 / v
    mu = float((w * y).sum() / w.sum())
    q = float((w * (y - mu) ** 2).sum())
    k = len(y)
    c = float(w.sum() - (w ** 2).sum() / w.sum())
    return (max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0), q


def reml_tau2(y, v):
    k = len(y)
    if k < 2:
        return 0.0
    from scipy.optimize import minimize_scalar

    def neg(t2):
        w = 1.0 / (v + t2)
        mu = float((w * y).sum() / w.sum())
        return 0.5 * (float(np.log(v + t2).sum()) + math.log(float(w.sum()))
                      + float((w * (y - mu) ** 2).sum()))
    hi = float(max(1.0, 4.0 * np.var(y, ddof=1)))
    r = minimize_scalar(neg, bounds=(0.0, hi), method="bounded",
                        options={"xatol": 1e-9})
    return float(max(0.0, r.x))


def pmo(y, v, tau2):
    w = 1.0 / (v + tau2)
    mu = float((w * y).sum() / w.sum())
    se = math.sqrt(1.0 / w.sum())
    return mu, se


def pool(y, v):
    k = len(y)
    tau_dl, q = dl_tau2(y, v)
    tau_re = reml_tau2(y, v)
    df = k - 1
    i2 = max(0.0, (q - df) / q) * 100 if q > 0 else 0.0
    qp = float(stats.chi2.sf(q, df)) if k > 1 else float("nan")
    out = {"k": k, "Q": round(q, 4), "Q_df": df, "Q_p": qp,
           "I2_percent": round(i2, 2),
           "tau2_DL": round(tau_dl, 6), "tau2_REML": round(tau_re, 6)}
    for tag, t2 in (("REML", tau_re), ("DL", tau_dl)):
        mu, se = pmo(y, v, t2)
        lo, hi = mu - 1.96 * se, mu + 1.96 * se
        sep = math.sqrt(se ** 2 + t2)
        tcrit = float(stats.t.ppf(0.975, df)) if df >= 1 else 1.96
        out[f"pooled_OR_{tag}"] = round(math.exp(mu), 4)
        out[f"pooled_CI_{tag}"] = [round(math.exp(lo), 4), round(math.exp(hi), 4)]
        out[f"PI_normal_{tag}"] = [round(math.exp(mu - 1.96 * sep), 4),
                                   round(math.exp(mu + 1.96 * sep), 4)]
        out[f"PI_t_{tag}"] = [round(math.exp(mu - tcrit * sep), 4),
                              round(math.exp(mu + tcrit * sep), 4)]
    mu_dl, se_dl = pmo(y, v, tau_dl)
    out["w_DL_pct"] = [round(100 * float(x), 2) for x in
                       (1.0 / (v + tau_dl)) / (1.0 / (v + tau_dl)).sum()]
    return out


def subgroup(y, v, g, tau2=0.0):
    groups = sorted(set(g))
    if len(groups) < 2:
        return {"testable": False}
    mus, ses = [], []
    for grp in groups:
        m = np.array(g) == grp
        mu, se = pmo(y[m], v[m], 0.0)     # fixed-effect within subgroup (declared)
        mus.append(mu)
        ses.append(se)
    wb = 1.0 / np.array(ses) ** 2
    mu_b = float((wb * np.array(mus)).sum() / wb.sum())
    qb = float((wb * (np.array(mus) - mu_b) ** 2).sum())
    d = len(groups) - 1
    return {"testable": True, "groups": groups,
            "per_group_OR": {gname: round(math.exp(m), 4)
                             for gname, m in zip(groups, mus)},
            "Q_between": round(qb, 4), "df": d,
            "p_between": float(stats.chi2.sf(qb, d))}


def main():
    fits = []
    for p in sorted(OUT.glob("recalc_fit_*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        for r in j["results"]:
            if r.get("status") == "ok":
                fits.append(r)
    df = pd.DataFrame(fits)
    df["log_or"] = np.log(df["odds_ratio"])
    df["var"] = df["se"] ** 2
    df["region"] = df["cohort"].map(REGION)
    df.to_csv(OUT / "recalc_confirmed_18.csv", index=False, encoding="utf-8")

    print(f"fitted cells: {len(df)}   expected 18")
    report = {}
    for rid, sub in df.groupby("rule_id"):
        y = sub["log_or"].to_numpy(float)
        v = sub["var"].to_numpy(float)
        if len(sub) < 2:
            report[rid] = {"k": len(sub), "note": "single cohort, not pooled",
                           "OR": float(sub["odds_ratio"].iloc[0])}
            continue
        rep = pool(y, v)
        rep["cohorts"] = sub["cohort"].tolist()
        rep["per_cohort_OR"] = dict(zip(sub["cohort"], sub["odds_ratio"]))
        rep["per_cohort_CI"] = {c: [lo, hi] for c, lo, hi in
                                zip(sub["cohort"], sub["ci_low"], sub["ci_high"])}
        rep["subgroup_by_region"] = subgroup(y, v, sub["region"].tolist())
        # meta-regression on mean age (WLS) -- only when residual df exists
        if len(sub) >= 4:
            w = 1.0 / (v + rep["tau2_REML"])
            X = np.column_stack([np.ones(len(sub)),
                                 sub["cohort"].map(MEAN_AGE).to_numpy(float)])
            W = np.diag(w)
            try:
                beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
                resid = y - X @ beta
                dof = len(sub) - 2
                s2 = float(resid @ W @ resid) / dof
                cov = s2 * np.linalg.inv(X.T @ W @ X)
                se_slope = math.sqrt(cov[1, 1])
                rep["meta_reg_mean_age"] = {
                    "slope_per_year": round(float(beta[1]), 5),
                    "se": round(se_slope, 5),
                    "p": float(2 * stats.t.sf(abs(beta[1] / se_slope), dof))}
            except Exception as e:
                rep["meta_reg_mean_age"] = {"error": str(e)}
        report[rid] = rep

    (OUT / "recalc_meta.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'rule':32s} {'k':>2s} {'pooled REML':>18s} {'pooled DL':>18s} "
          f"{'I2%':>7s} {'Q_p':>10s} {'PI(REML,t)':>18s}")
    for rid, r in report.items():
        if "pooled_OR_REML" not in r:
            print(f"{rid:32s} {r['k']:>2d}  single cohort OR={r['OR']}")
            continue
        print(f"{rid:32s} {r['k']:>2d} "
              f"{r['pooled_OR_REML']:>7.3f} [{r['pooled_CI_REML'][0]:.3f},"
              f"{r['pooled_CI_REML'][1]:.3f}] "
              f"{r['pooled_OR_DL']:>7.3f} [{r['pooled_CI_DL'][0]:.3f},"
              f"{r['pooled_CI_DL'][1]:.3f}] "
              f"{r['I2_percent']:>7.2f} {r['Q_p']:>10.3g} "
              f"[{r['PI_t_REML'][0]:.2f},{r['PI_t_REML'][1]:.2f}]")
        sd = r["subgroup_by_region"]
        if sd.get("testable"):
            print(f"      region {sd['per_group_OR']}  "
                  f"Q_between={sd['Q_between']} df={sd['df']} "
                  f"p={sd['p_between']:.3g}")
        if "meta_reg_mean_age" in r and "p" in r["meta_reg_mean_age"]:
            m = r["meta_reg_mean_age"]
            print(f"      meta-reg age slope={m['slope_per_year']:+.5f}/yr "
                  f"p={m['p']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
