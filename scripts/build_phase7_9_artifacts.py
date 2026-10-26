#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the three phase-7_9 artifacts the package was missing.

The skill's SUBMISSION_FILES list names eight files. Six existed; three did not:

  highlights.md          -- Elsevier requires 3-5 bullets, each <= 85 characters
  data_availability.md   -- per-cohort access routes
  graphical_abstract.svg -- the skill ships a placeholder scaffold that is
                            meant to be replaced, not shipped

(manuscript.en.md is not applicable: the manuscript is English-native, so the
bilingual pair the skill assumes does not exist. That is recorded rather than
papered over with an empty file.)

The bullet length limit is enforced here rather than eyeballed, because a
highlights file that exceeds it is rejected at upload and the failure is silent
until then.

Run: python scripts/build_phase7_9_artifacts.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "outputs" / "paper"
SUB = ROOT / "outputs" / "submission"

HIGHLIGHTS = [
    "21 literature-derived rules for eye disease tested in 8 ageing cohorts",
    "Age-cataract pooled OR 1.99/decade, I-squared 99.2%, more heterogeneous "
    "than any rule",
    "NHANES: self-reported cataract tracks age at OR 4.27, objective acuity 1.32",
    "Self-report measures having been diagnosed, so pooling it pools access "
    "to care",
    "Report prevalence by cohort beside pooled estimates of self-reported "
    "outcomes",
]

DATA_AVAILABILITY = """# Data availability

**No new data were generated.** This study reanalyses existing third-party
population surveys. None of the source data may be redistributed by us, so the
statement below gives the access route for each rather than a repository link.

## Cohort data

| Cohort | Access route |
|---|---|
| SHARE | Registration and free access for scientific use: share-project.org |
| HRS | Registration and free access: hrs.isr.umich.edu |
| ELSA | Application to the UK Data Service: ukdataservice.ac.uk |
| KLoSA | Application to the Korea Employment Information Service |
| LASI | Application to the Gateway to Global Aging Data (g2aging.org) |
| MHAS | Registration and free access: mhasweb.org |
| CLHLS | Open deposit, DOI 10.18170/DVN/MKB1LF (Peking University Open Research Data) |
| CRELES | Open deposit, DOIs 10.7910/DVN/7AUOAO and 10.3886/icpsr26681.v2 |

KLoSA has no citable public deposit; access is by application to the data owner,
and the Data availability statement says so rather than implying a DOI exists.

## Validation data

NHANES 2005-2006 and 2007-2008 (vision examination and questionnaire files) and
KNHANES and CHARLS are public: cdc.gov/nchs/nhanes, knhanes.kdca.go.kr, and
charls.pku.edu.cn respectively.

## Code and derived data

Analysis code, the audit trail, the cohort frames (derived variables only,
containing no redistributable source records) and an archived snapshot with a
DOI will be deposited on acceptance. **The deposit DOI must be inserted here
before submission** -- it is not yet minted.

## What cannot be shared

Individual-level records from the registered-access cohorts cannot be
redistributed under their terms of use. The derived frames contain recoded
variables and person identifiers that are cohort-specific; they are shared for
reproducibility of the analysis, not as a substitute for the source data.
"""

