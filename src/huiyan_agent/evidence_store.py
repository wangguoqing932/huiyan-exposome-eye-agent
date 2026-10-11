"""evidence_store — 证据块存储与风险制导的等级加权检索。

数据源：data/seed/evidence_chunks.jsonl（Phase 2 构建，每行一个 EvidenceChunk JSON）。
证据分级（EVIDENCE_LEVEL_WEIGHTS）：A=监管标签/指南 > B=Meta > C=原创研究 > D=体外/动物 > E=机制推断。

检索策略（risk-guided retrieval）::
    score = Σ(词项命中权重) × 证据等级权重 × chunk 自身 weight
    词项命中：title ×3、实体名/别名命中 ×2、正文 ×1；命中 A/B 实体 id 额外强加权
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from .schemas import EvidenceChunk

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

EVIDENCE_LEVEL_WEIGHTS: dict[str, float] = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0}

# 通用停用词（检索降噪；刻意保持域中立——领域词由查询方提供）
_STOPWORDS = {
    "and", "or", "of", "the", "in", "with", "for", "to", "a", "an", "is", "are",
    "on", "by", "from", "as", "at", "be", "was", "were", "this", "that",
    "patient", "patients", "case", "study", "report", "effect", "effects",
    "use", "used", "may", "can", "risk",
}

_TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+")


def _tokenize(text: str) -> list[str]:
    """中英文混合分词：拉丁词 + CJK 单字（bigram 由调用方按需组合）。"""
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


class EvidenceStore:
    """证据块存储。空库（Phase 2 之前）优雅降级：retrieve 恒返回 []。"""

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            path = _PROJECT_ROOT / "data" / "seed" / "evidence_chunks.jsonl"
        self.path = Path(path)
        self.chunks: list[EvidenceChunk] = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Field mapping: evidence_chunks.jsonl uses chunk_id/journal/linked_rules/tags/provenance
                    # Schema expects: evidence_id/source/entities_a/entities_b/risk_types
                    data.setdefault("evidence_id", data.pop("chunk_id", f"ev_{len(self.chunks):04d}"))
                    data.setdefault("source", data.get("journal", data.get("provenance", "")))
                    data.setdefault("entities_a", data.get("linked_rules", "").split(",") if isinstance(data.get("linked_rules"), str) else [])
                    data.setdefault("entities_b", [])
                    data.setdefault("risk_types", [])
                    data.setdefault("evidence_relation", data.get("tags", ""))
                    data.setdefault("source_locator", data.get("doi", ""))
                    data.setdefault("citation_hint", data.get("doi", ""))
                    self.chunks.append(EvidenceChunk.model_validate(data))
                except Exception:
                    continue  # 坏行跳过，不阻塞整库

    def __len__(self) -> int:
        return len(self.chunks)

    def stats(self) -> dict:
        """证据级别分布（Streamlit Overview / phase2 progress 用）。"""
        dist = Counter(ev.evidence_level or "?" for ev in self.chunks)
        return {"total": len(self.chunks), **{f"level_{k}": v for k, v in sorted(dist.items())}}

    # ------------------------------------------------------------------ #
    # retrieval
    # ------------------------------------------------------------------ #
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        entity_a_id: str | None = None,
        entity_b_id: str | None = None,
    ) -> list[EvidenceChunk]:
        """等级加权的关键词检索；query 可为空（此时仅按实体匹配 + 等级排序）。"""
        tokens = _tokenize(query or "")
        scored: list[tuple[float, int, EvidenceChunk]] = []
        for idx, ev in enumerate(self.chunks):
            score = 0.0
            title_l = ev.title.lower()
            text_l = ev.text.lower()
            ent_l = " ".join(ev.entities_a + ev.entities_b).lower()
            for tok in set(tokens):
                if not tok:
                    continue
                if tok in title_l:
                    score += 3.0
                if tok in ent_l:
                    score += 2.0
                if tok in text_l:
                    score += 1.0
            # 实体强匹配加分（软偏好，不硬过滤——保留近邻证据）
            if entity_a_id and entity_a_id.lower() in ent_l:
                score += 5.0
            if entity_b_id and entity_b_id.lower() in ent_l:
                score += 5.0
            if score <= 0:
                continue
            level_w = EVIDENCE_LEVEL_WEIGHTS.get((ev.evidence_level or "E").upper(), 1.0)
            score *= level_w * max(1, ev.weight)
            scored.append((score, idx, ev))

        scored.sort(key=lambda t: (-t[0], t[1]))
        return [ev for _s, _i, ev in scored[: max(0, top_k)]]

    # ------------------------------------------------------------------ #
    # context 组装（LLM 仲裁输入）
    # ------------------------------------------------------------------ #
    def build_context(self, chunks: list[EvidenceChunk], char_limit: int = 6000) -> str:
        """把证据块拼成带编号与来源标注的上下文文本，超限截断。"""
        parts: list[str] = []
        used = 0
        for i, ev in enumerate(chunks, 1):
            loc = f" | {ev.source_locator}" if ev.source_locator else ""
            cite = ev.citation_hint or ev.pmid or ev.doi
            cite_s = f" | 引文:{cite}" if cite else ""
            block = f"[EV{i}] (Level {ev.evidence_level or '?'} | {ev.source}{loc}{cite_s}) {ev.title}\n{ev.text}"
            if used + len(block) > char_limit:
                block = block[: max(0, char_limit - used)]
            if not block:
                break
            parts.append(block)
            used += len(block) + 2
            if used >= char_limit:
                break
        return "\n\n".join(parts)


def load_evidence_chunks(path: str | Path | None = None) -> list[EvidenceChunk]:
    """便捷加载（供 naive_rag 基线等直接用 chunk 列表的调用方）。"""
    return EvidenceStore(path).chunks
