#!/usr/bin/env python
"""Extend the verified citation pool with 7_6 (Introduction) references.

Same rules as scripts/build_citation_pool.py: live API only (Rule 1), DOI
cross-confirmed in Crossref + OpenAlex (Rule 3), retraction flag (Rule 4),
clickable URL (Rule 5), and no finding asserted where the abstract was not
retrieved (Rule 6).

Matching is deliberately strict -- exact expected title, token overlap >= 0.72
AND year within +-2. Both guards are needed: the overlap test alone admitted a
2024 Korean-journal reprint of STROBE as if it were the 2007 statement, and
loose substring matching admitted a Nutrients paper as the CRELES cohort
profile.

Run: python scripts/extend_citation_pool_intro.py
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_citation_pool import RAW, fetch, openalex, similarity  # noqa: E402

OUT = ROOT / "outputs" / "paper" / "citation_pool.json"
UA = "huiyan-citation-verifier/1.0 (mailto:research@example.org)"

CLAIMS = [
    ("C016", "Global burden of blindness and vision impairment in ageing populations",
     "Trends in prevalence of blindness and distance and near vision impairment over 30 years",
     "Trends in prevalence of blindness and distance and near vision impairment over 30 years", 2021),
    ("C017", "Cataract as a leading cause of blindness and vision impairment",
     "Cataract and visual impairment global burden",
     "Global prevalence of cataract", 2021),
    ("C018", "Smoking as a risk factor for age-related cataract",
     "Smoking and risk of age-related cataract: a meta-analysis",
     "Smoking and risk of age-related cataract: a meta-analysis", 2012),
    ("C019", "Diabetes as a risk factor for cataract",
     "Diabetes mellitus and risk of cataract: a systematic review and meta-analysis",
     "Diabetes mellitus and risk of cataract", 2019),
    ("C020", "The exposome concept: complementing the genome with exposure",
     "Complementing the genome with an exposome: the outstanding challenge of environmental exposure measurement in molecular epidemiology",
     "Complementing the genome with an exposome", 2005),
    ("C021", "Age-related macular degeneration: prevalence and burden",
     "Global prevalence of age-related macular degeneration and disease burden projection",
     "Global prevalence of age-related macular degeneration", 2014),
    ("C022", "Diabetic retinopathy: global prevalence",
     "Global prevalence of diabetic retinopathy and projection of burden through 2045",
     "Global prevalence of diabetic retinopathy", 2021),
    ("C023", "Glaucoma: global prevalence and burden",
     "Global prevalence of glaucoma and projections of glaucoma burden through 2040",
     "Global prevalence of glaucoma", 2014),
    ("C024", "External validation and transportability of clinical prediction models",
     "External validation of clinical prediction models: a systematic review",
     "External validation of clinical prediction models", 2020),
    ("C025", "Explainability requirements for clinical decision support systems",
     "Explainable artificial intelligence in clinical decision support",
     "Explainable artificial intelligence", 2020),
]


def crossref(query: str) -> dict | None:
    q = urllib.parse.quote(query)
    url = (f"https://api.crossref.org/works?query.bibliographic={q}&rows=10"
           f"&select=DOI,title,container-title,issued,author,type,update-to"
           f"&mailto=research@example.org")
    return fetch(url, RAW / f"intro_{abs(hash(query)) % 10**10}.json")


def main() -> int:
    pool = json.loads(OUT.read_text(encoding="utf-8"))
    have = {e["pool_id"] for e in pool["entries"]}
    REJECT = {"dataset", "thesis", "dissertation", "posted-content",
              "component", "peer-review", "report"}
    added, failed = 0, []

    for pid, claim, query, must, year in CLAIMS:
        if pid in have:
            continue
        print(f"  {pid}")
        cr = crossref(query)
        item = None
        if cr:
            for it in cr.get("message", {}).get("items", []):
                ty = (it.get("type") or "").lower()
                if ty in REJECT:
                    continue
                t = " ".join(it.get("title") or [])
                iy = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
                if similarity(must, t) >= 0.72 and iy and abs(int(iy) - year) <= 2:
                    item = it
                    break
        if not item:
            failed.append(pid)
            print("    -> NOT FOUND (recorded; will not be cited)")
            continue
        doi = item["DOI"]
        oa = openalex(doi)
        oa_ok = bool(oa and doi.lower() in str(oa.get("doi", "")).lower())
        retr = any((u or {}).get("type") == "retraction"
                   for u in (item.get("update-to") or []))
        if oa:
            retr = retr or bool(oa.get("is_retracted"))
        pool["entries"].append({
            "pool_id": pid, "doi": doi,
            "title": " ".join(item.get("title") or []),
            "year": (item.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "journal": " ".join(item.get("container-title") or []),
            "url": f"https://doi.org/{doi}",
            "verification_status": ("cross_verified" if oa_ok
                                    else "single_source_crossref"),
            "verified_in": (["crossref", "openalex"] if oa_ok else ["crossref"]),
            "retraction_flag": retr, "retraction_checked_on": str(date.today()),
            "abstract_retrieved": False,
            "metadata_only_note": "abstract not retrieved; no finding asserted",
            "used_in_sections": ["introduction"],
            "claim_supported": claim, "added_at_phase": "7_6"})
        added += 1
        print(f"    -> {doi} | "
              f"{'cross_verified' if oa_ok else 'SINGLE'}"
              f"{' | RETRACTED' if retr else ''}")

    pool["entries"].sort(key=lambda e: e["pool_id"])
    pool["n_entries"] = len(pool["entries"])
    if failed:
        prev = pool.setdefault("failed_claims", [])
        pool["failed_claims"] = sorted(set(prev) | set(failed))
    OUT.write_text(json.dumps(pool, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\nadded {added}  failed {failed}  total {pool['n_entries']}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
