#!/usr/bin/env python
"""R5 independent recalculation -- step 4: per-pair minimum detectable OR.

INDEPENDENT REWRITE of scripts/cohort_power.py.

Declared formula (methods.md / analysis_plan 17):
    SE(logOR) ~ sqrt(1/(n1 p) + 1/(n1 (1-p)) + 1/(n0 p) + 1/(n0 (1-p))),  p1=p0=p
    MDE_OR   = exp((z_0.975 + z_0.80) * SE)

Reported TWO ways, because the project's own power table and its own result
table use different denominators for SHARE:
  (A) `as_published`  -- n = non-missing rows of (exposure, outcome) over the
      WHOLE frame, i.e. all five SHARE imputation replicates counted as separate
      observations (this reproduces cohort_power.csv);
  (B) `analysed`      -- n = the complete-case analysis sample of a single
      replicate (the n actually reported with the OR).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "review" / "recalc"
Z_A, Z_P = 1.959963985, 0.8416212336

RULE_COLS = {
    "r02_hyperglycemia_x_cataract": ("diabetes", "cataract_any"),
    "r10_smoking_x_cataract": ("current_smoking", "cataract_any"),
    "r11_smoking_x_amd_late": ("current_smoking", "amd_any"),
    "r12_alcohol_x_cataract": ("alcohol_intake", "cataract_any"),
    "r13_bmi_x_cataract": (None, "cataract_any"),
    "r20_smoking_x_vi_mod_severe": ("current_smoking",
                                    "vision_impairment_moderate"),
}
BMI_CUT = {"KLoSA": 25, "MHAS": 25, "LASI": 25, "CLHLS": 25,
           "SHARE": 30, "HRS": 30, "ELSA": 30, "CRELES": 30}
# rule x cohort cells analysed (analysis_plan 19.6)
CELLS = [("r02_hyperglycemia_x_cataract", c) for c in
         ("CLHLS", "CRELES", "LASI", "SHARE")] + \
        [("r10_smoking_x_cataract", c) for c in
         ("CLHLS", "CRELES", "ELSA", "SHARE")] + \
        [("r11_smoking_x_amd_late", "ELSA")] + \
        [("r12_alcohol_x_cataract", c) for c in ("CLHLS", "SHARE")] + \
        [("r13_bmi_x_cataract", c) for c in ("CRELES", "SHARE")] + \
        [("r20_smoking_x_vi_mod_severe", c) for c in
         ("CLHLS", "ELSA", "HRS", "KLoSA", "SHARE")]


def mde(n, pe, p0):
    n = float(n)
    n1, n0 = n * pe, n * (1 - pe)
    if n1 < 2 or n0 < 2 or not (0 < p0 < 1):
        return float("nan")
    se = math.sqrt(1 / (n1 * p0) + 1 / (n1 * (1 - p0))
                   + 1 / (n0 * p0) + 1 / (n0 * (1 - p0)))
    return math.exp((Z_A + Z_P) * se)


rows = []
for coh in sorted({c for _, c in CELLS}):
    d = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False)
    has_imp = "implicat" in d.columns and d["implicat"].nunique() > 1
    for rid, c2 in CELLS:
        if c2 != coh:
            continue
        xb, ycol = RULE_COLS[rid]
        xcol = f"bmi_high_{BMI_CUT[coh]}" if xb is None else xb
        if xcol not in d.columns or ycol not in d.columns:
            continue
        # (A) as published: whole frame, all implicates
        sub = d[[xcol, ycol]].apply(pd.to_numeric, errors="coerce").dropna()
        nA = len(sub)
        peA = float(sub[xcol].mean())
        p0A = float(sub.loc[sub[xcol] == 0, ycol].mean())
        # (B) analysed: replicate 1, complete cases on y,x,age,sex,wave
        cols = [xcol, ycol, "age", "sex", "wave"]
        d1 = d[d["implicat"] == d["implicat"].min()] if has_imp else d
        s1 = d1[cols].apply(pd.to_numeric, errors="coerce").dropna()
        nB = len(s1)
        peB = float(s1[xcol].mean())
        p0B = float(s1.loc[s1[xcol] == 0, ycol].mean())
        rows.append({
            "cohort": coh, "rule_id": rid, "exposure": xcol, "outcome": ycol,
            "n_as_published": nA,
            "exposure_prev_as_published": round(peA, 4),
            "outcome_prev_unexp_as_published": round(p0A, 4),
            "mde_as_published": round(mde(nA, peA, p0A), 4),
            "n_analysed": nB,
            "exposure_prev_analysed": round(peB, 4),
            "outcome_prev_unexp_analysed": round(p0B, 4),
            "mde_analysed": round(mde(nB, peB, p0B), 4),
            "n_ratio": round(nA / nB, 3) if nB else None})

df = pd.DataFrame(rows)
df.to_csv(OUT / "recalc_power.csv", index=False, encoding="utf-8")

print(df[["cohort", "rule_id", "n_as_published", "mde_as_published",
          "n_analysed", "mde_analysed", "n_ratio"]].to_string(index=False))
print()
print("median MDE by rule (as published):")
print(df.groupby("rule_id")["mde_as_published"].median().round(4).to_string())
print()
print("median MDE by rule (analysed n only):")
print(df.groupby("rule_id")["mde_analysed"].median().round(4).to_string())
print()
print("cells where the published n is >2x the analysed n:")
flag = df[df.n_ratio > 2]
print(flag[["cohort", "rule_id", "n_as_published", "n_analysed", "n_ratio",
            "mde_as_published", "mde_analysed"]].to_string(index=False))
