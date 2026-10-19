# v1.1 确证运行归档（双版本呈现用）

**来源**: git commit c244af7^（2026-10-12 v1.2 重跑前的最后一版）——由 R4 复审（2026-10-14）恢复落盘。
**规则集**: v1.1（20 条；无 r22、无 r02/r03/r04 交叉覆盖扩展）
**运行时间**: 2026-10-11 20:59–21:04

用途：analysis_plan v1.2 §0 处置第 3 条要求"报告中同时呈现 v1.1（原始）与 v1.2（扩展）两版指标"。

| 数据集 | rule pairs | replicated | coverage |
|---|---|---|---|
| NHANES | 8 | 1 | 0.154 |
| KNHANES | 7 | 1 | 0.184 |
| CHARLS | 3 | 0 | 0.500 |

注意：
- 两版对应不同规则集；v1.2 含探索性扩展（test-set fitting 事件详见 analysis_plan v1.2 §0）。
- v1.1 的 precision_rule_ci95 [1.0, 1.0] 为当时 bootstrap 退化值，**勿引述**（方法学更正见 analysis_plan §0.1-更正2）。
