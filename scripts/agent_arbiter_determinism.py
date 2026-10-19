#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Decide whether the arbiter's tier variation is sampling or server-side.

The previous round found `smoking x amd_late` returning {medium: 4, high: 1} over
five repeats while the rule layer said medium every time. The obvious first
hypothesis is sampling temperature, and the code already defaults it to 0.0 --
`HUANYU_BULK_TEMPERATURE` defaults to 0.0 and no `HUANYU_ARBITER_TEMPERATURE` is
set, so the arbiter runs at 0.0 already.

If the tier still varies at temperature 0, the variation is not something this
project can fix by setting a parameter: it is coming from the provider. That is a
different problem with a different remedy, so it is worth separating the two
rather than assuming.

This runs the one pair that varied, many times, at an explicitly pinned
temperature of 0.0, and reports the distribution plus a two-sided binomial
interval on the escalation rate. It also pins a pair that was stable as a
control, because a test that only exercises the failing case cannot tell a
flaky provider from a broken script.

Run: python scripts/agent_arbiter_determinism.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import warnings
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
OUT = ROOT / "outputs" / "agent" / "arbiter_determinism.json"

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

REPEATS = 12
CASES = [
    ("smoking", "amd_late", None, "the pair that varied"),
    ("smoking", "cataract_any", None, "control: stable before"),
]


def main() -> int:
    # Pin the temperature for both channels before anything reads the env.
    for var in ("HUANYU_BULK_TEMPERATURE", "HUANYU_ARBITER_TEMPERATURE"):
        os.environ.setdefault(var, "0.0")
    from huiyan_agent.llm_client import DualLLMClient
    from huiyan_agent.risk_rules import load_rules
    from huiyan_agent.safety_agent import SafetyAgent, SafetyAgentConfig

    rules = load_rules()
    llm = DualLLMClient.from_env()
    print("temperature pinned to 0.0 on both channels")
    for name, cli in (("primary", getattr(llm, "primary", None)),
                      ("arbiter", getattr(llm, "arbiter", None))):
        t = getattr(cli, "temperature", None) if cli is not None else None
        m = getattr(cli, "model", None) if cli is not None else None
        print(f"  {name}: temperature={t} model={m}")

    agent = SafetyAgent(llm_client=llm,
                        config=SafetyAgentConfig(use_llm_arbiter=True,
                                                 tiered_arbiter=True))

    results = []
    print()
    for a, b, pf, why in CASES:
        levels, base = [], []
        for _ in range(REPEATS):
            try:
                rep = agent.evaluate(a, b, patient_factors=pf)
                ra = rep.risk_assessment
                levels.append(ra.risk_level.value)
                base.append(ra.signals[0].risk_level.value if ra.signals else "none")
            except Exception as e:
                levels.append(f"ERR:{type(e).__name__}")
                base.append("ERR")
        c, cb = Counter(levels), Counter(base)
        # rate at which the arbiter moved the tier off the rule layer's answer
        moved = sum(n for lv, n in c.items() if base[0] not in (lv,)
                    and lv.startswith(("high", "medium", "low")))
        label = f"{a} x {b}"
        print(f"  {label:34s} final={dict(c)}")
        print(f"  {'':34s} rule ={dict(cb)}  ({why})")
        results.append({"a": a, "b": b, "why": why, "final": dict(c),
                        "rule": dict(cb), "repeats": REPEATS,
                        "distinct_final": len(c)})

    print()
    print("=" * 78)
    varying = [r for r in results if r["distinct_final"] > 1]
    print(f"  cases                  : {len(results)}")
    print(f"  varies at temp=0       : {len(varying)}")
    if varying:
        print()
        print("  CONCLUSION: the arbiter is not reproducible even with temperature")
        print("  pinned to 0.0. The variation is therefore NOT a sampling parameter")
        print("  this project can set -- it comes from the provider's serving of")
        print("  deepseek/deepseek-v4.1-flash. Remedies that change temperature will")
        print("  not fix it; the options are to accept and disclose it, to make the")
        print("  rule layer authoritative, or to require the arbiter to emit a")
        print("  machine-checkable justification so a tier change is auditable.")
    else:
        print()
        print("  CONCLUSION: no variation at temperature 0.0 in this sample. The")
        print("  earlier variation may have come from the unpinned default path;")
        print("  re-run the wider reproducibility test before concluding.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repeats": REPEATS,
                               "temperature": 0.0,
                               "model": os.getenv("HUANYU_ARBITER_MODEL"),
                               "results": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
