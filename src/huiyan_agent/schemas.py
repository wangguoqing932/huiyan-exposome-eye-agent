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
