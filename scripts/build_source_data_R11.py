#!/usr/bin/env python
"""Regenerate outputs/figures/source_data/*.csv from the R11 result files.

This is the pipeline-sanctioned seam between Executor and Writer: the R11
re-validation results are projected into the figure source_data contract that
`medical-agent-writer/scripts/build_figures.py` consumes.

It reads ONLY already-computed R11 result files — no dataset is re-read and no
model is re-fitted — so it cannot change any number.

Design constraint: build_figures.py loads exactly ONE source_data CSV per
contract and a panel cannot filter rows. Source CSV shapes are therefore chosen
to match the plot_types the renderer actually implements (grouped_bar / forest /
heatmap / scatter / horizontal_bar / stacked_bar / network). Column names follow
the renderer's lookup hints.

Run: PYTHONUTF8=1 python scripts/build_source_data_R11.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "outputs" / "confirmatory"
SD = ROOT / "outputs" / "figures" / "source_data"
TAB = ROOT / "outputs" / "tables"
SD.mkdir(parents=True, exist_ok=True)

R11 = "R11 (variable_map v2, 2026-10-15)"


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _cp_ci(k, n):
    from scipy.stats import beta
    lo = beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return float(lo), float(hi)


# ---------------------------------------------------------------- figure 2
def figure2():
    """System vs three LLM baselines, scored against the R11 gold.

    Long format (one row per method x seed) so the `forest` renderer can
    aggregate to mean +- SD by method label, which is what the figure needs.
    """
    src = ROOT / "outputs" / "baseline_summary_R11_corrected_gold.json"
    if not src.exists():
        print("[F2] missing baseline_summary_R11_corrected_gold.json — skipped")
        return
    b = _j(src)
    m = b["metrics"]
    order = ["full_system", "pure_llm", "lightrag", "naive_rag"]
    rows = []
    for meth in order:
        rec = m[meth]["R11_gold"]
        seeds = rec["per_seed_F1"]
        for i, f1 in enumerate(seeds):
            rows.append({
                "method": meth,
                "dataset": "NHANES",
                "dataset_id": "NHANES",
                "dataset_role": "internal_validation",
                "ruleset": "v1.2" if meth == "full_system" else "n/a",
                "seed": [11, 22, 33, 44, 55][i % 5],
                "estimate": f1, "F1": f1,
                # forest uses ci_low/ci_high when present; per-seed F1 has no CI,
                # so leave them equal to the estimate and let the aggregator
                # build mean +- SD across seeds.
                "ci_low": f1, "ci_high": f1,
                "P": rec["P"], "R": rec["R"], "mean_F1": rec["F1"],
            })
    # v1.1 replay = pre-expansion ruleset on the same gold (mandatory dual report)
    rep = ROOT / "outputs" / "confirmatory" / "v11_replay_R5.json"
    if rep.exists():
        v = _j(rep).get("R11_gold", _j(rep).get("R5_gold", {}))
        if v.get("F1") is not None:
            rows.append({"method": "full_system_v1.1_replay", "dataset": "NHANES",
                         "dataset_id": "NHANES", "dataset_role": "internal_validation",
                         "ruleset": "v1.1", "seed": 0, "estimate": v["F1"], "F1": v["F1"],
                         "ci_low": v["F1"], "ci_high": v["F1"],
                         "P": v.get("P"), "R": v.get("R"), "mean_F1": v["F1"]})
    df = pd.DataFrame(rows)
    df.to_csv(SD / "figure2_performance.csv", index=False, encoding="utf-8-sig")
    print(f"[F2] figure2_performance.csv  rows={len(df)}  R11 gold  "
          f"(full_system F1={m['full_system']['R11_gold']['F1']}, "
          f"lightrag {m['lightrag']['R11_gold']['F1']}, "
          f"pure_llm {m['pure_llm']['R11_gold']['F1']}, "
          f"naive_rag {m['naive_rag']['R11_gold']['F1']})")


# ---------------------------------------------------------------- figure 3
def figure3():
    """Rule-level evaluation under the R11 three-state protocol.

    Long format (label, estimate, ci_low, ci_high, dataset, metric) so a single
    `forest` panel carries every proportion with its Clopper-Pearson interval:
    dual precision by layer, then replication by evidence level.
    """
    rows = []
    for ds, tag in (("nhanes", "NHANES"), ("knhanes", "KNHANES")):
        # Read the authoritative metrics JSON rather than recomputing here.
        # Recomputing from the raw CSV omits the judgeable-B-item filter that
        # compute_metrics_v11 applies, which gives 6/19 = 0.316 instead of the
        # reported 6/16 = 0.375 — a silent figure/table mismatch.
        m = _j(CONF / f"{ds}_metrics_v11.json")
        rows.append(dict(method="declared-domain precision", dataset=tag,
                         metric="precision_rule_declared",
                         estimate=m["precision_rule"],
                         ci_low=m["precision_rule_ci95"][0],
                         ci_high=m["precision_rule_ci95"][1],
                         k=m["replicated"], n=m["replicated"] + m["contradicted"]))
        rows.append(dict(method="conservative precision", dataset=tag,
                         metric="precision_rule_uninf_as_fp",
                         estimate=m["precision_binary_uninf_as_fp"],
                         ci_low=m["precision_binary_ci95"][0],
                         ci_high=m["precision_binary_ci95"][1],
                         k=m["replicated"], n=m["rule_pairs_tested"]))
        rows.append(dict(method="rule coverage", dataset=tag, metric="coverage",
                         estimate=m["coverage"], ci_low=np.nan, ci_high=np.nan,
                         k=m["rule_pairs_tested"], n=m["rule_relevant_pairs"]))

    hs = pd.read_csv(TAB / "headline_sensitivity.csv", encoding="utf-8-sig")
    for rs, lab in (("A_level_only", "A"), ("A_and_B_level_only", "A+B"),
                    ("all_rules (current)", "all")):
        for ds in ("NHANES", "KNHANES"):
            r = hs[(hs.rule_set == rs) & (hs.dataset == ds)]
            if not len(r):
                continue
            rep, n = int(r.replicated.iloc[0]), int(r.rule_pairs_tested.iloc[0])
            lo, hi = _cp_ci(rep, n) if n else (0.0, 1.0)
            rows.append(dict(method=f"replication rate · level {lab}",
                             dataset=ds, metric="replication_rate",
                             estimate=rep / n if n else 0.0, ci_low=lo, ci_high=hi,
                             k=rep, n=n))
    df = pd.DataFrame(rows)
    df["ci_low"] = df["ci_low"].fillna(df["estimate"])
    df["ci_high"] = df["ci_high"].fillna(df["estimate"])
    df.to_csv(SD / "figure3_rule_evaluation.csv", index=False, encoding="utf-8-sig")
    print(f"[F3] figure3_rule_evaluation.csv  rows={len(df)} "
          f"(dual precision + coverage + replication by evidence level)")


# ---------------------------------------------------------------- figure 4
def figure4():
    """Demo-case plate: R11 survey-variance numbers for the traced pair."""
    d = pd.read_csv(CONF / "nhanes_confirmatory.csv")
    keep = d[(d.status == "tested") & (d.predicted.fillna(False).astype(bool))].copy()
    keep = keep[keep.gold3 == "replicated"].nlargest(1, "n")
    if not len(keep):
        print("[F4] no replicated rule pair found — skipped")
        return
    r = keep.iloc[0]
    out = pd.DataFrame([{
        "entity_a": r.a_flag, "entity_b": r.b_item, "layer": "rule_engine",
        "action": str(r.rule_ids),
        "OR_nhanes": r["or"], "OR_low": r.ci_lo, "OR_high": r.ci_hi,
        "p": r.p_svy if "p_svy" in r and pd.notna(r.p_svy) else r.p,
        "q_bhy": r.q_svy_primary if "q_svy_primary" in r else r.q,
        "gold3": r.gold3, "n": int(r.n), "n_pos": int(r.n_pos),
        "variance": "survey svyglm (strata/PSU)", "source": R11,
    }])
    out.to_csv(SD / "figure4_demo_case.csv", index=False, encoding="utf-8-sig")
    print(f"[F4] figure4_demo_case.csv  {r.a_flag} x {r.b_item} "
          f"OR={r['or']:.3f} q_svy={out.iloc[0]['q_bhy']:.3g}")


# ---------------------------------------------------------------- figure 6
def figure6():
    """Continuous (per-1-SD) dose-response for rule-relevant pairs — forest sh
    ape so each OR per SD carries its survey 95% CI."""
    src = CONF / "dose_response_matrix.csv"
    if not src.exists():
        print("[F6] missing dose_response_matrix.csv — skipped")
        return
    d = pd.read_csv(src)
    d = d[d.is_rule_pair.fillna(False).astype(bool)].copy()
    d = d[d["q_primary"].notna()]
    out = pd.DataFrame({
        "method": d.a_flag + " · " + d.b_item,
        "dataset": d.dataset.str.upper(),
        "estimate": d.odds_ratio, "ci_low": d.ci_lo, "ci_high": d.ci_hi,
        "q": d.q_primary, "n": d.n,
        "significant": np.where(d.q_primary < 0.05, "q<0.05", "n.s."),
    }).sort_values(["dataset", "estimate"])
    out.to_csv(SD / "figure6_dose_response.csv", index=False, encoding="utf-8-sig")
    print(f"[F6] figure6_dose_response.csv  rows={len(out)}  "
          f"significant={int((out.significant == 'q<0.05').sum())}")


def figure7():
    """Power figure: minimum detectable OR vs the observed OR, rule-relevant pairs.

    This is the only visual carrier of the paper's central negative claim — that
    the rule nulls are informative rather than underpowered. It existed only as
    an ad-hoc render (outputs/figures/legacy/figure3_power_mde_R11.png) before
    R11 integrated it into the contract pipeline.
    """
    frames = []
    for ds, tag in (("nhanes", "NHANES"), ("knhanes", "KNHANES")):
        p = CONF / f"power_analysis_{ds}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p)
        d = d[d.predicted.fillna(False).astype(bool)].copy()
        d = d[d.mde_or_80.notna() & d["or"].notna()]
        d["dataset"] = tag
        frames.append(d)
    if not frames:
        print("[F7] no power analysis CSVs — skipped")
        return
    a = pd.concat(frames, ignore_index=True)
    out = pd.DataFrame({
        "mde_or_80": a.mde_or_80,
        # NOTE: the column must NOT be named "or". build_figures._find_column does
        # a case-insensitive SUBSTRING match and returns the FIRST hit, so a
        # y_axis hint of "or" matched the earlier column `mde_or_80` and the
        # scatter silently plotted MDE against itself (x == y) — the rendered
        # figure hid every large observed OR. `odds_ratio` contains no "or"
        # substring and is unambiguous.
        "odds_ratio": a["or"],
        "ci_low": a.ci_lo, "ci_high": a.ci_hi,
        "gold3": a.gold3,
        "dataset": a.dataset,
        # one colour column so a single scatter panel distinguishes both layers
        "layer_gold": a.dataset + " · " + a.gold3.astype(str),
        "pair": a.a_flag + " · " + a.b_item,
        "rule_ids": a.rule_ids.fillna(""),
        "n": a.n, "power_class": a.power_class, "null_type": a.null_type,
    })
    out.to_csv(SD / "figure7_power_mde.csv", index=False, encoding="utf-8-sig")
    print(f"[F7] figure7_power_mde.csv  rows={len(out)}  "
          f"powered_null={int((out.null_type == 'powered_null').sum())}")


def main() -> int:
    print("Rebuilding figure source_data from R11 results (no datasets re-read)")
    figure2()
    figure3()
    figure4()
    figure6()
    figure7()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
