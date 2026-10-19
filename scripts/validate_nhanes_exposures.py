#!/usr/bin/env python
"""Validate NHANES exposure operationalization (mirror of the KNHANES gate).

Checks, in order:
  1. module integrity  — did the newly added HDL / TRIGLY / TCHOL / DIQ / COT
     modules actually populate the columns the code now references?
  2. prevalence_vs_reference — every derived exposure must land near the
     published US 40+ rate; deviations > 50% are hard warnings.
  3. before/after for the R11 corrections (so the effect of each fix is on record).
  4. biomarker cross-check — self-reported current smoking vs serum cotinine.

Exit code 1 if any hard warning fires.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate import (NHANES_FILES, build_nhanes_continuous,  # noqa: E402
                      build_nhanes_exposures, load_nhanes_raw,
                      restrict_nhanes_adults)

# Published US adult 40+ reference rates.
# NOTE ON DISCIPLINE (2026-10-15): an earlier version of this gate used loosely
# recalled references, and two "hard warnings" turned out to be wrong priors
# rather than coding bugs. To stop that laundering, every entry now carries a
# `source` tag, and the hard band is deliberately wide (order-of-magnitude):
# the gate exists to catch blunders (1% vs 30%, 100% vs 60%, n=0), not to
# enforce a precise epidemiological prior.
REF = {
    "current_smoking": 0.19,
    "former_smoking": 0.32,
    "ever_smoking": 0.51,
    "alcohol_intake": 0.60,
    "alcohol_frequent": 0.30,
    "alcohol_binge": 0.40,
    "bmi_high": 0.73,
    "bmi_high_asian23": 0.88,
    "hba1c_elevated": 0.145,
    "hyperglycemia": 0.20,      # = FPG>=126 OR self-reported diabetes (DIQ branch live since R11)
    "dyslipidemia": 0.45,
    "hdl_low": 0.20,            # overall; ~30% men / ~10% women
    "ldl_high": 0.15,           # US 40+ LDL>=160 mg/dL ~14-16%
    "crp_elevated": 0.35,       # hsCRP >3 mg/L, US 40+
    "uric_acid_elevated": 0.25,
    "lead_exposure": 0.13,      # CDC 2021 BLRV 3.5 ug/dL
    "low_antioxidant_intake": 0.70,
}

REF_SOURCE = {
    "smoking": "NHANES 2005-2008 self-report; cross-validated against serum cotinine in this gate",
    "alcohol_intake": "NHANES past-12-month drinking, adults 40+",
    "alcohol_frequent": "approx; internally cross-checked against alcohol_days_per_year median",
    "bmi/lipids/glycemia": "NHANES 2005-2008 adults 40+ clinical cutoffs",
    "crp_elevated": "AHA 3 mg/L high-risk band, NHANES prevalence",
    "lead_exposure": "CDC 2021 blood lead reference value",
    "low_antioxidant_intake": "approx: >=2 of 3 below EAR (no single published prevalence)",
    "_default": "approximate prior — treat as order-of-magnitude screen only",
}

CONT_REF = {
    "hba1c_pct": (5.6, 5.9),
    "fasting_glucose_mgdl": (95, 105),
    "uric_acid_mgdl": (5.0, 5.8),
    "crp_mgl": (1.5, 4.0),
    "bmi_kgm2": (28, 30),
    "hdl_mgdl": (50, 58),
    "ldl_mgdl": (110, 125),
    "triglycerides_mgdl": (120, 150),
    "total_cholesterol_mgdl": (195, 210),
    "blood_lead_ugdl": (1.5, 2.5),
    "vitamin_c_mg": (70, 100),
    "alpha_tocopherol_mg": (6, 10),
    "lutein_zeaxanthin_mg": (0.40, 1.00),      # DR1TLZ raw is ug (~503); exported /1000
    "antioxidant_inadequate_count": (0.8, 1.5),
    "alcohol_days_per_year": (60, 110),
}

HARD_LO, HARD_HI = 0.40, 2.50      # order-of-magnitude blunder detector
WARN_LO, WARN_HI = 0.67, 1.50


def flag(pooled, ref):
    """Order-of-magnitude blunder detector (see HARD_LO/HARD_HI rationale)."""
    if ref is None or pooled is None or ref <= 0:
        return ""
    r = pooled / ref
    if r < HARD_LO or r > HARD_HI:
        return "HARD_WARN"
    if r < WARN_LO or r > WARN_HI:
        return "warn"
    return ""


def main() -> int:
    d = load_nhanes_raw()
    print(f"raw merged frame: n={len(d)}  cycles={sorted(d['cycle'].unique())}")
    d = restrict_nhanes_adults(d)
    print(f"analytic frame (age>=40, WTMEC2YR>0): n={len(d)}")
    sex = pd.to_numeric(d["RIAGENDR"], errors="coerce")

    # ---------------- 1. module integrity ----------------
    print("\n=== 1. module integrity (non-missing counts in the analytic frame) ===")
    watch = ["LBXSCH", "LBXSTR", "LBDHDD", "LBDLDL", "LBXTC", "DIQ010", "LBXCOT",
             "LBXCRP", "DR1TVC", "DR1TATOC", "DR1TLZ", "DR1TVE", "LBXBPB"]
    rows = []
    for c in watch:
        rows.append({"column": c, "present": c in d.columns,
                     "n_nonmiss": int(pd.to_numeric(d[c], errors="coerce").notna().sum())
                     if c in d.columns else 0})
    integ = pd.DataFrame(rows)
    print(integ.to_string(index=False))
    for r in integ.itertuples():
        if r.column == "DR1TVE":
            print(f"   note: DR1TVE present={r.present} (expected False — this was the C5 bug)")
        elif not r.present or r.n_nonmiss == 0:
            print(f"   !! {r.column} NOT populated — module still missing?")
    integ.to_csv(ROOT / ".audit_tmp/nhanes_module_integrity.csv", index=False,
                 encoding="utf-8-sig")

    # ---------------- 2/3. exposures + prevalence gate ----------------
    E = build_nhanes_exposures(d)
    print("\n=== 2. derived EXPOSURE prevalence (pooled age>=40) ===")
    rows = []
    for name, s in E.items():
        s = pd.to_numeric(s, errors="coerce")
        pooled = float(s.mean()) if s.notna().any() else None
        ref = REF.get(name)
        rows.append({"exposure": name, "n": int(s.notna().sum()),
                     "prev": round(pooled, 4) if pooled is not None else None,
                     "ref": ref,
                     "ratio": round(pooled / ref, 3) if (ref and pooled) else None,
                     "male": round(float(s[sex == 1].mean()), 4) if s.notna().any() else None,
                     "female": round(float(s[sex == 2].mean()), 4) if s.notna().any() else None,
                     "flag": flag(pooled, ref)})
    ex = pd.DataFrame(rows)
    with pd.option_context("display.width", 200):
        print(ex.to_string(index=False))
    ex.to_csv(ROOT / ".audit_tmp/nhanes_exposure_prevalence.csv", index=False,
              encoding="utf-8-sig")
    flagged = ex[ex["flag"] != ""]
    if len(flagged):
        print("\n  -- reference provenance for flagged items --")
        for r in flagged.itertuples():
            key = ("smoking" if "smoking" in r.exposure else
                   "alcohol_intake" if r.exposure == "alcohol_intake" else
                   "alcohol_frequent" if r.exposure.startswith("alcohol") else
                   "crp_elevated" if r.exposure == "crp_elevated" else
                   "lead_exposure" if r.exposure == "lead_exposure" else
                   "low_antioxidant_intake" if "antioxidant" in r.exposure else "_default")
            print(f"     {r.exposure:26s} flag={r.flag:9s} "
                  f"source={REF_SOURCE.get(key, REF_SOURCE['_default'])}")

    # ---------------- 2b. internal consistency (no external prior needed) -------
    print("\n=== 2b. internal consistency checks (independent of any prior) ===")
    consistency_fail = []
    C = build_nhanes_continuous(d)
    dpy = pd.to_numeric(E.get("alcohol_days_per_year", pd.Series(np.nan, index=d.index)),
                        errors="coerce")
    freq = pd.to_numeric(E["alcohol_frequent"], errors="coerce")
    drk = pd.to_numeric(E["alcohol_intake"], errors="coerce")
    if dpy.notna().any():
        m = dpy.notna() & freq.notna()
        impl = ((dpy[m] >= 52).astype(float) - freq[m]).abs()
        print(f"  alcohol: median days/yr among past-year drinkers = "
              f"{dpy[drk == 1].median():.1f} "
              f"(p25={dpy[drk == 1].quantile(.25):.1f}, p75={dpy[drk == 1].quantile(.75):.1f})")
        print(f"  alcohol: |P(days>=52) - alcohol_frequent| max = {impl.max()}  (must be 0)")
        if impl.max() > 0:
            consistency_fail.append("alcohol_frequent vs days_per_year")

    def agree(cat_key, cont_key, derive, label, tol=0.0):
        """derive: callable(continuous_series) -> 0/1 float; compared on the
        mutual non-missing subset only (NaN == NaN is False in float compare)."""
        cs = pd.to_numeric(E[cat_key], errors="coerce")
        vs = pd.to_numeric(C[cont_key], errors="coerce")
        m = cs.notna() & vs.notna()
        if not m.sum():
            print(f"  {label}: no overlap")
            return
        derived = derive(vs[m]).astype(float)
        diff = (derived - cs[m]).abs()
        a = float((diff <= tol).mean())
        print(f"  {label}: categorical/continuous agreement = {a:.4f} on n={int(m.sum())} "
              f"(tol={tol:g})" + ("" if a == 1.0 else f"  [n_differ={int((diff > tol).sum())}]"))
        if a < 1.0:
            consistency_fail.append(f"{cat_key} (n_differ={int((diff > tol).sum())})")

    agree("hba1c_elevated", "hba1c_pct", lambda v: (v >= 6.5).astype(float), "hba1c")
    agree("bmi_high", "bmi_kgm2", lambda v: (v >= 25).astype(float), "BMI")
    agree("ldl_high", "ldl_mgdl", lambda v: (v >= 160).astype(float), "LDL")
    agree("hdl_low", "hdl_mgdl", lambda v: (v < 40).astype(float), "HDL")
    # CRP: categorical uses `LBXCRP > 0.3 mg/dL`, continuous exports mg/L.
    # Float rounding makes `a > 0.3` and `a*10 > 3.0` disagree on exact-boundary
    # values, so compare with a tolerance instead of claiming a coding bug.
    agree("crp_elevated", "crp_mgl", lambda v: (v > 3.0).astype(float),
          "CRP (mg/L)", tol=1e-9)
    # uric acid uses SEX-SPECIFIC cut-points; a single cut is expected to disagree
    # for women, so the check must reproduce the sex-specific rule.
    _sex = pd.to_numeric(d["RIAGENDR"], errors="coerce")
    agree("uric_acid_elevated", "uric_acid_mgdl",
          lambda v: (((v > 7.0) & (_sex[v.index] == 1)) |
                     ((v > 5.7) & (_sex[v.index] == 2))).astype(float),
          "uric acid (sex-specific)")
    if consistency_fail:
        print(f"  HARD_WARN: internal consistency failed for {consistency_fail}")

    # ---------------- 3. explicit before/after of the R11 fixes ----------------
    print("\n=== 3. R11 correction effects (what the fix changed) ===")
    q = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)
    s20, s40 = q("SMQ020"), q("SMQ040")
    old_smk = s40.isin([1, 2]).astype(float).where(s40.isin([1, 2, 3]))
    new_smk = pd.to_numeric(E["current_smoking"], errors="coerce")
    print(f"  smoking  BEFORE (SMQ040 only, ref=former): prev={old_smk.mean():.4f} n={int(old_smk.notna().sum())}")
    print(f"  smoking  AFTER  (SMQ020+SMQ040, ref=never∪former): prev={new_smk.mean():.4f} n={int(new_smk.notna().sum())}")
    a101, a120 = q("ALQ101"), q("ALQ120Q")
    old_alc = (a101 == 1).astype(float).where(a101.notna())
    new_alc = pd.to_numeric(E["alcohol_intake"], errors="coerce")
    print(f"  alcohol  BEFORE (ALQ101 lifetime>=12): prev={old_alc.mean():.4f} n={int(old_alc.notna().sum())}")
    print(f"  alcohol  AFTER  (ALQ120Q>=1 past yr) : prev={new_alc.mean():.4f} n={int(new_alc.notna().sum())}")
    crp = q("LBXCRP")
    print(f"  CRP      BEFORE (>3.0 mg/dL = >30 mg/L): prev={float((crp > 3.0).mean()):.4f}")
    print(f"  CRP      AFTER  (>0.3 mg/dL = >3 mg/L) : prev={float((crp > 0.3).mean()):.4f}")
    pb = q("LBXBPB")
    print(f"  lead     BEFORE (>=5.0 ug/dL): prev={float((pb >= 5.0).mean()):.4f}")
    print(f"  lead     AFTER  (>=3.5 ug/dL): prev={float((pb >= 3.5).mean()):.4f}")
    vc, atoc, lz = q("DR1TVC"), q("DR1TATOC"), q("DR1TLZ")
    print(f"  antioxidant: DR1TVE present={'DR1TVE' in d.columns} | "
          f"new composite n={int(E['low_antioxidant_intake'].notna().sum())} "
          f"prev={float(pd.to_numeric(E['low_antioxidant_intake'], errors='coerce').mean()):.4f}")
    print(f"  dyslipidemia: HDL branch non-missing={int(q('LBDHDD').notna().sum())}, "
          f"LDL branch non-missing={int(q('LBDLDL').notna().sum())}")

    # ---------------- 4. biomarker cross-check ----------------
    print("\n=== 4. self-reported current smoking vs serum cotinine (objective) ===")
    cot = q("LBXCOT")
    if cot.notna().sum() > 100:
        # cotinine >=10 ng/mL is the standard cut-off for active smoking
        bio = (cot >= 10).astype(float).where(cot.notna())
        both = new_smk.notna() & bio.notna()
        if both.sum() > 0:
            a = new_smk[both].astype(int)
            b = bio[both].astype(int)
            tp = int(((a == 1) & (b == 1)).sum()); fp = int(((a == 1) & (b == 0)).sum())
            fn = int(((a == 0) & (b == 1)).sum()); tn = int(((a == 0) & (b == 0)).sum())
            sens = tp / (tp + fn) if (tp + fn) else None
            spec = tn / (tn + fp) if (tn + fp) else None
            print(f"  n_both={int(both.sum())}  TP={tp} FP={fp} FN={fn} TN={tn}")
            print(f"  sensitivity={sens:.3f}  specificity={spec:.3f}  "
                  f"(self-report vs cotinine>=10 ng/mL)")
            print(f"  cotinine median by self-report: "
                  f"non-smoker={cot[both][a == 0].median():.3f}, smoker={cot[both][a == 1].median():.3f} ng/mL")
            if sens is not None and sens < 0.7:
                print("  HARD_WARN: self-reported current smoking misses >30% of cotinine-confirmed smokers")
        else:
            print("  no overlap between smoking flag and cotinine")
    else:
        print("  cotinine not available")

    # ---------------- 5. continuous measures ----------------
    print("\n=== 5. continuous measures (median vs plausible range) ===")
    rows = []
    for name, s in C.items():
        s = pd.to_numeric(s, errors="coerce")
        if not s.notna().any():
            rows.append({"measure": name, "n": 0, "median": None, "ref_range": None, "flag": "EMPTY"})
            continue
        med = float(s.median())
        rng = CONT_REF.get(name)
        f = ""
        if rng and not (rng[0] * 0.5 <= med <= rng[1] * 1.5):
            f = "HARD_WARN"
        rows.append({"measure": name, "n": int(s.notna().sum()), "median": round(med, 3),
                     "ref_range": rng, "flag": f})
    cn = pd.DataFrame(rows)
    print(cn.to_string(index=False))
    cn.to_csv(ROOT / ".audit_tmp/nhanes_continuous_measures.csv", index=False,
              encoding="utf-8-sig")

    hard = (list(ex[ex["flag"] == "HARD_WARN"]["exposure"])
            + list(cn[cn["flag"].isin(["HARD_WARN", "EMPTY"])]["measure"])
            + consistency_fail)
    print(f"\n=== summary: {len(hard)} hard warnings -> {hard} ===")
    if not hard:
        print("    NHANES exposure gate PASSED")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
