# R5 科研诚信与可重现性审计报告（预注册纪律 · 版本链路 · 验证独立性）

- 审计轮次：R5（writer 阶段前最后一轮）
- 审计日期：2026-10-14
- 审计对象：R4_FIXLOG_2026-10-14.txt 全部修复声明 + 版本链路完整性
- 审计方式：只读实盘验证。不采信任何声明，关键数字全部独立重算/实跑（sha256 实算、graphml 节点实数、引用门函数实调模拟、pytest/freshness 门/handoff 门实跑、Crossref 联网复核）。未修改项目任何文件（含 .zcode/.dsh skill 脚本，仅读取与模块加载模拟）。

---

## 一、总结论

**R4 修复批次声明与磁盘实况高度相符：16 项核心声明中 13 项完全验证通过、3 项部分通过，无一项虚假。r22 引文更正是真实修复（Crossref 实查新 DOI 主题匹配、走严格双侧判定，非词表放行）；索引重建、sha 三方绑定、基线 valid 视图、v1.1 归档全部实盘成立；三门（引用门证据文件 / freshness / handoff）与 pytest 15/15 实跑通过。**

但审计发现 **1 项重要的门语义问题（P1）**：扩展后的引用门确定性关键词层存在 domain-relaxed 弱路径，**实测 r22 的旧错误引文（BMI×白内障 meta）在该新词表下同样会 PASS**——即"21/21 绿灯"的证明力低于"每条引文均经主题匹配"的表面含义（24 条中 22 条走严格双侧路径，2 条走弱路径；且全部判定仅基于标题，摘要未启用）。这不构成诚信硬伤（修复本身是真的、且经我独立联网复核），但属于"改尺子"边界的实质部分，须在 §0.1 披露并对弱路径引文补检。另有 source_coverage_report.json 陈旧（r22 仍指旧 DOI，早于修复 19 分钟生成、未再生成）与 performance_matrix.csv 的 Wilson 文字残留两个 P1 级交付物问题。**无 P0。处理完 3 项 P1 后可进入 writer。**

---

## 二、R4 修复逐项复核表

