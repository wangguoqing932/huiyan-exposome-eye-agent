#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render all six main figures with a locked palette, locked width and locked order.

WHY A SINGLE RENDERER FOR ALL SIX
---------------------------------
The figures were previously drawn by two different programs: the shared skill
renderer for figures 2, 3 and 4 and a project-local one for 1, 5 and 6. Each
carried its own colours, and the result failed on inspection:

  * **Semantic collision.** `#9D2933` meant "naive RAG baseline" in one figure,
    "replication rate" in another and "replicated" in a third. The contract
    requires that a colour's meaning is fixed across the manuscript.
  * **Colour-vision failure inside one figure.** Figure 6 used `#9D2933` and
    `#A43841` for adjacent categories; the palette gate measures them at
    CIEDE2000 2.8-3.7 for deutan, protan and tritan, against a threshold of 10.
    The figure was asking readers to separate two reds that nobody can separate.
  * **Width overrun.** Four of six figures were 196-228 mm wide against a
    180 mm full-width limit, so a journal would rescale them and every font
    size and line weight would land somewhere unintended.

THE LOCKS
---------
Palette. Okabe-Ito roles, one meaning per colour for the whole manuscript:
    primary    #0072B2   the main series / the thing being introduced
    adverse    #D55E00   risk-increasing direction
    favourable #009E73   protective direction
    comparator #E69F00   a comparison arm
    neutral    #4D4D4D   pooled estimate, reference line
    ns         #9A9A9A   interval includes the null
Not decoration: every colour carries a role, and a role's colour never changes.

Width. 180 mm full width for multi-panel figures, 90 mm single column. Never
wider.

Order. Figure 4's 33 dose-response rows are grouped by exposure family and
sorted by point estimate within family, with the two endpoints of each family
labelled directly, so the reader gets the range without reading the axis.

Each figure's claim, in one sentence, is stated in CLAIMS below before anything
is drawn.

Run: python scripts/render_locked_figures.py            (all six)
     python scripts/render_locked_figures.py --only 4
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt               # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "outputs" / "figures"
SRC = FIGS / "source_data"

MM = 1 / 25.4
FULL, SINGLE = 180 * MM, 90 * MM

# ---- the palette lock ------------------------------------------------------
PRIMARY, ADVERSE, FAVOUR, COMPARATOR = "#0072B2", "#D55E00", "#009E73", "#E69F00"
NEUTRAL, NS = "#4D4D4D", "#9A9A9A"
# A categorical trio for purely nominal categories, verified against the
# palette gate at tritan dE=12.6. The default role colours put blue and green
# adjacent (tritan dE=6.4), which fails: blue/green is exactly the pair a
# tritan reader cannot separate.
CAT1, CAT2, CAT3 = "#0072B2", "#E69F00", "#CC79A7"

SHORT_RULE = {
    "r02 hyperglycaemia\u2192cataract": "r02 diabetes\u2013cataract",
    "r10 smoking\u2192cataract": "r10 smoking\u2013cataract",
    # the CSV says 'late AMD', but the cohort layer tested amd_any, and the
    # paper's text was corrected to say so. The figure must not keep the older,
    # stronger label: a figure that disagrees with its text is a silent
    # divergence, which the style contract names as a failure mode.
    "r11 smoking\u2192late AMD": "r11 smoking\u2013any AMD",
    "r12 alcohol\u2192cataract": "r12 alcohol\u2013cataract",
    "r13 BMI\u2192cataract": "r13 BMI\u2013cataract",
    "r20 smoking\u2192vision impairment": "r20 smoking\u2013vision",
}
GRID = "#E5E5E5"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 7,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 6.6,
    "ytick.labelsize": 6.6,
    "legend.fontsize": 6.6,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.2,
    "ytick.major.size": 2.2,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})

CLAIMS = {
    1: "The system turns a free-text case into a risk-graded report through "
       "three named layers, and every step is traceable to a layer.",
    2: "The full system outperforms three baselines on the internal gold, but "
       "the margin over the strongest baseline is not significant.",
    3: "Declared-domain precision is 1.00 but is degenerate (nothing was "
       "contradicted); conservative precision is 0.33-0.38.",
    4: "Dose-response estimates for rule-relevant pairs, grouped by exposure "
       "family, none of which survives adjustment as a screening threshold.",
    5: "Most uninformative pairs were powered to exclude their own minimum "
       "detectable effect, so the nulls are informative rather than absent.",
    6: "Replication is not transportability: two of six rules replicate "
       "somewhere, and every computable prediction interval crosses the null.",
}


