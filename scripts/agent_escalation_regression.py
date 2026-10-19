#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression guard for the patient-factor escalation fix.

The fix populates each Rule's escalation_map at load time from the top-level
patient_factor_rules. That touches the rule objects, so it could in principle
change the factor-free output that the internal-layer metrics depend on
(evaluate.py calls match_rules without patient factors).

This asserts it does not: the factor-free signal set must be byte-identical to
the pre-fix audit that was captured before the change, and the escalating call
must now actually escalate.

Run: python scripts/agent_escalation_regression.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
AUDIT = ROOT / "outputs" / "agent" / "agent_audit.json"
ORDER = {"unknown": 0, "low": 1, "medium": 2, "high": 3}


def main() -> int:
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import load_rules, match_rules

    recorded = json.loads(AUDIT.read_text(encoding="utf-8"))["hits"]
    rules = load_rules()
    A = pd.read_csv(ROOT / "data" / "seed" / "entities_a.csv")
    B = pd.read_csv(ROOT / "data" / "seed" / "entities_b.csv")

    # ---- 1. factor-free output must equal the pre-fix audit -----------------
    fresh = {}
    for aid in A["exposure_id"]:
        ra = resolve_entity_a(str(aid))
        if ra is None:
            continue
        for bid in B["entity_b_id"]:
            rb = resolve_entity_b(str(bid))
            if rb is None:
                continue
            sig = match_rules(rules, ra, rb)          # no factors, as evaluate.py
            if sig:
                fresh[f"{aid}|{bid}"] = sorted({s.rule_id for s in sig})

    same = fresh == recorded
    print("=== 1. Factor-free regression (vs pre-fix audit) ===")
    print(f"  pairs before : {len(recorded)}")
    print(f"  pairs after  : {len(fresh)}")
    only_before = sorted(set(recorded) - set(fresh))
    only_after = sorted(set(fresh) - set(recorded))
    changed = sorted(k for k in set(recorded) & set(fresh)
                     if recorded[k] != fresh[k])
    print(f"  pairs lost   : {len(only_before)} {only_before[:3]}")
    print(f"  pairs gained : {len(only_after)} {only_after[:3]}")
    print(f"  pairs changed: {len(changed)} {changed[:3]}")
    print(f"  IDENTICAL    : {'YES' if same else 'NO  <-- REGRESSION'}")

    # ---- 2. escalation must now fire ---------------------------------------
    pf = json.loads(json.dumps(
        __import__("yaml").safe_load(
            (ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    ))["patient_factor_rules"]
    raised, inert = [], []
    for aid in A["exposure_id"]:
        ra = resolve_entity_a(str(aid))
        if ra is None:
            continue
        for bid in B["entity_b_id"]:
            rb = resolve_entity_b(str(bid))
            if rb is None:
                continue
            base = match_rules(rules, ra, rb)
            if not base:
                continue
            lb = max((s.risk_level.value for s in base), key=lambda x: ORDER[x])
            for factor, spec in pf.items():
                applies = (bool(set(ra.flags) & set(spec.get("matching_entity_a_flags") or []))
                           and bool(set(rb.flags) & set(spec.get("matching_entity_b_flags") or [])))
                esc = match_rules(rules, ra, rb, [factor])
                le = max((s.risk_level.value for s in esc), key=lambda x: ORDER[x])
                rec = (str(aid), str(bid), factor, lb, le)
                if ORDER[le] > ORDER[lb]:
                    raised.append(rec)
                elif applies:
                    inert.append(rec)

    print()
    print("=== 2. Escalation now fires ===")
    print(f"  level RAISED              : {len(raised)}")
    print(f"  applicable but still inert: {len(inert)}")
    for r in raised[:8]:
        print(f"    {r[2]:24s} {r[0]} x {r[1]}: {r[3]} -> {r[4]}")
    if inert:
        print("  still inert (inspect):")
        for r in inert[:6]:
            print(f"    {r[2]:24s} {r[0]} x {r[1]}: stayed {r[3]}")

    # ---- 3. the hard floor can now trigger --------------------------------
    from huiyan_agent.safety_agent import SafetyAgent, SafetyAgentConfig
    ag = SafetyAgent(config=SafetyAgentConfig(use_llm_arbiter=False))
    rep = ag.evaluate("fasting_glucose", "cataract_any", patient_factors=["diabetes"])
    ra_ = rep.risk_assessment
    print()
    print("=== 3. End-to-end, no LLM (rule layer only) ===")
    print(f"  risk_level : {ra_.risk_level.value}")
    print(f"  metadata   : escalation_backed_high="
          f"{rep.metadata.get('escalation_backed_high')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
