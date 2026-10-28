#!/usr/bin/env python
"""R31 addendum P6 (pre-registered, sha256 aa749c7d…): agent-level evaluation on the
18 confirmatory (rule x cohort) cells across eight ageing cohorts.

Three arms, fixed before the run:
  G0  "assume transport": rule exists -> predict replicated (18/18)
  G2  population-conditioned evidence gate
  LLM one call per cell, fixed prompt

Output: outputs/confirmatory/r31_cohort_agent.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from huiyan_agent.evidence_store import EvidenceStore
from huiyan_agent.llm_client import LLMClient

A_TERMS = {
    "diabetes": ["hyperglycemia", "fasting glucose"],
    "smoking": ["smoking", "cigarette", "tobacco"],
    "bmi": ["body mass index", "obesity"],
    "alcohol": ["alcohol", "drinking"],
}
B_TERMS = {
    "cataract_any": ["cataract"],
    "amd_late": ["age-related macular degeneration", "macular degeneration"],
    "vi_mod_severe": ["vision impairment", "visual impairment"],
}
POP = {
    "HRS": ["united states", "usa", "u.s.", "american"],
    "ELSA": ["england", "english", "britain", "uk", "united kingdom"],
    "SHARE": ["europe", "european"],
    "KLoSA": ["korea", "korean"],
    "LASI": ["india", "indian"],
    "MHAS": ["mexico", "mexican"],
    "CLHLS": ["china", "chinese"],
    "CRELES": ["costa rica", "costa rican"],
}
LEVELS = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}


def main() -> int:
    df = pd.read_csv(ROOT / "outputs/cohorts/cohort_rule_results.csv")
    cells = df[(df.rule_relevant == True) & (df.family == "confirmatory")].copy()  # noqa: E712
    store = EvidenceStore()
    arb = LLMClient(provider="local", temperature=0.0, seed=20261015)
    llm_only = LLMClient(provider="local", temperature=0.0, seed=20261015)

    out = []
    for r in cells.itertuples():
        a_terms = A_TERMS.get(r.exposure, [r.exposure])
        b_terms = B_TERMS.get(r.outcome, [r.outcome])
        pops = POP.get(r.cohort, [r.cohort.lower()])
        query = " ".join(a_terms[:2] + b_terms[:2] + pops[:1])
        evs = store.retrieve(query, top_k=8)
        a_tok = a_terms[0].lower()
        b_tok = b_terms[0].lower()
        rel = []
        for e in evs:
            txt = (e.text or "").lower()
            if a_tok in txt and b_tok in txt and any(p in txt for p in pops):
                rel.append(e)
        if not rel:
            g2, gate = False, "no_population_evidence"
        else:
            best = max(LEVELS.get((e.evidence_level or "E").upper(), 0) for e in rel)
            if best >= LEVELS["B"]:
                g2, gate = True, "evidence_Bplus"
            else:
                ctx = store.build_context(rel[:3], char_limit=3000)
                try:
                    resp = arb.complete(
                        prompt=(f"Evidence chunks:\n{ctx}\n\nQuestion: does this evidence support that "
                                f"{a_terms[0]} increases {b_terms[0]} in {pops[0]}? Answer strictly "
                                f"YES or UNKNOWN on the first line."),
                        system="You are a conservative evidence arbiter. Output a single word.",
                        raise_on_error=True)
                    g2 = (resp.text or "").strip().upper().startswith("YES")
                    gate = "arbiter_yes" if g2 else "arbiter_unknown"
                except Exception as e:  # pragma: no cover
                    g2, gate = False, f"arbiter_error:{type(e).__name__}"
        # LLM-only arm, fixed prompt
        try:
            resp = llm_only.complete(
                prompt=(f"In {pops[0]}, does {a_terms[0]} increase the risk of {b_terms[0]}? "
                        f"Answer strictly YES or NO on the first line."),
                system="Answer as a conservative epidemiologist with one word.",
                raise_on_error=True)
            llm_pred = (resp.text or "").strip().upper().startswith("YES")
            llm_txt = (resp.text or "")[:80]
        except Exception as e:  # pragma: no cover
            llm_pred, llm_txt = False, f"error:{type(e).__name__}"
        out.append({"cohort": r.cohort, "rule_id": r.rule_id, "gold3": r.three_state,
                    "observed_or": float(r.odds_ratio), "n_evidence_hits": len(rel),
                    "G0": True, "G2": g2, "gate": gate, "LLM": llm_pred,
                    "llm_text": llm_txt})

    def score(key):
        rep = [c for c in out if c["gold3"] == "replicated"]
        con = [c for c in out if c["gold3"] == "contradicted"]
        uni = [c for c in out if c["gold3"] == "uninformative"]
        tp = sum(c[key] for c in rep)
        fp = sum(c[key] for c in uni + con)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / len(rep) if rep else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        return {"TP": tp, "FP": fp, "FN": len(rep) - tp,
                "recall_replicated": round(rec, 3),
                "flag_rate_contradicted": round(sum(c[key] for c in con) / len(con), 3) if con else None,
                "flag_rate_uninformative": round(sum(c[key] for c in uni) / len(uni), 3) if uni else None,
                "precision": round(prec, 3), "F1": round(f1, 3),
                "accuracy": round((tp + sum(not c[key] for c in con + uni)) / len(out), 3)}

    result = {"protocol": "docs/analysis_plan_R31_addendum.md P6, sha256 aa749c7d957d8fe775c81b070339221469e81379e0c097f2463dd74e75fa23ea",
              "unit": "18 confirmatory (rule x cohort) cells", "n": len(out),
              "gold": {"replicated": sum(c["gold3"] == "replicated" for c in out),
                       "contradicted": sum(c["gold3"] == "contradicted" for c in out),
                       "uninformative": sum(c["gold3"] == "uninformative" for c in out)},
              "arms": {"G0_assume_transport": score("G0"), "G2_population_gate": score("G2"),
                       "LLM_only": score("LLM")},
              "cells": out,
              "caveat": "the 18 observed states were already published at the rule level; this is a post hoc descriptive re-analysis, not a confirmatory test"}

    path = ROOT / "outputs/confirmatory/r31_cohort_agent.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({k: result[k] for k in ("n", "gold", "arms")}, indent=2, ensure_ascii=False))
    print("\ncells:")
    for c in out:
        print(f"  {c['cohort']:7s} {c['rule_id']:38s} {c['gold3']:14s} G2={c['G2']!s:5s} LLM={c['LLM']!s:5s} gate={c['gate']}")
    print("\nwrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