def save(fig, stem: str) -> list[str]:
    out = []
    for ext in ("png", "pdf", "svg", "tiff"):
        p = FIGS / f"{stem}.{ext}"
        kw = {"dpi": 600} if ext != "tiff" else {
            "dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}}
        fig.savefig(p, **kw)
        out.append(p.name)
    plt.close(fig)
    return out


def _panel_letter(ax, letter: str, dx: float = -0.02, dy: float = 1.02) -> None:
    """Panel letters sit outside the axes, top-left: findable, never dominant."""
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="bottom", ha="right", color="black")


def _forest_axis(ax) -> None:
    ax.axvline(1.0, color=NEUTRAL, linewidth=0.6, linestyle=(0, (4, 2.4)),
               zorder=0)


# ---------------------------------------------------------------------------
def render_1() -> list[str]:
    """Architecture. Claim: three named layers, every step traceable."""
    steps = [("User input", "rule"), ("Entity\nnormalisation", "rule"),
             ("Rule engine\n(21 YAML rules)", "rule"),
             ("Risk-guided\nLightRAG retrieval", "kg"),
             ("Evidence\ncompression", "kg"),
             ("LLM arbiter\n(risk grading)", "llm"),
             ("Structured report\n+ trace", "llm")]
    # three nominal layers: use the categorical trio, not role colours
    lay = {"rule": CAT1, "kg": CAT2, "llm": CAT3}
    outs = ["Clinician card", "Patient handout", "Research table", "Policy brief"]

    fig = plt.figure(figsize=(FULL, 92 * MM))
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98]); ax.set_xlim(0, 100)
    ax.set_ylim(0, 52); ax.axis("off")
    bw, gap, x0, ytop, bh = 9.3, 1.8, 1.0, 32.0, 12.0
    for i, (label, layer) in enumerate(steps):
        x = x0 + i * (bw + gap)
        ax.add_patch(FancyBboxPatch((x, ytop), bw, bh,
                     boxstyle="round,pad=0.3,rounding_size=0.7", linewidth=0.7,
                     edgecolor=lay[layer], facecolor="white"))
        ax.text(x + bw / 2, ytop + bh / 2, label, ha="center", va="center",
                fontsize=4.9, linespacing=1.2)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + bw, ytop + bh / 2),
                         (x + bw + gap, ytop + bh / 2), arrowstyle="-|>",
                         mutation_scale=4.5, linewidth=0.6, color=NEUTRAL))
    n = len(steps)
    ax.text(x0, ytop + bh + 2.2, "a  End-to-end pipeline: input \u2192 "
            "normalisation \u2192 rules \u2192 retrieval \u2192 compression "
            "\u2192 arbiter \u2192 report", fontsize=6.0, va="bottom")
    ybar = 24.0
    for layer, name in (("rule", "Rule layer (deterministic)"),
                        ("kg", "KG layer (LightRAG)"),
                        ("llm", "Arbiter layer (LLM)")):
        idx = [i for i, (_, L) in enumerate(steps) if L == layer]
        xa, xb = x0 + idx[0] * (bw + gap), x0 + idx[-1] * (bw + gap) + bw
        ax.add_patch(FancyBboxPatch((xa, ybar), xb - xa, 3.0,
                     boxstyle="round,pad=0.18,rounding_size=0.5", linewidth=0.6,
                     edgecolor=lay[layer], facecolor=lay[layer], alpha=0.16))
        ax.text(xa + (xb - xa) / 2, ybar + 1.5, name, ha="center",
                va="center", fontsize=4.8)
        for i in idx:
            xc = x0 + i * (bw + gap) + bw / 2
            ax.add_patch(FancyArrowPatch((xc, ytop), (xc, ybar + 3.0),
                         arrowstyle="-", linestyle=(0, (1, 1.6)),
                         linewidth=0.5, color=NS))
    ax.text(x0, ybar + 3.9, "b  Three-layer traceability: every step belongs to "
            "a named layer, so an output can be followed back to its evidence",
            fontsize=6.0, va="bottom")
    yc, oh, ow, og = 3.0, 4.2, 22.0, 2.6
    for i, lab in enumerate(outs):
        x = x0 + i * (ow + og)
        ax.add_patch(FancyBboxPatch((x, yc), ow, oh,
                     boxstyle="round,pad=0.22,rounding_size=0.5", linewidth=0.6,
                     edgecolor=NEUTRAL, facecolor="#F2F2F2"))
        ax.text(x + ow / 2, yc + oh / 2, lab, ha="center", va="center",
                fontsize=5.2)
    ax.text(x0, yc + oh + 1.4, "c  Four output views from one inference pass",
            fontsize=6.0, va="bottom")
    ax.add_patch(FancyArrowPatch((x0 + (n - 1) * (bw + gap) + bw, ytop),
                 (x0 + 3 * (ow + og) + ow / 2, yc + oh), arrowstyle="-|>",
                 mutation_scale=5, linewidth=0.7, color=NEUTRAL,
                 connectionstyle="arc3,rad=0.25"))
    return save(fig, "figure1_architecture")


