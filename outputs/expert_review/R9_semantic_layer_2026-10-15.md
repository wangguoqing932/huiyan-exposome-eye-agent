# R9 复审报告：R6.0 语义检索层大工程优化（§15）科学闭环验证

- **审计日期**：2026-10-15
- **审计对象**：`docs/analysis_plan.md` §15（R6.0 预注册）、`scripts/run_fused_system_v3.py`、`src/huiyan_agent/semantic_retrieval.py`、`outputs/confirmatory/fused_system_R6.jsonl` + `fused_system_R6_summary.json` 及级联交付物
- **审计方式**：只读审计；指标从 jsonl 独立重算；向量解码手工复验；pytest 实跑；语义资产冒烟（不调外部 API 部分）
- **审计员**：科研复审审计员（R9 轻量复审）

---

## 总结论

**R6.0 语义检索层负结果科学闭环成立，8 项验证全部通过（其中项 1 附两处瑕疵备注，不影响结论科学性）。** 三项声明的负结果（G5a 无净增益 0.476 vs 0.500、G5b 零触发自锁、τ 三档恒等）经独立复算与逐对核验全部属实，未发现任何选择性报告或以 gold 调参的痕迹；"正式系统定格 G2"的决策在各交付物中级联一致。遗留 3 处披露精度问题（预注册时序证据缺失未像 §13 那样降格声明、chunk 数 1047 与实际 1054 不符、KNHANES 同对退化未明示），建议下一轮修订时统一补正，均不动摇结论。

---

## 逐项验证（1–8）

### 项 1｜预注册与实现一致性 — **通过（附备注）**

| 预注册要素 | §15 落盘文字 | 实现 | 一致性 |
|---|---|---|---|
| τ 主值 0.55 | L222"τ 主值 **0.55**（先验，非搜索）" | `run_fused_system_v3.py` L38 `TAU_MAIN = 0.55` | 一致 |
| τ 敏感性 {0.45, 0.65} 全报告 | L222 | L39 `TAU_SENS = [0.45, 0.65]`；jsonl 含全部 6 臂 | 一致 |
| 相关块判据 | L220"相似度 ≥τ 且（注记命中暴露或结局 flag 名 **或** 文本含双文献词）" | `semantic_retrieval.py` `filter_relevant` L101–120：`sim<τ` 滤除 → 注记子串命中（a_flag/b_flag 任一向）→ 否则文本双词子串 | 一致（构造用例验证四分支行为正确） |
| G5b 双注记门槛 | L226"等级 ≥B 者 ≥2 个且注记双命中（exposure 与 outcome 都在注记中）" | v3 L104–113 `dual = [c for c in rel if level≥B and flag_a 含 a_flag and flag_b 含 b_flag]`，`len(dual)>=2` | 一致 |
| G5a 结构 | L225"相关块最高等级 ≥B → YES；否则 LLM 仲裁" | 三分支镜像 §13 G2：B+→`sem_evidence_Bplus` YES；有相关块但 <B→仲裁；无相关块→`sem_no_relevant` 弃权 | **文字歧义**（见备注 c） |
| 阈值未被 gold 调整 | — | 三档结果恒等（无择优空间）；τ 常量与 §15 逐字对应；全 scripts 无 τ sweep 痕迹；且 R5/R6 两版 jsonl 的 judgeable/gold3/rule_ids 逐对完全相同（同口径同规则，不存在借道调参） | 支持 |

**备注**：
- (a) **时序证据弱**：§15 声称"预注册先于任何 R6.0 运行"，但 `analysis_plan.md` 未提交 git（工作树 M 状态，最后一次提交 10-12，早于 §15 存在）；文件 mtime 链为 `semantic_retrieval.py` 03:33:36 < `run_fused_system_v3.py` 03:34:37 < R6 输出 03:35:05 < `analysis_plan.md` 03:35:45（后者晚于运行系运行记录追加所致，策略段本身的落盘时间不可独立验证）。R8 复审已就 §13 同类问题要求降格披露（§13 已加"时序披露"句），**§15 未复制该披露句**——属同类遗留。
- (b) chunk 数：§15 写"1047 chunks"，vdb 实际 1054 条（pool 1060 条全量嵌入 vdb 者 1054，id 全部可回 join）。1047 与两者均不符，系记录笔误，无科学影响。
- (c) §15"否则 LLM 仲裁"未显式覆盖"无相关块"分支；实现按 §13 G2 三分支镜像（无相关→UNKNOWN 不仲裁），且 §15 运行记录自身以"关键词版判无相关证据弃权"描述 G2 行为，可证实现属合理镜像而非偏离。引用时以实现为准即可。

