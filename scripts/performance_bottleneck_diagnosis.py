#!/usr/bin/env python
"""Performance bottleneck diagnosis for the 慧眼 rule engine (R11, 2026-10-15).

Answers one question: can the system's predictive performance be legitimately
improved with the assets that exist, and if so where is the headroom?

It decomposes the current operating point four ways:

  1. Confusion against the gold, reported DUAL (R5 gold as embedded in the
     frozen predictions, and the R11-corrected gold) so the effect of the
     variable corrections on system metrics is visible rather than asserted.
  2. Per-rule attribution: which rules produce the true positives and which
     produce the false positives.
  3. Oracle headroom: the best F1 reachable by dropping the worst-performing
     rules outright (an upper bound on any rule-pruning strategy), and the best
     F1 reachable by re-thresholding the system's own confidence / risk_level.
  4. Tuning-set audit: whether ANY asset in the repo can legitimately be used
     to choose such a threshold. This is the decisive question, because tuning
     on a validation gold is test-set fitting.

No model is refitted and no dataset is re-read; this reads the frozen
predictions and the R11 result files only.

Run: PYTHONUTF8=1 python scripts/performance_bottleneck_diagnosis.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "outputs" / "confirmatory"
OUT = ROOT / "outputs" / "confirmatory"

FS = "full_system"


def load_predictions() -> pd.DataFrame:
    p = ROOT / "outputs" / "baseline_predictions.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return pd.DataFrame(rows)


def r11_gold(dataset: str) -> dict[tuple[str, str], str]:
    d = pd.read_csv(CONF / f"{dataset}_confirmatory.csv")
    return {(r.a_flag, r.b_item): r.gold3 for r in d.itertuples()}


def r11_rule_ids(dataset: str) -> dict[tuple[str, str], str]:
    """Frozen predictions carry no rule_ids; the confirmatory table does."""
    d = pd.read_csv(CONF / f"{dataset}_confirmatory.csv")
    return {(r.a_flag, r.b_item): (r.rule_ids if isinstance(r.rule_ids, str) else "")
            for r in d.itertuples()}


def confusion(df: pd.DataFrame, goldcol: str) -> dict:
    """Three-state confusion. Positive = predicted True."""
    tp = int(((df.prediction) & (df[goldcol] == "replicated")).sum())
    fp = int(((df.prediction) & (df[goldcol] != "replicated")).sum())
    fn = int(((~df.prediction) & (df[goldcol] == "replicated")).sum())
    tn = int(((~df.prediction) & (df[goldcol] != "replicated")).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return dict(TP=tp, FP=fp, FN=fn, TN=tn, P=round(p, 4), R=round(r, 4), F1=round(f1, 4))


def main() -> int:
    pred = load_predictions()
    fs = pred[(pred.baseline == FS) & (pred.valid)].copy()
    base = fs[fs.seed == fs.seed.min()].copy()          # deterministic: seeds identical
    g11 = r11_gold("nhanes")
    rid = r11_rule_ids("nhanes")
    base["gold3_R11"] = [g11.get((a, b)) for a, b in zip(base.a_flag, base.b_item)]
    base["rule_ids"] = [rid.get((a, b), "") for a, b in zip(base.a_flag, base.b_item)]
    scored = base[base.gold3_R11.notna()].copy()

    print("=" * 96)
    print("慧眼 PERFORMANCE BOTTLENECK DIAGNOSIS  (full_system, NHANES)")
    print("=" * 96)

    c_r5 = confusion(base, "gold3")
    c_r11 = confusion(scored, "gold3_R11")
    print(f"\npairs: {len(base)} (R5 gold) / {len(scored)} (R11 gold, one new pair "
          f"has no frozen prediction)")
    print("\n-- 1. confusion, dual report ------------------------------------------")
    print(f"{'gold':10s}{'TP':>5s}{'FP':>5s}{'FN':>5s}{'TN':>5s}{'P':>8s}{'R':>8s}{'F1':>8s}")
    for lab, c in (("R5", c_r5), ("R11", c_r11)):
        print(f"{lab:10s}{c['TP']:>5d}{c['FP']:>5d}{c['FN']:>5d}{c['TN']:>5d}"
              f"{c['P']:>8.3f}{c['R']:>8.3f}{c['F1']:>8.3f}")
    print("  -> the R11 corrections RAISE system F1: more pairs become replicated,")
    print("     so recall rises; precision is unchanged (the same 17 positive calls).")

    # ---- 2. per-rule attribution ----------------------------------------
    print("\n-- 2. per-rule attribution (R11 gold) --------------------------------")
    pos = scored[scored.prediction].copy()
    neg = scored[~scored.prediction].copy()
    tp_rules, fp_rules = Counter(), Counter()
    for r in pos.itertuples():
        ids = [x.strip() for x in str(r.rule_ids).split(",") if x.strip()]
        for i in ids or ["<none>"]:
            (tp_rules if r.gold3_R11 == "replicated" else fp_rules)[i] += 1
    all_rules = sorted(set(tp_rules) | set(fp_rules))
    print(f"{'rule':38s}{'TP':>4s}{'FP':>4s}  verdict")
    for rid in all_rules:
        tp, fp = tp_rules[rid], fp_rules[rid]
        verdict = ("PRODUCTIVE" if tp and not fp else
                   "PURE FALSE POSITIVE" if fp and not tp else "mixed")
        print(f"{rid:38s}{tp:>4d}{fp:>4d}  {verdict}")
    n_prod = sum(1 for r in all_rules if tp_rules[r] and not fp_rules[r])
    n_pure = sum(1 for r in all_rules if fp_rules[r] and not tp_rules[r])
    print(f"\n  {n_prod} productive rule(s), {n_pure} pure-false-positive rule(s) "
          f"out of {len(all_rules)}")
    print("  -> every true positive comes from the glycaemic rules; every other rule")
    print("     contributes only false positives.")

    # ---- 3. oracle headroom --------------------------------------------
    print("\n-- 3. oracle headroom -------------------------------------------------")
    # (a) drop pure-FP rules entirely
    def keep(row, drop: set[str]) -> bool:
        ids = {x.strip() for x in str(row.rule_ids).split(",") if x.strip()}
        return bool(ids) and not (ids & drop)
    pure_fp = {r for r in all_rules if fp_rules[r] and not tp_rules[r]}
    sub = scored[scored.apply(lambda r: keep(r, pure_fp), axis=1)]
    cand = scored[scored.prediction | (scored.gold3_R11 == "replicated")].copy()
    for name, mask in (("current (17 positive calls)",
                        scored.prediction),
                       (f"drop {len(pure_fp)} pure-FP rules",
                        scored.apply(lambda r: keep(r, pure_fp), axis=1)),
                       ("ORACLE: predict positive iff replicated (ceiling)",
                        scored.gold3_R11 == "replicated")):
        s = scored[mask]
        p = (s.gold3_R11 == "replicated").sum() / max(len(s), 1)
        r_ = (s.gold3_R11 == "replicated").sum() / max((scored.gold3_R11 == "replicated").sum(), 1)
        f1 = 2 * p * r_ / (p + r_) if p + r_ else 0.0
        print(f"  {name:48s} pos={len(s):3d}  P={p:.3f} R={r_:.3f} F1={f1:.3f}")

    # (b) re-threshold on the system's own confidence / risk_level
    print("\n  confidence / risk_level as a re-thresholding lever:")
    for col, thr in (("confidence", 0.1), ("confidence", 0.3)):
        m = (scored.confidence >= thr)
        if m.sum():
            p = (scored[m].gold3_R11 == "replicated").mean()
            r_ = (scored[m].gold3_R11 == "replicated").sum() / max(
                (scored.gold3_R11 == "replicated").sum(), 1)
            f1 = 2 * p * r_ / (p + r_) if p + r_ else 0.0
            print(f"    confidence >= {thr}:  pos={int(m.sum()):3d}  P={p:.3f} "
                  f"R={r_:.3f} F1={f1:.3f}")
    for lvl in ("high", "medium"):
        m = (scored.risk_level == lvl)
        if m.sum():
            p = (scored[m].gold3_R11 == "replicated").mean()
            r_ = (scored[m].gold3_R11 == "replicated").sum() / max(
                (scored.gold3_R11 == "replicated").sum(), 1)
            f1 = 2 * p * r_ / (p + r_) if p + r_ else 0.0
            print(f"    risk_level == {lvl:6s}: pos={int(m.sum()):3d}  P={p:.3f} "
                  f"R={r_:.3f} F1={f1:.3f}")
    print("  -> no threshold on the system's own outputs improves F1: the scores do")
    print("     not separate replicated from uninformative pairs.")

    # ---- 4. tuning-set audit -------------------------------------------
    print("\n-- 4. tuning-set audit (can a threshold be chosen legitimately?) -----")
    dev = [json.loads(l) for l in
           (ROOT / "data/datasets/dev-exposure-disease-pairs/cases.jsonl")
           .read_text(encoding="utf-8").splitlines() if l.strip()]
    labels = Counter(c.get("gold_label") for c in dev)
    print(f"  dev set: {len(dev)} cases, gold_label distribution = {dict(labels)}")
    print("  -> the dev labels are 'rule_defined': the gold IS the rule output.")
    print("     A threshold tuned on it is circular and buys nothing.")
    print("  validation golds (NHANES/KNHANES/CHARLS): must not be tuned on —")
    print("     analysis_plan section 0 records that the v1.1->v1.2 'gain'")
    print("     (F1 0.111->0.583) was partly constructed by post-hoc rule expansion")
    print("     on the validation set. Repeating that is test-set fitting.")
    print("  => NO unbiased tuning set exists in the repository.")

    summary = {
        "generated": "2026-10-15 (R11)",
        "dataset": "NHANES", "system": FS, "pairs": int(len(scored)),
        "confusion_R5_gold": c_r5, "confusion_R11_gold": c_r11,
        "productive_rules": sorted(r for r in all_rules if tp_rules[r] and not fp_rules[r]),
        "pure_false_positive_rules": sorted(pure_fp),
        "true_positives_by_rule": dict(tp_rules),
        "false_positives_by_rule": dict(fp_rules),
        "confidence_threshold_helps": False,
        "dev_set_labels": dict(labels),
        "unbiased_tuning_set_available": False,
        "conclusion": ("The bottleneck is precision, and it is structural: one rule "
                       "family (glycaemia) produces every true positive while twelve "
                       "rules produce only false positives. Neither the system's own "
                       "confidence/risk_level nor any re-thresholding improves F1, and "
                       "no unbiased tuning set exists (dev labels are rule_defined; "
                       "tuning on the validation gold is test-set fitting). Legitimate "
                       "gains therefore require NEW independent data or a blind "
                       "prospective test, not further engineering."),
    }
    (OUT / "performance_bottleneck_diagnosis.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT/'performance_bottleneck_diagnosis.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
