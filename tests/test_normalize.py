"""Tests for huiyan_agent.normalize."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry, resolve_entity_a, resolve_entity_b

def test_a_count():
    assert len(load_entity_a_registry()) >= 40

def test_b_count():
    assert len(load_entity_b_registry()) == 15

def test_resolve_a():
    a = resolve_entity_a("current_smoking")
    assert a is not None

def test_resolve_b():
    b = resolve_entity_b("cataract_any")
    assert b is not None
