#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Withdraw figure4 and figure5 from the submission package entirely.

Moving a blank figure to the supplement does not fix it. figure4's four panels
and figure5's first two panels contain only the renderer's placeholder text;
shipping them as Figure S1 and S2 would put two blank pages in the supplement,
which is the same defect in a different place.

The two figures are also the weakest in the paper for its actual argument: they
illustrate the internal LLM system, whereas the claim is about cross-cohort rule
transportability. Three reviewers recommended removing them.

So they are WITHDRAWN, and the supplement says so in plain terms — including
that they were blank, so that a reader who saw an earlier version is not left
wondering where they went. Their contracts are retained, marked `withdrawn`,
because the QC should keep reporting them rather than have them quietly vanish:
a scan that cannot see a withdrawn figure cannot tell withdrawal from a fix.

Run: python scripts/withdraw_blank_figures.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CON = ROOT / "outputs" / "figures" / "contracts"
PKG = ROOT / "outputs" / "submission"
FIGS = ROOT / "outputs" / "figures"

WITHDRAWN = ["figure4_demo_case", "figure5_reasoning_trace"]

NOTE = """

---

## Figures withdrawn from this submission

**Two figures from an earlier version are withdrawn and are not included here.**

They showed, respectively, one worked case end to end and a reasoning trace
through the three architectural layers of the system. **Both were withdrawn
because they were not rendered**: the panels contained only the figure
renderer's placeholder text, and this was not detected by the automated
figure QC, which checks that the rendering pipeline ran rather than that it
produced content. The defect was found by inspecting the rendered images.

They are also not needed for the argument. The claims of this paper concern
cross-cohort transportability of literature-derived rules, and neither figure
bears on that; the internal system evaluation they belonged to is reported in
the tables and is not load-bearing for any conclusion here. Shipping them as
supplementary figures would have placed two blank pages in the supplement, so
they are removed rather than relocated.

**The pipeline has been changed so that this cannot recur**: a placeholder scan
now tests both the figure contracts and the rendered pixels, and reports the two
figures as failures. The withdrawn contracts are retained deliberately, so that
the scan keeps reporting them: a check that cannot see a withdrawn figure cannot
distinguish withdrawal from repair.
"""


def main() -> int:
    for stem in WITHDRAWN:
        cpath = CON / f"{stem}.yaml"
        if cpath.exists():
            t = cpath.read_text(encoding="utf-8")
            if "disposition:" not in t:
                t += ("\ndisposition: withdrawn\n"
                      "withdrawn_reason: >\n"
                      "  Panels contained only the renderer's placeholder text. Not\n"
                      "  rendered, and not needed for the cohort-layer argument. Retained\n"
                      "  here so the placeholder scan keeps reporting it.\n")
                cpath.write_text(t, encoding="utf-8")
            print(f"  {cpath.name}: marked withdrawn")
        for ext in ("png", "svg", "pdf", "tiff"):
            f = FIGS / f"{stem}.{ext}"
            if f.exists():
                f.unlink()
                print(f"    removed {f.name}")
        for f in (PKG / "figures").glob(f"{stem}*") if (PKG / "figures").exists() else []:
            f.unlink()
            print(f"    removed from package: {f.name}")

    supp = PKG / "supplementary_material.md"
    if supp.exists():
        t = supp.read_text(encoding="utf-8")
        if "Figures withdrawn from this submission" not in t:
            supp.write_text(t.rstrip() + NOTE, encoding="utf-8")
            print("  supplementary_material.md: withdrawal note added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
