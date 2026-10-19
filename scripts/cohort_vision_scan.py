#!/usr/bin/env python
"""Vision-variable scan with NON-MISSING COUNTS (the C19 discipline).

The first reconnaissance pass ranked files by whether a variable NAME or LABEL
matched a vision keyword. That metric is not evidence of availability: KLoSA's
vision block is declared with correct Korean and English labels in every wave
and contains ZERO non-missing values in all nine of them. Relying on names is
the same failure mode as R11 correction C5 (NHANES antioxidant composite was
entirely NaN because a non-existent column was referenced).

This script therefore reports, for every candidate variable, the actual
non-missing count and the value distribution, so "available" means "has data".

Usage:
  python scripts/cohort_vision_scan.py SHARE
  python scripts/cohort_vision_scan.py SHARE --budget 300
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = Path(r"E:\BaiduNetdiskDownload\所有数据库")
OUT = ROOT / "outputs" / "confirmatory"

COHORTS = {
    "HRS":   DB / "03. HRS 美国健康与退休研究/HRS_美国/Raw_data",
    "ELSA":  DB / "02. ELSA 英国老龄化纵向研究/Raw_data",
    "KLoSA": DB / "04. KLoSA 韩国老龄化纵向研究/KLoSA_韩国/Raw_data",
    "LASI":  DB / "05. LASI 印度老龄化纵向研究/LASI_印度/Raw_data",
    "MHAS":  DB / "06. MHAS 墨西哥健康与老龄化研究/MHAS_墨西哥/Raw_data",
    "SHARE": DB / "07. SHARE 欧洲健康退休与老龄化调查/SHARE_欧洲/Raw_data",
    # CRELES ships inside 8 zips; extract to data/raw/creles first
    # (scripts/extract_creles.py), then scan the extracted plain .dta files.
    "CRELES": ROOT / "data" / "raw" / "creles",
    "CLHLS": DB / "09. CLHLS 中国老年健康影响因素跟踪调查/clhls",
}

# Vision / eye-disease vocabulary.
#
# R1 2026-10-15: tightened after three confirmed false-positive classes:
#   * bare `sight` matched "gaining INsight into other people's …" (SHARE
#     interviewer survey)            -> require `eyesight`, not `sight`
#   * `glasses` matched "GLASSES of sherry/wine" (ELSA alcohol items)
#                                   -> require a vision context, and veto
#                                      drink/alcohol words outright
#   * `will` / generic hits pulled in "family provisions in will" (HRS KT002)
#                                   -> excluded by the semantic veto list
VISION = re.compile(
    r"(eyesight|eye\s*sight|\bvision\b|visual\s+(acuity|impair|function)|"
    r"cataract|catract|glaucoma|glaucome|\bblind\b|blindness|"
    r"spectacle|corrective\s+lens|reading\s+glasses|"
    r"retinopath|maculopath|macular\s+degener|"
    r"시력|안경|백내장|녹내장|실명|"
    r"视力|眼睛|白内|青光|失明|视物|"
    r"vista|visi[oó]n|catarata|ciego)", re.I)

# Semantic veto: a candidate whose NAME or LABEL contains any of these is not
# an eye variable regardless of keyword hits.
VETO = re.compile(
    r"(sherry|wine|beer|spirit|whisk|vodka|liquor|alcohol|drink|drank|"
    r"insight|foresight|provision|\bwill\b|testament|"
    r"supervis|revis|visionary|television|provision)", re.I)

# Aggressive filters: only plain raw questionnaire files.
def is_raw(f: Path) -> bool:
    n = f.name
    if not n.lower().endswith(".dta"):
        return False
    if n.startswith("H_") or re.match(r"^h_[a-z]+_", n, re.I):
        return False
    low = str(f).lower()
    for bad in ("harmonized", "gateway", "working_data", "temp_data", "韩语版"):
        if bad.lower() in low:
            return False
    if "_cn" in n.lower():                     # prior CN-adapted copies
        return False
    return True


def label_of(labs, c):
    return str(labs.get(c, ""))


def scan(name: str, budget_s: float, max_files_data: int = 40):
    root = COHORTS[name]
    rec = {"cohort": name, "root": str(root), "files": 0, "scanned": 0,
           "candidates": [], "notes": []}
    if not root.exists():
        rec["notes"].append("root missing")
        return rec
    files = sorted(f for f in root.rglob("*.dta") if is_raw(f))
    rec["files"] = len(files)
    t0 = time.time()
    cand_files = []
    for f in files:
        if time.time() - t0 > budget_s:
            rec["notes"].append(f"header budget hit at {rec['scanned']}/{len(files)}")
            break
        rec["scanned"] += 1
        try:
            it = pd.read_stata(str(f), iterator=True)
            labs = it.variable_labels()
        except Exception:
            continue
        hits = [c for c in labs
                if (VISION.search(c) or VISION.search(label_of(labs, c)))
                and not VETO.search(c) and not VETO.search(label_of(labs, c))]
        if hits:
            try:
                rel = str(f.relative_to(root))
            except ValueError:
                rel = f.name
            cand_files.append((f, rel, hits[:12], len(labs)))

    # Now measure DATA presence for the candidates (this is the real evidence).
    #
    # R2 fix 2026-10-15 — CRITICAL. The first version counted availability as
    # `pd.to_numeric(s).notna().sum()`. For a Stata variable with value labels,
    # pandas returns a **categorical whose categories are the label strings**
    # (e.g. ht015 -> 'Yes'/'No'), and `to_numeric` converts every entry to NaN.
    # That produced FALSE "empty" verdicts: LASI ht015 really has n=73,198 but
    # was reported as n=0. Any verdict of "declared but empty" obtained with
    # `to_numeric` is therefore untrustworthy and must be re-derived with
    # `notna()`. Availability is now measured on the raw Series.
    cand_files.sort(key=lambda t: t[3])
    for f, rel, hits, nvars in cand_files[:max_files_data]:
        try:
            d = pd.read_stata(str(f), columns=hits)
        except Exception as e:
            rec["candidates"].append({"file": rel, "error": type(e).__name__})
            continue
        for c in hits:
            if c not in d.columns:
                continue
            s = d[c]
            nn = int(s.notna().sum())          # NOT to_numeric — see note above
            # value distribution: numeric when possible, else the label strings
            num = pd.to_numeric(s, errors="coerce")
            if num.notna().sum() >= nn and nn:
                vc = num.value_counts(dropna=True).sort_index()
            else:
                vc = s.astype(str).value_counts(dropna=True).sort_index()
            rec["candidates"].append({
                "file": rel, "var": c, "rows": len(d), "n_valid": nn,
                "dtype": str(s.dtype), "n_distinct": int(vc.size),
                "values": {str(k): int(v) for k, v in list(vc.items())[:10]},
            })
    rec["files_with_candidates"] = len(cand_files)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cohort", choices=list(COHORTS))
    ap.add_argument("--budget", type=float, default=180.0)
    args = ap.parse_args()

    rec = scan(args.cohort, args.budget)
    print(f"=== {args.cohort} ===  raw .dta={rec['files']} scanned={rec['scanned']} "
          f"files-with-candidates={rec.get('files_with_candidates')}")
    for n in rec["notes"]:
        print("  NOTE:", n)

    with_any = [c for c in rec["candidates"] if c.get("n_valid")]
    empty = [c for c in rec["candidates"] if "n_valid" in c and not c["n_valid"]]
    print(f"\n  候选变量: {len(rec['candidates'])}  有数据: {len(with_any)}  "
          f"全空: {len(empty)}")
    if empty:
        print(f"  *** {len(empty)} 个候选变量非缺失为 0 —— 声明了但无数据（C19 型陷阱）")
    print("\n  --- 有数据的候选（按非缺失数降序，前 30）---")
    for c in sorted(with_any, key=lambda x: -x["n_valid"])[:30]:
        vals = ", ".join(f"{k}:{v}" for k, v in list(c["values"].items())[:6])
        print(f"    {c['var']:16s} n={c['n_valid']:7d}/{c['rows']:7d} "
              f"distinct={c['n_distinct']:3d}  [{c['file'][:44]}]  {vals}")

    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"vision_scan_{args.cohort}.json"
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
