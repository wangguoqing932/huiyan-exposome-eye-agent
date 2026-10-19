"""Record the executed regrade and its verified consequences."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十、降级已执行，后果已量化

§八 的建议未停留在纸面。按"声明必须与引文相符"这一**正确性**要求（非判断项）
执行了降级。

### 改了什么

`configs/rules.yaml`：11 条规则的 `evidence_level` 与 `severity` 同步下调
（`_EVIDENCE_TO_SEVERITY` 强制 A→high / B→medium / C→low，二者必须同时动），
每条规则 rationale 内留有带日期的更正说明，文件顶部补记了分级纪律与本次核验。

| | 降级前 | 降级后 |
|---|---|---|
| A | r10, r13 | **（无）** |
| B | 14 条 | **7 条**：r02 r06 r07 r10 r11 r13 r17 |
| C | 5 条 | **14 条**：r01 r03 r04 r05 r08 r09 r12 r14 r16 r18 r19 r20 r21 r22 |

### 验证

| 检查 | 结果 |
|---|---|
| YAML 可解析、21 条规则 | ✓ |
| `patient_factor_rules` 四个因素的 severity **未被误改** | ✓ 仍为 high/medium/medium/low |
| `load_rules()` 通过（含 severity↔level 一致性校验） | ✓ |
| **队列层输出** | **零波及**：68 行 × 20 列逐值一致，数值列 max\\|Δ\\|=0.000e+00 |
| `evaluate.py` 运行 | ✓ exit=0，不崩 |

### 已量化的后果：§4 预注册第四态空转

`evaluate.py` 的 `direction_review` 只作用于 **A 级配对**。降级后：

```
nhanes_confirmatory.csv: direction_review = 全 False（0 / 180）
```

而 `direction_review_nhanes.csv`（2 行）/ `_knhanes.csv`（1 行）/ `_charls.csv`（1 行）
是**降级前的陈旧文件**——说明此前确有配对落入第四态，**现在没有了**。

**这是必须如实声明的后果**：本项目**没有任何规则占用 A 级**
（语料中不存在监管标签或临床指南，任何规则所引最强证据是 meta 分析），
因此 analysis_plan §4 那个预注册的安全机制**失去了作用对象**。

**两条出路（需作者定）**：

- **补指南**：为 r10（吸烟→白内障）等找到真正的指南级引文。
  已检索：8 条 `guideline` 类型命中**全是白内障手术管理指南**，
  唯一可能相关的 AAO *Cataract in the Adult Eye Preferred Practice Pattern*
  （PMID 34780842）**在 PubMed 无摘要，无法从元数据确认其是否列吸烟**。
  **需作者读该 PPP 原文确认**——这是我做不了的一步。
- **改机制**：若确认无指南支撑，则应把 §4 的触发判据从"A 级配对"
  改为其他刻画的"高证据配对"（例如"引文为 meta 分析"即 B 级），
  否则该机制在代码里存在但在运行中永不触发。

### 本轮我自己的两个错误（均已修正）

1. **§八 的降级脚本首版把 `patient_factor_rules` 里四个因素的 `severity` 也改了**：
   规则条目与顶层键都在第 0 列，我的"遇到顶层键就停止"的边界判断因此在每个规则行
   都把自己关掉。dry run 里表现为重复的 "r21 severity" 行。**已改为按顶层键切换段落
   并把 `- ` 开头的行识别为列表项。**
2. **第二版让 `rules.yaml` 无法解析**：追加的更正说明含冒号
   （`... Cataract: A Meta-Analysis ...`）落在未加引号的 YAML 标量里。
   **已给脚本加写盘前自校验**——解析失败或规则数/因素数不对就拒绝写入。
   两次都从备份恢复，`rules.yaml` 未受污染。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "降级已执行，后果已量化" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
