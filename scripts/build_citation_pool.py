#!/usr/bin/env python
"""Build outputs/paper/citation_pool.json by live API verification (writer 7_5).

Follows the kuku-paper-lookup mandatory rules:
  * Rule 1 -- every entry comes from a live response received here; nothing is
    written from memory. A query that returns nothing is recorded as FAILED and
    the manuscript must not cite it.
  * Rule 3 -- each entry is cross-verified in Crossref AND OpenAlex, and the
    DOI must match across both.
  * Rule 4 -- each entry carries a retraction flag from Crossref `update-to`
    and OpenAlex `is_retracted`.
  * Rule 5 -- each entry carries a clickable URL.
  * Rule 6 -- `claim_supported` records only what the retrieved metadata
    supports; abstracts are not retrieved here, so no finding is asserted.

The claim list is enumerated first (reporting guidelines, statistical methods,
and the data sources this project actually used), because citing a source the
manuscript does not use is as wrong as missing one it does.

Run: python scripts/build_citation_pool.py
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "paper" / "citation_pool.json"
RAW = ROOT / "outputs" / "paper" / "citation_raw"
UA = "huiyan-citation-verifier/1.0 (mailto:research@example.org)"

# (pool_id, claim_supported, crossref query, title must contain, expected year)
def similarity(a: str, b: str) -> float:
    """Token-overlap (Jaccard-ish) between two titles, lowercased."""
    import re as _re
    ta = set(_re.findall(r"[a-z0-9]+", a.lower()))
    tb = set(_re.findall(r"[a-z0-9]+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


CLAIMS = [
    ("C001", "TRIPOD+AI reporting guideline for clinical prediction models",
     "TRIPOD+AI: an updated reporting guideline for clinical prediction models",
     "TRIPOD+AI: an updated reporting guideline for clinical prediction models", 2024),
    ("C002", "DECIDE-AI reporting guideline for early-stage clinical AI evaluation",
     "DECIDE-AI: new reporting guidelines to bridge the development-to-implementation gap in clinical artificial intelligence",
     "DECIDE-AI: new reporting guidelines to bridge the development-to-implementation gap in clinical artificial intelligence", 2022),
    ("C003", "STROBE reporting guideline for observational studies",
     "Strengthening the Reporting of Observational Studies in Epidemiology (STROBE): explanation and elaboration",
     "Strengthening the Reporting of Observational Studies in Epidemiology (STROBE): explanation and elaboration", 2007),
    ("C004", "Benjamini-Yekutieli procedure for controlling FDR under dependency",
     "The control of the false discovery rate in multiple testing under dependency",
     "The control of the false discovery rate in multiple testing under dependency", 2001),
    ("C005", "Clopper-Pearson exact binomial confidence interval",
     "The use of confidence or fiducial limits illustrated in the case of the binomial",
     "The use of confidence or fiducial limits illustrated in the case of the binomial", 1934),
    ("C006", "SHARE cohort: Survey of Health, Ageing and Retirement in Europe",
     "Data resource profile: the Survey of Health, Ageing and Retirement in Europe (SHARE)",
     "Data resource profile: the Survey of Health, Ageing and Retirement in Europe (SHARE)", 2013),
    ("C007", "HRS: Health and Retirement Study cohort profile",
     "Cohort profile: the Health and Retirement Study (HRS)",
     "Cohort profile: the Health and Retirement Study (HRS)", 2014),
    ("C008", "ELSA: English Longitudinal Study of Ageing cohort profile",
     "Cohort profile: the English Longitudinal Study of Ageing",
     "Cohort profile: the English Longitudinal Study of Ageing", 2013),
    ("C009", "LASI: Longitudinal Ageing Study in India cohort profile",
     "Cohort profile: the Longitudinal Ageing Study in India (LASI)",
     "Cohort profile: the Longitudinal Ageing Study in India (LASI)", 2022),
    ("C010", "MHAS: Mexican Health and Aging Study cohort profile",
     "Cohort profile: the Mexican Health and Aging Study (MHAS)",
     "Cohort profile: the Mexican Health and Aging Study (MHAS)", 2017),
    ("C011", "CLHLS: Chinese Longitudinal Healthy Longevity Survey cohort profile",
     "Cohort profile: the Chinese Longitudinal Healthy Longevity Survey",
     "Cohort profile: the Chinese Longitudinal Healthy Longevity Survey", 2017),
    ("C012", "CRELES: Costa Rican Study on Longevity and Healthy Ageing",
     "The Costa Rican Longevity and Healthy Aging Study (CRELES)",
     "The Costa Rican Longevity and Healthy Aging Study (CRELES)", 2013),
    ("C013", "CHARLS: China Health and Retirement Longitudinal Study cohort profile",
     "Cohort profile: the China Health and Retirement Longitudinal Study (CHARLS)",
     "Cohort profile: the China Health and Retirement Longitudinal Study (CHARLS)", 2014),
    ("C014", "KNHANES: Korea National Health and Nutrition Examination Survey",
     "Data resource profile: the Korea National Health and Nutrition Examination Survey (KNHANES)",
     "Data resource profile: the Korea National Health and Nutrition Examination Survey (KNHANES)", 2014),
    ("C015", "Multiple imputation and Rubin's combining rules",
     "Multiple Imputation for Nonresponse in Surveys",
     "Multiple Imputation for Nonresponse in Surveys", 1987),
]


def fetch(url: str, path: Path, _retry: bool = True) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read().decode("utf-8", "replace")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return json.loads(body)
    except urllib.error.HTTPError as e:
        if e.code == 429 and _retry:
            # Rule: on 429, wait briefly and retry EXACTLY once. A rate limit is
            # NOT evidence that a paper does not exist, so it must never be
            # recorded as a not-found result.
            print("    HTTP 429 -> waiting 8s and retrying once")
            time.sleep(8.0)
            return fetch(url, path, _retry=False)
        print(f"    FETCH FAIL {type(e).__name__}: {e}")
        return None
    except Exception as e:  # Rule 1: report, never fabricate
        print(f"    FETCH FAIL {type(e).__name__}: {e}")
        return None


def crossref(query: str) -> dict | None:
    q = urllib.parse.quote(query)
    url = (f"https://api.crossref.org/works?query.bibliographic={q}&rows=10"
           f"&select=DOI,title,container-title,issued,author,type,update-to"
           f"&mailto=research@example.org")
    return fetch(url, RAW / f"crossref_{abs(hash(query)) % 10**10}.json")


def openalex(doi: str) -> dict | None:
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
    return fetch(url, RAW / f"openalex_{doi.replace('/', '_')}.json")


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    entries, failed = [], []
    # Resumable: Crossref rate-limits hard, and a 429 is not a "not found".
    # Keep whatever is already cross-verified and only re-query the rest, so a
    # rerun makes progress instead of restarting from zero.
    prior = {}
    if OUT.exists():
        try:
            for e in json.loads(OUT.read_text(encoding="utf-8"))["entries"]:
                if e.get("verification_status") == "cross_verified":
                    prior[e["pool_id"]] = e
        except Exception:
            pass
    if prior:
        print(f"  resuming: {len(prior)} already cross-verified")
    REDO = {"C003", "C007", "C011", "C012"}
    for pid, claim, query, must, year in CLAIMS:
        if pid in prior and pid not in REDO:
            entries.append(prior[pid])
            continue
        print(f"  {pid}: {must}")
        cr = crossref(query)
        REJECT_TYPES = {"dataset", "thesis", "dissertation",
                        "posted-content", "component", "peer-review"}
        item = None
        if cr:
            for it in cr.get("message", {}).get("items", []):
                t = " ".join(it.get("title") or [])
                ty = (it.get("type") or "").lower()
                if ty in REJECT_TYPES:
                    print(f"    skip wrong type '{ty}': {t[:56]}")
                    continue
                # must is the EXPECTED TITLE; accept only a close match AND
                # a year within +-2 of the expected one. Title alone is not
                # enough: a 2024 Korean-journal reprint of STROBE has a nearly
                # identical title and would otherwise be cited as the 2007
                # statement.
                iy = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
                if similarity(must, t) >= 0.72 and iy and abs(int(iy) - year) <= 2:
                    item = it
                    break
                if must.lower() in t.lower():
                    print(f"    weak match rejected: {t[:60]}")
        if not item:
            failed.append(pid)
            print("    -> NOT FOUND in Crossref (recorded as FAILED)")
            time.sleep(4.0)
            continue
        doi = item.get("DOI", "")
        title = " ".join(item.get("title") or [])
        journal = " ".join(item.get("container-title") or [])
        yr = (item.get("issued", {}).get("date-parts") or [[None]])[0][0]
        authors = item.get("author") or []
        first = (f"{authors[0].get('family', '')} "
                 f"{authors[0].get('given', '')}").strip() if authors else ""
        retr = any((u or {}).get("type") == "retraction"
                   for u in (item.get("update-to") or []))

        oa = openalex(doi) if doi else None
        oa_ok = bool(oa and oa.get("doi", "").lower().endswith(doi.lower()))
        if oa:
            retr = retr or bool(oa.get("is_retracted"))

        entries.append({
            "pool_id": pid,
            "doi": doi,
            "title": title,
            "year": yr,
            "journal": journal,
            "first_author": first,
            "url": f"https://doi.org/{doi}" if doi else "",
            "verification_status": ("cross_verified" if oa_ok
                                    else "single_source_crossref"),
            "verified_in": (["crossref", "openalex"] if oa_ok else ["crossref"]),
            "retraction_flag": retr,
            "retraction_checked_on": str(date.today()),
            "abstract_retrieved": False,
            "metadata_only_note": "abstract not retrieved; no finding asserted",
            "used_in_sections": ["methods"],
            "claim_supported": claim,
            "added_at_phase": "7_5",
        })
        print(f"    -> {doi} | {yr} | {journal[:40]} | "
              f"{'cross_verified' if oa_ok else 'SINGLE SOURCE'}"
              f"{' | RETRACTED' if retr else ''}")
        time.sleep(4.0)

    OUT.write_text(json.dumps(
        {"schema_version": "v3.0",
         "generated_by": "scripts/build_citation_pool.py",
         "generated_on": str(date.today()),
         "rule_note": ("kuku-paper-lookup Rules 1/3/4/5/6; entries are live API "
                       "responses only, DOI cross-confirmed in Crossref+OpenAlex "
                       "where marked cross_verified"),
         "n_entries": len(entries),
         "failed_claims": failed,
         "entries": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nentries {len(entries)}  failed {len(failed)} {failed}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
