#!/usr/bin/env python
"""R11 (2026-10-15): baseline metrics under the corrected gold — dual report.

R11 审计修复了 NHANES 吸烟参照组(A1)与终生饮酒(A2)操作化错误,gold3 标签
逐对变化(NHANES: current_smoking×dr_npdr replicated→uninformative)。
基线预测是冻结的 R5 记录(baseline_predictions.jsonl 的 prediction 字段),
金标准是外部量——本脚本把同一批预测在【R5 gold(jsonl 内嵌)】与
【R11 corrected gold(nhanes_confirmatory.csv 现行 gold3)】两个口径下并列重算,
写出 outputs/baseline_summary_R11_corrected_gold.json。
不修改 baseline_summary_R5.json(R5 记录保留)。

注:修正后 NHANES tested=81 对(jsonl 仍为 80 对——多出的 1 对为修正后新增的
规则覆盖对,无基线预测,在两个口径下均不计入,如实注记)。

Run: PYTHONUTF8=1 python scripts/make_baseline_summary_R11_goldcheck.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from scipy import stats as st

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"


def metrics(rows, goldmap):
    tp = sum(1 for r in rows if r["prediction"] and goldmap[(r["a_flag"], r["b_item"])] == "replicated")
    fp = sum(1 for r in rows if r["prediction"] and goldmap[(r["a_flag"], r["b_item"])] != "replicated")
    fn = sum(1 for r in rows if not r["prediction"] and goldmap[(r["a_flag"], r["b_item"])] == "replicated")
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else (0.0 if (tp + fp or tp + fn) else None)
    return {"TP": tp, "FP": fp, "FN": fn, "P": round(prec, 3) if prec is not None else None,
            "R": round(rec, 3) if rec is not None else None,
            "F1": round(f1, 3) if f1 is not None else None}


def mcnemar(a_rows, b_rows, goldmap):
    ka = {(r["a_flag"], r["b_item"]): r["prediction"] for r in a_rows}
    kb = {(r["a_flag"], r["b_item"]): r["prediction"] for r in b_rows}
    keys = sorted(set(ka) & set(kb))
    pos = lambda k: goldmap[k] == "replicated"
    b_ = sum(1 for k in keys if ka[k] and not kb[k])
    c_ = sum(1 for k in keys if not ka[k] and kb[k])
    n = b_ + c_
    p = 1.0 if n == 0 else min(1.0, 2 * st.binom.cdf(min(b_, c_), n, 0.5))
    return {"b_full_yes_base_no": b_, "c_full_no_base_yes": c_, "p_exact": round(p, 5)}


def main() -> int:
    recs = [json.loads(l) for l in
            (OUT / "baseline_predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    conf = pd.read_csv(OUT / "confirmatory/nhanes_confirmatory.csv", encoding="utf-8-sig")
    gold_r11 = {(r.a_flag, r.b_item): r.gold3 for r in conf.itertuples()
                if r.status == "tested" and isinstance(r.gold3, str)}
    runs = defaultdict(lambda: defaultdict(list))
    for r in recs:
        if r.get("valid", True):
            runs[r["baseline"]][r["seed"]].append(r)

    import statistics as stats
    out = {"date": "2026-10-15 (R11 gold correction A1/A2)",
           "note": ("dual report: identical frozen R5 predictions scored against (a) the gold "
                    "embedded in baseline_predictions.jsonl (R5, survey variance) and (b) the "
                    "corrected gold in nhanes_confirmatory.csv after the R11 smoking/alcohol "
                    "operationalization fixes (analysis_plan §0.3). NHANES tested=81 after "
                    "correction; the 1 new pair has no baseline predictions and is excluded "
                    "from both arms."),
           "metrics": {}}
    def agg(fx):
        d = {}
        for k2 in ("P", "R", "F1"):
            vals = [x[k2] for x in fx if x[k2] is not None]
            d[k2] = round(sum(vals) / len(vals), 3) if vals else None
        d["per_seed_F1"] = [x["F1"] for x in fx]
        return d

    for bl in ["full_system", "pure_llm", "naive_rag", "lightrag"]:
        f5 = [metrics(rs, {(r["a_flag"], r["b_item"]): r["gold3"] for r in rs}) for rs in runs[bl].values()]
        f11 = [metrics(rs, gold_r11) for rs in runs[bl].values()]
        out["metrics"][bl] = {"R5_gold": agg(f5), "R11_gold": agg(f11)}
    out["mcnemar_R11_gold"] = {}
    for bl in ["pure_llm", "naive_rag", "lightrag"]:
        ps = [mcnemar(runs["full_system"][s], runs[bl][s], gold_r11)["p_exact"]
              for s in sorted(runs["full_system"]) if s in runs[bl]]
        out["mcnemar_R11_gold"][bl] = {"p_exact_range": [float(min(ps)), float(max(ps))],
                                        "sig_at_005_any_seed": bool(min(ps) < 0.05)}
    path = OUT / "baseline_summary_R11_corrected_gold.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for bl, v in out["metrics"].items():
        print(f"{bl:12s} F1 R5gold={v['R5_gold']['F1']}  F1 R11gold={v['R11_gold']['F1']}")
    for bl, v in out["mcnemar_R11_gold"].items():
        print(f"McNemar full_system vs {bl} (R11 gold): {v}")
    print(f"[R11] → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
