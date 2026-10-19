#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update the manuscript after the subgroup-pooling correction.

WHAT CHANGED
------------
`subgroup_diff()` pooled within each region using FIXED-effect weights. Because
SHARE's variance is two orders of magnitude below the others, Europe's pooled
value was ~93% SHARE by weight, so "Europe = 1.0817" was SHARE, and the
between-region p for r10 was 4.5e-06. Recomputing with random-effects weights
within each region gives Europe = 0.9394 and p = 0.45.

The consequence is that the paper's second headline claim does not hold. There
is no significant regional difference for r10. What the data support is:
three cohorts agree with each other (dropping SHARE takes I-squared to 0.0 and
the pooled estimate to 0.747, 0.66-0.84), and SHARE alone disagrees, at a
precision roughly twenty times greater. The disagreement is therefore about one
cohort, not about regions.

Run: python scripts/update_after_subgroup_correction.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

PAIRS = [
    # ---- Results: the r10 paragraph --------------------------------------
    ("results.md",
     "Two rules did not transport. **r10 (smoking → cataract) reversed direction by\n"
     "region**: it was risk-increasing in SHARE (OR 1.11, 1.04–1.18, q = 0.0095) but\n"
     "significantly **protective** in CLHLS (OR 0.748, 0.64–0.87, q = 0.0012), with\n"
     "ELSA (0.77) and CRELES (0.70) also protective though uninformative. The sign\n"
     "therefore splits one against three, but the split is not regional: ELSA is\n"
     "European and points the same protective way as CLHLS and CRELES, so the\n"
     "risk-increasing estimate comes from a single cohort (SHARE) rather than from a\n"
     "European subgroup. Leave-one-out analysis confirms this — see below.",
     "Two rules did not transport. **r10 (smoking → cataract)** is risk-increasing in\n"
     "SHARE (OR 1.11, 1.04–1.18, q = 0.0095) and **protective** in CLHLS (OR 0.748,\n"
     "0.64–0.87, q = 0.0012), with ELSA (0.77) and CRELES (0.70) also protective\n"
     "though uninformative. The sign splits one against three, but **the split is\n"
     "not regional and not explained by region**: ELSA is European and points the\n"
     "same protective way as CLHLS and CRELES, and a between-region test is not\n"
     "significant once each region is pooled with random-effects rather than\n"
     "fixed-effect weights (Europe 0.94, p = 0.45; using fixed-effect weights the\n"
     "same test gives 1.08 and p < 0.0001, but that is an artefact — Europe's pool\n"
     "would be 93% SHARE by weight because SHARE's standard error is roughly twenty\n"
     "times smaller than the others'). The disagreement is between **one cohort and\n"
     "the other three**, which leave-one-out analysis confirms: dropping SHARE takes\n"
     "I² to 0.0% and the pooled estimate to 0.747 (0.66–0.84)."),
    # ---- Abstract --------------------------------------------------------
    ("abstract.md",
     "Smoking–cataract reversed by region (SHARE 1.11, 1.04–1.18; CLHLS 0.748,\n"
     "0.64–0.87) and its **pooled estimate was null (0.84, 0.67–1.05) while regional\n"
     "subgroups differed (p < 0.0001)** — a summary describing no population studied.",
     "For smoking–cataract the pooled estimate was null (0.84, 0.67–1.05) while\n"
     "three cohorts agreed on a protective association (dropping SHARE: I² = 0.0%,\n"
     "pooled 0.747, 0.66–0.84) and one disagreed. A between-region test was **not**\n"
     "significant once regions were pooled with random-effects weights (p = 0.45), so\n"
     "this is one cohort against three rather than a regional reversal."),
    # ---- Discussion: the regional framing --------------------------------
    ("discussion.md",
     "For smoking and cataract the pooled estimate is null (OR 0.84, 95% CI 0.67–1.05)\n"
     "while the regional subgroups differ significantly (Europe 1.08 versus Asia 0.75\n"
     "and the Americas 0.70; p < 0.0001). The pooled number describes no population\n"
     "that was actually studied.",
     "For smoking and cataract the pooled estimate is null (OR 0.84, 95% CI 0.67–1.05)\n"
     "while three cohorts agree with one another and a fourth does not. The pooled\n"
     "number is a weighted compromise between a large, precise cohort and three small\n"
     "ones, and describes neither."),
]

REMOVALS = [
    # the regional-reversal explanation section no longer has a premise
    ("discussion.md",
     "**Selective survival.** The CLHLS cohort has a mean age of 92.0 years.",
     "**One cohort, not a region.** An earlier version of this analysis reported r10\n"
     "as a regional reversal. That was wrong twice over: ELSA is European and\n"
     "protective, so the protective cohorts were not all non-European; and the\n"
     "between-region test had pooled within region using fixed-effect weights, which\n"
     "at this level of heterogeneity made Europe 93% SHARE by weight. Pooled\n"
     "correctly, the regional difference is not significant (p = 0.45). What remains\n"
     "is a single cohort whose estimate differs from three others that agree with\n"
     "each other, and which carries roughly twenty times their precision. Three\n"
     "explanations are still available for that difference, and this layer cannot\n"
     "distinguish them; what it can do is bound them.\n\n"
     "**Selective survival.** The CLHLS cohort has a mean age of 92.0 years."),
]


def main() -> int:
    problems = []
    for fname, old, new in PAIRS:
        p = SEC / fname
        t = p.read_text(encoding="utf-8")
        n = t.count(old)
        if n != 1:
            problems.append(f"{fname}: {n}x -> {old[:70]!r}")
            continue
        p.write_text(t.replace(old, new), encoding="utf-8")
        print(f"  {fname}: replaced")
    for fname, anchor, new in REMOVALS:
        p = SEC / fname
        t = p.read_text(encoding="utf-8")
        if anchor not in t:
            problems.append(f"{fname}: removal anchor missing")
            continue
        if new.split("\n")[0] in t:
            print(f"  {fname}: already updated")
            continue
        p.write_text(t.replace(anchor, new, 1), encoding="utf-8")
        print(f"  {fname}: explanation section reframed")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
