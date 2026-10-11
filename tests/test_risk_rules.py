"""Tests for huiyan_agent.risk_rules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules, assess, escalate
from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b

def test_rules_load():
    rules = load_rules()
    assert len(rules) == 21

def test_severity_c_low():
    rules = load_rules()
    for r in rules:
        if hasattr(r, "_data") and r._data.get("evidence_level") == "C":
            assert r.severity == "low", f"{r.id}: C should be low"

def test_mechanism_coverage():
    rules = load_rules()
    mech = set(r.risk_type for r in rules)
    assert len(mech) >= 7

def test_smoking_amd():
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
