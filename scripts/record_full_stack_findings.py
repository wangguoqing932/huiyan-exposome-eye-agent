"""Record the full-stack test and the tier reproducibility finding."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十二、整栈测试：按应用的入口构造（首次）

### 为什么此前没测到

前面所有测试都是直接构造 `SafetyAgent(...)`。但全项目**唯一的
`agent.evaluate` 调用方是 `app/streamlit_app.py`**，而它自己不构造 agent——
它调用 `get_agent(use_real_llm, use_lightrag, top_k)`。
**所以用户真正跑的是 `get_agent` 里的那套配置，而它从未被端到端测过。**

这很重要，因为三层会以不同方式失效，而直接构造可能悄悄少掉两层：
`self.llm is None` 时仲裁直接返回，agent 看起来只是个规则引擎；
`self.lightrag is None` 时检索为空，报告有理由但无引文。

### 结果（`scripts/agent_full_stack_test.py`）

```
rule engine      : 21 rules
evidence store   : present
lightrag         : present
llm arbiter      : present
built in 5.5s
```

| 探针 | 最终等级 | 规则 | 证据 | 耗时 |
|---|---|---|---|---|
| smoking × cataract_any | medium | 1 | 5 | 5.4s |
| fasting_glucose × cataract_any **+diabetes** | **high** | 1 | 5 | 4.6s |
| pm25_exposure × glaucoma_iop_elevated **+hypertension** | medium | 1 | 5 | 4.8s |
| aspirin × cataract_any | unknown | 0 | 5 | **0.6s** |
| totally_unknown_exposure × cataract_any | unknown | 0 | 5 | **0.5s** |
| smoking × amd_late | medium | 1 | 5 | 4.5s |

**三层齐备，各路径都通**：4/6 产出信号、2/6 正确越界、6/6 有证据（各 5 条）。
患者因素升级生效（diabetes → high）；r11 降级生效（smoking×amd → medium）。

**越界探针耗时 0.5–0.6s，其余 4.5–5.4s**——说明越界在规则层短路，
未调用仲裁。这是合理设计，也让"是否越界"可被耗时识别。

### 本轮我自己的两个探针错误（已修正，未据此下结论）

1. 我探 `agent.evidence_store`，而 `SafetyAgent` 把它存在 **`self.store`**，
   于是三层齐备的 agent 被报成 `evidence_store: ABSENT`。
   **推翻它的证据就在同一份输出里**：6 个探针各返回 5 条证据。
2. 我探 `rep.out_of_scope`，而**该字段不在 `RiskAssessment` 或 `SafetyReport` 上**——
   它在 `report.metadata` 里（`safety_agent.py:316`）。于是两个真越界探针被报成
   `out_of_scope: 0`，而同一份输出里它们的等级正是 `unknown`。

**两次都是"用一个我以为存在的字段名去读，读到默认值就当成结论"。**
这与 §七 的 `usecols` 是同一类错误：**读不到不等于不存在，而默认值看起来像答案。**

---

## 十三、★ 等级可重复性：规则层确定，仲裁层会变

### 起因

整栈测试两次运行对同一输入给出不同等级：`smoking × amd_late` 首跑 `high`、
次跑 `medium`。两次之间我只改了两个探针属性名，不可能影响评估。

### 结果（`scripts/agent_tier_reproducibility.py`，每对 5 次）

| 配对 | 最终等级分布 | 规则层分布 | 判定 |
|---|---|---|---|
| **smoking × amd_late** | **{medium: 4, high: 1}** | {medium: 5} | **★ 变化** |
| smoking × cataract_any | {medium: 5} | {medium: 5} | 稳定 |
| fasting_glucose × cataract_any +diabetes | {high: 5} | {high: 5} | 稳定 |
| pm25 × glaucoma_iop_elevated +hypertension | {medium: 5} | {medium: 5} | 稳定 |

- **规则层自身变化数：0**（确定性设计成立 ✓）
- **仲裁层在 1/4 配对上引入运行间变异**：`smoking × amd_late` 约 20% 的运行
  被从 medium 上调为 high

### 为什么这条要写进审计

**规则层是确定的，而用户看到的最终等级不是。**
`smoking × amd_late` 这个具体的规则，其展示等级**不是输入的函数**——
同一输入五次里有一次不同。因此任何"系统将该规则判为 high"的陈述
**不可重复**。

**这是否可接受，取决于是否被告知。** 项目已做对的一半：
`report_text` 会打印 LLM 仲裁的改级动作（§五 已核实），
所以**单次输出内部是自洽的**；缺的是**跨运行的稳定性声明**。

**建议（需你定）**：
- **A**：对仲裁层设 `temperature=0` 并要求其在报告中给出改级的依据文本，
  再测一次可重复性——**若 0 温仍变化，则说明变化来自服务端而非采样参数**
- **B**：在文档与 UI 中声明"最终等级含 LLM 判断，同一输入可能不同"，
  并同时展示规则层等级（已在上表中可见）
- **C**：把仲裁降级为"建议"而非"改级"，最终等级一律取规则层——
  **最可重复，但会失去仲裁的设计价值**

**未动手**：改温或改分工属 agent 行为设计，须你定。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "整栈测试：按应用的入口构造" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
