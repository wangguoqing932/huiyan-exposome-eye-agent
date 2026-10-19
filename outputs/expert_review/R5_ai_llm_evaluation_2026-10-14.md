# R5 专家评审报告：AI/LLM 系统评测视角（基线公平性 · 输出稳定性 · RAG 评测）

- 评审人角色：医学 AI / LLM 系统评测（RAG 评测、基线公平性、LLM 输出稳定性）
- 评审日期：2026-10-14（writer 阶段前最后一轮，R5）
- 评审方式：只读评审。全部结论基于源码/数据文件核验 + 本地只读重算（指标复算、McNemar/paired bootstrap、v1.1 规则集回放、lightrag 两代重放比对）。未调用任何 LLM 跑新基线，未修改项目任何文件（本报告除外）。
- 评审对象：`src/huiyan_agent/`（llm_client / lightrag_adapter / evidence_store / naive_rag / risk_rules）、`scripts/run_baselines.py`、`scripts/run_multiseed.py`、`scripts/evaluate.py`、`outputs/baseline_*`、`outputs/figures/contracts/figure2_performance.yaml` + `source_data/figure2_performance.csv`、`outputs/README_baseline_predictions.md`、`R4_FIXLOG_2026-10-14.txt`、`AUDIT_R4_FULL_2026-10-14.txt`、`docs/analysis_plan.md`、`docs/limitations.md`、`outputs/confirmatory/*`、`outputs/source_coverage_report.json`、`app/streamlit_app.py`（略查）。

---

## 一、总结论

**数据管道与失败治理是可信的，但"4 基线对比"这一核心结果目前既不公平也不显著，不能以现在的形态写进论文。** 具体为三点：

1. **（P0）full_system 的 R=1.0（进而 F1=0.583"最高"）由事后规则扩展构造而来。** analysis_plan §0 已诚实记录 v1.2 的 r02/r03/r04 交叉覆盖 + r22 新增是"测试集拟合"，但 figure2 的 source_data 只给了 writer 一行 v1.2 full_system 数据。我用 v1.1（20 条）规则集在同一 71 对上回放：full_system(v1.1) **TP=1, FP=10, FN=6, P=0.091, R=0.143, F1=0.111**——在 4 基线中垫底（低于 naive_rag 0.182）。若 figure2/正文只呈现 v1.2 的 0.583 并写"highest F1"，等于把 test-set fitting 的产物当性能证据，审稿人复算规则时间线后必然击穿。
2. **（P1）0.583 vs 0.421 的领先在统计噪声之内。** 71 对配对比较，full_system vs pure_llm 的 McNemar 精确检验 b=8, c=7, **p=1.000**；paired bootstrap ΔF1 的 95% CI 为 **[-0.100, 0.452]**，跨零。"descriptive only" 的契约声明是对的，但 core_conclusion 里 "attains the highest F1" 的排序表述必须拿掉或降级（vs lightrag 的领先是真的：McNemar b=19, c=2, p≈0.0002）。
3. **（P1）"temp=0.7, seed=11" 的 seed 从未真正传给推理服务**——只写进了 jsonl 元数据。llama-server 每次请求自行取随机种子，所以"seed=11"不提供任何可复现性；预注册的 5 seeds（analysis_plan §9）也从未执行（`run_multiseed.py` 是 return 1 的占位）。且 3 个 LLM 基线各只有 1 次抽样运行，temp=0.7 下的运行间方差从未测量。

另有两处"基线名不副实"（naive_rag 实际用了带等级加权的系统检索器；lightrag 实际走 naive 纯向量模式、不走 KG 图结构，且"KG evidence"是同一模型 temp=0.7 自生成的综合文本）和一处机器可读文件自相矛盾（full_system provider 标成 deepseek:legacy）。

**修复成本评估：P0/P1 中除"用自然语言实体名重跑 LLM 基线"外，全部可在本地零 API 成本完成（补 5 seeds 本地跑约 71×3×4 次 0.3s 级调用；v1.1 回放已有现成数据）。**

