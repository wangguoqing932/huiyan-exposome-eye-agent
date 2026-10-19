#!/usr/bin/env python
"""Cohort-layer per-pair power: minimum detectable OR at 80% power.

The R11 layers had this (figure 7) and it is what let the paper say that most
nulls were informative nulls rather than failures of power. The cohort layer
asserted the equivalent in prose -- "the intervals are wide" -- which is not a
quantity. This computes it per pair from the analysed n and the observed
margins, with the same approximation used in the R11 layer so the two are
comparable.

  SE(log OR) ~ sqrt( 1/(n1*p1) + 1/(n1*(1-p1)) + 1/(n0*p0) + 1/(n0*(1-p0)) )
  MDE_OR     = exp( (z_0.975 + z_0.80) * SE )   evaluated at p1 = p0

A pair is called a POWERED NULL when the upper bound of its own CI excludes the
MDE, i.e. the study could have detected an association as small as (or smaller
than) the one it failed to find; otherwise the null is uninformative.

Output: outputs/cohorts/cohort_power.csv
Run: python scripts/cohort_power.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts"
COV = ROOT / "outputs" / "confirmatory" / "cohort_rule_coverage.json"
RES = ROOT / "outputs" / "cohorts" / "cohort_rule_results.csv"

Z_A = 1.959964
Z_P = 0.8416212
BMI_PRIMARY = {"KLoSA": "bmi_high_25", "MHAS": "bmi_high_25", "LASI": "bmi_high_25",
               "CLHLS": "bmi_high_25", "SHARE": "bmi_high_30", "HRS": "bmi_high_30",
               "ELSA": "bmi_high_30", "CRELES": "bmi_high_30"}


def mde(n: int, pe: float, p0: float) -> float:
    """Minimum detectable OR at 80% power for a two-group contrast."""
    n = float(n)
    n1, n0 = n * pe, n * (1.0 - pe)
    if n1 < 2 or n0 < 2 or not (0 < p0 < 1):
        return float("nan")
    se = math.sqrt(1.0 / (n1 * p0) + 1.0 / (n1 * (1 - p0))
                   + 1.0 / (n0 * p0) + 1.0 / (n0 * (1 - p0)))
    return math.exp((Z_A + Z_P) * se)


def main() -> int:
    cov = json.loads(COV.read_text(encoding="utf-8"))
    res = pd.read_csv(RES, low_memory=False)
    rows = []
    for path in sorted(FRAMES.glob("cohort_*.csv")):
        coh = path.stem.replace("cohort_", "")
        d = pd.read_csv(path, low_memory=False)
        # SHARE ships five imputation replicates stacked as rows. Counting all
        # five inflates n by exactly 5x, which shrinks SE by sqrt(5) and makes
        # every MDE look better than it is. The prevalence gate and all
        # descriptive statistics already use replicate 1 only; the power
        # calculation must do the same, and Table 6 previously did not --
        # its SHARE n was exactly 5x the confirmatory result file, and that
        # inflated n fed the MDE.
        if "implicat" in d.columns and d["implicat"].nunique() > 1:
            d = d[d["implicat"] == d["implicat"].min()]
        for rid, per in cov["matrix"].items():
            v = per.get(coh)
            if not v or not v.get("testable"):
                continue
            xcol = v["exposure_col"]
            if v["exposure_flag"] == "bmi_high":
                xcol = BMI_PRIMARY.get(coh, xcol)
            ycol = v["outcome_col"]
            if xcol not in d.columns or ycol not in d.columns:
                continue
            sub = d[[xcol, ycol]].apply(pd.to_numeric, errors="coerce").dropna()
            if len(sub) < 100:
                continue
            pe = float(sub[xcol].mean())
            p0 = float(sub.loc[sub[xcol] == 0, ycol].mean())
            pe = min(max(pe, 0.01), 0.99)
            if not (0 < p0 < 1):
                continue
            m = mde(len(sub), pe, p0)
            r = res[(res.rule_id == rid) & (res.cohort == coh)]
            if r.empty:
                continue
            r = r.iloc[0]
            # A powered null is one whose CI EXCLUDES its own MDE. An earlier
            # version tested ci_low > m for OR>1, which only catches CIs lying
            # wholly ABOVE the MDE and misses those lying wholly below it.
            powered = math.isfinite(m) and (m < r.ci_low or m > r.ci_high)
            rows.append({
                "cohort": coh, "rule_id": rid, "n": len(sub),
                "exposure_prevalence": round(pe, 4),
                "outcome_prevalence_unexposed": round(p0, 4),
                "mde_or_80": round(m, 4) if math.isfinite(m) else None,
                "observed_or": r.odds_ratio,
                "ci_low": r.ci_low, "ci_high": r.ci_high,
                "three_state": r.three_state,
                "powered_null": bool(powered and r.three_state == "uninformative"),
                "null_interpretation": (
                    "powered_null" if powered and r.three_state == "uninformative"
                    else "replicated" if r.three_state == "replicated"
                    else "contradicted" if r.three_state == "contradicted"
                    else "underpowered_or_indeterminate")})

    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "cohort_power.csv", index=False, encoding="utf-8")

    conf = df[df.rule_id != ""]
    med = conf.groupby("rule_id")["mde_or_80"].median()
    n_pn = int(df.powered_null.sum())
    n_un = int((df.three_state == "uninformative").sum())
    print(f"pairs with power computed: {len(df)}")
    print(f"median MDE-OR by rule:")
    for rid, v in med.items():
        print(f"  {rid:38s} {v:.3f}")
    print(f"\nuninformative pairs: {n_un}")
    print(f"of which POWERED NULLS (could have excluded their own MDE): {n_pn} "
          f"({100*n_pn/max(n_un,1):.1f}%)")
    print(df[["cohort", "rule_id", "n", "mde_or_80", "observed_or",
              "null_interpretation"]].to_string(index=False))
    print(f"\n-> {OUT/'cohort_power.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
