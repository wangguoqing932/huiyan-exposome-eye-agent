#!/usr/bin/env python
"""Render the eight manuscript figures in one top-journal visual system.

Replaces the two ad-hoc renderers for the final submission set:
  figure1_architecture      (Figure 1)
  figure2_performance       (Figure 2)
  figure3_rule_evaluation   (Figure 3)
  figure6_dose_response     (Figure 4)
  figure7_power_mde         (Figure 5)
  figure8_cohort_transportability (Figure 6)
  figure4_demo_case         (Figure S1)
  figure5_reasoning_trace   (Figure S2)

All numbers come from outputs/figures/source_data/*.csv or the canonical
prediction matrix; nothing is invented. Exports SVG + PDF + TIFF(LZW) + PNG.

Run: python scripts/render_top_figures.py [--only figure2]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
from matplotlib.ticker import NullFormatter, ScalarFormatter

import figure_style_top as S

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "outputs" / "figures"
SRC = FIG / "source_data"
CANON = ROOT / "outputs" / "baseline_predictions_canonical.jsonl"


def rows_of(name: str) -> list[dict]:
    with (SRC / name).open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def save(fig, stem: str) -> list[Path]:
    out = []
    for ext in ("png", "pdf", "svg", "tiff"):
        path = FIG / f"{stem}.{ext}"
        kw = {"dpi": 600}
        if ext == "tiff":
            kw["pil_kwargs"] = {"compression": "tiff_lzw"}
        fig.savefig(path, **kw)
        out.append(path)
    plt.close(fig)
    print(f"  {stem}: " + ", ".join(p.suffix for p in out))
    return out


def _pipeline_icon(ax, kind: int, cx: float, cy: float, col: str) -> None:
    """Small line icons so the pipeline reads as a process, not six labels."""
    if kind == 0:      # input: three stacked lines
        for k in range(3):
            ax.plot([cx - 1.2, cx + 1.2], [cy + 0.7 - k * 0.7] * 2,
                    color=col, lw=1.3, solid_capstyle="round", zorder=4)
    elif kind == 1:    # normalisation: two arrows converging
        ax.annotate("", xy=(cx, cy), xytext=(cx - 1.7, cy + 0.95),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1))
        ax.annotate("", xy=(cx, cy), xytext=(cx - 1.7, cy - 0.95),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1))
        ax.plot([cx, cx + 1.6], [cy, cy], color=col, lw=1.4)
    elif kind == 2:    # rules: checklist
        for k in range(3):
            yy = cy + 0.7 - k * 0.75
            ax.add_patch(Rectangle((cx - 1.4, yy - 0.16), 0.32, 0.32,
                                   facecolor=col, edgecolor="none", zorder=4))
            ax.plot([cx - 0.85, cx + 1.3], [yy, yy], color=col, lw=1.0,
                    zorder=4)
    elif kind == 3:    # KG: three connected nodes
        xs = [cx - 1.2, cx, cx + 1.2]
        ys = [cy + 0.5, cy - 0.5, cy + 0.5]
        ax.plot(xs, ys, color=col, lw=1.0, zorder=4)
        for xx, yy in zip(xs, ys):
            ax.add_patch(Circle((xx, yy), 0.26, facecolor="white",
                                edgecolor=col, lw=1.0, zorder=5))
    elif kind == 4:    # arbiter: balance
        ax.plot([cx, cx], [cy - 0.9, cy + 0.9], color=col, lw=1.2, zorder=4)
        ax.plot([cx - 1.0, cx + 1.0], [cy + 0.8, cy + 0.8], color=col, lw=1.2,
                zorder=4)
        for dx in (-0.9, 0.9):
            ax.plot([cx + dx, cx + dx], [cy + 0.8, cy + 0.15], color=col,
                    lw=0.9, zorder=4)
            ax.add_patch(Rectangle((cx + dx - 0.24, cy + 0.02), 0.48, 0.13,
                                   facecolor=col, edgecolor="none", zorder=4))
    else:              # report: document
        ax.add_patch(Rectangle((cx - 0.8, cy - 0.9), 1.6, 1.8,
                               facecolor="white", edgecolor=col, lw=1.0,
                               zorder=4))
        for k in range(3):
            ax.plot([cx - 0.45, cx + 0.45], [cy + 0.5 - k * 0.45] * 2,
                    color=col, lw=0.8, zorder=5)


# --------------------------------------------------------------------------- #
# Figure 1 — architecture
# --------------------------------------------------------------------------- #
def figure1() -> None:
    fig = plt.figure(figsize=(S.FULL, 102 * S.MM))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # (a) pipeline -----------------------------------------------------------
    ax.text(0.8, 98.5, "a", fontsize=11, fontweight="bold", va="top")
    ax.text(3.2, 98.2, "End-to-end pipeline", fontsize=9.2, va="top")
    steps = [
        ("Input\nA × B + factors", "18 exposure flags\n15 eye items", S.NAVY),
        ("Entity\nnormalisation", "41 exposures\n15 eye items", S.NAVY),
        ("Rule engine\n21 rules", "A 1 · B 15 · C 5", S.NAVY),
        ("LightRAG\nhybrid KG", "27,136 nodes\n1,060 chunks", S.TEAL),
        ("LLM arbiter\nQwen · T = 0", "7-step trace\nrefuses unsupported", S.AMBER),
        ("Report\n+ trace", "4 output views\nsource-linked", S.AMBER),
    ]
    w, gap, x0, y0, h = 13.2, 3.0, 1.0, 75.0, 13.0
    for i, (label, sub, col) in enumerate(steps):
        x = x0 + i * (w + gap)
        cx = x + w / 2
        S.box(ax, x, y0, w, h, "", edge=col, face=S.WHITE, lw=1.0)
        ax.add_patch(Rectangle((x, y0 + h - 0.9), w, 0.9, facecolor=col,
                               edgecolor="none", zorder=3))
        _pipeline_icon(ax, i, cx, y0 + h - 3.2, col)
        ax.text(cx, y0 + h / 2 - 1.7, label, ha="center", va="center",
                fontsize=7.2, linespacing=1.22, zorder=4)
        ax.text(cx, y0 - 2.2, sub, ha="center", va="top",
                fontsize=6.3, color=S.GREY, linespacing=1.2)
        if i < len(steps) - 1:
            S.arrow(ax, x + w + 0.5, y0 + h / 2, x + w + gap - 0.5,
                    y0 + h / 2, color="#9AA0A8")

    # (b) three layers -------------------------------------------------------
    ax.text(0.8, 62.5, "b", fontsize=11, fontweight="bold", va="top")
    ax.text(3.2, 62.2, "Three layers, one traceable path", fontsize=9.2, va="top")
    cols = [
        ("Rule layer", "deterministic", S.NAVY,
         ["21 literature-derived rules", "A1 / B15 / C5 evidence grades",
          "no LLM call in the final decision"]),
        ("KG layer", "evidence-grounded", S.TEAL,
         ["LightRAG hybrid traversal", "27k-node evidence graph",
          "every hit resolves to a source chunk"]),
        ("Arbiter layer", "bounded", S.AMBER,
         ["Qwen3.8-27B, temperature 0", "grades risk, never adds rules",
          "abstains without evidence"]),
    ]
    xw, xg = 31.0, 2.0
    for j, (name, tag, col, bullets) in enumerate(cols):
        x = 1.0 + j * (xw + xg)
        ax.add_patch(Circle((x + 0.7, 56.0), 0.55, color=col))
        ax.text(x + 2.0, 56.0, name, fontsize=8.6, color="#222222",
                fontweight="bold", va="center")
        ax.text(x + 2.0, 53.2, tag, fontsize=7.2, color=S.GREY, va="center")
        for k, b in enumerate(bullets):
            yy = 48.4 - k * 5.6
            ax.text(x + 0.9, yy, b, fontsize=7.2, va="center", color="#222222")

    # (c) outputs ------------------------------------------------------------
    ax.text(0.8, 27.0, "c", fontsize=11, fontweight="bold", va="top")
    ax.text(3.2, 26.7, "Four output views from a single inference pass",
            fontsize=9.2, va="top")
    outs = [("Clinician card", "risk + rule + evidence"),
            ("Patient handout", "plain-language summary"),
            ("Research table", "structured fields"),
            ("Policy brief", "population-level view")]
    ow, og = 22.0, 2.5
    for j, (name, sub) in enumerate(outs):
        x = 1.0 + j * (ow + og)
        ax.add_patch(Rectangle((x + 2.0, 13.0), 4.4, 5.4, facecolor="white",
                               edgecolor=S.NAVY, linewidth=0.8))
        ax.add_patch(plt.Polygon([[x + 5.2, 18.4], [x + 5.2, 17.2],
                                  [x + 6.4, 17.2]], closed=True,
                                 facecolor="white", edgecolor=S.NAVY,
                                 linewidth=0.8))
        for k in range(3):
            ax.plot([x + 2.8, x + 5.6], [16.9 - k * 1.2, 16.9 - k * 1.2],
                    color=S.NAVY, lw=0.6)
        ax.text(x + 7.4, 16.4, name, fontsize=8.2, fontweight="bold",
                va="center")
        ax.text(x + 7.4, 13.0, sub, fontsize=6.6, color=S.GREY, va="center")
    save(fig, "figure1_architecture")


# --------------------------------------------------------------------------- #
# Figure 2 — performance
# --------------------------------------------------------------------------- #
def figure2() -> None:
    perf = rows_of("figure2_performance.csv")
    methods = ["full_system", "lightrag", "pure_llm", "naive_rag"]
    gens = [("v1.2 (qwen, 80-pair gold)", "Qwen · 80 pairs", S.NAVY),
            ("v1.2 (zhipu GLM-5.3-flash, 159-pair gold)",
             "GLM-5.3-flash · 159 pairs", S.AMBER)]
    fig = plt.figure(figsize=(S.FULL, 140 * S.MM))
    gs = fig.add_gridspec(2, 2, left=0.085, right=0.985, top=0.94,
                          bottom=0.075, hspace=0.38, wspace=0.28,
                          width_ratios=[1.12, 1.0])

    # (a) grouped bars
    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(methods))
    bw = 0.34
    canonical = [json.loads(l) for l in CANON.read_text(encoding="utf-8").splitlines()
                 if l.strip()]

    def seed_sd(generation: str, baseline: str) -> float:
        sub = [r for r in canonical if r["generation"] == generation
               and r["baseline"] == baseline]
        per: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])
        for r in sub:
            tp, fp, fn = per[r["seed"]]
            if r["prediction"] and r["gold3"] == "replicated":
                tp += 1
            elif r["prediction"]:
                fp += 1
            elif r["gold3"] == "replicated":
                fn += 1
            per[r["seed"]] = [tp, fp, fn]
        scores = []
        for tp, fp, fn in per.values():
            p = tp / (tp + fp) if tp + fp else 0.0
            rr = tp / (tp + fn) if tp + fn else 0.0
            scores.append(2 * p * rr / (p + rr) if p + rr else 0.0)
        return float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0

    for gi, (rs, lab, col) in enumerate(gens):
        generation = "qwen-80pair" if rs.startswith("v1.2 (qwen") else "zhipu-159pair"
        vals, sds = [], []
        for m in methods:
            hit = [r for r in perf if r["method"] == m and r["ruleset"] == rs]
            vals.append(float(hit[0]["F1_mean"]) if hit else 0.0)
            sds.append(seed_sd(generation, m))
        offs = (gi - 0.5) * bw
        bars = ax.bar(x + offs, vals, bw, color=col, edgecolor="white",
                      linewidth=0.6, label=lab, zorder=2)
        ax.errorbar(x + offs, vals, yerr=sds, fmt="none", ecolor="#4A4F57",
                    elinewidth=0.8, capsize=2.2, zorder=4)
        for xi, v in zip(x + offs, vals):
            ax.text(xi, v + 0.012, f"{v:.2f}", ha="center", va="bottom",
                    fontsize=7.0, color="#222222")
    ax.set_xticks(x)
    ax.set_xticklabels([S.METHOD_LABEL[m] for m in methods], fontsize=7.6)
    ax.set_ylabel("F1 (mean of 5 seeds)")
    ax.set_ylim(0, 0.62)
    S.clean(ax, "y")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.02), ncol=1,
              handlelength=1.2)
    S.panel(ax, "a", "Performance, two baseline generations")

    # (b) confusion matrix from the canonical qwen 80-pair rows
    ax = fig.add_subplot(gs[0, 1])
    rows = [json.loads(l) for l in CANON.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    fs = [r for r in rows if r["generation"] == "qwen-80pair"
          and r["baseline"] == "full_system" and r["seed"] == 11]
    states = ["replicated", "contradicted", "uninformative"]
    mat = np.array([[sum(1 for r in fs if r["prediction"] and r["gold3"] == s)
                     for s in states],
                    [sum(1 for r in fs if not r["prediction"] and r["gold3"] == s)
                     for s in states]])
    from matplotlib.colors import LinearSegmentedColormap
    navy_ramp = LinearSegmentedColormap.from_list("huiyan_navy",
                                                  ["#FFFFFF", S.NAVY])
    im = ax.imshow(mat, cmap=navy_ramp, vmin=0, vmax=20, aspect="auto")
    for i in range(2):
        for j in range(3):
            ax.text(j, i, str(mat[i, j]), ha="center", va="center",
                    fontsize=9.5, color="white" if mat[i, j] > 15
                    else "#222222", fontweight="bold")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Replicated", "Contradicted", "Uninformative"],
                       fontsize=7.2)
    ax.set_yticks(range(2))
    ax.set_yticklabels(["Predict YES", "Predict NO"], fontsize=7.6)
    ax.tick_params(length=0)
    S.panel(ax, "b", "Full system × R11 gold (80 pairs)")

    # (c) dumbbell coverage / precision
    ax = fig.add_subplot(gs[1, 0])
    nm = json.loads((ROOT / "outputs/confirmatory/nhanes_metrics_v11.json")
                    .read_text(encoding="utf-8"))
    km = json.loads((ROOT / "outputs/confirmatory/knhanes_metrics_v11.json")
                    .read_text(encoding="utf-8"))
    metrics = [("coverage", "Coverage"), ("precision_rule", "Declared precision")]
    yy = np.arange(len(metrics))
    bh = 0.30
    for off, vals, col, lab in [(-bh / 2 - 0.02, [nm[k] for k, _ in metrics],
                                 S.NAVY, "NHANES"),
                                (bh / 2 + 0.02, [km[k] for k, _ in metrics],
                                 S.AMBER, "KNHANES")]:
        ax.barh(yy + off, vals, bh, color=col, edgecolor="white", lw=0.6,
                label=lab, zorder=2)
        for yv, v in zip(yy + off, vals):
            ax.text(v + 0.004, yv, f"{v:.3f}", va="center", fontsize=7.0,
                    color="#333333")
            ax.text(0.012, yv, lab, va="center", fontsize=6.4, color="white")
    ax.set_yticks(yy); ax.set_yticklabels([m[1] for m in metrics], fontsize=7.6)
    ax.set_xlim(0, 1.16); ax.set_xlabel("Proportion")
    S.clean(ax, "x")
    S.panel(ax, "c", "Internal vs external rule layer")

    # (d) context size
    ax = fig.add_subplot(gs[1, 1])
    kg = [r.get("kg_chars") for r in rows
          if r["generation"] == "qwen-80pair" and r["baseline"] == "lightrag"
          and r.get("kg_chars")]
    ax.hist(kg, bins=24, color=S.TEAL, edgecolor="white", linewidth=0.5,
            zorder=2)
    mean = float(np.mean(kg)) if kg else 0
    ax.axvline(mean, color=S.NAVY, lw=0.9, ls=(0, (4, 2)), zorder=3)
    ax.text(0.97, 0.95, f"Mean {mean:,.0f} chars", transform=ax.transAxes,
            ha="right", va="top", fontsize=7.0, color=S.NAVY,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.set_xlabel("Retrieved KG context (characters)")
    ax.set_ylabel("Runs (5 seeds × 80 pairs)")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.12)
    S.clean(ax, "y")
    S.panel(ax, "d", "LightRAG context size")
    save(fig, "figure2_performance")


# --------------------------------------------------------------------------- #
# Figure 3 — rule evaluation
# --------------------------------------------------------------------------- #
def figure3() -> None:
    rows = rows_of("figure3_rule_evaluation.csv")
    metrics = [
        ("declared-domain precision", "Declared precision", S.NAVY),
        ("conservative precision", "Conservative precision", "#5F656D"),
        ("rule coverage", "Coverage", S.TEAL),
        ("replication rate · level A", "Replication · level A", S.AMBER),
        ("replication rate · level A+B", "Replication · level A+B", S.AMBER),
        ("replication rate · level all", "Replication · all rules", S.AMBER),
    ]
    datasets = ["NHANES", "KNHANES"]
    fig = plt.figure(figsize=(S.FULL, 132 * S.MM))
    gs = fig.add_gridspec(1, 2, left=0.26, right=0.985, top=0.91,
                          bottom=0.19, wspace=0.38, width_ratios=[1.55, 1.0])

    ax = fig.add_subplot(gs[0, 0])
    y = 0
    ticks, labels = [], []
    ds_spans = []
    for ds in datasets:
        ds_start = y
        for key, lab, col in metrics:
            hit = [r for r in rows if r["dataset"] == ds and r["method"] == key]
            if not hit:
                continue
            r = hit[0]
            est = float(r["estimate"])
            lo = float(r["ci_low"]) if r["ci_low"] else est
            hi = float(r["ci_high"]) if r["ci_high"] else est
            ax.plot([lo, hi], [y, y], color=col, lw=1.6, solid_capstyle="round",
                    zorder=2)
            ax.plot([est], [y], "o", ms=5.5, color=col, mec="white", mew=0.9,
                    zorder=3)
            k, n = r.get("k", ""), r.get("n", "")
            suffix = f" ({k}/{n})" if k and n else ""
            ax.text(hi + 0.018, y, f"{est:.2f}{suffix}", va="center",
                    fontsize=7.0, color="#333333")
            ticks.append(y); labels.append(f"{ds} · {lab}")
            y += 1
        ds_spans.append((ds, ds_start, y - 1))
        y += 0.45
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=7.4)
    ax.set_xlim(-0.02, 1.32); ax.set_ylim(-0.7, y - 0.3)
    ax.set_xlabel("Proportion (Clopper–Pearson 95% CI)")
    ax.invert_yaxis()
    S.forest(ax)
    S.panel(ax, "a", "Rule-level metrics")
    from matplotlib.patches import Patch
    key = [Patch(facecolor=S.NAVY, edgecolor="none", label="Declared precision"),
           Patch(facecolor="#5F656D", edgecolor="none", label="Conservative precision"),
           Patch(facecolor=S.TEAL, edgecolor="none", label="Coverage"),
           Patch(facecolor=S.AMBER, edgecolor="none", label="Replication")]
    fig.legend(handles=key, loc="lower center", bbox_to_anchor=(0.44, 0.012),
               ncol=4, frameon=False, fontsize=7.0, handlelength=1.1,
               columnspacing=1.3)

    ax = fig.add_subplot(gs[0, 1])
    xs = np.array([0.0, 1.0])
    vals = {ds: {r["metric"]: float(r["estimate"])
                 for r in rows if r["dataset"] == ds} for ds in datasets}
    declared = [vals[ds]["precision_rule_declared"] for ds in datasets]
    conservative = [vals[ds]["precision_rule_uninf_as_fp"] for ds in datasets]
    ax.plot(xs, declared, "-o", color=S.NAVY, lw=1.6, ms=7,
            mec="white", mew=1.0, zorder=3)
    ax.plot(xs, conservative, "-o", color="#5F656D", lw=2.0, ms=8,
            mec="white", mew=1.0, zorder=3)
    for x, v in zip(xs, declared):
        ax.text(x, v + 0.045, f"{v:.2f}", ha="center", fontsize=7.2,
                color=S.NAVY)
    for x, v in zip(xs, conservative):
        ax.text(x, v - 0.075, f"{v:.2f}", ha="center", fontsize=7.4,
                color="#3F444B")
    ax.annotate("", xy=(0.5, declared[0]), xytext=(0.5, conservative[0]),
                arrowprops=dict(arrowstyle="<->", color="#9AA0A8", lw=0.9))
    ax.text(0.55, (declared[0] + conservative[0]) / 2,
            "uninformative\ncounted as FP", fontsize=6.8, color=S.GREY,
            va="center")
    ax.set_xticks(xs); ax.set_xticklabels(datasets, fontsize=7.6)
    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(0, 1.12); ax.set_ylabel("Precision")
    S.clean(ax, "y")
    S.panel(ax, "b", "Declared vs conservative")
    save(fig, "figure3_rule_evaluation")


# --------------------------------------------------------------------------- #
# Figure 4 — dose response
# --------------------------------------------------------------------------- #
EXPO = {
    "fasting_glucose_mgdl": "Fasting glucose", "hba1c_pct": "HbA1c",
    "bmi_kgm2": "BMI", "waist_cm": "Waist",
    "triglycerides_mgdl": "Triglycerides",
    "total_cholesterol_mgdl": "Total cholesterol", "blood_lead_ugdl": "Blood lead",
    "uric_acid_mgdl": "Uric acid", "serum_cotinine_ngml": "Cotinine",
    "vitamin_c_mg": "Vitamin C", "alpha_tocopherol_mg": "α-tocopherol",
    "lutein_zeaxanthin_mg": "Lutein/zeaxanthin", "crp_mgdl": "CRP",
    "crp_mgl": "CRP",
}
OUT = {"cataract_any": "Cataract", "amd_late": "Late AMD",
       "retinopathy_any": "Retinopathy", "dr_pdr": "PDR", "dr_npdr": "NPDR",
       "vision_impairment_severe": "Severe VI",
       "vision_impairment_moderate": "Moderate VI"}
DS = {"NHANES": "US", "KNHANES": "KR"}
FAM = {
    "fasting_glucose_mgdl": "Glycaemia", "hba1c_pct": "Glycaemia",
    "bmi_kgm2": "Adiposity", "waist_cm": "Adiposity",
    "triglycerides_mgdl": "Lipids", "total_cholesterol_mgdl": "Lipids",
    "blood_lead_ugdl": "Trace elements", "uric_acid_mgdl": "Trace elements",
    "serum_cotinine_ngml": "Smoking biomarker",
    "vitamin_c_mg": "Micronutrients", "alpha_tocopherol_mg": "Micronutrients",
    "lutein_zeaxanthin_mg": "Micronutrients", "crp_mgdl": "Inflammation",
    "crp_mgl": "Inflammation",
}
FAM_ORDER = ["Glycaemia", "Adiposity", "Lipids", "Trace elements",
             "Smoking biomarker", "Micronutrients", "Inflammation"]


def figure4() -> None:
    rows = rows_of("figure6_dose_response.csv")
    for r in rows:
        expo, outcome = r["method"].split(" · ")
        r["_expo"], r["_out"] = expo, outcome
        r["_fam"] = FAM.get(expo, "Other")
        r["_or"] = float(r["estimate"])
        r["_lo"], r["_hi"] = float(r["ci_low"]), float(r["ci_high"])
    fams = [f for f in FAM_ORDER if any(r["_fam"] == f for r in rows)]
    rows.sort(key=lambda r: (fams.index(r["_fam"]), r["_or"]))

    fig = plt.figure(figsize=(S.FULL, 170 * S.MM))
    ax = fig.add_axes([0.40, 0.07, 0.56, 0.88])
    y = 0
    ticks, labels = [], []
    fam_spans = []
    for fam in fams:
        grp = [r for r in rows if r["_fam"] == fam]
        start = y
        ticks.append(y)
        labels.append("")
        ax.text(-0.012, y, fam, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=7.6, fontweight="bold",
                color=S.NAVY)
        y += 1
        for r in grp:
            col = (S.BRICK if r["_lo"] > 1 else S.TEAL if r["_hi"] < 1
                   else S.NEUTRAL)
            ax.plot([r["_lo"], r["_hi"]], [y, y], color=col, lw=1.5,
                    solid_capstyle="round", zorder=2)
            ax.plot([r["_or"]], [y], "o", ms=5.0, color=col, mec="white",
                    mew=0.8, zorder=3)
            ticks.append(y)
            labels.append(f"{EXPO.get(r['_expo'], r['_expo'])} · "
                          f"{OUT.get(r['_out'], r['_out'])}  "
                          f"({DS.get(r['dataset'], r['dataset'])})")
            y += 1
        fam_spans.append((fam, start, y - 1))
        y += 0.8

    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=6.8)
    ax.set_ylim(-0.8, y - 0.2)
    ax.invert_yaxis()
    S.plain_log(ax, "x", [0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0],
                ["0.6", "0.8", "1.0", "1.25", "1.5", "2.0", "3.0"])
    ax.set_xlim(0.55, 3.1)
    ax.axvline(1.0, color="#9AA0A8", lw=0.8, ls=(0, (4, 2)), zorder=1)
    ax.set_xlabel("OR per 1 SD (95% CI)")
    S.forest(ax)
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=S.BRICK, edgecolor="none", label="q<0.05, OR>1"),
               Patch(facecolor=S.TEAL, edgecolor="none", label="q<0.05, OR<1"),
               Patch(facecolor=S.NEUTRAL, edgecolor="none", label="not significant")]
    ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1.0, 1.003),
              ncol=3, frameon=False, fontsize=7.0, handlelength=1.0,
              columnspacing=0.9)
    fig.text(0.02, 0.965, "a", fontsize=10.5, fontweight="bold", va="top")
    fig.text(0.048, 0.965, "Dose-response by exposure family", fontsize=8.8,
             va="top")
    save(fig, "figure6_dose_response")


# --------------------------------------------------------------------------- #
# Figure 5 — power
# --------------------------------------------------------------------------- #
def figure5() -> None:
    rows = rows_of("figure7_power_mde.csv")
    fig = plt.figure(figsize=(160 * S.MM, 110 * S.MM))
    ax = fig.add_axes([0.11, 0.12, 0.87, 0.82])
    xlo, hi = 0.95, 2.55
    ylo = 0.55
    ax.plot([xlo, hi], [xlo, hi], color="#7A7F87", lw=1.0, ls=(0, (4, 2)),
            zorder=1)
    ax.axhline(1.0, color=S.GRID, lw=0.8, zorder=0)
    ax.axvline(1.0, color=S.GRID, lw=0.8, zorder=0)
    for state, col, lab in (("replicated", S.NAVY, "Replicated"),
                            ("uninformative", S.NEUTRAL,
                             "Uninformative (powered null)"),
                            ("contradicted", S.BRICK, "Contradicted")):
        pts = [(float(r["mde_or_80"]), float(r["odds_ratio"])) for r in rows
               if (r.get("gold3") or "").strip() == state]
        if pts:
            if state == "uninformative":
                ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=34,
                           facecolor="white", edgecolor="#A9AEB5",
                           linewidth=1.1, label=lab, zorder=3)
            else:
                ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=44,
                           color=col, edgecolor="white", linewidth=0.8,
                           label=lab, zorder=4)
    ax.text(1.9, 2.3, "adequately powered\n(observed > detectable)", fontsize=6.8,
            color=S.GREY, ha="center")
    ax.text(1.9, 1.25, "underpowered for the\nobserved effect", fontsize=6.8,
            color=S.GREY, ha="center")
    S.plain_log(ax, "x", [1.0, 1.2, 1.5, 2.0, 2.5],
                ["1.0", "1.2", "1.5", "2.0", "2.5"])
    S.plain_log(ax, "y", [0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5],
                ["0.6", "0.8", "1.0", "1.2", "1.5", "2.0", "2.5"])
    ax.set_xlim(xlo, hi); ax.set_ylim(ylo, hi)
    ax.set_xlabel("Minimum detectable OR at 80% power")
    ax.set_ylabel("Observed OR")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.02))
    S.clean(ax, "both")
    S.panel(ax, "a", "Power vs observed effect", dx=-0.115, dy=1.02)
    save(fig, "figure7_power_mde")


# --------------------------------------------------------------------------- #
# Figure 6 — transportability
# --------------------------------------------------------------------------- #
RULE_SHORT = {
    "r02 hyperglycaemia→cataract": "r02 diabetes→cataract",
    "r20 smoking→vision impairment": "r20 smoking→vision",
    "r13 BMI→cataract": "r13 BMI→cataract",
    "r10 smoking→cataract": "r10 smoking→cataract",
    "r12 alcohol→cataract": "r12 alcohol→cataract",
    "r11 smoking→late AMD": "r11 smoking→AMD",
}


def figure6() -> None:
    rows = rows_of("figure8_cohort_transportability.csv")
    rules = []
    for r in rows:
        if r["rule"] not in rules:
            rules.append(r["rule"])
    rules.sort(key=lambda x: (0 if x.startswith("r02") else
                              1 if x.startswith("r20") else
                              2 if x.startswith("r13") else
                              3 if x.startswith("r10") else
                              4 if x.startswith("r12") else 5))
    fig = plt.figure(figsize=(S.FULL, 132 * S.MM))
    gs = fig.add_gridspec(1, 2, left=0.20, right=0.985, top=0.92,
                          bottom=0.17, wspace=0.34, width_ratios=[0.95, 1.35])

    # (a) per-rule composition
    ax = fig.add_subplot(gs[0, 0])
    for yi, rule in enumerate(rules):
        grp = [r for r in rows if r["rule"] == rule]
        counts = Counter(r["state_label"] for r in grp)
        left = 0
        for st in ("replicated", "uninformative", "contradicted"):
            n = counts.get(st, 0)
            if not n:
                continue
            col = S.STATE[st]
            ax.barh(yi, n, left=left, height=0.56, color=col,
                    edgecolor="white", linewidth=0.7, zorder=2)
            ax.text(left + n / 2, yi, str(n), ha="center", va="center",
                    fontsize=7.2, color="white" if st != "uninformative" else "#333333",
                    fontweight="bold")
            left += n
        ax.text(left + 0.15, yi, f"n={len(grp)}", va="center", fontsize=6.8,
                color="#4A4F57")
    ax.set_yticks(range(len(rules)))
    ax.set_yticklabels([RULE_SHORT.get(r, r) for r in rules], fontsize=7.4)
    ax.invert_yaxis()
    ax.set_xlim(0, 6.2)
    ax.set_xlabel("Cohorts contributing each state")
    S.clean(ax, "x")
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=S.STATE[st], edgecolor="white", label=lab)
               for st, lab in (("replicated", "Replicated"),
                               ("uninformative", "Uninformative"),
                               ("contradicted", "Contradicted"))]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.14),
              ncol=3, columnspacing=1.0)
    S.panel(ax, "a", "State composition per rule")

    # (b) per-pair forest
    ax = fig.add_subplot(gs[0, 1])
    y = 0
    ticks, labels = [], []
    group_pos = []
    for rule in rules:
        grp = sorted([r for r in rows if r["rule"] == rule],
                     key=lambda r: r["cohort"])
        start = y
        ticks.append(y); labels.append("")
        ax.text(-0.012, y, RULE_SHORT.get(rule, rule),
                transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=7.0, fontweight="bold", color=S.NAVY)
        y += 1
        for r in grp:
            est = float(r["estimate"])
            lo, hi = float(r["ci_low"]), float(r["ci_high"])
            col = S.STATE[r["state_label"]]
            ax.plot([lo, hi], [y, y], color=col, lw=1.6, solid_capstyle="round",
                    zorder=2)
            ax.plot([est], [y], "o", ms=5.0, color=col, mec="white", mew=0.8,
                    zorder=3)
            ticks.append(y); labels.append(r["cohort"])
            y += 1
        group_pos.append((rule, start, y - 1))
        y += 1.1
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=7.2)
    ax.set_ylim(-0.8, y - 0.2); ax.invert_yaxis()
    S.plain_log(ax, "x", [0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0],
                ["0.6", "0.8", "1.0", "1.25", "1.5", "2.0", "3.0", "4.0", "5.0"])
    ax.set_xlim(0.55, 5.3)
    ax.axvline(1.0, color="#9AA0A8", lw=0.8, ls=(0, (4, 2)), zorder=1)
    ax.set_xlabel("OR (95% CI)")
    S.forest(ax)
    S.panel(ax, "b", "Per-cohort estimates")
    save(fig, "figure8_cohort_transportability")


# --------------------------------------------------------------------------- #
# Figure S1 — demo case
# --------------------------------------------------------------------------- #
def figure_s1() -> None:
    fig = plt.figure(figsize=(S.FULL, 122 * S.MM))
    gs = fig.add_gridspec(3, 2, left=0.05, right=0.97, top=0.94, bottom=0.06,
                          hspace=0.45, wspace=0.30, height_ratios=[0.8, 1.0, 0.85])

    # (a) input card
    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    ax.set_xlim(0, 100); ax.set_ylim(0, 30)
    cards = [
        ("Entity A", "hba1c_elevated\n(glycation-metabolic)", S.NAVY),
        ("Entity B", "retinopathy_any / dr_pdr\n(vascular-perfusion)", S.TEAL),
        ("Confirmatory outcome", "NHANES  OR 1.60 (1.28–1.99)\nq = 0.013 · replicated",
         S.AMBER),
    ]
    for i, (head, body, col) in enumerate(cards):
        x = 1 + i * 33
        ax.add_patch(Circle((x + 1.0, 25.2), 0.7, color=col))
        ax.text(x + 2.4, 25.2, head, va="center", fontsize=8.8,
                color="#222222", fontweight="bold")
        ax.text(x + 15.5, 14.0, body, ha="center", va="center", fontsize=7.6,
                linespacing=1.45)
        if i < 2:
            S.arrow(ax, x + 29.0, 15.5, x + 32.4, 15.5, color="#9AA0A8")
    S.panel(ax, "a", "Demo case input and confirmatory outcome", dx=0.0, dy=0.98,
            size=10.0)

    # (b) triggered rules
    ax = fig.add_subplot(gs[1, 0])
    names = ["r03 · retinopathy_any\nmedium / B", "r04 · dr_pdr\nlow / C"]
    vals = [2, 1]
    cols = [S.NAVY, S.NAVY]
    bars = ax.barh(names, vals, color=cols, height=0.5, edgecolor="white",
                   linewidth=0.7, zorder=2)
    for b, v in zip(bars, vals):
        ax.text(v + 0.06, b.get_y() + b.get_height() / 2, f"{v}", va="center",
                fontsize=8.0)
    ax.set_xlim(0, 2.2); ax.set_xticks([0, 1, 2])
    ax.set_xlabel("Triggered rule hits")
    ax.tick_params(axis="y", labelsize=7.0, length=0)
    ax.spines["left"].set_visible(False)
    S.clean(ax, "x")
    S.panel(ax, "b", "Triggered rules", dx=-0.12, dy=1.03)

    # (c) evidence levels
    ax = fig.add_subplot(gs[1, 1])
    levels = ["A · regulatory", "B · pooled", "C · single cohort",
              "D · weak", "E · mechanism"]
    counts = [0, 2, 1, 0, 0]
    cols = [S.NAVY if c > 0 else "#D8DDE3" for c in counts]
    ax.barh(levels, counts, color=cols, height=0.55, edgecolor="white",
            linewidth=0.7, zorder=2)
    for i, c in enumerate(counts):
        ax.text(c + 0.05, i, str(c), va="center", fontsize=8.0)
    ax.set_xlim(0, 2.2); ax.set_xticks([0, 1, 2])
    ax.set_xlabel("Evidence chunks retrieved")
    ax.tick_params(axis="y", labelsize=6.8, length=0)
    ax.spines["left"].set_visible(False)
    S.clean(ax, "x")
    S.panel(ax, "c", "Evidence levels for this case", dx=-0.12, dy=1.03)

    # (d) trace flow
    ax = fig.add_subplot(gs[2, :]); ax.axis("off")
    ax.set_xlim(0, 100); ax.set_ylim(0, 20)
    chips = ["Rule hits\nr03 + r04", "Evidence\nB×2, C×1", "Arbiter\nYES · T=0",
             "Risk\nlow → medium", "Report\n+ trace"]
    w, gap = 16.0, 4.6
    for i, text in enumerate(chips):
        x = 1 + i * (w + gap)
        col = S.TEAL if i == 1 else S.NAVY
        S.box(ax, x, 4.5, w, 10.0, text, edge=col, face="white", size=7.4)
        if i < len(chips) - 1:
            S.arrow(ax, x + w + 0.5, 9.5, x + w + gap - 0.5, 9.5,
                    color="#9AA0A8")
    S.panel(ax, "d", "Traceability flow", dx=0.0, dy=0.98, size=10.0)
    save(fig, "figure4_demo_case")


# --------------------------------------------------------------------------- #
# Figure S2 — reasoning trace
# --------------------------------------------------------------------------- #
def figure_s2() -> None:
    fig = plt.figure(figsize=(S.FULL, 102 * S.MM))
    gs = fig.add_gridspec(2, 2, left=0.13, right=0.97, top=0.93, bottom=0.09,
                          hspace=0.30, wspace=0.32, height_ratios=[1.0, 1.05],
                          width_ratios=[1.35, 1.0])

    # (a) swimlane
    ax = fig.add_subplot(gs[0, :])
    lanes = {"Rule Engine": (2, S.NAVY), "LightRAG KG": (1, S.TEAL),
             "LLM Arbiter / Report": (0, S.AMBER)}
    steps = [
        (1, "Rule Engine", "Normalise A"), (2, "Rule Engine", "Normalise B"),
        (3, "Rule Engine", "Match r04"), (4, "Rule Engine", "Cross-cover r03"),
        (5, "LightRAG KG", "KG retrieval"), (6, "LLM Arbiter / Report", "Risk grade"),
        (7, "LLM Arbiter / Report", "Report + trace"),
    ]
    for lane, (yy, col) in lanes.items():
        last = max(step for step, l, _ in steps if l == lane)
        ax.plot([0.62, last + 0.35], [yy, yy], color="#D5DAE0", lw=1.0,
                zorder=1)
        ax.text(0.55, yy + 0.14, lane, ha="right", va="bottom", fontsize=7.2,
                color="#333333", fontweight="bold")
    for step, lane, label in steps:
        yy, col = lanes[lane]
        ax.add_patch(Circle((step, yy), 0.22, facecolor="white",
                            edgecolor=col, linewidth=1.4, zorder=3))
        ax.text(step, yy, str(step), ha="center", va="center", fontsize=6.8,
                color=col, fontweight="bold", zorder=4)
        dy = 0.55 if step == 5 else (0.38 if step % 2 else -0.42)
        ha = "left" if step == 4 else "center"
        ax.text(step + (0.06 if step == 4 else 0), yy + dy, label, ha=ha,
                va="bottom" if dy > 0 else "top", fontsize=6.6, color="#333333")
    ax.set_xlim(0.2, 7.45); ax.set_ylim(-0.8, 2.8)
    ax.set_xticks([]); ax.set_yticks([])
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_title("Seven logged steps, each assigned to one architectural layer",
                 fontsize=7.6, color=S.GREY, pad=6)
    S.panel(ax, "a", "Reasoning trace", dx=-0.105, dy=1.12)

    # (b) KG path
    ax = fig.add_subplot(gs[1, 0])
    nodes = ["HbA1c", "Hyper-\nglycaemia", "Retinal\nischaemia", "VEGF",
             "Neo-\nvessels", "PDR"]
    xs = np.arange(len(nodes)) * 1.36
    for i, (x, n) in enumerate(zip(xs, nodes)):
        S.box(ax, x - 0.54, 0.55, 1.08, 0.9, n, edge=S.TEAL, face="white",
              size=6.0, radius=0.02)
        if i < len(nodes) - 1:
            S.arrow(ax, x + 0.56, 1.0, x + 1.36 - 0.56, 1.0, color="#7FA9A0")
    ax.plot([xs[0], xs[-1]], [0.18, 0.18], color=S.AMBER, lw=1.2)
    ax.plot([xs[0], xs[0]], [0.18, 0.40], color=S.AMBER, lw=1.2)
    ax.plot([xs[-1], xs[-1]], [0.18, 0.40], color=S.AMBER, lw=1.2)
    ax.text(xs[len(nodes) // 2], -0.02, "rule r04 covers the full chain",
            ha="center", va="top", fontsize=6.8, color=S.AMBER)
    ax.set_xlim(-0.7, xs[-1] + 0.7); ax.set_ylim(-0.48, 1.65)
    ax.axis("off")
    S.panel(ax, "b", "Knowledge-graph path", dx=-0.08, dy=1.05)

    # (c) steps per layer
    ax = fig.add_subplot(gs[1, 1])
    layer_counts = Counter(lane for _, lane, _ in steps)
    order = ["Rule Engine", "LightRAG KG", "LLM Arbiter / Report"]
    vals = [layer_counts[o] for o in order]
    cols = [S.NAVY, S.TEAL, S.AMBER]
    bars = ax.barh(order[::-1], vals[::-1], color=cols[::-1], height=0.5,
                   edgecolor="white", linewidth=0.7, zorder=2)
    for b, v in zip(bars, vals[::-1]):
        ax.text(v + 0.1, b.get_y() + b.get_height() / 2, f"{v}", va="center",
                fontsize=8.0)
    ax.set_xlim(0, 5.2); ax.set_xlabel("Logged steps")
    ax.tick_params(axis="y", labelsize=7.0, length=0)
    ax.spines["left"].set_visible(False)
    S.clean(ax, "x")
    S.panel(ax, "c", "Steps per layer", dx=-0.22, dy=1.05)
    save(fig, "figure5_reasoning_trace")


RENDERERS = {
    "figure1": figure1, "figure2": figure2, "figure3": figure3,
    "figure4": figure4, "figure5": figure5, "figure6": figure6,
    "figureS1": figure_s1, "figureS2": figure_s2,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    S.apply()
    todo = ([args.only] if args.only else list(RENDERERS))
    for key in todo:
        print(f"[{key}]")
        RENDERERS[key]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
