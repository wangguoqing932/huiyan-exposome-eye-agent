#!/usr/bin/env python
"""Literature-based external validation (analysis_plan §12, pre-registered
2026-10-15 BEFORE any run).

Independent PubMed validation of all 21 v1.2 rules: per-rule search
(exposure terms AND outcome terms), efetch title/abstract, exclude the
rule's own citations (anti-circular), tag evidence-pool overlap, LLM
extract direction per study (local qwen, temp=0), aggregate to a
pre-registered literature three-state verdict per rule.

Stages (resumable):
  search   — esearch+efetch → data/processed/lit_validation_pubmed.json
  extract  — per-article LLM extraction → data/processed/lit_validation_extracts.jsonl (append)
  summary  — verdicts + sensitivity S1/S2/S3 → outputs/confirmatory/literature_validation_*

Usage:
  PYTHONUTF8=1 python scripts/literature_validation.py --stage search
  PYTHONUTF8=1 python scripts/literature_validation.py --stage extract
  PYTHONUTF8=1 python scripts/literature_validation.py --stage summary
"""
from __future__ import annotations
import argparse, json, random, re, sys, time, unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from huiyan_agent.llm_client import LLMClient

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_JSON = ROOT / "data/processed/lit_validation_pubmed.json"
EXTRACTS = ROOT / "data/processed/lit_validation_extracts.jsonl"
OUTDIR = ROOT / "outputs/confirmatory"
TOP_N = 40
LLM_SEED = 20261015


# ── helpers ──────────────────────────────────────────────────────────
def _ascii_terms(*vals: str) -> list[str]:
    """Split semicolon/comma lists, keep ASCII-only terms."""
    out = []
    for v in vals:
        if not v:
            continue
        for t in re.split(r"[;,]", v):
            t = t.strip()
            if t and all(ord(c) < 128 for c in t) and len(t) > 2:
                out.append(t)
    return out


# ── search-term thesaurus (disclosed in analysis_plan §12; registry names
#    contain operationalization suffixes like "(graded)" that never appear
#    verbatim in the literature, so standard literature MeSH-style terms
#    are mapped per flag) ─────────────────────────────────────────────
A_FLAG_TERMS = {
    "uric_acid_elevated": ["uric acid"],
    "hyperglycemia": ["hyperglycemia", "fasting glucose", "high blood glucose"],
    "hba1c_elevated": ["hemoglobin A1c", "glycated hemoglobin", "HbA1c"],
    "dyslipidemia": ["dyslipidemia", "cholesterol", "triglycerides", "serum lipids"],
    "crp_elevated": ["C-reactive protein", "CRP"],
    "bmi_high": ["body mass index", "BMI", "obesity", "overweight"],
    "current_smoking": ["smoking", "cigarette", "tobacco"],
    "alcohol_intake": ["alcohol", "drinking"],
    "lead_exposure": ["lead exposure", "blood lead"],
    "pm25_exposure": ["particulate matter", "air pollution", "PM2.5"],
    "uv_exposure": ["ultraviolet", "sunlight", "UV exposure"],
    "mediterranean_diet": ["Mediterranean diet"],
    "low_antioxidant_intake": ["antioxidant", "carotenoids", "lutein", "zeaxanthin"],
    "vitamin_d_deficiency": ["vitamin D", "25-hydroxyvitamin D", "25(OH)D"],
    "pro_inflammatory_diet": ["dietary inflammatory index", "pro-inflammatory diet"],
}
B_FLAG_TERMS = {
    "cataract_any": ["cataract"],
    "retinopathy_any": ["diabetic retinopathy", "retinopathy"],
    "dr_npdr": ["diabetic retinopathy", "retinopathy"],
    "dr_pdr": ["diabetic retinopathy", "proliferative retinopathy"],
    "amd_early": ["age-related macular degeneration", "macular degeneration"],
    "amd_late": ["age-related macular degeneration", "macular degeneration"],
    "glaucoma_iop_elevated": ["glaucoma", "intraocular pressure"],
    "glaucoma_suspect_cdr": ["glaucoma", "cup-to-disc ratio"],
    "vision_impairment_moderate": ["visual impairment", "vision loss"],
    "vision_impairment_severe": ["visual impairment", "vision loss", "blindness"],
}


