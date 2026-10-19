#!/usr/bin/env python
"""R5 independent recalculation -- step 2: per-(rule x cohort) logistic fits.

INDEPENDENT REWRITE. Does not import any project script. Reads only the raw
cohort frames and re-implements the model declared in methods.md:

    logit(P(outcome)) = b0 + b1*exposure + b2*age + b3*sex + wave fixed effects
    variance clustered by mergeid (participant)
    SHARE: fit per `implicat` replicate, combine by Rubin's rules
    BMI cut-point: Asian cohorts (KLoSA/MHAS/LASI/CLHLS) 25, others 30

Usage: python r5_02_confirm.py <COHORT> [--pairs r02,r10,...]
Writes outputs/review/recalc/recalc_fit_<COHORT>.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import statsmodels.api as sm
from scipy import stats

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "review" / "recalc"

# ---- pre-registered testable (rule x cohort) cells, analysis_plan 19.6 ------
PAIRS = {
    "r02_hyperglycemia_x_cataract": ["CLHLS", "CRELES", "LASI", "SHARE"],
    "r10_smoking_x_cataract": ["CLHLS", "CRELES", "ELSA", "SHARE"],
    "r11_smoking_x_amd_late": ["ELSA"],
    "r12_alcohol_x_cataract": ["CLHLS", "SHARE"],
    "r13_bmi_x_cataract": ["CRELES", "SHARE"],
    "r20_smoking_x_vi_mod_severe": ["CLHLS", "ELSA", "HRS", "KLoSA", "SHARE"],
}
# fixed exposure/outcome column per rule (construct discipline, 19.4)
RULE_COLS = {
    "r02_hyperglycemia_x_cataract": ("diabetes", "cataract_any"),
    "r10_smoking_x_cataract": ("current_smoking", "cataract_any"),
    "r11_smoking_x_amd_late": ("current_smoking", "amd_any"),
    "r12_alcohol_x_cataract": ("alcohol_intake", "cataract_any"),
    "r13_bmi_x_cataract": (None, "cataract_any"),          # resolved by cut-point
    "r20_smoking_x_vi_mod_severe": ("current_smoking",
                                    "vision_impairment_moderate"),
}
BMI_CUT = {"KLoSA": 25, "MHAS": 25, "LASI": 25, "CLHLS": 25,
           "SHARE": 30, "HRS": 30, "ELSA": 30, "CRELES": 30}
RULE_DIR = {k: "risk_up" for k in PAIRS}


def build_design(d, xcol, ycol, wave_col):
    """Complete-case design matrix; returns (y, X, groups, n)."""
    cols = [ycol, xcol, "age", "sex", "mergeid"] + ([wave_col] if wave_col else [])
    sub = d[cols].copy()
    for c in cols:
        if c == "mergeid":
            continue
        sub[c] = pd.to_numeric(sub[c], errors="coerce")
    sub = sub.dropna(subset=[c for c in cols if c != "mergeid"])
    n = len(sub)
    if n < 200 or sub[ycol].nunique() < 2 or sub[xcol].nunique() < 2:
        return None
    parts = [pd.Series(1.0, index=sub.index, name="const"),
             sub[xcol].astype(float).rename(xcol),
             sub["age"].astype(float).rename("age"),
             sub["sex"].astype(float).rename("sex")]
    if wave_col is not None and sub[wave_col].nunique() > 1:
        wd = pd.get_dummies(sub[wave_col].astype("category"), prefix="w",
                            drop_first=True).astype(float)
        parts.append(wd)
    X = pd.concat(parts, axis=1)
    return sub[ycol].astype(float), X, sub["mergeid"], n


def fit_once(d, xcol, ycol, wave_col):
    b = build_design(d, xcol, ycol, wave_col)
    if b is None:
        return None
    y, X, groups, n = b
    try:
        m = sm.GLM(y, X, family=sm.families.Binomial())
        r = m.fit(cov_type="cluster", cov_kwds={"groups": groups},
                  maxiter=200, tol=1e-10)
    except Exception as e:                                       # pragma: no cover
        return {"error": f"{type(e).__name__}: {e}"}
    b1, se1 = float(r.params[xcol]), float(r.bse[xcol])
    return {"beta": b1, "se": se1, "n": int(n),
            "n_events": int(y.sum()), "n_clusters": int(groups.nunique())}


def rubin(fits):
    """Rubin's rules over m imputation replicates."""
    m = len(fits)
    betas = np.array([f["beta"] for f in fits], float)
    vars_ = np.array([f["se"] ** 2 for f in fits], float)
    qbar = float(betas.mean())
    ubar = float(vars_.mean())
    b = float(betas.var(ddof=1)) if m > 1 else 0.0
    tvar = ubar + (1.0 + 1.0 / m) * b if m > 1 else ubar
    se = math.sqrt(max(tvar, 1e-300))
    # Barnard-Rubin df (reported for transparency; z used for the CI as declared)
    if m > 1 and b > 0:
        lam = (1.0 + 1.0 / m) * b / tvar
        df = (m - 1) / (lam ** 2) if lam > 0 else np.inf
    else:
        df = np.inf
    return qbar, se, df, m, float(ubar), b


