# R6 修复验证复审（fix verification）· 2026-10-15

- 复审人：科研复审审计员（R6 轻量复审，只读审计）
- 复审对象：R5 修复批次（2026-10-14/15 "应修尽修"）是否真正闭环
- 审计方式：全部结论基于磁盘实况（文件内容、行号、命令输出、独立重算），未修改任何项目文件（本报告除外）
- 复审范围：A–J 共 10 项声明，逐项验证

## 总结论

**R5 修复批次实质闭环，可进 writer。** 10 项中 9 项完整通过，1 项（F 文档级联）通过但含 2 处轻微数字转写瑕疵与 1 处口径标签泛化——均为文档层转写问题，不影响任何落盘数据、指标、门或结论方向，无阻塞项。遗留问题共 4 条（1 低 + 3 极低），均不影响 writer 启动，建议随下一轮文字稿一并修正。

关键独立复核（非引用自报）：基线 1600 行 jsonl 逐行重算 P/R/F1 与 baseline_summary_R5.json 完全一致；McNemar b/c 不一致对计数逐 seed 一致（JSON p 值为标准双侧精确检验 2×P(X≤k)，本审计重算首次取单侧后已校正确认）；rules.yaml sha256 实算 = 5aee851d358324d4be2e35da39dad8c7fcdd9c32ae5c2c9a8010d7a5219d4504，与引用门报告完全一致；pytest 本次实跑 15/15。

## A–J 逐项验证表

### A. 数据口径三修复 —— **通过**

| # | 声明 | 实盘证据 | 状态 |
|---|---|---|---|
| A1 | KNHANES 8/9 改缺失、双眼任一眼阳性；n≈17119/8546，OR≈25.0/28.4；bi() 只认 0/1 | `knhanes_confirmatory.csv` L12：hyperglycemia×retinopathy_any n=17119, n_pos=425, OR=25.0287（replicated）；L20：hba1c×retinopathy_any n=8546, n_pos=412, OR=28.3842（replicated）。`scripts/evaluate_knhanes.py` L60-73 `bi()`：`graded = m.isin([0, 1])`（8/9 → 缺失）、`any_pos = (m == 1).any(axis=1)`（任一眼阳性）、`return any_pos...where(graded.any(axis=1))`（无分级眼才缺失），附 R5-P0 fix 注释 | 通过 |
| A2 | coverage 按库 judgeable；三库 0.23/0.233/0.308 | `scripts/evaluate.py` L403 `compute_metrics_v11(res, dataset_key="nhanes")`，L27-41 `get_judgeable_b_items` 读 `entities_b.csv` 的 `{dataset_key}_judgeable` 列；调用点：evaluate.py L461（"nhanes"）、evaluate_knhanes.py L187（"knhanes"）、evaluate_charls.py L118（"cohort"，与 entities_b.csv 的 `cohort_judgeable` 列名一致）。三库 metrics JSON coverage：nhanes 0.23 / knhanes 0.233 / charls 0.308；judgeable 计数 nhanes=10、knhanes=12、cohort=3 | 通过 |
| A3 | NHANES VI 用 VIDRVA/VIDLVA 较差眼 logMAR | `scripts/evaluate.py` L160-172：`va_r = q("VIDRVA").where(...between(20,666))`、`va_l = q("VIDLVA")...`、`va = np.log10(concat/20.0).max(axis=1)`（较差眼=max logMAR，单眼缺失回退可用眼），logMAR 换算注释 20/40→0.30、20/60→0.48、20/200→1.00 | 通过 |

### B. survey 方差主口径 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| survey_sensitivity_R5.csv 存在（129 对） | 文件在盘；实数 129 行 = nhanes 80 + knhanes 49（列：dataset/pair/n/or/ci_lo/ci_hi/p，R svyglm 输出） | 通过 |
| confirmatory CSV 有 or_svy/p_svy/q_svy/gold3_svy/gold3_freq 列 | nhanes/knhanes 两 CSV 表头均含全部 5 列 | 通过 |
| gold3 = survey 口径，NHANES replicated=5 | nhanes gold3（主口径）与 gold3_svy 计数一致：replicated 5 / uninformative 12；5 对为 hyperglycemia×{retinopathy_any,dr_npdr}、hba1c×{cataract_any,retinopathy_any,dr_npdr}；freq 敏感性口径 replicated=7，与 metrics JSON `sensitivity_freq_weights.replicated=7` 互洽 | 通过 |
| metrics JSON 有 sensitivity_freq_weights + variance_standard | nhanes/knhanes metrics JSON 均含 `variance_standard: "survey svyglm (analysis_plan §6, pre-registered)"` 与 `sensitivity_freq_weights` 完整子段。CHARLS metrics 无此二字段——经查为**有意豁免**：analysis_plan §0.2 更正 7 明示"CHARLS 无 PSU 信息，维持点估计+声明（§6 降级路径）" | 通过 |
| KNHANES 2 复证不变 | knhanes gold3 replicated=2：hyperglycemia×retinopathy_any、hba1c×retinopathy_any（gold3=gold3_svy=replicated） | 通过 |

