#!/usr/bin/env python
"""huiyan executor phase5 — CHARLS pair-level validation (external_validation, cohort layer 1/9).

Cohort arm per PHASE3B §1.4: self-report outcomes only (cataract_any via surgery da035/da036,
glaucoma_selfreport da037); per-cohort run then combine. CHARLS 2011 wave.
- Frame: demographic(ba004 age, rgender) + health(da033-037, da059/061 smoking, da067 alcohol)
  + Blood_20140429(newua/newglu/newhba1c/newcho/newtg/newhdl/newldl/newcrp) + weight(ind_weight).
- Exposables: uric (unit sanity µmol/L->mg/dL), glucose, hba1c, dyslipidemia, crp, smoking, alcohol.
  (BMI/diet/metals/PM2.5/UV not available in this merge - coverage note.)
- Covariates age/sex; weights ind_weight normalized.
- Vision self-rated (da033/da034) kept as exploratory contrast layer (not in the 15-item primary list).
Run: PYTHONUTF8=1 python scripts/phase5_charls_pairs.py
"""
from __future__ import annotations
import json, math, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import statsmodels.api as sm

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
CH = Path(r"E:\BaiduNetdiskDownload\所有数据库\01. CHARLS 中国健康与养老追踪调查\CHARLS_中国\Raw_data\2011charls")

def rd(name, cols):
    df = pd.read_stata(CH / name, columns=cols)
    lab = pd.io.stata.StataReader(CH / name).variable_labels()
    return df.rename(columns={c: lab.get(c, c) for c in cols})

def build() -> pd.DataFrame:
    demo = pd.read_stata(CH / "demographic_background.dta", columns=["ID", "rgender", "ba004", "ba002_1"])
    hlth = pd.read_stata(CH / "health_status_and_functioning.dta",
                         columns=["ID", "da033", "da034", "da035", "da036", "da037", "da059", "da061", "da067"])
    blood = pd.read_stata(CH / "Blood_20140429.dta",
                          columns=["ID", "newua", "newglu", "newhba1c", "newcho", "newtg", "newhdl", "newldl", "newcrp"])
    wgt = pd.read_stata(CH / "weight.dta", columns=["ID", "ind_weight"])
    d = demo.merge(hlth, on="ID", how="inner").merge(blood, on="ID", how="left").merge(wgt, on="ID", how="left")
    by = pd.to_numeric(d["ba002_1"], errors="coerce")
    age = 2011 - by
    age = age.fillna(pd.to_numeric(d["ba004"], errors="coerce"))
    d["age_calc"] = age
    d = d[age >= 45]
    d = d[pd.to_numeric(d["ind_weight"], errors="coerce") > 0]
    return d

def code(s: pd.Series) -> pd.Series:
    """CHARLS labeled categoricals like '1 Yes'/'2 No' -> numeric code."""
    return pd.to_numeric(s.astype(str).str.strip().str.split().str[0], errors="coerce")

