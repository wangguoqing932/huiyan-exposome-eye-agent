"""Which of the 21 rules are actually evaluated by any confirmatory layer?"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "src")
from huiyan_agent.risk_rules import load_rules

rules = load_rules()
print(f"rules in configs/rules.yaml: {len(rules)}")
print("levels:", {l: sum(1 for r in rules if r.evidence_level == l) for l in "ABCDE"})
print("negative_control:", [r.id for r in rules if r.negative_control])

files = {
    "NHANES": "outputs/confirmatory/nhanes_confirmatory.csv",
    "KNHANES": "outputs/confirmatory/knhanes_confirmatory.csv",
    "CHARLS2011": "outputs/confirmatory/charls_confirmatory.csv",
    "CHARLS2015": "outputs/confirmatory/charls2015_confirmatory.csv",
}
hit = {r.id: {} for r in rules}
for ds, p in files.items():
    df = pd.read_csv(p)
    tested = df[df["status"] == "tested"]
    for _, row in tested.iterrows():
        for rid in str(row["rule_ids"]).split(","):
            rid = rid.strip()
            if rid in hit:
                hit[rid].setdefault(ds, []).append(f"{row['a_flag']}x{row['b_item']}({row['gold3']})")

print("\n=== rule x layer coverage (tested pairs only) ===")
never = []
for r in rules:
    layers = hit[r.id]
    if not layers:
        never.append((r.id, r.evidence_level))
        print(f"{r.id:34s} [{r.evidence_level}] NEVER TESTED in any layer")
    else:
        print(f"{r.id:34s} [{r.evidence_level}] " +
              " | ".join(f"{k}: {len(v)} ({','.join(sorted(set(x.split('(')[1][:-1] for x in v)))})"
                         for k, v in layers.items()))
print(f"\nrules never tested anywhere: {len(never)}/{len(rules)} -> {[x[0] for x in never]}")

# NHANES alcohol / lead exposure prevalence
NH = Path(r"E:\BaiduNetdiskDownload\所有数据库\16.NHANES")
frames = {}
for cyc, suf in {"2005-2006": "_D", "2007-2008": "_E"}.items():
    for base, mod in [("DEMO", "D"), ("ALQ", "A"), ("PBCD", "P")]:
        f = NH / cyc / f"{base}{suf}.XPT"
        if f.exists():
            d = pd.read_sas(str(f), format="xport", encoding="utf-8").set_index("SEQN")
            frames.setdefault(mod, []).append(d)
alb = pd.concat(frames["A"]).reset_index()
demo = pd.concat(frames["D"]).reset_index()
m = demo[pd.to_numeric(demo["RIDAGEYR"], errors="coerce") >= 40]
al = alb.merge(m[["SEQN"]], on="SEQN")
print(f"\nNHANES 40+ n={len(al)}")
print(f"  ALQ101==1 (lifetime >=12 drinks ever) prevalence: {100*(al['ALQ101']==1).mean():.1f}%  "
      f"-> this is what the repo calls 'alcohol_intake'")
for c in ["ALQ120Q", "ALQ130"]:
    if c in al.columns:
        s = pd.to_numeric(al[c], errors="coerce")
        print(f"  {c}: non-missing={s.notna().sum()} median={s.median()}")
