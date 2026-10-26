# 局限性与诚实陈述（Limitations）· v1.2（R5 修订 2026-10-14）

> 本文件为论文 Discussion/Limitations 章节的素材底稿，全部陈述与 `outputs/` 落盘数据一致。
> 生成日期 2026-10-12 · R5 修订 2026-10-14（五专家评审后：数据管道修复 + survey 方差主口径，见 analysis_plan §0.2）
> **R11 修订 2026-10-15**：变量操作化修复（吸烟参照组/终生饮酒/KNHANES 无效变量，见 analysis_plan §0.3 更正 10-13）；
> 本文件 §2 数字已按修正后口径更新，另见 §8 新增条目。
> **命名纪律**：三库验证层不称"确证通过"。NHANES 层为 **internal consistency check**（规则与同一库的方向一致性，且 v1.2 规则含事后扩展）；KNHANES 层为 **transportability check**（方向级跨人群迁移）；CHARLS 层为 **feasibility check**（0 信息性对，仅证明管线可运行）。

## 1. 协议偏离：规则集在确证结果之后被修改（最重大局限）

在首轮确证结果（2026-10-12 07:12）产出**之后**，规则集发生了一次修改（r02/r03/r04 交叉覆盖扩展 + r22 新增），随后基线运行显示 recall 从 0.143 升至 1.000。该提升部分源于"看过测试集后修正规则"，属**测试集拟合（test-set fitting）**，不能作为系统真实性能证据。以 v1.1（原始 20 条）规则回放同一测试集，full_system F1=0.111（4 方法中最低）——v1.2 的性能优势主要由事后扩展构造。

处置（详见 analysis_plan v1.2 §0/§0.2）：
- 该事件完整记录为协议偏离，附时间线；
- v1.2 规则集（21 条）落盘时冻结，此后不再修改；r22 引文更正（2026-10-14，§0.1 更正 1）为唯一冻结后变动（元数据级）；
- r22 降级为 C 级/低严重度，标注"探索性规则扩展"；R5 survey 方差下其两条 NHANES 对 q=0.150/0.191 → **不构成复证**（§0.2 更正 7）；
- 论文须同时呈现 v1.1（原始）与 v1.2（扩展）两版指标，v1.2 的 recall=1.000 **不得**单独引述为系统性能；
- NHANES 5 条 survey 口径复证中，r03/r04/r02 扩展贡献的 by-construction 对占多数；真正"事前注册规则"的干净复证信息每库仅 1 条构造（血糖标志×DR）；
- 未来工作：预注册一套全新测试对（未参与任何规则迭代），做完全盲的确证。

## 2. 信息性对数量少，置信区间宽

确证层信息性对（replicated+contradicted）极少。修正后 R11 主口径（survey svyglm 方差）：NHANES 15 对（**5 复证 0 反证**）、KNHANES 7 对（2 复证 0 反证）、CHARLS 4 对（0 复证 0 反证，precision 无定义）。precision_rule=1.000 的 Clopper-Pearson 95% CI 分别为 **[0.478, 1.000]** 与 [0.158, 1.000]；**保守二元口径（uninformative 记 FP）下仅 0.333 [0.118,0.616] 与 0.286 [0.037,0.710]——两口径必须并列呈现**（§0.3 更正 13）——**点估计完美但区间宽**，后验上 7/7 不能排除真实 precision 低于预注册线 0.70（P(true≥0.70)≈0.08）。敏感性口径（freq_weights GLM）下 NHANES 为 7 复证 [0.590,1.000]（r22 两条临界对 q≈0.034-0.037，在 survey 方差下不再显著）——两口径差异本身即为小样本下推断脆弱性的证据，论文双呈。

## 3. 覆盖率优先于召回的设计取舍

