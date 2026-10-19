#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate Table 2 from rules.yaml, so it cannot go stale.

Table 2 lists every rule with its severity and evidence_level. Nothing generated
it: `assemble_manuscript.py` reads the file to inline it into the manuscript, and
that was the only reference in the repository. So it was a hand-built artifact
with no link to its source.

That went wrong the moment the grades changed. Two rules were regraded A -> B
(after their citations resolved to meta-analyses and four independent checks
showed no cataract guideline is obtainable), and Table 2 kept printing them as
`high | A` -- including in the submission package copy, which is what a reviewer
would read. Nothing would have caught it: the manuscript QC counts table
references, and the numeric verifier checks the cohort numbers, neither of which
reads a severity column.

The fix is the one that was missing: derive the table from `configs/rules.yaml`
on demand. This is the same class of gap as the submission package that never
refreshed its figures (`if not d.exists()`), and it is closed the same way -- by
regenerating rather than by remembering.

Run: python scripts/build_table2.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "tables" / "table2_rules.md"
CSV_OUT = ROOT / "outputs" / "tables" / "rule_list.csv"

TITLE = ("# Table 2. The 21 literature-derived exposome rules: entity flags, "
         "direction, evidence level and source")
COLS = ["rule_id", "severity", "risk_type", "evidence_level", "direction",
        "a_flags", "b_flags", "negative_control", "note"]


def main() -> int:
    from huiyan_agent.risk_rules import load_rules
    rules = load_rules()

    lines = [TITLE, "", "| " + " | ".join(COLS) + " |",
             "|" + "---|" * len(COLS)]
    for r in rules:
        lines.append("| " + " | ".join([
            r.id,
            r.severity,
            r.risk_type,
            r.evidence_level,
            r.direction,
            ",".join(r.entity_a_flags),
            ",".join(r.entity_b_flags),
            str(bool(r.negative_control)),
            "",                      # note column, filled by hand when needed
        ]) + " |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Table 2 written: {len(rules)} rules -> {OUT}")

    # rule_list.csv is the same content in machine-readable form; keep the two in
    # step so they cannot disagree about a grade either.
    with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in rules:
            w.writerow([r.id, r.severity, r.risk_type, r.evidence_level,
                        r.direction, ",".join(r.entity_a_flags),
                        ",".join(r.entity_b_flags), bool(r.negative_control), ""])
    print(f"rule_list.csv written: {CSV_OUT}")

    dist: dict[str, int] = {}
    for r in rules:
        dist[r.evidence_level] = dist.get(r.evidence_level, 0) + 1
    print(f"  evidence_level distribution: {dict(sorted(dist.items()))}")
    for rid in ("r10_smoking_x_cataract", "r11_smoking_x_amd_late",
                "r13_bmi_x_cataract"):
        r = next(x for x in rules if x.id == rid)
        print(f"  {rid}: {r.severity} / {r.evidence_level}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
