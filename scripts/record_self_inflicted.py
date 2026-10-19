"""Record the retrospective correction: the arbiter instability was self-inflicted."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 二十三、★★ 重大更正：那个"仲裁不确定"是我自己造成的

### 事实

r11 恢复 A/high 之后（§二十一），重跑确定性脚本：

```
smoking x amd_late   final={'high': 12}   rule={'high': 12}     12/12 稳定
smoking x cataract   final={'high': 12}   rule={'high': 12}     12/12 稳定
varies at temp=0     : 0
```

**而 §十三 记录的同一配对是 `{medium: 11, high: 1}`、§十八 是 20%–50% 摆动。**

### 完整时间线

| 时点 | r11 的级别 | 规则层输出 | 仲裁行为 | 我当时的解读 |
|---|---|---|---|---|
| §六（最早） | **A/high** | high | **稳定 `{high: 5}`** | 仲裁层稳定 ✓ |
| §八 | 我错降为 B/medium | medium | **摆动 medium↔high** | "仲裁不确定"（§十三/§十四） |
| §十六 | 同上 | medium | 随措辞 0%→100% 变化 | "措辞是最强杠杆" |
| §十八 | 同上 | medium | 自陈置信与稳定性**反向** | "该字段会误导" |
| §二十一 | **恢复 A/high** | high | **稳定 `{high: 12}`** | — |

### 所以真实发生的是

**仲裁层一直在正确地坚持 high。** 它读到的证据——
AAO PPP AMD 原文 "Cigarette smoking has been identified as the **primary
modifiable risk factor** in numerous studies on advanced AMD"——
**是一份指南级的强陈述。**

**是我把 r11 降到 B/medium，让规则层输出 medium，制造出一个规则层与证据相矛盾的场景，
然后请仲裁去裁决那个矛盾。**

**仲裁每次都倾向 high，所以看起来"不确定"。它不是不确定——
它是在反复告诉我规则层错了。**

### 因此必须撤回的结论

| 节 | 原结论 | 现状 |
|---|---|---|
| §十三 | 等级不可重复：规则层确定、仲裁层会变 | **撤回**。在规则层未被破坏时，两者都稳定 |
| §十四 | 仲裁不可重复且非采样参数 | **撤回归因**。变异源于规则层被错降，不是提供方 serving |
| §十六 | 仲裁等级是提示词措辞的函数 | **部分保留**——三个措辞变体的差异是实测的；**但它是在一个被破坏的规则层上测的**，不能据以推断正常运行时的灵敏度 |
| §十八 | `arbiter_confidence` 与稳定性反向，会误导 | **保留观察，撤回解释**——"反向"是在被破坏的状态下测的；该字段是否在正常状态下也无用，**未测** |
| §十七 | 仲裁层缺少回归测试 | **保留**。这条与上面的错误无关，且基线现已重录 |

### 关于 `arbiter_confidence` 的处置不变

**仍然只进 metadata、不进入面向用户的展示。**理由改变了：
不再是"它与稳定性反向"，而是**"我们尚未在规则层正常的状态下测过它是否有用"**。
**在测过之前不展示一个未经验证的确定性指标**——这条纪律本身与上述错误无关。

### 这次连锁错误的形状

**一个错误（§八 错降 r11）→ 产生一个症状（仲裁看起来不稳定）→ 我为那个症状写了五节分析
（§十三/§十四/§十六/§十七/§十八）→ 全部建立在被我自己破坏的状态之上。**

**我从未在诊断前先确认"被测对象是否处于正常状态"。**
这与 §二十二 修掉的字母歧义是同一类问题的两种形态：
**§二十二 是字段含义不一致；这一节是"被测系统已被我改动"。**

**留给下次的纪律**：
**在把某个行为判定为缺陷之前，先确认产生该行为的输入与配置处于已知的正常状态。**
本会话里我至少三次违背这条：§八（未查 `linked_rules` 是否可靠）、
§十三–§十八（未查规则层是否被我改坏）、§十九（未查正则是否会过度匹配）。

### 未受影响的部分

**§二十二（字母 A 的歧义与校验）不受影响**——那个歧义是真实的，
它正是让我做出 §八 那次错降的原因，修它是对的。

**§十七（仲裁回归测试）不受影响**——它现在是记录"正常状态"的基线，
而正常状态下的分布已重录为全稳定。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "那个" in t and "仲裁不确定" in t and "是我自己造成的" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
