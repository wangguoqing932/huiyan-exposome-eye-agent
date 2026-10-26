#!/usr/bin/env python
"""R15:per-dataset 基线汇总(skill v3.0 偏离 2 修复)+ skill 模板指标(偏离 1 修复)。

偏离 2:四基线 × 每个验证数据集。KNHANES 层产物 = baseline_predictions_knhanes.jsonl
  (追加式;**同一 (baseline, provider, seed) 取最新一段完整 run**——位置法,M11 代际纪律)。
偏离 1:skill 模板指标 sens / spec / Cohen κ(skill 的 Phase2/3 验收口径),按
  "系统 YES/NO vs gold replicated(+)/其他(−)" 计算;4 级准确率声明为 N/A
  (金标准为三态关联标签,不存在四级风险金标准——如实注记,不硬造)。

NHANES 层:复用冻结 jsonl(seed=11,与既有 R13 口径一致)。
CHARLS 层:full_system 直接取 confirmatory.csv 的 predicted 列(规则引擎,无 LLM)。

Run: PYTHONUTF8=1 python scripts/per_dataset_summary_R15.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pandas as pd
from scipy import stats as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def prf_tp_fp_fn(preds, golds):
    tp = sum(1 for p, g in zip(preds, golds) if p and g)
    fp = sum(1 for p, g in zip(preds, golds) if p and not g)
    fn = sum(1 for p, g in zip(preds, golds) if not p and g)
    tn = sum(1 for p, g in zip(preds, golds) if not p and not g)
    sens = tp / (tp + fn) if tp + fn else None
    spec = tn / (tn + fp) if tn + fp else None
    prec = tp / (tp + fp) if tp + fp else None
    f1 = (2 * prec * sens / (prec + sens)) if prec and sens else (0.0 if tp == 0 else None)
    # Cohen κ(二值)
    kappa = None
    if len(set(preds)) > 1 and len(set(golds)) > 1:
        # Cohen κ 手写(scipy 无此函数,免 sklearn 依赖):
        # κ = (po − pe) / (1 − pe)
        n_ = len(preds)
        po = sum(1 for p, g in zip(preds, golds) if bool(p) == bool(g)) / n_
        pp = sum(1 for p in preds if p) / n_
        gp = sum(1 for g in golds if g) / n_
        pe = pp * gp + (1 - pp) * (1 - gp)
        kappa = round((po - pe) / (1 - pe), 3) if pe < 1 else None
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "sens": None if sens is None else round(sens, 3),
            "spec": None if spec is None else round(spec, 3),
            "precision": None if prec is None else round(prec, 3),
            "F1": None if f1 is None else round(f1, 3),
            "kappa": None if kappa is None else round(kappa, 3)}


def latest_runs_knhanes():
    """(baseline, provider, seed) → 最新一段连续 run(位置法取末段)。"""
    path = ROOT / "outputs" / "baseline_predictions_knhanes.jsonl"
    if not path.exists():
        return {}
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    # M11 代际纪律:同 key 多代 run 时取【末尾一个完整长度段】(本层段长=301;
    # 旧代无效行若与之相邻也不得连坐)。段长取该 key 出现次数最多的计数。
    RUN_LEN = 301  # 本层单代 run 长度(evaluate 矩阵 tested 数)
    by_key: dict = {}
    for r in rows:
        by_key.setdefault((r["baseline"], str(r.get("provider", "?")), r["seed"]), []).append(r)
    out = {}
    for key, seg in by_key.items():
        # 末尾连续有效块 = 该 key 最新一代 run;若两代皆有效且相邻(系统定义变更
        # 后重跑),按单代长度(本层众数 301)截断取最新一代
        tail: list = []
        for r in reversed(seg):
            if r.get("valid", True):
                tail.append(r)
            else:
                break
        tail.reverse()
        if len(tail) > RUN_LEN:
            tail = tail[-RUN_LEN:]
        if len(tail) >= 70:
            out[key] = tail
    return out


def main() -> int:
    results = []
    # ── NHANES(冻结 jsonl seed=11,qwen 代 + full_system)──
    recs = [json.loads(l) for l in
            (ROOT / "outputs/baseline_predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    for bl in ["full_system", "pure_llm", "naive_rag", "lightrag"]:
        rows = [r for r in recs if r["baseline"] == bl and r["seed"] == 11 and r.get("valid", True)]
        golds = [r["gold3"] == "replicated" for r in rows]
        preds = [bool(r["prediction"]) for r in rows]
        m = prf_tp_fp_fn(preds, golds)
        m.update({"dataset": "nhanes", "method": bl,
                  "provider": rows[0].get("provider", "?"), "n": len(rows)})
        results.append(m)
    # ── KNHANES(zhipu 代)──
    runs = latest_runs_knhanes()
    for (bl, prov, seed), rows in sorted(runs.items()):
        golds = [r["gold3"] == "replicated" for r in rows]
        preds = [bool(r["prediction"]) for r in rows]
        m = prf_tp_fp_fn(preds, golds)
        m.update({"dataset": "knhanes", "method": bl, "provider": prov,
                  "seed": seed, "n": len(rows)})
        results.append(m)
    # ── CHARLS(full_system 规则档,confirmatory 直取)──
    try:
        d = pd.read_csv(ROOT / "outputs/confirmatory/charls_confirmatory.csv", encoding="utf-8-sig")
        d = d[d.status == "tested"]
        golds = [g == "replicated" for g in d.gold3]
        preds = [bool(p) for p in d.predicted]
        m = prf_tp_fp_fn(preds, golds)
        m.update({"dataset": "charls", "method": "full_system",
                  "provider": "rule_engine:deterministic", "n": len(d)})
        results.append(m)
    except Exception as e:  # noqa: BLE001
        print("[charls] skip:", e)

    df = pd.DataFrame(results)
    cols = ["dataset", "method", "provider", "seed", "n", "sens", "spec",
            "precision", "F1", "kappa", "TP", "FP", "FN", "TN"]
    df = df[[c for c in cols if c in df.columns]]
    out = ROOT / "outputs/tables/skill_template_metrics.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(df.to_string(index=False))
    note = {
        "four_level_accuracy": "N/A——金标准为三态关联标签,无四级风险金标准;强行构造将循环。skill 模板的其余指标(sens/spec/κ)已按原义计算。",
        "pass_bars": {"phase2": "sens>=0.70, spec>=0.60", "phase3": "sens>=0.70, spec>=0.80"},
    }
    (ROOT / "outputs/tables/skill_template_metrics_note.json").write_text(
        json.dumps(note, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[写盘] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
