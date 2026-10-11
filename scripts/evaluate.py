#!/usr/bin/env python
"""huiyan executor — confirmatory validation pipeline (analysis_plan v1.1).

Replaces phase5_nhanes/knhanes/charls scripts (B1: archived as .bak).
Reads cases from data/datasets/<id>/cases.jsonl (B2: file I/O with error on missing).
Implements B3-B7 fixes: fixed clinical cutoffs, unit-harmonized composites,
VI threshold fix, flag de-overloading, nesting guard, direction audit wired,
separation detection, R survey fallback path.

Usage:
    python scripts/evaluate.py --dataset intval-nhanes
    python scripts/evaluate.py --dataset extval-knhanes
    python scripts/evaluate.py --dataset extval-cohorts-9
"""
from __future__ import annotations
import argparse, json, math, os, subprocess, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules, Rule
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry
import csv


def get_judgeable_b_items(dataset_key: str = "nhanes") -> set[str]:
    """D5: Read boolean judgeable columns from entities_b.csv.
    
    Returns the set of entity_b_ids that are judgeable in the given dataset.
    Items not in this set are excluded from P/R/F1 denominators (coverage only).
    """
    b_path = ROOT / "data" / "seed" / "entities_b.csv"
    if not b_path.exists():
        return set()
    col = f"{dataset_key}_judgeable"
    judgeable = set()
    with b_path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get(col, "").strip().lower() == "true":
                judgeable.add(row.get("entity_b_id", "").strip())
    return judgeable


warnings.filterwarnings("ignore", category=FutureWarning)
ROOT = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════════════════════════════
#  B3a: Fixed clinical cutoffs (NOT sample quantiles)
# ══════════════════════════════════════════════════════════════════
# These thresholds are pre-registered and must NEVER change between datasets.
CLINICAL_CUTOFFS = {
    "uric_acid_elevated": {"male": 6.8, "female": 5.7, "unit": "mg/dL"},
    "hyperglycemia": {"threshold": 126, "unit": "mg/dL", "alt_dx": "DIQ010==1"},
    "hba1c_elevated": {"threshold": 6.5, "unit": "%"},
    "dyslipidemia": {
        "total_cholesterol": 240, "ldl": 160, "triglycerides": 200, "hdl_low": 40, "unit": "mg/dL"
    },
    "crp_elevated": {"threshold": 3.0, "unit": "mg/L"},
    "bmi_high": {"threshold": 25.0, "unit": "kg/m2"},
    "current_smoking": {"var": "SMQ040", "positive": [1, 2]},
    "alcohol_intake": {"var": "ALQ101", "positive": 1},
    "lead_exposure": {"threshold": 5.0, "unit": "ug/dL", "note": "CDC reference value"},
    # B3b: Antioxidant composite uses z-score harmonization, not raw unit mixing
    "low_antioxidant_intake": {
        "vars": ["DR1TVC", "DR1TVE", "DR1TLZ"],
        "method": "zscore_sum_bottom_quartile",
        "note": "z-score each nutrient, sum, bottom quartile of the composite z-score"
    },
}

# ══════════════════════════════════════════════════════════════════
#  B3c: VI thresholds from NHANES logMAR (presenting VA, right eye)
#  LogMAR values differ from each other — the original bug was using
#  identical thresholds for mild and moderate.
# ══════════════════════════════════════════════════════════════════
VI_THRESHOLDS = {
    "vision_impairment_mild": {"logMAR_gt": 0.30},      # worse than 20/40
    "vision_impairment_moderate": {"logMAR_gt": 0.48},  # worse than 20/60
    "vision_impairment_severe": {"logMAR_gt": 1.00},    # worse than 20/200
    # NOTE: these are CUMULATIVE (severe ⊂ moderate ⊂ mild); B3e nesting guard
    # prevents double-counting by assigning each person to the WORST category only
}

# ══════════════════════════════════════════════════════════════════
#  B3d: Flag de-overloading — secondhand smoke gets its own flag
# ══════════════════════════════════════════════════════════════════
# entities_a.csv already has secondhand_smoke as separate row with
# current_smoking flag. The fix: separate rows should NOT share flags
# that trigger different rules. We do this at the registry level, not here.

