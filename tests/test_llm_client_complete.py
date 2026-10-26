"""R15 回归锁:complete() 必须永远返回 ChatResponse,不得静默 None。

背景:R13-D 抽函数时漏了 _nc=1 的委托分支,complete() 掉尾返回 None,
直到 2026-10-20 智谱接入时才暴露。此测试以 monkeypatch 模拟传输层锁定契约。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def test_complete_returns_response(monkeypatch):
    from huiyan_agent.llm_client import LLMClient
    c = LLMClient(provider="stub", temperature=0.0)
    monkeypatch.setattr(c, "degraded", False, raising=False)
    monkeypatch.setattr(c, "_chat", lambda msgs: "ok-answer")
    r = c.complete("q")
    assert r is not None and r.text == "ok-answer"


def test_complete_consistent_majority(monkeypatch, tmp_path):
    import os
    from huiyan_agent.llm_client import LLMClient
    c = LLMClient(provider="stub", temperature=0.0)
    monkeypatch.setattr(c, "degraded", False, raising=False)
    calls = iter(["A", "B", "B"])
    monkeypatch.setattr(c, "_chat", lambda msgs: next(calls))
    # 缓存指到临时文件,避免污染真实缓存
    import huiyan_agent.llm_client as m
    monkeypatch.setenv("HUIYAN_ARBITER_CONSISTENCY", "3")
    import json
    cache = tmp_path / "cache.json"
    cache.write_text("{}", encoding="utf-8")
    real_open = open
    def fake_open(p, *a, **k):
        if str(p).endswith("arbiter_consistency_cache.json"):
            return real_open(cache, *a, **k)
        return real_open(p, *a, **k)
    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(m.Path, "read_text", lambda self, encoding="utf-8": cache.read_text(encoding=encoding), raising=False)
    r = c.complete("q")
    monkeypatch.delenv("HUIYAN_ARBITER_CONSISTENCY")
    assert r is not None, "自一致路径也不得返回 None"
