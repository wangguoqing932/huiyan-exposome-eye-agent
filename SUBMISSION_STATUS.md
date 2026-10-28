# SUBMISSION_STATUS.md — 慧眼（huiyan）

**期刊**：Journal of Medical Internet Research (J Med Internet Res)
**文章类型**：Original Paper（Section: Clinical Information and Decision Making）
**稿件编号**：**115413**
**状态**：2026-10-27 提交（Submission Completed, articleId 115413）→ **已退稿，理由为方法学问题** → 2026-10-28 完成 R31 方法学修复（见 `docs/history/R31_METHODS_FIX_2026-10-28.md`）；待选下一家期刊
**预警名单核查**：2026-10-24，check_warning_journal.py（刊名 + ISSN 1438-8871 双查）——未命中 2020–2026 任何年度预警名单

## R31 修复后的主结果（2026-10-28）

- **外部（KNHANES 301 对，同一 gold3）**：全智能体 G2 F1 **0.312**（P 0.357 / R 0.278）；规则层 G0 **0.360**（P 0.281 / R 0.500）；基线 LightRAG 0.145、pure LLM 0.135、naive RAG 0.094
- **外部结论**：agent 胜过三个 LLM/RAG 基线，但**低于自身确定性规则层**（证据门提精度、砍召回）
- **内部（NHANES 80/159）**：G2 0.571 / 0.522，标 **in-sample**（规则在首次确证后修订，R=1.000 为构造值；修订前 v1.1 = 0.111）
- 重跑可复现：2026-10-28 与 2026-10-15 逐位一致（`outputs/confirmatory/g2_rerun_20261028.json`）

## 稿件
- 主稿：outputs/paper/manuscript_agent_first.docx / .pdf（37 页，4 表 + 6 主图，正文 5,988 词 Word 口径，摘要 346 词 ≤350，portrait，0 中文）
- Multimedia Appendix 1：outputs/submission/Multimedia_Appendix_1.docx（补充表 S1–S8 + 图 S1–S2 + 移入的扩展分析）
- Cover letter：outputs/submission/cover_letter.docx / .md（JMIR 四点 fit + 开源仓库）
- 投稿版图（≤1200×1200 px）：outputs/figures/submission_1200/

## 提交记录（2026-10-27）
| 步骤 | 内容 |
|---|---|
| Step 1 | Section + Article Type + 11 项声明复选框 + 三个 radio |
| Step 2 | 两作者（Guoqing Wang / Xianglong Yi，均带 ORCID）、机构、标题、346 词摘要、6 关键词；通讯作者为 Xianglong Yi |
| Step 3 | 主稿 docx（2 MB）；AI 使用声明 = Yes，7 个用途类别 + 开源模型/Other 工具，含确认勾选 |
| Step 4 | 6 张主图（各带数据库图注）+ Multimedia Appendix 1 + cover letter（reviewer 不可见） |
| Step 5 | Finish Submission → Submission Completed |

## 代码开源（JMIR ML 政策第 3 条）
- 公开仓库：https://github.com/wangguoqing932/huiyan-exposome-eye-agent
- Declarations "Code availability" 已填该 URL；Zenodo DOI 录用后归档

## JMIR 政策对照
- 独立数据验证 ✓｜面向医务者的语言 ✓｜开源工具 ✓｜ML 报告指南（TRIPOD+AI + STROBE）✓
- 生成式 AI 使用披露 ✓（系统声明 + 稿件 Declarations）｜P 值口径统一 ✓｜摘要 346≤350 ✓｜图表竖版 ✓

## 后续
- 确认邮件发至 17690924120@163.com；审稿意见经系统邮件驱动
- 可在 https://www.jmir.org/author 查看状态（当前 Unassigned）
- 可选：Fast-Track 付费加速未选择

## 费用
- JMIR Original Paper APC：接收后计费（以官网 Fee Schedule 为准）