def expo(d):
    def n(c): return pd.to_numeric(d[c], errors="coerce")
    sex = code(d["rgender"])
    ua = n("newua")
    if ua.notna().sum() and ua.median() > 100:  # µmol/L -> mg/dL
        ua = ua / 16.8
    e = {}
    e["uric_acid_elevated"] = (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype(float).where(ua.notna())
    glu = n("newglu")
    e["hyperglycemia"] = (glu >= 126).astype(float).where(glu.notna())
    gh = n("newhba1c")
    e["hba1c_elevated"] = (gh >= 6.5).astype(float).where(gh.notna())
    tc, tg, hdl, ldl = n("newcho"), n("newtg"), n("newhdl"), n("newldl")
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    crp = n("newcrp")
    e["crp_elevated"] = (crp > 3.0).astype(float).where(crp.notna())
    s1, s2 = code(d["da059"]), code(d["da061"])
    e["current_smoking"] = ((s1 == 1) & (s2 == 1)).astype(float).where(s1.notna() & s2.notna())
    alc = code(d["da067"])
    e["alcohol_intake"] = (alc == 1).astype(float).where(alc.notna())
    return e

def outc(d):
    o = {}
    cat = code(d["da035"])
    o["cataract_any"] = (cat == 1).astype(float).where(cat.notna())
    glc = code(d["da037"])
    o["glaucoma_selfreport"] = (glc == 1).astype(float).where(glc.notna())
    return o

def fdr_bhy(p):
    """Benjamini-Yekutieli step-up FDR（analysis_plan.md §7），含单调化。

    审核 141：原 `p*n/rank` 缺累积最小值步 → q 非单调；审核 F5：原非 BHY；
    审核 148：原 `fillna(1.0)` 掩盖退化拟合的 NaN p。
    """
    p = pd.Series(p).astype(float)
    q = pd.Series(np.nan, index=p.index, dtype=float)
    pv = p.dropna()
    n = len(pv)
    if n:
        order = pv.sort_values(kind="mergesort")
        c_n = float(np.sum(1.0 / np.arange(1, n + 1)))
        ranked = order.to_numpy() * n * c_n / np.arange(1, n + 1)
        ranked = np.minimum.accumulate(ranked[::-1])[::-1]
        q.loc[order.index] = np.clip(ranked, 0.0, 1.0)
    return q

bh = fdr_bhy  # 兼容旧调用点名称

def main() -> int:
    d = build()
    print(f"CHARLS frame n={len(d)}")
    E, B = expo(d), outc(d)
    age = pd.to_numeric(d["age_calc"], errors="coerce")
    sex = code(d["rgender"])
    cov = pd.DataFrame({"age": age, "age2": age ** 2 / 100, "sex": sex})
    rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    pos = {}
    for r in rules:
        for b in r["entity_b_flags"]:
            for a in r["entity_a_flags"]:
                pos[(a, b)] = {"rule": r["id"], "level": r.get("evidence_level", "?"), "dir": r.get("direction", "risk_up")}
    rows = []
    for a, ev in E.items():
        for b, ov in B.items():
            sub = pd.DataFrame({"y": ov, "x": ev}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30:
                rows.append({"a_flag": a, "b_item": b, "n": len(sub), "n_pos_outcome": ny, "or": np.nan,
                             "p": np.nan, "status": "underpowered_or_unmeasured", "predicted": (a, b) in pos})
                continue
            X = sm.add_constant(sub[["x", "age", "age2", "sex"]].astype(float))
            w = pd.to_numeric(d.loc[sub.index, "ind_weight"], errors="coerce").clip(lower=1)
            w = w / w.mean()
            try:
                fit = sm.GLM(sub["y"].astype(float), X, family=sm.families.Binomial(), freq_weights=w).fit()
                beta, se = fit.params["x"], fit.bse["x"]
                rows.append({"a_flag": a, "b_item": b, "n": len(sub), "n_pos_outcome": ny,
                             "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                             "ci_hi": math.exp(beta + 1.96 * se), "p": float(fit.pvalues["x"]),
                             "status": "tested", "predicted": (a, b) in pos})
            except Exception as ex:
                rows.append({"a_flag": a, "b_item": b, "n": len(sub), "n_pos_outcome": ny, "or": np.nan,
                             "p": np.nan, "status": f"fit_fail:{type(ex).__name__}", "predicted": (a, b) in pos})
    res = pd.DataFrame(rows)
    m = res["status"] == "tested"
    res.loc[m, "q"] = bh(res.loc[m, "p"])
    def gold(r):
        if r["status"] != "tested":
            return "not_tested"
        meta = pos.get((r["a_flag"], r["b_item"]))
        want_lt = bool(meta and meta["dir"] == "risk_down")
        sig = (not np.isnan(r["q"])) and r["q"] < 0.05
        good = (r["or"] < 1) if want_lt else (r["or"] > 1)
        return "gold_positive" if (sig and good) else "gold_negative"
    res["gold"] = res.apply(gold, axis=1)
    t = res[m]
    tp = int((t["predicted"] & (t["gold"] == "gold_positive")).sum())
    fp = int((t["predicted"] & (t["gold"] == "gold_negative")).sum())
    fn = int((~t["predicted"] & (t["gold"] == "gold_positive")).sum())
    tn = int((~t["predicted"] & (t["gold"] == "gold_negative")).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    metrics = {"dataset": "CHARLS-2011(45+)", "pairs_tested": int(m.sum()),
               "pairs_underpowered": int((~m).sum()), "rule_pairs_tested": int(t["predicted"].sum()),
               "TP": tp, "FP": fp, "FN": fn, "TN": tn,
               "precision": round(prec, 3) if prec == prec else None,
               "recall": round(rec, 3) if rec == rec else None,
               "notes": ["cohort arm layer 1/9: cataract_any(surgery)+glaucoma_selfreport only (coverage matrix)",
                         "BMI/diet/metals/PM2.5/UV exposures not in this merge (documented)",
                         "self-rated eyesight (da033/34) reserved as exploratory contrast, not scored"]}
    out = ROOT / "outputs" / "tables"
    res.to_csv(out / "charls_pair_results.csv", index=False, encoding="utf-8-sig")
    (out / "charls_pair_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