def build_query_maps():
    return dict(A_FLAG_TERMS), dict(B_FLAG_TERMS)


def rule_citation_exclusion():
    """PMIDs and DOIs cited BY the rules themselves (per-rule and global)."""
    rep = json.loads((ROOT / "outputs/citation_verification_report.json").read_text(encoding="utf-8"))
    per_rule, all_pmids, all_dois = {}, set(), set()
    for r in rep.get("rules", []):
        rid = r["id"].split("_")[0]  # r01 ... r22
        s = per_rule.setdefault(rid, {"pmids": set(), "dois": set()})
        for c in r.get("citations", []):
            meta = c.get("meta", {}) or {}
            pm = meta.get("pmid") or ""
            m = re.search(r"(\d{6,})", str(pm))
            if m:
                s["pmids"].add(m.group(1)); all_pmids.add(m.group(1))
            doi = meta.get("doi") or (c.get("raw", {}) or {}).get("ref") or ""
            if doi and "/" in str(doi):
                s["dois"].add(str(doi).lower()); all_dois.add(str(doi).lower())
    return per_rule, all_pmids, all_dois


def evidence_pool_pmids() -> set:
    pool = set()
    p = ROOT / "data/seed/evidence_chunks.jsonl"
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        pid = str(r.get("pmid") or "").strip()
        if pid:
            pool.add(pid)
    return pool


def http_get(url: str, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "huiyan-litval/1.0"})
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(2 ** i)
    raise RuntimeError(f"HTTP failed after {retries}: {url[:120]} ({last})")


