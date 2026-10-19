#!/usr/bin/env python
"""Cohort-layer confirmatory analysis (analysis_plan.md section 19).

Runs ONLY after section 19 was written to disk. Section 19 froze, in advance:
the cohort/wave list, the construct rules, the gate-audit construction of every
binary exposure, the measured set of testable (rule, cohort) pairs, the model
and covariate set, the per-cohort BMI cut-point, the two FDR families, the
three-state definitions and the transportability criteria. Nothing here is
chosen after seeing a result.

Model, per (rule, cohort) pair
------------------------------
  logistic(outcome ~ exposure + age + sex + C(wave)), clustered by person.
  * SHARE carries five imputation replicates (`implicat`); the model is fitted
    on each and combined by Rubin's rules (within + between variance), as
    pre-registered. Nothing else is pooled.
  * Covariates age/sex are complete-case per model; the analysable n is
    reported for every pair.

Inference
---------
  q_rule   BHY over the pre-registered confirmatory family (ruled pairs only)
  q        BHY over the exploratory family (every exposure x outcome pair
           actually tested in that cohort)
  three-state per analysis_plan section 19.7, identical to R11's definition.

Outputs
  outputs/cohorts/cohort_rule_results.csv
  outputs/cohorts/cohort_transportability.json

Usage: python scripts/cohort_confirmatory.py
"""
from __future__ import annotations

import itertools
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts"
COVERAGE = ROOT / "outputs" / "confirmatory" / "cohort_rule_coverage.json"

# Per-cohort primary BMI cut, pre-declared in section 19.7 (C58 evidence: the
# two-tier prevalence gate separated the Asian from the international cut).
BMI_PRIMARY = {
    "KLoSA": "bmi_high_25", "MHAS": "bmi_high_25", "LASI": "bmi_high_25",
    "CLHLS": "bmi_high_25",
    "SHARE": "bmi_high_30", "HRS": "bmi_high_30", "ELSA": "bmi_high_30",
    "CRELES": "bmi_high_30",
}

# outcome columns that may serve each rule outcome flag, in preference order
OUTCOME_COLS = {
    "cataract_any": ["cataract_any"],
    "vision_impairment_moderate": ["vision_impairment_moderate"],
    "vision_impairment_severe": ["vision_impairment_severe"],
    "amd_late": ["amd_any"],
    "amd_early": ["amd_any"],
}
EXPOSURE_COLS = {
    "current_smoking": ["current_smoking"],
    "alcohol_intake": ["alcohol_intake"],
    "bmi_high": None,           # resolved per cohort via BMI_PRIMARY
    "hyperglycemia": ["diabetes"],
    "hba1c_elevated": ["diabetes"],
}


def fdr_bhy(p: pd.Series) -> pd.Series:
    """BHY step-up FDR with monotonicity (analysis_plan section 7)."""
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


def three_state(or_val, q_val, rule_dir="risk_up"):
    if not np.isfinite(q_val) or q_val >= 0.05:
        return "uninformative"
    if not np.isfinite(or_val) or abs(float(or_val) - 1.0) < 1e-9:
        return "uninformative"
    if rule_dir == "risk_down":
        return "replicated" if or_val < 1 else "contradicted"
    return "replicated" if or_val > 1 else "contradicted"


