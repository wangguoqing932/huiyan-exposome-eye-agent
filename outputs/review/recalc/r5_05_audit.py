#!/usr/bin/env python
"""R5 independent recalculation -- step 5: evidence-base audit counts.

INDEPENDENT REWRITE of scripts/evidence_base_audit.py. Presence of every flag is
re-derived from the raw frames at MIN_N non-missing values; the rule definitions
(entity_a_flags / entity_b_flags) are read from configs/rules.yaml because they
ARE the pre-registered rule base and cannot be altered.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "review" / "recalc"
MIN_N = 200
COHORTS = ["SHARE", "HRS", "ELSA", "KLoSA", "LASI", "MHAS", "CLHLS", "CRELES"]

EXPOSURE_MODALITY = {
    "current_smoking": "questionnaire_behaviour",
    "alcohol_intake": "questionnaire_behaviour",
    "bmi_high": "anthropometry",
    "hyperglycemia": "selfreport_or_assay_metabolic",
    "hba1c_elevated": "blood_assay", "dyslipidemia": "blood_assay",
    "crp_elevated": "blood_assay", "vitamin_d_deficiency": "blood_assay",
    "uric_acid_elevated": "blood_assay", "lead_exposure": "blood_assay",
    "low_antioxidant_intake": "dietary_index",
    "mediterranean_diet": "dietary_index",
    "pro_inflammatory_diet": "dietary_index",
    "pm25_exposure": "geocoded_environment", "uv_exposure": "geocoded_environment",
}
OUTCOME_MODALITY = {
    "cataract_any": "selfreport_ocular_diagnosis",
    "glaucoma_selfreport": "selfreport_ocular_diagnosis",
    "vision_impairment_moderate": "vision_rating",
    "vision_impairment_severe": "vision_rating",
    "amd_late": "fundus_imaging_or_grading", "amd_early": "fundus_imaging_or_grading",
    "retinopathy_any": "fundus_imaging", "dr_npdr": "fundus_imaging",
    "dr_pdr": "fundus_imaging", "glaucoma_iop_elevated": "tonometry",
    "glaucoma_suspect_cdr": "optic_disc_grading",
}
FLAG_TO_COLUMNS = {
    "current_smoking": ["current_smoking"], "alcohol_intake": ["alcohol_intake"],
    "bmi_high": ["bmi_high_25", "bmi_high_30"], "hyperglycemia": ["diabetes"],
    "cataract_any": ["cataract_any"], "glaucoma_selfreport": ["glaucoma_selfreport"],
    "vision_impairment_moderate": ["vision_impairment_moderate"],
    "vision_impairment_severe": ["vision_impairment_severe"],
    "amd_late": ["amd_any", "amd_late"], "amd_early": ["amd_any", "amd_early"],
}
# everything else resolves to an empty candidate list (absent by construction)
for f in (EXPOSURE_MODALITY | OUTCOME_MODALITY):
    FLAG_TO_COLUMNS.setdefault(f, [])

rules = yaml.safe_load((ROOT / "configs" / "rules.yaml")
                       .read_text(encoding="utf-8"))["rules"]
print(f"rules in configs/rules.yaml: {len(rules)}")

nonmiss: dict[str, dict[str, int]] = {}
for coh in COHORTS:
    dd = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False)
    nonmiss[coh] = {c: int(pd.to_numeric(dd[c], errors="coerce").notna().sum())
                    for c in dd.columns}


def present(flag, coh):
    return any(nonmiss.get(coh, {}).get(col, 0) >= MIN_N
               for col in FLAG_TO_COLUMNS.get(flag, []))


cells = []
for r in rules:
    for coh in COHORTS:
        a = list(r.get("entity_a_flags") or [])
        b = list(r.get("entity_b_flags") or [])
        a_ok = any(present(f, coh) for f in a)
        b_ok = any(present(f, coh) for f in b)
        blocked = ("none" if (a_ok and b_ok) else
                   "both_sides" if (not a_ok and not b_ok) else
                   "exposure_missing" if not a_ok else "outcome_missing")
        cells.append({"rule": r["id"], "cohort": coh, "feasible": a_ok and b_ok,
                      "blocked_by": blocked})
df = pd.DataFrame(cells)
total, feas = len(df), int(df.feasible.sum())
by_block = {k: int(v) for k, v in
            df[~df.feasible].blocked_by.value_counts().items()}
feasible_pairs = set(zip(df[df.feasible]["rule"], df[df.feasible]["cohort"]))

unlock = {}
for mod in sorted(set(EXPOSURE_MODALITY.values())):
    flags = {f for f, m in EXPOSURE_MODALITY.items() if m == mod}
    n = 0
    for r in rules:
        a = set(r.get("entity_a_flags") or [])
        if not (a & flags):
            continue
        for coh in COHORTS:
            if any(present(f, coh) for f in a):
                continue
            if any(present(f, coh) for f in (r.get("entity_b_flags") or [])):
                n += 1
    if n:
        unlock[mod] = n
for mod in sorted(set(OUTCOME_MODALITY.values())):
    flags = {f for f, m in OUTCOME_MODALITY.items() if m == mod}
    n = 0
    for r in rules:
        b = set(r.get("entity_b_flags") or [])
        if not (b & flags):
            continue
        for coh in COHORTS:
            if any(present(f, coh) for f in b):
                continue
            if any(present(f, coh) for f in (r.get("entity_a_flags") or [])):
                n += 1
    if n:
        unlock[f"OUTCOME:{mod}"] = n

rep = {"possible_cells": total, "feasible_cells": feas,
       "feasible_fraction": round(feas / total, 4),
       "blocked_by": by_block,
       "rules_total": len(rules),
       "rules_testable_somewhere": int(df[df.feasible]["rule"].nunique()),
       "unlock_if_modality_added": dict(sorted(unlock.items(),
                                               key=lambda kv: -kv[1])),
       "feasible_pairs": sorted(f"{r}@{c}" for r, c in feasible_pairs)}
(OUT / "recalc_evidence_audit.json").write_text(
    json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"possible cells        : {total}")
print(f"feasible cells        : {feas} ({100*feas/total:.1f}%)")
print(f"blocked_by            : {by_block}  (sum {sum(by_block.values())})")
print(f"rules testable >=1    : {rep['rules_testable_somewhere']}")
print("unlock ranking:")
for k, v in rep["unlock_if_modality_added"].items():
    print(f"   {k:42s} +{v}")