系统按 precision-first 设计：规则仅在文献证据充分时触发，无规则对返回 UNKNOWN 而非猜测。代价是覆盖率低（R5 按库 judgeable 集口径：NHANES 0.23 / KNHANES 0.233 / CHARLS 0.308），大量显著对未被规则覆盖（NHANES uncovered_significant 见 metrics json）。论文须明确：本系统定位是**高精度筛选器**，非全覆盖搜索引擎。（口径注记：R5 修复了 coverage 分母的 judgeable 集硬编码缺陷，修复前 KNHANES 0.263 / CHARLS 0.667 为高估，见 §0.2 更正 6。）

## 4. 横断面数据的因果局限与测量口径

验证数据库均为横断面（NHANES/KNHANES）或自报结局（CHARLS）：
- 吸烟×白内障出现"保护性"方向反转（详见 docs/bias_investigation_smoking_cataract.md）：60-69 岁层各吸烟组患病率均约 11%，指示年龄混杂 + 反向因果（晶状体混浊确诊后戒烟）+ 存活者偏倚。R5 起方向审计按预注册 §4 记录一切 OR<1 的 A 级对（第四态 direction_review，r10/r13 已入册并有偏倚调查结案）；自动隔离保留"≥2 显著反向"为记录在案的偏离（§0.2 更正 8）；
- CHARLS 眼病为问卷自报，两波（2011、2015 时间外层）均 0 信息性对——2015 波自报白内障患病率仅 1.7%（275/16,592），漏报是根本限制；唯一接近显著的同向信号 hba1c×cataract OR=1.71 [1.21,2.43] q=0.096 未过 BHY 线；
- **测量口径修复（R5）**：KNHANES 眼底结局 8/9（未检查/不可分级）此前被当阴性，修复后按缺失（复证对 OR 由 24.2/27.2 升至 25.0/28.4，方向不变）；NHANES VI 此前误用屈光球镜度 VIXPRS，已改 VIDRVA/VIDLVA presenting 较差眼 logMAR（§0.2 更正 4/5）；
- 同名暴露 flag 跨库操作化存在差异（alcohol 三库三定义、白内障"手术史 vs 自报诊断"等），论文方法节须附逐库对照表；
- 所有 OR 为横断面加权关联，不构成因果推断。

## 5. 基线对比的后端局限、prompt 敏感性与多种子波动

三个 LLM 基线（pure_llm / naive_rag / lightrag）在**本地 Qwen3.8-27B（3bit 量化，关闭思维链）**上完成（temp=0.7，预注册 5 seeds [11,22,33,44,55]，seed 已传入 API 请求体，各 run 0 失败；原定 DeepSeek 因 commandcode 周额度 429 限流切换）。full_system 为确定性规则引擎（provider=rule_engine:deterministic，零 LLM 调用，seed 不变式）。R5 公平协议修复后（seed 贯通、naive_rag 改用无等级加权的 NaiveRAG、prompt 用注册表人类可读名、no-evidence 解析透明化）：

