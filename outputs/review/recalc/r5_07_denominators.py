#!/usr/bin/env python
"""R5 independent recalculation -- step 7: denominators, BHY, three-state.

* person-wave reconciliation across the eight frames (the paper's "2.0 million
  person-wave records");
* duplicate-row structure per frame;
* which waves survive complete-case adjustment (covariates age/sex/wave);
* Benjamini-Yekutieli over MY 18 confirmatory p-values, compared with the
  project's q_rule and the resulting three-state.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "review" / "recalc"
COHORTS = ["SHARE", "HRS", "ELSA", "KLoSA", "LASI", "MHAS", "CLHLS", "CRELES"]


def bhy(p):
    p = pd.Series(p, dtype=float)
    n = len(p)
    order = p.sort_values(kind="mergesort")
    cn = float(np.sum(1.0 / np.arange(1, n + 1)))
    r = order.to_numpy() * n * cn / np.arange(1, n + 1)
    r = np.minimum.accumulate(r[::-1])[::-1]
    q = pd.Series(np.nan, index=p.index)
    q.loc[order.index] = np.clip(r, 0, 1)
    return q


# ---------------- person-wave reconciliation --------------------------------
rec = []
for coh in COHORTS:
    d = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False)
    imp = sorted(d["implicat"].dropna().unique()) if "implicat" in d.columns else []
    n_imp = len(imp)
    pw = int(d.drop_duplicates(["mergeid", "wave"]).shape[0])
    dup = len(d) - pw
    rec.append({"cohort": coh, "rows": len(d), "n_implicates": n_imp,
                "unique_person_wave": pw,
                "distinct_person_wave_after_collapsing_implicates": pw // max(n_imp, 1),
                "duplicate_rows": dup,
                "pct_duplicate": round(100 * dup / len(d), 1)})
rdf = pd.DataFrame(rec)
rdf.to_csv(OUT / "recalc_personwave.csv", index=False, encoding="utf-8")
print("=== PERSON-WAVE RECONCILIATION ===")
print(rdf.to_string(index=False))
true_pw = int(rdf.distinct_person_wave_after_collapsing_implicates.sum())
print(f"\nrows counted by the paper as 'person-wave records' : "
      f"{int(rdf['rows'].sum()):,}")
print(f"distinct person-wave observations (implicates      : "
      f"{true_pw:,}")
print(f"collapsed, duplicates removed)                     "
      f"  -> inflation factor {rdf['rows'].sum()/true_pw:.2f}x")

# ---------------- which waves survive complete-case -------------------------
print("\n=== WAVE COVERAGE AFTER COMPLETE-CASE ON age/sex/wave ===")
wav = []
for coh in COHORTS:
    d = pd.read_csv(FRAMES / f"cohort_{coh}.csv", low_memory=False)
    if "implicat" in d.columns and d["implicat"].nunique() > 1:
        d = d[d["implicat"] == d["implicat"].min()]
    for w, g in d.groupby("wave"):
        wav.append({"cohort": coh, "wave": w, "rows": len(g),
                    "age_nonmiss": int(pd.to_numeric(g["age"],
                                                     errors="coerce").notna().sum()),
                    "sex_nonmiss": int(pd.to_numeric(g["sex"],
                                                     errors="coerce").notna().sum())})
wdf = pd.DataFrame(wav)
wdf["age_ok"] = wdf.age_nonmiss >= 200
print(wdf.to_string(index=False))
lost = wdf[~wdf.age_ok]
print("\nWAVES LOST TO COMPLETE-CASE ON age/sex:")
print(lost.to_string(index=False) if len(lost) else "  none")
wdf.to_csv(OUT / "recalc_waves.csv", index=False, encoding="utf-8")

# ---------------- BHY over my 18 confirmatory p-values ---------------------
fits = []
for p in sorted(OUT.glob("recalc_fit_*.json")):
    for r in json.loads(p.read_text(encoding="utf-8"))["results"]:
        if r.get("status") == "ok":
            fits.append(r)
mine = pd.DataFrame(fits)[["rule_id", "cohort", "odds_ratio", "p_two_sided"]]
mine = mine.sort_values(["rule_id", "cohort"]).reset_index(drop=True)
mine["q_BHY_confirmatory"] = bhy(mine["p_two_sided"].to_numpy())
mine["three_state"] = np.where(
    mine.q_BHY_confirmatory >= 0.05, "uninformative",
    np.where(mine.odds_ratio < 1, "contradicted", "replicated"))
mine.to_csv(OUT / "recalc_three_state.csv", index=False, encoding="utf-8")
print("\n=== THREE-STATE FROM MY OWN 18 p-VALUES (BHY over the "
      "confirmatory family) ===")
print(mine.to_string(index=False))
print("\ncounts:", mine.three_state.value_counts().to_dict())

# ---------------- compare with the project's own table ---------------------
proj = pd.read_csv(ROOT / "outputs" / "cohorts" / "cohort_rule_results.csv")
proj = proj[proj.rule_relevant.astype(bool)][
    ["rule_id", "cohort", "odds_ratio", "q_rule", "three_state", "n"]]
j = mine.merge(proj, on=["rule_id", "cohort"], how="outer",
               suffixes=("_mine", "_project"))
j["d_OR"] = (j.odds_ratio_mine - j.odds_ratio_project).round(6)
j["state_agree"] = j.three_state_mine == j.three_state_project
j.to_csv(OUT / "recalc_vs_project.csv", index=False, encoding="utf-8")
print("\n=== MY VALUES vs THE PROJECT'S OWN TABLE ===")
print(j[["rule_id", "cohort", "odds_ratio_mine", "odds_ratio_project", "d_OR",
         "q_rule", "q_BHY_confirmatory", "three_state_mine", "three_state_project",
         "state_agree"]].to_string(index=False))
print("\nmax |dOR| =", float(j.d_OR.abs().max()))
print("three-state agreement:", bool(j.state_agree.all()))
