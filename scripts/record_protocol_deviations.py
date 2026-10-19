#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Record the three protocol deviations the review found (ledger B1-B3).

These are the three findings each of NEJM, JAMA and the ethics reviewer called
fatal, and all three are deviations that the project's OWN analysis plan
documents and the manuscript did not carry forward.

B1  Variance method. Plan section 19.7 requires survey design (strata/PSU/
    weights) for the cohorts that ship design weights, notably SHARE and LASI.
    The implementation used an unweighted cluster-robust GLM. This is not a
    choice that was made and then defended; the frames were BUILT WITHOUT any
    design variable -- a scan of all eight frames finds no weight, strata or PSU
    column (the only regex hit is CLHLS's `weight_kg`, which is body weight), and
    SHARE's `country` column is empty in all 1,693,515 rows. Every confidence
    interval, q-value and three-state label in the cohort layer therefore rests
    on unweighted variance.

B2  Rule set modified after the confirmatory run. Plan section 0 records it:
    2026-10-11 20:59 confirmatory run on v1.1 (20 rules); 2026-10-12 07:12 the
    rule set was changed (r02/r03/r04 cross-coverage and r22 added) giving v1.2
    (21 rules); 2026-10-12 07:13 baselines re-run. The plan calls this
    test-set fitting in its own words and states that R = 1.000 is constructed
    rather than earned. The manuscript reports the NHANES layer as internal
    validation with 6 replicated / 0 contradicted / declared-domain precision
    1.00 and never mentions the timeline.

B3  The heterogeneity-aware criterion is post hoc. Section 19.7 pre-registered
    one criterion: replicated with q < 0.05 in at least two cohorts. The
    "prediction interval excludes 1 and I-squared below 75%" criterion appears
    nowhere in the plan; the 75% value is hard-coded in the analysis script; and
    the script's own comments describe it as an upgrade written after the
    pre-registered rule turned out to be too permissive. It must be demoted to a
    post hoc sensitivity analysis, with the pre-registered criterion restored as
    the primary basis for the Abstract and Conclusions.

Run: python scripts/record_protocol_deviations.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "outputs" / "paper" / "sections"

# --- B1 + B2: extend the deviations table in Methods ------------------------
OLD_ROW_ANCHOR = (
    "| Measurement-modality audit and cohort-layer power calculation | No | after |")
NEW_ROWS = (
    "| Measurement-modality audit and cohort-layer power calculation | No | after |\n"
    "\n"
    "**Two further deviations are recorded here because they bear on every "
    "estimate in this layer.**\n"
    "\n"
    "**Variance method (section 19.7, not implemented).** The pre-registration "
    "specifies survey design variance — strata, primary sampling units and "
    "weights — for the cohorts that distribute design weights, naming SHARE and "
    "LASI. The analysis as run used an unweighted cluster-robust generalised "
    "linear model. This is not a modelling preference that was weighed and "
    "rejected: **the cohort frames were built without any design variable.** A "
    "scan of all eight frames finds no weight, strata or PSU column, and SHARE's "
    "`country` field is empty in all 1,693,515 of its rows. Every confidence "
    "interval, every q-value and therefore every three-state label reported for "
    "this layer rests on unweighted variance. Because SHARE contributes 137,183 "
    "of the 285,878 participants and is the cohort whose estimate drives the "
    "heterogeneity of r10, a design-based re-analysis could move that rule's "
    "conclusions in either direction; we report the deviation rather than "
    "assume it away.\n"
    "\n"
    "**Rule set modified after the confirmatory run (section 0, not reported in "
    "the manuscript).** The internal layers were first run on a 20-rule set "
    "(v1.1). The following morning the rule set was changed — the exposure "
    "cross-coverage of r02, r03 and r04 was altered and rule r22 was added — "
    "giving the 21-rule set (v1.2) used throughout this paper, and the "
    "confirmatory analysis was re-run on it. The pre-registration records this "
    "in its own words as **test-set fitting**, and states that the resulting "
    "recall of 1.000 is constructed rather than earned. The internal-layer "
    "results below are therefore reported on a rule set that was adjusted after "
    "seeing outcome data, and **the declared-domain precision of 1.00 in the "
    "NHANES and KNHANES layers should be read in that light**. The "
    "pre-registration requires both versions to be shown; the v1.1 figures are "
    "not reconstructible from the artefacts retained here, which is itself "
    "reported as a limitation rather than papered over.\n"
    "\n"
    "**Consequence for the conclusions.** The rule-level claims of this paper "
    "are made on the cohort layer, which was run once and not re-run after any "
    "rule change. The internal-layer precision figures are reported for "
    "completeness and are not load-bearing for anything argued here."
)

# --- B3: demote the post hoc criterion --------------------------------------
OLD_B3 = (
    "**no rule was reliably transportable**. Under a criterion that also requires\n"
    "the between-cohort heterogeneity to be tolerable, **none did**: both qualifying\n"
    "rules had I² above 90% and prediction intervals spanning unity, so a further\n"
    "population could plausibly show no association at all.")

PLAN = [
    ("../scripts/first_edits.py", None, None),
]


def main() -> int:
    problems = []
    m = SEC / "methods.md"
    t = m.read_text(encoding="utf-8")
    if "Two further deviations are recorded here" in t:
        print("  methods.md: deviations already recorded")
    elif OLD_ROW_ANCHOR in t:
        m.write_text(t.replace(OLD_ROW_ANCHOR, NEW_ROWS, 1), encoding="utf-8")
        print("  methods.md: B1 + B2 recorded")
    else:
        problems.append("methods.md: deviations table anchor missing")

    # B3 -- restore the pre-registered criterion as primary in the Discussion
    d = SEC / "discussion.md"
    td = d.read_text(encoding="utf-8")
    old3 = ("We therefore report both verdicts and treat their disagreement as a result. A\n"
            "transportability assessment that is to be useful should require the prediction\n"
            "interval to exclude the null and heterogeneity to be below a declared threshold;\n"
            "on that reading, the honest summary of this layer is that **none of the six\n"
            "testable rules was reliably transportable**, which is a weaker claim than the\n"
            "pre-registered criterion supports and a stronger one than a naive reading of the\n"
            "replication counts would suggest.")
    new3 = ("We therefore report both verdicts and treat their disagreement as a result.\n"
            "**The pre-registered criterion, and not the stricter one, is the basis of this\n"
            "paper's conclusions.** The stricter criterion — prediction interval excluding\n"
            "the null and I² below 75% — was written after the pre-registered rule turned\n"
            "out to be too permissive, and the 75% figure was chosen with the results in\n"
            "view; it is reported as a post hoc sensitivity analysis and is labelled as\n"
            "such throughout. Read on the pre-registered criterion, **two of six testable\n"
            "rules were transportable**; read on the post hoc one, none was. The useful\n"
            "methodological observation is the disagreement itself: a transportability\n"
            "criterion that counts replications is insensitive to between-cohort\n"
            "heterogeneity, which is why the two readings differ, and a criterion intended\n"
            "for prospective use should be fixed in advance with both properties in mind.")
    if new3.split("\n")[0] in td:
        print("  discussion.md: B3 already demoted")
    elif old3 in td:
        d.write_text(td.replace(old3, new3, 1), encoding="utf-8")
        print("  discussion.md: B3 demoted to post hoc")
    else:
        problems.append("discussion.md: B3 anchor missing")

    # B3 -- align the Abstract with the pre-registered criterion
    a = SEC / "abstract.md"
    ta = a.read_text(encoding="utf-8")
    olda = ("but both had I² above 90% and\n"
            "prediction intervals spanning unity (0.84–4.57; 0.81–1.89), so under a criterion\n"
            "also requiring tolerable heterogeneity **no rule was reliably transportable**.")
    newa = ("Both were accompanied by high between-cohort\n"
            "heterogeneity (I² above 90%) and prediction intervals spanning unity\n"
            "(0.84–4.57; 0.81–1.89), so a post hoc stricter criterion requiring a prediction\n"
            "interval to exclude the null would have accepted **neither**. On the\n"
            "pre-registered criterion **two rules were transportable**; the disagreement\n"
            "between the two readings is itself reported as a finding.")
    if newa.split("\n")[0] in ta:
        print("  abstract.md: B3 already aligned")
    elif olda in ta:
        a.write_text(ta.replace(olda, newa, 1), encoding="utf-8")
        print("  abstract.md: B3 aligned to the pre-registered criterion")
    else:
        problems.append("abstract.md: B3 anchor missing")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print("  " + x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