- **R5.2 结果（judgeable 62 对口径=与确证层 metrics 同分母；survey 方差 gold，5 复证）**：G2 融合系统（规则+证据门控+LLM 仲裁）F1=**0.500** > G1 负控门控 0.476 > G0 裸规则 0.455 > pure_llm 0.418 > lightrag 0.350 > naive_rag 0.073；
- **配对 McNemar（精确）**：G2 vs 三个 LLM 基线**全部显著**（pure_llm p=0.001-0.012、naive_rag p=0.012-0.023、lightrag p=0.012-0.022）；G2 vs G0 p=0.50（2 对 discordant——门控改善方向一致但小样本下未达显著）；G0 裸规则对 lightrag 不显著（80 对旧口径 p=0.057-0.092；judgeable 口径 p=0.092-0.146，结论同）——融合组件使系统领先全部基线；**R17 双呈（zhipu GLM-5.3-flash 满血基线，159 对）**：full_system 0.480 对 lightrag 0.186 / pure_llm 0.178 / naive_rag 0.069，McNemar 全部显著（p≈10⁻¹¹~10⁻¹⁹ / 0.006-0.012）——基线升级与后端换血后排序不变且显著性增强；**归因红线**：G2 的 FP 下降来自负控弃权与证据存在性门控，LLM 仲裁 3 次全 YES 未拒任何命中——F1 提升不得归因于"LLM 仲裁把关"；
- **门控策略为先验设定非数据驱动**（§13 预注册）：负控不发言 + ≥B 级相关块发言 + C 级以下 LLM 仲裁；dev 集金标准为 rule_defined 循环结构，不可作调参集（R5.2 查明并弃用）——策略未经任何 gold 驱动的阈值搜索，属架构实现而非性能拟合；证据检索词源曾误用注册表操作化名（首次运行 G2 F1=0.143 的 bug），修正为文献词表后重跑（§13 运行记录）；
- **优化边界已由 R5.3/R6.0 消融划定（§14/§15，负结果如实报告）**：G3 文献共识门控为无操作路径（mixed 规则 r07/r08 在三库无发言对）；G4 关键词证据直推有害（F1 0.500→0.417，直推 4 次发言全为 uninformative AMD 对）；G5a 语义确认无净增益（0.476 vs 0.500——B3 实体注记已使关键词规则关联匹配≈语义检索，**检索层不是瓶颈**）；G5b 语义直推零触发（双注记门槛对无规则对逻辑自锁）；τ 相似度阈值三档结果恒等（判别由注记命中主导）。**G4+G5b 合并结论：无规则发言的先验阈值空间中不存在可用中间点（松则 FP 灾难、严则自锁）**——性能上限受三重约束：规则集冻结（科学纪律）、gold 层功效（FP 多为 uninformative 而非方向错误）、无规则发言缺乏独立依据；进一步提升需新数据扩容或预注册 v1.3+全新盲测，非推理层工程。正式系统定格 G2；
- **必须双呈 v1.1**：v1.1（事前注册规则）回放同一 gold 得 F1=0.111（TP1/FP10/FN6）——v1.2 的优势主要由事后扩展构造（§1）；figure2 已设 v1.1 影线柱，正文不得只引 v1.2；G2 门控作用于 v1.2 规则之上，不改变该构造性质；
- 本地模型为 3bit 量化 + thinking disabled，其参数化医学知识弱于满血 API 模型，可能**低估** LLM 基线上限（尤其 pure_llm）；
- **prompt 敏感性**：解析规则/prompt 措辞的变更（round 1→round 2，§0.2 更正 9）使 pure_llm 均值 F1 从 0.540 移至 0.347——在 n=5 复证的 gold 上，措辞级扰动即可改变方法排序结论，基线对比只能作描述性+有限显著性证据；
- lightrag 档在 qwen 代曾为 naive 检索模式（残血，R17 前的缺陷）；R17 基线公平修复后升级为 hybrid KG 图遍历（mix+rerank 实测更差故弃用），并在更强商用后端（GLM-5.3-flash）重跑：zhipu 代 159 对 lightrag F1=0.186 仍低于 full_system 0.480，McNemar p≈3×10⁻¹¹。其检索倾向过度肯定的模式（R=0.83、P≈0.10）与证据池发表偏倚一致（见 §6）。

## 6. 规则证据的时效与来源偏差

规则仅来自文献/指南（PPP 指南 + PubMed 检索池，1,060 chunks），存在发表偏倚（阴性结果少）与检索窗口偏差；证据等级为人工判定（A/B/C），未见双盲二次评分。r15（镉×白内障）因唯一证据报 OR≈0.97 被撤销，说明池内"唯一来源"规则稳健性有限。两套分级并存（证据池块级 A–E 与规则级 A–C）同名不同义，论文方法节须显式区分。AAO PPP 全文进入知识图谱作检索背景（关键词粗分 34A/125D），**规则本身 0 条直接引用指南**——"PPP 提供 Level A 证据"一类表述不成立，只能表述为"指南全文作为知识图谱背景语料增强检索"。个别规则引文与命题存在错配（r04 为 GxE 效应修饰研究、r16 为小鼠机制研究、r20/r21 结局定义与引文不一致），已在 rule_rationale.md 逐条如实标注。

