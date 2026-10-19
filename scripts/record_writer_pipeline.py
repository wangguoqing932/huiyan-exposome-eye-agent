"""Record the move from ad-hoc scripts to the medical-agent-writer pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 三十四、把产出交回 medical-agent-writer 流水线（作者纠正后的返工）

### 纠正

作者指出：**文章必须是 `medical-agent` 技能流水线的产物，而不是我临时脚本的堆叠。**
本条纠正落在实处——本会话我写了 `assemble_manuscript.py`、`assemble_submission_zip.py`、
`build_cover_letter.py` 等脚本，**全部绕过了技能自己的 7_8 / 7_9**。

### 查明：技能这两个阶段本来就是脚手架

| 阶段 | 技能脚本 | 实际状态 |
|---|---|---|
| 7_8 | `scripts/polish_bilingual.py` | **L111-112 两个 TODO**；L115 写的是 `_Scaffold stub — fill in during writer.phase7_5_` |
| 7_9 | `scripts/build_submission_pkg.py` | **L103-107 四个 TODO**；且自带一个 `assemble_manuscript()` |

**所以技能自身的 7_8/7_9 从未实现** —— 这正是我先前绕道的原因，
**但绕道是错的解法**：技能为此提供了 `user_overrides/` 通道
（README：「Customize per-project without modifying the skill source. Updates
preserve your overrides.」），**正确做法是把它们实现进去。**

### 7_9 技能脚本里我先前查到的两个不安全行为（本节复述，因它们正是覆盖的理由）

1. **它自己 `assemble_manuscript()` 只拼接四个 IMRaD 章节 + 图例。**
   跑在 7_8 之后会**丢掉标题、摘要、全部表格与 Declarations 块**——
   **没有 Declarations 的稿件在 ICMJE 期刊是直接退稿项。**
2. **它只从 `outputs/paper/` 读顶层文件**，而 `cover_letter.md`/`highlights.md`/
   `data_availability.md` 在 `outputs/submission/` —— **静默遗漏。**

### 已交付：两个覆盖脚本

**`user_overrides/polish_bilingual.py`（7_8）**
- **保留技能原 `check_consistency()` 逐字不动**（那是可用代码，5 项检查齐全）
- 替换的只有写 stub 的分支：改为**真正组装**（标题 + 摘要 + IMRaD + Declarations
  + 图例 + 8 张表），并写 `manuscript_assembly_manifest.json` 记录每个源的 SHA-256
- **英文母语项目**：`.en.md` 写成精确副本使技能的双语契约成立，
  **并明说这是副本而非独立译文**，不把一致性检查冒充为独立证据
- 追加**源 SHA 复核**：确认后某个章节被改动则报 FAIL，使"事后漂移"可见

**`user_overrides/build_submission_pkg.py`（7_9）**
- **不重复组装**（7_8 负责），改为**校验** 7_8 的产物
- 实现四个 TODO：
  1. **按快照限额校验**——且**快照若声明限额无法确立，就不假装满足**，
     而是列为未校验项
  2. Data Availability 存在且非占位
  3. Cover letter 无未填字段
  4. Highlights 3–5 条且每条 ≤85 字符
- 从 `paper/` 与 `submission/` **两处**定位文件（技能原脚本只看 `paper/`）

### 流水线跑出的三个结果

**① 7_8 组装出 122,335 B，比我的脚本更完整**——含 **Table 5b**，
而我的 `TABLES` 列表里没有它。

**② 7_9 抓到两个我自写检查漏掉的真缺陷：**

| 缺陷 | 我的检查为何漏掉 |
|---|---|
| `highlights.md` 的第一条是**元注记被写成 bullet** | 我只查 longest ≤ 85，**从未数条数** |
| `cover_letter.md` 5 处未填字段 | 我明知是草稿，但**我的打包脚本不检查就发** |

**元注记那条已修**：它用 `*...*` 斜体，前导 `*` 与 bullet 标记撞了——
改用 `_..._`。**真正的 5 条是 70/85/75/78/77，全部合规。**

**③ 而我自己的解析器也有一个假警报**：报 `figures 24 / 3 OVER`。
快照 L16 明写"**cannot state the target journal's** figure/t[able limit]"，
**它根本没有任何限额**——我的正则匹配到 "figure/t" 又抓了邻近数字，
于是把一个 24 图的真实项目报成"超限 8 倍"。

**已修**：解析器改为两步——**快照若声明限额未确立，则一个数字都不取**；
否则只读显式的限额表格行。**那种形状的假警报比不检查更糟：它训练读者忽略这个检查。**

### 覆盖后的实际行为（技能产出）

```
7_8  组装 manuscript.md  122,335 B
     6 章节 + 图例 + 8 表，逐源记 SHA
     双语一致性 OK
7_9  guideline snapshot: numeric limits found = none
     NOT established: [site unreachable, abstract words, main text words,
                       figures, tables, references]
     highlights: 5 bullets, longest 85 chars        ✓
     data availability present                       ✓
     REFUSING TO PACKAGE — 仅一项:
       cover_letter.md contains 5 unfilled bracketed fields
```

**这才是应有的终态。我的手写脚本会照样打包发出去；技能的流水线拒绝。**

**而它现在只卡在一件只有作者能定的事上**：投稿信的目标期刊与作者信息
（`[Date]`、`[Journal name]`、`[Corresponding author…]`、`[Affiliation…]`）。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "把产出交回 medical-agent-writer 流水线" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
