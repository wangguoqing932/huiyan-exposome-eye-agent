#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Is the OUTCOME the weak measurement? NHANES 2005-2008, three constructs at once.

THE QUESTION THE POSITIVE CONTROL RAISED
-----------------------------------------
The positive control found age-cataract to be more heterogeneous across the
ageing cohorts (I2 = 99.2%) than any exposure rule, with the per-cohort estimate
running from 1.15 in CLHLS to 3.14 in ELSA. Age's association with cataract is
not in dispute, so at least one of those two numbers is measuring something other
than the construct it names.

CLHLS and ELSA ascertain cataract the same way on paper -- self-reported
physician diagnosis -- so the difference is either in the populations or in what
the self-report captures in each. That cannot be settled inside the ageing
cohorts, because they have no objective ocular measurement.

NHANES 2005-2008 can settle it, because it measured the SAME people three ways:

    VIQ071   ever had a cataract operation          self-report (questionnaire)
    VIQ200   eye surgery for cataracts              self-report (at the exam)
    VIXNC1   line read on the near card             OBJECTIVE functional acuity
    VIQ031   general condition of eyesight          self-rated vision

If age predicts the objective acuity measure much more strongly than it predicts
self-reported cataract, then self-reported cataract is the weaker instrument,
and that is the explanation for the CLHLS-ELSA gap -- a measurement explanation,
demonstrated rather than asserted.

Run: python scripts/nhanes_outcome_validation.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")
OUT = ROOT / "outputs" / "cohorts" / "nhanes_outcome_validation.json"
WAVES = [("2005-2006", "_D"), ("2007-2008", "_E")]


def load_wave(w: str) -> pd.DataFrame:
    d = NH / w
    def rd(name):
        f = d / name
        if not f.exists():
            return None
        df, _ = pyreadstat.read_xport(str(f))
        return df
    viq = rd(f"VIQ{'_D' if w == '2005-2006' else '_E'}.XPT")
    vix = rd(f"VIX{'_D' if w == '2005-2006' else '_E'}.XPT")
    demo = rd(f"DEMO{'_D' if w == '2005-2006' else '_E'}.XPT")
    if viq is None or demo is None:
        return pd.DataFrame()
    keep_viq = [c for c in ("SEQN", "VIQ031", "VIQ071", "VIQ200") if c in viq.columns]
    out = viq[keep_viq].copy()
    if vix is not None:
        vcols = [c for c in ("SEQN", "VIXNC1", "VIQ200") if c in vix.columns]
        out = out.merge(vix[vcols], on="SEQN", how="left", suffixes=("", "_vix"))
    dcols = [c for c in ("SEQN", "RIDAGEYR", "RIAGENDR") if c in demo.columns]
    out = out.merge(demo[dcols], on="SEQN", how="left")
    out["wave"] = w
    return out


