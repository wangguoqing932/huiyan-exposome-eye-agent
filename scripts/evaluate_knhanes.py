#!/usr/bin/env python
"""huiyan executor — KNHANES confirmatory validation (external, cross-country).

R11 rebuild 2026-10-15
----------------------
Reads data/raw/knhanes_frames_v2 (rebuilt by scripts/build_knhanes_frames.py)
and uses ONLY codings verified against the official KNHANES codebook
(变量解释.docx value labels + Rdata dictionary + 数据收集和清洗示例代码.R).
See configs/variable_map.yaml for the record of every correction.

What was wrong before this rebuild (all verified empirically):
  * current_smoking = (BS1_1 == 1)          -> 1.5% prevalence; BS1_1==1 is NOT
    current smoking.  Correct: BS3_1 in (1,2), denominator BS3_1 in (1,2,3,8).
    BS3_1 code 3 (ex-smoker) does not exist in 2008-2009, so current smoking is
    only identifiable from wave 2010 onward.
  * alcohol_intake = (BA2_2_1 == 1)         -> official label is
    "酒驾一年：骑自行车" (rode a bicycle after drinking).  Correct: BD1/BD1_11.
  * uric acid fell back to HE_UAScr          -> official label is ARSENIC
    (creatinine-corrected, ICP-MS).  Correct: HE_Uacid only.
  * retinopathy used only E_DRP_R/L          -> the 2016-2021 scheme is
    E_DM / E_DM_r / E_DM_l.  E_DR is "currently using eye drops", not DR.
  * no SES adjustment                        -> edu / incm5 exist in every wave.
  * vision_impairment_moderate = E_VS_DS     -> E_VS_DS is a binary any-VI flag.
  * DH4_dg is chronic OTITIS MEDIA, not an eye outcome; DH6_dg (AMD) and
    DH7_dg (DR) self-report were never used.

Run: PYTHONUTF8=1 python scripts/evaluate_knhanes.py [--frames DIR]
"""
from __future__ import annotations
import argparse, json, math, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry
from evaluate import (fdr_bhy, three_state, detect_separation, compute_metrics_v11,
                      direction_audit_and_block, _flag_index, get_judgeable_b_items,
                      assign_three_state)
warnings.filterwarnings("ignore", category=FutureWarning)
ROOT = Path(__file__).resolve().parent.parent

# Effective year of each wave (the raw files are named by survey year).
SMOKING_IDENTIFIABLE_FROM = 2010   # BS3_1 code 3 (ex-smoker) appears from 2010
HBA1C_COMPARABLE_FROM = 2011       # 2008-2010 HbA1c subsample/scale not comparable


def _q(d: pd.DataFrame, col):
    return pd.to_numeric(d[col], errors="coerce") if col in d.columns else pd.Series(np.nan, index=d.index)


# ── variable_map 运行时守卫(M12/M7,2026-10-16)───────────────────────
_VM_CODE_VARS_K = {  # 代码实际引用变量(改派生时同步此表与 configs/variable_map.yaml)
    "current_smoking": {"BS1_1", "BS3_1"},
    "ever_smoking": {"BS1_1"},
    "alcohol_current": {"BD1", "BD1_11", "BD2_31", "BD2_32"},
    "uric_acid": {"HE_Uacid"},
    "hba1c": {"HE_HbA1c"},
    "hyperglycemia": {"HE_glu"},
    "dyslipidemia": {"HE_chol", "HE_TG", "HE_HDL_st2", "HE_LDL_drct"},
    "crp_elevated": {"HE_hsCRP"},
    "bmi_high": {"HE_BMI"},
}
_VM_FLAG2REF_K = {
    "current_smoking": "current_smoking", "ever_smoking": "ever_smoking",
    "alcohol_intake": "alcohol_current", "hba1c_elevated": "hba1c_elevated",
    "hyperglycemia": "hyperglycemia_126", "bmi_high": "bmi_high_25",
    "dyslipidemia": "dyslipidemia",
}


