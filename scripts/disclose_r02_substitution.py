#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Disclose the r02 exposure substitution (review finding F3).

WHAT WAS WRONG
--------------
Rule r02 is stated in the rule base and in configs/rules.yaml as
hyperglycaemia -> cataract, and its sibling rule r03 requires a MEASURED HbA1c.
In the cohort layer neither a fasting glucose nor an HbA1c measurement exists in
any of the eight cohorts, so both exposure flags were operationalised as
SELF-REPORTED physician-diagnosed diabetes
(scripts/cohort_confirmatory.py: EXPOSURE_MAP maps "hyperglycemia" AND
"hba1c_elevated" to the column `diabetes`).

The manuscript called it "hyperglycaemia -> cataract" throughout and never
disclosed the substitution. Two things make that serious rather than cosmetic:

  * it contradicts this project's own stated discipline, that measured exposures
    are preferred to self-report; and
  * it undermines the paper's closing conclusion, since the headline rule that
    "transported" did so on a self-report substitute because the measurement was
    absent. The measurement problem the paper diagnoses had already occurred
    inside the paper.

Self-reported diabetes prevalence across the four cohorts that tested r02 spans
1.36% (CLHLS) to 19.14% (CRELES) — a 14-fold range, which is itself evidence
that the exposure is not the same construct across cohorts.

This script renames the exposure where it is described, adds the disclosure, and
recasts the conclusion so the substitution becomes the concrete instance of the
paper's own argument rather than a hidden defect.

Run: python scripts/disclose_r02_substitution.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

# (file, old, new) — literal replacements, each asserted to apply exactly once
EDITS = [
    ("abstract.md",
     "(hyperglycaemia–cataract, pooled OR 1.95, 95% CI 1.33–2.88;",
     "(self-reported diabetes–cataract, pooled OR 1.95, 95% CI 1.32–2.88;"),
    ("results.md",
     "Two rules transported. **r02 (hyperglycaemia → cataract)** replicated in three of",
     "Two rules transported. **r02 replicated in three of"),
    ("results.md",
     "| r02 hyperglycaemia → cataract | 4 | 1.95 (1.33–2.88) | 90.5% | <0.0001 | 0.84–4.57 | p = 0.0004 |",
     "| r02 self-reported diabetes → cataract | 4 | 1.95 (1.32–2.88) | 90.5% | <0.0001 | 0.84–4.57 | p = 0.0004 (same test as Q) |"),
    ("results.md",
     "the hyperglycaemia–cataract estimate in CLHLS has an E-value of 6.64 (4.69) and",
     "the diabetes–cataract estimate in CLHLS has an E-value of 6.64 (4.69) and"),
]

# the disclosure paragraph, inserted into Methods after the outcomes section
DISCLOSURE = """
### Disclosure: the r02 exposure is self-reported, not measured

Rule r02 is stated as hyperglycaemia → cataract and its sibling rule r03
requires a measured HbA1c. **No cohort in this layer has a usable fasting
glucose or HbA1c measurement, and both flags were therefore operationalised as
self-reported physician-diagnosed diabetes.** The rule is titled
"self-reported diabetes → cataract" wherever this layer's results are reported,
and the substitution is stated here rather than left implicit.

Two consequences should be weighed. First, this contradicts the preference for
measured over self-reported exposures stated above; it was unavoidable in this
layer, but it means r02's transportability in these cohorts is transportability
of a *self-report* rule, and the NHANES/KNHANES layers — which test the same
rule on measured glycaemic markers — are not testing the same construct.

Second, the substitution is not neutral across cohorts. Self-reported diabetes
prevalence in the four cohorts that tested r02 ranges from **1.36% (CLHLS) to
19.14% (CRELES)**, a fourteen-fold spread. Differential under-ascertainment of
diagnosed diabetes tracks access to care, which is itself correlated with the
outcome, so the exposure is not on the same scale in each cohort. The CLHLS
estimate is the largest in the set (OR 3.59) and comes from the cohort with by
far the lowest reported prevalence, which is the pattern that differential
ascertainment would produce.

This is not an incidental limitation. **It is the paper's own argument occurring
inside the paper**: the measurement the rule requires does not exist in the
populations asked to test it, and the substitute that was used is not comparable
across them.
"""


def main() -> int:
    problems = []
    for fname, old, new in EDITS:
        p = SEC / fname
        t = p.read_text(encoding="utf-8")
        n = t.count(old)
        if n != 1:
            problems.append(f"{fname}: anchor found {n} times: {old[:56]!r}")
            continue
        p.write_text(t.replace(old, new), encoding="utf-8")
        print(f"  {fname}: replaced 1 occurrence")

    m = SEC / "methods.md"
    t = m.read_text(encoding="utf-8")
    if "Disclosure: the r02 exposure" in t:
        print("  methods.md: disclosure already present")
    else:
        anchor = "## The three-state standard"
        if anchor in t:
            t = t.replace(anchor, DISCLOSURE.strip() + "\n\n" + anchor, 1)
            m.write_text(t, encoding="utf-8")
            print("  methods.md: disclosure inserted")
        else:
            problems.append("methods.md: no anchor for the disclosure")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
