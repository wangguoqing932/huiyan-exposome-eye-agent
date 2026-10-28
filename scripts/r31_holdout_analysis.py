#!/usr/bin/env python
"""R31 addendum analyses P1-P4 (pre-registered in docs/analysis_plan_R31_addendum.md,
sha256 00323e28cd1f9e30…, committed before this script ran).

P1  internal matrix: enumerate replicated pairs and the share touched by the rules
    modified after the first confirmatory run (r02/r03/r04/r22).
P2  contamination-free estimate: KNHANES clean subset (non-touched pairs), G0/G1/G2
    and the three baselines.
P3  three-state decomposition: recall on replicated, flag rate on contradicted,
    flag rate on uninformative (keeps uninformative out of the negative class).
P4  Benjamini-Hochberg correction over the 15 McNemar tests per dataset.

Output: outputs/confirmatory/r31_holdout.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "outputs" / "confirmatory"
SEEDS = [11, 22, 33, 44, 55]
REVISED = ("r02_", "r03_", "r04_", "r22_")
BASELINES = ("lightrag", "pure_llm", "naive_rag")


def touched(rule_ids) -> bool:
    s = str(rule_ids or "")
    return any(x in s for x in REVISED)


def load_g2(dataset: str):
    rows = []
    for line in (CONF / "fused_system_R5.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["dataset"] == dataset and r["gold3"] != "not_tested":
            rows.append(r)
    return rows


def load_baselines(dataset: str):
    """(baseline, seed) -> {(a_flag, b_item): prediction}, per amendment P0.

    Only valid==True parses count as predictions; a failed parse is missing data,
    never a negative. Cells with no valid parse at a given seed are dropped from
    that seed's metrics, and the count is reported.
    """
    path = ROOT / "outputs" / f"baseline_predictions_{'knhanes' if dataset == 'knhanes' else 'nhanes'}.jsonl"
    if not path.exists():
        return {}, {}
    out = defaultdict(dict)
    stats = defaultdict(lambda: {"rows": 0, "invalid": 0, "cells": set()})
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        bl = r.get("baseline")
        if bl == "full_system":          # deterministic ablation, taken from fused jsonl
            continue
        key = (bl, r.get("seed"))
        cell = (r.get("a_flag"), r.get("b_item"))
        stats[key]["rows"] += 1
        stats[key]["cells"].add(cell)
        if not r.get("valid"):
            stats[key]["invalid"] += 1
            continue
        val = bool(r.get("prediction"))
        if cell in out[key] and out[key][cell] != val:
            raise SystemExit(f"conflicting valid duplicate for {key} {cell}")
        out[key][cell] = val
    report = {f"{k[0]}|{k[1]}": {"rows": v["rows"], "invalid": v["invalid"],
                                  "cells": len(v["cells"]),
                                  "cells_with_valid": len(out.get(k, {}))}
              for k, v in stats.items()}
    return out, report


def counts(rows, pred_key_or_fn):
    tp = fp = fn = tn = 0
    for r in rows:
        p = pred_key_or_fn(r)
        g = r["gold3"] == "replicated"
        tp += p and g
        fp += p and not g
        fn += (not p) and g
    tn = len(rows) - tp - fp - fn
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "P": round(prec, 4), "R": round(rec, 4), "F1": round(f1, 4)}


def three_state(rows, pred_fn):
    rep = [r for r in rows if r["gold3"] == "replicated"]
    con = [r for r in rows if r["gold3"] == "contradicted"]
    uni = [r for r in rows if r["gold3"] == "uninformative"]
    def rate(subset):
        return round(sum(1 for r in subset if pred_fn(r)) / len(subset), 4) if subset else None
    return {"n_replicated": len(rep), "n_contradicted": len(con), "n_uninformative": len(uni),
            "recall_replicated": rate(rep),
            "flag_rate_contradicted": rate(con),
            "flag_rate_uninformative": rate(uni)}


def mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / (2 ** n))


def bh(pvals):
    """Benjamini-Hochberg q-values, order-preserving."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank in range(n - 1, -1, -1):
        idx = order[rank]
        val = min(prev, p[idx] * n / (rank + 1))
        q[idx] = val
        prev = val
    return [float(round(x, 8)) for x in q]


def per_seed_baseline(rows, base, subset_key):
    """Accuracy McNemar G2 vs a baseline, per seed, on a row subset."""
    out = []
    for seed in SEEDS:
        table = base.get((subset_key["baseline"], seed), {})
        b = c = n = 0
        for r in rows:
            cell = (r["a_flag"], r["b_item"])
            if cell not in table:
                continue
            n += 1
            g2ok = bool(r["G2"]) == (r["gold3"] == "replicated")
            bok = table[cell] == (r["gold3"] == "replicated")
            if g2ok and not bok:
                b += 1
            elif bok and not g2ok:
                c += 1
        out.append({"seed": seed, "n": n, "b": b, "c": c, "p": mcnemar(b, c)})
    return out


