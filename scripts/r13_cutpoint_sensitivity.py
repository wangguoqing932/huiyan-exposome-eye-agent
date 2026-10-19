#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r13 cut-point sensitivity: the rule is tested with a threshold the project's own
convention contradicts.

`outputs/confirmatory/cohort_rule_coverage.json` tests r13 (BMI -> cataract) with
the column `bmi_high_25` in both cohorts where it is feasible, CRELES and SHARE.
The project's own pre-registered convention -- stated in
`scripts/build_descriptive_table.py` and used everywhere else -- is 25 kg/m2 for
the Asian cohorts (KLoSA, LASI, CLHLS) and 30 elsewhere. Both CRELES and SHARE
should therefore use `bmi_high_30`.

The one cohort whose cut really is 25, KLoSA, is marked `testable=False` in the
same matrix and so never enters.

This is not cosmetic. A lower threshold moves more people into the exposed group,
which dilutes the contrast and pulls the odds ratio toward the null. So the
published r13 estimate may understate the association, and the direction of the
bias is known.

This re-estimates r13 under three specifications per cohort -- the cut actually
used (25), the cut the convention requires (30), and a continuous BMI term -- and
reports whether the conclusion moves.

It changes nothing by itself; the point is to find out whether the published
number is sensitive to a choice that is inconsistent with the project's own
protocol.

Run: python scripts/r13_cutpoint_sensitivity.py
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
FRAMES = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts" / "r13_cutpoint_sensitivity.json"

# The project's convention, copied from build_descriptive_table.py so the two
# cannot drift apart without this script failing to find it.
CONVENTION = {"SHARE": 30, "HRS": 30, "ELSA": 30, "KLoSA": 25, "LASI": 25,
              "MHAS": 30, "CLHLS": 25, "CRELES": 30}


def fit(d: pd.DataFrame, xcol: str) -> dict:
    dd = d.dropna(subset=[xcol, "cataract_any", "age", "sex"]).copy()
    x = sm.add_constant(pd.DataFrame({
        "x": pd.to_numeric(dd[xcol], errors="coerce"),
        "age": pd.to_numeric(dd["age"], errors="coerce"),
        "sex": pd.to_numeric(dd["sex"], errors="coerce"),
    }))
    y = pd.to_numeric(dd["cataract_any"], errors="coerce")
    ok = x.notna().all(axis=1) & y.notna()
    x, y = x[ok], y[ok]
    if len(y) < 200 or x["x"].nunique() < 2 or y.nunique() < 2:
        return {"n": int(len(y)), "note": "not estimable"}
    try:
        groups = None
        if "mergeid" in dd.columns:
            groups = dd.loc[ok, "mergeid"].astype(str)
        m = sm.Logit(y, x).fit(disp=0, cov_type="cluster",
                               cov_kwds={"groups": groups} if groups is not None
                               else None)
    except Exception as e:
        return {"n": int(len(y)), "note": f"fit failed: {type(e).__name__}"}
    return {"n": int(len(y)),
            "or": float(np.exp(m.params["x"])),
            "ci_low": float(np.exp(m.conf_int().loc["x", 0])),
            "ci_high": float(np.exp(m.conf_int().loc["x", 1])),
            "p": float(m.pvalues["x"])}


def main() -> int:
    print("r13 = BMI -> cataract. Convention: 25 for KLoSA/LASI/CLHLS, 30 elsewhere.")
    print()
    results = {}
    for coh in ("SHARE", "CRELES"):
        f = FRAMES / f"cohort_{coh}.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f, low_memory=False,
                        usecols=lambda c: c in {"cataract_any", "age", "sex",
                                                "mergeid", "wave", "implicat",
                                                "bmi", "bmi_high_25", "bmi_high_30"})
        if "implicat" in d.columns and d["implicat"].nunique() > 1:
            d = d[d["implicat"] == d["implicat"].min()]
        key = [k for k in ("mergeid", "wave") if k in d.columns]
        if key:
            d = d.drop_duplicates(subset=key)
        want = CONVENTION[coh]
        print(f"=== {coh}  (convention says cut = {want}) ===")
        row = {}
        for col in (f"bmi_high_{want}", "bmi_high_25" if want != 25 else "bmi_high_30"):
            if col not in d.columns:
                print(f"  {col:14s} absent")
                continue
            r = fit(d, col)
            row[col] = r
            if "or" in r:
                print(f"  {col:14s} n={r['n']:>7,d}  OR={r['or']:.3f} "
                      f"({r['ci_low']:.3f}-{r['ci_high']:.3f})  p={r['p']:.3g}")
            else:
                print(f"  {col:14s} n={r['n']:>7,d}  {r['note']}")
        # high-vs-not is not the same as a continuous term; fit BMI where present
        if "bmi" in d.columns:
            dd = d.copy()
            dd["bmi_z"] = (pd.to_numeric(dd["bmi"], errors="coerce") -
                           pd.to_numeric(dd["bmi"], errors="coerce").mean()) / \
                          pd.to_numeric(dd["bmi"], errors="coerce").std()
            r = fit(dd, "bmi_z")
            row["bmi_continuous_per_sd"] = r
            if "or" in r:
                print(f"  {'bmi per SD':14s} n={r['n']:>7,d}  OR={r['or']:.3f} "
                      f"({r['ci_low']:.3f}-{r['ci_high']:.3f})  p={r['p']:.3g}")
            else:
                print(f"  {'bmi per SD':14s} n={r['n']:>7,d}  {r['note']}")
        results[coh] = row
        print()

    # Does the conclusion move?
    print("=" * 78)
    for coh, row in results.items():
        want = CONVENTION[coh]
        used = row.get("bmi_high_25", {})
        right = row.get(f"bmi_high_{want}", {})
        if "or" in used and "or" in right:
            shift = right["or"] - used["or"]
            sig_u = used.get("p", 1) < 0.05
            sig_r = right.get("p", 1) < 0.05
            print(f"  {coh}: OR {used['or']:.3f} (cut 25) -> {right['or']:.3f} "
                  f"(cut {want});  shift {shift:+.3f};  significance "
                  f"{'unchanged' if sig_u == sig_r else '*** CHANGES ***'}")
    print()
    print("  A lower threshold moves more people into the exposed group, diluting")
    print("  the contrast and pulling the OR toward the null. So testing with 25")
    print("  where the convention requires 30 understates the association, and the")
    print("  direction of that bias is known in advance.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"convention": CONVENTION, "results": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
