"""Append the arbiter-reliability findings to the agent audit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 六、LLM 仲裁层可靠性（首次测试）

第三层是 LLM 在决定风险等级，三项性质此前从未测过。

### 1. 重复一致性 ✅

同一案例（`fasting_glucose × cataract_any` + `diabetes`）跑 5 次：

```
run 1: high   run 2: high   run 3: high   run 4: high   run 5: high
distribution: {'high': 5}      稳定: YES      平均 3.1s/次
```

### 2. 越界处理 ✅

未注册实体必须读作 UNKNOWN（"看不了"），不能读作 LOW（"看了，没事"）：

| 输入 | 结果 |
|---|---|
| `aspirin × cataract_any` | unknown ✓ `out_of_scope=True` |
| `fasting_glucose × macular_hole` | unknown ✓ |
| `totally_unknown_exposure × cataract_any` | unknown ✓ |

**3/3 正确。**

### 3. 升级硬底线 ⚠️ **未被实证**

6 个案例实测 `arbiter_floor_triggered` **全部为 False**：

| 案例 | 规则层 | 仲裁后 | floor 触发 | backed |
|---|---|---|---|---|
| `fasting_glucose × cataract_any` +diabetes | high | high | False | True |
| `hba1c × dr_npdr` +diabetes | high | high | False | True |
| `hba1c × retinopathy_any` +diabetes | high | high | False | True |
| `fasting_glucose × dr_pdr` +diabetes | high | high | False | True |
| `serum_uric_acid × cataract_any` +CKD | medium | medium | False | False |
| `pm25_exposure × glaucoma_iop_elevated` +hypertension | medium | **high** | False | False |

**`safety_agent.py` 中"患者因素支持的 high 不可被仲裁降级"这条防线，
在这 6 个案例中从未被触发——因为 LLM 每次都同意或上调。**

**结论的措辞必须准确**：我上一轮写的"硬底线恢复生效"应更正为
**"硬底线具备了触发条件（`escalation_backed_high` 现在可以是真的），
但其拦截逻辑仍未经过实证检验"**。其正确性目前只有代码审查支撑。

要实证它，需要一个 LLM 确实建议降级的案例；这不能靠构造输入保证，
只能靠更大样本或对抗性提示。**列为未完成项。**

### 4. 新观察：仲裁层可以越过规则层

`pm25_exposure × glaucoma_iop_elevated` + `hypertension`：
规则层 medium（高血压对该规则的 floor 也是 medium，无升级），
**而仲裁把它升到 high**。

即：**修复之后，最终等级仍不完全由规则决定。** 这是"仲裁"这个名字的本意，
但它有一个具体后果——**该案例报告里的 high 没有规则层依据**，
读者从报告看不出这个 high 是 LLM 加的。审计建议：
报告应在仲裁层改变了等级时**显式标注**（现有元数据里的
`level_before_arbiter` 在 JSON 里有，但 report_text 里没有）。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "LLM 仲裁层可靠性" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
