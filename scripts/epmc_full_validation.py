#!/usr/bin/env python
"""R18b:Europe PMC 补全剩余规则 + 三库汇总(多数据库文献验证)。

数据源:
  - PubMed 层(文献验证 R5.1):750 篇,precision=0.889(已有)
  - WoS 层(R18):r03/r10 已判定(multidb_validation_R18.json)
  - EPMC 层(本脚本):全部 21 规则,top-25 relevance,含摘要
产出:outputs/confirmatory/multidb_final_R18.json + 论文用三库对照表
"""
from __future__ import annotations
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

QUERIES = {
    "r01": "(\"uric acid\" OR hyperuricemia) AND cataract*",
    "r02": "(diabet* OR hyperglycemi*) AND cataract*",
    "r03": "(HbA1c OR \"glycosylated hemoglobin\") AND \"diabetic retinopathy\"*",
    "r04": "(HbA1c OR \"glycosylated hemoglobin\") AND (\"proliferative retinopathy\" OR PDR)",
    "r05": "(dyslipidemia OR hypercholesterolemia OR cholesterol) AND (\"macular degeneration\" OR AMD)",
    "r06": "(\"C-reactive protein\" OR CRP) AND (\"macular degeneration\" OR AMD)",
    "r07": "\"vitamin D\" AND retinopathy*",
    "r08": "(antioxidant* OR lutein OR zeaxanthin) AND cataract*",
    "r09": "(\"Mediterranean diet\" OR \"dietary pattern\") AND (\"macular degeneration\" OR AMD)",
    "r10": "smoking AND cataract*",
    "r11": "smoking AND (\"macular degeneration\" OR AMD)",
    "r12": "alcohol* AND cataract*",
    "r13": "(\"body mass index\" OR BMI OR obes*) AND cataract*",
    "r14": "lead AND cataract*",
    "r16": "(\"particulate matter\" OR \"PM2.5\") AND (glaucoma OR \"intraocular pressure\")",
    "r17": "(\"particulate matter\" OR \"PM2.5\") AND \"macular degeneration\"*",
    "r18": "(ultraviolet* OR \"UV radiation\") AND cataract*",
    "r19": "(\"pro-inflammatory diet\" OR \"dietary inflammatory\") AND retinopathy*",
    "r20": "smoking AND (\"vision impairment\" OR \"visual acuity\")",
    "r21": "(\"particulate matter\" OR \"PM2.5\") AND (\"vision impairment\" OR \"visual loss\")",
    "r22": "(\"body mass index\" OR BMI OR obes*) AND retinopathy*",
}


def epmc_search(query: str, n: int = 25) -> list[dict]:
    q = urllib.parse.urlencode({
        "query": f"({query}) AND HAS_ABSTRACT:Y AND SRC:MED",
        "format": "json", "pageSize": n, "resultType": "core"})
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{q}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = json.loads(r.read())
            out = []
            for x in d.get("resultList", {}).get("result", []):
                ab = x.get("abstractText", "") or ""
                if len(ab) > 150:
                    out.append({"pmid": x.get("pmid", ""), "title": x.get("title", ""),
                                "abstract": ab[:900], "year": x.get("pubYear", "")})
            return out
        except Exception:
            time.sleep(5 * (attempt + 1))
    return []


def main() -> int:
    from huiyan_agent.llm_client import LLMClient

    rules = yaml.safe_load((ROOT / "configs/rules.yaml").read_text(encoding="utf-8"))
    rl = rules["rules"] if isinstance(rules, dict) and "rules" in rules else rules
    rule_info = {r["id"].split("_")[0]: {
        "claim": r.get("rationale", "")[:150],
        "direction": r.get("direction", "risk_up"),
        "a": re.findall(r"'([^']+)'", str(r.get("entity_a_flags", ""))),
        "b": re.findall(r"'([^']+)'", str(r.get("entity_b_flags", ""))),
    } for r in rl}

    llm = LLMClient(provider="zhipu", temperature=0.0)
    prompt_tpl = """Evaluate whether this paper supports or contradicts a claimed exposure-disease relationship.

CLAIM: {claim} (direction: {direction})
EXPOSURE: {a_terms}
OUTCOME: {b_terms}
PAPER: {title}
ABSTRACT: {abstract}

Answer ONE line: TYPE|DIRECTION|EVIDENCE
TYPE: etiological|interventional|review|other
DIRECTION: CONCORDANT|DISCORDANT|NULL|UNCLEAR
"""
    # 跳过 WoS 已判定的(也可重复,双源对照)
    skip_done = set()
    wos_file = ROOT / "outputs/confirmatory/multidb_validation_R18.json"
    if wos_file.exists():
        skip_done = set(json.loads(wos_file.read_text(encoding="utf-8")).keys())
    print(f"WoS 已判定: {sorted(skip_done)}(EPMC 将重复判定作对照)")

    final = {}
    for rid, query in QUERIES.items():
        info = rule_info.get(rid)
        if not info:
            continue
        papers = epmc_search(query)
        print(f"\n[{rid}] EPMC {len(papers)} 篇", end="", flush=True)
        judged = []
        for rec in papers:
            prompt = prompt_tpl.format(
                claim=info["claim"][:100], direction=info["direction"],
                a_terms=", ".join(info["a"][:3]), b_terms=", ".join(info["b"][:3]),
                title=rec["title"][:150], abstract=rec["abstract"][:900])
            try:
                resp = llm.complete(prompt, raise_on_error=True)
                line = resp.text.strip().split("\n")[0]
                parts = line.split("|")
                if len(parts) >= 2:
                    judged.append({"pmid": rec["pmid"], "type": parts[0].strip().lower(),
                                   "direction": parts[1].strip().upper()})
            except Exception:
                pass
            time.sleep(0.3)
        etio = [r for r in judged if "etiol" in r["type"]]
        conc = sum(1 for r in etio if r["direction"] == "CONCORDANT")
        disc = sum(1 for r in etio if r["direction"] == "DISCORDANT")
        inf = conc + disc
        prec = round(conc / inf, 3) if inf else None
        final[rid] = {"n_epmc": len(papers), "n_judged": len(judged),
                      "etiological": len(etio), "concordant": conc, "discordant": disc,
                      "precision_epmc": prec}
        print(f" → {conc}一致/{disc}反向 | precision={prec}")

    out = ROOT / "outputs/confirmatory/multidb_final_R18.json"
    out.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[写盘] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
