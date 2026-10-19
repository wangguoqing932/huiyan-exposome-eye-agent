#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebuild Table 5 from the corrected heterogeneity output.

Changes carried in from review:
  * prediction intervals now use t on k-2 df, not the normal quantile, so the
    intervals are 2-3x wider (r02: 0.30-12.63 rather than 0.84-4.57) and are not
    computable at all for k=2 (r12, r13);
  * the subgroup column marks the k=2 rows as the same test as Q;
  * E-values are the corrected ones (odds ratio converted to risk ratio);
  * leave-one-out is stated.

Run: python scripts/rebuild_table5.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = ROOT / "outputs" / "cohorts" / "cohort_heterogeneity.json"
OUT = ROOT / "outputs" / "tables" / "table5_heterogeneity.md"

EPS = [
    ("r10 smoking-cataract in CLHLS", "1.87 (CI bound 1.47)"),
    ("r10 smoking-cataract in SHARE", "1.43 (1.22)"),
    ("r12 alcohol-cataract in CLHLS", "1.66 (1.27)"),
    ("r02 diabetes-cataract in CLHLS", "4.51 (3.35)"),
]


def main() -> int:
    h = json.loads(H.read_text(encoding="utf-8"))
    head = ("| Rule | k | Pooled OR (95% CI) | I² | τ² | Q p | Prediction "
            "interval | Subgroup test |")
    lines = [
        "# Table 5. Between-cohort heterogeneity and prediction intervals "
        "(cohort external-validation layer)",
        "",
        "Random-effects pooling with REML τ², computed in Python/SciPy (no "
        "external meta-analysis package), so the estimator is stated explicitly.",
        "",
        "**The prediction interval is computed with t on k−2 degrees of freedom, "
        "not the normal quantile** (Higgins, Thompson & Spiegelhalter 2009). An "
        "earlier version of this table used 1.96 throughout, which made every "
        "interval 2–3× too narrow: r02's became 0.30–12.63 rather than 0.84–4.57. "
        "**For the two-cohort rules (r12, r13) no prediction interval exists at "
        "all** — t on 0 degrees of freedom is undefined — and none is reported. "
        "The interval is the range in which a NEW cohort's true effect would be "
        "expected to fall.",
        "",
        head,
        "|---|---|---|---|---|---|---|---|",
    ]
    for rid, r in h["by_rule"].items():
        if "pooled_OR" not in r:
            lines.append(f"| {rid} | {r['k']} | single cohort | — | — | — | — | "
                         f"not applicable |")
            continue
        k = r["k"]
        pi = r.get("prediction_interval")
        pi_s = (f"{pi[0]:.2f}–{pi[1]:.2f}" if pi else "**not computable (k<3)**")
        sd = r.get("subgroup_by_region") or {}
        if not sd.get("testable"):
            sub = "not applicable"
        elif k == 2:
            sub = "same test as Q p (see note)"
        else:
            p = sd["p_between"]
            sub = f"p {'<0.0001' if p < 1e-4 else f'{p:.4f}'}"
        lines.append(
            f"| {rid} | {k} | {r['pooled_OR']:.2f} "
            f"({r['pooled_ci'][0]:.2f}–{r['pooled_ci'][1]:.2f}) | "
            f"{r['I2_percent']:.1f}% | {r['tau2']:.4f} | "
            f"{'<0.0001' if r['Q_p'] < 1e-4 else f'{r[chr(81)+chr(95)+chr(112)]:.4f}'} | "
            f"{pi_s} | {sub} |")
    lines += [
        "",
        "**I² must be read alongside τ².** On the log-odds-ratio scale the fitted "
        "τ² corresponds to cross-cohort ratio differences of only about 1.2× to "
        "2.1×. The high I² is driven by SHARE's very small standard error (its "
        "confidence intervals are an order of magnitude narrower than the other "
        "cohorts'), so using I² alone as a rejection criterion would partly be a "
        "sample-size penalty. Both are therefore reported.",
        "",
        "**Note on the subgroup column.** The regional subgroups (Europe / Asia / "
        "Americas) were NOT pre-specified; they were constructed after the primary "
        "analysis and are reported as post hoc. Pooling within subgroup uses "
        "random-effects weights — an earlier version used fixed-effect weights, "
        "which at this level of heterogeneity made Europe 93% SHARE by weight and "
        "produced a spurious p < 0.0001 for r10; the corrected value is p = 0.45. "
        "For the two-cohort rules the subgroup test is not an independent test: "
        "with one cohort per group the between-group statistic is the same "
        "quantity as the overall Q (r12 both 0.027334; r13 both 0.027220).",
        "",
        "**E-values** (minimum confounder strength that could explain the estimate "
        "away), computed after converting each odds ratio to a risk ratio, since "
        "cataract is not rare in these cohorts (unexposed risk 8.8%–21.1%):",
        "",
    ]
    lines += [f"* {a}: {b}" for a, b in EPS]
    lines += [
        "",
        "**Leave-one-cohort-out (Supplementary S4) qualifies the r10 row.** "
        "Removing SHARE reduces I² from 91.0% to 0.0% and moves the pooled "
        "estimate to 0.747 (0.66–0.84), so r10's heterogeneity is driven by one "
        "cohort rather than distributed across them; the remaining three cohorts "
        "agree with each other and their pooled estimate excludes unity.",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("Table 5 rebuilt with t-based prediction intervals")
    for ln in lines[7:16]:
        print("  " + ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