def main() -> int:
    result = {"protocol": "docs/analysis_plan_R31_addendum.md sha256 00323e28cd1f9e3061573019c6f390467759ceedfc57fe851f787593c1fbe163",
              "seeds": SEEDS, "revised_rules": list(REVISED)}

    # ---------- P1 ----------
    nh = load_g2("nhanes")
    rep = [r for r in nh if r["gold3"] == "replicated"]
    rep_touched = [r for r in rep if touched(r.get("rule_ids"))]
    result["P1_internal"] = {
        "n_pairs": len(nh),
        "n_replicated": len(rep),
        "n_replicated_touched": len(rep_touched),
        "share_touched": round(len(rep_touched) / len(rep), 4) if rep else None,
        "replicated_pairs": [{"a_flag": r["a_flag"], "b_item": r["b_item"],
                              "rule_ids": r.get("rule_ids"), "touched": touched(r.get("rule_ids"))}
                             for r in rep],
        "clean_subset_positives": sum(1 for r in nh if r["gold3"] == "replicated" and not touched(r.get("rule_ids"))),
        "reading": "if share_touched == 1.0 the internal matrix contains no replicated pair that the revision did not touch, so its F1 carries no out-of-sample information about the rules",
    }

    # ---------- P2 / P3 / P4 ----------
    kn = load_g2("knhanes")
    clean = [r for r in kn if not touched(r.get("rule_ids"))]
    base, base_report = load_baselines("knhanes")
    result["P0_baseline_parsing"] = base_report

    def block(rows, label):
        b = {"label": label, "n_pairs": len(rows),
             "gold": {"replicated": sum(1 for r in rows if r["gold3"] == "replicated"),
                      "contradicted": sum(1 for r in rows if r["gold3"] == "contradicted"),
                      "uninformative": sum(1 for r in rows if r["gold3"] == "uninformative")},
             "arms": {}}
        for arm in ("G0", "G1", "G2"):
            b["arms"][arm] = {"binary": counts(rows, lambda r, a=arm: bool(r[a])),
                              "three_state": three_state(rows, lambda r, a=arm: bool(r[a]))}
        b["baselines"] = {}
        for bl in BASELINES:
            f1s, precs, recs, ss = [], [], [], []
            for seed in SEEDS:
                table = base.get((bl, seed), {})
                sub = [r for r in rows if (r["a_flag"], r["b_item"]) in table]
                if not sub:
                    continue
                met = counts(sub, lambda r, t=table: t[(r["a_flag"], r["b_item"])])
                f1s.append(met["F1"]); precs.append(met["P"]); recs.append(met["R"])
            if f1s:
                b["baselines"][bl] = {"n_pairs": len([r for r in rows if (r["a_flag"], r["b_item"]) in base.get((bl, SEEDS[0]), {})]),
                                      "F1_mean": round(float(np.mean(f1s)), 4),
                                      "F1_range": [round(min(f1s), 4), round(max(f1s), 4)],
                                      "P_mean": round(float(np.mean(precs)), 4),
                                      "R_mean": round(float(np.mean(recs)), 4)}
        return b

    result["P2_knhanes_clean"] = block(clean, "KNHANES clean subset (non-touched)")
    result["P2_knhanes_full"] = block(kn, "KNHANES full 301")
    result["P3_three_state"] = {"full": {a: result["P2_knhanes_full"]["arms"][a]["three_state"] for a in ("G0", "G1", "G2")},
                                "clean": {a: result["P2_knhanes_clean"]["arms"][a]["three_state"] for a in ("G0", "G1", "G2")}}

    p4 = {}
    for label, rows in (("knhanes_full", kn), ("knhanes_clean", clean)):
        fam, meta = [], []
        for bl in BASELINES:
            for rec in per_seed_baseline(rows, base, {"baseline": bl}):
                fam.append(rec["p"]); meta.append({"baseline": bl, **rec})
        qs = bh(fam)
        for m, q in zip(meta, qs):
            m["q_BH"] = q
        p4[label] = meta
    result["P4_mcnemar_BH"] = p4

    out = CONF / "r31_holdout.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # console summary
    print("P1 internal: replicated", len(rep), "touched", len(rep_touched),
          "clean positives", result["P1_internal"]["clean_subset_positives"])
    for label in ("P2_knhanes_full", "P2_knhanes_clean"):
        b = result[label]
        print(f"\n{label}: n={b['n_pairs']} gold={b['gold']}")
        for arm in ("G0", "G1", "G2"):
            m = b["arms"][arm]["binary"]
            print(f"  {arm}: TP{m['TP']} FP{m['FP']} FN{m['FN']} F1 {m['F1']}")
        for bl, m in b["baselines"].items():
            print(f"  {bl}: F1 {m['F1_mean']} {m['F1_range']}")
    print("\nwrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
