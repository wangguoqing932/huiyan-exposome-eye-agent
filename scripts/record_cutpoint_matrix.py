"""Record the r13 cut-point matrix defect, the convention drift, and my own error."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 三十二、切点约定散落在八个脚本里，而矩阵报错了列——包括骗过我自己

### 事实链（逐条查证）

**① coverage matrix 报错了 r13 的暴露列。**

```
matrix:      CRELES → bmi_high_25     SHARE → bmi_high_25
项目约定:     CRELES = 30              SHARE = 30        （25 只给亚洲队列）
```

**② 但已发表的数字是对的**——`cohort_confirmatory.py` 自带
`BMI_PRIMARY` 字典（L55-58），正确指定 SHARE/CRELES → `bmi_high_30`，
并在读到 `bmi_high` 标志时**覆盖矩阵的列**。重跑队列层前后 OR 逐值一致：
SHARE 1.2439、CRELES 0.9911。

**③ 然而矩阵是公开产物，而我是它的消费者。**

**上一轮（§二十九/§三十）我的 `ipd_interaction.py` 直接读矩阵的
`exposure_col`，因此用错了切点。**更正后 r13 的交互 p 从 **0.572 变为 0.1496**。

**结论方向不变**（两阶段 p=1.69e-32 仍是加权伪影，0.149 仍不显著），
**但数值必须改**——已同步正文与 Table 5b。

**④ 约定散落在八个以上脚本里，没有任何一处校验它。**

```
提及 bmi_high_25 / 切点约定的脚本:
  build_cohort_frames.py(5) · cohort_confirmatory.py(3) · evaluate.py(7)
  cohort_power.py(2) · cohort_rule_coverage.py(2) · build_descriptive_table.py(2)
  evidence_base_audit.py(1) · append_ledger_round34.py(1)
```

**没有单一来源，也没有检查** —— 这就是矩阵报错列的成因。

### 已修

1. **`cohort_rule_coverage.py` 新增 `BMI_CUT` 表与 `resolve_bmi_col()`**，
   并把 `EXPOSURE_MAP["bmi_high"]` 的候选列表改为 `["__cohort_bmi_cut__"]`——
   **切点由队列决定，不再由列表顺序决定**（原注释写"in preference order"，
   而两个帧都含两列，于是永远取到 25）。

2. **重新生成矩阵**：CRELES 与 SHARE 现在都是 `bmi_high_30` ✓，
   KLoSA 正确为 25（不可检验），可检验规则数不变（6/21）。

3. **正文与 Table 5b 的 r13 数值已更正**（0.57 → 0.15）。

### 这一节值得单列的原因

**矩阵报错列、而被发表的数字是对的——因为下游脚本自己修了它。**
**这种"上游错、下游补"的结构比单纯的上游错更危险**：
它让错误长期不可见，**直到出现一个新的、信任上游的消费者**。

**那个消费者就是我上一轮的分析。** 我用矩阵的列、算出 0.572、写进正文、
并宣称"两队列异质是加权伪影"——**结论碰巧对，而数值是错的。**

**这与本项目反复出现的那类问题不同**：前面几次是"没人同步"，
**这次是"两处各有各的对，而它们不一致"。**

### 留给下次的做法

**当一个约定在多处重复时，正确的动作不只是"改对那处"，
而是把约定收敛到单一来源，并让偏离它的地方失败。**

本轮做了前半（单一来源在 coverage 脚本里），**后半没做**——
`cohort_confirmatory.py` 的 `BMI_PRIMARY` 仍在，与新的 `BMI_CUT` 并存。
**两处仍可能再次分歧。** 应收敛为一处，或让其中一处导入另一处。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "切点约定散落在八个脚本里" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