### 项 2｜向量库解码正确性 — **通过**

手工复验 `data/processed/lightrag_index/vdb_chunks.json`：`zlib.decompress(base64.b64decode(vector))` → `np.float16→float32`，**1054 条记录维度全部 2048**（文件自带 `embedding_dim: 2048` 字段）；抽第 1 条 raw norm=0.9985（Ark 输出近似归一），显式 L2 归一后 **norm=1.0**；全库逐一验证归一后 norm min=max=1.0。块首注记正则 `[exposure: … | outcome: …]` 抽样解析正确（多 flag 逗号分隔亦子串命中），注记覆盖 548/1054=52%，与 §15"52% 覆盖"一致。

### 项 3｜指标独立复算 — **通过（18/18 格全对）**

从 `fused_system_R6.jsonl`（143 条记录）独立重算 TP/FP/FN/F1，与 `fused_system_R6_summary.json` 全部 18 格（3 库 × 6 臂）逐一相符，零偏差：

| 数据集 | judgeable | 各臂（三 τ × G5a/G5b 恒同） | 复算=声明 |
|---|---|---|---|
| NHANES | 62（replicated 7） | TP5 / FP9 / FN2，P=0.357 R=0.714 **F1=0.476** | 是（全档） |
| KNHANES | 43（replicated 3） | TP2 / FP8 / FN1，P=0.200 R=0.667 **F1=0.308** | 是（全档） |
| CHARLS | 14（replicated 0） | TP0 / FP4 / FN0，F1=0.0 | 是（全档） |

### 项 4｜差异对与零触发核验 — **通过（附披露备注）**

- **NHANES G5a_0.55 vs G2**（逐对 join R5/R6 jsonl）：judgeable 内**唯一**差异对 = `dyslipidemia × amd_late`——G2 gate=`no_relevant_evidence` 弃权（规则 r05 命中）→ G5a top1_sim=**0.756** 召回成功过 B 级门槛 gate=`sem_evidence_Bplus` 发言，gold=`uninformative`、judgeable=True → +1 FP，F1 0.500→0.476。与 §15 运行记录逐字吻合。
- **G5b 零触发**：110 个无规则对（rule_ids 空），三档 τ 的 gate 分布均为 `direct_threshold_not_met(0) × 110`；且 143 对中 G5b 与 G5a 逐对完全相同（直推路径从未改变任何决策）。自锁机制经代码阅读成立：注记按规则 flag 打标（B3），无规则命中的对天然缺乏双注记块。
- **披露备注**：KNHANES 存在同对差异（`dyslipidemia × amd_late`，G2 0.333→G5a 0.308，同为 +1 FP），§15 运行记录与 `performance_by_dataset.csv` 的 G5 行 note 仅披露 NHANES 差异对，**KNHANES 退化未明示**。方向与负结果结论一致、不改变"定格 G2"决策，但属披露不完整。
- 另有 3 个**非 judgeable** 对（nhanes/knhanes 的 current_smoking × VI_moderate/severe）在 τ=0.65 翻转（True→False，`sem_evidence_Bplus`→`sem_arbiter_unknown`），不进入指标口径（与项 5 相关）。

### 项 5｜τ 不敏感性解释核验 — **通过（表述偏强）**

- 全局：143 对 top1_sim 中位 0.702，**125/143 ≥0.65**（min 0.544）。
- 抽 5 对：2 个 G5a 证据发言对（hyperglycemia×cataract_any 0.735；hyperglycemia×retinopathy_any 0.748，top1_level=B）top1_sim 均 ≥0.65，τ 门槛不构成约束；3 个零触发无规则对（uric_acid_elevated×VI_mild/moderate/severe，top1_sim 0.607–0.635）双注记计数=0，τ 三档下结局不变——相关判定确由注记主导。
- 机制核验：**judgeable 对在三档 τ 间逐对零翻转**（0/119），指标恒等由此成立。
- 表述偏强处："相似度门槛不参与判别"仅对 judgeable 层面成立；τ=0.65 在 3 个非 judgeable 对上实际改变了决策（见项 4），"三档全部结果恒等"准确说法是"三档 judgeable 指标与逐对决策恒等"。

