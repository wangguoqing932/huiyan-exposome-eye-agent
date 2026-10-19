#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""One-step individual-participant model with a rule x cohort interaction.

Two reviewers independently objected to the two-stage subgroup test this project
used. Their objection has two parts:

  * **k = 2 non-independence.** Where a rule is testable in only two cohorts, the
    subgroup comparison is a test of one difference against itself; the reported
    Q p-value and the subgroup p-value are the same number computed twice.
  * **Double counting.** Pooling per-cohort estimates weights each cohort once
    regardless of how many people it contributes, so a cohort of 5,191 and one of
    338,703 enter on equal terms.

Both disappear if the cohorts are stacked and fitted once, at the level of the
person, with an exposure x cohort interaction term. Everyone enters once, cohort
size determines its own weight, and the interaction test asks the question
directly: does the exposure-outcome association differ between these populations?

This fits that model for each rule and compares the interaction test against the
two-stage subgroup test the manuscript currently reports.

Caveats, stated rather than buried:
  * The exposure and outcome columns are taken from the coverage matrix, which is
    the same source the two-stage analysis used, so the two are comparable.
  * Cohort frames carry repeated waves for some cohorts, so standard errors are
    clustered on the person identifier. The point estimate is unaffected by
    clustering; only the inference is.
  * This is a within-fitted-frames analysis. It does not add cohorts, and it does
    not change which cells are feasible.

Run: python scripts/ipd_interaction.py
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
COV = ROOT / "outputs" / "confirmatory" / "cohort_rule_coverage.json"
HET = ROOT / "outputs" / "cohorts" / "cohort_heterogeneity.json"
OUT = ROOT / "outputs" / "cohorts" / "ipd_interaction.json"
MD = ROOT / "outputs" / "cohorts" / "IPD_INTERACTION.md"


