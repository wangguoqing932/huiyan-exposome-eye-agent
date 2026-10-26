# R22 图表独立评审（2026-10-23）

三组独立智能体、互不共享结论，对同一套 8 张图分别做：
A 顶刊美术编辑、B 数据可视化/统计图形、C 出版一致性。
评审对象为 `outputs/figures/` 下 8 个 PNG（Figure 1–6 + S1/S2）。

## 一、评分总表

| 图 | A 美术 | B 数据 | C 一致性 |
|---|---:|---:|---:|
| Figure 1 架构 | 8 | 9 | 7 |
| Figure 2 性能 | 7 | 7 | 7 |
| Figure 3 规则评价 | 8 | 8 | 7 |
| Figure 4 剂量反应 | 6 ✗ | 8 | 6 ✗ |
| Figure 5 效能 | 6 ✗ | 7 | 6 ✗ |
| Figure 6 可迁移性 | 8 | 8 | 8 |
| Figure S1 演示病例 | 6 ✗ | 7 | 6 ✗ |
| Figure S2 推理轨迹 | 8 | 9 | 9 |
| **整套** | **7 fail** | **8 pass** | **7 fail** |

> 图中编号为稿件编号：Figure 4 = 剂量反应（contract figure6），
> Figure 5 = 效能（contract figure7）。评审 agent 按文件序号评分，本表已换算成稿件编号。

## 二、三组一致认可的优点

- 五色语义系统在多数图中成立：navy / teal / amber / brick / 中性灰。
- 背景纯白，无浅色底板；Figure 6/S2 的白色背景与留白获得明确好评。
- 森林图的对数轴、OR=1 参考线、方向性编码正确；Figure 6 被两位评审称为"最强数据图"。
- S2 的七步泳道、各层计数（4/1/2）与 Figure 1 的层配色一致。
- 字号在 180 mm 下总体可读；无中文、无 Markdown 残留。

## 三、必须处理（P0，影响数据完整性）

### P0-1 Figure 5（效能图）漏掉了 5 个数据点

- 图的 y 轴下限是 **0.95**，而源数据 `figure7_power_mde.csv` 中观测 OR 低于 0.95 的点有：
  `lead_exposure · cataract_any` **0.60**、`current_smoking · cataract_any` **0.756**、
  `pm25_exposure · amd_early` **0.925**、`current_smoking · vision_impairment_severe` **0.935**、
  `alcohol_intake · cataract_any` **0.940**。
- 这不是"一个点被轴线切掉"，而是**五个点在图中完全不存在**。审稿人若对照源数据会发现图与数据不一致。
- 修复方向：y 轴改为约 0.55–2.6（log），x 轴保持 0.95–2.6；identity 线从 0.55 起；
  下限刻度用 0.6/0.8/1.0/1.2/1.5/2.0/2.5。五个低 OR 点会落在 identity 线下方（效能不足区）。

## 四、建议处理（P1，影响可解读性/一致性）

### P1-1 Figure 2 面板 a：有均值、没有种子间变异

- 图注写 "mean of 5 seeds"，但没有 SD/误差条；`figure2_performance.csv` 只有 `F1_mean`，没有 SD。
- canonical 预测文件可以逐 seed 重算 F1，补 SD 误差条（full_system 确定性，SD=0）。
- 同一图内 navy/amber 在面板 a 表示 qwen/zhipu，在面板 c 表示 NHANES/KNHANES，
  是两套变量共用一套颜色；面板 c 已有 in-bar 标签，建议图注明确"颜色在本图内按面板定义"。
- 面板 b 的蓝色序列是 matplotlib `Blues`，不在五色系统内，且无 colorbar；
  建议改为 white→navy 的单色阶，并保留"每格印计数、底纹仅辅助"的图注。

### P1-2 Figure 3：覆盖率行没有区间、所有行没有分母

- `figure3_rule_evaluation.csv` 中 coverage 的 `ci_low = ci_high = estimate`，所以图中是一个裸点；
  其他行都有区间，编码不一致。
- 建议把每行的 `k/n` 加进数值标签：declared 6/6 与 5/5、conservative 6/16 与 5/15、
  coverage 16/18 与 15/17、replication A 0/1、A+B 4/13、all 6/19 与 5/16。
  这样既解释了 coverage 无区间（census proportion），也避免 1.00 被误读为精确值。

### P1-3 amber 仍是两个 hex

- 一致性评审采样确认：Figure 1 的流程框/顶条使用亮琥珀 `#D9A441`，
  而 panel b 的 "Arbiter layer"、Figure 3 的 replication、S1 的 "Confirmatory outcome"
  使用暗赭 `#A9711B`。同一语义两种 hex。
