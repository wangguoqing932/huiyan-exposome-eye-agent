#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LLM arbiter reliability — the third layer, which had never been tested.

The arbiter is an LLM deciding a risk level. Three properties matter and none had
been checked:

  1. REPEATABILITY. The same case run repeatedly must not wander. Some variation
     is expected from a sampling model, but a level that flips between runs makes
     the report unusable as a screening output.
  2. THE ESCALATION FLOOR HOLDS. safety_agent.py refuses any arbiter downgrade of
     a high that patient factors legitimately produced. That guard had never been
     exercised, because the rule layer never produced such a high (the defect
     fixed in the previous round). Now it can, so the guard is testable.
  3. OUT OF SCOPE READS AS UNKNOWN, NOT AS LOW. An unregistered entity must not
     be reported as "assessed, nothing found" -- that is the difference between
     "we looked and it is fine" and "we could not look".

Run: python scripts/agent_arbiter_reliability.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "arbiter_reliability.json"

REPEATS = 5
LEVEL_ORDER = {"unknown": 0, "low": 1, "medium": 2, "high": 3}


def build(use_llm: bool = True):
    from huiyan_agent.evidence_store import EvidenceStore
    from huiyan_agent.llm_client import DualLLMClient, LLMClient, LLMConfig
    from huiyan_agent.safety_agent import SafetyAgent, SafetyAgentConfig
    llm = DualLLMClient.from_env() if use_llm else LLMClient(LLMConfig(provider="stub"))
    return SafetyAgent(evidence_store=EvidenceStore(), llm_client=llm,
                       config=SafetyAgentConfig(use_llm_arbiter=use_llm,
                                                tiered_arbiter=True, top_k_evidence=5))


def main() -> int:
    import logging
    logging.disable(logging.CRITICAL)
    import warnings
    warnings.filterwarnings("ignore")

    ag = build(True)
    record = {}

    # ---- 1. repeatability ---------------------------------------------------
    print(f"=== 1. Repeatability ({REPEATS} runs on one case) ===")
    case = ("fasting_glucose", "cataract_any", ["diabetes"])
    levels, times = [], []
    for i in range(REPEATS):
        t = time.time()
        rep = ag.evaluate(case[0], case[1], patient_factors=case[2])
        times.append(time.time() - t)
        lv = rep.risk_assessment.risk_level.value
        levels.append(lv)
        print(f"  run {i+1}: level={lv:7s} arbiter={rep.metadata.get('llm_role')} "
              f"{times[-1]:.1f}s")
    dist = Counter(levels)
    print(f"  distribution: {dict(dist)}")
    print(f"  stable: {'YES' if len(dist) == 1 else 'NO  <-- varies across runs'}")
    record["repeatability"] = {"case": list(case), "levels": levels,
                               "distribution": dict(dist),
                               "stable": len(dist) == 1,
                               "mean_seconds": round(sum(times) / len(times), 1)}

    # ---- 2. escalation floor ------------------------------------------------
    print()
    print("=== 2. Escalation floor (arbiter must not downgrade a backed high) ===")
    from huiyan_agent.safety_agent import SafetyAgent, SafetyAgentConfig
    rule_only = SafetyAgent(config=SafetyAgentConfig(use_llm_arbiter=False))
    floor_cases = [("fasting_glucose", "cataract_any", ["diabetes"]),
                   ("hba1c", "dr_npdr", ["diabetes"]),
                   ("serum_uric_acid", "cataract_any", ["chronic_kidney_disease"])]
    floor_rows = []
    for a, b, f in floor_cases:
        r0 = rule_only.evaluate(a, b, patient_factors=f)
        backed = bool(r0.metadata.get("escalation_backed_high"))
        r1 = ag.evaluate(a, b, patient_factors=f)   # with arbiter
        l0, l1 = (r0.risk_assessment.risk_level.value,
                  r1.risk_assessment.risk_level.value)
        held = (not backed) or LEVEL_ORDER[l1] >= LEVEL_ORDER[l0]
        floor_rows.append({"exposure": a, "disease": b, "factors": f,
                           "rule_only_level": l0, "with_arbiter_level": l1,
                           "escalation_backed_high": backed, "floor_held": held})
        print(f"  {a} x {b} +{f}: rule={l0} arbiter={l1} "
              f"backed={backed} held={'OK' if held else 'VIOLATED'}")
    record["escalation_floor"] = floor_rows

    # ---- 3. out of scope ----------------------------------------------------
    print()
    print("=== 3. Out of scope reads as UNKNOWN ===")
    oos = []
    for a, b in [("aspirin", "cataract_any"), ("fasting_glucose", "macular_hole"),
                 ("totally_unknown_exposure", "cataract_any")]:
        rep = ag.evaluate(a, b)
        lv = rep.risk_assessment.risk_level.value
        ok = lv == "unknown"
        oos.append({"exposure": a, "disease": b, "level": lv,
                    "out_of_scope": rep.metadata.get("out_of_scope"),
                    "reported_as_unknown": ok})
        print(f"  {a} x {b}: level={lv} out_of_scope="
              f"{rep.metadata.get('out_of_scope')} "
              f"{'OK' if ok else '<-- reported as something other than UNKNOWN'}")
    record["out_of_scope"] = oos

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