---

## 二、P0（评测口径硬伤：结果不可信/不可比）

### P0-1 figure2 只给 writer v1.2 full_system 数据，"highest F1" 结论由 test-set fitting 驱动

**证据**
- `docs/analysis_plan.md` §0（行 8–30）：2026-10-12 07:12（确证运行之后、基线运行之前）修改 r02/r03/r04 flags 并新增 r22；原文自认"**测试集拟合（test-set fitting）**……R=1.000 是构造的，不是性能提升"。
- 我用 `configs/rules.yaml` 回退上述改动（r02 A=['hyperglycemia']、r03 A=['hba1c_elevated']、r04 A=['hba1c_elevated']/B=['dr_pdr']、删 r22）在 `outputs/confirmatory/nhanes_confirmatory.csv` 的 71 个 tested 对上重跑 `match_rules`：**v1.1 full_system = TP 1 / FP 10 / FN 6 / P 0.091 / R 0.143 / F1 0.111**；漏掉的 6 个阳性恰好是 r02/r03/r04 扩展与 r22 覆盖的对（hba1c×cataract、hyperglycemia×retinopathy/npdr、hba1c×npdr、bmi×retinopathy/npdr）。与归档 `outputs/confirmatory/archive_v1.1/`（NHANES 8 rule pairs / 1 replicated / cov 0.154）交叉验证一致。
- `outputs/figures/source_data/figure2_performance.csv` 只有 4 行，full_system 仅 v1.2 一行（F1 0.583）；契约 `figure2_performance.yaml` 行 14–20 core_conclusion 写 "the full 慧眼 system attains the highest F1 (0.583…)"；行 163–164 的 mitigation 只要求 caption 注明，且引用的 "v1.1 metrics (archive_v1.1/)" 里**没有** 4 基线对比口径的 v1.1 full_system 数字。

**为什么是 P0**：这是同一测试集上"先看答案再改规则"的构造性结果，与单次抽样的 LLM 基线同图排名即是不可比。任何审稿人对照 analysis_plan §0 时间线（07:12 改规则 → 07:13 跑基线）都能发现；figure2 若照现契约渲染即为过度声明。

**修法（具体）**
1. `figure2_performance.csv` 增加 `full_system_v1.1` 行（TP1/FP10/FN6, P=0.091, R=0.143, F1=0.111），panel_a 画成 v1.1/v1.2 双柱或以 v1.1 为主、v1.2 标注 "exploratory extension (post-hoc)"。
2. core_conclusion 删除 "attains the highest F1"，改为事实性陈述：v1.2 扩展后 F1 0.583，但其 R=1.0 源于 gold-positive 驱动的规则扩展（引用 analysis_plan §0），不构成泛化性能证据；v1.1 口径下 full_system F1=0.111。
3. 正文/表格同样双版本呈现（analysis_plan §0 处置第 3 条本来就是这么要求的）。

---

## 三、P1（重大：审稿人大概率攻击）

### P1-1 full_system vs pure_llm 的 F1 差异不显著；契约措辞仍是排序性声明

**证据**：我用 `baseline_predictions_valid.jsonl` 284 行做配对分析（本机只读重算）：
- McNemar（逐对 correct/incorrect）：full_system vs pure_llm **b=8, c=7, exact p=1.000**；
- paired bootstrap（resample 71 对，B=5000, seed=42）：ΔF1 均值 0.166，**95% CI [-0.100, 0.452]**，P(Δ≤0)=0.119；
- full_system vs lightrag：b=19, c=2, **p≈0.0002**（这个领先是真的）；vs naive_rag 同样显著。
- `figure2_performance.yaml` 行 18–20、行 39 已声明 "single run; descriptive; no significance testing"，但行 14–15 的 "attains the highest F1" 与该声明自相矛盾。

