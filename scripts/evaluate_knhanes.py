#!/usr/bin/env python
"""huiyan executor — KNHANES confirmatory validation (external, cross-country).

Uses same framework as NHANES confirmatory (scripts/evaluate.py) with KNHANES variables.
Variable drift resolved: uric=HE_UAScr, HDL=HE_HDL_st2, LDL=HE_LDL_drct, alcohol=BA2_2_1.
Run: PYTHONUTF8=1 python scripts/evaluate_knhanes.py
"""
from __future__ import annotations
import json, math, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry
from evaluate import (fdr_bhy, three_state, detect_separation, compute_metrics_v11,
                      direction_audit_and_block, _flag_index, get_judgeable_b_items)
warnings.filterwarnings("ignore", category=FutureWarning)
ROOT = Path(__file__).resolve().parent.parent

def build_knhanes_exposures(d: pd.DataFrame) -> dict[str, pd.Series]:
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    def first(*cands):
        for c in cands:
            if c in d.columns: return q(c)
        return pd.Series(np.nan, index=d.index)
    sex = q("sex")
    e = {}
    # Uric: HE_UAScr (2008) or HE_Uacid (2017+); unit sanity
    ua = first("HE_Uacid", "HE_UAScr", "HE_UAScr_AAS")
    if ua.notna().sum() and ua.median() > 100: ua = ua / 16.8  # μmol/L → mg/dL
    e["uric_acid_elevated"] = (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype(float).where(ua.notna())
    glu = first("HE_glu")
    e["hyperglycemia"] = (glu >= 126).astype(float).where(glu.notna())
    gh = first("HE_HbA1c", "HE_DM_HbA1c")
    e["hba1c_elevated"] = (gh >= 6.5).astype(float).where(gh.notna())
    tc, tg = first("HE_chol", "HE_CHOL"), first("HE_TG", "HE_HTG")
    hdl, ldl = first("HE_HDL", "HE_HDL_st2"), first("HE_LDL", "HE_LDL_drct")
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    crp = first("HE_hsCRP")
    e["crp_elevated"] = (crp > 3.0).astype(float).where(crp.notna())
    bmi = first("HE_BMI")
    e["bmi_high"] = (bmi >= 25).astype(float).where(bmi.notna())
    smk = q("BS1_1")  # 1=current, 2=former, 3=never
    e["current_smoking"] = (smk == 1).astype(float).where(smk.isin([1, 2, 3]))
    # Alcohol: BA2_2_1 (drink more than once/month) or BA2_22 frequency
    alc = first("BA2_2_1", "BA2_22")
    if alc.name == "BA2_2_1":
        e["alcohol_intake"] = (alc == 1).astype(float).where(alc.notna())
    else:  # frequency-based: any non-zero frequency = drinker
        e["alcohol_intake"] = (alc > 0).astype(float).where(alc.notna())
    return e

def build_knhanes_outcomes(d: pd.DataFrame) -> dict[str, pd.Series]:
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    def bi(*cands):
        for c in cands:
            if c in d.columns:
                s = q(c)
                return s.isin([1]).astype(float).where(s.notna())
        return pd.Series(np.nan, index=d.index)
    o = {}
    o["cataract_any"] = bi("DH2_lt")
    o["glaucoma_selfreport"] = bi("DH3_lt")
    o["retinopathy_any"] = bi("E_DRP_R", "E_DRP_L")
    o["amd_early"] = bi("E_AMD_ELY_R", "E_AMD_ELY_L")
    o["amd_late"] = bi("E_AMD_LATE_R", "E_AMD_LATE_L")
    o["vision_impairment_moderate"] = bi("E_VS_DS")  # any VI
    # IOP
    iop_c = [c for c in ("E_Gr_p", "E_Pr_1", "E_GR") if c in d.columns]
    if iop_c:
        iop = pd.concat([q(c) for c in iop_c], axis=1).max(axis=1).where(lambda x: x < 80)
        o["glaucoma_iop_elevated"] = (iop > 21).astype(float).where(iop.notna())
    # CDR
    cdr_c = [c for c in ("E_Grv", "E_Glv") if c in d.columns]
    if cdr_c:
        cdr = pd.concat([q(c) for c in cdr_c], axis=1).max(axis=1).where(lambda x: x <= 1.0)
        o["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype(float).where(cdr.notna())
    return o

def main() -> int:
    print("\n" + "="*60)
    print("KNHANES confirmatory (analysis_plan v1.1)")
    print("="*60)
    # Load frames
    FR = ROOT / "data/raw/knhanes_frames"
    parts = []
    for p in sorted(FR.glob("knhanes_20*.csv")):
        df = pd.read_csv(p, low_memory=False)
        parts.append(df)
    d = pd.concat(parts, ignore_index=True, sort=False)
    d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
    w = "wt_itvex" if "wt_itvex" in d.columns else ("wt_itv" if "wt_itv" in d.columns else "wt_ex")
    d = d[pd.to_numeric(d.get(w, 0), errors="coerce") > 0]
    print(f"frame: n={len(d)}, waves={d.get('year', pd.Series()).nunique()}")

    E = build_knhanes_exposures(d)
    B = build_knhanes_outcomes(d)
    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = _flag_index(a_reg), _flag_index(b_reg)
    cov = pd.DataFrame({
        "age": pd.to_numeric(d["age"], errors="coerce"),
        "age2": pd.to_numeric(d["age"], errors="coerce") ** 2 / 100,
        "sex": pd.to_numeric(d["sex"], errors="coerce"),
    })
    results = []
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            a_ent = a_idx.get(a_flag) or a_reg.get(a_flag)
            b_ent = b_idx.get(b_item) or b_reg.get(b_item)
            predicted, rule_ids, is_nc, direction = False, [], False, "risk_up"
            if a_ent and b_ent:
                sigs = match_rules(rules, a_ent, b_ent)
                predicted = len(sigs) > 0
                rule_ids = [s.rule_id for s in sigs]
                by_id = {r.id: r for r in rules}
                hit = [by_id[i] for i in rule_ids if i in by_id]
                is_nc = any(r.negative_control for r in hit)
                dirs = [r.direction for r in hit]
                direction = "risk_down" if dirs and all(dd == "risk_down" for dd in dirs) else "risk_up"
            meta = {"a_flag": a_flag, "b_item": b_item, "predicted": predicted,
                    "rule_ids": ",".join(rule_ids), "negative_control": is_nc, "direction": direction}
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30 or ny > len(sub) - 30:
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": "underpowered"}); continue
            if detect_separation(sub["y"], sub["x"]):
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": "separation"}); continue
            try:
                X = sm.add_constant(sub[["x", "age", "age2", "sex"]].astype(float))
                y = sub["y"].astype(float)
                wt = d.loc[sub.index, w].astype(float)
                wt = wt.where(wt > 0, 1.0) / wt.mean()
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=wt).fit()
                if not getattr(fit, "converged", True): raise RuntimeError("not converged")
                beta, se = fit.params["x"], fit.bse["x"]
                results.append({**meta, "n": len(sub), "n_pos": ny,
                                "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                                "ci_hi": math.exp(beta + 1.96 * se), "p": float(fit.pvalues["x"]),
                                "status": "tested"})
            except Exception as ex:
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": f"fit_fail:{type(ex).__name__}"})
    res = pd.DataFrame(results)
    m = res["status"] == "tested"
    res.loc[m, "q"] = fdr_bhy(res.loc[m, "p"])
    res["gold3"] = res.apply(
        lambda r: three_state(r.get("or", np.nan), r.get("q", np.nan), r.get("direction", "risk_up"))
        if r["status"] == "tested" else "not_tested", axis=1)

    # Direction audit
    quarantine, n_rev = direction_audit_and_block(res, rules, "KNHANES")

    if not quarantine:
        # D5: filter by KNHANES judgeable
        judgeable = get_judgeable_b_items("knhanes")
        if judgeable:
            before = len(res[res["status"] == "tested"])
            res_m = res[(res["status"] == "tested") & (res["b_item"].isin(judgeable))]
            excluded = before - len(res_m)
            if excluded:
                print(f"[metrics] D5: excluded {excluded} non-judgeable pairs")
                # Merge back non-tested rows
                res_final = pd.concat([res_m, res[res["status"] != "tested"]])
            else:
                res_final = res
        else:
            res_final = res

        metrics = compute_metrics_v11(res_final)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        out = ROOT / "outputs" / "confirmatory"
        out.mkdir(parents=True, exist_ok=True)
        res.to_csv(out / "knhanes_confirmatory.csv", index=False, encoding="utf-8-sig")
        (out / "knhanes_metrics_v11.json").write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        out = ROOT / "outputs" / "confirmatory"
        out.mkdir(parents=True, exist_ok=True)
        res.to_csv(out / "knhanes_quarantined.csv", index=False, encoding="utf-8-sig")
    return 0

if __name__ == "__main__":
    sys.exit(main())
