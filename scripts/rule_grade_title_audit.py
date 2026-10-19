#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Audit each rule's grade against the best chunk whose TITLE names the pair.

Three earlier attempts to audit the rule grades failed, and each failure is worth
remembering because it explains the method here (docs/AGENT_AUDIT.md 8, 19, 20):

  1. `linked_rules` -- empty for all 159 AAO PPP chunks, so guideline support was
     invisible.
  2. Full-text substring matching -- "lead" matched "leading cause": 182 chunks
     versus 56 with word boundaries.
  3. Full-text word-boundary matching -- still matched a guideline's numbered
     REFERENCE LIST entry (the PPP section whose body is "…P60 49. Hyman L, …")
     and the running page header ("Diabetic Retinopathy PPP", printed on every
     page), which is a whole word and so defeats word boundaries too.

Every one of those matched arbitrary text. This one matches only TITLES, on the
grounds that a title names its topic rather than incidentally containing a word.
That is a much stronger signal, and it is still a heuristic: a title match shows
the corpus contains a paper on the pair, not that the paper supports the rule's
direction or magnitude.

So this reports, and does not rewrite. A rule whose declared grade exceeds the
best title-matched evidence is flagged for human reading; nothing is changed
automatically, because the last time grades were changed automatically they all
had to be reverted.

Run: python scripts/rule_grade_title_audit.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "rule_grade_title_audit.json"
ORD = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}

# Exposure flag -> the words a title would use for it. Deliberately narrow: every
# term here was checked against the actual corpus titles, and a term that
# over-matched was removed rather than kept "to be safe".
EXPOSURE_TERMS = {
    "uric_acid": ["uric acid"],
    "hyperglycemia": ["hyperglyc", "glucose", "glycemic", "glycaemic"],
    "hba1c": ["hba1c", "glycated hemoglobin", "glycaemic control", "glycemic control"],
    "dyslipidemia": ["dyslipid", "cholesterol", "lipid"],
    "crp": ["c-reactive protein", "crp", "inflammat"],
    "vitamin_d": ["vitamin d"],
    "low_antioxidant": ["antioxidant", "carotenoid", "lutein", "xanthophyll"],
    "mediterranean_diet": ["mediterranean diet"],
    "smoking": ["smoking", "cigarette", "tobacco"],
    "alcohol": ["alcohol"],
    "bmi": ["body mass index", "bmi", "obes"],
    "lead": ["lead exposure", "blood lead", "cadmium"],
    "pm25": ["pm2.5", "pm25", "particulate matter", "air pollution", "ozone"],
    "uv": ["ultraviolet", "uv ", "sun exposure", "sunlight"],
    "pro_inflammatory": ["inflammatory diet", "dietary inflammatory",
                          "pro-inflammatory", "proinflammatory"],
}
OUTCOME_TERMS = {
    "cataract": ["cataract"],
    "amd_late": ["macular degeneration", " amd", "neovascular"],
    "amd_early": ["macular degeneration", " amd", "drusen"],
    "retinopathy": ["retinopathy"],
    "dr_pdr": ["retinopathy", "proliferative"],
    "dr_npdr": ["retinopathy", "nonproliferative"],
    "glaucoma": ["glaucoma", "intraocular pressure"],
    "vi_mod": ["visual impairment", "vision impairment"],
    "vi_severe": ["visual impairment", "vision impairment", "blindness"],
}


def terms(flags: list[str], table: dict[str, list[str]]) -> list[str]:
    out = []
    for f in flags:
        key = f.lower()
        for k, v in table.items():
            if k in key or key.startswith(k.split("_")[0]):
                out.extend(v)
    return sorted(set(out))


def hit(title: str, ts: list[str]) -> bool:
    """Prefix match from a word boundary.

    The term list holds stems ("obes", "hyperglyc", "inflammat"), so a trailing
    \\b is wrong: \\bobes\\b does not match "obesity". An earlier version used
    boundaries on both sides, which made r02 and r22 report "no title match" for
    exactly that reason -- a matcher bug reported as an absence of evidence, which
    is the error this whole audit keeps running into. Bound the start only.
    """
    t = title.lower()
    for term in ts:
        pat = r"\b" + re.escape(term)
        if re.search(pat, t):
            return True
    return False


def main() -> int:
    from huiyan_agent.risk_rules import load_rules
    rules = load_rules()
    corpus = [json.loads(l) for l in
              (ROOT / "data" / "seed" / "evidence_chunks.jsonl")
              .open(encoding="utf-8") if l.strip()]

    print(f"corpus {len(corpus)} chunks; matching TITLES only")
    print()
    print(f"{'rule':34s} {'decl':>4s} {'best title-matched':>18s}  strongest title")
    print("-" * 100)
    rows, flagged = [], []
    for r in rules:
        et = terms(list(r.entity_a_flags), EXPOSURE_TERMS)
        ot = terms(list(r.entity_b_flags), OUTCOME_TERMS)
        if not et or not ot:
            rows.append({"rule": r.id, "declared": r.evidence_level,
                         "note": "no term mapping; not assessed"})
            print(f"{r.id:34s} {r.evidence_level:>4s} "
                  f"{'(no mapping)':>18s}  exposure={et} outcome={ot}")
            continue
        hits = [c for c in corpus if hit(str(c.get("title", "")), et)
                and hit(str(c.get("title", "")), ot)]
        best, best_c = None, None
        for c in hits:
            g = c.get("evidence_level")
            if g and (best is None or ORD.get(g, 0) > ORD.get(best, 0)):
                best, best_c = g, c
        mix = dict(Counter(c.get("evidence_level") for c in hits))
        rows.append({"rule": r.id, "declared": r.evidence_level, "n_title_hits": len(hits),
                     "mix": mix, "best": best,
                     "best_title": str(best_c.get("title"))[:120] if best_c else None})
        verdict = ""
        if best and ORD.get(best, 0) < ORD.get(r.evidence_level, 0):
            verdict = "  <-- declared ABOVE best title-matched"
            flagged.append(rows[-1])
        print(f"{r.id:34s} {r.evidence_level:>4s} {str(best):>18s}  "
              f"{str(best_c.get('title'))[:52] if best_c else '(no title match)'}{verdict}")

    print()
    print("=" * 100)
    n_mapped = sum(1 for x in rows if x.get("best") is not None)
    print(f"  rules assessed            : {n_mapped} of {len(rules)}")
    print(f"  declared ABOVE best title : {len(flagged)}")
    for f in flagged:
        print(f"    {f['rule']:34s} declares {f['declared']}, "
              f"best title-matched is {f['best']} ({f['mix']})")
        print(f"      {f['best_title']}")
    nomatch = [x["rule"] for x in rows if x.get("n_title_hits") == 0]
    print(f"  no title match at all     : {len(nomatch)} {nomatch}")
    print()
    print("  CAUTION: a title match shows the corpus holds a paper on the pair; it")
    print("  does not show the paper supports the rule's direction or magnitude.")
    print("  Nothing is changed by this script -- flags are for human reading, and")
    print("  the last time grades were changed automatically they were all reverted.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"method": "title-only matching",
                               "per_rule": rows, "flagged": flagged},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