| # | FIXLOG 声明 | 实盘验证结果 | 状态 |
|---|---|---|---|
| 1 | r22 引文更换 + rationale 同步 | `configs/rules.yaml` L272-287：新 DOI `10.1097/MD.0000000000011807`；rationale 如实写明 RR=1.40 (T2DM 亚组)、NHANES OR≈1.47 方向一致、"数据驱动的探索性扩展"定性；头注释 L3 有更正记录。**Crossref 联网实查**：该 DOI = "Association of obesity and risk of diabetic retinopathy in diabetes patients"（Medicine, 2018）——与 r22 命题（bmi_high × retinopathy）主题匹配。旧 DOI pone.0089923 仅存于 r13（白内障），属正确归属 | **通过** |
| 2 | 词表扩展两套安装 md5 一致 | md5 实算：`.zcode` 与 `.dsh` 两份 `verify_rule_citations.py` 均为 `3696dae3359b5778bf601db4d0d0d0e9`；两处 `.bak-20261014` 备份在；huiyan 段在 L1391-1434（ENTITY_B 10 flag + ENTITY_A 15 flag + MECHANISM 6 组），append-only 模式与 jingming/mingmu 先例一致；`.config/opencode` 旧版（54172 字节，md5 88116cd0）确实未动 | **通过** |
| 2b | （重点审查）关键词层验证语义 | 见下文"专项分析"。22/24 走严格 `b=hit a=hit`（双侧主题匹配，标题级）；2/24（r10、r11 的唯一引文）走 domain-relaxed 弱路径，退化为单侧存在性检查；全部 24 条 `abstract_len=0`（未用 `--with-abstracts`）。**实测旧 r22 错误引文在新词表下也 PASS** | **部分通过（P1）** |
| 3 | 引用门 strict 21/21、24/24、exit 0 | `outputs/citation_verification_report.json`（2026-10-14T23:04:51 生成）：overall=pass，summary 21/21、by_status verified=24、rules_yaml_sha256=5aee851d…与当前规则一致、degraded_mode=False。r22 判定为 `b=hit a=hit`（真主题匹配，非词表放行），kuku 双源（crossref+openalex）确认。确定性成立（关键词层离线决定全部 24 条，不依赖 LLM 抖动） | **通过** |
| 4 | analysis_plan §0.1 三项更正 | §0.1-更正1（r22 引文 + 作者裁决维持 C/low）、更正2（bootstrap→CP）、更正3（词表修复）全部在盘；§3 标题行有"以 §0.1-更正2 为准"指引 | **通过** |
| 5 | CI 统一 Clopper-Pearson | 三个 `*_metrics_v11.json` 的 `ci_method` 均为 CP，数值 [0.59,1.0] / [0.158,1.0] / [null,null]；`performance_by_dataset.csv` ci_note=CP 且数值一致。**残留**：`performance_matrix.csv` methodology 列仍写 "three-state gold + **Wilson CI**"（数值已是 CP、标签未改）——修复声明"三处同为 CP"只对了数值没对文字。grep 全 outputs 无 normal-approx 残留 | **部分通过（P1：交付表方法标签错）** |
| 6 | progress.json phase3/phase4 实况 | phase3.rules_yaml_sha256 = phase4.index_built_against_rules_sha256 = `5aee851d358324d4…`（与下述实算一致）；phase4: nodes 27136 / edges 23722 / docs 1054 / 注记 548/1054=52% / freshness 字段在，逐项与磁盘实测相符 | **通过** |
| 7 | state.json 补齐 | completed 13 项（含 executor.phase3/4/5）；latest_validation → `outputs/confirmatory/nhanes_confirmatory.csv`（不再指 exploratory）；history 含 10-14 三条以上事件（含"旧索引 12% 未达声称 52%"的诚实补记与重建完成记录） | **通过** |
| 8 | dataset_summary.csv 实况化 | dev=n/a、nhanes/knhanes=done、cohorts=partial (CHARLS 2011 only) | **通过** |
| 9 | bootstrap 备注更新 | `baseline_fullsystem_bootstrap_ci.json` llm_baselines_note 已更新为"10-12 本地 qwen 重跑 0 失败"。附注：该文件 B=2000（seed 42），计划原文为"1000 次重采样"，此差异未记录（P2） | **通过（附 P2）** |
| 10 | figure2 契约按 v1.2 重写 | 已撤 5-seeds/t-test/significantly 表述；四 panels（P/R/F1 柱状、三态混淆、泛化落差、上下文分布）与实况一致；legend 的 gold3 7/3/61 与 nhanes_confirmatory.csv 实测完全一致；"contradicted 全部在规则覆盖外"实测成立（3 个 contradicted 对 rule_ids 均为空）；review_risks 4 条含 recall 膨胀警示 | **通过** |
| 11 | figure2 source_data 补列 | dataset_id / dataset_role 列在；契约 schema 与 CSV 列完全一致 | **通过** |
| 12 | v1.1 归档 | `archive_v1.1/` 7 文件（3 CSV + 3 metrics + README）；三个 metrics JSON 与 `git show c244af7^` 原文逐字段一致（8/1/0.154、7/1/0.184、3/0/0.500）；README 注明双版对照用途与 [1,1] 退化 CI 勿引述 | **通过** |
| 13 | v1.2 gap 表 | summary：35 共同对、28 同态（80%）、coverage_gap=0.006、precision_gap=0.0；CSV 实测 28/35 同态，与 summary、figure2 契约三方一致 | **通过** |
| 14 | 基线 valid 视图 + README | valid 视图 284 行 = 4×71；**从 valid 视图独立重算**：full_system 7/10/0 (F1 0.583)、pure_llm 4/8/3 (0.421)、naive_rag 1/3/6 (0.182)、lightrag 5/25/2 (0.270)——与 baseline_summary_v12.json 全等。原始文件 639 行 4 代结构（旧代 284 行无 provider 全 NO；lightrag 三次运行含 71 行 valid:false）与 README 描述一致；README 的污染演示（0.421→0.308）与陷阱警告如实 | **通过** |
| 15 | 回归验证 | 本审计实跑 `pytest -p no:cacheprovider`：**15 passed**；freshness 门实跑 exit 0（三 sha 一致输出）；handoff 门 `executor-to-writer` 实跑 OK | **通过** |
| 16 | 索引重建（27,136 节点 / 52% 注记 / 1054 processed） | 日志 `data/processed/index_rebuild_20261014.log` 在盘（6.5MB，22:42 完成，DONE 16627s）；graphml 节点实数 **27136**（旧索引备份实数 23826）；doc_status **1054 processed / 0 failed**；注记实测 starts-with `[exposure:` 的 chunk = **548/1054**（log L4342：101 rule-linked + 447 keyword）；ev0005 抽检：注记 `[exposure: hba1c_elevated, hyperglycemia | outcome: retinopathy_any]` = v1.2 flags；B5 伪造完成标记 0/1054；旧索引备份目录在；lightrag 重跑 P=0.167 R=0.714 F1=0.270 与 summary_v12 及 figure2 数据一致 | **通过** |
| — | sha 三方一致（freshness 门全绿） | 实算 `configs/rules.yaml` sha256 = `5aee851d358324d4be2e35da39dad8c7fcdd9c32ae5c2c9a8010d7a5219d4504`；与 progress.json phase3/phase4 字段、引用报告 sha 一致；freshness 门实跑输出三行相同 sha、exit 0 | **通过** |

