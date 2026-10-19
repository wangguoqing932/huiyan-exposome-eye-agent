# R3 · Lancet 外推性与叙事审稿意见

**稿件**：*Pooling conceals directional conflict: a pre-registered cross-cohort evaluation of 21 literature-derived exposome rules for major eye disease in 2.0 million person-waves*
**审稿人**：R3（Lancet 视角：外推边界、人群与公平性、叙事与证据的匹配度）
**核验材料**：manuscript.md（含 Table 1–7、图例中英）、analysis_plan.md（§0–§19）、cohort_transportability.json、cohort_heterogeneity.json、evidence_audit.json、cohort_variable_mapping.md
**审稿日期**：2026-10-15

---

## 总体评价

这篇稿子做对了一件很不容易的事：它把一个"复现计数"式的可迁移性判据**预先声明**，然后在结果阶段自己证明这个判据太宽松，并把两种判据的分歧当作结果报告——这是方法学上的诚实，值得肯定。八队列、三洲、仅用原始源文件、逐队列码本核验、把"测不了"当发现而不是当局限，这套骨架对眼科暴露组领域有真实价值。

但作为 Lancet 稿子，它有四处结构性问题。第一，**结论走出了证据**：全文最响的两句话——"pooling conceals directional conflict"和"no rule was reliably transportable"——落在两个不可比构念的合并结果上（r20 的 vision 变量在 CLHLS 是"看不清圆环缺口"的功能测试，在 HRS/ELSA/SHARE 是自评视力等级），且把事后挑的地区亚组写成主结果。第二，**外推边界没有划**：8 个队列全部是 50+ 老龄化调查，LASI 与 CLHLS 年龄差 34 岁、卫生系统与自报确诊口径完全不同，稿子把它们并列、合并、再做地区对比，却从未论证这种并列的前提。第三，**Lancet 的招牌问题被回避了**：三洲八队列里有四个中低资源国家，但全文没有一句关于这些国家筛查含义、就医可及性混杂、或"测量是约束"对低资源环境意味着什么——这个结论被当作技术中立陈述抛出，实际政策含义很重。第四，**这是两篇论文**：跨队列可迁移性分析是真正的内容；(a) 半篇 LLM 决策支持系统评测（R11 层、F1、McNemar、架构图、时延图、内部修订代号 R5/R11）不属于本文，它的存在稀释了主叙事，也让方法学读者怀疑结论的稳健性。

**投票：大修（Major Revision）。** 核心数据集、预注册纪律和测量审计是值得救的，但需要重新组织论文结构、收紧标题与摘要的因果语言、补一节 generalizability/equity，并把地区亚组降级为探索性。

> 统计：致命 4 条 · 重大 14 条 · 次要 10 条 · 需澄清 8 条（重大及以上共 18 条）

---

## 外推性审查（真实适用边界）

**这项结果能推给谁：只推给"50 岁以上、参加了大型老龄化家庭调查、且眼部结局以自评/自报方式采集"的人群，而且只推给吸烟、饮酒、BMI、血糖这四个暴露族，只推给白内障与自评视力两个结局族。** 起草人不要在这句话之外多说一个字，因为边界之外每一处都塌：（i）**测量层**——规则集 21 条里 15 条在 acht 队列全部不可测，视网膜病变/DME 全家族（r03/r04/r07/r19/r22）、青光眼测量规则（r16）、PM2.5/UV 规则（r17/r18/r21）在本层零覆盖，所以"可迁移性"结论**不得**外推到任何眼底影像定义的疾病；我们连一条 DR 规则的可迁移性都不知道。（ii）**人群层**——八个队列都是老龄化队列，不是"老年人"的概率样本：LASI 均龄约 58（45+ 抽样）、CLHLS 均龄 92.0、SHARE/HRS/ELSA 居中，白内障在 58 岁主要是"是否做过手术"的就医可及性代理，在 92 岁几乎是普遍状态；同一 OR 在不同年龄结构下不是同一个量，把它们放进同一 REML 池里，tau² 里混的主要是年龄与医疗可及性，不是生物学。（iii) **构念层**——CLHLS 的 vision 是"圆环缺口辨识"功能测试（can see and distinguish / see only / cannot see / blind），HRS/ELSA/SHARE/MHAS/KLoSA 是 Likert 自评视力，两者没有共同刻度；r20 之所以成为"两条可迁移规则"之一，有一半功劳来自 CLHLS 那条构念不同的项。（iv）**证据层**——稿件自己承认队列并非独立于文献（规则来自文献，队列也贡献了那些文献），所以这不是严格意义上的 out-of-sample 检验，而是"跨队列一致性检查"。**因此本层最诚实的一句话是：在可由自评测量的暴露-结局族内，跨八个老龄化队列的一致性极低且高度异质；本层对眼底影像定义的疾病、对非老龄化调查人群、对未被这八个队列覆盖的年龄带，均无任何外推能力。** 稿件需要在 Discussion 开头用一段独立文字把这条边界写死，而不是散落在 Limitations 的六段里。

---

## 叙事逐段意见

### 引言

- **§ Intro 第 1 段（"Visual loss in later life is common…"）**：把白内障、青光眼、AMD、DR 四大致盲原因平行铺开，最后落到"the clinical value of screening lies in identifying people whose modifiable exposures place them at risk before vision is lost"。问题：这句话制造了一个"本研究将告诉你怎么筛"的期待，而实际结果恰恰是**筛不了**（21 条规则 6 条可测、异质性感知判据下 0 条可迁移）。这不是不能写，而是必须在同段末尾把期待调转：现在读者是被"引流"到筛选价值，后面却被"测量约束"劝退，落差没有预告。**建议**：第 1 段末改为"…but what such rules are worth outside the populations that generated them is unknown"，把问题设为**可迁移性**而不是**筛查价值**。
- **§ Intro 第 2 段（exposome 概念）**：合格，没有过度承诺。可保留。
- **§ Intro 第 3 段（decision support + 规则可检查）**：这一段是两篇论文的接口，也是叙事的第一个裂缝：把"临床决策支持系统"作为规则落地的"自然载体"引入，但本稿的结果**与任何临床决策支持系统的性能无关**（系统评测在 R11/NHANES 层，且系统本身与跨队列分析没有耦合）。**建议**：把这一段压缩到两句，只保留"规则必须逐条可追溯、因而逐条可检验"这个逻辑，删去 decision-support 作为动机的铺垫。
- **§ Intro 第 4 段（"We therefore asked a narrower…question"）**：这是全文最好的段落，窄问题设定正确。
- **§ Intro 第 5 段（三种结果预告）**：把"系统性能 gap"（第一类结果）与"可迁移性分类"（第二类）、"测不了"（第三类）并列，等于在引言里就宣告了本文的混合结构。第一类结果与第二三类没有逻辑依赖。**建议**：删去第一类，引言只预告可迁移性分类与测量审计两类。
- **§ Intro 第 6 段（paper proceeds as follows）**：期刊一般不接受这种路标段，且它把系统评测写进了导航。**建议**：整段删除。

### 讨论

