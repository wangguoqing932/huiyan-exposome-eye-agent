"""R16 回归锁:结局变体规范化回退(variable_map.outcome_alias)。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def test_outcome_alias_mapping():
    from huiyan_agent.variable_map import load_variable_map, outcome_alias
    amap = outcome_alias(load_variable_map())
    assert amap.get("cataract_dx") == "cataract_any"
    assert amap.get("retinopathy_selfreport") == "retinopathy_any"
    assert "amd_any" not in amap  # 混合构念(早+晚期)不得映射


def test_match_rules_canonical_fires_via_alias():
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import load_rules, match_rules, match_rules_canonical
    rules = load_rules()
    ra = resolve_entity_a("hba1c")
    direct = match_rules(rules, ra, resolve_entity_b("cataract_any"))
    assert direct, "canonical 行本身应命中"
    sigs, aliased = match_rules_canonical(
        rules, ra, None, resolve_entity_b("cataract_any"))
    assert sigs and aliased, "无原实体+有 canonical → 应经别名命中且 aliased=True"
    sigs_none, aliased_none = match_rules_canonical(rules, ra, None, None)
    assert not sigs_none and not aliased_none
