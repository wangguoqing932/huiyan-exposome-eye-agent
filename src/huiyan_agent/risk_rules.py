"""risk_rules — 慧眼规则引擎：flags 驱动的暴露×眼病相互作用规则匹配。

机制（与 PLAN.md §4 / configs/rules.yaml 严格对应）::

    规则命中 = entity_a_flags 有交集 **且** entity_b_flags 有交集
    严重度   = 规则基础 severity，可被两类患者因素机制上调：
               (1) rule.patient_factors 命中 → 上调一级
               (2) rule.escalation_map[factor] 命中 → 直接抬到该级（floor）
    置信度   = 规则强度(≤0.5) + 同级规则一致(≤0.2) + 证据支持(≤0.3)

引擎零域逻辑：所有领域内容（flags、rationale、citations）都在 rules.yaml，
由 Phase 3 按文献逐条落定。无规则命中 → LOW（TongYuan 惯例：no-signal = LOW）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .schemas import RISK_ORDER, EntityA, EntityB, RiskAssessment, RiskLevel, RiskSignal

SEVERITY_ORDER: dict[str, int] = {"unknown": 0, "low": 1, "medium": 2, "high": 3}
SEVERITY_STRENGTH: dict[str, float] = {"high": 0.5, "medium": 0.3, "low": 0.1}

# 监管标签类来源在置信度中计双倍（methodology_skeleton: FDA/regulatory counts double）
_DOUBLE_SOURCE_MARKERS = ("fda", "dailymed", "setid", "label", "nmpa", "ema", "guideline")


@dataclass
class Rule:
    """rules.yaml 中单条规则的运行时形态。"""

    id: str
    severity: str  # high | medium | low
    risk_type: str
    entity_a_flags: list[str] = field(default_factory=list)
    entity_b_flags: list[str] = field(default_factory=list)
    patient_factors: list[str] = field(default_factory=list)  # 命中即上调一级
    escalation_map: dict[str, str] = field(default_factory=dict)  # factor → floor severity
    rationale: str = ""
    recommendation: str = ""
    citations: list = field(default_factory=list)


def _severity_key(level: str) -> int:
    return SEVERITY_ORDER.get(str(level).lower(), 0)


def escalate(level: str) -> str:
    """严重度上调一级（high 封顶）。"""
    order = ["low", "medium", "high"]
    lvl = str(level).lower()
    return order[min(order.index(lvl) + 1, len(order) - 1)] if lvl in order else lvl


def load_rules(path: str | Path | None = None) -> list[Rule]:
    """从 rules.yaml 加载规则；路径缺省为 <project_root>/configs/rules.yaml。"""
    if path is None:
        path = Path(__file__).resolve().parents[2] / "configs" / "rules.yaml"
    path = Path(path)
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules: list[Rule] = []
    for item in raw.get("rules", []) or []:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        rules.append(
            Rule(
                id=str(item["id"]),
                severity=str(item.get("severity", "low")).lower(),
                risk_type=str(item.get("risk_type", "unclassified")),
                entity_a_flags=[str(f) for f in item.get("entity_a_flags", []) or []],
                entity_b_flags=[str(f) for f in item.get("entity_b_flags", []) or []],
                patient_factors=[str(f) for f in item.get("patient_factors", []) or []],
                escalation_map={
                    str(k): str(v).lower()
                    for k, v in (item.get("escalation_map", {}) or {}).items()
                },
                rationale=str(item.get("rationale", "")),
                recommendation=str(item.get("recommendation", "")),
                citations=list(item.get("citations", []) or []),
            )
        )
    return rules


def _hit_set(rule_flags: list[str], entity_flags: list[str]) -> list[str]:
    return sorted(set(rule_flags) & set(entity_flags))


def match_rules(
    rules: list[Rule],
    entity_a: EntityA,
    entity_b: EntityB,
    patient_factors: list[str] | None = None,
) -> list[RiskSignal]:
    """返回命中的 RiskSignal 列表（含患者因素升级后的最终严重度）。"""
    factors_set = {str(f).strip() for f in (patient_factors or []) if str(f).strip()}
    signals: list[RiskSignal] = []

    for rule in rules:
        hit_a = _hit_set(rule.entity_a_flags, entity_a.flags)
        hit_b = _hit_set(rule.entity_b_flags, entity_b.flags)
        if not hit_a or not hit_b:
            continue

        final = rule.severity
        matched_factors = sorted(factors_set & set(rule.patient_factors))
        if matched_factors:
            final = escalate(final)
        floor_hits = sorted(factors_set & set(rule.escalation_map.keys()))
        for f in floor_hits:
            floor_level = rule.escalation_map[f]
            if _severity_key(floor_level) > _severity_key(final):
                final = floor_level

        matched_terms = {
            "entity_a_flags": hit_a,
            "entity_b_flags": hit_b,
            "patient_factors": matched_factors + floor_hits,
        }
        if rule.citations:
            matched_terms["citations"] = [
                c if isinstance(c, str) else str(c.get("ref", "")) for c in rule.citations
            ]

        signals.append(
            RiskSignal(
                rule_id=rule.id,
                risk_level=RiskLevel(final),
                risk_type=rule.risk_type,
                rationale=rule.rationale,
                recommendation=rule.recommendation,
                matched_terms=matched_terms,
            )
        )
    return signals


def unique_evidence_sources(evidence_chunks: list) -> list[str]:
    """从证据块提取独立来源标识（pmid/doi/citation_hint/source_locator）。"""
    sources: list[str] = []
    for ev in evidence_chunks:
        for cand in (
            getattr(ev, "pmid", ""),
            getattr(ev, "doi", ""),
            getattr(ev, "citation_hint", ""),
            getattr(ev, "source_locator", ""),
        ):
            token = str(cand or "").strip()
            if token and token not in sources:
                sources.append(token)
    return sources


def evidence_confidence(evidence_chunks: list) -> float:
    """证据支持分：每独立来源 +0.10，监管标签类来源 +0.20，封顶 0.3。

    无规则信号时由 assess() 恒置 0（避免无信号对的置信度虚高，methodology_skeleton 原则）。
    """
    if not evidence_chunks:
        return 0.0
    score = 0.0
    for src in unique_evidence_sources(evidence_chunks):
        lowered = src.lower()
        weight = 0.20 if any(m in lowered for m in _DOUBLE_SOURCE_MARKERS) else 0.10
        score += weight
    return min(0.3, score)


def assess(
    signals: list[RiskSignal],
    evidence_chunks: list | None = None,
) -> RiskAssessment:
    """汇总 RiskSignal → RiskAssessment（最高严重度 + 置信度混合）。

    置信度组成（methodology_skeleton）：
      规则强度  ≤ 0.5  — high=0.5 / medium=0.3 / low=0.1，取信号中的最大值
      规则一致  ≤ 0.2  — ≥2 条信号落在同一（最高）级别 +0.2
      证据支持  ≤ 0.3  — 每独立可溯源来源 +0.10（监管类 +0.20）；无信号时为 0
    """
    evidence_chunks = evidence_chunks or []
    if not signals:
        return RiskAssessment(
            risk_level=RiskLevel.LOW,
            risk_types=[],
            signals=[],
            confidence=0.0,
            confidence_score=0.0,
        )

    top_level = max((s.risk_level for s in signals), key=lambda lv: RISK_ORDER[lv])
    strength = SEVERITY_STRENGTH.get(top_level.value, 0.1)
    n_same = sum(1 for s in signals if s.risk_level == top_level)
    agreement = 0.2 if n_same >= 2 else 0.0
    total = min(1.0, strength + agreement + evidence_confidence(evidence_chunks))

    risk_types: list[str] = []
    for s in sorted(signals, key=lambda x: -RISK_ORDER[x.risk_level]):
        if s.risk_type not in risk_types:
            risk_types.append(s.risk_type)

    return RiskAssessment(
        risk_level=top_level,
        risk_types=risk_types,
        signals=signals,
        confidence=round(total, 3),
        confidence_score=round(total, 3),
    )
