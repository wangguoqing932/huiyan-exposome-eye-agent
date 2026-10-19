# R1 · NEJM 视角审稿意见（立意 / 结论-数据匹配）

**稿件**：Pooling conceals directional conflict: a pre-registered cross-cohort evaluation of 21 literature-derived exposome rules for major eye disease in 2.0 million person-waves
**目标期刊**：Ophthalmology（按作者设定审阅，标准按 NEJM 层级把关）
**审阅范围**：manuscript.md + sections/*（abstract/introduction/methods/results/discussion）+ table1–7 + figure contracts + docs/analysis_plan.md（含 §0 全部更正记录、§19 队列层预注册）+ outputs/cohorts/*（cohort_rule_results.csv、cohort_transportability.json、cohort_heterogeneity.json、cohort_power.csv、evidence_audit.json）+ docs/cohort_variable_mapping.md（C1–C69）。
**审阅人立场**：只问两件事——这篇稿子值不值得存在；结论配不配得上数据。

---

## 总体评价

作者做了一件真功夫：用 SHARE/HRS/ELSA/KLoSA/LASI/MHAS/CLHLS/CRELES 的**原始文件**（拒绝 Gateway harmonized、easySHARE、RAND Fat File）重建队列层，并留下了一份比论文本身更诚实、更详细的变量操作化台账（C1–C69，含五类同源错误的三次以上复发记录）——这份台账是本文最硬的资产。但论文的两处核心主张与数据之间存在结构性错配。第一，"可迁移性不能靠数复现队列数建立"这个结论，**不是被预注册判据推翻的，而是被一个事后追加的 I² < 75% 阈值推翻的**（§19.7 预注册判据里没有任何异质性条件）；用事后判据否定预注册判据，同时把预注册判据称为"primary"，逻辑上不能同时成立。第二，"pooling 掩盖方向冲突"这一标题级主张，全部重量压在一个规则（r10 吸烟×白内障）上，而这个规则的"方向冲突"实际由**单一队列 CLHLS** 拉动，且 CLHLS 在该规则上用的是 1.29% 自报糖尿病/功能测试视力一类与其余队列**不可通约的操作化**。与此同时，稿件最该披露的三件事——规则文本在确证运行之后被改过（test-set fitting，§0 已自认）、r02 的暴露被替换为自报糖尿病（与 §18 自己讲的"必须用 HbA1c/血糖"相矛盾）、完整病例限制导致 HRS 丢掉 51% 的年龄、ELSA/HRS 丢掉 20%/51% 的性别——在正文里全部缺席。**投票：大修（Major revision）**；若作者拒绝按"绝对值异质性"重写核心结论、拒绝补报操作化替换与完整病例损耗，则应转拒稿——因为那时的卖点会变成"把已知的 meta 分析常识包装成新发现"。

---

## 立意判定

**"So what"的答案目前答不上来。** 试着回答"这项研究改变哪条临床决策"：没有一条。r02（糖尿病×白内障）、r20（吸烟×视力损害）都是临床与流行病学教科书级关联，本文的作用是确认它们"大概是对的、但幅度跨人群不稳"；16/21 条规则在八个队列里根本测不了，也不改变任何决策——它改变的是**资助方和队列设计者该加什么测量**。这是有价值的，但它是"研究基础设施评论"，不是临床研究。

再往下一层：这个层级期刊会追问"新在哪"。文献层早就知道吸烟×白内障存在跨人群异质性（IOVS 2012 的吸烟-白内障 meta 分析本身就报告了显著异质性与地区间差异；抗氧化剂/饮食类规则的"保护/无效"混合结果同样是既有共识）。作者的贡献因此只能是方法学的——"用预测区间代替合并值、不要把复现计数当可迁移性"。这个提醒本身正确，但它是 meta 分析领域二十年前就确立的常识（异质性 + 预测区间优于合并 OR），本文只是把它搬到一个眼科规则库上做了一次演示，并且**在演示中自己用错了工具**（用 I² 做否决策，而 I² 对绝对异质性不敏感、k=2 时几乎无意义）。

立意的真实成色：**一个中等强度的、方法学导向的"阴性资源审计"**。它可以存在于这个领域，但当前包装成"pooling conceals directional conflict"的标题级发现是超配的。对 Ophthalmology，我倾向于"值得发、但要换一个诚实的题目和结论层级"；对 NEJM 层级，它的临床重量不足，方法学重量又被自己用错误的异质性判据削弱了。

另有一个未被论文处理的定位问题：本文实际是**两个项目被缝在一篇稿子里**——一套暴露组规则推荐系统（含 F1、架构、演示案例、四视图输出）与一次队列层外部验证。系统那半与本文的队列结论在逻辑上互不依赖（Results §"System performance" 与 3.8 节整段可以整体删除而不损失任何一条队列层结论），却占据了最容易被读成"这是 AI 论文"的位置。撤稿级风险不在这里，但审稿人一定会问："你到底是验证规则，还是推销系统？"

---

## 结论-数据匹配审查（逐句对照）

**① 摘要 Conclusions（abstract.md §Conclusions，manuscript 40–43）**："Transportability could not be established by counting replications, and pooling concealed a directional conflict rather than resolving it."
- 数据支撑度：**部分**。前半句真实但归因错误——预注册判据（≥2 队列 replicated，§19.7）确实把 r02/r20 判为 transportable，推翻它的是事后追加的"PI 排除 null 且 I²<75%"（results.md 113–118 / manuscript 394–399），而该阈值在 §19 预注册文本中**不存在**。因此这句话的准确版本是"我们的预注册判据被我们自己在看到数据后换了"。后半句由单规则 r10 承担，而 r10 的负向结论 3/4 来自非显著队列（ELSA 0.77、CRELES 0.70，均 uninformative），仅 CLHLS 显著（0.748）——用三个方向一致、两个不显著的估计去论证"方向冲突"，是把"方向一致但幅度不同 + 一个异常队列"说成"冲突"。

**② 摘要 Results（abstract.md 28–31；manuscript 35–37）**："its pooled estimate was null (0.84, 0.67–1.05) while regional subgroups differed (p < 0.0001) — a summary describing no population studied."
- 数据支撑度：**不成立**。pooled 0.84 落在 CLHLS 0.748、ELSA 0.7675、CRELES 0.7023 三者之间且几乎重合——它**准确描述了 4 个队列中的 3 个**（cohort_heterogeneity.json:88–91）。真正没被描述的是 SHARE（1.109），唯一与 pooled 反向的队列。另外"regional subgroups differed (p<0.0001)"的分组是 Americas = CRELES 一个队列、Asia = CLHLS 一个队列、Europe = SHARE+ELSA（cohort_heterogeneity.json:95–107），**两个"区域"各只含一个队列**，把 Q_between 的自由度 2 说成"regional difference"是把队列效应改名为地区效应。

**③ 讨论首段（discussion.md 8–14；manuscript 496–502）**："Under a criterion that also requires the between-cohort heterogeneity to be tolerable, none did."
- 数据支撑度：**依赖未披露的事后阈值**。"tolerable"= I²<75%，而观测值为 79.5/79.5/90.5/91.0/93.8——阈值刚好卡在所有观测值之下。任何设在 75–79.5 之间的常数都能得到同一结论，这一点必须写明，否则读者会以为阈值来自领域共识。（补充：r12/r13 的 k=2，I² 与 Q p 在 k=2 时是几乎无信息的统计量，把它们的 79.5% 计入"每一条多队列规则都是极端异质性"是统计上的过度解读。）

**④ 讨论 §"The direction reversal"（discussion.md 42–54）**："This explanation predicts that the protective direction should strengthen with increasing cohort age. It does not: the meta-regression slope on mean age was −0.008 log-OR per year (p = 0.52)."
- 数据支撑度：**技术上成立，逻辑上有漏洞**。队列均值年龄的 meta 回归（k=4，年龄跨度 57.9–92.0）对**个体层面**的年龄混杂几乎没有检验力；用一个 4 点回归的 null 结果去"否证"个体层面年龄混杂，是生态学谬误的镜像。若 HRS r20 的 OR 1.61 中有相当部分来自"重度视力损害者更年长、更年长者更多是现吸烟者"，那么主结论 r20 的幅度也被同一机制污染——论文**只在讨论反转时提出年龄混杂，却从未把它作为主结果的威胁来量化**（例如细年龄分层、年龄×吸烟交互、或把 age 换成年龄组/样条）。

**⑤ 结果 §"Between-cohort heterogeneity"末段（results.md 120–131；manuscript 401–412）**："Cohort mean age did not explain the heterogeneity (p = 0.42–0.52)"（摘要同句）
- 数据支撑度：**与自己的数据不符**。三条规则的 p 实际为 0.418、0.517、**0.347**（cohort_heterogeneity.json:56/112/272）。摘要把 r20 的 0.347 排除在区间外，使数值区间看起来更整齐。同时"由队列均值年龄解释异质性"这个原命题本身就不是正确的混杂检验对象，删掉或改写为"队列层面年龄差异不支持年龄构成解释（低检验力）"更合适。

**⑥ 讨论 §"A criterion that was too permissive"（discussion.md 106–121）**："which is a weaker claim than the pre-registered criterion supports and a stronger one than a naive reading of the replication counts would suggest."
- 数据支撑度：**自我矛盾**。"weaker than pre-registered supports"承认预注册判据说 2 条可迁移，"stronger than naive counts"说计数过于宽松；两句并存等于承认"结论随判据变"。审稿人会直接问：既然两个判据给出相反的 headline，为什么不把二者都当作**并列结果**（预注册判据为主，异质性判据为敏感性），而要用事后判据覆盖预注册判据？

**⑦ 讨论 §"Measurement as the limiting factor"（discussion.md 123–137）**："Fundus imaging is the single highest-value addition, unlocking 15 further cells."
- 数据支撑度：**可追，但被重复计数放大**。evidence_audit.json:14 的 OUTCOME:fundus_imaging = 15，但同表另有 OUTCOME:fundus_imaging_or_grading = 5（与前者高度重叠、属包含关系），Table 7 逐项相加为 63 个解锁单元，而不可行单元总数只有 150（一个单元可被多个模态同时解锁）。把"边际价值排序"当投资排序给出，未披露重叠，会误导读者把它读成"加眼底影像能多测 15 条规则"（实际是多解锁 15 个 rule×cohort 单元，且部分单元同时也被其他模态解锁）。

**⑧ 结果 §"What the evidence base cannot test"（results.md 52–56；manuscript 333–338）**："Fifteen were not testable in any cohort: five require fundus imaging (r03, r04, r07, r19, r22), one requires tonometry or optic-disc grading (r16), three require geocoded exposure (r17, r18, r21), three require blood assays (r01, r06, r14) and two require dietary indices (r08, r09); r05 requires a lipid panel."
- 数据支撑度：**算术不成立**。该枚举 5+1+3+3+2+1 = **15**，但表内含 **16** 个不同规则（r01,r03,r04,r06,r07,r08,r09,r14,r16,r17,r18,r19,r21,r22,r05 共 15 个；再加上由 r16 承担的"tonometry"分类本身即重复计入 r16）。核对 §19.6 预注册表，r07 同时列在"需眼底影像"与"需血液指标"，r19 同时列在"需眼底影像"与"需膳食指数"。因此"15 条不可测"与"5 条需眼底影像"两个表述至少有一个是错的。同一稿内 Figure 8 图例写"13 rules have no bar"（21−6=15，figure8 yaml 第 199 行、manuscript 807），Table 7 写"the two glaucoma-measurement rules (r16)"（只有一条，manuscript 1102），三处互不一致。

**⑨ 结果 §"Cross-cohort transportability"（results.md 79–83；manuscript 360–364）**："its interval (0.86, 0.55–1.34) excludes associations of that size, so it is a powered null rather than an absence of evidence."
- 数据支撑度：**措辞与自己的表述纪律冲突**。OR=0.86（<1）而规则方向为 risk_up，这是**与声明方向相反的**估计，把它称为 powered null 掩盖了方向信息。另外效力口径用 MDE ≤ 2.0 记 powered_null（§17），MDE 1.70 刚过 2.0 阈值以内，所以"排除 1.7 倍"实际是"设计能排除 1.7 倍"，而吸烟×AMD 的文献效应量通常远小于 1.7——这正是"powered null"标签最容易被误读的地方。

**⑩ 结果 §"Exploratory associations"（results.md 160–168；manuscript 439–449）**："All three point the same way as r20 and are consistent with a metabolic and smoking-related contribution to vision loss; none is offered as a confirmed finding."
- 数据支撑度：**可以，但遗漏了必要的限定**。这三个探索性结果用的是同一 survey 数据、同一自报结局、且与 r20 共享暴露与人群；HRS 的"现吸 × 重度视力损害 OR 1.98"与主分析 r20 的 HRS 估计（1.61，结局为 moderate）出自同一批 13,511–28,654 条记录。把它们作为"与 r20 一致的佐证"列出，会让读者误以为这是独立信号。至少应写明这三条与 r20 完全重叠于同一数据，不构成独立复现。

**⑪ 讨论 Constraints（discussion.md 152–161；manuscript 640–649）**："The eight cohorts are independent of each other and of the NHANES, KNHANES and CHARLS layers: no participant appears in more than one, and no cohort contributed to rule construction."
- 数据支撑度：**字面可辩，实质误导**（详见下节专条）。另有一处更硬的问题被漏掉：**NHANES 不是"internal validation"**。analysis_plan §0（2026-10-12）自己记录：确证运行（2026-10-11）之后、基线运行之前，规则集被修改（r02/r03/r04 交叉覆盖 + 新增 r22），性质被自己定性为 test-set fitting。也就是说，规则是在看过 NHANES 结果之后改的，因此 NHANES 层的 6/16 复证（precision 1.00）**既不是内部验证、也不是外部验证，而是拟合并入**。正文 Methods（manuscript 133–143）只说"四层"，完全没有把这条时间线写进去——这比任何一处统计细节都更影响读者对"预注册"的信任。

---

## 致命 / 重大 / 次要 / 需澄清

### 致命（Fatal）

**F-1｜核心结论所依赖的"可迁移性判据"是事后追加的，且与预注册判据直接冲突。**
- 位置：Results §"Between-cohort heterogeneity"末段（results.md 110–118；manuscript 391–399）；Discussion §"A criterion that was too permissive"（discussion.md 106–121）；Abstract Results 末句；analysis_plan §19.7（预注册文本，570–572 行）。
- 问题：§19.7 预先声明"某规则在 ≥2 个队列中同向且 q<0.05 记 transportable"，**没有任何异质性条款**。稿件却在看到数据后以"prediction interval excluding the null 且 I² < 75%"宣布"none of the six testable rules was reliably transportable"，并把这一结论写进摘要与全文结论。
- 为什么是问题：这是本稿唯一的方法学卖点。若结论可以靠事后阈值产生，那么"预注册"在整个论证中就只剩装饰作用；而 75% 这个数恰好落在观测值 79.5% 之下，任何 76–79% 的常数都能复制同一结论——读者无法判断这是领域标准还是拟合出来的门槛。这正是项目自己在 §0 里反复声讨的 test-set fitting，只是从规则集转移到了判据上。
- 建议：三选一，必须做。(a) 恢复预注册判据为唯一 primary，把异质性判据明确标注为 **post hoc sensitivity**，摘要改写为"预注册判据判定 2/6 条可迁移；事后异质性敏感性分析提示该判据不能区分'方向一致但幅度不稳'的情形"；(b) 或新判据改为**事先可辩护的量**——τ² 的绝对阈值或以 OR 尺度表述的临床阈值，例如"预测区间上界 < 1.0 或下界 > 1.25"，并说明为何选它；(c) 至少补一句："The I²<75% threshold was chosen after observing I²≥79.5% in all multi-cohort rules; it is not pre-registered."

**F-2｜规则文本在确证运行之后被修改，NHANES 层因此不是验证层；正文未披露。**
- 位置：analysis_plan §0（8–31 行）；manuscript Methods §"Reporting and study design"（133–143）与 Results §"The internal layers"（296–311）。
- 问题：§0 明确记载 2026-10-11 确证运行 → 2026-10-12 07:12 修改规则（r02/r03/r04 交叉覆盖 + 新增 r22）→ 07:13 基线运行，并自认"R=1.000 是构造的，不是性能提升"。正文把 NHANES 写作 internal validation、KNHANES/CHARLS 写作 external validation，全文不含这条时间线。
- 为什么是问题：这是 Methods 完整性与"预注册"可信度的硬约束。TRIPOD+AI 声明在稿中，却没有报告这一偏离。审稿人一旦发现 analysis_plan 里写着"测试集拟合"，会连带怀疑其余所有"预注册"表述。
- 建议：Methods 增一段并可直用："The rule set was revised after the first confirmatory run (analysis_plan §0); three rules had flags expanded and one rule (r22) was added. NHANES results therefore reflect partial test-set fitting and are reported as a development-adjacent layer, not as internal validation. All cohort-layer analyses used the v1.2 rule set frozen on 2026-10-12, before the cohort layer was run."

**F-3｜r02 的"高血糖"在所有四个队列里都是自报糖尿病——操作化替换未披露，且与作者自己 §18 的结论矛盾。**
- 位置：Results §"Cross-cohort transportability"（results.md 60–62，manuscript 341–344）；摘要 Results（abstract.md 24）；Table 6 第 1 行（exposure_prevalence 0.0129）；cohort_rule_results.csv 第 2 行（`exposure=diabetes`）；scripts/cohort_confirmatory.py:73–74（`"hyperglycemia": ["diabetes"], "hba1c_elevated": ["diabetes"]`）；对照 analysis_plan §18 运行结果（428–437 行）。
- 问题：规则 r02 的暴露 flag 是 `hyperglycemia`（NHANES 层定义为 FPG≥126 或 DIQ010==1，见 scripts/evaluate.py:141）。队列层没有血糖测量，于是四个队列全部用自报糖尿病替代；`hba1c_elevated` 甚至也被映射到同一变量（cohort_rule_coverage.py:52 注释"no HbA1c in the cohort files"）。四个队列的暴露定义因此不同质：CLHLS 是"医生是否告知糖尿病"（1.29%，C64 自认这是自报 vs 测量口径差异且糖尿病自报率仅 1.36%，远低于中国同龄人群），CRELES/LASI/SHARE 各为自报 19.1%/12.1%/13.6%。而 §18 恰恰刚得出"A 级规则 r13 在二分类下无效是切点所致""吸烟的无效在血清可替宁下依然成立"——作者自己在队列层项目里主张"必须用测量值而非自报值"，转头在 r02 上把自报值当测量值用，并且这是全文两条"可迁移"规则之一。
- 为什么是问题：把"自报糖尿病 × 自报白内障"包装成"高血糖 → 白内障"是本稿最大的内部不一致。它同时(a) 使 pooled OR 1.95 变成一个跨四种不同暴露构念的加权平均，异质性有相当部分来自操作化而非人群；(b) 与论文的收尾论点"limiting factor is measurement"形成直接反证——在没有测量时，作者选择了替代而不是报告"不可测"，而这恰恰是 §19.6 对 r01/r06/r14 采用的纪律。
- 建议：二选一并写进摘要级披露。**推荐**：把 r02 重命名为"self-reported diabetes → self-reported cataract"，在 Results 与 Table 6 中显式标出四队列暴露定义，并在 Limitations 增句："r02 was operationalised as self-reported physician-diagnosed diabetes in all four cohorts because no cohort in this layer measured glucose or HbA1c; it is therefore not a test of the hyperglycaemia rule as specified in Table 2, and its pooled estimate averages four different exposure constructs." 随后把"measurement is the limiting factor"的结论改为支持该披露的版本（这反而更强）。**次选**：按 §19.6 的"不可测"纪律把 r02 移出本层。

### 重大（Major）

**M-1｜"pooling conceals a directional conflict"是单规则、单队列驱动的结论，标题级别过高。**
- 位置：标题（manuscript 1）；摘要 Background/Conclusions；Discussion §"Principal findings"第二条（discussion.md 16–23）。
- 问题：18 个确认性配对中只有 r10 存在符号对立，且其反向侧（ELSA 0.7675、CRELES 0.7023）在 q 上均为 uninformative；显著的反向仅 CLHLS 一处。同时 pooled 0.84 描述了三/四个队列。
- 为什么是问题：既然是标题，就必须是**规则库级的规律**而非一个规则的轶事。目前证据强度只支持"在一个规则上观察到方向不一致，且它由单一队列贡献"。
- 建议：标题改为不含"conceals"的表述，例如 **"Directional disagreement in one of six testable exposome rules: a pre-registered cross-cohort evaluation of 21 literature-derived rules in eight ageing cohorts"**；Discussion 第二条改为："In one rule (smoking × cataract) the four cohort estimates did not share a sign; three of the four were protective and only one was statistically significant in that direction. The pooled estimate (0.84) coincided with three of the four cohort estimates, so the failure here is not that pooling produced a number no cohort shares, but that pooling produced a number that cannot be applied to the one cohort with the opposite sign."

**M-2｜异质性用 I² 裁决，而 I² 的绝对异质性其实很小；τ² 与真实尺度差异被隐去。**
- 位置：Table 5（outputs/tables/table5_heterogeneity.md）；Discussion §"Why the pooled estimate is the wrong summary here"（discussion.md 91–99）。
- 问题：cohort_heterogeneity.json 给出 τ² = 0.0381（r20）、0.0421（r10）、0.1487（r02）。换算到 OR 尺度，典型的跨队列倍率差异约为 1.04–1.16——即在临床上是**接近可忽略的绝对异质性**。论文却用 90–94% 的 I² 与"extreme between-cohort heterogeneity""pooling conceals"的语言描述它。
- 为什么是问题：I² 是异质性与抽样精度的比值；SHARE 有 71 万条记录使 SE 极小，于是任何微小的真实差异都会把 I² 推到 90%+。以 I² 作否决策，等于"样本量越大越不可迁移"——这会把结论变成一个样本量惩罚项，且正是作者批评别处"只看复现计数"时同一类工具误用。同时，若作者真的主张异质性不可接受，就应给出 τ² 的临床解读（例如"新队列的 OR 有 95% 概率落在 0.81–1.89"已经足够，不必靠 I²）。
- 建议：把主判据改为**临床尺度的预测区间**（已有），把 I² 降为辅助描述，并在正文加一句："On the log-OR scale τ was 0.20–0.39; expressed as a ratio of odds ratios between cohorts, the typical difference is about 1.04–1.16. The I² values above 90% reflect the very small within-cohort standard errors of SHARE rather than clinically large disagreement." 这句话会让本文的方法学主张更站得住，而且不会削弱原有提醒。

**M-3｜"regional difference"实际是单队列对比，区域分组与队列身份完全混杂。**
- 位置：Table 5 末列"Regional p"；Results（results.md 106–108，manuscript 387–390）；Discussion 第二条（discussion.md 19–20）。
- 问题：cohort_heterogeneity.json 显示分组为（r10）Americas={CRELES}、Asia={CLHLS}、Europe={SHARE,ELSA}；（r20）Americas={HRS}、Asia={KLoSA,CLHLS}、Europe={SHARE,ELSA}；（r12）Asia={CLHLS}、Europe={SHARE}；（r13）Americas={CRELES}、Europe={SHARE}。即在 r10、r13、r12 中每个"区域"各只含一个队列，Table 5 的"Regional p"因此等于队列间检验（r12/r13 上与 Q p 数值完全相同：0.0273/0.0272），而非区域效应。
- 为什么是问题：读者会把"区域差异"理解为地理/人群层面的发现，从而接受"Europe 1.08 vs Asia 0.75 vs Americas 0.70"这类表述；实际它是"CLHLS 与其他队列不同"。这是把 cohort effect 改名成 region effect。
- 建议：Table 5 该列改名为"between-cohort subgroup p (groups: region; see footnote)"并加脚注："For r10 and r20 the Americas subgroup contains one cohort (CRELES) and the Asia subgroup contains one (r10) or two (r20) cohorts; the subgroup test is therefore not separable from cohort identity." 正文删去"the single positive cohort is European while all three protective cohorts are not"这类地理化表述，改为直接指名队列。

**M-4｜完整病例限制造成的大规模选择性损耗完全未报告（HRS 年龄缺 51.3%、ELSA/HRS 性别缺 19.8%/51.3%）。**
- 位置：Methods §"Statistical analysis"（manuscript 242–248，仅写"age and sex as covariates"）；Table 6 的 n 列。
- 问题：独立复算文件（outputs/review/recalc/recalc_datahealth.csv:2–9）显示：HRS age_missing_pct = 51.31、sex_missing_pct = 51.31；ELSA age_missing 20.49、sex_missing 19.83；MHAS 80.67（无参赛配对）；CLHLS age 7.26。这一损耗直接体现在分析样本上：HRS 全层仅 28,654 条参与 r20（占 42,946 的 67%），ELSA r20 仅 4,546（占 9,771 的 47%），ELSA r10 仅 4,050。
- 为什么是问题：年龄与性别是**仅有的两个协变量**，它们的缺失不是协变量问题而是分析样本定义问题；这是选择偏倚，论文自己的 Limitations 只写了"self-report under-ascertainment"，完全没写这一条。而 HRS 的年龄来自 `PA019`（scripts/build_cohort_frames.py:402，2016 波个体级文件），其覆盖本就有限，正文却未说明。
- 建议：Methods 加一句披露，并在 Table 6 增列"analysis n / frame n"："Age (HRS PA019, 2016 wave) and sex were missing for 51.3% of HRS person-waves and about 20% of ELSA person-waves; the regressions are therefore restricted to those with complete covariates. For HRS this halves the contributing sample. Because missingness is unlikely to be independent of the exposures, the cohort estimates are subject to selection bias of unknown size." 至少在 Limitations 增一条 Selection。

**M-5｜"Independence achieved"的限制段落，对"不独立于产生规则的文献"这一点仍然不够诚实。**
- 位置：Discussion §Limitations 第一条（discussion.md 152–161；manuscript 640–649）。**这是审稿清单第 3 条特别要求核查的声明。**
- 问题：作者写了"not independent of the literature from which the rules were derived"，这句话本身已经比多数稿件诚实——但它被放在段落后半，前半句"no participant appears in more than one, and no cohort contributed to rule construction"给读者的是**独立性的印象**，后半句的限定则被写成一个"严格意义上的措辞问题"。实际后果远比措辞严重：21 条规则中大量条目（糖尿病-白内障、吸烟-白内障、吸烟-视力损害、BMI-白内障）本身就来自包括 SHARE/HRS 在内的这些队列所在人群的文献；当一条规则是"从队列 A 的文献里总结出来、再在队列 A 里检验"时，那不是外部验证，而是**同一证据体的自我回归**。更关键的是，作者用来"减轻"这一点的措施（用原始文件而非 harmonized）**在逻辑上不能减轻它**——操作化方式是否来自第三方，与规则与被检验人群是否共享文献来源，是两个不相关的维度。把它写成 mitigation 是不成立的。
- 为什么是问题：这是本稿最根本的效力边界，决定读者能否把"replicated"读成"在新人群中成立"。目前段落的写法会让读者低估它。此外，§12 的文献层验证（precision_lit 0.889）也面对同一循环——它的检索排除了规则自身引文，但不可用原始数据集里同样的人也不是"独立"的（§12 自己承认证据池重叠只标记不剔除）。
- 建议：改写为独立的一段，放在 Limitations 之首，并直说结论边界（可直接使用）：
  > **Independence, and its limit.** The eight cohorts share no participants with each other or with the NHANES, KNHANES and CHARLS layers, and the rule set was frozen before the cohort layer was run. They are not, however, independent of the literature that generated the rules, and several of the six testable rules concern exposures and outcomes whose published evidence derives in part from these same populations. For such rules, replication here is not out-of-sample in the strict sense: it is an association re-estimated in the population that helped generate it. Using raw rather than harmonised files removes another team's operationalisation but does nothing to remove this shared evidential origin. The layer should therefore be read as a test of **whether the magnitude is stable across populations**, not as an independent confirmation that the association exists.

**M-6｜Table 2 不携带任何规则来源，读者无法核验"literature-derived"。**
- 位置：Table 2（manuscript 979–1003）；Methods §"The rule base"（145–153）。
- 问题：21 条规则的证据基础、每条规则对应的文献/效应量区间、以及单条规则下"证据强度 A/B/C 如何判定"全部不可见。§19.7 与 §0.1-更正 1 显示 r22 的引文曾被替换（原引文是 BMI×白内障 meta，与她自己的 r13 同源），这说明规则-引文对应关系本身是本项目的高风险环节。稿件还把 `low_antioxidant_intake`、`mediterranean_diet`、`pro_inflammatory_diet` 这三个 dietary 规则标为 B 级，但队列层里它们"unbuildable"——读者最想知道的正是"B 级"的判据是什么。
- 建议：Table 2 增列"evidence anchor"（每条 rule 1–2 条代表性文献的 DOI/PMID + 该文献的效应量方向与量级），并加一列"testable in cohort layer (Y/N, reason)"。这同时能让 M-1/F-3 的讨论落在证据上，而不是落在规则编号上。

**M-7｜不可测规则的原因分类在规则层与单元层之间不自洽，计数无法核对。**
- 位置：Results（results.md 52–56；manuscript 333–338）；Table 7 末段（manuscript 1102）；Figure 8 图例/契约（manuscript 807；figure8_cohort_transportability.yaml:74、199）；analysis_plan §19.6 原因表（537–546）。
- 问题：正文枚举为 5+1+3+3+2+1 = 15（恰为 21−6，总数对得上），但其中 **r07 同时出现在"需眼底影像"与"需血液指标"，r19 同时出现在"需眼底影像"与"需膳食指数"**（analysis_plan §19.6 同样如此），于是"五条需眼底影像"这一句在规则层只成立三条专属（r03/r04/r22）。同时 r08（低抗氧化物摄入）、r09（地中海饮食）、r22（BMI）在稿件枚举里被写成"需膳食指数"或"需眼底影像"，但项目自己的台账 configs/variable_map.yaml:506–533 给出的原因完全不同：r08 与 r09 是 **not_yet_built**（指数权重与切点尚未预注册——即"本可以测但没做"），r19 亦为 not_yet_built，r22 是数据驱动的探索性扩展。把"未构建"写成"需膳食指数（不可得）"，是把可补的工程缺口与不可补的数据缺口合并叙述。
- 为什么是问题：Table 7 与 Figure 8 是"measurement 是瓶颈"这一结论的唯一证据载体。计数（15 vs 13 vs "two (r16)"）与原因归属（不可得 vs 未构建）都核对不上时，10.7% 这个比例与投资排序的可信度会被一并质疑。
- 建议：(a) 在增补材料给出规则级 21 行清单，每行**一个**主因（不可得/未构建分开标注），并在正文、Table 7、Figure 8 三处引用同一份清单；(b) 把 not_yet_built 的 r08/r09/r19 单列一组，并在 Limitations 写明"这三条在当前数据下可测但指数尚未预注册，属工程缺口而非数据缺口"；(c) 删除 Table 7 的复数笔误"the two glaucoma-measurement rules (r16)"。

**M-8｜r11 的"powered null"标签与本层的判读纪律不一致，且 MDE≤2.0 的阈值偏宽。**
- 位置：Results（results.md 79–83）；Discussion §Limitations "Power"（discussion.md 173–176）。
- 问题：OR 0.86（0.55–1.34）方向与规则相反，却记作 powered null；同时 §17 把 powered_null 定义为 MDE ≤ 2.0，而本层最关心的效应量级是 1.1–1.3，用 2.0 作"有信息量的阴性"门槛会系统性高估阴性结果的可解释性（Table 6 中 CRELES r02 的 MDE 1.23、observed 1.31 被记 underpowered，逻辑自洽；但阈值本身值得质疑）。
- 建议：（a）把方向相反但未达显著的估计单列一态或在表中以符号标出"opposite direction, not significant"，不要把 0.86 写成 powered null；（b）把"powered null"的阈值改为与规则声明效应量挂钩（如"CI 排除 1.5"或"CI 排除该规则文献效应的下限"），并在 §17/Table 6 中统一。

### 次要（Minor）

- **N-1｜数字与 Table 5 不一致**：r02 pooled CI 正文 1.33–2.88（abstract.md 24、results.md 100）vs Table 5 与 JSON 的 1.32–2.88；r13 pooled 正文 1.14（results.md 104）vs Table 5/JSON 1.13。建议全部改为从 cohort_heterogeneity.json 直出。
- **N-2｜摘要的年龄 p 区间过窄**：见 §结论-数据匹配 ⑤，改为"p = 0.35–0.52"。
- **N-3｜摘要缺样本量**：Methods 里有 2.0 million person-wave，Results/Conclusions 没有任何队列规模或人群数。Ophthalmology 要求摘要内含研究规模。建议在 Methods 句末补"（≈280,000 unique participants）"并说明 person-wave 与参与者的区别（见 N-4）。
- **N-4｜"2.0 million person-wave records"是表述性夸大**：1,693,515/2,036,518 = 83% 来自 SHARE，其独立参与者仅 137,183；全层独立参与者约 28 万。而 variance 按人聚类（Methods 242–248 已声明）。建议标题与摘要改写为"2.0 million person-wave records from ≈280,000 participants（SHARE contributes 83% of person-waves）"，以免读者把 person-wave 当独立样本。
- **N-5｜"four waves of increasing independence"是修辞**：development/NHANES/KNHANES/CHARLS 并非彼此独立（规则经 NHANES 后修改，见 F-2）。建议改为"four evaluation layers"，并在 F-2 段落说明其非独立性。
- **N-6｜去掉与队列结论无关的系统性能半篇**：Results §"System performance"（results.md 195–204）与 Figure 4/5 及示例图例，与本文任何一条队列层结论都不发生关系；且 outputs/review/FATAL_blank_figures.md 记录 Figure 1/4/5 曾为空白占位图。删除可同时解决篇幅、空白图与"这是 AI 论文还是验证论文"的定位混淆。若必须保留，移入补充材料并说明它与本层结论无关。
- **N-7｜Table 7 的"actionable ordering"需注明重叠**：见 §结论-数据匹配 ⑦；建议加注"modalities are not mutually exclusive; a cell may be unlocked by more than one".
- **N-8｜"the remaining two rules were uninformative in a way that carries no weight"**（results.md 77）——被归为"无重量"却在下一句用它们支撑 r11 的判读。删掉这句评价性措辞。
- **N-9｜规则编号在 Table 2 中乱序**（r22 排在 r18 与 r19 之间）且未标"exploratory extension"以外的含义。建议按编号排序并在 note 列保留 v1.2 扩展标记。

### 需澄清（Clarification）

- **Q-1｜LTFU/波次纵向性**：Methods 写"wave fixed effects where more than one wave contributed"，Limitations 写"Most contributing waves are cross-sectional for the exposure"。但 SHARE 5 波、CLHLS 8 波、KLoSA 5 波都是同一批人重复观测（CLHLS r02 的 15,462 条观测来自 8,040 人）。请澄清：(a) 暴露是否随时间变化（作为时变协变量还是基线值）；(b) 在纵向队列里"cross-sectional for the exposure"是什么意思——若暴露与结局在同一波测量，是否允许暴露晚于结局的观测进入模型？这直接决定 r10 的"protective"能否用反向因果解释。
- **Q-2｜与 §18 的连续性**：analysis_plan §18（428–437）已给出"吸烟的无效在血清可替宁下依然成立"等 MHC 层面结论，本文完全没有引用或衔接。请说明队列层与 §18 是同一项目的不同层，还是彼此无关的两条线；若是前者，正文应交代为什么队列层不再使用连续暴露与中介分析（尽管 §18 已预注册它们为主交付）。
- **Q-3｜Table 6 的 MDE 计算口径**：MDE 由"observed n、暴露率、未暴露者事件率"导出（§17），但观察到的 OR 在 CLHLS r02 为 3.59 而 MDE 仅 1.69，MDE 未反映暴露组事件分布的不平衡。请补充暴露组事件数与非暴露组事件数两列，使读者能判断 CLHLS 3.59 是否受稀疏/不平衡影响（analysis_plan 的 C64 自己记录了 CLHLS 自报糖尿病 1.36% 属自报口径差异）。
- **Q-4｜Table 3/4 与正文口径**：Table 4 的 "tested"（159/301/14）与正文的 "testable pairs"（16/15/4 为规则相关对）是两个不同分母，Table 3 列名 `pairs_tested` 为空列。请统一列名并在表注中写出分母定义。
- **Q-5｜预注册时点**：§19 落盘日期 2026-10-15，队列层运行与更正记录也在 2026-10-15（同日）；§12/§13/§15 已自认"无预运行 git 快照可证"。请提供 §19 可独立验证的落盘时点（文件系统时间戳之外，如提交哈希/外部时间戳），否则"pre-registered"的证明力与 §12 同等级别。

---

## 如果只能改一句话（主编视角）

**不改标题，改结论的最后一句。**

现稿（manuscript 692–695；discussion.md 204–207）：
> For ophthalmic exposome screening specifically, the limiting factor is measurement: the eight cohorts hold two million person-wave records and still cannot address the majority of the rules, because they lack fundus imaging, blood assays and geocoded exposure — not because they lack participants.

问题：这句话与本文自己的操作方式互相拆台——r02 正是"没有血液测量 → 用自报值替代 → 判为可迁移"的那一条；把"measurement is the limiting factor"作为收官结论，等于在自己的最大妥协处宣布胜利。

改为：
> For ophthalmic exposome screening, the limiting factor was measurement, and this layer shows what happens when measurement is missing: the one rule whose exposure required a blood assay (r02) was tested with self-reported physician-diagnosed diabetes instead, in four cohorts whose diabetes prevalence ranged from 1.3% to 19.1%. The eight cohorts hold two million person-wave records from roughly 280,000 participants and still cannot address 15 of the 21 rules — not because they lack participants, but because they lack fundus imaging, blood assays and geocoded exposure. Until those measurements exist, exposome screening rules will continue to be evaluated against substitutes for the exposures they were written about.

这一改动的价值：它把全文从"我们的预注册判据不好用"（自我指涉的方法学练习）转向"缺测量的代价是可量化的、且已经在本文里发生过一次"，同时把 F-3 从隐藏缺陷变成论点的组成部分——这是本文唯一能对眼科学读者产生实际行为改变（资助/队列设计）的落点。

---

## 附：核查过程中被否证或确认的关键数字（供作者复核）

| 稿件表述 | 源文件 | 核对结果 |
|---|---|---|
| "8 replicated, 8 uninformative, 2 contradicted" | cohort_rule_results.csv（rule_relevant=True, 18 行） | ✅ 一致 |
| r02 pooled 1.95 (1.33–2.88) | cohort_heterogeneity.json:12–16 | ⚠️ CI 应为 1.3245–2.8828（1.32） |
| r13 pooled 1.14 | cohort_heterogeneity.json:179–182 | ⚠️ 应为 1.1349（1.13） |
| 年龄 meta 回归 "p = 0.42–0.52" | cohort_heterogeneity.json:56/112/272 | ⚠️ 实际 0.418/0.517/0.347 |
| r10 pooled 0.84，区域 p<0.0001 | cohort_heterogeneity.json:68–107 | ✅ 数值一致；但 Americas/Asia 各仅 1 队列 |
| r20 "all five cohorts pointed the same way" | cohort_rule_results.csv:11–19 | ✅ 五队列点估计均 >1；仅 3 条显著 |
| 不可测规则枚举 15 条 | evidence_audit.json:11–12；§19.6；variable_map.yaml:506–533 | ⚠️ 总数 15 对（21−6）；但枚举含 16 个项目，r07 与 r19 各被重复计入两个模态；r08/r09/r22 的原因被写成"数据不可得"而台账实为 not_yet_built / 探索性扩展 |
| "2.0 million person-wave records" | cohort_heterogeneity / frame 台账 §0.16 | ⚠️ 合计 2,036,518；参与者约 28 万；SHARE 占 83% |
| 队列独立性 | analysis_plan §0（8–31） | ❌ NHANES 规则改动发生在确证运行之后（test-set fitting） |
| HRS/ELSA 协变量完整性 | recalc_datahealth.csv:5（HRS age/sex 各缺 51.31%）、:4（ELSA 20.49/19.83） | ❌ 正文与 Limitations 均未报告 |
