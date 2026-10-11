"""End-to-end integration: A4 import chain test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
def test_streamlit_imports():
    from huiyan_agent.evidence_store import EvidenceStore
    from huiyan_agent.lightrag_adapter import LightRAGAdapter
    from huiyan_agent.llm_client import DualLLMClient, LLMClient, LLMConfig
    from huiyan_agent.normalize import (load_entity_a_registry, load_entity_b_registry,
        resolve_entity_a, resolve_entity_b, clear_cache)
    from huiyan_agent.safety_agent import SafetyAgent, SafetyAgentConfig

def test_full_pipeline():
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import load_rules, match_rules, assess
    rules = load_rules()
    a = resolve_entity_a("current_smoking")
    b = resolve_entity_b("amd_late")
    sigs = match_rules(rules, a, b)
    result = assess(sigs)
    assert result.risk_level.value in ("low","medium","high")

def test_abstention():
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import load_rules, match_rules, assess
    rules = load_rules()
    a = resolve_entity_a("blood_mercury")
    b = resolve_entity_b("cataract_any")
    if a and b:
        sigs = match_rules(rules, a, b)
        r = assess(sigs)
        assert r.risk_level.value == "low"
        assert r.confidence == 0.0
