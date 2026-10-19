#!/usr/bin/env python
"""CHARLS 2015 wave — temporal external validation layer (analysis_plan §16,
pre-registered 2026-10-15 before any 2015-layer run).

The v1.2 rule set (frozen 2026-10-12) has never seen any pair-level result
from the 2015 wave. Same operationalization as the 2011 layer, BHY q +
direction three-state, plus G0/G2 system metrics on the judgeable scope.

Run: PYTHONUTF8=1 python scripts/evaluate_charls2015.py
"""
from __future__ import annotations
import json, math, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from huiyan_agent.risk_rules import load_rules, match_rules
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry
from evaluate import (fdr_bhy, three_state, detect_separation, compute_metrics_v11,
                      _flag_index, get_judgeable_b_items)
warnings.filterwarnings("ignore", category=FutureWarning)

CH = Path(r"E:\BaiduNetdiskDownload\所有数据库\01. CHARLS 中国健康与养老追踪调查\CHARLS_中国\Raw_data\2015charls")
OUT = ROOT / "outputs/confirmatory"


def _code(s):
    return pd.to_numeric(s.astype(str).str.strip().str.split().str[0], errors="coerce")


def main() -> int:
    print("\n" + "=" * 60)
    print("CHARLS 2015 temporal validation (analysis_plan §16)")
    print("=" * 60)
    demo = pd.read_stata(CH / "Demographic_Background.dta",
                         columns=["ID", "ba000_w2_3", "ba002_1", "ba004_w3_1"])
    demo = demo.rename(columns={"ba000_w2_3": "rgender"})
    hlth = pd.read_stata(CH / "Health_Status_and_Functioning.dta",
                         columns=["ID", "zda035", "zda037", "da059", "da061", "da067"])
    blood = pd.read_stata(CH / "Blood.dta")
    bio = pd.read_stata(CH / "Biomarker.dta", columns=["ID", "qi002", "qi003"])
    wgt = pd.read_stata(CH / "Weights.dta", columns=["ID", "INDV_weight"])

    d = (demo.merge(hlth, on="ID", how="inner")
             .merge(blood[["ID", "bl_ua", "bl_glu", "bl_hbalc", "bl_cho", "bl_tg",
                           "bl_hdl", "bl_ldl", "bl_crp"]], on="ID", how="left")
             .merge(bio, on="ID", how="left")
             .merge(wgt, on="ID", how="left"))
    age = 2015 - pd.to_numeric(d["ba002_1"], errors="coerce")
    age = age.fillna(pd.to_numeric(d["ba004_w3_1"], errors="coerce"))
    d["age_calc"] = age
    d = d[age >= 45]
    d = d[pd.to_numeric(d["INDV_weight"], errors="coerce") > 0]
    print(f"frame: n={len(d)}")

    sex = _code(d["rgender"])

    def n(c):
        return pd.to_numeric(d[c], errors="coerce")

    E = {}
    ua = n("bl_ua")
    if ua.notna().sum() and ua.median() > 100:
        ua = ua / 16.8
    E["uric_acid_elevated"] = (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype(float).where(ua.notna())
    E["hyperglycemia"] = (n("bl_glu") >= 126).astype(float).where(n("bl_glu").notna())
    E["hba1c_elevated"] = (n("bl_hbalc") >= 6.5).astype(float).where(n("bl_hbalc").notna())
    tc, tg, hdl, ldl = n("bl_cho"), n("bl_tg"), n("bl_hdl"), n("bl_ldl")
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    E["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    E["crp_elevated"] = (n("bl_crp") > 3.0).astype(float).where(n("bl_crp").notna())
    # NOTE: no BMI in the 2015 wave (Biomarker has height qi002 only; the
    # weight item is absent) — and the 2011 layer never measured bmi either,
    # so dropping bmi_high keeps the two CHARLS layers aligned.
    s1, s2 = _code(d["da059"]), _code(d["da061"])
    E["current_smoking"] = ((s1 == 1) & (s2 == 1)).astype(float).where(s1.notna() & s2.notna())
    alc = _code(d["da067"])
    E["alcohol_intake"] = (alc == 1).astype(float).where(alc.notna())

    B = {}
    # 2015 wave: raw da035/da037 are fragmented by questionnaire skip logic
    # (97.6% missing); use CHARLS official cleaned variables zda035/zda037
    cat = _code(d["zda035"])
    B["cataract_any"] = (cat == 1).astype(float).where(cat.notna())
    glc = _code(d["zda037"])
    B["glaucoma_selfreport"] = (glc == 1).astype(float).where(glc.notna())

    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
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
                wt = pd.to_numeric(d.loc[sub.index, "INDV_weight"], errors="coerce").clip(lower=1)
                wt = wt / wt.mean()
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=wt).fit()
                if not getattr(fit, "converged", True):
                    raise RuntimeError("not converged")
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
    metrics = compute_metrics_v11(res, "cohort")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

    # G0/G2 system metrics on judgeable scope
    judgeable = get_judgeable_b_items("cohort")
    j = res[(res["status"] == "tested") & (res["b_item"].isin(judgeable))]
    g2_map = {}
    try:
        for line in (ROOT / "outputs/confirmatory/fused_system_R5.jsonl").read_text(encoding="utf-8").splitlines():
            r2 = json.loads(line)
            if r2["dataset"] == "charls":
                g2_map[(r2["a_flag"], r2["b_item"])] = r2["G2"]
    except FileNotFoundError:
        pass
    # G2 gate logic re-applied for flags absent from the 2011 run (semantic-naive:
    # NC abstain + keyword evidence confirmation identical to §13)
    from huiyan_agent.evidence_store import EvidenceStore
    store = EvidenceStore()
    from literature_validation import A_FLAG_TERMS, B_FLAG_TERMS
    LEVELS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}
    for _, row in j.iterrows():
        key = (row["a_flag"], row["b_item"])
        if key in g2_map:
            continue
        hit_ids = [i for i in str(row["rule_ids"]).split(",") if i]
        if not hit_ids or row["negative_control"]:
            g2_map[key] = False
            continue
        a_terms = A_FLAG_TERMS.get(row["a_flag"], [row["a_flag"]])
        b_terms = B_FLAG_TERMS.get(row["b_item"], [row["b_item"]])
        evs = store.retrieve(" ".join(a_terms[:2] + b_terms[:2]), top_k=5)
        a_tok, b_tok = a_terms[0].lower().split()[-1], b_terms[0].lower().split()[0]
        rel = [e for e in evs
               if any(i in (e.entities_a or []) for i in hit_ids)
               or (a_tok in e.text.lower() and b_tok in e.text.lower())]
        if rel and max(LEVELS.get((e.evidence_level or "E").upper(), 0) for e in rel) >= LEVELS["B"]:
            g2_map[key] = True
        elif rel:
            g2_map[key] = False  # arbiter path not re-run offline; conservative
        else:
            g2_map[key] = False
    for arm in ("G0", "G2"):
        tp = sum(1 for _, r in j.iterrows() if (r["predicted"] if arm == "G0" else g2_map.get((r["a_flag"], r["b_item"]), False)) and r["gold3"] == "replicated")
        fp = sum(1 for _, r in j.iterrows() if (r["predicted"] if arm == "G0" else g2_map.get((r["a_flag"], r["b_item"]), False)) and r["gold3"] != "replicated")
        fn = sum(1 for _, r in j.iterrows() if not (r["predicted"] if arm == "G0" else g2_map.get((r["a_flag"], r["b_item"]), False)) and r["gold3"] == "replicated")
        p = tp / (tp + fp) if tp + fp else None
        rc = tp / (tp + fn) if tp + fn else None
        f1 = 2 * p * rc / (p + rc) if p and rc else 0.0
        metrics[f"system_{arm}"] = {"TP": tp, "FP": fp, "FN": fn,
                                    "P": round(p, 3) if p else None,
                                    "R": round(rc, 3) if rc else None, "F1": round(f1, 3)}
    metrics["layer"] = "charls_2015_temporal (plan §16); G2 arbiter-offline conservative fallback for new pairs"

    OUT.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT / "charls2015_confirmatory.csv", index=False, encoding="utf-8-sig")
    (OUT / "charls2015_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("system:", json.dumps({k: v for k, v in metrics.items() if k.startswith("system_")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