**修法**：core_conclusion 改为"full_system(v1.2) F1=0.583，与 pure_llm 0.421 的差异在 71 对上不显著（McNemar p=1.0；ΔF1 bootstrap 95% CI 跨零），显著高于 lightrag/naive_rag（p<0.001）"。既然我一条只读脚本就能算出，writer 阶段补这两行统计零成本；不做，审稿人自己会算。

### P1-2 seed 未传入推理 API；"seed=11" 无可复现语义；预注册 5 seeds 未执行

**证据**
- `scripts/run_baselines.py`：`--seed` 只进入结果 dict 的 meta（行 113/121/157/177/197），从未调用 `random.seed()`，也从未作为 API 参数发送。
- `src/huiyan_agent/llm_client.py` `_chat`（行 212–218）与 `_chat_urllib`（行 226–231）：请求体只有 model/messages/temperature/max_tokens(+extra_body)，**无 seed 字段**。llama-server 未收到 seed 时每次请求自选随机种子。
- 因此 `baseline_summary_v12.json` 行 4、`figure2_performance.yaml` 行 40、`limitations.md` §5、`performance_by_dataset.csv` 中 "seed 11 / seed=11" 均为"标签"而非"控制"。
- `scripts/run_multiseed.py` 行 15–20：多种子实现是 stub，直接 `return 1`；`analysis_plan.md` §9（行 103–105）预注册 "4 基线 × ≥5 seeds，seed 列表 [11,22,33,44,55]"，实况 n_seeds=1（`performance_by_dataset.csv` 自己也记了 n_seeds=1）。该偏离未进 §0 偏离记录。
- `baseline_fullsystem_bootstrap_ci.json` 行 32 把补种子挂在"DeepSeek 额度恢复"上——但现行基线已是本地 llama-server，跑 4 个额外种子不花任何额度（71 对 × 3 基线 × 4 seed ≈ 852 次 0.3s 级调用）。

**修法**
1. `llm_client._chat/_chat_urllib` 增加 `seed` 入参并在请求体透传（OpenAI 兼容端点与 llama-server 均支持），`run_baselines.make_llm` 接 seed；
2. 本地补跑 seeds 22/33/44/55（同 temp=0.7），报各基线 mean±std（`run_multiseed.py` 顺手实现，验收标准已写在其 docstring）；
3. 论文与 summary/figure2 中的表述改为实测口径："temp=0.7, k=5 independent runs（或如实写 single run）"；§0 偏离记录补记 seed 未执行的偏离。
4. 若不补跑：至少在 limitations 写明"seed 仅作运行标识未传入服务端，单次运行结果受 temp=0.7 采样噪声影响"。

### P1-3 naive_rag 基线接的是系统检索器（EvidenceStore 等级加权），不是专门写的公平版 NaiveRAG

**证据**
- `scripts/run_baselines.py` 行 167–175：`from huiyan_agent.evidence_store import EvidenceStore; store = EvidenceStore(); evidence = store.retrieve(query, top_k=3)`。
- `src/huiyan_agent/evidence_store.py` 行 6–8、21、112–113：retrieve 是 **risk-guided 等级加权检索**（title×3/实体×2/正文×1，再乘证据等级权重 A=5.0/B=4.0/C=3.0 与 chunk weight）——这是 full_system 的组件。
- `src/huiyan_agent/naive_rag.py` 行 1–4、19：项目专门写了 `NaiveRAG`（纯词频、无等级加权、无实体强匹配），docstring 明言"关键词检索基线（**4 基线对比中的 naive_rag 档**）……基线公平性"，但 `run_baselines.py` 从未引用它（全仓 grep 只有定义处）。

**影响**：论文若把该档描述为 "naive keyword retrieval"，与实现不符（实际多了等级加权与权重乘子）；同时 `top_k=3`（非默认 5）未披露。审稿人读代码即见。

**修法**：要么把 runner 切到 `NaiveRAG`（符合命名与论文叙事），要么改名/如实描述该档为 "level-weighted lexical retrieval (system retriever, top-3)"。两者任选，重跑本地零成本。

