"""Record the A-level ambiguity fix and its enforcement."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十二、修掉那场混乱的根因：字母 `A` 的歧义，并加校验钉死

### 根因

`evidence_level: A` 在两处含义不同：

| 出处 | A 的含义 | 后果 |
|---|---|---|
| `rules.yaml` 纪律（`risk_rules._EVIDENCE_TO_SEVERITY`） | 监管标签 / 临床指南 | **severity 由它强制派生为 high** |
| `evidence_chunks.jsonl` | "高质量证据"，**含 meta 分析** | 一篇 meta 分析能把规则推到最高严重度 |

§八 的审计正是踩在这条缝上：它据语料的 A 判 11 条规则"高评"，
改动全部生效，而后全部回退（§8–§21）。

### 语料其实已带可区分两者的字段

```
source_type:  guideline 159  ·  literature 901

evidence_level × source_type:
    A × guideline      34    ← 正确
    A × literature     13    ← 错：文献被标成 A
    D × guideline     125    ← 指南的背景章节标成 D（本次未动）
```

**那 13 条全是期刊文章**——综述、系统综述、meta 分析或原创研究，**没有一条是
指南或监管文件**。按纪律逐条重判：

| 新级别 | 条数 | 例 |
|---|---|---|
| **B**（综述/meta 分析） | 11 | `BMI and cataract: a meta-analysis`、`Appraising the causal role of smoking…: A systematic review`、`Mediterranean Diet…: Systematic Review and Meta-Analysis` |
| **C**（原创研究） | 2 | `Association of long-term ozone air pollution and AMD in older Chinese`、`Current status of diabetes mellitus care… in the Philippines` |

分级分布：`{A:47, B:125, C:129, D:125, E:634}` → **`{A:34, B:136, C:131, D:125, E:634}`**

### 校验（E5b）——钉死歧义

`scripts/build_evidence_base.py` 新增 E5b：**`A` 只允许给
`source_type == guideline` 的块。**

双向实测：

```
正常      → [evidence] E1-E7 校验通过
篡改一块  → [evidence] FAIL E5b A 级但 source_type≠guideline 的块 1 个
             : ['ev_ppp_AMD_008']
还原      → 通过
```

**被篡改的那块正是 `AAO PPP AMD - Section 9`**——即我读原文据以恢复 r11 的那一块。

### 检索层复验

```
smoking × amd_late → high, 5 条证据
  EV1 [A] AAO PPP AMD - Section 12        ← 浮上来的是真指南
  EV2 [B] Global Incidence, Progression, and Risk Factors of AMD
  EV3 [B] Smoking and the risk of AMD: a meta-analysis
  EV4 [B] Association of combined cigarette smoking and ARMS2…
  EV5 [B] Smoking and risk of age-related cataract: a meta-analysis
```

**修前 A 级里混着 meta 分析，现在 A 级只剩指南。**

### 这条修复与前二十一节的关系

§一–§二十一 记录了一次由"字段含义不一致"引发的连锁错误；
**§二十二 修的是那个不一致本身**，并加了校验使它无法静默复发。

**留一句给下次**：本审计仍未核验任何一条规则的级别是否正确——
它只**未能**证伪它们（§二十一）。r11 = A 是唯一经读原文确认的一条。
**核验分级只能读原文；任何字符串匹配都会制造假支持**（§二十 的三类假匹配）。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "字母 `A` 的歧义，并加校验钉死" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
