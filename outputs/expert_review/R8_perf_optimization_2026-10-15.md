# R8 轻量复审：R5.2 系统性能优化（证据门控融合推理）· 2026-10-15

- 审计对象：`docs/analysis_plan.md` §13（L178-199）、`scripts/run_fused_system.py`、`outputs/confirmatory/fused_system_R5.jsonl` + `fused_system_summary.json`、`outputs/baseline_predictions.jsonl`、`outputs/tables/performance_by_dataset.csv`、`docs/limitations.md` §5、`.executor/progress.json`、`.medical-agent/state.json`
- 审计方式：只读独立复算（Python 脚本逐对重算 TP/FP/FN、McNemar 精确检验、门控分类复现），未修改任何项目文件；pytest 实跑一次
- 审计人：科研复审审计员（R8）

## 总结论

**通过（有保留）。** R5.2 的数字层完全闭环：三库 G0/G1/G2 指标、基线 judgeable 口径、全部 McNemar p 值、门控计数、级联文件数字均与独立复算一致（0 处数字错误）；代码阈值与 §13 预注册逐项一致，无数据驱动调参痕迹；首跑 bug 的运行记录诚实且算术自洽（0.143 = 2/(2+8+4)，TP1/FP8/FN4）。**保留事项一条（P1）**：§13"先于任何融合系统运行落盘"的时序声明**无独立可证证据**——§13 未提交 git（工作区未提交，analysis_plan 最后一次提交为 2026-10-12，不含 §13），无预运行见证文件，首跑产物已被覆盖，analysis_plan.md 的 mtime（02:23:35）晚于运行输出（02:23:06，运行记录回填所致）。建议按 §12 round-1/2 先例（R7 已如实降格）在 §13/limitations 补一句时序可证性限制的披露。另有两处 80 对口径旧值残留（std 列、G0-vs-lightrag p 值），不影响任何结论。

## 逐项验证表

| # | 验证项 | 状态 | 关键证据 |
|---|---|---|---|
| 1 | §13 预注册纪律 | **通过（时序可证性缺口）** | 内容完整：三档定义 L184-192、先验理由 L180/186/188-192、评估口径 L193、dev 集 rule_defined 循环弃用声明 L180、运行记录 L195-199 如实记首跑 bug（registry 名→4 个 TP 误弃权→G2 F1 0.143→只修词源重跑）。0.143 算术自洽：TP1/FP8/FN4 → 2/(2+8+4)=0.1429，且 FP=8 与终版 G2 FP=8 相符（词源修复只救回 TP 未动 FP）。**但**"先于运行落盘"不可独立复核：git log analysis_plan.md 最后提交 2026-10-12（568bf8a，无 §13）；R6（01:01）/R7（02:08:59）报告均无 §13 先行见证；mtime 链 02:22:53 脚本→02:23:06 输出→02:23:35 plan 仅与叙述自洽 |
| 2 | 无数据驱动调参 | **通过** | 代码与 §13 逐项一致：top_k=5（run_fused_system.py L101）、≥B 级发言（L111，LEVELS B=3）、仲裁 temp=0.0/seed=20261015/thinking disabled（L70 + llm_client.py L213-217 local 分支 `enable_thinking: False`、L221-223 seed 入请求体）、YES/UNKNOWN 严格二值 prompt（L117-121）。词源修正证据：L38-40 注释 + `from literature_validation import A_FLAG_TERMS, B_FLAG_TERMS`（§12 文献词表，非 registry 名）。无网格搜索/阈值扫描痕迹；仲裁 3/3 全 YES，无"调仲裁压 FP"迹象；G2 vs G0 如实报 n.s.。轻微偏差：§13 L188 相关块判据括注"块实体含该暴露或该结局"与实现不符——实现主判据为 chunk.linked_rules 含命中规则 id（EvidenceStore entities_a 映射自 linked_rules），辅判据为文本同时含暴露+结局双 token（AND，较 §13 的"或"更严）；脚本 docstring（L13-14）与实现一致，属 plan 措辞不精确 |
| 3 | 指标复算（三库） | **通过（逐格一致）** | 独立重算 fused_system_R5.jsonl（143 记录=80+49+14）：NHANES judgeable 62 对 G0 TP5/FP10/FN2 P0.333 R0.714 **F1=0.455**；G1 TP5/FP9/FN2 **0.476**；G2 TP5/FP8/FN2 P0.385 **0.500**。KNHANES 43 对：G0/G1 2/8/1 **0.308**、G2 2/7/1 **0.333**。CHARLS 14 对：TP0/FP 5→4→4、F1=0（P/R 无定义）。与 fused_system_summary.json 九格全部一致 |
| 4 | 基线 judgeable 口径 | **通过** | 从 baseline_predictions.jsonl 独立重算（judgeable 集取 entities_b.csv nhanes_judgeable=true，10 个 b_item，62 对）：full_system **0.455**（与 G0 逐对预测完全相同，0 差异）、pure_llm **0.418**、lightrag **0.350**、naive_rag **0.073**（5-seed 均值）；80 对口径复算 0.417/0.347/0.317/0.073 与 README_baseline_predictions.md/R5_FIXLOG 一致。**差 = 18 对非 judgeable = vision_impairment_moderate 9 + vision_impairment_severe 9**，与 §13 L182 声明吻合。gold3 三源零不一致（baseline jsonl / fused jsonl / nhanes_confirmatory.csv） |
| 5 | McNemar 复核 | **通过** | G2 vs G0（NHANES judgeable）：b=0、c=2（r01 nc_abstain + r05 no_relevant_evidence），精确 p=0.50，与 summary 一致。G2 vs 三基线（逐 seed）：pure_llm p=0.0010-0.0117、lightrag p=0.0117-0.0215、naive_rag p=0.0117-0.0225——与 §13/limitations 所报 0.001-0.012 / 0.012-0.022 / 0.012-0.023 全部吻合（四舍五入），全部 ≤0.023。附带复核：G0 vs lightrag 在 judgeable 口径实为 p=0.092-0.146（limitations §5 L41 引的 0.057-0.092 是 80 对口径旧值；"不显著"结论两口径均成立） |
| 6 | 门控明细 | **通过（全量复核，非抽样）** | 计数与 summary 完全一致：evidence_Bplus 26 / arbiter_yes 3 / nc_abstain 2 / no_relevant_evidence 2 / no_rule 110（143）。注：no_relevant_evidence 实际仅 **2** 对（清单写 3 对，以数据为准），两对均已独立复现：r05 dyslipidemia×amd_late（nhanes+knhanes），top-5 检索全为 AMD 通用块、无一同时含 "dyslipidemia" token 且 r05 在证据池 0 条 linked chunks→按预注册判据弃权正确，各删 1 FP（G1 FP9→8、FP8→7）。arbiter_yes 3 对=三库 r02 hyperglycemia×cataract（relevant 仅 C 级→仲裁 YES，arbiter_note 均 "YES"，gold uninformative→维持 FP，未引入新 FP）。**5 个 NHANES replicated TP 全部 evidence_Bplus、无一弃权**（含首跑曾被误弃的 4 个）；KNHANES 2 TP 同。门控逻辑逐对符合 §13 |
| 7 | 级联 | **通过（两处旧值残留）** | performance_by_dataset.csv 6 行均值全对：pure_llm 0.418 / naive_rag 0.073 / lightrag 0.350 / full_system(G0) 0.455 / G1 0.476 / G2 0.500，n=62、McNemar 注记与 §13 一致。瑕疵：**std 列沿用 80 对口径旧值**——pure_llm 0.017（judgeable 口径 ddof=0 应 ≈0.005）、lightrag 0.005（应 ≈0.006）；naive_rag 0.089 两口径恰同值。limitations §5 L40-42 数字一致（0.500/0.476/0.455、p 值组）、**v1.1 双呈纪律行仍在（L43）**；progress.json phase6 note 含 R5.2 段（数字一致）；state.json history 末条为 R5.2 完成事件 |
| 8 | pytest | **通过** | `python -m pytest tests/ -q` → **15 passed** (0.23s)，与声明 15/15 一致 |