### P1-4 lightrag 基线走 naive 模式（不用 KG 图结构），"KG evidence" 是同模型自生成文本——FP=25/30 的机制解释必须按此写

**证据**
- `scripts/run_baselines.py` 行 194–196：`kg_result = adapter.query(query, mode="naive")`；query = "What is the relationship between {a} and {b}?"。LightRAG naive 模式 = 纯向量块检索 + **LLM 综合成自然语言答案**（该综合调用走传入的同一 qwen，temp=0.7，见 `lightrag_adapter.py` 行 124–156 的 llm_model_func）。kg_chars 分布 1374–4914、0 个为空（valid 视图统计），与"生成文本"而非"原始块拼接"一致。
- 因此最终判官看到的 "KG evidence: …" 是**同一个模型在 temp=0.7 下对预设性问题生成的综合**，再让它自己回答 YES/NO（system="Answer based on KG evidence"）。三重 YES 偏置：①"what is the relationship" 预设关系存在；②自生成证据自我强化；③无 abstain 选项。
- 实测：lightrag 30/71 判 YES（42%），FP=25，其中 2/3 个 contradicted 对（hba1c×vi_severe、alcohol×retinopathy_any）也判 YES（本报告重算）。
- `figure2_performance.yaml` panel_d（行 76–84）只画 kg_chars 分布，无机制解释；`limitations.md` §6 把倾向归到证据池发表偏倚——不完整。

**修法**：论文中该档描述为 "LightRAG (naive mode: vector retrieval + LLM synthesis)"，不得写成"知识图谱结构检索"；FP 过半的解释按上述三机制写，并注明与证据池偏倚（limitations §6）叠加。若想真测 KG 结构增益，补 hybrid/local 模式一档（本地可跑）。

### P1-5 lightrag 内部综合调用未纳入 fail-loud（残余 fail-open 洞）

**证据**
- `src/huiyan_agent/llm_client.py` 行 166–192：`complete()` 默认 `raise_on_error=False`，异常被吞成 `ChatResponse(text="[llm error] …", degraded=True)`。
- `src/huiyan_agent/lightrag_adapter.py` 行 144–156：`llm_model_func` 调 `self.chat.complete(prompt=…, system=…)` **未传 raise_on_error**，也不检查 `resp.degraded`；行 153 的重试循环只捕异常——而异常已被 complete 吞掉，重试永远不会触发。
- 后果：lightrag 基线跑批中若 API 故障，检索/综合会静默返回 "[llm error] …" 字符串当作 KG 证据进入最终 prompt；最终判官调用仍可成功 → 该对被计为有效预测。R4 的 fail-loud 只覆盖了 `_llm_predict` 的判官调用（run_baselines.py 行 129–144），未覆盖 adapter 内部调用。
- 本次运行 0 失败属运气（本地服务稳定），但"0 failures"的保证对该路径不成立。

**修法**：`llm_model_func` 改为 `self.chat.complete(prompt=…, system=…, raise_on_error=True)`（其 4 次指数退避重试本为此设计），并检查 `resp.degraded` 为 True 时抛错；canary 增加 `adapter.query("hyperglycemia × retinopathy", mode="naive")` 连通探针。

### P1-6 full_system 的 provider 标注 "deepseek:legacy" 与事实矛盾（机器可读文件自相矛盾）

**证据**
- `outputs/baseline_summary_v12.json` 行 41 与 `outputs/figures/source_data/figure2_performance.csv` 末行：full_system `provider="deepseek:legacy"`。
- 但 `run_baselines.py` 行 92–126：`run_full_system` 不构造任何 LLMClient、不发起任何 LLM 调用；`baseline_predictions_valid.jsonl` 中 71 行 full_system 记录**均无 provider 字段**（重算确认 providers: {None: 71}）。
- `docs/limitations.md` §5 行 34 自己写明 "full_system 为确定性规则引擎"。三处互相矛盾。