# ── stage: search ────────────────────────────────────────────────────
def stage_search():
    doc = yaml.safe_load((ROOT / "configs/rules.yaml").read_text(encoding="utf-8"))
    rules = doc["rules"]
    a_map, b_map = build_query_maps()
    per_rule_cit, all_cit_pmids, all_cit_dois = rule_citation_exclusion()
    pool = evidence_pool_pmids()

    out = {}
    for rule in rules:
        rid = rule["id"].split("_")[0]
        a_terms = []
        for f in rule.get("entity_a_flags", []):
            a_terms += a_map.get(f, [])
        b_terms = []
        for f in rule.get("entity_b_flags", []):
            b_terms += b_map.get(f, [])
        a_terms = list(dict.fromkeys(a_terms))[:3]
        b_terms = list(dict.fromkeys(b_terms))[:3]
        if not a_terms or not b_terms:
            out[rule["id"]] = {"status": "no_search_terms", "a_terms": a_terms, "b_terms": b_terms}
            continue
        q = "(" + " OR ".join(f"{t}[tiab]" for t in a_terms) + ") AND (" + \
            " OR ".join(f"{t}[tiab]" for t in b_terms) + ") AND english[lang]"
        try:
            es = http_get(f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax={TOP_N}&term=" + urllib.parse.quote(q))
            ids = json.loads(es)["esearchresult"].get("idlist", [])
        except Exception as e:
            out[rule["id"]] = {"status": f"search_fail:{type(e).__name__}", "query": q}
            continue
        arts = []
        for i in range(0, len(ids), 20):
            batch = ids[i:i + 20]
            try:
                xml = http_get(f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(batch))
            except Exception as e:
                out[rule["id"]] = {"status": f"efetch_fail:{type(e).__name__}", "query": q}
                arts = []
                break
            arts += parse_pubmed_xml(xml)
        excl = per_rule_cit.get(rid, {"pmids": set(), "dois": set()})
        kept, excluded_own, overlap = [], 0, 0
        seen = set()
        for a in arts:
            pid = a["pmid"]
            if pid in seen:
                continue
            seen.add(pid)
            if pid in excl["pmids"] or pid in all_cit_pmids or (a["doi"] and a["doi"].lower() in all_cit_dois):
                excluded_own += 1
                continue
            a["pool_overlap"] = pid in pool
            overlap += int(a["pool_overlap"])
            kept.append(a)
        out[rule["id"]] = {
            "status": "ok", "query": q, "a_terms": a_terms, "b_terms": b_terms,
            "n_found": len(ids),
            "n_kept": len(kept), "n_excluded_own_citation": excluded_own,
            "n_pool_overlap": overlap,
            "direction": rule.get("direction", "risk_up"),
            "negative_control": bool(rule.get("negative_control", False)),
            "articles": kept,
        }
        print(f"[search] {rule['id']}: found {len(ids)}, kept {len(kept)} "
              f"(own-citation excluded {excluded_own}, pool overlap {overlap})")
        time.sleep(0.5)
    PUBMED_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[search] → {PUBMED_JSON}")


def parse_pubmed_xml(xml: str) -> list[dict]:
    arts = []
    for m in re.finditer(r"<PubmedArticle>(.*?)</PubmedArticle>", xml, re.DOTALL):
        b = m.group(1)
        pmid = (re.search(r"<PMID[^>]*>(\d+)</PMID>", b) or [None, ""])[1]
        ti = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", b, re.DOTALL)
        ab = re.search(r"<AbstractText[^>]*>(.*?)</AbstractText>", b, re.DOTALL)
        doi_m = re.search(r'<ArticleId IdType="doi">(.*?)</ArticleId>', b)
        year_m = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", b, re.DOTALL)
        ptypes = re.findall(r"<PublicationType[^>]*>(.*?)</PublicationType>", b)
        clean = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
        arts.append({
            "pmid": pmid, "doi": clean(doi_m.group(1) if doi_m else ""),
            "title": clean(ti.group(1) if ti else ""),
            "abstract": clean(ab.group(1) if ab else "")[:2500],
            "year": year_m.group(1) if year_m else "",
            "pubtypes": ptypes[:6],
        })
    return arts


# ── stage: extract ───────────────────────────────────────────────────
def stage_extract(limit_per_rule: int = 40):
    data = json.loads(PUBMED_JSON.read_text(encoding="utf-8"))
    done = set()
    if EXTRACTS.exists():
        for line in EXTRACTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["rule_id"], r["pmid"]))
    llm = LLMClient(provider=__import__("os").environ.get("HUIYAN_LLM_PROVIDER", "local"), temperature=0.0, seed=LLM_SEED)
    rng = random.Random(LLM_SEED)
    n_new, n_fail = 0, 0
    for rule_id, d in data.items():
        if d.get("status") != "ok":
            continue
        arts = d["articles"][:limit_per_rule]
        claim_dir = "increased" if d["direction"] == "risk_up" else "decreased"
        a_disp = " / ".join(d.get("a_terms") or ["the exposure"])
        b_disp = " / ".join(d.get("b_terms") or ["the eye outcome"])
        for a in arts:
            if (rule_id, a["pmid"]) in done:
                continue
            prompt = (
                f'Rule claim: "{a_disp}" (exposure) is associated with {claim_dir} risk of "{b_disp}" (eye outcome).\n'
                f"Study {a['pmid']} ({a['year']}): {a['title']}\n"
                f"Abstract: {a['abstract'] or '(no abstract in record)'}\n\n"
                "Answer as STRICT JSON only (no prose, no markdown):\n"
                '{"relevant": <true|false>, '
                '"study_class": <"etiological"|"interventional">, '
                '"direction": <"concordant"|"discordant"|"null"|"unclear">, '
                '"study_type": <"RCT"|"cohort"|"case_control"|"cross_sectional"|"meta_systematic"|"case_report"|"mechanistic"|"review_other">, '
                '"note": "<=12 words>"}\n'
                "relevant = this study examines or reports THIS exposure-outcome pair; false only if the pair is not studied at all. "
                "TWO-STEP direction logic (follow exactly): "
                "Step 1 classify: 'etiological' (compares exposure LEVELS/status vs outcome risk) or 'interventional' "
                "(administers/removes the exposure agent — RCT, animal or mechanistic treatment/rescue studies). "
                "Step 2 judge direction: "
                "ETIOLOGICAL: if the claim says LOW exposure raises risk, a finding that HIGHER exposure relates to LOWER risk is CONCORDANT "
                "(same association, inverse framing) — and vice versa; a finding that higher exposure relates to HIGHER risk is DISCORDANT. "
                "INTERVENTIONAL: supplementing the agent IMPROVING the outcome is CONCORDANT with 'low intake raises risk' / 'high intake "
                "lowers risk' claims; supplementing with NO effect is 'null'; worsening the outcome is DISCORDANT. "
                "null = explicitly no association/effect; unclear = cannot tell."
            )
            rec = {"rule_id": rule_id, "pmid": a["pmid"], "pool_overlap": a.get("pool_overlap", False),
                   "title": a["title"][:160], "year": a["year"]}
            raw = ""
            try:
                resp = llm.complete(prompt=prompt, system="You extract study findings. Output strict JSON only.",
                                    raise_on_error=True)
                raw = (resp.text or "").strip()
                m = re.search(r"\{.*\}", raw, re.DOTALL)
                j = json.loads(m.group(0))
                rec["relevant"] = bool(j.get("relevant"))
                rec["direction"] = str(j.get("direction", "unclear")).lower()
                rec["study_type"] = str(j.get("study_type", "review_other")).lower()
                rec["note"] = str(j.get("note", ""))[:120]
                assert rec["direction"] in ("concordant", "discordant", "null", "unclear")
            except Exception as e:
                rec["relevant"] = None
                rec["direction"] = "parse_fail"
                rec["error"] = f"{type(e).__name__}: {str(e)[:100]}"
                n_fail += 1
            # 15% second pass for stability check (S3)
            if rng.random() < 0.15:
                try:
                    resp2 = llm.complete(prompt=prompt, system="You extract study findings. Output strict JSON only.",
                                         raise_on_error=True)
                    m2 = re.search(r"\{.*\}", resp2.text or "", re.DOTALL)
                    j2 = json.loads(m2.group(0))
                    rec["second_pass_direction"] = str(j2.get("direction", "")).lower()
                except Exception:
                    rec["second_pass_direction"] = "parse_fail"
            with EXTRACTS.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_new += 1
            if n_new % 50 == 0:
                print(f"[extract] {n_new} new extractions (fails so far: {n_fail})")
    print(f"[extract] done: {n_new} new, {n_fail} parse failures → {EXTRACTS}")


