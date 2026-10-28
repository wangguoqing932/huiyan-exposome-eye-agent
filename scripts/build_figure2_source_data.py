#!/usr/bin/env python
"""Build the Figure 2 source data from the R31 artifacts.

Panels
  a  external F1 by method, all 301 KNHANES pairs vs the 296 revision-free pairs
  b  gate decisions over the 474 pairs of the fused run
  c  replicated pairs by provenance (touched / clean) for the development matrix
     (NHANES) and the external matrix (KNHANES)
  d  three-state flag decomposition of G0 and G2 on the 301 pairs
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "outputs" / "confirmatory"
OUT = ROOT / "outputs" / "figures" / "source_data" / "figure2_performance.csv"

rows = []

h = json.loads((CONF / "r31_holdout.json").read_text(encoding="utf-8"))
for block, scope in (("P2_knhanes_full", "301 pairs"), ("P2_knhanes_clean", "296 revision-free pairs")):
    b = h[block]
    for arm, label in (("G2", "agent (G2)"), ("G0", "rule layer (G0)")):
        m = b["arms"][arm]["binary"]
        rows.append(dict(panel="a", group=label, series=scope, value=m["F1"],
                         n=b["n_pairs"], detail=f"P {m['P']:.3f} / R {m['R']:.3f}"))
    for bl, label in (("lightrag", "LightRAG"), ("pure_llm", "pure LLM"), ("naive_rag", "naive RAG")):
        m = b["baselines"][bl]
        rows.append(dict(panel="a", group=label, series=scope, value=m["F1_mean"],
                         n=b["n_pairs"], detail=f"range {m['F1_range'][0]:.3f}-{m['F1_range'][1]:.3f} over 5 seeds"))

s = json.loads((CONF / "fused_system_summary.json").read_text(encoding="utf-8"))
gates = s["gate_distribution"]
gate_labels = {
    "no_rule": "no rule fires",
    "evidence_Bplus": "evidence >= B confirms",
    "arbiter_yes": "LLM arbiter: yes",
    "nc_abstain": "negative-control abstain",
    "no_relevant_evidence": "no relevant evidence",
}
total = sum(gates.values())
for k, v in sorted(gates.items(), key=lambda kv: -kv[1]):
    rows.append(dict(panel="b", group=gate_labels.get(k, k), series="474 pairs",
                     value=v, n=total, detail=f"{v / total:.1%}"))

p1 = h["P1_internal"]
rows.append(dict(panel="c", group="NHANES (development)", series="touched by revision",
                 value=p1["n_replicated_touched"], n=p1["n_replicated"],
                 detail=f"all {p1['n_replicated']} replicated pairs; {p1['clean_subset_positives']} clean"))
rows.append(dict(panel="c", group="NHANES (development)", series="clean",
                 value=p1["clean_subset_positives"], n=p1["n_replicated"],
                 detail="no contamination-free positive"))
clean_rep = h["P2_knhanes_clean"]["arms"]["G0"]["three_state"]["n_replicated"]
touched_rep = h["P2_knhanes_full"]["arms"]["G0"]["three_state"]["n_replicated"] - clean_rep
rows.append(dict(panel="c", group="KNHANES (external)", series="touched by revision",
                 value=touched_rep, n=18, detail="5 replicated pairs on revised rules"))
rows.append(dict(panel="c", group="KNHANES (external)", series="clean",
                 value=clean_rep, n=18, detail=f"{clean_rep} of 18 replicated pairs untouched"))

for arm in ("G0", "G2"):
    t = h["P2_knhanes_full"]["arms"][arm]["three_state"]
    rows.append(dict(panel="d", group="recall on replicated", series=arm,
                     value=t["recall_replicated"], n=t["n_replicated"], detail="higher is better"))
    rows.append(dict(panel="d", group="flag rate on contradicted", series=arm,
                     value=t["flag_rate_contradicted"], n=t["n_contradicted"], detail="lower is better"))
    rows.append(dict(panel="d", group="flag rate on uninformative", series=arm,
                     value=t["flag_rate_uninformative"], n=t["n_uninformative"], detail="lower is better"))

df = pd.DataFrame(rows)
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"[source] {OUT}  rows={len(df)}")
