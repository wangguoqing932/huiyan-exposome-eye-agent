#!/usr/bin/env python
"""R19:CNKI 中文文献方向判定(知网批量采集结果 → LLM 中文两步法判定)。

输入: data/processed/cnki_batch1.json(知网标题采集,8 规则)
输出: outputs/confirmatory/cnki_validation_R19.json
说明: 知网免费层只有标题(摘要在详情页);中文标题通常自带方向信息
(如"...相关影响因素分析""...病例对照研究"),标题级判定可行,
标 confidence=title_level 如实注记。
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

RULE_CN = {
    "r02": {"claim": "高血糖/糖尿病增加白内障风险(方向:风险升高)", "a": "糖尿病/高血糖", "b": "白内障"},
    "r03": {"claim": "糖化血红蛋白升高与糖尿病视网膜病变相关(方向:风险升高)", "a": "糖化血红蛋白", "b": "糖尿病视网膜病变"},
    "r10": {"claim": "吸烟增加白内障风险(方向:风险升高)", "a": "吸烟", "b": "白内障"},
    "r12": {"claim": "饮酒与白内障相关(方向:风险升高)", "a": "饮酒", "b": "白内障"},
    "r13": {"claim": "肥胖/高体重指数增加白内障风险(方向:风险升高)", "a": "肥胖/体重指数", "b": "白内障"},
    "r16": {"claim": "颗粒物暴露与青光眼/眼压升高相关(方向:风险升高)", "a": "颗粒物/PM2.5", "b": "青光眼/眼压"},
    "r18": {"claim": "紫外线暴露增加白内障风险(方向:风险升高)", "a": "紫外线", "b": "白内障"},
    "r20": {"claim": "吸烟与视力损害相关(方向:风险升高)", "a": "吸烟", "b": "视力损害"},
}


def main() -> int:
    from huiyan_agent.llm_client import LLMClient

    data = json.loads((ROOT / "data/processed/cnki_batch1.json").read_text(encoding="utf-8"))
    llm = LLMClient(provider="zhipu", temperature=0.0)
    prompt_tpl = """你是流行病学专家。判断以下中文文献标题所报告的暴露-疾病关系,是否支持该规则声明。

规则声明:{claim}
文献标题:{title}

标题若为横断面/病例对照/队列研究且报告了该暴露与疾病的关联 → 判断方向:
- 支持声明方向 = CONCORDANT
- 报告相反方向(保护效应) = DISCORDANT
- 未报告该关联或仅综述/述评 = UNCLEAR

只输出一行:CONCORDANT|DISCORDANT|UNCLEAR(加 10 字以内依据)
"""
    final = {}
    for rid, titles in data.items():
        if rid not in RULE_CN or not titles:
            continue
        info = RULE_CN[rid]
        judged = []
        for t in titles:
            try:
                resp = llm.complete(prompt_tpl.format(claim=info["claim"], title=t), raise_on_error=True)
                line = resp.text.strip().split("\n")[0]
                m = re.search(r"(CONCORDANT|DISCORDANT|UNCLEAR)", line.upper())
                d = m.group(1) if m else "UNCLEAR"
                judged.append({"title": t, "direction": d, "confidence": "title_level"})
            except Exception:
                pass
            time.sleep(0.3)
        conc = sum(1 for r in judged if r["direction"] == "CONCORDANT")
        disc = sum(1 for r in judged if r["direction"] == "DISCORDANT")
        inf = conc + disc
        prec = round(conc / inf, 3) if inf else None
        final[rid] = {"n_titles": len(titles), "n_judged": len(judged),
                      "concordant": conc, "discordant": disc,
                      "precision_cnki": prec, "confidence": "title_level",
                      "detail": judged}
        print(f"{rid}: {len(titles)} 标题 | {conc}一致/{disc}反向 | precision={prec}")

    out = ROOT / "outputs/confirmatory/cnki_validation_R19.json"
    out.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[写盘] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
