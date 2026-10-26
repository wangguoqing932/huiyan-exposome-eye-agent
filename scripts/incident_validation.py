#!/usr/bin/env python
"""多波队列前瞻(新发)验证层 —— R14(2026-10-20)。

设计(预注册式,先落盘后运行):
  1. 逐队列逐结局:基线 = 首个结局非缺失且=0、暴露非缺失的波;
     新发 = 之后任一波(间隔≥1波)结局=1;末次仍=0 为非病例(删失于末次观测)。
     基线已患病者( prevalent case )剔除——这是与横断面层的本质区别。
  2. 暴露取基线波测量(吸烟/饮酒/糖尿病/BMI≥25),协变量 age/sex(基线)。
  3. 模型:logistic(是否新发);效应量 OR≈风险比近似,报告随访波数中位数。
  4. 三态标签:BHY q 在本层全族内校正;q<0.05 且与规则方向同向=replicated,
     反向=contradicted,否则 uninformative。规则方向全部 risk_up。
  5. 对照输出:与横断面层( outputs/cohorts/cohort_rule_results.csv )逐对并列,
     检验"横断面方向反转是否在新发层消失"(反向因果预测)。

Run: PYTHONUTF8=1 python scripts/incident_validation.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate import fdr_bhy  # noqa: E402

FR = ROOT / "data" / "frames"
OUT = ROOT / "outputs" / "cohorts"
MIN_AGE = 40

# (队列, 暴露列, 结局列, 规则) —— 与横断面层可测集一致;方向全 risk_up
TESTS = [
    ("SHARE", "current_smoking", "cataract_any", "r10"),
    ("SHARE", "alcohol_intake", "cataract_any", "r12"),
    ("SHARE", "diabetes", "cataract_any", "r02"),
    ("SHARE", "bmi_high_25", "cataract_any", "r13"),
    ("SHARE", "current_smoking", "vision_impairment_moderate", "r20"),
    ("ELSA", "current_smoking", "cataract_any", "r10"),
    ("ELSA", "current_smoking", "amd_any", "r11"),
    ("ELSA", "current_smoking", "vision_impairment_moderate", "r20"),
    ("KLoSA", "current_smoking", "cataract_surgery", "r10"),
    ("KLoSA", "diabetes", "cataract_surgery", "r02"),
    ("KLoSA", "bmi_high_25", "cataract_surgery", "r13"),
    ("CLHLS", "current_smoking", "cataract_any", "r10"),
    ("CLHLS", "alcohol_intake", "cataract_any", "r12"),
    ("CLHLS", "diabetes", "cataract_any", "r02"),
    ("CLHLS", "current_smoking", "vision_impairment_moderate", "r20"),
]


def build_incident(d: pd.DataFrame, exposure: str, outcome: str):
    """返回基线一行/人的分析框:incident∈{0,1} + 基线协变量。"""
    need = ["mergeid", "wave", outcome, exposure, "age", "sex"]
    d = d[need].copy()
    for c in (outcome, exposure, "age", "sex"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["age"] >= MIN_AGE]
    d = d.sort_values(["mergeid", "wave"])
    # 有效性:结局非缺失;基线=首个结局==0 且暴露非缺失的波
    obs = d.dropna(subset=[outcome])
    base = (obs[obs[outcome] == 0]
            .dropna(subset=[exposure, "age", "sex"])
            .groupby("mergeid", as_index=False).first())
    if base.empty:
        return base
    # 新发:基线波之后任一非缺失结局==1
    later = obs.merge(base[["mergeid", "wave"]].rename(columns={"wave": "bw"}),
                      on="mergeid")
    later = later[later["wave"] > later["bw"]]
    inc = later.groupby("mergeid")[outcome].max().rename("incident")
    fw = later.groupby("mergeid")["wave"].max().rename("last_wave")
    out = base.merge(inc, on="mergeid", how="left").merge(fw, on="mergeid", how="left")
    out["incident"] = out["incident"].fillna(0.0)
    out["follow_waves"] = out["last_wave"] - out["wave"]
    return out[(out["follow_waves"] >= 1)]


def main() -> int:
    frames = {c: pd.read_csv(FR / f"cohort_{c}.csv", low_memory=False)
              for c in {t[0] for t in TESTS}}
    rows = []
    for cohort, expo, outc, rule in TESTS:
        d = frames[cohort]
        if expo not in d.columns or outc not in d.columns:
            rows.append({"cohort": cohort, "rule": rule, "exposure": expo,
                         "outcome": outc, "status": "variables_missing"})
            continue
        an = build_incident(d, expo, outc)
        if len(an) < 200 or an["incident"].sum() < 30:
            rows.append({"cohort": cohort, "rule": rule, "exposure": expo,
                         "outcome": outc, "status": "underpowered",
                         "n": len(an), "n_incident": int(an["incident"].sum())})
            continue
        X = sm.add_constant(pd.DataFrame({
            "x": an[expo].astype(float), "age": an["age"], "sex": an["sex"]}))
        y = an["incident"].astype(float)
        try:
            m = sm.GLM(y, X, family=sm.families.Binomial()).fit()
        except Exception as e:  # noqa: BLE001
            rows.append({"cohort": cohort, "rule": rule, "exposure": expo,
                         "outcome": outc, "status": f"fit_failed:{type(e).__name__}",
                         "n": len(an), "n_incident": int(y.sum())})
            continue
        rows.append({
            "cohort": cohort, "rule": rule, "exposure": expo, "outcome": outc,
            "status": "tested",
            "n": len(an), "n_incident": int(y.sum()),
            "n_exposed": int(an[expo].sum()),
            "incident_rate": round(float(y.mean()), 4),
            "median_follow_waves": float(an["follow_waves"].median()),
            "or": float(np.exp(m.params["x"])),
            "ci_low": float(np.exp(m.conf_int().loc["x", 0])),
            "ci_high": float(np.exp(m.conf_int().loc["x", 1])),
            "p": float(m.pvalues["x"]),
        })
        print(f"[incident] {cohort} {rule} {expo}->{outc}: n={len(an)} "
              f"inc={int(y.sum())} OR={rows[-1]['or']:.2f} p={rows[-1]['p']:.3g}")
    res = pd.DataFrame(rows)
    tested = res[res.status == "tested"].copy()
    if len(tested):
        tested["q"] = fdr_bhy(tested["p"])
        tested["three_state"] = np.where(
            tested["q"] >= 0.05, "uninformative",
            np.where(tested["or"] > 1, "replicated", "contradicted"))
        res = pd.concat([tested, res[res.status != "tested"]], ignore_index=True)
    OUT.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT / "incident_results.csv", index=False, encoding="utf-8-sig")
    from collections import Counter
    summary = {
        "date": "2026-10-20 (R14)",
        "design": ("baseline disease-free by self-report at first measured wave; "
                   "incident = any later wave reports diagnosis; exposure at baseline; "
                   "logistic, covariates age+sex; BHY q within this layer; all rules risk_up"),
        "n_tests": len(res),
        "status_counts": dict(Counter(res.status)),
        "three_state_counts": dict(Counter(tested["three_state"])) if len(tested) else {},
        "per_rule": {r: {"states": dict(Counter(g["three_state"])),
                          "ors": [round(x, 2) for x in g["or"]]}
                     for r, g in (tested.groupby("rule") if len(tested) else [])},
    }
    (OUT / "incident_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