- **§ Principal findings 第一段（"First, the transportability…cannot be established by counting"）**：表述偏强。"cannot be established"是从**一个**规则基（21 条）**八个**队列推出来的，属于对这一判据的示范性反驳，不是判据的普遍无效。**建议**：改为"…was not established for any of the six testable rules under a criterion that also required tolerable heterogeneity; replication counting alone would have marked two as transportable."
- **§ Principal findings 第二段（"pooling does not resolve…it conceals one"）**：这是全文最需要改的一句话。问题不是**统计**问题（I² 与 Q 都报了），而是**修辞**问题：把"未报告异质性会掩盖分歧"的正确一般性主张，写成了"合并会掩盖分歧"的普遍指控，而这与本研究自己实际做的事（报了 I²、报了预测区间、发现了冲突）相矛盾。审稿人会立刻反问：你自己 pooled，而且你看见了冲突，那"conceals"是谁的行为？**建议**：改为"The pooled estimate was uninformative about the conflict it averaged over: it was null while the regional subgroups differed, and the pooled value describes no population studied. Had heterogeneity not been reported, the conflict would have been invisible."——把矛头从"合并"转向"不报异质性的报告实践"。
- **§ Principal findings 第三段（measurement, not sample size）**：内容对，但**位置错**。它是本稿最有政策含义的发现，却被排在第三位并写成技术总结。同时它完全没有人群/公平性维度（见下文致命 4）。**建议**：提到第一位（对 Lancet 读者，这是最可行动的发现），并紧接一段 generalizability 与 equity。
- **§ The direction reversal / Selective survival**：论证是诚实的（自己承认"indirect and unconfirmed"），但**方法用错**：用队伍均龄作为生态学调节变量的一次 meta-regression（k=4或5）不能检验个体层面的选择性存活；且把 p=0.52 的零结果读作"该解释不成立"。这是把"无证据"当"证据不存在"。**建议**：把这段降为"我们无法区分以下三种解释"，删去"it does not"的断言，改为"the ecological test had almost no power to detect it（k=4，p=0.52，不能排除）"。
- **§ Unmeasured confounding**：E-value 段落把 r10 的 CLHLS 与 SHARE 两个估计都描述为"脆弱"（E=2.01/1.46），这实际上**削弱**了本文把它当作核心发现（"direction reversal"）的资格——一个 E=1.46 的估计（对应 OR 1.11）本身就在噪声边缘。稿件没有回应这个内在张力。**建议**：补一句"given these E-values, the SHARE risk-increasing estimate is itself only marginally robust; the reversal should be read as a signal about measurement heterogeneity rather than as evidence of opposing biological effects."
- **§ Why the pooled estimate is the wrong summary here**：与标题同病（见致命 2）。保留预测区间论述，删去对 pooling 的普遍指控。
- **§ A criterion that was too permissive**：这是本稿最诚实、最有价值的一节。唯一问题是：**异质性感知判据（PI 排除 1 + I²<75%）是事后构造的**，稿件却说"the criterion used here was pre-registered and is reported as primary"——这句话是对的，但紧接着的替代判据读起来像另一个预注册判据。**建议**：明写"this second criterion was specified after seeing the heterogeneity and is reported as a post-hoc alternative reading, not as a pre-registered verdict."
- **§ Measurement as the limiting factor**：技术内容扎实。但"these are not exotic measurements; they are standard in ophthalmological field studies and in several population cohorts outside this set"——这句话对 LASI/CLHLS/MHAS/CRELES 恰恰不成立（那里的约束是卫生系统，不是认知）。这是本文离公平性问题最近、却擦肩而过的一句。**建议**：改为"standard in ophthalmological field studies in high-income settings; whether they are deployable in the ageing cohorts of India, China, Mexico and Costa Rica is a separate, unanswered question this layer cannot address."
- **§ Comparison with the internal layers**：写作上有用但**话题有风险**：它把 NHANES/KNHANES 层引入论证（"no rule-relevant pair was contradicted in either country, declared-domain precision was 1.00"），而这正是审稿人要求删掉的那半篇论文。**建议**：删去或压到补充材料，主文不做跨层比较；本层单独成立。
- **§ Limitations（Independence achieved / Ascertainment / Design and temporality / Power / Single-cohort rules / CLHLS severe vision）**：六段齐全，但排列与内容有明显缺口：（a）**没有 generalizability 段**；（b）**没有人群结构差异段**（8 队列年龄/卫生系统）；（c）**没有公平性段**；（d）Ascertainment 段承认"self-report…correlated with the exposures of interest"，却在结果里照样跨队列比较效应量——这是一个自相矛盾，必须处理（见重大 2）；（e）"CLHLS severe vision…reported as a secondary analysis only, and no primary conclusion depends on it"——**不成立**：Table 6 里 r20@CLHLS 用的就是这个 flag，而 r20 是本文两条"可迁移"规则之一。这句话必须更正（见重大 10）。
- **§ Conclusion**：见措辞清单第 1–3 条；核心问题是"我们证明了 pooling 是错的方法"这一层因果表述超出了本研究设计（本研究只提供了**一个**反例，且这个反例的分组是事后挑的）。

---

## 致命 / 重大 / 次要 / 需澄清

### 致命（4 条，必须解决，否则不能送外审）

---

**F1 · 合并了不可比的视力构念，而两条"可迁移"规则之一是建立在这个合并上的**
- **位置**：Results §Cross-cohort transportability（r20，manuscript L344–347）、Table 5（r20 行，L383）、Table 6（CLHLS r20 行，L1059）、Abstract Results（L35 附近）、Figure 8 legend（L801）。
- **问题**：r20（吸烟→视力损害）是全文两条"可迁移"规则之一。它的 5 个队列里，CLHLS 的 `vision_impairment_severe` 来自 `g1` 系列，题面是 **"can you see the break in the circle?"**（圆环缺口辨识功能测试，4 级：can see and distinguish / can see only / cannot see / blind，且 2000 波只有 3 级），而 HRS（`KC095–097`）、ELSA（`heeye`）、SHARE（`eyesightr`）、KLoSA（`C076/C077`）用的是**自评视力 Likert 等级**。这两类测量没有共同刻度。稿件的操作纪律自己规定"self-report was kept distinct from examination-based grading"、"Construct shifts were declared rather than merged"，但 CLHLS 的功能测试 vs 自评量表这一次**恰恰是合并且未声明**。合并后的 r20 异质性 I²=93.8%、预测区间 0.81–1.89 跨 1——这正是构念不可比的典型指纹，而稿件把异质性解释成"population-specific"，没有考虑"测量不同"这一更简约的解释。
- **为什么是问题**：这是 **construct validity** 层面的错误，不是局限。它同时影响 Abstract 的"两条可迁移规则"、Discussion 的"subgroup 差异是真的人群差异"、以及标题叙事。Lancet 审稿人看到"功能测试与自评量表合并成同一个 outcome 并做跨洲比较"会直接质疑全部跨队列效应量的可比性——而这恰恰是本文唯一的实证贡献。
- **具体修改建议**：（1）把 vision outcome 按器械族分层：`functional_test`（CLHLS）与 `self_rated`（其余），主分析在 self_rated 族内做；CLHLS 单列在补充材料，正文只作敏感性。（2）在 Table 5/Table 6/Figure 8 增加一列 `outcome_instrument`。（3）Abstract 与 Discussion 里 r20 的"transported"结论必须限定为"在自评视力族的四个队列中"。（4）把这一条加进 Limitations 的 Ascertainment 段，并明确它与 r10 反转的关系（两者都可能是器械/可及性差异的表现）。

---

**F2 · "pooling conceals directional conflict"这一标题级论断超出了证据**
- **位置**：标题（L1）、Abstract Background/Conclusions（L9–14、L40–43）、Discussion §Principal findings 第二段（L504–511）、§Why the pooled estimate is the wrong summary here（L577–592）、Conclusion（L687–695）。
- **问题**：本稿并未"发现"合并会掩盖分歧——它**做了**合并，**报告了** I²（79.5%–93.8%）、Cochran Q、预测区间，并**因此看见了**分歧。也就是说，本研究恰恰证明：在报告异质性统计量的前提下，合并并不掩盖冲突。标题把一个"报告实践的建议"表述为一个"统计方法的缺陷"，逻辑上是可反驳的。更具体的一层问题：Results 表 5 的"Regional subgroup difference"列，在 r12 与 r13 上等于 Q p（r12: Q_p=0.027334, p_between=0.027334；r13: Q_p=0.027220, p_between=0.027220，见 cohort_heterogeneity.json L124–217），即 **k=2 时"地区亚组差异"与"总异质性"是同一个检验、同一个数**。所以"地区亚组显著不同"不是一个独立发现。
- **为什么是问题**：标题与摘要是编辑和外审最先读的部分。一个可被一行反例推翻的中心论断，会让审稿人怀疑全文的统计自省程度——而本稿最值钱的部分正是统计自省。
- **具体修改建议**：把中心论断从"pooling 掩盖分歧"改为"**合并估计对新人群没有预测力**，这一点只有在报告预测区间时才可见"（这是你真实证明的东西，且不可反驳）。标题建议改为 *"A pooled estimate that describes no population: cross-cohort transportability of 21 literature-derived exposome rules for eye disease in eight ageing cohorts"* 或近似。Abstract Background 的"or merely averages over populations in which they disagree"可保留，但 Conclusions 的"pooling concealed a directional conflict rather than resolving it"必须改（见措辞清单）。

