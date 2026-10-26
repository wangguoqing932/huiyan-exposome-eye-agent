#!/usr/bin/env python
"""Verify that the canonical prediction matrix reproduces every reported F1.

This is the regression test for `build_canonical_predictions.py`: if the
dedup rule, the gold source, or the generation split drifts, the numbers printed
here stop matching the manuscript and the script exits non-zero.

Run: python scripts/verify_canonical_predictions.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = ROOT / "outputs" / "baseline_predictions_canonical.jsonl"

EXPECTED = {
    ("intval-nhanes", "qwen-80pair", "full_system"): 0.522,
    ("intval-nhanes", "qwen-80pair", "lightrag"): 0.392,
    ("intval-nhanes", "qwen-80pair", "pure_llm"): 0.335,
    ("intval-nhanes", "qwen-80pair", "naive_rag"): 0.080,
    ("intval-nhanes", "zhipu-159pair", "full_system"): 0.480,
    ("intval-nhanes", "zhipu-159pair", "lightrag"): 0.186,
    ("intval-nhanes", "zhipu-159pair", "pure_llm"): 0.178,
    ("intval-nhanes", "zhipu-159pair", "naive_rag"): 0.069,
    ("extval-knhanes", "zhipu-knhanes-301pair", "full_system"): 0.360,
    ("extval-knhanes", "zhipu-knhanes-301pair", "lightrag"): 0.145,
    ("extval-knhanes", "zhipu-knhanes-301pair", "pure_llm"): 0.135,
    ("extval-knhanes", "zhipu-knhanes-301pair", "naive_rag"): 0.094,
}
TOL = 0.003


def f1(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def main() -> int:
    rows = [json.loads(line) for line in CANON.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["dataset_id"], row["generation"], row["baseline"])].append(row)

    failures = 0
    print(f"[canonical] {len(rows):,} rows, {len(groups)} groups")
    for key, expected in EXPECTED.items():
        sub = groups.get(key)
        if not sub:
            print(f"  MISSING {key}")
            failures += 1
            continue
        per_seed = defaultdict(lambda: [0, 0, 0])
        for row in sub:
            tp, fp, fn = per_seed[row["seed"]]
            if row["prediction"] and row["gold3"] == "replicated":
                tp += 1
            elif row["prediction"]:
                fp += 1
            elif row["gold3"] == "replicated":
                fn += 1
            per_seed[row["seed"]] = [tp, fp, fn]
        scores = [f1(*counts) for counts in per_seed.values()]
        mean = sum(scores) / len(scores)
        ok = abs(mean - expected) <= TOL
        failures += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'} {key[0]:16s} {key[1]:22s} {key[2]:12s} "
              f"F1={mean:.3f} (expected {expected:.3f}, n/seed={len(sub)//len(per_seed)})")

    print(f"\n{len(EXPECTED) - failures}/{len(EXPECTED)} checks PASS")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
