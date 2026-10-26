#!/usr/bin/env python
"""Build the canonical, de-duplicated baseline prediction matrix.

Why this file exists
--------------------
`baseline_predictions.jsonl` and `baseline_predictions_knhanes.jsonl` are
append-only journals: re-runs and discarded variants were appended without a
variant field. Reading them naively (group by baseline+seed) mixes runs and
produces wrong F1 values -- e.g. NHANES full_system 0.385 instead of 0.480,
KNHANES full_system 0.345 instead of 0.360.

The two rules that reproduce every number reported in the manuscript are:

  1. keep only `valid == True` rows (where the field exists);
  2. for each (dataset, generation, baseline, seed, a_flag, b_item) keep the
     LAST row, because later appended blocks are the corrected re-runs.

This script writes `outputs/baseline_predictions_canonical.jsonl` with explicit
`dataset_id`, `dataset_role` and `generation` fields so downstream code no
longer has to know the journal's ordering. The raw journals are left untouched.

NHANES has two generations: qwen (80 pairs, R11 gold) and zhipu GLM-5.3-flash
(159 pairs). The qwen full_system rows are scored against the R11 gold in
`outputs/confirmatory/nhanes_confirmatory.csv`, not against the gold embedded
in the journal, so the 0.522 the manuscript reports is reproducible.

Run: python scripts/build_canonical_predictions.py
Verify: python scripts/verify_canonical_predictions.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
NHANES = OUT / "baseline_predictions.jsonl"
KNHANES = OUT / "baseline_predictions_knhanes.jsonl"
DEST = OUT / "baseline_predictions_canonical.jsonl"

QWEN_PROVIDER = "local:qwen3.8-27b"
ZHIPU_PROVIDER = "zhipu:glm-5.3-flash"


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def dedup_last(rows: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    """Keep the last appended row for each key (later blocks are corrected re-runs)."""
    kept: dict[tuple, dict] = {}
    for row in rows:
        kept[tuple(row.get(k) for k in key_fields)] = row
    return list(kept.values())


def add_meta(rows: list[dict], dataset_id: str, role: str, generation: str) -> list[dict]:
    out = []
    for row in rows:
        row = dict(row)
        row["dataset_id"] = dataset_id
        row["dataset_role"] = role
        row["generation"] = generation
        out.append(row)
    return out


def main() -> int:
    nhanes = load(NHANES)
    knhanes = load(KNHANES)

    # qwen-generation pair set defines the 80-pair scoring surface.
    qwen_pairs = {(r["a_flag"], r["b_item"]) for r in nhanes
                  if r["baseline"] == "lightrag" and r["provider"] == QWEN_PROVIDER}
    if len(qwen_pairs) != 80:
        raise SystemExit(f"expected 80 qwen pairs, found {len(qwen_pairs)}")

    # R11 gold for the 80-pair surface (confirmatory table is the authority).
    gold = pd.read_csv(OUT / "confirmatory" / "nhanes_confirmatory.csv",
                       encoding="utf-8-sig").drop_duplicates(
                           ["a_flag", "b_item"]).set_index(
                               ["a_flag", "b_item"])["gold3"].to_dict()

    canonical: list[dict] = []

    def apply_r11_gold(rows: list[dict]) -> list[dict]:
        """Score the qwen generation against the R11 gold, not the embedded R5 gold."""
        for row in rows:
            row["gold3"] = gold.get((row["a_flag"], row["b_item"]), row["gold3"])
        return rows

    # --- NHANES, qwen generation (80 pairs) ---------------------------------
    for baseline in ("lightrag", "pure_llm", "naive_rag"):
        rows = [r for r in nhanes
                if r["baseline"] == baseline and r["provider"] == QWEN_PROVIDER
                and r.get("valid", True)]
        rows = apply_r11_gold(dedup_last(rows, ("seed", "a_flag", "b_item")))
        canonical += add_meta(rows, "intval-nhanes", "internal_validation",
                              "qwen-80pair")

    fs_qwen = [r for r in nhanes
               if r["baseline"] == "full_system"
               and (r["a_flag"], r["b_item"]) in qwen_pairs]
    fs_qwen = apply_r11_gold(dedup_last(fs_qwen, ("seed", "a_flag", "b_item")))
    canonical += add_meta(fs_qwen, "intval-nhanes", "internal_validation",
                          "qwen-80pair")

    # --- NHANES, zhipu generation (159 pairs) -------------------------------
    for baseline in ("lightrag", "pure_llm", "naive_rag"):
        rows = [r for r in nhanes
                if r["baseline"] == baseline and r["provider"] == ZHIPU_PROVIDER
                and r.get("valid", True)]
        rows = dedup_last(rows, ("seed", "a_flag", "b_item"))
        canonical += add_meta(rows, "intval-nhanes", "internal_validation",
                              "zhipu-159pair")

    fs_zhipu = [r for r in nhanes if r["baseline"] == "full_system"]
    fs_zhipu = dedup_last(fs_zhipu, ("seed", "a_flag", "b_item"))
    canonical += add_meta(fs_zhipu, "intval-nhanes", "internal_validation",
                          "zhipu-159pair")

    # --- KNHANES (301 pairs, zhipu backend) ---------------------------------
    for baseline in ("full_system", "lightrag", "pure_llm", "naive_rag"):
        rows = [r for r in knhanes
                if r["baseline"] == baseline and r.get("valid", True)]
        rows = dedup_last(rows, ("seed", "a_flag", "b_item"))
        canonical += add_meta(rows, "extval-knhanes", "external_validation",
                              "zhipu-knhanes-301pair")

    order = {"intval-nhanes": 0, "extval-knhanes": 1}
    canonical.sort(key=lambda r: (
        order.get(r["dataset_id"], 9), r["generation"], r["baseline"],
        r["seed"], r["a_flag"], r["b_item"]))

    with DEST.open("w", encoding="utf-8") as fh:
        for row in canonical:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"[canonical] {len(canonical):,} rows -> {DEST}")
    counts = __import__("collections").Counter(
        (r["dataset_id"], r["generation"], r["baseline"]) for r in canonical)
    for (ds, gen, bl), n in sorted(counts.items()):
        print(f"  {ds:16s} {gen:22s} {bl:12s} {n:5d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