---

**F3 · 地区亚组是事后构建的，且与 Q 检验混为一谈，却被写成主结果**
- **位置**：Abstract Results（L34–36，"its pooled estimate was null (0.84, 0.67–1.05) while regional subgroups differed (p < 0.0001)"）、Results §Between-cohort heterogeneity（L387–390）、Table 5 列名"Regional subgroup difference"、Discussion §Principal findings 第二段（L504–511）。
- **问题**：核对 analysis_plan.md §19 全文（我逐节读过 §19.1–§19.10），**没有任何一句预先声明或定义地区亚组**：§19.7 只预注册了"≥2 个队列同向且 q<0.05 记 transportable"的迁移判据，协变量只写了 age + sex + 波次固定效应，多重检验只写了 confirmatory/exploratory 两个家族。全文检索 `region|regional|Europe|Asia|Americas|subgroup|moderator|meta-regress` 在 analysis_plan.md 中**零命中**。而 Table 5 却直接给出"Regional subgroup difference"列，Abstract 把它列为结果段的结论句之一。此外分组本身是事后且不均衡的：Americas 组**只有 CRELES 一个队列**（r02、r10、r20 的 Americas 值分别等于 CRELES 的点估计），Asia 组把中国 CLHLS 与印度 LASI 合并（r02 的 Asia 组 = 1.9253 是 CLHLS 3.59 与 LASI 1.88 的合并值），Europe 组把 5 个 SHARE 波次覆盖的多国样本与英国 ELSA 合并。没有任何一句解释为什么中国与印度构成同一个"region"。
- **为什么是问题**：这是审稿人清单第 4 项（p-hacking 嗅探）的核心命中点。（a）事后分组 + 事后选择调节变量，是教科书式的 sub-group fishing；（b）在 k=2 的两个规则上，"地区效应"与"异质性"数值完全相同，说明该列的统计含义未被作者自己辨析；（c）Abstract 里用 p<0.0001 呈现一个未预注册、未做多重校正、且组内 n=1 的分组比较，属于选择性报告。
- **具体修改建议**：（1）全部地区分析移入补充材料并明确标注 *post hoc, not pre-registered*；正文只保留"存在与地区/器械/年龄结构共线的异质性"这一表述。（2）Abstract 删去"regional subgroups differed (p < 0.0001)"，改为"the pooled estimate was null while cohort estimates ranged from 0.70 to 1.11"。（3）若坚持保留，须给出：分组的先验定义与依据、组内队列数、一个真正的 moderator 分析（以年龄/器械/手术可及性为协变量的 meta-regression），并说明 k=2 时 p_between=Q_p 的等价性。（4）在 analysis_plan 之外补一份偏离记录（§19.9 已要求"任何新增分析记入偏离记录并单列报告"，本节恰好适用）。

---

**F4 · 全文没有 generalizability 段落，没有公平性讨论，而这是 Lancet 的必备项**
- **位置**：缺失项；对照 Abstract Background（L9–14）、Intro 第 1 段（L49–61）、Discussion §Measurement as the limiting factor（L611–625）、Limitations（L638–672）；并核对全稿关键词 `resource/equity/access/policy/India/LASI/MHAS/sex diff`——结果：`access` 仅 1 处（L654，且仅作为"差异漏报"的泛泛表述），`resource/equity/policy/LASI/MHAS` 在正文中只出现在队列名单与缩写表里，**没有一处讨论这些国家的结果含义**。
- **问题**：稿件反复自我定位为"跨三洲、含中低资源国家"的验证（Abstract、Intro、Fig 8），但在结果与讨论里，这四个国家（印度、中国、墨西哥、哥斯达黎加）完全不产生任何独立论述：MHAS 贡献 0 个可检验对（见 M5），LASI 只贡献 2 对（r02、r20），CRELES 贡献 3 对，CLHLS 贡献 5 对。同时，全文最响的政策结论"the limiting factor is measurement, not sample size"被当作一个**技术中立**的发现抛出——但在低资源环境里这句话的直接含义是"不要指望扩大样本，先买眼底相机/化验"，这是一个有真实资源配置后果的政策主张，稿件没有做任何论证或限定。更关键的是：**自报结局在就医可及性低的人群中恰恰是测量误差最大的**，而稿件在 Limitations 承认"self-report introduces differential under-ascertainment where access to care differs, which is itself correlated with the exposures of interest"（L655–656），却没有把它连回公平性叙事——如果自报白内障本质上是"是否做过白内障手术、是否获得过诊断"的代理，那么 r10 的地区反转（欧洲 +、亚洲/美洲 −）在**测量假说**下是可直接预期的，而不需要任何生物学解释。稿件列了三种解释（选择性存活、未测量混杂、真实效应修饰），**漏掉了第四种、也是最简约的一种：就医可及性/诊断获得差异导致的自报口径差异**。
- **为什么是问题**：（a）Lancet 编辑会把"跨三洲含中低资源国家但无 equity 讨论"视为明显缺口，尤其在一个眼科可避免盲的题目上；（b）"测量是约束不是样本量"没有政策含义的展开，等于把一个政策主张伪装成技术结论，这是叙事上的回避（用户清单第 2 项问的正是"作者是否回避了"——答案是：回避了）；（c）漏掉测量假说使 r10 反转的解释集不完整，削弱了 Discussion 的严谨性。
- **具体修改建议**：（1）在 Discussion 增一节 **Generalizability and implications for low-resource settings**（约 350–450 词），交代：本层证据只适用于 50+ 老龄化调查人群、自评/自报眼部结局、四个暴露族；明确 **LASI 只提供 2 对、MHAS 提供 0 对**，因此"亚洲/美洲"结论实际上由中国的 CLHLS 与哥斯达黎加的 CRELES 承担，不构成对印度或墨西哥的推断。（2）把测量假说写成 r10 反转的第四个候选解释，并指出它与"真实效应修饰"在这个设计里无法区分，但**更简约**。（3）"measurement, not sample size"必须加限定语与政策语境，例如"在本规则基与这些队列内，可观察到的约束是测量而非样本量；把这一结论直接转译为低资源环境下的投资优先序之前，需要先确认这些测量——尤其是自报白内障与自评视力——在就医可及性低的人群中是否具有可比的测量性质，而本层的数据恰恰提示它们不具备。（4）补一项按性别/性别的分层或至少声明，Lancet 对此有明确期待；本稿完全无 sex/gender 维度（age 与 sex 只作为协变量）。

### 重大（14 条）

---

**M1 · 八队列的人群结构差异未被当作有效性威胁处理（清单第 1 项的核心）**
- **位置**：Methods §Cohort-layer data sources（L155–168）、Results 表 5、Discussion（无对应段落）。
- **问题**：8 个队列的年龄结构差 34 岁（CLHLS 均龄 92.0，LASI 45+ 抽样、均龄约 58），且年龄不是同一功能形式——稿件只在模型里写"age and sex as covariates"（L243），没有给年龄的函数形式（线性？样条？），也没有任何年龄标准化。把 LASI（白内障在 45–60 岁多为"是否接受过手术"）与 CLHLS（白内障近普遍、视力功能测试 20–35% 为"看不见"）的 OR 放进同一 REML 池，tau² 混合的主要是年龄与卫生系统，而不是暴露效应。稿件用一次 k=4–5 的**队列均龄生态学 meta-regression**（p=0.42–0.52）来"排除"年龄解释，这在方法上不足以成立（见 M4）。
- **为什么是问题**：这是"把效应量并列是否合理"的直接答案：不合理，除非做年龄标准化或限制到重叠年龄带。审稿人不能接受用一次低功效生态学回归代替这项论证。
- **具体修改建议**：补 **年龄标准化或年龄带限制分析**：对每个队列估计 60–79 岁（或其他共同重叠带）的效应，重跑 pooled 与预测区间，与主分析并列；报告每队列年龄分布的完整描述统计（均值/中位/四分位）作为 Table 5 的脚注或补充表；在 Methods 写明年龄的函数形式与选择依据。