**修法**：summary 与 figure2 CSV 的 provider 改为 `deterministic:rule_engine_v1.2 (no LLM)`。这是 writer 直接消费的两个文件，5 分钟改完；不改则读者第一眼就困惑"确定性引擎为何有 LLM provider"。

### P1-7 limitations.md §5 的 lightrag 数字未随 2026-10-14 重跑级联更新

**证据**：`docs/limitations.md` 行 35、38 仍写 "lightrag 0.263"、"P=0.161（31/71 YES）"、"其 5 个 FP"——旧索引代数字；现行（重建索引）：F1=0.270、P=0.167、30/71、FP=25（`baseline_summary_v12.json` 行 28–38、`README_baseline_predictions.md`）。R4_FIXLOG 第 117 行声称级联更新了 summary/figure2/README/valid 视图，漏了 limitations.md。另 "其 5 个 FP" 与任何一代都对不上（旧代 FP=26、新代 FP=25），疑为笔误。

**修法**：同步为 0.270 / 0.167 / 30/71 / FP=25，并核对 §5 全段。

### P1-8 LLM 基线 prompt 直接喂内部 flag ID，未用 registry 人类可读名（对 full_system 的信息呈现不对等）

**证据**
- `run_baselines.py` 行 154、173、194：prompt 直接使用 `p['a_flag']`/`p['b_item']` 原始 ID，如 "Is hba1c_elevated a known risk factor for dr_npdr?"、"glaucoma_suspect_cdr"、"vision_impairment_moderate"。
- `src/huiyan_agent/normalize.py` 的 entity_b registry 已有 `generic_name`（"Non-proliferative DR"、"Glaucoma suspect (CDR)" 等，实测列出），但 runner 不使用；仅 lightrag 的 `_expand_bilingual`（lightrag_adapter.py 行 277–299）做了别名扩展。
- full_system 侧经 registry flag 解析匹配，不存在该损耗。三个 LLM 基线彼此一致（内部公平），但相对 full_system 构成系统性的呈现劣势，"npdr"/"cdr" 这类行话尤其可能拉低 pure_llm。

**修法**：至少在 limitations 披露"LLM 基线以内部 flag ID 提问"；更好是用 registry primary/generic name 生成 prompt 后本地重跑三基线（成本同 P1-2，可与补种子合并一次跑）。若重跑，须整套三基线同批重跑并全量替换，不得只换其一。

---

## 四、P2（建议）

### P2-1 三基线 prompt 非严格同文
pure_llm 问 "Is X a **known** risk factor…? Answer YES or NO **on the first line only**."（system="You are a medical knowledge classifier. Be concise."），naive_rag/lightrag 问 "Is X a risk factor…? YES or NO."（system 分别为 "Answer based only on provided evidence."/"Answer based on KG evidence."），canary 又是第三种问法（run_baselines.py 行 58–61 vs 153–181）。跨基线的 question 措辞与指令位置应统一（差异只保留检索上下文部分），否则 YES 率差异部分来自 prompt 而非检索。重跑时一并修复。

### P2-2 naive_rag 的 55/71 零检索主要由分词失配造成，解释要写透
查询串 "hyperglycemia retinopathy_any" 经 `_TOKEN_RE=[\w…]+` 分词后 "retinopathy_any" 是**单个 token**（下划线属于 \w），与证据正文中的自然词 "retinopathy" 永不命中（evidence_store.py 行 31、96–104 是子串匹配）。实测 55/71 对 n_evidence=0 → prompt 注入 "No evidence found." → 无 abstain 机制下全判 NO。naive_rag F1=0.182 主要测的是"词表失配 + 强制二答"，不是"RAG 不会推理"。论文按此解释，并把 n_evidence 分布（0:55 / 3:16）附上。

