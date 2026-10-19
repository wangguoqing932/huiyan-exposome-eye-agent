#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Downgrade r10 and r13 from A to B. Basis: their own citations, and the absence
of any cataract guideline.

This changes grades for the second time in this audit, so the difference from the
first attempt matters and is stated here rather than left implicit.

The FIRST attempt (docs/AGENT_AUDIT.md section 8) downgraded eleven rules on the
strength of the per-chunk `linked_rules` field. That field is empty for all 159
guideline chunks, so the audit could not see guideline support, and every one of
the eleven changes had to be reverted (section 21).

THIS change rests on four independent checks, none of which is a text match:

  1. **The rules' own citations, resolved through PubMed publication types.**
     r10 cites 10.1016/j.ebiom.2022.104154 -> PMID 35816897, typed
     `Meta-Analysis, Systematic Review`.
     r13 cites 10.1371/journal.pone.0089923 -> a meta-analysis of prospective
     cohort studies.
     A meta-analysis is grade B under this project's scheme; A is reserved for a
     regulatory label or clinical guideline.

  2. **A PubMed search for a cataract risk-factor guideline** -- zero hits.

  3. **The project's own cached guidelines** -- data/raw/aao_ppp/ holds
     AMD_PPP.pdf, DR_PPP.pdf, POAG_PPP.pdf. There is no cataract PPP, and
     network_and_proxy.md records why: the cataract PPP is a members-only page
     (HTML 500), so it was never obtainable.

  4. **The corpus's guideline chunks** -- 159 in total, covering
     {AMD: 49, DR: 52, POAG: 58}. Cataract: zero.

Four independent lines agree that no guideline-level support for a cataract rule
is available to this project, and the rules cite meta-analyses for their grade A.

Scope: r10 and r13 only. The other nine rules the first attempt touched are left
at their original grades, because the title audit (section 25) found same-grade
title-matched evidence for all of them, and r02 and r04 were confirmed correct by
reading their citations.

Run: python scripts/regrade_cataract_rules.py            (dry run)
     python scripts/regrade_cataract_rules.py --apply
"""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "configs" / "rules.yaml"

TARGETS = {
    "r10": ("B", "medium",
            "引文 10.1016/j.ebiom.2022.104154 经 PubMed 解析为 "
            "Meta-Analysis + Systematic Review（PMID 35816897），属 B 级；"
            "A 级保留给监管标签/临床指南。且四个独立来源一致表明本项目无法获得"
            "白内障指南：PubMed 检索白内障危险因素指南 0 条命中；"
            "data/raw/aao_ppp/ 只有 AMD/DR/POAG 三份（白内障 PPP 为会员墙，见 "
            "network_and_proxy.md）；语料 159 个指南块覆盖 "
            "{AMD:49, DR:52, POAG:58}，白内障 0。故 A 无据，降为 B。"),
    "r13": ("B", "medium",
            "引文 10.1371/journal.pone.0089923 为 BMI×白内障的前瞻队列 meta 分析，"
            "属 B 级；A 级保留给监管标签/临床指南。与 r10 同因：本项目不存在可及的"
            "白内障指南（PubMed 0 命中；aao_ppp 缓存无白内障；语料指南块不含白内障）。"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    lines = YAML.read_text(encoding="utf-8").split("\n")
    out, cur, changed, in_rules = [], None, [], False
    for ln in lines:
        st = ln.strip()
        top = (bool(ln) and not ln[0].isspace()
               and not st.startswith("#") and not st.startswith("- "))
        if top:
            in_rules = st.startswith("rules:")
            if not in_rules:
                cur = None
        if st.startswith("- id:"):
            cur = st.split(":", 1)[1].strip().split("_")[0] if in_rules else None
        if cur in TARGETS:
            lv, sev, why = TARGETS[cur]
            if st.startswith("evidence_level:") and st.split(":", 1)[1].strip() != lv:
                out.append(f"  evidence_level: {lv}")
                changed.append((cur, "evidence_level", lv))
                continue
            if st.startswith("severity:") and st.split(":", 1)[1].strip() != sev:
                out.append(f"  severity: {sev}")
                changed.append((cur, "severity", sev))
                continue
            if st.startswith("rationale:") and "降级依据" not in ln:
                out.append(ln.rstrip() + f"【2026-10-16 降级依据 A→B】{why}")
                continue
        out.append(ln)

    text = "\n".join(out)
    import yaml as _y
    try:
        d = _y.safe_load(text)
        assert len(d["rules"]) == 21
        assert len(d.get("patient_factor_rules") or {}) == 4
    except Exception as e:
        print(f"REFUSING TO WRITE: {e}")
        return 1

    print(f"changes: {len(changed)}")
    for c in changed:
        print(f"  {c[0]:6s} {c[1]:16s} -> {c[2]}")
    if not a.apply:
        print("\n(dry run -- pass --apply to write)")
        return 0

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    (ROOT / ".audit_tmp").mkdir(exist_ok=True)
    shutil.copy(YAML, ROOT / ".audit_tmp" / f"rules_pre_cataract_regrade_{ts}.yaml")
    YAML.write_text(text, encoding="utf-8")
    print(f"\nwritten; backup .audit_tmp/rules_pre_cataract_regrade_{ts}.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