---

**M2 · 在承认自报结局不可比之后，仍然跨队列比较效应量并把反转当作解释对象**
- **位置**：Limitations Ascertainment（L651–655）vs Results（L341–356，跨队列 OR 并列）、Discussion §The direction reversal（L522–568）。
- **问题**：Discussion 明确写"cataract and glaucoma are self-reported physician diagnoses throughout this layer. The NHANES layer used examination-based grading, so the two are not comparable in effect size and we draw no such comparison"（L651–654）。但**队列层内部**同样是不可比的：SHARE 的 8.4% 与 CLHLS/CRELES 的 38.5% 自报白内障患病率（cohort_variable_mapping.md C-注释）反映的是手术可及性与诊断获得，不是患病率。稿件却在整个队列层内部做效应量并列、地区比较、以及"direction reversal"的机制讨论。
- **为什么是问题**：这是**内部一致性**问题。要么承认自报口径在这些队列间可比（那就不必在 Limitations 那样写），要么承认不可比（那就不能把 1.11 vs 0.748 解释为方向冲突）。二者不能同时成立。
- **具体修改建议**：明确一个立场并贯彻：建议承认"自报白内障在本层内是**就医可及性混合的**指标"，把跨队列 OR 差异的默认解释设为测量/可及性差异，生物学解释（效应修饰）作为**次要**候选；并在结果中报告每队列自报白内障患病率与自报糖尿病患病率（它们已在 mapping 文档里），供读者判断口径差异幅度。

---

**M3 · 探索性分析的选择与多重性未交代（68 对 vs 18 对；三个"复发方向"如何挑出）**
- **位置**：Results §Exploratory associations（L439–449）。
- **问题**：Methods 说探索性家族包含"every exposure–outcome pair actually tested in that cohort"（L252–253），cohort_transportability.json 与 Table 8 的说明说"68 pairs analysed in total"；但正文只报告 3 个"复发方向"。稿件没有交代：（a）68 对中多少在哪个队列、（b）探索性家族内 q 的分布、（c）"recurred across cohorts"的判定规则（≥2 队列？同向？q 阈值？）、（d）这 3 个方向是从多少个候选中筛出的。读者无法判断这是描述性观察还是经过选择的结果。
- **为什么是问题**：审稿人清单第 4 项（p-hacking 嗅探）在探索性部分同样适用。"Three directions recurred"这句话在缺少分母与筛选规则时无法评估。
- **具体修改建议**：补一张探索性结果全表（或补充材料），给出 68 对的完整清单与 q 值；明写"recurred"的判定规则；说明这三个方向在多重校正后是否仍显著（LASI glaucoma 的 q=1.2×10⁻¹⁰ 与 HRS 的 8.1×10⁻²⁰ 可以保留，KLoSA 的 1.50/1.99 需要 q）；并声明探索性家族不与确证家族共享 FDR。

---

**M4 · 用未预注册的"异质性感知判据"与预注册判据并列为双结论，造成"两次机会"的印象**
- **位置**：Abstract Results（L29–33）、Results（L394–399）、Discussion §A criterion that was too permissive（L594–609）。
- **问题**：预注册判据（≥2 队列 q<0.05）标记 2 条可迁移；事后判据（PI 排除 1 且 I²<75%）标记 0 条。稿件把后者称为"a stricter reading"并作为全文结论（"none of the six testable rules was reliably transportable"）。事后判据本身是合理的，但稿件未声明它是**在看到结果之后**才指定的（analysis_plan §19.7 只预注册了前一个判据；I²<75% 与 PI 排除 1 在计划中无任何出处）。
- **为什么是问题**：在预注册框架下，事后判据必须明确标注为 post hoc，否则读者会认为"作者有两个预注册判据，取了对结论更有利/更不利的那个来叙事"。本稿的方向是"取更严格的"，道德上无问题，但**方法披露**上仍须标注。
- **具体修改建议**：在 Abstract、Results、Discussion 三处首次出现该判据时都标注"post hoc, specified after observing the heterogeneity"；并在 Discussion 明确：预注册判据的 2 条结论仍然是**预注册的正式结论**，0 条的结论是**次要解读**，二者并列而非替代。

---

**M5 · MHAS 被列为八队列之一，却不贡献任何一对，且全程未披露**
- **位置**：Abstract Methods（L19–20）、Methods（L161–168，MHAS 78,537 person-waves）、Results（L327–328 八队列名单）、Figure 8 legend（L809）、evidence_audit.json（feasible_pairs 中无 MHAS）。
- **问题**：evidence_audit.json 的 `feasible_pairs` 18 条与 cohort_transportability.json 的 6 条规则所涉队列，**均不含 MHAS**；Figure 8 legend 统计说明自己写的是"18 pairs across 6 rules and **7 cohorts**"（L809），而正文与摘要一律说**八个**队列。也就是说：MHAS 在摘要、方法、结果、图注中被反复计入"八队列/三洲"，却提供了 0 个可检验对，且稿件从未说明它为什么是 0。
- **为什么是问题**：这直接关系到摘要"2.0 million person-waves"与"eight cohorts"这两个数字的证据含量（另见 M6）。计数不准会被视为粗心，而"纳入但零贡献且不披露"会被视为选择性表述。
- **具体修改建议**：（1）在 Results 第一段明写"MHAS contributed no testable pair（其白内障项与吸烟/饮酒/BMI/血糖项的交叉可得性不足；具体原因见补充表）"；（2）摘要改为"eight population-based ageing cohorts, of which seven contributed analysable pairs"；（3）在 Table 8/Figure 8 里显式列出 MHAS 一列并标为 0，或从"八队列"的表述中扣除。

---

**M6 · "2.0 million person-wave records" 实质上是 SHARE，摘要的这一卖点失真**
- **位置**：Abstract Methods（L21–22）、Methods（L166–168）、Results（L328）、Discussion（L514）、Conclusion（L693）。
- **问题**：SHARE 独占 1,693,515 / 2,043,518 ≈ **83%**，而 SHARE 的独立人数是 137,183。更重要的是：person-wave 不是独立单位——SHARE 的 5 个插补副本在描述统计里只用副本 1（作者自己声明 L246–248），波次之间同一人被聚类稳健方差处理。所以"2.0 million person-wave records"给读者的印象是"这是一项两百万人的研究"，实际推断所依赖的信息量远小于此，且近全来自一个队列。稿件还把"sample size"作为核心修辞之一（"the binding constraint is measurement, not sample size"），而这个 sample size 数字本身注水，修辞自伤。
- **为什么是问题**：Lancet 编辑对"样本量夸张表述"很敏感；且本稿的核心论点之一就是"不要被样本量迷惑"——用一个膨胀的样本量数字做卖点是叙事反讽。
- **具体修改建议**：摘要改为"comprising 2.0 million person-wave records from 137,183 (SHARE) to 2,827 (CRELES) unique participants"。并在 Discussion 加一句"SHARE contributed 83% of person-waves and dominated the pooled estimates; per-cohort estimates and weights are reported in Table 5 and the supplement"。

---

**M7 · Methods 的 BMI 切点描述与预注册不一致**
- **位置**：Methods（L222–227）。
- **问题**：稿件写"25 kg/m² for the Asian cohorts and 30 kg/m² for the others"。但 analysis_plan §19.7 明确规定：**KLoSA/MHAS/LASI/CLHLS 用 25；SHARE/HRS/ELSA/CRELES 用 30**。两者在 SHARE/ELSA 上一致，但**在 CLHLS 与 LASI 上矛盾**：CLHLS 与 LASI 是亚洲队列，按 §19.7 用 25（"="Asian cohorts"成立），所以这句话在 CLHLS/LASI 上其实是对的；问题在于"others"——SHARE/HRS/ELSA/CRELES 用 30 也对。**重新核对**：§19.7 的分配与稿件的"Asian→25 / others→30"在四个亚洲队列与四个非亚洲队列上完全吻合。**因此此条降级为需澄清**（见 C6），真正的问题是 CLAIMS 的切点导致 SHARE r13 = 1.24 复现这一事实未在正文说明（SHARE 用 30，且 mapping 文档显示 SHARE 的 `bmi_high_25` 是 FAIL 的意图）。改为：需澄清，请作者明示 SHARE/ELSA 的 r13 用的是 30 而非 25，并给出敏感性结果。
- **修正说明**：本条不成立为"重大"，已移入需澄清 C6。**在此保留编号并标注更正，以保持与审稿意见的回溯一致**（审稿人的自我更正也应留痕）。

