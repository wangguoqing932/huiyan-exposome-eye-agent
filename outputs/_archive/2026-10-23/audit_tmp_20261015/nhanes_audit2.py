"""NHANES audit round 2: unit / existence verification for the variables that
round 1 found suspicious, plus what modules exist on disk to unlock rules.
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")
CYCLES = {"2005-2006": "_D", "2007-2008": "_E"}


def load(cyc, base):
    p = NH / cyc / f"{base}{CYCLES[cyc]}.XPT"
    if not p.exists():
        return None
    d = pd.read_sas(str(p), format="xport", encoding="utf-8")
    return d.set_index("SEQN").reset_index() if "SEQN" in d.columns else d


# ---- 1. what module files actually exist on disk (2005-2008)?
print("=== NHANES module files available (2005-2008) ===")
for cyc, suf in CYCLES.items():
    files = sorted(p.name for p in (NH / cyc).glob("*.XPT"))
    print(f"{cyc}: {len(files)} files")
    for key in ["VID", "VIT", "DIQ", "CRP", "BIOPRO", "PBCD", "GHB", "GLU",
                "DR1TOT", "DR2TOT", "ALQ", "SMQ", "VIX", "OPXRET", "BMX"]:
        hit = [f for f in files if f.upper().startswith(key)]
        if hit:
            print(f"   {key:8s} -> {hit}")

# ---- 2. LBXCRP units
print("\n=== LBXCRP (hsCRP) distribution + implied units ===")
crp = []
for cyc in CYCLES:
    d = load(cyc, "CRP")
    if d is None:
        print(f"  {cyc}: CRP module missing"); continue
    print(f"  {cyc} CRP columns: {[c for c in d.columns if 'CRP' in c.upper()]}")
    for c in [c for c in d.columns if c.upper().startswith("LBX")]:
        s = pd.to_numeric(d[c], errors="coerce").dropna()
        print(f"    {c}: n={len(s)} min={s.min():.3g} p25={s.quantile(.25):.3g} "
              f"med={s.median():.3g} p75={s.quantile(.75):.3g} max={s.max():.3g}")
        for thr, lab in [(3.0, ">3.0"), (0.3, ">0.3"), (1.0, ">1.0")]:
            print(f"      {lab}: {100*(s > thr).mean():.2f}%")
        crp.append(s)
c = pd.concat(crp)
print(f"  POOLED n={len(c)}")
for thr, lab in [(0.3, ">0.3 mg/dL (=3 mg/L, AHA high-risk)"), (1.0, ">1.0 mg/dL (=10 mg/L)"),
                 (3.0, ">3.0 (as coded)")]:
    print(f"    {lab}: {100*(c > thr).mean():.2f}%")

# ---- 3. LBXSUA uric acid units / sex pattern
print("\n=== LBXSUA (uric acid) ===")
parts = []
for cyc in CYCLES:
    d = load(cyc, "DEMO"); b = load(cyc, "BIOPRO")
    if d is None or b is None:
        continue
    m = d[["SEQN", "RIDAGEYR", "RIAGENDR"]].merge(
        b[["SEQN", "LBXSUA"]], on="SEQN", how="inner")
    parts.append(m)
ua = pd.concat(parts)
ua = ua[pd.to_numeric(ua.RIDAGEYR, errors="coerce") >= 40]
u = pd.to_numeric(ua.LBXSUA, errors="coerce")
print(f"  n={u.notna().sum()} min={u.min():.2f} med={u.median():.2f} max={u.max():.2f}")
for sx, lab in [(1, "male"), (2, "female")]:
    s = u[ua.RIAGENDR == sx]
    print(f"  {lab}: n={s.notna().sum()} med={s.median():.2f} "
          f">=6.8(m)/5.7(f): {100*(s >= (6.8 if sx==1 else 5.7)).mean():.1f}%")
print("  -> mg/dL reference: men 3.5-7.2, women 2.6-6.0; hyperuricemia >7.0 (M) / >5.7 (F)")

# ---- 4. what vitamin/antioxidant columns does DR1TOT actually have?
print("\n=== DR1TOT nutrient columns available (vitamins / carotenoids) ===")
d = load("2005-2006", "DR1TOT")
if d is not None:
    cols = [c for c in d.columns if c.upper().startswith("DR1T")]
    print(f"  total DR1T* columns: {len(cols)}")
    for key in ["VC", "VE", "VK", "LZ", "BTO", "BCA", "CRYP", "LYC", "ATOC", "FOLA", "VIT"]:
        hit = [c for c in cols if key in c.upper()]
        if hit:
            print(f"   {key:6s} -> {hit}")
    print(f"  all: {cols}")

# ---- 5. correct alcohol definitions
print("\n=== alcohol: candidate definitions ===")
parts = []
for cyc in CYCLES:
    d = load(cyc, "DEMO"); a = load(cyc, "ALQ")
    if d is None or a is None:
        continue
    keep = [c for c in ["ALQ101", "ALQ110", "ALQ120Q", "ALQ120U", "ALQ130"] if c in a.columns]
    parts.append(d[["SEQN", "RIDAGEYR"]].merge(a[["SEQN"] + keep], on="SEQN", how="inner"))
al = pd.concat(parts, ignore_index=True)
al = al[pd.to_numeric(al.RIDAGEYR, errors="coerce") >= 40]
n = len(al)
a101 = pd.to_numeric(al.ALQ101, errors="coerce")
a110 = pd.to_numeric(al.ALQ110, errors="coerce")
a120q = pd.to_numeric(al.ALQ120Q, errors="coerce")
print(f"  analytic n={n}")
print(f"  ALQ101==1 (repo 'alcohol_intake', LIFETIME >=12 ever): {100*(a101==1).mean():.1f}%")
past_year = ((a101 == 1) | (a110 == 1))
print(f"  (ALQ101==1 | ALQ110==1)  past-year >=12 drinks:        {100*past_year.mean():.1f}%")
ct = (a120q >= 1)
print(f"  ALQ120Q>=1 (drinking days in past yr, among asked):    "
      f"{100*ct.mean():.1f}%  (denominator incl. NaN as 0)")
print(f"  ALQ130>=2 (>=2 drinks/drinking day):                   "
      f"{100*(pd.to_numeric(al.ALQ130, errors='coerce')>=2).mean():.1f}%")
lifetime_abst = ((a101 == 2) & (a110 == 2))
print(f"  lifetime abstainer (ALQ101==2 & ALQ110==2):            {100*lifetime_abst.mean():.1f}%")
print("  cross-tab ALQ101 x ALQ110:")
print(pd.crosstab(a101, a110, dropna=False))
