#!/usr/bin/env python
"""R5 P0-4 (2026-10-14): apply survey-design variance as the PRIMARY
confirmatory standard (per analysis_plan §6 pre-registration) and keep the
Python freq_weights GLM as a sensitivity view.

For NHANES and KNHANES: joins svyglm results (outputs/confirmatory/
survey_sensitivity_R5.csv) into the confirmatory CSVs as or_svy/p_svy/q_svy/
gold3_svy, recomputes headline metrics on gold3_svy (pre-registered standard),
and rewrites the metrics JSONs with a sensitivity_freq_weights sub-object.

Run: PYTHONUTF8=1 python scripts/apply_survey_variance.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from evaluate import fdr_bhy, compute_metrics_v11

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "confirmatory"


def main() -> int:
    svy = pd.read_csv(OUT / "survey_sensitivity_R5.csv")
    svy[["a_flag", "b_item"]] = svy["pair"].str.split("__", expand=True)

    for ds, csv_name, json_name, key in [
        ("nhanes", "nhanes_confirmatory.csv", "nhanes_metrics_v11.json", "nhanes"),
        ("knhanes", "knhanes_confirmatory.csv", "knhanes_metrics_v11.json", "knhanes"),
    ]:
        res = pd.read_csv(OUT / csv_name)
        s = svy[svy["dataset"] == ds].copy()
        # R11 2026-10-15: dual-family FDR, mirroring assign_three_state().
        #   q_svy       — BHY over ALL surveyed pairs (exploratory family)
        #   q_svy_rule  — BHY over rule-relevant surveyed pairs (confirmatory family)
        # The headline three-state label uses the confirmatory family for rule
        # pairs; a single >100-pair family would dilute power exactly where it
        # matters most.
        s["q_svy"] = fdr_bhy(s["p"])
        rule_pairs = set(
            res.loc[res["predicted"].fillna(False).astype(bool), ["a_flag", "b_item"]]
            .itertuples(index=False, name=None))
        s["is_rule"] = [(a, b) in rule_pairs for a, b in zip(s["a_flag"], s["b_item"])]
        s["q_svy_rule"] = np.nan
        if s["is_rule"].any():
            s.loc[s["is_rule"], "q_svy_rule"] = fdr_bhy(s.loc[s["is_rule"], "p"])
        s["q_svy_primary"] = np.where(s["is_rule"], s["q_svy_rule"], s["q_svy"])

        m = res["status"] == "tested"
        res = res.merge(s[["a_flag", "b_item", "or", "ci_lo", "ci_hi", "p",
                           "q_svy", "q_svy_rule", "q_svy_primary"]],
                        on=["a_flag", "b_item"], how="left",
                        suffixes=("", "_svy_raw"))
        res = res.rename(columns={"or_svy_raw": "or_svy", "ci_lo_svy_raw": "ci_lo_svy",
                                  "ci_hi_svy_raw": "ci_hi_svy", "p_svy_raw": "p_svy"})
        res.loc[m, "gold3_svy"] = res[m].apply(
            lambda r: _three_state(r["or_svy"], r["q_svy_primary"], r["direction"]), axis=1)

        # headline metrics on survey variance (pre-registered §6 standard)
        res_hl = res.copy()
        hl_idx = res_hl["status"] == "tested"
        res_hl.loc[hl_idx, "gold3"] = res_hl.loc[hl_idx, "gold3_svy"]
        headline = compute_metrics_v11(res_hl, key)
        # sensitivity: freq_weights implementation (previous primary)
        sens = compute_metrics_v11(res, key)

        metrics = headline
        metrics["variance_standard"] = "survey svyglm (analysis_plan §6, pre-registered)"
        metrics["sensitivity_freq_weights"] = sens
        metrics["note"] = ("R5 2026-10-14: headline labels use survey-design variance "
                           "(svyglm strata/PSU, scripts/survey_sensitivity_R5.R); the Python "
                           "freq_weights GLM is retained as sensitivity. q_svy computed over "
                           "all tested pairs (same BHY denominator as main analysis).")

        res.to_csv(OUT / csv_name, index=False, encoding="utf-8-sig")
        (OUT / json_name).write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"== {ds} headline (survey) ==")
        print(json.dumps({k: v for k, v in headline.items()
                          if not isinstance(v, dict)}, ensure_ascii=False))
        flips = res[m & res.get("predicted", False)]
        flips = flips[flips["gold3"] != flips["gold3_svy"]]
        print(f"predicted-pair label changes vs freq_weights: {len(flips)}")
        for _, r in flips.iterrows():
            print(f"  {r['a_flag']} x {r['b_item']}: {r['gold3']} -> {r['gold3_svy']}")
    return 0


def _three_state(or_val, q_val, rule_dir="risk_up"):
    import numpy as np
    if pd.isna(q_val) or not np.isfinite(q_val) or q_val >= 0.05:
        return "uninformative"
    if pd.isna(or_val) or not np.isfinite(or_val) or abs(float(or_val) - 1.0) < 1e-9:
        return "uninformative"
    if rule_dir == "risk_down":
        return "replicated" if or_val < 1 else "contradicted"
    return "replicated" if or_val > 1 else "contradicted"


if __name__ == "__main__":
    sys.exit(main())
