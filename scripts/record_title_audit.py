"""Record the title-only grade audit and its one blind spot."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十五、标题级评级审计：20/21 完成，并暴露一个结构性盲区

### 方法（第四次尝试，前三次的失败方式见 §八/§十九/§二十）

**只匹配 `title` 字段**，不匹配正文。依据是标题命名主题，而正文会顺带提到词——
前三次失败全部来自匹配任意文本：`linked_rules` 为空、`lead` 撞 `leading`、
参考文献条目、文档页眉。

**它仍是启发式**：标题命中说明语料里有研究该配对的论文，
**不说明该论文支持规则的方向或量级**。因此本脚本**只报告、不改动**。

### 结果（20/21 条评估完成）

**14 条有 ≥ 声明级别的标题级证据：**

| 规则 | 声明 | 最佳标题命中 | 标题 |
|---|---|---|---|
| r01 | C | C | Uric acid–driven NLRP3 inflammasome activation… |
| r03 | B | B | The Role of Glycemic Control and Variability in DR |
| r05 | C | C | Relationships between Lipid-Related Metabolites and… |
| r06 | B | B | A review and meta-analysis of the association between CRP… |
| r07 | B | B | **Vitamin D and Diabetic Retinopathy** |
| r08 | B | B | **Antioxidants and cataract** |
| r09 | B | B | Mediterranean Diet on Development and Progression of AMD |
| r12 | B | B | **Alcohol intake and the risk of age-related cataracts** |
| r14 | B | B | **Cadmium and lead exposure and risk of cataract surgery** |
| r16 | B | B | Airborne particulate matter (PM2.5) triggers ocular… |
| r17 | B | B | Association between ambient air pollution and AMD |
| r18 | B | B | Correlation of Sunlight Exposure and Different Morph… |
| r19 | C | C | Association of standard dietary inflammatory index with… |
| r20 | B | B | **Smoking, urinary cotinine levels and incidence of VI** |
| r21 | B | B | **Residential greenness, air pollution and visual impairment** |

（十五条，其中 r05/r01/r19 为 C 级规则、命中亦为 C 级。）

### ★ 结构性盲区：本审计看不到指南

**AAO PPP 块的标题是 `AAO PPP AMD - Section 9` 这样的章节标签，不含暴露或结局词。**
因此**任何声明 A 级的规则都会被本审计标记为"声明高于最佳标题命中"**——
不是因为它的 A 无据，而是因为**测它的那个工具看不见指南**。

**本轮 4 个标记里 3 个正是这个产物：**

| 规则 | 标记 | 实际 |
|---|---|---|
| **r11** | A > B | **假阳性**——§二十 已读 PPP Section 9 原文确认 A 成立（"primary modifiable risk factor"） |
| **r10** | A > B | **待核**——语料内**不存在白内障指南**（cataract PPP 是会员墙），故其 A 在本语料中无法确证 |
| **r13** | A > B | 同上 |
| **r02** | B > C | **待核**——最佳命中是 `Hyperglycemia and Hypo-HDL-cholesterolemia Are Primary Risk Factors for ARC`，是原创研究（C）；其 B 需一篇本语料没有的 meta 分析支撑 |

### 另发现一条可能被**低**评

**r04（HbA1c → PDR）声明 C，而标题级证据有 B**（`The Role of Glycemic Control and
Variability in Diabetic Retinopathy`）。**本审计只查"声明高于证据"，这一条是反向的。**
（r04 目前 C/low，若应升 B 则 severity 由 low 变 medium——**但那要读原文定，不是标题能定的。**）

### 未评估与不足

- **r22（BMI → 视网膜病变）无标题命中**。其引文
  `Association of obesity and risk of diabetic retinopathy` 应能命中——
  **说明词表或 `bmi_high`/`retinopathy_any` 的映射仍有缺口**，未查明。
- **本审计未改动任何分级。**上一次自动改分级的结果是 11 条全部回退（§二十一）。

### 结论

**21 条中 14–15 条的声明级别有同级的标题证据支持；3 条 A 级的可见性受盲区限制；
1 条（r02）待核；1 条（r04）可能被低评；1 条（r22）未评估。**

**要收敛剩下的，只有读原文**——对 r10/r13 是读那两份白内障 meta 分析的摘要，
对 r02 是确认其 B 的依据，对 r04 是确认是否该升 B。
**四项，每项读一两段即可。仍不是脚本任务。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "标题级评级审计" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