### 项 6｜级联一致性 — **通过**

| 交付物 | 内容 | 数字一致 |
|---|---|---|
| §15 运行记录段 | G5a 0.476 / G5b 零触发 / τ 恒等 / 定格 G2 | 是 |
| `docs/limitations.md` L43 优化边界段 | R5.3/R6.0 合并结论（G3/G4/G5a/G5b/τ + 三重约束 + "正式系统定格 G2"） | 是 |
| `outputs/tables/performance_by_dataset.csv` | `fused_G5a_semantic` F1=0.476、`fused_G5b_semantic_direct` F1=0.476 两行（method=ablation_negative_result，note 注明 official system = G2）；G2 行 0.5 在册 | 是 |
| `.medical-agent/state.json` | log 末条 R6.0（G5a 0.476、G5b 零触发、τ 三档不敏感、定格 G2、新增 semantic_retrieval.py 资产） | 是 |

### 项 7｜pytest 实跑 — **通过**

`python -m pytest tests/ -q` → **15 passed in 0.23s**（15/15）。

### 项 8｜语义检索资产可用性 — **通过**

- `SemanticEvidenceIndex()` 实例化成功（不调外部 API）：加载 1054 chunks，level join 正确（A47/B125/C129/D125/E628）。
- `filter_relevant` 纯逻辑构造用例验证四分支：sim<τ 滤除（sim=0.50 在 τ=0.45 入选、τ=0.55 排除）；注记单 flag 命中；多 flag 逗号分隔注记子串命中（`[exposure: dyslipidemia, obesity | …]`）；无注记时文本双词回退；高相似但无注记无双词正确排除。
- 查询 embedding 与索引构建同源：`embed()` 与 `lightrag_adapter.py` 均走 `ArkVisionEmbedding`（doubao-embedding-vision-251215，dim 2048），"与索引同模型查询"声明成立。

---

## 遗留问题（不推翻结论，建议下轮修订）

1. **§15 预注册时序披露缺失**：§15 无 §13 那样的"时序披露（R8 复审指出）"降格句。预注册先于运行无独立可证证据（git 无 §15 快照；plan 文件 mtime 晚于 R6 输出系运行记录追加）。建议在 §15 运行记录处补一句与 §13 同款披露。
2. **三处数字/披露精度**：(a) §15"1047 chunks"应为 1054（vdb 实际）；(b) KNHANES G5a 退化（0.333→0.308，同 dyslipidemia×amd_late 对）未在 §15/csv note 明示；(c) "τ 三档全部结果恒等"宜精确为"judgeable 口径恒等"（3 个非 judgeable 对在 0.65 翻转）。
3. **G5a 预注册文字歧义**：§15"否则 LLM 仲裁"未覆盖"无相关块"分支（实现=§13 G2 三分支镜像，无相关→UNKNOWN）。论文或后续引用以实现为准，建议括注说明。

## 审计证据索引

- 复算脚本结果：18/18 格与 `outputs/confirmatory/fused_system_R6_summary.json` 零偏差
- 逐对 join：R5/R6 jsonl 的 judgeable/gold3/rule_ids 完全一致；G5a-vs-G2 差异全集=9 条翻转记录（judgeable 内仅 NHANES dyslipidemia×amd_late 一对，其余为 KNHANES 同对与非 judgeable τ=0.65 翻转）
- 关键文件：`docs/analysis_plan.md`（§13 L178–199、§15 L216–235）、`scripts/run_fused_system_v3.py`（L38–39、L85–117）、`src/huiyan_agent/semantic_retrieval.py`（L55–76、L101–120）、`data/processed/lightrag_index/vdb_chunks.json`（1054×2048）、`docs/limitations.md` L43、`outputs/tables/performance_by_dataset.csv`（G5 两行）、`.medical-agent/state.json`（R6.0 条目）
