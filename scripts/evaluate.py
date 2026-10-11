#!/usr/bin/env python
"""huiyan executor — confirmatory pair-level validation (C1/C2 methodology fix).

Implements docs/analysis_plan.md v1.0:
- Three-state gold labels (replicated / contradicted / uninformative)
- Rule-scoped precision (not global); type-2 gap recall only
- Direction-plausibility pre-audit (C4)
- Bootstrap 95% CI for all headline metrics (C7)
- Negative-control (r01) single-column reporting (C10)
- Unified covariates: age, age2/100, sex (C3)

Reads cases from data/datasets/<id>/cases.jsonl (B5 fix).
Engine independence (B8): uses huiyan_agent.risk_rules.match_rules/assess, not raw YAML.
"""
from __future__ import annotations
import json, math, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from huiyan_agent.risk_rules import load_rules, match_rules, assess
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry

# 审核 145：原为 warnings.filterwarnings("ignore")，把 statsmodels 的
# PerfectSeparationWarning / 收敛告警全部吞掉 → 分离伪影被静默记为 uninformative 或 replicated。
# 现只屏蔽噪声最大的两类，保留分离/收敛告警。
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels.tools.sm_exceptions",
                        message=".*convergence.*")
ROOT = Path(__file__).resolve().parent.parent

def fdr_bhy(p):
    """Benjamini-Yekutieli step-up FDR（analysis_plan.md §7 指定），含单调化。

    审核 141：原实现 `p*n/rank` 缺累积最小值步 → q 对 p 非单调
      （实测 bh([0.04,0.045]) = [0.08,0.045]：更大的 p 被判显著、更小的 p 不显著）。
    审核 148：原实现 `p.fillna(1.0)` 把退化拟合的 NaN p 静默变成"不显著"；此处保留 NaN。
    审核 F5：原实现亦非计划指定的 BHY。
    """
    p = pd.Series(p).astype(float)
    q = pd.Series(np.nan, index=p.index, dtype=float)
    pv = p.dropna()
    n = len(pv)
    if n:
        order = pv.sort_values(kind="mergesort")
        c_n = float(np.sum(1.0 / np.arange(1, n + 1)))  # BHY 因子
        ranked = order.to_numpy() * n * c_n / np.arange(1, n + 1)
        ranked = np.minimum.accumulate(ranked[::-1])[::-1]  # 单调化
        q.loc[order.index] = np.clip(ranked, 0.0, 1.0)
    return q

# 兼容旧调用点名称；语义自本轮起为 BHY（analysis_plan.md §7）
bh = fdr_bhy
bh_fdr = fdr_bhy

def bootstrap_ci(vals, n_boot=1000, seed=42):
    """对规则对的 gold3 标签做百分位 bootstrap。

    审核 142：原实现把 0/0 的 replicate 记为 0.0，使退化样本产出**零宽区间**
      （全 uninformative -> (0.0,0.0)；全 replicated -> (1.0,1.0)；单观测 -> (1.0,1.0)），
      且可与 precision_rule=None 并列出现 —— 等于用一个零宽区间为不存在的估计背书。
      现改为：无有效 replicate 时返回 (None, None)。
    审核 131：重采样单位是**对标签**而非患者，无法表示抽样不确定性。
      按人聚类重采样需先把患者 ID 贯穿到结果表（工单 WO-15，**尚未完成**）。
    """
    vals = np.asarray(vals, dtype=object)
    if len(vals) == 0:
        return (None, None)
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(n_boot):
        s = rng.choice(vals, size=len(vals), replace=True)
        rep = int((s == "replicated").sum()); con = int((s == "contradicted").sum())
        if rep + con > 0:
            samples.append(rep / (rep + con))
    if not samples:
        return (None, None)
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return (round(float(lo), 3), round(float(hi), 3))

def three_state(or_val, q_val, rule_dir="risk_up"):
    """三态金标准。审核 130/149：调用点此前从不传 rule_dir，且 OR==1 被判 contradicted。"""
    if not np.isfinite(q_val) or q_val >= 0.05:
        return "uninformative"
    if not np.isfinite(or_val) or abs(float(or_val) - 1.0) < 1e-9:
        return "uninformative"          # 无方向可言，不得算作 contradicted
    if rule_dir == "risk_down":
        return "replicated" if or_val < 1 else "contradicted"
    return "replicated" if or_val > 1 else "contradicted"

