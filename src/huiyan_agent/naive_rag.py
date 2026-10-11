"""naive_rag — 关键词检索基线（4 基线对比中的 naive_rag 档）。

与 EvidenceStore 的区别（基线公平性）：**不做**证据等级加权、**不做**实体 id
强匹配加分——纯词项命中率排序。接口与 EvidenceStore.retrieve 保持一致，
便于 run_baselines 在同一评估循环中切换。
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .evidence_store import _tokenize
from .schemas import EvidenceChunk

if TYPE_CHECKING:  # 仅注解用；运行时走局部导入避免环
    from .evidence_store import EvidenceStore


class NaiveRAG:
    """纯词频检索基线。"""

    def __init__(self, source: EvidenceStore | list[EvidenceChunk] | str | Path | None = None) -> None:
        if source is None:
            from .evidence_store import EvidenceStore  # 局部导入避免环

            self.chunks = EvidenceStore().chunks
        elif isinstance(source, list):
            self.chunks = source
        elif isinstance(source, str | Path):
            from .evidence_store import EvidenceStore

            self.chunks = EvidenceStore(source).chunks
        else:  # EvidenceStore 实例
            self.chunks = source.chunks

    def __len__(self) -> int:
        return len(self.chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        entity_a_id: str | None = None,
        entity_b_id: str | None = None,
    ) -> list[EvidenceChunk]:
        """词项命中计数排序（title ×1 / 实体 ×1 / 正文 ×1，无等级加权）。"""
        tokens = set(_tokenize(query or ""))
        scored: list[tuple[int, int, EvidenceChunk]] = []
        for idx, ev in enumerate(self.chunks):
            bag = _tokenize(ev.title + " " + " ".join(ev.entities_a + ev.entities_b) + " " + ev.text)
            if not tokens:
                hits = 0
            else:
                counts = Counter_safe(bag)
                hits = sum(counts.get(t, 0) for t in tokens)
            if hits <= 0:
                continue
            scored.append((hits, idx, ev))
        scored.sort(key=lambda t: (-t[0], t[1]))
        return [ev for _h, _i, ev in scored[: max(0, top_k)]]


def Counter_safe(bag: list[str]) -> dict[str, int]:
    """轻量词频计数（避免基线依赖 collections.Counter 的额外语义）。"""
    freq: dict[str, int] = {}
    for tok in bag:
        freq[tok] = freq.get(tok, 0) + 1
    return freq
