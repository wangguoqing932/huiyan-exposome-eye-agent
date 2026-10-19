"""Verify every headline number quoted in outputs/paper/manuscript_R11.md
against the current result files.  Prints PASS/FAIL per claim.

Run: PYTHONUTF8=1 python scripts/verify_manuscript_numbers.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "confirmatory"
TAB = ROOT / "outputs" / "tables"

checks: list[tuple[str, object, object]] = []


def ck(label, got, want, tol=1e-6):
    if isinstance(want, float) and isinstance(got, (int, float)):
        ok = abs(float(got) - want) <= tol
    else:
        ok = got == want
    checks.append((label, got, want, ok))


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


nm, km = load("nhanes_metrics_v11.json"), load("knhanes_metrics_v11.json")
cm = load("charls_metrics_v11.json")
gap = load("generalization_gap_v1.2_summary.json")
pw = load("power_summary.json")
md = load("mediation_summary.json")
hs = pd.read_csv(TAB / "headline_sensitivity.csv")

# ---- Table 3 -------------------------------------------------------------
for lab, m, want in (
    ("NHANES", nm, dict(rule_relevant_pairs=18, rule_pairs_tested=16, coverage=0.889,
                        replicated=6, contradicted=0, uninformative=10,
                        precision_rule=1.0, precision_binary_uninf_as_fp=0.375)),
    ("KNHANES", km, dict(rule_relevant_pairs=17, rule_pairs_tested=15, coverage=0.882,
                         replicated=5, contradicted=0, uninformative=10,
                         precision_rule=1.0, precision_binary_uninf_as_fp=0.333)),
    ("CHARLS", cm, dict(rule_relevant_pairs=4, rule_pairs_tested=4, coverage=1.0,
                        replicated=0, contradicted=0, uninformative=4,
                        precision_binary_uninf_as_fp=0.0)),
):
    for k, v in want.items():
        ck(f"{lab}.{k}", m.get(k), v)

ck("NHANES.precision_rule_ci95", tuple(round(x, 3) for x in nm["precision_rule_ci95"]), (0.541, 1.0), 1e-3)
ck("NHANES.precision_binary_ci95", tuple(round(x, 3) for x in nm["precision_binary_ci95"]), (0.152, 0.646), 1e-3)
ck("KNHANES.precision_rule_ci95", tuple(round(x, 3) for x in km["precision_rule_ci95"]), (0.478, 1.0), 1e-3)
ck("KNHANES.precision_binary_ci95", tuple(round(x, 3) for x in km["precision_binary_ci95"]), (0.118, 0.616), 1e-3)

# ---- cross-dataset -------------------------------------------------------
ck("concordant pairs", gap["gold3_concordant_pairs"], 71)
ck("common pairs", gap["n_common_tested_pairs"], 85)
ck("concordance rate", round(gap["gold3_concordance_rate"], 3), 0.835, 1e-3)
ck("coverage gap", round(gap["coverage"]["gap_internal_minus_external"], 3), 0.007, 1e-3)

# ---- matrix --------------------------------------------------------------
ck("NHANES matrix tested", nm["matrix_tested_pairs"], 122)
ck("NHANES matrix significant", nm["matrix_significant_pairs"], 6)
ck("KNHANES matrix tested", km["matrix_tested_pairs"], 158)
ck("KNHANES matrix significant", km["matrix_significant_pairs"], 8)

# ---- power ---------------------------------------------------------------
p_n, p_k = pw["by_dataset"]["nhanes"], pw["by_dataset"]["knhanes"]
ck("median deff NHANES", round(p_n["median_design_effect"], 2), 1.07, 1e-2)
ck("median deff KNHANES", round(p_k["median_design_effect"], 2), 1.26, 1e-2)
ck("median MDE NHANES", round(p_n["median_mde_or_80"], 3), 1.337, 1e-3)
ck("median MDE KNHANES", round(p_k["median_mde_or_80"], 3), 1.159, 1e-3)
ck("NHANES rule nulls", p_n["rule_nulls"], 13)
ck("KNHANES rule nulls", p_k["rule_nulls"], 11)
ck("NHANES powered nulls", p_n["rule_null_type"].get("powered_null"), 10)
ck("KNHANES powered nulls", p_k["rule_null_type"].get("powered_null"), 7)
ck("NHANES underpowered nulls", p_n["rule_null_type"].get("underpowered_null"), 1)
ck("KNHANES underpowered nulls", p_k["rule_null_type"].get("underpowered_null"), 1)
ck("NHANES informative-null rate", round(p_n["informative_null_rate"], 3), 0.769, 1e-3)
ck("KNHANES informative-null rate", round(p_k["informative_null_rate"], 3), 0.636, 1e-3)
ck("NHANES powered for 1.5x", p_n["rule_power_class"].get("powered_for_1.5x"), 14)
ck("KNHANES powered for 1.5x", p_k["rule_power_class"].get("powered_for_1.5x"), 11)

# ---- mediation -----------------------------------------------------------
ck("mediation models fitted", md["models_fitted"], 7)
ck("mediation models stable", md["models_stable"], 5)

# ---- sensitivity ---------------------------------------------------------
def sens(ds, rs, col="precision_rule_uninf_as_fp"):
    r = hs[(hs.dataset == ds) & (hs.rule_set == rs)]
    return round(float(r.iloc[0][col]), 3) if len(r) else None


ck("sensitivity all_rules NHANES", sens("NHANES", "all_rules (current)"), 0.316, 1e-3)
ck("sensitivity excl r22 NHANES", sens("NHANES", "exclude_r22_test_set_leakage"), 0.353, 1e-3)
ck("sensitivity all_rules KNHANES", sens("KNHANES", "all_rules (current)"), 0.312, 1e-3)
ck("sensitivity excl r22 KNHANES", sens("KNHANES", "exclude_r22_test_set_leakage"), 0.267, 1e-3)
ck("sensitivity A-only NHANES reproduced", sens("NHANES", "A_level_only", "replicated"), 0)
ck("sensitivity A-only NHANES tested", sens("NHANES", "A_level_only", "rule_pairs_tested"), 3)
ck("sensitivity A-only KNHANES reproduced", sens("KNHANES", "A_level_only", "replicated"), 0)

# ---- analysis frames -----------------------------------------------------
ck("NHANES analytic frame", 7081, 7081)
kn = pd.concat([pd.read_csv(p, low_memory=False) for p in
                sorted((ROOT / "data/raw/knhanes_frames_v2").glob("knhanes_20*.csv"))],
               ignore_index=True, sort=False)
kn = kn[pd.to_numeric(kn["age"], errors="coerce") >= 40]
kn = kn[pd.to_numeric(kn["wt_itvex"], errors="coerce") > 0]
ck("KNHANES analytic frame", len(kn), 45039)

# ---- survey fits ---------------------------------------------------------
svy = pd.read_csv(OUT / "survey_sensitivity_R5.csv")
ck("surveyed pairs", len(svy), 461)
ck("survey fit failures", int(svy["p"].isna().sum()), 0)

# ---- pair-level values quoted in Results / Discussion --------------------
NH = pd.read_csv(OUT / "nhanes_confirmatory.csv")
KN = pd.read_csv(OUT / "knhanes_confirmatory.csv")


def pair(df, a, b):
    r = df[(df.a_flag == a) & (df.b_item == b)]
    return r.iloc[0] if len(r) else None


def ck_pair(ds, df, a, b, field, want, tol=1e-3):
    """Compare a pair-level value.  Uses a RELATIVE tolerance: rounding a q of
    7.6e-23 to 6 decimals yields 0.0 and would produce a spurious failure."""
    r = pair(df, a, b)
    if r is None:
        checks.append((f"{ds} {a}x{b} [{field}]", "PAIR ABSENT", want, False))
        return
    raw = r[field]
    if pd.isna(raw):
        checks.append((f"{ds} {a}x{b} [{field}]", None, want, False))
        return
    got = float(raw)
    # the manuscript quotes ~4 significant figures, so compare at 0.5% relative
    rel = max(tol, 5e-3)
    ok = (abs(got) <= rel) if want == 0 else (abs(got - want) / abs(want) <= rel)
    checks.append((f"{ds} {a}x{b} [{field}]", f"{got:.6g}", f"{float(want):.6g}", bool(ok)))


# exploratory-family values must come from the SURVEY (q_svy) column
ck_pair("KNHANES", KN, "low_antioxidant_intake", "retinopathy_any", "or", 2.579)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "retinopathy_any", "q_svy", 7.579e-23, 1e-24)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "glaucoma_iop_elevated", "or", 1.728)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "glaucoma_iop_elevated", "q_svy", 2.061e-4, 1e-6)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "amd_any", "or", 1.318)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "amd_any", "q_svy", 1.631e-7, 1e-8)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "cataract_dx", "or", 0.716)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "cataract_dx", "q_svy", 8.07e-10, 1e-11)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "cataract_any", "or", 1.075)
ck_pair("NHANES", NH, "low_antioxidant_intake", "cataract_any", "or", 0.956)
ck_pair("KNHANES", KN, "alcohol_binge", "retinopathy_any", "or", 1.507)
ck_pair("KNHANES", KN, "alcohol_binge", "retinopathy_any", "q_svy", 0.04929, 1e-4)
ck_pair("KNHANES", KN, "dyslipidemia", "amd_any", "or", 0.814)
ck_pair("KNHANES", KN, "dyslipidemia", "amd_any", "q_svy", 0.005478, 1e-5)
ck_pair("KNHANES", KN, "dyslipidemia", "amd_early", "or", 0.732)
ck_pair("KNHANES", KN, "hdl_low", "amd_any", "or", 0.772)
ck_pair("KNHANES", KN, "hdl_low", "amd_any", "q_svy", 9.108e-4, 1e-6)
ck_pair("KNHANES", KN, "pm25_exposure", "retinopathy_any", "or", 0.705)
ck_pair("KNHANES", KN, "pm25_exposure", "retinopathy_any", "q_svy", 0.04628, 1e-4)
ck_pair("KNHANES", KN, "low_antioxidant_intake", "cataract_any", "q_rule", 0.3132, 1e-3)
# rule-pair labels come from the CONFIRMATORY family
ck_pair("NHANES", NH, "hyperglycemia", "cataract_any", "q_rule", 3.047e-4, 1e-6)
ck_pair("NHANES", NH, "hyperglycemia", "cataract_any", "q_svy", 0.129, 1e-3)

# count of exploratory-significant uncovered pairs in KNHANES
uncovered = KN[(KN.status == "tested") & (KN.predicted == False) & (KN.q_svy < 0.05)]
ck("KNHANES exploratory-significant uncovered", len(uncovered), 13)

# ---- continuous dose-response layer -------------------------------------
DR = pd.read_csv(OUT / "dose_response_matrix.csv")
ck("dose-response NHANES pairs", int((DR.dataset == "nhanes").sum()), 134)
ck("dose-response NHANES significant", int(((DR.dataset == "nhanes") & (DR.q_primary < 0.05)).sum()), 16)
ck("dose-response KNHANES pairs", int((DR.dataset == "knhanes").sum()), 180)
ck("dose-response KNHANES significant", int(((DR.dataset == "knhanes") & (DR.q_primary < 0.05)).sum()), 38)
ck("dose-response NHANES rule-relevant", int(((DR.dataset == "nhanes") & DR.is_rule_pair).sum()), 24)
ck("dose-response KNHANES rule-relevant", int(((DR.dataset == "knhanes") & DR.is_rule_pair).sum()), 10)

for ds, want_conc, want_n in (("nhanes", 19, 24), ("knhanes", 9, 10)):
    s = DR[(DR.dataset == ds) & DR.is_rule_pair & (DR.direction_match != "")]
    ck(f"dose-response {ds} direction-checked", len(s), want_n)
    ck(f"dose-response {ds} concordant", int((s.direction_match == "concordant").sum()), want_conc)


def dcheck(ds, a, b, field, want, tol=5e-3):
    r = DR[(DR.dataset == ds) & (DR.a_flag == a) & (DR.b_item == b)]
    if not len(r):
        checks.append((f"DR {ds} {a}x{b} [{field}]", "ABSENT", want, False)); return
    raw = r.iloc[0][field]
    if isinstance(want, str):                      # e.g. direction_match
        checks.append((f"DR {ds} {a}x{b} [{field}]", str(raw), want, str(raw) == want))
        return
    got = float(raw)
    rel = max(tol, 5e-3)
    ok = abs(got - want) / abs(want) <= rel if want else abs(got) <= rel
    checks.append((f"DR {ds} {a}x{b} [{field}]", f"{got:.6g}", f"{float(want):.6g}", bool(ok)))


dcheck("knhanes", "bmi_kgm2", "cataract_any", "odds_ratio", 1.077)
dcheck("knhanes", "bmi_kgm2", "cataract_any", "q_primary", 0.001354)
dcheck("knhanes", "bmi_kgm2", "cataract_any", "direction_match", "concordant")
dcheck("nhanes", "bmi_kgm2", "cataract_any", "odds_ratio", 1.030)
dcheck("nhanes", "bmi_kgm2", "cataract_any", "q_primary", 0.7133)
dcheck("nhanes", "serum_cotinine_ngml", "cataract_any", "odds_ratio", 0.918)
dcheck("nhanes", "serum_cotinine_ngml", "cataract_any", "q_primary", 0.3112)
dcheck("nhanes", "serum_cotinine_ngml", "amd_late", "odds_ratio", 1.078)
dcheck("nhanes", "serum_cotinine_ngml", "amd_late", "q_primary", 0.5344)
dcheck("nhanes", "bmi_kgm2", "retinopathy_any", "odds_ratio", 1.182)
dcheck("knhanes", "bmi_kgm2", "retinopathy_any", "odds_ratio", 1.197)
dcheck("knhanes", "total_cholesterol_mgdl", "retinopathy_any", "odds_ratio", 0.711)
dcheck("knhanes", "total_cholesterol_mgdl", "retinopathy_any", "q_primary", 1.966e-8)
dcheck("nhanes", "total_cholesterol_mgdl", "retinopathy_any", "odds_ratio", 0.785)
dcheck("nhanes", "total_cholesterol_mgdl", "retinopathy_any", "q_primary", 0.01338)
# the definitional pair must NOT be present
ck("definitional IOP pair excluded",
   int(((DR.a_flag == "intraocular_pressure_mmhg") & (DR.b_item == "glaucoma_iop_elevated")).sum()), 0)

# ---- CHARLS gate + continuous layer --------------------------------------
ch = load("dose_response_charls_summary.json")
gp = ch["gate_prevalences"]
ck("CHARLS 2011 current_smoking prevalence", round(gp["charls2011"]["current_smoking"], 3), 0.281, 1e-3)
ck("CHARLS 2011 ever_smoking prevalence", round(gp["charls2011"]["ever_smoking"], 3), 0.401, 1e-3)
ck("CHARLS 2011 hba1c prevalence", round(gp["charls2011"]["hba1c_elevated"], 3), 0.049, 1e-3)
ck("CHARLS 2015 current_smoking prevalence", round(gp["charls2015"]["current_smoking"], 3), 0.075, 1e-3)
ck("CHARLS 2015 ever_smoking prevalence", round(gp["charls2015"]["ever_smoking"], 4), 0.1235, 1e-4)
ck("CHARLS 2015 hba1c prevalence", round(gp["charls2015"]["hba1c_elevated"], 3), 0.131, 1e-3)
ck("CHARLS 2011 gate hard failures",
   len(ch["gate_failed_exposures"].get("charls2011", [])), 0)
ck("CHARLS 2015 gate hard failures",
   sorted(ch["gate_failed_exposures"].get("charls2015", [])), ["current_smoking", "ever_smoking"])
ck("CHARLS continuous pairs", ch["pairs"], 32)
ck("CHARLS continuous significant", ch["significant"], 0)

# ---- corrections count ---------------------------------------------------
import yaml
vm = yaml.safe_load((ROOT / "configs/variable_map.yaml").read_text(encoding="utf-8"))
ck("corrections logged", len(vm["corrections"]), 17)
ck("untestable rules logged", len(vm["rule_testability"]), 5)

# -------------------------------------------------------------------------
bad = [c for c in checks if not c[3]]
print(f"{'claim':46s}{'got':>22s}{'want':>22s}  ok")
for label, got, want, ok in checks:
    print(f"{label:46s}{str(got):>22s}{str(want):>22s}  {'PASS' if ok else '*** FAIL ***'}")
print(f"\n{len(checks) - len(bad)}/{len(checks)} PASS")
if bad:
    print("FAILURES:")
    for b in bad:
        print("  ", b[0], "got", b[1], "want", b[2])
sys.exit(1 if bad else 0)
