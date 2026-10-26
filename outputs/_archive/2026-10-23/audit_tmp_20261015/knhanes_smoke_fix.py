"""Quantify the KNHANES smoking variable error: repo BS1_1==1 vs correct BS3_1 in {1,2}."""
import warnings, glob, math
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings("ignore")

parts = []
for p in sorted(glob.glob("data/raw/knhanes_frames/knhanes_20*.csv")):
    parts.append(pd.read_csv(p, low_memory=False))
d = pd.concat(parts, ignore_index=True, sort=False)
d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
d = d[pd.to_numeric(d["wt_itvex"], errors="coerce") > 0]
print("KNHANES analytic frame (age>=40):", len(d))

q = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)
sex = q("sex")
repo = (q("BS1_1") == 1).astype(float).where(q("BS1_1").isin([1, 2, 3]))
fix = q("BS3_1").isin([1, 2]).astype(float).where(q("BS3_1").isin([1, 2, 8]))

print(f"\nrepo  current_smoking = BS1_1==1 : prev={repo.mean():.4f} "
      f"(M {repo[sex==1].mean():.4f} / F {repo[sex==2].mean():.4f}) n={int(repo.notna().sum())}")
print(f"fix   current_smoking = BS3_1 in(1,2): prev={fix.mean():.4f} "
      f"(M {fix[sex==1].mean():.4f} / F {fix[sex==2].mean():.4f}) n={int(fix.notna().sum())}")
print("  [Korea 2008 national adult current-smoking reference: overall ~28%, men ~48%, women ~10%]")

def bi(*cands):
    cols = [q(c) for c in cands if c in d.columns]
    if not cols:
        return pd.Series(np.nan, index=d.index)
    m = pd.concat(cols, axis=1)
    graded = m.isin([0, 1])
    return (m == 1).any(axis=1).astype(float).where(graded.any(axis=1))

outcomes = {
    "cataract_any": bi("DH2_lt"),
    "retinopathy_any": bi("E_DRP_R", "E_DRP_L"),
    "amd_early": bi("E_AMD_ELY_R", "E_AMD_ELY_L"),
    "amd_late": bi("E_AMD_LATE_R", "E_AMD_LATE_L"),
}
cov = pd.DataFrame({"age": q("age"), "age2": q("age") ** 2 / 100, "sex": sex})
w = q("wt_itvex")

def fit(x, y, label):
    sub = pd.DataFrame({"y": y, "x": x}).join(cov).dropna()
    sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
    ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
    if len(sub) < 200 or ny < 30 or nx < 30:
        print(f"  {label:46s} n={len(sub)} events={ny} exposed={nx} -> underpowered")
        return
    X = sm.add_constant(sub[["x", "age", "age2", "sex"]].astype(float))
    ww = w.reindex(sub.index).astype(float); ww = ww.where(ww > 0, 1.0) / ww.mean()
    f = sm.GLM(sub["y"].astype(float), X, family=sm.families.Binomial(), freq_weights=ww).fit()
    print(f"  {label:46s} n={len(sub):5d} events={ny:4d} OR={math.exp(f.params['x']):6.3f} "
          f"CI=[{math.exp(f.params['x']-1.96*f.bse['x']):.2f},{math.exp(f.params['x']+1.96*f.bse['x']):.2f}] "
          f"p={f.pvalues['x']:.4g}")

for name, y in outcomes.items():
    print(f"\n== {name} ==")
    fit(repo, y, "REPO  BS1_1==1")
    fit(fix, y, "FIXED BS3_1 in (1,2)")
