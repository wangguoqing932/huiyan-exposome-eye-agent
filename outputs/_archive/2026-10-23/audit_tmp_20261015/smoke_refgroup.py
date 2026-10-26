"""Decisive test: does the NHANES 'current_smoking' exposure use the right reference group?

Repo definition (scripts/evaluate.py:143-144):
    smk = q("SMQ040"); current_smoking = smk.isin([1,2]).where(smk.isin([1,2,3]))
NHANES SMQ040 is asked ONLY of SMQ020==1 ("smoked >=100 cigarettes in life").
So the reference group is FORMER smokers, not never-smokers.
"""
import sys, math
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm
warnings = __import__("warnings"); warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")
CYCLES = {"2005-2006": "_D", "2007-2008": "_E"}

def load(cycles, files):
    parts = []
    for cyc, suf in cycles.items():
        frames = {}
        for base in files:
            p = NH / cyc / f"{base}{suf}.XPT"
            if not p.exists():
                continue
            df = pd.read_sas(str(p), format="xport", encoding="utf-8")
            if "SEQN" in df.columns:
                df = df.set_index("SEQN")
            frames[base] = df
        out = None
        for m, df in frames.items():
            if out is None:
                out = df
            else:
                ov = [c for c in df.columns if c in out.columns]
                out = out.join(df.drop(columns=ov), how="outer")
        parts.append(out.reset_index())
    return pd.concat(parts, ignore_index=True, sort=False)

d = load(CYCLES, ["DEMO", "SMQ", "VIQ"])
d = d[pd.to_numeric(d["RIDAGEYR"], errors="coerce") >= 40]
d = d[pd.to_numeric(d["WTMEC2YR"], errors="coerce") > 0]
print("analytic frame (age>=40, wt>0):", len(d))

q = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)
smq020, smq040 = q("SMQ020"), q("SMQ040")
y = (q("VIQ071") == 1).astype(float).where(q("VIQ071").notna())

print("\n--- raw cross-tab SMQ020 (ever smoked 100+) x SMQ040 (now smoke) ---")
print(pd.crosstab(smq020, smq040, dropna=False))

# (a) repo definition
repo = smq040.isin([1, 2]).astype(float).where(smq040.isin([1, 2, 3]))
# (b) correct: never / former / current with never as reference
never   = (smq020 == 2).astype(float)
former  = ((smq020 == 1) & (smq040 == 3)).astype(float)
current = ((smq020 == 1) & smq040.isin([1, 2])).astype(float)
valid3 = (smq020.isin([1, 2]) & (smq040.isin([1, 2, 3]) | (smq020 == 2))).astype(bool)

cov = pd.DataFrame({
    "age": q("RIDAGEYR"), "age2": q("RIDAGEYR") ** 2 / 100,
    "sex": q("RIAGENDR"), "race": q("RIDRETH1"), "pir": q("INDFMPIR"),
})
w = q("WTMEC2YR")

def fit(xcol, sub_mask, label):
    sub = pd.DataFrame({"y": y, "x": xcol}).join(cov).dropna()
    sub = sub[sub["y"].isin([0, 1])]
    if sub_mask is not None:
        sub = sub[sub_mask.reindex(sub.index).fillna(False)]
    sub = sub[sub["x"].notna()]
    ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
    if len(sub) < 100 or ny < 20 or nx < 20:
        print(f"{label:52s} n={len(sub)} events={ny} exposed={nx} -> UNDERpowered")
        return
    X = sm.add_constant(sub[["x", "age", "age2", "sex", "race", "pir"]].astype(float))
    ww = w.reindex(sub.index).astype(float)
    ww = ww.where(ww > 0, 1.0) / ww.mean()
    f = sm.GLM(sub["y"].astype(float), X, family=sm.families.Binomial(), freq_weights=ww).fit()
    orv = math.exp(f.params["x"]); p = f.pvalues["x"]
    print(f"{label:52s} n={len(sub):5d} events={ny:4d} exposed={nx:5d} "
          f"prev={nx/len(sub):5.3f}  OR={orv:6.3f} p={p:.4g}")

print("\n=== cataract (VIQ071) regressions, same covariates as evaluate.py ===")
fit(repo, None, "(a) REPO: SMQ040 in(1,2) vs former only  [x=current]")
fit(current, valid3, "(b) FIXED: current vs (never+former)          [x=current]")
fit(former, smq020.isin([1, 2]) & smq040.isin([1, 2, 3]), "(c) former vs never                           [x=former]")
fit(current, smq020.isin([1, 2]) & smq040.isin([1, 2, 3]), "(d) current vs never                          [x=current]")
fit((smq020 == 1).astype(float), None, "(e) ever vs never                             [x=ever]")
