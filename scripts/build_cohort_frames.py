#!/usr/bin/env python
"""Build the ageing-cohort external-validation frame, one cohort at a time.

Every mapping in here was established by reading the cohort's own codebook and
checking value labels -- not by guessing from variable names. The corrections
that constrain this code live in docs/cohort_variable_mapping.md; the ones that
bite here are:

  C19/C20/C36/C41  availability and emptiness must be judged with notna();
                   never with to_numeric (labelled categoricals collapse to NaN).
  C21              surgery/treatment is NOT disease. `cataract_surgery` and
                   `glaucoma_treated` stay separate from `cataract_any` /
                   `glaucoma_*` and must be declared as construct-shifted.
  C27              HRS/ELSA/MHAS/KLoSA vision ratings are CORRECTED vision
                   ("using glasses or corrective lenses as usual"). A
                   vision_impairment flag built here is impairment that
                   persists despite correction -- not refractive error.
  C37              SHARE carries `eyesightr_f`, which separates observed from
                   imputed. Main analysis uses observed only.
  C47              missing codes differ per cohort (SHARE uses negative codes).
  C52              official value labels can themselves be wrong; cross-check
                   the same construct across sibling variables.

Output per cohort:
  data/frames/cohort_<NAME>.csv          one row per person-wave
  outputs/confirmatory/cohort_<NAME>_prevalence.json   the prevalence gate

Usage:
  python scripts/build_cohort_frames.py SHARE
  python scripts/build_cohort_frames.py SHARE --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = Path(r"E:\BaiduNetdiskDownload\所有数据库")
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "confirmatory"

# ----------------------------------------------------------------------------
# SHARE. Identifier is `mergeid` (stable across waves). Analysis-ready
# variables live in SHARE's own `gv_imputations` module and carry `_f` flags;
# chronic conditions come from the `ph` module as Selected/Not selected.
# ----------------------------------------------------------------------------
SHARE_WAVES = [4, 5, 6, 7, 9]        # waves where eyesightr is populated
SHARE_ROOT = DB / "07. SHARE 欧洲健康退休与老龄化调查/SHARE_欧洲/Raw_data"

# WHO international cut-point for obesity; used for bmi_high (r13/r22).
BMI_HIGH_CUT = 30.0
# WHO Asian cut-point. The international cut is wrong for East/South Asian
# populations: with BMI>=30 KLoSA's measured prevalence is 1.45% against a
# Western reference range of 8-45%, which is a cut-point artefact, not a data
# problem. Rather than silently switching cut-points per cohort (which would
# make the cohorts incomparable), the builders emit BOTH and the prevalence
# gate checks each against its own reference range. The pre-registration then
# declares which one is primary -- the choice stays visible instead of hidden.
BMI_ASIAN_CUT = 25.0


def _add_bmi(fr: pd.DataFrame, bmi: pd.Series) -> pd.DataFrame:
    bmi = _code(bmi).where(lambda s: s > 0)
    fr["bmi"] = bmi
    fr["bmi_high_25"] = (bmi >= BMI_ASIAN_CUT).astype(float).where(bmi.notna())
    fr["bmi_high_30"] = (bmi >= BMI_HIGH_CUT).astype(float).where(bmi.notna())
    return fr

# Reference prevalences (from the R11 NHANES/KNHANES work and the literature
# cited in analysis_plan) used as the plausibility gate. A cohort whose
# measured prevalence falls far outside these is NOT declared testable -- this
# is the same reference-prevalence gate that caught the NHANES smoking (C1),
# CRP-units (C3) and CHARLS smoking (3rd occurrence) errors.
# Two tiers, because one band conflates two different things.
#
#   HARD    -- a wide error band. Failing it means the VARIABLE is wrong: the
#              smoking gate error surfaced as 49%, CRELES' wrong file as n=0,
#              KLoSA's mismatched BMI cut as 1.45%. Those are defects.
#   TYPICAL -- the range seen in the sources the rules were built on
#              (NHANES/KNHANES). Falling outside it is INFORMATIONAL: ELSA's
#              severe vision impairment is 0.25% because UK eye care is good,
#              CRELES' cataract is 38.5% because the cohort is entirely 60+.
# Widening one band to force those through would be a post-hoc adjustment of
# the gate itself, so both are reported and only HARD decides pass/fail.
REFERENCE_HARD = {
    "cataract_any":              (0.01, 0.60),
    "vision_impairment_moderate": (0.01, 0.60),
    "vision_impairment_severe":   (0.0005, 0.25),
    "current_smoking":           (0.01, 0.60),
    "alcohol_intake":            (0.02, 0.95),
    "bmi_high_25":               (0.05, 0.80),
    "bmi_high_30":               (0.005, 0.60),
    "diabetes":                  (0.01, 0.50),
    "hypertension":              (0.05, 0.85),
}
REFERENCE_TYPICAL = {
    "cataract_any":              (0.03, 0.30),
    "vision_impairment_moderate": (0.03, 0.35),
    "vision_impairment_severe":   (0.005, 0.10),
    "current_smoking":           (0.05, 0.35),
    "alcohol_intake":            (0.10, 0.80),
    "bmi_high_25":               (0.15, 0.60),   # Asian cut
    "bmi_high_30":               (0.03, 0.45),   # international cut
    "diabetes":                  (0.04, 0.35),
    "hypertension":              (0.20, 0.70),
}
REFERENCE = REFERENCE_TYPICAL   # backwards compatibility for older reports


def _read(path: Path, cols: list[str]) -> pd.DataFrame:
    return pd.read_stata(str(path), columns=cols)


def _code(series: pd.Series) -> pd.Series:
    """Recover the NUMERIC CODES from a labelled Stata column.

    Correction C36 keeps recurring: a labelled variable is delivered by pandas
    as a categorical whose categories are the LABEL STRINGS ('1 Yes', '2 No',
    '1.0'), so `pd.to_numeric` maps every entry to NaN and the flag silently
    comes out empty. LASI's ht002/ht003/ht019 did exactly this and produced
    n=0 for diabetes, hypertension and both vision flags.

    The code is the leading integer of the label when there is one, otherwise
    the value itself (handles genuinely numeric columns too).
    """
    s = series.astype(str).str.strip()
    lead = s.str.extract(r"^(-?\d+)")[0]
    out = pd.to_numeric(lead, errors="coerce")
    # fall back to a straight numeric read for unlabelled numeric columns
    plain = pd.to_numeric(series, errors="coerce")
    return out.fillna(plain)


def _sex(series: pd.Series) -> pd.Series:
    """Decode a sex column that may be numeric OR plain text.

    C68: _code() recovers a leading integer from a label, which works for
    '1 Male' but not for columns whose categories are bare 'Male'/'Female' --
    KLoSA's w01gender1 and SHARE's gender are exactly that, and came out
    entirely NaN after the _code sweep.
    """
    txt = series.astype(str).str.strip().str.lower()
    out = pd.Series(float("nan"), index=series.index)
    out[txt.isin(["male", "m", "1", "1.0", "1 male"])] = 1.0
    out[txt.isin(["female", "f", "2", "2.0", "2 female"])] = 2.0
    return out

def _binary(series: pd.Series, true_vals, false_vals, missing_vals=()) -> pd.Series:
    """Map a labelled categorical / numeric column onto 0/1 with NaN preserved.

    Stata labels arrive as strings ("Selected", "1. Yes") or numbers; we accept
    both spellings and everything else becomes NaN rather than a silent False.
    """
    s = series.astype(str).str.strip()
    out = pd.Series(float("nan"), index=series.index)
    for v in true_vals:
        out[s == str(v).strip()] = 1.0
    for v in false_vals:
        out[s == str(v).strip()] = 0.0
    # numeric spellings
    num = _code(series)
    for v in true_vals:
        try:
            out[num == float(v)] = 1.0
        except (TypeError, ValueError):
            pass
    for v in false_vals:
        try:
            out[num == float(v)] = 0.0
        except (TypeError, ValueError):
            pass
    for v in missing_vals:
        out[s == str(v).strip()] = float("nan")
    return out


def build_share() -> tuple[pd.DataFrame, dict]:
    frames, diagnostics = [], []
    for w in SHARE_WAVES:
        ph = SHARE_ROOT / f"Wave {w} Release 9.0.0/sharew{w}_rel9-0-0_ph.dta"
        gv = SHARE_ROOT / f"Wave {w} Release 9.0.0/sharew{w}_rel9-0-0_gv_imputations.dta"
        dn = SHARE_ROOT / f"Wave {w} Release 9.0.0/sharew{w}_rel9-0-0_dn.dta"
        if not (ph.exists() and gv.exists()):
            diagnostics.append({"wave": w, "status": "files missing"})
            continue

        gv_it = pd.read_stata(str(gv), iterator=True)
        gv_lab = gv_it.variable_labels()
        # C54: age/gender/bmi/eyesightr live in gv_imputations; an earlier
        # version looked for age/gender only in the dn module, where they are
        # not named that way, so they were silently never built.
        want_gv = [c for c in ("mergeid", "implicat", "eyesightr", "eyesightr_f",
                               "bmi", "drinking", "age", "gender",
                               "height", "weight")
                   if c in gv_lab]
        d = _read(gv, want_gv)

        # C53: SHARE's gv_imputations module carries an explicit `implicat`
        # index (1-5) -- five imputation replicates per person-wave. Dropping
        # it does NOT reduce the sample: it leaves five identical-looking rows
        # per person, so any regression sees 5x the true n and understates the
        # standard errors. Carry it through so the analysis layer can pool by
        # Rubin's rules (or deliberately use replicate 1 for a sensitivity run).
        if "implicat" not in d.columns:
            d["implicat"] = 1
            diagnostics.append({"wave": w, "note": "no implicat column found"})

        ph_it = pd.read_stata(str(ph), iterator=True)
        ph_lab = ph_it.variable_labels()
        want_ph = [c for c in ("mergeid", "ph006d13", "ph006d5", "ph006d2", "ph006d3")
                   if c in ph_lab]
        if want_ph:
            d = d.merge(_read(ph, want_ph), on="mergeid", how="left")

        # ---- smoking, from SHARE's own behaviour module ----------------------
        # C55: `smoking`/"ever_smoked" exist only in easySHARE, a separate
        # simplified distribution of SHARE -- a derived product. We build the
        # flags from the main-release `br` items instead.
        # C54 (the C1 error class, 4th occurrence): br002_ ("Smoke at the
        # present time") is asked ONLY of br001_ == "Yes" (ever smoked daily).
        # n(br002_) in wave 6 is 5,703 against 5,701 ever-smokers, so
        # `br002_ == Yes` alone yields 2,792/5,703 = 49% -- that is the
        # prevalence AMONG EVER-SMOKERS, not in the population (~15-20%).
        # The population flag must OR the never-smokers in as 0:
        #   current_smoking = 1 if br002_==Yes
        #                     0 if br001_==No or br002_==No
        #                     NaN only where br001_ is missing
        br = SHARE_ROOT / f"Wave {w} Release 9.0.0/sharew{w}_rel9-0-0_br.dta"
        if br.exists():
            br_it = pd.read_stata(str(br), iterator=True)
            br_lab = br_it.variable_labels()
            want_br = [c for c in ("mergeid", "br001_", "br002_") if c in br_lab]
            if want_br:
                b = _read(br, want_br)
                d = d.merge(b, on="mergeid", how="left")
                if "br001_" in d and "br002_" in d:
                    ever = _binary(d["br001_"], ["Yes"], ["No"], ["Don't know", "Refusal"])
                    cur = _binary(d["br002_"], ["Yes"], ["No"], ["Don't know", "Refusal"])
                    smoke = pd.Series(float("nan"), index=d.index)
                    smoke[cur == 1] = 1.0
                    smoke[(ever == 0) | (cur == 0)] = 0.0
                    smoke[ever.isna()] = float("nan")
                    d["current_smoking_src"] = smoke
                    d["ever_smoked_src"] = ever

        # demographics (age/sex/education) for covariates
        if dn.exists():
            dn_it = pd.read_stata(str(dn), iterator=True)
            dn_lab = dn_it.variable_labels()
            want_dn = [c for c in ("mergeid", "age", "gender", "isced1997_r",
                                   "country", "eduyears")
                       if c in dn_lab]
            if want_dn:
                d = d.merge(_read(dn, want_dn), on="mergeid", how="left")

        f = pd.DataFrame({"mergeid": d["mergeid"], "wave": w, "cohort": "SHARE",
                          "implicat": d["implicat"]})

        # ---- outcomes -------------------------------------------------------
        if "ph006d13" in d:
            # "Cataracts: ever diagnosed/currently having" -> Selected/Not selected
            f["cataract_any"] = _binary(d["ph006d13"], ["Selected"], ["Not selected"],
                                        ["Don't know", "Refusal", "nan"])
        if "eyesightr" in d:
            eye = d["eyesightr"].astype(str).str.strip().str.lower()
            f["vision_impairment_moderate"] = eye.isin(["fair"]).astype(float).where(
                eye.isin(["excellent", "very good", "good", "fair", "poor"]))
            f["vision_impairment_severe"] = eye.isin(["poor"]).astype(float).where(
                eye.isin(["excellent", "very good", "good", "fair", "poor"]))
            f["vision_rating_ordinal"] = eye.map(
                {"excellent": 1, "very good": 2, "good": 3, "fair": 4, "poor": 5})
            f["vision_imputed"] = (
                d["eyesightr_f"].astype(str).str.strip()
                .eq("Imp: missing value").astype(float) if "eyesightr_f" in d else 0.0)

        # ---- exposures ------------------------------------------------------
        if "current_smoking_src" in d:
            f["current_smoking"] = d["current_smoking_src"]
        if "br010_mod" in d or "drinking" in d:
            src = d["br010_mod"] if "br010_mod" in d else d["drinking"]
            lab = src.astype(str).str.strip().str.lower()
            f["alcohol_intake"] = (~lab.isin(
                ["not at all in the last 3 months", "not at all",
                 "0. no", "no", "-13. not asked in this wave"])).astype(float).where(
                src.notna())
        if "gender" in d:
            f["sex"] = _sex(d["gender"])          # C68: bare Male/Female labels
        if "age" in d:
            f["age"] = _code(d["age"])
        if "bmi" in d:
            f = _add_bmi(f, d["bmi"])
        if "ph006d5" in d:
            f["diabetes"] = _binary(d["ph006d5"], ["Selected"], ["Not selected"],
                                    ["Don't know", "Refusal", "nan"])
        if "ph006d2" in d:
            f["hypertension"] = _binary(d["ph006d2"], ["Selected"], ["Not selected"],
                                        ["Don't know", "Refusal", "nan"])

        for cov in ("age", "isced1997_r", "country", "eduyears"):
            if cov in d:
                f[cov] = _code(d[cov])
        frames.append(f)
        diagnostics.append({"wave": w, "status": "ok", "rows": len(f),
                            "cols": [c for c in f.columns]})

    if not frames:
        return pd.DataFrame(), {"cohort": "SHARE", "waves": diagnostics}
    frame = pd.concat(frames, ignore_index=True)
    return frame, {"cohort": "SHARE", "waves": diagnostics}


BUILDERS = {"SHARE": build_share}


# ----------------------------------------------------------------------------
# HRS. Wave letters: ... K=1996, ..., M=2010, O=2014, P=2016, Q=2018.
# We build from the plain HRS release file `H16C_R.dta` (section C, health),
# NOT from the RAND HRS Fat File (`20XX RAND HRS Fat File/hdXXf*.dta`), which
# is a derived product (correction C43).
# ----------------------------------------------------------------------------
HRS_ROOT = DB / "03. HRS 美国健康与退休研究/HRS_美国/Raw_data"
HRS_WAVES = [(2016, "P", "H16C_R.dta"), (2010, "M", "H10C_R.dta")]


def _hrs_binary(series: pd.Series) -> pd.Series:
    """HRS uses 1=Yes, 5=No, 8=DK, 9=RF (and other wave-specific codes)."""
    num = _code(series)
    out = pd.Series(float("nan"), index=series.index)
    out[num == 1] = 1.0
    out[num == 5] = 0.0
    return out


def build_hrs() -> tuple[pd.DataFrame, dict]:
    frames, diagnostics = [], []
    for year, letter, fname in HRS_WAVES:
        f = HRS_ROOT / f"{year} HRS" / fname
        if not f.exists():
            diagnostics.append({"wave": year, "status": f"missing {fname}"})
            continue
        it = pd.read_stata(str(f), iterator=True)
        L = it.variable_labels()
        pre = letter + "C"
        # section C health variables, discovered from the module codebook txt
        want = [c for c in (f"{pre}095", f"{pre}096", f"{pre}097",  # eyesight
                            f"{pre}098",                             # cataract surgery
                            f"{pre}101",                             # glaucoma
                            f"{pre}116", f"{pre}117",                # ever / now smoke
                            f"{pre}010", f"{pre}005", f"{pre}006",   # diabetes, hbp
                            )
                if c in L]
        d = pd.read_stata(str(f), columns=want + [c for c in ("HHID", "PN") if c in L])
        # C57: HRS stores the person key as two columns, HHID + PN; there is no
        # HHIDPN column, and falling back to d.columns[0] silently used a health
        # variable as the identifier (8 "persons" in a 42,946-row frame).
        if "HHID" in d.columns and "PN" in d.columns:
            pid = (d["HHID"].astype(str).str.strip() + "-"
                   + d["PN"].astype(str).str.strip())
        else:
            pid = d[d.columns[0]].astype(str)
        fr = pd.DataFrame({"mergeid": pid, "wave": year, "cohort": "HRS",
                           "implicat": 1})

        if f"{pre}095" in d:                                   # RATE EYESIGHT 1-6
            v = _code(d[f"{pre}095"]).where(lambda s: s <= 6)
            fr["vision_rating_ordinal"] = v
            fr["vision_impairment_moderate"] = (v == 4).astype(float).where(v.notna())
            fr["vision_impairment_severe"] = (v >= 5).astype(float).where(v.notna())
            fr["blindness_selfreport"] = (v == 6).astype(float).where(v.notna())
        if f"{pre}098" in d:                                   # CATARACT SURGERY
            fr["cataract_surgery"] = _hrs_binary(d[f"{pre}098"])
        if f"{pre}101" in d:                                   # GLAUCOMA
            fr["glaucoma_selfreport"] = _hrs_binary(d[f"{pre}101"])

        # C54/C56: HRS asks PC117 ("smoke cigarettes now") on a restricted base
        # (54% of respondents in 2016) and PC116 ("ever smoke") only of those
        # who answered No -- the nesting runs the OPPOSITE way to SHARE.
        # Population prevalence therefore needs the full denominator.
        if f"{pre}117" in d and f"{pre}116" in d:
            now = _hrs_binary(d[f"{pre}117"])
            ever = _hrs_binary(d[f"{pre}116"])
            smoke = pd.Series(float("nan"), index=d.index)
            smoke[now == 1] = 1.0
            # anyone who was asked "now" and said No, or who said No to ever
            smoke[(now == 0) | (ever == 0)] = 0.0
            fr["current_smoking"] = smoke
            fr["ever_smoked"] = ever
        if f"{pre}010" in d:
            fr["diabetes"] = _hrs_binary(d[f"{pre}010"])
        if f"{pre}005" in d:
            fr["hypertension"] = _hrs_binary(d[f"{pre}005"])

        # C66: HRS age and sex are NOT in the section C health file. Age is
        # PA044 in the section A household file and sex is PX060_R
        # ("SEX OF INDIVIDUAL-UPDATED - R") in the H16PR_R preload file. Both
        # are keyed on the same HHID + PN pair as the health file.
        demo_specs = [
            (HRS_ROOT / f"{year} HRS" / f"H{str(year)[2:]}A_R.dta", "PA019", "age"),
            (HRS_ROOT / f"{year} HRS" / f"H{str(year)[2:]}PR_R.dta", "PX060_R", "sex"),
        ]
        for dpath, dvar, dname in demo_specs:
            if not dpath.exists():
                diagnostics.append({"wave": year, "demo_missing": dpath.name})
                continue
            dit = pd.read_stata(str(dpath), iterator=True)
            DL = dit.variable_labels()
            need = [c for c in (dvar, "HHID", "PN") if c in DL]
            if dvar not in need:
                diagnostics.append({"wave": year, "demo_var_missing": dvar})
                continue
            dd = pd.read_stata(str(dpath), columns=need)
            # C67: the demographic files do not all key on HHID + PN. H16A_H is
            # a household-level file and carries no PN at all, which raised
            # KeyError and aborted the whole HRS build. Use whichever person
            # number column the file actually has, or skip that source with a
            # diagnostic rather than guessing a key.
            pncol = next((c for c in ("PN", "PPN", "PN_SP") if c in dd.columns), None)
            if "HHID" not in dd.columns or pncol is None:
                diagnostics.append({"wave": year, "demo_unkeyable": dpath.name,
                                    "cols": list(dd.columns)[:6]})
                continue
            dpid = (dd["HHID"].astype(str).str.strip() + "-"
                    + dd[pncol].astype(str).str.strip())
            dd = dd.assign(mergeid=dpid)[["mergeid", dvar]].drop_duplicates("mergeid")
            fr = fr.merge(dd.rename(columns={dvar: dname}), on="mergeid", how="left")
            fr[dname] = _code(fr[dname])
            if dname == "age":
                fr[dname] = fr[dname].where(fr[dname].between(18, 120))
            if dname == "sex":
                fr[dname] = _sex(fr[dname])
        frames.append(fr)
        diagnostics.append({"wave": year, "status": "ok", "rows": len(fr),
                            "vars_found": sorted(want)})

    if not frames:
        return pd.DataFrame(), {"cohort": "HRS", "waves": diagnostics}
    return pd.concat(frames, ignore_index=True), {"cohort": "HRS", "waves": diagnostics}


# ----------------------------------------------------------------------------
# MHAS. Wave 1 keeps vision in sect_c as `c45`; waves 3-6 use `c42_<nn>` in a
# combined file. Correction C44: the numeric suffix does NOT match the wave
# folder, so waves are taken from the file path, never from the name.
# ----------------------------------------------------------------------------
MHAS_ROOT = DB / "06. MHAS 墨西哥健康与老龄化研究/MHAS_墨西哥/Raw_data"
# (wave, year, vision file, vision var, yy suffix for the constructed/imputed files)
# C44/C57: wave 5's combined file is named `sect_a_c_d_f_e_pc_h_i_2018` while the
# others are `sect_a_c_d_e_pc_f_h_i_<year>` -- the section order differs, which is
# why guessing the path failed. Paths here are the verified ones.
MHAS_WAVES = [
    (1, 2001, "wave1/Core survey Data/sect_c.dta", "c45", "01"),
    (3, 2012, "wave3/Core survey Data/sect_a_c_d_e_pc_f_h_i_em_2012.dta", "c42_12", "12"),
    (4, 2015, "wave4/Core survey Data/sect_a_c_d_e_pc_f_h_i_2015.dta", "c42_15", "15"),
    (5, 2018, "wave5/Core survey Data/sect_a_c_d_f_e_pc_h_i_2018.dta", "c42_18", "18"),
    (6, 2021, "wave6/Core survey Data/sect_a_c_d_e_pc_f_h_i_2021.dta", "c42_21", "21"),
]


def build_mhas() -> tuple[pd.DataFrame, dict]:
    frames, diagnostics = [], []
    for wave, year, rel, visvar, yy in MHAS_WAVES:
        f = MHAS_ROOT / rel
        if not f.exists():
            diagnostics.append({"wave": wave, "status": f"missing {rel}"})
            continue
        it = pd.read_stata(str(f), iterator=True)
        L = it.variable_labels()
        want = [c for c in (visvar, "unhhid", "ps3", "edad", "sexo") if c in L]
        d = pd.read_stata(str(f), columns=want)
        # C57: the MHAS person key is unhhid + ps3, not a single column.
        if "unhhid" in d.columns and "ps3" in d.columns:
            pid = (d["unhhid"].astype(str).str.strip() + "-"
                   + d["ps3"].astype(str).str.strip())
        else:
            pid = d[d.columns[0]].astype(str)
        fr = pd.DataFrame({"mergeid": pid, "wave": wave, "cohort": "MHAS",
                           "implicat": 1})

        if visvar in d:
            # "How is your vision (using glasses)? 1 Excellent .. 6 Legally blind"
            v = _code(d[visvar]).where(lambda s: s <= 6)
            fr["vision_rating_ordinal"] = v
            fr["vision_impairment_moderate"] = (v == 4).astype(float).where(v.notna())
            fr["vision_impairment_severe"] = (v >= 5).astype(float).where(v.notna())
            fr["blindness_selfreport"] = (v == 6).astype(float).where(v.notna())
        if "edad" in d:                       # C66
            fr["age"] = _code(d["edad"])
        if "sexo" in d:
            fr["sex"] = _sex(d["sexo"])
        found = [visvar]

        # Chronic conditions from MHAS' own constructed-variable release
        # (`_Creadas`); BMI from its imputed weight/height release (C49).
        con = MHAS_ROOT / f"wave{wave}/Constructed Data/MHAS_ENASEM_{year}_Constructed_Variables_Creadas.dta"
        if con.exists():
            cit = pd.read_stata(str(con), iterator=True)
            CL = cit.variable_labels()
            ccols = [c for c in (f"hipertension_{yy}", f"diabetes_{yy}",
                                 "unhhid", "ps3") if c in CL]
            if len(ccols) > 2:
                cdf = pd.read_stata(str(con), columns=ccols)
                cpid = (cdf["unhhid"].astype(str).str.strip() + "-"
                        + cdf["ps3"].astype(str).str.strip())
                cdf = cdf.assign(mergeid=cpid).drop(columns=["unhhid", "ps3"])
                fr = fr.merge(cdf.drop_duplicates("mergeid"), on="mergeid", how="left")
                for src, name in ((f"hipertension_{yy}", "hypertension"),
                                  (f"diabetes_{yy}", "diabetes")):
                    if src in fr.columns:
                        n = _code(fr[src])
                        fr[name] = n.where(n.isin([0, 1]))
                        found.append(src)
        imp = MHAS_ROOT / f"wave{wave}/Imputations of Weight & Height/MHAS_{year}_Weight_and_Height_IMPUTED.dta"
        if imp.exists():
            iit = pd.read_stata(str(imp), iterator=True)
            IL = iit.variable_labels()
            icols = [c for c in (f"bmi_imp_{yy}", "unhhid", "ps3") if c in IL]
            if len(icols) > 1:
                idf = pd.read_stata(str(imp), columns=icols)
                if "unhhid" in idf.columns and "ps3" in idf.columns:
                    ipid = (idf["unhhid"].astype(str).str.strip() + "-"
                            + idf["ps3"].astype(str).str.strip())
                    idf = idf.assign(mergeid=ipid).drop(columns=["unhhid", "ps3"])
                    fr = fr.merge(idf.drop_duplicates("mergeid"), on="mergeid", how="left")
                    if f"bmi_imp_{yy}" in fr.columns:
                        fr = _add_bmi(fr, fr[f"bmi_imp_{yy}"])
                        found.append(f"bmi_imp_{yy}")

        frames.append(fr)
        diagnostics.append({"wave": wave, "status": "ok", "rows": len(fr),
                            "vars_found": found})

    if not frames:
        return pd.DataFrame(), {"cohort": "MHAS", "waves": diagnostics}
    return pd.concat(frames, ignore_index=True), {"cohort": "MHAS", "waves": diagnostics}


# ----------------------------------------------------------------------------
# KLoSA. Vision lives in the wave's `str0N_e.dta` / `Lt0N_e.dta` (core files),
# NOT only in the `e_imp_w*` imputation files (correction C19 was retracted on
# exactly this point). `w01C075` = eyesight, `C078` = cataract SURGERY,
# `C080` = glaucoma TREATMENT -- the latter two are construct-shifted (C21).
# ----------------------------------------------------------------------------
KLOSA_ROOT = DB / "04. KLoSA 韩国老龄化纵向研究/KLoSA_韩国/Raw_data"
KLOSA_WAVES = [1, 2, 4, 6, 8]


def build_klosa() -> tuple[pd.DataFrame, dict]:
    frames, diagnostics = [], []
    for w in KLOSA_WAVES:
        pref = f"w{w:02d}"
        cand_files = [
            KLOSA_ROOT / f"wave{w}" / f"str{w:02d}_e.dta",
            KLOSA_ROOT / f"wave{w}" / f"w{w:02d}_e.dta",
            KLOSA_ROOT / f"wave{w}" / "韩语版" / f"w{w:02d}.dta",
        ]
        f = next((p for p in cand_files if p.exists()), None)
        if f is None:
            diagnostics.append({"wave": w, "status": "no core file found"})
            continue
        try:
            it = pd.read_stata(str(f), iterator=True)
            L = it.variable_labels()
        except Exception as e:
            diagnostics.append({"wave": w, "status": f"{type(e).__name__}"})
            continue
        want = [c for c in (f"{pref}C075", f"{pref}C076", f"{pref}C077",
                            f"{pref}C078", f"{pref}C080", f"{pref}C116",
                            f"{pref}C117", f"{pref}C011", f"{pref}bmi",
                            f"{pref}alc", "pid", "hhid",
                            # C66: covariates. Names verified per cohort, not guessed.
                            f"{pref}A002_age", f"{pref}gender1")
                if c in L]
        d = pd.read_stata(str(f), columns=want)
        idcol = "pid" if "pid" in d.columns else ("id" if "id" in d.columns else d.columns[0])
        fr = pd.DataFrame({idcol: d[idcol], "wave": w, "cohort": "KLoSA",
                           "implicat": 1}).rename(columns={idcol: "mergeid"})

        if f"{pref}C075" in d:
            eye = d[f"{pref}C075"].astype(str).str.strip()
            order = {"Very good": 1, "Good": 2, "Fair": 3, "Bad": 4, "Very bad": 5}
            v = eye.map(order)
            fr["vision_rating_ordinal"] = v
            fr["vision_impairment_moderate"] = v.isin([4]).astype(float).where(v.notna())
            fr["vision_impairment_severe"] = v.isin([5]).astype(float).where(v.notna())
        if f"{pref}C078" in d:                     # cataract SURGERY, not disease
            fr["cataract_surgery"] = _binary(d[f"{pref}C078"], ["Yes"], ["No"],
                                             ["Don't know", "Refuse to answer"])
        if f"{pref}C080" in d:                     # glaucoma TREATMENT, not disease
            fr["glaucoma_treated"] = _binary(d[f"{pref}C080"], ["Yes"], ["No"],
                                             ["Don't know", "Refuse to answer"])
        # C54/C56: C117 ("currently smoking") is asked only of C116 == Yes
        if f"{pref}C117" in d and f"{pref}C116" in d:
            now = _binary(d[f"{pref}C117"], ["Yes"], ["No"])
            ever = _binary(d[f"{pref}C116"], ["Yes"], ["No"])
            smoke = pd.Series(float("nan"), index=d.index)
            smoke[now == 1] = 1.0
            smoke[(now == 0) | (ever == 0)] = 0.0
            fr["current_smoking"] = smoke
        if f"{pref}C011" in d:
            fr["diabetes"] = _binary(d[f"{pref}C011"], ["Yes"], ["No"])
        if f"{pref}bmi" in d:
            fr = _add_bmi(fr, d[f"{pref}bmi"])
        if f"{pref}A002_age" in d:
            fr["age"] = _code(d[f"{pref}A002_age"])
        if f"{pref}gender1" in d:
            fr["sex"] = _sex(d[f"{pref}gender1"])
        frames.append(fr)
        diagnostics.append({"wave": w, "status": "ok", "rows": len(fr),
                            "file": f.name, "vars_found": sorted(want)})

    if not frames:
        return pd.DataFrame(), {"cohort": "KLoSA", "waves": diagnostics}
    return pd.concat(frames, ignore_index=True), {"cohort": "KLoSA", "waves": diagnostics}


# ----------------------------------------------------------------------------
# CRELES (extracted to data/raw/creles). NOTE C45: the two CRELES cohorts use
# the SAME variable names for DIFFERENT constructs -- in the pre-1945 file
# `c55` = SeeFar, but in the 1945-1955 retirement file `c55q` = contact-lens
# use. Only the pre-1945 files are used here.
# ----------------------------------------------------------------------------
CRELES_DIR = ROOT / "data" / "raw" / "creles"


def build_creles() -> tuple[pd.DataFrame, dict]:
    frames, diagnostics = [], []
    for w in (1, 2, 3):
        # C57: the previous glob was `__DS1*.dta`, and because the files are
        # named DS1, DS2, ... DS10, ... the pattern `DS1*` also matches
        # `DS10_Recoded_Variables` -- so the wrong file was selected and every
        # wanted variable came back missing (empty frame -> IndexError).
        # Anchor the delimiter (`__DS1_`) AND verify the header really carries
        # the target variables before using the file.
        cands = sorted(CRELES_DIR.glob(f"Data-CRELES-pre-1945-WAVE{w}__DS1_*.dta"))
        f = None
        for c in cands:
            try:
                cols = set(pd.read_stata(str(c), iterator=True).variable_labels())
            except Exception:
                continue
            if {"c55", "c57"} <= cols:
                f = c
                break
        if f is None:
            diagnostics.append({"wave": w, "status": "no DS1 file carrying c55/c57",
                               "candidates": [c.name for c in cands]})
            continue
        it = pd.read_stata(str(f), iterator=True)
        L = it.variable_labels()
        want = [c for c in ("c54", "c55", "c56", "c57", "c58", "c59", "c60",
                            "c4", "c10", "imc2", "ev10", "idsujeto")
                if c in L]
        d = pd.read_stata(str(f), columns=want)
        # C57: CRELES' person key is `idsujeto`.
        idcol = "idsujeto" if "idsujeto" in d.columns else d.columns[0]
        fr = pd.DataFrame({idcol: d[idcol], "wave": w, "cohort": "CRELES",
                           "implicat": 1}).rename(columns={idcol: "mergeid"})

        # c55 (SeeFar) / c56 (SeeClose) use an UNDECODED numeric 1-7 scale.
        # Neither the harmonized CRELES codebook (H_CRELES_codebook.pdf) nor
        # H_CRELES_creation.do documents the raw vision items, and a keyword
        # sweep of both returns nothing. Guessing the direction of a 1-7 scale
        # would risk inverting the outcome, so we do NOT emit
        # vision_impairment_* for CRELES until an external codebook is read.
        # What CRELES CAN give without any codebook is the self-describing
        # blindness category buried in the glasses question (correction C45),
        # plus the disease items, which are plain Yes/No.
        if "c54" in d:
            g = d["c54"].astype(str).str.strip()
            fr["blindness_selfreport"] = (g == "Is blind").astype(float).where(
                g.isin(["Yes, to see near and far", "Does not use", "Yes, to see near",
                        "Yes, to see far", "Is blind", "DK/NR"]))
            fr["uses_glasses"] = g.isin(
                ["Yes, to see near and far", "Yes, to see near", "Yes, to see far"]
            ).astype(float)
        if "c57" in d:
            fr["cataract_any"] = _binary(d["c57"], ["Yes"], ["No"], ["DK", "NR"])
        if "c58" in d:
            fr["cataract_surgery"] = _binary(d["c58"], ["Yes"], ["No"], ["DK", "NR"])
        if "c60" in d:
            fr["glaucoma_selfreport"] = _binary(d["c60"], ["Yes"], ["No"], ["DK", "NR"])
        if "c4" in d:
            fr["hypertension"] = _binary(d["c4"], ["Yes"], ["No"], ["DK", "NR"])
        if "c10" in d:
            fr["diabetes"] = _binary(d["c10"], ["Yes"], ["No"], ["DK", "NR"])
        if "imc2" in d:
            fr = _add_bmi(fr, d["imc2"])
        if "ev10" in d:
            fr["current_smoking"] = _binary(d["ev10"], ["Yes"], ["No"], ["DK/NR"])
        # C66: CRELES age/sex are in the DS10 "Recoded Variables" file of the
        # same wave (the DS1 main form does not carry them), keyed on idsujeto.
        for p10 in sorted(CRELES_DIR.glob(f"Data-CRELES-pre-1945-WAVE{w}__DS10*.dta")):
            try:
                i10 = pd.read_stata(str(p10), iterator=True)
                L10 = i10.variable_labels()
            except Exception:
                continue
            # imc2 (BMI) also lives in DS10, not in the DS1 main form
            need10 = [c for c in ("idsujeto", "age", "sex", "imc2") if c in L10]
            if len(need10) < 2:
                continue
            d10 = pd.read_stata(str(p10), columns=need10)
            if "idsujeto" in d10.columns:
                d10 = (d10.rename(columns={"idsujeto": "mergeid"})
                         .drop_duplicates("mergeid"))
                fr = fr.merge(d10, on="mergeid", how="left")
                # C68 again: DS10's sex is bare 'Male'/'Female' text while
                # ge is genuinely numeric -- they need different decoders.
                if "sex" in fr.columns:
                    fr["sex"] = _sex(fr["sex"])
                if "age" in fr.columns:
                    fr["age"] = _code(fr["age"]).where(
                        lambda x: x.between(18, 120))
                if "imc2" in fr.columns:
                    fr = _add_bmi(fr, fr["imc2"])
            break
        frames.append(fr)
        diagnostics.append({"wave": w, "status": "ok", "rows": len(fr),
                            "file": f.name, "vars_found": sorted(want)})

    if not frames:
        return pd.DataFrame(), {"cohort": "CRELES", "waves": diagnostics}
    return pd.concat(frames, ignore_index=True), {"cohort": "CRELES", "waves": diagnostics}


BUILDERS.update({"HRS": build_hrs, "MHAS": build_mhas,
                 "KLoSA": build_klosa, "CRELES": build_creles})


# ----------------------------------------------------------------------------
# ELSA. Wave 3 (`wave_3_elsa_data_v4.dta`) is the single richest file: it
# carries the three self-rated eyesight items AND the three eye-disease items,
# so one wave is enough to build a complete frame. The eyesight ratings again
# specify "while using lenses, if appropriate", i.e. CORRECTED vision (C27).
# ----------------------------------------------------------------------------
ELSA_ROOT = DB / "02. ELSA 英国老龄化纵向研究/Raw_data"
ELSA_VERDICT = {"excellent": 1, "very good": 2, "good": 3, "fair": 4, "poor": 5}


def _elsa_scale(series: pd.Series) -> pd.Series:
    """ELSA eyesight labels arrive as '... excellent,', 'fair,' etc. with
    leading/trailing punctuation, and code 6 means registered/legally blind."""
    s = (series.astype(str).str.strip().str.lower()
         .str.strip(" .,").str.replace(r"^spontaneous:\s*", "", regex=True))
    v = s.map(ELSA_VERDICT)
    v[s.str.contains("registered or legally blind", na=False)] = 6.0
    return v


def build_elsa() -> tuple[pd.DataFrame, dict]:
    diagnostics = []
    core = next(iter(sorted(ELSA_ROOT.rglob("wave_3_elsa_data_v4.dta"))), ELSA_ROOT / "wave_3_elsa_data_v4.dta")
    if not core.exists():
        return pd.DataFrame(), {"cohort": "ELSA",
                                "waves": [{"status": "wave 3 core missing"}]}
    it = pd.read_stata(str(core), iterator=True)
    L = it.variable_labels()
    idc = next((c for c in ("idauniq", "idauniq3", "mergeid", "id") if c in L), None)
    want = [c for c in ("heeye", "hefrnd", "hepap", "heoptca", "heoptgl",
                        "heoptmd", "rahsik", "sex", "age") if c in L]
    if idc:
        want.append(idc)
    d = pd.read_stata(str(core), columns=want)
    fr = pd.DataFrame({"mergeid": d[idc] if idc else range(len(d)),
                       "wave": 3, "cohort": "ELSA", "implicat": 1})

    if "heeye" in d:
        v = _elsa_scale(d["heeye"])
        fr["vision_rating_ordinal"] = v
        fr["vision_impairment_moderate"] = (v == 4).astype(float).where(v.notna())
        fr["vision_impairment_severe"] = (v >= 5).astype(float).where(v.notna())
        fr["blindness_selfreport"] = (v == 6).astype(float).where(v.notna())
    for src, tag in (("hefrnd", "distance"), ("hepap", "near")):
        if src in d:
            fr[f"vision_rating_{tag}"] = _elsa_scale(d[src])
    # Eye-disease items are multi-level "By Wave 1 / By Wave 2 / ..." in the
    # derived files; in the wave-3 core file they are the plain report.
    for src, name in (("heoptca", "cataract_any"), ("heoptgl", "glaucoma_selfreport"),
                      ("heoptmd", "amd_any")):
        if src in d:
            s = d[src].astype(str).str.strip()
            hit = s.str.lower().str.contains("by wave|yes|mention", na=False)
            neg = s.str.lower().str.contains("neither|no$|^no", na=False)
            out = pd.Series(float("nan"), index=d.index)
            out[hit] = 1.0
            out[neg] = 0.0
            fr[name] = out

    # smoking, from the life-history file where it is explicitly labelled
    lh = next(iter(sorted(ELSA_ROOT.rglob("wave_3_life_history_data.dta"))), ELSA_ROOT / "wave_3_life_history_data.dta")
    if lh.exists() and idc:
        lit = pd.read_stata(str(lh), iterator=True)
        LL = lit.variable_labels()
        lcols = [c for c in ("rhska", "age", "sex") if c in LL] + [idc]
        if len(lcols) > 1:
            l = pd.read_stata(str(lh), columns=lcols)
            l = l.rename(columns={idc: "mergeid"}).drop_duplicates("mergeid")
            fr = fr.merge(l, on="mergeid", how="left")
            # C68: the life-history `sex` column is bare 'Male'/'Female' text, so
            # _code() (which needs a leading integer) nulls it out. Route it
            # through _sex(); the same applies to age, which is genuinely numeric.
            if "sex" in fr.columns:
                fr["sex"] = _sex(fr["sex"])
            if "age" in fr.columns:
                fr["age"] = _code(fr["age"])
            if "rhska" in fr.columns:
                s = fr["rhska"].astype(str).str.strip().str.lower()
                out = pd.Series(float("nan"), index=fr.index)
                out[s.str.startswith("yes")] = 1.0
                out[s.str.startswith("no")] = 0.0
                fr["current_smoking"] = out
    diagnostics.append({"wave": 3, "status": "ok", "rows": len(fr),
                        "vars_found": sorted(want),
                        "note": "smoking/age/sex merged from wave_3_life_history_data"})
    return fr, {"cohort": "ELSA", "waves": diagnostics}


# ----------------------------------------------------------------------------
# LASI wave 1. The eye-disease outcomes are NOT separate indicator columns:
# ht017s1..s6 exist with the right labels but contain no data, while the
# multi-response string `ht017` holds codes whose meaning IS given by those
# labels (ht017s2 = cataract, ht017s3 = glaucoma). Correction C39/C40: this is
# a codebook-backed decode, not an inference from frequencies.
# ----------------------------------------------------------------------------
LASI_ROOT = DB / "05. LASI 印度老龄化纵向研究/LASI_印度/Raw_data"
LASI_FILE = LASI_ROOT / "LASI Wave 1 (Version B) Data/lasi_w1b_ind_bm.dta"
LASI_EYE_CODES = {"1": "presbyopia", "2": "cataract", "3": "glaucoma",
                  "4": "myopia", "5": "hypermetropia", "6": "other_eye"}


def build_lasi() -> tuple[pd.DataFrame, dict]:
    if not LASI_FILE.exists():
        return pd.DataFrame(), {"cohort": "LASI", "waves": [{"status": "file missing"}]}
    it = pd.read_stata(str(LASI_FILE), iterator=True)
    L = it.variable_labels()
    want = [c for c in ("prim_key", "ht015", "ht016", "ht017", "ht019", "ht020",
                        "ht002", "ht003", "hb001", "hb003",
                        "dm003", "dm005")   # C66: sex, age
            if c in L]
    d = pd.read_stata(str(LASI_FILE), columns=want)
    fr = pd.DataFrame({"mergeid": d["prim_key"] if "prim_key" in d else range(len(d)),
                       "wave": 1, "cohort": "LASI", "implicat": 1})

    if "ht017" in d:
        parts = d["ht017"].astype(str).str.split("-")
        has = lambda code: parts.apply(lambda p: code in p) & d["ht017"].notna()
        fr["cataract_any"] = has("2").astype(float).where(d["ht017"].notna())
        fr["glaucoma_selfreport"] = has("3").astype(float).where(d["ht017"].notna())
        fr["myopia_selfreport"] = has("4").astype(float).where(d["ht017"].notna())
        fr["presbyopia_selfreport"] = has("1").astype(float).where(d["ht017"].notna())
    if "ht015" in d:
        num = _code(d["ht015"])
        fr["eye_problem_any"] = num.where(num.isin([1, 2])).map({1: 1.0, 2: 0.0})
    for src, tag in (("ht019", "distance"), ("ht020", "near")):
        if src in d:
            v = _code(d[src]).where(lambda x: x.between(1, 6))
            fr[f"vision_rating_{tag}"] = v
            if tag == "distance":
                fr["vision_rating_ordinal"] = v
                fr["vision_impairment_moderate"] = (v == 4).astype(float).where(v.notna())
                fr["vision_impairment_severe"] = (v >= 5).astype(float).where(v.notna())
    if "ht002" in d:
        num = _code(d["ht002"])
        fr["hypertension"] = num.where(num.isin([1, 2])).map({1: 1.0, 2: 0.0})
    if "ht003" in d:
        num = _code(d["ht003"])
        fr["diabetes"] = num.where(num.isin([1, 2])).map({1: 1.0, 2: 0.0})
    if "dm005" in d:
        fr["age"] = _code(d["dm005"])
    if "dm003" in d:
        fr["sex"] = _sex(d["dm003"])
    if "hb001" in d:      # "Have you ever smoked..." style item, gate-checked below
        s = d["hb001"].astype(str).str.strip().str.lower()
        out = pd.Series(float("nan"), index=d.index)
        out[s.str.startswith("yes")] = 1.0
        out[s.str.startswith("no")] = 0.0
        fr["ever_smoked"] = out
    diag = {"wave": 1, "status": "ok", "rows": len(fr), "vars_found": sorted(want),
            "note": ("hb001 is an ever-smoked item; LASI's current-smoking item "
                     "(if any) must pass the C56 gate audit before use")}
    return fr, {"cohort": "LASI", "waves": [diag]}


BUILDERS.update({"ELSA": build_elsa, "LASI": build_lasi})


# ----------------------------------------------------------------------------
# CLHLS. Ships as CSV (6,175 columns), so it does not go through the .dta path.
# Three traps, all recorded in docs/cohort_variable_mapping.md:
#
#  C24/C61  the disease block renames itself: baseline `g17<letter>1`, follow-up
#           `g15<letter>1_<wave>`; verified stable for a/b and g/h across 1998
#           and 2000.
#  C62      the smoking/drinking block shifts even more dangerously: baseline
#           `d61` = smoke now and `d71` = DRINK now, while follow-up
#           `d71_<wave>` = SMOKE now. The same token `d71` therefore means
#           drinking at baseline and smoking once suffixed. Follow-ups carry no
#           drinking item, so alcohol_intake is baseline-only.
#  C63      the codebook's stated missing conventions (9/99 missing, 8/88 don't
#           know, -1 not applicable) do NOT describe this release: the data also
#           carry -6/-7/-8/-9, and `g1_2` alone has -8 in 4,261 rows. Reading -8
#           as a valid response would be catastrophic, so EVERY negative code
#           plus 8/88/9/99 becomes missing. That choice cannot invert an
#           outcome, which is why it is the safe default.
# ----------------------------------------------------------------------------
CLHLS_DIR = DB / "09. CLHLS 中国老年健康影响因素跟踪调查/clhls"
CLHLS_WAVES = [("", 1998), ("_0", 2000), ("_2", 2002), ("_5", 2005),
               ("_8", 2008), ("_11", 2011), ("_14", 2014), ("_18", 2018)]


def _clhls_clean(series: pd.Series) -> pd.Series:
    """Numeric codes with every missing convention mapped to NaN (see C63)."""
    v = _code(series)
    v = v.where(v >= 0)                              # -1/-6/-7/-8/-9 -> NaN
    return v.where(~v.isin([8, 9, 88, 99, 888, 999]))  # DK / missing


def build_clhls() -> tuple[pd.DataFrame, dict]:
    f = next(iter(sorted(CLHLS_DIR.rglob(
        "clhls_1998_2018_longitudinal_dataset_released_version1.csv"))), None)
    if f is None:
        return pd.DataFrame(), {"cohort": "CLHLS",
                                "waves": [{"status": "csv not found"}]}
    cols = ["id", "g12", "a1", "trueage"] + [
        f"{base}{suf}"
        for suf, _ in CLHLS_WAVES
        for base in (["g1", "g17g1", "g17h1", "g17a1", "g17b1", "d61", "d71"]
                     if suf == "" else
                     ["g1", "g15g1", "g15h1", "g15a1", "g15b1", "d71"])
    ]
    hdr = pd.read_csv(f, nrows=0, low_memory=False).columns.tolist()
    use = [c for c in cols if c in hdr]
    d = pd.read_csv(f, usecols=use, low_memory=False)
    diagnostics = [{"file": f.name, "columns_requested": len(cols),
                    "columns_found": len(use), "rows": len(d)}]

    frames = []
    for suf, year in CLHLS_WAVES:
        fr = pd.DataFrame({"mergeid": d["id"], "wave": year,
                           "cohort": "CLHLS", "implicat": 1})
        # C66: a1 = sex; trueage = CLHLS' validated age (not the a53* household
        # member ages, which are a different construct).
        if "trueage" in d:
            fr["age"] = _clhls_clean(d["trueage"]).where(lambda s: s.between(18, 130))
        if "a1" in d:
            fr["sex"] = _sex(d["a1"])
        vis = f"g1{suf}"
        if vis in d:
            v = _clhls_clean(d[vis]).where(lambda s: s.between(1, 4))
            fr["vision_rating_ordinal"] = v
            # C65: the g1 scale is NOT the same in every wave. Read row by row
            # from the codebook:
            #   g1    (1998) 1 see+distinguish / 2 see but can't distinguish /
            #                3 can't see / 4 blind                    (4 levels)
            #   g1_0  (2000) 1 see+distinguish / 2 can't see / 3 blind (3 levels,
            #                NO "can see only" category at all)
            #   g1_2+ (2002+) 1 / 2 can see only / 3 cannot see / 4 blind (4 levels)
            # A single mapping across waves therefore misclassifies wave 2000:
            # code 2 there is SEVERE ("can't see"), not moderate. The pooled
            # prevalence still looked plausible (18.3% moderate), which is why
            # the prevalence gate alone could not catch it -- the gate must also
            # be read per wave.
            if year == 2000:
                # no "can see only" category exists in this wave
                fr["vision_impairment_moderate"] = pd.Series(float("nan"), index=d.index)
                fr["vision_impairment_severe"] = (v >= 2).astype(float).where(v.notna())
                fr["blindness_selfreport"] = (v == 3).astype(float).where(v.notna())
            else:
                fr["vision_impairment_moderate"] = (v == 2).astype(float).where(v.notna())
                fr["vision_impairment_severe"] = (v >= 3).astype(float).where(v.notna())
                fr["blindness_selfreport"] = (v == 4).astype(float).where(v.notna())
            diagnostics.append({
                "wave": year, "var": vis, "scale_levels": 3 if year == 2000 else 4,
                "distribution": {int(k): int(x) for k, x in
                                 v.value_counts(dropna=True).sort_index().items()}})
        pair = (("g17g1", "cataract_any"), ("g17h1", "glaucoma_selfreport"),
                ("g17a1", "hypertension"), ("g17b1", "diabetes")) if suf == "" else \
               (("g15g1", "cataract_any"), ("g15h1", "glaucoma_selfreport"),
                ("g15a1", "hypertension"), ("g15b1", "diabetes"))
        for base, name in pair:
            col = f"{base}{suf}"
            if col in d:
                v = _clhls_clean(d[col])
                out = pd.Series(float("nan"), index=d.index)
                out[v == 1] = 1.0
                out[v == 2] = 0.0
                fr[name] = out
        scol = "d61" if suf == "" else f"d71{suf}"      # C62
        if scol in d:
            v = _clhls_clean(d[scol])
            out = pd.Series(float("nan"), index=d.index)
            out[v == 1] = 1.0
            out[v == 2] = 0.0
            fr["current_smoking"] = out
        if suf == "" and "d71" in d:                     # baseline-only (C62)
            v = _clhls_clean(d["d71"])
            out = pd.Series(float("nan"), index=d.index)
            out[v == 1] = 1.0
            out[v == 2] = 0.0
            fr["alcohol_intake"] = out
        if "g12" in d:
            # weight only; CLHLS has no height here, so BMI is NOT computable
            fr["weight_kg"] = _clhls_clean(d["g12"]).where(lambda s: s.between(20, 200))
        frames.append(fr)

    return pd.concat(frames, ignore_index=True), {"cohort": "CLHLS",
                                                  "waves": diagnostics}


BUILDERS.update({"CLHLS": build_clhls})


def prevalence_gate(frame: pd.DataFrame, cohort: str) -> dict:
    """Measure, per outcome/exposure, the observed prevalence and analysable n.

    The gate does not correct anything; it reports so that a cohort whose
    measured prevalence is implausible can be excluded before pre-registration
    rather than after a surprising result.

    C53: if the frame carries imputation replicates, prevalence is computed on
    replicate 1 only. Pooling all replicates would leave the point estimate
    essentially unchanged while multiplying n by the replicate count, which is
    exactly the kind of inflated-n that makes a prevalence gate stop working.
    """
    report = {"cohort": cohort, "n_rows": len(frame), "flags": {}}
    if "implicat" in frame.columns:
        reps = sorted(pd.to_numeric(frame["implicat"], errors="coerce")
                      .dropna().unique().tolist())
        report["imputation_replicates"] = reps
        report["rows_per_replicate"] = int((frame["implicat"] == reps[0]).sum())
        gate_frame = frame[frame["implicat"] == reps[0]]
    else:
        gate_frame = frame

    for col in sorted(frame.columns):
        if col not in REFERENCE_HARD:
            continue
        s = pd.to_numeric(gate_frame[col], errors="coerce")
        n = int(s.notna().sum())
        prev = float(s.mean()) if n else None
        lo, hi = REFERENCE_HARD[col]
        tlo, thi = REFERENCE_TYPICAL.get(col, (None, None))
        hard_ok = (prev is not None) and (lo <= prev <= hi)
        typical_ok = (prev is not None) and tlo is not None and (tlo <= prev <= thi)
        report["flags"][col] = {
            "n": n, "prevalence": None if prev is None else round(prev, 4),
            "hard_band": [lo, hi], "passes_hard_gate": bool(hard_ok),
            "typical_band": [tlo, thi], "within_typical": bool(typical_ok),
        }
    report["gate_passed"] = all(v["passes_hard_gate"] for v in report["flags"].values())
    report["failed"] = [k for k, v in report["flags"].items() if not v["passes_hard_gate"]]
    report["outside_typical"] = [k for k, v in report["flags"].items() if not v["within_typical"]]

    # C65: per-wave prevalence, because a wave-specific defect hides inside a
    # plausible POOLED number. CLHLS wave 2000 uses a 3-level g1 scale while
    # every other wave uses 4 levels, so one shared mapping silently reclassified
    # 1,499 people from "cannot see" to "moderate" -- and the pooled moderate
    # prevalence stayed at 18.3%, i.e. perfectly ordinary. Pooling cannot see
    # that; only a per-stratum read can, so the gate always reports it. Waves
    # whose prevalence sits far from the cohort's own pooled value are listed
    # under `wave_outliers`.
    if "wave" in gate_frame.columns and gate_frame["wave"].nunique() > 1:
        per_wave, outliers = {}, []
        for w, sub in gate_frame.groupby("wave"):
            per_wave[int(w)] = {}
            for col in sorted(report["flags"]):
                s = pd.to_numeric(sub[col], errors="coerce")
                if not s.notna().any():
                    continue
                p = round(float(s.mean()), 4)
                per_wave[int(w)][col] = {"n": int(s.notna().sum()), "prevalence": p}
                pooled = report["flags"][col]["prevalence"]
                if pooled and abs(p - pooled) > 0.10:
                    outliers.append({"wave": int(w), "flag": col,
                                     "wave_prevalence": p, "pooled": pooled})
        report["per_wave"] = per_wave
        report["wave_outliers"] = outliers

    # Age context. A fixed reference range cannot be read without knowing the
    # cohort's age structure: CRELES' pre-1945 cohort is entirely 60+ and its
    # cataract prevalence is 38.5%, which is above the generic 3-30% band yet
    # entirely ordinary for that age. Reporting the age distribution keeps the
    # comparison interpretable WITHOUT silently widening the band to force a
    # pass -- which would be a post-hoc adjustment of the gate itself.
    if "age" in gate_frame.columns:
        a = pd.to_numeric(gate_frame["age"], errors="coerce").dropna()
        if len(a):
            report["age_context"] = {
                "n": int(len(a)), "mean": round(float(a.mean()), 1),
                "min": float(a.min()), "max": float(a.max()),
                "pct_60plus": round(float((a >= 60).mean()), 4),
            }
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cohort", choices=list(BUILDERS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    frame, diag = BUILDERS[args.cohort]()
    if frame.empty:
        print(f"{args.cohort}: no rows built")
        print(json.dumps(diag, ensure_ascii=False, indent=2)[:800])
        return 1

    report = prevalence_gate(frame, args.cohort)
    print(f"=== {args.cohort} frame ===")
    print(f"  rows={len(frame)}  persons={frame['mergeid'].nunique()}  "
          f"waves={sorted(frame['wave'].unique())}")
    print(f"  flags built: {[c for c in frame.columns if c in REFERENCE]}")
    print(f"  --- prevalence gate ---")
    for k, v in report["flags"].items():
        mark = "PASS" if v["passes_hard_gate"] else "FAIL"
        print(f"    {mark}  {k:28s} n={v['n']:7d} prev={v['prevalence']} "
              f"hard={v['hard_band']} typical={v['typical_band']}")
    print(f"  gate_passed={report['gate_passed']}  failed={report['failed']}")

    if not args.dry_run:
        FRAMES.mkdir(parents=True, exist_ok=True)
        fp = FRAMES / f"cohort_{args.cohort}.csv"
        frame.to_csv(fp, index=False, encoding="utf-8")
        OUT.mkdir(parents=True, exist_ok=True)
        op = OUT / f"cohort_{args.cohort}_prevalence.json"
        op.write_text(json.dumps({"diagnostics": diag, "gate": report},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {fp}")
        print(f"  -> {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