- 修复方向二选一：
  (a) 全部改为 `#D9A441`，标题文字改用黑色 + 琥珀色圆点（保证对比度）；
  (b) 全部改为 `#A9711B`，但 Figure 2 的 zhipu 柱要跟着改，会破坏作者认可的 Figure 2 配色。
  推荐 (a)。

### P1-4 Figure S1 面板 c：颜色没有定义

- B · pooled 用 teal、C · single cohort 用 navy，但图内没有图例；读者会问"颜色代表什么"。
- 证据等级是序数变量，不是分类色。建议所有非零条统一用 navy，计数直接标在条末；
  颜色不再承担未声明的含义。

## 五、可选（P2，不影响投稿）

- **Figure S1 面板 a 的空带**：panel a 与 b/c 之间的垂直空白约占画布 15%；
  把 panel a 高度比从 1.0 降到 0.8 可收紧。
- **Figure 1 面板字母位置**：a/b/c 贴在画布左边缘，其他图缩进在坐标轴上方；可统一缩进。
- **Figure 7（效能）画布宽度**：125 mm，其他图 180 mm；最终在 Word 里都缩放到 15.4 cm，
  字号反而更大，不是生产缺陷，可不改。
- **Figure 6 的 "CLHS"**：一致性评审报告 r02 组首行为 CLHS。核对源 CSV 与渲染代码：
  所有行均为 `CLHLS`，渲染直接读 `r["cohort"]`；这是 600 dpi 下字母 L 与 I 相邻造成的**误读**，
  不是数据错误。
- **Figure 4 navy 的双重角色**：评审认为 panel a 的 navy=Replicated、panel b 的 navy=significant OR>1；
  实际 panel b 的 navy 仍是 Replicated（图例如此），该条为评审误读，不需要改。

## 六、结论

整套图的**设计语言已经统一**（配色、字体、面板标签、纯白背景），S2 与 Figure 6 达到 9 分；
但 **Figure 5 存在真实的数据省略**，必须在投稿前修正。P1 的四项属于可解读性与一致性，
建议在投稿前一并处理；P2 可留到校样阶段。

> 本报告只做评审，未改动任何图片或稿件。

## 七、处理结果（review → fix 闭环）

作者指令"能处理的全部处理"后，P0/P1/P2 已落地并复验：

| 项 | 状态 |
|---|---|
| P0 图 5 漏 5 个低 OR 点 | ✅ y 轴改为 0.55–2.55（log），0.60/0.756/0.925/0.935/0.940 全部可见；画布 160 mm |
| P1 图 2 无种子间变异 | ✅ 从 canonical 逐 seed 重算 F1，补 ±1 SD 误差条；naive RAG 的大 SD 如实显示 |
| P1 图 2 热图 off-palette | ✅ 改为 white→navy 单色阶（vmax=20），11/61 可区分；图注保留"底纹仅辅助、计数已印" |
| P1 图 3 coverage 无区间、无分母 | ✅ 每行数值标签加 k/n（0.38 (6/16)、0.89 (16/18)、0.00 (0/1)…） |
| P1 amber 两个 hex | ✅ 全部统一为 #D9A441；标题文字改黑色 + 彩色圆点，对比度反而更好 |
| P1 S1 面板 c 颜色无定义 | ✅ 非零证据条统一 navy，计数直接标注 |
| P2 S1 空带 | ✅ 画布 122 mm，panel a 高度比 0.8，b/c 上移 |
| P2 图 1 面板字母贴边 | ✅ 缩进 0.8 单位，与其他图一致 |
| 图 3 "bDeclared" 碰撞 | ✅ 面板标题偏移 0.06→0.085，复验通过 |
| S2 步骤 5 标签被泳道线穿过 | ✅ 标签上移到 0.55，复验通过 |
| CLHS 拼写 | ❌ 非缺陷：源 CSV 全为 CLHLS，600 dpi 下误读 |
| 图 4 navy 双重角色 | ❌ 非缺陷：panel b 的 navy 仍是 Replicated，评审误读 |

**美学复评（同一 agent，5 张改动图）：Figure 1/2/3/5/S1 全部 9 分。**
评审确认："no points below 0.95 are missing"、"SD whiskers visible"、
"no amber split remains"、"headers black text + coloured dots resolves the contrast caveat"。

**投稿 Word**：`manuscript_final.docx` 55 页，0 中文；图页 48–55 复验通过
（其中 50/55 在两次布局修复后单独复查）。

### 仍未处理（非阻断）

- 图 5 的 0.935 与 0.95 两枚开口圆仍轻微相切；两枚都可见，未遮挡读数。
- 图 2 矩阵色阶无 colorbar；图注已声明"底纹仅辅助、每格有计数"。
- 图 3 的 k/n 后缀增加了标签宽度；180 mm 下可读，期刊再缩版时可考虑只在图注列 k/n。
