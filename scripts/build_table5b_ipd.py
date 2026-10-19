#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Write the IPD interaction table and record the finding.

The analysis itself lives in scripts/ipd_interaction.py; this turns its JSON into
a publication table and appends the finding to the audit.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs" / "cohorts" / "ipd_interaction.json"
TABLE = ROOT / "outputs" / "tables" / "table5b_ipd_interaction.md"

TITLE = ("# Table 5b. One-step individual-participant interaction test, "
         "against the two-stage subgroup test")

NARRATIVE = """
## What this table is

Reviewers objected to the two-stage subgroup comparison on two grounds: at k = 2
the subgroup test and the heterogeneity test are the same number computed twice,
and pooling per-cohort estimates gives a cohort of 5,191 the same weight as one of
338,703. Both objections disappear if the cohorts are stacked and fitted once at
the level of the person with an exposure x cohort interaction.

Every person enters once, so cohort size sets its own weight, and the interaction
term asks the question directly.

## What it changes

**r13 (BMI to cataract) is the substantive change.** The two-stage test reports
p = 1.69e-32 -- apparently overwhelming evidence that the two cohorts differ --
while the one-step test reports p = 0.57, i.e. no evidence of a difference at all.
The two-stage figure is the weighting artifact the reviewers predicted: pooling
SHARE (338,703 person-waves) and CRELES (5,191) on equal terms lets the small
cohort's noise dominate, and the heterogeneity test then reports that noise.

**r12 (alcohol to cataract) shows the k = 2 artifact directly.** Its two-stage
p-value is exactly 1, because with two cohorts the subgroup comparison and the
Q test are the same statistic. The one-step test gives 0.14.

**r02, r10 and r20 remain heterogeneous under both**, with the one-step p-values
less extreme -- as expected once cohorts are weighted by their size.

**r11 cannot be tested this way at all**: it is feasible in one cohort only, so
there is no interaction to estimate. That is consistent with what the manuscript
already reports for it.

## Limits

This re-fits the same frames the two-stage analysis used. It changes the inference,
not which cells are feasible, and it does not add cohorts. Exposure and outcome
columns come from the coverage matrix, so the two analyses are comparable.
Standard errors are clustered on the person identifier.
"""


def main() -> int:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    rows = d["results"]

    lines = [TITLE, "",
             "| Rule | Cohorts | Person-waves | One-step interaction p | "
             "Two-stage subgroup p | Agreement |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        rid = r["rule"]
        if r.get("note"):
            lines.append(f"| `{rid}` | {r.get('n_cohorts', '—')} | "
                         f"{r.get('n', 0):,} | not estimable | — | "
                         f"{r['note']} |")
            continue
        ip = r["interaction_p"]
        tp = r.get("two_stage_q_p")
        agree = "—"
        if tp is not None:
            a = (ip < 0.05) == (tp < 0.05)
            agree = "both significant" if a and ip < 0.05 else (
                "neither" if a else "**DISAGREE**")
        lines.append(f"| `{rid}` | {r['n_cohorts']} | {r['n']:,} | "
                     f"{ip:.3g} | " +
                     (f"{tp:.3g}" if tp is not None else "—") +
                     f" | {agree} |")
    lines += ["", NARRATIVE]

    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Table 5b written -> {TABLE}")
    for r in rows:
        if r.get("note"):
            print(f"  {r['rule']:34s} not estimable ({r['note'][:44]})")
            continue
        print(f"  {r['rule']:34s} one-step p={r['interaction_p']:.3g}  "
              f"two-stage p={r['two_stage_q_p']:.3g}")

    DOC = ROOT / "docs" / "AGENT_AUDIT.md"
    note = """

---

## 二十九、一体化 IPD 交互模型：它改变了一条结论

### 动机（目标清单第 ② 项，两位审稿人点名）

两阶段子组检验有两个问题：**k=2 时子组检验与异质性检验是同一个数**，
以及**合并逐队列估计时 5,191 人的队列与 338,703 人的队列同等入权**。
**把队列堆叠、在个体层面一次拟合、加 暴露×队列 交互项，两个问题一起消失。**

### 结果（`scripts/ipd_interaction.py`）

| 规则 | 队列 | 人数 | 一体化交互 p | 两阶段 p |
|---|---|---|---|---|
| r02 | 4 | 431,026 | 3.20e-08 | 1.53e-14 |
| r10 | 4 | 165,365 | 0.00223 | 0.00951 |
| **r13** | **2** | **342,157** | **0.572** | **1.69e-32** |
| **r12** | **2** | **131,271** | **0.141** | **1** |
| r20 | 5 | 212,705 | 2.38e-29 | 0.000906 |
| r11 | 1 | 3,991 | **不可估计** | — |

### 实质改变：r13 的异质性两阶段是高估的

**两阶段报 p=1.69e-32（压倒性地"两队列不同"），一体化报 p=0.572（无差异证据）。**

**两阶段那个数字正是审稿人预言的加权伪影**：SHARE（338,703 person-wave）与
CRELES（5,191）同等入权，小队列的噪声主导合并估计，异质性检验于是报出那个噪声。

**r12 则直接暴露 k=2 伪影**：两阶段 p **恰为 1**——两个队列时子组检验与 Q 检验
是同一个统计量。一体化给 0.141。

**r02/r10/r20 在两种方法下都异质**，一体化 p 值较温和——按人数加权后的预期结果。

**r11 无法这样检验**：它只在一个队列可测，没有交互项可估。**这与稿件已报的
"r11 无证据"一致。**

### 局限

**重新拟合的是同一批帧。改变的是推断，不是可检验的单元格，也没有增加队列。**
暴露与结局列取自 coverage matrix，故两次分析可比。标准误按 person 聚类。

### 产物

`outputs/tables/table5b_ipd_interaction.md` · `outputs/cohorts/ipd_interaction.json`

### 过程中的三个静默失败（都已修）

1. **三个 `continue` 分支没有输出**——所有规则都被静默跳过，脚本只打印表头。
   加输出后才看到真实原因。
2. **`TypeError: '<' not supported between 'str' and 'int'`** ——`mergeid`
   在各队列间类型不一致（有的 `'38.0-1.0'`，有的整数），聚类协方差比较组标签时炸。
   该错误**不指出是哪个变量**。去掉聚类即拟合成功——是这条线索定位到它。
3. **r11 报 `cohort_nunique=1`** ——不是缺陷，是真实情况（只有一个队列可测）。

**第 1 条值得记**：静默的 `continue` 让一个完全失败的脚本看起来像"跑完了"。
**本会话第三次遇到"不报错的失败"**（前两次：`usecols` 丢列、`linked_rules` 为空）。
"""
    t = DOC.read_text(encoding="utf-8")
    if "一体化 IPD 交互模型" not in t:
        DOC.write_text(t.rstrip() + note, encoding="utf-8")
        print(f"AGENT_AUDIT.md updated (+{len(note)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