### 专项分析：引用门关键词层到底验证了什么（用户重点审查项）

**判定逻辑（verify_rule_citations.py L778-816）**：对每条经 kuku 双源真实性验证的引文，取 title+abstract 与规则词表匹配——
- 主路径 `b=hit a=hit`：**暴露侧词与眼病侧词都在标题/摘要中出现** → 这是（粗粒度的）引文主题与规则声明匹配，不是单纯存在性检查；
- 三条 domain-relaxed 弱路径：`a+mech+family`、`a+family`、`b+family` —— 只要求单侧命中 + 一个"领域家族词"。

**实证结果（直接 import 该脚本调用 keyword_relevance 模拟）**：
1. 24 条引文中 **22 条走严格双侧路径**（含 r22 新引文 "obesity…diabetic retinopathy"）；
2. **r10（吸烟×白内障）唯一引文** "Appraising the causal role of smoking in multiple diseases…（MR 系统综述）" 走 `a+family`——family 命中来自 exposure_family 表内的 `"smok"`，它是 a 侧命中词 "smoking" 的子串（同一词自我满足），标题完全未提白内障；
3. **r11（吸烟×AMD）唯一引文** "Risk factors for age-related macular degeneration…" 走 `b+family`——family 命中来自 OPHTHALMIC_FAMILY 的 `"macular"`，同样是 b 侧命中词自身；标题未提吸烟；
4. **决定性反证**：把 r22 的旧错误引文标题（"Body Mass Index and Risk of Age-Related Cataract…"）在扩展后词表下模拟 → `(True, 'domain-relaxed (a+family)')` **PASS**。即：**即使不修复 r22 引文，新确定性门也会给 21/21 绿灯**。R4 之所以能抓到该错误，靠的是当时（词表扩展前的）LLM 层。

**结论**：词表扩展本身遵循 append-only 先例、且已披露（§0.1-更正3），r22 修复也是真修复——**不构成"改答案"**；但门的证明力被部分高估：对走弱路径的引文（r10/r11），"verified" 退化为"真实存在 + 单侧关键词"；且全部 24 条判定 `abstract_len=0`（仅标题，未用 `--with-abstracts`）。LLM 层只在关键词层判否时才被调用，故对这 2 条从未经过任何主题匹配。属"改尺子"边界的实质部分 → **P1**。

---

## 三、B 部分：版本链路与科研诚信

### B1. 协议偏离披露链完整性 —— 验证通过（1 个小缺口）
`git diff 9a92b61^ 9a92b61 -- configs/rules.yaml` 实际改动 = 新增 4 个 flag + r22 新规则块。逐项对照 analysis_plan §0：
- r02 += hba1c_elevated ✓ 已记录
- r03 += hyperglycemia ✓ 已记录
- r04 += hyperglycemia、+= dr_npdr（覆盖 NPDR）✓ 已记录
- r22 新增（evidence_level B→C、severity→low）✓ 已记录
- 性质定性（test-set fitting、R=1.000 是构造的）✓ 如实
- 小缺口：**LLM temperature 0.0→0.7**（c244af7 提交信息）未进 §0 偏离记录，仅在 docs/limitations.md §5 披露（P2）。