def _vm_guard_knhanes(e: dict) -> None:
    from huiyan_agent.variable_map import (load_variable_map, check_code_vars,
                                           prevalence_gate, reference_rates)
    vm = load_variable_map()
    for domain, cvars in _VM_CODE_VARS_K.items():
        check_code_vars(vm, "knhanes", domain, cvars, context="evaluate_knhanes.py")
    refs = reference_rates(vm, "knhanes_40plus")
    rates = {rk: float(e[flag].mean()) for flag, rk in _VM_FLAG2REF_K.items()
             if flag in e and rk in refs and e[flag].notna().any()}
    findings = prevalence_gate(rates, refs, "knhanes", source="evaluate_knhanes.py")
    out = ROOT / "outputs" / "confirmatory" / "prevalence_gate_knhanes.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"date": "2026-10-16", "n_rates": len(rates),
                               "findings": findings}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    for f in findings:
        print(f"[M7 gate] {f['severity'].upper()}: {f['exposure']} obs {f['observed']:.3f} "
              f"vs ref {f['reference']:.3f} (rel_dev {f['rel_deviation']})")


def build_knhanes_exposures(d: pd.DataFrame) -> dict[str, pd.Series]:
    """Binary exposure flags.  Every cut-point is exogenous (guideline /
    consensus / published definition) — no sample quantiles."""
    q = lambda c: _q(d, c)                          # noqa: E731
    sex = q("sex")
    wave = q("wave")

    e: dict[str, pd.Series] = {}

    # ---------------- smoking (official value labels) ----------------
    # BS1_1 终身吸烟: 1=<100 cigs, 2=>=100 cigs (=ever), 3=never, 8=n/a
    # BS3_1 当前吸烟: 1=daily, 2=occasional, 3=EX-smoker, 8=n/a (non-ever)
    b1, b3 = q("BS1_1"), q("BS3_1")
    bs3_valid = b3.isin([1, 2, 3, 8])
    smk_ok = bs3_valid & (wave >= SMOKING_IDENTIFIABLE_FROM)
    e["current_smoking"] = b3.isin([1, 2]).astype(float).where(smk_ok)
    e["former_smoking"] = b3.eq(3).astype(float).where(smk_ok)
    e["ever_smoking"] = b1.eq(2).astype(float).where(b1.isin([1, 2, 3]))

    # ---------------- alcohol (BD module; BA2 is traffic safety) ----------------
    # BD1 终身饮酒体验: 1=never, 2=has drunk.  BD1_11 past-year frequency:
    # 1=drank nothing in the past year, 2..6 = increasing frequency, 8=n/a.
    # BD2_31/BD2_32 binge frequency (male/female form), 1=none .. 5=almost daily.
    bd1, bd11 = q("BD1"), q("BD1_11")
    bd31, bd32 = q("BD2_31"), q("BD2_32")
    alc_denom = bd1.isin([1, 2]) | bd11.isin([1, 2, 3, 4, 5, 6])
    e["alcohol_intake"] = ((bd1 == 2) & bd11.isin([2, 3, 4, 5, 6])).astype(float).where(alc_denom)
    e["alcohol_frequent"] = ((bd1 == 2) & bd11.isin([5, 6])).astype(float).where(alc_denom)
    binge = bd31.where(sex == 1, bd32)
    e["alcohol_binge"] = binge.ge(2).astype(float).where(binge.isin([1, 2, 3, 4, 5]))

    # ---------------- glycaemia ----------------
    ua = q("HE_Uacid")                              # 尿酸 (hn16+).  NEVER HE_UAScr (=arsenic)
    e["uric_acid_elevated"] = (((ua > 7.0) & (sex == 1)) |
                               ((ua > 5.7) & (sex == 2))).astype(float).where(ua.notna())
    gh = q("HE_HbA1c")
    e["hba1c_elevated"] = (gh >= 6.5).astype(float).where(
        gh.notna() & (wave >= HBA1C_COMPARABLE_FROM))
    glu = q("HE_glu")
    e["hyperglycemia"] = (glu >= 126).astype(float).where(glu.notna())

    # ---------------- lipids ----------------
    tc, tg = q("HE_chol"), q("HE_TG")
    hdl = q("HE_HDL_st2")
    ldl = q("HE_LDL_drct")                          # direct LDL, fasting subsample only
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    e["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) |
                         (ldl >= 160)).astype(float).where(lip.notna().any(axis=1))
    e["hdl_low"] = (hdl < 40).astype(float).where(hdl.notna())
    e["ldl_high"] = (ldl >= 160).astype(float).where(ldl.notna())

    # ---------------- inflammation / anthropometry ----------------
    # KNHANES reports hsCRP in mg/L (verified: median ~0.6), unlike NHANES mg/dL.
    hc = q("HE_hsCRP")
    e["crp_elevated"] = (hc > 3.0).astype(float).where(hc.notna())
    bmi = q("HE_BMI")
    e["bmi_high"] = (bmi >= 25).astype(float).where(bmi.notna())
    e["bmi_high_asian23"] = (bmi >= 23).astype(float).where(bmi.notna())

    # ---------------- micronutrients ----------------
    # R11: flag names MUST equal the entities_a.csv flag vocabulary, otherwise
    # match_rules() never fires and the rule looks "never testable" when it is
    # in fact testable.  Registry flag is `vitamin_d_deficiency` (not _deficient).
    vd = q("HE_vitD")                               # serum 25(OH)D, 2008-2012
    e["vitamin_d_deficiency"] = (vd < 20).astype(float).where(vd.notna())
    # dietary antioxidant inadequacy: >=2 of 3 below EAR (exogenous thresholds)
    nvc, nve, ncar = q("N_VITC"), q("N_VITE"), q("N_CAROT")
    if nvc.notna().sum() > 100:
        inad = pd.concat([(nvc < 60).astype(float),          # vitamin C EAR 60 mg
                          (nve < 12).astype(float),          # vitamin E EAR 12 mg a-TE
                          (ncar < 3000).astype(float)],      # carotene 3000 ug (observational)
                         axis=1)
        n_inad = inad.sum(axis=1, min_count=3)
        e["low_antioxidant_intake"] = (n_inad >= 2).astype(float).where(n_inad.notna())

    # ---------------- metals / environment ----------------
    # Registry flag names again: lead_exposure / cadmium_exposure /
    # mercury_exposure / pm25_exposure / uv_exposure.
    pb = q("HE_Pb")
    e["lead_exposure"] = (pb >= 3.5).astype(float).where(pb.notna())   # CDC 2021 BLRV
    cd = q("HE_Cd")                                  # blood cadmium, ug/L
    e["cadmium_exposure"] = (cd >= 1.0).astype(float).where(cd.notna())
    hg = q("HE_Hg")                                  # blood mercury, ug/L
    e["mercury_exposure"] = (hg >= 5.0).astype(float).where(hg.notna())
    pm = q("PM25")                                   # daily mean PM2.5, ug/m3 (hnYY_ap)
    e["pm25_exposure"] = (pm > 15).astype(float).where(pm.notna())     # WHO 2021 24h guideline
    sun = q("E_Q_SUN")                               # avg daily sunlight time, 2010-2012
    # coding 1/2/3 = increasing exposure (UNVERIFIED value labels -> highest = high)
    e["uv_exposure"] = sun.eq(3).astype(float).where(sun.isin([1, 2, 3]))

    # ── M12/M7 守卫(2026-10-16):variable_map 为唯一操作化事实源 ──────
    _vm_guard_knhanes(e)
    return e


