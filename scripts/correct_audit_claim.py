"""Correct a wrong claim in the agent audit.

I wrote that "the reader cannot tell from the report that the high was added by
the LLM". That is false. The report prints an explicit LLM-arbiter line stating
the rule engine's level, the patient factors, the evidence relied on and the
direction of the change. Corrected here rather than left standing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

OLD = """即：**修复之后，最终等级仍不完全由规则决定。** 这是"仲裁"这个名字的本意，
但它有一个具体后果——**该案例报告里的 high 没有规则层依据**，
读者从报告看不出这个 high 是 LLM 加的。审计建议：
报告应在仲裁层改变了等级时**显式标注**（现有元数据里的
`level_before_arbiter` 在 JSON 里有，但 report_text 里没有）。"""

NEW = """即：**修复之后，最终等级仍不完全由规则决定。** 这是"仲裁"这个名字的本意。

**更正（同一轮内自查）**：我先前在本节写下"读者从报告看不出这个 high 是
LLM 加的"，**这是错的**。实测该案例的 `report_text` 里有专门一行：

```
- **LLM 仲裁**: 规则引擎为 medium 且患者因素（hypertension）非空，但证据 [EV1]
  显示 PM2.5 经 NLRP3 焦亡通路直接导致 IOP 升高，[EV3] 在大型人群队列中支持
  PM2.5 与青光眼/IOP 的关联，机制与人群证据一致且无矛盾，故上调一级至 high。
```

**报告显式写出了规则层等级、所依据的证据块编号、以及调整方向。**
因此"仲裁层改变了等级却未披露"这一指控不成立，审计建议撤回。

保留的观察只有一条中性的：**最终等级依赖 LLM，因此不是纯确定性的**——
这是设计选择，且该选择是被披露的。若要追求完全可复现，需在
`SafetyAgentConfig` 里把仲裁限制为"只降不升"或全部关闭（`use_llm_arbiter=False`），
两种模式现有代码都支持。"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "更正（同一轮内自查）" in t:
        print("already corrected")
        return 0
    if OLD not in t:
        print("anchor not found -- inspect manually")
        return 1
    DOC.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("correction applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
