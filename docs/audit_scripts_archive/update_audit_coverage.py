"""Record the judgeable-vs-ruleable finding in the agent audit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 七、证据分级与"可判定 ≠ 可成规则"

### 7.1 更正上一节的警报：规则引文是干净的

我先前据语料整体分级（A=47, B=125, C=129, D=125, **E=634**，E 占 60%）
提出"规则强度存疑"。**该警报针对了错误的子集。**

语料 1060 块中**只有 101 块带 `linked_rules`**——即规则引文；
其余 959 块是 `probe_landscape`（491）与指南背景材料。

**规则引文的分级：A=8, B=24, C=69 —— 没有 D 或 E。**
**建立在 D/E 证据上的规则：0 条。**

逐规则：19 条的**最佳链接证据 ≥ 声明级别**。例外两条：

| 规则 | 问题 | 处置 |
|---|---|---|
| **r11** | 声明 **A/high**，但引文 Crossref 解析为 *Medicine* 2025 的 **systematic review and meta-analysis**（应属 B），语料链接亦为 1×B + 3×C 无 A | **已降为 B/medium**，rationale 留更正记录 |
| **r22** | **零 `linked_rules`** | **非缺陷**：语料 provenance 为 `2026-10-11 phase2`，而 r22 于 **2026-10-12** 追加，语料早于规则 |

**r11 降级的零波及已验证**：`cohort_confirmatory.py:176` 只读
`rules[rid]["direction"]`（未改动）；`cohort_heterogeneity.py`/`cohort_power.py`
不读 rules.yaml。重跑队列层，**68 行 × 20 列逐值一致**（数值列 max|Δ| = 0.000e+00，
文本列 0 处不等）。

### 7.2 `judgeable` 与 `ruleable` 是两个不同的属性

注册表 15 个结局中有 5 个无任何规则引用。查语料后原因明确：

| 结局 | 语料块数 | 有规则 |
|---|---|---|
| `cataract_any` | 172 | ✓ |
| `amd_late` | 217 | ✓ |
| `retinopathy_any` | 188 | ✓ |
| `vision_impairment_moderate` | 135 | ✓ |
| `optic_disc_abnormality` | 17 | ✗ |
| `cataract_subtype_graded` | 16 | ✗ |
| `glaucoma_selfreport` | **1** | ✗ |
| `amd_selfreport` | **1** | ✗ |
| `vision_impairment_mild` | **0** | ✗ |

**有规则的结局有 135–217 块文献；无规则的有 0–17 块。**
所以规则库不是随意遗漏——**文献语料支撑不了它们**。

**但注册表把 `glaucoma_selfreport` 与 `amd_selfreport` 标为
KNHANES 与队列层"可判定"（judgeable=True），而语料各只有 1 块。**

**结论：`judgeable` 描述的是数据可得性，不是证据可得性。
系统里没有任何机制要求"可判定"的结局必须有文献支撑。**

**后果**：一个使用者看到某结局 `judgeable=True`，会以为系统能对它给出风险判断；
实际引擎对该结局永远返回无信号（因为没有任何规则引用它）。
**这两个字段从未对账。**

**建议（需你定）**：
- **A**：给注册表增加 `ruleable` 字段，由规则库反向派生，并在 UI 中区分
  "该结局可测量"与"该结局有规则覆盖"——**诚实的做法，倾向于这个**
- **B**：为 `optic_disc_abnormality`（17 块）与 `cataract_subtype_graded`（16 块）
  补规则——但它们已被证据基础审计判定为**本层不可检验**（无检查队列），
  补了规则也无数据可验
- **C**：从注册表移除这 5 个结局——**但它们是真实存在、且部分库确实测了的结局**，
  移除会丢失信息
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "可判定 ≠ 可成规则" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
