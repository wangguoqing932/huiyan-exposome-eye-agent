"""NHANES variable audit: verify every variable referenced by
scripts/evaluate.py actually exists in the module that evaluate.py loads,
and report prevalence of each derived exposure/outcome under the CURRENT code.

Output: .audit_tmp/nhanes_variable_audit.csv  (+ console table)
"""
from __future__ import annotations
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")

# exactly the FILES dict from scripts/evaluate.py
FILES = {"DEMO": ("DEMO", True), "BIOPRO": ("BIOPRO", True), "VIQ": ("VIQ", True),
         "VIX": ("VIX", True), "OPXRET": ("OPXRET", True), "SMQ": ("SMQ", True),
         "ALQ": ("ALQ", True), "BMX": ("BMX", True), "CRP": ("CRP", True),
         "PBCD": ("PBCD", True), "DR1TOT": ("DR1TOT", True),
         "GLU": ("GLU", True), "GHB": ("GHB", True),
         "DEQ": ("DEQ", "D"), "VITAEC": ("VITAEC", "D")}

# every variable name appearing in build_nhanes_exposures / build_nhanes_outcomes / covars
REF = {
    # exposures
    "LBXSUA": "uric_acid_elevated", "LBXGL": "hyperglycemia", "LBXSGL": "hyperglycemia",
    "DIQ010": "hyperglycemia(dx branch)", "LBXGH": "hba1c_elevated",
    "LBXSCH": "dyslipidemia", "LBXSTR": "dyslipidemia", "LBDHDD": "dyslipidemia",
    "LBDHDL": "dyslipidemia", "LBDLDL": "dyslipidemia",
    "LBXCRP": "crp_elevated", "BMXBMI": "bmi_high",
    "DR1TVC": "low_antioxidant_intake", "DR1TVE": "low_antioxidant_intake",
    "DR1TLZ": "low_antioxidant_intake",
    "SMQ040": "current_smoking", "SMQ020": "current_smoking(ref group)",
    "ALQ101": "alcohol_intake", "ALQ110": "alcohol_intake(alt)",
    "ALQ120Q": "current drinking", "ALQ120U": "current drinking unit",
    "ALQ130": "current drinking amount",
    "LBXBPB": "lead_exposure",
    # outcomes
    "VIQ071": "cataract_any", "VIDRVA": "vision_impairment", "VIDLVA": "vision_impairment",
    "OPDURL4": "retinopathy_any/dr", "OPDUARM": "amd_early", "OPDUPIGA": "amd_early",
    "OPDULARM": "amd_late", "OPDUGA": "amd_late", "OPDUEXU": "amd_late",
    "OPDDVCDR": "glaucoma_suspect_cdr", "OPDSVCDR": "glaucoma_suspect_cdr",
    # covariates
    "RIDAGEYR": "covariate", "RIAGENDR": "covariate", "RIDRETH1": "covariate",
    "INDFMPIR": "covariate", "DMDEDUC2": "covariate", "DMDEDUC3": "covariate",
    "WTMEC2YR": "weight", "SDMVSTRA": "design strata", "SDMVPSU": "design PSU",
    # vitD not used by evaluate.py but needed for rule r07
    "LBXVIDMS": "vitamin_d_deficiency (rule r07, NOT implemented)",
}

CYCLES = {"2005-2006": "_D", "2007-2008": "_E"}


def load_cycle(cycle_dir: Path, suf: str) -> tuple[pd.DataFrame, dict[str, list[str]], dict[str, str]]:
    frames, present = {}, {}
    for mod, (base, cyc) in FILES.items():
        if cyc is True:
            name = f"{base}{suf}.XPT"
        elif cyc == suf or (isinstance(cyc, str) and suf.endswith(cyc)):
            name = f"{base}{suf}.XPT"
        else:
            continue
        p = cycle_dir / name
        if not p.exists():
            present[mod] = ["<FILE MISSING: %s>" % name]
            continue
        df = pd.read_sas(str(p), format="xport", encoding="utf-8")
        present[mod] = list(df.columns)
        frames[mod] = df.set_index("SEQN") if "SEQN" in df.columns else df
    out = None
    for m, df in frames.items():
        if out is None:
            out = df
        else:
            ov = [c for c in df.columns if c in out.columns]
            out = out.join(df.drop(columns=ov), how="outer")
    return (out.reset_index() if out is not None else pd.DataFrame()), present, {}


