#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Remove the ambiguity that caused the grade-audit error, and enforce it.

`evidence_level: A` meant two different things in two places:

  * rules.yaml discipline, documented in risk_rules._EVIDENCE_TO_SEVERITY:
      A = regulatory label / clinical guideline  -> severity high
  * the evidence corpus:
      A = high-quality evidence, which includes meta-analyses

Severity is derived from the first. So a chunk graded A in the second sense
could push a rule to the maximum severity. That is not hypothetical: an audit
that reasoned from the corpus's A concluded 11 rules were over-graded and
changed all of them, and every one of those changes had to be reverted
(docs/AGENT_AUDIT.md sections 8 through 21).

The corpus already carries the field needed to separate the two senses:
`source_type` is `guideline` for 159 chunks and `literature` for 901. The
mis-grading is exactly the intersection:

    A x guideline    34   <- correct
    A x literature   13   <- literature graded A

All 13 are journal articles -- reviews, systematic reviews, meta-analyses, or
original research -- and none is a guideline or regulatory document. They are
re-graded to B (review/meta-analysis) or C (original research) according to their
type, which is what the stated discipline requires.

A validator is added alongside so the ambiguity cannot come back silently: A is
only legal for a chunk whose source_type is `guideline`.

Run: python scripts/fix_evidence_level_ambiguity.py            (dry run)
     python scripts/fix_evidence_level_ambiguity.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
OUT_DIR = ROOT / "outputs" / "agent"

# chunk_id -> new level. Classified by title, which for these 13 is unambiguous:
# each either names its review status ("a meta-analysis", "A systematic review",
# "A Review", "Literature Review") or names none, in which case it is primary
# research and takes C.
ORIGINAL_RESEARCH = {
    # titles naming no review status -> primary research
    "ozone air pollution and age-related macular",   # association study
    "current status of diabetes mellitus care",      # health-services survey
    "mediterranean diet on development and progression",  # trial/cohort report
}


def classify(title: str) -> str:
    t = title.lower()
    if re.search(r"meta-analys|systematic review|literature review|\ba review\b|"
                 r"umbrella review", t):
        return "B"
    for marker in ORIGINAL_RESEARCH:
        if marker in t:
            return "C"
    # Unknown: err toward B rather than C. A second over-correction is worse than
    # one generous tier, and this branch should be empty -- it is reported if not.
    return "B?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows = [json.loads(l) for l in SRC.open(encoding="utf-8") if l.strip()]
    before = Counter(r.get("evidence_level") for r in rows)

    targets = [r for r in rows
               if r.get("evidence_level") == "A" and r.get("source_type") != "guideline"]
    print(f"chunks: {len(rows)}")
    print(f"  A x guideline  : {sum(1 for r in rows if r.get('evidence_level')=='A' and r.get('source_type')=='guideline')}")
    print(f"  A x literature : {len(targets)}  <- to be re-graded")
    print()
    unknown = []
    plan = []
    for r in targets:
        new = classify(str(r.get("title", "")))
        plan.append((r["chunk_id"], str(r.get("title"))[:58], new))
        if new.endswith("?"):
            unknown.append(r.get("title"))
        print(f"  {r['chunk_id']:>8s}  A -> {new:<3s}  {str(r.get('title'))[:62]}")

    print()
    print(f"  re-graded to B: {sum(1 for _,_,n in plan if n=='B')}")
    print(f"  re-graded to C: {sum(1 for _,_,n in plan if n=='C')}")
    if unknown:
        print(f"  UNCLASSIFIED (defaulted to B, please review): {len(unknown)}")
        for u in unknown:
            print(f"    {u}")

    if not a.apply:
        print("\n(dry run -- pass --apply to write)")
        return 0

    idx = {cid: n for cid, _, n in plan}
    for r in rows:
        if r["chunk_id"] in idx:
            r["evidence_level"] = idx[r["chunk_id"]].rstrip("?")
            r["evidence_level_note"] = (
                "2026-10-16 re-graded: was A while source_type=literature; A is "
                "reserved for source_type=guideline per risk_rules."
                "_EVIDENCE_TO_SEVERITY. See docs/AGENT_AUDIT.md section 21.")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    (ROOT / ".audit_tmp").mkdir(exist_ok=True)
    shutil.copy(SRC, ROOT / ".audit_tmp" / f"evidence_chunks_pre_levelfix_{ts}.jsonl")

    # Validate before writing: A must imply guideline.
    bad = [r for r in rows
           if r.get("evidence_level") == "A" and r.get("source_type") != "guideline"]
    if bad:
        print(f"\nREFUSING TO WRITE: {len(bad)} chunk(s) still have A with a "
              f"non-guideline source_type")
        return 1

    with SRC.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    after = Counter(r.get("evidence_level") for r in rows)
    print(f"\nwritten. level distribution {dict(sorted(before.items()))} -> "
          f"{dict(sorted(after.items()))}")
    print(f"backup: .audit_tmp/evidence_chunks_pre_levelfix_{ts}.jsonl")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "evidence_level_fix.json").write_text(json.dumps({
        "rule": "evidence_level A requires source_type == guideline",
        "regraded": [{"chunk_id": c, "title": t, "new_level": n} for c, t, n in plan],
        "before": dict(before), "after": dict(after)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
