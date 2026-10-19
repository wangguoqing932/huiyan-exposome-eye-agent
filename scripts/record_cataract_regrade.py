"""Record the cataract-rule regrade and why it differs from the first attempt."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十六、r10 与 r13 降为 B：四条独立证据，无一是文本匹配

### 与第一次降级的区别（必须说清）

**第一次**（§八）据 `linked_rules` 降了 11 条——该字段对全部 159 个指南块为空，
所以审计看不见指南支持，**11 条全部回退**（§二十一）。

**本次**只降 2 条，依据是四项检查，**没有一项是文本匹配**：

| # | 检查 | 结果 |
|---|---|---|
| 1 | **两条规则自己的引文**（经 PubMed 出版物类型解析） | r10 引 `10.1016/j.ebiom.2022.104154` → PMID 35816897，类型 **Meta-Analysis, Systematic Review**（B）；r13 引 `10.1371/journal.pone.0089923` → 前瞻队列 meta 分析（B）。**A 级在本项目纪律里保留给监管标签/临床指南。** |
| 2 | **PubMed 检索白内障危险因素指南** | **0 条命中** |
| 3 | **项目自己缓存的指南** | `data/raw/aao_ppp/` 只有 `AMD_PPP.pdf`、`DR_PPP.pdf`、`POAG_PPP.pdf`——**无白内障**；`network_and_proxy.md` 记录白内障 PPP 是会员墙（HTML 500），从未获得 |
| 4 | **语料的指南块** | 159 块，覆盖 `{AMD:49, DR:52, POAG:58}`，**白内障 0** |

**四条独立来源一致：本项目无法获得任何白内障指南级证据，而两条规则各以一篇
meta 分析支撑其 A 级。**

### 同时确认无误的两条（未改动）

| 规则 | 声明 | 依据 |
|---|---|---|
| **r02** | B | 语料有 `[B] A systematic review of risk factors for cataract in type 2 diabetes`——**同级的系统综述**。§二十五 的标题审计漏了它，因为我的暴露词表里没有 "diabetes"（又一个不完整词表造成的假标记） |
| **r04** | C | 其引文 `10.1167/iovs.17-22804` → PMID 29288266，**原创研究**，C 正确 |

### 改动

```
r10_smoking_x_cataract   A/high   -> B/medium
r13_bmi_x_cataract       A/high   -> B/medium
（两条 rationale 内均写入四条依据）

分布  A=3 B=13 C=5   ->   A=1 B=15 C=5
```

**A 级现在恰有一条：r11。**这与证据库的覆盖自洽——
本项目全部指南级证据只覆盖 AMD/DR/POAG，**而这 21 条规则中只有 r11 的结局是 AMD
且其暴露（吸烟）在该指南里被逐字列为危险因素。**

### 验证

```
队列层     max|Δ|=0.000e+00  文本不等=0          （direction 未动，零波及）
pytest     15 passed, 1 skipped
agent 输出 smoking × amd_late   -> high     (r11=A)
           smoking × cataract   -> medium   (r10=B)
           bmi × cataract       -> medium   (r13=B)
```

**输出与证据自洽：只有经指南原文证实的那一条是 high。**

### 为什么这次可以直接改而第一次不行

**第一次的依据本身不可靠**——`linked_rules` 全空，它不产生任何矛盾输出，
所以错误无法在改动前被察觉。

**这次的依据可在改动前逐项复核**：引文的出版物类型是 PubMed 的一等字段、
指南是否存在可检索、项目缓存可直接列目录、语料的 tags 可直接统计。
**四项都能被独立重跑，且四项一致。**

### 未改动

**其余 9 条**（r03, r08, r09, r12, r14, r16, r18, r20, r21）保持原级——
§二十五 的标题审计为它们全部找到了同级的标题级证据，
其中 r08/r12/r14/r20/r21 的命中标题**即为该命题本身**
（`Antioxidants and cataract`、`Alcohol intake and the risk of age-related cataracts`、
`Cadmium and lead exposure and risk of cataract surgery`、
`Smoking, urinary cotinine levels and incidence of visual impairment`、
`Residential greenness, air pollution and visual impairment`）。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "r10 与 r13 降为 B" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
