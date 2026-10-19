#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Positive control: can these cohorts detect an association that is certainly real?

WHY THIS IS THE LOAD-BEARING ANALYSIS
-------------------------------------
The paper argues that measurement availability, not sample size, bounds what
this rule base can test, and that the rules that WERE testable show heterogeneity
too large for a pooled estimate to predict a new population. A reviewer is
entitled to the alternative explanation: perhaps these cohorts are simply too
noisy or too incomparably measured to detect anything, in which case the rule
heterogeneity says nothing about the rules.

That alternative is testable. Age and sex are associated with cataract and with
vision impairment in every population where anyone has looked, with large effect
sizes and no serious disagreement about direction. If the cohorts recover those
associations with LOW between-cohort heterogeneity, then the cohorts can detect
real associations and measure their outcomes comparably, and the high
heterogeneity of the rules must come from the exposures and the constructs --
which is the paper's claim. If the positive controls are ALSO wildly
heterogeneous, the paper's premise fails and we need to say so.

So this script is a falsification test of our own argument, not a supporting
exhibit. It is reported whichever way it comes out.

Run: python scripts/positive_control.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from cohort_heterogeneity import reml_tau2  # noqa: E402

FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts" / "positive_control.json"

# outcome -> {cohort: column}
OUTCOMES = {
    "cataract_any": {
        "SHARE": "cataract_any", "ELSA": "cataract_any", "LASI": "cataract_any",
        "CLHLS": "cataract_any", "CRELES": "cataract_any",
    },
    "vision_impairment_moderate": {
        "SHARE": "vision_impairment_moderate", "ELSA": "vision_impairment_moderate",
        "HRS": "vision_impairment_moderate", "KLoSA": "vision_impairment_moderate",
        "CLHLS": "vision_impairment_moderate",
    },
}


def load(cohort: str) -> pd.DataFrame:
    cols = {"age", "sex", "wave", "implicat", "mergeid"} | set(
        c for m in OUTCOMES.values() for c in m.values())
    d = pd.read_csv(FRAMES / f"cohort_{cohort}.csv", low_memory=False,
                    usecols=lambda x: x in cols)
    if "implicat" in d.columns and d["implicat"].nunique() > 1:
        d = d[d["implicat"] == d["implicat"].min()].copy()
    return d


def fit(d: pd.DataFrame, outcome: str, term: str) -> dict | None:
    """Logistic OR for `term` (age_decade or female) adjusted for the other plus
    wave, clustered by participant."""
    import statsmodels.api as sm

    y = pd.to_numeric(d[outcome], errors="coerce")
    age = pd.to_numeric(d["age"], errors="coerce")
    sex = pd.to_numeric(d["sex"], errors="coerce")
    m = y.notna() & age.notna() & sex.notna()
    if m.sum() < 500 or y[m].nunique() < 2:
        return None
    X = pd.DataFrame({"age_decade": age[m] / 10.0, "female": (sex[m] == 2).astype(float)})
    if "wave" in d.columns and d["wave"].nunique() > 1:
        w = pd.get_dummies(d["wave"][m].astype("category"), prefix="w",
                           drop_first=True, dtype=float)
        X = pd.concat([X, w], axis=1)
    X = sm.add_constant(X, has_constant="add")
    try:
        r = sm.GLM(y[m].astype(float), X,
                   family=sm.families.Binomial()).fit(
            cov_type="cluster", cov_kwds={"groups": d["mergeid"][m]})
    except Exception:
        return None
    if term not in r.params:
        return None
    b, se = float(r.params[term]), float(r.bse[term])
    return {"cohort_n": int(m.sum()), "beta": b, "se": se,
            "odds_ratio": float(math.exp(b)),
            "ci_low": float(math.exp(b - 1.96 * se)),
            "ci_high": float(math.exp(b + 1.96 * se)),
            "p": float(r.pvalues[term])}


