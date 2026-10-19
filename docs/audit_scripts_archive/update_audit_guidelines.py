"""Record the guideline search and correct this round's over-strong conclusion."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 九、A 级引文的检索结果：不能证实，也不能证伪

### 做了什么

§八 的修复方案要"为 r10/r13 补真指南引文"。为此检索了 PubMed，
按 `guideline[Publication Type]` 与标题关键词（guideline/consensus/
recommendation）找指南级证据。

### 结果

| 规则 | 指南类型命中 | 实际内容 |
|---|---|---|
| **r10** smoking×cataract | 8 条 | **但全部是白内障手术管理指南**：ESCRS 2024 手术指南、术前麻醉评估、中国成人白内障手术指南、干眼共识等 |
| **r13** BMI×cataract | **0 条** | — |

**8 条命中里只有一条可能相关**：`Cataract in the Adult Eye Preferred Practice
Pattern`（AAO，PMID 34780842）——真正的临床指南。

**但它的 PubMed 摘要长度为 0**（PPP 在 PubMed 不带摘要），
**因此无法确认它是否将吸烟列为白内障危险因素。**

另找到 PMID 41180462，摘要明确写：
> "Smoking is a major modifiable risk factor for cataract, with strong
> biological and epidemiological evidence supporting this association."

**但这是全球负担的描述性研究，不是指南**，不能支撑 A 级。

### 更正本轮的过强结论

`find_guideline_citations.py` 在检索后打印
"grade A CAN be substantiated for these rules"——
**该结论不成立，属脚本自行拔高**：它只数了 `guideline` 类型的条数，
没有核对指南的内容是否涉及该暴露。8 条里 7 条讲的是手术管理，与吸烟无关。

### 因此得到的确定结论

| 规则 | 判定 |
|---|---|
| **r13** BMI×cataract | **A 无支撑，应为 B**（0 条指南命中） |
| **r10** smoking×cataract | **悬而未决**：需读 AAO PPP 原文确认其危险因素章节是否含吸烟。**该文档作者可直接获取**，我从 PubMed 元数据无法确认 |

**若作者确认 AAO PPP 列了吸烟**：r10 保持 A，A 级层有实，§4 机制可用。
**若未列或无法确认**：r10 降 B，则**本项目没有任何 A 级规则**，
应在分级方案中明确写"A 级为保留层级、当前未被占用"，
并相应修改 `evaluate.py` 的 §4 触发判据（否则该预注册机制空转）。

### 仍未动手的原因

无论走哪条路，都会改 `evaluate.py` 的 A 级判据与稿件 Table 2，
属会向下游扩散的改动。**本项等作者对 AAO PPP 的确认或对方案的选择。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "A 级引文的检索结果" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
