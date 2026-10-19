"""Record the correction of the grade audit — the session's most important fix."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十九、★ 更正 §八–§十：那次评级审计的方法本身是错的

### 我错在哪

§八 判定"21 条规则中 11 条高评一级"，依据是每块的 `linked_rules` 字段：
r11 的链接块是 1×B + 3×C 且无 A，于是判它声明的 A 级不成立，并据此**降级了 11 条规则**。

**该判定不成立，原因是一条事实：**

```
语料中 AAO PPP 块: 159
其中 A 级:          34
其中 linked_rules 非空的: 0        ← 全部为空
```

**语料里确实有指南级证据，只是"规则↔指南"的链接从未建立。**
而检索层是拿得到它们的——对 `smoking × amd_late`，agent 实际取回了
`[A] AAO PPP AMD - Section 9`，其原文逐字为：

> "Risk factors for the development of advanced AMD include **smoking**,
> increasing age, northern European ancestry, and genetic factors.
> **Cigarette smoking has been identified as the primary modifiable risk factor**
> in numerous studies on advanced AMD. It is strongly recommended to advise
> patients with AMD or those at risk for AMD to stop smoking."

**这是指南级的直接陈述。r11 声明的 A 级本来就是对的，是我的审计错了。**

### 错误的性质——本会话反复出现的同一类

**我把一个空字段读成了一条实质结论。**

- §七：`usecols` 在读文件时丢掉列 → 变量显示"不可用"，而代码里再映射也看不到
- §十二：探错属性名（`evidence_store` 实为 `store`）→ 三层齐备的 agent 被报成缺一层
- §十二：`out_of_scope` 找错位置（在 `metadata`）→ 两个真越界被报成 0
- **§八：`linked_rules` 为空 → 判"无指南证据"**

**前三次我都在同一份输出里找到了反证（6 探针各 5 条证据、越界探针等级是 unknown）。
这一次没有——因为 `linked_rules` 为空这件事本身不产生任何矛盾输出，它只是安静地什么都没说。**

### 已回退

**r11 恢复 A/high**，理由（AAO PPP Section 9 原文）写入其 rationale，
`tests/test_risk_rules.py::test_smoking_amd` 的断言一并改回，并在 docstring 里
写明两次改动的完整经过。`direction` 未动，故**队列层与论文数字不受影响**。

现分布：**A=1, B=6, C=14**（回退前 A=0, B=7, C=14）。

### 其余 10 条：我不能说它们对，也不能说它们错

**我尝试用"扫描语料文本"代替 `linked_rules` 重新审计，而该尝试同样不可用。**
两轮都失败：

| 尝试 | 失败方式 |
|---|---|
| 子串匹配 | `"lead"` 命中 `"leading cause"`——182 块 vs 词边界的 56 块，**126 块假匹配** |
| 词边界匹配 | 仍无法区分"指南陈述了 X"与"指南的**参考文献列表**里有标题为 X 的论文" |

第二条的实证：r08 的"A 级命中"是 `AAO PPP AMD - Section 58`，其正文为
`"Age-Related Macular Degeneration PPP P60 49. Hyman L, Schachat AP, ... "`
——**那是第 49 号参考文献条目**。而 r10 的"A 级命中"是
`[A] Appraising the causal role of smoking in multiple diseases:
A systematic review and meta-analysis`——**它是 meta 分析**。

### 顺带查出的第三件事：语料自身的分级也有错

上面那条 meta 分析在**语料里被标为 A 级**，而按项目纪律 A 只给监管标签/指南、
meta 分析是 B。**所以 `evidence_level` 这个字段本身也不完全可靠。**

### 因此的结论

**本项目的规则分级目前处于"未经可靠核验"的状态**，具体地：

1. **`linked_rules` 不可用作评级依据**——159 个 PPP 块全为空，用它审计会系统性漏掉指南证据
2. **关键词扫描不可用作评级依据**——既漏（PPP 正文）又误（参考文献条目、标题巧合）
3. **`evidence_level` 不可用作评级依据**——至少有一块 meta 分析被标成 A

**唯一可靠的核验方式是逐条读原文**，如我对 r11 所做。**21 条规则需要这样过一遍，
这是一次人工精读任务，不是脚本任务。**

**我未对其余 10 条做任何改动**——在无法判定时不动，比按一个已知不可靠的方法再动一次要好。
§八 的降级仍在生效，但**其依据已被证伪，应视为待复核而非已定论**。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "更正 §八–§十" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
