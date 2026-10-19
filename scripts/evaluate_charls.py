#!/usr/bin/env python
"""huiyan executor — CHARLS confirmatory validation (cohort layer 1/9).

Run: PYTHONUTF8=1 python scripts/evaluate_charls.py
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

def _code(s):
    return pd.to_numeric(s.astype(str).str.strip().str.split().str[0], errors="coerce")

def main() -> int:
    print("\n" + "="*60)
    print("CHARLS confirmatory (analysis_plan v1.1)")
    print("="*60)
    CH = Path(r"E:\BaiduNetdiskDownload\所有数据库\01. CHARLS 中国健康与养老追踪调查\CHARLS_中国\Raw_data\2011charls")
    demo = pd.read_stata(CH / "demographic_background.dta", columns=["ID", "rgender", "ba004", "ba002_1"])
    hlth = pd.read_stata(CH / "health_status_and_functioning.dta",
                         columns=["ID", "da035", "da036", "da037", "da059", "da061", "da067"])
    blood = pd.read_stata(CH / "Blood_20140429.dta",
                          columns=["ID", "newua", "newglu", "newhba1c", "newcho", "newtg", "newhdl", "newldl", "newcrp"])
    wgt = pd.read_stata(CH / "weight.dta", columns=["ID", "ind_weight"])
    d = demo.merge(hlth, on="ID", how="inner").merge(blood, on="ID", how="left").merge(wgt, on="ID", how="left")
    age = 2011 - pd.to_numeric(d["ba002_1"], errors="coerce")
    age = age.fillna(pd.to_numeric(d["ba004"], errors="coerce"))
    d["age_calc"] = age
    d = d[age >= 45]
    d = d[pd.to_numeric(d["ind_weight"], errors="coerce") > 0]
    print(f"frame: n={len(d)}")

    sex = _code(d["rgender"])
    def n(c): return pd.to_numeric(d[c], errors="coerce")
    E = {}
    ua = n("newua")
    if ua.notna().sum() and ua.median() > 100: ua = ua / 16.8
    E["uric_acid_elevated"] = (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype(float).where(ua.notna())
    E["hyperglycemia"] = (n("newglu") >= 126).astype(float).where(n("newglu").notna())
    E["hba1c_elevated"] = (n("newhba1c") >= 6.5).astype(float).where(n("newhba1c").notna())
    tc, tg, hdl, ldl = n("newcho"), n("newtg"), n("newhdl"), n("newldl")
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    E["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    E["crp_elevated"] = (n("newcrp") > 3.0).astype(float).where(n("newcrp").notna())
    s1, s2 = _code(d["da059"]), _code(d["da061"])
    E["current_smoking"] = ((s1 == 1) & (s2 == 1)).astype(float).where(s1.notna() & s2.notna())
    alc = _code(d["da067"])
    E["alcohol_intake"] = (alc == 1).astype(float).where(alc.notna())

    B = {}
    cat = _code(d["da035"])
    B["cataract_any"] = (cat == 1).astype(float).where(cat.notna())
    glc = _code(d["da037"])
    B["glaucoma_selfreport"] = (glc == 1).astype(float).where(glc.notna())

    rules = load_rules()
    a_reg = load_entity_a_registry(); b_reg = load_entity_b_registry()
    a_idx, b_idx = _flag_index(a_reg), _flag_index(b_reg)
    cov = pd.DataFrame({"age": d["age_calc"], "age2": d["age_calc"] ** 2 / 100, "sex": sex})
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
            if len(sub) < 200 or ny < 30 or nx < 30:
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": "underpowered"}); continue
            if detect_separation(sub["y"], sub["x"]):
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": "separation"}); continue
            try:
                X = sm.add_constant(sub[["x", "age", "age2", "sex"]].astype(float))
                y = sub["y"].astype(float)
                wt = pd.to_numeric(d.loc[sub.index, "ind_weight"], errors="coerce").clip(lower=1)
                wt = wt / wt.mean()
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
    quarantine, n_rev = direction_audit_and_block(res, rules, "CHARLS")
    if not quarantine:
        metrics = compute_metrics_v11(res, "cohort")
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        out = ROOT / "outputs" / "confirmatory"
        out.mkdir(parents=True, exist_ok=True)
        res.to_csv(out / "charls_confirmatory.csv", index=False, encoding="utf-8-sig")
        (out / "charls_metrics_v11.json").write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
