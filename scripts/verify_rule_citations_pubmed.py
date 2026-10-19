#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resolve the eight unverifiable cases through PubMed, which carries abstracts.

Crossref held no abstract for 8 of the 10 flagged rules, so the title-only
downgrade could be neither confirmed nor withdrawn. PubMed usually has the
abstract, and the project already has an NCBI key configured, so this resolves
each DOI to a PMID, fetches the abstract, and looks for review methodology.

The point is to stop reporting a title heuristic as a finding. Whatever this
returns, the number of rules actually shown to be over-graded is what gets
reported -- which may well be fewer than ten, and may be two.

Run: python scripts/verify_rule_citations_pubmed.py
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CROSS = ROOT / "outputs" / "agent" / "rule_citation_verification.json"
OUT = ROOT / "outputs" / "agent" / "rule_citation_pubmed.json"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

REVIEW_RE = re.compile(
    r"meta-analy|meta analy|systematic review|pooled (analysis|estimate|effect)|"
    r"we searched|were searched|PRISMA|random[- ]effects model|"
    r"studies were included|literature search", re.I)


def api_key() -> str:
    """Read the NCBI key without printing it."""
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("NCBI_API_KEY"):
            return line.split("=", 1)[1].strip()
    return ""


def get(url: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": "huiyan/1.0"}), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def main() -> int:
    key = api_key()
    tail = f"&api_key={key}" if key else ""
    d = json.loads(CROSS.read_text(encoding="utf-8"))
    targets = [r for r in d["per_rule"] if r.get("over_graded")]
    print(f"resolving {len(targets)} flagged rules through PubMed"
          f"{' (with API key)' if key else ' (no API key)'}")
    print()
    out = []
    for r in targets:
        doi = r["doi"]
        q = urllib.parse.quote(f'{doi}[DOI]')
        try:
            sr = get(f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json"
                     f"&term={q}{tail}")
            ids = json.loads(sr)["esearchresult"].get("idlist") or []
        except Exception as e:
            ids = []
        time.sleep(0.4)
        if not ids:
            out.append({**r, "pmid": None, "pm_verdict": "no PubMed record"})
            print(f"  {r['rule'][:34]:34s} no PubMed record for the DOI")
            continue
        pmid = ids[0]
        try:
            fr = get(f"{EUTILS}/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml{tail}")
        except Exception:
            fr = ""
        time.sleep(0.4)
        ab = " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>",
                                 fr, re.S))
        ab = re.sub(r"<[^>]+>", " ", ab)
        ab = re.sub(r"\s+", " ", ab).strip()
        ptypes = re.findall(r"<PublicationType[^>]*>(.*?)</PublicationType>", fr)
        is_review = bool(REVIEW_RE.search(ab))
        typed_meta = any(re.search(r"Meta-Analysis|Systematic Review", p, re.I)
                         for p in ptypes)
        typed_guide = any(re.search(r"Guideline|Practice Guideline|Consensus",
                                    p, re.I) for p in ptypes)
        if typed_guide:
            verdict, why = "supports_declared", f"PubMed type says guideline ({ptypes})"
        elif typed_meta or is_review:
            verdict, why = "supports_declared", \
                f"PubMed type={ptypes} or abstract shows review methodology"
        else:
            verdict, why = "still_questionable", \
                f"PubMed type={ptypes}, abstract shows no review methodology"
        out.append({**r, "pmid": pmid, "pubmed_types": ptypes,
                    "abstract_len": len(ab), "abstract_head": ab[:400],
                    "pm_verdict": verdict, "pm_why": why})
        print(f"  {r['rule'][:34]:34s} PMID {pmid}  types={ptypes}  "
              f"ab={len(ab):>5d}  -> {verdict}")

    cleared = [x for x in out if x.get("pm_verdict") == "supports_declared"]
    stands = [x for x in out if x.get("pm_verdict") == "still_questionable"]
    unknown = [x for x in out if x.get("pm_verdict") not in
               ("supports_declared", "still_questionable")]
    print()
    print("=" * 96)
    print(f"  downgrade WITHDRAWN (PubMed supports the declared grade): {len(cleared)}")
    for x in cleared:
        print(f"    {x['rule'][:32]:32s} {x['pm_why'][:74]}")
    print(f"  downgrade STANDS   (no review evidence found)          : {len(stands)}")
    for x in stands:
        print(f"    {x['rule'][:32]:32s} {x['cited_title'][:56]}")
    print(f"  still unresolved                                       : {len(unknown)}")
    for x in unknown:
        print(f"    {x['rule'][:32]:32s} {x['pm_verdict']}")

    OUT.write_text(json.dumps({"per_rule": out, "withdrawn": cleared,
                               "standing": stands, "unresolved": unknown},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
