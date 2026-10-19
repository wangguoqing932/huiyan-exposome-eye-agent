#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebuild every table to one shape, and make Table 1 say what its title promises.

DEFECTS FOUND BY INSPECTION
---------------------------
1. Table 1's title promised "cohorts analysed ... sources, participants and the
   reason each is in the layer", but its body was a variable registry
   (entity_a 41 / entity_b 15) -- a different table entirely. It was also the
   only table using CRLF line endings.
2. Tables 1, 2, 3 and 7 carried BLANK LINES BETWEEN ROWS. That is valid
   GitHub-flavoured markdown only by tolerance; many renderers and most
   journal-conversion pipelines read each blank-separated block as its own
   table, so the table silently splits. The tables looked right in a preview and
   were structurally wrong.
3. Structure was inconsistent: tables 4-7 had a lead-in paragraph before the
   table and 1-3 did not.

WHAT THIS DOES
--------------
Every table is written in one shape: title, optional lead-in, contiguous table
rows with no interior blank lines, LF endings, then footnotes. Table 1 is
rebuilt from the cohort frames as the table its title claims -- per-cohort
source, unique participants, unique person-waves, waves, and why the cohort is
in the layer -- which is also the participant accounting that the manuscript was
missing.

Run: python scripts/rebuild_all_tables.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "outputs" / "tables"
FRAMES = ROOT / "data" / "frames"

SOURCE = {
    "SHARE": "Survey of Health, Ageing and Retirement in Europe",
    "HRS": "Health and Retirement Study",
    "ELSA": "English Longitudinal Study of Ageing",
    "KLoSA": "Korean Longitudinal Study of Ageing",
    "LASI": "Longitudinal Ageing Study in India",
    "MHAS": "Mexican Health and Aging Study",
    "CLHLS": "Chinese Longitudinal Healthy Longevity Survey",
    "CRELES": "Costa Rican Study on Longevity and Healthy Ageing",
}
CUT = {"SHARE": 30, "HRS": 30, "ELSA": 30, "KLoSA": 25, "LASI": 25,
       "MHAS": 30, "CLHLS": 25, "CRELES": 30}
REASON = {
    "SHARE": "Largest contributor; supplies r02, r10, r12, r13, r20",
    "HRS": "Supplies r02, r10, r20",
    "ELSA": "Only source of an AMD item; supplies r10, r11, r20",
    "KLoSA": "Supplies r10, r20",
    "LASI": "Supplies r02 only; r13 untestable (no BMI)",
    "MHAS": "Contributes no testable pair (exposures and outcomes do not co-occur)",
    "CLHLS": "Supplies r02, r10, r12, r20",
    "CRELES": "Supplies r02, r10, r13",
}


def cohort_stats() -> list[dict]:
    cov = json.loads((ROOT / "outputs" / "confirmatory" /
                      "cohort_rule_coverage.json").read_text(encoding="utf-8"))
    rows = []
    for c in SOURCE:
        d = pd.read_csv(FRAMES / f"cohort_{c}.csv", low_memory=False,
                        usecols=lambda x: x in ("mergeid", "wave", "implicat"))
        if "implicat" in d.columns and d["implicat"].nunique() > 1:
            d = d[d["implicat"] == d["implicat"].min()]
        key = ["mergeid"] + (["wave"] if "wave" in d.columns else [])
        n_wave = d[key].drop_duplicates().shape[0]
        n_person = d["mergeid"].nunique()
        waves = d["wave"].nunique() if "wave" in d.columns else 1
        rows.append({"cohort": c, "source": SOURCE[c], "persons": n_person,
                     "person_waves": n_wave, "waves": waves,
                     "bmi_cut": CUT[c], "reason": REASON[c]})
    return rows


def write(name: str, title: str, lead: str, header: list[str],
          body: list[list[str]], notes: list[str]) -> None:
    lines = [f"# {title}", ""]
    if lead:
        lines += [lead, ""]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in body:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    if notes:
        lines += [""] + [f"* {n}" for n in notes]
    (T / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    st = cohort_stats()
    body = [[r["cohort"], f"{r['persons']:,}", f"{r['person_waves']:,}",
             r["waves"], r["bmi_cut"], r["reason"]] for r in st]
    write("table1_registry.md",
          "Table 1. Cohorts, participants and person-waves in the "
          "external-validation layer",
          "Participants are counted once per cohort. Person-waves count each "
          "person once per wave; SHARE's five imputation replicates are "
          "combined to a single record per person-wave, so the person-wave "
          "column is the analysed unit and not the raw row count.",
          ["Cohort", "Participants", "Person-waves", "Waves",
           "BMI cut-point (kg/m²)", "Why the cohort is in the layer"],
          body,
          [f"**Total: {sum(r['persons'] for r in st):,} participants and "
           f"{sum(r['person_waves'] for r in st):,} person-waves across "
           f"{len(st)} cohorts.**",
           "The BMI cut-point is 25 kg/m² for the Asian cohorts and 30 kg/m² "
           "otherwise, fixed by the prevalence gate before the confirmatory "
           "analysis and reported per cohort because it changes what the "
           "adiposity rule tests.",
           "MHAS is retained in the table even though it contributes no "
           "testable pair. Excluding a cohort that was analysed, because it "
           "turned out to be uninformative, would hide the reason the "
           "transportability figure shows fewer cohorts than the layer "
           "contains."])

    # strip interior blank lines and normalise endings on the remaining tables
    for p in sorted(T.glob("table*.md")):
        if p.name == "table1_registry.md":
            continue
        raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
        lines = raw.split("\n")
        idx = [i for i, l in enumerate(lines) if l.startswith("|")]
        if idx:
            a, b = idx[0], idx[-1]
            block = [l for l in lines[a:b + 1] if l.strip()]
            lines = lines[:a] + block + lines[b + 1:]
        p.write_text("\n".join(lines), encoding="utf-8")

    print("Table 1 rebuilt from the frames; interior blank lines stripped "
          "from the others")
    for p in sorted(T.glob("table*.md")):
        t = p.read_text(encoding="utf-8")
        n = sum(1 for l in t.split("\n")
                if l.startswith("|"))
        blanks = 0
        idx = [i for i, l in enumerate(t.split("\n")) if l.startswith("|")]
        if idx:
            ls = t.split("\n")
            blanks = sum(1 for i in range(idx[0], idx[-1]) if not ls[i].strip())
        print(f"  {p.name:30s} 表行={n:>3}  表内空行={blanks}  "
              f"CRLF={'是' if chr(13) in t else '否'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
