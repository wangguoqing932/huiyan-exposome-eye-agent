#!/usr/bin/env python
"""huiyan executor phase5 — NHANES pair-level validation (internal_validation).

Design (PHASE3B §1.2 + PLAN §6):
- Cycles 2005-2006 + 2007-2008 (BIOPRO/OPXRET/PBCD overlap window); UV & serum carotenoids 2005-06 only.
- Sample: age>=40, MEC-examined (WTMEC2YR>0).
- Unit of analysis: (A-flag x B-item) pair. Rules => predicted positive; no rule => predicted negative.
- Gold: survey-weighted logistic per pair (freq_weights), covariates age/sex/race/edu/PIR (+BMI / +smoking when not the exposure);
  BH-FDR within dataset; positive = q<0.05 AND direction consistent (OR>1 risk; OR<1 protective).
- Outputs: outputs/tables/nhanes_pair_results.csv + nhanes_pair_metrics.json (+ coverage report).

Honesty notes:
- Weighted logistic (statsmodels GLM freq_weights) approximates NHANES design; full survey-design SEs (Taylor/PSU) deferred to sensitivity (documented).
- r01 (uric x cataract) expected gold-negative per our group's prior bi-cohort work (see docs/rule_rationale.md).
Run: PYTHONUTF8=1 .venv/Scripts/python.exe scripts/phase5_nhanes_pairs.py
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
NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")
CYCLES = {"2005-2006": "_D", "2007-2008": "_E"}

FILES = {  # module -> (base, per-cycle suffix)
    "DEMO": ("DEMO", True), "BIOPRO": ("BIOPRO", True), "VIQ": ("VIQ", True),
    "VIX": ("VIX", True), "OPXRET": ("OPXRET", True), "SMQ": ("SMQ", True),
    "ALQ": ("ALQ", True), "BMX": ("BMX", True), "CRP": ("CRP", True),
    "PBCD": ("PBCD", True), "DR1TOT": ("DR1TOT", True),
    "GLU": ("GLU", True), "GHB": ("GHB", True),
    "DEQ": ("DEQ", "D"), "VITAEC": ("VITAEC", "D"),  # 2005-06 only
}

def load_cycle(cycle_dir: Path, suf: str) -> pd.DataFrame:
    frames = {}
    for mod, (base, cyc) in FILES.items():
        if cyc is True:
            name = f"{base}{suf}.XPT"
        elif cyc == suf or (isinstance(cyc, str) and suf.endswith(cyc)):
            name = f"{base}{suf}.XPT"
        else:
            continue
        p = cycle_dir / name
        if not p.exists():
            continue
        df = pd.read_sas(str(p), format="xport", encoding="utf-8")
        cols = [c for c in df.columns if c not in ("SEQN",)]
        frames[mod] = df.set_index("SEQN")[cols]
    out = None
    for m, df in frames.items():
        if out is None:
            out = df
        else:
            overlap = [c for c in df.columns if c in out.columns]
            if overlap:
                df = df.drop(columns=overlap)  # first module wins (e.g., VIQ vars duplicated inside OPXRET)
            out = out.join(df, how="outer") if len(df.columns) else out
    return out.reset_index()

def build_frame() -> pd.DataFrame:
    parts = []
    for cyc, suf in CYCLES.items():
        df = load_cycle(NH / cyc, suf)
        df["cycle"] = cyc
        parts.append(df)
    d = pd.concat(parts, ignore_index=True)
    d = d[d["RIDAGEYR"] >= 40]
    wcol = "WTMEC2YR" if "WTMEC2YR" in d.columns else None
    d = d[(d[wcol] > 0) if wcol else True]
    return d

# ---------- exposure operationalization (A-flag -> binary) ----------
def expo_defs(d: pd.DataFrame) -> dict[str, pd.Series]:
    e: dict[str, pd.Series] = {}
    def q(col): return d[col] if col in d.columns else pd.Series(np.nan, index=d.index)
    e["uric_acid_elevated"] = (((q("LBXSUA") >= 6.8) & (d["RIAGENDR"] == 1)) | ((q("LBXSUA") >= 5.7) & (d["RIAGENDR"] == 2))).astype("float").where(q("LBXSUA").notna())  # NHANES mg/dL, sex-specific hyperuricemia
    glu = q("LBXGL") if "LBXGL" in d.columns else q("LBXSGL")
    e["hyperglycemia"] = ((glu >= 126) | (q("DIQ010") == 1)).astype("float").where(glu.notna() | q("DIQ010").notna())
    gh = q("LBXGH")
    e["hba1c_elevated"] = (gh >= 6.5).astype("float").where(gh.notna())
    tc, ldl, tg, hdl = q("LBXSCH"), q("LBDLDL") if "LBDLDL" in d else q("LBXTC"), q("LBXSTR"), q("LBDHDD") if "LBDHDD" in d else q("LBDHDL")
    lip = pd.concat([tc, ldl, tg, hdl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (ldl >= 160) | (tg >= 200) | (hdl < 40)).astype("float").where(lip.notna().any(axis=1))
    crp = q("LBXCRP")
    e["crp_elevated"] = (crp > 3.0).astype("float").where(crp.notna())
    e["bmi_high"] = (q("BMXBMI") >= 25).astype("float").where(q("BMXBMI").notna())
    vc, ve, lz = q("DR1TVC"), q("DR1TVE"), q("DR1TLZ")
    antio = pd.concat([vc, ve, lz], axis=1)
    comp = antio.mean(axis=1).where(antio.notna().sum(axis=1) >= 2)
    e["low_antioxidant_intake"] = (comp < comp.quantile(0.25)).astype("float").where(comp.notna())
    e["current_smoking"] = q("SMQ040").isin([1, 2]).astype("float").where(q("SMQ040").notna())
    alq = q("ALQ101") if "ALQ101" in d else q("ALQ110")
    e["alcohol_intake"] = (alq == 1).astype("float").where(alq.notna())
    for flag, col, nm in [("lead_exposure", "LBXBPB", "lead"), ("cadmium_exposure", "LBXBCD", "cadmium")]:
        s = q(col)
        cut = s.quantile(0.75)
        e[flag] = (s >= cut).astype("float").where(s.notna())
    pa = q("PAD320") if "PAD320" in d else q("PAD680")
    if pa.name in d.columns:
        e["physical_inactivity"] = (pa < 10).astype("float").where(pa.notna())  # sedentary proxy; exploratory
    if "DEQ038A" in d.columns:
        uv = d["DEQ038A"]
        e["uv_exposure"] = (uv == 1).astype("float").where(uv.notna())
    return e

# ---------- outcome operationalization (B-item -> binary) ----------
def outc_defs(d: pd.DataFrame) -> dict[str, pd.Series]:
    o: dict[str, pd.Series] = {}
    def q(col): return d[col] if col in d.columns else pd.Series(np.nan, index=d.index)
    o["cataract_any"] = (q("VIQ071") == 1).astype("float").where(q("VIQ071").notna())
    va = q("VIXPRS").where(q("VIXPRS") < 50)  # 88/999 codes excluded
    va = va.where(va > -5)
    o["vision_impairment_mild"] = (va > 0.30).astype("float").where(va.notna())
    o["vision_impairment_moderate"] = (va > 0.48).astype("float").where(va.notna())
    o["vision_impairment_severe"] = (va > 1.00).astype("float").where(va.notna())
    ret = q("OPDURL4")
    o["retinopathy_any"] = ret.isin([2, 3, 4]).astype("float").where(ret.notna())
    o["dr_npdr"] = ret.isin([2, 3]).astype("float").where(ret.notna())
    o["dr_pdr"] = (ret == 4).astype("float").where(ret.notna())
    arm = q("OPDUARM"); pig = q("OPDUPIGA")
    e1 = ((arm >= 1) | (pig >= 1)).astype("float").where(arm.notna() | pig.notna())
    o["amd_early"] = e1
    larm, ga, exu = q("OPDULARM"), q("OPDUGA"), q("OPDUEXU")
    o["amd_late"] = ((larm >= 1) | (ga >= 1) | (exu >= 1)).astype("float").where(larm.notna() | ga.notna() | exu.notna())
    cdr = pd.concat([q("OPDDVCDR"), q("OPDSVCDR")], axis=1).max(axis=1)
    o["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype("float").where(cdr.notna())
    return o

EDU = "DMDEDU2"  # fallback DMDEDU3 (some cycles)

def pick_cov(d: pd.DataFrame) -> list[str]:
    cols = ["RIDAGEYR", "RIAGENDR", "RIDRETH1"]
    for c in ("DMDEDU2", "DMDEDU3"):
        if c in d.columns:
            cols.append(c); break
    if "INDFMPIR" in d.columns:
        cols.append("INDFMPIR")
    return cols

def fdr_bhy(p: pd.Series) -> pd.Series:
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


bh_fdr = fdr_bhy  # 兼容旧调用点名称

def main() -> int:
    d = build_frame()
    print(f"analysis frame: n={len(d)}, cycles={d['cycle'].nunique()}")
    E = expo_defs(d); B = outc_defs(d)
    covars = pick_cov(d)
    cov = d[covars].copy()
    cov["RIAGENDR"] = cov["RIAGENDR"].astype("float")
    extra_bmi = pd.to_numeric(d["BMXBMI"], errors="coerce")
    extra_smk = (d["SMQ040"].isin([1, 2]) if "SMQ040" in d else np.nan).astype("float")
    rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))["rules"]
    pos_pairs: dict[tuple[str, str], dict] = {}
    for r in rules:
        for b in r["entity_b_flags"]:
            for a in r["entity_a_flags"]:
                pos_pairs[(a, b)] = {"rule": r["id"], "level": r.get("evidence_level", "?"), "dir": r.get("direction", "risk_up")}
    rows = []
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna(subset=["y", "x"])
            sub = sub.dropna(subset=["RIDAGEYR", "RIAGENDR"])
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            npos_y = int(sub["y"].sum()); npos_x = int(sub["x"].sum())
            if len(sub) < 200 or npos_y < 30 or npos_x < 30 or npos_y > len(sub) - 30:
                rows.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos_outcome": npos_y,
                             "or": np.nan, "p": np.nan, "q": np.nan, "status": "underpowered_or_unmeasured",
                             "predicted": (a_flag, b_item) in pos_pairs})
                continue
            X = sub[["x"] + covars].copy()
            X["RIDAGEYR2"] = X["RIDAGEYR"] ** 2 / 1000
            if a_flag != "bmi_high":
                X["bmi"] = extra_bmi.reindex(sub.index)
            if a_flag != "current_smoking":
                X["smoke"] = extra_smk.reindex(sub.index) if not isinstance(extra_smk, float) else np.nan
            X = pd.get_dummies(X, columns=[c for c in ("RIDRETH1", "DMDEDU2", "DMDEDU3") if c in X.columns], drop_first=True, dummy_na=True)
            X = X.astype(float)
            X = X.loc[:, X.notna().mean() > 0.7].fillna(X.median(numeric_only=True))
            X = sm.add_constant(X)
            y = sub["y"].astype(float)
            w = d.loc[sub.index, "WTMEC2YR"].astype(float).clip(lower=1)
            w = w / w.mean()  # normalize: effective n == sample n (freq_weights inflation fix)
            try:
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
                beta = fit.params["x"]; se = fit.bse["x"]
                orv = math.exp(beta); lo = math.exp(beta - 1.96 * se); hi = math.exp(beta + 1.96 * se)
                p = float(fit.pvalues["x"])
                rows.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos_outcome": npos_y,
                             "or": orv, "ci_lo": lo, "ci_hi": hi, "p": p, "status": "tested",
                             "predicted": (a_flag, b_item) in pos_pairs})
            except Exception as ex:
                rows.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos_outcome": npos_y,
                             "or": np.nan, "p": np.nan, "status": f"fit_fail:{type(ex).__name__}",
                             "predicted": (a_flag, b_item) in pos_pairs})
    res = pd.DataFrame(rows)
    m = res["status"] == "tested"
    res.loc[m, "q"] = res.loc[m].pipe(lambda x: bh_fdr(x["p"]))
    def gold(r):
        if r["status"] != "tested":
            return "not_tested"
        meta = pos_pairs.get((r["a_flag"], r["b_item"]))
        want_or = "<1" if (meta and meta["dir"] == "risk_down") else ">1"
        sig = (not np.isnan(r["q"])) and r["q"] < 0.05
        good_dir = (r["or"] < 1) if want_or == "<1" else (r["or"] > 1)
        return "gold_positive" if (sig and good_dir) else "gold_negative"
    res["gold"] = res.apply(gold, axis=1)
    tested = res[res["status"] == "tested"]
    tp = int(((tested["predicted"]) & (tested["gold"] == "gold_positive")).sum())
    fp = int(((tested["predicted"]) & (tested["gold"] == "gold_negative")).sum())
    fn = int(((~tested["predicted"]) & (tested["gold"] == "gold_positive")).sum())
    tn = int(((~tested["predicted"]) & (tested["gold"] == "gold_negative")).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec and rec and not math.isnan(prec + rec) else float("nan")
    metrics = {"dataset": "NHANES-2005-08", "pairs_tested": int(m.sum()),
               "pairs_underpowered": int((res["status"] != "tested").sum()),
               "rule_pairs_tested": int(tested["predicted"].sum()),
               "TP": tp, "FP": fp, "FN": fn, "TN": tn,
               "precision": round(prec, 3) if prec == prec else None,
               "recall": round(rec, 3) if rec == rec else None, "F1": round(f1, 3) if f1 == f1 else None,
               "by_level": {}}
    for lvl in ["A", "B", "C"]:
        keys = [k for k, v in pos_pairs.items() if v["level"] == lvl]
        mask = pd.Series([k in keys for k in zip(tested["a_flag"], tested["b_item"])], index=tested.index)
        sel = tested.loc[mask]
        if len(sel) == 0:
            metrics["by_level"][lvl] = {"rule_pairs": len(keys), "tested": 0, "TP": 0, "FP": 0}
            continue
        ltp = int(((sel["predicted"]) & (sel["gold"] == "gold_positive")).sum())
        lfp = int(((sel["predicted"]) & (sel["gold"] == "gold_negative")).sum())
        metrics["by_level"][lvl] = {"rule_pairs": len(keys), "tested": len(sel), "TP": ltp, "FP": lfp}
    out_t = ROOT / "outputs" / "tables"; out_t.mkdir(parents=True, exist_ok=True)
    res.to_csv(out_t / "nhanes_pair_results.csv", index=False, encoding="utf-8-sig")
    (out_t / "nhanes_pair_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