def main():
    rows = []
    alldata = []
    cols_union = {}
    for cyc, suf in CYCLES.items():
        d, present, _ = load_cycle(NH / cyc, suf)
        d["cycle"] = cyc
        alldata.append(d)
        for mod, cols in present.items():
            cols_union[f"{cyc}:{mod}"] = cols

    # which module supplies each referenced variable, and is it loaded?
    print("=== variable provenance check (both cycles) ===")
    for v, role in REF.items():
        where = []
        for key, cols in cols_union.items():
            if v in cols:
                where.append(key.split(":")[1])
        loaded_mods = set(m for m in FILES)
        ok = bool(set(where) & loaded_mods)
        rows.append({"variable": v, "role": role,
                     "found_in_modules": "|".join(sorted(set(where))) or "NOT FOUND",
                     "loaded_by_evaluate": ok})
        flag = "OK " if ok else "!! NOT LOADED"
        print(f"  {flag} {v:10s} [{role}] -> {sorted(set(where)) or 'ABSENT FROM ALL MODULES'}")

    pd.DataFrame(rows).to_csv(ROOT / ".audit_tmp/nhanes_variable_audit.csv",
                              index=False, encoding="utf-8-sig")

    d = pd.concat(alldata, ignore_index=True, sort=False)
    d = d[pd.to_numeric(d["RIDAGEYR"], errors="coerce") >= 40]
    d = d[pd.to_numeric(d.get("WTMEC2YR", 0), errors="coerce") > 0]
    print(f"\nanalytic frame (age>=40, wt>0): n={len(d)}")

    q = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)
    sex = q("RIAGENDR")
    prev = {}

    def add(name, s, note=""):
        s = pd.to_numeric(s, errors="coerce")
        prev[name] = {"n_nonmiss": int(s.notna().sum()),
                      "prev": round(float(s.mean()), 4) if s.notna().any() else None,
                      "male": round(float(s[sex == 1].mean()), 4) if s.notna().any() else None,
                      "female": round(float(s[sex == 2].mean()), 4) if s.notna().any() else None,
                      "note": note}

    print("\n=== derived exposure prevalence under CURRENT code ===")
    ua = q("LBXSUA")
    add("uric_acid_elevated", (((ua >= 6.8) & (sex == 1)) | ((ua >= 5.7) & (sex == 2))).astype(float).where(ua.notna()))
    glu = q("LBXGL") if "LBXGL" in d else q("LBXSGL")
    diq = q("DIQ010")
    add("hyperglycemia", ((glu >= 126) | (diq == 1)).astype(float).where(glu.notna() | diq.notna()),
        "DIQ010 not loaded -> dx branch dead")
    add("hba1c_elevated", (q("LBXGH") >= 6.5).astype(float).where(q("LBXGH").notna()))
    tc, tg, hdl = q("LBXSCH"), q("LBXSTR"), q("LBDHDD")
    ldl = q("LBDLDL")
    lip = pd.concat([tc, tg, hdl, ldl], axis=1)
    add("dyslipidemia", ((tc >= 240) | (tg >= 200) | (hdl < 40) | (ldl >= 160)).astype(float).where(lip.notna().any(axis=1)))
    add("crp_elevated", (q("LBXCRP") > 3.0).astype(float).where(q("LBXCRP").notna()))
    add("bmi_high(>=25)", (q("BMXBMI") >= 25).astype(float).where(q("BMXBMI").notna()))
    vc, ve, lz = q("DR1TVC"), q("DR1TVE"), q("DR1TLZ")
    if vc.notna().sum() > 100:
        z = ((vc - vc.mean()) / vc.std() + (ve - ve.mean()) / ve.std() + (lz - lz.mean()) / lz.std()) / 3
        add("low_antioxidant_intake", (z <= z.quantile(0.25)).astype(float).where(z.notna()),
            "SAMPLE-QUANTILE cutoff, not pre-registered")
    smk = q("SMQ040")
    add("current_smoking (CURRENT CODE)", smk.isin([1, 2]).astype(float).where(smk.isin([1, 2, 3])),
        "ref group = FORMER smokers only")
    s20, s40 = q("SMQ020"), q("SMQ040")
    add("never_smoker", (s20 == 2).astype(float).where(s20.isin([1, 2])))
    add("former_smoker", ((s20 == 1) & (s40 == 3)).astype(float).where(s20.isin([1, 2])))
    add("current_smoking (FIXED, vs never+former)",
        ((s20 == 1) & s40.isin([1, 2])).astype(float).where(s20.isin([1, 2])))
    add("ever_smoking", (s20 == 1).astype(float).where(s20.isin([1, 2])))
    alq = q("ALQ101")
    add("alcohol_intake (CURRENT CODE=ALQ101)", (alq == 1).astype(float).where(alq.notna()),
        "= lifetime ever had >=12 drinks")
    add("current_drinker(ALQ120Q>0)", (q("ALQ120Q") > 0).astype(float).where(q("ALQ120Q").notna()),
        "ALQ120Q>=1 means >=1 day in past 12 mo")
    add("frequent_drinker(ALQ120Q>=52)", (q("ALQ120Q") >= 52).astype(float).where(q("ALQ120Q").notna()))
    add("lead_exposure(>=5ug/dL)", (q("LBXBPB") >= 5.0).astype(float).where(q("LBXBPB").notna()))
    add("lead_exposure(>=3.5ug/dL)", (q("LBXBPB") >= 3.5).astype(float).where(q("LBXBPB").notna()))

    for k, v in prev.items():
        print(f"  {k:44s} n={v['n_nonmiss']:5d} prev={v['prev']} (M {v['male']} / F {v['female']}) {v['note']}")

    print("\n=== derived outcome prevalence under CURRENT code ===")
    o_prev = {}
    o_prev["cataract_any"] = (q("VIQ071") == 1).astype(float).where(q("VIQ071").notna())
    va_r = q("VIDRVA").where(q("VIDRVA").between(20, 666))
    va_l = q("VIDLVA").where(q("VIDLVA").between(20, 666))
    va = np.log10(pd.concat([va_r, va_l], axis=1) / 20.0).max(axis=1)
    o_prev["VI_mild"] = ((va > 0.30) & ~(va > 0.48)).astype(float).where(va.notna())
    o_prev["VI_moderate"] = ((va > 0.48) & ~(va > 1.00)).astype(float).where(va.notna())
    o_prev["VI_severe"] = (va > 1.00).astype(float).where(va.notna())
    ret = q("OPDURL4")
    o_prev["retinopathy_any"] = ret.isin([2, 3, 4]).astype(float).where(ret.notna())
    o_prev["dr_npdr"] = ret.isin([2, 3]).astype(float).where(ret.notna())
    o_prev["dr_pdr"] = (ret == 4).astype(float).where(ret.notna())
    arm, pig = q("OPDUARM"), q("OPDUPIGA")
    o_prev["amd_early"] = ((arm >= 1) | (pig >= 1)).astype(float).where(arm.notna() | pig.notna())
    larm, ga, exu = q("OPDULARM"), q("OPDUGA"), q("OPDUEXU")
    o_prev["amd_late"] = ((larm >= 1) | (ga >= 1) | (exu >= 1)).astype(float).where(larm.notna() | ga.notna() | exu.notna())
    cdr = pd.concat([q("OPDDVCDR"), q("OPDSVCDR")], axis=1).max(axis=1)
    o_prev["glaucoma_suspect_cdr"] = (cdr >= 0.70).astype(float).where(cdr.notna())
    for k, s in o_prev.items():
        s = pd.to_numeric(s, errors="coerce")
        print(f"  {k:24s} n_nonmiss={int(s.notna().sum()):5d} prev={float(s.mean()):.4f}")

    # raw value sanity for the ones the code reinterprets
    print("\n=== raw value ranges for reinterpreted variables ===")
    for c in ["OPDURL4", "OPDUARM", "OPDUPIGA", "OPDULARM", "OPDUGA", "OPDUEXU",
              "OPDDVCDR", "OPDSVCDR", "VIDRVA", "VIDLVA", "VIQ071", "LBXBPB"]:
        if c in d.columns:
            s = pd.to_numeric(d[c], errors="coerce")
            print(f"  {c:10s} n={s.notna().sum():5d} min={s.min():.3g} med={s.median():.3g} "
                  f"max={s.max():.3g}  uniq={s.nunique()}")

    pd.DataFrame(o_prev).describe()
    pd.DataFrame([{"name": k, **v} for k, v in prev.items()]).to_csv(
        ROOT / ".audit_tmp/nhanes_exposure_prevalence.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    sys.exit(main())