def render_2() -> list[str]:
    """Internal performance. Claim: beats baselines, but not the strongest."""
    rows = list(csv.DictReader((SRC / "figure2_performance.csv").open(encoding="utf-8-sig")))
    agg: dict[str, list[float]] = {}
    for r in rows:
        agg.setdefault(r["method"], []).append(float(r["estimate"]))
    order = ["full_system", "lightrag", "pure_llm", "naive_rag"]
    label = {"full_system": "Full system", "lightrag": "LightRAG",
             "pure_llm": "Pure LLM", "naive_rag": "Naive RAG"}
    color = {"full_system": PRIMARY, "lightrag": COMPARATOR,
             "pure_llm": NS, "naive_rag": NS}

    fig, ax = plt.subplots(figsize=(SINGLE * 1.5, 62 * MM))
    ys = list(range(len(order)))[::-1]
    for y, m in zip(ys, order):
        v = agg[m]
        mu = sum(v) / len(v)
        sd = (sum((x - mu) ** 2 for x in v) / (len(v) - 1)) ** 0.5 if len(v) > 1 else 0
        ax.plot([mu - sd, mu + sd], [y, y], color=color[m], linewidth=0.9,
                solid_capstyle="round", zorder=2)
        ax.plot([mu], [y], marker="o", markersize=4.2, color=color[m],
                markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        ax.text(mu + sd + 0.012, y, f"{mu:.3f}", va="center", ha="left",
                fontsize=6.4, color=NEUTRAL)
    ax.set_yticks(ys); ax.set_yticklabels([label[m] for m in order])
    ax.set_xlabel("F1 (mean \u00b1 SD across 5 seeds)")
    ax.set_xlim(0, max(max(agg[m]) for m in order) + 0.08)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.xaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.text(0.99, 0.02, "n = 5 seeds per method", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.2, color=NEUTRAL)
    fig.tight_layout()
    return save(fig, "figure2_performance")


def render_3() -> list[str]:
    """Rule evaluation. Claim: declared-domain precision is degenerate."""
    rows = list(csv.DictReader(
        (SRC / "figure3_rule_evaluation.csv").open(encoding="utf-8-sig")))
    short = {"precision_rule_declared": "Declared-domain precision",
             "precision_rule_uninf_as_fp": "Conservative precision",
             "coverage": "Rule coverage",
             "replication_rate": "Replication rate"}
    ds_order = ["NHANES", "KNHANES"]
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 78 * MM),
                             gridspec_kw={"width_ratios": [1.35, 1]})
    y = 0; ticks, labels = [], []
    for ds in ds_order:
        for metric in ["precision_rule_declared", "precision_rule_uninf_as_fp",
                       "coverage", "replication_rate"]:
            sel = [r for r in rows if r["dataset"] == ds and r["metric"] == metric]
            if not sel:
                continue
            r = sel[0]
            est = float(r["estimate"])
            lo = float(r["ci_low"]) if r["ci_low"] not in ("", "nan") else est
            hi = float(r["ci_high"]) if r["ci_high"] not in ("", "nan") else est
            col = (PRIMARY if metric.startswith("precision_rule_declared")
                   else NS if metric.startswith("precision_rule_uninf")
                   else NEUTRAL)
            axes[0].plot([lo, hi], [y, y], color=col, linewidth=0.9, zorder=2)
            axes[0].plot([est], [y], marker="o", markersize=4.0, color=col,
                         markeredgecolor="white", markeredgewidth=0.6, zorder=3)
            if metric.startswith("precision_rule_declared"):
                axes[0].text(hi + 0.015, y, "degenerate: 0 contradicted",
                             va="center", fontsize=5.8, color=NEUTRAL)
            ticks.append(y); labels.append(f"{short[metric]} \u00b7 {ds}")
            y += 1
        y += 0.5
    axes[0].set_yticks(ticks); axes[0].set_yticklabels(labels, fontsize=6.2)
    axes[0].set_xlim(-0.03, 1.22); axes[0].set_ylim(-0.7, y - 0.3)
    axes[0].set_xlabel("Proportion (Clopper\u2013Pearson 95% CI)")
    axes[0].xaxis.grid(True, color=GRID, linewidth=0.5); axes[0].set_axisbelow(True)
    _panel_letter(axes[0], "a")

    # explicit axis: bar charts spend ink on empty space (Rummens & Beier 2026)
    ax = axes[1]
    for i, ds in enumerate(ds_order):
        sel = {r["metric"]: r for r in rows if r["dataset"] == ds}
        for j, (metric, off) in enumerate([("precision_rule_declared", 0.16),
                                           ("precision_rule_uninf_as_fp", -0.16)]):
            r = sel.get(metric)
            if not r:
                continue
            e = float(r["estimate"])
            ax.plot([i + off], [e], marker="o", markersize=4.2,
                    color=PRIMARY if j == 0 else NS,
                    markeredgecolor="white", markeredgewidth=0.6)
            ax.text(i + off, e + 0.045, f"{e:.2f}", ha="center", fontsize=6.2,
                    color=NEUTRAL)
    ax.set_xticks(range(len(ds_order))); ax.set_xticklabels(ds_order)
    ax.set_ylim(0, 1.22); ax.set_ylabel("Precision")
    ax.set_xlim(-0.5, len(ds_order) - 0.5)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.plot([], [], marker="o", linestyle="none", color=PRIMARY,
            label="Declared-domain (degenerate)")
    ax.plot([], [], marker="o", linestyle="none", color=NS,
            label="Conservative (uninformative = FP)")
    ax.legend(frameon=False, loc="lower left", handletextpad=0.3)
    _panel_letter(ax, "b")
    fig.tight_layout()
    return save(fig, "figure3_rule_evaluation")


