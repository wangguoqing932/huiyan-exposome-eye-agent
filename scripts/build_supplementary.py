#!/usr/bin/env python
"""Assemble the supplementary material file (writer 7_9 checklist item).

WHY THIS RATHER THAN MORE WORD-SHAVING
--------------------------------------
The manuscript body is 6,167 words. The target journal's limit is UNKNOWN: all
three official sources for Ophthalmology returned HTTP 403 and the local
checklist has no entry for it (see journal_guidelines_snapshot.md). Cutting prose
towards a guessed limit risks removing science while still breaching the real
cap.

Moving detail into supplementary material is the opposite trade: it is required
by the submission checklist regardless of the cap, it protects the argument, and
it is where a 10+ IF journal expects the reproducibility detail to live. Every
file assembled here is a generated artefact with a source script, so a reviewer
can reproduce it.

Run: python scripts/build_supplementary.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUB = ROOT / "outputs" / "submission"
CO = ROOT / "outputs" / "cohorts"
TAB = ROOT / "outputs" / "tables"

# (heading, source file, why it is supplementary rather than main text)
ITEMS = [
    ("S1. Variable operationalisation and quality-control log",
     ROOT / "docs" / "cohort_variable_mapping.md",
     "Per-cohort variable maps and every correction applied to them (C19-C69). "
     "The main text states the three blocking QC rules and the construct "
     "shifts; the per-variable evidence belongs here for reproducibility."),
    ("S2. Per-pair statistical power in the cohort layer",
     TAB / "table6_power.md",
     "Eighteen rows of n, exposure prevalence, outcome prevalence and MDE-OR. "
     "The main text reports the median range and the powered-null count."),
    ("S3. Between-cohort heterogeneity, full output",
     CO / "cohort_heterogeneity.json",
     "Per-rule REML tau^2, I^2, Cochran Q, prediction intervals, regional "
     "subgroup tests, meta-regression on mean age, and E-values, verbatim."),
    ("S4. Leave-one-cohort-out influence analysis",
     CO / "cohort_influence.csv",
     "Every rule x dropped-cohort refit, showing the directional conflict is "
     "not produced by any single cohort."),
    ("S5. Measurement-modality evidence audit, full output",
     CO / "evidence_audit.json",
     "The 168-cell feasibility matrix, the blocked-by decomposition and the "
     "unlock ranking. Main text reports the totals and the top three."),
    ("S6. Rule-coverage measurement",
     ROOT / "outputs" / "confirmatory" / "cohort_rule_coverage.json",
     "The measured testable (rule, cohort) pairs with the column, n and flag "
     "used for each side, so the coverage claim is auditable."),
    ("S7. Verified citation pool",
     ROOT / "outputs" / "paper" / "citation_pool.json",
     "The verified citation pool (all entries) with DOI, cross-verification "
     "source, retraction status and the claim each supports."),
    ("S8. Figure source data",
     ROOT / "outputs" / "figures" / "source_data" / "figure8_cohort_transportability.csv",
     "The single CSV behind Figure 8, so every plotted value is traceable."),
]


def main() -> int:
    SUB.mkdir(parents=True, exist_ok=True)
    parts = [
        "# Supplementary Material",
        "",
        "**Even age does not transport: a pooled multi-cohort exposome estimate "
        "describes no population, in 285,878 participants and 21 "
        "literature-derived rules**",
        "",
        f"Assembled {date.today()}. Every item below is a generated artefact; "
        "the script that produces it is named so the analysis can be "
        "reproduced.",
        "",
        "| Item | Contents | Produced by |",
        "|---|---|---|",
    ]
    body = []
    manifest = []
    for heading, path, why in ITEMS:
        if not path.exists():
            manifest.append({"item": heading, "status": "MISSING",
                             "path": str(path.relative_to(ROOT))})
            continue
        gen = {
            "S1": "docs/cohort_variable_mapping.md (hand-maintained ledger)",
            "S2": "scripts/cohort_power.py",
            "S3": "scripts/cohort_heterogeneity.py",
            "S4": "scripts/cohort_heterogeneity.py",
            "S5": "scripts/evidence_base_audit.py",
            "S6": "scripts/cohort_rule_coverage.py",
            "S7": "scripts/build_citation_pool.py, scripts/extend_citation_pool_intro.py",
            "S8": "scripts/build_source_data_cohort.py",
        }.get(heading[:2], "--")
        parts.append(f"| {heading.split('.')[0]} | {heading.split('. ', 1)[1]} "
                     f"| `{gen}` |")
        body += ["", f"## {heading}", "", f"*Why supplementary:* {why}", "",
                 "```"]
        txt = path.read_text(encoding="utf-8")
        if len(txt) > 60000:
            body.append(txt[:60000])
            body.append(f"... [truncated in this assembly; full file is "
                        f"{len(txt):,} bytes at outputs/"
                        f"{path.relative_to(ROOT / 'outputs')}]")
        else:
            body.append(txt.rstrip())
        body += ["```", ""]
        manifest.append({"item": heading, "status": "included",
                         "path": str(path.relative_to(ROOT)),
                         "bytes": path.stat().st_size, "produced_by": gen})

    out = SUB / "supplementary_material.md"
    out.write_text("\n".join(parts + body).rstrip() + "\n", encoding="utf-8")
    (SUB / "supplementary_manifest.json").write_text(
        json.dumps({"assembled_on": str(date.today()), "items": manifest,
                    "note": ("supplementary item S1 is a hand-maintained ledger "
                             "rather than a generated artefact; all others are "
                             "regenerable from the named script")},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [m for m in manifest if m["status"] == "MISSING"]
    print(f"supplementary items included: "
          f"{len([m for m in manifest if m['status'] == 'included'])}")
    if missing:
        print(f"MISSING: {[m['item'] for m in missing]}")
    print(f"-> {out}  ({out.stat().st_size:,} B)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
