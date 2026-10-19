#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the patient-factor escalation, which is a claimed agent feature.

The first audit counted SIGNALS and so reported "patient factors change nothing".
That was the wrong metric: match_rules uses patient factors to escalate the risk
LEVEL, not to add signals. This tests the level.

The four factors the rule base knows are diabetes, hypertension,
chronic_kidney_disease and elderly; each names the exposure flags and outcome
flags it applies to, so escalation should fire only on matching pairs and must
never fire on a pair whose flags are outside the map.

Run: python scripts/agent_escalation_test.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "escalation_test.json"

ORDER = {"unknown": 0, "low": 1, "medium": 2, "high": 3}


def level(signals) -> str:
    if not signals:
        return "low"
    return max((s.risk_level.value for s in signals), key=lambda x: ORDER[x])


def main() -> int:
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import match_rules
    from huiyan_agent.safety_agent import SafetyAgent

    agent = SafetyAgent()
    rules = agent.rules
    pf = yaml.safe_load((ROOT / "configs" / "rules.yaml")
                        .read_text(encoding="utf-8"))["patient_factor_rules"]
    print(f"Patient factors known to the rule base: {sorted(pf)}")
    print()

    A = pd.read_csv(ROOT / "data" / "seed" / "entities_a.csv")
    B = pd.read_csv(ROOT / "data" / "seed" / "entities_b.csv")

    raised, unchanged, would_raise = [], [], []
    for aid in A["exposure_id"]:
        ra = resolve_entity_a(str(aid))
        if ra is None:
            continue
        for bid in B["entity_b_id"]:
            rb = resolve_entity_b(str(bid))
            if rb is None:
                continue
            base = match_rules(rules, ra, rb, [])
            if not base:
                continue
            for factor in sorted(pf):
                esc = match_rules(rules, ra, rb, [factor])
                lb, le = level(base), level(esc)
                # should this factor apply to this pair at all?
                spec = pf[factor]
                applies = (bool(set(ra.flags) & set(spec.get("matching_entity_a_flags") or []))
                           and bool(set(rb.flags) & set(spec.get("matching_entity_b_flags") or [])))
                rec = {"exposure": str(aid), "disease": str(bid), "factor": factor,
                       "level_base": lb, "level_with_factor": le,
                       "should_apply": applies}
                if ORDER[le] > ORDER[lb]:
                    raised.append(rec)
                elif applies and ORDER[le] == ORDER[lb]:
                    would_raise.append(rec)
                else:
                    unchanged.append(rec)

    print("=== Escalation behaviour across every pair that has a signal ===")
    print(f"  factor applications tested : {len(raised)+len(unchanged)+len(would_raise)}")
    print(f"  level RAISED               : {len(raised)}")
    print(f"  applicable but NOT raised  : {len(would_raise)}   <-- would be a defect")
    print(f"  not applicable (correctly inert): {len(unchanged)}")
    print()
    if raised:
        print("  examples of escalation:")
        for r in raised[:8]:
            print(f"    {r['factor']:24s} {r['exposure']} x {r['disease']}: "
                  f"{r['level_base']} -> {r['level_with_factor']}")
    if would_raise:
        print()
        print("  APPLICABLE BUT INERT (these are defects):")
        for r in would_raise[:10]:
            print(f"    {r['factor']:24s} {r['exposure']} x {r['disease']}: "
                  f"stayed {r['level_base']}")

    # does the escalation ever fire on a non-matching pair?
    spurious = [r for r in raised if not r["should_apply"]]
    print()
    print(f"  escalations on a pair the map does NOT cover: {len(spurious)} "
          f"{'(defect)' if spurious else '(none)'}")
    for r in spurious[:5]:
        print(f"    {r['factor']} {r['exposure']} x {r['disease']}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "factors": sorted(pf), "n_tested": len(raised) + len(unchanged) + len(would_raise),
        "raised": raised, "applicable_but_inert": would_raise,
        "spurious_escalations": spurious, "n_inert_not_applicable": len(unchanged)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
