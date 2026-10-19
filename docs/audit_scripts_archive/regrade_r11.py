#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regrade r11 from A to B, which its own citation cannot support.

The project's grading scheme is explicit: A is a regulatory label or guideline,
B is a meta-analysis, C original research, D in-vitro/animal, E mechanism
inference. load_rules enforces the pairing (A->high, B->medium, C->low) and
refuses to load a rule whose severity and evidence_level disagree.

r11 (smoking -> late AMD) declares A, hence severity high. Its citation,
resolved through Crossref, is:

    10.1097/MD.0000000000041599
    "Risk factors for age-related macular degeneration: Updated systematic
     review and meta-analysis", Medicine, 2025, type journal-article

A systematic review and meta-analysis is grade B under the project's own scheme,
not grade A. The corpus links corroborate this: r11's linked chunks are 1 x B and
3 x C, with no A among them. So r11 is over-graded by one tier, and because the
grade drives severity, it is also over-severitised: high instead of medium.

This does not touch the cohort layer. cohort_confirmatory.py reads only
rules[rid]["direction"], which is unchanged; cohort_heterogeneity.py,
cohort_power.py and evidence_base_audit.py do not read rules.yaml at all. The
change affects what the agent reports, which is the point.

Run: python scripts/regrade_r11.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "configs" / "rules.yaml"


def main() -> int:
    t = YAML.read_text(encoding="utf-8")
    lines = t.split("\n")
    out, in_r11, changed = [], False, []
    for ln in lines:
        if ln.strip().startswith("- id:"):
            in_r11 = ln.strip().endswith("r11_smoking_x_amd_late")
        if in_r11 and ln.strip().startswith("evidence_level:"):
            out.append(ln.replace("A", "B")); changed.append(("evidence_level", ln.strip()))
            continue
        if in_r11 and ln.strip().startswith("severity:"):
            out.append(ln.replace("high", "medium")); changed.append(("severity", ln.strip()))
            continue
        out.append(ln)

    if not changed:
        print("no change made -- anchors not found (already regraded?)")
        return 0

    t2 = "\n".join(out)
    # leave an audit note inside the rationale
    note = ("【2026-10-16 降级更正】原判 A/high 依据 DOI 10.1097/MD.0000000000041599，"
            "经 Crossref 解析为 Medicine 2025 的 systematic review and meta-analysis，"
            "按本项目分级纪律（A=监管标签/指南，B=Meta 分析）应为 B/medium；"
            "语料侧链接亦为 1×B + 3×C 且无 A。已降为 B/medium。")
    t2 = t2.replace(
        "rationale: 吸烟是晚期 AMD 的确立危险因素（AMD 风险因素 meta 分析）。",
        f"rationale: 吸烟是晚期 AMD 的确立危险因素（AMD 风险因素 meta 分析）。{note}", 1)
    YAML.write_text(t2, encoding="utf-8")
    for k, v in changed:
        print(f"  r11 {k}: {v}  ->  changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