def fit(d: pd.DataFrame, ycol: str, invert: bool = False) -> dict | None:
    """OR per decade of age, adjusted for sex and wave."""
    raw = pd.to_numeric(d[ycol], errors="coerce")
    if ycol == "VIQ031":
        # 1 excellent / 2 good / 3 fair / 4 poor / 5 very poor / 9 don't know
        y = raw.map({1: 0.0, 2: 0.0, 3: 1.0, 4: 1.0, 5: 1.0})
    elif ycol in ("VIQ071", "VIQ200"):
        # 1 yes / 2 no / 9 don't know
        y = raw.map({1: 1.0, 2: 0.0})
    else:
        # VIXNC1: lines read on the near card, 0-8, HIGHER is better
        y = np.where(raw <= 3, 1.0, 0.0)
        y = pd.Series(y, index=raw.index).where(raw.notna())
    age = pd.to_numeric(d["RIDAGEYR"], errors="coerce")
    sex = pd.to_numeric(d["RIAGENDR"], errors="coerce")
    m = y.notna() & age.notna() & sex.notna() & (age >= 40)
    if m.sum() < 300 or y[m].nunique() < 2:
        return None
    X = pd.DataFrame({"age_decade": age[m] / 10.0,
                      "female": (sex[m] == 2).astype(float)})
    if d["wave"][m].nunique() > 1:
        X = pd.concat([X, pd.get_dummies(d["wave"][m].astype("category"),
                                         prefix="w", drop_first=True,
                                         dtype=float)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    try:
        r = sm.GLM(y[m].astype(float), X, family=sm.families.Binomial()).fit()
    except Exception:
        return None
    b, se = float(r.params["age_decade"]), float(r.bse["age_decade"])
    # prevalence of the coded event
    prev = float(y[m].mean())
    return {"n": int(m.sum()), "event_prevalence": round(prev, 4),
            "OR_per_decade": round(math.exp(b), 3),
            "ci_low": round(math.exp(b - 1.96 * se), 3),
            "ci_high": round(math.exp(b + 1.96 * se), 3),
            "p": float(r.pvalues["age_decade"])}


CONSTRUCTS = [
    ("VIQ071", "self-reported cataract operation (questionnaire)", False),
    ("VIQ200", "self-reported cataract surgery (at the exam)", False),
    ("VIQ031", "self-rated fair/poor eyesight", True),
    ("VIXNC1", "objective near-card acuity, below median", True),
]


def main() -> int:
    frames = [load_wave(w) for w, _ in WAVES]
    d = pd.concat([f for f in frames if len(f)], ignore_index=True)
    print(f"NHANES 2005-2008 pooled: n = {len(d):,}")
    print()
    print(f"{'construct':50s} {'n':>7s} {'prev':>7s} {'OR/decade':>10s} "
          f"{'95% CI':>17s}")
    print("-" * 100)
    res = {}
    for col, label, inv in CONSTRUCTS:
        if col not in d.columns:
            print(f"{label:50s} column absent")
            continue
        r = fit(d, col, invert=inv)
        if not r:
            print(f"{label:50s} not estimable")
            continue
        res[col] = dict(r, label=label)
        print(f"{label:50s} {r['n']:>7,} {r['event_prevalence']:>7.3f} "
              f"{r['OR_per_decade']:>10.3f} "
              f"[{r['ci_low']:.2f},{r['ci_high']:.2f}]")

    print()
    if "VIQ071" in res and "VIXNC1" in res:
        sr = res["VIQ071"]["OR_per_decade"]
        ob = res["VIXNC1"]["OR_per_decade"]
        ratio = ob / sr
        print("=" * 100)
        print(f"  age -> self-reported cataract : OR {sr:.2f} per decade")
        print(f"  age -> objective acuity       : OR {ob:.2f} per decade")
        print(f"  ratio (objective / self-report): {ratio:.2f}x")
        print()
        if ratio > 1.3:
            print("  => The objective measure tracks age markedly more strongly")
            print("     than the self-report. Self-reported cataract is the weaker")
            print("     instrument, which is the measurement explanation for the")
            print("     CLHLS-ELSA gap in the positive control.")
            verdict = "self_report_weaker"
        elif ratio < 0.77:
            print("  => The self-report tracks age MORE strongly than the")
            print("     objective measure. The measurement explanation is not")
            print("     supported and must be withdrawn.")
            verdict = "self_report_stronger"
        else:
            print("  => The two are comparable. Self-report is not obviously")
            print("     the weaker instrument, so the CLHLS-ELSA gap is not")
            print("     explained by the reporting mode alone.")
            verdict = "comparable"
    else:
        ratio, verdict = None, "not estimable"

    OUT.write_text(json.dumps({
        "why": ("NHANES 2005-2008 measured the same people with a self-reported "
                "cataract item and an objective acuity test; this isolates "
                "whether the outcome construct is the weak measurement"),
        "wave_files": [w for w, _ in WAVES], "n_pooled": int(len(d)),
        "results": res, "objective_over_selfreport_ratio": (
            round(ratio, 3) if ratio else None), "verdict": verdict},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
