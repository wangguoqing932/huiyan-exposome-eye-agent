#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Disclose every construct substitution in the cohort layer, as a set.

The r02 disclosure (scripts/disclose_r02_substitution.py) fixed one instance.
Review then found the same defect elsewhere, and enumerating it shows it is
systematic rather than incidental: the cohort layer's outcome and exposure maps
collapse distinct declared constructs onto whichever broader column the data
support.

Enumerated from scripts/cohort_confirmatory.py, the many-to-one mappings are:

    amd_any      <- amd_late (r05, r06, r09, r11) and amd_early (r17)
    diabetes     <- hyperglycemia (r02) and hba1c_elevated (r03, r04)

So five rules that name a specific AMD stage — four of them LATE AMD, one EARLY
— are all tested against "any AMD", and the distinction the rules draw is
discarded. Of those five, only r11 is testable in the cohort layer; the rest are
blocked by missing blood assays or geocoded exposure. The r02 substitution is
the same pattern on the exposure side.

WHY THIS MATTERS MORE THAN AS A CAVEAT. The paper's own conclusion is that
measurement availability, not sample size, bounds what can be tested. These
substitutions are that conclusion occurring inside the analysis: the rule names
a construct, the cohort lacks the measurement, and a broader construct is used
instead. Reporting them one at a time as limitations understates the pattern;
reporting them as a set makes them the evidence for the thesis.

Run: python scripts/disclose_all_substitutions.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

METHODS_BLOCK = """
### Construct substitutions: every rule that was tested on a broader construct

The rule base names specific constructs; the cohort layer tests whichever
construct the data can support. Where those differ, the difference is a
substitution and is listed here rather than left implicit. Enumerated from the
outcome and exposure maps, there are two, and between them they affect seven
rules.

| Rule(s) | Declared construct | Construct actually tested | Why |
|---|---|---|---|
| r05, r06, r09, r11 | late AMD | **any AMD** | no cohort separates late from early AMD |
| r17 | early AMD | **any AMD** | same |
| r02 | hyperglycaemia | **self-reported diabetes** | no fasting glucose or HbA1c measurement |
| r03, r04 | measured HbA1c | **self-reported diabetes** | same |

**Five rules that name a specific AMD stage — four of them late AMD, one early —
are all tested against "any AMD", so the stage distinction the rules draw is
discarded.** Of those five only r11 is testable in this layer (r05 and r06 lack
blood assays, r09 lacks a dietary index, r17 lacks geocoded exposure), and r11 is
therefore reported as **any AMD**, not late AMD. The r02 substitution is the same
pattern on the exposure side and is described in its own section above.

**This is not a list of incidental caveats; it is the paper's thesis occurring
inside the paper.** In each row the rule names a construct, the population lacks
the measurement that would identify it, and a broader construct is used instead.
The substitutes are not equivalent — "any AMD" mixes two diseases with different
natural histories, and self-reported diabetes ascertains only diagnosed disease,
with the under-ascertainment tracking access to care. Reporting the substitutions
one at a time as limitations would understate what they show; reporting them
together is what makes them evidence for the conclusion that measurement
availability, and not sample size, is the binding constraint on this rule base.
"""

LIMITATIONS_BLOCK = """
**Construct substitutions.** Seven rules were tested on a broader construct than
they declare — five AMD rules against "any AMD" rather than late or early AMD,
and two glycaemic rules against self-reported diabetes rather than a measured
marker (the Methods table lists each). Only two of the seven are testable in
this layer, so the substitutions affect r02 and r11 directly. Their direction of
bias is not uniform and cannot be signed in general: broader outcome definitions
usually dilute an association, whereas self-reported exposure with
access-dependent under-ascertainment can move an estimate either way. What can
be said is that neither r02 nor r11 tests the construct its citation supports,
and that this is the same limitation the paper identifies in the field it is
describing.
"""


def main() -> int:
    problems = []

    m = SEC / "methods.md"
    t = m.read_text(encoding="utf-8")
    anchor = "## Deviations from the pre-registered protocol"
    if "Construct substitutions: every rule" in t:
        print("  methods.md: substitution table already present")
    elif anchor in t:
        m.write_text(t.replace(anchor, METHODS_BLOCK.strip() + "\n\n" + anchor, 1),
                     encoding="utf-8")
        print("  methods.md: substitution table inserted")
    else:
        problems.append("methods.md: anchor missing")

    d = SEC / "discussion.md"
    td = d.read_text(encoding="utf-8")
    anchor2 = "**Single-cohort rules.**"
    if "Seven rules were tested on a broader construct" in td:
        print("  discussion.md: limitation already present")
    elif anchor2 in td:
        d.write_text(td.replace(anchor2, LIMITATIONS_BLOCK.strip() + "\n\n" + anchor2, 1),
                     encoding="utf-8")
        print("  discussion.md: limitation inserted")
    else:
        problems.append("discussion.md: anchor missing")

    # r11 must be named as any AMD wherever its result is reported
    r = SEC / "results.md"
    tr = r.read_text(encoding="utf-8")
    swaps = [
        ("r11 (smoking \u2192 AMD)", "r11 (smoking \u2192 any AMD)"),
        ("r11 (smoking \u2192 late AMD)", "r11 (smoking \u2192 any AMD)"),
    ]
    n = 0
    for a, b in swaps:
        if a in tr:
            tr = tr.replace(a, b)
            n += 1
    if n:
        r.write_text(tr, encoding="utf-8")
        print(f"  results.md: {n} r11 label(s) corrected to any AMD")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
