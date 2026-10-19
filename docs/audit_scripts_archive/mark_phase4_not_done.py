#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mark PLAN.md's Phase 4 with its real status.

PLAN.md lists four validation phases with acceptance criteria. Three were
carried out. The fourth -- an 8-case x 3-expert blind panel with a kappa
threshold -- was never conducted, and the plan does not say so, so a reader
sees four phases and no indication that one of them never happened.

The project already handled this correctly at the data layer: the figure-3
source CSV states in plain terms that the panel was not collectable and that
fabricating ratings would be research fraud, and the figure-3 contract was
superseded by the confirmatory rule-evaluation figure. The manuscript never
mentions expert evaluation or kappa. Only the plan is out of date.

Marking it does not change any result. It changes what the plan claims.

Run: python scripts/mark_phase4_not_done.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "PLAN.md"

OLD = """### Phase 4：盲法专家评估（n = 8 cases × 3 experts）

**验收**：系统-专家 κ ≥ 0.6；Fleiss κ ≥ 0.6。"""

NEW = """### Phase 4：盲法专家评估（n = 8 cases × 3 experts）—— **未进行**

**原验收标准**：系统-专家 κ ≥ 0.6；Fleiss κ ≥ 0.6。

**实际状态（2026-10-16 据实补记）：该阶段从未开展。**

- 未招募专家、未收集任何评分，**因此没有任何 κ 值**
- `outputs/figures/source_data/figure3_expert_agreement.csv` 中留有明确记录：
  `NOT_COLLECTABLE: 4-expert blind panel was never conducted in this project.
  Fabricating expert ratings would constitute research fraud.`
- 原 figure3 契约（专家一致性）已被 `figure3_rule_evaluation` 取代，
  图 3 改为呈现确证三态结果
- **稿件全文不含 expert / kappa / blinded panel 任何表述**（已 grep 确认），
  故不影响已报告的结论

**对本项目的影响**：四阶段验证中 Phase 1–3 已完成，
Phase 4 缺失意味着**系统输出未经人类专家盲法核验**，
"与专家判断一致性"这一主张**在本项目中无证据支持，不得写入论文**。

**若日后要补做**：需 8 个案例 × 3 位眼科专家、盲法、预先注册评分表与 κ 阈值；
在此之前任何 κ 数值都不得出现在任何产物中。"""


def main() -> int:
    t = PLAN.read_text(encoding="utf-8")
    if "该阶段从未开展" in t:
        print("already marked")
        return 0
    if OLD not in t:
        print("anchor not found -- inspect PLAN.md manually")
        return 1
    PLAN.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("PLAN.md Phase 4 marked as not conducted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
