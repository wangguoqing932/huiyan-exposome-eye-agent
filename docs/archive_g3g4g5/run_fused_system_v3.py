#!/usr/bin/env python
"""R6.0 fused system v3 (analysis_plan §15, pre-registered 2026-10-15):
semantic-retrieval evidence layer over the LightRAG vector store.

  G5a = rule hit (non-NC) -> semantic retrieval -> best relevant chunk >=B
        => YES; else LLM arbiter (as §13).
  G5b = G5a + evidence-only path: no rule hit -> if >=2 relevant chunks of
        level >=B whose annotations hit BOTH exposure and outcome flags ->
        strict arbiter (as §14) => YES/UNKNOWN.

Relevance: sim >= tau AND (annotation contains either flag OR text contains
both literature terms). tau prior 0.55 (main), sensitivity {0.45, 0.65}.

Usage: PYTHONUTF8=1 python scripts/run_fused_system_v3.py
"""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from huiyan_agent.risk_rules import load_rules, match_rules
from huiyan_agent.normalize import load_entity_a_registry, load_entity_b_registry
from huiyan_agent.llm_client import LLMClient
from huiyan_agent.semantic_retrieval import SemanticEvidenceIndex
from evaluate import get_judgeable_b_items
from literature_validation import A_FLAG_TERMS, B_FLAG_TERMS
from scipy import stats as st

OUTJ = ROOT / "outputs/confirmatory/fused_system_R6.jsonl"
OUTS = ROOT / "outputs/confirmatory/fused_system_R6_summary.json"
ARBITER_SEED = 20261015
LEVELS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}
TAU_MAIN = 0.55
TAU_SENS = [0.45, 0.65]


def main() -> int:
    rules = load_rules()
    by_id = {r.id: r for r in rules}
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = {}, {}
    for ent in a_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            a_idx.setdefault(str(f), ent)
    for ent in b_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            b_idx.setdefault(str(f), ent)

    idx = SemanticEvidenceIndex()
    arbiter = LLMClient(provider="local", temperature=0.0, seed=ARBITER_SEED)

    datasets = {
        "nhanes": ("outputs/confirmatory/nhanes_confirmatory.csv", "nhanes"),
        "knhanes": ("outputs/confirmatory/knhanes_confirmatory.csv", "knhanes"),
        "charls": ("outputs/confirmatory/charls_confirmatory.csv", "cohort"),
    }
    records = []
    per_ds = {}
    for ds, (csvp, key) in datasets.items():
        df = pd.read_csv(ROOT / csvp)
        tested = df[df["status"] == "tested"]
        judgeable = get_judgeable_b_items(key)
        rows = []
        for _, row in tested.iterrows():
            a_ent = a_idx.get(row["a_flag"])
            b_ent = b_idx.get(row["b_item"])
            sigs = match_rules(rules, a_ent, b_ent) if (a_ent and b_ent) else []
            hit_ids = [s.rule_id for s in sigs]
            is_nc = any(by_id[i].negative_control for i in hit_ids if i in by_id)
            a_terms = A_FLAG_TERMS.get(row["a_flag"], [row["a_flag"]])
            b_terms = B_FLAG_TERMS.get(row["b_item"], [row["b_item"]])
            query = f"{a_terms[0]} {b_terms[0]}"
            chunks = idx.search(query, top_k=8)

            rec = {"dataset": ds, "a_flag": row["a_flag"], "b_item": row["b_item"],
                   "gold3": row["gold3"], "judgeable": row["b_item"] in judgeable,
                   "rule_ids": ",".join(hit_ids), "negative_control": is_nc,
                   "G0": len(hit_ids) > 0}
            for tau in [TAU_MAIN] + TAU_SENS:
                rel = idx.filter_relevant(chunks, tau, row["a_flag"], row["b_item"],
                                          a_terms[0], b_terms[0])
                arm_a = f"G5a_{tau}"
                arm_b = f"G5b_{tau}"
                g5a, gate = False, "no_rule"
                if hit_ids and not is_nc:
                    if rel:
                        if max(LEVELS.get(c.level or "E", 0) for c in rel) >= LEVELS["B"]:
                            g5a, gate = True, "sem_evidence_Bplus"
                        else:
                            g5a, gate = arbiter_decide(arbiter, [c.text for c in rel[:3]],
                                                       a_terms, b_terms)
                    else:
                        gate = "sem_no_relevant"
                elif is_nc:
                    gate = "nc_abstain"
                g5b, gate_b = g5a, gate
                if not hit_ids:
                    dual = [c for c in rel
                            if LEVELS.get(c.level or "E", 0) >= LEVELS["B"]
                            and c.flag_a and c.flag_b
                            and row["a_flag"] in (c.flag_a or "")
                            and row["b_item"] in (c.flag_b or "")]
                    if len(dual) >= 2:
                        g5b, gate_b = strict_arbiter(arbiter, [c.text for c in dual[:3]],
                                                     a_terms, b_terms)
                    else:
                        gate_b = f"direct_threshold_not_met({len(dual)})"
                rec[arm_a] = g5a
                rec[f"gate_{arm_a}"] = gate
                rec[arm_b] = g5b
                rec[f"gate_{arm_b}"] = gate_b
            rec["top1_sim"] = round(chunks[0].sim, 3) if chunks else None
            rec["top1_level"] = chunks[0].level if chunks else None
            rows.append(rec)
        records += rows
        m = {}
        for arm in [f"G5a_{TAU_MAIN}", f"G5b_{TAU_MAIN}"] + \
                   [f"G5a_{t}" for t in TAU_SENS] + [f"G5b_{t}" for t in TAU_SENS]:
            j = [r for r in rows if r["judgeable"]]
            tp = sum(1 for r in j if r[arm] and r["gold3"] == "replicated")
            fp = sum(1 for r in j if r[arm] and r["gold3"] != "replicated")
            fn = sum(1 for r in j if not r[arm] and r["gold3"] == "replicated")
            p = tp / (tp + fp) if tp + fp else None
            rc = tp / (tp + fn) if tp + fn else None
            f1 = 2 * p * rc / (p + rc) if p and rc else 0.0
            m[arm] = {"TP": tp, "FP": fp, "FN": fn, "P": round(p, 3) if p else None,
                      "R": round(rc, 3) if rc else None, "F1": round(f1, 3)}
        per_ds[ds] = m

    with OUTJ.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    nh = [r for r in records if r["dataset"] == "nhanes" and r["judgeable"]]

    def mcn(arm_a, arm_b):
        b = sum(1 for r in nh if r[arm_a] and not r[arm_b])
        c = sum(1 for r in nh if not r[arm_a] and r[arm_b])
        n = b + c
        return {"b": b, "c": c,
                "p_exact": round(1.0 if n == 0 else min(1.0, 2 * st.binom.cdf(min(b, c), n, 0.5)), 5)}

    summary = {
        "date": "2026-10-15", "protocol": "analysis_plan §15 (pre-registered before run)",
        "tau_main": TAU_MAIN, "tau_sensitivity": TAU_SENS,
        "metrics_by_dataset": per_ds,
        "mcnemar_nhanes": {
            "G5b055_vs_G0": mcn("G5b_0.55", "G0"),
        },
        "records": len(records),
        "note": "G0/G2 reference numbers in prior summaries (§13/§14).",
    }
    OUTS.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"metrics_by_dataset": per_ds, "mcnemar_nhanes": summary["mcnemar_nhanes"]},
                     ensure_ascii=False, indent=1))
    return 0


