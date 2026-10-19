#!/usr/bin/env python
"""Continuous (per-1-SD) exposure x eye-disease association matrix.

Complements the binary rule-validation layer: every continuous measure was
standardised to per-1-SD before fitting, so the coefficient is an OR per
standard deviation — a dose-response estimate that does not depend on the
choice of a clinical cut-point.

Answers two questions the dichotomised layer cannot:
  1. Was a null rule result an artefact of dichotomisation?  (Signals that are
     monotone but sub-threshold can be invisible as a 0/1 flag yet clear per SD.)
  2. What is the continuous-construct replication of the rule directions?

Survey-design variance (svyglm strata/PSU) from outputs/confirmatory/
dose_response_svyglm.csv.  FDR is applied within the same two pre-registered
families used elsewhere (confirmatory = rule-relevant, exploratory = full matrix).

Run: PYTHONUTF8=1 python scripts/dose_response_matrix.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "confirmatory"
TAB = ROOT / "outputs" / "tables"

# continuous measure -> (binary flag it operationalises, expected sign of OR
# per SD for a RISK-up rule).  sign=+1 means higher continuous value = more risk.
CONSTRUCT = {
    "hba1c_pct": ("hba1c_elevated", +1),
    "fasting_glucose_mgdl": ("hyperglycemia", +1),
    "uric_acid_mgdl": ("uric_acid_elevated", +1),
    "crp_mgl": ("crp_elevated", +1),
    "bmi_kgm2": ("bmi_high", +1),
    "waist_cm": ("bmi_high", +1),
    "hdl_mgdl": ("hdl_low", -1),          # higher HDL = lower risk
    "ldl_mgdl": ("ldl_high", +1),
    "triglycerides_mgdl": ("dyslipidemia", +1),
    "total_cholesterol_mgdl": ("dyslipidemia", +1),
    "blood_lead_ugdl": ("lead_exposure", +1),
    "serum_cotinine_ngml": ("current_smoking", +1),
    "vitamin_c_mg": ("low_antioxidant_intake", -1),        # higher intake = lower risk
    "alpha_tocopherol_mg": ("low_antioxidant_intake", -1),
    "lutein_zeaxanthin_mg": ("low_antioxidant_intake", -1),
}
# exact duplicate of lutein_zeaxanthin_mg (same column, different unit scaling)
DROP = {"lutein_zeaxanthin_ug", "log_blood_lead", "antioxidant_inadequate_count"}

# Definitional (tautological) pairs: the outcome flag is DERIVED from the very
# measurement used as the exposure, so the fit is an identity, not an
# association.  `glaucoma_iop_elevated` is literally "IOP above threshold"
# (svyglm returns OR = inf).  These must never enter the matrix.
DEFINITIONAL = {
    ("intraocular_pressure_mmhg", "glaucoma_iop_elevated"),
}


def fdr_bhy(p):
    p = np.asarray(p, dtype=float)
    ok = np.isfinite(p)
    q = np.full_like(p, np.nan)
    pv = p[ok]
    if pv.size == 0:
        return q
    n = pv.size
    order = np.argsort(pv)
    ranked = pv[order]
    qv = ranked * n / (np.arange(1, n + 1))
    qv = np.minimum.accumulate(qv[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(qv, 0, 1)
    q[ok] = out
    return q


def rule_lookup():
    """(a_flag, b_item) -> rule_ids, taken from the binary confirmatory layer."""
    m = {}
    for f in ("nhanes_confirmatory.csv", "knhanes_confirmatory.csv"):
        p = OUT / f
        if not p.exists():
            continue
        d = pd.read_csv(p)
        d = d[d["predicted"].fillna(False).astype(bool)]
        for r in d.itertuples():
            m.setdefault((r.a_flag, r.b_item), set()).update(
                x.strip() for x in str(r.rule_ids).split(",") if x.strip())
    return m


def main() -> int:
    src = OUT / "dose_response_svyglm.csv"
    if not src.exists():
        raise SystemExit("run: python scripts/survey_sensitivity_export.py --mode continuous "
                         "&& SVY_INDIR=... SVY_OUTFILE=... Rscript scripts/survey_sensitivity_R5.R")
    d = pd.read_csv(src)
    d[["a_flag", "b_item"]] = d["pair"].str.split("__", expand=True)
    d = d[~d["a_flag"].isin(DROP)].copy()
    def_mask = [ (a, b) in DEFINITIONAL for a, b in zip(d["a_flag"], d["b_item"]) ]
    if any(def_mask):
        print(f"[dose-response] dropped {sum(def_mask)} definitional (tautological) pair(s): "
              f"{sorted(DEFINITIONAL)}")
        d = d[[not m for m in def_mask]].copy()
    # `or` is a Python keyword, so itertuples cannot expose it as `r.or`.
    d = d.rename(columns={"or": "odds_ratio"})
    d["expected_sign"] = d["a_flag"].map(lambda k: CONSTRUCT.get(k, (None, 0))[1])
    d["binary_flag"] = d["a_flag"].map(lambda k: CONSTRUCT.get(k, (None, 0))[0])

    rl = rule_lookup()
    d["rule_ids"] = [
        ",".join(sorted(rl.get((b, o), set()))) if b else "" for b, o in
        zip(d["binary_flag"], d["b_item"])]
    d["is_rule_pair"] = d["rule_ids"].str.len() > 0

    # two pre-registered FDR families
    d["q_exploratory"] = fdr_bhy(d["p"])
    d["q_confirmatory"] = np.nan
    if d["is_rule_pair"].any():
        d.loc[d["is_rule_pair"], "q_confirmatory"] = fdr_bhy(
            d.loc[d["is_rule_pair"], "p"])
    d["q_primary"] = d["q_confirmatory"].fillna(d["q_exploratory"])

    d["direction_match"] = np.where(
        d["expected_sign"].eq(0), "",
        np.where(
            ((d["expected_sign"] > 0) & (d["odds_ratio"] > 1)) |
            ((d["expected_sign"] < 0) & (d["odds_ratio"] < 1)), "concordant", "opposite"))

    keep = ["dataset", "a_flag", "b_item", "binary_flag", "n", "odds_ratio", "ci_lo", "ci_hi",
            "p", "q_primary", "q_exploratory", "is_rule_pair", "rule_ids",
            "expected_sign", "direction_match"]
    d[keep].sort_values(["dataset", "q_primary"]).to_csv(
        OUT / "dose_response_matrix.csv", index=False, encoding="utf-8-sig")

    print("=" * 100)
    print("CONTINUOUS EXPOSURE x EYE DISEASE MATRIX  (OR per 1 SD, survey svyglm)")
    print("=" * 100)
    for ds in sorted(d["dataset"].unique()):
        s = d[d["dataset"] == ds]
        sig = s[s["q_primary"] < 0.05]
        print(f"\n[{ds}] {len(s)} pairs fitted, {len(sig)} significant "
              f"(confirmatory family n={int(s['is_rule_pair'].sum())})")
        print("  top 12 by q:")
        for r in s.nsmallest(12, "q_primary").itertuples():
            tag = f"  [{r.rule_ids}]" if r.rule_ids else ""
            print(f"    {r.a_flag:24s} -> {r.b_item:26s} OR/SD={r.odds_ratio:6.3f} "
                  f"({r.ci_lo:.3f}-{r.ci_hi:.3f}) q={r.q_primary:.3g} "
                  f"{r.direction_match}{tag}")

    # rule-relevant dose-response summary
    rp = d[d["is_rule_pair"]].copy()
    print("\n" + "=" * 100)
    print("RULE-RELEVANT CONTINUOUS PAIRS: did dichotomisation hide anything?")
    print("=" * 100)
    for ds in sorted(rp["dataset"].unique()):
        s = rp[rp["dataset"] == ds]
        both = s[s["direction_match"] != ""]
        conc = int((both["direction_match"] == "concordant").sum())
        print(f"  [{ds}] rule-relevant continuous pairs={len(s)}  "
              f"significant={int((s['q_primary'] < 0.05).sum())}  "
              f"direction checked={len(both)} concordant={conc}"
              + (f" ({conc/len(both):.0%})" if len(both) else ""))
        for r in s[s["q_primary"] < 0.05].itertuples():
            print(f"      SIGNIFICANT {r.a_flag:22s} -> {r.b_item:24s} "
                  f"OR/SD={r.odds_ratio:.3f} q={r.q_primary:.3g} {r.direction_match} [{r.rule_ids}]")

    summary = {
        "method": ("OR per 1 standard deviation, survey svyglm (strata/PSU), same covariates "
                   "as the binary layer; FDR within the confirmatory (rule-relevant) and "
                   "exploratory (full matrix) families."),
        "pairs": int(len(d)), "pairs_significant": int((d["q_primary"] < 0.05).sum()),
        "by_dataset": {
            ds: {
                "pairs": int((d["dataset"] == ds).sum()),
                "significant": int(((d["dataset"] == ds) & (d["q_primary"] < 0.05)).sum()),
                "rule_relevant": int(((d["dataset"] == ds) & d["is_rule_pair"]).sum()),
            } for ds in sorted(d["dataset"].unique())
        },
        "note": ("Dropped as redundant/derived: " + ", ".join(sorted(DROP))),
    }
    (OUT / "dose_response_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[dose-response] -> {OUT/'dose_response_matrix.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
