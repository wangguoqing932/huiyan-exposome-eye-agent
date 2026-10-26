# R24 — 论文重新框定为 agent 构建与验证（2026-10-24）

> 作者指出：论文是构建 agent，但摘要只把"21 条文献规则 + 三态标准"写成一句话，
> 读起来像一篇暴露组转运性研究，而不是 agent 论文。

## 改动

- **标题**：改为
  "An explainable rule-knowledge-graph-LLM agent for exposome-eye screening:
  strong system performance but poor rule transportability across eight cohorts"
- **摘要**：重写为 agent-first 结构。
  Background 讲多层 agent 的可检查性与文献规则异质性；Methods 明确写
  "We built Huiyan"（21 条规则 + LightRAG KG 1,060 chunks + LLM arbiter）；
  Results 先给系统性能（0.522 vs 0.392/0.335/0.080；0.480 vs 0.186/0.178/0.069，
  McNemar 全显著），再给规则层验证（6/21 可测、18 对 8/8/2、两条 pre-registered
  transportable 但 PI 跨 1）；Conclusions 明确"agent 能跑赢基线，但规则不转运，
  瓶颈是测量"。
- **Introduction**：新增 Huiyan 三层架构段（规则引擎 + LightRAG + LLM arbiter，
  LLM 不能加规则、只能分级与弃权），并把研究问题改为两问：系统是否跑赢基线、
  哪些规则能转运。
- **Results 顺序**：System performance 从最后移到 Internal layers 之后、
  Cross-cohort transportability 之前，读者先看到 agent，再看规则层验证。
- **Discussion 首段**：三项主发现改为（1）agent 性能胜基线；（2）性能不等于规则可转运；
  （3）测量是瓶颈。Conclusion 首句改为 "We built an explainable rule-KG-LLM agent..."。

## 结果

- 正文 6,602 词（原 6,417；增加来自 agent 架构段与摘要重构）。
- 标题页/页眉同步；Word 45 页，0 中文。
- QC：20/20、数字 70/70、双语 OK。
- 作者门 7_4/7_5/7_6/7_7 仍为 awaiting_author_confirmation（本轮改动再次落在这些节）。
