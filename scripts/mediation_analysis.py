#!/usr/bin/env python
"""Mediation analysis: is the glycaemia -> vision-impairment association
explained by diabetic retinopathy / cataract?  (R11 2026-10-15)

Rationale for the paper
-----------------------
The exposure-wide screen found a consistent, cross-dataset signal:
dysglycaemia is associated with vision impairment in BOTH national surveys
(NHANES: HbA1c x VI-mild OR 1.50 p=0.0013; KNHANES: HbA1c x VI OR 2.16 p=0.012).
VI is not part of the definition of diabetes, so this is not a tautological
association -- but it is also not novel unless we can say HOW MUCH of it runs
through the two known ocular complications.

Method
------
Binary exposure X, binary mediator M, binary outcome Y, survey weights.
  a-path  : logit(M) ~ X + covariates            -> alpha
  b-path  : logit(Y) ~ X + M + covariates        -> beta_M
  total   : logit(Y) ~ X + covariates            -> beta_total
  direct  : same fit as b-path                   -> beta_direct
  indirect (log-OR scale) = alpha * beta_M       (product of coefficients)
  proportion mediated    = (beta_total - beta_direct) / beta_total
  SE(indirect) by the delta method; CI on the log scale, exponentiated where
  an OR is the natural scale.

Estimates are approximate (logistic outcome, logit mediator) and are reported
as such; the sign and rough magnitude are what the paper should lean on.

Run: PYTHONUTF8=1 python scripts/mediation_analysis.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "confirmatory"

warnings_ = __import__("warnings")
warnings_.filterwarnings("ignore")

# ---- which models to run -------------------------------------------------
# (dataset, exposure, outcome, mediator, exposure build, outcome build, mediator build)
TRIPLES = [
    # ---------- NHANES ----------
    dict(dataset="nhanes", x="hba1c_elevated", y="vision_impairment_mild",
         m="retinopathy_any", cov="RIDAGEYR,RIAGENDR,RIDRETH1,INDFMPIR"),
    dict(dataset="nhanes", x="hba1c_elevated", y="vision_impairment_mild",
         m="cataract_any", cov="RIDAGEYR,RIAGENDR,RIDRETH1,INDFMPIR"),
    dict(dataset="nhanes", x="hba1c_elevated", y="vision_impairment_moderate",
         m="retinopathy_any", cov="RIDAGEYR,RIAGENDR,RIDRETH1,INDFMPIR"),
    dict(dataset="nhanes", x="hba1c_elevated", y="vision_impairment_severe",
         m="retinopathy_any", cov="RIDAGEYR,RIAGENDR,RIDRETH1,INDFMPIR"),
    # ---------- KNHANES ----------
    dict(dataset="knhanes", x="hba1c_elevated", y="vision_impairment_any",
         m="retinopathy_any", cov="age,age2,sex,edu,incm5"),
    dict(dataset="knhanes", x="hba1c_elevated", y="vision_impairment_any",
         m="cataract_any", cov="age,age2,sex,edu,incm5"),
    dict(dataset="knhanes", x="hyperglycemia", y="vision_impairment_any",
         m="retinopathy_any", cov="age,age2,sex,edu,incm5"),
    dict(dataset="knhanes", x="hyperglycemia", y="vision_impairment_any",
         m="cataract_any", cov="age,age2,sex,edu,incm5"),
]


def load_nhanes():
    from evaluate import (build_nhanes_exposures, build_nhanes_outcomes,
                          load_nhanes_raw, restrict_nhanes_adults)
    d = restrict_nhanes_adults(load_nhanes_raw())
    E, B = build_nhanes_exposures(d), build_nhanes_outcomes(d)
    cov = pd.DataFrame({"RIDAGEYR": pd.to_numeric(d["RIDAGEYR"], errors="coerce"),
                        "RIAGENDR": pd.to_numeric(d["RIAGENDR"], errors="coerce"),
                        "RIDRETH1": pd.to_numeric(d["RIDRETH1"], errors="coerce"),
                        "INDFMPIR": pd.to_numeric(d["INDFMPIR"], errors="coerce")})
    cov["age2"] = cov["RIDAGEYR"] ** 2 / 100
    return d, {**E, **B}, cov, "WTMEC2YR"


def load_knhanes():
    from evaluate_knhanes import (build_knhanes_exposures, build_knhanes_outcomes)
    FR = ROOT / "data/raw/knhanes_frames_v2"
    parts = []
    for p in sorted(FR.glob("knhanes_20*.csv")):
        df = pd.read_csv(p, low_memory=False)
        df["wave"] = int(p.stem.split("_")[1])
        parts.append(df)
    d = pd.concat(parts, ignore_index=True, sort=False)
    d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
    d = d[pd.to_numeric(d["wt_itvex"], errors="coerce") > 0]
    cov = pd.DataFrame({"age": pd.to_numeric(d["age"], errors="coerce")})
    cov["age2"] = cov["age"] ** 2 / 100
    cov["sex"] = pd.to_numeric(d["sex"], errors="coerce")
    for c in ("edu", "incm5"):
        if c in d.columns:
            cov[c] = pd.to_numeric(d[c], errors="coerce")
    return d, {**build_knhanes_exposures(d), **build_knhanes_outcomes(d)}, cov, "wt_itvex"


def fit_logit(y, Xdf, w, label):
    X = sm.add_constant(Xdf.astype(float))
    try:
        f = sm.GLM(y.astype(float), X, family=sm.families.Binomial(), freq_weights=w).fit()
        if not getattr(f, "converged", True):
            return None
        return f
    except Exception as e:
        print(f"    [{label}] fit failed: {type(e).__name__}")
        return None


def run_triple(spec, data):
    d, flags, cov, wtcol = data
    need = [spec["x"], spec["y"], spec["m"]]
    if any(k not in flags for k in need):
        return {"status": "missing_variable", "missing": [k for k in need if k not in flags]}
    covs = [c.strip() for c in spec["cov"].split(",") if c.strip() in cov.columns]
    sub = pd.DataFrame({spec["x"]: flags[spec["x"]], spec["y"]: flags[spec["y"]],
                        spec["m"]: flags[spec["m"]]}).join(cov[covs]).dropna()
    sub = sub[(sub[spec["x"]].isin([0, 1])) & (sub[spec["y"]].isin([0, 1]))
              & (sub[spec["m"]].isin([0, 1]))]
    n = len(sub)
    ny = int(sub[spec["y"]].sum()); nm = int(sub[spec["m"]].sum())
    nx = int(sub[spec["x"]].sum())
    if n < 300 or ny < 30 or nm < 30 or nx < 30:
        return {"status": "underpowered", "n": n, "n_y": ny, "n_m": nm, "n_x": nx}

    w = d.loc[sub.index, wtcol].astype(float)
    w = w.where(w > 0, 1.0) / w.mean()

    f_total = fit_logit(sub[spec["y"]], sub[[spec["x"]] + covs], w, "total")
    f_b = fit_logit(sub[spec["y"]], sub[[spec["x"], spec["m"]] + covs], w, "b-path")
    f_a = fit_logit(sub[spec["m"]], sub[[spec["x"]] + covs], w, "a-path")
    if f_total is None or f_b is None or f_a is None:
        return {"status": "fit_failed", "n": n}

    b_tot = float(f_total.params[spec["x"]]); s_tot = float(f_total.bse[spec["x"]])
    b_dir = float(f_b.params[spec["x"]]); s_dir = float(f_b.bse[spec["x"]])
    b_m = float(f_b.params[spec["m"]]); s_m = float(f_b.bse[spec["m"]])
    a = float(f_a.params[spec["x"]]); s_a = float(f_a.bse[spec["x"]])

    ind = a * b_m
    se_ind = math.sqrt((a ** 2) * (s_m ** 2) + (b_m ** 2) * (s_a ** 2))
    z_ind = ind / se_ind if se_ind > 0 else np.nan
    p_ind = float(2 * (1 - norm.cdf(abs(z_ind)))) if np.isfinite(z_ind) else np.nan
    prop = (b_tot - b_dir) / b_tot if b_tot != 0 else np.nan

    return {
        "status": "ok", "n": n, "n_x": nx, "n_y": ny, "n_m": nm,
        "or_total": round(math.exp(b_tot), 3),
        "or_total_ci": [round(math.exp(b_tot - 1.96 * s_tot), 3),
                        round(math.exp(b_tot + 1.96 * s_tot), 3)],
        "or_direct": round(math.exp(b_dir), 3),
        "or_direct_ci": [round(math.exp(b_dir - 1.96 * s_dir), 3),
                         round(math.exp(b_dir + 1.96 * s_dir), 3)],
        "or_mediator_in_model": round(math.exp(b_m), 3),
        "indirect_log_or": round(ind, 4),
        "indirect_se": round(se_ind, 4),
        "indirect_p": p_ind,
        "proportion_mediated": round(float(prop), 3) if np.isfinite(prop) else None,
        "attenuation_pct": (round(float(100 * (1 - math.exp(b_dir - b_tot))), 1)
                            if np.isfinite(b_dir) and np.isfinite(b_tot) else None),
    }


def main() -> int:
    cache = {"nhanes": load_nhanes(), "knhanes": load_knhanes()}
    rows = []
    for spec in TRIPLES:
        print(f"\n[{spec['dataset']}] {spec['x']} -> {spec['y']}  (mediator: {spec['m']})")
        r = run_triple(spec, cache[spec["dataset"]])
        rows.append({**{k: spec[k] for k in ("dataset", "x", "y", "m")}, **r})
        if r.get("status") == "ok":
            print(f"    n={r['n']}  total OR={r['or_total']} {r['or_total_ci']}  "
                  f"direct OR={r['or_direct']}  mediator OR={r['or_mediator_in_model']}")
            print(f"    indirect(logOR)={r['indirect_log_or']} p={r['indirect_p']:.4g}  "
                  f"proportion mediated={r['proportion_mediated']}  "
                  f"attenuation={r['attenuation_pct']}%")
        else:
            print(f"    {r}")

    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- stability screen -------------------------------------------------
    # Degenerate models (a handful of outcome events, or a total-effect CI
    # spanning an order of magnitude) produce absurd mediation fractions, e.g.
    # proportion mediated = 1.02.  Flag them so they can never be quoted as
    # findings.
    def stability(r):
        if r.get("status") != "ok":
            return r.get("status")
        issues = []
        if r.get("n_y", 0) < 80:
            issues.append(f"n_events={r.get('n_y')}")
        if r.get("n_m", 0) < 80:
            issues.append(f"n_mediator={r.get('n_m')}")
        try:
            lo, hi = r["or_total_ci"]
            if math.log(hi) - math.log(lo) > math.log(6):
                issues.append(f"total_CI_width_or={hi/lo:.1f}")
        except Exception:
            pass
        pm = r.get("proportion_mediated")
        if pm is not None and (pm < -0.5 or pm > 0.9):
            issues.append(f"prop_mediated={pm}")
        return "UNSTABLE: " + "; ".join(issues) if issues else "stable"

    if len(df):
        df["stability"] = df.apply(stability, axis=1)
        df.loc[df["status"] == "ok", "stability"] = df[df["status"] == "ok"].apply(stability, axis=1)

    df.to_csv(OUT / "mediation_analysis.csv", index=False, encoding="utf-8-sig")
    ok = df[(df["status"] == "ok") & (df["stability"] == "stable")]
    print(f"\n[mediation] {int((df['status'] == 'ok').sum())} fitted, {len(ok)} stable")
    if len(df):
        unstable = df[df.get("stability", pd.Series(dtype=str)).astype(str).str.startswith("UNSTABLE")]
        for r in unstable.itertuples():
            print(f"   UNSTABLE {r.dataset} {r.x}->{r.y} (M={r.m}): {r.stability}")
    summary = {
        "method": ("binary X, binary mediator, binary Y; product-of-coefficients on the "
                   "log-OR scale with delta-method SE; survey weights; proportion mediated "
                   "from the difference method. Approximate."),
        "models_attempted": int(len(df)),
        "models_fitted": int((df["status"] == "ok").sum()) if len(df) else 0,
        "models_stable": int(len(ok)),
        "median_proportion_mediated_stable": (float(ok["proportion_mediated"].median())
                                              if len(ok) else None),
        "stability_rule": ("UNSTABLE if <80 outcome events or <80 mediator cases, or the "
                           "total-effect CI spans >6-fold, or proportion mediated outside "
                           "[-0.5, 0.9]"),
        "results": df.to_dict(orient="records"),
    }
    (OUT / "mediation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[mediation] -> {OUT/'mediation_analysis.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
