#!/usr/bin/env python
"""Build LightRAG index. B2: uses insert_chunks (not nonexistent build_from_jsonl).

A2: builds CORE SET only (rule evidence + competitor, ~28 chunks).
    Full 521-chunk index deferred until core quality validated.
B1: passes ids (chunk_id) and file_paths (DOI/PMID) for traceability.
B3: pre-injects entity annotations (entities_a/b flags from rules + registry).
B6: filters out <300 char garbage chunks (corrigendum/editorial/comment).

Run: PYTHONUTF8=1 .venv/Scripts/python.exe scripts/build_lightrag_index.py
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("LIGHTRAG_WORKING_DIR", str(ROOT / "data/processed/lightrag_index"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

def prepare_core_chunks() -> tuple[list[str], list[str], list[str]]:
    """B2+B3+B4+B6: Load, annotate, filter, and return (texts, ids, file_paths)."""
    import yaml
    import csv

    rules = yaml.safe_load((ROOT / "configs/rules.yaml").read_text(encoding="utf-8"))["rules"]
    # B4: short-to-full rule ID mapping
    short_to_rule = {}
    for r in rules:
        sid = r["id"].split("_")[0]
        short_to_rule[sid] = r

    chunks = []
    with (ROOT / "data/seed/evidence_chunks.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    # B6: Filter garbage (<300 chars)
    filtered = [c for c in chunks if len(c.get("text", "")) >= 300]
    garbage_count = len(chunks) - len(filtered)

    # A2 revised: Build FULL index (~1060 chunks after PPP cleaning), not just core 30.
    # User decision 2026-10-11: 30-chunk core was too small for a meaningful KG.
    # 91% of probe chunks contain relevant eye/exposure content.
    core = filtered

    print(f"[build] {len(chunks)} total → {garbage_count} garbage removed → {len(core)} chunks for full index")

    # B3: Inject entity annotations from rules (B4 short IDs handled)
    annotated = 0
    for c in core:
        linked = c.get("linked_rules", "").strip()
        if not linked:
            continue
        entities_a = []
        entities_b = []
        for sid in linked.split(","):
            sid = sid.strip()
            r = short_to_rule.get(sid)
            if r:
                entities_a.extend(r.get("entity_a_flags", []))
                entities_b.extend(r.get("entity_b_flags", []))
        if entities_a or entities_b:
            c["entities_a"] = list(set(entities_a))
            c["entities_b"] = list(set(entities_b))
            annotated += 1

    print(f"[build] {annotated}/{len(core)} rule-linked chunks annotated with entity flags")

    # Prepare insert lists (B1: ids + file_paths for traceability)
    texts, ids, fps = [], [], []
    for c in core:
        texts.append(c.get("text", ""))
        ids.append(c.get("chunk_id", f"unk_{len(ids)}"))
        doi = c.get("doi", "")
        pmid = c.get("pmid", "")
        fps.append(f"doi:{doi}" if doi else (f"pmid:{pmid}" if pmid else c.get("chunk_id", "unknown")))

    return texts, ids, fps


def main() -> int:
    print("=" * 60)
    print("LightRAG Core Index Build (A1=English, A2=core~28, B1-B8 fixes)")
    print("=" * 60)

    texts, ids, fps = prepare_core_chunks()
    if not texts:
        print("[build] ERROR: 0 core chunks — check evidence_chunks.jsonl")
        return 1
    print(f"[build] Inserting {len(texts)} chunks...")
    print(f"[build] Working dir: {os.environ.get('LIGHTRAG_WORKING_DIR', 'default')}")

    from huiyan_agent.lightrag_adapter import LightRAGAdapter
    adapter = LightRAGAdapter()  # A1: language="English" is now the default

    t0 = time.time()
    adapter.insert_chunks(texts, ids=ids, file_paths=fps, batch_size=10)
    elapsed = time.time() - t0

    stats = adapter.stats()
    fabricated = getattr(adapter, "_completion_marker_fabricated", 0)

    print(f"\n[build] Done in {elapsed:.0f}s")
    print(f"[build] Stats: {json.dumps(stats, indent=2)}")
    print(f"[build] B5 fabricated COMPLETE markers: {fabricated}/{len(texts)}")
    if fabricated > len(texts) * 0.3:
        print(f"[build] WARNING: >30% outputs needed fabricated markers — raise max_tokens")

    # B8: Clean shutdown (kill lingering event loop threads + httpx connections)
    print("[build] Cleaning up...")
    import gc
    del adapter
    gc.collect()
    os._exit(0)

if __name__ == "__main__":
    sys.exit(main())
