#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write the NHANES outcome-construct validation into the manuscript.

This is the paper's mechanistic core and it replaces a claim we would otherwise
have made wrongly. Before running it we expected self-reported cataract to be the
weaker instrument; NHANES 2005-2008 shows the opposite (age OR 4.27 for
self-reported cataract against 1.32 for objective near acuity), so the
"self-report is weak" explanation is withdrawn and replaced by the
access-dependent-ascertainment explanation, which the same data support.

Run: python scripts/write_nhanes_validation.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

METHODS = """
### Construct validation against an examination survey

The positive control left an ambiguity that the ageing cohorts cannot resolve.
CLHLS and ELSA both ascertain cataract by self-reported physician diagnosis, yet
age predicts it 1.15-fold per decade in one and 3.14-fold in the other. Either
the populations differ, or the same nominal self-report captures different things
in each. The ageing cohorts have no objective ocular measurement, so we turned to
a survey that has both.

**NHANES 2005-2008 measured the same participants with a self-reported cataract
item and an objective near-vision test.** We pooled the two waves (n = 14,440)
and fitted, for each of four constructs, the same model used on the ageing
cohorts: outcome ~ age (per decade) + sex + wave. The four were: self-reported
cataract operation on the questionnaire; the same question asked at the
examination; self-rated fair-or-poor eyesight; and objective near-card acuity
below the impaired threshold. Coding follows the release documentation
(yes/no items as 1/2; the eyesight item as a 1-5 scale collapsed to
excellent-or-good versus fair-to-very-poor; acuity as lines read).

**We state the expectation we held before running this**, because the result
contradicted it: we expected the self-reported item to track age weakly and the
objective test to track it strongly, which would have made self-report the weaker
instrument. **It is the reverse.**
"""

RESULTS_ADD = """
### The outcome construct itself is population-dependent

The positive control left open whether self-reported cataract is simply a weak
instrument. **NHANES 2005-2008 says it is not.** In that survey, which measured
the same people with both a self-report and an objective near-vision test:

| Construct | n | Age OR per decade (95% CI) |
|---|---|---|
| Self-reported cataract operation | 7,074 | **4.27** (3.91–4.67) |
| Same question asked at the examination | 6,429 | **4.30** (3.90–4.74) |
| Self-rated fair-or-poor eyesight | 7,065 | 1.15 (1.11–1.20) |
| Objective near acuity, impaired | 4,786 | 1.32 (1.22–1.42) |

**Self-reported cataract tracks age 3.2 times more strongly than the objective
acuity test**, so self-report is not intrinsically the weaker instrument. That
removes the explanation we expected and leaves the harder one: if a
well-conducted survey gets 4.27 on this construct, CLHLS's 1.22 is a property of
CLHLS, not of self-report.

**It is not the wave structure.** Restricting CLHLS to the 1998 wave alone — the
one whose provenance is unambiguous — leaves the gradient flat: prevalence is
17.9% at ages 75–80, 16.6% at 80–85, 17.8% at 85–90 and 18.4% at 90–95, rising
only past 95. The age odds ratio is **1.22 per decade** (p = 1.2 × 10⁻⁷) against
NHANES's 4.27.

**The item measures diagnosis, and diagnosis is access-dependent.** The CLHLS
question asks whether the respondent suffers from cataract; cataract is diagnosed
by an eye examination. In rural China in 1998 such examinations were uncommon and
their availability tracked access to care, so the item records the probability of
having been diagnosed rather than the probability of having the disease. That is
the same mechanism we invoke — and had previously only conceded in passing — for
smoking and cataract: **where a self-reported outcome depends on being diagnosed,
its measured prevalence depends on who has access to diagnosis.**

**Consequence for pooling.** Two cohorts can use the same nominal outcome, the
same nominal ascertainment and the same model, and still be measuring different
quantities. This is not a caveat appended to the analysis; it is the reason the
pooled estimate in this paper describes no population, and it is demonstrable
with a benchmark rather than asserted.
"""

DISCUSSION_ADD = """
**What the outcome validation settles, and what it withdraws.** We expected
self-reported cataract to be the weaker instrument and designed the NHANES
comparison to show it. It showed the opposite: self-reported cataract tracks age
at OR 4.27 per decade while objective near acuity tracks it at 1.32. The
"self-report is intrinsically weak" explanation is therefore withdrawn, and what
replaces it is both less obvious and more useful. **A nominal construct can be
ascertained the same way in two cohorts and still measure different quantities,
because what a self-report captures depends on who in that population has access
to the diagnosis.** CLHLS's flat age gradient for cataract (1.22, and flat across
four age bands even in the clean single wave) is the signature of that mechanism,
and it is the mechanism we had already conceded in the Limitations without
letting it do any work.

**The practical rule.** In any multi-cohort pooling of self-reported outcomes,
the quantity that makes the cohorts comparable is not the wording of the item but
the population's underlying rate of diagnosis. Reporting a pooled odds ratio
across cohorts whose diagnosis rates differ converts a difference in access to
care into an apparent difference in biology. The minimum safeguard is to report
the outcome's prevalence by cohort alongside the pooled estimate, and to prefer
examination-based measurement where the construct permits it — which, as this
paper's own modality audit shows, is precisely what the ophthalmic exposome
evidence base most often lacks.
"""


def main() -> int:
    problems = []
    m = SEC / "methods.md"
    t = m.read_text(encoding="utf-8")
    a = "### Positive control: a falsification test of our own premise"
    if "Construct validation against an examination survey" in t:
        print("  methods.md: already present")
    elif a in t:
        m.write_text(t.replace(a, METHODS.strip() + "\n\n" + a, 1), encoding="utf-8")
        print("  methods.md: NHANES validation added")
    else:
        problems.append("methods.md: anchor missing")

    r = SEC / "results.md"
    tr = r.read_text(encoding="utf-8")
    a2 = "## Between-cohort heterogeneity"
    if "The outcome construct itself is population-dependent" in tr:
        print("  results.md: already present")
    elif a2 in tr:
        r.write_text(tr.replace(a2, RESULTS_ADD.strip() + "\n\n" + a2, 1),
                     encoding="utf-8")
        print("  results.md: NHANES validation added")
    else:
        problems.append("results.md: anchor missing")

    d = SEC / "discussion.md"
    td = d.read_text(encoding="utf-8")
    a3 = "## Measurement as the limiting factor"
    if "What the outcome validation settles" in td:
        print("  discussion.md: already present")
    elif a3 in td:
        d.write_text(td.replace(a3, DISCUSSION_ADD.strip() + "\n\n" + a3, 1),
                     encoding="utf-8")
        print("  discussion.md: NHANES validation added")
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
