# R7 轻量复审报告：文献层外部验证（R5.1）科学闭环审计

- 审计日期：2026-10-15
- 审计对象：analysis_plan §12 / scripts/literature_validation.py / data/processed/lit_validation_* / outputs/confirmatory/literature_validation_* 及级联交付物
- 审计方式：只读。指标用独立脚本从 CSV 重算；PubMed 摘要经 E-utilities 只读核对 3 条。
- 严重度分级：高（推翻结论）/ 中（影响个别规则判定或声明可信度）/ 中低 / 低 / 微（措辞）。

## 总结论

**基本闭环，通过（附条件）。** 数据链完整（21 规则 → 750 篇检索 → 750 篇抽取 → 750 行明细），全部指标（21 规则判定、S1/S2/S3、precision_lit=0.889、CP CI [0.653, 0.986]）可从明细 CSV **逐位复算一致**；独立性（自引文排除）与敏感性分析真实可验证；三轮全量重抽的修订理由经归档复核**如实**；级联交付（交付表、limitations §7.5、progress、state）数字一致；fail-loud 声明属实（三轮 0 解析失败）。

主要保留：(a) r08 治疗类文献的方向判定在最终轮**仍未收敛**——抽查 3 篇 discordant 全部违反预注册两步判定协议（联网摘要确认），"两步协议收敛"表述偏乐观；(b) §12"先于任何文献验证运行落盘"对 round-1/2 **不可验证**（无 git 快照，文件 mtime 晚于前两轮运行），仅 round-3（唯一进入最终数字的轮次）可证协议先行；(c) 两处协议-实现文字差（human[filter] 缺失、"relevance 排序"实为默认近因序）未入偏离册。上述瑕疵对 headline 的影响有界：若 r08 的 8 篇 discordant 按协议重标为 concordant，precision_lit=17/18=0.944；若剔除 r08，16/17=0.941——结论方向均不变。

## 1–8 逐项验证表

| # | 验证项 | 状态 | 证据 |
|---|--------|------|------|
| 1 | 预注册纪律 | **部分通过** | §12 内容完整（五类判定阈值、检索协议、自引文排除、S1/S2/S3 定义、precision_lit+CP CI、定位声明，docs/analysis_plan.md L152-174）；三轮修订入册且理由经归档复核**全部属实**（见下）。时序：git HEAD（2026-10-12）不含 §12；analysis_plan.md mtime=01:42:50 **晚于** round1（01:24:53）/round2（01:41:44）运行、**早于** round3（02:00:48）。"先于任何运行"字面声明不可证 |
| 2 | 独立性 | **通过** | rule_citation_exclusion() 排除 per-rule ∪ 全局被引 PMID（比协议更严，scripts/literature_validation.py L94-110, L186）；citation_verification_report.json 含 23 个被引 PMID，抽查 r02=30209868、r08=23438873、r17=38684968、r12=17173974——**均不在 CSV 任何行**；全量交集 23∩750=∅，同规则违规 0；检索阶段实时排除自引文 6 条；pool_overlap 列存在，69 行=True（19 规则有分布） |
| 3 | 数据完整性 | **通过** | pubmed.json 21 规则全部 status=ok、共 750 kept（n_found 763 − 6 自引文 − 7 重复）；extracts.jsonl=750 行；round1/round2 归档各 750 行在盘（data/processed/）；CSV=750 行+表头；逐规则 n_searched 与 CSV 行数全等（复算表 OK×21） |
| 4 | 指标重算 | **通过** | 独立重算 21 规则 n_conc/n_disc/n_null/n_unclear/主判定/S1/S2 与 summary **零偏差**；precision_lit 重算 16/18=0.8889（summary 0.889）；CP CI 用 scipy beta.ppf 重算 [0.653, 0.986] 一致；负控 r01（mixed）已单列、不入 headline（20 主规则口径复算确认） |
| 5 | 判定质量抽查 | **不通过（局部）** | 12 篇抽查：3 篇 r08 discordant **违反两步判定协议**（治疗有效应判 concordant；PMID 41864488 经 PubMed 摘要确认为 resveratrol 保护性治疗研究）；1 篇 r17 concordant **偏宽**（PMID 34454934 摘要仅 NO2/CO/PM10↑、O3↓ 显著，**PM2.5 未报告**，严格应 unclear）；其余 8 篇符合协议。同轮同设计文献标注分裂（hesperetin=concordant vs resveratrol/aesculetin=discordant），§7.5 已如实披露。另核实 r12 唯一 discordant（PMID 41416118，MR：随餐饮酒 OR=0.67 保护 vs 规则"酒精↑风险"）判定**正确** |
| 6 | 敏感性 | **通过** | S1 剔除 69 篇 pool_overlap 后 **20/20 主判定不变**（21 规则含负控亦 0 变化）；S2 仅人群研究 **16/20 不变、4 条变化**（r05/r08/r14/r22 → uninformative），与 progress.json/limitations 记载一致（注：任务书"S2 16/20 变化"应为"16/20 不变"之笔误，以复算为准）；S3 复算 68/68=100% 一致 |
| 7 | 级联 | **通过** | performance_by_dataset.csv 末 2 行 Literature_PubMed：precision_lit 0.889 [0.653,0.986] n_cases=18、n_relevant_articles=750，与 summary 一致；limitations §7.5（L58 起）存在，precision_lit/S1=20/20/r08 三轮 0/10→2/16→11/8/S2 四规则名单均一致；progress.json phase5 note 有 R5.1 全套数字；state.json history 末条（2026-10-15）为 R5.1 条目，数字一致。微瑕：§7.5 行文"16/17 复证"与 headline 16/18 口径不一（疑为剔除 r08 后口径，未注明） |
| 8 | fail-loud | **通过** | 三轮 jsonl 及 CSV 中 direction='parse_fail' 行数=0，relevant=None 行数=0；三份抽取日志（extract/extract2/extract3.log）均记"750 new, 0 parse failures"；检索失败路径（3 次重试 + search_fail 状态、不静默补）在代码中实现（L126-135, L166-167），本轮 21 规则全部 ok 未触发 |

