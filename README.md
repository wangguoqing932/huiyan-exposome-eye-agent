# 慧眼（huiyan）

**唯一目标（R12 起约束）**：用 medical-agent skill 搭建暴露组×眼病智能体，并写出论文。仓库一切内容服务于这条主线；史档已归位 `docs/history/`，一次性脚本见 `scripts/README.md` 注册表 D 组。

## Project Status（2026-10-19，合规修复轮后）

📋 **Planner 0–4.5、Executor 0–6 完成且四门全绿（phase3 引用门重验、索引 freshness 重建绑定）；Writer 7_8 已按当前规则与数据重组装（137,288 B，含 References 27 条 / 9 表 / 8 图例）；7_1、7_2、7_4、7_5 因修正后重开待作者复核；7_9 唯一阻塞项在作者侧（目标期刊与通讯作者信息）。**

**agent 三层现状**：
- 规则层确定；**患者因素升级已修复并有单测锁定**（`tests/test_synthetic_regression.py::test_escalation_fixed`，修复前 272 测试 0 触发 → 现 17 触发且范围受限）；
- **M1 合成效应注入回归已建**（`scripts/synthetic_regression.py`，已知真值评估面：OR=2 检出 100%、假阳性 0%、中位估计恢复真值；此前 80 对/5 信息性对无功效的问题就此补上）；
- **M12 操作化字典已真接入**：`configs/variable_map.yaml` 为唯一事实源，`src/huiyan_agent/variable_map.py` 运行时守卫（代码变量 ⊆ 字典，漂移即 fail-loud）+ 患病率门（>50% 偏离报警/>2.5× 阻断）已在 evaluate.py / evaluate_knhanes.py 生效，落盘 `outputs/confirmatory/prevalence_gate_*.json`；
- ⚠️ **仲裁层非确定**：温度钉 0.0 仍有约 1/12 运行改级（原因在提供方），`confidence` 由规则层独算不反映仲裁犹豫（docs/AGENT_AUDIT.md §十四）；
- G3/G4/G5 负结果路径已归档（docs/archive_g3g4g5/，M8）；推理层禁止再投入。

**R11 主口径 headline**（2026-10-19 重跑；详见 `outputs/README_baseline_predictions.md`）：NHANES 16 规则对 / 6 复证 / 0 反证（CP [0.541,1.0]）；KNHANES 15 / 5 / 0（[0.478,1.0]）；CHARLS 4 对全 uninformative；full_system F1 = 0.522（R11 修正 gold，5 seeds）> 纯 LLM 基线（McNemar 显著；对 lightrag 不显著 p=0.057–0.092）；G2 定格 0.500；**v1.1/v1.2 双呈义务**（回放 F1=0.111）。

**论文两条线（均未投出）**：① 八队列测量学稿 `outputs/paper/manuscript.md`（7_8 已重组装：References 27 条、9 表、6 主图 + S1/S2；r13/Table 5b 的“两阶段 p”列已从单队列 q 更正为 Cochran Q，见 AGENT_AUDIT §三十六）；② 三库复现稿 `outputs/paper/manuscript_R11.md`（仍为 10-15 草稿、未走 writer 流水线，内含旧“A 级=3”表述，暂勿投）。投稿包：旧版已归档 `outputs/submission/_superseded_20261019/`；7_9 在作者提供期刊/作者信息前保持 fail-loud 拒绝打包（封面信 5 处未填字段）。

## Quick Navigation

| 路径 | 内容 |
|---|---|
| [PLAN.md](PLAN.md) | 主执行计划（8 阶段） |
| [AGENT_V2_MUSTFIX_2026-10-16.md](AGENT_V2_MUSTFIX_2026-10-16.md) | 框架必改单（当前执行基准） |
| [docs/analysis_plan.md](docs/analysis_plan.md) | 预注册计划 v1.2 + §0.1–0.3 更正记录 |
| [docs/AGENT_AUDIT.md](docs/AGENT_AUDIT.md) | agent 三层审计（14 节） |
| [docs/limitations.md](docs/limitations.md) | 局限与诚实陈述 |
| [docs/history/](docs/history/) | 全部历史审计/修复/阶段文档（R4–R11 共 19 件） |
| [scripts/README.md](scripts/README.md) | **脚本注册表**（A 核心管道/B 队列层/C agent 诊断/D 写作一次性） |
| `configs/` | rules.yaml（v1.2 冻结）、variable_map.yaml（操作化唯一事实源） |
| `src/huiyan_agent/` | 核心源码（规则/检索/仲裁/报告/variable_map 守卫） |
| `data/` | seed（注册表+证据池）、raw/knhanes_frames_v2（重建帧）、frames（8 队列帧） |
| `outputs/confirmatory/` | 四库确证+survey 链+prevalence_gate_* |
| `outputs/agent/` | agent 诊断+合成回归产物 |
| `outputs/paper/` `outputs/submission/` | 两条论文线与投稿包 |
| `outputs/tables/`、`outputs/figures/` | 交付表 8 张、论文图 6 张 |

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
