"""Record the Table 2 staleness gap and its closure."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十七、Table 2 没有任何生成器：改了分级，它不会跟着变

### 发现

分级改动（§二十六：r10/r13 A→B）之后，检查下游产物时发现：

```
outputs/tables/table2_rules.md   →   | r10_smoking_x_cataract | high | ... | A |
outputs/submission/tables/table2_rules.md → 同上
outputs/paper/manuscript.md (内联)        → 同上
```

**而 `configs/rules.yaml` 里 r10 已经是 `medium / B`。**

### 根因：该表是手工产物，全仓库只有一处引用它

搜遍所有脚本，`table2_rules.md` **只被 `assemble_manuscript.py` 引用一次**
（用于把它内联进稿件），**没有任何脚本生成它**。

所以它自建立之日起就与 `configs/rules.yaml` 脱钩——
**规则一分级、表就陈旧，而没有任何机制会发现。**

### 为什么现有的门禁抓不到

| 门禁 | 为什么不报 |
|---|---|
| `qc_english_manuscript.py` | 数的是表格**引用**（"Table 2"），不读表内单元格 |
| `verify_results_numbers.py` | 校验的是队列层数字（OR/CI/q），不读 severity 列 |

**两个门禁都通过，而 Table 2 里两条规则的严重度是错的**——包括投稿包里的那一份，
**那正是审稿人会读到的那份。**

### 这与本项目其它陈旧问题同类

- 投稿包的图件因 `if not d.exists()` 永不刷新（已修）
- README 声称 `outputs/` 为空、仲裁确定（已修）
- **Table 2 无生成器**（本节）

**共同点：产物与来源之间没有可执行的链接，只能靠人记得同步。**

### 已修：加生成器

新增 `scripts/build_table2.py`——**从 `configs/rules.yaml` 派生 Table 2**，
同时输出 `rule_list.csv`（同内容的机读形式，两者一起写，免得它们之间再出现分歧）。

### 传递验证

```
Table 2            21 条规则 · 分布 {A:1, B:15, C:5}
  r10_smoking_x_cataract : medium / B
  r11_smoking_x_amd_late : high   / A
  r13_bmi_x_cataract     : medium / B

稿件重新组装   118,498 B -> 118,470 B（Table 2 内的空行一并清理）
QC            20/20 PASS
数字校验       70/70 PASS
投稿包         figures 24 · tables 8 · 全部必需文件在包内
包内 Table 2   outputs/tables 与 outputs/submission/tables 均为新版
```

**稿件内联的那份（L1505 所在表）也已同步**——重跑 `assemble_manuscript.py` 后
三行分别为 `medium | B`、`high | A`、`medium | B`。

### 留下的一句

**这个项目里凡是"手工建立、无脚本生成"的产物，都已经陈旧过一次。**
本节新增的生成器是第三次这类修复（前两次：投稿包图件、Table 1b 描述表）。
**建议对 `outputs/` 下的每一件产物注明其生成脚本**，
凡是注不出来的，就是下一次会陈旧的那一件。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "Table 2 没有任何生成器" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