GRAPHICAL_ABSTRACT = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500" width="900" height="500"
     font-family="Helvetica, Arial, sans-serif">
  <rect width="900" height="500" fill="#ffffff"/>

  <text x="450" y="40" text-anchor="middle" font-size="21" font-weight="bold"
        fill="#111111">Pooled exposome estimates do not transport between populations</text>
  <text x="450" y="64" text-anchor="middle" font-size="14" fill="#4D4D4D">
    21 literature-derived rules, 8 ageing cohorts, 598,386 person-waves
  </text>

  <!-- Step 1: rule construction -->
  <rect x="40" y="96" width="240" height="150" rx="8" fill="#F2F7FB"
        stroke="#0072B2" stroke-width="1.5"/>
  <text x="160" y="122" text-anchor="middle" font-size="14" font-weight="bold"
        fill="#0072B2">1. Rules from the literature</text>
  <text x="60" y="148" font-size="12" fill="#333333">21 exposure-outcome rules</text>
  <text x="60" y="170" font-size="12" fill="#333333">citation verification</text>
  <text x="60" y="188" font-size="12" fill="#333333">regraded evidence levels</text>
  <text x="60" y="206" font-size="12" fill="#333333">to A1 / B15 / C5</text>
  <text x="60" y="224" font-size="12" fill="#333333">(final grading)</text>

  <!-- arrow -->
  <line x1="285" y1="171" x2="325" y2="171" stroke="#4D4D4D" stroke-width="1.5"
        marker-end="url(#a)"/>

  <!-- Step 2: cohorts -->
  <rect x="330" y="96" width="240" height="150" rx="8" fill="#F2F7FB"
        stroke="#0072B2" stroke-width="1.5"/>
  <text x="450" y="122" text-anchor="middle" font-size="14" font-weight="bold"
        fill="#0072B2">2. Tested in 8 cohorts</text>
  <text x="350" y="148" font-size="12" fill="#333333">SHARE HRS ELSA KLoSA</text>
  <text x="350" y="168" font-size="12" fill="#333333">LASI MHAS CLHLS CRELES</text>
  <text x="350" y="194" font-size="12" fill="#333333">18 of 168 (rule x cohort)</text>
  <text x="350" y="212" font-size="12" fill="#333333">cells were feasible</text>
  <text x="350" y="234" font-size="12" font-weight="bold" fill="#D55E00">
    only 6 of 21 rules testable</text>

  <!-- arrow -->
  <line x1="575" y1="171" x2="615" y2="171" stroke="#4D4D4D" stroke-width="1.5"
        marker-end="url(#a)"/>

  <!-- Step 3: result -->
  <rect x="620" y="96" width="240" height="150" rx="8" fill="#FDF3EE"
        stroke="#D55E00" stroke-width="1.5"/>
  <text x="740" y="122" text-anchor="middle" font-size="14" font-weight="bold"
        fill="#D55E00">3. Estimates do not carry</text>
  <text x="640" y="148" font-size="12" fill="#333333">I-squared 79.5-93.8%</text>
  <text x="640" y="168" font-size="12" fill="#333333">prediction intervals span</text>
  <text x="640" y="186" font-size="12" fill="#333333">the null for every rule</text>
  <text x="640" y="212" font-size="12" fill="#333333">no rule describes any</text>
  <text x="640" y="230" font-size="12" fill="#333333">single studied population</text>

  <!-- Positive control -->
  <rect x="40" y="286" width="390" height="176" rx="8" fill="#F1F8F5"
        stroke="#009E73" stroke-width="1.5"/>
  <text x="235" y="312" text-anchor="middle" font-size="14" font-weight="bold"
        fill="#009E73">Positive control: even age does not transport</text>
  <text x="60" y="340" font-size="12" fill="#333333">Age to cataract, pooled OR 1.99 per decade</text>
  <text x="60" y="360" font-size="12" fill="#333333">I-squared 99.2% - MORE heterogeneous than</text>
  <text x="60" y="378" font-size="12" fill="#333333">any exposure rule</text>
  <text x="60" y="404" font-size="12" fill="#333333">per cohort: SHARE 2.25, ELSA 3.14, LASI 2.16,</text>
  <text x="60" y="422" font-size="12" fill="#333333">CRELES 1.81, CLHLS 1.15</text>
  <text x="60" y="448" font-size="12" font-weight="bold" fill="#009E73">
    So the constraint is the outcome definition, not the sample size</text>

  <!-- Mechanism -->
  <rect x="470" y="286" width="390" height="176" rx="8" fill="#FFFBF0"
        stroke="#E69F00" stroke-width="1.5"/>
  <text x="665" y="312" text-anchor="middle" font-size="14" font-weight="bold"
        fill="#B87700">Why: the item measures diagnosis</text>
  <text x="490" y="340" font-size="12" fill="#333333">NHANES 2005-2008, same people measured twice</text>
  <text x="490" y="364" font-size="12" fill="#333333">self-reported cataract vs age: OR 4.27</text>
  <text x="490" y="384" font-size="12" fill="#333333">objective near acuity vs age: OR 1.32</text>
  <text x="490" y="410" font-size="12" fill="#333333">Self-report is NOT the weaker instrument - it</text>
  <text x="490" y="428" font-size="12" fill="#333333">tracks age more strongly, through diagnosis</text>
  <text x="490" y="452" font-size="12" font-weight="bold" fill="#B87700">
    Pooling it pools access to care</text>

  <defs>
    <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
            markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#4D4D4D"/>
    </marker>
  </defs>
</svg>
"""


def main() -> int:
    # Highlights, with the 85-character rule enforced rather than assumed.
    bad = [(i + 1, b, len(b)) for i, b in enumerate(HIGHLIGHTS) if len(b) > 85]
    lines = [
        "# Highlights",
        "",
        f"*{len(HIGHLIGHTS)} bullet points, each at most 85 characters "
        f"(Elsevier limit). Longest: {max(len(b) for b in HIGHLIGHTS)} "
        f"characters.*",
        "",
    ]
    for b in HIGHLIGHTS:
        lines.append(f"* {b}")
    lines += ["", "## Character counts", "",
              "| # | Characters | Bullet |", "|---|---|---|"]
    for i, b in enumerate(HIGHLIGHTS, 1):
        lines.append(f"| {i} | {len(b)} | {b} |")
    (PAPER / "highlights.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"highlights.md: {len(HIGHLIGHTS)} bullets, "
          f"longest {max(len(b) for b in HIGHLIGHTS)} chars")
    for i, b, n in bad:
        print(f"  OVER LIMIT: bullet {i} is {n} chars: {b}")

    (SUB / "data_availability.md").write_text(DATA_AVAILABILITY, encoding="utf-8")
    print(f"data_availability.md: {len(DATA_AVAILABILITY):,} B")

    (SUB / "graphical_abstract.svg").write_text(GRAPHICAL_ABSTRACT, encoding="utf-8")
    # The skill's own scaffold ships placeholder tokens; shipping it unchanged
    # would put literal braces in front of a reviewer. Verify none survive.
    assert "{{" not in GRAPHICAL_ABSTRACT, "unfilled placeholder in the SVG"
    print(f"graphical_abstract.svg: {len(GRAPHICAL_ABSTRACT):,} B, "
          f"no unfilled placeholders")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