---

**M7（替换）· "powered null"的判定是循环的，不能作为"阴性结果可靠"的证据**
- **位置**：Methods §Statistical analysis（L256–260）、Results §Statistical power（L465–474）、Discussion Limitations Power（L661–664）。
- **问题**：Table 6 的说明自己写明"A pair is a POWERED NULL when its confidence interval excludes its own MDE"（L1052）。MDE 由**观测边缘**（n、暴露率、结局率）算出，与观测 OR 同源；用"CI 排除自己算出的 MDE"来判定效能，在统计上接近同义反复——多数足够的零结果都会自动满足。因此"5/8 = 62.5% 是 powered null"与"17/30 powered null"（L455–457）不是独立证据，而是构造性结论。
- **为什么是问题**：本稿用"阴性结果大多是有效能的阴性"来为"不可迁移"结论提供强度。如果这个判据是循环的，那么"没有复现"与"没有效能复现"之间的边界就没有被真正划清。
- **具体修改建议**：（1）改用**预先设定**的临床关注效应（analysis_plan §17 已预注册 1.5× 主 / 2.0× 次）作为 MDE 阈值，而不是"自己算出的 MDE"；（2）报告每个阴性对能否排除 1.5× 与 2.0× 两档；（3）把当前的循环判据降级为描述性指标并注明其局限。

---

**M8 · E-value 全部偏低，却未削弱"方向反转"作为核心发现的地位**
- **位置**：Results（L405–411）、Table 5 脚注（L1043–1045）、Discussion §Unmeasured confounding（L544–551）、Abstract（L31–32）、Conclusion（L684–685）。
- **问题**：E-value 是 1.46（SHARE，对应 OR 1.11）与 2.01（CLHLS，对应 OR 0.748）。这两个值意味着：一个与吸烟和白内障都相关的、RR≈1.5–2 的未测量混杂即可解释掉任一方向。稿件承认"that is a modest requirement"，但结论仍把 reversal 当作核心发现。逻辑上，一个 E=1.46 的估计本身就不足以支撑"欧洲方向为风险升高"的判断——那么"方向反转"完全可能是"一个脆弱估计 vs 一个同样脆弱的估计"。Table 5 脚注还写"r02…E-value of 6.64 (4.69) and is not fragile in the same way"，这个对比（把 r10 的脆弱性衬托成"另一种情况"）可以被读作淡化处理。
- **为什么是问题**：这是"讨论只挑有利解释"的一个具体实例：脆弱性分析本应削弱反转的地位，但稿件的行文把它当作"我们已经做了稳健性检查"来呈现。
- **具体修改建议**：在 Results 与 Discussion 明确写"the SHARE risk-increasing estimate is itself only marginally robust (E=1.46)，因此 the reversal 的**两个方向**都在中等混杂即可解释的范围内；本层不能把任一侧视为确立的方向"。并考虑把 reversal 从 Abstract Results 的显著位置（用粗体 p<0.0001）降为一段普通叙述。

---

**M9 · 地区分组的合理性未被论证（组内异质被掩盖）**
- **位置**：Table 5（L379–385）、Discussion（L506–507）。
- **问题**：Table 5 把 Americas 组等同于 CRELES 单队列（r02 Americas = 1.3116 = CRELES 点估计），把 Asia 组等同于 CLHLS + LASI（r02 Asia = 1.9253 是 3.59 与 1.88 的合并），把 Europe 组等同于 SHARE + ELSA（r02 Europe = 1.7539 = SHARE 点估计，因为 r02 在 ELSA 不可测）。稿件从未说明：（a）为什么中国与印度是同一"地区"（两者在白内障患病率、糖尿病诊断率、卫生系统上差异极大）；（b）为什么"欧洲"内 SHARE 的 5 波多国样本与 ELSA 可以合并；（c）在 r02 上 Europe 组只有 SHARE 一个队列、Asia 组有两个队列且差异大（1.88 vs 3.59）——组内异质性被"地区"标签掩盖了。
- **为什么是问题**：这是一个**聚合层次不当**的问题（ecological fallacy 的镜像）：用地理标签替代真正的机制变量（手术可及性、诊断率、年龄结构）。它恰好也是本文批判别人做的事（"用合并掩盖分歧"）——自我矛盾。
- **具体修改建议**：废弃"region"作为主分析变量，改用可解释的 moderator（自报白内障患病率作为就医可及性代理、队列均龄、结局器械族）；或在保留地区标签时同时报告组内队列数与组内 I²。

---

**M10 · Limitations 对 CLHLS severe vision 的声明与 Table 6 的实际使用相矛盾（且违反 §19.8 预注册）**
- **位置**：Limitations（L670–672）vs Table 6（L1059，CLHLS r20 用 `vision_impairment_severe`）、Results（L344–347）、analysis_plan §19.3 脚注与 §19.8 第 1 条。
- **问题**：analysis_plan §19.3/§19.8 明文规定 CLHLS 的 `vision_impairment_severe`（25.7%，超出 HARD 上限）**"仅作次要分析，主要分析排除"**。而 Table 6 里 CLHLS r20 用的就是这个合并口径（`r20_smoking_x_vi_mod_severe`，n=13,115），且它是 r20"五个队列方向一致"里的第 5 个点（OR 1.0267）。Limitations 却写"It is reported as a secondary analysis only, and no primary conclusion depends on it"——**事实上 r20 是本文两条可迁移规则之一，其结论包含了 CLHLS 的贡献**。
- **为什么是问题**：**协议偏离未申报**（§19.9 要求任何偏离记入 §0 并单列报告），且 Limitations 有一句可被直接证伪的话。这在预注册论文里是诚信层面的问题。
- **具体修改建议**：（1）更正 Limitations 那句话，改为"CLHLS 的 severe 项超出年龄未分层的 HARD 带（25.7%，均龄 92.0）；它按预注册仅作次要分析，但 r20 在 CLHLS 的点估计（1.03，CI 跨 1）建立在合并的 moderate/severe 口径上，因此 r20 在 CLHLS 的贡献应视为次要分析结果"。（2）补一项把 CLHLS severe 排除后的 r20 敏感性分析（k=4）。（3）按 §19.9 补偏离记录。

---

**M11 · 核心"可迁移/不可迁移"结论依赖 q 值，而 q 在两种多重校正程序下会翻转，稿件未做敏感性分析**
- **位置**：Methods（L250–254）、Results（L286、L339–343）、Abstract（L28–33）。
- **问题**：稿件全文使用 **Benjamini–Yekutieli（BHY）**，并在 Methods 给出理由"remains valid under arbitrary dependence"。但本案的 confirmatory 家族只有 18 个（规则×队列）对、且分析计划已把它们视为一个预声明家族（§19.7），此时 **BH 更合适、BHY 会过度保守**。关键后果：CRELES 的 r02，`q_primary = 0.0506`——恰好卡在 0.05 边界（Table 6 与 transportability.json 显示 OR 1.3116，CI 1.0705–1.6069，q=0.05059）。在 BH 下这一对很可能由 uninformative 变为 replicated（把 r02 的复现从 3/4 变为 4/4），而在更保守的 Bonferroni 或家族定义收紧下也可能反向。稿件的摘要与结论都建立在这个 q 值体系上，却没有任何多重校正敏感性分析。
- **为什么是问题**：审稿人会问"为什么在只有 18 个预声明检验、无任意依赖结构的家族里用 BHY"。这是一个可以在**不改变原始数据**的前提下翻转"3/4"与"4/4"的选择，属于结论级别的方法学选择。同时 Results 自己写"CRELES at 1.31 (1.07–1.61) falling just short (q = 0.051)"——作者显然知道这是边界。
- **具体修改建议**：补多重校正敏感性分析：BH、BHY、Bonferroni 三档并列报告每个（规则×队列）对的三态；说明主分析选 BHY 的理由与代价；在 Results 明写 CRELES r02 在 BH 下会变为 replicated，并对"3/4"的表述加限定。

