"""Record the output-provenance audit, including that its own number overstates."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十八、产物溯源审计：方法太粗，而我给的数字夸大了问题

### 动机

§二十七 结尾我写下一条可执行建议：**对 `outputs/` 下每件产物注明生成脚本；
凡注不出来的，就是下一次会陈旧的那一件。** 本节把它做了。

### 结果

```
outputs/ 产物            358 件
  被某个脚本命名           159
  ★ 无脚本命名             199
```

**按扩展名**：`.json 129 · .md 24 · .csv 22 · .py 9 · .yaml 5 · .jsonl 3 · 其它 7`

### 但这个数字夸大了问题，原因是两条

**① 我的审计只扫项目内的 `scripts/`、`app/`、`src/`，看不见 skill 自带的脚本。**

例如 `outputs/paper/figure_table_qc_report.md` 被判为无生成器，
而它由 skill 的 `medical-agent-writer/scripts/verify_figures_tables.py` 产生——
**在 `C:\\Users\\Administrator\\.dsh\\skills\\` 下，不在工作区内。**

**② 大量"无生成器"其实是循环里动态拼名的。**

`outputs/confirmatory/cohort_{COHORT}_prevalence.json` 这类（34 件）
由循环写出，文件名不在任何脚本里以字符串形式出现。

### 真正会漂的那一类，以及它们的现状

**风险不在数据文件，在"陈述了项目事实的散文"。** 24 个 `.md` 中：

| 类别 | 件数 | 处置 |
|---|---|---|
| `outputs/expert_review/*`（R5–R9 报告，带日期） | 12 | **本就不该重新生成**——它们是历史记录 |
| QC 报告（由 skill 脚本产生） | 3 | 非孤儿，见上① |
| `outputs/paper/sections/declarations.md` | 1 | 流水线产物 |
| **陈述项目事实的手写文档** | 2 | **逐个查了** |

**逐个查的两个：**

| 文档 | 是否被我改的分级波及 |
|---|---|
| `outputs/README_baseline_predictions.md`（47 个数字） | **否**——讲基线预测文件（F1/seeds），**提及规则 ID 0 次、提及分级 0 次** |
| `outputs/cohorts/RESULTS_COHORT.md`（95 个数字） | **否**——讲队列层可迁移性与 OR，**提及分级 0 次**；而 `direction` 从未改动 |

**所以这两件在我这轮改动下仍然正确。**

### 结论：本节的方法不足以支撑它想支撑的结论

**它想回答"哪些产物会陈旧"，实际只回答了"哪些文件名没出现在脚本里"。**
后者既漏（看不见 skill 脚本）又误（动态拼名、历史记录），
**与 §八 的 `linked_rules`、§十九 的正则、§二十五 的词表是同一类**：
**用一个粗代理去回答一个它测不准的问题。**

**已被其它手段抓到的、真正的陈旧实例仍是那三件**：
投稿包图件（§投稿包）、Table 2（§二十七）、README（§README）——
**三件都不是靠本节这种全局扫描发现的，而是靠"改了一处、去查下游"。**

### 留下的方法（比本节工具更有用）

**"改一处、查下游"比"全局扫描找孤儿"更有效**，本会话三次都验证了：
改了分级 → 查到 Table 2 陈旧；改了规则 → 查到 README 陈旧；
重建包 → 查到图件从不刷新。

**反之，全局扫描一次也没找到过一件真问题。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "产物溯源审计" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
