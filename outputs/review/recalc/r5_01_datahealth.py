#!/usr/bin/env python
"""R5 independent statistical recalculation -- step 1: data health check.

Independent rewrite. Reads ONLY the raw cohort frames and the methods/results
text; does not import or call any project script.

Output: recalc_datahealth.csv / .json  (+ console)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "review" / "recalc"
OUT.mkdir(parents=True, exist_ok=True)

# paper-stated person-wave record counts (methods.md line 46-47)
PAPER_ROWS = {"SHARE": 1693515, "MHAS": 78537, "LASI": 73408, "CLHLS": 72744,
              "HRS": 42946, "KLoSA": 40406, "ELSA": 9771, "CRELES": 5191}
# paper-stated unique persons (analysis_plan 19.3)
PAPER_PERSONS = {"SHARE": 137183, "HRS": 27261, "KLoSA": 11137, "LASI": 73408,
                 "MHAS": 15199, "CLHLS": 9093, "ELSA": 9771, "CRELES": 2827}

rows = []
detail = {}
for path in sorted(FRAMES.glob("cohort_*.csv")):
    coh = path.stem.replace("cohort_", "")
    d = pd.read_csv(path, low_memory=False)
    n = len(d)
    n_person = int(d["mergeid"].nunique())
    waves = sorted(pd.to_numeric(d["wave"], errors="coerce").dropna().unique().tolist())
    imp = (sorted(pd.to_numeric(d["implicat"], errors="coerce").dropna()
                  .unique().tolist()) if "implicat" in d.columns else [])
    rec = {
        "cohort": coh, "rows_actual": n, "rows_paper": PAPER_ROWS.get(coh),
        "rows_diff": n - PAPER_ROWS.get(coh, np.nan),
        "persons_actual": n_person, "persons_paper": PAPER_PERSONS.get(coh),
        "persons_diff": n_person - PAPER_PERSONS.get(coh, np.nan),
        "n_waves": len(waves), "waves": ",".join(str(int(w)) for w in waves),
        "implicat_values": ",".join(str(int(i)) for i in imp) or "none",
        "n_implicates": len(imp),
        "dup_mergeid_wave": int(n - d.drop_duplicates(["mergeid", "wave"]).shape[0]),
        "age_mean": round(float(pd.to_numeric(d["age"], errors="coerce").mean()), 2),
        "age_missing_pct": round(100 * float(d["age"].isna().mean()), 2),
        "sex_missing_pct": round(100 * float(d["sex"].isna().mean()), 2),
    }
    # key flag prevalences (replicate 1 only, so an implicate is not a person)
    d1 = d[d["implicat"] == imp[0]] if imp else d
    d1 = d1.drop_duplicates(["mergeid", "wave"])
    for c in ("current_smoking", "alcohol_intake", "diabetes", "bmi_high_25",
              "bmi_high_30", "cataract_any", "glaucoma_selfreport",
              "vision_impairment_moderate", "vision_impairment_severe",
              "amd_any", "blindness_selfreport"):
        if c in d.columns:
            v = pd.to_numeric(d1[c], errors="coerce")
            rec[f"p_{c}"] = round(100 * float(v.mean()), 2)
            rec[f"nmiss_{c}"] = int(v.isna().sum())
            rec[f"ctype_{c}"] = str(d[c].dtype)
    rows.append(rec)

df = pd.DataFrame(rows)
df.to_csv(OUT / "recalc_datahealth.csv", index=False, encoding="utf-8")
detail["n_rows_table"] = rows
detail["total_rows_actual"] = int(df["rows_actual"].sum())
detail["total_rows_paper"] = int(sum(PAPER_ROWS.values()))
(OUT / "recalc_datahealth.json").write_text(
    json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

pd.set_option("display.width", 250)
print(df[["cohort", "rows_actual", "rows_paper", "rows_diff", "persons_actual",
          "persons_paper", "persons_diff", "n_waves", "implicat_values",
          "dup_mergeid_wave", "age_mean"]].to_string(index=False))
print()
print(df[["cohort", "p_current_smoking", "p_diabetes", "p_cataract_any",
          "p_vision_impairment_moderate", "p_amd_any"]].to_string(index=False))
print()
print(df[["cohort", "ctype_current_smoking", "ctype_diabetes",
          "ctype_cataract_any"]].to_string(index=False))
print()
print("total rows actual:", int(df.rows_actual.sum()),
      " paper sum:", int(sum(PAPER_ROWS.values())))