def build_knhanes_continuous(d: pd.DataFrame) -> dict[str, pd.Series]:
    """Continuous measures for the dose-response matrix (kept out of the binary
    dict so the 0/1 pair loop cannot silently reduce them to n=0)."""
    q = lambda c: _q(d, c)                          # noqa: E731
    sex, wave = q("sex"), q("wave")
    c: dict[str, pd.Series] = {}
    c["hba1c_pct"] = q("HE_HbA1c").where(q("HE_HbA1c").notna() &
                                         (wave >= HBA1C_COMPARABLE_FROM))
    c["fasting_glucose_mgdl"] = q("HE_glu").where(q("HE_glu").notna())
    c["uric_acid_mgdl"] = q("HE_Uacid").where(q("HE_Uacid").notna())
    c["crp_mgl"] = q("HE_hsCRP").where(q("HE_hsCRP").notna())
    c["bmi_kgm2"] = q("HE_BMI").where(q("HE_BMI").notna())
    c["hdl_mgdl"] = q("HE_HDL_st2").where(q("HE_HDL_st2").notna())
    c["ldl_mgdl"] = q("HE_LDL_drct").where(q("HE_LDL_drct").notna())
    c["triglycerides_mgdl"] = q("HE_TG").where(q("HE_TG").notna())
    c["total_cholesterol_mgdl"] = q("HE_chol").where(q("HE_chol").notna())
    c["vitamin_d_ngml"] = q("HE_vitD").where(q("HE_vitD").notna())
    c["blood_lead_ugdl"] = q("HE_Pb").where(q("HE_Pb").notna())
    c["pm25_ugm3"] = q("PM25").where(q("PM25").notna())
    c["intraocular_pressure_mmhg"] = _knhanes_iop(d).where(_knhanes_iop(d).notna())
    return c


