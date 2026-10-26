# outputs/agent/ — agent 诊断与回归

**不属于确证指标**；这里的产物回答“系统是否按设计工作”，不是“规则是否成立”。

- `agent_audit*`：三层架构审计；
- `agent_full_stack_test*` / `agent_escalation_*`：端到端与升档测试；
- `agent_arbiter_*` / `arbiter_*`：仲裁确定性、可靠性、信心；
- `synthetic_regression*`：M1 合成效应注入回归（已知真值）；
- `output_provenance.json`：产物溯源清单。

任何 agent 性能声明必须出自 M1 评估面或预注册盲测集（见 README 纪律第 2 条）。
