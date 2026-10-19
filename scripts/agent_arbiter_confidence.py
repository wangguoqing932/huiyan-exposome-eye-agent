#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Does the agent tell you when the arbiter is unsure?

At temperature 0.0, `smoking x amd_late` still returns high about once in twelve
runs while a control pair is stable twelve out of twelve, and the rule layer is
stable in both cases. That pattern -- instability concentrated in one pair --
suggests the arbiter is near a decision boundary there rather than the provider
being uniformly noisy.

`RiskAssessment` carries `confidence` and `confidence_score`. If the borderline
case reports lower confidence than the stable ones, then the system already
contains the information a user needs to know when to trust the tier, and the
remedy is to surface it rather than to make the model deterministic. If it does
not, then confidence is not measuring what its name suggests and should not be
displayed as though it were.

Either answer is useful; guessing between them is not.

Run: python scripts/agent_arbiter_confidence.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "arbiter_confidence.json"

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

REPEATS = 6
CASES = [
    ("smoking", "amd_late", None, "borderline (varied ~8% at temp 0)"),
    ("smoking", "cataract_any", None, "stable"),
    ("fasting_glucose", "cataract_any", ["diabetes"], "stable, factor escalation"),
    ("pm25_exposure", "glaucoma_iop_elevated", ["hypertension"], "stable"),
    ("aspirin", "cataract_any", None, "out of scope (no arbiter call)"),
]


def main() -> int:
    for var in ("HUANYU_BULK_TEMPERATURE", "HUANYU_ARBITER_TEMPERATURE"):
        os.environ.setdefault(var, "0.0")
    sys.path.insert(0, str(ROOT / "app"))
    from streamlit_app import get_agent
    agent = get_agent(use_real_llm=True, use_lightrag=True, top_k=5)

    print(f"temperature pinned to 0.0; {REPEATS} repeats per case")
    print()
    print(f"{'case':44s} {'level':>8s} {'conf':>6s} {'score':>6s} {'arbiter':>8s}")
    print("-" * 72)
    rows = []
    for a, b, pf, why in CASES:
        lv, cf, sc, ac = [], [], [], []
        for _ in range(REPEATS):
            rep = agent.evaluate(a, b, patient_factors=pf)
            ra = rep.risk_assessment
            lv.append(ra.risk_level.value)
            cf.append(getattr(ra, "confidence", None))
            sc.append(getattr(ra, "confidence_score", None))
            ac.append(getattr(ra, "arbiter_confidence", None))
        def rng(v):
            vv = [x for x in v if isinstance(x, (int, float))]
            if not vv:
                return "n/a"
            return f"{min(vv):.2f}" if min(vv) == max(vv) else f"{min(vv):.2f}-{max(vv):.2f}"
        label = f"{a} x {b}" + (f" +{','.join(pf)}" if pf else "")
        print(f"{label:44s} {str(len(set(lv)))+' lvl':>8s} "
              f"{rng(cf):>6s} {rng(sc):>6s} {rng(ac):>8s}")
        rows.append({"a": a, "b": b, "factors": pf, "why": why,
                     "levels": lv, "distinct_levels": len(set(lv)),
                     "confidence": rng(cf), "score": rng(sc),
                     "arbiter_confidence": rng(ac), "confidence_raw": cf,
                     "arbiter_confidence_raw": ac})

    print()
    print("=" * 72)
    print("  per-case detail")
    for r in rows:
        print(f"    {r['a']} x {r['b']}: levels={dict((x, r['levels'].count(x)) for x in set(r['levels']))}")
        print(f"      confidence={r['confidence']}  score={r['score']}  ({r['why']})")

    numeric = [r for r in rows if r["score"] != "n/a"]
    print()
    if numeric:
        vals = []
        for r in numeric:
            s = r["score"]
            vals.append((r["a"] + " x " + r["b"],
                         float(s.split("-")[0]), r["distinct_levels"]))
        vals.sort(key=lambda x: x[1])
        print("  cases ordered by lowest confidence score:")
        for name, v, dl in vals:
            print(f"    {v:.2f}  {name}  (distinct levels: {dl})")
        lo = [v for _, v, _ in vals[:1]]
        print()
        print(f"  lowest score={lo[0]:.2f}; highest={max(v for _, v, _ in vals):.2f}")
    else:
        print("  CONFIDENCE IS NOT POPULATED: the field exists but carries no "
              "numeric value, so it cannot be used to flag uncertain decisions.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repeats": REPEATS, "cases": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
