#!/usr/bin/env python
"""Exposure-side reconnaissance for the eight ageing cohorts.

Companion to cohort_vision_scan.py, and it follows the same hard-won rules:

  * availability is measured with `s.notna().sum()` -- NEVER with
    `pd.to_numeric`, which turns every labelled-categorical variable into NaN
    and silently reports "empty" (correction C36). The `if n > 0` filter must
    therefore never sit on top of a to_numeric-derived count (correction C41).
  * a name or label hit is not evidence: the label is printed so the semantic
    can be checked by eye, and a veto list removes the false-positive classes
    already confirmed for this project ("glasses of wine", "insight into",
    "under supervision", "HSE year", "family provisions in will", "ever told").
  * variable names are NOT stable across cohorts or releases, so every row
    carries its file and its official value labels where the file supplies them.

Output: outputs/confirmatory/exposure_scan_<COHORT>.json

Usage:
  python scripts/cohort_exposure_scan.py HRS --budget 300
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
    "CRELES": ROOT / "data" / "raw" / "creles",
    "CLHLS": DB / "09. CLHLS 中国老年健康影响因素跟踪调查/clhls",
}

# Exposure vocabulary: smoking, alcohol, body size, glycaemia, blood pressure.
EXPOSURE = re.compile(
    r"(smok|tobacco|cigarett|"
    r"\bdrink|alcohol|alcoh|"
    r"\bbmi\b|body mass|height|weight|waist|"
    r"diabet|blood sugar|glucose|hba1c|"
    r"hypertens|blood pressure|"
    r"흡연|담배|음주|술|키|몸무게|당뇨|혈압|"
    r"吸烟|喝酒|饮酒|身高|体重|糖尿病|血压|"
    r"fuma|tabaco|alcohol|estatura|peso|diabet|presi[oó]n)", re.I)

VETO = re.compile(
    r"(insight|foresight|supervis|revis|television|provision|"
    r"drinking water|water source|"
    r"height of|household member|"
    r"weight of|birth weight|birthweight)", re.I)


def is_raw(f: Path) -> bool:
    n = f.name
    if not n.lower().endswith(".dta"):
        return False
    if n.startswith("H_") or re.match(r"^h_[a-z]+_", n, re.I):
        return False
    low = str(f).lower()
    for bad in ("harmonized", "gateway", "working_data", "temp_data",
                "韩语版", "rand hrs fat"):
        if bad in low:
            return False
    if "_cn" in n.lower():
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cohort", choices=list(COHORTS))
    ap.add_argument("--budget", type=float, default=240.0)
    # R5: the first run capped data reads at 30 candidate files sorted by
    # variable count, which silently skipped SHARE's `ph` module in later
    # waves and made hypertension/diabetes look unavailable. The cap must not
    # be so low that whole modules are never read. Raise and report truncation.
    ap.add_argument("--max-files", type=int, default=400)
    args = ap.parse_args()

    root = COHORTS[args.cohort]
    rec = {"cohort": args.cohort, "root": str(root), "files": 0,
           "scanned": 0, "candidates": [], "notes": []}
    if not root.exists():
        rec["notes"].append("root missing")
    else:
        files = sorted(f for f in root.rglob("*.dta") if is_raw(f))
        rec["files"] = len(files)
        t0 = time.time()
        cand = []
        for f in files:
            if time.time() - t0 > args.budget:
                rec["notes"].append(
                    f"header budget hit at {rec['scanned']}/{len(files)}")
                break
            rec["scanned"] += 1
            try:
                it = pd.read_stata(str(f), iterator=True)
                labs = it.variable_labels()
            except Exception:
                continue
            if not labs:
                continue
            hits = [c for c in labs
                    if (EXPOSURE.search(c) or EXPOSURE.search(str(labs.get(c, ""))))
                    and not VETO.search(c) and not VETO.search(str(labs.get(c, "")))]
            if hits:
                try:
                    rel = str(f.relative_to(root))
                except ValueError:
                    rel = f.name
                cand.append((f, rel, hits[:14], len(labs), labs))

        cand.sort(key=lambda t: t[3])
        if len(cand) > args.max_files:
            rec["notes"].append(
                f"candidate files truncated: reading {args.max_files} of "
                f"{len(cand)} -- results may be incomplete")
        for f, rel, hits, nvars, labs in cand[:args.max_files]:
            try:
                d = pd.read_stata(str(f), columns=hits)
            except Exception as e:
                rec["candidates"].append({"file": rel, "error": type(e).__name__})
                continue
            for c in hits:
                if c not in d.columns:
                    continue
                s = d[c]
                nn = int(s.notna().sum())          # C36/C41 discipline
                if nn == 0:
                    continue
                num = pd.to_numeric(s, errors="coerce")
                if num.notna().sum() >= nn:
                    vc = num.value_counts(dropna=True).sort_index()
                else:
                    vc = s.astype(str).value_counts(dropna=True).sort_index()
                rec["candidates"].append({
                    "file": rel, "var": c, "rows": len(d), "n_valid": nn,
                    "dtype": str(s.dtype),
                    "label": str(labs.get(c, ""))[:110],
                    "n_distinct": int(vc.size),
                    "values": {str(k): int(v) for k, v in list(vc.items())[:8]},
                })

    print(f"=== {args.cohort} === raw .dta={rec['files']} scanned={rec['scanned']} "
          f"candidates_with_data={len(rec['candidates'])}")
    for n in rec["notes"]:
        print("  NOTE:", n)
    # R6 fix: the guard for error-entries (which carry only {file, error}) used
    # to live inside the print loop, i.e. AFTER the `sorted(key=...)` call that
    # needs it. A single unreadable file (KLoSA's cp949-encoded waves) therefore
    # raised KeyError('n_valid') and the JSON was never written at all. Filter
    # FIRST, then sort. Same failure family as C41/C46: a guard placed after the
    # operation that depends on it turns "partial" into "nothing".
    ok = [c for c in rec["candidates"] if c.get("n_valid")]
    bad = [c for c in rec["candidates"] if "n_valid" not in c]
    if bad:
        print(f"  WARNING: {len(bad)} candidate file(s) could not be read "
              f"(e.g. {bad[0].get('file')} -> {bad[0].get('error')})")
    for c in sorted(ok, key=lambda x: -x["n_valid"])[:34]:
        vals = ", ".join(f"{k}:{v}" for k, v in list(c["values"].items())[:5])
        print(f"  {c['var']:14s} n={c['n_valid']:7d}/{c['rows']:7d} "
              f"[{c['label'][:56]:56s}] {vals}")

    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"exposure_scan_{args.cohort}.json"
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
