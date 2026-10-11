"""report — 慧眼结构化筛查报告生成（markdown，FDI 域原生）。

报告对象为 SafetyReport.report_text；所有分级标签、免责声明均为暴露×眼病
相互作用域原生文案（与 app/streamlit_app.py 的 RISK_COLORS 分级一致）。
"""
from __future__ import annotations

from .schemas import EvidenceChunk, RiskAssessment, RiskLevel

# 分级 → 中文标签（FDI 语境：规避 / 限量错时 / 未见显著 / 证据不足）
LEVEL_LABELS: dict[RiskLevel, str] = {
    RiskLevel.HIGH: "高风险 — 建议规避该组合并咨询眼科/临床药师",
    RiskLevel.MEDIUM: "中等风险 — 建议限量、错时服用并加强监测",
    RiskLevel.LOW: "低风险 — 目前证据未见显著相互作用",
    RiskLevel.UNKNOWN: "证据不足 — 建议关注后续研究并随访",
}

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
    level_label = LEVEL_LABELS[assessment.risk_level]
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
        lines.append("未触发任何规则：当前规则库在该暴露×眼病组合上无可识别的相互作用机制。")
    else:
        order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
        for sig in sorted(assessment.signals, key=lambda s: order.get(s.risk_level.value, 9)):
            lines.append(f"### [{sig.risk_level.value.upper()}] `{sig.rule_id}` · {sig.risk_type}")
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
