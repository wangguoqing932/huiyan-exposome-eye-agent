#!/usr/bin/env python
"""Phase 4 专家盲评分析:读取问卷答案,计算 Cohen κ(系统 vs 每位专家)
与 Fleiss κ(专家间),输出 skill 验收判定。

用法:
  PYTHONUTF8=1 python scripts/phase4_kappa.py --input outputs/expert_review/phase4_answers.json

输入 JSON 格式(每份问卷一条):
{
  "expert_id": 1,
  "answers": [
    {"case": 1,  "A": "Y", "B": "M", "C": 4},
    ...
  ]
}
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

# ── 系统的"金标准"答案(盲评对照面,不告知专家)──────────────────
# A: Y=确立 P=可能 U=不确定 N=否
# B: H/M/L 风险程度
SYSTEM_ANSWERS = {
    1:  {"a_flag": "hyperglycemia", "b_item": "cataract_any",
         "system_A": "Y", "system_B": "M", "rule": "r02",
         "gold3": "replicated", "gold_note": "NHANES survey OR=1.58"},
    2:  {"a_flag": "hba1c_elevated", "b_item": "retinopathy_any",
         "system_A": "Y", "system_B": "M", "rule": "r03",
         "gold3": "replicated", "gold_note": "NHANES survey OR=5.92"},
    3:  {"a_flag": "current_smoking", "b_item": "cataract_any",
         "system_A": "Y", "system_B": "H", "rule": "r10",
         "gold3": "uninformative", "gold_note": "NHANES 二分口径 null(文献 A 级)"},
    4:  {"a_flag": "bmi_high", "b_item": "cataract_any",
         "system_A": "Y", "system_B": "M", "rule": "r13",
         "gold3": "uninformative", "gold_note": "NHANES 二分 null;KNHANES per-SD q=0.0014"},
    5:  {"a_flag": "uric_acid_elevated", "b_item": "cataract_any",
         "system_A": "N", "system_B": "L", "rule": "r01(负控)",
         "gold3": "uninformative", "gold_note": "负控:如预期不显著"},
    6:  {"a_flag": "dyslipidemia", "b_item": "amd_late",
         "system_A": "Y", "system_B": "L", "rule": "r05",
         "gold3": "uninformative", "gold_note": "NHANES null;文献混合"},
    7:  {"a_flag": "crp_elevated", "b_item": "amd_late",
         "system_A": "Y", "system_B": "M", "rule": "r06",
         "gold3": "uninformative", "gold_note": "NHANES null;文献偏阳性"},
    8:  {"a_flag": "uric_acid_elevated", "b_item": "vision_impairment_moderate",
         "system_A": "N", "system_B": "L", "rule": "(无规则)",
         "gold3": "uninformative", "gold_note": "系统沉默(TN)"},
    9:  {"a_flag": "current_smoking", "b_item": "vision_impairment_moderate",
         "system_A": "Y", "system_B": "H", "rule": "r20",
         "gold3": "uninformative", "gold_note": "NHANES null;8 队列 3/5 复证"},
    10: {"a_flag": "alcohol_intake", "b_item": "cataract_any",
         "system_A": "Y", "system_B": "L", "rule": "r12",
         "gold3": "uninformative", "gold_note": "NHANES/KNHANES/前瞻 null"},
}


def cohen_kappa(r1: list, r2: list) -> float:
    """Cohen κ for two raters (same categories)."""
    n = len(r1)
    cats = sorted(set(r1) | set(r2))
    idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    m = np.zeros((k, k))
    for a, b in zip(r1, r2):
        m[idx[a], idx[b]] += 1
    po = np.trace(m) / n
    pe = sum(m[i, :].sum() / n * m[:, i].sum() / n for i in range(k))
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def fleiss_kappa(matrix: np.ndarray) -> float:
    """Fleiss κ. matrix: n_items × n_categories (counts per rater)."""
    n_items, n_cats = matrix.shape
    n_raters = matrix[0, :].sum()
    p_j = matrix.sum(axis=0) / (n_items * n_raters)
    p_i = ((matrix ** 2).sum(axis=1) - n_raters) / (n_raters * (n_raters - 1))
    p_bar = p_i.mean()
    p_e_bar = sum(p ** 2 for p in p_j)
    return (p_bar - p_e_bar) / (1 - p_e_bar) if p_e_bar < 1 else 1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSON 文件路径(可含多位专家)")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]  # 单专家

    experts = {d["expert_id"]: {int(a["case"]): a for a in d["answers"]} for d in data}
    n_experts = len(experts)
    print(f"\n专家数: {n_experts}")

    # ── Cohen κ(系统 vs 每位专家, 问题 A)───────────────────────
    results = {"per_expert": {}, "summary": {}}
    for eid, answers in sorted(experts.items()):
        sys_A = [SYSTEM_ANSWERS[c]["system_A"] for c in sorted(SYSTEM_ANSWERS)]
        exp_A = [answers.get(c, {}).get("A", "U") for c in sorted(SYSTEM_ANSWERS)]
        kap = cohen_kappa(sys_A, exp_A)
        agree = sum(1 for a, b in zip(sys_A, exp_A) if a == b) / len(sys_A)
        # 问题 B 的 κ(仅对双方都非 N/U 的案例)
        sys_B = [SYSTEM_ANSWERS[c]["system_B"] for c in sorted(SYSTEM_ANSWERS)
                 if SYSTEM_ANSWERS[c]["system_A"] in ("Y", "P")]
        exp_B = [answers.get(c, {}).get("B", "L") for c in sorted(SYSTEM_ANSWERS)
                 if SYSTEM_ANSWERS[c]["system_A"] in ("Y", "P")]
        kap_B = cohen_kappa(sys_B, exp_B) if len(sys_B) >= 3 else None
        # Likert
        likerts = [answers.get(c, {}).get("C") for c in sorted(SYSTEM_ANSWERS) if answers.get(c, {}).get("C")]
        likert_mean = sum(likerts) / len(likerts) if likerts else None
        results["per_expert"][eid] = {
            "kappa_A": round(float(kap), 3), "agreement_A": round(float(agree), 3),
            "kappa_B": round(float(kap_B), 3) if kap_B is not None else None,
            "likert_usefulness_mean": likert_mean,
            "pass_kappa_ge_06": bool(kap >= 0.6),
            "pass_likert_ge_4": bool(likert_mean is not None and likert_mean >= 4),
        }
        print(f"  专家 {eid}: κ(A)={kap:.3f} 一致率={agree:.1%} "
              f"κ(B)={kap_B if kap_B is not None else '—'} "
              f"Likert={likert_mean:.1f}/5 "
              f"{'✓' if kap >= 0.6 else '✗'}κ {'✓' if likert_mean and likert_mean >= 4 else '✗'}L")

    # ── Fleiss κ(专家间, 问题 A)───────────────────────────────
    if n_experts >= 2:
        cats = sorted({a.get("A", "U") for e in experts.values() for a in e.values()})
        n_cases = len(SYSTEM_ANSWERS)
        matrix = np.zeros((n_cases, len(cats)))
        for eid, answers in experts.items():
            for ci, case_num in enumerate(sorted(SYSTEM_ANSWERS)):
                r = answers.get(case_num, {}).get("A", "U")
                matrix[ci, cats.index(r)] += 1
        fk = fleiss_kappa(matrix)
        results["summary"]["fleiss_kappa_A"] = round(fk, 3)
        results["summary"]["fleiss_pass_ge_06"] = bool(fk >= 0.6)
        print(f"\n  Fleiss κ(专家间, A): {fk:.3f} {'✓' if fk >= 0.6 else '✗'}(门槛 0.6)")

    # ── 汇总判定─────────────────────────────────────────────
    all_pass = all(v["pass_kappa_ge_06"] for v in results["per_expert"].values())
    likert_pass = all(v["pass_likert_ge_4"] for v in results["per_expert"].values())
    fleiss_pass = results.get("summary", {}).get("fleiss_pass_ge_06", None)
    results["summary"]["phase4_pass"] = bool(all_pass and likert_pass and
                                             (fleiss_pass in (None, True) or fleiss_pass))
    print(f"\n  Phase 4 判定: {'✅ PASS' if results['summary']['phase4_pass'] else '❌ FAIL'}")
    print(f"    κ≥0.6: {'✓' if all_pass else '✗'} | Likert≥4: {'✓' if likert_pass else '✗'}"
          f" | Fleiss≥0.6: {fleiss_pass}")

    # 逐案对照(供论文报告)
    detail = []
    for c in sorted(SYSTEM_ANSWERS):
        s = SYSTEM_ANSWERS[c]
        row = {"case": c, "pair": f"{s['a_flag']}×{s['b_item']}",
               "system_A": s["system_A"], "system_B": s["system_B"],
               "gold3": s["gold3"]}
        for eid in sorted(experts):
            a = experts[eid].get(c, {})
            row[f"expert{eid}_A"] = a.get("A", "?")
            row[f"expert{eid}_B"] = a.get("B", "—")
            row[f"expert{eid}_C"] = a.get("C", "—")
        detail.append(row)
    results["case_detail"] = detail

    out = ROOT / "outputs" / "expert_review" / "phase4_kappa_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1, default=lambda o: bool(o) if isinstance(o, (np.bool_,)) else str(o)), encoding="utf-8")
    print(f"\n[写盘] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
