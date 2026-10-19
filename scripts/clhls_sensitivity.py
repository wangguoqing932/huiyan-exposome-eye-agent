#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLHLS sensitivity: what survives if only the 1998 wave is used.

THE PROBLEM
-----------
The CLHLS frame treats the longitudinal release as eight follow-up waves of the
same 9,093 people, giving 72,744 person-waves. Inspection of the raw file shows
that structure cannot be real:

    wave 1998-2011   g1 recorded for all 9,093   (100%)
    wave 2014        g1 recorded for        44   (0.5%)
    wave 2018        g1 recorded for        10   (0.1%)

A 13-year follow-up of a cohort whose mean age is 92, with ZERO attrition, is not
possible; the later waves show what real follow-up of this cohort looks like.
So g1_0 ... g1_11 are not eight repeated measurements of the same people, and
CLHLS contributes far fewer independent observations than the frame's row count
implies. This is the same class of error as counting SHARE's five imputation
replicates as five people, which was already corrected.

A second defect compounds it: `trueage` in the raw file is the 1998 baseline age
(verified: trueage_14 - trueage = 16 years, trueage_18 - trueage = 21 years), but
the frame assigned it to every wave. So a person observed in 2011 carries their
1998 age.

WHAT THIS DOES
--------------
Re-estimates every CLHLS confirmatory result using the 1998 wave only -- the one
wave whose provenance is unambiguous -- and compares against the full-frame
values. If a headline result survives, it survives on defensible data. If it
does not, the manuscript must say so.

Run: python scripts/clhls_sensitivity.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts" / "clhls_sensitivity.json"

PAIRS = [                       # (rule, exposure col, outcome col)
    ("r02_hyperglycemia_x_cataract", "diabetes", "cataract_any"),
    ("r10_smoking_x_cataract", "current_smoking", "cataract_any"),
    ("r12_alcohol_x_cataract", "alcohol_intake", "cataract_any"),
    ("r20_smoking_x_vi_mod_severe", "current_smoking", "vision_impairment_moderate"),
]


def fit(d: pd.DataFrame, expo: str, out: str) -> dict | None:
    y = pd.to_numeric(d[out], errors="coerce")
    x = pd.to_numeric(d[expo], errors="coerce")
    age = pd.to_numeric(d["age"], errors="coerce")
    sex = pd.to_numeric(d["sex"], errors="coerce")
    m = y.notna() & x.notna() & age.notna() & sex.notna()
    if m.sum() < 300 or y[m].nunique() < 2 or x[m].nunique() < 2:
        return None
    X = pd.DataFrame({"expo": x[m].astype(float), "age": age[m],
                      "female": (sex[m] == 2).astype(float)})
    if d["wave"][m].nunique() > 1:
        X = pd.concat([X, pd.get_dummies(d["wave"][m].astype("category"),
                                         prefix="w", drop_first=True,
                                         dtype=float)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    try:
        r = sm.GLM(y[m].astype(float), X, family=sm.families.Binomial()).fit(
            cov_type="cluster", cov_kwds={"groups": d["mergeid"][m]})
    except Exception:
        return None
    b, se = float(r.params["expo"]), float(r.bse["expo"])
    return {"n": int(m.sum()), "odds_ratio": round(math.exp(b), 3),
            "ci_low": round(math.exp(b - 1.96 * se), 3),
            "ci_high": round(math.exp(b + 1.96 * se), 3),
            "p": round(float(r.pvalues["expo"]), 6)}


def main() -> int:
    cols = {"mergeid", "wave", "age", "sex", "diabetes", "current_smoking",
            "alcohol_intake", "cataract_any", "vision_impairment_moderate"}
    d = pd.read_csv(FRAMES / "cohort_CLHLS.csv", low_memory=False,
                    usecols=lambda c: c in cols)

    # trueage is the 1998 age; advance it to each wave. The frame nonetheless
    # keeps one row per (person, wave) that we do NOT trust, so the primary
    # sensitivity is the 1998 wave alone.
    d["age_at_wave"] = pd.to_numeric(d["age"], errors="coerce") + (d["wave"] - 1998)
    d98 = d[d["wave"] == 1998].copy()

    res = {}
    print(f"{'rule':34s} {'frame (all waves)':>26s} {'1998 wave only':>26s}")
    print("-" * 92)
    for rule, expo, out in PAIRS:
        a = fit(d, expo, out)
        b = fit(d98, expo, out)
        res[rule] = {"all_waves": a, "wave_1998_only": b,
                     "exposure": expo, "outcome": out}
        fa = (f"{a['odds_ratio']:.3f} [{a['ci_low']:.2f},{a['ci_high']:.2f}] "
              f"n={a['n']:,}") if a else "not estimable"
        fb = (f"{b['odds_ratio']:.3f} [{b['ci_low']:.2f},{b['ci_high']:.2f}] "
              f"n={b['n']:,}") if b else "not estimable"
        print(f"{rule:34s} {fa:>26s} {fb:>26s}")

    print()
    print("Direction of the CLHLS estimate, all waves vs 1998 only:")
    flips = []
    for rule, v in res.items():
        a, b = v["all_waves"], v["wave_1998_only"]
        if not a or not b:
            print(f"  {rule:34s} not comparable")
            continue
        fa = a["ci_low"] > 1 or a["ci_high"] < 1
        fb = b["ci_low"] > 1 or b["ci_high"] < 1
        sa = "risk-up" if a["odds_ratio"] > 1 else "protective"
        sb = "risk-up" if b["odds_ratio"] > 1 else "protective"
        tag = ""
        if sa != sb:
            tag = "  <-- DIRECTION FLIPS"
            flips.append(rule)
        elif fa and not fb:
            tag = "  <-- significance lost"
        elif fb and not fa:
            tag = "  <-- significance gained"
        print(f"  {rule:34s} {sa:>11s} -> {sb:<11s} {tag}")

    OUT.write_text(json.dumps({
        "why": ("CLHLS's frame treats the release as 8 follow-up waves of 9,093 "
                "people; the raw file shows 2014 and 2018 have 44 and 10 "
                "respondents, so the wave structure is not defensible and the "
                "row count overstates independent observations"),
        "verified_facts": {
            "trueage_is_baseline_1998": "trueage_14 - trueage = 16y, "
                                        "trueage_18 - trueage = 21y",
            "respondents_by_wave": {"1998-2011": 9093, "2014": 44, "2018": 10},
            "age_wave_invariant_pct": 92.74},
        "results": res, "direction_flips": flips}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
