#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Search for genuine guideline-level citations for r10 and r13.

The rule base's own scheme reserves grade A for regulatory labels and clinical
guidelines. Verification found no rule whose citation is a guideline: every one
is a meta-analysis (at most B) or original research (C). The two rules currently
declaring A -- r10 (smoking -> cataract) and r13 (BMI -> cataract) -- cite
meta-analyses, so their A is not supported by what they cite.

Two ways out: downgrade them to B and accept that the A tier is empty, or find
the guideline evidence their A claims. This searches for the latter. If genuine
guidelines exist, A becomes real and the pre-registered direction_review
mechanism in evaluate.py keeps its subject matter. If none exists, the honest
conclusion is that A is not a tier this rule base occupies and the scheme should
say so.

Run: python scripts/find_guideline_citations.py
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "agent" / "guideline_search.json"
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "huiyan/1.0"}

QUERIES = {
    "r10_smoking_x_cataract": [
        'smoking cataract[Title] AND (guideline[Publication Type] OR '
        'practice guideline[Publication Type] OR consensus[Title])',
        '(cataract[Title]) AND (guideline[Publication Type])',
        'smoking AND (cataract OR lens opacity) AND (recommendation OR guideline)',
    ],
    "r13_bmi_x_cataract": [
        'obesity cataract[Title] AND (guideline[Publication Type] OR '
        'consensus[Title])',
        '(cataract[Title]) AND (risk factor[Title]) AND guideline[Publication Type]',
        'body mass index AND cataract AND (guideline OR recommendation)',
    ],
}


def key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("NCBI_API_KEY"):
            return line.split("=", 1)[1].strip()
    return ""


def get(url: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    k = key()
    tail = f"&api_key={k}" if k else ""
    print("searching for guideline-level evidence")
    print()
    found = {}
    for rule, queries in QUERIES.items():
        print(f"=== {rule} ===")
        hits, seen = [], set()
        for q in queries:
            url = (f"{E}/esearch.fcgi?db=pubmed&retmode=json&retmax=8"
                   f"&term={urllib.parse.quote(q)}{tail}")
            try:
                ids = json.loads(get(url))["esearchresult"].get("idlist") or []
            except Exception:
                ids = []
            time.sleep(0.4)
            if not ids:
                print(f"  (no hits) {q[:70]}")
                continue
            fr = get(f"{E}/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml{tail}")
            time.sleep(0.4)
            arts = re.findall(r"<PubmedArticle>.*?</PubmedArticle>", fr, re.S)
            for a in arts:
                pmid = re.search(r"<PMID[^>]*>(\d+)</PMID>", a)
                title = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", a, re.S)
                jrn = re.search(r"<Title>(.*?)</Title>", a, re.S)
                ptypes = re.findall(r"<PublicationType[^>]*>(.*?)</PublicationType>", a)
                pmid = pmid.group(1) if pmid else "?"
                title = re.sub(r"<[^>]+>", "", title.group(1)) if title else "?"
                if pmid in seen:
                    continue
                seen.add(pmid)
                is_guide = any(re.search(r"Guideline|Consensus|Recommendation",
                                         p, re.I) for p in ptypes)
                hits.append({"pmid": pmid, "title": title[:150],
                             "journal": (jrn.group(1) if jrn else "")[:70],
                             "types": ptypes, "guideline_type": is_guide})
                mark = "GUIDELINE" if is_guide else "        "
                print(f"  {mark}  PMID {pmid:>9s}  {title[:74]}")
        found[rule] = hits
        guides = [h for h in hits if h["guideline_type"]]
        print(f"  -> guideline-typed hits: {len(guides)} of {len(hits)}")
        print()

    total_guides = sum(len([h for h in v if h["guideline_type"]])
                       for v in found.values())
    print("=" * 90)
    if total_guides:
        print(f"  guideline-typed records found: {total_guides}")
        print("  => grade A CAN be substantiated for these rules; r10/r13 should")
        print("     cite the guideline rather than the meta-analysis.")
    else:
        print("  guideline-typed records found: 0")
        print("  => no guideline evidence located. Grade A is not a tier this")
        print("     rule base actually occupies, and r10/r13 should be regraded")
        print("     B, with the scheme amended to say A is reserved and unused.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"queries": QUERIES, "results": found,
                               "guideline_hits": total_guides},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
