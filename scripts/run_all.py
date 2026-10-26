#!/usr/bin/env python
"""R11-D1 (2026-10-15): canonical pipeline runner — 固化 8 步确证链。

存在动机：单独跑 scripts/evaluate.py 会用 freq_weights 口径覆盖 headline 并删掉
svy 列（R11 实测）——canonical 顺序必须整体执行。本脚本按序运行全链并在任一步
非零退出时立即停止（fail-loud），避免半链状态污染交付物。

默认只跑纯本地步骤（不需要 LLM/NCBI）；--with-baseline 追加基线汇总与 bootstrap。

Run:
  PYTHONUTF8=1 python scripts/run_all.py
  PYTHONUTF8=1 python scripts/run_all.py --with-baseline
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("校验资产完整性", [sys.executable, "scripts/build_entity_a_registry.py"]),
    ("", [sys.executable, "scripts/build_entity_b_registry.py"]),
    ("", [sys.executable, "scripts/build_evidence_base.py"]),
    ("", [sys.executable, "scripts/generate_cases.py"]),
    ("NHANES 确证", [sys.executable, "scripts/evaluate.py", "--dataset", "intval-nhanes"]),
    ("KNHANES 确证", [sys.executable, "scripts/evaluate_knhanes.py"]),
    ("CHARLS 确证", [sys.executable, "scripts/evaluate_charls.py"]),
    ("CHARLS 2015", [sys.executable, "scripts/evaluate_charls2015.py"]),
    ("survey 导出", [sys.executable, "scripts/survey_sensitivity_export.py"]),
    ("survey svyglm", ["Rscript", "scripts/survey_sensitivity_R5.R"]),
    ("回写主口径", [sys.executable, "scripts/apply_survey_variance.py"]),
    ("重建交付物", [sys.executable, "scripts/rebuild_deliverables_R5.py"]),
    ("生成/校验表", [sys.executable, "scripts/generate_paper_tables.py"]),
    ("渲染图", [sys.executable, "scripts/render_top_figures.py"]),
    ("基线 gold 双呈", [sys.executable, "scripts/make_baseline_summary_R11_goldcheck.py"]),
]
BASELINE_STEPS = [
    ("基线汇总(R5 记录)", [sys.executable, "scripts/make_baseline_summary_R5.py"]),
    ("bootstrap CI", [sys.executable, "scripts/make_baseline_bootstrap_ci.py"]),
]


def main() -> int:
    steps = STEPS + (BASELINE_STEPS if "--with-baseline" in sys.argv else [])
    for name, cmd in steps:
        label = name or "(续)"
        print(f"\n=== {label}: {' '.join(cmd[1:])} ===", flush=True)
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            print(f"[run_all] FAIL at {label} (exit {r.returncode}) — 链在此中断，"
                  f"交付物可能处于中间状态，勿直接引用", file=sys.stderr)
            return r.returncode
    print("\n[run_all] 全链完成（headline=survey svyglm 主口径）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
