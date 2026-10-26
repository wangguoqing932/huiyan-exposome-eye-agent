"""Audit: replicate evaluate_knhanes exposure construction and report prevalence."""
import sys, warnings, glob
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_knhanes import build_knhanes_exposures, build_knhanes_outcomes

FR = ROOT / "data/raw/knhanes_frames"
parts = []
for p in sorted(FR.glob("knhanes_20*.csv")):
    parts.append(pd.read_csv(p, low_memory=False))
d = pd.concat(parts, ignore_index=True, sort=False)
print("raw frame rows:", len(d), " waves:", d["year"].nunique() if "year" in d else "?")
d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
w = "wt_itvex" if "wt_itvex" in d.columns else ("wt_itv" if "wt_itv" in d.columns else "wt_ex")
d = d[pd.to_numeric(d.get(w, 0), errors="coerce") > 0]
print("analytic frame (age>=40 & wt>0):", len(d))

E = build_knhanes_exposures(d)
B = build_knhanes_outcomes(d)
sex = pd.to_numeric(d["sex"], errors="coerce")
rows = []
for name, s in E.items():
    s = pd.to_numeric(s, errors="coerce")
    rows.append({"var": "E:" + name, "n_nonmiss": int(s.notna().sum()),
                 "prev_overall": round(float(s.mean()), 4),
                 "prev_male": round(float(s[sex == 1].mean()), 4),
                 "prev_female": round(float(s[sex == 2].mean()), 4)})
for name, s in B.items():
    s = pd.to_numeric(s, errors="coerce")
    rows.append({"var": "O:" + name, "n_nonmiss": int(s.notna().sum()),
                 "prev_overall": round(float(s.mean()), 4),
                 "prev_male": round(float(s[sex == 1].mean()), 4),
                 "prev_female": round(float(s[sex == 2].mean()), 4)})
out = pd.DataFrame(rows)
print(out.to_string(index=False))

print("\n--- corroborating raw columns (full frame, all ages) ---")
for c in ["BS1_1", "BA2_2_1", "BA2_22", "HE_UAScr", "HE_UAScr_AAS", "HE_Uacid"]:
    if c in d.columns:
        vc = d[c].value_counts(dropna=False).sort_index()
        print(f"{c:14s} " + " ".join(f"{k}={v}" for k, v in list(vc.items())[:8]))
    else:
        print(f"{c:14s} ABSENT from analytic frame")