**三轮修订理由复核（第 1 项附属证据，独立从归档重算）**：

| 轮次 | §12 记载 | 归档重算 | 核实 |
|------|----------|----------|------|
| round1 | r08"10/12 discordant 全为抗氧化剂保护/治疗研究" | r08：0 conc/10 disc/1 null，10 篇 discordant 逐篇核（quercetin 纳米乳、kaempferol、curcumin、Grx、二氧化铈纳米酶、lutein 纳米粒、N-乙酰肌肽金纳米、resveratrol、树突状纳米凝胶、hesperetin 纳米悬液）全部为治疗/保护类 | **属实** |
| round2 | framing note 使 r07 mixed→replicated；r08 恶化 conc=2/disc=16 | r07：11 conc/1 disc→replicated；r08：2/16→mixed；日志 precision 0.944=17/18 吻合 | **属实** |
| round3 | 两步判定协议，全量重抽 | r07：7/4/6 mixed；r08：11/8/1 mixed；precision 0.889=16/18 吻合 | **属实**（但 r08 未真正收敛，见遗留问题 1） |

## 遗留问题（按严重度）

1. **[中] r08 治疗类文献方向判定最终轮仍不一致，"两步协议收敛"表述偏乐观。** 抽查 3 篇 r08 discordant（PMID 42193946/42636787/41864488）全部为"抗氧化制剂改善结局"类研究，按 §12 Round-3 预注册的两步协议（interventional 补充有效=concordant）应判 concordant，且同轮内同设计的 hesperetin（41765388）/curcumin（42650832）/kaempferol（42654113）确实被判 concordant——同一轮同一协议下同类文献判定分裂，说明 round-3 并未收敛（仅从 round-1 的 contradicted 移到 mixed）。该敏感性已在 §12/§7.5 如实披露，且影响有界（重标→17/18=0.944；剔除 r08→16/17=0.941，方向不变），故不推翻结论；但建议论文表述改为"两步协议使 r08 从 contradicted 移至 mixed，未完全收敛"。
2. **[中低] 预注册时序对 round-1/2 不可验证。** §12 标题声明"落盘——先于任何文献验证运行"，但 git HEAD（2026-10-12 15:17）不含 §12、工作区未提交，无任何版本快照；analysis_plan.md mtime（01:42:50）晚于 round-1 检索（01:10）/抽取（01:24:53）与 round-2（01:41:44）。可证实的是：round-3 协议（脚本两步 prompt 01:42:33 + §12 修订 01:42:50）先于 round-3 运行（02:00:48），而 round-3 是唯一进入最终交付的轮次；阈值五类三轮未变（round-1/2 可用同阈值复算出与日志一致的 16/18、17/18）。修订以入册方式透明登记而非回填掩盖，属善意；但"先于任何运行"字面声明目前无证据支撑。建议：预注册段落未来单独 commit 或附内容哈希时间戳。
3. **[低] §12.2 检索协议与实现有两处文字差，均未入 §0 偏离册。** (a) 协议写 `english[lang] AND human[filter]`，实际 21 条检索式 0/21 含 human[filter]（全文核对 pubmed.json query 字段）——机械/动物研究因此入池（与 §12 动机"覆盖所有研究类型"自洽，但与 §12.2 文字自相矛盾）；(b) 协议写"默认 relevance 排序"，esearch 调用未传 sort 参数（L163），PubMed 默认为近因序——750 篇中 2026 年 438 篇+2025 年 138 篇（合计 76.7%）证实为近因窗口而非相关性排序。§7.5"top-40 按 relevance 排序偏向近期治疗学文献"的归因表述应更正为"默认近因序截断"。
4. **[低] §12 Round-3 承诺"输出增 study_class 字段"未落盘。** prompt 确实要求 LLM 输出 study_class（L258），但 stage_extract 未持久化该字段：extracts.jsonl 与 CSV 均无此列（0/750）。两步判定的中间分类不可审计——这正是 r08 判定分裂难以定位的原因。建议补落盘或在 §12 注明"仅用于提示词内推理，不持久化"。
5. **[低] uninformative_lit 实现为"残余类"，超出 §12 字面定义。** §12 定义 uninformative=relevant 总数<2；但 r12（6 relevant，0 conc/1 disc/1 null）与 r19（4 relevant，1 conc/0/0）经脚本残余分支（L321）落入 uninformative。结果保守（不夸大复证）、方向正确，但字面协议未覆盖"relevant≥2 而各方向均<2"的情形，属预注册措辞缺口，应补记。
6. **[微] §7.5"16/17 复证"口径未注明**（headline 为 16/18；若为剔除 r08 后口径应加注）。