# ── stage: summary ───────────────────────────────────────────────────
def _verdict(n_conc, n_disc, n_null, n_rel):
    if n_rel < 2:
        return "uninformative_lit"
    if n_conc >= 2 and n_disc >= 2:
        return "mixed_lit"
    if n_conc >= 2 and n_conc > n_disc and n_conc >= n_null:
        return "replicated_lit"
    if n_disc >= 2 and n_disc > n_conc:
        return "contradicted_lit"
    if n_null >= 2 and n_null > max(n_conc, n_disc):
        return "null_dominant_lit"
    return "uninformative_lit"


def stage_summary():
    data = json.loads(PUBMED_JSON.read_text(encoding="utf-8"))
    recs = [json.loads(l) for l in EXTRACTS.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = []
    for r in recs:
        d = data.get(r["rule_id"], {})
        r2 = dict(r)
        r2["direction_rule"] = d.get("direction")
        r2["negative_control"] = d.get("negative_control", False)
        rows.append(r2)
    from collections import defaultdict
    by_rule = defaultdict(list)
    for r in rows:
        by_rule[r["rule_id"]].append(r)

    HUMAN = {"RCT", "cohort", "case_control", "cross_sectional", "meta_systematic"}
    verdicts, conc_disagree = {}, []
    for rid, rs in by_rule.items():
        rel = [r for r in rs if r.get("relevant")]
        cnt = lambda sub, k: sum(1 for r in sub if r.get("direction") == k)
        n_conc, n_disc, n_null = cnt(rel, "concordant"), cnt(rel, "discordant"), cnt(rel, "null")
        v_main = _verdict(n_conc, n_disc, n_null, len(rel))
        # S1: drop evidence-pool overlap
        s1 = [r for r in rel if not r.get("pool_overlap")]
        v_s1 = _verdict(cnt(s1, "concordant"), cnt(s1, "discordant"), cnt(s1, "null"), len(s1))
        # S2: human-study designs only
        s2 = [r for r in rel if r.get("study_type") in HUMAN]
        v_s2 = _verdict(cnt(s2, "concordant"), cnt(s2, "discordant"), cnt(s2, "null"), len(s2))
        # S3: second-pass stability
        sec = [r for r in rs if r.get("second_pass_direction") and r.get("relevant")]
        agree = sum(1 for r in sec if r["second_pass_direction"] == r.get("direction"))
        if sec:
            conc_disagree.append((rid, agree, len(sec)))
        verdicts[rid] = {
            "n_searched": len(rs), "n_relevant": len(rel),
            "n_concordant": n_conc, "n_discordant": n_disc, "n_null": n_null,
            "n_unclear": cnt(rel, "unclear"),
            "study_types": dict(sorted((t, sum(1 for r in rel if r.get("study_type") == t))
                                       for t in {r.get("study_type") for r in rel})),
            "verdict": v_main, "verdict_S1_no_pool_overlap": v_s1,
            "verdict_S2_human_studies_only": v_s2,
            "negative_control": rs[0].get("negative_control", False),
        }
    main_rules = {k: v for k, v in verdicts.items() if not v["negative_control"]}
    rep = sum(1 for v in main_rules.values() if v["verdict"] == "replicated_lit")
    con = sum(1 for v in main_rules.values() if v["verdict"] == "contradicted_lit")
    mix = sum(1 for v in main_rules.values() if v["verdict"] == "mixed_lit")
    prec = rep / (rep + con + mix) if (rep + con + mix) else None
    ci = (None, None)
    if prec is not None and (rep + con + mix):
        from scipy import stats as _st
        n = rep + con + mix
        lo = _st.beta.ppf(0.025, rep, n - rep + 1) if rep > 0 else 0.0
        hi = _st.beta.ppf(0.975, rep + 1, n - rep) if rep < n else 1.0
        ci = (round(float(lo), 3), round(float(hi), 3))
    sec_tot = sum(b for _, a, b in conc_disagree)
    sec_agree = sum(a for _, a, b in conc_disagree)
    summary = {
        "date": "2026-10-15", "protocol": "analysis_plan §12 (pre-registered before run)",
        "verdicts": verdicts,
        "precision_lit": round(prec, 3) if prec is not None else None,
        "precision_lit_ci95_clopper_pearson": ci,
        "counts": {"replicated_lit": rep, "contradicted_lit": con, "mixed_lit": mix,
                   "null_dominant": sum(1 for v in main_rules.values() if v["verdict"] == "null_dominant_lit"),
                   "uninformative": sum(1 for v in main_rules.values() if v["verdict"] == "uninformative_lit"),
                   "main_rules": len(main_rules)},
        "S3_stability": {"second_pass_pairs": sec_tot, "agree": sec_agree,
                         "agreement_rate": round(sec_agree / sec_tot, 3) if sec_tot else None},
        "note": ("Literature layer is an EXTERNAL CONSISTENCY validation, not causal confirmation; "
                 "search window/publication bias/LLM extraction error declared in limitations. "
                 "Rule own-citations excluded; evidence-pool overlap tagged (S1 drops it)."),
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "literature_validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    import csv as _csv
    all_keys = []
    for r in rows:
        for k in r.keys():
            if k not in all_keys:
                all_keys.append(k)
    with (OUTDIR / "literature_validation_R5.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = _csv.DictWriter(f, fieldnames=all_keys)
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({k: summary[k] for k in ("precision_lit", "precision_lit_ci95_clopper_pearson",
                                              "counts", "S3_stability")}, ensure_ascii=False, indent=1))
    print(f"[summary] → {OUTDIR/'literature_validation_R5.csv'} & literature_validation_summary.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True, choices=["search", "extract", "summary", "all"])
    args = ap.parse_args()
    if args.stage in ("search", "all"):
        stage_search()
    if args.stage in ("extract", "all"):
        stage_extract()
    if args.stage in ("summary", "all"):
        stage_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