### B2. 预注册时点纪律 —— v1.0 可证，v1.2 结构性不可证（P1）
- **v1.0/v1.1：git 可证先注册后确证**。计划 v1.0 首次落盘于 c54c3b2（10-11 17:59，"pre-registered analysis plan"）；首个确证真实结果提交于 03cec9a（10-11 20:59）。计划文本（含"确证运行以本文件落盘之后为起点"）早于结果 3 小时入库。✓
- **v1.2：冻结先于重跑无法从 git 独立验证**。规则修改（10-12 07:12）、计划 v1.2 文本、v1.2 确证重跑结果**同在 c244af7 一个提交**（10-12 08:02；CSV 落盘 mtime 07:44）。git 只能证明三者都发生在 08:02 之前，无法证明计划文本写就先于重跑启动——只能依赖计划内时间线表的自述。缓解因素：v1.2 扩展已被定性为探索性、v1.1 指标作为主确证视图并行呈现（figure2 契约 review_risks 明示）、偏离本身已如实披露。**建议**：limitations 中明示"v1.2 冻结-重跑次序由内部时间线佐证（单提交）"，以后冻结类文件单独先行提交。

### B3. 数据可溯源 —— 链路成立，1 个交付物陈旧（P1）
- 文献块 901/1060 带 PMID（880 带 DOI），provenance="PubMed efetch 2026-10-11 huiyan phase2"；PPP 指南块 159 个 provenance 指名源 PDF，`data/raw/aao_ppp/` 3 个 PDF 实物在盘。chunk→PMID/DOI→源文件链路抽查通过。
- r22 在 `citation_verification_report.json` 中已是新引文的新判定（b=hit a=hit + 新标题 + 双源 kuku）——**不是**靠词表放行的旧判定。✓
- **P1：`outputs/source_coverage_report.json`（10-14 17:24:50 生成）早于 r22 修复（rules.yaml mtime 17:43:38）约 19 分钟，其中 r22 仍列旧 DOI `10.1371/journal.pone.0089923`，修复后未再生成**。writer 若从该表取引文会把错 DOI 写进论文。须用当前 rules.yaml 重跑 find_authoritative_sources 后再提交。

### B4. outputs/paper 与 outputs/submission —— 验证通过
两目录均为空（writer 未开始），与阶段声明一致。exploratory 隔离目录、figure3 NOT_COLLECTABLE 占位均在原状。

### B5. fail-open → fail-hard —— 基线管道已 fail-hard，残留 3 处 demo/报告路径降级（P2）
- `run_baselines.py`：两处 LLM 调用均 `raise_on_error=True`（L58-61、L133）；canary 前置；失败计数落盘 error 字段、run 级 valid=False 不入均值；any_total_failure → exit 1。✓ fail-hard 成立。
- 残留（均不在指标路径，full_system 基线为纯规则引擎不经过它们）：
  1. `safety_agent.py` L152-153：LightRAG 检索失败 `except: pass`（静默，注释明示"不阻塞流水线"）；
  2. `safety_agent.py` L179-180：仲裁 degraded → 静默回退纯规则、无 note（与 L217 异常路径带"仲裁失败"note 的处理不一致）；
  3. `llm_client.py` 默认 `raise_on_error=False`（返回 `[llm error]` 降级文本）——基线已覆盖，但 `app/streamlit_app.py` L612 演示路径仍用默认值（有外层 try/except 显示错误，勉强可接受）。

---

## 四、问题清单（按严重度）

### P0（诚信/链路硬伤，阻塞投稿）
无。

### P1（重大，进 writer 前应处理）
1. **引用门弱路径证明力 + 2 条引文未经主题匹配**：r10、r11 的唯一引文走 domain-relaxed 单侧路径（family 词与 a/b 词自我循环），且全部门判定仅用标题；实测旧 r22 错误引文在新词表下也 PASS。处置：① 对 r10/r11 两条引文以 `--with-abstracts` + LLM 层补一次主题判定；② 在 analysis_plan §0.1-更正3 补充披露弱路径语义局限；③（可选）修 skill 词表：family 词表剔除与 a/b 词表自我循环的项，或弱路径加 mech 前置条件。
2. **source_coverage_report.json 陈旧**：r22 仍指旧 DOI（17:24 生成 < 17:43 修复）。处置：用当前 rules.yaml 重跑 find_authoritative_sources 再生成，随修复批次提交。
3. **performance_matrix.csv 方法标签残留 "Wilson CI"**（数值已是 CP）。R4 修复声明"三处同为 CP"未完全兑现。处置：一行文字更正。
4. **v1.2 冻结-重跑次序 git 不可证**（计划与结果同提交）：在 limitations 或 §0.1 补一句证据等级说明；此后冻结类文件单独提交。