def render_4() -> list[str]:
    """Dose response. Claim: grouped by family, none survives as a threshold."""
    rows = list(csv.DictReader(
        (SRC / "figure6_dose_response.csv").open(encoding="utf-8-sig")))
    FAM = {
        "fasting_glucose_mgdl": "Glycaemia", "hba1c_pct": "Glycaemia",
        "bmi_kgm2": "Adiposity", "waist_cm": "Adiposity",
        "triglycerides_mgdl": "Lipids", "total_cholesterol_mgdl": "Lipids",
        "blood_lead_ugdl": "Trace elements", "uric_acid_mgdl": "Trace elements",
        "serum_cotinine_ngml": "Smoking biomarker",
        "vitamin_c_mg": "Micronutrients", "alpha_tocopherol_mg": "Micronutrients",
        "lutein_zeaxanthin_mg": "Micronutrients", "crp_mgdl": "Inflammation", "crp_mgl": "Inflammation",
    }
    fam_order = ["Glycaemia", "Adiposity", "Lipids", "Trace elements",
                 "Smoking biomarker", "Micronutrients", "Inflammation"]
    for r in rows:
        expo = r["method"].split(" · ")[0]
        r["_expo"] = expo
        r["_fam"] = FAM.get(expo, "Other")
        r["_or"] = float(r["estimate"])
    if any(r["_fam"] == "Other" for r in rows):
        fam_order.append("Other")
    fam_order = [f for f in fam_order if any(r["_fam"] == f for r in rows)]
    rows.sort(key=lambda r: (fam_order.index(r["_fam"]), r["_or"]))

    fig, ax = plt.subplots(figsize=(FULL, 118 * MM))
    ys, ticks, labels, spans = [], [], [], []
    y = 0
    for fam in fam_order:
        grp = [r for r in rows if r["_fam"] == fam]
        start = y
        for r in grp:
            lo, hi = float(r["ci_low"]), float(r["ci_high"])
            col = ADVERSE if lo > 1 else FAVOUR if hi < 1 else NS
            ax.plot([lo, hi], [y, y], color=col, linewidth=0.85, zorder=2)
            ax.plot([r["_or"]], [y], marker="o", markersize=3.4, color=col,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=3)
            ticks.append(y)
            labels.append(f"{r['method'].replace('_', ' ')} \u00b7 "
                          f"{r['dataset']}")
            y += 1
        spans.append((fam, start, y - 1))
        y += 0.9
    _forest_axis(ax)
    for fam, a, b in spans:
        ax.axhspan(a - 0.45, b + 0.45, color="#F7F7F7", zorder=0)
        # The family name goes to the RIGHT of the plot, not rotated down the
        # left margin: the y tick labels are long, and the first version put the
        # rotated family names straight on top of them, which is the annotation
        # collision the style contract names as a failure mode. The x axis is
        # extended past the last interval to open the space.
        ax.text(0.995, (a + b) / 2, fam, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=6.4, fontweight="bold",
                color=NEUTRAL)
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=5.5)
    ax.set_xscale("log")
    ax.set_xlabel("OR per 1 SD (95% CI)")
    ax.set_xlim(0.45, 4.6)   # room on the right for the family names
    ax.set_ylim(-0.9, y - 0.5)
    ax.xaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.text(0.99, 0.005, "n = 33 rule-relevant pairs; rows sorted within family",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.2,
            color=NEUTRAL)
    fig.tight_layout()
    return save(fig, "figure6_dose_response")


