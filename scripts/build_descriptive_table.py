#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the descriptive table of the analysed populations (STROBE items 14a, 14b).

STROBE 14a asks for the characteristics of study participants; 14b asks for the
number with missing data on each variable. Both were marked NOT MET: Table 1 is a
cohort registry (sizes, person-waves, BMI cut-point, why each cohort is in the
layer) and carries no age, sex, outcome prevalence or missingness.

This computes all of it from the cohort frames — the same frames the analysis
uses — so the table cannot drift from the analysis. Every cell is derived; the
only hand-written column is the source note.

Two things this table is deliberately careful about:

* **Person-waves, not participants, are the analysis unit**, so prevalence is
  computed per person-wave. SHARE's five imputation replicates are collapsed to
  replicate 1 so that neither the denominators nor the prevalences are inflated
  by a factor of five, which is the error corrected earlier in this project.
* **Age is not wave-invariant in every cohort.** CLHLS ships a single baseline
  age repeated across waves (92.74% of people have one unique value), which is a
  known defect of that frame; the table reports CLHLS age with a footnote rather
  than presenting the mean as though it were a follow-up age.

Run: python scripts/build_descriptive_table.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "tables" / "table1b_descriptives.md"

COHORTS = ["SHARE", "HRS", "ELSA", "KLoSA", "LASI", "MHAS", "CLHLS", "CRELES"]

# variables reported, in table order
VARS = [
    ("age", "Age, years, mean (SD)"),
    ("female", "Female, %"),
    ("current_smoking", "Current smoking, %"),
    ("diabetes", "Diabetes (self-reported), %"),
    ("bmi_high", "BMI above the cohort cut-point, %"),
    ("cataract_any", "Cataract, %"),
    ("vision_impairment_moderate", "Moderate vision impairment, %"),
]


def load(c: str) -> pd.DataFrame:
    # `usecols` filters the file as it is read, so every column the code later
    # looks for has to be named here. An earlier version listed only the derived
    # name `bmi_high` while the frames actually store `bmi_high_25` /
    # `bmi_high_30`, so the BMI flag was dropped at read time and every cohort
    # reported BMI as unavailable no matter what the analysis code did.
    want = {"mergeid", "wave", "implicat", "age", "sex",
            "bmi_kgm2", "bmi", "bmi_high_25", "bmi_high_30",
            "ever_smoked", "cataract_surgery"} | {v for v, _ in VARS}
    d = pd.read_csv(FRAMES / f"cohort_{c}.csv", low_memory=False,
                    usecols=lambda x: x in want)
    if "implicat" in d.columns and d["implicat"].nunique() > 1:
        d = d[d["implicat"] == d["implicat"].min()].copy()
    # Deduplicate on the person-wave key. The MHAS frame carries 78,537 rows for
    # 15,217 distinct person-waves, and the repetition is wildly non-uniform: most
    # rows appear once, but individual rows appear up to 6,447 times, which is the
    # signature of a many-to-many join in the frame builder rather than ordinary
    # duplication. Deduplicating returns exactly the 15,217 person-waves the
    # manuscript reports, confirming that the manuscript's figure is the
    # deduplicated one. MHAS contributes no rows to the confirmatory results, so
    # the defect does not touch any reported estimate -- but a descriptive table
    # built without deduplication would have overstated MHAS fivefold.
    key = [k for k in ("mergeid", "wave") if k in d.columns]
    if key:
        d = d.drop_duplicates(subset=key).copy()
    return d