### P2（建议）
1. `*_metrics_v11.json` 文件名与内容口径错位：现役文件名 v11、内容为 v1.2（ci_method 字段与 archive README 可辨，但同名异义目录易误取）。建议现役改名 `_v12` 或加 `ruleset` 字段。
2. bootstrap 文件 B=2000 vs 计划原文"1000 次重采样"未记录差异。
3. temperature 0.0→0.7 只在 limitations 披露、未进 §0 偏离记录。
4. `data/processed/` 整目录 gitignore：索引与重建日志（6.5MB）不入库，sha 链在 git 侧仅靠 progress.json 字段佐证。建议将重建日志（或其哈希+关键统计摘录）强制入库。
5. safety_agent 两处静默降级（L152 / L179）与 llm_client 默认 fail-open —— 不在指标路径，但与项目 fail-hard 标准不一致。
6. `run_baselines.py` 汇总仍用 `r.get("valid", True)` 语义（旧代行无 valid 字段会被计入控制台 Summary；已由 valid 视图与 README 在消费侧兜底）。

---

## 五、建议的 git 提交分组（20 个未提交文件）

原则：sha 绑定链必须与被绑定的规则文件同批入库，否则 `5aee851d…` 悬空指向未提交状态。

| 组 | 文件 | 理由 |
|---|---|---|
| 1（必须首先提交）| `configs/rules.yaml` + `docs/analysis_plan.md` + `outputs/citation_verification_report.json` | r22 引文更正 + §0.1 更正记录 + 门证据（报告内含 sha 与 21/21 结果）。这是版本链锚点：规则 sha 只有提交后才成为可引用的冻结点 |
| 2（同批或紧随）| `.executor/progress.json` + `.medical-agent/state.json` + `R4_FIXLOG_2026-10-14.txt` + `AUDIT_R4_FULL_2026-10-14.txt` | phase3/phase4 sha 绑定、索引重建实况与审计链。data/processed 不入库，这两份状态文件是 git 侧唯一的链路证据 |
| 3 | `outputs/tables/performance_by_dataset.csv` + `outputs/tables/dataset_summary.csv` + `outputs/tables/performance_matrix.csv`（**先修 Wilson 残留**）+ `outputs/baseline_fullsystem_bootstrap_ci.json` | CI 统一与交付表实况化 |
| 4 | `outputs/confirmatory/archive_v1.1/` + `outputs/confirmatory/generalization_gap_v1.2.csv` + `…_summary.json` | v1.1 归档 + v1.2 泛化落差表（analysis_plan §0 处置3 的兑现物） |
| 5 | `outputs/baseline_predictions.jsonl` + `outputs/baseline_predictions_valid.jsonl` + `outputs/README_baseline_predictions.md` + `outputs/baseline_summary_v12.json` | 基线四代历史 + 唯一有效视图 + 读取说明 + lightrag 重跑级联 |
| 6 | `outputs/figures/contracts/figure2_performance.yaml` + `outputs/figures/source_data/figure2_performance.csv` | figure2 契约 v1.2 化 |
| 7（暂缓）| `outputs/source_coverage_report.json` | **当前陈旧（r22 旧 DOI），须先用新 rules.yaml 重跑再生成后提交**（P1-2） |

---

## 六、审计方法附记（可复现）

- sha256：`python -c "import hashlib; print(hashlib.sha256(open('configs/rules.yaml','rb').read()).hexdigest())"` → 5aee851d…
- 节点实数：grep -c "<node " 于新旧 graphml（27136 / 23826）；doc_status Counter（1054 processed）；注记计数（startswith `[exposure:` = 548）
- 引用门模拟：importlib 加载 skill 脚本后调用 `build_rule_keywords` + `keyword_relevance`，对旧/新 r22 标题、r10/r11 标题实测（结果见专项分析）
- 实跑：pytest 15/15（no:cacheprovider）；check_index_freshness exit 0；validate_handoff exit 0；Crossref API 复核新 DOI
- 独立重算：基线四方法 TP/FP/FN/P/R/F1 从 valid 视图全等复现；gap 28/35；gold3 7/3/61；v1.1 归档与 c244af7^ 对照
