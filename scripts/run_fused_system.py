#!/usr/bin/env python
"""Fused evidence-gated inference (analysis_plan §13, pre-registered
2026-10-15 BEFORE any fused-system run).

Three pre-registered ablation arms:
  G0 bare rules      — rule hit ⇒ YES (current full_system; NC included)
  G1 NC-gated        — G0 + negative-control hits abstain
  G2 evidence-gated  — G1 + EvidenceStore confirmation for non-NC hits:
        >=B relevant chunk  ⇒ YES
        only C/D/E relevant ⇒ LLM arbiter (local qwen, temp=0, fixed seed)
        no relevant chunk   ⇒ UNKNOWN

Relevance (prior, no tuning): chunk.entities_a contains the hit rule id,
OR chunk text contains both the exposure term and the outcome term.

Evaluation: judgeable-scope pairs per dataset (NHANES main), survey-variance
gold3; G2 vs G0 paired McNemar. Output: outputs/confirmatory/fused_system_R5.jsonl
+ fused_system_summary.json.

Usage: PYTHONUTF8=1 python scripts/run_fused_system.py
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
from scipy import stats as st
# literature-standard search terms (same thesaurus as plan §12 / literature_validation.py —
# registry names carry operationalization suffixes that never match corpus text)
from literature_validation import A_FLAG_TERMS, B_FLAG_TERMS
from huiyan_agent.variable_map import outcome_alias
import yaml as _yaml
_VM = _yaml.safe_load((ROOT / "configs" / "variable_map.yaml").read_text(encoding="utf-8"))
B_ALIAS = outcome_alias(_VM)

OUTJ = ROOT / "outputs/confirmatory/fused_system_R5.jsonl"
OUTS = ROOT / "outputs/confirmatory/fused_system_summary.json"
ARBITER_SEED = 20261015
LEVELS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}


def flag_maps():
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
    return a_idx, b_idx, a_name, b_name


def main() -> int:
    rules = load_rules()
    by_id = {r.id: r for r in rules}
    a_idx, b_idx, a_name, b_name = flag_maps()
    store = EvidenceStore()
    arbiter = LLMClient(provider=__import__("os").environ.get("HUIYAN_LLM_PROVIDER", "local"), temperature=0.0, seed=ARBITER_SEED)

    datasets = {
        "nhanes": ("outputs/confirmatory/nhanes_confirmatory.csv", "nhanes"),
        "knhanes": ("outputs/confirmatory/knhanes_confirmatory.csv", "knhanes"),
        "charls": ("outputs/confirmatory/charls_confirmatory.csv", "cohort"),
    }
    records = []
    per_ds_metrics = {}
    for ds, (csvp, key) in datasets.items():
        df = pd.read_csv(ROOT / csvp)
        tested = df[df["status"] == "tested"]
        judgeable = get_judgeable_b_items(key)
        rows = []
        for _, row in tested.iterrows():
            # R31 P0b: G0 must be the confirmatory rule layer itself (CSV `predicted`),
            # not a re-implementation keyed on registry names — the CSVs use concept
            # names and outcome variants (hyperglycemia, cataract_dx, ...) that the
            # registry does not carry, which silently dropped 16/32 KNHANES hits.
            hit_ids = [s.strip() for s in str(row.get("rule_ids") or "").split(";")
                       if s.strip() and not s.strip().startswith("~")]
            is_nc = bool(row.get("negative_control")) or any(
                by_id[i].negative_control for i in hit_ids if i in by_id)
            g0 = bool(row.get("predicted"))
            g1 = g0 and not is_nc
            g2, gate, arb_note = False, "no_rule", ""
            if not g0:
                gate = "no_rule"
            elif is_nc:
                gate = "nc_abstain"
            else:
                # R31 P0c: outcome variants (cataract_dx, retinopathy_selfreport, ...)
                # must resolve to the canonical outcome before the term lookup; without
                # this the query degenerates to the literal item code, retrieves nothing,
                # and the gate abstains on true positives.
                b_key = B_ALIAS.get(str(row["b_item"]), row["b_item"])
                a_terms = A_FLAG_TERMS.get(row["a_flag"], [a_name.get(row["a_flag"], row["a_flag"])])
                b_terms = B_FLAG_TERMS.get(b_key, [b_name.get(b_key, b_key)])
                query = " ".join(a_terms[:2] + b_terms[:2])
                evs = store.retrieve(query, top_k=5)
                a_tok = a_terms[0].lower().split()[-1]
                b_tok = b_terms[0].lower().split()[0]
                rel = [e for e in evs
                       if any(i in (e.entities_a or []) for i in hit_ids)
                       or (a_tok in e.text.lower() and b_tok in e.text.lower())]
                if not rel:
                    gate = "no_relevant_evidence"
                else:
                    best = max(LEVELS.get((e.evidence_level or "E").upper(), 0) for e in rel)
                    if best >= LEVELS["B"]:
                        g2, gate = True, f"evidence_Bplus"
                    else:
                        ctx = store.build_context(rel[:3], char_limit=3000)
                        try:
                            resp = arbiter.complete(
                                prompt=(f"Evidence chunks:\n{ctx}\n\nQuestion: does this evidence support "
                                        f"that {a_terms[0]} is associated with {b_terms[0]}? Answer strictly "
                                        f"YES or UNKNOWN on the first line."),
                                system="You are a conservative evidence arbiter. Output strict JSON-free single word.",
                                raise_on_error=True)
                            first = (resp.text or "").strip().upper()
                            if first.startswith("YES"):
                                g2, gate = True, "arbiter_yes"
                                arb_note = first[:80]
                            else:
                                gate = f"arbiter_unknown"
                                arb_note = first[:80]
                        except Exception as e:
                            gate = f"arbiter_error:{type(e).__name__}"
                if g2:
                    pass
            rows.append({
                "dataset": ds, "a_flag": row["a_flag"], "b_item": row["b_item"],
                "gold3": row["gold3"], "judgeable": row["b_item"] in judgeable,
                "rule_ids": ",".join(hit_ids), "negative_control": is_nc,
                "G0": g0, "G1": g1, "G2": g2, "gate": gate, "arbiter_note": arb_note,
            })
        records += rows
        m = {}
        for arm in ("G0", "G1", "G2"):
            j = [r for r in rows if r["judgeable"]]
            tp = sum(1 for r in j if r[arm] and r["gold3"] == "replicated")
            fp = sum(1 for r in j if r[arm] and r["gold3"] != "replicated")
            fn = sum(1 for r in j if not r[arm] and r["gold3"] == "replicated")
            p = tp / (tp + fp) if tp + fp else None
            rc = tp / (tp + fn) if tp + fn else None
            f1 = 2 * p * rc / (p + rc) if p and rc else 0.0
            m[arm] = {"TP": tp, "FP": fp, "FN": fn, "P": round(p, 3) if p else None,
                      "R": round(rc, 3) if rc else None, "F1": round(f1, 3)}
        per_ds_metrics[ds] = m

    with OUTJ.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # McNemar G2 vs G0 on NHANES judgeable scope
    nh = [r for r in records if r["dataset"] == "nhanes" and r["judgeable"]]
    b = sum(1 for r in nh if r["G2"] and not r["G0"])
    c = sum(1 for r in nh if not r["G2"] and r["G0"])
    n = b + c
    p_mcn = 1.0 if n == 0 else min(1.0, 2 * st.binom.cdf(min(b, c), n, 0.5))

    gates = defaultdict(int)
    for r in records:
        gates[r["gate"]] += 1
    summary = {
        "date": "2026-10-15", "protocol": "analysis_plan §13 (pre-registered before run)",
        "arbiter": "local qwen3.8-27b, thinking disabled, temp=0.0, seed=20261015",
        "evaluation_scope": "judgeable pairs per dataset; survey-variance gold3",
        "metrics_by_dataset": per_ds_metrics,
        "mcnemar_G2_vs_G0_nhanes": {"b_g2_yes_g0_no": b, "c_g2_no_g0_yes": c, "p_exact": round(p_mcn, 5)},
        "gate_distribution": dict(gates),
        "records": len(records),
    }
    OUTS.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in
                      ("metrics_by_dataset", "mcnemar_G2_vs_G0_nhanes", "gate_distribution")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
