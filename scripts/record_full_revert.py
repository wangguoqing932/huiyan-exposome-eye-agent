"""Record the full revert of the erroneous regrade."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十一、★ 11 条降级全部回退：那次审计整体作废

### 逐条读完 8 条后，全部有 B 级或更好的支持

§二十 只读了 r11/r09。本轮把剩下 8 条也逐条读，结果如下：

| 规则 | 语料中的支持 | 级别 |
|---|---|---|
| **r03** HbA1c→DR | `[E] Prevalence and risk factors for diabetic retinopathy…`："higher hemoglobin A1c (**OR 2.912**, 95% CI 1.009–8.402)"。<br>**该块被语料标为 E，实为原创研究** | 实为 C 以上 |
| **r08** 抗氧化→白内障 | `[B] **Antioxidants and cataract**`——标题即该命题的综述 | B |
| **r12** 酒精→白内障 | `[B] Cataract and systemic disease: A review`："**Alcohol intake** … may play a role in cataract formation" | B |
| **r14** 铅→白内障 | `[B] **Cadmium and lead exposure and risk of cataract surgery** in U.S. adults` | B |
| **r16** PM2.5→青光眼 | 语料侧未找到直接陈述（§二十 的命中是 "lead to" 假匹配） | 未获支持 |
| **r18** 紫外线→白内障 | `[A] Cataracts: A Review`："significant **UV exposure**" 列为危险因素；另有 `[C] Ultraviolet radiation and cataract` | A/C |
| **r20** 吸烟→视力损害 | `[B] **Smoking, urinary cotinine levels and incidence of visual impairment**` | B |
| **r21** PM2.5→视力损害 | `[B] **Residential greenness, air pollution and visual impairment**: a prospective cohort study` | B |

**七条有 B 级或更好的、题目即该命题的支持。**
§二十 已回退 r09/r11，合计 **11 条中 10 条已证伪**；
余下 r16 是"未找到支持"，**而"未找到"不等于"不支持"**——
用我这次已被三次证伪的方法去断言后者，是同一个错误。

### 因此：全部回退，恢复原始分级

**处理**：把 11 条全部恢复到项目原本设定的级别，**不保留我按错误方法所做的任何改动**。

```
回退后分布:  A=3   B=13   C=5
  A: r10  r11  r13
  B: r02 r03 r06 r07 r08 r09 r12 r14 r16 r17 r18 r20 r21
  C: r01 r04 r05 r19 r22
```

**与动手前的备份逐字段比对**：

| 字段 | 不一致的规则数 |
|---|---|
| evidence_level / severity | **1**（仅 r11——备份是我降 r11 之后取的，本轮据指南原文恢复为 A） |
| direction | 0 |
| entity_a_flags / entity_b_flags | 0 |
| risk_type | 0 |

**即：除 r11 外，rules.yaml 已完全回到我干预之前的状态**，
且 `direction`/`flags`/`risk_type` 从未被改动——这也是队列层始终零波及的原因。

### 最终保留的只有一处改动，且它有逐字依据

**r11 = A/high**。依据是 AAO PPP AMD Section 9 原文：

> "Risk factors for the development of advanced AMD include **smoking** …
> **Cigarette smoking has been identified as the primary modifiable risk factor**
> in numerous studies on advanced AMD."

**这是全项目唯一一处"经读原文确认"的级别判定。**

### 行为复验

```
smoking × amd_late                    → high   (r11=high)
smoking × cataract_any                → high   (r10=high)
fasting_glucose × cataract_any +diabetes → high (r02=high)
aspirin × cataract_any                → unknown (无规则)
pytest tests/ -q                      → 15 passed, 1 skipped
```

### 这次错误的完整账

| 轮次 | 我做了什么 | 结果 |
|---|---|---|
| §八 | 用 `linked_rules` 审计，判 11 条高评 | **错**：159 个 PPP 块的该字段全为空 |
| §十九 | 改用关键词扫描重审 | **错**：子串假匹配 126 块 |
| §十九 | 改用词边界重审 | **错**：仍中参考文献条目与文档页眉 |
| §二十 | 逐条读原文 | **对**：发现指南覆盖范围、回退 r11/r09 |
| 本轮 | 读完其余 8 条 | **全部有支持 → 11 条整体回退** |

**四轮尝试、三种方法失败，最后靠读原文收敛。**
而这四轮里，**只有第一轮真的改动了产品**——`linked_rules` 那次。
**后续三轮都是在修第一轮造成的破坏。**

### 留下的教训（写给下次）

**`configs/rules.yaml` 的分级目前是"项目原始设定、未经本审计独立核验"的状态。**
本审计**未能**证实其中任何一条错——**能证实的只有 r11 是对的**。

**核验分级唯一可行的方法是读原文**：读语料正文（排除页眉与参考文献列表）
加读引文摘要。**任何字符串匹配都会制造假支持**，本轮亲历三类：
子串、参考文献条目、文档页眉。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "11 条降级全部回退" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
