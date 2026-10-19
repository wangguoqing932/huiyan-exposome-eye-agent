"""Record the discovery-vs-hardcode finding: the system must discover, not list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 三十五、系统应当**发现**，不该写死——而写死当场就漏了一张表

### 作者的问题

**「不是说做 agent 论文系统吗」** —— 是的。所以上一节那两个覆盖还不够：
它们把**本项目的章节名与表名硬编码**了。那是给一个项目打的补丁，
**不是一套系统。**

### 差距的准确位置

查技能自身的设计意图：

| 位置 | 做法 |
|---|---|
| `build_submission_pkg.py` L117 | `tables.glob("table*.md")` —— **发现式** |
| `verify_figures_tables.py` L161 | `tables_dir.glob("table*.md")` —— **发现式** |
| `build_submission_pkg.py` L58 | `SECTION_ORDER = [...]` —— 硬编码（IMRaD 契约，可接受） |

**所以技能原本就是"表格发现、章节固定"。而我的覆盖把 8 个表名写死，
方向与技能设计相反。**

### 改写后立刻暴露的问题

**发现式一上去就找到 9 张表，而我硬编码的清单里只有 8 张：**

```
table1_registry.md
table1b_descriptives.md   ← 硬编码丢掉了它（3,924 B）
table2_rules.md
table3_performance.md
table4_validation.md
table5_heterogeneity.md
table5b_ipd_interaction.md
table6_power.md
table7_evidence_audit.md
```

**`table1b_descriptives.md` 正是本会话为 598,386 person-wave 分母问题专门建的那张表**
（含 8 队列逐队列参与者计数与 5 条脚注）。**硬编码把它静默丢掉了。**

**稿件 122,335 B → 126,196 B。**这是发现式在第一次运行时就收回的成本。

### 顺带修掉的排序问题

朴素字典序会把 `table10.md` 排在 `table2.md` 之前，并把带后缀的补充表排到所有编号表之后。
**改用数值为主键、后缀为次键**，于是顺序成为
`table1 → table1b → table2 → … → table5 → table5b → table6 → table7`，
与稿件里的呈现顺序一致。

### 这一节的教训（与本会话前几次同源）

| 前面的实例 | 本次实例 |
|---|---|
| Table 2 无生成器，改了分级它不改 | 表格清单写死，加了表它不装 |
| 投稿包图件因 `if not d.exists()` 永不刷新 | 同上 |
| **共同点：把"当前有哪些"当成常量，而不是去问** |

**"发现"这个动作本身就是校验：它每次运行都重新回答"有哪些"，
而写死的清单只在写下的那一刻正确。**

### 技能产出与自写脚本的当前差异

| | 我的脚本 | 技能流水线 |
|---|---|---|
| 表格 | 8 张（写死） | **9 张（发现）** |
| 稿件完整性检查 | 仅数表格引用 | **拒绝缺 Abstract/Declarations 的稿件** |
| 限额校验 | 无 | **有，且声明未确立的不冒充满足** |
| 投稿信未填字段 | **不检查就打包** | **拒绝打包** |
| 源漂移检测 | 无 | **逐源 SHA 复核** |

**作者要求"由技能产出"，收效是可量化的：多一张表、四处更严的门。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "系统应当**发现**，不该写死" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