## 抽查 12 篇判定明细表

抽签种子 42，分组按任务书配额（r08 concordant/discordant 各 3、r02/r17 concordant 各 2、r12 uninformative 2）。协议依据：§12 Round-3 两步判定（etiological 反向措辞等价；interventional 补充有效=concordant、无效=null、恶化=discordant）；r02/r08/r12/r17 声明方向均为 risk_up（pubmed.json direction 字段）。

| # | 规则 | PMID | 年份 | 标题（截断） | CSV 判定 | study_type | note（截断） | 审计判定 | 依据 |
|---|------|------|------|--------------|----------|------------|--------------|----------|------|
| 1 | r08 低抗氧化×白内障 | 41765388 | 2026 | Instillation of Hesperetin Nanosuspensions Prevent Lens Opacification… | concordant | mechanistic | Antioxidant prevented cataract, supporting protective role | **符合** | interventional 补充有效→concordant，两步协议正确执行 |
| 2 | r08 | 42650832 | 2026 | Curcumin Nanoemulsion … Effect on Cataracts in Vivo/Ex Vivo | concordant | mechanistic | Curcumin reversed cataracts | **符合** | 同上 |
| 3 | r08 | 42654113 | 2026 | Kaempferol's Therapeutic Applications … Ocular Diseases | concordant | review_other | Kaempferol protects against diabetic cataract | **符合** | 同上（综述转述保护性证据） |
| 4 | r08 | 42193946 | 2026 | The Interplay Between Antioxidant and Chaperone Functions of α-Crystallin | discordant | review_other | Antioxidant function protects lens, opposing risk claim | **违反协议** | 保护性（内源性抗氧化功能）按两步协议应 concordant；且 α-crystallin 非"抗氧化摄入"，relevant=True 亦偏宽 |
| 5 | r08 | 42636787 | 2026 | Ocular topical aesculetin delivery via VA64/TPGS micelles… | discordant | mechanistic | Antioxidant treatment prevented cataract, contradicting claim | **违反协议** | 与 #1（hesperetin）同构之治疗预防研究，同轮同协议下判定分裂；note 自述"prevented cataract"却记"contradicting" |
| 6 | r08 | 41864488 | 2026 | Resveratrol protects lens epithelial cells and delays cataract… | discordant | mechanistic | Resveratrol delays cataract, contradicting claim | **违反协议（联网确认）** | PubMed 摘要核实为 resveratrol 抑制 TXNIP 延缓白内障的保护性治疗研究→应 concordant |
| 7 | r02 高血糖×白内障 | 42334146 | 2026 | Senp1 O-GlcNAcylation Promotes Mitochondrial Fragmentation… Diabetic Cataract | concordant | mechanistic | Hyperglycemia drives O-GlcNAcylation causing cataract | **符合** | 高血糖→白内障机制证据，方向一致 |
| 8 | r02 | 39580915 | 2025 | …mangiferin with aldose reductase… | concordant | mechanistic | Mechanistic link hyperglycemia-cataract via AR pathway | **符合（略宽）** | AR 通路=高血糖→糖性白内障经典机制；研究本身偏治疗配体，判 concordant 可接受 |
| 9 | r17 PM2.5×早期 AMD | 41850516 | 2026 | Cellular responses of human Muller glia exposed to test dust pollution | concordant | mechanistic | ATD increased ROS, disrupted antioxidant mechanisms | **符合** | 颗粒物→视网膜胶质细胞氧化应激，方向一致 |
| 10 | r17 | 34454934 | 2022 | Long-term exposure to ambient air pollutants and AMD（KNHANES 15,115 人） | concordant | cross_sectional | NO2, CO, PM10 associated with higher AMD prevalence | **偏宽（联网确认）** | PubMed 摘要全文：显著者为 NO2/CO/PM10↑与 O3↓，**PM2.5 未报告任何关联**；note 如实记录却仍判 concordant，严格应 unclear（空气污染混合物层面弱支持） |
| 11 | r12 饮酒×白内障 | 41783692 | 2026 | Healthy Dietary Patterns and Risk of Major Eye Diseases | unclear | cross_sectional | Alcohol only mentioned as subgroup modifier | **符合** | 非主暴露→unclear 合理（判 relevant=False 亦可，均不改判定） |
| 12 | r12 | 37792333 | 2023 | Is Occasional Alcohol Drinking and Smoking Related to … Cataract? | unclear | cohort | No abstract provided to determine direction | **符合** | 记录无摘要，fail-safe 判 unclear 而非臆断，符合协议 |

