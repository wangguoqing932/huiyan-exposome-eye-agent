# R29 主稿压缩为 4 表 / 6 图（2026-10-23）

## 触发

作者反馈三点：

1. PDF 在 ZCode 里显示为白色；
2. 正文表格太多，4 个表差不多；
3. 正文图片最多 6 张。

## 主稿表图调整

### 正文 4 表

| 主表 | 内容 | 来源 |
|---|---|---|
| Table 1 | 八队列参与者、person-waves、BMI cut-point、入组理由 | `table1_registry.md` |
| Table 2 | 21 条规则的 flag、方向、证据等级、来源 | `table2_rules.md` |
| Table 3 | 每个数据集的系统级 F1（full vs 三条基线）+ 规则层 R/C/U | `table3_performance_by_dataset.md`（原 Table 8） |
| Table 4 | 八队列 between-cohort heterogeneity、I²、τ²、prediction interval | `table4_transportability.md`（原 Table 5） |

Table 3 把“系统级性能”和“规则层结果”放在同一张表：NHANES 两代、KNHANES、CHARLS、八队列、四库文献。
“not run”只表示该系统级基线未跑，不是结果缺失；表注写明。

### 移入 Supplement 的 6 表

| 补充表 | 内容 |
|---|---|
| Supplementary Table S1 | 八队列描述性特征（原 Table 1b） |
| Supplementary Table S2 | NHANES/KNHANES/CHARLS 规则层 precision/coverage（原 Table 3） |
| Supplementary Table S3 | 四层验证的 pairs/testable/informative（原 Table 4） |
| Supplementary Table S4 | 两队列规则的 participant-level interaction（原 Table 5b） |
| Supplementary Table S5 | 统计 power / MDE（原 Table 6） |
| Supplementary Table S6 | 测量模态 evidence audit（原 Table 7） |

补充表与 S1/S2 图例统一收在
`outputs/submission/supplementary_tables_figures.md`；原始表文件移到
`outputs/tables/supplementary/`。

### 正文 6 图

- Figure 1 architecture
- Figure 2 system performance
- Figure 3 rule-level evaluation
- Figure 4 dose-response
- Figure 5 power
- Figure 6 cohort transportability

Figure S1（demo case）与 Figure S2（reasoning trace）移入 Supplement；
`figure_legends_main.md` 只保留 Figure 1–6，`figure_legends_supp.md` 收 S1/S2。
正文引用改为 “Supplementary Figure S1/S2”。

### 引用重映射

| 原引用 | 新引用 |
|---|---|
| Table 8 | Table 3 |
| Table 5 | Table 4 |
| Table 1b | Supplementary Table S1 |
| Table 3（敏感性） | Supplementary Table S2 |
| Table 4（验证层） | Supplementary Table S3 |
| Table 5b | Supplementary Table S4 |
| Table 6（power） | Supplementary Table S5 |
| Table 7（evidence audit） | Supplementary Table S6 |
| Figure S1/S2 | Supplementary Figure S1/S2 |

## PDF 白色问题

ZCode 内置 PDF 查看器对 LibreOffice 生成的矢量 PDF 显示为白页；同一 PDF 在
PyMuPDF 渲染正常。已生成 **RGB 栅格预览 PDF**：
`manuscript_agent_first_preview.pdf`（96 dpi，JPEG 80，40 页，4.9 MB），
用于 ZCode 预览；投稿仍用矢量 `manuscript_agent_first.pdf`。

## 验收

- `manuscript.md`：91,168 B。
- 正文 7,700 词；abstract 412 词；References 27 条。
- Word/PDF：40 页，4 表，6 主图，0 中文。
- `qc_english_manuscript.py`：20/20 PASS（tables cited [1,2,3,4]）。
- `verify_results_numbers.py`：70/70 PASS。
- `polish_bilingual.py --check-only`：OK；`.md` 与 `.en.md` 逐字节相同。
- 补充文件：`outputs/submission/supplementary_tables_figures.md`（6 表 + S1/S2 图例）。

## 门与文件

- 7_1（图表 QC）、7_2（图例）、7_4（Results 引用）、7_5（Methods 引用）、
  7_7（Discussion 引用）、7_8（装配）因 R29 表图调整重新提交待作者确认。
- 当前主稿文件：`manuscript.md` / `.en.md`、`manuscript_agent_first.docx`、
  `manuscript_agent_first.pdf`、`manuscript_agent_first_preview.pdf`。
- 未投稿。