### P2-3 LLM 基线无 CI；建议统一 pair-level bootstrap
`baseline_fullsystem_bootstrap_ci.json` 只给 full_system（P [0.167,0.667], F1 [0.286,0.8]，B=2000 seed=42，方法与措辞 OK）。LLM 三基线无任何不确定度展示。建议用同一脚本对 4 基线都出 bootstrap CI，或在 figure2 panel_a 加 error bars——n_positives=7 的现实下，这比任何显著性检验都更需要让读者看见。

### P2-4 valid 视图里 full_system 行无 `valid` 字段
`baseline_predictions_valid.jsonl` 的 full_system 71 行没有 valid 键（生成时只有 LLM 基线被打标）。README 用 "`baseline == 'full_system'`" 特判兜住了，但下游再消费时是隐患。建议 valid 视图统一补 `"valid": true`。

### P2-5 README_baseline_predictions 补"复现命令"与模型指纹
现文件讲清了 4 代混存与过滤规则（好），但缺：生成 valid 代的精确命令行（可从 provider/seed 字段反推 `--provider local --seed 11`，不如写明）、本地模型指纹（qwen3.8-27b 3bit、llama-server 版本/启动参数）、以及"seed 未传服务端"的事实（P1-2 修复后一并写入）。

### P2-6 canary 不覆盖 lightrag 检索链路
canary（run_baselines.py 行 56–70）只测 judge 通道的连通与可解析性；历史上 lightrag 曾整代 valid=False（error="unparsable: 'BASED ON THE PROVIDED KG EVIDENCE…'"，本次从 jsonl 重放确认），说明检索链路（索引可开、综合可解析）需要自己的 canary。与 P1-5 一并修。

### P2-7 fail-loud/canary 无单元测试
`tests/` 仅 evidence_store/integration/normalize/risk_rules 四件；run_baselines 的失败计数、valid 标记、非零退出逻辑无回归测试。建议补 3 个用例（stub LLM 抛错→valid=False；unparsable→failures++；canary 失败→abort）。

### P2-8 "仅 1 对翻转"的稳定性声明限定语
重建索引前后两代 lightrag 确实只翻 1 对（我重放比对：crp_elevated×dr_npdr YES→NO，n_yes 31→30，声明属实）。但两代共享同一判官、同一 temp=0.7、语料基本相同，该比较度量的是"索引重建的影响"，不度量"运行间方差"（后者从未测过，见 P1-2）。论文表述建议写成 "index-rebuild sensitivity: 1/71 flip"，不要引申为 "output stability"。

### P2-9 关于 temp 0.0→0.7（W2）的历史变更
现 valid 代的三个 LLM 基线全部在 temp=0.7 下同批跑（2026-10-12），对比内部自洽，无需回滚；但论文方法节应记一句"早期 temp=0.0 的运行已随 fail-open 事故作废，不在任何指标中"，避免两个温度的数字被读者混引。

---

## 五、通过项（明确核查无问题的方面）

