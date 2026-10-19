#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regrade the 11 rules whose citations do not support their declared grade.

Verified in the previous rounds: each rule's cited DOI was resolved through
Crossref and PubMed, and the publication type and abstract were compared against
the project's own scheme (A = regulatory label or clinical guideline,
B = meta-analysis or systematic review, C = original research). Eleven of twenty-
one rules declare a grade their citation cannot carry:

    r10, r13        declare A, cite a meta-analysis            -> B
    r03, r08, r09, r12, r14, r16, r18, r20, r21
                    declare B, cite original research          -> C

severity is derived from the grade and enforced at load time
(_EVIDENCE_TO_SEVERITY rejects a mismatched pair), so both fields move together.

The consequence that must be stated rather than buried: after this change the
rule base has NO grade-A rule. Nothing in the corpus is a regulatory label or a
clinical guideline; the strongest evidence any rule cites is a meta-analysis.
evaluate.py's pre-registered fourth state (direction_review, analysis_plan
section 4) selects A-level pairs, so with no A-level rule that mechanism has no
subject. That is reported, not hidden, and the scheme is amended below to say A
is a reserved tier this rule base does not currently occupy.

Every changed rule gets the reason written into its rationale, so the correction
is visible where the rule is read.

Run: python scripts/regrade_rules.py            (dry run)
     python scripts/regrade_rules.py --apply
"""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "configs" / "rules.yaml"

# rule short id -> (new grade, new severity, why)
REGRADE = {
    "r10": ("B", "medium",
            "引文为 Meta-Analysis + Systematic Review（PubMed PublicationType），"
            "按分级纪律应 B 而非 A"),
    "r13": ("B", "medium",
            "引文为 'Body Mass Index and Risk of Age-Related Cataract — "
            "A Meta-Analysis of Prospective Cohort Studies'（PLoS ONE），应 B 而非 A"),
    "r03": ("C", "low", "引文为 Journal Article，摘要无综述方法学"),
    "r08": ("C", "low", "引文为叙述性 Review，非 meta 分析"),
    "r09": ("C", "low", "两篇引文分别为队列研究与随机对照试验，均非 meta 分析"),
    "r12": ("C", "low", "引文为 Journal Article，摘要无综述方法学"),
    "r14": ("C", "low", "引文为 Journal Article，摘要无综述方法学"),
    "r16": ("C", "low", "引文为 Journal Article，摘要无综述方法学"),
    "r18": ("C", "low", "两篇引文均为原创研究（其一为 GSTM1 多态性研究）"),
    "r20": ("C", "low", "引文为 Journal Article，摘要无综述方法学"),
    "r21": ("C", "low", "引文为 Journal Article，摘要无综述方法学"),
}

SCHEME_NOTE = """
# ── 分级纪律（2026-10-16 核实后补记）────────────────────────────────────
# A = 监管标签 / 临床指南    → severity high
# B = Meta 分析 / 系统综述   → severity medium
# C = 原创研究              → severity low
#
# 2026-10-16 逐条核验 21 条规则的首篇引文 DOI（Crossref 解析 + PubMed 摘要
# 与 PublicationType），发现 11 条声明了引文支撑不了的级别，已按上表降级：
#   r10, r13：声明 A，引文实为 meta 分析 → B
#   r03, r08, r09, r12, r14, r16, r18, r20, r21：声明 B，引文实为原创研究 → C
#
# **后果（如实声明）：本规则库当前没有任何 A 级规则。**
# 语料中不存在监管标签或临床指南；任何规则所引的最强证据是 meta 分析。
# 因此 evaluate.py 的 §4 预注册第四态（direction_review，只作用于 A 级配对）
# 暂无作用对象。A 级在本项目中是**保留层级、当前未被占用**，
# 待引入真正的指南级引文后再启用。
# 核验脚本：scripts/verify_rule_citations.py / _pubmed.py
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    lines = YAML.read_text(encoding="utf-8").split("\n")
    out, cur, changes = [], None, []
    # Section tracking. The file has two top-level keys that both contain
    # `severity:` lines: `rules:` (21 rules) and `patient_factor_rules:` (4
    # factors). An earlier version kept the last rule id in scope past the end of
    # the rules list, so it rewrote the four factor severities as though they
    # belonged to rule r21 -- visible in the dry run as a duplicated
    # "r21 severity" line. A second attempt reset the guard on every rule line,
    # because rule entries are themselves written at column 0 (`- id: ...`), so
    # the guard was already off by the time it was needed.
    #
    # The fix is to enter and leave sections on top-level keys only, treating a
    # line beginning with "- " as a list item rather than a key.
    in_rules = False
    for ln in lines:
        s = ln.strip()
        is_top_key = (bool(ln) and not ln[0].isspace()
                      and not s.startswith("#") and not s.startswith("- "))
        if is_top_key:
            in_rules = s.startswith("rules:")
            if not in_rules:
                cur = None
        if s.startswith("- id:"):
            full = s.split(":", 1)[1].strip()
            # REGRADE is keyed by the short id (r03), the file carries the full
            # id (r03_hba1c_x_retinopathy_any)
            cur = full.split("_")[0] if in_rules else None
        if cur in REGRADE:
            new_lv, new_sev, why = REGRADE[cur]
            if s.startswith("evidence_level:"):
                old = s.split(":", 1)[1].strip()
                if old != new_lv:
                    changes.append((cur, "evidence_level", old, new_lv))
                    out.append(f"  evidence_level: {new_lv}")
                    continue
            if s.startswith("severity:"):
                old = s.split(":", 1)[1].strip()
                if old != new_sev:
                    changes.append((cur, "severity", old, new_sev))
                    out.append(f"  severity: {new_sev}")
                    continue
            if s.startswith("rationale:"):
                note = f"【2026-10-16 降级更正 {REGRADE[cur][0]}/{REGRADE[cur][1]}】{why}。"
                if note not in ln:
                    out.append(ln.rstrip() + note)
                    continue
        out.append(ln)

    # keep the scheme note at the top of the file, once
    text = "\n".join(out)
    if "分级纪律（2026-10-16 核实后补记）" not in text:
        text = text.replace("risk_levels:", SCHEME_NOTE.strip() + "\n\nrisk_levels:", 1)

    print(f"changes: {len(changes)}")
    for rid, field, old, new in changes:
        print(f"  {rid:6s} {field:16s} {old:8s} -> {new}")

    if not a.apply:
        print("\n(dry run -- pass --apply to write)")
        return 0

    # Self-check before writing. An earlier run appended a correction note whose
    # text contained a colon inside an unquoted YAML scalar ("... Cataract: A
    # Meta-Analysis ...") and produced a file that would not parse. A script that
    # edits a config must refuse to write one it cannot itself load.
    import yaml as _yaml
    try:
        parsed = _yaml.safe_load(text)
        n = len(parsed["rules"])
        assert n == 21, f"expected 21 rules, parsed {n}"
        factors = parsed.get("patient_factor_rules") or {}
        assert len(factors) == 4, f"expected 4 patient factors, parsed {len(factors)}"
    except Exception as e:
        print(f"\nREFUSING TO WRITE: result does not parse or is malformed -- {e}")
        return 1

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    (ROOT / ".audit_tmp").mkdir(exist_ok=True)
    shutil.copy(YAML, ROOT / ".audit_tmp" / f"rules_preregrade_{ts}.yaml")
    YAML.write_text(text, encoding="utf-8")
    print(f"\nwritten; backup at .audit_tmp/rules_preregrade_{ts}.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
