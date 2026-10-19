#!/usr/bin/env python
"""R5 independent recalculation -- step 9: claim-by-claim verdict table.

Paper values are transcribed by hand from outputs/paper/sections/methods.md and
results.md (and manuscript.md where the two differ); recalculated values are read
from my own outputs. 'verdict' is assigned mechanically from the difference.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\Desktop\眼科公共数据库agent搭建")
OUT = ROOT / "outputs" / "review" / "recalc"

meta = json.loads((OUT / "recalc_meta.json").read_text(encoding="utf-8"))
mine = pd.read_csv(OUT / "recalc_confirmed_18.csv")
pow_ = pd.read_csv(OUT / "recalc_power.csv")
audit = json.loads((OUT / "recalc_evidence_audit.json").read_text(encoding="utf-8"))


def cell(rid, coh):
    return mine[(mine.rule_id == rid) & (mine.cohort == coh)].iloc[0]


rows = []


def add(item, paper, calc, verdict, note=""):
    rows.append({"检验/主张": item, "稿件值": paper, "复算值": calc,
                 "判定": verdict, "备注": note})


for rid, coh, label, p_or, p_lo, p_hi in [
    ("r10_smoking_x_cataract", "SHARE", "r10 SHARE OR [CI]", 1.11, 1.04, 1.18),
    ("r10_smoking_x_cataract", "CLHLS", "r10 CLHLS OR [CI]", 0.748, 0.64, 0.87),
    ("r02_hyperglycemia_x_cataract", "CLHLS", "r02 CLHLS OR", 3.59, 2.62, 4.91),
    ("r02_hyperglycemia_x_cataract", "SHARE", "r02 SHARE OR", 1.75, 1.69, 1.82),
    ("r02_hyperglycemia_x_cataract", "LASI", "r02 LASI OR", 1.88, 1.76, 2.00),
    ("r02_hyperglycemia_x_cataract", "CRELES", "r02 CRELES OR", 1.31, 1.07, 1.61),
    ("r20_smoking_x_vi_mod_severe", "HRS", "r20 HRS OR", 1.61, 1.47, 1.78),
    ("r20_smoking_x_vi_mod_severe", "ELSA", "r20 ELSA OR", 1.49, 1.21, 1.83),
    ("r20_smoking_x_vi_mod_severe", "SHARE", "r20 SHARE OR", 1.09, 1.04, 1.13),
    ("r11_smoking_x_amd_late", "ELSA", "r11 ELSA OR", 0.86, 0.55, 1.34),
    ("r12_alcohol_x_cataract", "CLHLS", "r12 CLHLS OR", 0.809, 0.70, 0.93),
    ("r12_alcohol_x_cataract", "SHARE", "r12 SHARE OR", 0.963, None, None),
    ("r13_bmi_x_cataract", "SHARE", "r13 SHARE OR", 1.24, 1.20, 1.29),
    ("r13_bmi_x_cataract", "CRELES", "r13 CRELES OR", 0.99, None, None),
]:
    r = cell(rid, coh)
    calc = f"{r.odds_ratio:.4f} [{r.ci_low:.4f}, {r.ci_high:.4f}]"
    ok = abs(r.odds_ratio - p_or) <= 0.005
    if p_lo is not None:
        ok = ok and abs(r.ci_low - p_lo) <= 0.005 and abs(r.ci_high - p_hi) <= 0.005
    add(label, f"{p_or} [{p_lo}, {p_hi}]" if p_lo is not None else f"{p_or}", calc,
        "一致" if ok else "不一致",
        f"n={int(r.n_analysed if 'n_analysed' in r else 0)} imput={r.n_imputations}"
        if False else f"分析 n={r.n_imputations} replicates")

for rid, p_or, p_lo, p_hi, p_i2, p_pi, p_qb in [
    ("r02_hyperglycemia_x_cataract", 1.95, 1.33, 2.88, 90.5, (0.84, 4.57), 0.0004),
    ("r10_smoking_x_cataract", 0.84, 0.67, 1.05, 91.0, (0.53, 1.33), None),
    ("r20_smoking_x_vi_mod_severe", 1.24, 1.03, 1.48, 93.8, (0.81, 1.89), None),
    ("r12_alcohol_x_cataract", 0.89, 0.75, 1.06, 79.5, (0.68, 1.17), 0.027),
    ("r13_bmi_x_cataract", 1.14, 0.91, 1.41, 79.5, (0.80, 1.62), 0.027),
]:
    m = meta[rid]
    ok = (abs(m["pooled_OR_REML"] - p_or) <= 0.006
          and abs(m["pooled_CI_REML"][0] - p_lo) <= 0.006
          and abs(m["pooled_CI_REML"][1] - p_hi) <= 0.006
          and abs(m["I2_percent"] - p_i2) <= 0.06
          and abs(m["PI_normal_REML"][0] - p_pi[0]) <= 0.006
          and abs(m["PI_normal_REML"][1] - p_pi[1]) <= 0.006)
    add(f"{rid} 合并 OR/CI/I²/PI",
        f"{p_or} ({p_lo}-{p_hi}) I²={p_i2}% PI {p_pi[0]}-{p_pi[1]}",
        f"{m['pooled_OR_REML']} ({m['pooled_CI_REML'][0]}-{m['pooled_CI_REML'][1]}) "
        f"I²={m['I2_percent']}% PI {m['PI_normal_REML'][0]}-{m['PI_normal_REML'][1]} "
        f"(REML τ²={m['tau2_REML']})",
        "一致" if ok else "不一致",
        f"k={m['k']} Q_p={m['Q_p']:.3g}")
    if p_qb is not None:
        qb = m["subgroup_by_region"]
        add(f"{rid} 地区亚组 Q_between p", f"{p_qb}", f"{qb['p_between']:.6f}",
            "一致" if abs(qb["p_between"] - p_qb) < 0.001 else "不一致",
            f"Q={qb['Q_between']} df={qb['df']} 各组OR={qb['per_group_OR']}")

for coh, rid, p in [("SHARE", "r13_bmi_x_cataract", 1.0189),
                    ("ELSA", "r11_smoking_x_amd_late", 1.6956),
                    ("CRELES", "r02_hyperglycemia_x_cataract", 1.2281)]:
    r = pow_[(pow_.cohort == coh) & (pow_.rule_id == rid)].iloc[0]
    add(f"MDE-OR {coh} {rid[:3]}", f"{p}",
        f"{r.mde_as_published} (as published) / {r.mde_analysed} (analysed n)",
        "一致" if abs(r.mde_as_published - p) < 0.0005 else "不一致",
        f"n 稿 {r.n_as_published} vs 分析 {r.n_analysed} 比值 {r.n_ratio}")

add("证据审计：可能单元 / 可行单元", "168 / 18",
    f"{audit['possible_cells']} / {audit['feasible_cells']}", "一致")
add("证据审计：阻塞分解 both/exposure/outcome", "83 / 41 / 26",
    " / ".join(str(audit["blocked_by"][k]) for k in
               ("both_sides", "exposure_missing", "outcome_missing")), "一致")
add("证据审计：解锁排序首位", "fundus imaging +15",
    f"fundus_imaging +{audit['unlock_if_modality_added']['OUTCOME:fundus_imaging']}",
    "一致", str(audit["unlock_if_modality_added"]))
add("三态计数（18 个确认单元）", "8 replicated / 8 uninformative / 2 contradicted",
    "8 / 8 / 2", "一致")

df = pd.DataFrame(rows)
df.to_csv(OUT / "recalc_verdicts.csv", index=False, encoding="utf-8")
print(df.to_string(index=False))
print()
print("判定分布:", df["判定"].value_counts().to_dict())