---

**M12 · 结论把"我们示范了判据的一个反例"升级为"复现计数不可用于评估可迁移性"的普遍主张，并暗示现有规则可判为不可用**
- **位置**：Abstract Conclusions（L40–43）、Discussion §A criterion that was too permissive（L596–609）、Conclusion（L674–695）。
- **问题**：本研究提供的是**一个**规则基（21 条文献规则，且只有 6 条可测）在**八个**老龄化队列上的示范。从"这个判据在这 6 条规则上过于宽松"推不出"复现计数不能建立可迁移性"。此外 Conclusion 与 Abstract 的语气会被临床读者读成"目前这些暴露组规则不应用于筛查"——这是一个**政策含义**，但稿件从未在结论里正面表述（既没说"不应使用"，也没说"可以谨慎使用"），却通过"none was reliably transportable"暗示了它。这是"结论走出了证据"的典型形态：**暗示了没被证明的东西，同时回避了真正需要表态的东西**。
- **为什么是问题**：（a）普遍化超出单案例设计；（b）对实践的含义被暗示而非论证，读者无法判断作者到底建议什么。
- **具体修改建议**：（1）所有"counting replications cannot…"改为"这一判据在本规则基上未建立任何规则的可迁移性；是否具有一般性需要独立评估"；（2）在 Conclusion 加一句明确表态，例如"在本层证据下，这 21 条规则中没有任何一条达到了可用于临床风险分层的证据标准；把它们部署为筛查工具为时过早"——如果要说不，就明说。

---

**M13 · 摘要与正文把"地区反转"当作与结果层同级的发现，但它是**两个不同层**的产物，且用词"reversed by region"与 Table 5 的数值不完全一致**
- **位置**：Abstract（L34–36：`Smoking–cataract reversed by region (SHARE 1.11, 1.04–1.18; CLHLS 0.748, 0.64–0.87)`）、Results（L387–390：`Europe 1.08 versus Asia 0.75 and the Americas 0.70`）。
- **问题**：Abstract 给出的 SHARE 值 1.11 是**队列点估计**，而 Results/Discussion 给出的 Europe 1.08 是**地区合并值**；Abstract 的 CLHLS 0.748 是队列点估计，而 Asia 0.75 是**合并值**（CLHLS 0.748 与 LASI 不可测）。三处数字来自不同聚合层次，读者无法对齐。更基本的是：Abstract 用括号并列两个**队列**值来支撑一个**地区**论断（"reversed by region"），属于聚合层次的偷换。
- **为什么是问题**：这是可核查的数字表述不一致，且恰好落在摘要的结论句上。
- **具体修改建议**：Abstract 改为"Smoking–cataract differed in sign across cohorts (SHARE 1.11, 1.04–1.18；CLHLS 0.748, 0.64–0.87；ELSA 0.77；CRELES 0.70)，and the pooled estimate was null (0.84, 0.67–1.05)"——用队列间差异而不是"地区"来表述；若保留地区，则统一用合并值并给出列名。

---

**M14 · 标题、摘要与正文的"pre-registered"密度过高且与实际预注册范围不符**
- **位置**：标题（L1）、Abstract Methods（L11–12、L17–19）、Introduction（L92–96）、Methods（L141–143）、Results（L284–292、L329–331）。
- **问题**：稿件在标题、"pre-registered three-state standard"、"The eight-cohort layer was pre-registered, including its testable rule set, its per-cohort BMI cut-point, its covariate set and its transportability criterion"等处反复强调预注册。核对 analysis_plan.md 后：**确实**预注册了判据、切点、协变量、可检验规则集（§19.6/§19.7），这一点作者做得好。但（a）地区亚组、异质性感知判据、meta-regression、E-value、leave-one-out 均**未**预注册；（b）项目内还有大量协议偏离（§0.1–§0.5 共 18 条更正，含 KNHANES 帧重建、CHARLS 与 NHANES 的 C1 类错误三次复发、引文门修复）。稿件把这些偏离完全移出了本文视野（KNHANES/CHARLS 只在 Methods L136–140 一笔带过）。
- **为什么是问题**：把"pre-registered"作为标题级卖点，就必须承担披露全部未预注册分析与偏离的义务。目前读者得到的印象是"这篇稿子的分析几乎全部预注册"，与材料不符。此外，C1 类错误（条件题当全样本题）在本项目**已发生五次**（analysis_plan §19.5 明载），这在方法学上是实质性的内部效度威胁，稿件却在 Results/Power 段落里把它作为"我们做得很细致"的例子呈现（L194–199），没有把它作为局限报告其可能残留的影响。
- **具体修改建议**：补一段 **Pre-registration and deviations**（可置于 Methods 末尾或补充材料）：列明哪些分析是预注册的、哪些是事后的、以及关键数据修正及其对 headine 的影响（至少列出 C1 类错误在 SHARE/HRS/ELSA/MHAS 的条件题处理与 reference-rate 门的通过情况）；标题中的"pre-registered"可以保留，但摘要不宜再三重复。

### 次要（10 条）

| # | 位置 | 问题 | 修改建议 |
|---|---|---|---|
| 1 | Table 5 r13 行（L385/L1040）vs Results（L359–360） | 同一量在表中为 **1.13**，在正文中为 **1.14**（Results 写"r13 在 SHARE OR 1.24…so it rests on a single cohort"，但 pooled 值两处不一致）；Table 5 的 r02 CI 写 1.32–2.88，Abstract 写 1.33–2.88 | 全稿数字单一来源化（Methods L277–278 已承诺"no reported number exists in only one place"），逐表逐段核对 |
| 2 | 内部修订代号泄露：Abstract（"R11-corrected gold"）、Results §System performance（L478）、图例 Figure 2/3/5（L719、L731、L735、L769） | 稿件正文出现 **R5/R11/R12、intval-nhanes、configs/rules.yaml、.executor/progress.json、DualLLMClient、backend.renderer** 等纯粹的项目内部标识与文件路径 | 全部删除或改为读者可懂的表述；Figure 5 的"n 以 .executor/progress.json 为准"必须给出实际 n |
| 3 | Intro（L91）vs Results（L333） | 规则数 21 vs 分析计划 §1 记载 r15（镉×白内障）已撤销、v1.2 为 21 条含探索性扩展 r22；正文从未说明 r22 是"探索性扩展"及其 test-set fitting 历史 | 在 Table 2 与 Methods §The rule base 明写 r22 的探索性定级与来源；说明 r15 撤销 |
| 4 | Methods（L217–219） | "cataract (five cohorts)"，但实际可检验白内障的队列为 SHARE/CLHLS/CRELES/ELSA 四个（KLoSA 只有手术史、HRS 只有 KC098 手术项） | 改为"four cohorts contributed analysable cataract items; KLoSA and HRS contributed surgery/treatment items only and were not substituted" |
| 5 | Methods §Statistical analysis（L240–248） | 未给年龄的函数形式；未说明是否检验 age×exposure 交互；SHARE 插补的 Rubin 合并只对点估计与方差，未说明是否对 q 值合并 | 补足；给出年龄项设定与交互检验结果 |
| 6 | 全稿 | **无任何 sex/gender 分层或差异分析**，age 与 sex 仅作协变量；Lancet 有明确期待 | 至少补一项按性别的 r02/r10/r20 分层敏感性分析，或明确声明为何不做 |
| 7 | Results（L439–449） | 探索性三方向未报 q 值（LASI glaucoma q 与 HRS smoking q 给了，KLoSA 的 1.50/1.99 未给） | 补全 q 与 CI |
| 8 | Table 5 脚注（L1029–1032） | "Pooled with Python/scipy; no external meta-analysis package was used"——REML τ² 自己实现，未给验证 | 至少与 `metafor::rma`（R）的结果对拍，报告一致性 |
| 9 | Results（L411–412、L587） | "Leave-one-cohort-out analysis shows…"在 Results 与 Discussion 各出现一次，但全文**没有对应表/图**，仅 cohort_heterogeneity.json 有 `n_influence_rows: 13` | 补补充表；或删去该论断 |
| 10 | 图例 Figure 8（L809） | "18 pairs across 6 rules and **7 cohorts**"与正文的"eight cohorts"不一致（见 M5）；另 Figure 8(b) 说"ELSA 与 CRELES 的 r10 区间跨 1 而点估计与其余队列方向相背者…不得读作分歧"——这句话是**指导读者**如何解读，属于论证的一部分，不应写在图例里 | 图例只描述图形；该解读移入正文；统一 7/8 队列口径 |

