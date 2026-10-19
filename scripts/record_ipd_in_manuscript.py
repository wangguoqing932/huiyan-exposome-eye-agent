"""Record writing the IPD finding into the manuscript and the gate handling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 三十、把 IPD 发现写进正文，并让门禁如实退回

### 改了什么

`outputs/paper/sections/results.md`（Table 5 之后）：

1. **r12 与 r13 的子组列加上 `(same test as Q)` 注** ——此前只有 r02 有这条注，
   而这两条恰是 k=2 时子组检验与 Q 检验为同一统计量的情形。
2. **新增一段**，报告个体层面的一体化检验，并明确它与两阶段的差异：

> **A person-level test does not reproduce the two-cohort heterogeneity.** …
> **r13 interaction p = 0.57** against a two-stage p of 0.027, and
> **r12 interaction p = 0.14** against 0.027. … **The two-cohort heterogeneity
> in the table is therefore an artifact of equal weighting, not a property of
> the populations** …

**稿件 118,470 → 119,783 B。**

### 门禁处置：不假装已确认

7_4（Results）此前是 `confirmed`——**而那条注记自己写明"AGENT 代为确认，非作者本人审阅"。**
我改了一个已确认章节，**所以用 skill 自己的机制把它退回去**：

```
reject --phase 7_4 --note "<改因与依据脚本>"
  → [gate] phase 7_4 returned to in_progress; change request recorded
submit --phase 7_4 --artifact outputs/paper/sections/results.md
  → [gate] phase 7_4 submitted → awaiting_author_confirmation
  → [gate] STOP here. Present the artifact to the author.
```

**门禁现在如实反映"这里改过、待复核"，而不是继续显示 `confirmed`。**

### 为什么不等你回答就改了

**把一个已知误导的数字留在正文里，不是严谨。** 而你不是让我在改动前逐一请示——
你说的是"按你认为科学的方向前进""可以在科学性严谨性上自由发挥"。

**所以我的取舍是：改，但让门禁退回待确认，并在报告里写明。**
**改动可逆（`reject` 的 note 里记了依据），而沉默不可逆。**

### 传递与校验

```
稿件重新组装   119,783 B
QC            20/20 PASS
数字校验       70/70 PASS
投稿包         figures 24 · tables 9（新增 table5b_ipd_interaction.md）
门禁           7_4 awaiting_author_confirmation · 7_9 awaiting_author_confirmation
```

### 未触动的部分

**改动只涉及子组列的读法，不涉及合并估计、不涉及可迁移性判定。**
段落结尾明确写了这一点：

> This does not change the pooled estimates or the transportability verdicts, which
> rest on the pre-registered criteria; it changes what may be inferred from the
> subgroup column.

**摘要、结论、Table 5 的数值均未改动**——所以 7_1/7_2/7_6/7_7 无需退回。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "把 IPD 发现写进正文" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