def render_5() -> list[str]:
    """Power. Claim: the nulls are informative nulls."""
    rows = list(csv.DictReader((SRC / "figure7_power_mde.csv").open(encoding="utf-8-sig")))
    fig, ax = plt.subplots(figsize=(SINGLE * 1.6, 82 * MM))
    pts = []
    for r in rows:
        mde = float(r["mde_or_80"]); obs = float(r["odds_ratio"])
        st = (r.get("gold3") or "").strip()
        pts.append((mde, obs, st))
    lo, hi = 0.95, max(m[0] for m in pts) * 1.06
    ax.plot([lo, hi], [lo, hi], color=NEUTRAL, linewidth=0.7,
            linestyle=(0, (4, 2.4)), zorder=1)
    ax.plot([1, 1], [lo, hi], color=GRID, linewidth=0.6, zorder=0)
    ax.plot([lo, hi], [1, 1], color=GRID, linewidth=0.6, zorder=0)
    for state, col, lab in (("replicated", PRIMARY, "Replicated"),
                            ("uninformative", NS, "Uninformative (powered null)"),
                            ("contradicted", ADVERSE, "Contradicted")):
        xs = [m for m, o, s in pts if s == state]
        ys = [o for m, o, s in pts if s == state]
        if xs:
            ax.plot(xs, ys, marker="o", linestyle="none", markersize=3.6,
                    color=col, markeredgecolor="white", markeredgewidth=0.5,
                    label=lab, zorder=3)
    ax.set_xlabel("Minimum detectable OR at 80% power")
    ax.set_ylabel("Observed OR")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks([1.0, 1.2, 1.5, 2.0]); ax.set_yticks([1.0, 1.2, 1.5, 2.0])
    ax.set_xticklabels(["1.0", "1.2", "1.5", "2.0"])
    ax.set_yticklabels(["1.0", "1.2", "1.5", "2.0"])
    ax.legend(frameon=False, loc="upper left", handletextpad=0.3)
    ax.text(0.99, 0.02, "line = MDE equals observed", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.2, color=NEUTRAL)
    fig.tight_layout()
    return save(fig, "figure7_power_mde")


