#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Apply the verified review corrections that are wording/framing, not data.

Four items, each traced to a reviewer finding that I independently confirmed:

1. TITLE. "Pooling conceals directional conflict" overreaches: the paper's own
   reporting of I2, Q and prediction intervals is precisely what stops pooling
   from concealing a conflict, so the title contradicts the method. The
   defensible claim is that the pooled estimate has no predictive value for a
   new population. "pre-registered" also becomes "pre-specified", because only
   four items were pre-specified and the five analyses carrying the quantitative
   argument were added afterwards.

2. ABSTRACT p-range. It read "p = 0.42-0.52"; the JSON holds 0.4178, 0.5169 and
   0.3472. The range silently dropped r20's value, which is the smallest and the
   only one that is not loosely consistent with the sentence.

3. "REVERSED BY REGION" framing. The text said "the single positive cohort is
   European while all three protective cohorts are not". ELSA is European and
   protective (0.7675), so this is factually wrong; and the Europe subgroup
   estimate of 1.0817 is the pooled value of two cohorts pointing OPPOSITE ways
   (SHARE 1.109, ELSA 0.7675), so a regional p-value packages within-group
   disagreement as a between-group difference. With leave-one-out showing SHARE
   alone drives the heterogeneity, the regional framing is dropped.

4. I2 versus absolute heterogeneity. I2 of 90-94% reads as "enormous
   inconsistency", but tau^2 on the log-OR scale corresponds to cross-cohort
   ratio differences of only 1.24x-2.13x, and the high I2 is driven by SHARE's
   very small standard error (710k observations). Using I2 alone as a rejection
   criterion is therefore partly a sample-size penalty. tau^2 and the ratio are
   now reported alongside I2.

Run: python scripts/apply_framing_corrections.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

EDITS = [
    # ---- 1. title -------------------------------------------------------
    ("../scripts/assemble_manuscript.py", None, None),   # handled separately
]

ABSTRACT_TITLE_OLD = (
    "Pooling conceals directional conflict: a pre-registered cross-cohort "
    "evaluation of 21 literature-derived exposome rules for major eye disease "
    "in 598,386 person-waves")
ABSTRACT_TITLE_NEW = (
    "Pooled exposome-eye disease estimates do not predict new populations: a "
    "pre-specified cross-cohort evaluation of 21 literature-derived rules in "
    "598,386 person-waves")

PAIRS = [
    # ---- 2. abstract p-range -------------------------------------------
    ("abstract.md",
     "Cohort mean age did not explain the heterogeneity (p = 0.42–0.52)",
     "Cohort mean age did not explain the heterogeneity (p = 0.35–0.52 across "
     "the three rules with four or more cohorts)"),
    # ---- 3. regional framing in Results --------------------------------
    ("results.md",
     "Four\ncohorts therefore split 1:3 on the sign of the association, and the single\n"
     "positive cohort is European while all three protective cohorts are not.",
     "The sign therefore splits one against three, but the split is not regional: "
     "ELSA is European and points the same protective way as CLHLS and CRELES, so "
     "the risk-increasing estimate comes from a single cohort (SHARE) rather than "
     "from a European subgroup. Leave-one-out analysis confirms this — see below."),
    # ---- 4. I2 vs absolute heterogeneity in Results ---------------------
    ("results.md",
     "Every rule with more than one cohort has extreme between-cohort heterogeneity, and for **every one of\n"
     "them the 95% prediction interval — the range in which a new cohort's true effect\n"
     "would be expected to fall — includes the null** (Table 5):",
     "Every rule with more than one cohort shows high between-cohort I², and for **every one of\n"
     "them the 95% prediction interval — the range in which a new cohort's true effect\n"
     "would be expected to fall — includes the null** (Table 5). I² must be read\n"
     "alongside τ² here: on the log-odds-ratio scale the fitted τ² corresponds to\n"
     "cross-cohort ratio differences of only **1.24× to 2.13×**, and the high I² is\n"
     "driven by SHARE's very small standard error rather than by large absolute\n"
     "divergence, so I² alone would partly be a sample-size penalty:"),
]


def main() -> int:
    problems = []
    for fname, old, new in PAIRS:
        p = SEC / fname
        t = p.read_text(encoding="utf-8")
        n = t.count(old)
        if n != 1:
            problems.append(f"{fname}: found {n}x -> {old[:64]!r}")
            continue
        p.write_text(t.replace(old, new), encoding="utf-8")
        print(f"  {fname}: ok")

    # title lives in the assembly script
    a = ROOT / "scripts" / "assemble_manuscript.py"
    t = a.read_text(encoding="utf-8")
    if ABSTRACT_TITLE_OLD in t:
        a.write_text(t.replace(ABSTRACT_TITLE_OLD, ABSTRACT_TITLE_NEW),
                     encoding="utf-8")
        print("  assemble_manuscript.py: title replaced")
    elif ABSTRACT_TITLE_NEW in t:
        print("  assemble_manuscript.py: title already replaced")
    else:
        problems.append("assemble_manuscript.py: title anchor not found")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
