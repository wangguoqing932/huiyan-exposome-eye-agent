# scripts/ 注册表(R12 2026-10-16 整理)

> 约束:本目录只收**可重复运行的管道脚本**。一次性记录/验证脚本属写作轮次产物,
> 改动它们不影响管道,但删除前先查 `outputs/paper/.writer/` 引用。

## A. 核心管道(入口:`run_all.py`,全部纯本地除标注外)

| 脚本 | 角色 |
|---|---|
| run_all.py | canonical 8 步链,任一步失败即中断 |
| build_entity_a/b_registry.py, build_evidence_base.py, generate_cases.py | 资产完整性校验器(A1-A5/B1-B6/E1-E7/C1-C6) |
| evaluate.py / evaluate_knhanes.py / evaluate_charls.py / evaluate_charls2015.py | 四库确证(接 variable_map 运行时守卫+患病率门) |
| survey_sensitivity_export.py / survey_sensitivity_R5.R / apply_survey_variance.py / rebuild_deliverables_R5.py | survey 方差主口径链(顺序敏感) |
| run_baselines.py / make_baseline_summary_R5.py / make_baseline_summary_R11_goldcheck.py / make_baseline_bootstrap_ci.py | 基线(需 llama-server:8082 的档标注在 README) |
| run_fused_system.py | G2 正式融合系统(G3/G4/G5 已归档 docs/archive_g3g4g5/) |
| literature_validation.py | 文献层(search 需 NCBI,extract 需 LLM) |
| generate_paper_tables.py / render_top_figures.py | 交付表(生成3+校验3)/8 张论文图(统一风格；旧 renderer 仅转发) |
| synthetic_regression.py | **M1 合成效应注入回归**(已知真值评估面,pytest 可跑) |
| build_lightrag_index.py | 索引重建(需 DeepSeek+Ark;索引已冻结 936MB) |
| fetch_pubmed.py | 证据池增量抓取 |

## B. 队列层(八队列论文线)

build_cohort_frames.py / cohort_confirmatory.py / cohort_rule_coverage.py / cohort_heterogeneity.py / cohort_power.py / cohort_raw_recon.py / cohort_exposure_scan.py / cohort_vision_scan.py / build_knhanes_frames.py(+.R) / validate_knhanes_frames.py / validate_nhanes_exposures.py / positive_control.py / ipd_interaction.py / mediation_analysis.py / power_analysis.py / dose_response_*.py / clhls_sensitivity.py / detect_exposure_gates.py / nhanes_outcome_validation.py / headline_sensitivity.py / r13_cutpoint_sensitivity.py

## C. Agent 诊断(outputs/agent/)

agent_audit / agent_full_stack_test / agent_escalation_test(+regression) / agent_arbiter_{determinism,reliability,confidence} / arbiter_confidence_usefulness / arbiter_regression / performance_bottleneck_diagnosis / audit_output_provenance

## D. 写作轮次一次性脚本(不动管道)

record_* / verify_* / build_canonical_predictions / verify_canonical_predictions / build_references_docx / build_manuscript_docx / rebuild_table* / rebuild_all_tables / renumber_figures / render_top_figures / figure_style_top / withdraw_blank_figures / refine_figure_legends / fix_* / apply_framing_corrections / disclose_* / correct_* / update_* / extend_citation_pool_intro / fill_chinese_legends / build_citation_pool / assemble_manuscript / assemble_submission_zip / build_submission_package / build_cover_letter / build_supplementary / build_strobe_checklist / qc_english_manuscript / qc_figure_placeholders / image_integrity_screen / figure_inventory_stage0 / retitle_* / write_* / find_guideline_citations / fetch_journal_guidelines / verify_manuscript_numbers / verify_r2_claims / verify_results_numbers / verify_rule_citations*(PubMed 版需联网) / regrade_rules / regrade_cataract_rules / rule_evidence_grade_audit / rule_grade_* / evidence_base_audit / fix_evidence_level_ambiguity / append_ledger_round34 / extract_creles / build_phase7_9_artifacts / build_source_data_* / build_descriptive_table / build_table2 / build_table5b_ipd / make_baseline_* 已列 A。phase5_*.py.bak 为存档。

## 纪律

1. 新脚本必须归入上表之一,或在 PR 说明里声明所属;
2. variable_map.yaml 是操作化唯一事实源(evaluate* 已接守卫,新分析脚本同样接);
3. jsonl 一律追加写 + epoch 字段(M11 待办,新写入者从现在起先带 epoch);
4. 归档区(docs/archive_g3g4g5、docs/history)只增不删。
