#!/usr/bin/env python
"""Semantic evidence retrieval over the LightRAG chunk vector store
(analysis_plan §15, R6.0).

Loads data/processed/lightrag_index/vdb_chunks.json (nano-vectordb export:
per-record zlib+base64 float16 2048-d vectors), joins chunk ids to
EvidenceChunk metadata from data/seed/evidence_chunks.jsonl (level/flags),
and provides cosine top-k search with Ark Doubao embedding queries (same
model family used to build the index).
"""
from __future__ import annotations
import base64
import json
import re
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


@dataclass
class SemChunk:
    chunk_id: str
    text: str
    level: str          # evidence level A-E from the pool (may be '')
    flag_a: str | None  # from [exposure: X] annotation, if present
    flag_b: str | None  # from [outcome: Y] annotation, if present
    sim: float = 0.0


_ANNOT_RE = re.compile(r"\[exposure:\s*([^\]|]+)\s*\|\s*outcome:\s*([^\]]+)\]")


class SemanticEvidenceIndex:
    def __init__(self, vdb_path: Path | None = None, pool_path: Path | None = None):
        vdb_path = vdb_path or ROOT / "data/processed/lightrag_index/vdb_chunks.json"
        pool_path = pool_path or ROOT / "data/seed/evidence_chunks.jsonl"
        d = json.loads(vdb_path.read_text(encoding="utf-8"))
        levels = {}
        for line in pool_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            levels[r.get("chunk_id")] = (r.get("evidence_level") or "").upper()
        self.ids: list[str] = []
        texts: list[str] = []
        vecs = []
        self.flags: list[tuple[str | None, str | None]] = []
        self.levels: list[str] = []
        for rec in d["data"]:
            raw = zlib.decompress(base64.b64decode(rec["vector"]))
            vec = np.frombuffer(raw, dtype=np.float16).astype(np.float32)
            vecs.append(vec)
            content = rec.get("content") or ""
            cid = rec.get("full_doc_id") or rec.get("__id__", "")
            m = _ANNOT_RE.search(content[:200])
            fa = m.group(1).strip() if m else None
            fb = m.group(2).strip() if m else None
            if fa is None:
                # annotation may embed multiple flags separated by /
                fa2 = re.search(r"exposure:\s*([^\]|]+)", content[:200])
                fa = fa2.group(1).strip() if fa2 else None
            self.ids.append(cid)
            texts.append(content)
            self.flags.append((fa, fb))
            self.levels.append(levels.get(cid, ""))
        self.texts = texts
        mat = np.vstack(vecs)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.mat = mat / norms
        self._embed_cache: dict[str, np.ndarray] = {}

    def embed(self, query: str) -> np.ndarray:
        if query in self._embed_cache:
            return self._embed_cache[query]
        from huiyan_agent.embedding_client import ArkVisionEmbedding
        ec = ArkVisionEmbedding()
        vec = np.asarray(ec.embed([query])[0], dtype=np.float32)
        n = float(np.linalg.norm(vec)) or 1.0
        vec = vec / n
        self._embed_cache[query] = vec
        return vec

    def search(self, query: str, top_k: int = 8) -> list[SemChunk]:
        q = self.embed(query)
        sims = self.mat @ q
        order = np.argsort(-sims)[:top_k]
        out = []
        for i in order:
            fa, fb = self.flags[i]
            out.append(SemChunk(self.ids[i], self.texts[i], self.levels[i],
                                fa, fb, float(sims[i])))
        return out

    def filter_relevant(self, chunks: list[SemChunk], tau: float,
                        a_flag: str, b_flag: str,
                        a_term: str, b_term: str) -> list[SemChunk]:
        """§15: relevant = sim>=tau AND (annotation hits exposure OR outcome
        flag OR text contains both literature terms)."""
        out = []
        for c in chunks:
            if c.sim < tau:
                continue
            annot_hit = False
            if c.flag_a or c.flag_b:
                fa, fb = c.flag_a or "", c.flag_b or ""
                annot_hit = (a_flag in fa or a_flag in fb
                             or b_flag in fa or b_flag in fb)
            if not annot_hit:
                tl = c.text.lower()
                annot_hit = a_term.lower() in tl and b_term.lower() in tl
            if annot_hit:
                out.append(c)
        return out