注（独立验算）：r22 两对 svyglm 原始 p=0.00616/0.00850（survey_sensitivity_R5.csv），经 80 对 BHY（保守因子 ≈(1+ln 80)）校正得 q_svy=0.204/0.260 → uninformative，与落盘一致——降级逻辑成立。

### C. 方向审计第四态 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| 三个 direction_review_*.csv 存在 | nhanes（2 行）/ knhanes（1 行：current_smoking×cataract_any OR=0.971）/ charls（1 行：OR=0.657）均在 `outputs/confirmatory/` | 通过 |
| NHANES 含 bmi_high×cataract_any（OR 0.986）与 current_smoking×cataract_any（OR 0.698） | direction_review_nhanes.csv 实测：bmi_high OR=0.9860（q=1.0，r13）、current_smoking OR=0.6976（q=0.749，r10） | 通过 |
| quarantine 逻辑保留 ≥2 显著 | evaluate.py L378-380：`rev = reversed_any[reversed_any["q"] < 0.05]`、`quarantine = len(rev) >= 2`；第四态 = 任何 OR<1 的 A 级对（`res["direction_review"] = review_mask`，confirmatory CSV 含该列），隔离仍需 ≥2 显著反向（§0.2 更正 8 记录为在案偏离） | 通过 |

### D. 基线公平协议重跑 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| jsonl 为 R5 数据，4 方法×5 seeds×80=1600 行 | `baseline_predictions.jsonl` 实数 1600 行；baseline 计数 full_system/pure_llm/naive_rag/lightrag 各 400；seeds {11,22,33,44,55}；(baseline,seed) 20 组各 80 行；valid 全 True；文件 mtime 2026-10-15 00:46（R5 窗口） | 通过 |
| seed 在 API 请求体 | `src/huiyan_agent/llm_client.py` L81-90（`__init__` seed 参数 + R5 fix 注释）；_chat L223：`**({"seed": self.seed} ...)` 进入 `chat.completions.create`；_chat_urllib L239-240：`body_d["seed"] = self.seed` | 通过 |
| naive_rag 用 NaiveRAG | `scripts/run_baselines.py` L221-222：`from huiyan_agent.naive_rag import NaiveRAG; store = NaiveRAG()`（无证据级加权）；类定义 `src/huiyan_agent/naive_rag.py` L19 | 通过 |
| full_system provider=rule_engine:deterministic | jsonl 实测：full_system 400 行全部 `provider: rule_engine:deterministic`；其余 1200 行 `local:qwen3.8-27b` | 通过 |
| summary 数字与 jsonl 独立重算一致 | 本审计逐行独立重算：full_system P/R/F1=0.2941/0.7143/0.4167±0（TP5/FP12/FN2 各 seed 相同）；pure_llm 0.2145±0.0093 / 0.9143±0.0700 / 0.3474±0.0172；lightrag 0.2033±0.0041 / 0.7143 / 0.3165±0.0049；naive_rag 0.1000±0.1225 / 0.0571±0.0700、TP/FP/FN 逐 seed 一致——全部与 baseline_summary_R5.json 逐位一致 | 通过 |
| McNemar p≤0.012 / ≤0.013 / ≥0.057 | 逐 seed 独立重算 b/c 计数与 JSON 完全一致（如 vs pure_llm seed11 b=4,c=18）；JSON p 值 = 标准双侧精确 McNemar（2×P(X≤k)，本审计复算确认：0.00434/0.01182/0.01294/0.05737…）。vs pure_llm p∈[0.00434,0.01182]≤0.012 ✓；vs naive_rag p∈[0.00024,0.01294]≤0.013 ✓；vs lightrag p∈[0.05737,0.09229]≥0.057 ✓ | 通过 |

注：naive_rag F1 的 per_seed 含 null（P=0 的 seed）而 mean/std 按 0 计入——为 make_baseline_summary_R5.py L85-89 有注释的显式约定，且 README_baseline_predictions.md 已披露，见遗留问题 #4。

