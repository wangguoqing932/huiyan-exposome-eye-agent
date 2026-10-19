#!/usr/bin/env python
"""Power analysis for the confirmatory matrix (R11 2026-10-15).

Why this exists
---------------
The pre-R11 deliverables reported "0 contradicted rule pairs" as if it were
evidence of correctness.  With 7-11 of every 14 "uninformative" pairs, absence
of a significant result carried almost no information: a null result is only
interpretable once you know the smallest effect the study could have detected.

What this computes
------------------
For every pair in the confirmatory CSVs:
  * MDE_OR  — minimum detectable odds ratio (OR>1) at 80% power, two-sided
              alpha = 0.05, from the observed n, exposed count and event count.
  * MDE_OR_inv — the mirror-image protective limit (OR<1).
  * design-effect adjustment — the survey design inflates the variance over a
    simple-random-sample model.  Instead of assuming a deff, we DERIVE it per
    pair from the ratio of the survey CI width to the model-based CI width
    (both are already in the CSV), then deflate the effective sample size.
  * null_type — splits "uninformative" into
        powered_null              : adequately powered to detect OR>=2, so the
                                    absence of association is informative
        underpowered_null         : cannot exclude a 2-fold effect
        severely_underpowered     : cannot even exclude a large effect

Outputs
-------
  outputs/confirmatory/power_analysis_<dataset>.csv
  outputs/confirmatory/power_summary.json

Run: PYTHONUTF8=1 python scripts/power_analysis.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "confirmatory"

ALPHA = 0.05
POWER = 0.80
Z_A = norm.ppf(1 - ALPHA / 2)
Z_B = norm.ppf(POWER)
CLINICAL_TARGETS = (1.5, 2.0)      # effect sizes we care about being able to exclude
SEVERE_TARGET = 3.0


def _p0_for_or(orr: float, px: float, py: float) -> float:
    """Event probability among the UNEXPOSED consistent with the marginal risk.

    p1 = OR*p0 / (1 - p0 + OR*p0);  solve  px*p1 + (1-px)*p0 = py  for p0.
    f is monotone increasing in p0, so a wide bracket always works.
    """
    def f(p0):
        p1 = orr * p0 / (1.0 - p0 + orr * p0)
        return px * p1 + (1.0 - px) * p0 - py
    lo, hi = 1e-9, 1.0 - 1e-9
    if f(lo) > 0 or f(hi) < 0:
        return np.nan
    return brentq(f, lo, hi, xtol=1e-12, rtol=1e-12)


def _se_logor(orr: float, n: float, px: float, py: float) -> float:
    p0 = _p0_for_or(orr, px, py)
    if not np.isfinite(p0) or p0 <= 0:
        return np.nan
    p1 = orr * p0 / (1.0 - p0 + orr * p0)
    n1, n0 = n * px, n * (1.0 - px)
    if min(p1, 1 - p1, p0, 1 - p0) <= 0 or n1 <= 1 or n0 <= 1:
        return np.nan
    return math.sqrt(1.0 / (n1 * p1 * (1 - p1)) + 1.0 / (n0 * p0 * (1 - p0)))


def min_detectable_or(n: float, px: float, py: float, direction: str = "up"):
    """Smallest |log OR| reachable at the target power (direction 'up' or 'down')."""
    if not (0 < px < 1) or not (0 < py < 1) or n <= 4:
        return np.nan
    if direction == "down":
        # mirror: analyse the complement exposure for the protective limit
        return min_detectable_or(n, 1.0 - px, py, "up")
    target = Z_A + Z_B

    def g(orr):
        se = _se_logor(orr, n, px, py)
        if not np.isfinite(se):
            return -1.0
        return math.log(orr) - target * se

    lo, hi = 1.0001, 1000.0
    if g(lo) > 0:
        return 1.0
    if g(hi) < 0:
        return np.inf                      # not reachable even at OR=1000
    return float(brentq(g, lo, hi, xtol=1e-6))


def derive_deff(row) -> float:
    """Design effect from the survey/model CI-width ratio (>=1 by construction)."""
    try:
        f_lo, f_hi = float(row["ci_lo"]), float(row["ci_hi"])
        s_lo, s_hi = float(row["ci_lo_svy"]), float(row["ci_hi_svy"])
    except (KeyError, TypeError, ValueError):
        return np.nan
    if not all(np.isfinite([f_lo, f_hi, s_lo, s_hi])) or f_lo <= 0 or s_lo <= 0:
        return np.nan
    w_f = math.log(f_hi) - math.log(f_lo)
    w_s = math.log(s_hi) - math.log(s_lo)
    if w_f <= 0:
        return np.nan
    deff = (w_s / w_f) ** 2
    return float(min(max(deff, 1.0), 25.0))


def classify(mde: float) -> str:
    if not np.isfinite(mde):
        return "not_assessable"
    if mde <= CLINICAL_TARGETS[0]:
        return "powered_for_1.5x"
    if mde <= CLINICAL_TARGETS[1]:
        return "powered_for_2.0x"
    if mde <= SEVERE_TARGET:
        return "powered_for_3.0x"
    return "severely_underpowered"


def null_type(gold3: str, mde: float) -> str:
    if gold3 != "uninformative":
        return ""
    if not np.isfinite(mde):
        return "not_assessable"
    if mde <= CLINICAL_TARGETS[1]:
        return "powered_null"
    return "underpowered_null"


def analyse(dataset: str, csv_name: str) -> pd.DataFrame | None:
    p = OUT / csv_name
    if not p.exists():
        print(f"[power] {csv_name} missing — skipped")
        return None
    d = pd.read_csv(p)
    if "n_exp" not in d.columns:
        print(f"[power] {csv_name} has no n_exp column — re-run the confirmatory layer first")
        return None

    tested = d[d["status"] == "tested"].copy()
    deff = tested.apply(derive_deff, axis=1)
    median_deff = float(np.nanmedian(deff)) if deff.notna().any() else 1.0
    deff = deff.fillna(median_deff)
    tested["deff"] = deff.round(3)
    tested["n_eff"] = (tested["n"] / tested["deff"]).round(1)

    mdes, minvs, classes, ntypes = [], [], [], []
    for r in tested.itertuples():
        n_eff = r.n_eff
        px = (r.n_exp / r.n) if r.n else np.nan
        py = (r.n_pos / r.n) if r.n else np.nan
        m = min_detectable_or(n_eff, px, py, "up")
        mi = min_detectable_or(n_eff, px, py, "down")
        mdes.append(round(m, 3) if np.isfinite(m) else np.nan)
        minvs.append(round(mi, 3) if np.isfinite(mi) else np.nan)
        classes.append(classify(m))
        ntypes.append(null_type(r.gold3, m))
    tested["mde_or_80"] = mdes
    tested["mde_or_inv_80"] = minvs
    tested["power_class"] = classes
    tested["null_type"] = ntypes

    keep = ["a_flag", "b_item", "predicted", "rule_ids", "n", "n_exp", "n_pos",
            "deff", "n_eff", "or", "ci_lo", "ci_hi", "p", "q", "gold3",
            "mde_or_80", "mde_or_inv_80", "power_class", "null_type"]
    tested[[c for c in keep if c in tested.columns]].to_csv(
        OUT / f"power_analysis_{dataset}.csv", index=False, encoding="utf-8-sig")
    print(f"\n=== {dataset}: {len(tested)} tested pairs, median design effect {median_deff:.2f} ===")
    return tested


def summarise(tested: pd.DataFrame, dataset: str) -> dict:
    rule = tested[tested["predicted"].fillna(False).astype(bool)]
    nulls = rule[rule["gold3"] == "uninformative"]
    mde = rule["mde_or_80"].dropna()
    return {
        "dataset": dataset,
        "tested_pairs": int(len(tested)),
        "median_design_effect": float(tested["deff"].median()),
        "median_mde_or_80": float(mde.median()) if len(mde) else None,
        "rule_relevant_tested": int(len(rule)),
        "rule_power_class": rule["power_class"].value_counts().to_dict(),
        "rule_nulls": int(len(nulls)),
        "rule_null_type": nulls["null_type"].value_counts().to_dict(),
        "informative_null_rate": (round(float((nulls["null_type"] == "powered_null").mean()), 3)
                                  if len(nulls) else None),
    }


def main() -> int:
    out = {}
    for ds, csv in (("nhanes", "nhanes_confirmatory.csv"),
                    ("knhanes", "knhanes_confirmatory.csv")):
        t = analyse(ds, csv)
        if t is not None:
            out[ds] = summarise(t, ds)

    print("\n" + "=" * 78)
    print("POWER SUMMARY — is a null result informative?")
    print("=" * 78)
    for ds, s in out.items():
        print(f"\n[{ds}]  tested={s['tested_pairs']}  median deff={s['median_design_effect']:.2f}"
              f"  median MDE(OR,80% power)={s['median_mde_or_80']}")
        print(f"   rule-relevant tested : {s['rule_relevant_tested']}")
        print(f"   power class          : {s['rule_power_class']}")
        print(f"   rule nulls           : {s['rule_nulls']} -> {s['rule_null_type']}")
        print(f"   informative-null rate: {s['informative_null_rate']}")

    (OUT / "power_summary.json").write_text(
        json.dumps({"alpha": ALPHA, "power": POWER, "method": "Wald log-OR, exact p0 solve, "
                    "design effect derived from survey/model CI-width ratio",
                    "clinical_targets": list(CLINICAL_TARGETS), "by_dataset": out},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[power] -> {OUT/'power_summary.json'} + power_analysis_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
