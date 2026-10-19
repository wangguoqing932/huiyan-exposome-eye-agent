#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression test for the arbiter layer, which previously had none.

The rule layer has had a determinism regression test since the beginning: the
same input always produces the same match, and a change that breaks that is
caught. The arbiter layer -- the third of the agent's three layers, and the one
that decides the tier a user finally sees -- had no test at all.

That gap is not theoretical. While implementing the confidence field, three
wording variants of the same JSON field list moved one pair from "high in 1 of 12
runs" to "high in 6 of 6" to "high in 0 of 12", with the model, the temperature
and the input held fixed. Nothing in the project would have noticed.

What this test asserts, and what it deliberately does not:

* It DOES assert that the rule layer is invariant across repeats. The rule layer
  is deterministic by construction, so any variation is a defect and the test
  fails hard.
* It does NOT assert that the arbiter is invariant, because it is not. It records
  the tier distribution and the arbiter's self-reported confidence, compares them
  against a stored baseline, and fails only when the distribution shifts beyond a
  set tolerance.

That asymmetry is the point. A test that demanded arbiter determinism would fail
permanently and be ignored; a test that demanded nothing would be decoration. The
baseline turns "the arbiter behaves differently now" from an invisible event into
a failing assertion, which is the only property that matters when the strongest
lever on this layer is prompt wording.

Run:  python scripts/arbiter_regression.py --update   (re-record the baseline)
      python scripts/arbiter_regression.py            (compare against it)
      python -m pytest tests/test_arbiter_regression.py -q
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import warnings
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
BASELINE = ROOT / "tests" / "data" / "arbiter_baseline.json"

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

# Fixed probes. Deliberately small so the test is cheap enough to actually run,
# and chosen so that each one covers a different arbitration path: a plain rule
# match, a patient-factor escalation, a rule whose evidence grade was corrected,
# and an out-of-scope pair that must not reach the arbiter at all.
PROBES = [
    ("smoking", "cataract_any", [], "plain rule match"),
    ("fasting_glucose", "cataract_any", ["diabetes"], "patient-factor escalation"),
    ("smoking", "amd_late", [], "rule whose grade was corrected A->B"),
    ("pm25_exposure", "glaucoma_iop_elevated", ["hypertension"], "rule plus factor"),
    ("aspirin", "cataract_any", [], "out of scope: no rule covers it"),
]
REPEATS = 6


def _agent():
    for var in ("HUANYU_BULK_TEMPERATURE", "HUANYU_ARBITER_TEMPERATURE"):
        os.environ.setdefault(var, "0.0")
    from streamlit_app import get_agent
    return get_agent(use_real_llm=True, use_lightrag=True, top_k=5)


def collect(repeats: int = REPEATS) -> dict:
    agent = _agent()
    out = {}
    for a, b, pf, why in PROBES:
        tiers, rule_tiers, conf = [], [], []
        for _ in range(repeats):
            rep = agent.evaluate(a, b, patient_factors=pf or None)
            ra = rep.risk_assessment
            tiers.append(ra.risk_level.value)
            rule_tiers.append(ra.signals[0].risk_level.value if ra.signals else "none")
            conf.append(ra.arbiter_confidence)
        key = f"{a}|{b}|{','.join(pf)}"
        out[key] = {"why": why, "tiers": dict(Counter(tiers)),
                    "rule_tiers": dict(Counter(rule_tiers)),
                    "rule_invariant": len(set(rule_tiers)) == 1,
                    "arbiter_conf": sorted({c for c in conf if c is not None})}
    return {"recorded_on": date.today().isoformat(), "repeats": repeats,
            "probes": out}


def compare(cur: dict, base: dict, tolerance: float) -> list[str]:
    """Report probes whose tier distribution moved by more than `tolerance`."""
    problems = []
    for key, c in cur["probes"].items():
        if not c["rule_invariant"]:
            problems.append(
                f"{key}: RULE LAYER NOT INVARIANT across repeats "
                f"({c['rule_tiers']}) -- the rule layer is deterministic by "
                f"construction, so this is a defect, not drift")
        b = (base.get("probes") or {}).get(key)
        if b is None:
            problems.append(f"{key}: not present in the baseline")
            continue
        n = max(1, sum(c["tiers"].values()))
        for tier in set(list(c["tiers"]) + list(b["tiers"])):
            pc = c["tiers"].get(tier, 0) / n
            pb = b["tiers"].get(tier, 0) / max(1, sum(b["tiers"].values()))
            if abs(pc - pb) > tolerance:
                problems.append(
                    f"{key}: share of '{tier}' moved {pb:.2f} -> {pc:.2f} "
                    f"(tolerance {tolerance:.2f}); baseline={b['tiers']} "
                    f"current={c['tiers']}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true",
                    help="re-record the baseline from the current behaviour")
    ap.add_argument("--repeats", type=int, default=REPEATS)
    ap.add_argument("--tolerance", type=float, default=0.34,
                    help="allowed shift in a tier's share before failing")
    a = ap.parse_args()

    cur = collect(a.repeats)
    print(f"arbiter probes: {len(cur['probes'])} x {a.repeats} repeats, "
          f"temperature pinned to 0.0")
    for key, v in cur["probes"].items():
        print(f"  {key:52s} tiers={v['tiers']}  "
              f"rule={v['rule_tiers']}  conf={v['arbiter_conf']}")

    if a.update or not BASELINE.exists():
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(cur, ensure_ascii=False, indent=2),
                            encoding="utf-8")
        print(f"\nbaseline recorded -> {BASELINE}")
        return 0

    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    problems = compare(cur, base, a.tolerance)
    print()
    if problems:
        print(f"ARBITER REGRESSION: {len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        print("\nNote: the rule-layer entry is always a defect. A moved arbiter "
              "distribution may be intended -- if the prompt or model change was "
              "deliberate, re-record with --update and say so in the audit.")
        return 1
    print(f"no drift beyond tolerance {a.tolerance:.2f}; "
          f"rule layer invariant in all probes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
