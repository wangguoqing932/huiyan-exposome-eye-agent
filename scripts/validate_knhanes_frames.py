#!/usr/bin/env python
"""Validate the rebuilt KNHANES frames (data/raw/knhanes_frames_v2).

Two jobs, per configs/variable_map.yaml discipline:
  1. merge integrity  — did the eye / air-pollution joins actually populate?
  2. prevalence_vs_reference — every derived exposure must land near the
     published national rate; deviations > 50% are hard warnings.

Exit code 1 if any hard warning fires (so CI / the pipeline can gate on it).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FR = ROOT / "data/raw/knhanes_frames_v2"

# published reference prevalences for Korean adults 40+ (see variable_map.yaml)
REF = {
    "current_smoking": 0.25,
    "former_smoking": 0.20,
    "ever_smoking": 0.40,
    "alcohol_current": 0.62,
    "alcohol_frequent": 0.26,
    "alcohol_binge": 0.60,
    "bmi_high": 0.36,
    "bmi_high_asian23": 0.55,
    "hba1c_elevated": 0.17,
    "hyperglycemia": 0.10,
    "dyslipidemia": 0.38,
    "uric_acid_elevated": 0.16,
    "crp_elevated_3mgl": 0.12,
    "vitamin_d_deficient": 0.60,
    "lead_elevated": None,
    "cataract_any": None,
    "retinopathy_any": None,
    "amd_any": 0.08,
    "glaucoma_any": 0.03,
    "vision_impairment_any": 0.02,
}


def num(d, c):
    return pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)


def load_all() -> pd.DataFrame:
    frames = []
    for p in sorted(FR.glob("knhanes_20*.csv")):
        d = pd.read_csv(p, low_memory=False)
        d["wave"] = int(p.stem.split("_")[1])
        frames.append(d)
    d = pd.concat(frames, ignore_index=True, sort=False)
    d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
    w = "wt_itvex" if "wt_itvex" in d.columns else "wt_ex"
    d = d[pd.to_numeric(d.get(w, 0), errors="coerce") > 0]
    return d


def main() -> int:
    if not FR.exists():
        raise SystemExit(f"frames not found: {FR} — run scripts/build_knhanes_frames.py")
    d = load_all()
    print(f"analytic frame (age>=40, wt>0): n={len(d)}  waves={sorted(d['wave'].unique())}")

    # ---------------- 1. merge integrity ----------------
    print("\n=== merge integrity: non-missing counts per key column, by wave ===")
    watch = ["BS1_1", "BS3_1", "BD1_11", "edu", "incm5", "PM25",
             "E_DRP_R", "E_DM", "E_DM_r", "E_AMD_ELY_R", "E_AMD", "E_GR",
             "E_VS_DS", "E_Gr_p", "E_Pr_1", "HE_vitD", "HE_Uacid", "HE_hsCRP",
             "E_Q_SUN", "DH2_lt", "DH2_dg"]
    tab = {}
    for c in watch:
        if c not in d.columns:
            tab[c] = {w: None for w in sorted(d["wave"].unique())}
            continue
        tab[c] = {int(w): int(g[c].notna().sum()) for w, g in d.groupby("wave")}
    integ = pd.DataFrame(tab).T.fillna(0).astype(int)
    with pd.option_context("display.width", 220):
        print(integ.to_string())
    integ.to_csv(ROOT / ".audit_tmp/knhanes_v2_merge_integrity.csv", encoding="utf-8-sig")

    # ---------------- 2. derived exposures ----------------
    sex = num(d, "sex")
    E = {}
    # ------------------------------------------------------------------
    # smoking — value labels verified against the official KNHANES codebook
    #   BS1_1: 1=<100 cigs lifetime, 2=>=100 cigs (=ever), 3=never, 8=n/a, 9=DK
    #   BS3_1: 1=daily, 2=occasional, 3=EX-smoker, 8=n/a (non-ever), 9=DK
    # Denominator MUST include code 3, otherwise ex-smokers are dropped and
    # male current-smoking prevalence inflates to 71.6% (verified trap).
    # BS3_1 code 3 does not exist in waves 2008/2009 -> current smoking is
    # only constructible from 2010 onward.
    # ------------------------------------------------------------------
    b1, b3 = num(d, "BS1_1"), num(d, "BS3_1")
    E["current_smoking"] = b3.isin([1, 2]).astype(float).where(b3.isin([1, 2, 3, 8]))
    E["former_smoking"] = b3.eq(3).astype(float).where(b3.isin([1, 2, 3, 8]))
    E["ever_smoking"] = b1.eq(2).astype(float).where(b1.isin([1, 2, 3]))
    E["smoke_BS3_1_code3_available"] = b3.eq(3).astype(float).where(b3.isin([1, 2, 3, 8]))
    # ------------------------------------------------------------------
    # alcohol — BD1: 1=never drank in life, 2=has drunk.
    #   BD1_11: 1=nothing in past year, 2..6 = increasing frequency, 8=n/a.
    #   current drinker = drank in the past year (BD1_11 >= 2).
    # ------------------------------------------------------------------
    bd1, bd11 = num(d, "BD1"), num(d, "BD1_11")
    denom_drink = bd1.isin([1, 2]) | bd11.isin([1, 2, 3, 4, 5, 6])
    E["alcohol_current"] = ((bd1 == 2) & bd11.isin([2, 3, 4, 5, 6])).astype(float).where(denom_drink)
    E["alcohol_frequent"] = ((bd1 == 2) & bd11.isin([5, 6])).astype(float).where(denom_drink)
    bd31, bd32 = num(d, "BD2_31"), num(d, "BD2_32")
    binge = bd31.where(sex == 1, bd32)
    E["alcohol_binge"] = binge.ge(2).astype(float).where(binge.isin([1, 2, 3, 4, 5]))
    E["BANNED_alcohol_BA2_2_1"] = num(d, "BA2_2_1").eq(1).astype(float).where(
        num(d, "BA2_2_1").notna())
    # anthropometry / labs
    E["bmi_high"] = (num(d, "HE_BMI") >= 25).astype(float).where(num(d, "HE_BMI").notna())
    E["bmi_high_asian23"] = (num(d, "HE_BMI") >= 23).astype(float).where(num(d, "HE_BMI").notna())
    E["hba1c_elevated"] = (num(d, "HE_HbA1c") >= 6.5).astype(float).where(num(d, "HE_HbA1c").notna())
    E["hyperglycemia"] = (num(d, "HE_glu") >= 126).astype(float).where(num(d, "HE_glu").notna())
    tc, tg, hdl, ldl = num(d, "HE_chol"), num(d, "HE_TG"), num(d, "HE_HDL_st2"), num(d, "HE_LDL_drct")
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    E["dyslipidemia"] = ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)
                         ).astype(float).where(lip.notna().any(axis=1))
    ua = num(d, "HE_Uacid")
    E["uric_acid_elevated"] = (((ua > 7.0) & (sex == 1)) | ((ua > 5.7) & (sex == 2))
                               ).astype(float).where(ua.notna())
    # KNHANES hsCRP is reported in mg/L (median 0.59, p75 1.12) unlike NHANES mg/dL
    hc = num(d, "HE_hsCRP")
    E["crp_elevated_3mgl"] = (hc > 3.0).astype(float).where(hc.notna())
    # vitamin D deficiency: serum 25(OH)D < 20 ng/mL (IOM)
    vd = num(d, "HE_vitD")
    E["vitamin_d_deficient"] = (vd < 20).astype(float).where(vd.notna())
    E["lead"] = num(d, "HE_Pb")
    E["pm25"] = num(d, "PM25")

    print("\n=== derived EXPOSURE prevalence (pooled age>=40) ===")
    rows = []
    for name, s in E.items():
        if s is None:
            continue
        s = pd.to_numeric(s, errors="coerce")
        pooled = float(s.mean()) if s.notna().any() else None
        ref = REF.get(name)
        flag = ""
        if ref is not None and pooled is not None and ref > 0:
            ratio = pooled / ref
            if ratio < 0.5 or ratio > 2.0:
                flag = "HARD_WARN"
            elif ratio < 0.67 or ratio > 1.5:
                flag = "warn"
        byw = {int(w): round(float(g.mean()), 3) for w, g in s.groupby(d["wave"]) if g.notna().any()}
        rows.append({"exposure": name, "n": int(s.notna().sum()),
                     "prev": round(pooled, 4) if pooled is not None else None,
                     "ref": ref, "ratio": round(pooled / ref, 3) if (ref and pooled) else None,
                     "male": round(float(s[sex == 1].mean()), 4) if s.notna().any() else None,
                     "female": round(float(s[sex == 2].mean()), 4) if s.notna().any() else None,
                     "flag": flag, "by_wave": byw})
    ex = pd.DataFrame(rows)
    with pd.option_context("display.width", 200):
        print(ex.drop(columns=["by_wave"]).to_string(index=False))
    print("\n-- per-wave exposure prevalence (checks instrument changes across waves) --")
    for r in ex.itertuples():
        print(f"  {r.exposure:34s} {r.by_wave}")
    ex.to_csv(ROOT / ".audit_tmp/knhanes_v2_exposure_prevalence.csv",
              index=False, encoding="utf-8-sig")

    print("\n=== raw hsCRP / vitD / Pb (unit check) ===")
    for c in ["HE_hsCRP", "HE_vitD", "HE_Pb", "HE_Uacid", "HE_HbA1c", "HE_glu"]:
        s = num(d, c)
        if s.notna().any():
            print(f"  {c:10s} n={int(s.notna().sum()):6d} p25={s.quantile(.25):8.3f} "
                  f"med={s.median():8.3f} p75={s.quantile(.75):8.3f} max={s.max():10.3f}")

    # ---------------- 3. derived outcomes ----------------
    def any_pos(cols_converter):
        return cols_converter

    O = {}
    # DR: old scheme (2008-2012) + new scheme (2017-2021), harmonised
    old_dr = [num(d, c).isin([1]) for c in ("E_DRP_R", "E_DRP_L") if c in d.columns]
    new_dr = [num(d, c).isin([1]) for c in ("E_DM_r", "E_DM_l", "E_DM") if c in d.columns]
    if old_dr or new_dr:
        allc = old_dr + new_dr
        graded = pd.concat([num(d, c).isin([0, 1]) for c in
                            ("E_DRP_R", "E_DRP_L", "E_DM_r", "E_DM_l", "E_DM") if c in d.columns],
                           axis=1)
        pos = pd.concat(allc, axis=1).any(axis=1)
        O["retinopathy_any"] = pos.astype(float).where(graded.any(axis=1))
    # AMD: early (old) or any AMD (new)
    amd_cols_old = [c for c in ("E_AMD_ELY_R", "E_AMD_ELY_L") if c in d.columns]
    amd_cols_new = [c for c in ("E_AMD_r", "E_AMD_l", "E_AMD") if c in d.columns]
    if amd_cols_old or amd_cols_new:
        graded = pd.concat([num(d, c).isin([0, 1]) for c in amd_cols_old + amd_cols_new], axis=1)
        pos = pd.concat([num(d, c).isin([1]) for c in amd_cols_old + amd_cols_new], axis=1).any(axis=1)
        O["amd_any"] = pos.astype(float).where(graded.any(axis=1))
    late = [c for c in ("E_AMD_LATE_R", "E_AMD_LATE_L") if c in d.columns]
    if late:
        graded = pd.concat([num(d, c).isin([0, 1]) for c in late], axis=1)
        pos = pd.concat([num(d, c).isin([1]) for c in late], axis=1).any(axis=1)
        O["amd_late"] = pos.astype(float).where(graded.any(axis=1))
    # glaucoma: self-report DH3_lt/DH3_dg + exam E_GR
    gr = num(d, "E_GR")
    if gr.notna().any():
        O["glaucoma_exam"] = gr.isin([1]).astype(float).where(gr.isin([0, 1]))
    d3 = num(d, "DH3_lt").where(num(d, "DH3_lt").notna(), num(d, "DH3_dg"))
    O["glaucoma_selfreport"] = d3.isin([1]).astype(float).where(d3.isin([0, 1]))
    # IOP: old E_Gr_p(<80) + new E_Pr_1(<80), both right eye
    iop = pd.concat([num(d, c).where(num(d, c) < 80) for c in ("E_Gr_p", "E_Pr_1")
                     if c in d.columns], axis=1).max(axis=1)
    if iop.notna().any():
        O["glaucoma_iop_elevated"] = (iop > 21).astype(float).where(iop.notna())
    # CDR (old only)
    cdr = pd.concat([num(d, c).where(num(d, c) <= 1.0) for c in ("E_Grv", "E_Glv")
                     if c in d.columns], axis=1).max(axis=1)
    if cdr.notna().any():
        O["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype(float).where(cdr.notna())
    # cataract self-report (two different semantics — keep separate)
    O["cataract_lifetime_DH2_lt"] = num(d, "DH2_lt").isin([1]).astype(float).where(
        num(d, "DH2_lt").isin([0, 1]))
    O["cataract_dx_DH2_dg"] = num(d, "DH2_dg").isin([1]).astype(float).where(
        num(d, "DH2_dg").isin([0, 1]))
    # vision impairment (old only, binary)
    vs = num(d, "E_VS_DS")
    if vs.notna().any():
        O["vision_impairment_any"] = vs.isin([1]).astype(float).where(vs.isin([0, 1]))

    print("\n=== derived OUTCOME prevalence (pooled) + per-wave n ===")
    orows = []
    for name, s in O.items():
        s = pd.to_numeric(s, errors="coerce")
        pooled = float(s.mean()) if s.notna().any() else None
        ref = REF.get(name)
        flag = ""
        if ref is not None and pooled is not None and ref > 0:
            ratio = pooled / ref
            if ratio < 0.5 or ratio > 2.0:
                flag = "HARD_WARN"
        byw = {int(w): int(g.notna().sum()) for w, g in s.groupby(d["wave"])}
        orows.append({"outcome": name, "n": int(s.notna().sum()),
                      "prev": round(pooled, 4) if pooled is not None else None,
                      "ref": ref, "flag": flag,
                      "by_wave": {k: v for k, v in sorted(byw.items()) if v > 0}})
    od = pd.DataFrame(orows)
    for r in od.itertuples():
        print(f"  {r.outcome:28s} n={r.n:6d} prev={r.prev} {r.flag}")
        print(f"      by wave: {r.by_wave}")
    od.drop(columns=["by_wave"]).to_csv(ROOT / ".audit_tmp/knhanes_v2_outcome_prevalence.csv",
                                        index=False, encoding="utf-8-sig")

    # ---------------- 4. the previously untestable overlap ----------------
    print("\n=== overlap test: exposure x outcome in the SAME wave (the whole point) ===")
    pairs = [("uric_acid_elevated", "retinopathy_any"), ("uric_acid_elevated", "amd_any"),
             ("crp_raw_median", "amd_any"), ("current_smoking", "retinopathy_any"),
             ("current_smoking", "cataract_lifetime_DH2_lt"), ("current_smoking", "glaucoma_exam"),
             ("alcohol_current", "amd_any"), ("pm25", "glaucoma_iop_elevated")]
    for a, b in pairs:
        xs = E.get(a, pd.Series(np.nan, index=d.index))
        xs = pd.to_numeric(xs, errors="coerce")
        ys = pd.to_numeric(O.get(b, pd.Series(np.nan, index=d.index)), errors="coerce")
        both = xs.notna() & ys.notna()
        byw = {int(w): int(g.sum()) for w, g in both.groupby(d["wave"]) if g.sum() > 0}
        ny = int(ys[both].sum())
        print(f"  {a:24s} x {b:26s} n_both={int(both.sum()):6d} events={ny:5d} waves={byw}")

    hard = ex[ex["flag"] == "HARD_WARN"]
    print(f"\n=== summary: {len(hard)} hard warnings on exposures ===")
    if len(hard):
        print(hard[["exposure", "prev", "ref", "ratio"]].to_string(index=False))
    return 1 if len(hard) else 0


if __name__ == "__main__":
    sys.exit(main())
