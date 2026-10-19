"""Record the prompt-sensitivity finding — the most important arbiter result so far."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十六、★ 仲裁层的等级是提示词措辞的函数

### 起因：我尝试做 §十四 的选项 B，但先撞上了别的

§十四 的结论是"`confidence` 由规则层独算、不反映仲裁的犹豫"，并留下
选项 B：让仲裁输出一个置信量并汇入。**本轮动手实施 B，结果没有达到目的，
而在排查过程中发现了更根本的事实。**

### 三个提示词变体，同一模型、同一温度、同一输入

为了实现 B，我给 `_ARBITER_SYSTEM` 的 JSON 字段表里加了 `confidence`。
第一版还写了一整段"何时取高值、何时取低值"的说明——**那是行为指令，
不只是让字段出现**。测得：

| 提示词变体 | `smoking × amd_late`（12 次） |
|---|---|
| **原始**（§十四 测的） | `{medium: 11, high: 1}` **摇摆** |
| **详细指令版**（我第一版） | **`{high: 6}` 恒定上调** |
| **极简版**（只把 `confidence` 加进字段列表） | **`{medium: 12}` 零变化** |

对照配对 `smoking × cataract_any` 在三个变体下都是 `{medium: 12}`。

**三者的模型、温度（0.0）、输入、规则层输出完全相同。
唯一差别是 JSON 字段表的措辞。**

### 这条事实的含义

1. **§十三/§十四 测到的"约 1/12 变异"很可能不是该配对的固有性质，
   而是那版措辞的产物**——换一个措辞就是 0/12。
   **所以"温度已 0 仍变异"这个观察成立，但"变异属于这个配对"不成立。**
2. **仲裁层的等级实质上是提示词措辞的函数。**
   固定温度不能带来确定性；**提示词是比温度更强的杠杆**。
3. **任何提示词编辑都会静默改变系统行为**，而项目里**没有任何测试会捕获它**——
   21 条规则的规则层有回归测试（§二），仲裁层没有。

### 对选项 B 的影响：存在观察者效应

我原以为"请它报一个置信度"是加字段，实测它是**改行为**：
详细版把摇摆变成恒定上调，极简版把摇摆变成恒定不动。
**一个用来度量判断不确定性的问题，本身改变了判断。**

**而且极简版自陈的置信度并不能识别边界情形**：它给 `smoking × amd_late`
报 0.85（高置信），而该配对正是规则层判 medium 的那个。
**即：仲裁对它自己的上调很自信，系统仍无从知道这里曾摇摆过。**

### 因此 B 的正确形态不是改分级提示词

**已实现且无害的部分**（本轮已落盘，可保留）：
- `RiskAssessment.arbiter_confidence: float | None` 与 `arbiter_rationale`——
  独立字段，不改 `confidence` 的既有语义，streamlit 的 `float(confidence)` 契约不变
- `_run_arbiter` 在**两条返回路径**都记录它（同意不改级的那条也记，
  否则该字段会变成"改级样本"的有偏集合）
- `report.metadata` 暴露二者

**未做且不该照现方案做的部分**：把"请给 confidence"写进分级提示词。
**正确做法是把它拆成对同一结论的独立追问**（先定级、再单独问该级的确定程度），
使度量不进入决策路径。**这需要改一次调用结构，属设计决定。**

### 顺带确立：仲裁层缺少回归测试

规则层有确定性回归测试；**仲裁层没有任何测试**，
所以本轮我改了提示词、行为从 0% 摆动到 100% 上调，
**若不是我刻意测三次并比对，这件事不会被任何检查发现。**

**建议**：为仲裁层加一个固定的探针集（若干配对 × 若干次），
记录等级分布与 `arbiter_confidence`，在提示词或模型变更时重跑比对。
本轮用的 `scripts/agent_arbiter_determinism.py` 已是可用的雏形。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "仲裁层的等级是提示词措辞的函数" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
