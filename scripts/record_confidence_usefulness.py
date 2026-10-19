"""Record the arbiter-confidence usefulness measurement."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十四、`arbiter_confidence` 的有用性：首次在正常状态下实测

### 为什么现在才测

§十八 曾判它"与稳定性反向、会误导"，但那个测量是在**规则层被我错降 r11 破坏**的
状态下做的（§二十三）。既然理由被撤回，问题就重新开放——**而开放且可测的问题应当测掉。**

### 假设（来自重录基线时的观察）

恢复后的基线里，唯一指南支持的 A 级规则 `smoking × amd_late` 稳定报 0.9，
而 B/C 级规则报 0.2–0.85 且散。**假设：该字段跟踪规则的证据级别。**

### 结果（7 探针 × 8 次 = 56 次观测，温度 0）

| 探针 | 级别 | 等级 | 自陈置信 |
|---|---|---|---|
| current_smoking × amd_late | A | high | **0.85–0.90** |
| current_smoking × cataract_any | B | high | **0.85** |
| c_reactive_protein × amd_late | B | medium | **0.75–0.85** |
| serum_uric_acid × cataract_any | C | low | 0.30–0.75 |
| serum_carotenoids × cataract_any | C | medium | 0.20–0.30 |
| alcohol_intake × cataract_any | C | medium | 0.45–0.75 |
| blood_lead × cataract_any | C | medium | 0.35–0.75 |

按声明级别汇总：

```
A: n= 8  median=0.85  range=0.85-0.90
B: n=16  median=0.85  range=0.75-0.85
C: n=32  median=0.40  range=0.20-0.75
```

### 结论一：假设成立，但分辨率是二值的

**C 级（中位 0.40）与 A/B 级（0.85）分离明显。**
**而 A 与 B 并列 0.85——该字段区分"C 与 A/B"，不区分"A 与 B"。**

对一个筛查工具，这个分辨率是有用的：**它标出证据较弱的那些规则。**
但样本只有 7 个探针，**因此这足以说明"不是无用"，不足以说明可以上界面。**

### 结论二（更关键）：单次取值不可用，中位数才可用

看探针内的范围：`serum_uric_acid` 在 8 次里给出 **0.30 到 0.75**，
`alcohol_intake` 0.45 到 0.75。**分布宽度接近甚至超过组间差异。**

**所以它有意义的形态是"重复若干次取中位数"，而单次查询拿到的是那个宽分布里的一次抽样。**
**作为每次查询都展示的分数，它是不可靠的。**

### 处置

**仍然只进 `report.metadata`，不进入面向用户的展示。**理由现在是实测的：

1. **分辨率是二值的**（C vs A/B），不是连续的
2. **单次抽样不可用**——同一输入 8 次里跨 0.45 宽
3. **样本仅 7 探针**，不足以支撑一个展示决策

**若要让它可用**，形态应是"对该配对重复 N 次取中位数"，代价是 N 倍调用。
**那是一个成本决定，须你定。**

### 顺带：这次我又犯了同一类错误，但当场抓住了

该脚本的第一版用了**我凭空写的实体名**（`crp_elevated`、`uric_acid_high`、
`low_antioxidant_intake`），它们**不匹配任何规则**，于是三个探针返回 `unknown`
且不调仲裁——**C 级一个数据点都没有**。

**而脚本仍打印了 "ORDERED A >= B >= C -> the field tracks declared grade"**，
依据是两个恰好有数据的级别。

**已修**：实体名改用 `data/seed/entities_a.csv` 里的真名；
结论守卫改为**三个级别都须有观测**，否则打印 CANNOT CONCLUDE。

**这与 §八、§十九 是同一类**：**从一个不完整的观测集里读出一个完整结论。**
本轮是唯一一次当场发现并修正的。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "`arbiter_confidence` 的有用性" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
