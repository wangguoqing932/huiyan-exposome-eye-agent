# 局限性与诚实陈述（Limitations）· v1.2

> 本文件为论文 Discussion/Limitations 章节的素材底稿，全部陈述与 `outputs/` 落盘数据一致。
> 生成日期 2026-10-12 · 对应 analysis_plan v1.2 冻结规则集

## 1. 协议偏离：规则集在确证结果之后被修改（最重大局限）

在首轮确证结果（2026-10-12 07:12）产出**之后**，规则集发生了一次修改（r02/r03/r04 交叉覆盖扩展 + r22 新增），随后基线运行显示 recall 从 0.143 升至 1.000。该提升部分源于"看过测试集后修正规则"，属**测试集拟合（test-set fitting）**，不能作为系统真实性能证据。

处置（详见 analysis_plan v1.2 §0）：
- 该事件完整记录为协议偏离，附时间线；
- v1.2 规则集（21 条）落盘时冻结，此后不再修改；
- r22 降级为 C 级/低严重度，标注"探索性规则扩展"；
- 论文须同时呈现 v1.1（原始）与 v1.2（扩展）两版指标，v1.2 的 recall=1.000 **不得**单独引述为系统性能；
- 未来工作：预注册一套全新测试对（未参与任何规则迭代），做完全盲的确证。

## 2. 信息性对数量少，置信区间宽

确证层信息性对（replicated+contradicted）极少：NHANES 14 对（7 复证 0 反证）、KNHANES 10 对（2 复证）、CHARLS 4 对（0 复证）。precision_rule=1.000 的 Clopper-Pearson 95% CI 分别为 [0.590, 1.000] 与 [0.158, 1.000]——**点估计完美但区间宽**，不能排除真实 precision 显著低于 1。full_system 基线 F1=0.583 的 bootstrap 95% CI 为 [0.286, 0.800]。

## 3. 覆盖率优先于召回的设计取舍

系统按 precision-first 设计：规则仅在文献证据充分时触发，无规则对返回 UNKNOWN 而非猜测。代价是覆盖率低（NHANES 0.269 / KNHANES 0.263 / CHARLS 0.667），大量显著对未被规则覆盖（NHANES uncovered_significant 见 metrics json）。论文须明确：本系统定位是**高精度筛选器**，非全覆盖搜索引擎。

## 4. 横断面数据的因果局限

验证数据库均为横断面（NHANES/KNHANES）或自报结局（CHARLS）：
- 吸烟×白内障出现"保护性"方向反转（详见 docs/bias_investigation_smoking_cataract.md）：60-69 岁层各吸烟组患病率均约 11%，指示年龄混杂 + 反向因果（晶状体混浊确诊后戒烟）+ 存活者偏倚。方向审计（C4）已将该类信号隔离；
- CHARLS 眼病为问卷自报，0/4 复证可能部分反映测量差异而非规则错误；
- 所有 OR 为横断面关联，不构成因果推断。

## 5. 基线比较不完整

pure_llm / naive_rag / lightrag 三个 LLM 基线在 2026-10-12 因 API 周额度限流（429）返回降级输出（全 NO），其有效结果仅来自 2026-10-11 的 temp=0.0 单种子运行。API 恢复（2026-10-14）后应重跑并以多种子均值±CI 报告。当前基线结论（full_system 优于 LLM 基线）为**初步**结论。

## 6. 规则证据的时效与来源偏差

规则仅来自文献/指南（PPP 指南 + PubMed 检索池，1,060 chunks），存在发表偏倚（阴性结果少）与检索窗口偏差；证据等级为人工判定（A/B/C），未见双盲二次评分。r15（镉×白内障）因唯一证据报 OR≈0.97 被撤销，说明池内"唯一来源"规则稳健性有限。

## 7. 指标口径

- precision_rule 分母为信息性对（rep+con），uninformative 不计入——这高估了与传统 binary gold 的可比性；
- FDR 为 BHY（任意依赖稳健），较 BH 保守，可能漏检部分真关联；
- 负控 r01（尿酸×白内障）如预期落入 uninformative，支持管线有效性，但仅 1 条负控，不足以系统评估假阳性率。

## 论文表述模板（Discussion 用）

> The rule set was modified once after observing first-round confirmatory results (protocol deviation, fully documented in analysis_plan v1.2 §0); consequently the reported recall of 1.000 for the v1.2 rule set is optimistic and should be interpreted as exploratory. Precision was 1.000 (95% CI 0.590–1.000, NHANES) over only 14 informative pairs; coverage was 0.269 by design (precision-first, UNKNOWN for unevidenced pairs). Cross-sectional databases limit causal interpretation; the smoking–cataract reversal is attributed to age confounding, reverse causation, and survivorship bias (direction audit quarantined). LLM-based baselines were API-rate-limited during final runs and will be re-run multi-seed; current baseline comparison is preliminary.