1. **指标数字本身可信**：我从 `baseline_predictions_valid.jsonl` 独立重算 4 基线 TP/FP/FN/P/R/F1，与 `baseline_summary_v12.json`、`README_baseline_predictions.md`、`figure2_performance.csv`、`performance_by_dataset.csv` 完全一致（full_system 7/10/0→0.583；pure_llm 4/8/3→0.421；lightrag 5/25/2→0.270；naive_rag 1/3/6→0.182）。full_system 基线行与 `nhanes_confirmatory.csv` 的 `predicted` 列 71 对逐一对齐（0 mismatch）。
2. **fail-loud 主路径实现到位**：`_llm_predict`（run_baselines.py 行 129–144）异常与不可解析均计数、error 落盘、run 标 valid=False 不入均值、任何失败非零退出；历史 fail-open 代（全 NO、无 provider）完整保留在 `baseline_predictions.jsonl` 作为失败证据，README 写明污染陷阱（实测旧代会把 pure_llm FN 3→10、F1 0.421→0.308）。canary 机制存在且每基线开跑前强制执行（本次各基线 0 失败与 jsonl 一致：valid 视图 284 行 0 个 error 字段）。
3. **gold 口径跨基线一致**：4 基线同 71 tested 对、同 gold3、同 positive=replicated、同 strict scoring（uninformative/contradicted 计负），与 headline precision_rule（排除负控与非可判、排除 uninformative）两种口径并行披露、未混用（figure2 契约行 30–34 明确要求两口径并报）。
4. **索引-规则版本绑定真实**：`.executor/progress.json` 三处 sha 一致（rules_yaml_sha256 == index_built_against_rules_sha256 == 5aee851d…），R4 重建（27,136 节点/23,722 边、注记 548/1054=52%、1054/1054 processed、B5 伪造标记 0）与 fresh 门全绿，防止索引与规则版本错配。
5. **lightrag 重建后重跑与级联更新**：summary/figure2/valid 视图/README/performance_by_dataset 五处均为重建后数字（0.270），"仅 1 对翻转"经重放验证属实。
6. **温度与 thinking 设置落在代码且有披露**：TEMPERATURE=0.7 硬编码于 runner 行 41；qwen `enable_thinking: False` 于 llm_client.py 行 211；论文 note/limitations 均注明（fast mode）。
7. **Streamlit app 与评估口径一致（略查）**：app 推理走同一 `risk_rules.match_rules/assess` 管道（streamlit_app.py 行 692–739 消费同一 RiskAssessment 结构），无规则命中渲染 UNKNOWN 弃权而非 LOW（与 risk_rules.py 审核 97 修复一致），与 full_system 基线同源。
8. **source_coverage_report**：21/21 规则全部有 literature 类来源覆盖（rules_covered=21, under_sourced=0），与 R4 引用门 21/21 PASS 一致。
9. **bootstrap CI 文件质量**：`baseline_fullsystem_bootstrap_ci.json` 的方法、B、seed、"deterministic → CI 仅反映有限测试集抽样不确定"的限定语均准确（唯一问题是 P1-7 指出的过期待办备注已更新、但 limitations 未跟上）。

---

## 六、修复优先级汇总（给 writer 前的 gate 建议）

| # | 级别 | 一句话 | 成本 |
|---|------|--------|------|
| P0-1 | 硬伤 | figure2 补 full_system_v1.1 行（F1=0.111），撤 "highest F1" 措辞 | 半小时（数据我已给全） |
| P1-1 | 重大 | 补 McNemar/bootstrap 两行统计，措辞降级为"与 pure_llm 不显著" | 半小时 |
| P1-2 | 重大 | seed 传入 API + 本地补 4 seeds 报 mean±std（或如实声明） | 代码 10 行 + 本地跑批 |
| P1-3 | 重大 | naive_rag 切 NaiveRAG 类或改名如实描述 + 重跑 | 本地跑批 |
| P1-4 | 重大 | lightrag 档改述为 naive 模式 + FP 三机制解释 | 写作层面 |
| P1-5 | 重大 | adapter 内部调用 raise_on_error=True + 检查 degraded | 3 行代码 |
| P1-6 | 重大 | provider 改 deterministic:rule_engine | 5 分钟 |
| P1-7 | 重大 | limitations §5 数字同步 0.270/0.167/30/71 | 10 分钟 |
| P1-8 | 重大 | prompt 用 registry 名重跑三基线（或披露） | 与 P1-2 合并跑 |
| P2-1..9 | 建议 | prompt 统一 / naive_rag 词表失配解释 / 全基线 CI / valid 字段 / README 复现段 / 检索 canary / 单测 / 稳定性限定语 / 温度史注记 | 随上述合并 |

**Go/No-Go 意见**：P0-1、P1-6、P1-7 是纯文档/数据修正，属 writer 前必须完成（半天内）；P1-2/3/5（+P1-8）建议合并成一次本地重跑（一次性解决 seed、检索器、prompt、fail-loud 残洞），否则论文的方法节将同时携带四处可被代码证伪的表述。P1-1/P1-4 是写作红线：任何"显著优于 pure_llm"或"KG 检索提升性能"的句子都会被击穿。
