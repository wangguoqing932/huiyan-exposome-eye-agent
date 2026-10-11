# 慧眼（huiyan）

**慧眼** — A oxidative_stress, glycation_metabolic, inflammation_immune, vascular_perfusion, endocrine_hormonal, heavy_metal_toxicity, photochemical_uv rule-based decision support framework for screening **暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证** in diabetic, hypertensive, rural_china, multi_country, with a focus on 多库跨文化验证：规则仅由文献/指南构建，性能在 NHANES（内部）→ KNHANES（独立国家）→ 9 国老龄队列（跨人群）三层独立验证并报告泛化落差；首个可解释的暴露组×眼病风险筛查 agent（暴露→机制→眼病→证据等级 全链溯源）.

This project reuses the methodology skeleton of **TongYuan** (FDI screening, *Nutrients* submission) and applies it to a new domain: 暴露组（代谢-营养-生活方式-环境） × 主要致盲眼病 combinations.

## Project Status

📋 **In execution (executor phase 3).** This project was scaffolded by the `medical-agent-planner` skill. The PLAN.md, README.md, pyproject.toml, schemas, and rule YAML templates are in place; the coding agent should now execute Phase 0 → Phase 8 per [PLAN.md](PLAN.md).

## Quick Navigation

| Document | Purpose |
|---|---|
| [PLAN.md](PLAN.md) | Master execution plan (8 phases, task list, subagent strategy, timeline) |
| `.planner.config.json` | Phase 1 investigation output (input to scaffold) |
| `src/huiyan_agent/` | Core source code (to be migrated from TongYuan) |
| `configs/rules.yaml` | Rule engine configuration (to be authored) |
| `data/seed/` | Knowledge base: entities_a.csv, entities_b.csv, evidence_chunks.jsonl (to be built) |

## Differentiation from Reference Project

| Dimension | Reference (TongYuan) | This Project |
|---|---|---|
| Entity A | food | 暴露组（代谢-营养-生活方式-环境） |
| Entity B | drug | 主要致盲眼病 |
| Interaction type | FDI | oxidative_stress, glycation_metabolic, inflammation_immune, vascular_perfusion, endocrine_hormonal, heavy_metal_toxicity, photochemical_uv |
| Rules | 15 | 12 |
| Data sources | FDA + USDA + LiverTox | NHANES 1999-2008 本地原始库（生化/膳食/毒物 + VIX 客观视力 / OPXRET 视网膜分级 / VIQ 眼病问卷）[local_confirmed], KNHANES 1998-2024 本地 Rdata 全集 + 官方变量字典（眼科检查模块，1,686 眼科变量）[local_confirmed], 9 大老龄队列原始库（CHARLS/HRS/ELSA/SHARE/KLoSA/LASI/MHAS/CRELES/CLHLS）[local_confirmed], GBD 视觉库（GBD 2023 近视力丧失 / 2023 盲与视力损害 / 2021 55+ 暴露-结局）[local_confirmed] |
| Target journal | Nutrients | Ophthalmology（IF 8+ 档候选；Phase 2 期刊适配检查后最终锁定） |

## Methodology Pipeline

```text
User input (暴露组（代谢-营养-生活方式-环境） + 主要致盲眼病 + patient factors)
  → entity normalization
  → rule-based screening (12 rules)
  → graph-organized evidence retrieval (LightRAG)
  → evidence compression (top-k, char limit)
  → structured safety report
  → expert-review export / evaluation
```

## Setup (conda env per project, Chinese mirrors pre-configured)

The default flow creates a **conda env named after this project** (`huiyan`) and installs all deps there.

```bash
python scripts/setup_environment.py --project-root . --mirror cn
conda activate huiyan
```

This will:
- `conda create -n huiyan python=3.11 -y` if the env doesn't exist (idempotent)
- Install `[dev, llm, lightrag, streamlit]` extras from `pyproject.toml`
- Configure Tsinghua PyPI / TUNA conda / hf-mirror.com mirrors
- Prompt for `DEEPSEEK_API_KEY` (chat) and `ARK_DOUBAO_API_KEY` (火山方舟 embedding) on first run

Alternatives:

```bash
# Different Python version
python scripts/setup_environment.py --project-root . --mirror cn --python 3.12

# Non-interactive (CI / scripted): pre-fill keys in .env first
python scripts/setup_environment.py --project-root . --mirror cn --non-interactive

# Fallback to local .venv if conda is unavailable
python scripts/setup_environment.py --project-root . --mirror cn --env-mode venv
```

Later sessions inside this project can re-discover the env via:

```bash
python C:/Users/heyb1/.claude/skills/medical-agent-planner/scripts/conda_helper.py discover --project-root .
```

## Execution Entry Point

The full development plan is in [PLAN.md](PLAN.md). To regenerate all artifacts from scratch:

```bash
# 1. Build knowledge base
python scripts/build_entity_a_registry.py
python scripts/build_entity_b_registry.py
python scripts/build_evidence_base.py

# 2. Fetch real evidence (needs NCBI + LLM keys in .env)
python scripts/fetch_pubmed.py --max-pairs 40
python scripts/scripts/build_evidence_base.py

# 3. Build validation sets + run baselines + evaluate
python scripts/generate_cases.py --target 400
python scripts/run_baselines.py
python scripts/run_multiseed.py --seeds 5
python scripts/evaluate.py

# 4. Generate figures/tables
python scripts/generate_paper_figures.py
python scripts/generate_paper_tables.py
```

## Interactive Demo (Streamlit)

```bash
pip install -e ".[streamlit]"
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501.

> ⚠️ The demo is for clinical decision support only and does not replace clinician or pharmacist judgement.

## Target Output

- Reproducible Python package with ~80% code reuse from TongYuan
- Validated 暴露组×眼病可解释风险筛查：代谢-营养-生活方式-环境四域暴露（含组合/交互）与主要眼病的关联筛查（规则引擎+知识图谱+LLM 仲裁混合系统），跨库跨国多源验证 screening system (4-phase validation)
- Manuscript submitted to *Ophthalmology（IF 8+ 档候选；Phase 2 期刊适配检查后最终锁定）* (or fallback journal)

## License

For peer review and academic reproducibility. All data derived from publicly available sources.
