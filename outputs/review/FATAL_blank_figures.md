# 致命发现：3/8 图是空白占位符，而自动 QC 全部 PASS

**审查人**：主审（基于 reviewer-panel 步骤 5 图像预检的人工目视延伸）
**日期**：2026-10-15
**严重度**：**致命**（不修正不可投稿）

## 发现

对 8 张图逐张目视检查后：

| 图 | 实际内容 | 7_1 自动 QC 判定 |
|---|---|---|
| figure1_architecture | **完全空白**：3/3 面板为占位文字 `[panel_x: plot_type="" not auto-rendered]` | **PASS** ❌ |
| figure2_performance | 正确渲染（0.435 / 0.327 / 0.301 / 0.080） | PASS ✅ |
| figure3_rule_evaluation | 正确渲染（12 行，数值与 Results 一致） | PASS ✅ |
| figure4_demo_case | **完全空白**：4/4 面板为占位文字（含 `plot_type="pyramid_stack" not auto-rendered`） | **PASS** ❌ |
| figure5_reasoning_trace | **2/3 面板空白**；面板 c 渲染但**节点标签重叠** | **PASS** ❌ |
| figure6_dose_response | 正确渲染（33 行剂量反应） | PASS ✅ |
| figure7_power_mde | 正确（4 轮迭代后；项目内渲染器） | PASS ✅ |
| figure8_cohort_transportability | 正确（4 轮迭代后；项目内渲染器） | PASS ✅ |

**3 张图有实质缺陷，全部通过了自动 QC。**

## 根本原因

`figure1`、`figure4`、`figure5` 的 archetype 分别是
`schematic_led_composite`、`image_plate_plus_quant`、`schematic_led_composite`
——它们的面板**没有声明 `plot_type`**（原计划由 7_3 生成 AI 示意图或手工拼版）。
共享渲染器遇到无 `plot_type` 的面板时写入一行占位文字并返回，
而 `verify_figures_tables.py` 检查的是：
- 契约能否解析 → 能
- source_data 是否存在 → 存在
- "N panels parsed" → 解析到 4 个面板
- "N rendered file(s)" → 写出了 2 个文件

**四项全部为真，而图是白的。** 检查器验证的是"渲染流程走完了"，
不是"渲染出了内容"。

## 我的报告错误（须一并更正）

在 writer 7_1–7_3 各轮中，我报告过
「自动 QC：PASS。**人工目视：PASS**」。
**该表述对全部 8 张图而言是错的**：我的目视检查当时只覆盖了 figure7 与 figure8
（各 4 轮迭代）。我把两张图的目视结论写成了对八张图的结论——**过度概括**。

本轮已在 `outputs/review/image_integrity_prescreen.json` 的
`honest_limitation` 字段中更正该范围，本文件为正式记录。

## 影响

- **Figure 1（架构图）与 Figure 4（演示案例）在正文被引用**
  （Results 末段 "Figure 4 shows one worked case end to end ... Figure 5 traces
  it through the three architectural layers"），而它们是白页。
- 投稿版图集含 3 张无内容图片 = 编辑直接退回。
- 图例（中英两版）对 figure1/4/5 做了详细的逐面板描述，
  **描述的是不存在的内容**——与 figure7（图例称有参考线而图上没有）
  和 figure2（图例称有 v1.1 行而源数据没有）属同一类缺陷，
  但这两处已修，figure1/4/5 尚未。

## 修法

**不是**把 `plot_type` 随便填一个值让它"能渲染"——那会生成与契约声明不符的图。
三条可行路径：

1. **手工/AI 生成示意图**：7_3 阶段已产出 figure1 与 figure5 的中英双版
   BioRender 风格提示词（`outputs/paper/figure_prompts.md`）。按提示词生成图，
   放入 `outputs/figures/manual/`，并在契约中声明为手工图
   （与 figure7/8 的项目内渲染同例）。
2. **改写契约为可渲染类型**：若 figure1 的"架构"可用 `horizontal_bar` 或
   流程式排版表达，就把契约改成渲染器支持的类型并重画 source_data。
   **但须先确认改写后的图仍表达契约声称的结论**，否则就是拿一张能渲染的图
   替换一张说真话的图。
3. **figure4（演示案例）建议删除或并入补充材料**：它展示的是系统输出的四个视图，
   与本文的规则可迁移性论点关系最弱；删掉可同时解决空白图与篇幅问题。

## 必须同时修的流程缺陷

`verify_figures_tables.py` 对占位符返回 PASS，这是**检查器的漏洞**。
最低成本的补救：在 7_1 QC 之后固定加一步"占位符扫描"——
对每张 PNG 检查是否包含渲染器写入的占位标记文本
（`not auto-rendered` / `missing ... col`）。该扫描成本极低且能拦住全部三处。
已在本轮实现并纳入 `scripts/qc_figure_placeholders.py`。
