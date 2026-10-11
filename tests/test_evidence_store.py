"""Tests for evidence_store."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.evidence_store import EvidenceStore, load_evidence_chunks

def test_chunks_exist():
    chunks = load_evidence_chunks()
    assert len(chunks) > 0

def test_search():
    store = EvidenceStore()
    results = store.retrieve("smoking cataract", top_k=3)
    assert isinstance(results, list)