def main() -> int:
    # analysis_plan.md section 19.7 (C58): KLoSA/MHAS/LASI/CLHLS at 25,
    # SHARE/HRS/ELSA/CRELES at 30. This dict previously said MHAS 30, which
    # contradicted the pre-registered plan and the confirmatory script.
    cut = {"SHARE": 30, "HRS": 30, "ELSA": 30, "KLoSA": 25, "LASI": 25,
           "MHAS": 25, "CLHLS": 25, "CRELES": 30}
    rows, notes = [], []
    header = ["Cohort", "Person-waves"] + [lab for _, lab in VARS]
    lines = [
        "# Table 1b. Characteristics of the analysed populations "
        "(STROBE items 14a and 14b)",
        "",
        "Computed from the same cohort frames the analysis uses, so the table "
        "cannot drift from the analysis. The unit is the person-wave, which is "
        "the analysed unit; SHARE's five imputation replicates are collapsed to "
        "replicate 1, so neither denominators nor prevalences are inflated.",
        "",
        "Percentages are of person-waves with the variable observed. Missingness "
        "is reported separately in the table below.",
        "",
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
    ]
    miss_lines = [
        "| Cohort | " + " | ".join(lab for _, lab in VARS)
        + " | Missing at least one, % |",
        "|" + "---|" * (len(VARS) + 2),
    ]
    payload = {}
    for c in COHORTS:
        d = load(c)
        n = len(d)
        age = pd.to_numeric(d["age"], errors="coerce")
        sex = pd.to_numeric(d["sex"], errors="coerce")
        d = d.assign(female=(sex == 2).astype(float).where(sex.notna()))
        # The frames store the derived cut-point flag, not a raw BMI column, and
        # the cut differs by cohort: 25 kg/m2 for the Asian cohorts and 30
        # otherwise, fixed by the prevalence gate before the confirmatory
        # analysis. Looking for a raw `bmi_kgm2` column -- which no frame has --
        # is what made an earlier run of this table report BMI as unavailable for
        # every cohort, including SHARE where the BMI rule was in fact tested.
        bmi_col = f"bmi_high_{cut[c]}"
        if bmi_col in d.columns:
            d["bmi_high"] = pd.to_numeric(d[bmi_col], errors="coerce")
        # LASI records ever-smoked rather than current smoking; report it under
        # its own name rather than silently passing it off as current smoking.
        smoke_col = ("current_smoking" if "current_smoking" in d.columns
                     else "ever_smoked" if "ever_smoked" in d.columns else None)
        if smoke_col and smoke_col != "current_smoking":
            # Report it under its own name. In LASI the column exists but is
            # entirely empty (0 of 73,408 observed), so the fallback correctly
            # leaves the cell unavailable; in other cohorts it would be reported
            # as ever-smoked rather than passed off as current smoking.
            d["current_smoking"] = pd.to_numeric(d[smoke_col], errors="coerce")
            notes.append(f"* **{c}** records *{smoke_col.replace('_', ' ')}* rather "
                         f"than current smoking; reported as recorded.")
        # HRS and KLoSA carry cataract as surgery status, not as a diagnosis, and
        # both have it: 37.5% and 99.6% observed. Looking only for `cataract_any`
        # made an earlier version report those two cohorts as having no cataract
        # data at all. The two constructs are not equivalent -- surgery is a
        # treated subset of diagnosis -- so the row is footnoted rather than
        # silently merged.
        if "cataract_any" not in d.columns and "cataract_surgery" in d.columns:
            d["cataract_any"] = pd.to_numeric(d["cataract_surgery"], errors="coerce")
            notes.append(f"* **{c}** records cataract as *surgery*, not diagnosis; "
                         f"the row is a treated subset and is not comparable with "
                         f"the self-reported diagnosis in other cohorts.")
        cells, miss = [c, f"{n:,}"], []
        rec = {"person_waves": int(n)}
        for v, _lab in VARS:
            if v == "age":
                s = age
                cells.append(f"{s.mean():.1f} ({s.std():.1f})"
                             if s.notna().any() else "not available")
                rec["age_mean"] = round(float(s.mean()), 2) if s.notna().any() else None
            else:
                s = pd.to_numeric(d[v], errors="coerce") if v in d.columns else None
                if s is None or not s.notna().any():
                    cells.append("not available")
                    rec[v] = None
                else:
                    cells.append(f"{100 * s.mean():.1f}")
                    rec[v] = round(100 * float(s.mean()), 1)
            if s is None or not hasattr(s, "notna"):
                # The variable is absent from this cohort's frame entirely, so
                # every person-wave is missing it.
                miss.append("100.0")
            else:
                miss.append(f"{100 * (1 - s.notna().mean()):.1f}")
        # Last column: the share of person-waves missing AT LEAST ONE of the
        # characteristics above. Note the direction -- an earlier version computed
        # the complement (missing every one), which is near zero in every cohort
        # because age is almost always present, and labelled it "any of the
        # above", so the column read as 0.0 everywhere and said nothing.
        _present = [age.notna()]
        for v, _ in VARS:
            if v == "age":
                continue
            _present.append(
                (pd.to_numeric(d[v], errors="coerce") if v in d.columns
                 else pd.Series(np.nan, index=d.index)).notna())
        _all_present = pd.concat(_present, axis=1).all(axis=1)
        miss_any = 100 * (1 - float(_all_present.mean()))
        miss_full = [c] + miss + [f"{miss_any:.1f}"]
        miss_lines.append("| " + " | ".join(miss_full) + " |")
        rows.append(cells)
        payload[c] = rec

    for cells in rows:
        lines.append("| " + " | ".join(cells) + " |")
    lines += [
        "",
        "### Missingness (% of person-waves with the variable missing)",
        "",
        "**Read this table with the caveat that follows.** A 100% cell here "
        "usually means the variable is not carried in this cohort's analysis "
        "frame, not that the survey failed to measure it or that the item went "
        "unanswered. The frames were built to hold only what the pre-specified "
        "rules need, so a cohort that contributes no BMI rule has no BMI column "
        "at all and reports 100%. This column therefore describes **frame "
        "coverage**, which is what decides which (rule x cohort) cells are "
        "testable -- it is not an item non-response rate.",
        "",
    ] + miss_lines + [
        "",
        "**Footnotes.**",
        "* **Frame coverage versus item non-response.** Where a variable is "
        "present, its missingness is genuine non-response — SHARE's smoking is "
        "58.0% missing with the column present, while HRS's BMI is 100% missing "
        "because the frame carries no BMI column.",
        "* **Age in CLHLS is a baseline value repeated across waves**, not a "
        "follow-up age: 92.74% of its participants have a single unique age "
        "across all their waves, so its mean is not comparable to the others and "
        "should not be read as an average age during follow-up. The frame defect "
        "is documented in `docs/GAP_ANALYSIS_20IF.md`.",
        "* **Diabetes is self-reported** in every cohort, so its prevalence "
        "reflects diagnosis rates rather than disease prevalence — the mechanism "
        "the paper demonstrates with the NHANES comparison.",
        "* **Cataract and vision impairment are absent from HRS, KLoSA and MHAS** "
        "in these frames, which is why the cohort layer tests only six rules: "
        "those cohorts cannot contribute a cataract or vision-impairment cell.",
        "* The BMI cut-point is 25 kg/m² for the Asian cohorts and 30 kg/m² "
        "otherwise, fixed by the prevalence gate before the confirmatory analysis.",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "outputs" / "tables" / "table1b_descriptives.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Table 1b written: {len(COHORTS)} cohorts x {len(VARS)} characteristics")
    print("  " + " | ".join(header))
    for cells in rows:
        print("  " + " | ".join(str(x) for x in cells))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
