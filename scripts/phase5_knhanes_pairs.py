#!/usr/bin/env python
"""huiyan executor phase5 — KNHANES pair-level validation (external_validation, cross-country).

Mirrors scripts/phase5_nhanes_pairs.py with KNHANES variable drift resolution.
- Frames: data/raw/knhanes_frames/knhanes_20XX.csv (eye+all merged by ID; 2008-12 + 2017-21).
- Sample: age>=40; weights wt_itvex normalized (mean 1). Covariates: age, sex (+age^2).
- Exposure var candidates resolved per year: uric [HE_Uacid, HE_UAScr, HE_UAScr_AAS]; glu [HE_glu];
  HbA1c [HE_HbA1c, HE_DM_HbA1c]; lipids [HE_chol/HE_TG/HE_HDL/HE_LDL]; CRP [HE_hsCRP]; BMI [HE_BMI];
  smoking BS1_1==1 (current). KNHANES pass-1 exclusions (documented): alcohol (var drift), diet-derived
  (24h recall not merged), metals/PM2.5 (not in all-table), vitamin D (not resolved).
- Outcomes per wave: cataract_any DH2_lt==1 (2008-12); glaucoma_selfreport DH3_lt==1 (2008-12);
  retinopathy_any E_DRP_R/L==1; amd_early E_AMD_ELY_R/L==1; amd_late E_AMD_LATE_R/L==1;
  glaucoma_iop_elevated IOP>21 [E_Gr_p,E_Pr_1,E_GR]; glaucoma_suspect_cdr E_Grv/E_Glv>=0.7 (2008-12);
  vision_impairment (any) E_VS_DS==1 (2008-12). VA severity ladder deferred (E_Cr_1 is 1-6 graded,
  codebook mapping pending - honest note).
Run: PYTHONUTF8=1 python scripts/phase5_knhanes_pairs.py
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
FR = ROOT / "data" / "raw" / "knhanes_frames"

def first_col(d: pd.DataFrame, cands: list[str]) -> str | None:
    for c in cands:
        if c in d.columns:
            return c
    lc = {c.lower(): c for c in d.columns}
    for c in cands:
        if c.lower() in lc:
            return lc[c.lower()]
    return None

def load_frames() -> pd.DataFrame:
    parts = []
    for p in sorted(FR.glob("knhanes_20*.csv")):
        d = pd.read_csv(p, low_memory=False)
        d["src_year"] = p.stem.split("_")[1]
        parts.append(d)
    return pd.concat(parts, ignore_index=True, sort=False)

def build(d: pd.DataFrame) -> pd.DataFrame:
    d = d[pd.to_numeric(d["age"], errors="coerce") >= 40].copy()
    w = first_col(d, ["wt_itvex", "wt_itv", "wt_ex"])
    if w:
        d["weight"] = pd.to_numeric(d[w], errors="coerce")
        d = d[d["weight"] > 0]
    return d

def expo_defs(d: pd.DataFrame) -> dict[str, pd.Series]:
    def num(cands):
        c = first_col(d, cands)
        return pd.to_numeric(d[c], errors="coerce") if c else pd.Series(np.nan, index=d.index)
    sex = pd.to_numeric(d["sex"], errors="coerce")
    ua = num(["HE_Uacid", "HE_UAScr", "HE_UAScr_AAS"])
    if ua.notna().sum() and ua.median() < 3.0:  # unit sanity (mmol/L -> mg/dL)
        ua = ua * 16.8
    e: dict[str, pd.Series] = {}
    e["uric_acid_elevated"] = (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype("float").where(ua.notna())
    glu = num(["HE_glu"])
    e["hyperglycemia"] = (glu >= 126).astype("float").where(glu.notna())
    gh = num(["HE_HbA1c", "HE_DM_HbA1c"])
    e["hba1c_elevated"] = (gh >= 6.5).astype("float").where(gh.notna())
    tc, tg = num(["HE_chol", "HE_CHOL"]), num(["HE_TG", "HE_HTG"])
    hdl, ldl = num(["HE_HDL"]), num(["HE_LDL", "HE_LDL_drct"])
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype("float").where(lip.notna().any(axis=1))
    crp = num(["HE_hsCRP"])
    e["crp_elevated"] = (crp > 3.0).astype("float").where(crp.notna())
    bmi = num(["HE_BMI"])
    e["bmi_high"] = (bmi >= 25).astype("float").where(bmi.notna())
    c = first_col(d, ["BS1_1"])
    smk = pd.to_numeric(d[c], errors="coerce") if c else pd.Series(np.nan, index=d.index)
    e["current_smoking"] = (smk == 1).astype("float").where(smk.isin([1, 2, 3]))
    return e

def outc_defs(d: pd.DataFrame) -> dict[str, pd.Series]:
    def bi(cands, yes=(1,)):
        c = first_col(d, cands)
        s = pd.to_numeric(d[c], errors="coerce") if c else pd.Series(np.nan, index=d.index)
        return s.isin(list(yes)).astype("float").where(s.notna())
    o: dict[str, pd.Series] = {}
    o["cataract_any"] = bi(["DH2_lt"])
    o["glaucoma_selfreport"] = bi(["DH3_lt"])
    o["retinopathy_any"] = bi(["E_DRP_R", "E_DRP_L"])
    o["amd_early"] = bi(["E_AMD_ELY_R", "E_AMD_ELY_L"])
    o["amd_late"] = bi(["E_AMD_LATE_R", "E_AMD_LATE_L", "E_AMD_WET_R", "E_AMD_WET_L"])
    o["vision_impairment_moderate"] = bi(["E_VS_DS"])  # any VI (severity ladder deferred, honest)
    iopc = first_col(d, ["E_Gr_p", "E_Pr_1", "E_GR"])
    iop = pd.to_numeric(d[iopc], errors="coerce") if iopc else pd.Series(np.nan, index=d.index)
    iop = iop.where(iop < 80)
    o["glaucoma_iop_elevated"] = (iop > 21).astype("float").where(iop.notna())
    cdrc = [c for c in ("E_Grv", "E_Glv") if c in d.columns]
    if cdrc:
        cdr = pd.concat([pd.to_numeric(d[c], errors="coerce") for c in cdrc], axis=1).max(axis=1)
        cdr = cdr.where(cdr <= 1.0)
        o["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype("float").where(cdr.notna())
    return o

def bh_fdr(p: pd.Series) -> pd.Series:
    p = p.fillna(1.0); n = len(p)
    q = p * n / p.rank(method="first")
    return q.clip(upper=1.0)

def main() -> int:
    d = build(load_frames())
    print(f"frame: n={len(d)} waves={d['src_year'].nunique()}")
    E, B = expo_defs(d), outc_defs(d)
    age = pd.to_numeric(d["age"], errors="coerce")
    sex = pd.to_numeric(d["sex"], errors="coerce")
    cov = pd.DataFrame({"age": age, "age2": age ** 2 / 100, "sex": sex})
    rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    pos: dict[tuple[str, str], dict] = {}
    for r in rules:
        for b in r["entity_b_flags"]:
            for a in r["entity_a_flags"]:
                pos[(a, b)] = {"rule": r["id"], "level": r.get("evidence_level", "?"), "dir": r.get("direction", "risk_up")}
    rows = []
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30 or ny > len(sub) - 30:
                rows.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos_outcome": ny,
                             "or": np.nan, "p": np.nan, "status": "underpowered_or_unmeasured",
                             "predicted": (a_flag, b_item) in pos})
                continue
            X = sm.add_constant(sub[["x", "age", "age2", "sex"]].astype(float))
            y = sub["y"].astype(float)
            w = d.loc[sub.index, "weight"].clip(lower=1); w = w / w.mean()
            try:
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
                beta, se = fit.params["x"], fit.bse["x"]
                rows.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos_outcome": ny,
                             "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                             "ci_hi": math.exp(beta + 1.96 * se), "p": float(fit.pvalues["x"]),
                             "status": "tested", "predicted": (a_flag, b_item) in pos})
            except Exception as ex:
                rows.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos_outcome": ny,
                             "or": np.nan, "p": np.nan, "status": f"fit_fail:{type(ex).__name__}",
                             "predicted": (a_flag, b_item) in pos})
    res = pd.DataFrame(rows)
    m = res["status"] == "tested"
    res.loc[m, "q"] = bh_fdr(res.loc[m, "p"])
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
    f1 = 2 * prec * rec / (prec + rec) if prec + rec and prec + rec == prec + rec else float("nan")
    # generalization gap vs NHANES (rule pairs)
    gap = []
    try:
        nh = pd.read_csv(ROOT / "outputs" / "tables" / "nhanes_pair_results.csv")
        rr = res[m].set_index(["a_flag", "b_item"])
        for (a, b), meta in pos.items():
            if (a, b) in rr.index and ((a, b) in set(zip(nh["a_flag"], nh["b_item"]))):
                k_gold = "gold_positive" if (rr.loc[(a, b), "gold"] == "gold_positive") else "gold_negative"
                nhrow = nh[(nh.a_flag == a) & (nh.b_item == b)].iloc[0]
                gap.append({"a": a, "b": b, "level": meta["level"], "kn_or": rr.loc[(a, b), "or"],
                            "kn_gold": k_gold, "nh_or": nhrow.get("or"), "nh_gold": nhrow.get("gold")})
    except Exception as ex:
        print("gap join skipped:", ex)
    metrics = {"dataset": "KNHANES-2008-21(40+)", "pairs_tested": int(m.sum()),
               "pairs_underpowered": int((~m).sum()), "rule_pairs_tested": int(t["predicted"].sum()),
               "TP": tp, "FP": fp, "FN": fn, "TN": tn,
               "precision": round(prec, 3) if prec == prec else None,
               "recall": round(rec, 3) if rec == rec else None,
               "F1": round(f1, 3) if f1 == f1 else None,
               "notes": ["covariates age/sex only (edu/PIR not in converted frames - documented)",
                         "alcohol/diet/metals/PM2.5/vitD pairs not testable this pass (var drift or not merged)",
                         "VA severity ladder deferred (E_Cr_1 graded 1-6, codebook pending) -> VI(any) only"]}
    out_t = ROOT / "outputs" / "tables"; out_t.mkdir(parents=True, exist_ok=True)
    res.to_csv(out_t / "knhanes_pair_results.csv", index=False, encoding="utf-8-sig")
    (out_t / "knhanes_pair_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(gap).to_csv(out_t / "generalization_gap_pairs.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
