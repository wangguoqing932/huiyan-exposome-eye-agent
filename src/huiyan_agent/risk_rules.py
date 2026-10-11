"""risk_rules — 慧眼规则引擎：flags 驱动的暴露×眼病相互作用规则匹配。

机制（与 PLAN.md §4 / configs/rules.yaml 严格对应）::

    规则命中 = entity_a_flags 有交集 **且** entity_b_flags 有交集
    严重度   = 规则基础 severity，可被两类患者因素机制上调：
               (1) rule.patient_factors 命中 → 上调一级
               (2) rule.escalation_map[factor] 命中 → 直接抬到该级（floor）
    置信度   = 规则强度(≤0.5) + 同级规则一致(≤0.2) + 证据支持(≤0.3)

引擎零域逻辑：所有领域内容（flags、rationale、citations）都在 rules.yaml，
由 Phase 3 按文献逐条落定。

无规则命中 → UNKNOWN（弃权）。**不得报为 LOW** —— 「未评估」不等于「无相互作用」。
（审核 97：原实现沿用 TongYuan 的 no-signal = LOW 惯例，使 561/615 个未覆盖组合
被渲染为「低风险 — 目前证据未见显著相互作用」，属肯定性的虚假安心。）
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

# 证据级 → 严重度的唯一纪律（rule_rationale.md:4）：A→high / B→medium / C→low
_EVIDENCE_TO_SEVERITY: dict[str, str] = {"A": "high", "B": "medium", "C": "low"}

_MECHANISMS_FALLBACK: tuple[str, ...] = (
    "oxidative_stress",
    "glycation_metabolic",
    "inflammation_immune",
    "vascular_perfusion",
    "endocrine_hormonal",
    "heavy_metal_toxicity",
    "photochemical_uv",
)


def canonical_mechanisms() -> tuple[str, ...]:
    """7 机制清单的唯一真相源。

    优先读 `.planner.config.json` 的 `interaction_mechanisms`；缺失时回退到内置常量。
    （审核 F6：此前 rules.yaml:5 指向 config 的该键，但引擎不读它，
    导致引擎与验证脚本各用一条真相源，漂移时无人报错。）
    """
    import json

    cfg = Path(__file__).resolve().parents[2] / ".planner.config.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        mech = data.get("interaction_mechanisms")
        if isinstance(mech, list) and mech:
            return tuple(str(m) for m in mech)
    except Exception:
        pass
    return _MECHANISMS_FALLBACK


@dataclass
class Rule:
    """rules.yaml 中单条规则的运行时形态。"""

    id: str
    severity: str  # high | medium | low
    risk_type: str
    evidence_level: str = "C"       # A | B | C（加载期校验与 severity 一致）
    direction: str = "risk_up"      # risk_up | risk_down（risk_down = 保护性关联）
    negative_control: bool = False  # 已知阴性对照：不得进 headline 指标
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
    mech = set(canonical_mechanisms())
    rules: list[Rule] = []
    for item in raw.get("rules", []) or []:
        if not isinstance(item, dict) or not item.get("id"):
            continue

        # ── 加载期校验（审核 F6/F13/F25：此前全部只在 match 期或根本不校验）──
        rid = str(item["id"])
        severity = str(item.get("severity", "")).strip().lower()
        if severity not in ("high", "medium", "low"):
            raise ValueError(f"{rid}: 非法 severity={severity!r}（应为 high|medium|low）")
        level = str(item.get("evidence_level", "")).strip().upper()
        if level not in _EVIDENCE_TO_SEVERITY:
            raise ValueError(f"{rid}: 非法 evidence_level={level!r}（应为 A|B|C）")
        if _EVIDENCE_TO_SEVERITY[level] != severity:
            raise ValueError(
                f"{rid}: severity={severity!r} 与 evidence_level={level!r} 不符"
                "（纪律：A→high / B→medium / C→low）"
            )
        rtype = str(item.get("risk_type", "")).strip()
        if rtype not in mech:
            raise ValueError(f"{rid}: risk_type={rtype!r} 不在 7 机制清单内 {sorted(mech)}")
        direction = str(item.get("direction", "risk_up")).strip()
        if direction not in ("risk_up", "risk_down"):
            raise ValueError(f"{rid}: 非法 direction={direction!r}（应为 risk_up|risk_down）")

        rules.append(
            Rule(
                id=rid,
                severity=severity,
                risk_type=rtype,
                evidence_level=level,
                direction=direction,
                negative_control=bool(item.get("negative_control", False)),
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

        protective = rule.direction == "risk_down"
        if protective:
            # 审核 98/128：保护性规则（如 r09 地中海饮食×晚期 AMD）此前被当作普通风险信号，
            # 在报告层渲染成「中等风险 — 建议限量、错时服用」，方向完全颠倒。
            matched_terms.setdefault("direction", []).append("risk_down（保护性关联）")
        if rule.negative_control:
            matched_terms.setdefault("negative_control", []).append("true（已知阴性对照，不进 headline 指标）")

        signals.append(
            RiskSignal(
                rule_id=rule.id,
                risk_level=RiskLevel(final),
                risk_type=rule.risk_type,
                rationale=rule.rationale,
                recommendation=rule.recommendation,
                matched_terms=matched_terms,
                protective=protective,
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

    # 保护性信号不参与风险等级（审核 98/128）
    risk_signals = [s for s in signals if not getattr(s, "protective", False)]

    if not risk_signals:
        # 无规则命中，或命中的全是保护性关联 → 弃权。
        # 审核 97：此前返回 RiskLevel.LOW，使未覆盖组合被渲染为
        # 「低风险 — 目前证据未见显著相互作用」（肯定性的虚假安心）。
        return RiskAssessment(
            risk_level=RiskLevel.UNKNOWN,
            risk_types=sorted({s.risk_type for s in signals}),
            signals=signals,
            confidence=0.0,
            confidence_score=0.0,
        )

    signals = risk_signals
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