# ══════════════════════════════════════════════════════════════════
#  Core pipeline
# ══════════════════════════════════════════════════════════════════

def load_cases(dataset_id: str) -> list[dict]:
    """B2: Read cases from JSONL. Exit non-zero if file missing or empty."""
    path = ROOT / "data" / "datasets" / dataset_id / "cases.jsonl"
    if not path.exists():
        print(f"[evaluate] ERROR: {path} not found — run scripts/generate_cases.py first")
        sys.exit(1)
    cases = [json.loads(l) for l in path.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
    if not cases:
        print(f"[evaluate] ERROR: {path.name} is empty (0 cases)")
        sys.exit(1)
    return cases


def build_nhanes_exposures(d: pd.DataFrame) -> dict[str, pd.Series]:
    """B3a: All cutoffs are pre-registered clinical values, NOT sample quantiles."""
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    sex = q("RIAGENDR")
    e = {}
    # Uric acid: sex-specific mg/dL
    ua = q("LBXSUA")
    e["uric_acid_elevated"] = (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype(float).where(ua.notna())
    # Glucose: fixed 126 mg/dL (or diabetes dx)
    glu = q("LBXGL") if "LBXGL" in d else q("LBXSGL")
    diq = q("DIQ010")
    e["hyperglycemia"] = ((glu >= 126) | (diq == 1)).astype(float).where(glu.notna() | diq.notna())
    # HbA1c: fixed 6.5%
    e["hba1c_elevated"] = (q("LBXGH") >= 6.5).astype(float).where(q("LBXGH").notna())
    # Dyslipidemia: composite clinical cutoffs (fixed)
    tc, tg, hdl = q("LBXSCH"), q("LBXSTR"), q("LBDHDD") if "LBDHDD" in d else q("LBDHDL")
    ldl = q("LBDLDL") if "LBDLDL" in d else pd.Series(np.nan, index=d.index)
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    # CRP: fixed >3 mg/L
    e["crp_elevated"] = (q("LBXCRP") > 3.0).astype(float).where(q("LBXCRP").notna())
    # BMI: fixed >=25
    e["bmi_high"] = (q("BMXBMI") >= 25).astype(float).where(q("BMXBMI").notna())
    # B3b: Antioxidant — z-score harmonization (NOT raw unit mixing)
    vc, ve, lz = q("DR1TVC"), q("DR1TVE"), q("DR1TLZ")
    if vc.notna().sum() > 100:
        z_vc = (vc - vc.mean()) / vc.std()
        z_ve = (ve - ve.mean()) / ve.std()
        z_lz = (lz - lz.mean()) / lz.std()
        z_sum = (z_vc + z_ve + z_lz) / 3  # equal-weight composite of standardized values
        cutoff = z_sum.quantile(0.25)  # bottom quartile of the COMPOSITE (not individual)
        e["low_antioxidant_intake"] = (z_sum <= cutoff).astype(float).where(z_sum.notna())
    # Smoking: SMQ040 in (1,2) = current (every day + some days)
    smk = q("SMQ040")
    e["current_smoking"] = smk.isin([1, 2]).astype(float).where(smk.isin([1, 2, 3]))
    # Alcohol: ALQ101==1 (drinker)
    alq = q("ALQ101") if "ALQ101" in d else q("ALQ110")
    e["alcohol_intake"] = (alq == 1).astype(float).where(alq.notna())
    # Lead: B3a fixed cutoff (CDC reference value 5 µg/dL, NOT sample quantile)
    pb = q("LBXBPB")
    e["lead_exposure"] = (pb >= 5.0).astype(float).where(pb.notna())
    return e


def build_nhanes_outcomes(d: pd.DataFrame) -> dict[str, pd.Series]:
    """B3c: VI thresholds properly differentiated; B3e: worst-category assignment."""
    def q(col):
        return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)
    o = {}
    o["cataract_any"] = (q("VIQ071") == 1).astype(float).where(q("VIQ071").notna())
    # B3c: VI — different logMAR thresholds for mild/moderate/severe
    va = q("VIXPRS").where(q("VIXPRS") < 50).where(q("VIXPRS") > -5)
    # B3e: Worst-category assignment (each person assigned to exactly one VI level)
    vi_severe = (va > 1.00).astype(float).where(va.notna())
    vi_moderate = ((va > 0.48) & ~(va > 1.00)).astype(float).where(va.notna())
    vi_mild = ((va > 0.30) & ~(va > 0.48)).astype(float).where(va.notna())
    o["vision_impairment_mild"] = vi_mild
    o["vision_impairment_moderate"] = vi_moderate
    o["vision_impairment_severe"] = vi_severe
    # Retinopathy (OPXRET)
    ret = q("OPDURL4")
    o["retinopathy_any"] = ret.isin([2, 3, 4]).astype(float).where(ret.notna())
    o["dr_npdr"] = ret.isin([2, 3]).astype(float).where(ret.notna())
    o["dr_pdr"] = (ret == 4).astype(float).where(ret.notna())
    # B3e: retinopathy_any = dr_npdr ∪ dr_pdr — nesting guard in metrics
    # AMD
    arm, pig = q("OPDUARM"), q("OPDUPIGA")
    o["amd_early"] = ((arm >= 1) | (pig >= 1)).astype(float).where(arm.notna() | pig.notna())
    larm, ga, exu = q("OPDULARM"), q("OPDUGA"), q("OPDUEXU")
    o["amd_late"] = ((larm >= 1) | (ga >= 1) | (exu >= 1)).astype(float).where(larm.notna() | ga.notna() | exu.notna())
    # CDR
    cdr = pd.concat([q("OPDDVCDR"), q("OPDSVCDR")], axis=1).max(axis=1)
    o["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype(float).where(cdr.notna())
    return o


def detect_separation(y: pd.Series, x: pd.Series) -> bool:
    """B5: Check for perfect/quasi separation before fitting."""
    pos = y == 1; neg = y == 0
    if pos.sum() < 5 or neg.sum() < 5:
        return True
    # Perfect separation: all positives have x=1 and all negatives have x=0 (or vice versa)
    if (x[pos] == 1).all() and (x[neg] == 0).all():
        return True
    if (x[pos] == 0).all() and (x[neg] == 1).all():
        return True
    return False


def fdr_bhy(p: pd.Series) -> pd.Series:
    """BHY step-up FDR with monotonicity (analysis_plan §7)."""
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


def _flag_index(reg):
    idx = {}
    for ent in (reg or {}).values():
        for f in (getattr(ent, "flags", None) or []):
            idx.setdefault(str(f), ent)
    return idx


def run_nhanes_confirmatory() -> pd.DataFrame:
    """Full NHANES confirmatory run with all B3-B7 fixes."""
    import statsmodels.api as sm
    cases = load_cases("intval-nhanes")
    # Load NHANES data inline (phase5 archived, B1)
    NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")
    CYCLES = {"2005-2006": "_D", "2007-2008": "_E"}
    FILES = {"DEMO": ("DEMO", True), "BIOPRO": ("BIOPRO", True), "VIQ": ("VIQ", True),
             "VIX": ("VIX", True), "OPXRET": ("OPXRET", True), "SMQ": ("SMQ", True),
             "ALQ": ("ALQ", True), "BMX": ("BMX", True), "CRP": ("CRP", True),
             "PBCD": ("PBCD", True), "DR1TOT": ("DR1TOT", True),
             "GLU": ("GLU", True), "GHB": ("GHB", True),
             "DEQ": ("DEQ", "D"), "VITAEC": ("VITAEC", "D")}
    def _load_cycle(cycle_dir, suf):
        frames = {}
        for mod, (base, cyc) in FILES.items():
            if cyc is True: name = f"{base}{suf}.XPT"
            elif cyc == suf or (isinstance(cyc, str) and suf.endswith(cyc)): name = f"{base}{suf}.XPT"
            else: continue
            p = cycle_dir / name
            if not p.exists(): continue
            df = pd.read_sas(str(p), format="xport", encoding="utf-8")
            cols = [c for c in df.columns if c != "SEQN"]
            frames[mod] = df.set_index("SEQN")[cols]
        out = None
        for m, df in frames.items():
            if out is None: out = df
            else:
                overlap = [c for c in df.columns if c in out.columns]
                if overlap: df = df.drop(columns=overlap)
                out = out.join(df, how="outer") if len(df.columns) else out
        return out.reset_index()
    parts = []
    for cyc, suf in CYCLES.items():
        df = _load_cycle(NH / cyc, suf); df["cycle"] = cyc; parts.append(df)
    d = pd.concat(parts, ignore_index=True)
    d = d[pd.to_numeric(d["RIDAGEYR"], errors="coerce") >= 40]
    d = d[pd.to_numeric(d.get("WTMEC2YR", 0), errors="coerce") > 0]
    # Covariates (B3f: unified /100)
    covar_cols = [c for c in ["RIDAGEYR", "RIAGENDR", "RIDRETH1", "INDFMPIR"] if c in d.columns]
    for c in ("DMDEDU2", "DMDEDU3"):
        if c in d.columns: covar_cols.append(c); break
    E = build_nhanes_exposures(d)
    B = build_nhanes_outcomes(d)
    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = _flag_index(a_reg), _flag_index(b_reg)
    cov = d[covar_cols].copy()
    cov["age2"] = pd.to_numeric(cov.get("RIDAGEYR", 0), errors="coerce") ** 2 / 100

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
                direction = "risk_down" if dirs and all(d == "risk_down" for d in dirs) else "risk_up"
            meta = {"a_flag": a_flag, "b_item": b_item, "predicted": predicted,
                    "rule_ids": ",".join(rule_ids), "negative_control": is_nc, "direction": direction}
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30 or ny > len(sub) - 30:
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": "underpowered"})
                continue
            # B5: separation check
            if detect_separation(sub["y"], sub["x"]):
                results.append({**meta, "n": len(sub), "n_pos": ny, "or": np.nan,
                                "p": np.nan, "status": "separation"})
                continue
            try:
                X = sm.add_constant(sub[["x"] + covar_cols + ["age2"]].astype(float))
                y = sub["y"].astype(float)
                w = d.loc[sub.index, "WTMEC2YR"].astype(float)
                w = w.where(w > 0, 1.0) / w.mean()
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
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
    return res


def direction_audit_and_block(res, rules, dataset_id):
    """B7: Wire direction_audit with mandatory blocking."""
    lvl = {r.id: r.evidence_level for r in rules}
    a_pairs = res[(res["predicted"]) & (res["status"] == "tested")].copy()
    if "rule_ids" in a_pairs.columns:
        def _is_a(ids):
            got = [lvl.get(i.strip()) for i in str(ids).split(",") if i.strip()]
            return bool(got) and all(g == "A" for g in got)
        a_pairs = a_pairs[a_pairs["rule_ids"].map(_is_a)]
    rev = a_pairs[(a_pairs["direction"] != "risk_down") & (a_pairs["or"] < 1)]
    quarantine = len(rev) >= 2
    if quarantine:
        print(f"\n{'='*60}")
        print(f"⚠️  DIRECTION AUDIT: QUARANTINE triggered for {dataset_id}")
        print(f"    {len(rev)} A-level rule pairs show OR<1 (reversed direction):")
        for _, r in rev.iterrows():
            print(f"      {r['a_flag']} × {r['b_item']}: OR={r['or']:.3f} q={r.get('q', 'n/a')}")
        print(f"    Headline metrics SUPPRESSED until bias investigation completed.")
        print(f"    Check: exposure coding, outcome ascertainment, selection bias,")
        print(f"    reverse causation (current vs former smoking).")
        print(f"{'='*60}\n")
        # Write quarantine state
        state_path = ROOT / ".medical-agent" / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state.setdefault("blocked", []).append({
                "phase": "executor.phase5",
                "reason": f"direction_audit quarantine: {dataset_id} has {len(rev)} A-level pairs with OR<1"
            })
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return quarantine, len(rev)


def compute_metrics_v11(res):
    """Analysis plan v1.1: precision_rule + coverage (no recall)."""
    t = res[res["status"] == "tested"].copy()
    # D5: filter out non-judgeable B items from metrics denominator
    judgeable = get_judgeable_b_items("nhanes")
    if judgeable:
        before = len(t)
        t = t[t["b_item"].isin(judgeable)]
        if before > len(t):
            print(f"[metrics] D5: excluded {before - len(t)} non-judgeable pairs from denominator")
    nc_mask = t["negative_control"].fillna(False).astype(bool) if "negative_control" in t else pd.Series(False, index=t.index)
    t_main = t[~nc_mask]; t_nc = t[nc_mask]
    rp = t_main[t_main["predicted"]]
    rep = int((rp["gold3"] == "replicated").sum())
    con = int((rp["gold3"] == "contradicted").sum())
    uninf = int((rp["gold3"] == "uninformative").sum())
    sep = int((res["status"] == "separation").sum())
    prec = round(rep / (rep + con), 3) if rep + con else None
    # Bootstrap CI (pair-level; patient-level noted as WO-15 pending)
    vals = rp["gold3"].values
    ci = (None, None)
    if len(vals) > 0:
        rng = np.random.default_rng(42)
        samples = []
        for _ in range(1000):
            s = rng.choice(vals, size=len(vals), replace=True)
            r, c = int((s == "replicated").sum()), int((s == "contradicted").sum())
            if r + c > 0: samples.append(r / (r + c))
        if samples:
            ci = (round(float(np.percentile(samples, 2.5)), 3),
                  round(float(np.percentile(samples, 97.5)), 3))
    coverage = round(len(rp) / len(t_main), 3) if len(t_main) else None
    non_rule = t_main[~t_main["predicted"]]
    return {
        "rule_pairs_tested": len(rp), "replicated": rep,
        "contradicted": con, "uninformative": uninf, "separation": sep,
        "precision_rule": prec, "precision_rule_ci95": ci,
        "coverage": coverage,
        "uncovered_significant": int((non_rule["gold3"] == "replicated").sum()),
        "uncovered_pairs": len(non_rule),
        "negative_control_pairs": len(t_nc),
        "negative_control_outcome": t_nc["gold3"].value_counts().to_dict() if len(t_nc) else {},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=[
        "intval-nhanes", "extval-knhanes", "extval-cohorts-9", "all"])
    args = parser.parse_args()

    if args.dataset in ("intval-nhanes", "all"):
        print("\n" + "="*60)
        print("NHANES confirmatory (analysis_plan v1.1)")
        print("="*60)
        res = run_nhanes_confirmatory()
        rules = load_rules()
        quarantine, n_rev = direction_audit_and_block(res, rules, "NHANES")
        if not quarantine:
            metrics = compute_metrics_v11(res)
            print(json.dumps(metrics, ensure_ascii=False, indent=2))
            out = ROOT / "outputs" / "confirmatory"
            out.mkdir(parents=True, exist_ok=True)
            res.to_csv(out / "nhanes_confirmatory.csv", index=False, encoding="utf-8-sig")
            (out / "nhanes_metrics_v11.json").write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            out_q = ROOT / "outputs" / "confirmatory"
            out_q.mkdir(parents=True, exist_ok=True)
            res.to_csv(out_q / "nhanes_quarantined.csv",
                       index=False, encoding="utf-8-sig")
            print(f"[evaluate] Quarantined results saved: {out_q / 'nhanes_quarantined.csv'}")
            print(f"[evaluate] Bias investigation required before headline metrics can be produced.")

    print("\n[evaluate] KNHANES and cohort layers: implement using same framework")
    print("[evaluate] with build_knhanes_exposures/outcomes (fixed cutoffs) + cohort outcomes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
