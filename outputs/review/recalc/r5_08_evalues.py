#!/usr/bin/env python
"""R5 independent recalculation -- step 8: E-values (VanderWeele & Ding 2017).

EV(RR) = RR + sqrt(RR (RR - 1)) with RR = max(OR, 1/OR); the CI bound reported is
the one nearer the null. Reproduces the numbers in table5_heterogeneity.md.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
OUT = ROOT / "outputs" / "review" / "recalc"


def ev(rr):
    rr = max(float(rr), 1e-12)
    if rr < 1:
        rr = 1.0 / rr
    return rr + math.sqrt(rr * (rr - 1.0))


mine = pd.read_csv(OUT / "recalc_three_state.csv")
rows = []
for rid, coh in (("r10_smoking_x_cataract", "CLHLS"),
                 ("r10_smoking_x_cataract", "SHARE"),
                 ("r12_alcohol_x_cataract", "CLHLS"),
                 ("r02_hyperglycemia_x_cataract", "CLHLS")):
    r = pd.read_csv(OUT / "recalc_confirmed_18.csv")
    r = r[(r.rule_id == rid) & (r.cohort == coh)].iloc[0]
    bound = r.ci_low if abs(math.log(r.ci_low)) < abs(math.log(r.ci_high)) \
        else r.ci_high
    rows.append({"rule": rid, "cohort": coh, "OR": r.odds_ratio,
                 "CI": f"{r.ci_low}-{r.ci_high}",
                 "E_value_point": round(ev(r.odds_ratio), 3),
                 "E_value_ci_bound": round(ev(bound), 3)})
df = pd.DataFrame(rows)
df.to_csv(OUT / "recalc_evalues.csv", index=False, encoding="utf-8")
print(df.to_string(index=False))
print("\npaper (table5_heterogeneity.md): CLHLS r10 2.01 (1.57); SHARE r10 1.46 "
      "(1.25); CLHLS r12 1.78 (1.36); CLHLS r02 6.64 (4.69)")
