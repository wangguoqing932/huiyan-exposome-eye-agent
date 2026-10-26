# 慧眼（huiyan）

**唯一目标（R12 起约束）**：用 medical-agent skill 搭建暴露组×眼病智能体，并写出论文。仓库一切内容服务于这条主线；史档已归位 `docs/history/`，一次性脚本见 `scripts/README.md` 注册表 D 组。

## Project Status（2026-10-23，R30 多视角审稿修正后）

📋 **Planner 0–4.5、Executor 0–6 完成且四门全绿（planner 自检 3/3、phase3 引用门 21/21、索引 freshness 三 sha 一致、executor→writer 门通过）；Writer 7_8 已从分节源重新装配（96,235 B；正文 5,988 词（Word 口径） Introduction–Discussion，Methods 1,575；abstract 412 词；References 27 条 / 4 表 / 6 主图 + S1/S2）；7_3 已确认；7_1、7_2、7_4、7_5、7_6、7_7、7_8 因 R29 表图压缩与 R30 审稿修正重新提交；7_9 唯一阻塞项在作者侧（目标期刊与通讯作者信息）。**

**R25–R29 叙事、结果与结构**：先报 agent 强且可用（NHANES 双代 + KNHANES 301 对均优于三条基线，Streamlit/来源可溯报告），再报八队列规则层可转运性失败，最后落在“agent 验证应报告规则层面可转运性，而不只是聚合系统性能”。标题同步改为 “strong system performance and usable reports, but poor rule transportability across eight cohorts”。R26 在 Results 开头新增“五个验证目标的核心结果”总览；R27 按 writer skill 的 dataset-centric 顺序重排 Results；R28 按 imrad_playbook 重写 Introduction、Methods、Discussion；R29 主稿压到 4 表（cohorts/rules/performance/transportability）与 6 图（S1/S2 移入 Supplement），6 张表移入 `outputs/tables/supplementary/` 并汇总到 `outputs/submission/supplementary_tables_figures.md`；正文 5,988 词（Word 口径），37 页。

**agent 三层现状**：
- 规则层确定；**患者因素升级已修复并有单测锁定**（`tests/test_synthetic_regression.py::test_escalation_fixed`，修复前 272 测试 0 触发 → 现 17 触发且范围受限）；
- **M1 合成效应注入回归已建**（`scripts/synthetic_regression.py`，已知真值评估面：OR=2 检出 100%、假阳性 0%、中位估计恢复真值；此前 80 对/5 信息性对无功效的问题就此补上）；
- **M12 操作化字典已真接入**：`configs/variable_map.yaml` 为唯一事实源，`src/huiyan_agent/variable_map.py` 运行时守卫（代码变量 ⊆ 字典，漂移即 fail-loud）+ 患病率门（>50% 偏离报警/>2.5× 阻断）已在 evaluate.py / evaluate_knhanes.py 生效，落盘 `outputs/confirmatory/prevalence_gate_*.json`；
- ⚠️ **仲裁层非确定**：温度钉 0.0 仍有约 1/12 运行改级（原因在提供方），`confidence` 由规则层独算不反映仲裁犹豫（docs/AGENT_AUDIT.md §十四）；
- G3/G4/G5 负结果路径已归档（docs/archive_g3g4g5/，M8）；推理层禁止再投入。

**R11/R17 双代 headline**（详见 `outputs/README_baseline_predictions.md`）：NHANES 16 规则对 / 6 复证 / 0 反证（CP [0.541,1.0]）；KNHANES 15 / 5 / 0（[0.478,1.0]）；CHARLS 4 对全 uninformative。系统性能双代双呈、不合并：qwen 代 80 对 full_system F1 = 0.522（R11 修正 gold，5 seeds；对 pure_llm/naive_rag 显著，对 lightrag 不显著 p=0.057–0.092）；zhipu GLM-5.3-flash 满血代 159 对 full 0.480 > lightrag 0.186 > pure_llm 0.178 > naive_rag 0.069（McNemar 对全部基线显著）。G2 定格 0.500；**v1.1/v1.2 双呈义务**（回放 F1=0.111）。

