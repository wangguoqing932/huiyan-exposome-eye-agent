#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Is `arbiter_confidence` useful in the normal state? A first measurement.

It is currently kept out of every user-facing surface because its usefulness was
never established. The reason it was doubted at all turned out to be wrong: the
"inverse relation to stability" measured earlier was taken while the rule layer
had been broken by an erroneous downgrade (docs/AGENT_AUDIT.md section 23). So
the question is genuinely open, and open questions that can be measured should be
measured rather than left hanging.

The hypothesis worth testing first is the one the baseline hints at. With the
rules restored, the grade-A rule (r11, supported by a guideline that calls
smoking the primary modifiable risk factor for AMD) reported confidence 0.90
consistently, while the B and C rules reported 0.20-0.85 with wide spread. If
`arbiter_confidence` tracks the rule's evidence grade, it carries information and
could be shown. If it does not, it should stay out of the interface.

A negative result here is as useful as a positive one, and cheaper than shipping
a number whose meaning nobody has established.

Run: python scripts/arbiter_confidence_usefulness.py
"""
from __future__ import annotations

import json
import logging
import os
import statistics
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
OUT = ROOT / "outputs" / "agent" / "arbiter_confidence_usefulness.json"

logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")

# One probe per evidence grade, chosen so the outcome differs across grades where
# possible -- otherwise the measurement would confound grade with outcome.
# Names taken from data/seed/entities_a.csv. The first version of this list used
# invented ids (crp_elevated, uric_acid_high, low_antioxidant_intake), which match
# no rule -- so those probes returned unknown with no arbiter call, the C grade
# had ZERO data points, and the summary still printed an ordering conclusion from
# the two grades that happened to have data.
PROBES = [
    ("current_smoking", "amd_late", [], "A", "r11: guideline says primary modifiable RF"),
    ("current_smoking", "cataract_any", [], "B", "r10: cataract, no guideline in corpus"),
    ("c_reactive_protein", "amd_late", [], "B", "r06: CRP -> late AMD"),
    ("serum_uric_acid", "cataract_any", [], "C", "r01: uric acid -> cataract"),
    ("serum_carotenoids", "cataract_any", [], "C", "r08: carotenoids -> cataract"),
    ("alcohol_intake", "cataract_any", [], "C", "r12: alcohol -> cataract"),
    ("blood_lead", "cataract_any", [], "C", "r14: lead -> cataract"),
]
REPEATS = 8


def main() -> int:
    for v in ("HUANYU_BULK_TEMPERATURE", "HUANYU_ARBITER_TEMPERATURE"):
        os.environ.setdefault(v, "0.0")
    from streamlit_app import get_agent
    from huiyan_agent.risk_rules import load_rules

    grades = {}
    for r in load_rules():
        grades[r.id.split("_")[0]] = r.evidence_level

    agent = get_agent(use_real_llm=True, use_lightrag=True, top_k=5)
    print(f"temperature pinned to 0.0; {REPEATS} repeats per probe")
    print()
    print(f"{'probe':40s} {'grade':>5s} {'tier':>8s} {'conf min-max':>14s}  n")
    print("-" * 84)
    rows = []
    for a, b, pf, want, why in PROBES:
        tiers, confs = [], []
        for _ in range(REPEATS):
            try:
                rep = agent.evaluate(a, b, patient_factors=pf or None)
            except Exception as e:
                rows.append({"a": a, "b": b, "grade": want, "error": str(e)[:60]})
                continue
            ra = rep.risk_assessment
            tiers.append(ra.risk_level.value)
            if ra.arbiter_confidence is not None:
                confs.append(ra.arbiter_confidence)
        label = f"{a} x {b}"
        obs_grade = None
        for s in (getattr(rep, "risk_assessment", None),):
            pass
        if tiers:
            tier = max(set(tiers), key=tiers.count)
        else:
            tier = "ERR"
        rng = (f"{min(confs):.2f}-{max(confs):.2f}" if confs else "none")
        print(f"{label:40s} {want:>5s} {tier:>8s} {rng:>14s}  {len(confs)}")
        rows.append({"a": a, "b": b, "claimed_grade": want, "why": why,
                     "tiers": {t: tiers.count(t) for t in set(tiers)},
                     "conf": confs,
                     "conf_median": round(statistics.median(confs), 3) if confs else None})

    # Does confidence order by grade?
    by_grade: dict[str, list[float]] = {}
    for r in rows:
        if r.get("conf"):
            by_grade.setdefault(r["claimed_grade"], []).extend(r["conf"])
    print()
    print("=" * 84)
    print("  arbiter_confidence pooled by the rule's declared grade:")
    for g in ("A", "B", "C"):
        v = by_grade.get(g)
        if v:
            print(f"    {g}: n={len(v):>3d}  median={statistics.median(v):.2f}  "
                  f"range={min(v):.2f}-{max(v):.2f}")
    meds = {g: statistics.median(v) for g, v in by_grade.items() if v}
    # Require data at ALL THREE grades before reading any ordering. The first
    # version accepted len(meds) >= 2 and duly announced that the field tracked
    # the declared grade while holding no C-grade observation at all -- a
    # conclusion drawn from absence, which is the failure this whole audit keeps
    # running into.
    print()
    if set(meds) != {"A", "B", "C"}:
        print(f"  CANNOT CONCLUDE: confidence available for grades {sorted(meds)}")
        print("  every grade needs observations before an ordering means anything.")
        print("  (A probe with no matching rule returns unknown and no arbiter")
        print("  call, so it contributes no confidence datum.)")
    else:
        ordered = [meds[g] for g in ("A", "B", "C")]
        if ordered == sorted(ordered, reverse=True):
            print("  ORDERED A >= B >= C -> the field tracks declared grade, on")
            print("  these probes. A wider probe set is needed before surfacing it.")
        else:
            print("  NOT ORDERED by grade -> the field does not track the rule's")
            print("  declared evidence grade. Keep it out of the interface.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repeats": REPEATS, "probes": rows,
                               "pooled_by_grade": {k: v for k, v in by_grade.items()}},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
