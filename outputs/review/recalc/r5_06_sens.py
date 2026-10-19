#!/usr/bin/env python
"""R5 independent recalculation -- step 6: sensitivity checks.

(a) r10 leave-one-cohort-out  -- is the regional direction split produced by any
    single cohort?
(b) r10 with the extreme-age tail removed -- CLHLS has mean age 92.0; restricting
    to age <= 85 asks whether the reversal survives when the very old are dropped.
(c) r13 with the BMI cut-point swapped (SHARE/CRELES 30 -> 25) -- does the
    direction change?
(d) leave-one-cohort-out on r02 and r20 (influence on a *replicated* rule).

NOTE on the brief: the BMI cut-point is definitionally irrelevant to r10, whose
exposure is current smoking, so "different BMI cut-point" cannot be applied to
r10; (c) applies it to the only rules it can touch (r13).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FRAMES = Path(r"D:\Desktop\眼科公共数据库agent搭建\data\frames")
OUT = HERE
from r5_02_confirm import fit_once, rubin          # noqa: E402
from r5_03_meta import pool, subgroup, REGION      # noqa: E402


def refit(coh, xcol, ycol, age_max=None, age_min=None):
    d = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False)
    if age_max is not None or age_min is not None:
        a = pd.to_numeric(d["age"], errors="coerce")
        m = pd.Series(True, index=d.index)
        if age_max is not None:
            m &= a <= age_max
        if age_min is not None:
            m &= a >= age_min
        d = d[m]
    wave_col = "wave" if d["wave"].nunique() > 1 else None
    if "implicat" in d.columns and d["implicat"].nunique() > 1:
        fits = [f for f in (fit_once(s, xcol, ycol, wave_col)
                            for _, s in d.groupby("implicat"))
                if f is not None and "beta" in f]
        if not fits:
            return None
        b, se, _, _, _, _ = rubin(fits)
    else:
        f = fit_once(d, xcol, ycol, wave_col)
        if f is None or "beta" not in f:
            return None
        b, se = f["beta"], f["se"]
    return {"cohort": coh, "beta": b, "se": se, "odds_ratio": math.exp(b),
            "ci_low": math.exp(b - 1.96 * se), "ci_high": math.exp(b + 1.96 * se)}


def summarize(rows, label):
    y = np.array([math.log(r["odds_ratio"]) for r in rows])
    v = np.array([r["se"] ** 2 for r in rows])
    g = [REGION[r["cohort"]] for r in rows]
    p = pool(y, v)
    sg = subgroup(y, v, g)
    return {"label": label, "k": len(rows),
            "cohorts": [r["cohort"] for r in rows],
            "per_cohort_OR": {r["cohort"]: round(r["odds_ratio"], 4) for r in rows},
            "pooled_OR": p["pooled_OR_REML"], "CI": p["pooled_CI_REML"],
            "I2": p["I2_percent"], "Q_p": p["Q_p"],
            "region_OR": sg.get("per_group_OR"), "Q_between_p": sg.get("p_between")}


bundle = json.loads((OUT / "recalc_fit_SHARE.json").read_text(encoding="utf-8"))
allfits = {}
for p in sorted(OUT.glob("recalc_fit_*.json")):
    j = json.loads(p.read_text(encoding="utf-8"))
    for r in j["results"]:
        if r.get("status") == "ok":
            allfits[(r["rule_id"], r["cohort"])] = r
print(f"loaded {len(allfits)} fitted cells")

out = {}

# ---------- (a)/(d) leave-one-cohort-out -----------------------------------
for rid in ("r10_smoking_x_cataract", "r02_hyperglycemia_x_cataract",
            "r20_smoking_x_vi_mod_severe"):
    rows = [r for (rr, _), r in allfits.items() if rr == rid]
    base = summarize(rows, "all")
    loo = []
    for drop in [r["cohort"] for r in rows]:
        sub = [r for r in rows if r["cohort"] != drop]
        loo.append(summarize(sub, f"drop {drop}"))
    out[f"loo_{rid}"] = {"base": base, "leave_one_out": loo}
    print(f"\n=== LEAVE-ONE-COHORT-OUT {rid} ===")
    for s in [base] + loo:
        print(f"  {s['label']:14s} k={s['k']} pooled={s['pooled_OR']:.3f} "
              f"[{s['CI'][0]:.3f},{s['CI'][1]:.3f}] I2={s['I2']:.1f} "
              f"region={s['region_OR']} p_between={s['Q_between_p']:.3g}")

# ---------- (b) r10 with extreme-age tail removed --------------------------
print("\n=== r10 SENSITIVITY: extreme-age tail removed ===")
r10_coh = [c for c in ("CLHLS", "CRELES", "ELSA", "SHARE")]
for cap_label, cap in (("age<=85", 85), ("age<=80", 80), ("age in 60-85", None)):
    rows = []
    for coh in r10_coh:
        if cap is None:
            r = refit(coh, "current_smoking", "cataract_any", 85, 60)
        else:
            r = refit(coh, "current_smoking", "cataract_any", cap, None)
        if r:
            rows.append(r)
    s = summarize(rows, cap_label)
    out[f"r10_age_{cap_label}"] = s
    print(f"  {cap_label:14s} k={s['k']} pooled={s['pooled_OR']:.3f} "
          f"[{s['CI'][0]:.3f},{s['CI'][1]:.3f}] I2={s['I2']:.1f} "
          f"region={s['region_OR']} p_between={s['Q_between_p']:.3g}")
    print(f"      per cohort: "
          f"{ {k: round(v,3) for k,v in s['per_cohort_OR'].items()} }")

# ---------- (c) r13 with the BMI cut-point swapped -------------------------
print("\n=== r13 SENSITIVITY: BMI cut-point swapped vs pre-declared ===")
r13 = {}
for tag, cut in (("pre-declared (SHARE/CRELES=30)", 30), ("swapped (SHARE/CRELES=25)", 25)):
    rows = []
    for coh in ("SHARE", "CRELES"):
        r = refit(coh, f"bmi_high_{cut}", "cataract_any")
        if r:
            rows.append(r)
    s = summarize(rows, tag)
    r13[tag] = s
    print(f"  {tag:30s} pooled={s['pooled_OR']:.3f} "
          f"[{s['CI'][0]:.3f},{s['CI'][1]:.3f}] I2={s['I2']:.1f} "
          f"per-cohort={ {k: round(v,3) for k,v in s['per_cohort_OR'].items()} }")
out["r13_bmi_cut"] = r13

# ---------- r13 alternative cut for the Asian cohorts (context) ------------
alt = {}
for coh in ("KLoSA", "MHAS", "LASI", "CLHLS"):
    dr = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False, nrows=1)
    miss = [c for c in ("cataract_any", "bmi_high_25", "bmi_high_30")
            if c not in dr.columns]
    if miss:
        alt[coh] = {"note": f"not testable: missing {miss}"}
        continue
    alt[coh] = {f"bmi_high_{c}": (refit(coh, f"bmi_high_{c}", "cataract_any") or
                                  {"note": "not testable"})
                for c in (25, 30)}
out["r13_alt_cut_asian"] = {k: {kk: (None if not vv or "beta" not in vv
                                     else round(vv["odds_ratio"], 4))
                                for kk, vv in v.items()} for k, v in alt.items()}
print("\n=== r13 alternative cut in the Asian cohorts (context only) ===")
for k, v in out["r13_alt_cut_asian"].items():
    print(f"  {k}: {v}")

(OUT / "recalc_sensitivity.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"\n-> {OUT/'recalc_sensitivity.json'}")