**论文（未投出）**：`outputs/paper/manuscript.md`（7_8 从分节源重装配：96,235 B；References 27 条、4 表、6 主图 + S1/S2；R25–R29 已按“强 agent→多数据集→可用→规则层教训”重排标题/摘要，并按 skill 重写 Results/Methods/Introduction/Discussion，主稿压到 4 表/6 图；Figure 2 为双代分组柱、panel b 仅 80 对 R11 gold）。R11 旧稿已归档 `outputs/_archive/2026-10-23/manuscript_R11.md`，不再作为投稿线。投稿包：旧版已归档 `outputs/submission/_superseded_20261019/`；7_9 在作者提供期刊/作者信息前保持 fail-loud 拒绝打包（封面信 5 处未填字段）。

## Quick Navigation

| 路径 | 内容 |
|---|---|
| [PLAN.md](PLAN.md) | 主执行计划（8 阶段） |
| [docs/README.md](docs/README.md) | **docs 索引**（方法/伦理/审计/前瞻四类） |
| [docs/AGENT_V2_MUSTFIX_2026-10-16.md](docs/AGENT_V2_MUSTFIX_2026-10-16.md) | 框架 V2 必改单（后续工程，非本稿前置） |
| [docs/analysis_plan.md](docs/analysis_plan.md) | 预注册计划 v1.2 + §0.1–0.3 更正记录 |
| [docs/AGENT_AUDIT.md](docs/AGENT_AUDIT.md) | agent 三层审计（R1–R21） |
| [docs/limitations.md](docs/limitations.md) | 局限与诚实陈述 |
| [docs/history/](docs/history/) | 全部历史审计/修复/阶段文档（R4–R21） |
| [scripts/README.md](scripts/README.md) | **脚本注册表**（A 核心管道/B 队列层/C agent 诊断/D 写作一次性） |
| [outputs/README.md](outputs/README.md) | **outputs 索引**（当前产物 vs 原始日志 vs 归档） |
| `configs/` | rules.yaml（v1.2 冻结）、variable_map.yaml（操作化唯一事实源） |
| `src/huiyan_agent/` | 核心源码（规则/检索/仲裁/报告/variable_map 守卫） |
| `data/` | seed（注册表+证据池）、raw/knhanes_frames_v2（重建帧）、frames（8 队列帧）；`processed/logs/` 为索引日志 |
| `outputs/confirmatory/` | 四库确证+survey 链+prevalence_gate_* |
| `outputs/agent/` | agent 诊断+合成回归产物 |
| `outputs/paper/` `outputs/submission/` | 论文主稿与投稿包（旧产物见 `outputs/_archive/`） |
| `outputs/tables/`、`outputs/figures/` | 4 张主表 + 6 张补充表、论文图 6 主 + S1/S2（契约 8 份，四格式） |
| `outputs/logs/` | 运行日志（R5–R19，只读证据；见其 README） |

## 重建前提（缺一不可）

1. **E:\ 盘原始数据**（54GB）：NHANES XPT、CHARLS dta、8 队列原始库、KNHANES Rdata；
2. **本地 llama-server**（qwen3.8-27b @ `http://127.0.0.1:8082/v1`）；
3. **R ≥ 4.x + survey**；4. **`.env` 密钥**（DeepSeek/Ark/NCBI）；5. Python ≥ 3.10 + `pip install -e .`。

## 管道与测试

```bash
python scripts/run_all.py                 # canonical 8 步链(顺序敏感,单跑 evaluate 会回退口径)
python scripts/run_all.py --with-baseline # 追加基线汇总+bootstrap
python -m pytest tests/ -q                # 17 测试(含 M1 合成回归 + 升级修复锁定)
PYTHONUTF8=1 python scripts/synthetic_regression.py
```

详细分步顺序见 `scripts/README.md` A 组表格；KNHANES 帧重建：`build_knhanes_frames.py`。

## 纪律（约束）

1. 规则集冻结；改操作化只改 variable_map.yaml（corrections 留痕），不改代码散点——运行时守卫会拦；
2. 推理层禁止再投入（消融已证非瓶颈）；一切 agent 性能声明必须出自 M1 评估面或预注册盲测集；
3. jsonl 追加写从现在起必须带 epoch 字段（M11 待办，先自律）；
4. 投稿包机械六项修完前任何期刊都不投。

## Interactive Demo (Streamlit)

```bash
pip install -e ".[streamlit]" && streamlit run app/streamlit_app.py
```

> ⚠️ The demo is for clinical decision support only and does not replace clinician judgement.

## License

For peer review and academic reproducibility. All data derived from publicly available sources.
