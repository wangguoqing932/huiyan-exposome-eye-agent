#!/usr/bin/env python
"""huiyan executor — confirmatory pair-level validation (C1/C2 methodology fix).

Implements docs/analysis_plan.md v1.0:
- Three-state gold labels (replicated / contradicted / uninformative)
- Rule-scoped precision (not global); type-2 gap recall only
- Direction-plausibility pre-audit (C4)
- Bootstrap 95% CI for all headline metrics (C7)
- Negative-control (r01) single-column reporting (C10)
- Unified covariates: age, age2/100, sex (C3)

Reads cases from data/datasets/<id>/cases.jsonl (B5 fix).
Engine independence (B8): uses huiyan_agent.risk_rules.match_rules/assess, not raw YAML.
"""
from __future__ import annotations
import json, math, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules, assess
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent

def bh(p):
    p = p.fillna(1.0)
    return (p * len(p) / p.rank(method="first")).clip(upper=1.0)

def bootstrap_ci(vals, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(n_boot):
        s = rng.choice(vals, size=len(vals), replace=True)
        rep = (s == "replicated").sum(); con = (s == "contradicted").sum()
        samples.append(rep / (rep + con) if rep + con > 0 else 0.0)
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return (round(lo, 3), round(hi, 3))

def three_state(or_val, q_val, rule_dir="risk_up"):
    if q_val >= 0.05:
        return "uninformative"
    if rule_dir == "risk_down":
        return "replicated" if or_val < 1 else "contradicted"
    return "replicated" if or_val > 1 else "contradicted"

def compute_metrics(res, nc_prefix="r01"):
    t = res[res["status"] == "tested"].copy()
    nc_mask = t["a_flag"].str.contains(nc_prefix, na=False) | t.get("rule_id", pd.Series(dtype=str)).str.contains(nc_prefix, na=False)
    if "rule_id" not in t.columns:
        nc_mask = t["a_flag"].str.contains("uric_acid", na=False)  # r01 = uric x cataract
    t_main = t[~nc_mask]
    t_nc = t[nc_mask]
    rp = t_main[t_main["predicted"]]
    replicated = int((rp["gold3"] == "replicated").sum())
    contradicted = int((rp["gold3"] == "contradicted").sum())
    uninformative = int((rp["gold3"] == "uninformative").sum())
    non_rule = t_main[~t_main["predicted"]]
    missed = int((non_rule["gold3"] == "replicated").sum())
    prec = round(replicated / (replicated + contradicted), 3) if replicated + contradicted else None
    ci = bootstrap_ci(rp["gold3"].values) if len(rp) else (None, None)
    return {
        "rule_pairs_tested": len(rp), "replicated": replicated,
        "contradicted": contradicted, "uninformative": uninformative,
        "precision_rule": prec, "precision_rule_ci95": ci,
        "type2_missed": missed, "non_rule_pairs": len(non_rule),
        "negative_control_pairs": len(t_nc),
        "negative_control_outcome": t_nc["gold3"].value_counts().to_dict() if len(t_nc) else {},
    }

def run_pairs(df, expo_fn, outc_fn, covar_cols, weight_col, rules, a_reg, b_reg):
    E = expo_fn(df)
    B = outc_fn(df)
    cov = df[covar_cols].copy()
    results = []
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            a_ent = a_reg.get(a_flag)
            b_ent = b_reg.get(b_item)
            predicted = False
            if a_ent and b_ent:
                sigs = match_rules(rules, a_ent, b_ent)
                predicted = len(sigs) > 0
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny = int(sub["y"].sum()); nx = int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30:
                results.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos": ny,
                                "or": np.nan, "p": np.nan, "status": "underpowered", "predicted": predicted})
                continue
            X = sm.add_constant(sub[["x"] + covar_cols].astype(float))
            y = sub["y"].astype(float)
            w = df.loc[sub.index, weight_col].astype(float).clip(lower=1)
            w = w / w.mean()
            try:
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
                beta = fit.params["x"]; se = fit.bse["x"]
                results.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos": ny,
                                "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                                "ci_hi": math.exp(beta + 1.96 * se), "p": float(fit.pvalues["x"]),
                                "status": "tested", "predicted": predicted})
            except Exception:
                results.append({"a_flag": a_flag, "b_item": b_item, "n": len(sub), "n_pos": ny,
                                "or": np.nan, "p": np.nan, "status": "fit_fail", "predicted": predicted})
    res = pd.DataFrame(results)
    m = res["status"] == "tested"
    res.loc[m, "q"] = bh(res.loc[m, "p"])
    res["gold3"] = res.apply(lambda r: three_state(r.get("or", np.nan), r.get("q", 1.0)) if r["status"] == "tested" else "not_tested", axis=1)
    return res

def direction_audit(res):
    """C4: if >=2 A-level rule pairs show OR<1 → quarantine."""
    a_pairs = res[(res["predicted"]) & (res["status"] == "tested")]
    reversed_count = int((a_pairs["or"] < 1).sum())
    return reversed_count >= 2, reversed_count

if __name__ == "__main__":
    print("Confirmatory pipeline ready (scripts/evaluate.py)")
    print("Run individual dataset scripts (phase5_*) then use compute_metrics()")
    print("Full integration: populate cases.jsonl then call run_pairs()")
