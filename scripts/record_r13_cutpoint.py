"""Record the r13 cut-point defect and its sensitivity analysis."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 三十一、★ r13 用了与项目自身约定矛盾的 BMI 切点

### 缺陷

`outputs/confirmatory/cohort_rule_coverage.json` 在 r13（BMI → 白内障）的
两个可检验队列上**都用 `bmi_high_25`**：

```
r13 实际用的列:   CRELES → bmi_high_25     SHARE → bmi_high_25
项目自身约定:     CRELES = 30              SHARE = 30
                  （25 只给 KLoSA / LASI / CLHLS）
```

**约定写在 `scripts/build_descriptive_table.py` 里，并在别处一致使用；
唯一切点确为 25 的 KLoSA 在同一矩阵里被标为 `testable=False`，从未进入分析。**

**即：r13 的两个单元格都用错了切点，而唯一用对的那个队列没被用。**

### 这不是外观问题

**更低阈值把更多人划入暴露组，稀释对比，把 OR 压向无效。偏差方向可事先预知。**

### 敏感性分析（`scripts/r13_cutpoint_sensitivity.py`）

| 队列 | 约定切点 | **正确切点** | **实际用的** | 偏移 |
|---|---|---|---|---|
| **SHARE** | 30 | **OR 1.235** (1.194–1.278) p=1.2e-33 | OR 1.139 (1.105–1.175) p=8.9e-17 | **+0.096** |
| **CRELES** | 30 | OR 0.995 (0.816–1.213) p=0.96 | OR 1.082 (0.917–1.277) p=0.35 | −0.087 |

**SHARE 正如预测被低估**（1.139 → 1.235）。CRELES 两种切点下都是 null。

**结论不变**：SHARE 显著、CRELES 无效，两种切点下都一样。

### 但 Table 5 里 r13 的合并值建立在这个偏差上

稿件报 r13 合并 OR **1.14 (0.91–1.41)**。**该值用的是 SHARE 的 1.139；
用正确切点是 1.235。所以合并估计被同一偏差拉低。**

**未重算合并值**——那会改动 Table 5 的数值与 §三十 刚确认过的那一段，
**属需要作者复核的改动，本轮只做敏感性分析、只报告。**

### 与 §二十九/§三十 的关系

§二十九 发现 **r13 的两队列异质性是一体化检验证伪的加权伪影**（两阶段 p=0.027
vs 个体层面 0.572）。本节又发现**它的两个单元格还用错了切点**。

**两条合起来：r13 在稿件中的呈现有两个来源不同的偏差，方向一致——都使它的
两队列对比看起来比实际更强。**

### 该项在目标清单中的位置

这正是 B4–B18 里的"**r13 切点敏感性**"。**至此它不再是一个待办项，而是一条已量化的发现。**

### 待作者决定的事项

1. **是否用正确切点重跑队列层**（会改 Table 5 的 r13 数值，并可能改其三态判定）
2. **是否把本节写进正文**（作为敏感性分析）
3. **coverage matrix 的切点约定是否需要在校验里固化**——
   目前约定只存在于一个脚本的字典里，没有任何检查会阻止 r13 用错列
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "r13 用了与项目自身约定矛盾的 BMI 切点" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
