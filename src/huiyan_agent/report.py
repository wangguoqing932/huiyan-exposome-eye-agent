"""report — 慧眼结构化筛查报告生成（markdown，暴露×眼病域）。

报告对象为 SafetyReport.report_text；所有分级标签、免责声明均为暴露×眼病
相互作用域文案（与 app/streamlit_app.py 的 RISK_COLORS 分级一致）。
"""
from __future__ import annotations

from .schemas import EvidenceChunk, RiskAssessment, RiskLevel

# 分级 → 中文标签（暴露×眼病语境）
# 审核 109：原文案继承自食物-药物相互作用（FDI）骨架，对 HbA1c / BMI / PM2.5 / UV
# 等暴露无意义（「限量、错时服用」「咨询临床药师」），已替换为域内可读文案。
LEVEL_LABELS: dict[RiskLevel, str] = {
    RiskLevel.HIGH: "高风险 — 建议优先干预该暴露并转诊眼科评估",
    RiskLevel.MEDIUM: "中等风险 — 建议加强监测，并在眼科随访时一并评估",
    RiskLevel.LOW: "低风险 — 已评估该组合，现有规则未提示显著风险",
    RiskLevel.UNKNOWN: "未评估 — 本系统未覆盖该组合，不能据此判断无风险",
}

# 全部命中信号均为保护性关联时的标签（审核 98/128）
_PROTECTIVE_LABEL = "保护性关联 — 现有证据提示该暴露与更低风险相关（非风险信号）"

_DISCLAIMER = (
    "本报告为说明书/指南/文献证据的可解释筛查输出，仅供临床决策支持，"
    "不构成诊疗建议；最终判断由临床医生做出。"
)


def _fmt_terms(matched: dict[str, list[str]]) -> str:
    parts = []
    for key in ("entity_a_flags", "entity_b_flags", "patient_factors", "citations"):
        vals = matched.get(key) or []
        if vals:
            parts.append(f"{key}: {', '.join(vals)}")
    return "；".join(parts) if parts else "-"


def build_report(
    entity_a_name: str,
    entity_b_name: str,
    assessment: RiskAssessment,
    evidence: list[EvidenceChunk],
    patient_factors: list[str] | None = None,
    case_id: str = "-",
    arbiter_note: str | None = None,
    registered: tuple[bool, bool] = (True, True),
) -> str:
    """组装 markdown 筛查报告。registered=(A是否在册, B是否在册)。"""
    all_protective = bool(assessment.signals) and all(
        getattr(s, "protective", False) for s in assessment.signals
    )
    level_label = _PROTECTIVE_LABEL if all_protective else LEVEL_LABELS[assessment.risk_level]
    factors = "、".join(patient_factors) if patient_factors else "无"

    lines: list[str] = []
    lines.append(f"# 慧眼筛查报告 — {entity_a_name} × {entity_b_name}")
    lines.append("")
    lines.append(f"- **case_id**: `{case_id}`")
    lines.append(f"- **患者/人群因素**: {factors}")
    if not all(registered):
        off = [n for n, ok in zip(("暴露", "眼病"), registered) if not ok]
        lines.append(
            f"- ⚠️ **范围外条目**: {'、'.join(off)}不在慧眼注册表中——"
            "本报告仅基于通用机制库给出保守参考，**不能视为「无相互作用」的结论**，请以说明书与医生意见为准。"
        )
    lines.append(
        f"- **综合风险**: **{assessment.risk_level.value.upper()}**（{level_label}）"
        f" · 置信度 **{assessment.confidence_score:.0%}**"
    )
    if arbiter_note:
        lines.append(f"- **LLM 仲裁**: {arbiter_note}")
    lines.append("")

    # ── 触发规则 ──
    lines.append(f"## 触发规则（{len(assessment.signals)} 条）")
    if not assessment.signals:
        lines.append(
            "**本系统未覆盖该组合**：规则库中没有针对该暴露×眼病组合的规则，"
            "因此**没有做任何评估**——这不等于「无相互作用」，也不等于低风险。"
        )
    else:
        order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
        for sig in sorted(assessment.signals, key=lambda s: order.get(s.risk_level.value, 9)):
            tag = "保护性" if getattr(sig, "protective", False) else sig.risk_level.value.upper()
            lines.append(f"### [{tag}] `{sig.rule_id}` · {sig.risk_type}")
            lines.append(f"- **依据**: {sig.rationale}")
            if sig.recommendation:
                lines.append(f"- **建议**: {sig.recommendation}")
            lines.append(f"- **匹配**: {_fmt_terms(sig.matched_terms)}")
            lines.append("")

    # ── 证据链 ──
    lines.append(f"## 证据链（{len(evidence)} 条）")
    if not evidence:
        lines.append("未检索到与该组合直接相关的证据片段。")
    else:
        for i, ev in enumerate(evidence, 1):
            loc = f"，{ev.source_locator}" if ev.source_locator else ""
            cite = ev.citation_hint or ev.pmid or ev.doi
            cite_s = f"（引文: {cite}）" if cite else ""
            lines.append(f"### [EV{i}] Level {ev.evidence_level or '?'} — {ev.title}")
            lines.append(f"- 来源: {ev.source}{loc}{cite_s}")
            text = ev.text if len(ev.text) <= 600 else ev.text[:600] + "…"
            lines.append(f"- 摘录: {text}")
            lines.append("")

    # ── 免责声明 ──
    lines.append("---")
    lines.append(f"> {_DISCLAIMER}")
    return "\n".join(lines)
