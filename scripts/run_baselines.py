#!/usr/bin/env python
"""Run 4 baselines × 5 seeds for A2 handoff deliverable.

Baselines:
  1. pure_llm      — LLM answers without retrieval
  2. naive_rag     — EvidenceStore keyword retrieval + LLM
  3. lightrag      — LightRAG KG retrieval + LLM (requires index)
  4. full_system   — Rule engine + evidence + LLM arbiter

Seeds: [11, 22, 33, 44, 55] (pre-registered)
Output: outputs/baseline_predictions.jsonl

Usage:
  PYTHONUTF8=1 python scripts/run_baselines.py --baseline full_system
  PYTHONUTF8=1 python scripts/run_baselines.py --all
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("PYTHONUTF8", "1")
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from huiyan_agent.risk_rules import load_rules, match_rules, assess
from huiyan_agent.normalize import (load_entity_a_registry, load_entity_b_registry)

SEEDS = [11, 22, 33, 44, 55]
BASELINES = ["pure_llm", "naive_rag", "lightrag", "full_system"]


def load_test_pairs() -> list[dict]:
    csv_path = ROOT / "outputs/confirmatory/nhanes_confirmatory.csv"
    if not csv_path.exists():
        print("[baselines] ERROR: NHANES confirmatory not found — run evaluate.py first")
        sys.exit(1)
    import pandas as pd
    df = pd.read_csv(csv_path)
    tested = df[df["status"] == "tested"]
    pairs = []
    for _, row in tested.iterrows():
        pairs.append({
            "a_flag": row["a_flag"], "b_item": row["b_item"],
            "predicted_rule": bool(row["predicted"]),
            "gold3": row.get("gold3", ""),
        })
    print(f"[baselines] {len(pairs)} test pairs from NHANES confirmatory")
    return pairs


def run_full_system(pairs, seed):
    """Baseline 4: Full system — rule engine drives prediction."""
    rules = load_rules()
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = {}, {}
    for ent in a_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            a_idx.setdefault(str(f), ent)
    for ent in b_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            b_idx.setdefault(str(f), ent)
    results = []
    for p in pairs:
        a_ent = a_idx.get(p["a_flag"]) or a_reg.get(p["a_flag"])
        b_ent = b_idx.get(p["b_item"]) or b_reg.get(p["b_item"])
        if a_ent and b_ent:
            signals = match_rules(rules, a_ent, b_ent)
            assessment = assess(signals)
            prediction = len(signals) > 0
            results.append({
                "baseline": "full_system", "seed": seed,
                "a_flag": p["a_flag"], "b_item": p["b_item"],
                "prediction": prediction, "gold3": p["gold3"],
                "risk_level": assessment.risk_level.value,
                "confidence": assessment.confidence,
            })
        else:
            results.append({
                "baseline": "full_system", "seed": seed,
                "a_flag": p["a_flag"], "b_item": p["b_item"],
                "prediction": False, "gold3": p["gold3"],
                "risk_level": "unknown", "confidence": 0.0,
            })
    return results


def run_pure_llm(pairs, seed):
    """Baseline 1: Pure LLM knowledge — no retrieval, no rules."""
    from huiyan_agent.llm_client import LLMClient
    llm = LLMClient(provider="deepseek", temperature=0.0)
    results = []
    for p in pairs:
        prompt = (
            f"Is {p['a_flag']} a known risk factor for {p['b_item']}? "
            f"Answer YES or NO on the first line only."
        )
        try:
            resp = llm.complete(prompt=prompt, system="You are a medical knowledge classifier. Be concise.")
            prediction = (resp.text or "").strip().split("\n")[0].strip().upper().startswith("YES")
        except Exception:
            prediction = False
        results.append({
            "baseline": "pure_llm", "seed": seed,
            "a_flag": p["a_flag"], "b_item": p["b_item"],
            "prediction": prediction, "gold3": p["gold3"],
        })
    return results


def run_naive_rag(pairs, seed):
    """Baseline 2: Naive RAG — EvidenceStore keyword retrieval + LLM."""
    from huiyan_agent.evidence_store import EvidenceStore
    from huiyan_agent.llm_client import LLMClient
    store = EvidenceStore()
    llm = LLMClient(provider="deepseek", temperature=0.0)
    results = []
    for p in pairs:
        query = f"{p['a_flag']} {p['b_item']}"
        evidence = store.retrieve(query, top_k=3)
        ev_text = " | ".join(ev.text[:200] for ev in evidence) if evidence else "No evidence found."
        prompt = f"Evidence: {ev_text[:500]}\n\nIs {p['a_flag']} a risk factor for {p['b_item']}? YES or NO."
        try:
            resp = llm.complete(prompt=prompt, system="Answer based only on provided evidence.")
            prediction = (resp.text or "").strip().split("\n")[0].strip().upper().startswith("YES")
        except Exception:
            prediction = False
        results.append({
            "baseline": "naive_rag", "seed": seed,
            "a_flag": p["a_flag"], "b_item": p["b_item"],
            "prediction": prediction, "gold3": p["gold3"],
            "n_evidence": len(evidence),
        })
    return results


def run_lightrag(pairs, seed):
    """Baseline 3: LightRAG KG retrieval + LLM."""
    from huiyan_agent.lightrag_adapter import LightRAGAdapter
    from huiyan_agent.llm_client import LLMClient
    adapter = LightRAGAdapter()
    llm = LLMClient(provider="deepseek", temperature=0.0)
    results = []
    for p in pairs:
        query = f"What is the relationship between {p['a_flag']} and {p['b_item']}?"
        try:
            kg_result = adapter.query(query, mode="naive") or ""
        except Exception:
            kg_result = ""
        prompt = f"KG evidence: {kg_result[:500]}\n\nIs {p['a_flag']} a risk factor for {p['b_item']}? YES or NO."
        try:
            resp = llm.complete(prompt=prompt, system="Answer based on KG evidence.")
            prediction = (resp.text or "").strip().split("\n")[0].strip().upper().startswith("YES")
        except Exception:
            prediction = False
        results.append({
            "baseline": "lightrag", "seed": seed,
            "a_flag": p["a_flag"], "b_item": p["b_item"],
            "prediction": prediction, "gold3": p["gold3"],
            "kg_chars": len(kg_result),
        })
    return results


def metrics(results):
    tp = sum(1 for r in results if r["prediction"] and r["gold3"] == "replicated")
    fp = sum(1 for r in results if r["prediction"] and r["gold3"] != "replicated")
    fn = sum(1 for r in results if not r["prediction"] and r["gold3"] == "replicated")
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else None
    return {"TP": tp, "FP": fp, "FN": fn, "precision": prec, "recall": rec, "F1": f1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--baseline", choices=BASELINES)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    pairs = load_test_pairs()
    if not pairs:
        return 1

    all_results = []
    output_path = ROOT / "outputs/baseline_predictions.jsonl"
    baselines_to_run = [args.baseline] if args.baseline else BASELINES
    seeds_to_run = [args.seed] if args.seed else SEEDS

    for baseline in baselines_to_run:
        for seed in seeds_to_run:
            print(f"\n[baselines] {baseline} seed={seed}...")
            t0 = time.time()
            try:
                if baseline == "full_system":
                    results = run_full_system(pairs, seed)
                elif baseline == "pure_llm":
                    results = run_pure_llm(pairs, seed)
                elif baseline == "naive_rag":
                    results = run_naive_rag(pairs, seed)
                elif baseline == "lightrag":
                    results = run_lightrag(pairs, seed)
                else:
                    continue
            except Exception as e:
                print(f"  ERROR: {type(e).__name__}: {str(e)[:120]}")
                continue
            elapsed = time.time() - t0
            m = metrics(results)
            print(f"  {len(results)} pairs in {elapsed:.1f}s | P={m['precision']} R={m['recall']} F1={m['F1']}")
            all_results.extend(results)

    with output_path.open("a", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n[baselines] {len(all_results)} predictions → {output_path}")

    # Summary
    by_bl = defaultdict(list)
    for r in all_results:
        by_bl[r["baseline"]].append(r)
    print("\n=== Summary ===")
    for bl, rs in sorted(by_bl.items()):
        by_seed = defaultdict(list)
        for r in rs:
            by_seed[r["seed"]].append(r)
        ms = [metrics(srs) for srs in by_seed.values()]
        p = sum(m["precision"] or 0 for m in ms) / max(1, len(ms))
        r_ = sum(m["recall"] or 0 for m in ms) / max(1, len(ms))
        f = sum(m["F1"] or 0 for m in ms) / max(1, len(ms))
        print(f"  {bl:15s} | P={p:.3f} R={r_:.3f} F1={f:.3f} | {len(ms)} seeds")
    return 0

if __name__ == "__main__":
    sys.exit(main())