def arbiter_decide(arbiter, texts, a_terms, b_terms):
    ctx = "\n\n".join(f"[EV{i}] {t[:800]}" for i, t in enumerate(texts, 1))
    try:
        resp = arbiter.complete(
            prompt=(f"Evidence chunks:\n{ctx}\n\nQuestion: does this evidence support that "
                    f"{a_terms[0]} is associated with {b_terms[0]}? Answer strictly YES or "
                    f"UNKNOWN on the first line."),
            system="You are a conservative evidence arbiter.", raise_on_error=True)
        first = (resp.text or "").strip().upper()
        return (True, "sem_arbiter_yes") if first.startswith("YES") else (False, "sem_arbiter_unknown")
    except Exception:
        return False, "sem_arbiter_error"


def strict_arbiter(arbiter, texts, a_terms, b_terms):
    ctx = "\n\n".join(f"[EV{i}] {t[:800]}" for i, t in enumerate(texts, 1))
    try:
        resp = arbiter.complete(
            prompt=(f"Evidence chunks:\n{ctx}\n\nQuestion: do these chunks EXPLICITLY report that "
                    f"{a_terms[0]} is associated with INCREASED risk of {b_terms[0]}? Answer YES only "
                    f"if at least one chunk explicitly reports such a positive association; otherwise "
                    f"UNKNOWN. First line: YES or UNKNOWN."),
            system="You are a strict evidence arbiter. Do not infer beyond the stated findings.",
            raise_on_error=True)
        first = (resp.text or "").strip().upper()
        return (True, "sem_direct_yes") if first.startswith("YES") else (False, "sem_direct_no")
    except Exception:
        return False, "sem_direct_error"


if __name__ == "__main__":
    sys.exit(main())