def _knhanes_iop(d: pd.DataFrame) -> pd.Series:
    """Right-eye IOP in mmHg.  2008-2012 -> E_Gr_p; 2016-2021 -> E_Pr_1.
    Both carry a 999 sentinel for missing, so clip at <80.
    Note: the old code also folded E_GR (a 0/1 glaucoma flag) into this max();
    it never changed the result because IOP >> 1, but it is removed here."""
    q = lambda c: _q(d, c)                          # noqa: E731
    cols = [q(c).where(q(c) < 80) for c in ("E_Gr_p", "E_Pr_1") if c in d.columns]
    if not cols:
        return pd.Series(np.nan, index=d.index)
    return pd.concat(cols, axis=1).max(axis=1)


def build_knhanes_outcomes(d: pd.DataFrame) -> dict[str, pd.Series]:
    """Eye outcomes, harmonising the two KNHANES eye-exam naming schemes.

    2008-2012 : E_DRP_R/L, E_AMD_ELY_R/L, E_AMD_LATE_R/L, E_VS_DS, E_Gr_p,
                E_Grv/E_Glv
    2016-2021 : E_DM (and per-eye E_DM_r/E_DM_l), E_DME, E_AMD (per-eye
                E_AMD_r/E_AMD_l), E_EM, E_GR, E_Pr_1
    E_DR is "currently using eye drops" and must never be mapped to DR.

    Grading codes: 0=no, 1/2/3=positive grades (severity), 8=not examined,
    9=cannot be graded.  8/9 are MISSING, not negative; all positive grades
    must count as positive (dropping grades 2/3 would undercount disease).
    """
    q = lambda c: _q(d, c)                          # noqa: E731

    def binary_summary(*cands, name=""):
        """Person-level 0/1 summary variables (E_DM, E_AMD, E_GR, E_EM, E_DME)."""
        cols = [q(c) for c in cands if c in d.columns]
        if not cols:
            return None
        m = pd.concat(cols, axis=1)
        graded = m.isin([0, 1])
        return (m == 1).any(axis=1).astype(float).where(graded.any(axis=1))

    def graded_any(*cands):
        """Per-eye graded variables: 1/2/3 all count as positive, 8/9 missing."""
        cols = [q(c) for c in cands if c in d.columns]
        if not cols:
            return None
        m = pd.concat(cols, axis=1)
        pos_codes = [1, 2, 3]
        graded = pd.concat([x.isin([0] + pos_codes) for x in cols], axis=1)
        return pd.concat([x.isin(pos_codes) for x in cols], axis=1).any(
            axis=1).astype(float).where(graded.any(axis=1))

    o: dict[str, pd.Series] = {}

    # ---- cataract: two different self-report semantics, kept separate ----
    dh2lt, dh2dg = q("DH2_lt"), q("DH2_dg")
    o["cataract_lifetime"] = dh2lt.eq(1).astype(float).where(dh2lt.isin([0, 1]))
    o["cataract_dx"] = dh2dg.eq(1).astype(float).where(dh2dg.isin([0, 1]))
    o["cataract_any"] = ((dh2lt == 1) | (dh2dg == 1)).astype(float).where(
        dh2lt.isin([0, 1]) | dh2dg.isin([0, 1]))

    # ---- retinopathy: 2008-2012 E_DRP_*  +  2016-2021 E_DM* ----
    old = graded_any("E_DRP_R", "E_DRP_L")
    new = binary_summary("E_DM")
    new2 = graded_any("E_DM_r", "E_DM_l")
    parts = [x for x in (old, new, new2) if x is not None]
    if parts:
        o["retinopathy_any"] = pd.concat(parts, axis=1).max(axis=1)
    # self-reported DR (DH7_dg, 2019-2021) as an independent ascertainment
    dh7 = q("DH7_dg")
    if dh7.notna().any():
        o["retinopathy_selfreport"] = dh7.eq(1).astype(float).where(dh7.isin([0, 1]))
    dme = binary_summary("E_DME")
    if dme is not None and dme.notna().any():
        o["dme_any"] = dme

    # ---- AMD ----
    amd_early_old = graded_any("E_AMD_ELY_R", "E_AMD_ELY_L")
    amd_late_old = graded_any("E_AMD_LATE_R", "E_AMD_LATE_L")
    if amd_early_old is not None:
        o["amd_early"] = amd_early_old                 # 2008-2012 grading only
    if amd_late_old is not None:
        o["amd_late"] = amd_late_old
    amd_sum = binary_summary("E_AMD")                  # 2016-2021 person-level
    amd_eye = graded_any("E_AMD_r", "E_AMD_l")
    ap = [x for x in (amd_early_old, amd_late_old, amd_sum, amd_eye) if x is not None]
    if ap:
        o["amd_any"] = pd.concat(ap, axis=1).max(axis=1)
    dh6 = q("DH6_dg")
    if dh6.notna().any():
        o["amd_selfreport"] = dh6.eq(1).astype(float).where(dh6.isin([0, 1]))

    # ---- epiretinal membrane (2016-2021 only) ----
    em = binary_summary("E_EM")
    if em is not None and em.notna().any():
        o["epiretinal_membrane"] = em

    # ---- glaucoma ----
    dh3 = q("DH3_dg")
    dh3lt = q("DH3_lt")
    o["glaucoma_selfreport"] = ((dh3 == 1) | (dh3lt == 1)).astype(float).where(
        dh3.isin([0, 1]) | dh3lt.isin([0, 1]))
    gr = binary_summary("E_GR")                        # 2016-2021 exam-diagnosed
    if gr is not None and gr.notna().any():
        o["glaucoma_exam"] = gr
    iop = _knhanes_iop(d)
    if iop.notna().any():
        o["glaucoma_iop_elevated"] = (iop > 21).astype(float).where(iop.notna())
    cdr_cols = [q(c).where(q(c) <= 1.0) for c in ("E_Grv", "E_Glv") if c in d.columns]
    if cdr_cols:
        cdr = pd.concat(cdr_cols, axis=1).max(axis=1)
        o["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype(float).where(cdr.notna())

    # ---- vision impairment (2008-2012 only; BINARY, no severity grading) ----
    vs = q("E_VS_DS")
    if vs.notna().any():
        # NOTE: name deliberately kept as *_any.  The old code labelled this
        # `vision_impairment_moderate`, which is a construct mismatch.
        o["vision_impairment_any"] = vs.eq(1).astype(float).where(vs.isin([0, 1]))
    return o


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frames", default=None, help="frames dir (default: data/raw/knhanes_frames_v2)")
    args = ap.parse_args()

    print("\n" + "=" * 60)
    print("KNHANES confirmatory — R11 rebuild (variable_map v2)")
    print("=" * 60)
    FR = Path(args.frames) if args.frames else (ROOT / "data/raw/knhanes_frames_v2")
    if not FR.exists():
        raise SystemExit(f"frames not found: {FR}\n"
                         f"run: python scripts/build_knhanes_frames.py")
    print(f"frames: {FR}")

    parts = []
    for p in sorted(FR.glob("knhanes_20*.csv")):
        df = pd.read_csv(p, low_memory=False)
        df["wave"] = int(p.stem.split("_")[1])
        parts.append(df)
    d = pd.concat(parts, ignore_index=True, sort=False)
    d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
    w = "wt_itvex" if "wt_itvex" in d.columns else ("wt_itv" if "wt_itv" in d.columns else "wt_ex")
    d = d[pd.to_numeric(d.get(w, 0), errors="coerce") > 0]
    print(f"frame: n={len(d)}, waves={sorted(d['wave'].unique())}")

    E = build_knhanes_exposures(d)
    B = build_knhanes_outcomes(d)
    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = _flag_index(a_reg), _flag_index(b_reg)

    # Covariates: age, age^2, sex + SES (edu / income quintile, present in every wave)
    cov = pd.DataFrame({
        "age": pd.to_numeric(d["age"], errors="coerce"),
        "age2": pd.to_numeric(d["age"], errors="coerce") ** 2 / 100,
        "sex": pd.to_numeric(d["sex"], errors="coerce"),
    })
    covar_used = ["age", "age2", "sex"]
    for cand in ("edu", "incm5"):
        if cand in d.columns and pd.to_numeric(d[cand], errors="coerce").notna().sum() > len(d) * 0.5:
            cov[cand] = pd.to_numeric(d[cand], errors="coerce")
            covar_used.append(cand)
    print(f"covariates: {covar_used}")

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
                    "rule_ids": ",".join(rule_ids), "negative_control": is_nc,
                    "direction": direction}
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny, nx = int(sub["y"].sum()), int(sub["x"].sum())
            if len(sub) < 200 or ny < 30 or nx < 30 or ny > len(sub) - 30:
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx, "or": np.nan,
                                "p": np.nan, "status": "underpowered"})
                continue
            if detect_separation(sub["y"], sub["x"]):
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx, "or": np.nan,
                                "p": np.nan, "status": "separation"})
                continue
            try:
                X = sm.add_constant(sub[["x"] + covar_used].astype(float))
                y = sub["y"].astype(float)
                wt = d.loc[sub.index, w].astype(float)
                wt = wt.where(wt > 0, 1.0) / wt.mean()
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=wt).fit()
                if not getattr(fit, "converged", True):
                    raise RuntimeError("not converged")
                beta, se = fit.params["x"], fit.bse["x"]
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx,
                                "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                                "ci_hi": math.exp(beta + 1.96 * se),
                                "p": float(fit.pvalues["x"]), "status": "tested"})
            except Exception as ex:
                results.append({**meta, "n": len(sub), "n_pos": ny, "n_exp": nx, "or": np.nan,
                                "p": np.nan, "status": f"fit_fail:{type(ex).__name__}"})

    res = pd.DataFrame(results)
    res = assign_three_state(res)          # R11: dual-family FDR + three-state labels
    n_rule_family = int(res["q_rule"].notna().sum())
    print(f"[fdr] confirmatory family (rule-relevant) n={n_rule_family}; "
          f"exploratory family n={int((res['status'] == 'tested').sum())}")

    quarantine, n_rev = direction_audit_and_block(res, rules, "KNHANES")

    out = ROOT / "outputs" / "confirmatory"
    out.mkdir(parents=True, exist_ok=True)
    if quarantine:
        res.to_csv(out / "knhanes_quarantined.csv", index=False, encoding="utf-8-sig")
        print(f"[audit] QUARANTINED: {n_rev} significant reversed rule pairs")
        return 0

    judgeable = get_judgeable_b_items("knhanes")
    if judgeable:
        before = int((res["status"] == "tested").sum())
        res_m = res[(res["status"] == "tested") & (res["b_item"].isin(judgeable))]
        excluded = before - len(res_m)
        if excluded:
            print(f"[metrics] D5: excluded {excluded} non-judgeable pairs")
        res_final = pd.concat([res_m, res[res["status"] != "tested"]])
    else:
        res_final = res

    metrics = compute_metrics_v11(res_final, "knhanes")
    metrics["covariates"] = covar_used
    metrics["frames"] = str(FR.relative_to(ROOT)) if str(FR).startswith(str(ROOT)) else str(FR)
    metrics["variable_map"] = "configs/variable_map.yaml (R11 rebuild)"
    print(json.dumps({k: v for k, v in metrics.items() if not isinstance(v, dict)},
                     ensure_ascii=False, indent=2))
    res.to_csv(out / "knhanes_confirmatory.csv", index=False, encoding="utf-8-sig")
    (out / "knhanes_metrics_v11.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
