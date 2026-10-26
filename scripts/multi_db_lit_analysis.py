#!/usr/bin/env python
"""R18:多数据库文献验证分析器(Embase/WoS/CNKI 结果导入后运行)。

用法:把数据库导出文件放到 data/processed/ 下,然后:
  PYTHONUTF8=1 python scripts/multi_db_lit_analysis.py

支持格式:.csv(标题+摘要列) / .ris(标准 RIS) / .json(自定义)
自动:去重(排除与 PubMed 证据池重叠)→ LLM 方向判定 → precision_lit_per_db
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


def load_ris(path: Path) -> list[dict]:
    """解析 RIS 文件,提取标题/摘要/DOI/数据库。"""
    papers = []
    current = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("TY  -"):
            current = {"database": path.stem}
        elif line.startswith("TI  -") or line.startswith("T1  -"):
            current["title"] = line[6:].strip()
        elif line.startswith("AB  -") or line.startswith("N2  -"):
            current["abstract"] = line[6:].strip()
        elif line.startswith("DO  -"):
            current["doi"] = line[6:].strip()
        elif line.startswith("ER  -"):
            if current.get("title"):
                papers.append(current)
            current = {}
    return papers


def load_csv(path: Path) -> list[dict]:
    """解析 CSV(列名需含 title 和 abstract,大小写不敏感)。"""
    import pandas as pd
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    cols = {c.lower(): c for c in df.columns}
    title_col = cols.get("title") or cols.get("Article Title") or cols.get("题名")
    abs_col = cols.get("abstract") or cols.get("Article Abstract") or cols.get("摘要")
    doi_col = cols.get("doi") or cols.get("Article DOI")
    papers = []
    for _, row in df.iterrows():
        papers.append({
            "database": path.stem,
            "title": str(row.get(title_col, "")) if title_col else "",
            "abstract": str(row.get(abs_col, ""))[:2000] if abs_col else "",
            "doi": str(row.get(doi_col, "")) if doi_col else "",
        })
    return [p for p in papers if p["title"] and p["title"] != "nan"]


def load_papers(path: Path) -> list[dict]:
    if path.suffix.lower() == ".ris":
        return load_ris(path)
    elif path.suffix.lower() == ".csv":
        return load_csv(path)
    elif path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    raise ValueError(f"不支持的格式: {path.suffix}")


def dedup_against_pool(papers: list[dict]) -> tuple[list[dict], int]:
    """排除与 PubMed 证据池重叠(按标题前 60 字符匹配)。"""
    pool_titles = set()
    pool_path = ROOT / "data/seed/evidence_chunks.jsonl"
    if pool_path.exists():
        for line in pool_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            c = json.loads(line)
            t = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]", "", str(c.get("title", ""))[:60]).lower()
            if t:
                pool_titles.add(t)
    unique, overlap = [], 0
    for p in papers:
        t = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]", "", p.get("title", "")[:60]).lower()
        if t in pool_titles:
            overlap += 1
        else:
            unique.append(p)
    return unique, overlap


def extract_rule_direction(llm, rule_claim: str, direction: str,
                           a_terms: str, b_terms: str,
                           title: str, abstract: str) -> dict:
    prompt = f"""Evaluate whether this paper supports or contradicts a claimed exposure-disease relationship.

CLAIM: {rule_claim[:100]} (direction: {direction})
EXPOSURE: {a_terms}
OUTCOME: {b_terms}
PAPER: {title}
ABSTRACT: {abstract[:800]}

Answer ONE line: TYPE|DIRECTION|EVIDENCE
TYPE: etiological|interventional|review|other
DIRECTION: CONCORDANT|DISCORDANT|NULL|UNCLEAR
"""
    try:
        resp = llm.complete(prompt, raise_on_error=True)
        line = resp.text.strip().split("\n")[0]
        parts = line.split("|")
        if len(parts) >= 3:
            return {"type": parts[0].strip().lower(),
                    "direction": parts[1].strip().upper(),
                    "evidence": parts[2].strip()[:80]}
    except Exception:
        pass
    return {"type": "unknown", "direction": "UNCLEAR", "evidence": ""}


def main() -> int:
    proc = ROOT / "data/processed"
    files = [f for f in proc.glob("*_results.*")
             if f.suffix.lower() in (".ris", ".csv", ".json")]
    if not files:
        print("未找到结果文件(data/processed/*_results.{ris,csv,json})")
        return 1
    print(f"发现 {len(files)} 个数据库结果文件: {[f.name for f in files]}")

    # 加载规则
    rules = yaml.safe_load((ROOT / "configs/rules.yaml").read_text(encoding="utf-8"))
    rl = rules["rules"] if isinstance(rules, dict) and "rules" in rules else rules
    rule_info = {r["id"].split("_")[0]: {
        "claim": r.get("rationale", "")[:150],
        "direction": r.get("direction", "risk_up"),
        "a": re.findall(r"'([^']+)'", str(r.get("entity_a_flags", ""))),
        "b": re.findall(r"'([^']+)'", str(r.get("entity_b_flags", ""))),
    } for r in rl}

    from huiyan_agent.llm_client import LLMClient
    llm = LLMClient(provider="zhipu", temperature=0.0)

    all_results = {}
    for f in files:
        db_name = f.stem.replace("_results", "")
        papers = load_papers(f)
        unique, overlap = dedup_against_pool(papers)
        print(f"\n[{db_name}] 总 {len(papers)} 篇 | 与 PubMed 池重叠 {overlap} | 独立 {len(unique)} 篇")

        # 对独立论文按规则做方向判定(简化:用关键词匹配找到最可能的规则)
        results = []
        for p in unique:
            text = f"{p.get('title','')} {p.get('abstract','')[:500]}".lower()
            best_rule = None
            for rid, info in rule_info.items():
                a_match = any(a.lower() in text for a in info["a"][:2])
                b_match = any(b.replace("_", " ").lower() in text for b in info["b"][:2])
                if a_match and b_match:
                    best_rule = rid
                    break
            if not best_rule:
                continue
            info = rule_info[best_rule]
            jd = extract_rule_direction(
                llm, info["claim"], info["direction"],
                ", ".join(info["a"][:3]), ", ".join(info["b"][:3]),
                p.get("title", ""), p.get("abstract", ""))
            results.append({"rule": best_rule, "title": p.get("title", "")[:50],
                            **jd})
            print(f"  {best_rule} | {jd['direction'][:10]} | {p.get('title','')[:40]}...")
            time.sleep(0.3)

        all_results[db_name] = results
        # precision
        etio = [r for r in results if "etiol" in r["type"]]
        if etio:
            conc = sum(1 for r in etio if r["direction"] == "CONCORDANT")
            disc = sum(1 for r in etio if r["direction"] == "DISCORDANT")
            inf = conc + disc
            prec = conc / inf if inf else None
            print(f"  → {db_name}: {conc}一致/{disc}反向/{inf}信息性对"
                  f" | precision = {prec:.3f}" if prec else
                  f"  → {db_name}: 信息性对={inf},precision 暂无定义")

    out = ROOT / "outputs/confirmatory/multi_db_lit_R18.json"
    out.write_text(json.dumps(all_results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[写盘] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
