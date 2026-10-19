#!/usr/bin/env python
"""R5 P0-4 (2026-10-14): export per-pair micro samples for survey-design
sensitivity analysis (R svyglm).

analysis_plan §6 pre-registered R svyglm (strata/PSU) as the confirmatory
variance standard; the main pipeline implements Python GLM with freq_weights
(no design effect). This script exports, for every pair that reaches
"tested" status in the main pipeline (restricted to dataset-judgeable
outcome items), the exact analysis sample with sampling design variables,
so scripts/survey_sensitivity_R5.R can re-fit each pair with proper
survey variance and compare p/q against the main analysis.

Run: PYTHONUTF8=1 python scripts/survey_sensitivity_export.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import (build_nhanes_exposures, build_nhanes_outcomes,
                      detect_separation, get_judgeable_b_items,
                      load_nhanes_raw, restrict_nhanes_adults)
from evaluate_knhanes import build_knhanes_exposures, build_knhanes_outcomes

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "data" / "processed" / "survey_pairs_R5"


def export_pairs(d: pd.DataFrame, E: dict, B: dict, judgeable: set[str],
                 cov_cols: list[str], wt_col: str, stratum_col: str,
                 psu_col: str, dataset: str, extra_round=None,
                 binary: bool = True, outdir: Path | None = None) -> int:
    """Export one CSV per testable judgeable pair. Returns count exported.

    binary=True  : x is a 0/1 flag (rule-validation layer).
    binary=False : x is a continuous measure, standardised to per-1-SD so the
                   fitted coefficient is an OR per SD (dose-response layer).
    """
    outdir = outdir or OUTDIR
    outdir.mkdir(parents=True, exist_ok=True)
    n_exp = 0
    for a_flag, evec in E.items():
        for b_item, ovec in B.items():
            if judgeable is not None and b_item not in judgeable:
                continue
            aux = [c for c in ("cycle",) if c in d.columns]
            keep = ["y", "x"] + cov_cols + aux + [wt_col, stratum_col, psu_col]
            x = pd.to_numeric(evec, errors="coerce")
            if binary:
                if not x.isin([0, 1]).any():
                    continue
            else:
                sd = float(x.std(skipna=True))
                if not np.isfinite(sd) or sd == 0:
                    continue
                x = (x - float(x.mean(skipna=True))) / sd      # OR per 1 SD
            sub = pd.DataFrame({"y": ovec, "x": x}).join(d[keep[2:]]).dropna()
            sub = sub[sub["y"].isin([0, 1])]
            if binary:
                sub = sub[sub["x"].isin([0, 1])]
            ny = int(sub["y"].sum())
            if binary:
                nx = int(sub["x"].sum())
                if len(sub) < 200 or ny < 30 or nx < 30 or ny > len(sub) - 30:
                    continue
                if detect_separation(sub["y"], sub["x"]):
                    continue
            else:
                if len(sub) < 200 or ny < 30 or ny > len(sub) - 30:
                    continue
            out = sub.rename(columns={wt_col: "wt", stratum_col: "strata",
                                      psu_col: "psu"}).copy()
            out["dataset"] = dataset
            out["pair"] = f"{a_flag}__{b_item}"
            if extra_round:  # weight adjuster, e.g. half-weight across cycles
                out["wt"] = out["wt"] * extra_round(sub)
            name = f"{dataset}__{a_flag}__{b_item}.csv".replace("/", "_")
            out.to_csv(outdir / name, index=False)
            n_exp += 1
    return n_exp


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["binary", "continuous"], default="binary",
                    help="binary: 0/1 exposure flags (rule-validation layer). "
                         "continuous: per-1-SD standardised measures written to "
                         "data/processed/survey_pairs_dose_response/ (dose-response layer).")
    args = ap.parse_args()
    binary = args.mode == "binary"
    outdir = OUTDIR if binary else (ROOT / "data" / "processed" / "survey_pairs_dose_response")
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob("*.csv"):
        old.unlink()
    print(f"[export] mode={args.mode} -> {outdir}")

    # ── NHANES ──────────────────────────────────────────────────────
    # R11 2026-10-15: use the SHARED loader from evaluate.py.  There used to be
    # three independent copies of the module table (evaluate.py,
    # evaluate_knhanes.py, here); keeping them in sync by hand is exactly how
    # the LBDHDD / DIQ010 / DR1TVE errors survived.  One source of truth now.
    d = load_nhanes_raw()
    d = restrict_nhanes_adults(d)
    cov_cols = ["RIDAGEYR", "RIAGENDR", "RIDRETH1", "INDFMPIR"]
    for c in ("DMDEDUC2", "DMDEDUC3"):
        if c in d.columns:
            cov_cols.append(c)
            break
    if binary:
        E = build_nhanes_exposures(d)
    else:
        from evaluate import build_nhanes_continuous
        E = {k: v for k, v in build_nhanes_continuous(d).items()
             if k not in ("log_blood_lead", "antioxidant_inadequate_count")}
    B = build_nhanes_outcomes(d)
    n1 = export_pairs(d, E, B, None,  # all tested pairs: BHY q denominator must match main analysis
                      cov_cols, "WTMEC2YR", "SDMVSTRA", "SDMVPSU", "nhanes",
                      extra_round=lambda s: s["cycle"].map({"2005-2006": 0.5, "2007-2008": 0.5}).fillna(1.0),
                      binary=binary, outdir=outdir)
    print(f"[export] NHANES pairs: {n1}")

    # ── KNHANES ─────────────────────────────────────────────────────
    # R11: frames_v2 (rebuilt with BS3_1 / edu / incm5 / BD* / PM25 / E_DM) and
    # SES covariates, matching evaluate_knhanes.py.
    FR = Path(os.environ.get("KNHANES_FRAMES_DIR", ROOT / "data/raw/knhanes_frames_v2"))
    if not FR.exists():
        raise SystemExit(f"KNHANES frames not found: {FR} — run scripts/build_knhanes_frames.py")
    print(f"[export] KNHANES frames: {FR}")
    parts = []
    for p in sorted(FR.glob("knhanes_20*.csv")):
        df = pd.read_csv(p, low_memory=False)
        df["wave"] = int(p.stem.split("_")[1])
        parts.append(df)
    d = pd.concat(parts, ignore_index=True, sort=False)
    d = d[pd.to_numeric(d["age"], errors="coerce") >= 40]
    w = "wt_itvex" if "wt_itvex" in d.columns else ("wt_itv" if "wt_itv" in d.columns else "wt_ex")
    d = d[pd.to_numeric(d.get(w, 0), errors="coerce") > 0]
    d["age2"] = pd.to_numeric(d["age"], errors="coerce") ** 2 / 100
    d = d.rename(columns={"age": "kage"})
    strat_col = "kstrata" if "kstrata" in d.columns else "strata"
    psu_col = "psu" if "psu" in d.columns else next((c for c in d.columns if c.lower() in ("psu", "sdmvpsu")), None)
    print(f"[export] KNHANES design cols: strata={strat_col}, psu={psu_col}, weight={w}")
    if psu_col is None:
        print("[export] KNHANES: no PSU column found — skipping survey export")
        return 0
    if binary:
        E = build_knhanes_exposures(d)
    else:
        from evaluate_knhanes import build_knhanes_continuous
        E = build_knhanes_continuous(d)
    B = build_knhanes_outcomes(d)
    d = d.rename(columns={"kage": "age"})
    kn_cov = ["age", "age2", "sex"]
    for cand in ("edu", "incm5"):
        if cand in d.columns and pd.to_numeric(d[cand], errors="coerce").notna().sum() > len(d) * 0.5:
            kn_cov.append(cand)
    print(f"[export] KNHANES covariates: {kn_cov}")
    n2 = export_pairs(d, E, B, None, kn_cov, w, strat_col, psu_col, "knhanes",
                      binary=binary, outdir=outdir)
    print(f"[export] KNHANES pairs: {n2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