## 7. 指标口径

- precision_rule 分母为信息性对（rep+con），uninformative 不计入——这高估了与传统 binary gold 的可比性；
- **R5 起 headline 三态标签以 survey svyglm 方差为准**（§6 预注册标准；freq_weights GLM 为敏感性口径双呈）——两者在临界对上分歧（r22），提示小样本下任何单一方差口径都不稳健；
- FDR 为 BHY（任意依赖稳健），较 BH 保守，可能漏检部分真关联；
- 负控 r01（尿酸×白内障）如预期落入 uninformative，支持管线有效性，但仅 1 条负控，不足以系统评估假阳性率；且负控预期来自课题组重叠数据的先验，非完全独立。

## 7.5 文献层外部验证的局限（R5.1，analysis_plan §12）

2026-10-15 新增的文献层外部验证（750 篇 PubMed 文献、21 条规则、排除规则自身引文）给出 precision_lit=0.889 [CP 0.653, 0.986]（16 复证 / 0 反证 / 2 混合 / 2 无信息，负控 r01 单列为 mixed）。该层的固有局限：

- **LLM 抽取协议敏感性（三轮全量重抽 + 人工复核修正轮实证）**：对"低暴露→风险升"类声明与治疗/干预类文献的方向映射，抽取协议经历三轮全量重抽（r08 判定 0/10→2/16→11/8，详见 §12 round1-3 记录）+ R7 独立抽查确认 4 处误判的人工裁定修正（round-4，修正后 r08 为 14 conc/5 disc 仍 mixed；precision_lit 不变 0.889；S3 双跑一致率 97.1%）；该敏感性说明**文献层结论对抽取器（本地 qwen 3bit）的语义能力有依赖**，未被抽查覆盖的同类文献可能仍含同类误判，理想情况下应由人工双重抽取复核（未来工作）；round-1/2 属协议形成期探索性运行（时序不可证），正式结果以 round-3+round-4 为准；
- **检索偏倚**：每规则 top-40 按 PubMed relevance 排序，偏向近期治疗学文献（如 r08 的病因学队列被纳米制剂治疗文献挤出 top-40——S2 敏感性下 r08/r05/r14/r22 变 uninformative 即此反映）；未做系统检索式的查全评估；
- **发表偏倚**：文献层天然继承发表偏倚（阳性结果更易发表），"16/17 复证"不可解读为真实 precision——它衡量的是与已发表文献共识的一致性，不是与真相的一致性；
- **证据等级未加权**：主分析按篇数等权（case report 与 meta 同权），敏感性 S2 仅保留人群病因研究；未做效应量 meta——方向投票是弱合成；
- **与规则引文的形式独立**：已排除规则自身引文并标记证据池重叠（S1 剔除重叠后 20/20 判定不变），但检索词与证据池建库词可能共享系统性偏好（同域检索习惯），非完全独立；
- 混合判定的两条规则（r07 维D×DR、r08 抗氧化×白内障）在文献层确实存在分歧证据，与 rationale 中记录的异质性一致；无信息的两条（r12 酒精、r19 促炎饮食）为相关文献不足，不构成反证。

## 论文表述模板（Discussion 用）

