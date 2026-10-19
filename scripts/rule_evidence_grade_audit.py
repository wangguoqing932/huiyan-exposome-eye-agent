#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Are the 21 rules supported at the grade they declare?

The corpus has 1060 chunks, but only 101 carry `linked_rules` -- those are the
rule citations. The rest are landscape probes (491) and guideline background.
So "the evidence base is four times its target" describes the landscape corpus,
not rule support, and the two must not be conflated.

This asks the question that matters: for each rule, what grades are the chunks
that the corpus itself links to it, and does the best of them reach the grade the
rule declares? A rule graded B whose linked chunks are all D/E is a rule whose
stated confidence the corpus does not carry.

Run: python scripts/rule_evidence_grade_audit.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "rule_evidence_grade_audit.json"
ORD = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}


def main() -> int:
    from huiyan_agent.risk_rules import load_rules

    rules = load_rules()
    rows = [json.loads(l) for l in
            (ROOT / "data" / "seed" / "evidence_chunks.jsonl")
            .open(encoding="utf-8") if l.strip()]
    linked = [c for c in rows if c.get("linked_rules")]

    print(f"corpus: {len(rows)} chunks, of which {len(linked)} carry linked_rules")
    print(f"  landscape/background (not rule support): {len(rows) - len(linked)}")
    print(f"  grade mix of the RULE-SUPPORTING chunks: "
          f"{dict(sorted(Counter(c['evidence_level'] for c in linked).items(), key=lambda x: -ORD.get(x[0],0)))}")
    print()

    # rule id -> chunks linked to it
    by_rule: dict[str, list] = {}
    for c in linked:
        v = c["linked_rules"]
        for rid in (v if isinstance(v, list) else [v]):
            key = str(rid).strip()
            # linked ids are short forms like "r02"; match against the full id
            by_rule.setdefault(key, []).append(c)

    short: dict[str, str] = {}
    for r in rules:
        short[r.id.split("_")[0]] = r.id

    def grade_of(rid_short: str) -> Counter:
        return Counter(c["evidence_level"] for c in by_rule.get(rid_short, []))

    print(f"{'rule':38s} {'decl':>5s} {'n':>3s}  best  linked grade mix")
    print("-" * 92)
    report, weak, short_of = [], [], []
    for r in rules:
        s = r.id.split("_")[0]
        mix = grade_of(s)
        n = sum(mix.values())
        best = max(mix, key=lambda g: ORD.get(g, 0)) if mix else None
        mix_s = " ".join(f"{g}:{m}" for g, m in sorted(mix.items(), key=lambda x: -ORD.get(x[0], 0)))
        print(f"{r.id:38s} {r.evidence_level:>5s} {n:>3d}  {str(best):>4s}  {mix_s}")
        report.append({"rule": r.id, "declared": r.evidence_level, "n_linked": n,
                       "best_linked_grade": best, "mix": dict(mix)})
        if n == 0:
            short_of.append(r.id)
        elif ORD.get(best, 0) < ORD.get(r.evidence_level, 0):
            weak.append({"rule": r.id, "declared": r.evidence_level, "best": best,
                         "n": n, "mix": dict(mix)})

    print()
    print("=" * 92)
    print(f"rules with NO linked chunk                     : {len(short_of)} {short_of}")
    print(f"rules whose best linked grade < declared grade : {len(weak)}")
    for w in weak:
        print(f"  {w['rule']:38s} declares {w['declared']}, best linked is "
              f"{w['best']} (n={w['n']}, mix={w['mix']})")

    dist = Counter(r["declared"] for r in report)
    print()
    print(f"declared grade distribution: {dict(sorted(dist.items()))}")
    e_only = [r["rule"] for r in report
              if r["n_linked"] and ORD.get(r["best_linked_grade"], 9) <= 2]
    print(f"rules whose BEST linked evidence is D or E: {len(e_only)}")
    for x in e_only:
        print(f"  {x}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "corpus_total": len(rows), "rule_supporting_chunks": len(linked),
        "rule_supporting_grade_mix": dict(Counter(c["evidence_level"] for c in linked)),
        "per_rule": report, "rules_without_linked_chunk": short_of,
        "rules_below_declared_grade": weak,
        "rules_best_is_D_or_E": e_only}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
