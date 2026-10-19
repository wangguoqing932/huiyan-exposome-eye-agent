#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify two JAMA-reviewer claims that would overturn headline findings.

CLAIM A -- the regional subgroup test is a model artefact.
  My `subgroup_diff()` pooled WITHIN each region using fixed-effect weights
  w = 1/v. At I-squared near 90% that is invalid, and because SHARE's variance
  is two orders of magnitude smaller than anyone else's, Europe's pooled value
  was ~93% SHARE by weight. The claim is that pooling within region with
  random-effects weights instead makes Q_between collapse.

CLAIM B -- the powered-null flag contradicts its own definition.
  The table header defines a powered null as one whose confidence interval
  EXCLUDES its own MDE. The implementation tested `ci_low > MDE` for OR > 1,
  which is a different condition. CLHLS r20 (MDE 1.2127, CI 0.8736-1.2066) is a
  powered null by the stated definition but was recorded as False.

Run: python scripts/verify_r2_claims.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from cohort_heterogeneity import reml_tau2  # noqa: E402

REGION = {"SHARE": "Europe", "ELSA": "Europe", "HRS": "Americas",
          "MHAS": "Americas", "CRELES": "Americas", "KLoSA": "Asia",
          "LASI": "Asia", "CLHLS": "Asia"}


def subgroup(y, v, g, mode: str):
    """Between-subgroup Q, pooling within subgroup by `mode`."""
    mus, ses = [], []
    for grp in sorted(set(g)):
        m = g == grp
        yy, vv = y[m], v[m]
        if mode == "fixed":
            w = 1.0 / vv
        else:                                  # random effects within subgroup
            t2 = reml_tau2(yy, vv) if len(yy) > 1 else 0.0
            w = 1.0 / (vv + t2)
        mus.append(float(np.sum(w * yy) / np.sum(w)))
        ses.append(float(math.sqrt(1.0 / np.sum(w))))
    wb = 1.0 / np.array(ses) ** 2
    mb = float(np.sum(wb * np.array(mus)) / np.sum(wb))
    qb = float(np.sum(wb * (np.array(mus) - mb) ** 2))
    df = len(mus) - 1
    return ([round(math.exp(m), 4) for m in mus], round(qb, 3), df,
            float(stats.chi2.sf(qb, df)))


def main() -> int:
    res = pd.read_csv(ROOT / "outputs" / "cohorts" / "cohort_rule_results.csv")
    conf = res[res.rule_relevant.astype(bool)].copy()
    conf["region"] = conf["cohort"].map(REGION)

    print("=" * 108)
    print("CLAIM A: within-subgroup pooling weights")
    print(f"{'rule':34s} {'k':>2s}  {'FIXED within group':44s} | {'RANDOM within group':44s}")
    print("-" * 108)
    flips = []
    for rid, sub in conf.groupby("rule_id"):
        y = np.log(sub["odds_ratio"].to_numpy(float))
        v = sub["se"].to_numpy(float) ** 2
        g = sub["region"].to_numpy()
        fo, fq, fdf, fp = subgroup(y, v, g, "fixed")
        ro, rq, rdf, rp = subgroup(y, v, g, "random")
        mark = ""
        if (fp < 0.05) != (rp < 0.05):
            mark = "  <-- SIGNIFICANCE FLIPS"
            flips.append(rid)
        print(f"{rid:34s} {len(sub):>2d}  OR={str(fo):22s} Q={fq:>7} p={fp:.2e} | "
              f"OR={str(ro):22s} Q={rq:>7} p={rp:.2e}{mark}")

    print()
    print("=" * 108)
    print("CLAIM B: powered-null flag vs its stated definition")
    pw = pd.read_csv(ROOT / "outputs" / "cohorts" / "cohort_power.csv")
    uninf = pw[pw.three_state == "uninformative"].copy()

    def by_definition(r) -> bool:
        """CI excludes the MDE, i.e. the analysis could have detected an
        association at least as small as its own minimum detectable effect."""
        if not np.isfinite(r.mde_or_80):
            return False
        if r.observed_or < 1:
            return r.ci_low > r.mde_or_80 if False else r.ci_high < r.mde_or_80
        return r.ci_low > r.mde_or_80

    uninf["by_definition"] = uninf.apply(by_definition, axis=1)
    uninf["disagrees"] = uninf["by_definition"] != uninf["powered_null"]
    cols = ["cohort", "rule_id", "mde_or_80", "observed_or", "ci_low", "ci_high",
            "powered_null", "by_definition"]
    print(uninf[cols].to_string(index=False))
    print()
    print(f"  stored powered_null : {int(pw.powered_null.sum())} of "
          f"{int((pw.three_state=='uninformative').sum())} uninformative")
    print(f"  by definition       : {int(uninf.by_definition.sum())}")
    print(f"  disagreeing rows    : {int(uninf.disagrees.sum())}")
    for _, r in uninf[uninf.disagrees].iterrows():
        print(f"     {r.cohort} {r.rule_id}: MDE={r.mde_or_80} "
              f"CI=[{r.ci_low},{r.ci_high}] -> defined True, stored "
              f"{r.powered_null}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