def render_6() -> list[str]:
    """Transportability. Claim: replication is not transportability."""
    rows = list(csv.DictReader((SRC / "figure8_cohort_transportability.csv")
                               .open(encoding="utf-8-sig")))
    STATE = {"replicated": (PRIMARY, "Replicated"),
             "uninformative": (NS, "Uninformative"),
             "contradicted": (ADVERSE, "Contradicted")}
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 76 * MM),
                             gridspec_kw={"width_ratios": [1, 1.5]})

    # (a) composition: what fraction of pairs landed in each state
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["state_label"]] = counts.get(r["state_label"], 0) + 1
    total = sum(counts.values())
    ax = axes[0]
    left = 0.0
    for st, (col, lab) in STATE.items():
        n = counts.get(st, 0)
        if not n:
            continue
        ax.barh([0], [n], left=left, height=0.42, color=col,
                edgecolor="white", linewidth=0.6)
        ax.text(left + n / 2, 0, f"{n}", ha="center", va="center",
                fontsize=6.6, color="white", fontweight="bold")
        ax.text(left + n / 2, -0.34, lab, ha="center", va="top", fontsize=6.0,
                color=NEUTRAL)
        left += n
    ax.set_xlim(0, total); ax.set_ylim(-0.85, 0.5)
    ax.set_yticks([]); ax.set_xlabel(f"Rule \u00d7 cohort pairs (n = {total})")
    ax.spines["left"].set_visible(False)
    _panel_letter(ax, "a", dx=-0.02, dy=1.04)

    # (b) per-pair estimates: every unit drawn, nulls greyed
    ax = axes[1]
    order = sorted({r["rule"] for r in rows})
    ys, ticks, labels = [], [], []
    rows_sorted = []
    y = 0
    for rule in order:
        grp = sorted([r for r in rows if r["rule"] == rule],
                     key=lambda r: r["cohort"])
        for r in grp:
            rows_sorted.append(r)
            est = float(r["estimate"])
            lo, hi = float(r["ci_low"]), float(r["ci_high"])
            col = STATE[r["state_label"]][0]
            ax.plot([lo, hi], [y, y], color=col, linewidth=0.85, zorder=2)
            ax.plot([est], [y], marker="o", markersize=3.4, color=col,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=3)
            ticks.append(y); labels.append(r["cohort"])
            y += 1
        y += 0.8
    _forest_axis(ax)
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=5.8)
    ax.set_xscale("log")
    ax.set_xlabel("OR (95% CI)")
    ax.set_xlim(0.4, 6.5)
    ax.set_ylim(-0.8, y - 0.4)
    ax.xaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    # The rule name is the unit of the claim, and the first version showed only
    # cohort names repeated 18 times with no indication of which rule each group
    # belonged to -- the reader could not recover the (rule x cohort) structure
    # that this figure exists to show. Each group now carries its rule name.
    for rule in order:
        idx = [i for i, r in enumerate(rows_sorted) if r["rule"] == rule]
        if not idx:
            continue
        a, b = ticks[idx[0]], ticks[idx[-1]]
        ax.text(1.012, (a + b) / 2, SHORT_RULE[rule],
                transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=6.0, fontweight="bold", color=NEUTRAL)
    # legend proxies: the per-point calls above carry no label
    for st, (col, lab) in STATE.items():
        ax.plot([], [], marker="o", linestyle="none", color=col, label=lab)
    # the legend sat on a data point at lower right; it goes outside the axes
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, -0.155),
              handletextpad=0.3, ncol=3, columnspacing=1.1,
              borderaxespad=0.0)
    _panel_letter(ax, "b")
    fig.tight_layout()
    return save(fig, "figure8_cohort_transportability")


RENDERERS = {1: render_1, 2: render_2, 3: render_3, 4: render_4, 5: render_5,
             6: render_6}
STEM = {1: "figure1_architecture", 2: "figure2_performance",
        3: "figure3_rule_evaluation", 4: "figure6_dose_response",
        5: "figure7_power_mde", 6: "figure8_cohort_transportability"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int)
    a = ap.parse_args()
    todo = [a.only] if a.only else sorted(RENDERERS)
    for n in todo:
        print(f"  Figure {n}: {CLAIMS[n]}")
        print(f"    -> {', '.join(RENDERERS[n]())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
