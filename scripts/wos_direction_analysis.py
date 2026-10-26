#!/usr/bin/env python
"""R18:WoS 导出文件解析 + LLM 方向判定(多数据库文献验证)。

输入: data/processed/wos_r*_export.txt (WoS plain text 导出)
输出: outputs/confirmatory/multidb_validation_R18.json
  - 每规则 concordant/discordant/null 计数
  - precision_lit_per_rule
  - 与 PubMed 层(0.889)对照
"""
from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def parse_wos_file(path: Path) -> list[dict]:
    """解析 WoS plain text 格式(字段前缀两字母)。"""
    txt = path.read_text(encoding="utf-8-sig")
    records = []
    for block in re.split(r"\nER\n", txt):
        if "PT " not in block:
            continue
        rec = {}
        # 多行字段(TI/AB/SO 等以两字母开头,续行三空格缩进)
        for m in re.finditer(r"\n([A-Z][A-Z0-9]) (.+?)(?=\n[A-Z][A-Z0-9] |\nER\n|\Z)", block, re.S):
            key, val = m.group(1), " ".join(m.group(2).split())
            rec[key] = val
        records.append({
            "ut": rec.get("UT", ""),
            "title": rec.get("TI", ""),
            "abstract": rec.get("AB", ""),
            "doi": rec.get("DI", ""),
            "year": rec.get("PY", ""),
            "journal": rec.get("SO", ""),
        })
    return records


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
    export_dir = ROOT / "data/processed"
    all_out = {}
    for path in sorted(export_dir.glob("wos_r*_export.txt")):
        rid = path.stem.replace("wos_", "").replace("_export", "")
        info = rule_info.get(rid)
        if not info:
            continue
        records = parse_wos_file(path)
        print(f"\n[{rid}] {len(records)} 篇来自 WoS")
        judged = []
        for rec in records:
            if len(rec["abstract"]) < 80:
                continue
            prompt = prompt_tpl.format(
                claim=info["claim"][:100], direction=info["direction"],
                a_terms=", ".join(info["a"][:3]), b_terms=", ".join(info["b"][:3]),
                title=rec["title"][:150], abstract=rec["abstract"][:900])
            try:
                resp = llm.complete(prompt, raise_on_error=True)
                line = resp.text.strip().split("\n")[0]
                parts = line.split("|")
                if len(parts) >= 2:
                    d = parts[1].strip().upper()
                    t = parts[0].strip().lower()
                    judged.append({"ut": rec["ut"], "type": t, "direction": d,
                                   "evidence": (parts[2].strip()[:60] if len(parts) > 2 else "")})
                    print(f"  {d:12s} | {rec['title'][:55]}")
            except Exception as e:
                print(f"  ERR {rec['ut']}: {str(e)[:50]}")
            time.sleep(0.35)
        etio = [r for r in judged if "etiol" in r["type"]]
        conc = sum(1 for r in etio if r["direction"] == "CONCORDANT")
        disc = sum(1 for r in etio if r["direction"] == "DISCORDANT")
        inf = conc + disc
        prec = round(conc / inf, 3) if inf else None
        all_out[rid] = {
            "n_papers": len(records), "n_judged": len(judged),
            "etiological": len(etio), "concordant": conc, "discordant": disc,
            "precision_lit": prec,
            "judged": judged,
        }
        print(f"  → {rid}: {conc}一致/{disc}反向 | precision={prec}")

    out = ROOT / "outputs/confirmatory/multidb_validation_R18.json"
    out.write_text(json.dumps(all_out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[写盘] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
