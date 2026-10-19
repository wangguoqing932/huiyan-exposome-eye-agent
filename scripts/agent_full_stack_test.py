#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Exercise the agent the way the application actually constructs it.

Every test so far built `SafetyAgent(...)` directly. But the only caller of
`agent.evaluate` in the whole project is `app/streamlit_app.py`, and it never
constructs the agent itself -- it calls `get_agent(use_real_llm, use_lightrag,
top_k)` and uses whatever comes back. So the configuration a user actually runs
is the one inside `get_agent`, and it has never been exercised end to end.

That matters because the three layers fail in different ways and a direct
construction can silently omit two of them:

  * with `self.llm is None` the arbiter returns early, so the agent looks like a
    pure rule engine and every LLM-dependent behaviour is absent;
  * with `self.lightrag is None` the evidence retrieval returns nothing, so
    reports come back with justifications but no citations.

This runs the canonical constructor with all three layers on, over a set of
probes chosen to hit different code paths, and records what each layer actually
contributed. It asserts that both optional layers are present, because a silent
degradation to the rule layer alone is precisely the failure mode that would let
a broken deployment look healthy.

Run: python scripts/agent_full_stack_test.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
OUT = ROOT / "outputs" / "agent" / "full_stack_test.json"

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

# Probes chosen to hit distinct paths rather than to flatter the system.
PROBES = [
    ("smoking", "cataract_any", None, "single rule, no patient factors"),
    ("fasting_glucose", "cataract_any", ["diabetes"],
     "rule plus a patient factor that should escalate"),
    ("pm25_exposure", "glaucoma_iop_elevated", ["hypertension"],
     "rule plus factor, arbiter previously escalated this one"),
    ("aspirin", "cataract_any", None, "out of scope -- no rule covers it"),
    ("totally_unknown_exposure", "cataract_any", None,
     "out of scope by construction"),
    ("smoking", "amd_late", None, "the rule whose grade was corrected"),
]


def main() -> int:
    from streamlit_app import get_agent

    print("constructing the agent through the application's own entry point")
    t0 = time.time()
    agent = get_agent(use_real_llm=True, use_lightrag=True, top_k=5)
    build_s = time.time() - t0

    llm = getattr(agent, "llm", None)
    lr = getattr(agent, "lightrag", None)
    # SafetyAgent stores the evidence store as self.store; probing
    # evidence_store returns None and reports the layer as ABSENT when it is
    # present and working. The first run of this test made exactly that error.
    ev = getattr(agent, "store", None) or getattr(agent, "evidence_store", None)
    print(f"  built in {build_s:.1f}s")
    print(f"  rule engine      : {len(getattr(agent, 'rules', []) or [])} rules")
    print(f"  evidence store   : {'present' if ev is not None else 'ABSENT'}")
    print(f"  lightrag         : {'present' if lr is not None else 'ABSENT'}")
    print(f"  llm arbiter      : {'present' if llm is not None else 'ABSENT'}")

    # A silent degradation to the rule layer alone is the failure this test is
    # for, so refuse to report a pass when a layer did not come up.
    degraded = []
    if llm is None:
        degraded.append("llm arbiter absent -- escalation and out-of-scope "
                        "handling would silently fall back to the rule layer")
    if lr is None:
        degraded.append("lightrag absent -- retrieval would return no citations")
    if degraded:
        print("\nDEGRADED CONSTRUCTION:")
        for d in degraded:
            print(f"  {d}")

    rows = []
    print(f"\n{'probe':46s} {'level':>8s} {'rules':>6s} {'ev':>4s} {'s':>6s}")
    print("-" * 78)
    for a, b, pf, why in PROBES:
        t = time.time()
        try:
            rep = agent.evaluate(a, b, patient_factors=pf)
        except Exception as e:
            rows.append({"a": a, "b": b, "factors": pf, "why": why,
                         "error": f"{type(e).__name__}: {e}"})
            print(f"{a + ' x ' + b:46s}  ERROR {type(e).__name__}: {str(e)[:30]}")
            continue
        dt = time.time() - t
        ra = getattr(rep, "risk_assessment", None)
        level = ra.risk_level.value if ra is not None and hasattr(ra, "risk_level") else "?"
        sig = list(getattr(ra, "signals", []) or []) if ra is not None else []
        evd = list(getattr(rep, "evidence", []) or [])
        txt = getattr(rep, "report_text", "") or ""
        rows.append({
            "a": a, "b": b, "factors": pf, "why": why, "level": level,
            "n_signals": len(sig),
            "rule_ids": [getattr(s, "rule_id", "?") for s in sig],
            "signal_levels": [getattr(getattr(s, "risk_level", None), "value", "?")
                              for s in sig],
            "n_evidence": len(evd),
            "seconds": round(dt, 2),
            # out_of_scope is not a field on RiskAssessment or SafetyReport; it lives in
        # report.metadata (safety_agent.py:316). Reading it off the report returns
        # False for every probe, including genuinely out-of-scope ones.
        "out_of_scope": bool((getattr(rep, "metadata", {}) or {}).get("out_of_scope", False)),
            "has_report_text": bool(txt.strip()),
            "mentions_llm": ("仲裁" in txt) or ("arbiter" in txt.lower()),
        })
        print(f"{a + ' x ' + b:46s} {level:>8s} {len(sig):>6d} {len(evd):>4d} "
              f"{dt:>6.1f}")

    print()
    oos = [r for r in rows if r.get("out_of_scope")]
    withsig = [r for r in rows if r.get("n_signals")]
    withcite = [r for r in rows if r.get("n_evidence")]
    withev = [r for r in rows if r.get("n_evidence")]
    print(f"  probes                 : {len(rows)}")
    print(f"  produced a signal      : {len(withsig)}")
    print(f"  produced evidence      : {len(withev)}")
    print(f"  flagged out_of_scope   : {len(oos)}")
    print(f"  produced report text   : {sum(1 for r in rows if r.get('has_report_text'))}")
    print(f"  mention the arbiter    : {sum(1 for r in rows if r.get('mentions_llm'))}")

    # The arbiter layer must actually appear in the reports when it is present;
    # a report that never mentions it while the layer is loaded means the layer
    # exists but is not wired into the output.
    if llm is not None and not any(r.get("mentions_llm") for r in rows):
        print("\n  WARNING: the arbiter is loaded but no report mentions it.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "built_seconds": round(build_s, 1),
        "layers": {"rules": len(getattr(agent, "rules", []) or []),
                   "evidence_store": ev is not None,
                   "lightrag": lr is not None, "llm": llm is not None},
        "degraded": degraded, "probes": rows},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 1 if degraded else 0


if __name__ == "__main__":
    raise SystemExit(main())