> The rule set was modified once after observing first-round confirmatory results (protocol deviation, documented in analysis_plan v1.2 §0). Under the pre-registered survey-design variance standard (R5), the internal consistency check on NHANES yielded 5/5 replicated with zero contradicted pairs (precision 1.000, 95% CI 0.478–1.000 over only 5 informative pairs); the KNHANES transportability check yielded 2/2 (CI 0.158–1.000); the CHARLS layer was a feasibility check only (0 informative pairs). These layers are NOT confirmatory passes: 5 informative pairs cannot statistically support the pre-registered 0.70 precision line, and most v1.2 replications involve rules added after seeing the data. Replaying the pre-expansion ruleset on the same gold gives F1=0.111 versus 0.417 for the full v1.2 system (5 seeds; local Qwen3.8-27B baselines): the difference is significant versus pure_llm and naive_rag (paired McNemar p≤0.013); after upgrading the LightRAG baseline to full knowledge-graph traversal on a stronger commercial backend, the full system remains ahead with McNemar p ≈ 10⁻¹¹ to 10⁻¹⁹ against all three baselines. Coverage is low by design (0.23/0.233/0.308; precision-first, UNKNOWN for unevidenced pairs). Cross-sectional databases limit causal interpretation; the smoking–cataract reversal is attributed to age confounding, reverse causation, and survivorship bias (fourth-state direction review; investigation on file). Baseline numbers are prompt-sensitive (a wording-level change moved pure_llm mean F1 from 0.54 to 0.35) and were obtained on a local 3-bit quantized model, likely understating LLM baseline ceilings.


## 8. R11 变量操作化修正引入的更新（2026-10-15，analysis_plan §0.3）

- **r10 相关"吸烟保护白内障"信号系编码伪影，已撤除**：原 NHANES current_smoking 参照组实为已戒烟者（SMQ040 跳转逻辑），修正后 current_smoking×dr_npdr replicated→uninformative；docs/bias_investigation_smoking_cataract.md 的混杂分析结论不再依赖该（伪）信号，但年龄混杂/反向因果/存活偏倚的机制讨论仍适用于文献层证据。
- **KNHANES 吸烟与饮酒对全部不可测**：帧内无 BS3_1 与任何有效饮酒变量（官方字典：BA2_2_1=酒驾自行车、BA2_22=搭乘酒驾、BA2_12/13=安全带），相关配对置 NA 转 underpowered，待帧重建；尿酸（HE_UAScr=砷注释错误）与 CRP 对在眼病波不可测——KNHANES 层 15 个 underpowered 中 14 个属此类结构性不可测，包括负控 r01 与 B 级 r06。
- **8/21 规则从未被任何层测到**（r07/r08/r09/r16/r17/r18/r21 B 级 + r19 C 级，见 rule_coverage_audit_R11.csv）；唯一 A 级规则 r11 被测到但 0 复证（r10/r13 已于 2026-10-16 分级审计降为 B 级，见 AGENT_AUDIT §二十六）；唯一复证的规则仍为血糖×糖尿病眼病（r02/r03/r04，与暴露-结局定义存在包含关系，同义反复风险须在 Discussion 处理）。
- **跨库同对三态标签一致率 37.5%**（48 对中 18 对，修正前 60.4%）：NHANES vs KNHANES 的 gold 本身分歧远大于 coverage gap=0.001 所示；论文不得以 gap≈0 表述"泛化无落差"。
- 基线与 G2 结论经修正 gold 双呈验证后不变（full_system 在 R11 修正 gold 上 F1=0.522、仍居首；G2=0.500 维持），但所有对外数字以 R11 修正口径为准、R5 口径仅作历史记录。2026-10-19 重跑 canonical 链后 headline 为 NHANES 16/6/0、KNHANES 15/5/0、CHARLS 4/0（上一轮 15/5 与 7/2 作废）。
- **本地数据扩容通道已关闭（CHNS 核查，2026-10-20）**：CHNS 作为候选第 13 层被结构性否决——全部健康模块仅命中 1 个"眼/耳疾病"四周急性条目，体检模块无任何视力/眼科测量，21 条规则的 B 侧可测格为 0；GBD 为汇总无个体、ICU/围术期 INSPIRE 结构性不可用。加上 NHANES 2011–2018 本地不可用、KNHANES 10 波已全用、CHARLS 2015 已入册，本地数据侧扩容至此穷尽（详见 `docs/CHNS_feasibility_2026-10-20.md`）。