def compute_metrics(res):
    """确证指标。

    审核 141/C1-C2：原实现用 `a_flag.str.contains("uric_acid")` 子串兜底识别阴性对照，
    把整个 uric 系（3 对）剔出 headline，而非注册的唯一对照 r01；
    且 `type2_missed` 并未限定在预注册的类型 2 空白内。
    此处改为消费 run_pairs 记录的 `negative_control` 列（来自 rules.yaml 的字段），
    并把该计数按实际含义更名为 uncovered_significant。

    关于 sensitivity / recall：**本函数不报告召回率，这是有意的**。
    analysis_plan.md §1/§3 把 FN 限定在类型 2 空白（physical_activity × glaucoma_*），
    而该层在注册表中没有对应实体（entities_a.csv:32 的 flag 是 physical_inactivity），
    分母恒为 0 —— 指标不可识别。改为报告两个定义良好的量：
      precision_rule  已覆盖且可测的对中，方向被证实的比例
      coverage        已覆盖对数 / 全部可测对数（覆盖率本身才是本设计的诚实指标）
    若作者要恢复 sensitivity 语义，须先修订 analysis_plan（把 FN 定义在声明的覆盖域上，
    或扩大覆盖域），这是作者决策，不由代码替选。
    """
    t = res[res["status"] == "tested"].copy()
    if "negative_control" in t.columns:
        nc_mask = t["negative_control"].fillna(False).astype(bool)
    else:
        nc_mask = pd.Series(False, index=t.index)
    t_main = t[~nc_mask]
    t_nc = t[nc_mask]
    rp = t_main[t_main["predicted"]]
    replicated = int((rp["gold3"] == "replicated").sum())
    contradicted = int((rp["gold3"] == "contradicted").sum())
    uninformative = int((rp["gold3"] == "uninformative").sum())
    non_rule = t_main[~t_main["predicted"]]
    uncovered_sig = int((non_rule["gold3"] == "replicated").sum())
    prec = round(replicated / (replicated + contradicted), 3) if replicated + contradicted else None
    ci = bootstrap_ci(rp["gold3"].values) if len(rp) else (None, None)
    coverage = round(len(rp) / len(t_main), 3) if len(t_main) else None
    return {
        "rule_pairs_tested": len(rp), "replicated": replicated,
        "contradicted": contradicted, "uninformative": uninformative,
        "precision_rule": prec, "precision_rule_ci95": ci,
        "coverage": coverage,
        "uncovered_significant": uncovered_sig, "uncovered_pairs": len(non_rule),
        "negative_control_pairs": len(t_nc),
        "negative_control_outcome": t_nc["gold3"].value_counts().to_dict() if len(t_nc) else {},
    }

def _flag_index(reg):
    """flag -> entity 索引。

    审核 122：注册表以 exposure_id 为键，而 run_pairs 用 flag 查表，
    18 个暴露 flag 中只有 4 个碰巧同名，其余 14 个静默变成"无规则"。
    """
    idx = {}
    for ent in (reg or {}).values():
        for f in (getattr(ent, "flags", None) or []):
            idx.setdefault(str(f), ent)
    return idx

