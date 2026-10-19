#!/usr/bin/env python
"""R13 方向B 实测:per-SD 连续通道能否挽回被切点埋没的信号(2026-10-16)。

数据:outputs/confirmatory/dose_response_matrix.csv(每 1SD OR,survey svyglm,
同二分层协变量,FDR 分族)× 冻结的系统预测(baseline jsonl seed=11)× 二分层 gold。

三种金标准口径:
  binary   现行主口径(切点二分暴露)
  per_sd   连续口径(per-SD 显著且方向一致 → replicated)
  union    双通道并集(任一通道 replicated → replicated;反证取任一通道 contradicted)
报告各口径下 full_system 的 TP/FP/FN/P/R/F1,以及 FP→TP 转化清单。

Run: PYTHONUTF8=1 python scripts/persd_experiment_R13.py
"""
from __future__ import annotations
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "agent" / "optimization_R13"


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if tp == 0 else None)
    return p, r, f


def main() -> int:
    dr = pd.read_csv(ROOT / "outputs/confirmatory/dose_response_matrix.csv",
                     encoding="utf-8-sig")
    recs = [json.loads(l) for l in
            (ROOT / "outputs/baseline_predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    preds = {(r["a_flag"], r["b_item"]): r["prediction"] for r in recs
             if r["baseline"] == "full_system" and r["seed"] == 11}
    # 逐库现行二分 gold
    bin_gold = {}
    for ds, f in [("nhanes", "nhanes_confirmatory.csv"), ("knhanes", "knhanes_confirmatory.csv")]:
        d = pd.read_csv(ROOT / "outputs" / "confirmatory" / f, encoding="utf-8-sig")
        d = d[d.status == "tested"]
        for r in d.itertuples():
            if isinstance(r.gold3, str) and r.gold3:
                bin_gold[(ds, r.a_flag, r.b_item)] = r.gold3

    # per-SD gold(只对规则相关对;binary_flag 即规则暴露 flag)
    per_sd_gold = {}
    for r in dr[dr.is_rule_pair == True].itertuples():  # noqa: E712
        ds = r.dataset
        sig = (r.q_primary < 0.05) if pd.notna(r.q_primary) else False
        if sig and r.direction_match == "concordant":
            g = "replicated"
        elif sig and str(r.direction_match) == "discordant":
            g = "contradicted"
        else:
            g = "uninformative"
        per_sd_gold[(ds, r.binary_flag, r.b_item)] = g

    rows = []
    for (ds, a, b), bg in bin_gold.items():
        if (a, b) not in preds:
            continue
        sg = per_sd_gold.get((ds, a, b))
        if sg is None:
            continue  # 无 per-SD 行(暴露无连续变量)
        ug = bg
        if sg == "replicated" or bg == "replicated":
            ug = "replicated"
        elif sg == "contradicted" or bg == "contradicted":
            ug = "contradicted" if not (sg == "replicated" or bg == "replicated") else "replicated"
        rows.append({"ds": ds, "a": a, "b": b, "pred": bool(preds[(a, b)]),
                     "gold_binary": bg, "gold_persd": sg, "gold_union": ug})
    df = pd.DataFrame(rows)
    res, flips = {}, []
    for name, col in [("binary", "gold_binary"), ("per_sd", "gold_persd"), ("union", "gold_union")]:
        tp = int(((df.pred) & (df[col] == "replicated")).sum())
        fp = int(((df.pred) & (df[col] != "replicated")).sum())
        fn = int((~df.pred) & (df[col] == "replicated")).sum() if False else int(((~df.pred) & (df[col] == "replicated")).sum())
        p, r_, f = prf(tp, fp, fn)
        res[name] = {"TP": tp, "FP": fp, "FN": fn,
                     "P": round(p, 3) if p else None, "R": round(r_, 3) if r_ else None,
                     "F1": round(f, 3) if f is not None else None}
    for r in df.itertuples():
        if r.pred and r.gold_binary == "uninformative" and r.gold_persd == "replicated":
            flips.append({"ds": r.ds, "pair": f"{r.a} x {r.b}", "verdict": "FP→TP 候选(per-SD 复现)"})
        if r.pred and r.gold_binary == "replicated" and r.gold_persd == "contradicted":
            flips.append({"ds": r.ds, "pair": f"{r.a} x {r.b}", "verdict": "TP 风险(per-SD 反向!)"})

    out = {"n_pairs_with_both_channels": len(df), "metrics_full_system": res,
           "flips": flips,
           "note": "union=任一通道 replicated 即 replicated;per-SD 层已含 FDR(q_primary)"}
    OUT.mkdir(parents=True, exist_ok=True)
    OUT.joinpath("persd_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
