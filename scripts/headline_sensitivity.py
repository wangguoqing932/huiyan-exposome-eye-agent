#!/usr/bin/env python
"""Headline sensitivity to the RULE-SET definition (R11 2026-10-15).

Why
---
Two rule-set decisions materially change the headline numbers and must not be
buried:

  * r22_bmi_x_retinopathy — its own rationale states it was added after seeing
    the NHANES result ("规则纳入属数据驱动的探索性扩展"), i.e. test-set leakage.
    It replicates in KNHANES.
  * r01_uric_acid_x_cataract — flagged `negative_control: true`, which removes
    it from the headline denominator even though it is a risk_up claim.

Rather than pick one definition, this script recomputes the confirmatory metrics
under every defensible rule-set definition and writes the comparison table, so
the choice is explicit and reviewable.

Run: PYTHONUTF8=1 python scripts/headline_sensitivity.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from huiyan_agent.risk_rules import load_rules          # noqa: E402

OUT = ROOT / "outputs" / "confirmatory"
TAB = ROOT / "outputs" / "tables"

LEAKY = {"r22_bmi_x_retinopathy"}
NEG_CONTROL = {"r01_uric_acid_x_cataract"}


def rule_meta():
    rules = load_rules()
    return ({r.id: r.evidence_level for r in rules},
            {r.id: bool(r.negative_control) for r in rules})


def hit_ids(cell) -> list[str]:
    return [x.strip() for x in str(cell).split(",") if x.strip() and x.strip() != "nan"]


def metrics(df: pd.DataFrame, keep, label: str) -> dict:
    """keep(rule_ids: list[str]) -> bool  decides whether the pair is in the family."""
    d = df[df["status"] == "tested"].copy()
    d = d[d["rule_ids"].map(lambda c: bool(hit_ids(c)) and keep(hit_ids(c)))]
    n = len(d)
    rep = int((d["gold3"] == "replicated").sum())
    con = int((d["gold3"] == "contradicted").sum())
    uninf = int((d["gold3"] == "uninformative").sum())
    prec_decl = round(rep / (rep + con), 3) if (rep + con) else None
    prec_cons = round(rep / n, 3) if n else None
    return {
        "rule_set": label, "rule_pairs_tested": n, "replicated": rep,
        "contradicted": con, "uninformative": uninf,
        "precision_rule_declared": prec_decl, "precision_rule_uninf_as_fp": prec_cons,
        "informative_nulls": None,   # filled from the power table when available
    }


def main() -> int:
    lvl, nc = rule_meta()
    keepers = {
        "all_rules (current)": lambda ids: True,
        "exclude_r22_test_set_leakage": lambda ids: not any(i in LEAKY for i in ids),
        "exclude_negative_control_r01": lambda ids: not any(i in NEG_CONTROL for i in ids),
        "exclude_both_r22_and_r01": lambda ids: not any(i in (LEAKY | NEG_CONTROL) for i in ids),
        "A_level_only": lambda ids: all(lvl.get(i) == "A" for i in ids),
        "A_and_B_level_only": lambda ids: all(lvl.get(i) in ("A", "B") for i in ids),
        "exclude_C_level": lambda ids: all(lvl.get(i) in ("A", "B") for i in ids),
    }

    rows = []
    for ds, csv in (("NHANES", "nhanes_confirmatory.csv"),
                    ("KNHANES", "knhanes_confirmatory.csv")):
        p = OUT / csv
        if not p.exists():
            print(f"[sens] missing {csv}")
            continue
        df = pd.read_csv(p)
        if "rule_ids" not in df.columns:
            print(f"[sens] {csv} has no rule_ids")
            continue
        for label, keep in keepers.items():
            r = metrics(df, keep, label)
            r["dataset"] = ds
            rows.append(r)

    out = pd.DataFrame(rows)[["dataset", "rule_set", "rule_pairs_tested", "replicated",
                              "contradicted", "uninformative",
                              "precision_rule_declared", "precision_rule_uninf_as_fp"]]
    TAB.mkdir(parents=True, exist_ok=True)
    out.to_csv(TAB / "headline_sensitivity.csv", index=False, encoding="utf-8-sig")

    print("=" * 96)
    print("HEADLINE SENSITIVITY TO THE RULE-SET DEFINITION")
    print("=" * 96)
    for ds in out["dataset"].unique():
        sub = out[out["dataset"] == ds]
        print(f"\n[{ds}]")
        print(f"  {'rule set':34s}{'tested':>7s}{'rep':>5s}{'con':>5s}{'uninf':>7s}"
              f"{'prec_decl':>11s}{'prec_cons':>11s}")
        for r in sub.itertuples():
            f = lambda v: "-" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.3f}"
            print(f"  {r.rule_set:34s}{r.rule_pairs_tested:>7d}{r.replicated:>5d}"
                  f"{r.contradicted:>5d}{r.uninformative:>7d}"
                  f"{f(r.precision_rule_declared):>11s}{f(r.precision_rule_uninf_as_fp):>11s}")

    payload = {
        "generated": "2026-10-15 (R11)",
        "leaky_rules": sorted(LEAKY),
        "negative_controls": sorted(NEG_CONTROL),
        "note": ("r22 is documented in its own rationale as added after seeing the "
                 "NHANES result; it replicates in KNHANES. Dropping it is the "
                 "conservative choice. Both rows are reported so the decision is "
                 "explicit rather than buried."),
        "table": out.to_dict(orient="records"),
    }
    (OUT / "headline_sensitivity.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[sens] -> {TAB/'headline_sensitivity.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
