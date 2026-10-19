#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Retitle the paper and rewrite the abstract around the positive control.

The title should carry the finding, and the finding is now the positive control:
a pooled multi-cohort exposome estimate does not describe a population, and that
is demonstrable with an association nobody disputes.

The previous title, "Pooled exposome-eye disease estimates do not predict new
populations", is still true but is no longer the sharpest statement available.
The sharper one leads with the control, because "even age does not replicate"
is the sentence that makes a reader who does not work on eyes stop.

Run: python scripts/retitle_for_positive_control.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"
ASM = ROOT / "scripts" / "assemble_manuscript.py"

OLD_TITLE = (
    'TITLE = (\n'
    '    "Pooled exposome-eye disease estimates do not predict new populations: a "\n'
    '    "pre-specified cross-cohort evaluation of 21 literature-derived rules in "\n'
    '    "598,386 person-waves"\n'
    ')')
NEW_TITLE = (
    'TITLE = (\n'
    '    "Even age does not transport: a pooled multi-cohort exposome estimate "\n'
    '    "describes no population, in 285,878 participants and 21 "\n'
    '    "literature-derived rules"\n'
    ')')

ABSTRACT_ADD = """
**A positive control fails.** Before testing the rules we tested an association
that is certainly real. Age is associated with cataract everywhere, yet pooled
across the five cohorts that can estimate it the association is OR 1.99 per
decade (1.45–2.75) with **I² = 99.2%**, and the per-cohort estimates run from
1.15 (CLHLS) to 3.14 (ELSA). **The positive control is more heterogeneous than
any of the exposure rules (79.5–93.8%).** The limitation of a pooled
multi-cohort exposome analysis therefore is not confined to the exposures: the
outcome definitions are not comparable enough either, and a pooled estimate
describes a quantity no single population has.
"""


def main() -> int:
    problems = []
    a = ASM.read_text(encoding="utf-8")
    if NEW_TITLE.split("\n")[1] in a:
        print("  title already updated")
    elif OLD_TITLE in a:
        ASM.write_text(a.replace(OLD_TITLE, NEW_TITLE, 1), encoding="utf-8")
        print("  title updated")
    else:
        problems.append("assemble_manuscript.py: title anchor missing")

    ab = SEC / "abstract.md"
    t = ab.read_text(encoding="utf-8")
    if "A positive control fails" in t:
        print("  abstract already carries the control")
    else:
        # the control goes immediately after the background/framing sentence so
        # it is read before the rule results
        marker = "\n\n"
        lines = t.split("\n")
        ins = None
        for i, ln in enumerate(lines):
            if ln.strip().startswith("We") and len(ln.strip()) > 60:
                ins = i + 1
                break
        if ins is None:
            problems.append("abstract.md: no insertion point found")
        else:
            lines.insert(ins, ABSTRACT_ADD.strip())
            ab.write_text("\n".join(lines), encoding="utf-8")
            print("  abstract updated with the positive control")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
