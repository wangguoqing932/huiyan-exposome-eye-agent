# outputs/logs/ 索引

运行日志按轮次保留，**只读证据**，不参与任何计算。
文件名里的 R5 / R15 / R17 / R19 即轮次；日期为落盘时间。

| 日志 | 日期 | 内容 |
|---|---|---|
| `baseline_rerun_R5.log` | 2026-10-15 | R5 基线公平协议首轮重跑（本地 qwen，5 seeds） |
| `baseline_rerun_R5_round2.log` | 2026-10-15 | R5 第二轮（解析器/公平性修正后） |
| `lit_validation_extract.log` / `2` / `3` | 2026-10-15 | R5.1 文献层三轮全量抽取（750 篇，两步判定协议） |
| `baseline_knhanes_R15_lightrag.log` | 2026-10-21 | R15 KNHANES 301 对 lightrag 基线 |
| `baseline_knhanes_R15_zhipu.log` | 2026-10-21 | R15 KNHANES 301 对 zhipu 后端 |
| `baseline_nhanes_R17_final.log` | 2026-10-21 | R17 NHANES 159 对 zhipu 满血基线（正式口径） |
| `baseline_nhanes_R17_lightrag_hybrid.log` | 2026-10-21 | R17 LightRAG 升级为 hybrid KG 遍历 |
| `baseline_nhanes_R17_lightrag_mix.log` | 2026-10-21 | R17 mix+rerank 变体（实测更差，已弃用） |
| `baseline_nhanes_R17_naive.log` | 2026-10-21 | R17 naive RAG（zhipu 后端） |
| `ipd_rerun_20261019.log` | 2026-10-19 | Table 5b 两阶段列更正重跑（Cochran Q） |
| `phase3_verify_run_20261019.log` | 2026-10-19 | phase3 引文门重验（21/21） |
| `run_all_20261019.log` / `b` | 2026-10-19 | canonical 8 步链重跑（恢复 phase5/6 产物） |

当前对外数字以 `outputs/baseline_predictions_canonical.jsonl` 与
`outputs/README_baseline_predictions.md` 为准；日志只用于追溯当时跑了什么。