## 遗留问题

1. **（P1·时序可证性）§13 "先于任何融合系统运行落盘"无独立证据。** §13 未提交 git（工作区全部 R5/R5.1/R5.2 变更未提交，最后提交 2026-10-12）；R6/R7 报告（更早落盘）无 §13 先行见证；首跑（0.143）的 jsonl/pyc 均被覆盖（pyc 为终版，marshal 常量与现源码一致）。内部一致性（0.143 精确分解、阈值全对上、如实报 n.s.、仲裁零拒真）支持叙述可信，但证据等级仅"叙事自洽"。**建议**：仿 §12 round-1/2 处理（R7 降格披露），在 §13 或 limitations 补注"§13 策略段无预运行 git 快照，时序以运行记录与内部一致性为证"；并建议将当前工作区提交一次 git 快照固定证据链。
2. **（P2·数字残留）performance_by_dataset.csv 的 std 列为 80 对口径旧值**：pure_llm 0.017 应为 ≈0.005、lightrag 0.005 应为 ≈0.006（judgeable 62 对、ddof=0）；均值、排序、显著性均不受影响。
3. **（P3·口径标注）limitations §5 L41 "G0 对 lightrag p=0.057-0.092"** 系 80 对口径旧值，judgeable 口径实为 0.092-0.146；§13 用"此前不显著"措辞尚可，limitations 未标口径（结论不变，建议加注）。
4. **（P3·措辞/实现偏差）§13 L188 相关块判据括注**与实现不符（实现=linked_rules 含命中规则 id 或文本双 token AND；见第 2 项）；且 a_tok/b_tok 启发式（取首词组末词/首词，如 "C-reactive protein"→"protein"、"age-related"）存在泛匹配风险。属先验实现细节而非调参，但 plan 措辞应与代码对齐。
5. **（观察·论文表述约束）** G2 的 FP 下降（10→8）全部来自 r01 负控弃权与 r05 无相关证据弃权——前者是评估语义对齐（负控本就单列），后者是检索未命中；**LLM 仲裁 3 次触发全部 YES，未拒绝任何命中**。写论文时不得将 F1 0.455→0.500 的改善归因于"LLM 仲裁把关"，且 G2 vs G0 p=0.50 不显著（§13/limitations 已如实呈报，此处仅作表述红线提醒）。

*审计完成时间：2026-10-15；所有复算脚本为一次性 stdin 运行，未落盘、未改动任何项目文件。*
