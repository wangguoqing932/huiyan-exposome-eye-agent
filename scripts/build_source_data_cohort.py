#!/usr/bin/env python
"""Source data for the cohort-layer figure (analysis_plan section 19 results).

Produces exactly ONE CSV per contract, as the renderer requires: panels may
select rows but must never re-filter a different file.

  outputs/figures/source_data/figure8_cohort_transportability.csv

Two panels read the same file:
  * panel A (heatmap)  rows=cohort, cols=rule, cells=state_code
        state_code:  1 = replicated, 0 = uninformative, -1 = contradicted
        A diverging scale is the honest encoding for a three-state outcome --
        collapsing "uninformative" into the same colour as either extreme
        would visually assert a direction the data does not support.
  * panel B (forest)   method = "<rule> · <cohort>", estimate = odds ratio,
                       ci_low / ci_high, dataset = cohort

Only the 18 pre-registered confirmatory pairs are included; the exploratory
sweep is reported in the results file, not in this figure.

Run: python scripts/build_source_data_cohort.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs" / "cohorts" / "cohort_rule_results.csv"
OUT = ROOT / "outputs" / "figures" / "source_data"

STATE_CODE = {"replicated": 1, "uninformative": 0, "contradicted": -1}

# short display labels, kept stable so the contract's expectations hold
RULE_SHORT = {
    "r02_hyperglycemia_x_cataract": "r02 hyperglycaemia→cataract",
    "r10_smoking_x_cataract": "r10 smoking→cataract",
    "r11_smoking_x_amd_late": "r11 smoking→late AMD",
    "r12_alcohol_x_cataract": "r12 alcohol→cataract",
    "r13_bmi_x_cataract": "r13 BMI→cataract",
    "r20_smoking_x_vi_mod_severe": "r20 smoking→vision impairment",
}
RULE_ORDER = list(RULE_SHORT)
COHORT_ORDER = ["SHARE", "HRS", "ELSA", "KLoSA", "LASI", "MHAS", "CLHLS", "CRELES"]


def main() -> int:
    d = pd.read_csv(SRC, low_memory=False)
    c = d[d["rule_relevant"].astype(bool)].copy()
    if c.empty:
        print("no confirmatory rows")
        return 1

    c["cohort"] = pd.Categorical(c["cohort"], COHORT_ORDER, ordered=True)
    c["rule_label"] = c["rule_id"].map(RULE_SHORT).fillna(c["rule_id"])
    c["rule_label"] = pd.Categorical(c["rule_label"],
                                     [RULE_SHORT[r] for r in RULE_ORDER],
                                     ordered=True)
    # The forest renderer colours rows by the prefix BEFORE the first ' · ' and
    # then appends ' · <dataset>' to the row label. Putting the THREE-STATE
    # first therefore does two useful things at once: it colour-codes rows by
    # state (so "uninformative" is never painted like either extreme, which the
    # contract requires), and it avoids the duplicated-cohort label that the
    # first render produced ("... · SHARE · SHARE") because the cohort is no
    # longer inside `method`.
    c["method"] = (c["three_state"].astype(str) + " · "
                   + c["rule_label"].astype(str))
    c["state_code"] = c["three_state"].map(STATE_CODE)
    c = c.sort_values(["rule_label", "cohort"])

    out = pd.DataFrame({
        "cohort": c["cohort"].astype(str),
        "rule": c["rule_label"].astype(str),
        "state_label": c["three_state"].astype(str),
        "state_code": c["state_code"],
        "three_state": c["three_state"],
        "method": c["method"],
        "dataset": c["cohort"].astype(str),
        "estimate": c["odds_ratio"],
        "ci_low": c["ci_low"],
        "ci_high": c["ci_high"],
        "n": c["n"],
        "q_rule": c["q_rule"],
        "q_exploratory": c["q"],
        # columns the stacked_bar renderer looks for BY NAME: it takes the case
        # from case_id, the stack layer from layer, and the value from the
        # contract's x_axis. count=1 per pair makes the stack a plain tally of
        # replicated / uninformative / contradicted per rule.
        "case_id": c["rule_label"].astype(str),
        "layer": c["three_state"].astype(str),
        "count": 1,
    })
    OUT.mkdir(parents=True, exist_ok=True)
    fp = OUT / "figure8_cohort_transportability.csv"
    out.to_csv(fp, index=False, encoding="utf-8")

    print(f"rows={len(out)}  cohorts={out['cohort'].nunique()}  "
          f"rules={out['rule'].nunique()}")
    print(f"three-state: {out['three_state'].value_counts().to_dict()}")
    print(out[["cohort", "rule", "estimate", "ci_low", "ci_high", "q_rule",
               "three_state"]].to_string(index=False))
    print(f"-> {fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
