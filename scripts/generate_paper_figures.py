#!/usr/bin/env python
"""按图件契约渲染论文图（R10 2026-10-15 实装，取代 WO-25 存根）。

可渲染：figure1（架构示意）、figure2（性能 4 面板）、figure4（演示病例）、
figure5（推理链）。
明确跳过：figure3（source_data 标注 NOT_COLLECTABLE——4 专家盲评从未实施，
渲染即伪造，反伪造条款优先于契约完整性）。

数据源：outputs/figures/source_data/*.csv；figure2 panel_b/d 补充读取
outputs/baseline_predictions.jsonl（逐对预测与 kg_chars，聚合值无法还原分布）。
导出：png + pdf（dpi=600，尺寸按契约 export.dimensions_mm）。
字体：契约要求 Arial；缺失时回退 DejaVu Sans（Windows 通常自带 Arial）。

Run: PYTHONUTF8=1 python scripts/generate_paper_figures.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "outputs" / "figures"
SD = FIG / "source_data"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 7, "axes.linewidth": 0.8,
    "svg.fonttype": "none", "pdf.fonttype": 42,
})
C_PRIMARY, C_SEC, C_TER, C_WARN, C_GREY = "#5B8FF9", "#61DDAA", "#F6BD16", "#E8684A", "#B8B8B8"


def _mm(figsize_of_contract: dict):
    w, h = figsize_of_contract["export"]["dimensions_mm"]
    return (w / 25.4, h / 25.4)


def _load(fig_id: str):
    return yaml.safe_load((FIG / "contracts" / f"{fig_id}.yaml").read_text(encoding="utf-8"))


def _save(fig, fig_id: str) -> None:
    for ext in ("png", "pdf", "svg", "tiff"):
        kw = {"dpi": 600, "bbox_inches": "tight"}
        if ext == "tiff":
            kw["pil_kwargs"] = {"compression": "tiff_lzw"}
        fig.savefig(FIG / f"{fig_id}.{ext}", **kw)
    plt.close(fig)
    print(f"[render] {fig_id}.png / .pdf / .svg / .tiff")


# ── Figure 1 ────────────────────────────────────────────────
def render_figure1() -> None:
    ct = _load("figure1_architecture")
    q = pd.read_csv(SD / "figure1_data.csv", encoding="utf-8-sig")
    fig = plt.figure(figsize=_mm(ct), dpi=600)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.5, 1], hspace=0.32, wspace=0.25)

    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    boxes = [("User input\n(A×B\n+ factors)", 0.03), ("Normal-\nization", 0.19),
             ("Rule Engine\n21 rules", 0.35), ("LightRAG\n27k-node KG", 0.51),
             ("LLM Arbiter\n(qwen, t=0)", 0.67), ("Report", 0.83)]
    for label, x in boxes:
        ax.add_patch(plt.Rectangle((x, 0.40), 0.135, 0.26, transform=ax.transAxes,
                                   fc=C_PRIMARY, ec="black", lw=0.6, alpha=0.85))
        ax.text(x + 0.0675, 0.53, label, ha="center", va="center", fontsize=5.6,
                transform=ax.transAxes)
        if x < 0.8:
            ax.annotate("", xy=(x + 0.158, 0.53), xytext=(x + 0.137, 0.53),
                        xycoords="axes fraction", arrowprops=dict(arrowstyle="-|>", lw=0.8))
    ax.set_title("a  End-to-end pipeline", loc="left", fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[1, 0]); ax.axis("off")
    for i, (name, note, color) in enumerate([("Rules", "deterministic", C_PRIMARY),
                                             ("KG (LightRAG)", "traceable", C_SEC),
                                             ("LLM arbiter", "flexible", C_TER)]):
        y = 0.72 - i * 0.28
        ax.add_patch(plt.Rectangle((0.08, y), 0.84, 0.2, transform=ax.transAxes,
                                   fc=color, ec="black", lw=0.6, alpha=0.85))
        ax.text(0.5, y + 0.1, f"{name} — {note}", ha="center", va="center",
                fontsize=7, transform=ax.transAxes)
        if i < 2:
            ax.annotate("", xy=(0.5, y - 0.08), xytext=(0.5, y - 0.005),
                        xycoords="axes fraction", arrowprops=dict(arrowstyle="-|>", lw=0.8))
    ax.set_title("b  Three layers", loc="left", fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[1, 1]); ax.axis("off")
    cells = ["clinician card", "patient handout", "research table", "policy brief"]
    for i, c in enumerate(cells):
        ax.add_patch(plt.Rectangle((0.05 + (i % 2) * 0.48, 0.52 - (i // 2) * 0.4),
                                   0.42, 0.32, transform=ax.transAxes,
                                   fc=C_GREY, ec="black", lw=0.5, alpha=0.5))
        ax.text(0.05 + (i % 2) * 0.48 + 0.21, 0.52 - (i // 2) * 0.4 + 0.16, c,
                ha="center", va="center", fontsize=6.5, transform=ax.transAxes)
    ax.set_title("c  Output views (single pass)", loc="left", fontsize=8, fontweight="bold")

    quant = " | ".join(f"{r.component}:{r.metric}={r.value}" for r in q.itertuples())
    fig.text(0.5, 0.005, quant, ha="center", fontsize=4.6, color="#555555", wrap=True)
    _save(fig, "figure1_architecture")


# ── Figure 2 ────────────────────────────────────────────────
def render_figure2() -> None:
    ct = _load("figure2_performance")
    perf = pd.read_csv(SD / "figure2_performance.csv", encoding="utf-8-sig")
    fig = plt.figure(figsize=_mm(ct), dpi=600)
    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.3)

    ax = fig.add_subplot(gs[0, 0])
    # R17 双代分组柱状:qwen 80 对 + zhipu 159 对,各 4 方法
    gens = [("v1.2 (qwen, 80-pair gold)", "qwen|80-pair"),
            ("v1.2 (zhipu GLM-5.3-flash, 159-pair gold)", "zhipu|159-pair")]
    methods = [m for m in ["full_system", "lightrag", "pure_llm", "naive_rag"]
               if (perf.method == m).any()]
    labels = {"full_system": "full", "lightrag": "lightrag",
              "pure_llm": "pure_llm", "naive_rag": "naive"}
    xw = 0.19
    group_x = np.arange(len(gens))
    colors = [C_PRIMARY, C_SEC, C_TER, C_WARN]
    xw = 0.19
    group_x = np.arange(len(methods))
    gen_colors = [C_PRIMARY, C_TER]
    gen_labels = [g[1] for g in gens]
    for gi, (rs_name, rs_label) in enumerate(gens):
        gen = perf[perf.ruleset == rs_name]
        if gen.empty:
            continue
        offs = (gi - 0.5) * xw * 2
        vals = []
        for m in methods:
            row = gen[gen.method == m]
            vals.append(float(row.F1_mean.iloc[0]) if len(row) else 0.0)
        bars = ax.bar(group_x + offs, vals, width=xw, color=gen_colors[gi],
                      ec="black", lw=0.5, label=rs_label)
        for xi, v in zip(group_x + offs, vals):
            if v > 0:
                ax.text(xi, v + 0.012, f"{v:.2f}", ha="center", fontsize=4.6)
    ax.set_xticks(group_x)
    ax.set_xticklabels([labels[m] for m in methods], fontsize=6)
    ax.set_ylabel("F1 (mean, 5 seeds)")
    ax.set_ylim(0, 0.55)
    ax.legend(fontsize=5, loc="upper right", framealpha=0.9)
    ax.set_title("a  NHANES dual-generation baselines", loc="left",
                 fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[0, 1])
    recs = [json.loads(l) for l in
            (ROOT / "outputs/baseline_predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    # Panel b scores the primary (qwen, 80-pair) generation only. Pooling both
    # generations would count 239 rows per seed and mix two different golds;
    # the earlier version did exactly that. Gold comes from the R11-corrected
    # confirmatory table, keyed on (a_flag, b_item).
    qwen_pairs = {(r["a_flag"], r["b_item"]) for r in recs
                  if r["baseline"] == "lightrag"
                  and r["provider"] == "local:qwen3.8-27b"}
    gold = pd.read_csv(ROOT / "outputs/confirmatory/nhanes_confirmatory.csv",
                       encoding="utf-8-sig").drop_duplicates(
                           ["a_flag", "b_item"]).set_index(
                               ["a_flag", "b_item"])["gold3"].to_dict()
    fs = {}
    for r in recs:
        if (r["baseline"] == "full_system" and r["seed"] == 11
                and (r["a_flag"], r["b_item"]) in qwen_pairs):
            fs.setdefault((r["a_flag"], r["b_item"]), r)
    states = ["replicated", "contradicted", "uninformative"]
    mat = np.array([[sum(1 for k, r in fs.items()
                         if r["prediction"] and gold.get(k, r["gold3"]) == s)
                     for s in states],
                    [sum(1 for k, r in fs.items()
                         if not r["prediction"] and gold.get(k, r["gold3"]) == s)
                     for s in states]])
    ax.imshow(mat, cmap="Blues", vmin=0, vmax=mat.max())
    for i in range(2):
        for j in range(3):
            ax.text(j, i, str(mat[i, j]), ha="center", va="center", fontsize=7,
                    color="white" if mat[i, j] > mat.max() * 0.6 else "black")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["replicated", "contra-\ndicted", "uninformative"],
                       fontsize=5.5)
    ax.set_yticks(range(2)); ax.set_yticklabels(["predict YES", "predict NO"], fontsize=6)
    ax.set_title("b  full_system × R11 gold (80 pairs)", loc="left",
                 fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[1, 0])
    conf = ROOT / "outputs/confirmatory"
    nm = json.loads((conf / "nhanes_metrics_v11.json").read_text(encoding="utf-8"))
    km = json.loads((conf / "knhanes_metrics_v11.json").read_text(encoding="utf-8"))
    for metric, y in [("coverage", 1), ("precision_rule", 0)]:
        vals = [nm[metric], km[metric]]
        ax.plot([vals[0], vals[1]], [y, y], "-", color=C_GREY, lw=1)
        ax.plot(vals[0], y, "o", color=C_PRIMARY, ms=5)
        ax.plot(vals[1], y, "o", color=C_WARN, ms=5)
        ax.text(vals[0] - 0.04, y, f"NHANES\n{vals[0]}", fontsize=5.5, ha="right",
                va="center", color=C_PRIMARY)
        ax.text(vals[1] + 0.04, y, f"KNHANES\n{vals[1]}", fontsize=5.5, ha="left",
                va="center", color=C_WARN)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["precision_rule", "coverage"], fontsize=6.5)
    ax.set_xlim(-0.35, 1.45); ax.set_ylim(-0.4, 1.6)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.tick_params(labelsize=6)
    ax.set_title("c  Internal vs transportability check", loc="left", fontsize=8,
                 fontweight="bold")

    ax = fig.add_subplot(gs[1, 1])
    kg = [r["kg_chars"] for r in recs
          if r["baseline"] == "lightrag"
          and r["provider"] == "local:qwen3.8-27b"
          and r.get("kg_chars")]
    ax.hist(kg, bins=30, color=C_SEC, ec="black", lw=0.4)
    ax.set_xlabel("retrieved KG context size (chars)", fontsize=6)
    ax.set_ylabel("runs (5 seeds × 80 pairs)", fontsize=6)
    ax.tick_params(labelsize=6)
    ax.set_title("d  lightrag context size", loc="left", fontsize=8, fontweight="bold")
    _save(fig, "figure2_performance")


# ── Figure 4 ────────────────────────────────────────────────
def render_figure4() -> None:
    ct = _load("figure4_demo_case")
    case = pd.read_csv(SD / "figure4_demo_case.csv", encoding="utf-8-sig")
    fig = plt.figure(figsize=_mm(ct), dpi=600)
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1.2, 1], hspace=0.55, wspace=0.3)

    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.25), 0.29, 0.5, transform=ax.transAxes,
                               fc=C_PRIMARY, ec="black", lw=0.6, alpha=0.85))
    ax.add_patch(plt.Rectangle((0.35, 0.25), 0.29, 0.5, transform=ax.transAxes,
                               fc=C_SEC, ec="black", lw=0.6, alpha=0.85))
    ax.add_patch(plt.Rectangle((0.68, 0.25), 0.3, 0.5, transform=ax.transAxes,
                               fc=C_TER, ec="black", lw=0.6, alpha=0.85))
    ax.text(0.165, 0.5, "Entity A\nhba1c_elevated\n(glycation_metabolic)", ha="center",
            va="center", fontsize=6.5, transform=ax.transAxes)
    ax.text(0.495, 0.5, "Entity B\nretinopathy_any /\ndr_pdr", ha="center", va="center",
            fontsize=6.5, transform=ax.transAxes)
    row = case.iloc[0]
    ax.text(0.83, 0.5, f"NHANES confirmatory\nOR={row.OR_nhanes:.2f}\nq={row.q_bhy:.1e}\ngold3={row.gold3}",
            ha="center", va="center", fontsize=6, transform=ax.transAxes)
    ax.set_title("a  Demo case input + confirmatory outcome", loc="left",
                 fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[1, 0])
    sig = [("retinopathy_any\n(r03, medium/B)", 2, C_WARN),
           ("dr_pdr (r04,\nlow/C)", 1, C_PRIMARY)]
    ax.barh([s[0] for s in sig], [s[1] for s in sig],
            color=[s[2] for s in sig], ec="black", lw=0.5)
    ax.set_xlim(0, 3.3); ax.tick_params(labelsize=6)
    ax.set_title("b  Triggered rules", loc="left", fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[1, 1]); ax.axis("off")
    lv_counts = {"B": 2, "C": 1}
    for i, name in enumerate(["A regulatory/guideline", "B pooled/mechanism-rich",
                              "C single cohort", "D weak", "E mechanism only"]):
        w = 0.9 - i * 0.13
        ax.add_patch(plt.Rectangle((0.5 - w / 2, 0.06 + i * 0.18), w, 0.14,
                                   transform=ax.transAxes, fc=C_PRIMARY,
                                   ec="black", lw=0.5, alpha=0.3 + i * 0.14))
        n = lv_counts.get(name[0], 0)
        label = f"{name}  ({n} hit)" if n else name
        ax.text(0.5, 0.06 + i * 0.18 + 0.07, label,
                ha="center", va="center", fontsize=5.8, transform=ax.transAxes)
    ax.set_title("c  Evidence pyramid (this case)", loc="left", fontsize=8, fontweight="bold")

    ax = fig.add_subplot(gs[2, :]); ax.axis("off")
    nodes = ["rule hits\nr03+r04", "evidence\n(B×2, C×1)", "LLM arbiter\n(YES, temp=0)",
             "risk level\nlow→medium", "report\n+ trace"]
    for i, label in enumerate(nodes):
        x = 0.04 + i * 0.195
        ax.add_patch(plt.Rectangle((x, 0.35), 0.15, 0.3, transform=ax.transAxes,
                                   fc=C_SEC if i == 1 else C_PRIMARY,
                                   ec="black", lw=0.6, alpha=0.85))
        ax.text(x + 0.075, 0.5, label, ha="center", va="center", fontsize=6,
                transform=ax.transAxes)
        if i < len(nodes) - 1:
            ax.annotate("", xy=(x + 0.2, 0.5), xytext=(x + 0.155, 0.5),
                        xycoords="axes fraction", arrowprops=dict(arrowstyle="-|>", lw=0.8))
    ax.set_title("d  Traceability flow", loc="left", fontsize=8, fontweight="bold")
    _save(fig, "figure4_demo_case")


# ── Figure 5 ────────────────────────────────────────────────
def render_figure5() -> None:
    ct = _load("figure5_reasoning_trace")
    trace = pd.read_csv(SD / "figure5_reasoning_trace.csv", encoding="utf-8-sig")
    paths = pd.read_csv(SD / "figure5_paths.csv", encoding="utf-8-sig")
    fig = plt.figure(figsize=_mm(ct), dpi=600)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.3, 1], hspace=0.5)

    lane_y = {"Rule Engine": 0.72, "LightRAG KG": 0.48, "LLM Arbiter / Report": 0.24}
    rule_lane = {"normalize": "Rule Engine", "rule_engine": "Rule Engine",
                 "kg_retrieval": "LightRAG KG", "arbiter": "LLM Arbiter / Report",
                 "report": "LLM Arbiter / Report"}
    ax = fig.add_subplot(gs[0]); ax.axis("off")
    for name, y in lane_y.items():
        ax.plot([0, 1], [y, y], transform=ax.transAxes, color=C_GREY, lw=0.5, alpha=0.5)
        ax.text(0.005, y + 0.06, name, fontsize=6, transform=ax.transAxes)
    order = trace.sort_values("step_id")
    xs = np.linspace(0.14, 0.92, len(order))
    lane_color = {"normalize": C_PRIMARY, "rule_engine": C_PRIMARY,
                  "kg_retrieval": C_SEC, "arbiter": C_TER, "report": C_TER}
    steps = []
    for (_, row), x in zip(order.iterrows(), xs):
        y = lane_y[rule_lane[row.layer]]
        step_no = int(str(row.step_id).replace("step", ""))
        ax.plot([x], [y], "o", ms=9, color=lane_color[row.layer], mec="black", mew=0.5)
        ax.text(x, y, str(step_no), fontsize=5, ha="center", va="center", color="white")
        steps.append((step_no, row.layer, row.content))
    ax.set_ylim(0.0, 1.0)
    ax.set_title("a  Reasoning trace: hba1c_elevated × dr_pdr (numbered steps below)",
                 loc="left", fontsize=8, fontweight="bold")
    legend = "   ".join(f"s{n} [{lay}] {txt}" for n, lay, txt in steps)
    ax.text(0.0, 0.03, legend, fontsize=5, va="bottom", ha="left", wrap=True,
            transform=ax.transAxes, color="#333333")

    ax = fig.add_subplot(gs[1]); ax.axis("off")
    chain = ["hba1c_elevated", "hyperglycemia", "retinal_ischemia", "VEGF_upregulation",
             "neovascularization", "dr_pdr"]
    nodes = sorted(set(paths.source_node) | set(paths.target_node))
    pos = {n: (0.06 + i * 0.16, 0.62) for i, n in enumerate(chain)}
    for i, n in enumerate([n for n in nodes if n not in pos]):
        pos[n] = (0.15 + i * 0.35, 0.15)
    for _, e in paths.iterrows():
        x1, y1 = pos[e.source_node]; x2, y2 = pos[e.target_node]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), xycoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", lw=0.8,
                                    color=C_WARN if e.edge_type == "rule_covers" else C_PRIMARY))
    for n, (x, y) in pos.items():
        ax.text(x, y + 0.1, n, fontsize=5.5, ha="center", transform=ax.transAxes)
    ax.set_title("b  KG path: flag → mechanism chain → outcome (orange = rule coverage)",
                 loc="left", fontsize=8, fontweight="bold")
    fig.text(0.02, 0.01, "panel latency_breakdown: per-layer timings were not logged in "
                         "R5 runs — omitted rather than fabricated.", fontsize=5.5,
             color="#777777")
    _save(fig, "figure5_reasoning_trace")


def main() -> int:
    print("[DEPRECATED] figures are rendered by scripts/render_top_figures.py; delegating.")
    import subprocess
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "render_top_figures.py")])

def _legacy_main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    skip = []
    f3 = SD / "figure3_expert_agreement.csv"
    if "NOT_COLLECTABLE" in f3.read_text(encoding="utf-8-sig", errors="ignore"):
        skip.append("figure3_expert_agreement（反伪造条款：4 专家盲评从未实施，不渲染）")
    failed = []
    for fn in (render_figure1, render_figure2, render_figure4, render_figure5):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 — 单图失败不阻断其余
            failed.append(fn.__name__)
            print(f"[render] FAILED {fn.__name__}: {e}", file=sys.stderr)
    for s in skip:
        print(f"[render] SKIP {s}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
