#!/usr/bin/env python
"""Evidence-base audit: quantify what the world's ageing cohorts can test.

"15 of 21 rules were untestable" is a count, not an analysis. This turns it into
a structured audit by classifying every rule by the MEASUREMENT MODALITY its
exposure and its outcome require, then asking, for each of the 8 cohorts:

  * which (rule x cohort) cells are feasible (21 x 8 = 168 possible tests);
  * for each infeasible cell, WHICH SIDE is missing -- exposure or outcome --
    because those imply different remedies;
  * and, for each single modality, how many extra cells it would unlock. That
    last column is the actionable one: it says where a consortium's next
    measurement should go, rather than only listing absences.

PRESENCE IS DERIVED, NEVER LISTED
---------------------------------
An earlier version hard-coded which cohort holds which flag. That is the same
error this project keeps finding elsewhere: it asserted, for instance, that ELSA
has a usable diabetes variable and that LASI has current smoking. Neither frame
does, so the audit claimed seven feasible cells that the confirmatory analysis
had already found untestable -- an internal contradiction between two tables of
the same paper. Presence is now read from the built frames at the same MIN_N the
coverage analysis uses, and the script exits non-zero if the two disagree.

Outputs
  outputs/cohorts/evidence_audit.json
  outputs/tables/table7_evidence_audit.md

Run: python scripts/evidence_base_audit.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts"

MIN_N = 200
COHORTS = ["SHARE", "HRS", "ELSA", "KLoSA", "LASI", "MHAS", "CLHLS", "CRELES"]

EXPOSURE_MODALITY = {
    "current_smoking": "questionnaire_behaviour",
    "alcohol_intake": "questionnaire_behaviour",
    "bmi_high": "anthropometry",
    "hyperglycemia": "selfreport_or_assay_metabolic",
    "hba1c_elevated": "blood_assay",
    "dyslipidemia": "blood_assay",
    "crp_elevated": "blood_assay",
    "vitamin_d_deficiency": "blood_assay",
    "uric_acid_elevated": "blood_assay",
    "lead_exposure": "blood_assay",
    "low_antioxidant_intake": "dietary_index",
    "mediterranean_diet": "dietary_index",
    "pro_inflammatory_diet": "dietary_index",
    "pm25_exposure": "geocoded_environment",
    "uv_exposure": "geocoded_environment",
}
OUTCOME_MODALITY = {
    "cataract_any": "selfreport_ocular_diagnosis",
    "glaucoma_selfreport": "selfreport_ocular_diagnosis",
    "vision_impairment_moderate": "vision_rating",
    "vision_impairment_severe": "vision_rating",
    "amd_late": "fundus_imaging_or_grading",
    "amd_early": "fundus_imaging_or_grading",
    "retinopathy_any": "fundus_imaging",
    "dr_npdr": "fundus_imaging",
    "dr_pdr": "fundus_imaging",
    "glaucoma_iop_elevated": "tonometry",
    "glaucoma_suspect_cdr": "optic_disc_grading",
}

FLAG_TO_COLUMNS = {
    "current_smoking": ["current_smoking"],
    "alcohol_intake": ["alcohol_intake"],
    "bmi_high": ["bmi_high_25", "bmi_high_30"],
    "hyperglycemia": ["diabetes"],
    "hba1c_elevated": [],
    "dyslipidemia": [],
    "crp_elevated": [],
    "vitamin_d_deficiency": [],
    "uric_acid_elevated": [],
    "lead_exposure": [],
    "low_antioxidant_intake": [],
    "mediterranean_diet": [],
    "pro_inflammatory_diet": [],
    "pm25_exposure": [],
    "uv_exposure": [],
    "cataract_any": ["cataract_any"],
    "glaucoma_selfreport": ["glaucoma_selfreport"],
    "vision_impairment_moderate": ["vision_impairment_moderate"],
    "vision_impairment_severe": ["vision_impairment_severe"],
    "amd_late": ["amd_any", "amd_late"],
    "amd_early": ["amd_any", "amd_early"],
    "retinopathy_any": [],
    "dr_npdr": [],
    "dr_pdr": [],
    "glaucoma_iop_elevated": [],
    "glaucoma_suspect_cdr": [],
}


def main() -> int:
    rules = yaml.safe_load(
        (ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))["rules"]

    n_by_cohort: dict[str, dict[str, int]] = {}
    for coh in COHORTS:
        fp = FRAMES / f"cohort_{coh}.csv"
        if not fp.exists():
            n_by_cohort[coh] = {}
            continue
        dd = pd.read_csv(fp, low_memory=False)
        n_by_cohort[coh] = {
            c: int(pd.to_numeric(dd[c], errors="coerce").notna().sum())
            for c in dd.columns}

    def present(flag: str, coh: str) -> bool:
        return any(n_by_cohort.get(coh, {}).get(col, 0) >= MIN_N
                   for col in FLAG_TO_COLUMNS.get(flag, []))

    cells = []
    for r in rules:
        rid = r["id"]
        a_flags = list(r.get("entity_a_flags") or [])
        b_flags = list(r.get("entity_b_flags") or [])
        for coh in COHORTS:
            a_ok = any(present(f, coh) for f in a_flags)
            b_ok = any(present(f, coh) for f in b_flags)
            if a_ok and b_ok:
                blocked = "none"
            elif not a_ok and not b_ok:
                blocked = "both_sides"
            elif not a_ok:
                blocked = "exposure_missing"
            else:
                blocked = "outcome_missing"
            cells.append({
                "rule_id": rid, "cohort": coh, "feasible": a_ok and b_ok,
                "blocked_by": blocked,
                "exposure_modalities": sorted({EXPOSURE_MODALITY[f]
                                               for f in a_flags
                                               if f in EXPOSURE_MODALITY}),
                "outcome_modalities": sorted({OUTCOME_MODALITY[f]
                                              for f in b_flags
                                              if f in OUTCOME_MODALITY})})

    df = pd.DataFrame(cells)
    total = len(df)
    feas = int(df.feasible.sum())
    by_block = {k: int(v) for k, v in
                df[~df.feasible].blocked_by.value_counts().items()}
    feasible_pairs = set(zip(df[df.feasible].rule_id, df[df.feasible].cohort))

    unlock: dict[str, int] = {}
    for mod in sorted(set(EXPOSURE_MODALITY.values())):
        flags = {f for f, m in EXPOSURE_MODALITY.items() if m == mod}
        newly = 0
        for r in rules:
            a = set(r.get("entity_a_flags") or [])
            if not (a & flags):
                continue
            for coh in COHORTS:
                if any(present(f, coh) for f in a):
                    continue
                if any(present(f, coh) for f in (r.get("entity_b_flags") or [])):
                    newly += 1
        if newly:
            unlock[mod] = newly
    for mod in sorted(set(OUTCOME_MODALITY.values())):
        flags = {f for f, m in OUTCOME_MODALITY.items() if m == mod}
        newly = 0
        for r in rules:
            b = set(r.get("entity_b_flags") or [])
            if not (b & flags):
                continue
            for coh in COHORTS:
                if any(present(f, coh) for f in b):
                    continue
                if any(present(f, coh) for f in (r.get("entity_a_flags") or [])):
                    newly += 1
        if newly:
            unlock[f"OUTCOME:{mod}"] = newly

    report = {
        "min_n": MIN_N,
        "possible_cells": total,
        "feasible_cells": feas,
        "feasible_fraction": round(feas / total, 4),
        "blocked_by": by_block,
        "rules_total": len(rules),
        "rules_testable_somewhere": int(df[df.feasible].rule_id.nunique()),
        "unlock_if_modality_added": dict(sorted(unlock.items(),
                                                key=lambda kv: -kv[1])),
        "feasible_pairs": sorted(f"{r}@{c}" for r, c in feasible_pairs),
        "note": ("Cells are (rule x cohort) pairs. Presence is derived from the "
                 "built frames at MIN_N; nothing is listed by hand. blocked_by "
                 "separates a missing exposure from a missing outcome because "
                 "the two imply different investments."),
    }

    cov_path = ROOT / "outputs" / "confirmatory" / "cohort_rule_coverage.json"
    agree = None
    if cov_path.exists():
        cov = json.loads(cov_path.read_text(encoding="utf-8"))
        cov_pairs = {(rid, c) for rid, per in cov["matrix"].items()
                     for c, v in per.items() if v.get("testable")}
        agree = {"audit_feasible": len(feasible_pairs),
                 "coverage_testable": len(cov_pairs),
                 "identical": feasible_pairs == cov_pairs,
                 "only_in_audit": sorted(f"{r}@{c}" for r, c in
                                         feasible_pairs - cov_pairs),
                 "only_in_coverage": sorted(f"{r}@{c}" for r, c in
                                            cov_pairs - feasible_pairs)}
        report["consistency_with_coverage"] = agree

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "evidence_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"possible (rule x cohort) cells : {total}")
    print(f"feasible                       : {feas} ({100*feas/total:.1f}%)")
    print(f"rules testable in >=1 cohort   : "
          f"{report['rules_testable_somewhere']}/{len(rules)}")
    print(f"blocked by                     : {by_block}")
    if agree:
        print(f"agrees with coverage analysis  : {agree['identical']} "
              f"(audit {agree['audit_feasible']} vs coverage "
              f"{agree['coverage_testable']})")
        if not agree["identical"]:
            print(f"   only in audit   : {agree['only_in_audit']}")
            print(f"   only in coverage: {agree['only_in_coverage']}")
    print("\nunlock value of a single added modality (extra rule x cohort cells):")
    for k, v in report["unlock_if_modality_added"].items():
        print(f"   {k:40s} +{v}")

    md = ["# Table 7. Evidence-base audit: what the eight ageing cohorts can and "
          "cannot test", "",
          f"Of {total} possible (rule × cohort) cells, **{feas} "
          f"({100*feas/total:.1f}%)** are feasible. A cell is feasible only when "
          f"both the exposure and the outcome exist in that cohort with at least "
          f"{MIN_N} non-missing observations.", "",
          "| Blocked by | Cells | Share of infeasible |", "|---|---|---|"]
    infeas = total - feas
    for k, v in sorted(by_block.items(), key=lambda kv: -kv[1]):
        md.append(f"| {k} | {v} | {100*v/infeas:.1f}% |")
    md += ["", "## Marginal value of adding one measurement modality", "",
           "| Modality added | Additional rule × cohort cells unlocked |",
           "|---|---|"]
    for k, v in report["unlock_if_modality_added"].items():
        md.append(f"| {k} | +{v} |")
    md += ["",
           "The outcome-side entries are the actionable ones. No cohort in this "
           "layer has fundus imaging, tonometry or optic-disc grading, which is "
           "why the entire retinopathy and diabetic macular oedema family "
           "(r03, r04, r07, r19, r22) and the two glaucoma-measurement rules "
           "(r16) cannot be assessed in any of the eight."]
    (ROOT / "outputs" / "tables" / "table7_evidence_audit.md").write_text(
        "\n".join(md), encoding="utf-8")
    print(f"\n-> {OUT/'evidence_audit.json'}")
    print("-> outputs/tables/table7_evidence_audit.md")
    return 0 if (agree is None or agree["identical"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
