# R31 · 2026-10-28 · 拒稿后的方法学修复：外部队齐 + 内部降级为开发集

## 触发

JMIR 退稿，意见指向方法学。自查确认三处真实问题（不是措辞问题）：

1. **主结果是样本内**。`docs/analysis_plan.md` §0 记录：2026-10-11 20:59 确证运行 → 2026-10-12 07:12 修改规则（r02–r04 暴露交叉覆盖改动、新增 r22）→ 同一批 NHANES 对上重算。文档原话定性为 *test-set fitting*，并写明"R=1.000 是构造的，不是性能提升"。摘要与 Results 却把 0.571/R 1.000 当头号卖点。
2. **外部层没有测 agent**。Table 3 的 KNHANES 行是 rule layer（0.360），CHARLS 与八队列只在规则层做方向核对。唯一 agent 级外部数字（G2 0.312）此前被写成"registry-matched 变体，不可比"，压在补充材料。
3. **两个矛盾产物未定性**。`g2_full_matrix_all.json`（10-27）的 NHANES 臂 TP=0，与 0.571 冲突；根因是那次运行时 llama-server 未启动，arbiter 全部走 `arbiter_error` 默认判否。

## 做了什么

### 1. 重跑确认可复现

- 启动本地 llama-server（qwen3.8-27b @ 8082），`scripts/run_fused_system.py` 全量重跑（474 对）
- 结果与 2026-10-15 那次**逐位一致**：NHANES judgeable G0 0.522 / G1 0.545 / G2 0.571；KNHANES judgeable G0 0.370 / G1 0.385 / G2 0.400
- 结论：模型确定性可复现，0.571 是真的；**10-27 那份 NHANES 全否产物无效**，已在该 JSON 与 R31 记录中标注
- 新落盘：`outputs/confirmatory/g2_rerun_20261028.json`；备份 `archive_pre_rerun_20261027/`

### 2. 把 KNHANES 拉回同一口径（301 对，同一 gold3）

| 方法 | TP | FP | FN | TN | P | R | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule layer (G0) | 9 | 23 | 9 | 260 | 0.281 | 0.500 | **0.360** |
| G1 (NC 门) | 5 | 10 | 13 | 273 | 0.333 | 0.278 | 0.303 |
| **G2 全智能体** | 5 | 9 | 13 | 274 | 0.357 | 0.278 | **0.312** |
| LightRAG | — | — | — | — | — | — | 0.145 |
| pure LLM | — | — | — | — | — | — | 0.135 |
| naive RAG | — | — | — | — | — | — | 0.094 |

**核心发现（必须如实写进论文）**：外部数据上证据门把 precision 从 0.281 提到 0.357，但吃掉 4 个真阳性、召回从 0.500 砍到 0.278，**全智能体（0.312）低于自己的确定性规则层（0.360）**。它仍高于三个 LLM/RAG 基线。

### 3. 稿件改动

- **Abstract（332 词）**：主外部结果改为 KNHANES 全智能体 0.312（对基线 0.145/0.135/0.094），并明确低于规则层 0.360；内部 0.571 标注 in-sample，R=1.000 降为"该次规则修订的产物"，同时给出修订前 v1.1 的 0.111；结论改为"胜过通用模型与 RAG、但外部不胜过自身规则层"。
- **Results**：Validation overview 与两段 system-level 重写；内部段显式声明 in-sample + test-set fitting；外部段给出 G2 全智能体 301 对结果、门控的 precision/recall 交换、以及重算的 accuracy McNemar（vs LightRAG p 1.8×10⁻¹⁵–1.2×10⁻¹³，vs pure LLM 2.1×10⁻²⁵–1.8×10⁻²⁰，vs naive RAG 5.1×10⁻⁴–0.087，五个 seed 中四个显著）。
- **Discussion**：主发现段与"性能来源"段重写，加入方向反转的机制解释（证据库对新国家复现的对少有 B 级以上 chunk → 确认门恰在规则层正确的处弃权）；结论段同步。
- **Table 3**：列改为 `Full agent F1 (G2)` + `Rule layer F1 (G0)`；NHANES 两行标 **in-sample**；KNHANES 行改为 agent 0.312 / rule 0.360。
- **Supplementary Table S7**：新增 KNHANES `full agent (G2)` 行（0.278/0.968/0.357/0.275），原行改标 `rule layer (G0)`，并注明 NHANES 各行 sensitivity 1.00 是构造值。

### 4. 复核

- `qc_english_manuscript.py` **20/20 PASS**，abstract 无孤立数字（0.28→0.278 已回填正文同值）
- 重建 docx（`manuscript_agent_first.docx`）与 PDF：**37 页**，4 表 6 图；正文 6,156 词
- 图 2 仍只画 NHANES（内部）；图注未声称外部分层，无需重渲染

## 仍未解决（留给下一轮，不能装作解决）

1. **图 2 缺外部面板**：论文的头号新结论（外部 agent < 规则层）目前只有表 3 承载，图上没有。要投下一家建议加一个 KNHANES 的 G0/G1/G2 三柱面板。
2. **真正的留出集仍不存在**：本轮只是把内部降级为 in-sample 并如实标注，没有做出"规则修订未使用过"的独立矩阵。若审稿人继续追这一点，唯一干净的解法是切出未参与修订的暴露族/结局族重跑。
3. **外部只有 KNHANES 一个国家**：CHARLS 与八队列仍是规则层。
4. **合著者/作者门**：7_1–7_8 的作者确认仍未回收。

## 附：arbiter 后端替换测试（2026-10-28 追加）

问题：本地 qwen 换成 glm-5.3-flash 能不能改善外部表现？

- 做法：同一 harness、同一温度/种子，只改 `HUIYAN_LLM_PROVIDER=zhipu`
- 先验证两个后端都真连通：zhipu → `glm-5.3-flash`，local → `qwen3.8-27b`，都返回正常
- 结果：**474 对预测逐字节相同**（jsonl sha256 前缀同为 `2171692f7d3bfeb7`）
- 原因：gate 分布显示 **arbiter 只决定 3 对**（且都是 hyperglycemia × cataract，两个模型都答 YES）；其余 471 对由规则层（434）、证据 B+ 门（32）、负对照门（3）、无相关证据（2）决定
- 结论：**换模型不是杠杆**。外部差距（G2 0.312 < 规则层 0.360）来自证据门弃权，不来自模型。要让 LLM 起作用，必须把更多判定交给它（协议变更、需预注册），而 standalone LLM 臂已证明那条路精度只有 0.10
- 证据落盘：`outputs/confirmatory/arbiter_backend_swap_20261028.json`、`fused_system_R5_zhipu.jsonl`
- 论文侧：Discussion "Where the performance comes from" 加一句（arbiter 决定 3/474、换 GLM 预测不变，增益属于规则与门控层）