### E. v1.1 回放 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| v11_replay_R5.json = TP1/FP10/FN6/F1=0.111 | 实测 JSON：TP=1, FP=10, FN=6, P=0.0909, R=0.1429, F1=0.1111 | 通过 |
| figure2 source_data 有 replay 行 | `outputs/figures/source_data/figure2_performance.csv` L22：`NHANES,internal_validation,full_system_v1.1_replay,...,1,10,6,80,11,0.0909,0.1429,0.1111`；契约 `figures/contracts/figure2_performance.yaml` L35/L134/L147 亦含影线柱定义 | 通过 |

### F. 文档级联 —— **通过（含轻微转写瑕疵，见遗留 #1/#2/#3）**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| §0.2 更正 4-9 存在且与实际一致 | analysis_plan.md L50-105：更正 4（KNHANES 8/9，OR 24.2→25.0/27.2→28.4，与实测 25.03/28.38 一致）、5（VIDRVA/VIDLVA）、6（按库 judgeable 0.233/0.308）、7（survey 主口径、7→5）、8（第四态+≥2 显著隔离）、9（基线协议逐条）全在，除更正 7 一处 q 数字外均与落盘一致 | 通过* |
| limitations.md 数字一致 | §2：5 复证 [0.478,1.000]、freq 敏感性 7 [0.590,1.000] ✓；§3：0.23/0.233/0.308 ✓；§5：F1 0.417±0.000/0.347±0.017/0.317±0.005/0.073±0.089（与重算逐位一致）、McNemar 0.004–0.012 / ≤0.013 / 0.057–0.092、v1.1=0.111 ✓ | 通过 |
| README_baseline_predictions.md 已更新 | 有"R5 现状（2026-10-14，本节为准）"节：四个文件用途、R5 指标表（数字与重算一致）、旧 v1.2 数字标注过时 | 通过 |
| performance_by_dataset.csv 基线行=5-seed 均值 | 4 行基线：pure_llm 0.3474±0.0172 / naive_rag 0.0727±0.0891 / lightrag 0.3165±0.0049 / full_system 0.4167±0.0（n_seeds=5）——与独立重算完全一致 | 通过 |
| performance_matrix.csv 无 Wilson 残留、数字=survey 口径 | 全表 methodology="three-state gold + survey svyglm variance + Clopper-Pearson CI"，无 wilson 字样；NHANES 5 复证 [0.478,1.0] cov=0.23、KNHANES 2 [0.158,1.0] cov=0.233、CHARLS 0/4 cov=0.308，均与 metrics JSON 一致 | 通过 |
| source_coverage_report.json r22=10.1097/MD.0000000000011807 | 实测 `r22_bmi_x_retinopathy: covered=true, literature: ["10.1097/MD.0000000000011807"]` | 通过 |
| rule_rationale 与 rules.yaml 五规则一致 | r04（C/risk_up/10.1167/iovs.17-22804）、r05（C/risk_up/10.62347/QJPQ2923）、r17（B/risk_up/10.1186/s12886-024-03465-y）、r20（B/risk_up/10.1038/s41598-020-79865-z）、r22（C/risk_up/10.1097/MD.0000000000011807）——等级/方向/DOI 三要素 5/5 一致 | 通过 |

### G. 归档完整性 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| archive_v1.2_preR5/（3 CSV+3 metrics+summary+valid.jsonl） | 目录在盘，实际 8 个文件，构成与声明列举完全一致（3 个 confirmatory CSV + 3 个 metrics_v11.json + baseline_summary_v12.json + baseline_predictions_valid.jsonl）；声明行"7 文件"为计数笔误（其自列构成即 8 项） | 通过 |
| round1 与 preR5 归档存在 | baseline_predictions_R5_round1.jsonl（360KB，10-15 00:34）、baseline_predictions_preR5_archive.jsonl（118KB，10-14 22:50）均在 | 通过 |

### H. 门与测试 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| pytest 15/15 | 本次实跑 `python -m pytest tests/ -q`：**15 passed in 0.23s** | 通过 |
| 引用门 strict PASS 24/24，sha 5aee851d | citation_verification_report.json：mode=strict、overall=pass、rules_pass 21/21、citations verified=24（unverified/retracted 均 0）；records sha=5aee851d3583...d4504，本次实算 rules.yaml sha256 **逐位一致** | 通过 |
| freshness OK | state.json 与 progress.json 均绑定同一 sha（三方绑定：phase3 冻结/phase4 索引/当前 yaml），本次实算第三边一致；R5_SUMMARY L97 记录三门实跑通过 | 通过 |
| handoff OK | state.json `blocked: []`（无阻塞项）；progress.json phases 全 complete 且 phase5/6 note 与磁盘实况一致（见 I 项交叉验证） | 通过 |

