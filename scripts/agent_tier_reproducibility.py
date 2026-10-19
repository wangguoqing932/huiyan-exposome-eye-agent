#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Is the agent's risk tier reproducible when the arbiter is in the loop?

Two runs of the full-stack test returned different tiers for the same input:
`smoking x amd_late` came back `high` in the first run and `medium` in the second.
The only difference between the runs was a fix to two probe attribute names, which
cannot affect the evaluation, so the variation comes from somewhere else.

An earlier reliability check found the arbiter stable across five repeats
(distribution {'high': 5}), but that was a single pair. This repeats several pairs
to find out whether the stability generalises or whether that one pair happened
to be stable.

This matters more than it looks. The rule layer is deterministic by construction;
if the final tier varies across runs, then the tier a user sees is not a property
of the input, and any downstream statement of the form "the system rates this
high" is not reproducible. That is acceptable for a screening aid only if it is
known and disclosed -- so it needs measuring, not assuming.

Run: python scripts/agent_tier_reproducibility.py
"""
from __future__ import annotations

import json
import logging
import sys
import warnings
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
OUT = ROOT / "outputs" / "agent" / "tier_reproducibility.json"

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

PAIRS = [
    ("smoking", "amd_late", None),
    ("smoking", "cataract_any", None),
    ("fasting_glucose", "cataract_any", ["diabetes"]),
    ("pm25_exposure", "glaucoma_iop_elevated", ["hypertension"]),
]
REPEATS = 5


def main() -> int:
    from streamlit_app import get_agent
    agent = get_agent(use_real_llm=True, use_lightrag=True, top_k=5)
    print(f"arbiter in the loop; {REPEATS} repeats per pair")
    print()
    results = []
    for a, b, pf in PAIRS:
        levels, rule_levels, secs = [], [], []
        for _ in range(REPEATS):
            rep = agent.evaluate(a, b, patient_factors=pf)
            ra = rep.risk_assessment
            levels.append(ra.risk_level.value)
            # what the RULE layer alone said, to separate the two sources
            rl = "none"
            if ra.signals:
                rl = ra.signals[0].risk_level.value
            rule_levels.append(rl)
        c = Counter(levels)
        cr = Counter(rule_levels)
        label = f"{a} x {b}" + (f" +{','.join(pf)}" if pf else "")
        stable = len(c) == 1
        results.append({"a": a, "b": b, "factors": pf,
                        "final_levels": dict(c), "rule_levels": dict(cr),
                        "stable": stable})
        print(f"  {label:48s} final={dict(c)}")
        print(f"  {'':48s} rule ={dict(cr)}  "
              f"{'STABLE' if stable else '*** VARIES ***'}")

    varies = [r for r in results if not r["stable"]]
    print()
    print("=" * 78)
    print(f"  pairs tested          : {len(results)}")
    print(f"  stable final tier     : {len(results) - len(varies)}")
    print(f"  VARIES across repeats : {len(varies)}")
    for v in varies:
        print(f"    {v['a']} x {v['b']}: {v['final_levels']}  "
              f"(rule layer was {v['rule_levels']})")
    rv = [r for r in results if len(r["rule_levels"]) > 1]
    print(f"  rule layer itself varying: {len(rv)} "
          f"(expect 0 -- the rule layer is deterministic)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repeats": REPEATS, "pairs": results,
                               "varies": len(varies)},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