**抽查小结**：12 篇中 8 篇符合协议、1 篇略宽（#8）、1 篇偏宽（#10，PM2.5 特异性缺失）、3 篇违反两步判定协议（#4/#5/#6，全部集中在 r08 discordant 侧）。方向判定错误：**确认 3 篇（均为 r08 discordant 误标，其中 1 篇经联网摘要确认、2 篇经标题+note 同构比对确认）+ 1 篇偏宽（r17 34454934）**。错误集中模式与 §7.5 披露的"抽取层对治疗类文献敏感"一致；对 r08 之外规则未见方向反转。附加核实 r12 discordant（41416118，MR 随餐饮酒 OR=0.67 保护）判定正确。

## 附：重算方法说明

- 逐规则计数与判定：直接从 literature_validation_R5.csv（utf-8-sig，750 行）按 §12 阈值重写 verdict() 复算；relevant/pool_overlap 布尔列按字符串 "True"/"False" 还原。
- CP CI：scipy.stats.beta.ppf(0.025, 16, 3) / beta.ppf(0.975, 17, 2) → [0.653, 0.986]。
- S1：剔除 pool_overlap=True（69 行）后重判；S2：仅保留 study_type∈{RCT, cohort, case_control, cross_sectional, meta_systematic} 重判；S3：second_pass_direction 与 direction 逐行比对（68 对）。
- 独立性：citation_verification_report.json 23 个被引 PMID 与 CSV 750 个 PMID 求交。
- 联网核对：NCBI E-utilities efetch（只读），PMID 34454934 / 41864488 / 41416118。
