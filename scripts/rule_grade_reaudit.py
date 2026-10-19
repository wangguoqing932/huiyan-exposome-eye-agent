#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Re-audit rule grades against what the corpus actually CONTAINS, not its links.

The earlier grade audit (which led to regrading 11 rules) read the per-chunk
`linked_rules` field and concluded that a rule whose linked chunks were all B or C
had no guideline support. That conclusion was wrong, and the way it was wrong
matters more than the conclusion:

**All 159 AAO PPP chunks in the corpus have `linked_rules` empty** -- 0 of 159 --
while 34 of them are grade A and one states, verbatim:

    "Risk factors for the development of advanced AMD include smoking ...
     Cigarette smoking has been identified as the primary modifiable risk factor
     in numerous studies on advanced AMD. It is strongly recommended to advise
     patients with AMD or those at risk for AMD to stop smoking."
    (AAO PPP AMD - Section 9, evidence_level A)

So grade-A guideline evidence existed, was retrievable (the agent surfaces it as
EV2/EV5), and was invisible to an audit that read `linked_rules`. "No link" is not
"no evidence", and an empty field defaulted to a substantive claim.

This re-audits by scanning corpus TEXT for each rule's own flags, which is
independent of `linked_rules`, and reports the best grade actually present.

Run: python scripts/rule_grade_reaudit.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "rule_grade_reaudit.json"
ORD = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}

# The 11 rules the earlier (flawed) audit downgraded, with what it changed.
DOWNGRADED = {
    "r10": ("A", "B"), "r13": ("A", "B"),
    "r03": ("B", "C"), "r08": ("B", "C"), "r09": ("B", "C"),
    "r12": ("B", "C"), "r14": ("B", "C"), "r16": ("B", "C"),
    "r18": ("B", "C"), "r20": ("B", "C"), "r21": ("B", "C"),
}


def text_of(c: dict) -> str:
    return " ".join(str(c.get(k, "")) for k in
                    ("title", "text", "tags")).lower()


def mentions(haystack: str, term: str) -> bool:
    """Word-boundary match, not substring.

    The first version of this script used `term in text`, which matched "lead"
    inside "leading cause" and turned 56 genuine lead chunks into 182. That is
    the exact failure the docstring warns about -- a loose matcher manufacturing
    support -- and it was present in the script that warns about it. A hyphen or
    a space inside the term is allowed to match either character so that
    "pm2.5" also matches "pm2 5".
    """
    pat = r"\b" + re.escape(term).replace(r"\ ", r"[\s\-]").replace("-", r"[\s\-]") + r"\b"
    return re.search(pat, haystack, re.I) is not None