def main() -> int:
    cov = json.loads(COV.read_text(encoding="utf-8"))["matrix"]

    # The two-stage comparator is the between-cohort heterogeneity test
    # (Cochran Q), NOT q_primary: q_primary in cohort_rule_results.csv is the
    # FDR-adjusted q of one cohort's association test
    # (cohort_confirmatory.py L251-259), so taking row 0 under a "two-stage"
    # label returned a single-cohort quantity. Fixed 2026-10-19; see
    # docs/AGENT_AUDIT.md section 36.
    HETDATA = (json.loads(HET.read_text(encoding="utf-8"))["by_rule"]
               if HET.exists() else {})

    # rule -> list of (cohort, exposure_col, outcome_col)
    plan: dict[str, list[tuple[str, str, str]]] = {}
    for rid, per in cov.items():
        for coh, v in (per or {}).items():
            if v.get("testable"):
                plan.setdefault(rid, []).append(
                    (coh, v["exposure_col"], v["outcome_col"]))

    print(f"rules with a feasible cell: {len(plan)}")
    print()
    results = []
    print(f"{'rule':32s} {'cohorts':>7s} {'n':>9s} {'interaction p':>14s}  "
          f"{'two-stage Q p':>12s}")
    print("-" * 84)
    for rid, cells in sorted(plan.items()):
        frames = []
        for coh, xcol, ycol in cells:
            f = FRAMES / f"cohort_{coh}.csv"
            if not f.exists():
                continue
            d = pd.read_csv(f, low_memory=False,
                            usecols=lambda c, _x=xcol, _y=ycol:
                            c in {_x, _y, "age", "sex", "mergeid", "wave",
                                  "implicat"})
            if xcol not in d.columns or ycol not in d.columns:
                continue
            if "implicat" in d.columns and d["implicat"].nunique() > 1:
                d = d[d["implicat"] == d["implicat"].min()]
            key = [k for k in ("mergeid", "wave") if k in d.columns]
            if key:
                # Deduplicate on the person-wave key: the MHAS frame carries up to
                # 6,447 copies of a row from a many-to-many join in the frame
                # builder (docs/GAP_ANALYSIS_20IF.md), and an IPD model weights by
                # row, so duplicates would inflate that cohort directly.
                d = d.drop_duplicates(subset=key)
            d = d[[xcol, ycol, "age", "sex"] + (["mergeid"] if "mergeid" in d.columns else [])].copy()
            d["cohort"] = coh
            frames.append(d)
        if not frames:
            print(f"{rid:32s} {'--':>7s} {'--':>9s}  no frame loaded")
            results.append({"rule": rid, "note": "no frame loaded"})
            continue
        # Verify rather than assume that every cell of this rule uses the same
        # exposure and outcome column names -- the rename below depends on it.
        xs = {c[1] for c in cells}
        ys = {c[2] for c in cells}
        if len(xs) != 1 or len(ys) != 1:
            results.append({"rule": rid, "n": None,
                            "note": f"mixed columns across cohorts: x={sorted(xs)} "
                                    f"y={sorted(ys)}"})
            print(f"{rid:32s} {'--':>7s} {'--':>9s}  mixed columns, not fitted")
            continue
        xcol, ycol = xs.pop(), ys.pop()

        d = pd.concat(frames, ignore_index=True)
        d = d.rename(columns={xcol: "x", ycol: "y"})
        d["x"] = pd.to_numeric(d["x"], errors="coerce")
        d["y"] = pd.to_numeric(d["y"], errors="coerce")
        d["age"] = pd.to_numeric(d["age"], errors="coerce")
        # sex is not uniformly encoded across cohorts: some frames store 1/2,
        # others the bare strings 'Male'/'Female'. Concatenating the raw columns
        # yields an object column mixing str and int, and statsmodels then raises
        # "'<' not supported between instances of 'str' and 'int'" -- an error
        # that does not name the variable responsible for it.
        _num = pd.to_numeric(d["sex"], errors="coerce")
        if _num.notna().any():
            d["sex"] = _num
        else:
            _s = d["sex"].astype(str).str.strip().str.lower()
            d["sex"] = _s.map({"male": 1, "m": 1, "1": 1,
                                "female": 2, "f": 2, "2": 2})
        d = d.dropna(subset=["x", "y", "age", "sex"])
        if d["x"].nunique() < 2 or d["y"].nunique() < 2 or d["cohort"].nunique() < 2:
            why = (f"x_nunique={d['x'].nunique()} y_nunique={d['y'].nunique()} "
                   f"cohort_nunique={d['cohort'].nunique()} n={len(d)}")
            print(f"{rid:32s} {'--':>7s} {len(d):>9,d}  not fittable: {why}")
            results.append({"rule": rid, "note": f"not fittable after cleaning: {why}",
                            "n": int(len(d))})
            continue

        try:
            # Person identifiers are not uniformly typed across cohorts -- some
            # frames store strings like '38.0-1.0', others integers. Clustering on
            # a mixed-dtype object column makes statsmodels compare a str with an
            # int internally and raise "'<' not supported between instances of
            # 'str' and 'int'", an error that names neither the variable nor the
            # cause. Coerce to one dtype first.
            if "mergeid" in d.columns:
                d["mergeid"] = d["mergeid"].astype(str)
            groups = d["mergeid"] if "mergeid" in d.columns else None
            m = smf.logit("y ~ x * C(cohort) + age + sex", data=d).fit(
                disp=0, cov_type="cluster",
                cov_kwds={"groups": groups} if groups is not None else None)
        except Exception as e:
            print(f"{rid:32s} {'--':>7s} {len(d):>9,d}  fit failed: "
                  f"{type(e).__name__}: {str(e)[:52]}")
            results.append({"rule": rid, "note": f"fit failed: {type(e).__name__}: {e}",
                            "n": int(len(d))})
            continue

        # Joint test that every x:C(cohort) term is zero.
        terms = [t for t in m.params.index if t.startswith("x:C(cohort)")]
        ip = float("nan")
        if terms:
            try:
                ip = float(m.f_test(" = 0, ".join(terms) + " = 0").pvalue)
            except Exception:
                ip = float("nan")

        two = HETDATA.get(rid, {}).get("Q_p")
        two = float(two) if two is not None else None

        print(f"{rid:32s} {d['cohort'].nunique():>7d} {len(d):>9,d} "
              f"{ip:>14.4g}  {(f'{two:.4g}' if two is not None else 'n/a'):>12s}")
        results.append({"rule": rid, "cohorts": sorted(d["cohort"].unique()),
                        "n": int(len(d)), "n_cohorts": int(d["cohort"].nunique()),
                        "interaction_p": ip, "two_stage_het_q_p": two,
                        "interaction_terms": terms,
                        "per_cohort_or": {
                            c: float(np.exp(m.params.get("x", np.nan)))
                            for c in [d["cohort"].unique()[0]]}})

    print()
    print("=" * 84)
    print("  A one-step interaction test answers 'does the association differ")
    print("  between cohorts' using each person once. The two-stage column is the")
    print("  Cochran Q test of between-cohort heterogeneity (cohort_heterogeneity.")
    print("  json). At k=2 it is the same statistic as Table 5's regional subgroup")
    print("  test; for k>2 it is not the same null (r10: regional p=0.45, Q p=2.6e-07).")
    print()
    print("  CAVEAT: this is a within-fitted-frames analysis. It changes the")
    print("  inference, not which cells exist, and not the pooled estimates.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