def run_pairs(df, expo_fn, outc_fn, covar_cols, weight_col, rules, a_reg, b_reg):
    E = expo_fn(df)
    B = outc_fn(df)
    cov = df[covar_cols].copy()
    a_idx, b_idx = _flag_index(a_reg), _flag_index(b_reg)
    results = []
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            # 审核 122：先按 flag 索引查，再回退到 id 键
            a_ent = a_idx.get(a_flag) or a_reg.get(a_flag)
            b_ent = b_idx.get(b_item) or b_reg.get(b_item)
            predicted = False
            rule_ids: list[str] = []
            is_neg_ctrl = False
            direction = "risk_up"
            if a_ent and b_ent:
                sigs = match_rules(rules, a_ent, b_ent)
                predicted = len(sigs) > 0
                rule_ids = [s.rule_id for s in sigs]
                by_id = {r.id: r for r in rules}
                hit = [by_id[i] for i in rule_ids if i in by_id]
                is_neg_ctrl = any(r.negative_control for r in hit)
                dirs = [r.direction for r in hit]
                direction = "risk_down" if dirs and all(d == "risk_down" for d in dirs) else "risk_up"
            meta = {"a_flag": a_flag, "b_item": b_item, "predicted": predicted,
                    "rule_ids": ",".join(rule_ids), "negative_control": is_neg_ctrl,
                    "direction": direction}
            sub = pd.DataFrame({"y": ovec, "x": evec}).join(cov).dropna()
            sub = sub[sub["y"].isin([0, 1]) & sub["x"].isin([0, 1])]
            ny = int(sub["y"].sum()); nx = int(sub["x"].sum())
            npos_ok = ny <= len(sub) - 30     # 恢复探索脚本的全阳结局守卫（审核 146）
            if len(sub) < 200 or ny < 30 or nx < 30 or not npos_ok:
                results.append({**meta, "n": len(sub), "n_pos": ny,
                                "or": np.nan, "p": np.nan, "status": "underpowered"})
                continue
            # 审核 144：.astype(float) 原在 try 之外，字符串型协变量会崩掉整轮
            try:
                X = sm.add_constant(sub[["x"] + covar_cols].astype(float))
                y = sub["y"].astype(float)
                # 审核 143：原 clip(lower=1) 在归一化前把 <1 的权重抹成 1
                w = df.loc[sub.index, weight_col].astype(float)
                w = w.where(w > 0, 1.0)
                w = w / w.mean()
                fit = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
                if not getattr(fit, "converged", True):
                    raise RuntimeError("fit not converged")
                beta = fit.params["x"]; se = fit.bse["x"]
                results.append({**meta, "n": len(sub), "n_pos": ny,
                                "or": math.exp(beta), "ci_lo": math.exp(beta - 1.96 * se),
                                "ci_hi": math.exp(beta + 1.96 * se), "p": float(fit.pvalues["x"]),
                                "status": "tested"})
            except Exception as ex:
                # 审核 145：原 except 不记录异常类型，分离/未收敛无法区分
                results.append({**meta, "n": len(sub), "n_pos": ny,
                                "or": np.nan, "p": np.nan,
                                "status": f"fit_fail:{type(ex).__name__}"})
    res = pd.DataFrame(results)
    m = res["status"] == "tested"
    res.loc[m, "q"] = bh(res.loc[m, "p"])
    # 审核 130：此前 three_state 从不接收 rule_dir，保护性规则会被判 contradicted（假阳性）
    res["gold3"] = res.apply(
        lambda r: three_state(r.get("or", np.nan), r.get("q", np.nan), r.get("direction", "risk_up"))
        if r["status"] == "tested" else "not_tested", axis=1)
    return res

def direction_audit(res, rules=None):
    """C4 方向前置审计：>=2 个**证据级 A** 的规则对方向相反 → 该库应进入 quarantine。

    审核 130/144：原实现 (a) 无任何调用点；(b) 未按自身 docstring 限定 A 级；
    (c) 把保护性方向（risk_down）也算作"反向"——而那恰恰是该规则被证实的表现。
    """
    lvl = {}
    for r in (rules or []):
        lvl[r.id] = r.evidence_level
    a_pairs = res[(res["predicted"]) & (res["status"] == "tested")].copy()
    if lvl and "rule_ids" in a_pairs.columns:
        def _is_a(ids):
            got = [lvl.get(i.strip()) for i in str(ids).split(",") if i.strip()]
            return bool(got) and all(g == "A" for g in got)
        a_pairs = a_pairs[a_pairs["rule_ids"].map(_is_a)]
    rev = a_pairs[(a_pairs["direction"] != "risk_down") & (a_pairs["or"] < 1)]
    return len(rev) >= 2, int(len(rev))

if __name__ == "__main__":
    print("Confirmatory pipeline ready (scripts/evaluate.py)")
    print("Run individual dataset scripts (phase5_*) then use compute_metrics()")
    print("Full integration: populate cases.jsonl then call run_pairs()")
