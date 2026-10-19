#!/usr/bin/env python
"""Stage-0 reconnaissance ledger for the 8 ageing-cohort raw data.

Purpose: locate, in the RAW questionnaire files only (no Gateway Harmonized
files, no prior working/temp intermediates), which file carries the vision/eye
questions and under what original variable names. Nothing is analysed; this only
reads Stata headers (variable names + labels), never the data.

Output: outputs/confirmatory/cohort_raw_recon.json  (+ console ledger)

Run: PYTHONUTF8=1 python scripts/cohort_raw_recon.py
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = Path(r"E:\BaiduNetdiskDownload\所有数据库")
OUT = ROOT / "outputs" / "confirmatory"

# Raw-data roots ONLY. The user's own prior intermediates (Working_data/,
# Temp_data/) and the Gateway Harmonized products (H_*.dta, h_*_g*.dta) are
# deliberately excluded — the operationalisation must be ours.
COHORTS = {
    "HRS":   DB / "03. HRS 美国健康与退休研究/HRS_美国/Raw_data",
    "ELSA":  DB / "02. ELSA 英国老龄化纵向研究/Raw_data",
    "KLoSA": DB / "04. KLoSA 韩国老龄化纵向研究/KLoSA_韩国/Raw_data",
    "LASI":  DB / "05. LASI 印度老龄化纵向研究/LASI_印度/Raw_data",
    "MHAS":  DB / "06. MHAS 墨西哥健康与老龄化研究/MHAS_墨西哥/Raw_data",
    "SHARE": DB / "07. SHARE 欧洲健康退休与老龄化调查/SHARE_欧洲/Raw_data",
    "CRELES": DB / "08. CRELES 哥斯达黎加老龄化健康研究/Raw_data",
    "CLHLS": DB / "09. CLHLS 中国老年健康影响因素跟踪调查/clhls",
}

VISION = re.compile(
    r"(sight|visio|visual|cataract|catract|glaucoma|glaucome|blind|"
    r"eyesight|eye\b|eyes\b|specs|glasses|retin|macul|iop\b|acuity)", re.I)

EXCLUDE_NAME = re.compile(r"^(h_|h[0-9]{2}.*cog|.*cogimp)", re.I)


def want(f: Path) -> bool:
    """Raw questionnaire file? Exclude harmonized products and prior work."""
    n = f.name
    if not n.lower().endswith(".dta"):
        return False
    if f.name.startswith("H_"):                 # Gateway Harmonized
        return False
    if re.match(r"^h_[a-z]+_", n, re.I):        # h_elsa_g3 etc.
        return False
    low = str(f).lower()
    if "harmonized" in low or "gateway" in low:
        return False
    if "working_data" in low or "temp_data" in low:
        return False
    return True


def scan_cohort(name: str, root: Path, budget_s: float = 90.0):
    rec = {"root": str(root), "exists": root.exists(),
           "dta_files": 0, "scanned": 0, "vision_files": [], "notes": []}
    if not root.exists():
        rec["notes"].append("root missing")
        return rec
    files = [f for f in root.rglob("*.dta") if want(f)]
    rec["dta_files"] = len(files)
    t0 = time.time()
    for f in files:
        if time.time() - t0 > budget_s:
            rec["notes"].append(
                f"time budget hit after {rec['scanned']}/{len(files)} files "
                f"— scan incomplete, raise budget_s to finish")
            break
        rec["scanned"] += 1
        try:
            it = pd.read_stata(str(f), iterator=True)
            labs = it.variable_labels()
            cols = list(labs.keys())
        except Exception:
            continue
        hits = [(c, str(labs.get(c, ""))[:70]) for c in cols
                if VISION.search(c) or VISION.search(str(labs.get(c, "")))]
        if hits:
            try:
                rel = str(f.relative_to(root))
            except ValueError:
                rel = f.name
            rec["vision_files"].append({
                "file": rel, "n_vars": len(cols),
                "size_mb": round(f.stat().st_size / 1e6, 1),
                "vision_vars": hits[:18],
            })
    return rec


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ledger = {}
    for name, root in COHORTS.items():
        print(f"\n=== {name} ===")
        rec = scan_cohort(name, root)
        ledger[name] = rec
        print(f"  dta(raw)={rec['dta_files']}  scanned={rec['scanned']}  "
              f"vision-bearing files={len(rec['vision_files'])}")
        for n in rec["notes"]:
            print(f"  NOTE: {n}")
        for vf in rec["vision_files"][:6]:
            names = ", ".join(c for c, _ in vf["vision_vars"][:8])
            print(f"    {vf['file'][:62]:62s} ({vf['size_mb']} MB)  {names}")

    (OUT / "cohort_raw_recon.json").write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {OUT/'cohort_raw_recon.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