def main() -> int:
    from huiyan_agent.risk_rules import load_rules
    rules = load_rules()
    corpus = [json.loads(l) for l in
              (ROOT / "data" / "seed" / "evidence_chunks.jsonl")
              .open(encoding="utf-8") if l.strip()]
    print(f"corpus: {len(corpus)} chunks "
          f"(linked_rules present on "
          f"{sum(1 for c in corpus if c.get('linked_rules'))})")
    print()

    # Guideline (A) chunks specifically -- these are what the earlier audit missed.
    guide = [c for c in corpus if c.get("evidence_level") == "A"]
    print(f"grade-A chunks in corpus: {len(guide)}, of which "
          f"{sum(1 for c in guide if not c.get('linked_rules'))} have no "
          f"linked_rules")
    print()

    # Flag -> the words a human would use for it. Kept small and explicit: a
    # loose term list would over-match and manufacture support, which is the
    # failure mode this script exists to correct.
    WORDS = {
        "smoking": ["smok", "cigarette", "tobacco"],
        "bmi": ["body mass", "obes", "bmi"],
        "cataract": ["cataract", "lens opacity"],
        "amd": ["macular degeneration", "amd"],
        "amd_late": ["advanced amd", "neovascular", "late amd"],
        "amd_early": ["early amd", "drusen"],
        "glaucoma": ["glaucoma", "intraocular pressure", "iop"],
        "retinopathy": ["retinopathy"],
        "vision": ["visual impairment", "vision impairment", "visual acuity"],
        "pm25": ["pm2.5", "pm25", "particulate matter", "air pollution"],
        "diabetes": ["diabet", "glyc", "hba1c"],
        "alcohol": ["alcohol"],
        "lead": ["lead"],
        "uv": ["ultraviolet", "sun exposure", "uv"],
        "dyslipidemia": ["lipid", "cholesterol"],
        "vitamin": ["vitamin d"],
        "crp": ["c-reactive protein", "crp"],
        "diet": ["diet", "mediterranean"],
        "uric": ["uric acid"],
        "antioxidant": ["antioxidant", "carotenoid"],
    }

    def words_for(flags: list[str]) -> list[str]:
        out = []
        for f in flags:
            key = f.lower()
            for stem, ws in WORDS.items():
                if stem in key or key.startswith(stem):
                    out.extend(ws)
        return sorted(set(out))

    rows, reverts = [], []
    print(f"{'rule':34s} {'now':>4s} {'corpus A?':>10s} {'best':>5s}  verdict")
    print("-" * 84)
    for r in rules:
        short = r.id.split("_")[0]
        w = words_for(list(r.entity_a_flags) + list(r.entity_b_flags))
        if not w:
            rows.append({"rule": r.id, "declared_now": r.evidence_level,
                         "term_list": [], "best_grade": None,
                         "verdict": "no term mapping -- not assessed"})
            print(f"{r.id:34s} {r.evidence_level:>4s} {'?':>10s} {'-':>5s}  "
                  f"no term mapping")
            continue
        # a chunk counts if it mentions an exposure term AND an outcome term
        exp = [t for f in r.entity_a_flags for t in words_for([f])]
        outc = [t for f in r.entity_b_flags for t in words_for([f])]
        hits = [c for c in corpus
                if any(mentions(text_of(c), t) for t in (exp or w))
                and any(mentions(text_of(c), t) for t in (outc or w))]
        A_hits = [c for c in hits if c.get("evidence_level") == "A"]
        best = None
        for c in hits:
            g = c.get("evidence_level")
            if g and (best is None or ORD.get(g, 0) > ORD.get(best, 0)):
                best = g
        verdict = "ok"
        if short in DOWNGRADED:
            was, now = DOWNGRADED[short]
            if A_hits:
                verdict = f"REVERT: corpus has {len(A_hits)} grade-A chunk(s)"
                reverts.append({"rule": r.id, "changed": f"{was}->{now}",
                                "restore_to": was, "n_grade_A": len(A_hits),
                                "example": str(A_hits[0].get("title"))})
            else:
                verdict = "downgrade stands (no grade-A chunk found)"
        rows.append({"rule": r.id, "declared_now": r.evidence_level,
                     "n_hits": len(hits), "n_grade_A": len(A_hits),
                     "best_grade": best, "verdict": verdict,
                     "example_A": str(A_hits[0].get("title")) if A_hits else None})
        print(f"{r.id:34s} {r.evidence_level:>4s} {len(A_hits):>10d} "
              f"{str(best):>5s}  {verdict}")

    print()
    print("=" * 84)
    print(f"  downgraded rules examined : {len(DOWNGRADED)}")
    print(f"  REVERT (corpus has grade-A): {len(reverts)}")
    for v in reverts:
        print(f"    {v['rule']:34s} {v['changed']}  restore {v['restore_to']}"
              f"  <- {v['example'][:44]}")
    stands = [r for r in rows if str(r.get("verdict", "")).startswith("downgrade stands")]
    print(f"  downgrade stands           : {len(stands)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"corpus": len(corpus),
                               "grade_A_chunks": len(guide),
                               "grade_A_without_links":
                                   sum(1 for c in guide if not c.get("linked_rules")),
                               "per_rule": rows, "reverts": reverts},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
