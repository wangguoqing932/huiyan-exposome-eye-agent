#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agent coverage and stability audit — the systematic test the agent never had.

WHY
---
The three layers were verified to work on one case. One case is not a test of an
agent. This runs the rule engine across every registered pair and reports what
the rule base can and cannot speak to, then checks that repeated runs agree.

Deliberately uses the RULE LAYER ONLY (no LLM, no retrieval) for the coverage
sweep: 615 pairs each making an LLM call would be slow and would confound "no
rule matched" with "the arbiter was unavailable". The LLM layer is exercised
separately on a sample.

Run: python scripts/agent_audit.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "agent_audit.json"


def main() -> int:
    from huiyan_agent.evidence_store import EvidenceStore
    from huiyan_agent.normalize import resolve_entity_a, resolve_entity_b
    from huiyan_agent.risk_rules import match_rules
    from huiyan_agent.safety_agent import SafetyAgent

    A = pd.read_csv(ROOT / "data" / "seed" / "entities_a.csv")
    B = pd.read_csv(ROOT / "data" / "seed" / "entities_b.csv")
    agent = SafetyAgent()
    rules = agent.rules

    print(f"Registry: {len(A)} exposures x {len(B)} eye diseases = "
          f"{len(A) * len(B)} possible pairs")
    print(f"Rule base: {len(rules)} rules")
    print()

    # ---------- 1. rule-level coverage ------------------------------------
    hits: dict[str, list[str]] = {}
    unresolved = []
    for aid in A["exposure_id"]:
        ra = resolve_entity_a(str(aid))
        if ra is None:
            unresolved.append(("a", str(aid)))
            continue
        for bid in B["entity_b_id"]:
            rb = resolve_entity_b(str(bid))
            if rb is None:
                unresolved.append(("b", str(bid)))
                continue
            sig = match_rules(rules, ra, rb, [])
            if sig:
                hits[f"{aid}|{bid}"] = sorted({s.rule_id for s in sig})

    total = len(A) * len(B)
    print("=== 1. Rule-layer coverage ===")
    print(f"  pairs evaluated        : {total}")
    print(f"  pairs with >=1 signal  : {len(hits)} ({len(hits)/total:.1%})")
    print(f"  pairs with no signal   : {total - len(hits)} "
          f"({(total-len(hits))/total:.1%})")
    if unresolved:
        print(f"  unresolved entities    : {len(unresolved)} "
              f"-> {unresolved[:4]}")

    # which rules fire at all
    fired = Counter(r for v in hits.values() for r in v)
    print()
    print(f"  rules that fire somewhere : {len(fired)} of {len(rules)}")
    dead = [r.id for r in rules if r.id not in fired]
    if dead:
        print(f"  rules that NEVER fire     : {len(dead)}")
        for d in dead:
            print(f"      {d}")

    # exposure coverage
    exp_hit = {k.split("|")[0] for k in hits}
    dis_hit = {k.split("|")[1] for k in hits}
    print()
    print(f"  exposures with any hit    : {len(exp_hit)} of {len(A)}")
    print(f"  diseases with any hit     : {len(dis_hit)} of {len(B)}")
    if len(dis_hit) < len(B):
        print(f"      unreachable diseases: "
              f"{sorted(set(B['entity_b_id']) - dis_hit)}")

    # ---------- 2. determinism --------------------------------------------
    print()
    print("=== 2. Determinism (same input, repeated) ===")
    sample = list(hits)[:20] or ["serum_uric_acid|cataract_any"]
    unstable = []
    for key in sample:
        aid, bid = key.split("|")
        ra, rb = resolve_entity_a(aid), resolve_entity_b(bid)
        seen = {tuple(sorted({s.rule_id for s in match_rules(rules, ra, rb, [])}))
                for _ in range(3)}
        if len(seen) > 1:
            unstable.append(key)
    print(f"  pairs re-run 3x      : {len(sample)}")
    print(f"  pairs giving varying rule sets: {len(unstable)} "
          f"{unstable[:3] if unstable else ''}")

    # ---------- 3. patient-factor escalation -------------------------------
    print()
    print("=== 3. Patient-factor escalation ===")
    esc_examples = []
    for key in sample[:12]:
        aid, bid = key.split("|")
        ra, rb = resolve_entity_a(aid), resolve_entity_b(bid)
        base = match_rules(rules, ra, rb, [])
        with_f = match_rules(rules, ra, rb, ["diabetes", "smoking", "hypertension"])
        if len(with_f) != len(base):
            esc_examples.append((key, len(base), len(with_f)))
    print(f"  pairs whose signal count changes when patient factors are added: "
          f"{len(esc_examples)}")
    for k, a, b in esc_examples[:5]:
        print(f"      {k}: {a} -> {b} signals")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "registry": {"exposures": len(A), "diseases": len(B),
                     "possible_pairs": total},
        "rules_total": len(rules),
        "pairs_with_signal": len(hits), "pairs_without_signal": total - len(hits),
        "rules_that_fire": len(fired), "rules_that_never_fire": dead,
        "exposures_with_hit": len(exp_hit), "diseases_with_hit": len(dis_hit),
        "unreachable_diseases": sorted(set(B["entity_b_id"]) - dis_hit),
        "unresolved_entities": unresolved,
        "nondeterministic_pairs": unstable,
        "escalation_examples": esc_examples,
        "hits": hits}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