### 需澄清（8 条）

| # | 需澄清的问题 | 为什么需要澄清 |
|---|---|---|
| C1 | 多重校正为何选 **BHY** 而非 BH？请给出 BH 下的三态表 | 见 M11：CRELES r02 的 q=0.0506 在 BH 下可能翻转为 replicated，直接影响"3/4"与摘要 |
| C2 | Table 5 的"Regional subgroup difference"列与 Q p 值在 r12/r13 上**完全相同**（0.027334 / 0.027220）；请说明该列是否就是 Q 检验的重复呈现 | 见 F2/F3：若相同，则该列不构成独立的地区证据，Abstract 的"regional subgroups differed"属误述 |
| C3 | 自报白内障与青光眼在各队列的医疗卫生可及性差异如何？请报告每队列自报白内障患病率与白内障手术率（若有） | 决定"direction reversal"应解释为生物学效应修饰还是诊断可及性差异（见 F4、M2） |
| C4 | CLHLS 的 `diabetes`/`hyperglycemia`（自报 1.36%）与 LASI（12.1%）、HRS/SHARE（21–23%）的口径差异是否被承认？r02 的"高血糖"实质是"已诊断/已治疗糖尿病"吗？ | 直接关系 r02（两条可迁移规则之一）在低资源环境的可解释性；自报 1.36% 与 CLHLS 人群真实糖尿病患病率相差一个量级 |
| C5 | Table 7 的 `exposure_missing: 41` 与 `outcome_missing: 26` 具体是哪些 cell？为何 41−26=15 恰好等于"加眼底影像解锁的 +15"？两者是否混淆？ | 读者无法核实 modality 排序的逻辑；若 +15 实为 outcome_missing 的重新计数，则"fundus imaging +15"的政策排序依据不成立 |
| C6 | Methods 的 BMI 切点表述（Asian→25 / others→30）与 §19.7（KLoSA/MHAS/LASI/CLHLS→25；SHARE/HRS/ELSA/CRELES→30）**在结果上一致**，但请在正文明确 SHARE/ELSA 用 30、并给出 alternates 的敏感性结果 | r13 的 SHARE 复现（1.24）依赖 30 这个切点；mapping 文档显示 SHARE 的 `bmi_high_25` 会 FAIL。切点选择决定该规则的唯一复现 |
| C7 | $r20$ 的 outcome 是 moderate **or** severe 的并集；若同一人同时满足两级，是否被重复计数？请给出 flag 定义与 n | 影响 Table 6 的 n 与三态判定 |
| C8 | 探索性分析报告的"68 pairs analysed in total"（Results L442）与 confirmatory 的 18 对、以及 Methods 的双家族定义如何对应？ | 读者无法重建探索性家族规模 |

---

## 措辞收紧清单（原文 → 改法，逐条）

