#!/usr/bin/env python
"""R5.3 fused system v2 (analysis_plan §14, pre-registered 2026-10-15):
literature-consensus gating (G3) + evidence-only direct inference path (G4),
on top of the G2 evidence-gated system (§13).

  G3 = G2 + lit-verdict gate: hits of rules whose §12 literature verdict is
       contradicted_lit/mixed_lit abstain (uninformative_lit keeps speaking).
  G4 = G3 + evidence-only path: for pairs with NO rule hit, if >=2 chunks of
       level >=B match BOTH the exposure term and outcome term in text ->
       strict LLM arbiter (YES only on an explicit positive association).

Evaluation: judgeable scope, survey-variance gold, three datasets; McNemar
vs G0/G2 and the three LLM baselines. Output: fused_system_R53.jsonl +
fused_system_R53_summary.json.

Usage: PYTHONUTF8=1 python scripts/run_fused_system_v2.py
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
from huiyan_agent.evidence_store import EvidenceStore
from huiyan_agent.llm_client import LLMClient
from evaluate import get_judgeable_b_items
from literature_validation import A_FLAG_TERMS, B_FLAG_TERMS
from scipy import stats as st

OUTJ = ROOT / "outputs/confirmatory/fused_system_R53.jsonl"
OUTS = ROOT / "outputs/confirmatory/fused_system_R53_summary.json"
ARBITER_SEED = 20261015
LEVELS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}


def lit_verdicts() -> dict:
    s = json.loads((ROOT / "outputs/confirmatory/literature_validation_summary.json")
                   .read_text(encoding="utf-8"))
    out = {}
    for rid_full, v in s["verdicts"].items():
        out[rid_full] = v["verdict"]
    return out


def main() -> int:
    rules = load_rules()
    by_id = {r.id: r for r in rules}
    a_reg = load_entity_a_registry()
    b_reg = load_entity_b_registry()
    a_idx, b_idx = {}, {}
    a_name = {}
    for ent in a_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            a_idx.setdefault(str(f), ent)
            a_name.setdefault(str(f), ent.primary_name or str(f))
    b_name = {k: (v.generic_name or k) for k, v in b_reg.items()}
    for ent in b_reg.values():
        for f in (getattr(ent, "flags", None) or []):
            b_idx.setdefault(str(f), ent)
            b_name.setdefault(str(f), ent.generic_name or str(f))

    store = EvidenceStore()
    arbiter = LLMClient(provider="local", temperature=0.0, seed=ARBITER_SEED)
    lit = lit_verdicts()

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
            a_terms = A_FLAG_TERMS.get(row["a_flag"], [a_name.get(row["a_flag"], row["a_flag"])])
            b_terms = B_FLAG_TERMS.get(row["b_item"], [b_name.get(row["b_item"], row["b_item"])])

            # G0/G1/G2 re-derived (same logic as §13 v1 script)
            g0 = len(hit_ids) > 0
            g1 = g0 and not is_nc
            g2, gate = False, "no_rule"
            if g1:
                evs = store.retrieve(" ".join(a_terms[:2] + b_terms[:2]), top_k=5)
                a_tok, b_tok = a_terms[0].lower().split()[-1], b_terms[0].lower().split()[0]
                rel = [e for e in evs
                       if any(i in (e.entities_a or []) for i in hit_ids)
                       or (a_tok in e.text.lower() and b_tok in e.text.lower())]
                if not rel:
                    gate = "no_relevant_evidence"
                elif max(LEVELS.get((e.evidence_level or "E").upper(), 0) for e in rel) >= LEVELS["B"]:
                    g2, gate = True, "evidence_Bplus"
                else:
                    g2, gate = arbiter_decide(arbiter, store, rel, a_terms, b_terms)
            elif is_nc:
                gate = "nc_abstain"

            # G3: literature-consensus gate on rule hits
            g3, g3gate = g2, gate
            lit_bad = [i for i in hit_ids if lit.get(i) in ("contradicted_lit", "mixed_lit")]
            if g2 and lit_bad:
                g3 = False
                g3gate = f"lit_gate:{','.join(i.split('_')[0] for i in lit_bad)}"

            # G4: evidence-only direct path for no-rule pairs
            g4, g4gate = g3, g3gate
            if not g0:
                evs = store.retrieve(" ".join(a_terms[:2] + b_terms[:2]), top_k=8)
                a_tok, b_tok = a_terms[0].lower().split()[-1], b_terms[0].lower().split()[0]
                dual = [e for e in evs
                        if LEVELS.get((e.evidence_level or "E").upper(), 0) >= LEVELS["B"]
                        and a_tok in e.text.lower() and b_tok in e.text.lower()]
                if len(dual) >= 2:
                    g4, g4gate = strict_arbiter(arbiter, store, dual, a_terms, b_terms)

            rows.append({
                "dataset": ds, "a_flag": row["a_flag"], "b_item": row["b_item"],
                "gold3": row["gold3"], "judgeable": row["b_item"] in judgeable,
                "rule_ids": ",".join(hit_ids),
                "G0": g0, "G2": g2, "G3": g3, "G4": g4,
                "gate_G2": gate, "gate_G3": g3gate, "gate_G4": g4gate,
            })
        records += rows
        m = {}
        for arm in ("G0", "G2", "G3", "G4"):
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

    # McNemar on NHANES judgeable
    nh = [r for r in records if r["dataset"] == "nhanes" and r["judgeable"]]

    def mcn(arm_a, arm_b):
        b = sum(1 for r in nh if r[arm_a] and not r[arm_b])
        c = sum(1 for r in nh if not r[arm_a] and r[arm_b])
        n = b + c
        return {"b": b, "c": c,
                "p_exact": round(1.0 if n == 0 else min(1.0, 2 * st.binom.cdf(min(b, c), n, 0.5)), 5)}

    gates = defaultdict(int)
    for r in records:
        gates[r["gate_G4"]] += 1
    summary = {
        "date": "2026-10-15", "protocol": "analysis_plan §14 (pre-registered before run)",
        "metrics_by_dataset": per_ds,
        "mcnemar_nhanes": {"G3_vs_G2": mcn("G3", "G2"), "G4_vs_G2": mcn("G4", "G2"),
                           "G4_vs_G0": mcn("G4", "G0")},
        "gate_distribution_G4": dict(gates),
        "records": len(records),
    }
    OUTS.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in
                      ("metrics_by_dataset", "mcnemar_nhanes", "gate_distribution_G4")},
                     ensure_ascii=False, indent=1))
    return 0


def arbiter_decide(arbiter, store, rel, a_terms, b_terms):
    ctx = store.build_context(rel[:3], char_limit=3000)
    try:
        resp = arbiter.complete(
            prompt=(f"Evidence chunks:\n{ctx}\n\nQuestion: does this evidence support that "
                    f"{a_terms[0]} is associated with {b_terms[0]}? Answer strictly YES or "
                    f"UNKNOWN on the first line."),
            system="You are a conservative evidence arbiter.", raise_on_error=True)
        first = (resp.text or "").strip().upper()
        if first.startswith("YES"):
            return True, "arbiter_yes"
        return False, "arbiter_unknown"
    except Exception:
        return False, "arbiter_error"


def strict_arbiter(arbiter, store, dual, a_terms, b_terms):
    """G4 evidence-only path: YES only on an explicit positive association."""
    ctx = store.build_context(dual[:3], char_limit=3000)
    try:
        resp = arbiter.complete(
            prompt=(f"Evidence chunks:\n{ctx}\n\nQuestion: do these chunks EXPLICITLY report that "
                    f"{a_terms[0]} is associated with INCREASED risk of {b_terms[0]} (a positive "
                    f"association with statistical or mechanistic support)? Answer YES only if at "
                    f"least one chunk explicitly reports such a positive association; otherwise "
                    f"answer UNKNOWN. First line: YES or UNKNOWN."),
            system="You are a strict evidence arbiter. Do not infer beyond the stated findings.",
            raise_on_error=True)
        first = (resp.text or "").strip().upper()
        if first.startswith("YES"):
            return True, "direct_evidence_yes"
        return False, "direct_evidence_no"
    except Exception:
        return False, "direct_arbiter_error"


if __name__ == "__main__":
    sys.exit(main())
