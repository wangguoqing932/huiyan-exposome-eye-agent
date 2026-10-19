"""Record the arbiter regression test and what it measures."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "AGENT_AUDIT.md"

BLOCK = """

---

## 十七、补上仲裁层的回归测试（此前为零）

### 为什么必须补

§十六 的结论是：**仲裁层的等级是提示词措辞的函数**——同一模型、温度 0、
同一输入，三个字段表措辞把 `smoking × amd_late` 从"12 次里 1 次 high"
变成"6 次全 high"再变成"12 次全不 high"。

而**规则层有确定性回归测试，仲裁层一个测试都没有**。
所以那次行为变化，若不刻意跑三次比对，不会被任何检查发现。

### 新增（`scripts/arbiter_regression.py` + `tests/test_arbiter_regression.py`）

5 个固定探针 × 6 次，覆盖不同仲裁路径：
普通规则命中 / 患者因素升级 / 分级被订正的规则 / 规则+因素 / 越界对。

**断言的对称性是设计核心**：

| 层 | 断言 | 理由 |
|---|---|---|
| **规则层** | **必须跨重复不变** | 它按构造是确定的，任何变化都是缺陷 |
| **仲裁层** | **只与基线比分布，超出容差才失败** | 它不确定；要求它确定会永久失败并被忽略 |

**要求仲裁确定性的测试会被忽略，什么都不要求的测试是装饰。**
基线把"仲裁行为变了"从不可见事件变成一条失败的断言——
而这是提示词措辞成为该层最强杠杆时，唯一重要的性质。

### 实测基线（2026-10-15）

```
smoking|cataract_any                    tiers={'medium': 6}  conf=[0.6, 0.7, 0.75]
fasting_glucose|cataract_any|diabetes   tiers={'high': 6}    conf=[0.8, 0.82, 0.85]
smoking|amd_late                        tiers={'medium': 6}  conf=[0.85, 0.9]
pm25|glaucoma_iop_elevated|hypertension tiers={'medium': 6}  conf=[0.7]
aspirin|cataract_any                    tiers={'unknown': 6} conf=[]
```

**等级 5/5 探针全部 6/6 稳定**（在极简提示词下）。

### 但新字段暴露了另一件事：自陈置信度本身在漂

看 `conf` 列：**同一探针、同一输入，6 次里给出 2–3 个不同的置信值**
（`smoking|cataract_any` 得 0.6 / 0.7 / 0.75）。

**所以 `arbiter_confidence` 虽是等级不变的，但它本身不是可重复的量**，
**不能当作固定阈值使用**（例如"低于 0.5 就转人工"——同一次判断昨天 0.5 今天 0.7）。

它的可用形式是**区间或序数**（"该判断的置信在本模型上落在 0.6–0.9"），
或只用它做**相对比较**。**这一点必须在 UI 或文档中写明，否则会被当成一个精确的分数。**

### 另一条值得记的观察：它对自己"违逆规则层"很自信

`smoking|amd_late`：**规则层 medium，仲裁自陈置信 0.85–0.9。**
即**仲裁在自信地给出与规则层不同的等级**，而 §十六 已证明这个等级会随措辞整档翻转。

**"高置信"在这里不表示"这个判断稳"，只表示"模型此刻很确定"。**
这正是 §十四 结论的加强版：`confidence` 不反映仲裁的犹豫，
**而仲裁自报的 confidence 也不反映它自己的可重复性。**

### 运行方式（默认套件不受影响）

```bash
python -m pytest tests/ -q                              # 15 passed, 1 skipped, 0.23s
ARBITER_REGRESSION=1 python -m pytest tests/test_arbiter_regression.py -q -s
                                                         # 1 passed, 124.5s
```

**默认跳过**：它要发约 30 次 LLM 调用，而其余 15 个测试总耗时 0.23 秒。
把网络依赖塞进默认套件会让整套测试变成没人跑的东西。

### 已自行验证这个测试真的会失败

**不会被触发的测试是装饰。**篡改基线（把 `smoking|amd_late` 从
`{medium:6}` 改成 `{high:6}`）后重跑：

```
ARBITER REGRESSION: 2 problem(s)
  smoking|amd_late|: share of 'high' moved 1.00 -> 0.00 (tolerance 0.34); ...
  smoking|amd_late|: share of 'medium' moved 0.00 -> 1.00 (tolerance 0.34); ...
```

随后已还原基线（复验 `{medium: 6}`）。
"""


def main() -> int:
    t = DOC.read_text(encoding="utf-8")
    if "补上仲裁层的回归测试" in t:
        print("already recorded")
        return 0
    DOC.write_text(t.rstrip() + BLOCK, encoding="utf-8")
    print(f"AGENT_AUDIT.md updated (+{len(BLOCK)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