### I. 状态文件 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| progress.json phase5/phase6 note 反映 R5 口径 | phase5 note：survey svyglm 主口径、按库 judgeable、NHANES 5 复证 [0.478,1.0] cov=0.23、KNHANES 2/10（8/9 改缺失、OR 24→25/27→28）、CHARLS 0/4 cov=0.308、第四态、v1.1 回放 0.111——与全部落盘一致；phase6 note：公平协议五要素、F1 排序与 McNemar 区间、round-1 归档——与落盘一致 | 通过 |
| state.json history 有 R5 条目 | history 最后一条（2026-10-14）：完整 R5 批次事件（P0×3+survey 主口径+第四态+5-seed 重跑+v1.1 双呈+三门+pytest 全绿） | 通过 |

### J. 新增脚本可运行性 —— **通过**

| 声明 | 实盘证据 | 状态 |
|---|---|---|
| 4 个 Python 脚本 py_compile | `python -m py_compile scripts/{survey_sensitivity_export,apply_survey_variance,rebuild_deliverables_R5,make_baseline_summary_R5}.py` → **ALL OK** | 通过 |
| survey_sensitivity_R5.R 在盘 | 文件在盘且 `Rscript parse`（stdin 方式绕过中文路径编码）**R PARSE OK, 44 lines**；其 129 对输出文件（survey_sensitivity_R5.csv）已在盘，证明曾成功执行 | 通过 |

## 遗留问题清单（均不阻塞 writer）

| # | 严重度 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| 1 | 低 | `docs/analysis_plan.md` §0.2 更正 7 | r22 两对 survey 方差 q 写作 "q=0.150/0.191"，与最终落盘 BHY 校正 q_svy **0.204/0.260** 不符（疑为 R5 早期轮次 BHY 分母不同的残留数字）。定性结论（q≥0.05 → uninformative、7→5 复证）与 limitations 表述（仅"不再显著"）不受影响 | 文字稿阶段把 0.150/0.191 改为 0.204/0.260（或引 survey_sensitivity_R5.csv 原始 p 0.0062/0.0085 + BHY 后 q） |
| 2 | 极低 | `docs/rule_rationale.md` r22 节 | "NHANES OR≈1.47、q=0.0396（临界）"引自 preR5 归档（archive 内实为 0.0395）；当前 R5 freq 口径 q=0.0337/0.0368。"临界"定性不变 | 随 #1 一并更新为当前值或标注数据版本 |
| 3 | 极低 | `outputs/tables/performance_matrix.csv` CHARLS 行 | methodology 列沿用统一标签 "survey svyglm variance"，而 CHARLS 实为无 PSU 的点估计+§6 降级路径（analysis_plan §0.2 更正 7 明示）；表格口径标签泛化，不改变数字本身 | 该行 methodology 改为 "point estimate (no PSU; §6 fallback)" 类表述 |
| 4 | 极低（已披露） | `outputs/baseline_summary_R5.json` naive_rag F1 | per_seed 显示 null（3 个 seed）而 mean/std 按 0 计入（0.0727±0.0891）——呈现口径不直观，但为 make_baseline_summary_R5.py L85-89 显式约定且 README_baseline_predictions.md 已写明"F1 无定义的 seed 按 0 计入均值（排除会高估）" | 可不改；若改则在 JSON 中加 `"f1_null_seeds_treated_as": 0` 说明字段 |

另记 1 条观察（非问题）：R5 修复声明 G 中"7 文件"为计数笔误——其自列构成（3 CSV+3 metrics+summary+valid.jsonl）即 8 项，归档目录实际 8 文件且构成完全匹配，归档完整。

## 审计方法备注

- pytest、py_compile、sha256、McNemar/P/R/F1 重算、coverage 与复证计数、表/文档数字核对均为**本次独立执行/重算**，非转引自 R5 自报材料。
- McNemar 重算首轮误用单侧（漏乘 2），与 JSON 差整倍数后定位原因，确认 JSON 为标准双侧精确检验，b/c 计数逐 seed 一致——JSON 正确，审计过程修正。
- CHARLS metrics JSON 无 variance_standard/sensitivity_freq_weights 属有意豁免（无 PSU），依据 analysis_plan §0.2 更正 7，不判缺陷。
