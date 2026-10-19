#!/usr/bin/env python
"""Measure which of the 21 pre-registered rules each cohort frame can actually test.

This is the evidence base for the cohort-layer pre-registration. It does not
guess from variable names or from the ledger's prose: it opens the built frames,
looks for the columns that operationalise each rule's exposure and outcome
flags, and reports the analysable n for the pair.

Mapping rule-flag vocabulary -> frame columns
---------------------------------------------
The rule file (configs/rules.yaml) uses the project's canonical flag names.
The cohort frames use the constructs the cohorts actually provide, and two of
those are deliberately NOT the canonical flag (corrections C21/C29/C45):

  cataract_any            <- cataract_any            (true disease)
  cataract_surgery        <- cataract_surgery        (NOT disease; construct-shifted)
  glaucoma_selfreport     <- glaucoma_selfreport     (self-reported dx)
  glaucoma_treated        <- glaucoma_treated        (NOT disease dx)
  vision_impairment_*     <- vision_impairment_*
  bmi_high                <- bmi_high_25 / bmi_high_30  (both cuts; C58)

A rule is marked testable only when BOTH sides are present with a minimum
number of non-missing observations, and the outcome is not a construct-shifted
proxy for the disease the rule is about. Rules whose outcome needs fundus
imaging, IOP or optic-disc grading are testable nowhere and are reported as
such rather than silently dropped.

Output: outputs/confirmatory/cohort_rule_coverage.json  (+ console matrix)

Usage: python scripts/cohort_rule_coverage.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "confirmatory"

MIN_N = 200          # minimum non-missing for either side to count as testable

# Single source of truth for the BMI cut-point, by cohort. Previously this
# convention existed only as a dict inside build_descriptive_table.py, while eight
# other scripts each carried their own copy or none, and nothing checked that the
# coverage matrix agreed with it.
# Copied from analysis_plan.md section 19.7 (C58), which pre-declares the primary
# cut per cohort: KLoSA/MHAS/LASI/CLHLS at the Asian cut 25, SHARE/HRS/ELSA/CRELES
# at the international cut 30. MHAS is 25 -- an earlier version of this table,
# copied from build_descriptive_table.py, said 30 there, and that file was wrong.
BMI_CUT = {"SHARE": 30, "HRS": 30, "ELSA": 30, "KLoSA": 25, "LASI": 25,
           "MHAS": 25, "CLHLS": 25, "CRELES": 30}


def resolve_bmi_col(coh: str) -> str | None:
    """The BMI cut column this cohort is entitled to, by convention."""
    cut = BMI_CUT.get(coh)
    return f"bmi_high_{cut}" if cut else None

# rule flag -> candidate frame columns, in preference order
EXPOSURE_MAP = {
    "current_smoking":       ["current_smoking"],
    "alcohol_intake":        ["alcohol_intake"],
    # The BMI cut-point is fixed by COHORT, not by preference order. Until
    # 2026-10-16 this entry read ["bmi_high_25", "bmi_high_30"] and the resolver
    # took the first column present -- and both frames carry BOTH columns, so every
    # cohort was tested at 25 kg/m2 regardless of the convention. r13's two
    # feasible cells (SHARE, CRELES) are both non-Asian and should have used 30;
    # the only cohort whose cut really is 25, KLoSA, is not feasible. Low
    # thresholds move more people into the exposed group, diluting the contrast
    # and pulling the OR toward the null: SHARE's estimate was 1.139 at cut 25
    # against 1.235 at the convention's 30 (scripts/r13_cutpoint_sensitivity.py).
    "bmi_high":              ["__cohort_bmi_cut__"],
    "hyperglycemia":         ["diabetes"],
    "hba1c_elevated":        ["diabetes"],      # no HbA1c in the cohort files
    "dyslipidemia":          ["dyslipidemia"],
    "crp_elevated":          [],                # needs a blood assay
    "vitamin_d_deficiency":  [],
    "low_antioxidant_intake": [],
    "mediterranean_diet":    [],
    "pro_inflammatory_diet": [],
    "uric_acid_elevated":    [],
    "lead_exposure":         [],
    "pm25_exposure":         [],                # needs geocoded linkage
    "uv_exposure":           [],
}
OUTCOME_MAP = {
    "cataract_any":              ["cataract_any"],
    "vision_impairment_moderate": ["vision_impairment_moderate"],
    "vision_impairment_severe":   ["vision_impairment_severe"],
    "amd_late":                  ["amd_any", "amd_late"],
    "amd_early":                 ["amd_any", "amd_early"],
    "glaucoma_selfreport":       ["glaucoma_selfreport"],
    "retinopathy_any":           [],            # needs fundus imaging
    "dr_npdr":                   [],            # needs fundus imaging
    "dr_pdr":                    [],            # needs fundus imaging
    "glaucoma_iop_elevated":     [],            # needs tonometry
    "glaucoma_suspect_cdr":      [],            # needs optic-disc grading
}
# Construct-shifted proxies: usable only if the pre-registration declares the
# shift. Recorded per cohort so the choice stays visible.
CONSTRUCT_SHIFTED = {"cataract_surgery", "glaucoma_treated"}


def load_rules() -> list[dict]:
    return yaml.safe_load(
        (ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))["rules"]


def main() -> int:
    rules = load_rules()
    frames = {p.stem.replace("cohort_", ""): p
              for p in sorted(FRAMES.glob("cohort_*.csv"))}
    matrix, per_cohort = {}, {}

    for coh, path in frames.items():
        d = pd.read_csv(path, low_memory=False)
        avail = set(d.columns)
        n_by_col = {c: int(pd.to_numeric(d[c], errors="coerce").notna().sum())
                    for c in avail}
        per_cohort[coh] = {"rows": len(d), "flags_present":
                           sorted(c for c in avail if n_by_col.get(c, 0) > 0)}
        for r in rules:
            rid = r["id"]
            a_flags = r.get("entity_a_flags", [])
            b_flags = r.get("entity_b_flags", [])

            a_ok, a_used, a_n = [], [], 0
            for f in a_flags:
                for col in EXPOSURE_MAP.get(f, []):
                    if col == "__cohort_bmi_cut__":
                        # Resolve by cohort, not by list order.
                        col = resolve_bmi_col(coh)
                        if col is None:
                            continue
                    if col in avail and n_by_col[col] >= MIN_N:
                        a_ok.append(f); a_used.append(col)
                        a_n = max(a_n, n_by_col[col]); break
            b_ok, b_used, b_n, shifted = [], [], 0, False
            for f in b_flags:
                for col in OUTCOME_MAP.get(f, []):
                    if col in avail and n_by_col[col] >= MIN_N:
                        if col in CONSTRUCT_SHIFTED:
                            shifted = True
                            continue          # not a disease outcome for this rule
                        b_ok.append(f); b_used.append(col)
                        b_n = max(b_n, n_by_col[col]); break

            testable = bool(a_ok) and bool(b_ok)
            matrix.setdefault(rid, {})[coh] = {
                "testable": testable,
                "exposure_flag": a_ok[0] if a_ok else None,
                "exposure_col": a_used[0] if a_used else None,
                "exposure_n": a_n,
                "outcome_flag": b_ok[0] if b_ok else None,
                "outcome_col": b_used[0] if b_used else None,
                "outcome_n": b_n,
                "construct_shifted_only": bool(shifted and not b_ok),
            }

    cohorts = list(frames)
    print(f"{'rule':38s} " + " ".join(f"{c[:6]:>7s}" for c in cohorts) + "   testable_in")
    print("-" * (40 + 8 * len(cohorts) + 12))
    summary = {}
    for rid in [r["id"] for r in rules]:
        row = matrix[rid]
        cells, ok_cohorts = [], []
        for c in cohorts:
            v = row[c]
            cells.append("  YES  " if v["testable"] else "   .   ")
            if v["testable"]:
                ok_cohorts.append(c)
        summary[rid] = ok_cohorts
        print(f"{rid:38s} " + " ".join(f"{x:>7s}" for x in cells)
              + f"   {len(ok_cohorts)}: {','.join(ok_cohorts) if ok_cohorts else '-'}")

    print()
    tested = [k for k, v in summary.items() if v]
    print(f"可检验规则 {len(tested)}/{len(rules)}")
    print(f"不可检验    {len(rules)-len(tested)}: "
          f"{[k for k, v in summary.items() if not v]}")

    OUT.mkdir(parents=True, exist_ok=True)
    op = OUT / "cohort_rule_coverage.json"
    op.write_text(json.dumps({"min_n": MIN_N, "cohorts": cohorts,
                              "per_cohort": per_cohort, "matrix": matrix,
                              "testable": summary}, ensure_ascii=False, indent=2),
                  encoding="utf-8")
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