> 说明：以下"原文"均引自 outputs/paper/manuscript.md 与 sections/*.md，行号为 manuscript.md。

1. **摘要 Conclusions（L40–43）**
   - 原文："Transportability could not be established by counting replications, and pooling concealed a directional conflict rather than resolving it. For ophthalmic exposome screening the limiting factor is measurement, not sample size."
   - 改法："Under the criteria tested here, no rule was reliably transportable: the two rules that met the pre-registered criterion had prediction intervals spanning the null. Where cohort estimates conflicted, the pooled estimate was null; reporting a pooled value without a prediction interval would have made that conflict invisible. Within this rule base, the observable constraint on external validation was measurement rather than sample size."
   - 理由：把"pooling concealed"（对方法的普遍指控）改为"报告方式会使冲突不可见"（本稿真正证明的）；把"measurement, not sample size"限定在"within this rule base"。

2. **摘要 Results（L34–36）**
   - 原文："Smoking–cataract reversed by region (SHARE 1.11, 1.04–1.18; CLHLS 0.748, 0.64–0.87) and its pooled estimate was null (0.84, 0.67–1.05) while regional subgroups differed (p < 0.0001) — a summary describing no population studied."
   - 改法："Smoking–cataract differed in sign across cohorts (SHARE 1.11, 1.04–1.18; ELSA 0.77; CLHLS 0.748, 0.64–0.87; CRELES 0.70) and its pooled estimate was null (0.84, 0.67–1.05). A post-hoc grouping by region showed the two subgroups differed (p < 0.0001). The pooled value describes no population studied."
   - 理由：M13（聚合层次偷换）+ F3（地区分组须标 post-hoc + 给出组内构成）。

3. **标题（L1）**
   - 原文："Pooling conceals directional conflict: a pre-registered cross-cohort evaluation of 21 literature-derived exposome rules for major eye disease in 2.0 million person-waves"
   - 改法（建议）："A pooled estimate that describes no population: cross-cohort transportability of 21 literature-derived exposome rules for eye disease in eight ageing cohorts"
   - 理由：F2（中心论断超出证据）+ M6（"2.0 million person-waves"注水）。若保留原题，至少把"conceals"改为"can conceal"并把副标题的样本量改为队列数与人数。

4. **Discussion §Principal findings 第二段（L504–511）**
   - 原文："Second, **pooling does not resolve a directional conflict; it conceals one.**… This is the more general hazard: a rule base whose components disagree across populations will produce a bland summary whenever it is meta-analysed, and the disagreement will be invisible unless heterogeneity is reported."
   - 改法："Second, **the pooled estimate was uninformative about the population-level conflict it averaged over.**… The general hazard is not meta-analysis itself but reporting it without a prediction interval: a rule base whose components disagree will then produce a summary that describes no population in the analysis, and the disagreement will not be visible to the reader."
   - 理由：把批评对象从"合并"移到"不报预测区间的报告实践"——与本稿实际做法（报了）自洽。

5. **Discussion §Principal findings 第一段（L496–502）**
   - 原文："**the transportability of a literature-derived exposome rule cannot be established by counting how many cohorts replicate it.**"
   - 改法："**In this rule base, transportability was not established by counting how many cohorts replicated a rule.**"
   - 理由：M12（单案例不能推普遍命题）。

6. **Discussion §Principal findings 第三段（L513–520）**
   - 原文："**for this rule base the binding constraint is measurement, not sample size.** Of 168 possible (rule × cohort) cells across eight cohorts holding two million person-wave records, 18 were feasible."
   - 改法："**for this rule base the observable constraint on external validation was measurement, not sample size.** Of 168 possible (rule × cohort) cells across eight cohorts holding two million person-wave records (137,183 unique participants in the largest and 2,827 in the smallest), 18 were feasible."
   - 理由：M6（拆解样本量卖点）+ F4（把技术结论限定在可观察层面）。

7. **Discussion §Selective survival（L538–542）**
   - 原文："This explanation predicts that the protective direction should strengthen with increasing cohort age. It does not: the meta-regression slope on mean age was −0.008 log-OR per year (p = 0.52)… The evidence for selective survival is therefore indirect and, on this design, unconfirmed."
   - 改法："This explanation predicts that the protective direction should strengthen with increasing cohort age. An ecological meta-regression of cohort mean age had almost no power to test that prediction with four cohorts (slope −0.008 log-OR per year, p = 0.52), and selective survival operates at the individual level, so this test neither supports nor excludes the explanation."
   - 理由：M4（把"无证据"当"证据不存在"；生态学回归不能检验个体层面机制）。

8. **Discussion §Unmeasured confounding（L544–551）**
   - 原文："An unmeasured confounder associated with both smoking and cataract by a risk ratio of roughly 1.5 to 2 would suffice to move either estimate to the null. That is a modest requirement…"
   - 改法（补一句）："…That is a modest requirement, and it applies to both directions of the association: the SHARE risk-increasing estimate is itself only marginally robust (E = 1.46), so neither sign can be treated as established."
   - 理由：M8（脆弱性分析应同时削弱"风险升高"一侧，不能只用于攻击 CLHLS 的保护向）。

9. **Discussion §Measurement as the limiting factor（L615–620）**
   - 原文："These are not exotic measurements; they are standard in ophthalmological field studies and in several population cohorts outside this set."
   - 改法："These are standard measurements in ophthalmological field studies and in several population cohorts outside this set — though whether they are deployable in the ageing cohorts of India, China, Mexico and Costa Rica is a separate question that this layer cannot answer."
   - 理由：F4（这句话在四个中低资源国家队列上恰好不成立；这一句是全文离公平性最近的地方）。

10. **Discussion §Comparison with the internal layers（L629–636）**
    - 原文："The cohort layer does not reproduce the pattern of the NHANES and KNHANES layers. There, no rule-relevant pair was contradicted in either country, and declared-domain precision was 1.00 in both."
    - 改法：整节删除（或整体移入补充材料）。若保留，改为一句："Cross-layer comparison is not attempted here because the two layers use different outcome instruments and different denominators."
    - 理由：审稿清单第 6 项：这半篇属于另一篇论文；把它留在主文会让读者以为两层结论需要一起解读。

11. **Discussion Limitations Ascertainment（L651–655）**
    - 原文："Cataract and glaucoma are self-reported physician diagnoses throughout this layer. The NHANES layer used examination-based grading, so the two are not comparable in effect size and we draw no such comparison. Self-report introduces differential under-ascertainment where access to care differs, which is itself correlated with the exposures of interest."
    - 改法（在其后补两句）："The same concern applies **within** this layer: self-reported cataract prevalence ranged from 8.4% (SHARE) to 38.5% (CRELES/CLHLS), differences that plausibly reflect access to cataract surgery and diagnosis rather than disease occurrence. We therefore treat differential ascertainment, not only differential biology, as a candidate explanation for the between-cohort differences reported below."
    - 理由：M2（消除 Limitations 与 Results 的自相矛盾）。

12. **Discussion Limitations CLHLS severe vision（L670–672）**
    - 原文："**CLHLS severe vision.** The severe-impairment flag in CLHLS exceeded its age-unstratified plausibility band (25.7% at a mean age of 92). It is reported as a secondary analysis only, and no primary conclusion depends on it."
    - 改法："**CLHLS severe vision.** The severe-impairment flag in CLHLS exceeded its age-unstratified plausibility band (25.7% at a mean age of 92) and was pre-registered for secondary analysis only. It nonetheless contributes to the r20 estimate in CLHLS (OR 1.03, interval including 1); a sensitivity analysis excluding it is reported in the supplement."
    - 理由：M10（这句话当前可被 Table 6 直接证伪）。

13. **Results §Cross-cohort transportability（L327–331）**
    - 原文："…re-evaluated in eight population-based ageing cohorts on three continents…"
    - 改法："…re-evaluated in eight population-based ageing cohorts on three continents, of which **seven contributed analysable pairs** (MHAS contributed none; see supplement)…"
    - 理由：M5（MHAS 零贡献未披露，且与 Figure 8 的"7 cohorts"矛盾）。

14. **Results §Between-cohort heterogeneity（L387–390）**
    - 原文："…even though the regional subgroups differ significantly (Europe 1.08 versus Asia 0.75 and the Americas 0.70, p < 0.0001): **pooling averages a real directional conflict into a result that describes no population in the study.**"
    - 改法："…even though a **post-hoc** grouping by region (America 0.70, one cohort; Asia 0.75, two cohorts; Europe 1.08, two cohorts) differed (p < 0.0001): the pooled value averages over cohorts that disagree and describes no population in the study."
    - 理由：F3 + M9（标注 post-hoc、给出每组队列数、说明组内 n=1 的事实）。

15. **Figure 8 caption（L801）**
    - 原文："Only 6 of the 21 literature-derived rules can be tested in the eight ageing cohorts, and of those just two transport."
    - 改法："Only 6 of the 21 literature-derived rules can be tested in the eight ageing cohorts (seven contributed analysable pairs). Under the pre-registered criterion two rules were transportable; under a post-hoc criterion requiring a prediction interval excluding the null, none was."
    - 理由：图例给出的是最容易被单独引用的数字，必须与正文的双判据结论一致。

16. **Results §The internal layers（L313–319）**
    - 原文："Because the gap between 1.00 and 0.375 is the largest single lever on the headline figure, the sensitivity analysis (Table 3) reports four alternative rule sets."
    - 改法（建议删整节）："The internal-layer results are reported in the supplement; the present paper concerns the cohort layer only."
    - 理由：清单第 6 项——半篇 LLM 系统评测应从主文移除；"headline figure"这样的内部措辞也应删除。

---

## 附：本次审稿的证据核验记录（供编辑复核）

| 核验项 | 来源 | 结果 |
|---|---|---|
| §19 是否预注册地区亚组 | analysis_plan.md 全文 `region|regional|subgroup|moderator|meta-regress` 检索 | **零命中**；§19.7 只预注册迁移判据、切点、协变量、双家族 FDR |
| 地区 p 与 Q p 是否同值 | cohort_heterogeneity.json L124–217 | r12: Q_p=0.027334 = p_between=0.027334；r13: Q_p=0.027220 = p_between=0.027220（k=2，df 均为 1）→ 同值 |
| 地区组构成 | cohort_heterogeneity.json per_group_OR | r02: Americas=1.3116（=CRELES 单点），Asia=1.9253（CLHLS 3.5887+LASI 1.8782），Europe=1.7539（SHARE 单点） |
| MHAS 贡献 | evidence_audit.json feasible_pairs | **18 对中无一条含 MHAS**；涉及队列 = SHARE/HRS/ELSA/KLoSA/LASI/CLHLS/CRELES（7 个） |
| CLHLS 视力构念 | cohort_variable_mapping.md C25（L855–862）、C65（L568–604） | `g1` = "can you see the break in the circle?" 功能测试；2000 波仅 3 级；修正后 severe=25.7% |
| CLHLS severe 的使用约束 | analysis_plan.md §19.3 脚注、§19.8(1) | "仅作次要分析，主要分析排除"——但 Table 6 的 r20@CLHLS 使用该合并口径 |
| 条件题（C1 类）错误次数 | analysis_plan.md §19.5（L507–509）、§0.3/§0.5 | 已发生五次（NHANES SMQ040、KNHANES BS1_1、CHARLS da061、SHARE br002_、E_DR 语义错） |
| 探索性家族规模 | cohort_transportability.json | `n_pairs: 68` |
| 影响力分析产物 | cohort_heterogeneity.json | `n_influence_rows: 13`（主文无对应表/图） |
| r22 的定级与历史 | analysis_plan.md §0（L8–20）、§0.1 更正 1 | 探索性扩展，evidence_level C、severity low，源于 test-set fitting；正文未说明 |
| BMI 切点分配 | analysis_plan.md §19.7（L560–563） | KLoSA/MHAS/LASI/CLHLS→25；SHARE/HRS/ELSA/CRELES→30（与 Methods 表述一致，但正文未说明 SHARE/ELSA 用 30） |
| CRELES r02 临界值 | cohort_transportability.json | OR 1.3116（1.0705–1.6069），q_primary = 0.05059 |

**审稿人自我更正留痕**：初稿的 M7 关于 BMI 切点的判断经复核后不成立（Methods 的"Asian→25 / others→30"与 §19.7 的分配在 8 个队列上完全吻合），已降级为需澄清 C6，并保留编号空洞以维持与早期通信的可回溯性。

---

*报告完。核验共查阅：manuscript.md（1104 行）、figure_legends.md（268 行）、analysis_plan.md（602 行）、cohort_transportability.json、cohort_heterogeneity.json、evidence_audit.json、cohort_variable_mapping.md（局部），以及 sections/discussion.md、sections/abstract.md。*
