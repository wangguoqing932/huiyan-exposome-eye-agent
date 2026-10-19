#!/usr/bin/env python
"""R5 (2026-10-14): baseline summary from the 5-seed rerun.

Reads outputs/baseline_predictions.jsonl (round-2 LLM baselines with the
transparent no-evidence parsing + the deterministic full_system runs),
computes per-seed P/R/F1, mean±std across seeds, and paired McNemar tests
(full_system vs each LLM baseline, per seed, exact binomial).

Writes outputs/baseline_summary_R5.json and refreshes the baseline rows of
outputs/tables/performance_by_dataset.csv.

Run: PYTHONUTF8=1 python scripts/make_baseline_summary_R5.py
"""
from __future__ import annotations
import json, math, sys
from collections import defaultdict
from pathlib import Path

from scipy import stats as st

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"


def metrics(rows):
    tp = sum(1 for r in rows if r["prediction"] and r["gold3"] == "replicated")
    fp = sum(1 for r in rows if r["prediction"] and r["gold3"] != "replicated")
    fn = sum(1 for r in rows if not r["prediction"] and r["gold3"] == "replicated")
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else None
    return {"TP": tp, "FP": fp, "FN": fn, "n_yes": tp + fp,
            "precision": prec, "recall": rec, "F1": f1}


def mcnemar_exact(rows_a, rows_b):
    """rows_a/b: same (a_flag,b_item) order (join by key). Exact McNemar."""
    ka = {(r["a_flag"], r["b_item"]): r["prediction"] for r in rows_a}
    kb = {(r["a_flag"], r["b_item"]): r["prediction"] for r in rows_b}
    keys = sorted(set(ka) & set(kb))
    b = sum(1 for k in keys if ka[k] and not kb[k])   # full YES, base NO
    c = sum(1 for k in keys if not ka[k] and kb[k])   # full NO, base YES
    n = b + c
    p = 1.0 if n == 0 else min(1.0, 2 * st.binom.cdf(min(b, c), n, 0.5))
    return {"b_full_yes_base_no": b, "c_full_no_base_yes": c, "p_exact": round(p, 5)}


def main() -> int:
    recs = [json.loads(l) for l in
            (OUT / "baseline_predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    # group ALL valid rows by (baseline, provider, seed); each group is one run's 80 rows
    # R13-M11:按 provider 分代际——qwen/deepseek 两代预测不得混入同一均值
    runs = defaultdict(lambda: defaultdict(list))  # (baseline, provider) -> seed -> rows
    for r in recs:
        if r.get("valid", True):
            runs[(r["baseline"], str(r.get("provider", "unknown")))][r["seed"]].append(r)
    # defensive: a run must have the full pair set; drop partial groups (<70 rows)
    for blp in list(runs):
        for s in list(runs[blp]):
            if len(runs[blp][s]) < 70:
                print(f"[warn] dropping partial run {blp} seed{s} ({len(runs[blp][s])} rows)")
                del runs[blp][s]

    summary = {
        "date": "2026-10-14 (R5 round 2)",
        "gold": "nhanes_confirmatory.csv gold3 (survey svyglm variance headline; positive=replicated)",
        "note": ("LLM baselines: local qwen3.8-27b, thinking disabled, temp=0.7, seeds [11,22,33,44,55] "
                 "passed in API request body; prompts use registry human-readable names; naive_rag uses "
                 "the plain NaiveRAG retriever (no level weighting); parsing maps explicit no-evidence "
                 "statements to NO (parsed=no_evidence_inference, auditable). full_system: deterministic "
                 "rule engine (provider=rule_engine:deterministic), 0 LLM calls, seed-invariant. "
                 "Round-1 outputs (stricter parser) archived in baseline_predictions_R5_round1.jsonl."),
        "baselines": {},
    }
    per_seed_table = {}
    for blp in sorted(runs):
        bl = blp[0] + "@" + blp[1]  # 展示名带 provider,两代并列不混淆
        seeds = sorted(runs[blp])
        ms = {}
        for s in seeds:
            rows = runs[blp][s]
            key = f"seed{s}"
            ms[key] = metrics(rows)
        vals = {k: [m[k] for m in ms.values()] for k in ("precision", "recall", "F1")}
        agg = {}
        for k, v in vals.items():
            if k == "F1":
                # a seed with no positive predictions (TP=FP=0) has F1=0 by
                # convention (system predicts nothing) — NOT excluded, which
                # would inflate the mean
                vv = [x if x is not None else 0.0 for x in v]
            else:
                vv = [x for x in v if x is not None]
            mean = sum(vv) / len(vv) if vv else None
            agg[k] = {
                "mean": round(mean, 4) if mean is not None else None,
                "std": round(math.sqrt(sum((x - mean) ** 2 for x in vv) / len(vv)), 4) if len(vv) > 1 else 0.0,
                "per_seed": [round(x, 4) if x is not None else None for x in v],
                "n_defined_seeds": len(vv),
            }
        summary["baselines"][bl] = {
            "provider": blp[1] if blp[0] != "full_system" else "rule_engine:deterministic",
            "n_seeds": len(seeds),
            **agg,
            "TP_per_seed": {f"seed{s}": ms[f"seed{s}"]["TP"] for s in seeds},
            "FP_per_seed": {f"seed{s}": ms[f"seed{s}"]["FP"] for s in seeds},
            "FN_per_seed": {f"seed{s}": ms[f"seed{s}"]["FN"] for s in seeds},
        }
        per_seed_table[bl] = {f"seed{s}": rows for s, rows in runs[blp].items()}

    # McNemar: full_system vs each LLM baseline, per seed + aggregate(同 provider 代际内比较)
    fs = per_seed_table.get("full_system@rule_engine:deterministic", {})
    mc = {}
    provs = sorted({k.split("@")[1] for k in per_seed_table if k != "full_system@rule_engine:deterministic"})
    for bl in ("pure_llm", "naive_rag", "lightrag"):
        for prov in provs:
            per_seed = {}
            for seed_key in sorted(fs):
                tb = per_seed_table.get(f"{bl}@{prov}", {})
                if seed_key in tb:
                    per_seed[seed_key] = mcnemar_exact(fs[seed_key], tb[seed_key])
            if per_seed:
                bs = [v["b_full_yes_base_no"] for v in per_seed.values()]
                cs = [v["c_full_no_base_yes"] for v in per_seed.values()]
                ps = [v["p_exact"] for v in per_seed.values()]
                mc[f"{bl}@{prov}"] = {
                    "per_seed": per_seed,
                    "aggregate_b": sum(bs), "aggregate_c": sum(cs),
                    "p_range": [min(ps), max(ps)],
                    "significant_at_0.05_any_seed": any(p < 0.05 for p in ps),
                }
    summary["mcnemar_full_system_vs"] = mc
    (OUT / "baseline_summary_R5.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    def _fmt(x):
        return "  n/a" if x is None else f"{x:.3f}"
    for bl, d in summary["baselines"].items():
        print(f"{bl:12s} P={_fmt(d['precision']['mean'])}±{_fmt(d['precision']['std'])} "
              f"R={_fmt(d['recall']['mean'])}±{_fmt(d['recall']['std'])} "
              f"F1={_fmt(d['F1']['mean'])}±{_fmt(d['F1']['std'])} ({d['n_seeds']} seeds)")
    for bl, d in mc.items():
        print(f"McNemar full_system vs {bl}: p range {d['p_range']}, "
              f"sig@0.05 any seed: {d['significant_at_0.05_any_seed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
