"""safety_agent — 慧眼三层筛查编排器（规则引擎 → 风险制导检索 → LLM 仲裁）。

流水线（PLAN.md §2）::

    用户输入 (entity_a + entity_b + 患者因素)
      → normalize（名称 → 注册表规范记录）
      → 规则引擎（risk_rules.match_rules，YAML 驱动）
      → 风险制导检索（EvidenceStore 等级加权 + LightRAG 可选增强）
      → 证据压缩（top-k + 字符上限）
      → LLM 仲裁（可选；tiered 模式仅在有规则信号时调用）
      → 结构化报告（report.build_report）+ 置信度混合（rules + 证据）

仲裁器可上调/下调一级（high 不下调至 low 以下，unknown 表示证据不足）；
仲裁失败静默降级为纯规则输出，并在 metadata 标注。
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from .evidence_store import EvidenceStore
from .normalize import resolve_entity_a, resolve_entity_b
from .report import build_report
from .risk_rules import RISK_ORDER, SEVERITY_ORDER, assess, load_rules, match_rules
from .schemas import (
    EntityA,
    EntityB,
    EvidenceChunk,
    RiskAssessment,
    RiskLevel,
    SafetyReport,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 仲裁器输出 JSON 解析容错（允许模型包裹 ```json 等）
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class SafetyAgentConfig:
    """编排配置（app/streamlit_app.py 契约）。"""

    use_lightrag: bool = True
    use_llm_arbiter: bool = True
    tiered_arbiter: bool = True   # True: 仅当存在规则信号时调用仲裁器（省调用、降噪）
    top_k_evidence: int = 5
    context_char_limit: int = 6000
    rules_path: str | None = None  # 缺省 <project_root>/configs/rules.yaml


# FDI 域原生仲裁提示词（全新撰写，仅依赖传入的规则信号与证据，禁止编造）
# v2.2（2026-10-09）：增设升级硬底线——患者因素支持的规则 high 不得降级（安全优先，
# 仲裁器只在证据明确矛盾时复核，不允许乐观偏置；代码层同步强制，见 _run_arbiter）
_ARBITER_SYSTEM = (
    "你是青光眼及眼科治疗背景下的暴露组×眼病（FDI）仲裁器。"
    "输入包括：暴露与眼病条目、规则引擎已命中的信号、以及检索到的证据片段。"
    "你的职责：在规则信号与证据的基础上做最终分级复核。"
    "规则：1) 只能基于给出的证据与药理常识推理，不得虚构文献或机制；"
    "2) 输出必须是单个 JSON 对象，字段："
    '{"risk_level": "high|medium|low|unknown", '
    '"rationale": "一句话机制依据", "recommendation": "一句可执行建议"}；'
    "3) risk_level 只能相对规则最高级上调或下调一级，或在该证据互相矛盾/不足时给 unknown；"
    "4) rationale 中引用证据时使用 [EVn] 编号；"
    "5) 升级硬底线：当【规则引擎当前分级】为 high 且【患者/人群因素】非空时，"
    "不得下调分级——除非证据与规则机制明确矛盾，且 rationale 必须引用具体 [EVn] 反证；"
    "本安全优先系统宁可过警，不可漏警。"
)

# 筛查系统版本（Methods 披露用；rules.yaml 冻结不变，仅仲裁层行为修订）
SYSTEM_VERSION = "mingmu-screening v2.2 (arbiter escalation floor)"


def _arbiter_user_prompt(
    entity_a: EntityA,
    entity_b: EntityB,
    assessment: RiskAssessment,
    context: str,
    patient_factors: list[str],
) -> str:
    sig_lines = [
        f"- [{s.risk_level.value}] {s.rule_id} ({s.risk_type}): {s.rationale}"
        for s in assessment.signals
    ] or ["- （无规则信号）"]
    return (
        f"【暴露】{entity_a.primary_name} (id={entity_a.entity_a_id}, flags={entity_a.flags})\n"
        f"【眼病】{entity_b.generic_name} (id={entity_b.entity_b_id}, flags={entity_b.flags})\n"
        f"【患者/人群因素】{patient_factors or '无'}\n"
        f"【规则引擎信号】\n" + "\n".join(sig_lines) + "\n"
        f"【规则引擎当前分级】{assessment.risk_level.value} (confidence={assessment.confidence_score:.2f})\n"
        f"【证据片段】\n{context or '（无检索证据）'}\n\n"
        "请输出最终分级 JSON。"
    )


class SafetyAgent:
    """三层混合筛查 agent。"""

    def __init__(
        self,
        evidence_store: EvidenceStore | None = None,
        lightrag=None,  # LightRAGAdapter | None
        llm_client=None,  # LLMClient | DualLLMClient
        config: SafetyAgentConfig | None = None,
    ) -> None:
        self.store = evidence_store or EvidenceStore()
        self.lightrag = lightrag
        self.config = config or SafetyAgentConfig()
        self.llm = llm_client
        self.rules = load_rules(self.config.rules_path)

    # ------------------------------------------------------------------ #
    def _retrieve(
        self,
        query: str,
        entity_a: EntityA,
        entity_b: EntityB,
    ) -> list[EvidenceChunk]:
        """风险制导检索：EvidenceStore 等级加权 + LightRAG 可选增强，按 evidence_id 去重。"""
        chunks: list[EvidenceChunk] = list(
            self.store.retrieve(
                query,
                top_k=self.config.top_k_evidence,
                entity_a_id=entity_a.entity_a_id,
                entity_b_id=entity_b.entity_b_id,
            )
        )
        if self.config.use_lightrag and self.lightrag is not None and getattr(self.lightrag, "available", True):
            try:
                rag_text = self.lightrag.query(query, mode="hybrid") or ""
                seen_keys = {
                    (ev.evidence_id, ev.text[:80]) for ev in chunks
                }
                for i, block in enumerate([b.strip() for b in rag_text.split("\n\n") if b.strip()]):
                    key = (f"lightrag_{i}", block[:80])
                    if key in seen_keys or not block:
                        continue
                    chunks.append(
                        EvidenceChunk(
                            evidence_id=f"lightrag_{i}",
                            title=block.split("\n")[0][:80],
                            source="LightRAG 图检索",
                            source_type="knowledge_graph",
                            evidence_level="E",  # 图检索输出按机制推断级处理，不虚标高等级
                            text=block,
                        )
                    )
                    seen_keys.add(key)
            except Exception:
                pass  # LightRAG 失败不阻塞流水线（EvidenceStore 结果已足够出报告）
        return chunks

    def _run_arbiter(
        self,
        entity_a: EntityA,
        entity_b: EntityB,
        assessment: RiskAssessment,
        context: str,
        patient_factors: list[str],
        escalation_backed_high: bool = False,
    ) -> tuple[RiskAssessment, str | None]:
        """LLM 仲裁：返回（可能调整后的 assessment, 仲裁说明）。失败时原样返回。

        v2.2 升级硬底线：escalation_backed_high=True（规则 high 由患者因素升级支持）时，
        仲裁降级建议一律拦截——提示词约束模型，代码层强制兜底。
        """
        if self.llm is None or not self.config.use_llm_arbiter:
            return assessment, None
        if self.config.tiered_arbiter and not assessment.signals:
            return assessment, None  # 分层仲裁：无信号不烧调用

        try:
            complete = getattr(self.llm, "complete_arbiter", None) or self.llm.complete
            prompt = _arbiter_user_prompt(entity_a, entity_b, assessment, context, patient_factors)
            resp = complete(prompt, system=_ARBITER_SYSTEM)
            if resp.degraded:
                return assessment, None
            m = _JSON_RE.search(resp.text)
            if not m:
                return assessment, None
            verdict = json.loads(m.group(0))
            new_level = str(verdict.get("risk_level", "")).lower()
            if new_level not in ("high", "medium", "low", "unknown"):
                return assessment, None

            old_key = SEVERITY_ORDER[assessment.risk_level.value]
            new_key = SEVERITY_ORDER[new_level]
            # v2.2 升级硬底线：患者因素支持的 high，任何降级建议一律拦截（含 unknown）
            if escalation_backed_high and new_key < old_key:
                return assessment, (
                    f"[arbiter_floor] 仲裁建议降级至 {new_level} 被升级硬底线拦截"
                    f"（患者因素支持的 {assessment.risk_level.value} 不可降，系统 v2.2）；"
                    f"仲裁理由存档：{verdict.get('rationale', '').strip()}"
                )
            # 只允许 ±1 级（unknown 视为 from-low 的特殊下调）且 high 不可降为 low
            allowed = (
                new_key == old_key
                or abs(new_key - old_key) == 1
                or (new_level == "unknown" and old_key <= SEVERITY_ORDER["low"])
            )
            if not allowed:
                new_level = assessment.risk_level.value
                note = f"仲裁建议越级（已忽略，维持 {new_level}）"
                return assessment, note

            note = f"{verdict.get('rationale', '').strip()}"
            final_level = RiskLevel(new_level)
            if final_level == assessment.risk_level:
                return assessment, note or None

            # 信号保持规则引擎原貌；总级由仲裁复核调整（报告里两者都有，可解释）
            new_assessment = assessment.model_copy(update={"risk_level": final_level})
            return new_assessment, note or None
        except Exception as e:
            return assessment, f"仲裁失败（降级为纯规则输出）：{type(e).__name__}"

    # ------------------------------------------------------------------ #
    def evaluate(
        self,
        entity_a_name: str,
        entity_b_name: str,
        patient_factors: list[str] | None = None,
        case_id: str = "case",
    ) -> SafetyReport:
        """主入口：暴露名 × 眼病名（+患者因素）→ SafetyReport。"""
        t0 = time.time()
        factors = [str(f).strip() for f in (patient_factors or []) if str(f).strip()]

        rec_a = resolve_entity_a(entity_a_name)
        rec_b = resolve_entity_b(entity_b_name)
        # 未注册条目按空 flags 处理（引擎自然 no-op），metadata 如实标注
        entity_a = rec_a or EntityA(entity_a_id=entity_a_name.strip().lower().replace(" ", "_") or "unknown_a",
                                    primary_name=entity_a_name)
        entity_b = rec_b or EntityB(entity_b_id=entity_b_name.strip().lower().replace(" ", "_") or "unknown_b",
                                    generic_name=entity_b_name)

        # ① 规则引擎
        signals = match_rules(self.rules, entity_a, entity_b, factors)
        base_level = (
            max((s.risk_level for s in signals), key=lambda lv: RISK_ORDER[lv]).value
            if signals else "low"
        )
        # v2.2 升级硬底线判定：规则 high 是否由患者因素升级支持
        # （对比无因素规则输出：升级贡献了级别 → 该 high 受因素证据支持，仲裁不可降）
        escalation_backed_high = False
        if factors and base_level == "high":
            sig_nf = match_rules(self.rules, entity_a, entity_b, [])
            base_nf = (
                max((s.risk_level for s in sig_nf), key=lambda lv: RISK_ORDER[lv]).value
                if sig_nf else "low"
            )
            escalation_backed_high = RISK_ORDER[base_nf] < RISK_ORDER["high"]

        # ② 风险制导检索 + 证据压缩
        query = " ".join(
            [entity_a.primary_name, entity_b.generic_name,
             entity_a.category, entity_b.category, base_level, "interaction"]
        )
        chunks = self._retrieve(query, entity_a, entity_b)
        top_chunks = chunks[: self.config.top_k_evidence]
        context = self.store.build_context(top_chunks, char_limit=self.config.context_char_limit)

        # ③ 置信度（规则 + 证据）→ 仲裁复核
        assessment = assess(signals, top_chunks)
        assessment, arbiter_note = self._run_arbiter(
            entity_a, entity_b, assessment, context, factors,
            escalation_backed_high=escalation_backed_high,
        )

        # ③.5 范围外语义（F5 审计）：任一实体未注册时顶层级别强制 UNKNOWN——
        # "评估范围外"必须长得像"不知道"，不能以 LOW 呈现（LOW = 已评估无显著）。
        level_before_scope = assessment.risk_level.value
        if not (rec_a is not None and rec_b is not None):
            assessment = assessment.model_copy(update={"risk_level": RiskLevel.UNKNOWN})

        # ④ 报告
        llm_label = getattr(self.llm, "label", "none") if self.llm is not None else "none"
        report_text = build_report(
            entity_a_name=entity_a.primary_name,
            entity_b_name=entity_b.generic_name,
            assessment=assessment,
            evidence=top_chunks,
            patient_factors=factors,
            case_id=case_id,
            arbiter_note=arbiter_note,
            registered=(rec_a is not None, rec_b is not None),
        )

        return SafetyReport(
            case_id=case_id,
            entity_a=entity_a.primary_name,
            entity_b=entity_b.generic_name,
            patient_factors=factors,
            risk_assessment=assessment,
            evidence=top_chunks,
            report_text=report_text,
            context_char_count=len(context),
            metadata={
                "entity_a_id": entity_a.entity_a_id,
                "entity_b_id": entity_b.entity_b_id,
                "entity_a_registered": rec_a is not None,
                "entity_b_registered": rec_b is not None,
                "llm_role": "arbiter" if arbiter_note and "失败" not in (arbiter_note or "") else (
                    "none" if self.llm is None or not self.config.use_llm_arbiter else "skipped_tiered"
                ),
                "llm_label": llm_label,
                "n_signals": len(assessment.signals),
                "n_evidence": len(top_chunks),
                "level_before_arbiter": base_level,
                "escalation_backed_high": escalation_backed_high,
                "arbiter_floor_triggered": bool(arbiter_note and "[arbiter_floor]" in arbiter_note),
                "system_version": SYSTEM_VERSION,
                "out_of_scope": not (rec_a is not None and rec_b is not None),
                "level_before_out_of_scope": level_before_scope,
                "elapsed_sec": round(time.time() - t0, 3),
            },
        )
