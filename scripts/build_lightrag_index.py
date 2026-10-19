#!/usr/bin/env python
"""Build LightRAG index — FINAL version with all pre-build fixes.

B1: passes ids + file_paths for traceability
B2: uses insert_chunks (not build_from_jsonl)
B3: entity annotations PREPENDED to text (not just metadata) — changes what goes into the index
B4: short-to-full rule ID mapping
B6: filters <300 char garbage
B7: stats reads actual graph storage
B8: sys.stdout.flush() before os._exit()
Resume: reads doc_status to skip completed, clean residues, ignore dup-*

Run: PYTHONUTF8=1 .venv/Scripts/python.exe scripts/build_lightrag_index.py
"""
from __future__ import annotations
import json, os, sys, time, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("PYTHONUTF8", "1")
WORKING_DIR = ROOT / "data/processed/lightrag_index"
os.environ.setdefault("LIGHTRAG_WORKING_DIR", str(ROOT / "data/processed/lightrag_index"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def prepare_chunks() -> tuple[list[str], list[str], list[str]]:
    """Load, annotate (B3: prepend to text), filter (B6), return (texts, ids, file_paths)."""
    import yaml

    rules = yaml.safe_load((ROOT / "configs/rules.yaml").read_text(encoding="utf-8"))["rules"]
    short_to_rule = {}
    for r in rules:
        sid = r["id"].split("_")[0]
        short_to_rule[sid] = r

    # Registry names for keyword matching of non-rule chunks
    import csv
    a_registry = {}
    with (ROOT / "data/seed/entities_a.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            names = [row.get("primary_name", "")]
            aliases = [a.strip() for a in row.get("aliases", "").split(";") if a.strip()]
            a_registry[row["exposure_id"]] = [n for n in names + aliases if n and len(n) >= 4]

    b_registry = {}
    with (ROOT / "data/seed/entities_b.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            names = [row.get("generic_name", "")]
            aliases = [a.strip() for a in row.get("aliases", "").split(";") if a.strip()]
            b_registry[row["entity_b_id"]] = [n for n in names + aliases if n and len(n) >= 4]

    chunks = []
    with (ROOT / "data/seed/evidence_chunks.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    # B6: Filter garbage
    filtered = [c for c in chunks if len(c.get("text", "")) >= 300]
    print(f"[prep] {len(chunks)} total → {len(chunks)-len(filtered)} garbage → {len(filtered)} chunks")

    # B3: Annotate text (prepend entity tags) — this is what LightRAG actually sees
    rule_annotated = 0
    kw_annotated = 0
    texts, ids, fps = [], [], []

    for c in filtered:
        text = c.get("text", "")
        chunk_id = c.get("chunk_id", f"unk_{len(ids)}")
        linked = c.get("linked_rules", "").strip()
        prefix_parts = []

        if linked:
            # Rule-linked chunk: prepend [exposure: X | outcome: Y]
            entities_a = set()
            entities_b = set()
            for sid in linked.split(","):
                sid = sid.strip()
                r = short_to_rule.get(sid)
                if r:
                    entities_a.update(r.get("entity_a_flags", []))
                    entities_b.update(r.get("entity_b_flags", []))
            if entities_a or entities_b:
                a_str = ", ".join(sorted(entities_a))
                b_str = ", ".join(sorted(entities_b))
                prefix_parts.append(f"[exposure: {a_str} | outcome: {b_str}]")
                rule_annotated += 1
        else:
            # Non-rule chunk: keyword match against registry
            text_lower = text.lower()
            matched_a = set()
            matched_b = set()
            for eid, names in a_registry.items():
                if any(n.lower() in text_lower for n in names):
                    matched_a.add(eid)
            for bid, names in b_registry.items():
                if any(n.lower() in text_lower for n in names):
                    matched_b.add(bid)
            if matched_a or matched_b:
                a_str = ", ".join(sorted(list(matched_a)[:5]))
                b_str = ", ".join(sorted(list(matched_b)[:5]))
                prefix_parts.append(f"[exposure: {a_str} | outcome: {b_str}]")
                kw_annotated += 1

        if prefix_parts:
            text = " ".join(prefix_parts) + "\n" + text

        doi = c.get("doi", "")
        pmid = c.get("pmid", "")
        fp = f"doi:{doi}" if doi else (f"pmid:{pmid}" if pmid else chunk_id)

        texts.append(text)
        ids.append(chunk_id)
        fps.append(fp)

    print(f"[prep] B3 annotations: {rule_annotated} rule-linked + {kw_annotated} keyword-matched = {rule_annotated + kw_annotated}/{len(filtered)} ({(rule_annotated+kw_annotated)/max(1,len(filtered))*100:.0f}%)")
    return texts, ids, fps


def check_resume(adapter) -> tuple[list[int], list[int]]:
    """Read doc_status to determine which chunks to skip vs insert.

    Returns (indices_to_skip, indices_to_insert).
    """
    status_file = Path(os.environ["LIGHTRAG_WORKING_DIR"]) / "kv_store_doc_status.json"
    if not status_file.exists():
        return [], list(range(len(_ALL_IDS)))

    try:
        status = json.loads(status_file.read_text(encoding="utf-8"))
    except Exception:
        return [], list(range(len(_ALL_IDS)))

    skip = []
    insert = []
    stale_processing = []

    for i, chunk_id in enumerate(_ALL_IDS):
        # Check original ID
        entry = status.get(chunk_id)
        if entry is None:
            # Check dup- prefixed IDs (LightRAG deduplication)
            dup_key = f"dup-{chunk_id}"
            dup_entry = status.get(dup_key)
            if dup_entry is not None:
                # dup- entries are historical artifacts; skip them
                continue

        if entry is None:
            insert.append(i)
            continue

        status_val = entry.get("status", "") if isinstance(entry, dict) else ""

        if status_val == "processed":
            skip.append(i)
        elif status_val in ("processing", "parsing", "analyzing"):
            stale_processing.append(i)
            insert.append(i)  # re-insert
        else:
            insert.append(i)  # failed or unknown → retry

    if stale_processing:
        print(f"[resume] {len(stale_processing)} stale processing entries will be re-inserted")
    if skip:
        print(f"[resume] {len(skip)} already processed → skipping")
    print(f"[resume] {len(insert)} to insert")

    return skip, insert


# Globals for resume check
_ALL_IDS: list[str] = []
_ALL_TEXTS: list[str] = []
_ALL_FPS: list[str] = []


def main() -> int:
    global _ALL_IDS, _ALL_TEXTS, _ALL_FPS

    print("=" * 60)
    print("LightRAG Full Index Build — FINAL")
    print(f"Working dir: {os.environ['LIGHTRAG_WORKING_DIR']}")
    print("=" * 60)

    texts, ids, fps = prepare_chunks()
    if not texts:
        print("[build] ERROR: 0 chunks")
        return 1

    _ALL_IDS = ids
    _ALL_TEXTS = texts
    _ALL_FPS = fps

    from huiyan_agent.lightrag_adapter import LightRAGAdapter
    adapter = LightRAGAdapter()

    # Resume check
    skip, insert = check_resume(adapter)
    if not insert:
        print("[build] All chunks already indexed — nothing to do")
        stats = adapter.stats()
        print(f"[build] Stats: {json.dumps(stats, indent=2)}")
        sys.stdout.flush()
        os._exit(0)

    print(f"\n[build] Inserting {len(insert)}/{len(ids)} chunks...")
    insert_texts = [texts[i] for i in insert]
    insert_ids = [ids[i] for i in insert]
    insert_fps = [fps[i] for i in insert]

    t0 = time.time()
    last_progress = 0

    for batch_start in range(0, len(insert_texts), 10):
        batch_texts = insert_texts[batch_start:batch_start+10]
        batch_ids = insert_ids[batch_start:batch_start+10]
        batch_fps = insert_fps[batch_start:batch_start+10]

        adapter.insert_chunks(batch_texts, ids=batch_ids, file_paths=batch_fps, batch_size=10)

        done = min(batch_start + 10, len(insert_texts))
        elapsed = time.time() - t0
        rate = done / max(1, elapsed) * 60  # chunks/min
        remaining = (len(insert_texts) - done) / max(0.1, rate)
        if done - last_progress >= 50 or done == len(insert_texts):
            print(f"[build] {done}/{len(insert_texts)} ({done/len(insert_texts)*100:.0f}%) | "
                  f"{elapsed:.0f}s elapsed | ~{remaining:.0f}min remaining")
            last_progress = done
            sys.stdout.flush()

    elapsed = time.time() - t0
    stats = adapter.stats()
    fabricated = getattr(adapter, "_completion_marker_fabricated", 0)

    print(f"\n{'='*60}")
    print(f"[build] DONE in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"[build] Stats: {json.dumps(stats, indent=2)}")
    print(f"[build] B5 fabricated COMPLETE markers: {fabricated}/{len(insert_texts)}")
    if fabricated > len(insert_texts) * 0.3:
        print(f"[build] WARNING: >30% needed fabricated markers")
    print(f"{'='*60}")

    # B8: flush before exit
    print("[build] Cleaning up...")
    sys.stdout.flush()
    sys.stderr.flush()
    import gc
    del adapter
    gc.collect()
    os._exit(0)

if __name__ == "__main__":
    sys.exit(main())
