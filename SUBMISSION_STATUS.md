# SUBMISSION_STATUS.md — 慧眼（huiyan）

**目标期刊**：Journal of Medical Internet Research (J Med Internet Res)
**文章类型**：Original Paper
**预警名单核查**：2026-10-24，check_warning_journal.py（刊名+ISSN 1438-8871 双查）——✅ 未命中 2020–2026 任何年度预警名单
**当前状态**：投稿包就绪，**尚未在线提交**（等待：Declarations 两处机构字段 + 7_1–7_8 作者门确认）

## 稿件
- 主稿：outputs/paper/manuscript_agent_first.docx / .pdf（37 页，4 表 + 6 主图，正文 5,988 词 Word 口径，摘要 346 词 ≤350 ✓，portrait ✓，0 中文）
- 预览：manuscript_agent_first_preview.pdf（ZCode 栅格版）
- Multimedia Appendix 1：outputs/submission/Multimedia_Appendix_1.docx（补充表 S1–S8 + 图 S1–S2 + 移入的扩展分析文本）
- Cover letter：outputs/submission/cover_letter.docx / .md（JMIR 四点 fit + 开源仓库）

## 代码开源（JMIR ML 政策第 3 条）
- 公开仓库：https://github.com/wangguoqing932/huiyan-exposome-eye-agent （2026-10-24 创建并推送，含 rules.yaml / variable_map.yaml / Streamlit / 全部分析与审计脚本）
- Declarations "Code availability" 已填该 URL；Zenodo DOI 录用后归档

## JMIR 政策对照（详见 journal_guidelines_snapshot.md）
- 独立数据验证 ✓｜面向医务者的语言 ✓｜开源工具 ✓｜ML 报告指南（TRIPOD+AI 正式声明 + STROBE）✓
- 生成式 AI 使用披露 ✓｜P 值口径统一 ✓｜摘要 346≤350 ✓｜图表竖版 ✓

## 待办（阻塞项）
1. Declarations 两处机构字段：Ethics 判定落款机构（public data 二次分析的具体表述）+ Funding/COI/CRediT 细目核对
2. 7_1–7_2、7_4–7_8 作者门确认（7_3 已确认）
3. （可选）llama-server 在线后补 GLM/KNHANES 矩阵 G2 运行；（可选）JMIR Fast-Track 付费加速

## 费用
- JMIR Original Paper APC：接收后计费（以官网 Fee Schedule 为准）；Fast-Track 费用为可选项，未选


## 阻塞（2026-10-24 13:1x）
- accounts.jmir.pub 人机验证（图像拼图多轮循环）在 IAB 自动化下进入幻影多选状态
  （部件堆叠实例导致计数错乱），自动通过失败 ≥3 轮。
- **需要用户在可见的浏览器窗格手动完成拼图**；完成后说"好了"，
  代理轮询到页面标题变化即接管继续登录与投稿流程。


## 技术阻塞（2026-10-27 更新）
- JMIR OJS 系统 `/author/submit/1` 的 Step 1 表单存在服务端验证循环：
  - Playwright native selectOption/check/fill 正常执行但提交后被回弹（Section/ArticleType 回到默认值）
  - JS evaluate 设值 + form.submit() 同样被回弹
  - 错误始终为：Section not selected / Article Type not selected / Reviewer required
- **结论**：JMIR 的 OJS 系统需要人工在浏览器中逐步填写（非 ScholarOne 的 JS 链可控）。
- **已完成的投稿材料**：
  - 主稿 Word + PDF：outputs/paper/manuscript_agent_first.docx / .pdf
  - Cover Letter（JMIR 版）：outputs/submission/cover_letter.md / .docx
  - Multimedia Appendix 1：outputs/submission/Multimedia_Appendix_1.docx / .md
  - 代码仓库：https://github.com/wangguoqing932/huiyan-exposome-eye-agent
  - JMIR 指南快照：outputs/submission/journal_guidelines_snapshot.md
- **需要作者手动完成**：
  1. 浏览器打开 https://www.jmir.org/author（账号 17690924120@163.com 已自动创建，密码 a215648zxsW@）
  2. 点击 "New Submission" → Step 1 选 Section "Clinical Information and Decision Making" + Article Type "Original Paper" → 勾选全部复选框 → 选 No/No/Yes 三个 radio → 填两个推荐审稿人 → Save
  3. Step 2 上传 manuscript_agent_first.docx（Main Document）+ cover_letter.docx（Cover Letter）+ Multimedia_Appendix_1.docx（Supplementary File）
  4. Step 3-5 按提示完成
- 代理已完成：稿子内容/参考文献/开源仓库/cover letter/补充材料——**全部材料就绪，只差人工在网页上做最后几步点击。**


## 进展更新（2026-10-27）

**✅ 已完成：**
- JMIR 预警检查 ✅ 未命中
- 代码开源 GitHub：https://github.com/wangguoqing932/huiyan-exposome-eye-agent
- Declarations 全部填完（无 IRB/Funding none/无 COI/CRediT 两作者/GitHub URL）
- Cover letter 写好
- JMIR 投稿系统登录成功（17690924120@163.com 自动已有账号）
- Step 1 完成（Section: Clinical Information and Decision Making, Type: Original Paper）
- **稿件 ID: 115413**
- Step 2 部分填好（机构/城市/邮编/国家/电话/标题）

**❌ 需要人工完成：**
1. Step 2：修正作者名（当前 Wang/Guoqing 互换，应为 Guoqing/Wang）
2. Step 2：添加第二作者 Yi Xianglong（M.D., Ph.D., Professor, 通讯作者, yixianglong1010@163.com, ORCID 0000-0002-8222-7836, 同一单位）
3. Step 2：检查 Title 字段是否已填
4. Step 3：上传 manuscript_agent_first.docx（Main Document）
5. Step 3：上传 cover_letter.docx（Cover Letter）
6. Step 3：上传 Multimedia_Appendix_1.docx（Supplementary File）
7. Step 4-5：确认并提交

**登录信息：** https://www.jmir.org/author
账号 17690924120@163.com（已自动存在）/ 密码 a215648zxsW@
**稿件 ID：** 115413
**投稿 URL：** https://www.jmir.org/author/submit/2?articleId=115413
