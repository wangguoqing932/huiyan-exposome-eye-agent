#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate the cover letter — the last missing piece of the submission package.

The letter states the finding, why it matters beyond ophthalmology, and the
disclosures that a general-medical editor will look for: the pre-registered items
versus the five analyses added afterwards, the survey-design deviation, the
withdrawn figures, and the honest limitations of the positive control.

The target journal is left as a placeholder because it is the author's decision:
the manuscript is now framed for a general-medicine audience (IF > 20 territory)
while the package manifest still says Ophthalmology, and those imply different
letters. The placeholder is marked so it cannot be sent by accident.

Run: python scripts/build_cover_letter.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "submission" / "cover_letter.md"

LETTER = """# Cover letter

> **DRAFT — the target journal is not yet fixed.** The bracketed fields must be
> completed and the journal-specific paragraph adapted before this is sent. The
> manuscript is currently framed for a general-medicine readership; the package
> manifest still records *Ophthalmology*, which would call for a different
> emphasis in paragraph 3.

[Date]

The Editors
**[Journal name]**

Dear Editors,

We submit for your consideration a cross-cohort study of what happens when
literature-derived exposome rules for eye disease are taken to populations that
had no part in their construction. Its result is negative in a way we did not
expect, and we lead with that rather than burying it.

**What we did.** We assembled 21 exposure–outcome rules for major eye disease
from the literature and evaluated them in eight population-based ageing cohorts
on three continents, using raw source files only, under a three-state standard
pre-specified before the analysis (replicated / contradicted / uninformative).
Eighteen of the 168 possible (rule × cohort) cells were feasible, and six rules
were testable anywhere.

**What we found.** Before testing the rules we ran a positive control on
associations nobody disputes. Age's association with cataract, pooled across the
five cohorts that can estimate it, is OR 1.99 per decade with **I² = 99.2%** —
more heterogeneous than any of the exposure rules, ranging from 1.15 in one
cohort to 3.14 in another. We then resolved why, using NHANES 2005–2008, which
measured the same people by self-report and by objective near-vision testing:
self-reported cataract tracks age at OR 4.27 while objective acuity tracks it at
1.32. **Self-report is therefore not the weak instrument we assumed it was.** The
one cohort with a flat gradient is measuring the probability of having been
diagnosed, and diagnosis tracks access to care.

**Why we think this belongs in [journal].** The finding is not about eyes. A
pooled multi-cohort estimate of a self-reported outcome is routinely read as the
effect to expect in a new setting, and we show that where diagnosis rates differ
across populations, what is being pooled is a difference in access to care
dressed as a difference in biology. The safeguard we propose is narrow and
practicable: report the outcome's prevalence by cohort alongside the pooled
estimate, and prefer examination-based measurement where the construct allows.

**Disclosures we want on the record.**
- **Four items were pre-specified** (the testable rule set, the per-cohort BMI
  cut-point, the covariate set, the transportability criterion). **Five analyses
  were added after the primary results were known** — random-effects pooling, the
  stricter heterogeneity criterion, the regional subgroups, the E-values, and the
  modality audit — and the manuscript says so where each is used.
- **A pre-specified variance method was not implemented.** The plan required
  survey design variance for the cohorts distributing design weights; the frames
  contain no design variable and an unweighted cluster-robust model was used.
  This is stated in the Methods, not only in the Limitations.
- **Two figures from an earlier draft are withdrawn** and are not included; they
  were never rendered. The pipeline now detects that class of failure
  automatically.
- **A blind expert panel was planned and never conducted.** No kappa is reported
  anywhere, in the manuscript or the supplement.

**Reporting.** The observational analyses follow STROBE and a completed checklist
is included; the cross-cohort synthesis follows standard meta-analytic reporting
(REML τ², Cochran's Q, I², prediction intervals). TRIPOD+AI and DECIDE-AI are not
applicable and are not claimed.

**Data and code.** All sources are third-party surveys requiring their own
registration or application; the Data availability statement lists each route.
Analysis code, the audit trail and an archived snapshot with a DOI are provided.

We confirm this work is original, is not under consideration elsewhere, and that
all authors have approved the submission and declare no competing interests
beyond those stated in the Declarations section.

Yours sincerely,

[Corresponding author, on behalf of all authors]
[Affiliation, address, email]
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(LETTER, encoding="utf-8")
    n = len(LETTER.split())
    print(f"cover letter written: {n} words -> {OUT}")
    print("  placeholders remaining: [Date], [Journal name], [journal], "
          "[Corresponding author...], [Affiliation...]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
