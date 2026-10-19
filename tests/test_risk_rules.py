"""Tests for huiyan_agent.risk_rules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules, assess, escalate
from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b

def test_rules_load():
    rules = load_rules()
    assert len(rules) == 21

def test_severity_matches_evidence_level():
    """审核 F6/F25：C→low 不变量此前从未被断言。

    原测试以 `hasattr(r, "_data")` 为门槛，而 Rule 没有 `_data` 属性，循环体永不执行。
    """
    from huiyan_agent.risk_rules import _EVIDENCE_TO_SEVERITY
    rules = load_rules()
    assert rules, "rules.yaml 未加载到规则"
    for r in rules:
        assert r.direction in ("risk_up", "risk_down"), r.id
        assert r.severity == _EVIDENCE_TO_SEVERITY[r.evidence_level], (
            f"{r.id}: severity={r.severity} 与 evidence_level={r.evidence_level} 不符"
        )

def test_mechanism_coverage():
    """7 机制：既要求全覆盖，也要求**不越界**（原测试只数个数）。"""
    from huiyan_agent.risk_rules import canonical_mechanisms
    mech = set(canonical_mechanisms())
    used = set(r.risk_type for r in load_rules())
    assert used == mech, f"未覆盖: {sorted(mech - used)}；越界: {sorted(used - mech)}"

def test_smoking_amd():
    """smoking -> late AMD resolves to the rule layer's high.

    This assertion has been changed twice, and the history is the point.

    On 2026-10-16 an audit read the per-chunk `linked_rules` field, found that
    r11's linked chunks were 1 x B and 3 x C, and concluded the rule's declared
    grade A was unsupported. The assertion was lowered to `medium` accordingly.

    That audit was wrong. **All 159 AAO PPP chunks in the corpus have
    `linked_rules` empty** -- 0 of 159 -- while 34 of them are grade A. The
    corpus does contain the guideline support, and the agent retrieves it: for
    smoking x late AMD it surfaces `[A] AAO PPP AMD - Section 9`, whose text
    reads "Risk factors for the development of advanced AMD include smoking ...
    Cigarette smoking has been identified as the primary modifiable risk factor
    in numerous studies on advanced AMD."

    So "no link" was read as "no evidence", an empty field was taken as a
    substantive claim, and a correct grade was lowered because of it. r11 is
    restored to A/high and the assertion follows it.
    """
    a = resolve_entity_a("current_smoking")
    b = resolve_entity_b("amd_late")
    assert a and b
    sigs = match_rules(load_rules(), a, b)
    assert len(sigs) > 0
    assert sigs[0].risk_level.value == "high"

def test_type1_gap():
    a = resolve_entity_a("blood_mercury")
    b = resolve_entity_b("cataract_any")
    if a and b:
        sigs = match_rules(load_rules(), a, b)
        assert len(sigs) == 0

def test_escalate():
    assert escalate("low") == "medium"
    assert escalate("high") == "high"
