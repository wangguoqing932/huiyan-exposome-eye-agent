#!/usr/bin/env python
"""M1(MUSTFIX 2026-10-16):合成效应注入回归——带已知真值的评估面。

动机:项目此前唯一的评估面(80 对/5 个信息性对)无统计功效,任何架构改动
都无法证明。本脚本在仿真数据上注入已知真值(OR 2.0 / 1.4 / 1.0 / 0.6),
走与确证层完全相同的统计链(statsmodels logit → evaluate.fdr_bhy → 三态标签),
校验:检出功效、假阳性控制、方向恢复。纯本地无 LLM,固定种子,可入 CI。

用法:
  PYTHONUTF8=1 python scripts/synthetic_regression.py            # 汇总落盘
  pytest tests/test_synthetic_regression.py                      # 断言门
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
sys.path.insert(0, str(ROOT / "src"))
from evaluate import fdr_bhy  # noqa: E402  确证层同一 FDR 实现

SEED = 20261016
SCENARIOS = [  # (真 OR, 对数, 期望行为)
    (2.0, 6, "strong"),
    (1.4, 8, "moderate"),
    (1.0, 8, "null"),
    (0.6, 4, "protective"),
]


def simulate(or_true: float, n: int, px: float, py0: float, seed: int):
    rng = np.random.default_rng(seed)
    x = rng.binomial(1, px, n)
    age = rng.normal(65, 10, n)
    sex = rng.binomial(1, 0.5, n)
    b0 = np.log(py0 / (1 - py0))
    lin = b0 + np.log(or_true) * x + 0.02 * (age - 65) + 0.10 * sex
    y = rng.binomial(1, 1 / (1 + np.exp(-lin)))
    return pd.DataFrame({"y": y, "x": x.astype(float), "age": age, "sex": sex})


def fit_or_p(df: pd.DataFrame) -> tuple[float, float]:
    X = sm.add_constant(df[["x", "age", "sex"]])
    m = sm.GLM(df["y"], X, family=sm.families.Binomial()).fit()
    return float(np.exp(m.params["x"])), float(m.pvalues["x"])


def three_state(or_hat: float, q: float, rule_dir: str = "risk_up") -> str:
    if q >= 0.05:
        return "uninformative"
    if rule_dir == "risk_up":
        return "replicated" if or_hat > 1 else "contradicted"
    return "replicated" if or_hat < 1 else "contradicted"


def run(n_per_pair: int = 6000) -> dict:
    rows = []
    seed = SEED
    for or_true, n_pairs, tag in SCENARIOS:
        for _ in range(n_pairs):
            seed += 1
            df = simulate(or_true, n_per_pair, px=0.25, py0=0.10, seed=seed)
            or_hat, p = fit_or_p(df)
            rows.append({"or_true": or_true, "tag": tag, "or_hat": or_hat, "p": p})
    res = pd.DataFrame(rows)
    res["q"] = fdr_bhy(res["p"])
    res["label"] = [three_state(o, q) for o, q in zip(res["or_hat"], res["q"])]

    def rate(mask, label):
        sub = res[mask]
        return (sub.label == label).mean() if len(sub) else None

    summary = {
        "seed": SEED, "n_pairs": len(res), "n_per_pair": n_per_pair,
        "power_or2_replicated": rate(res.tag == "strong", "replicated"),
        "power_or1_4_replicated": rate(res.tag == "moderate", "replicated"),
        "fpr_or1_replicated": rate(res.tag == "null", "replicated"),
        "protective_contradicted": rate(res.tag == "protective", "contradicted"),
        "null_contradicted": rate(res.tag == "null", "contradicted"),
        "median_or_hat_by_truth": {str(t): round(g.or_hat.median(), 3)
                                   for t, g in res.groupby("or_true")},
    }
    out = ROOT / "outputs" / "agent" / "synthetic_regression.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


if __name__ == "__main__":
    s = run()
    print(json.dumps(s, ensure_ascii=False, indent=1))
