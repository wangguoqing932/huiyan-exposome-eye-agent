# 专家盲评操作指南(给研究者)

> 目的:完成 skill Phase 4(face validity + agreement),补齐四阶段验证的最后一环。

## 你需要做的

1. **打印 3 份** [phase4_questionnaire.md](phase4_questionnaire.md)(每位专家一份)
2. **发给 3-4 位眼科专家**(最好含不同亚专科:白内障/眼底/青光眼)
3. **告知**:凭专业知识独立判断,不查文献,不讨论,10-15 分钟
4. **收回**后,将答案转录为 JSON 文件(格式见下),运行分析脚本

## 答案转录格式

收回问卷后,把每位专家的答案录入以下格式,存为 `phase4_answers.json`:

```json
[
  {
    "expert_id": 1,
    "answers": [
      {"case": 1,  "A": "Y", "B": "M", "C": 4},
      {"case": 2,  "A": "Y", "B": "H", "C": 5},
      {"case": 3,  "A": "Y", "B": "H", "C": 4},
      {"case": 4,  "A": "P", "B": "M", "C": 3},
      {"case": 5,  "A": "U", "B": "—", "C": 2},
      {"case": 6,  "A": "P", "B": "L", "C": 3},
      {"case": 7,  "A": "U", "B": "—", "C": 3},
      {"case": 8,  "A": "N", "B": "—", "C": 2},
      {"case": 9,  "A": "Y", "B": "H", "C": 4},
      {"case": 10, "A": "P", "B": "L", "C": 3}
    ]
  },
  {
    "expert_id": 2,
    "answers": [ ... 同上格式 ... ]
  },
  {
    "expert_id": 3,
    "answers": [ ... 同上格式 ... ]
  }
]
```

**字段说明**:
- A:Y(是)/ P(可能)/ U(不确定)/ N(否) —— 与问卷的勾选框对应
- B:H(高)/ M(中)/ L(低) —— A 为 U 或 N 时填 "—"
- C:1-5 整数(Likert 有用性)

## 运行分析

```bash
PYTHONUTF8=1 python scripts/phase4_kappa.py --input outputs/expert_review/phase4_answers.json
```

## 通过标准(skill Phase 4)

| 指标 | 门槛 | 含义 |
|---|---|---|
| 系统-专家 Cohen κ(问题 A) | ≥0.6 | 系统判断与专家一致 |
| 专家间 Fleiss κ(问题 A) | ≥0.6 | 专家之间彼此一致(排除"专家自己都不统一"的假阳性) |
| 有用性 Likert(问题 C) | ≥4/5 | 专家认为系统输出对临床有参考价值 |

## 10 个案例的设计逻辑(你不需要告知专家)

| 案例 | 暴露×疾病 | 系统输出 | 金标准 | 设计意图 |
|---|---|---|---|---|
| 1 | 高血糖×白内障 | YES/M | replicated | TP:核心代谢通路 |
| 2 | HbA1c×视网膜病变 | YES/M | replicated | TP:最强信号(OR=5.9) |
| 3 | 吸烟×白内障 | YES/H | uninformative | FP:A 级文献规则,数据 null(反向因果) |
| 4 | BMI×白内障 | YES/M | uninformative | FP:per-SD 有信号但二分 null |
| 5 | 尿酸×白内障 | NO/L | uninformative | 负控:系统正确沉默 |
| 6 | 血脂异常×AMD | YES/L | uninformative | FP:文献混合 |
| 7 | CRP×AMD | YES/M | uninformative | FP:炎症标志 |
| 8 | 尿酸×视力损伤 | NO/L | uninformative | TN:无规则=正确沉默 |
| 9 | 吸烟×视力损伤 | YES/H | uninformative | FP:8 队列 3/5 复证 |
| 10 | 饮酒×白内障 | YES/L | uninformative | FP:三库+前瞻全 null |

**案例分布**:2 TP + 5 FP(系统说话但数据不支持)+ 2 TN(系统沉默且正确)+ 1 NC。
故意让 FP 多于 TP——**测试的是专家在"系统说 YES 但证据可能不足"时是否同意**,
这比"大家都说 YES"的虚高一致率更有区分力。

## 注意事项

- 专家**不看到**系统的答案和金标准(盲评)
- 专家**不看到**彼此的答案(独立)
- 如果 3 位专家的 Fleiss κ <0.6,说明专家间缺乏共识,需要增加专家数或讨论后再评
- κ 结果无论高低都如实入册(论文 limitations 可讨论)
