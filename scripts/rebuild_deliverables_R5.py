#!/usr/bin/env python
"""R5 (2026-10-14): rebuild downstream deliverables after P0 fixes.

1. Promote survey-variance labels to the primary gold3 column in the
   confirmatory CSVs (gold3_freq keeps the freq_weights sensitivity view).
2. Rebuild outputs/confirmatory/generalization_gap_v1.2.csv (+summary)
   on the primary labels.
3. Update outputs/tables/{performance_matrix,performance_by_dataset,
   dataset_summary}.csv to the R5 headline numbers.

Baseline rows in performance_by_dataset.csv are refreshed later by the
baseline rerun; this script leaves them untouched.

Run: PYTHONUTF8=1 python scripts/rebuild_deliverables_R5.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "confirmatory"
TAB = ROOT / "outputs" / "tables"


def promote_gold3(csv_name: str) -> pd.DataFrame:
    res = pd.read_csv(OUT / csv_name)
    if "gold3_freq" not in res.columns:
        res["gold3_freq"] = res["gold3"]
    res["gold3"] = res["gold3_svy"]
    res.to_csv(OUT / csv_name, index=False, encoding="utf-8-sig")
    return res


def rebuild_gap():
    n = pd.read_csv(OUT / "nhanes_confirmatory.csv")
    k = pd.read_csv(OUT / "knhanes_confirmatory.csv")
    cols = ["a_flag", "b_item", "gold3", "or_svy", "q_svy", "predicted", "rule_ids"]
    n2 = n[cols].rename(columns={"gold3": "nhanes_gold3", "or_svy": "nhanes_or",
                                 "q_svy": "nhanes_q", "predicted": "nhanes_predicted"})
    k2 = k[cols].rename(columns={"gold3": "knhanes_gold3", "or_svy": "knhanes_or",
                                 "q_svy": "knhanes_q", "predicted": "knhanes_predicted"})
    g = n2.merge(k2, on=["a_flag", "b_item"], how="inner")
    g["gold3_concordant"] = g["nhanes_gold3"] == g["knhanes_gold3"]
    out_cols = ["a_flag", "b_item", "nhanes_gold3", "nhanes_or", "nhanes_q",
                "knhanes_gold3", "knhanes_or", "knhanes_q", "gold3_concordant"]
    g[out_cols].to_csv(OUT / "generalization_gap_v1.2.csv", index=False, encoding="utf-8-sig")

    nm = json.loads((OUT / "nhanes_metrics_v11.json").read_text(encoding="utf-8"))
    km = json.loads((OUT / "knhanes_metrics_v11.json").read_text(encoding="utf-8"))
    cov_gap = round(nm["coverage"] - km["coverage"], 3)
    summary = {
        "datasets": "NHANES (internal) vs KNHANES (external)",
        "metric_basis": ("R11 2026-10-15: three-state gold under survey svyglm variance "
                         "(analysis_plan §6 primary standard); coverage = P(tested | rule "
                         "exists, judgeable, non-negative-control) — the pre-R11 formula "
                         "divided by ALL testable pairs and became meaningless once the "
                         "exposure×outcome matrix was expanded"),
        "n_common_tested_pairs": len(g),
        "gold3_concordant_pairs": int(g["gold3_concordant"].sum()),
        "gold3_concordance_rate": (round(float(g["gold3_concordant"].mean()), 3) if len(g) else None),
        "coverage": {
            "nhanes": nm["coverage"], "knhanes": km["coverage"],
            "gap_internal_minus_external": cov_gap,
        },
        "precision_rule": {
            "nhanes": nm["precision_rule"], "knhanes": km["precision_rule"],
            "gap_internal_minus_external": (
                None if nm["precision_rule"] is None or km["precision_rule"] is None
                else round(nm["precision_rule"] - km["precision_rule"], 3)),
            "note": (f"point estimates with CP CIs: NHANES {nm['precision_rule_ci95']} / "
                     f"KNHANES {km['precision_rule_ci95']} (width reflects small informative n)"),
        },
        "precision_binary_uninf_as_fp": {
            "nhanes": nm.get("precision_binary_uninf_as_fp"),
            "knhanes": km.get("precision_binary_uninf_as_fp"),
            "note": ("R11: the conservative reading (uninformative counted as a failed "
                     "prediction). Report BOTH this and precision_rule; the old "
                     "deliverables showed only the favourable denominator."),
        },
        "matrix": {
            "nhanes_tested": nm.get("matrix_tested_pairs"),
            "nhanes_significant": nm.get("matrix_significant_pairs"),
            "knhanes_tested": km.get("matrix_tested_pairs"),
            "knhanes_significant": km.get("matrix_significant_pairs"),
            "note": "full exposure×outcome matrix, exploratory family (separate from rule metrics)",
        },
        "generated": "2026-10-15 (R11)",
    }
    (OUT / "generalization_gap_v1.2_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[gap] common={len(g)} concordant={int(g['gold3_concordant'].sum())} "
          f"cov_gap={cov_gap}")
    return summary


def update_tables():
    nm = json.loads((OUT / "nhanes_metrics_v11.json").read_text(encoding="utf-8"))
    km = json.loads((OUT / "knhanes_metrics_v11.json").read_text(encoding="utf-8"))
    cm = json.loads((OUT / "charls_metrics_v11.json").read_text(encoding="utf-8"))
    # 审计 2026-10-15 修复：CHARLS 无 PSU/分层设计变量，svyglm 从未在其上运行，
    # 不得与 NHANES/KNHANES 共用 survey 方差文案（此前每次重建都会覆写手工修正）。
    meth = "three-state gold + survey svyglm variance (plan §6; R5) + Clopper-Pearson CI"
    meth_charls = "point estimates + declared fallback (no PSU; plan §6); three-state gold, R5"

    matrix = pd.DataFrame([
        {"dataset": "NHANES", "pairs_tested": "", "rule_pairs_tested": nm["rule_pairs_tested"],
         "replicated": nm["replicated"], "contradicted": nm["contradicted"],
         "uninformative": nm["uninformative"], "precision_rule": nm["precision_rule"],
         "precision_rule_ci95": str(nm["precision_rule_ci95"]).replace("None", "None"),
         "precision_binary_uninf_as_fp": nm.get("precision_binary_uninf_as_fp", ""),
         "coverage": nm["coverage"], "phase": "confirmatory_R5", "methodology": meth},
        {"dataset": "KNHANES", "pairs_tested": "", "rule_pairs_tested": km["rule_pairs_tested"],
         "replicated": km["replicated"], "contradicted": km["contradicted"],
         "uninformative": km["uninformative"], "precision_rule": km["precision_rule"],
         "precision_rule_ci95": str(km["precision_rule_ci95"]), "coverage": km["coverage"],
         "precision_binary_uninf_as_fp": km.get("precision_binary_uninf_as_fp", ""),
         "phase": "confirmatory_R5", "methodology": meth},
        {"dataset": "CHARLS", "pairs_tested": "", "rule_pairs_tested": cm["rule_pairs_tested"],
         "replicated": cm["replicated"], "contradicted": cm["contradicted"],
         "uninformative": cm["uninformative"],
         "precision_rule": cm["precision_rule"] if cm["precision_rule"] is not None else "n/a (0 informative)",
         "precision_rule_ci95": str(cm["precision_rule_ci95"]),
         "precision_binary_uninf_as_fp": cm.get("precision_binary_uninf_as_fp", ""),
         "coverage": cm["coverage"], "phase": "confirmatory_R5", "methodology": meth_charls},
    ])
    matrix.to_csv(TAB / "performance_matrix.csv", index=False, encoding="utf-8-sig")

    pbd = pd.read_csv(TAB / "performance_by_dataset.csv", encoding="utf-8-sig")
    def upd(ds, metric, mean=None, n=None, lo=None, hi=None, note=None, role=None):
        m = (pbd["dataset_id"] == ds) & (pbd["metric"] == metric)
        if not m.any(): return
        if mean is not None: pbd.loc[m, "mean"] = mean
        if n is not None: pbd.loc[m, "n_cases"] = n
        if lo is not None: pbd.loc[m, "ci_lo"] = lo
        if hi is not None: pbd.loc[m, "ci_hi"] = hi
        if note is not None: pbd.loc[m, "ci_note"] = note
        if role is not None: pbd.loc[m, "dataset_role"] = role
    upd("NHANES", "coverage", nm["coverage"], nm["rule_pairs_tested"],
        note="R5: survey svyglm variance (plan §6); judgeable set=nhanes")
    upd("NHANES", "precision_rule", nm["precision_rule"], nm["replicated"],
        nm["precision_rule_ci95"][0], nm["precision_rule_ci95"][1],
        "R5: Clopper-Pearson exact 95% CI [0.478, 1.00] (survey variance headline; freq_weights sensitivity=7/7 [0.59,1.0])")
    upd("KNHANES", "coverage", km["coverage"], km["rule_pairs_tested"],
        note="R5: judgeable set=knhanes (was nhanes-hardcoded, 0.263 inflated)")
    upd("KNHANES", "precision_rule", km["precision_rule"], km["replicated"],
        km["precision_rule_ci95"][0], km["precision_rule_ci95"][1],
        "R5: Clopper-Pearson exact 95% CI [0.158, 1.00]; 8/9 codes now missing")
    upd("CHARLS", "coverage", cm["coverage"], cm["rule_pairs_tested"],
        note="R5: judgeable set=cohort (was nhanes-hardcoded, 0.667 inflated)")
    upd("NHANES_minus_KNHANES", "coverage_gap",
        round(nm["coverage"] - km["coverage"], 3), nm["rule_pairs_tested"],
        note=f"R5: internal − external; {nm['coverage']} − {km['coverage']}（survey 方差三态口径）")
    upd("NHANES_minus_KNHANES", "precision_rule_gap",
        round(nm["precision_rule"] - km["precision_rule"], 3), nm["replicated"],
        note="R5: internal − external; 1.0 − 1.0（两层 CI 均宽，见各库行）")

    # R11 2026-10-15: writer 侧 7_1 QC (verify_figures_tables.py T4) requires rows
    # whose metric name starts with `gap_`; this file historically used the
    # `<metric>_gap` suffix, so the QC reported "MISSING gap_<metric> rows
    # despite internal+external datasets" even though the gaps were present.
    # Emit BOTH conventions so either consumer works.
    for _metric, _val, _n, _note in (
        ("gap_coverage", round(nm["coverage"] - km["coverage"], 3),
         nm["rule_pairs_tested"], "alias of coverage_gap (writer QC T4 naming)"),
        ("gap_precision_rule", round(nm["precision_rule"] - km["precision_rule"], 3),
         nm["replicated"], "alias of precision_rule_gap (writer QC T4 naming)"),
    ):
        _row = pbd[(pbd.dataset_id == "NHANES_minus_KNHANES") & (pbd.metric == _metric)]
        if len(_row) == 0:
            _tmpl = pbd[pbd.dataset_id == "NHANES_minus_KNHANES"].head(1).copy()
            if len(_tmpl):
                _tmpl["metric"] = _metric
                _tmpl["mean"] = _val
                _tmpl["n_cases"] = _n
                _tmpl["ci_note"] = _note
                pbd = pd.concat([pbd, _tmpl], ignore_index=True)

    # R11: writer QC opens these CSVs with encoding="utf-8"; a BOM made the first
    # column name "\ufeffdataset_id", so dataset-id lookups returned None and T3
    # reported "cases.jsonl missing" for every dataset. Write without BOM.
    pbd.to_csv(TAB / "performance_by_dataset.csv", index=False, encoding="utf-8")

    ds = pd.read_csv(TAB / "dataset_summary.csv", encoding="utf-8-sig")
    ds.loc[ds.dataset_id == "intval-nhanes", "confirmatory_run"] = (
        f"done (R5: {nm['rule_pairs_tested']} rule pairs, {nm['replicated']} replicated under survey variance; nhanes_confirmatory.csv)")
    ds.loc[ds.dataset_id == "extval-knhanes", "confirmatory_run"] = (
        f"done (R11: {km['rule_pairs_tested']} rule pairs, {km['replicated']} replicated under "
        f"survey variance after the frame rebuild; knhanes_confirmatory.csv)")
    ds.loc[ds.dataset_id == "extval-cohorts-9", "confirmatory_run"] = (
        f"partial (R11: CHARLS 2011 wave, {cm['rule_pairs_tested']} rule pairs 0 informative; "
        f"CHARLS 2015 smoking exposures failed the prevalence gate and are excluded; "
        f"charls_confirmatory.csv)")
    # R11: expose n_cases (writer QC T3 compares it against cases.jsonl line
    # counts) and write without BOM so column names survive a utf-8 read.
    _root = TAB.parent.parent
    ds["n_cases"] = [
        sum(1 for ln in (_root / "data" / "datasets" / str(i) / "cases.jsonl")
            .read_text(encoding="utf-8").splitlines() if ln.strip())
        if (_root / "data" / "datasets" / str(i) / "cases.jsonl").exists()
        else int(ds.loc[ds.dataset_id == i, "cases_populated"].iloc[0])
        for i in ds.dataset_id
    ]
    ds.to_csv(TAB / "dataset_summary.csv", index=False, encoding="utf-8")
    print("[tables] performance_matrix / performance_by_dataset / dataset_summary updated")


def main() -> int:
    promote_gold3("nhanes_confirmatory.csv")
    promote_gold3("knhanes_confirmatory.csv")
    rebuild_gap()
    update_tables()
    return 0


if __name__ == "__main__":
    sys.exit(main())
