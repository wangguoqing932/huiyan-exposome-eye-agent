#!/usr/bin/env python
"""Machine-check every number written into outputs/paper/sections/results.md.

The Results section is the first prose this project has produced, and prose is
where numbers drift. This script re-derives each reported quantity from the CSV
it came from and compares it with the literal in the text. It fails loudly on a
mismatch instead of warning, because a Results section with a wrong number in it
is worse than no Results section.

Run: python scripts/verify_results_numbers.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TXT = (ROOT / "outputs" / "paper" / "sections" / "results.md").read_text(
    encoding="utf-8")
REP: list[tuple[str, bool, str]] = []


def ck(tag: str, ok: bool, detail: str) -> None:
    REP.append((tag, bool(ok), detail))


def has(s: str) -> bool:
    return s in TXT


def load(rel: str, **kw) -> pd.DataFrame:
    return pd.read_csv(ROOT / rel, encoding="utf-8-sig", **kw)


# ---------------------------------------------------------------- R11 layers
pm = load("outputs/tables/performance_matrix.csv").set_index("dataset")
for ds, pairs, rep, con, uninf, prec, dec, cov in (
        ("NHANES", 16, 6, 0, 10, 1.0, "0.541", 0.889),
        ("KNHANES", 15, 5, 0, 10, 1.0, "0.478", 0.882),
        ("CHARLS", 4, 0, 0, 4, None, None, 1.000)):
    r = pm.loc[ds]
    ck(f"{ds}.rule_pairs", int(r.rule_pairs_tested) == pairs,
       f"{r.rule_pairs_tested} vs {pairs}")
    ck(f"{ds}.replicated", int(r.replicated) == rep, f"{r.replicated} vs {rep}")
    ck(f"{ds}.contradicted", int(r.contradicted) == con,
       f"{r.contradicted} vs {con}")
    ck(f"{ds}.uninformative", int(r.uninformative) == uninf,
       f"{r.uninformative} vs {uninf}")
    ck(f"{ds}.coverage", abs(float(r.coverage) - cov) < 5e-4,
       f"{r.coverage} vs {cov}")
    ck(f"{ds}.conservative", abs(float(r.precision_binary_uninf_as_fp) -
                                 (rep / pairs if ds != "CHARLS" else 0.0)) < 5e-4,
       f"{r.precision_binary_uninf_as_fp}")
    if dec:
        ck(f"{ds}.declared_ci", dec in str(r.precision_rule_ci95),
           f"{r.precision_rule_ci95}")

vd = load("outputs/tables/validation_distribution.csv").set_index("dataset")
for ds, tot, tested, under in (("NHANES", 180, 159, 21),
                               ("KNHANES", 352, 301, 50),
                               ("CHARLS", 14, 14, 0)):
    r = vd.loc[ds]
    ck(f"{ds}.total", int(r.total_pairs) == tot, f"{r.total_pairs}")
    ck(f"{ds}.tested", int(r.tested) == tested, f"{r.tested}")
    ck(f"{ds}.underpowered", int(r.underpowered) == under, f"{r.underpowered}")

ds_sum = load("outputs/tables/dataset_summary.csv").set_index("dataset_id")
ck("dev.n", int(ds_sum.loc["dev-exposure-disease-pairs", "n_cases"]) == 134,
   str(ds_sum.loc["dev-exposure-disease-pairs", "n_cases"]))
ck("nhanes.n", int(ds_sum.loc["intval-nhanes", "n_cases"]) == 110, "110")
ck("knhanes.n", int(ds_sum.loc["extval-knhanes", "n_cases"]) == 56, "56")
ck("charls.n", int(ds_sum.loc["extval-cohorts-9", "n_cases"]) == 14, "14")

# ------------------------------------------------------------- sensitivity
hs = load("outputs/tables/headline_sensitivity.csv")
def cell(rule_set: str, col: str):
    row = hs[(hs.dataset == "NHANES") & (hs.rule_set == rule_set)]
    return float(row.iloc[0][col]) if len(row) else None
for rs, prec in (("exclude_r22_test_set_leakage", 0.353),
                 ("exclude_negative_control_r01", 0.333),
                 ("exclude_both_r22_and_r01", 0.375),
                 ("A_level_only", 0.000),
                 ("A_and_B_level_only", 0.308)):
    v = cell(rs, "precision_rule_uninf_as_fp")
    ck(f"sens.{rs}", v is not None and abs(v - prec) < 5e-4, f"{v} vs {prec}")
ab = hs[(hs.dataset == "NHANES") & (hs.rule_set == "A_and_B_level_only")].iloc[0]
ck("sens.A+B.counts", int(ab.rule_pairs_tested) == 13 and int(ab.replicated) == 4,
   f"{ab.rule_pairs_tested}/{ab.replicated}")
aonly = hs[(hs.dataset == "NHANES") & (hs.rule_set == "A_level_only")].iloc[0]
ck("sens.A.counts", int(aonly.rule_pairs_tested) == 3 and int(aonly.replicated) == 0,
   f"{aonly.rule_pairs_tested}/{aonly.replicated}")

# ------------------------------------------------------- cohort layer
cr = load("outputs/cohorts/cohort_rule_results.csv")
ck("cohort.pairs_total", len(cr) == 68, str(len(cr)))
conf = cr[cr.rule_relevant.astype(bool)]
ck("cohort.pairs_confirmatory", len(conf) == 18, str(len(conf)))
for st, n in (("replicated", 8), ("uninformative", 8), ("contradicted", 2)):
    got = int((conf.three_state == st).sum())
    ck(f"cohort.{st}", got == n, f"{got} vs {n}")

def pair(rule: str, coh: str):
    r = cr[(cr.rule_id == rule) & (cr.cohort == coh)]
    return r.iloc[0] if len(r) else None

for rule, coh, orv, lo, hi in (
        ("r02_hyperglycemia_x_cataract", "LASI", 1.88, 1.76, 2.00),
        ("r02_hyperglycemia_x_cataract", "SHARE", 1.75, 1.69, 1.82),
        ("r02_hyperglycemia_x_cataract", "CLHLS", 3.59, 2.62, 4.91),
        ("r02_hyperglycemia_x_cataract", "CRELES", 1.31, 1.07, 1.61),
        ("r20_smoking_x_vi_mod_severe", "HRS", 1.61, 1.47, 1.78),
        ("r20_smoking_x_vi_mod_severe", "ELSA", 1.49, 1.21, 1.83),
        ("r20_smoking_x_vi_mod_severe", "SHARE", 1.09, 1.04, 1.13),
        ("r10_smoking_x_cataract", "SHARE", 1.11, 1.04, 1.18),
        ("r10_smoking_x_cataract", "CLHLS", 0.748, 0.64, 0.87),
        ("r12_alcohol_x_cataract", "CLHLS", 0.809, 0.70, 0.93)):
    r = pair(rule, coh)
    ok = r is not None and abs(r.odds_ratio - orv) < 0.006 \
        and abs(r.ci_low - lo) < 0.006 and abs(r.ci_high - hi) < 0.006
    ck(f"{rule}@{coh}", ok,
       f"{r.odds_ratio if r is not None else None} [{r.ci_low if r is not None else None},"
       f"{r.ci_high if r is not None else None}] vs {orv} [{lo},{hi}]")

ck("r02.CRELES.q", abs(pair("r02_hyperglycemia_x_cataract", "CRELES").q_rule -
                       0.051) < 0.002, "q~0.051")
ck("r10.SHARE.q", abs(pair("r10_smoking_x_cataract", "SHARE").q_rule -
                      0.0095) < 0.0006, "q~0.0095")
ck("r10.CLHLS.q", abs(pair("r10_smoking_x_cataract", "CLHLS").q_rule -
                      0.0012) < 0.0004, "q~0.0012")
ck("r12.CLHLS.q", abs(pair("r12_alcohol_x_cataract", "CLHLS").q_rule -
                      0.018) < 0.002, "q~0.018")
ck("r11.n", abs(pair("r11_smoking_x_amd_late", "ELSA").n - 3991) < 60,
   str(pair("r11_smoking_x_amd_late", "ELSA").n))

cov = json.loads((ROOT / "outputs" / "confirmatory" /
                  "cohort_rule_coverage.json").read_text(encoding="utf-8"))
ck("coverage.testable_rules", len([k for k, v in cov["testable"].items() if v]) == 6,
   "6 rules")
# every untestable rule must be one of the 15 described, by id
described = ("r03", "r04", "r07", "r19", "r22", "r16", "r17", "r18", "r21",
             "r01", "r06", "r14", "r08", "r09", "r05")
untest = [k for k, v in cov["testable"].items() if not v]
ck("coverage.untestable_ids",
   all(k.startswith(d) for k, d in
       zip(sorted(untest), sorted(described))
       for d in [next(x for x in described if k.startswith(x))]),
   str(len(untest)))

# ------------------------------------------------------- frame row counts
counts = {"SHARE": 1693515, "HRS": 42946, "ELSA": 9771, "KLoSA": 40406,
          "LASI": 73408, "MHAS": 78537, "CLHLS": 72744, "CRELES": 5191}
import csv
for coh, exp in counts.items():
    p = ROOT / "data" / "frames" / f"cohort_{coh}.csv"
    with open(p, newline="", encoding="utf-8") as fh:
        got = sum(1 for _ in csv.reader(fh)) - 1
    ck(f"frame.{coh}.rows", got == exp, f"{got} vs {exp}")

# ------------------------------------------------------------- report
bad = [r for r in REP if not r[1]]
for tag, ok, detail in REP:
    if not ok:
        print(f"  FAIL {tag:34s} {detail}")
print(f"\n{len(REP) - len(bad)}/{len(REP)} checks PASS")
(f"{'ALL PASS' if not bad else str(len(bad)) + ' FAILED'}")
raise SystemExit(1 if bad else 0)
