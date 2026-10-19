#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Append the round-34 corrections to the review findings ledger."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "outputs" / "review" / "REVIEW_FINDINGS_LEDGER.md"

ADD = """

---

## E. 第三轮修复（round 34）

| # | 发现 | 核验 | 状态 |
|---|---|---|---|
| E1 | **构念置换是系统性的：7 条规则**被测试在比其声明更宽的构念上 | 枚举两张多对一映射：`amd_any` ← `amd_late`（r05/r06/r09/r11）+ `amd_early`（r17）；`diabetes` ← `hyperglycemia`（r02）+ `hba1c_elevated`（r03/r04） | **已修**：Methods 新增逐条表 + Discussion 限制段，**按"这组置换就是论文论点本身"框架化**，使其成为支持结论的证据而非附带说明 |
| E2 | **E-value 把 OR 当 RR**（未暴露风险 8.8%–21.1%，罕见结局假设明确被违反） | 按精确公式 `RR = OR/(1-p0+p0·OR)` 重算；我的结果与 R2 完全吻合 | **已修**：r02@CLHLS **6.64→4.51**（高估 47%）、r10@CLHLS 2.01→1.87、r12@CLHLS 1.78→1.66、r10@SHARE 1.46→1.43；**Methods 补 E-value 方法段并写明换算** |
| E3 | **预测区间用 z 而非 t(k−2)** | 改为 t 后：r02 **0.84–4.57 → 0.30–12.63**（R2 的预测值一字不差）、r10 0.53–1.33 → **0.30–2.31**、r20 0.81–1.89 → **0.62–2.46** | **已修**：Table 5 重生成并写明乘数；正文与摘要同步 |

### E3 的后果

论文核心主张"每个预测区间都跨 1"**仍然成立，而且更强**：三个可计算的区间全部跨 1，
现在用的是诚实的宽度。但 **r12 与 r13 不再声称有预测区间**——
原先报出的 0.68–1.17 与 0.80–1.62 是**并不存在的量**（k=2 时 t 的自由度为 0）。

### 尚未修（B4–B6、B10–B18）

HRS r20 实为单波（2016）估计 · 协变量缺失未披露（HRS 51.31%、MHAS 80.7%）·
MHAS 78,537 行中 63,320 行完全重复 · **r13 的 BMI 切点选择翻转显著性与异质性结论** ·
性能数字 SD 与均值取自不同金标准 · Figure 图例计数（"13 条"应为 15）·
Table 2 无来源 · generalizability 与公平性段缺失 · 移出 R11 系统层 · STROBE 缺项
"""


def main() -> int:
    t = LEDGER.read_text(encoding="utf-8")
    if "E. 第三轮修复" in t:
        print("ledger already carries round 34")
        return 0
    LEDGER.write_text(t.rstrip() + ADD, encoding="utf-8")
    print(f"ledger updated: {len(ADD)} chars appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
