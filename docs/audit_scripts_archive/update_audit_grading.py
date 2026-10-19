"""Record the systematic rule over-grading finding in the agent audit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 八、★ 系统性发现：21 条规则中 11 条高评一级

### 方法

逐条取规则的**首篇引文 DOI**，经 Crossref 解析、再经 PubMed 取摘要与
`PublicationType`，按项目自己的分级纪律判定：

```
A = 监管标签 / 指南        → severity high
B = Meta 分析 / 系统综述   → severity medium
C = 原创研究              → severity low
```

**18 条规则只有 1 篇引文**，对它们该引文即全部依据；3 条有 2 篇
（r07/r09/r18），第二篇亦已核。**21 条全部有 PubMed 记录。**

### 结果

| 规则 | 声明 | 引文的实际类型 | 应为 |
|---|---|---|---|
| **r10** smoking×cataract | **A** | PubMed 类型含 **Meta-Analysis + Systematic Review** | **B** |
| **r13** BMI×cataract | **A** | "…: A **Meta-Analysis** of Prospective Cohort Studies"（PLoS ONE） | **B** |
| r03 hba1c×retinopathy | B | Journal Article，摘要无综述方法学 | **C** |
| r08 antioxidants×cataract | B | Journal Article + Review（叙述性综述，非 meta） | **C** |
| r09 Mediterranean diet×AMD | B | 1st 原创；2nd **Randomized Controlled Trial** | **C** |
| r12 alcohol×cataract | B | Journal Article | **C** |
| r14 lead×cataract | B | Journal Article | **C** |
| r16 PM2.5×glaucoma | B | Journal Article，摘要无综述方法学 | **C** |
| r18 UV×cataract | B | 1st 原创；2nd 原创（GSTM1 多态性研究） | **C** |
| r20 smoking×vision | B | Journal Article | **C** |
| r21 PM2.5×vision | B | Journal Article | **C** |

**11 / 21（52%）声明了自身引文支撑不了的级别。**

对照组（评级成立）：r01/r04/r05/r22/r19（C 级 + 原创研究）、
r02/r06/r17（B 级 + 综述/meta 标题）、**r07（B 级 + 第二篇确为 Meta-Analysis）**、
**r11（已降为 B）**。

### 为什么这次不能像 r11 那样直接改

**r11 的降级是零波及的，因为它只改了一条规则。本项会波及两处：**

1. **`scripts/evaluate.py:555-566`**：
   ```python
   lvl = {r.id: r.evidence_level for r in rules}
   def _is_a(ids):
       got = [lvl.get(i.strip()) for i in ...]
       return bool(got) and all(g == "A" for g in got)
   ```
   筛出 **A 级配对**，供**第四态 `direction_review`**（analysis_plan §4 预注册触发）使用。

2. **稿件 Table 2** 含 `severity` 与 `evidence_level` 列；figure 2 图例按 severity 绘制。

### ★ 更深的一层：A 级层是空的

降级后**项目将没有任何 A 级规则**（r11 已降、r10/r13 待降）。
而 §4 的 `direction_review` 第四态**只作用于 A 级配对**——
**A 级层清空意味着这个预注册安全机制空转。**

**所以问题可能不是"评级偏高"，而是"A 级规则从未真正存在"**：
21 条规则里**没有一条的引文是监管标签或临床指南**，
全部是 meta 分析（至多 B）或原创研究（C）。

### 建议（需你定，因为它改结果）

| 方案 | 内容 | 代价 |
|---|---|---|
| **A** | 降 11 条规则的级别（A→B、B→C），severity 同步 | 内部层指标与 Table 2 变动；§4 第四态空转，需同时改 `evaluate.py` 的 A 级判据 |
| **B** | **为 r10/r13 找真正的指南引文**（如 WHO/AAO 白内障或 AMD 指南），使 A 级名副其实 | 需检索与人工判断；但能保住 §4 机制 |
| **C** | 保持现状，在文档中声明"A 级指本规则引文为综述级证据，非指南" | 不改数字，但需改分级定义与 UI 文案，否则分级名不副实 |

**我倾向 B + 对 9 条 B→C 采用 A**：
即**为两条 A 级规则补检索指南证据**（它们确实有——吸烟与白内障、
BMI 与白内障都有 AAO/WHO 级别的表述），
**同时把 9 条缺少 meta 支撑的 B 级降为 C**。
这样 A 级有实、B 级不虚，§4 机制继续可用。

**未动手**：本项会改内部层指标与 Table 2，属会向下游扩散的改动。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "系统性发现：21 条规则中 11 条高评" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
