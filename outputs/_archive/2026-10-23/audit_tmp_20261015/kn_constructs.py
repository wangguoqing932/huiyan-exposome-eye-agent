"""Confirm the value distributions behind the smoking/alcohol constructs, using
the now-verified official value labels, and recompute prevalences correctly.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FR = ROOT / "data/raw/knhanes_frames_v2"

frames = []
for p in sorted(FR.glob("knhanes_20*.csv")):
    d = pd.read_csv(p, low_memory=False)
    d["wave"] = int(p.stem.split("_")[1])
    frames.append(d)
d = pd.concat(frames, ignore_index=True, sort=False)
d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
d = d[pd.to_numeric(d["wt_itvex"], errors="coerce") > 0]
sex = pd.to_numeric(d["sex"], errors="coerce")
num = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)

print(f"analytic frame n={len(d)}  male share={(sex==1).mean():.3f}")


def vc(col, by_wave=True):
    s = num(col)
    print(f"\n=== {col} : value counts ===")
    if by_wave:
        t = pd.crosstab(d["wave"], s)
        print(t.to_string())
    print("  overall:", dict(s.value_counts(dropna=False).sort_index().items()))


vc("BS1_1")
vc("BS3_1")
vc("BS5")
vc("BD1")
vc("BD1_11")
vc("BD2_1")

print("\n\n=== CORRECTED constructs (official value labels) ===")
b1, b3 = num("BS1_1"), num("BS3_1")
bd1, bd111 = num("BD1"), num("BD1_11")
bd21 = num("BD2_1")
bd31, bd32 = num("BD2_31"), num("BD2_32")

E = {
    # smoking: BS1_1==2 = has smoked >=100 cigarettes in life; BS3_1: 1=daily,2=occasional,3=ex
    "smoke_ever_BS1_1_2": b1.eq(2).astype(float).where(b1.isin([1, 2, 3])),
    "smoke_current_BS3_1_12": b3.isin([1, 2]).astype(float).where(b3.isin([1, 2, 3, 8])),
    "smoke_former_BS3_1_3": b3.eq(3).astype(float).where(b3.isin([1, 2, 3, 8])),
    "smoke_current_and_ever_BS1_1_2_BS3_1_12": ((b1 == 2) & b3.isin([1, 2])).astype(float).where(
        b1.isin([1, 2, 3]) & b3.isin([1, 2, 3, 8])),
    # alcohol: BD1_11 == 1 means "drank nothing in the past year"
    "alcohol_never_BD1_1": bd1.eq(1).astype(float).where(bd1.isin([1, 2])),
    "alcohol_current_BD1_11_ge2": bd111.ge(2).astype(float).where(bd111.isin([1, 2, 3, 4, 5, 6])),
    "alcohol_frequent_BD1_11_56": bd111.isin([5, 6]).astype(float).where(bd111.isin([1, 2, 3, 4, 5, 6])),
    "alcohol_binge_BD2_31_ge2": bd31.ge(2).astype(float).where(bd31.isin([1, 2, 3, 4, 5])),
    "alcohol_heavy_amount_BD2_1_ge3": bd21.ge(3).astype(float).where(bd21.isin([1, 2, 3, 4, 5])),
}
rows = []
for k, s in E.items():
    s = pd.to_numeric(s, errors="coerce")
    rows.append({"construct": k, "n": int(s.notna().sum()),
                 "prev": round(float(s.mean()), 4) if s.notna().any() else None,
                 "male": round(float(s[sex == 1].mean()), 4) if s.notna().any() else None,
                 "female": round(float(s[sex == 2].mean()), 4) if s.notna().any() else None})
res = pd.DataFrame(rows)
print(res.to_string(index=False))

print("\nREFERENCE (Korean adults 40+): current smoking ~25% (M ~45-50%, F ~5-8%); "
      "ever smoking ~40% (M ~70-75%, F ~8-10%);")
print("                              past-year drinking ~55-65%; monthly+ drinking ~50%")
res.to_csv(ROOT / ".audit_tmp/knhanes_v2_corrected_constructs.csv",
           index=False, encoding="utf-8-sig")

print("\n=== sanity: does BS3_1 code 3 exist in ANY wave? ===")
s3 = num("BS3_1")
for w, g in s3.groupby(d["wave"]):
    codes = sorted(g.dropna().unique().tolist())
    print(f"  {int(w)}: codes={codes}  n3={int((g==3).sum())}")
