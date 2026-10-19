#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check the questionable downgrades against the citations' own abstracts.

The title classifier flagged nine rules as "declares B, implies C" purely because
their titles do not contain meta-analysis wording. A meta-analysis can easily
have such a title, so the flag is a hypothesis, not a finding. This fetches each
cited work's abstract and looks for review language, which is a far better signal
than the title.

Run: python scripts/verify_rule_citation_abstracts.py
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs" / "agent" / "rule_citation_verification.json"
OUT = ROOT / "outputs" / "agent" / "rule_citation_abstracts.json"
UA = {"User-Agent": "huiyan-verify/1.0 (mailto:research@example.org)"}

REVIEW_RE = re.compile(
    r"meta-analy|meta analy|systematic review|pooled (analysis|estimate|effect)|"
    r"we (searched|identified|included).{0,80}(databases|studies)|PRISMA|"
    r"random[- ]effects model|heterogeneity", re.I)
GUIDE_RE = re.compile(r"\bguideline|consensus|recommendation|position statement",
                      re.I)


def fetch(doi: str) -> dict | None:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                    timeout=45) as r:
            return json.loads(r.read().decode("utf-8", "replace"))["message"]
    except Exception:
        return None


def main() -> int:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    targets = [r for r in d["per_rule"] if r.get("over_graded")]
    print(f"inspecting {len(targets)} flagged rules against their abstracts")
    print()
    results = []
    for r in targets:
        doi = r["doi"]
        m = fetch(doi)
        time.sleep(0.4)
        if m is None:
            results.append({**r, "abstract_verdict": "unfetchable"})
            print(f"  {r['rule'][:34]:34s} abstract unfetchable")
            continue
        ab = re.sub(r"<[^>]+>", " ", m.get("abstract") or "")
        ab = re.sub(r"\s+", " ", ab).strip()
        is_review = bool(REVIEW_RE.search(ab))
        is_guide = bool(GUIDE_RE.search(ab))
        if not ab:
            verdict, why = "no_abstract", "Crossref carries no abstract"
        elif is_guide and r["declared"] in ("A", "B"):
            verdict, why = "supports_declared", "abstract reads as guideline"
        elif is_review:
            verdict, why = "supports_declared", \
                "abstract contains review/meta methodology language"
        else:
            verdict, why = "still_questionable", \
                "abstract shows no review methodology"
        results.append({**r, "abstract_len": len(ab),
                        "abstract_head": ab[:400],
                        "abstract_verdict": verdict, "abstract_why": why})
        print(f"  {r['rule'][:34]:34s} declared {r['declared']}  "
              f"abstract={len(ab):>5d}ch  review_lang={is_review}  -> {verdict}")

    still = [x for x in results if x.get("abstract_verdict") == "still_questionable"]
    cleared = [x for x in results if x.get("abstract_verdict") == "supports_declared"]
    print()
    print("=" * 96)
    print(f"  downgrade WITHDRAWN (abstract supports the declared grade): {len(cleared)}")
    for x in cleared:
        print(f"    {x['rule'][:32]:32s} {x['abstract_why']}")
    print(f"  downgrade STANDS (abstract shows no review methodology)   : {len(still)}")
    for x in still:
        print(f"    {x['rule'][:32]:32s} {x['cited_title'][:56]}")

    OUT.write_text(json.dumps({
        "why": "title-only downgrades re-checked against the citations' abstracts",
        "withdrawn": cleared, "standing": still, "all": results},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
