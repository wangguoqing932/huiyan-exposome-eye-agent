"""Record the close-reading pass and the three false-match classes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十、逐条精读：语料里的"A"与规则纪律里的"A"不是同一个 A

### 方法

§十九 证明关键词扫描不可用，于是改用**读原文**：把语料里全部 A 级块读一遍，
看每块真正支持哪条规则。这比按规则各搜一轮更彻底——**先看证据有什么，再看规则要什么。**

### 发现一：47 个"A 级"块里只有 34 个是指南

| tags | 数量 | 实际是什么 |
|---|---|---|
| `guideline_AMD_riskfactor` | 10 | **真指南**（AAO PPP AMD） |
| `guideline_DR_riskfactor` | 14+ | **真指南**（AAO PPP DR，共 52 块，其中风险因素章节 14） |
| `guideline_POAG_riskfactor` | 10 | **真指南**（AAO PPP 青光眼） |
| `rule_citation` | 3 | **meta 分析／综述**：`BMI and risk of age-related cataract: a meta-analysis`、`Appraising the causal role of smoking…: A systematic review and meta-analysis`、`Cataracts: A Review` |
| `max_*` | 10 | **meta 分析**：`Impact of Environmental Factors on Glaucoma Progression: A Systematic Review` 等 |

**即：语料的 `evidence_level: A` 表示"高质量证据"，而 `rules.yaml` 的纪律写的是
"A = 监管标签 / 指南"。** 同一个字母，两套含义。§八 的审计同时踩了两边。

### 发现二：真指南只覆盖三个疾病，没有白内障

```
AMD 10 块 · DR 14 块 · POAG 10 块      ← 全部指南级证据的覆盖范围
白内障：0 块   视力损害：0 块
```

与网络文档一致：`cataract-in-adult-eye-ppp` 是会员墙（HTML 500），
免费集只有青光眼／AMD／DR 三份。

**这条直接判定了一件事**：**r10（吸烟→白内障）与 r13（BMI→白内障）声明的 A 级
在本语料中无法支撑——不存在白内障指南。§八 把它们降为 B 是错的理由、对的结果。**

### 发现三：逐条精读的结果

| 规则 | 指南原文 | 判定 |
|---|---|---|
| **r11** 吸烟→AMD | "Cigarette smoking has been identified as the **primary modifiable risk factor**" | **A 成立** → 已回退 |
| **r09** 地中海饮食→AMD | "**A Mediterranean diet is associated with a reduced risk of developing AMD** and of existing AMD becoming worse" | **指南支持** → 已回退为 B |
| r10/r13 →白内障 | 无白内障指南 | **B 正确** |
| r06 CRP→AMD | 只提到 "fatty acids … decrease inflammatory mediators" | 无 CRP 陈述 → B 站得住 |
| r05 血脂→AMD | 原文是 "higher intake of **saturated fats and cholesterol**" | 是**膳食脂肪**，非血清血脂，构念不同 → C 站得住 |
| r08 抗氧化→白内障 | 抗氧化原文在讲 **AMD（AREDS2）** | 与白内障无关 → C 站得住 |
| r16 PM2.5→青光眼 | 命中 "may **lead to** alterations" | 假匹配 → C 站得住 |
| r03/r04 HbA1c→DR | 命中 DR 文档**页眉标题** "Diabetic Retinopathy PPP" | 假匹配 → 未获支持 |
| r22 肥胖→DR | 原文讲 "obesity … causes relative insulin resistance"（肥胖致糖尿病） | 不是肥胖致 DR → 未获支持 |
| r19 促炎饮食→DR | 原文 "Management of DR includes following a **healthy diet**" | **治疗建议**，非危险因素 → 未获支持 |

### 发现四：正则在这里根本不可用——共三类假匹配

本轮亲历的三类，每一类都会凭空制造支持：

1. **子串**：`lead` 命中 `leading cause`（182 块 vs 词边界 56 块）
2. **参考文献条目**：`AAO PPP AMD - Section 58` 的正文是 `…PPP P60 49. Hyman L, Schachat AP, …`——**第 49 号文献**
3. **文档页眉**：`diabet` 命中每页都印的 `Diabetic Retinopathy PPP`，
   于是"9 块 DR 血糖证据"实为 9 次页眉命中

**第 3 类尤其阴险**：§十九 的第二次尝试已用词边界，仍会在这一关上失败——
**因为页眉里的 `Diabetic` 是一个完整的词。词边界挡不住它。**

### 现状与结论

**已定案**：r11=A（回退）· r09=B（回退）· r10/r13=B（原降级正确）。
现分布 **A=1, B=7, C=13**。

**未定案**：r03, r08, r12, r14, r16, r18, r20, r21 的 B→C 降级——
本轮逐条看过 r03/r08/r16，**三条都站得住**，但没有一条是"经指南确认"，
而是"未找到支持"。**这两者不同，本审计不把它们混为一谈。**

**方法上的结论**：**规则分级不能由脚本核验。** 三类假匹配全部来自"用字符串找证据"，
而唯一的替代是读原文。**建议把剩余 8 条按本轮 r11/r09 的方式逐条读原文定案**
（读语料原文 + 读引文摘要），每条约需读 2–4 段。**这是人工精读任务。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "语料里的" in t and "不是同一个 A" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
