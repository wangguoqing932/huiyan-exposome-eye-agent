#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Correct the E-values: convert odds ratios to risk ratios before applying them.

WHAT WAS WRONG
--------------
`e_value()` fed odds ratios straight into VanderWeele & Ding's formula, which is
derived for RISK RATIOS. The approximation RR ~ OR is only defensible when the
outcome is rare. Cataract is not rare in these cohorts — 17.8% of unexposed CLHLS
participants have it — so the substitution inflates the E-value and makes the
result look more robust to unmeasured confounding than it is.

The exact conversion needs the unexposed risk p0:
    RR = OR / (1 - p0 + p0 * OR)

p0 is not in the confirmatory output, so it is computed here from the cohort
frames for the four pairs whose E-values are reported.

Run: python scripts/correct_evalues.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts" / "cohort_evalues_corrected.json"

# (rule, cohort, exposure column, outcome column)
PAIRS = [
    ("r10_smoking_x_cataract", "CLHLS", "current_smoking", "cataract_any"),
    ("r10_smoking_x_cataract", "SHARE", "current_smoking", "cataract_any"),
    ("r12_alcohol_x_cataract", "CLHLS", "alcohol_intake", "cataract_any"),
    ("r02_hyperglycemia_x_cataract", "CLHLS", "diabetes", "cataract_any"),
]


def ev(rr: float) -> float:
    """E-value for a risk ratio (VanderWeele & Ding 2017)."""
    rr = max(float(rr), 1e-12)
    if rr < 1:
        rr = 1.0 / rr
    return rr + math.sqrt(rr * (rr - 1.0))


def or_to_rr(o: float, p0: float) -> float:
    """Exact odds-ratio to risk-ratio conversion given the unexposed risk."""
    return o / (1.0 - p0 + p0 * o)


def main() -> int:
    cache: dict[str, pd.DataFrame] = {}
    rows, out = [], {}
    for rule, coh, exc, outc in PAIRS:
        key = coh
        if key not in cache:
            cols = ["current_smoking", "alcohol_intake", "diabetes", "cataract_any"]
            d = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False,
                            usecols=lambda c: c in cols)
            if "implicat" in d.columns and d["implicat"].nunique() > 1:
                d = d[d["implicat"] == d["implicat"].min()]
            cache[key] = d
        d = cache[key]
        x = pd.to_numeric(d[exc], errors="coerce")
        y = pd.to_numeric(d[outc], errors="coerce")
        m = x.notna() & y.notna()
        x, y = x[m], y[m]
        p0 = float(y[x == 0].mean())          # unexposed risk
        p1 = float(y[x == 1].mean())
        rr = p1 / p0 if p0 > 0 else float("nan")
        rows.append({"rule": rule, "cohort": coh, "n": int(m.sum()),
                     "exposed_risk": round(p1, 4), "unexposed_risk": round(p0, 4),
                     "risk_ratio": round(rr, 4)})
        out[f"{rule}@{coh}"] = {"p0_unexposed": round(p0, 4),
                                "rr_observed": round(rr, 4)}

    df = pd.DataFrame(rows)
    print("=== 未暴露风险与实际风险比 ===")
    print(df.to_string(index=False))
    print()

    # the odds ratios as reported, and their corrected E-values
    res = pd.read_csv(ROOT / "outputs" / "cohorts" / "cohort_rule_results.csv")
    print(f"{'pair':44s} {'OR':>6s} {'p0':>7s} {'RR':>6s} "
          f"{'E(OR-as-RR)':>12s} {'E(corrected)':>13s} {'inflation':>10s}")
    for rule, coh, _, _ in PAIRS:
        r = res[(res.rule_id == rule) & (res.cohort == coh)]
        if not len(r):
            continue
        o = float(r.iloc[0].odds_ratio)
        lo, hi = float(r.iloc[0].ci_low), float(r.iloc[0].ci_high)
        p0 = out[f"{rule}@{coh}"]["p0_unexposed"]
        rr = or_to_rr(o, p0)
        rr_lo, rr_hi = or_to_rr(lo, p0), or_to_rr(hi, p0)
        e_naive = ev(o)
        e_corr = ev(rr)
        bound = min((abs(math.log(rr_lo)), rr_lo), (abs(math.log(rr_hi)), rr_hi))[1]
        out[f"{rule}@{coh}"].update({
            "or_point": round(o, 4), "rr_point": round(rr, 4),
            "evalue_naive_or_as_rr": round(e_naive, 3),
            "evalue_corrected": round(e_corr, 3),
            "evalue_corrected_ci_bound": round(ev(bound), 3),
            "inflation_factor": round(e_naive / e_corr, 3)})
        print(f"{rule[:26]+'@'+coh:44s} {o:6.3f} {p0:7.4f} {rr:6.3f} "
              f"{e_naive:12.2f} {e_corr:13.2f} {e_naive/e_corr:9.2f}x")

    OUT.write_text(json.dumps({
        "why": ("e_value() fed odds ratios into a formula derived for risk "
                "ratios; cataract is not rare, so the naive E-values overstate "
                "robustness to unmeasured confounding"),
        "conversion": "RR = OR / (1 - p0 + p0 * OR), p0 = risk among the unexposed",
        "pairs": out}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
