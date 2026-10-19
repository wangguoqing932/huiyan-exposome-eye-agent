"""Record the MHAS cut-point error I introduced, and its correction."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 三十三、我引入了一个新错误，并在同轮抓到：MHAS 的切点

### 经过

§三十二 我写了"约定散落在八个脚本里，应收敛到单一来源"，并把
`cohort_rule_coverage.py` 的 `BMI_CUT` 从 `build_descriptive_table.py` 抄了一份。

**抄之前我没查哪一份是权威的。抄完才发现两份在 MHAS 上不一致：**

```
cohort_confirmatory.py      MHAS -> bmi_high_25   （注释称 "pre-declared in section 19.7"）
build_descriptive_table.py  MHAS -> 30            （我早前写的）
我的新 BMI_CUT              MHAS -> 30            （抄了后者）
```

### 权威是谁：预注册原文

`docs/analysis_plan.md` §19.7（C58）逐队列声明：

> **BMI 切点**（C58）：逐队列**主切点预先声明**——
> **KLoSA/MHAS/LASI/CLHLS 用亚洲切点 25**；
> **SHARE/HRS/ELSA/CRELES 用国际切点 30**。
> 依据是两层参考率门的实测判别
> （KLoSA：25 → 23.06% PASS / 30 → 1.45% FAIL；SHARE：25 → 63.83% FAIL / 30 → 22.81% PASS）。

**所以 `cohort_confirmatory.py` 对，`build_descriptive_table.py` 错，而我抄了错的那个。**

### 这件事的形态与前面几次不同

| 前面几次 | 这一次 |
|---|---|
| 产物陈旧，没人同步 | **两处各有各的约定，而它们不一致** |
| 修法：加生成器 | 修法：**先查谁是权威，再收敛** |

**"收敛到单一来源"这个建议本身不足以防止错误——还要知道该收敛到哪一个。**
我差点把两处都改成错的那个，那样反而会让错误获得"单一来源"的正当性。

### 已修

1. **`cohort_rule_coverage.py` 的 `BMI_CUT`**：MHAS 30 → **25**，并注明依据是 §19.7（C58）
2. **`build_descriptive_table.py` 的 `cut`**：MHAS 30 → **25**，同一注明
3. **复验两份字典**：

```
coverage.BMI_CUT          {'SHARE':30,'HRS':30,'ELSA':30,'KLoSA':25,'LASI':25,'MHAS':25,'CLHLS':25,'CRELES':30}
confirmatory.BMI_PRIMARY  {'KLoSA':'bmi_high_25','MHAS':'bmi_high_25','LASI':'bmi_high_25',
                           'CLHLS':'bmi_high_25','SHARE':'bmi_high_30','HRS':'bmi_high_30',
                           'ELSA':'bmi_high_30','CRELES':'bmi_high_30'}
两处不一致：无 —— 全队列一致 ✓
```

### 对已发表结果的影响：无

**MHAS 在队列层不可检验**（无白内障列、无可测的 r13 单元格），
`build_descriptive_table.py` 里 MHAS 的 BMI 也一直是 `not available`（帧无 BMI 列）。
**所以这个错约定从未进入任何已报告的数值。**

**它进入的是我一个尚未进入正文的中间产物**——我在 §三十二 新写的 `BMI_CUT`
如果留在盘上，就是下一个消费者会踩的坑。

### 一句留给下次

**当两处约定不一致时，先找权威来源，再收敛。**
**"收敛"这个动作本身不保证正确——收敛到错的那一处，比保留分歧更糟，
因为它会让错误看起来只有一个来源。**
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "我引入了一个新错误" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
