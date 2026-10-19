"""Record the empty-A-tier guard and the precise cost of the regrade."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十一、补上我自己制造的空转：A 级为空的显式告警

### 问题

§十 的降级使 A 级层为空。而 `evaluate.py` 的 §4 预注册第四态按 A 级筛配对：

```python
a_tier = sorted(rid for rid, lv in lvl.items() if lv == "A")   # 现在为空
a_pairs = res[res["predicted"] & (res["status"] == "tested")]
... mask = a_pairs["rule_ids"].map(_is_a) ...
```

A 级为空 → 筛出空集 → **不打印任何信息** → 运行看起来"通过"了。

**这与本审计第一节的白图问题同类：检查因为作用对象为空而通过。**
"没找到反转的 A 级配对"与"该审计无法运行"是两句不同的话，
而代码只说得出前一句。

### 修法（已实现，不改科学）

在筛选前加显式告警：

```
[audit] ========================================================
[audit] WARNING: no rule is graded A, so the pre-registered
[audit] section 4 direction audit has NO SUBJECT for NHANES.
[audit] An empty result below means 'the audit could not run',
[audit] NOT 'no reversed A-level pair was found'.
[audit] See docs/AGENT_AUDIT.md section 10.
[audit] ========================================================
```

实测触发 ✓，`evaluate.py` exit=0 不崩 ✓。
**未改 §4 的判据本身**——那是预注册的协议要素，改动属科学决定，须由作者做。

### ★ 降级的精确代价（已量化）

降级前被 §4 标记 `direction_review` 的配对（现存文件为降级前产物）：

| 数据集 | 配对 | 规则 | OR | q |
|---|---|---|---|---|
| NHANES | current_smoking × cataract_any | r10 | 0.756 | 1.000 |
| NHANES | bmi_high × cataract_any | r13 | 0.986 | 1.000 |
| KNHANES | current_smoking × cataract_any | r10 | 0.971 | 1.000 |
| CHARLS | current_smoking × cataract_any | r10 | 0.657 | 0.817 |

**共 4 个配对，全部 q ≥ 0.817，无一显著。**quarantine 要求
"≥2 个**显著**反转"，因此**从未触发过**。

**所以代价是**：4 个"方向与规则声明相反、值得人工查看"的配对
不再被系统surface出来。**没有导致任何结论改变**（无显著反转、无 quarantine），
但**一个为"surface 反转供调查"而设的机制，现在对这 4 个配对不再起作用。**

### 一个值得注意的交叉印证

`current_smoking × cataract_any`（r10）在**内部层的三个数据集里全部反转**
（OR 0.756 / 0.971 / 0.657，均 <1，与规则声明的 risk_up 相反），
而在**队列层**该规则也正是唯一出现方向分歧的那一条
（SHARE 1.109 vs CLHLS 0.748 / ELSA 0.767 / CRELES 0.702）。

**两层独立地指向同一件事：吸烟与白内障的关联方向在这批数据里不稳定。**
这不是新结论，但它说明 §4 机制即使只为 A 级配对服务，
其**选取范围过窄**——r10 的这次反转正落在它该管的地方，
却因为它降级而不再被它看见。

### 建议（需作者定，因为改的是预注册判据）

把 §4 的触发判据从"A 级配对"改为**与证据级别解耦的判据**，例如：

- 所有 `predicted & tested` 的规则相关配对中，方向与规则声明相反者**一律 surface**
  （不自动 quarantine，只标记）；或
- 按其引文证据级别加权 surface（B 级也可触发标记，quarantine 仍限高证据级别）

**两者都改 analysis_plan §4 的预注册文本，属科学决定，我不擅自改。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "补上我自己制造的空转" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