def fit_one(df: pd.DataFrame, y: str, x: str, wave_col: str | None):
    """Return (beta, se, n) for the exposure coefficient, clustered by person."""
    d = df[[y, x, "age", "sex", "mergeid"] +
           ([wave_col] if wave_col else [])].dropna()
    if len(d) < 200 or d[y].nunique() < 2 or d[x].nunique() < 2:
        return None
    X = pd.DataFrame({x: d[x].astype(float), "age": d["age"].astype(float),
                      "sex": d["sex"].astype(float)})
    if wave_col:
        X = pd.concat([X, pd.get_dummies(d[wave_col].astype("category"),
                                         prefix="w", drop_first=True)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    try:
        m = sm.GLM(d[y].astype(float), X, family=sm.families.Binomial())
        r = m.fit(cov_type="cluster", cov_kwds={"groups": d["mergeid"]})
    except Exception:
        return None
    if x not in r.params:
        return None
    return float(r.params[x]), float(r.bse[x]), int(len(d))


def rubin_pool(est: list[tuple[float, float]]):
    """Rubin's rules over imputation replicates."""
    est = [e for e in est if e is not None]
    m = len(est)
    if m == 0:
        return None
    betas = np.array([e[0] for e in est])
    variances = np.array([e[1] ** 2 for e in est])
    qbar = betas.mean()
    ubar = variances.mean()
    b = betas.var(ddof=1) if m > 1 else 0.0
    tvar = ubar + (1.0 + 1.0 / m) * b
    return float(qbar), float(np.sqrt(max(tvar, 1e-12)))


def main() -> int:
    rules = {r["id"]: r for r in yaml.safe_load(
        (ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))["rules"]}
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    matrix = cov["matrix"]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []

    for path in sorted(FRAMES.glob("cohort_*.csv")):
        coh = path.stem.replace("cohort_", "")
        d = pd.read_csv(path, low_memory=False)
        for c in ("age", "sex"):
            if c not in d.columns:
                d[c] = np.nan
        has_wave = "wave" in d.columns and d["wave"].nunique() > 1
        wave_col = "wave" if has_wave else None
        has_imp = "implicat" in d.columns and d["implicat"].nunique() > 1

        # ---- confirmatory family: the pre-registered ruled pairs -----------
        pair_flags = {}
        for rid, per_coh in matrix.items():
            v = per_coh.get(coh)
            if not v or not v["testable"]:
                continue
            xflag = v["exposure_flag"]
            xcol = v["exposure_col"]
            if xflag == "bmi_high":
                xcol = BMI_PRIMARY.get(coh, xcol)
            if xcol not in d.columns:
                continue
            ycol = v["outcome_col"]
            if ycol not in d.columns:
                cand = OUTCOME_COLS.get(v["outcome_flag"], [])
                ycol = next((c for c in cand if c in d.columns), None)
                if ycol is None:
                    continue
            pair_flags[rid] = (xcol, ycol, rules[rid].get("direction", "risk_up"))

        # ---- exploratory family: every exposure x outcome actually present -
        exp_cols = sorted({c for c in d.columns
                           if c in ("current_smoking", "alcohol_intake",
                                    "bmi_high_25", "bmi_high_30", "diabetes")})
        out_cols = sorted({c for c in d.columns
                           if c in ("cataract_any", "vision_impairment_moderate",
                                    "vision_impairment_severe", "amd_any",
                                    "glaucoma_selfreport", "blindness_selfreport")})

        def run(xcol, ycol, direction, rule_id):
            rec = {"cohort": coh, "rule_id": rule_id, "exposure": xcol,
                   "outcome": ycol, "direction": direction}
            if has_imp:
                est = []
                for imp, sub in d.groupby("implicat"):
                    r = fit_one(sub, ycol, xcol, wave_col)
                    if r:
                        est.append((r[0], r[1]))
                pooled = rubin_pool(est)
                if pooled is None:
                    return None
                beta, se = pooled
                rec["n_imputations"] = len(est)
                n = int(pd.to_numeric(
                    d.loc[d["implicat"] == d["implicat"].min(), [xcol, ycol]]
                    .dropna().index.size, errors="coerce") or len(d))
                rec["n"] = n
            else:
                r = fit_one(d, ycol, xcol, wave_col)
                if r is None:
                    return None
                beta, se, n = r
                rec["n"] = n
            rec["beta"] = round(beta, 5)
            rec["se"] = round(se, 5)
            rec["odds_ratio"] = round(float(np.exp(beta)), 4)
            rec["ci_low"] = round(float(np.exp(beta - 1.96 * se)), 4)
            rec["ci_high"] = round(float(np.exp(beta + 1.96 * se)), 4)
            rec["z"] = round(beta / se, 3) if se else None
            rec["p"] = np.nan          # set exactly in run2 from the normal CDF
            return rec

        # z-based p, computed exactly rather than by simulation
        from scipy import stats as _st

        def run2(xcol, ycol, direction, rule_id):
            rec = run(xcol, ycol, direction, rule_id)
            if rec is not None and rec.get("z") is not None:
                rec["p"] = float(2 * _st.norm.sf(abs(rec["z"])))
            return rec

        for rid, (xcol, ycol, direction) in pair_flags.items():
            rec = run2(xcol, ycol, direction, rid)
            if rec:
                rec["family"] = "confirmatory"
                rec["rule_relevant"] = True
                rows.append(rec)
        for xcol, ycol in itertools.product(exp_cols, out_cols):
            rec = run2(xcol, ycol, "risk_up", "")
            if rec:
                rec["family"] = "exploratory"
                rec["rule_relevant"] = False
                rows.append(rec)

    res = pd.DataFrame(rows)
    if res.empty:
        print("no results")
        return 1

    # de-duplicate: a ruled pair may also appear in the exploratory sweep
    res = res.sort_values(["rule_relevant"], ascending=False) \
             .drop_duplicates(["cohort", "exposure", "outcome"], keep="first")

    res["q"] = np.nan
    res["q_rule"] = np.nan
    m = res["p"].notna()
    if m.any():
        res.loc[m, "q"] = fdr_bhy(res.loc[m, "p"])
    rm = m & res["rule_relevant"]
    if rm.any():
        res.loc[rm, "q_rule"] = fdr_bhy(res.loc[rm, "p"])
    res["q_primary"] = np.where(rm, res["q_rule"], res["q"])
    res["three_state"] = [
        three_state(o, q, dr) if pd.notna(q) else "not_tested"
        for o, q, dr in zip(res["odds_ratio"], res["q_primary"], res["direction"])]

    res.to_csv(OUT / "cohort_rule_results.csv", index=False, encoding="utf-8")

    # ---- transportability per rule ---------------------------------------
    transp = {}
    for rid in [r for r in matrix]:
        sub = res[(res["rule_id"] == rid)]
        if sub.empty:
            continue
        states = sub["three_state"].tolist()
        reps = int((sub["three_state"] == "replicated").sum())
        cons = int((sub["three_state"] == "contradicted").sum())
        if reps >= 2:
            verdict = "transportable"
        elif reps == 1 and cons == 0:
            verdict = "single_cohort"
        elif cons > 0 and reps == 0:
            verdict = "non_transportable"
        else:
            verdict = "mixed"
        transp[rid] = {"cohorts_tested": sub["cohort"].tolist(),
                       "n_pairs": int(len(sub)), "replicated": reps,
                       "contradicted": cons, "states": states,
                       "verdict": verdict,
                       "per_cohort": sub[["cohort", "odds_ratio", "ci_low",
                                          "ci_high", "q_primary", "three_state"]]
                       .to_dict(orient="records")}
    OUT.joinpath("cohort_transportability.json").write_text(
        json.dumps({"note": "analysis_plan section 19 cohort layer",
                    "n_pairs": int(len(res)),
                    "by_rule": transp}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print(f"pairs tested: {len(res)}  "
          f"(confirmatory {int(res['rule_relevant'].sum())})")
    print(res[["cohort", "rule_id", "exposure", "outcome", "n", "odds_ratio",
               "ci_low", "ci_high", "q_rule", "q", "three_state"]]
          .to_string(index=False))
    print()
    for rid, v in transp.items():
        print(f"  {rid:38s} {v['verdict']:18s} "
              f"rep={v['replicated']} con={v['contradicted']} "
              f"in {','.join(v['cohorts_tested'])}")
    print(f"-> {OUT/'cohort_rule_results.csv'}")
    print(f"-> {OUT/'cohort_transportability.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
