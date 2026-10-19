#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write the positive control into the manuscript.

The positive control is now the paper's load-bearing analysis, so it goes into
Methods (as a pre-specified falsification test of our own premise), Results (as
the first result, before the rules), the Discussion and the Abstract.

Its result is that the control FAILS: age-cataract has I2 = 99.2% across the
five cohorts that can estimate it, higher than any of the exposure rules. The
manuscript must say that plainly rather than present the control as a
reassurance, because the failure is what the paper now argues.

Run: python scripts/write_positive_control.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

METHODS = """
### Positive control: a falsification test of our own premise

The argument of this paper is that measurement availability, not sample size,
bounds what this rule base can test, and that the rules that were testable show
more between-cohort heterogeneity than a pooled estimate can carry. **A reviewer
is entitled to the opposite reading: that these cohorts are too noisily or too
incomparably measured to detect anything, in which case the rule heterogeneity
says nothing about the rules.** That reading is testable, so we tested it.

Age and sex are associated with cataract and with vision impairment in every
population in which anyone has looked, with large effects and no disagreement
about direction. We therefore estimated, in every cohort that can support it:

    outcome ~ age (per decade) + female + wave, clustered by participant

and pooled the results across cohorts **with the same random-effects estimator
used for the rules**, so that the control and the rules are directly comparable.
The control was specified before it was run as a falsification test: if the
cohorts cannot recover an association that is certainly real with tolerable
heterogeneity, then the rule heterogeneity must not be read as evidence about
the rules. **We report the outcome whichever way it falls.**
"""

RESULTS = """
### A positive control fails, and that failure frames everything below

Before the rules, the control. Age is associated with cataract in every
population studied, with a large effect and no dispute about direction. Pooled
across the five cohorts that can estimate it, the association is **OR 1.99 per
decade (1.45–2.75) with I² = 99.2%** — and per cohort it is 2.25 in SHARE, 3.14
in ELSA, 2.16 in LASI, 1.81 in CRELES and **1.15 in CLHLS**. For vision
impairment the age association is OR 1.36 (1.11–1.66) with **I² = 99.5%**. The
sex associations are less extreme but still heterogeneous (cataract 65.0%,
vision impairment 96.2%).

**The positive controls are more heterogeneous than any of the exposure rules
(79.5–93.8%).** This is not the result we expected and it changes what the paper
can claim:

1. **The strongest form of our original claim does not hold.** We cannot
   attribute the rules' heterogeneity to the exposures alone, because the
   outcomes are heterogeneous too — even for age, whose association with
   cataract is not in doubt.
2. **The narrower claim is better supported and more general.** In this data
   layer, neither the outcomes nor the exposures are comparable enough across
   cohorts for a pooled estimate to predict a new population. That is now
   demonstrable using associations that are certainly real, rather than resting
   on rules whose truth is exactly what is in question.
3. **A pooled multi-cohort exposome estimate should not be read as a
   population-transportable quantity.** That is the paper's warning, and the
   positive control is its evidence.

**Two consequences for reading the rest of this paper.** First, the rule results
below should be interpreted as describing *this evidence base*, not the
underlying biology: where a rule fails to transport, the failure may lie in
either the rule or the measurement, and this layer cannot separate them.
Second, the construct substitutions documented in the Methods are not a minor
caveat but an instance of the same phenomenon — the measurement a rule needs
does not exist in the populations asked to test it.
"""

DISCUSSION = """
**The positive control reframes the finding.** We expected the control to
validate the pipeline: if age predicts cataract consistently everywhere, then
the cohorts can detect real associations and the rule heterogeneity must be
about the rules. It did not. Age-cataract is more heterogeneous across these
cohorts (I² = 99.2%) than any of the exposure rules, and the CLHLS estimate is a
third of the ELSA estimate for an association whose direction is not in
disputation.

That result is uncomfortable for the paper and we have kept it in the
foreground rather than in the supplement, because it is the more useful finding.
It means the limitation of a pooled multi-cohort exposome analysis is not
confined to the exposures: **the outcome definitions are themselves not
comparable enough, and a pooled estimate therefore describes a quantity no
single population has.** The practical rule that follows is narrow but real:
a pooled exposome estimate should be published with its prediction interval and
its per-population estimates, and should not be presented as the effect to
expect in a new setting. A pooled point estimate from cohorts this heterogeneous
is a summary of a literature, not a parameter of nature.
"""


def main() -> int:
    problems = []
    m = SEC / "methods.md"
    t = m.read_text(encoding="utf-8")
    anchor = "### E-values"
    if "falsification test of our own premise" in t:
        print("  methods.md: positive control already present")
    elif anchor in t:
        m.write_text(t.replace(anchor, METHODS.strip() + "\n\n" + anchor, 1),
                     encoding="utf-8")
        print("  methods.md: positive control added")
    else:
        problems.append("methods.md: anchor missing")

    r = SEC / "results.md"
    tr = r.read_text(encoding="utf-8")
    anchor2 = "## Between-cohort heterogeneity"
    if "A positive control fails" in tr:
        print("  results.md: already present")
    elif anchor2 in tr:
        r.write_text(tr.replace(anchor2, RESULTS.strip() + "\n\n" + anchor2, 1),
                     encoding="utf-8")
        print("  results.md: positive control added")
    else:
        problems.append("results.md: anchor missing")

    d = SEC / "discussion.md"
    td = d.read_text(encoding="utf-8")
    anchor3 = "## Measurement as the limiting factor"
    if "The positive control reframes the finding" in td:
        print("  discussion.md: already present")
    elif anchor3 in td:
        d.write_text(td.replace(anchor3, DISCUSSION.strip() + "\n\n" + anchor3, 1),
                     encoding="utf-8")
        print("  discussion.md: positive control added")
    else:
        problems.append("discussion.md: anchor missing")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
