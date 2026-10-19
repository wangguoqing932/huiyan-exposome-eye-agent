"""Record the determinism and confidence findings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十四、仲裁的不可重复性：不是采样参数，且置信度救不了它

### 上一节留下的问题，已用测量关闭

§十三 发现 `smoking × amd_late` 五跑一变成 high，并列出三个选项让作者决定。
**其中"设 temperature=0 重测"不是行为设计，是测量——所以不该拿来问。**

### 测量一：0 温下仍然变（`scripts/agent_arbiter_determinism.py`）

代码里温度默认本就是 0.0（`HUANYU_BULK_TEMPERATURE` 默认 0.0，
且未设 `HUANYU_ARBITER_TEMPERATURE`）。本轮在两通道上**显式钉住 0.0** 后测 12 次：

```
primary: temperature=0.0  model=deepseek/deepseek-v4.1-flash
arbiter: temperature=0.0  model=deepseek/deepseek-v4.1-flash

smoking x amd_late        final={'medium': 11, 'high': 1}   rule={'medium': 12}
smoking x cataract_any    final={'medium': 12}              rule={'medium': 12}
```

**结论：温度不是原因。**0 温下同一输入仍在约 1/12 的运行里被上调。
**所以"改温度"这条补救被排除**，变异来自提供方对
`deepseek/deepseek-v4.1-flash` 的serving，不是本项目能设的参数。

对照配对 12/12 稳定、规则层 12/12 稳定 ——
**所以不稳定是集中在一个配对上的，不是全域噪声。**

### 测量二：置信度无法标记这种边界情形（`scripts/agent_arbiter_confidence.py`）

假设：不稳定的那个配对是因为仲裁在那里接近决策边界，那么它的 `confidence`
应当更低。6 次重复：

| 配对 | 等级分布 | confidence |
|---|---|---|
| **smoking × amd_late** | **{medium: 4, high: 2}** | **0.60** |
| smoking × cataract_any | {medium: 6} | **0.60** |
| pm25 × glaucoma +hypertension | {medium: 6} | **0.60** |
| fasting_glucose +diabetes | {high: 6} | 0.80 |
| aspirin（越界） | {unknown: 6} | 0.00 |

**边界情形与两个稳定情形报同一个 0.60。假设不成立。**

### 根因：置信度是纯规则层的量（`risk_rules.py:316-320`）

```python
top_level = max((s.risk_level for s in signals), key=...)
strength  = SEVERITY_STRENGTH.get(top_level.value, 0.1)
n_same    = sum(1 for s in signals if s.risk_level == top_level)
agreement = 0.2 if n_same >= 2 else 0.0
total     = min(1.0, strength + agreement + evidence_confidence(evidence_chunks))
```

**`confidence` = 最高等级强度 + 规则间一致性 + 证据置信度。**
**仲裁的结果不进入这个式子**——它在规则层就被算完了。

所以同为 medium、单规则、同证据的三个配对必然同为 0.60，
**这在结构上就不可能反映仲裁的不确定性**。

### 这条发现的价值

它把"系统不稳定"从一句抱怨变成一条**可修的结构性事实**：

**若要让系统在仲裁不确定时自我标记，仲裁的输出必须带一个置信量并
汇入 `total`；现状下无论仲裁多犹豫，`confidence` 都照旧。**

### 三条路（现在只剩两条是实解）

| | 内容 | 评价 |
|---|---|---|
| ~~A~~ | 设 temperature=0 | **本轮已排除**——已 0 温，仍变 |
| **B** | 让仲裁输出一个置信量并汇入 `confidence`，边界情形显式标记 | **唯一能保留仲裁设计价值又能自陈不确定的做法** |
| **C** | 仲裁降为"建议"，最终等级一律取规则层 | 最可重复，但失去仲裁价值 |
| D | 接受并声明"最终等级含 LLM 判断，同一输入可能不同" | 诚实，但等于把问题交还给使用者 |

**未动手**：B 要改 `RiskAssessment` 的语义与仲裁提示词，C 要改分工——
都属 agent 行为设计，须你定。**但 A 已由测量排除，不再需要你判断。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "仲裁的不可重复性：不是采样参数" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
