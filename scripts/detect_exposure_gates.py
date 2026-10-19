#!/usr/bin/env python
"""Detect gated (conditional) exposure questions before building any flag.

Correction C54 records the single most recurrent error in this project: a
binary exposure variable that is asked only of a subset, then used as if it
described the whole sample. Four confirmed occurrences so far --

    NHANES  SMQ040 ("do you now smoke")        gated on SMQ020 == 1
    KLoHANES BS1_1  (lifetime-ever, not current)
    CHARLS  da061  ("do you currently smoke")  gated on da059 == 1
    SHARE   br002_ ("smoke at the present time") gated on br001_ == Yes

Each one produced a prevalence that looked like a plausible percentage and was
actually a rate *among the gate-positive subset* (SHARE: 49% instead of 17%).

The signature is mechanical and therefore detectable: a gated variable V has

    n_valid(V)  ~=  #positive(G)      for some sibling "gate" variable G
    n_valid(V)  <<  n_valid(G)

so this script looks for exactly that relationship. It reads the JSON ledgers
already produced by cohort_exposure_scan.py, so it costs no data I/O.

Output: outputs/confirmatory/exposure_gates_<COHORT>.json

Usage:
  python scripts/detect_exposure_gates.py SHARE
  python scripts/detect_exposure_gates.py ALL
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "confirmatory"

# Variables that are themselves "whole-sample" questions and therefore never a
# gated subset variable. Used to seed the search for gate candidates.
GATE_PAT = re.compile(
    r"(ever|diagnos|told you|do you|have you|是否|曾经|目前|현재|과거|"
    r"fuma|ha fumado|alguna vez)", re.I)
TARGET_PAT = re.compile(r"(now|present|current|currently|at the present)", re.I)

# A gate must be about the SAME topic as its target. Without this constraint
# the n-arithmetic alone produces spurious candidates: SHARE's hypertension
# item ph006d2 and its drinking item br039_ both happen to have positive counts
# within a few percent of br002_'s non-missing count, and were reported as
# gates for smoking. The real gate is the sibling that shares the topic
# (smoke -> ever smoked, drink -> ever drank, diabetes -> ever diagnosed).
TOPICS = {
    "smok":  r"(smok|tobacco|cigarett|fuma|흡연|담배|吸烟)",
    "drink": r"(drink|alcohol|alcoh|음주|饮酒|喝酒)",
    "diab":  r"(diabet|blood sugar|glucose|hba1c|당뇨|糖尿)",
    "bp":    r"(hypertens|blood pressure|혈압|血压)",
    "bmi":   r"(\bbmi\b|body mass|mass index)",
}


def topic_of(*texts: str) -> str | None:
    for name, pat in TOPICS.items():
        rx = re.compile(pat, re.I)
        if any(rx.search(str(t)) for t in texts):
            return name
    return None


def positives(entry: dict) -> int | None:
    """Positive count for a 0/1-ish or Yes/No variable.

    Stored values are stringified labels or numeric codes. We accept the usual
    affirmative spellings; anything else returns None and the entry is skipped
    rather than guessed at (correction C52: official labels can themselves be
    wrong, so we never fabricate a count).
    """
    vals = entry.get("values") or {}
    yes = 0
    found = False
    for k, v in vals.items():
        kl = str(k).strip().lower()
        if kl in ("1", "1.0", "yes", "1. yes", "selected", "si", "sí",
                  "current", "1 yes"):
            yes += v
            found = True
    return yes if found else None


def scan(coh: str) -> dict:
    p = OUT / f"exposure_scan_{coh}.json"
    if not p.exists():
        return {"cohort": coh, "error": "exposure scan JSON missing"}
    rec = json.loads(p.read_text(encoding="utf-8"))
    entries = [e for e in rec.get("candidates", []) if e.get("n_valid")]

    findings = []
    for e in entries:
        label = str(e.get("label", ""))
        if not TARGET_PAT.search(label):
            continue
        n_v = e["n_valid"]
        if n_v == 0:
            continue
        pos_v = positives(e)
        topic_v = topic_of(label, e["var"])
        # candidate gates: whole-sample "ever/do you" questions with a much
        # larger n than the target, and a positive count near n_v
        cands = []
        for g in entries:
            if g is e:
                continue
            if not GATE_PAT.search(str(g.get("label", ""))):
                continue
            # same-topic constraint (see TOPICS note)
            if topic_v is not None and topic_of(str(g.get("label", "")),
                                                g["var"]) != topic_v:
                continue
            n_g = g["n_valid"]
            if n_g < n_v * 1.2:          # gate must cover materially more people
                continue
            pos_g = positives(g)
            if not pos_g:
                continue
            rel = abs(pos_g - n_v) / max(n_v, 1)
            if rel <= 0.10:              # within 10% -> strong gate signature
                cands.append({
                    "gate_var": g["var"], "gate_label": g["label"][:80],
                    "gate_n": n_g, "gate_positives": pos_g,
                    "rel_diff": round(rel, 4), "gate_file": g["file"],
                })
        findings.append({
            "var": e["var"], "label": label[:90], "n_valid": n_v,
            "own_positives": pos_v,
            "own_positive_rate_if_naive":
                None if not pos_v else round(pos_v / n_v, 4),
            "looks_gated": bool(cands),
            "gate_candidates": sorted(cands, key=lambda c: c["rel_diff"])[:3],
        })

    return {"cohort": coh, "n_targets": len(findings), "findings": findings}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cohort", help="cohort name or ALL")
    args = ap.parse_args()

    names = (sorted(p.stem.replace("exposure_scan_", "")
                    for p in OUT.glob("exposure_scan_*.json"))
             if args.cohort == "ALL" else [args.cohort])

    for coh in names:
        res = scan(coh)
        if res.get("error"):
            print(f"=== {coh} === {res['error']}")
            continue
        print(f"=== {coh} === targets={res['n_targets']}")
        for f in res["findings"]:
            flag = "GATED  " if f["looks_gated"] else "       "
            naive = f["own_positive_rate_if_naive"]
            print(f"  {flag}{f['var']:12s} n={f['n_valid']:7d} "
                  f"naive_rate={naive}  [{f['label'][:46]}]")
            for c in f["gate_candidates"]:
                print(f"           └ gate: {c['gate_var']} "
                      f"pos={c['gate_positives']} n={c['gate_n']} "
                      f"(rel {c['rel_diff']}) [{c['gate_label'][:44]}]")
        OUT.mkdir(parents=True, exist_ok=True)
        op = OUT / f"exposure_gates_{coh}.json"
        op.write_text(json.dumps(res, ensure_ascii=False, indent=2),
                      encoding="utf-8")
        print(f"  -> {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