def pool(rows: list[dict]) -> dict:
    y = np.array([r["beta"] for r in rows])
    v = np.array([r["se"] ** 2 for r in rows])
    k = len(y)
    tau2 = reml_tau2(y, v)
    w = 1.0 / (v + tau2)
    mu = float(np.sum(w * y) / np.sum(w))
    se = float(math.sqrt(1.0 / np.sum(w)))
    q = float(np.sum((1.0 / v) * (y - np.sum(y / v) / np.sum(1.0 / v)) ** 2))
    i2 = max(0.0, (q - (k - 1)) / q) * 100 if q > 0 else 0.0
    tcrit = float(stats.t.ppf(0.975, k - 2)) if k >= 3 else float("nan")
    sep = math.sqrt(se ** 2 + tau2)
    return {"k": k, "pooled_OR": round(math.exp(mu), 3),
            "ci": [round(math.exp(mu - 1.96 * se), 3),
                   round(math.exp(mu + 1.96 * se), 3)],
            "I2_percent": round(i2, 1), "tau2": round(tau2, 5),
            "Q": round(q, 3), "Q_p": round(float(stats.chi2.sf(q, k - 1)), 6),
            "ratio_spread": round(math.exp(1.96 * math.sqrt(tau2)), 3),
            "prediction_interval": (
                [round(math.exp(mu - tcrit * sep), 3),
                 round(math.exp(mu + tcrit * sep), 3)] if k >= 3 else None)}


def main() -> int:
    cache: dict[str, pd.DataFrame] = {}
    report, all_rows = {}, {}
    print(f"{'outcome':28s} {'cohort':9s} {'n':>9s} {'OR':>7s} {'95% CI':>18s}")
    for outcome, per in OUTCOMES.items():
        rows = []
        for cohort, col in per.items():
            if cohort not in cache:
                cache[cohort] = load(cohort)
            d = cache[cohort]
            if col not in d.columns:
                continue
            for term, label in (("age_decade", "age/decade"),
                                ("female", "female")):
                r = fit(d, col, term)
                if r:
                    r["cohort"], r["term"] = cohort, label
                    rows.append(r)
                    print(f"{outcome[:26]:28s} {cohort:9s} {r['cohort_n']:>9,} "
                          f"{r['odds_ratio']:>7.3f} "
                          f"[{r['ci_low']:.3f},{r['ci_high']:.3f}]")
        all_rows[outcome] = rows
        report[outcome] = {t: pool([r for r in rows if r["term"] == t])
                           for t in ("age/decade", "female")
                           if any(r["term"] == t for r in rows)}

    print()
    print("=" * 88)
    print("POSITIVE CONTROL: pooled estimates and, critically, the heterogeneity")
    print(f"{'outcome':28s} {'term':12s} {'k':>2s} {'pooled OR':>10s} "
          f"{'95% CI':>18s} {'I2':>7s} {'spread':>8s}")
    print("-" * 88)
    for outcome, per_term in report.items():
        for term, r in per_term.items():
            ci = f"[{r['ci'][0]:.2f}, {r['ci'][1]:.2f}]"
            print(f"{outcome[:26]:28s} {term:12s} {r['k']:>2d} "
                  f"{r['pooled_OR']:>10.3f} {ci:>18s} {r['I2_percent']:>6.1f}% "
                  f"{r['ratio_spread']:>7.2f}x")

    # the comparison that carries the argument
    het = json.loads((ROOT / "outputs" / "cohorts" /
                      "cohort_heterogeneity.json").read_text(encoding="utf-8"))
    rule_i2 = sorted(r["I2_percent"] for r in het["by_rule"].values()
                     if "I2_percent" in r)
    ctrl_i2 = sorted(r["I2_percent"] for p in report.values()
                     for r in p.values())
    print()
    print("=" * 88)
    print("THE COMPARISON")
    print(f"  positive controls (certain associations): I2 = "
          f"{', '.join(f'{x:.1f}' for x in ctrl_i2)}")
    print(f"  the exposure rules:                        I2 = "
          f"{', '.join(f'{x:.1f}' for x in rule_i2)}")
    print()
    ok = all(r["I2_percent"] < 75 for p in report.values() for r in p.values())
    print(f"  controls below the 75% threshold: {'YES' if ok else 'NO'}")
    if ok:
        print("  => the cohorts CAN recover a real association with tolerable")
        print("     heterogeneity, so the rule heterogeneity is about the")
        print("     exposures and their measurement, not about a data layer")
        print("     that cannot detect anything. The paper's claim survives.")
    else:
        print("  => at least one positive control is itself highly")
        print("     heterogeneous. The cohort layer cannot cleanly separate")
        print("     'the rule does not transport' from 'this data layer is too")
        print("     noisy'. This must be reported as a limitation on the")
        print("     strongest form of the claim.")

    OUT.write_text(json.dumps({
        "why": ("falsification test of the paper's premise: if the cohorts "
                "cannot recover age and sex associations with low "
                "heterogeneity, the rule heterogeneity is uninformative"),
        "per_cohort": all_rows, "pooled": report,
        "rule_I2_percent": rule_i2, "control_I2_percent": ctrl_i2,
        "controls_below_75": ok}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
