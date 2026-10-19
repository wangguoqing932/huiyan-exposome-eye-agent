#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify every rule's cited DOI against Crossref, and check the grade against it.

r11 was found to declare grade A while its citation resolves to a systematic
review and meta-analysis, which the project's own scheme grades B. One instance
does not tell us whether the rule base is systematically over-graded, so this
resolves all 21 rules' citations and compares the publication type against the
declared grade.

The classifier reads the title and the Crossref type, and is deliberately
conservative: it only downgrades a rule when the evidence of a lower tier is
unambiguous (a meta-analysis title for an A-declared rule, an original-research
article for an A- or B-declared rule). Anything it cannot classify is reported as
unclassified rather than guessed at, because a wrong downgrade is as damaging as
a missed one.

Grade scheme (configs/rules.yaml discipline):
  A = regulatory label / guideline      -> severity high
  B = meta-analysis / systematic review -> severity medium
  C = original research                 -> severity low

Run: python scripts/verify_rule_citations.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "rule_citation_verification.json"
UA = {"User-Agent": "huiyan-citation-verifier/1.0 (mailto:research@example.org)"}

META_RE = re.compile(
    r"meta-analysis|meta analysis|systematic review|pooled analysis|"
    r"umbrella review", re.I)
GUIDE_RE = re.compile(
    r"\bguideline|\bguidelines|consensus|recommendation|position statement|"
    r"practice parameter|criteria for", re.I)


def crossref(doi: str) -> dict | None:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=45) as r:
            return json.loads(r.read().decode("utf-8", "replace"))["message"]
    except Exception:
        return None


def classify(m: dict) -> tuple[str, str]:
    title = (m.get("title") or [""])[0]
    ctype = str(m.get("type", ""))
    if ctype in ("dataset", "posted-content", "component"):
        return "other", f"crossref type={ctype}"
    if GUIDE_RE.search(title):
        return "A", "title reads as guideline/consensus"
    if META_RE.search(title):
        return "B", "title reads as meta-analysis / systematic review"
    if ctype == "journal-article":
        return "C", "journal article, not a review by title"
    return "?", f"unclassified (type={ctype})"


def main() -> int:
    from huiyan_agent.risk_rules import load_rules
    rules = load_rules()
    ORD = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "?": 0}

    rows, over, unclassified, unresolved = [], [], [], []
    print(f"{'rule':36s} {'decl':>4s} {'sev':>7s} {'implied':>7s}  cited title")
    print("-" * 112)
    for r in rules:
        cites = r.citations or []
        doi = None
        for c in cites:
            ref = c.get("ref") if isinstance(c, dict) else str(c)
            m = re.search(r"10\.\d{4,9}/[^\s\"']+", str(ref))
            if m:
                doi = m.group(0).rstrip(".,;)")
                break
        if not doi:
            rows.append({"rule": r.id, "declared": r.evidence_level,
                         "severity": r.severity, "doi": None,
                         "verdict": "no DOI in citations"})
            unresolved.append(r.id)
            print(f"{r.id:36s} {r.evidence_level:>4s} {r.severity:>7s} "
                  f"{'-':>7s}  (no DOI)")
            continue
        m = crossref(doi)
        time.sleep(0.4)
        if m is None:
            rows.append({"rule": r.id, "declared": r.evidence_level,
                         "severity": r.severity, "doi": doi,
                         "verdict": "DOI did not resolve"})
            unresolved.append(r.id)
            print(f"{r.id:36s} {r.evidence_level:>4s} {r.severity:>7s} "
                  f"{'-':>7s}  UNRESOLVED {doi}")
            continue
        implied, why = classify(m)
        title = (m.get("title") or ["?"])[0]
        flag = ""
        if implied != "?" and ORD[implied] < ORD[r.evidence_level]:
            flag = "   <-- OVER-GRADED"
            over.append({"rule": r.id, "declared": r.evidence_level,
                         "severity": r.severity, "implied_by_citation": implied,
                         "why": why, "doi": doi, "title": title})
        elif implied == "?":
            unclassified.append({"rule": r.id, "why": why, "doi": doi,
                                 "title": title})
        rows.append({"rule": r.id, "declared": r.evidence_level,
                     "severity": r.severity, "doi": doi,
                     "cited_title": title, "journal": (m.get("container-title") or [""])[0],
                     "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                     "crossref_type": m.get("type"),
                     "cited_by": m.get("is-referenced-by-count"),
                     "implied_grade": implied, "classifier": why,
                     "over_graded": bool(flag)})
        print(f"{r.id:36s} {r.evidence_level:>4s} {r.severity:>7s} "
              f"{implied:>7s}  {title[:52]}{flag}")

    print()
    print("=" * 112)
    print(f"  citations resolved       : {len(rows) - len(unresolved)} of {len(rules)}")
    print(f"  OVER-GRADED rules        : {len(over)}")
    for o in over:
        print(f"    {o['rule']:34s} declares {o['declared']}/{o['severity']}, "
              f"citation implies {o['implied_by_citation']}  ({o['why']})")
    print(f"  unclassified by title    : {len(unclassified)}")
    for u in unclassified:
        print(f"    {u['rule']:34s} {u['why']}  {u['title'][:44]}")
    print(f"  unresolved / no DOI      : {len(unresolved)} {unresolved}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "method": "each rule's first cited DOI resolved via Crossref; title and "
                  "type compared against the project's grade scheme",
        "caution": "title-based classification; unclassified reported, not guessed",
        "per_rule": rows, "over_graded": over, "unclassified": unclassified,
        "unresolved": unresolved}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