def run_pair(coh, rid, d, wave_col):
    xbase, ycol = RULE_COLS[rid]
    if xbase is None:
        xcol = f"bmi_high_{BMI_CUT[coh]}"
    else:
        xcol = xbase
    if xcol not in d.columns or ycol not in d.columns:
        return {"cohort": coh, "rule_id": rid, "status": "column_absent",
                "exposure": xcol, "outcome": ycol}
    rec = {"cohort": coh, "rule_id": rid, "exposure": xcol, "outcome": ycol,
           "bmi_cut": BMI_CUT[coh], "direction": RULE_DIR[rid],
           "status": "ok"}
    t0 = time.time()
    if "implicat" in d.columns and d["implicat"].nunique() > 1:
        fits = []
        for imp, sub in d.groupby("implicat"):
            f = fit_once(sub, xcol, ycol, wave_col)
            if f is not None and "beta" in f:
                f["implicat"] = int(imp)
                fits.append(f)
        if not fits:
            return {"cohort": coh, "rule_id": rid, "status": "no_fit",
                    "exposure": xcol, "outcome": ycol}
        beta, se, df, m, ubar, b = rubin(fits)
        rec.update({"n_imputations": m, "rubin_within_var": ubar,
                    "rubin_between_var": b, "rubin_df": (None if not np.isfinite(df)
                                                         else round(float(df), 2)),
                    "per_implicate": [{k: (round(v, 6) if isinstance(v, float) else v)
                                       for k, v in f.items()} for f in fits]})
    else:
        f = fit_once(d, xcol, ycol, wave_col)
        if f is None or "beta" not in f:
            return {"cohort": coh, "rule_id": rid, "status": "no_fit",
                    "exposure": xcol, "outcome": ycol}
        beta, se = f["beta"], f["se"]
        rec.update({"n_imputations": 1, "n": f["n"], "n_events": f["n_events"],
                    "n_clusters": f["n_clusters"]})
    z = beta / se if se else float("nan")
    rec.update({
        "beta": round(float(beta), 6), "se": round(float(se), 6),
        "odds_ratio": round(float(math.exp(beta)), 4),
        "ci_low": round(float(math.exp(beta - 1.959963985 * se)), 4),
        "ci_high": round(float(math.exp(beta + 1.959963985 * se)), 4),
        "z": round(float(z), 4),
        "p_two_sided": float(2 * stats.norm.sf(abs(z))),
        "seconds": round(time.time() - t0, 1)})
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cohort")
    ap.add_argument("--pairs", default=None)
    a = ap.parse_args()
    coh = a.cohort
    rids = ([r for r in PAIRS] if not a.pairs else a.pairs.split(","))
    rids = [r for r in rids if coh in PAIRS.get(r, [])]
    d = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False)
    wave_col = "wave" if d["wave"].nunique() > 1 else None
    res = []
    for rid in rids:
        r = run_pair(coh, rid, d, wave_col)
        res.append(r)
        print(f"[{coh}] {rid:34s} {r.get('status'):12s} "
              f"OR={r.get('odds_ratio')} [{r.get('ci_low')},{r.get('ci_high')}] "
              f"n={r.get('n')} m={r.get('n_imputations')} "
              f"q={r.get('p_two_sided')} ({r.get('seconds')}s)", flush=True)
    (OUT / f"recalc_fit_{coh}.json").write_text(
        json.dumps({"cohort": coh, "wave_col": wave_col,
                    "n_waves": int(d["wave"].nunique()), "results": res},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
