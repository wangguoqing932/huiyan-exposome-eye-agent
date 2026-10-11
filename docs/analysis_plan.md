# huiyan 分析计划（预注册）· Analysis Plan

> 版本 v1.0 · 制定日期 2026-10-11（第三轮全阶段审核后）
> **定位声明**：此前已运行的三库对级检验（nhanes/knhanes/charls_pair_results.csv，2026-10-11）一律定性为 **exploratory（探索性）**，其指标（P/R/F1）因口径缺陷（审核 C1/C2：金标准自证循环 + 非显著≠反证混标）**不进入论文正文**。本计划规定 confirmatory（确证性）重跑的全部口径；确证运行以本文件落盘之后为起点。

## 1. 分析单元与定义域（分母纪律）

- 单元 = (A-flag, B-item) 对。
- **规则声明域**：11/15 B 条目（vi_mild、glaucoma/amd_selfreport、optic_disc_abnormality 已声明剔除，只报覆盖率）。
- **FN 只在类型 2 空白内评估**（physical_activity × glaucoma_*）；类型 1 结构性空白（mercury、physical_inactivity × 任意 B）与**未立项对不计 FN**——它们是覆盖范围问题，不是系统错误（审核 C2）。
- r01（尿酸×白内障）登记为**阴性对照规则**（negative_control），单列报告，不进 headline 指标（审核 C10）。

## 2. 金标准三态标签（取代二值 gold，审核 C1/C2）

对每个可测规则对（引擎输出的 predicted-positive 对）在库内估计加权关联后：
- **replicated**：q<0.05 且方向与规则声明一致；
- **contradicted**：q<0.05 且方向相反（唯一计入 FP 的状态）；
- **uninformative**：q≥0.05（无论方向——不构成反证，不计 FP，单列报告）。

对 predicted-negative 的可测对（类型 2 空白内）：**missed_association**（q<0.05 且为风险方向）计入 FN；其余为 TN。

## 3. headline 指标（全部带 bootstrap 95% CI，1000 次重采样，审核 C7）

- **Precision_rule = replicated / (replicated + contradicted)**（引擎发言范围内的精确率；uninformative 单列）；
- **Recall_gap = replicated / (replicated + missed_association)**（仅类型 2 空白内）；
- 阴性对照（r01）与全量明细表单列；
- **分层**：证据级（修正后 A3/B15/C3）× 数据集；
- **Δ 指标只在两层均可判的交集对上计算**（审核 C8）。

## 4. 方向合理性前置审计（审核 C4）

指标产出前必须先过：对**证据级 A 的确立危险因素对**（r10/r11/r13）逐对核对库内方向；若 ≥2 个 A 级对在同库呈反向（OR<1），该库标签进入 **quarantine**（隔离）：先查暴露编码、结局口径、选择偏倚（存活/患病）、反向因果（现吸烟 vs 曾吸烟），出具书面归因后方可解除；未解除前该库不产出 headline 指标。

## 5. 协变量统一（审核 C3）

- **主模型（全层统一）**：age、age²/100、sex。
- **敏感性（仅 NHANES 可得层）**：+race、education、PIR、BMI、smoking（暴露为该变量时移除自身）。
- 层间比较只用主模型口径；敏感性结果单列附录。

## 6. 方差估计（审核 C5）

- NHANES：以 R `survey` 包 svyglm（strata=SDMVSTRA, psu=SDMVPSU, weights=WTMEC2YR）为确证标准；Python 归一化权重的 GLM 仅作开发近似并声明。
- KNHANES：同法（kstrata/psu，wt_itvex）。
- CHARLS：个体权重 svydesign（无分层信息时声明）。
- R survey 不可用时的降级路径：报告 design-effect 无法校正的局限，headline 只报点估计+bootstrap CI（对权重不敏感），并显著标注。

## 7. 多重检验

每库内对全部进入检验的对做 BHY FDR；报告 q 与 p 双列；α=0.05。

## 8. 数据集交付口径（审核 B4/B5/B6）

- 目标维持 config 值：dev 400 / intval 400 / extval-K 300 / extval-C 120（**上限**）；
- 每集产出 per-dataset `cases.jsonl`（含 provenance：变量映射、纳入排除、每步 N）后，验证脚本必须**从 cases.jsonl 读取**（脚本内即时造对不再允许，审核 B5/B8）；
- 引擎与验证脚本分离：验证只消费 `huiyan_agent.risk_rules` 的输出（审核 B8）。

## 9. 基线与 seeds

4 基线（pure_llm / naive_rag / lightrag / full_system）× ≥5 seeds；seed 列表预注册 [11, 22, 33, 44, 55]。

## 10. 预注册阈值（不变项）

内部 sens≥0.70 / spec≥0.60；外部 sens≥0.70 / spec≥0.80（按新三态口径换算后评估：precision_rule≥0.70 内部 /≥0.80 外部对应原 spec 语义——换算关系在确证报告中显式给出）；未达标 → state `blocked[]` 记录，不得标 complete。

## 11. 版本与变更

- 本计划一经确证运行开始不得修改；任何修订以 v1.1+ 记录变更理由。
- 探索性结果与确证性结果在 outputs/ 下分目录存放：`outputs/exploratory/`（移入现有三库产物）与 `outputs/confirmatory/`。
