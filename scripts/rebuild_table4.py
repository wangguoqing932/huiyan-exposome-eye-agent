#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebuild Table 4 so its columns add up and it carries no BOM.

Two defects, both found by review:

1. BOM. The generated file began with a UTF-8 BOM, which leaks into the first
   header cell. Several generated tables in this project have had this problem;
   it is invisible in a rendered table and shows up only when the file is parsed
   by something that does not strip it.

2. The KNHANES row reported 352 total pairs, 301 tested and 50 underpowered, so
   the two columns summed to 351 of 352. One pair hit a stratum in which the
   outcome was constant, so no odds ratio could be estimated: it is neither a
   powered test nor a power failure. The residual is now its own column rather
   than being absorbed into either of the others, because letting two columns
   look as though they add up when they do not is the kind of small
   inconsistency that costs a reader's trust.

Run: python scripts/rebuild_table4.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs" / "tables" / "validation_distribution.csv"
OUT = ROOT / "outputs" / "tables" / "table4_validation.md"

HEADER = ("| Dataset | Total pairs | Tested | Underpowered | Rule-relevant "
          "tested | Replicated | Contradicted | Uninformative | Not estimable |")


def main() -> int:
    vd = pd.read_csv(SRC)
    lines = [
        "# Table 4. Validation layers: pairs available, testable and informative",
        "",
        HEADER,
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in vd.iterrows():
        resid = int(r.total_pairs) - int(r.tested) - int(r.underpowered)
        lines.append(
            f"| {r.dataset} | {int(r.total_pairs)} | {int(r.tested)} | "
            f"{int(r.underpowered)} | {int(r.rule_pairs_tested)} | "
            f"{int(r.replicated)} | {int(r.contradicted)} | "
            f"{int(r.uninformative)} | {resid} |")
    lines += [
        "",
        "**On the \"not estimable\" column.** Tested plus underpowered does not "
        "equal the total for KNHANES (301 + 50 = 351 of 352), and the residual is "
        "shown here rather than absorbed into either column. One pair encountered "
        "a stratum in which the outcome was constant, so no odds ratio could be "
        "estimated; it is neither a powered test nor a power failure.",
        "",
        "**On the two denominators.** The rule-relevant counts (NHANES 16, "
        "KNHANES 15) are those used under the pre-registered three-state standard. "
        "Other figures in this paper quote 17 and 16, or 19 and 16, because they "
        "count the extended v1.2 rule set. The difference is stated here so that "
        "the denominators are not confused with one another.",
        "",
    ]
    # encoding without BOM
    OUT.write_text("\n".join(lines), encoding="utf-8")
    raw = OUT.read_bytes()
    has_bom = raw[:3] == b"\xef\xbb\xbf"
    print(f"Table 4 rebuilt: {len(raw)} B, file BOM={has_bom}")
    for ln in lines[2:7]:
        print("  " + ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
