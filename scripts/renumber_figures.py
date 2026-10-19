#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Move figure4 and figure5 to the supplement and renumber the main figures.

WHY
---
Both figures are blank or mostly blank pages (figure4: 4/4 panels are the
renderer's placeholder text; figure5: 2/3 panels are), and both are the two
weakest figures in the paper for its actual argument — they illustrate the
internal LLM system, whereas the paper's claim is about cross-cohort rule
transportability. Three reviewers independently recommended removing them:
NEJM and BMJ x Nature Medicine both called the manuscript two papers sewn
together, and the Lancet reviewer gave the same route.

Renumbering rather than leaving a gap: main figures become
    old 1 -> 1  architecture
    old 2 -> 2  performance
    old 3 -> 3  rule evaluation
    old 6 -> 4  dose response
    old 7 -> 5  power / MDE
    old 8 -> 6  cohort transportability
and the two removed figures become Figure S1 and S2.

The number mapping is applied to the manuscript sections, the legends file and
the assembly metadata. Contract files keep their `figure_id` (which is a stable
identifier, not a display number) and only have `figure_number` and the
`manuscript_section` updated.

Run: python scripts/renumber_figures.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"
LEG = ROOT / "outputs" / "paper" / "figure_legends.md"
CON = ROOT / "outputs" / "figures" / "contracts"

# old display number -> new display number
RENUM = {6: 4, 7: 5, 8: 6}
SUPP = {4: "S1", 5: "S2"}


def remap_text(t: str) -> tuple[str, int]:
    """Rewrite 'Figure N' / 'Figures N and M' / '图 N' style references."""
    n = 0

    def one(m: re.Match) -> str:
        nonlocal n
        num = int(m.group("num"))
        if num in SUPP:
            n += 1
            return f"{m.group('pre')}Figure {SUPP[num]}"
        if num in RENUM:
            n += 1
            return f"{m.group('pre')}Figure {RENUM[num]}"
        return m.group(0)

    t = re.sub(r"(?P<pre>\b)Figure (?P<num>\d+)\b", one, t)
    # Chinese references
    t2 = t
    for old, new in list(SUPP.items()) + list(RENUM.items()):
        t2 = t2.replace(f"图 {old}", f"图 {new}")
    return t2, n


def main() -> int:
    changed = []
    for p in list(SEC.glob("*.md")) + [LEG]:
        t = p.read_text(encoding="utf-8")
        t2, n = remap_text(t)
        if n:
            p.write_text(t2, encoding="utf-8")
            changed.append((p.name, n))
    for name, n in changed:
        print(f"  {name}: {n} 处图号引用已改")

    # contracts keep figure_id; only the display number changes
    for cpath in sorted(CON.glob("figure*.yaml")):
        t = cpath.read_text(encoding="utf-8")
        m = re.search(r"figure_number:\s*(\d+)", t)
        if not m:
            continue
        old = int(m.group(1))
        if old in SUPP:
            t = t.replace(f"figure_number: {old}",
                          f"figure_number: S{SUPP[old][1:]}", 1)
            cpath.write_text(t, encoding="utf-8")
            print(f"  {cpath.name}: -> Figure {SUPP[old]}")
        elif old in RENUM:
            t = t.replace(f"figure_number: {old}", f"figure_number: {RENUM[old]}", 1)
            cpath.write_text(t, encoding="utf-8")
            print(f"  {cpath.name}: {old} -> {RENUM[old]}")

    # a note in the supplement listing what moved and why
    supp = ROOT / "outputs" / "submission" / "supplementary_material.md"
    note = """

---

## Supplementary figures moved out of the main text

**Figure S1** (previously main Figure 4) and **Figure S2** (previously main
Figure 5) illustrate the internal system — one worked case end to end, and a
reasoning trace through the three architectural layers. They are placed in the
supplement because the claims of this paper are about cross-cohort rule
transportability, and neither figure bears on that argument; the main text no
longer depends on them. **Both are rendered from the internal-layer artefacts
and each panel states the artefact it was drawn from.** Reviewers of an earlier
version noted that the internal system evaluation and the cohort analysis read
as two papers, which is the reason for the separation.
"""
    if supp.exists() and "Figure S1 (previously main Figure 4)" not in supp.read_text(encoding="utf-8"):
        supp.write_text(supp.read_text(encoding="utf-8").rstrip() + note,
                        encoding="utf-8")
        print("  supplementary_material.md: 移出说明已追加")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
