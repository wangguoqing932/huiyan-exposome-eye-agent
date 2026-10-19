from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):   # Py3.10 兼容（StrEnum 为 Python 3.11+）
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.UNKNOWN: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}


class EntityA(BaseModel):
    """Entity A registry record (e.g., Food / Herb / Gene / Microbiota).

    Rename `EntityA` to the domain-specific name (Food, Herb, Variant, Microbe, Symptom, Supplement).
    Extend fields as needed but keep `flags` (list of mechanism tags) — the rule engine depends on it.
    """
    entity_a_id: str
    primary_name: str = ""
    aliases: list[str] = Field(default_factory=list)
    category: str = ""
    active_mechanisms: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    evidence_sources: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class EntityB(BaseModel):
    """Entity B registry record (eye disease item)."""
    entity_b_id: str
    generic_name: str
    aliases: list[str] = Field(default_factory=list)
    category: str = ""
    flags: list[str] = Field(default_factory=list)
    pathology: list[str] = Field(default_factory=list)
    grading_source: list[str] = Field(default_factory=list)
    judged_in: bool = False
    label_source: str = ""


class PatientFactors(BaseModel):
    factors: list[str] = Field(default_factory=list)


class InteractionCase(BaseModel):
    case_id: str
    entity_a: str
    entity_b: str
    patient_factors: list[str] = Field(default_factory=list)
    gold_risk_level: RiskLevel | None = None
    risk_type: list[str] = Field(default_factory=list)
    notes: str = ""


class EvidenceChunk(BaseModel):
    evidence_id: str
    title: str
    source: str
    source_type: str
    evidence_level: str = ""
    evidence_relation: str = ""
    source_locator: str = ""
    citation_hint: str = ""
    pmid: str = ""
    doi: str = ""
    verification_status: str = ""
    source_quality_rank: str = ""
    entities_a: list[str] = Field(default_factory=list)
    entities_b: list[str] = Field(default_factory=list)
    risk_types: list[str] = Field(default_factory=list)
    text: str
    url: str = ""
    weight: int = 1


class RiskSignal(BaseModel):
    rule_id: str
    risk_level: RiskLevel
    risk_type: str
    rationale: str
    recommendation: str
    matched_terms: dict[str, list[str]] = Field(default_factory=dict)
    protective: bool = False  # True = 该规则声明 direction: risk_down（保护性关联），不参与风险等级


class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    risk_types: list[str] = Field(default_factory=list)
    signals: list[RiskSignal] = Field(default_factory=list)
    confidence: float = 0.0        # 数值置信度 [0,1]（streamlit 契约: float(confidence)）
    confidence_score: float = 0.0  # 同 confidence（语义别名，供评估脚本使用）
    # 仲裁层自陈的置信度；None 表示未使用仲裁层。
    #
    # 需要独立字段的原因：`confidence` 完全由规则层算出（risk_rules.py 的
    # strength + agreement + evidence_confidence），**仲裁的结果不进入那个式子**，
    # 所以它结构上无法反映仲裁的犹豫——实测一个在不同运行间 medium/high 摇摆的
    # 配对与两个始终稳定的配对，三者 `confidence` 同为 0.60。
    # 单独存放仲裁的自陈置信度，既不改 `confidence` 的既有语义
    # （streamlit 的 float(confidence) 契约不变），又让"仲裁有多确定"可读可测。
    arbiter_confidence: float | None = None
    arbiter_rationale: str | None = None
    # 仲裁建议的等级。在 arbiter_authority="advisory" 下，risk_level 保持规则层的值，
    # 这里记录仲裁原本想改成什么——既保留它的判断供人看，又不让它改最终输出。
    # 见 safety_agent.SafetyAgentConfig.arbiter_authority 的说明。
    arbiter_suggested_level: str | None = None


class SafetyReport(BaseModel):
    case_id: str
    entity_a: str
    entity_b: str
    patient_factors: list[str] = Field(default_factory=list)
    risk_assessment: RiskAssessment
    evidence: list[EvidenceChunk] = Field(default_factory=list)
    report_text: str
    context_char_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
