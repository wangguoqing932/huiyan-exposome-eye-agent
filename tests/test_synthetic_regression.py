"""M1/M2 锁定测试(2026-10-16):

- test_synthetic_regression: 合成效应注入回归的断言门(已知真值的评估面)。
- test_escalation_fixed: 患者因素升级修复的回归锁(AGENT_AUDIT 发现的 0 触发 bug)。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))


def test_synthetic_regression():
    from synthetic_regression import run
    s = run(n_per_pair=6000)
    # 检出功效:强效应(OR=2)应 ≥90% 复现;中等(1.4)应 ≥70%
    assert s["power_or2_replicated"] >= 0.90, s
    assert s["power_or1_4_replicated"] >= 0.70, s
    # 假阳性:零效应族被 BHY 后误标 replicated ≤10%,且不得反向
    assert s["fpr_or1_replicated"] <= 0.10, s
    assert (s["null_contradicted"] or 0) <= 0.10, s
    # 方向恢复:保护效应(0.6)在 risk_up 规则下应 ≥80% 记 contradicted
    assert s["protective_contradicted"] >= 0.80, s


def test_escalation_fixed():
    """AGENT_AUDIT:患者因素升级此前从未生效;修复后必须可触发且范围受限。"""
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import match_rules
    from huiyan_agent.safety_agent import SafetyAgent

    agent = SafetyAgent()
    rules = agent.rules

    def level(exposure, disease, factors):
        ra = resolve_entity_a(exposure)
        rb = resolve_entity_b(disease)
        sigs = match_rules(rules, ra, rb, factors)
        assert sigs, f"无规则命中: {exposure} x {disease}"
        order = {"low": 0, "medium": 1, "high": 2}
        return max((s.risk_level.value for s in sigs), key=lambda x: order[x])

    base = level("fasting_glucose", "cataract_any", [])
    with_factor = level("fasting_glucose", "cataract_any", ["diabetes"])
    assert base == "medium" and with_factor == "high", (base, with_factor)

    # 范围受限:map 不覆盖的对加因素不得升级(防误伤)
    b2 = level("fasting_glucose", "cataract_any", ["hypertension"])
    assert b2 == base, (base, b2)
