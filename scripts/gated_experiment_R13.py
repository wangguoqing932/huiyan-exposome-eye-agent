#!/usr/bin/env python
"""R13 方向A 实测:测量感知弃权能否提升系统性能(2026-10-16)。

纪律:
1. 门控策略只用【测量手段/功效元数据】(结局变量来自问卷还是检查、
   阳性事件数 n_pos),不接触 gold3 标签——防止测试集拟合;
2. 公平:同一门控套用在全部方法(full_system / pure_llm / naive_rag /
   lightrag / G2 融合)的冻结预测上;
3. abstain 在保守口径下记 NO(不缩分母),同时报告选择性预测口径
   (发言率 + 发言内 precision/recall)。

策略:
  P0        无门控(基线)
  P1_selfreport  结局测量=自报 → 弃权(按 variable_map 的结局变量族判定)
  P2_construct   规则构造要求该库不存在的仪器(如 IOP/CDR 无眼压计时)→ 弃权
  P3_power       结局阳性事件 n_pos<30(该管道自身的 underpowered 阈值)→ 弃权
  P1P3           P1+P3 组合

Run: PYTHONUTF8=1 python scripts/gated_experiment_R13.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "outputs" / "agent" / "optimization_R13"
OUT.mkdir(parents=True, exist_ok=True)

# ── 结局测量模态(仅由 variable_map 的变量名判定:VIQ/DH=问卷自报,
#    OPD/E_/OPX=检查分级,VID/E_VS/视标=测量)——不看 gold ──────────────
SELFREPORT_PREFIX = ("VIQ", "DH2", "DH3", "KIQ")

def outcome_modality(b_item: str, dataset: str, vm: dict) -> str:
    spec = (vm["outcomes"].get(b_item) or {})
    entry = spec.get(dataset) or {}
    names = set()

    def walk(n):
        if isinstance(n, str):
            import re
            names.update(re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", n))
        elif isinstance(n, dict):
            for v in n.values(): walk(v)
        elif isinstance(n, (list, tuple)):
            for v in n: walk(v)
    walk(entry)
    if not names:
        return "unknown"
    if any(n.startswith(SELFREPORT_PREFIX) for n in names) and not any(
            n.startswith(("OPD", "OPX", "VID", "E_")) for n in names):
        return "selfreport"
    return "exam_or_measured"


# 规则构造→仪器要求(b_flag 语义;IOP/CDR 需要眼压计/视盘成像)
CONSTRUCT_NEEDS = {
    "glaucoma_iop_elevated": {"instrument": "tonometry", "present_in": {"knhanes"}},
    "glaucoma_suspect_cdr": {"instrument": "optic_disc_imaging", "present_in": {"knhanes"}},
    "dr_npdr": {"instrument": "fundus_grading", "present_in": {"nhanes", "knhanes"}},
    "dr_pdr": {"instrument": "fundus_grading", "present_in": {"nhanes", "knhanes"}},
}


def gate(policy: str, a: str, b: str, dataset: str, modality: str, n_pos) -> bool:
    """True=允许发言,False=弃权。"""
    if policy == "P0":
        return True
    if policy in ("P1_selfreport", "P1P3"):
        if modality == "selfreport":
            return False
    if policy in ("P2_construct",):
        need = CONSTRUCT_NEEDS.get(b)
        if need and dataset not in need["present_in"]:
            return False
    if policy in ("P3_power", "P1P3"):
        try:
            if n_pos is None or pd.isna(n_pos) or float(n_pos) < 30:
                return False
        except (TypeError, ValueError):
            return False
    return True


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if tp == 0 else None)
    return p, r, f


def main() -> int:
    vm = yaml.safe_load((ROOT / "configs" / "variable_map.yaml").read_text(encoding="utf-8"))
    gold_rows = []  # (dataset,a,b,gold3,predicted_by_rules,n_pos,modality)
    for ds, csv_name, key in [("nhanes", "nhanes_confirmatory.csv", "nhanes"),
                              ("knhanes", "knhanes_confirmatory.csv", "knhanes")]:
        d = pd.read_csv(ROOT / "outputs" / "confirmatory" / csv_name, encoding="utf-8-sig")
        d = d[d.status == "tested"]
        for r in d.itertuples():
            if not isinstance(r.gold3, str) or not r.gold3:
                continue
            gold_rows.append({
                "dataset": key, "a": r.a_flag, "b": r.b_item, "gold3": r.gold3,
                "pred_rule": bool(r.predicted),
                "n_pos": getattr(r, "n_pos", None),
                "modality": outcome_modality(r.b_item, key, vm),
            })
    # 冻结预测(基线 jsonl seed=11 + G2)
    recs = [json.loads(l) for l in
            (ROOT / "outputs" / "baseline_predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    methods = {}
    for bl in ["full_system", "pure_llm", "naive_rag", "lightrag"]:
        methods[bl] = {(r["a_flag"], r["b_item"]): r["prediction"]
                       for r in recs if r["baseline"] == bl and r["seed"] == 11}
    fused = [json.loads(l) for l in
             (ROOT / "outputs" / "confirmatory" / "fused_system_R53.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    methods["G2"] = {(r["dataset"], r["a_flag"], r["b_item"]): str(r.get("G2", "")).lower() == "true"
                     for r in fused if str(r.get("judgeable", "")).lower() == "true"}

    rows_meta = {(g["dataset"], g["a"], g["b"]): g for g in gold_rows}
    results = {}
    for policy in ["P0", "P1_selfreport", "P2_construct", "P3_power", "P1P3"]:
        results[policy] = {}
        for mname, preds in methods.items():
            tp = fp = fn = spoken = spoken_tp = spoken_pos = 0
            for g in gold_rows:
                key = (g["dataset"], g["a"], g["b"])
                pred = preds.get((g["dataset"], g["a"], g["b"])) if mname == "G2"                     else preds.get((g["a"], g["b"]))
                if pred is None:
                    continue
                allow = gate(policy, g["a"], g["b"], g["dataset"], g["modality"], g["n_pos"])
                eff = bool(pred) and allow  # 弃权在保守口径=NO
                if eff:
                    spoken += 1
                if g["gold3"] == "replicated":
                    if eff:
                        tp += 1; spoken_tp += 1
                    else:
                        fn += 1
                    if eff or pred:
                        spoken_pos += (1 if eff else 0)
                elif eff:
                    fp += 1
            p, r, f = prf(tp, fp, fn)
            gold_pos = sum(1 for g in gold_rows if g["gold3"] == "replicated")
            results[policy][mname] = {
                "TP": tp, "FP": fp, "FN": fn,
                "P": round(p, 3) if p is not None else None,
                "R": round(r, 3) if r is not None else None,
                "F1": round(f, 3) if f is not None else None,
                "speak_rate": round(spoken / len(gold_rows), 3),
            }
    OUT.joinpath("gating_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    hdr = f"{'policy':14s} " + " ".join(f"{m:>22s}" for m in methods)
    print(hdr)
    for policy, per in results.items():
        cells = []
        for m in methods:
            v = per[m]
            cells.append(f"F1={v['F1']} P={v['P']} sp={v['speak_rate']}")
        print(f"{policy:14s} " + " ".join(f"{c:>22s}" for c in cells))
    print(f"\n[写盘] {OUT/'gating_results.json'}")


    # McNemar(full_system vs lightrag),逐策略,弃权=NO 口径
    from scipy import stats as st
    mcn = {}
    for policy in results:
        pf, pl = methods["full_system"], methods["lightrag"]
        b_ = c_ = 0
        for g in gold_rows:
            k = (g["a"], g["b"])
            if k not in pf or k not in pl:
                continue
            allow = gate(policy, g["a"], g["b"], g["dataset"], g["modality"], g["n_pos"])
            f_yes = bool(pf[k]) and allow
            l_yes = bool(pl[k]) and allow
            if f_yes and not l_yes: b_ += 1
            if l_yes and not f_yes: c_ += 1
        n = b_ + c_
        pv = 1.0 if n == 0 else min(1.0, 2 * st.binom.cdf(min(b_, c_), n, 0.5))
        mcn[policy] = {"b_full_lightrag": b_, "c_lightrag_full": c_, "p_exact": round(pv, 4)}
        print(f"McNemar[{policy}] full vs lightrag: b={b_} c={c_} p={pv:.4f}")
    OUT.joinpath("mcnemar_full_vs_lightrag.json").write_text(
        json.dumps(mcn, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
