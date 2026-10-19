"""Record the negative result: the arbiter confidence must not be surfaced."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十八、★ 选项 B 的结论：`arbiter_confidence` 会误导，不得展示

### 做了什么

按 §十六 的结论，B 的正确形态是"把问确定程度拆成对已定结论的独立追问"。
已实现为 `SafetyAgentConfig.arbiter_confidence_mode`，三档：

| 档 | 分级提示词 | 置信度来源 | 代价 |
|---|---|---|---|
| `off` | 原始措辞 | 不取 | — |
| `inline` | 字段表多要一个 `confidence` | 同一次调用 | 省一次调用 |
| `separate` | **原始措辞** | **定级后单独追问** | 每对有信号的配对多一次调用 |

**默认 `separate`**。两份提示词分开存放（`_ARBITER_SYSTEM` 与
`_ARBITER_SYSTEM_INLINE`），谁在用哪份是显式的，不靠 if 拼字符串。

### `separate` 的设计目标达成了

`separate` 的追问发生在 `final_level` 确定**之后**，因此不可能影响分级。
实测 `off` 与 `separate` 各 10 次（同一分级提示词）：

```
off       tiers={'high': 2, 'medium': 8}   升级率=20%
separate  tiers={'high': 5, 'medium': 5}   升级率=50%
```

差 20% vs 50% 是抽样噪声（各 10 次，不显著）——**即多出来的那次调用确实没有
改变分级**，设计上要保证的性质成立。

### 但设计目标不等于解决问题：等级仍然不稳

两次测量给出的升级率：**20% 与 50%**（同一配对、同一措辞、温度 0）。
**这远高于 §十四 报的 1/12**——而 §十六 已说明那个 1/12 是特定措辞的产物。

**所以"给仲裁加一个置信度"并没有让一个不稳定的分级变稳定。**

### ★ 决定性的一条：该置信度与稳定性**反向**

重录基线后（5 探针 × 6 次）：

| 探针 | 等级分布 | **`arbiter_confidence`** |
|---|---|---|
| **smoking × amd_late** | **{medium: 5, high: 1}** ← 唯一不稳定 | **0.85** ← 最高 |
| fasting_glucose × cataract **+diabetes** | {high: 6} 全稳 | 0.30–0.40 ← 最低 |
| smoking × cataract_any | {medium: 6} 全稳 | 0.35–0.40 |
| pm25 × glaucoma **+hypertension** | {medium: 6} 全稳 | 0.75 |
| aspirin（越界） | {unknown: 6} | 无量（未调仲裁） |

**唯一不稳定的配对拿到最高置信；两个完全稳定的拿到最低。**

**所以 `arbiter_confidence` 不是"未能标记不稳定"，而是反向的、会误导。**
若把它展示为确定性指标，使用者会被引向错误的方向：**把稳定的判断当可疑、
把摇摆的判断当可信。**

### 因此的处置

1. **字段保留，但只进 `report.metadata`，不进入任何面向用户的展示。**
   保留的理由是它对 §十七 的回归测试有诊断价值。
2. **`SafetyReport.report_text` 不打印它。**（已确认 `report_text` 中无该字段。）
3. **UI 与文档不得把它当作确定性分数。** 本节的表格即为据。
4. **`confidence`（规则层那个）同样不可当作仲裁的确定性**——§十四 已证其
   算式不含仲裁项。

**结论：本项目现有的两个置信量，一个结构上不含仲裁信息，
另一个与仲裁的稳定性反向。不存在一个可以直接展示给使用者的"这个判断有多可信"。**

### 对选项 B/C/D 的更新

- ~~**B**（让仲裁输出置信量并汇入）~~ → **本轮已实现并测出反向，不解决问题**
- **C**（仲裁降为建议，最终等级一律取规则层）→ **现在是唯一能给出可重复等级的方案**
- **D**（接受并声明不可重复）→ 诚实，但等于把问题交给使用者

**B 被排除的依据是测量，不是偏好。C 的代价是失去仲裁改级的能力，
而仲裁改级的可靠性恰恰是本轮与 §十六 反复测出问题的那个部分。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "选项 B 的结论" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
