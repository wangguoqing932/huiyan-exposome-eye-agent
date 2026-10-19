"""Update AGENT_AUDIT.md: the escalation defect is now fixed and verified."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

FIX = """

---

## 五、★ 修复已完成并验证（同轮）

### 改了什么

`src/huiyan_agent/risk_rules.py` 的 `load_rules`：**在加载期按 flag 匹配，把顶层
`patient_factor_rules` 落到每条规则的 `escalation_map` 上。**

```python
# 顶层规格：每条列出 severity 与适用的 entity_a / entity_b flags
# 加载时：若 rule.entity_a_flags ∩ matching_entity_a_flags 且
#         rule.entity_b_flags ∩ matching_entity_b_flags 均非空
#         → rule.escalation_map[factor] = severity
```

选择这个改法的三个理由：

1. **`match_rules` 一行未动** —— 它本来就会读 `rule.escalation_map`（文档第 (2) 条
   "直接抬到该级（floor）"），缺的只是数据没被填进去
2. **保留表达力** —— 顶层规格按实体 flag 决定是否适用，摊平成逐规则字段会丢失这个条件
3. **语义一致** —— 规格给的是目标 `severity`，正是 floor 语义

### 验证（`scripts/agent_escalation_regression.py`）

| 检查 | 结果 |
|---|---|
| **不带因素时 68 个配对的输出** | **与修复前审计逐条一致，0 丢失 / 0 新增 / 0 变化 → `IDENTICAL: YES`** |
| 升级触发数 | **0 → 17** |
| `escalation_backed_high` | **False → True**（那条死掉的防降级硬底线恢复生效） |
| 仍惰性的 3 例 | **非缺陷**：规则基线已是 medium，因素 floor 也是 medium，无可升级 |

**零波及证明**：`scripts/evaluate.py:458` 调用 `match_rules(rules, a, b)`
**不传患者因素**，因此内部层（NHANES/KNHANES/CHARLS）指标不受影响；
队列层三个脚本（confirmatory / heterogeneity / power）**根本不 import agent**。
受影响面仅为交互界面，而那是此前表现错误的地方。

### 后果

修复前：`fasting_glucose × cataract_any` + `diabetes` 的等级由 **LLM 仲裁**从
medium 抬到 high（元数据 `level_before_arbiter: medium`），规则层无贡献；
`safety_agent.py` 中"患者因素支持的 high 不可被仲裁降级"的安全底线
因 `escalation_backed_high` 恒为 False 而**永不触发**。

修复后：规则层在关闭 LLM 时（`use_llm_arbiter=False`）即产出
`risk_level = high`、`escalation_backed_high = True`。
**升级回到确定性层，LLM 不再需要为它兜底。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "修复已完成并验证" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + FIX, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(FIX)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
