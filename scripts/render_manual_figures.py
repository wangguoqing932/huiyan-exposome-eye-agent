#!/usr/bin/env python
"""Project-local renderer for the figures the shared renderer cannot draw faithfully.

WHY THIS EXISTS
---------------
`~/.dsh/skills/medical-agent-writer/scripts/build_figures.py` is the authoritative
renderer for the skill family, and for eight of the nine figures in this project it
is exactly right. But its `forest` branch has no hook for two things a forest plot
of RATIOS cannot do without:

  * a logarithmic x axis -- on a linear axis an odds ratio of 0.70 and one of 1.43
    are, wrongly, shown as equally distant from the null; and
  * the null reference line -- the branch calls `make_forest_plot` without `ref`,
    so the helper falls back to its default ref=0.0, which lies outside the
    plotted range and is therefore invisible.

Both gaps were found by INSPECTING THE RENDER, then confirmed by reading the
renderer source -- not assumed from the contract. They affect two figures:

  figure7_power_mde             (MDE-OR vs observed OR, needs the identity line)
  figure8_cohort_transportability (odds ratios, needs the null line at 1)

The shared renderer lives outside this workspace and is read-only under the
current sandbox, and it is shared across projects, so it is not modified here.
This script renders those figures locally instead, following the project's
existing precedent for manual figures. The figure contracts remain the single
source of truth for what each figure claims; this script only draws them.

Output matches the shared renderer's export spec (600 dpi, svg/pdf/tiff/png,
180 mm wide) so nothing downstream has to special-case it.

Run: python scripts/render_manual_figures.py            (both figures)
     python scripts/render_manual_figures.py --only figure8
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "outputs" / "figures" / "source_data"
OUT = ROOT / "outputs" / "figures"

MM = 1 / 25.4
DPI = 600
FORMATS = ("svg", "pdf", "tiff", "png")

# One colour per outcome state. Muted so that the three remain separable in
# greyscale print as well: they differ in LIGHTNESS, not only in hue.
STATE_COLOR = {
    "replicated": "#9D2933",
    "uninformative": "#BFBFBF",
    "contradicted": "#2F5C8F",
}
STATE_ORDER = ["replicated", "uninformative", "contradicted"]


def _read(name: str) -> list[dict]:
    # utf-8-sig, not utf-8: figure7's CSV was written with a BOM, and a
    # csv.DictReader opened as plain utf-8 sees the first column as
    # \ufeffmde_or_80, which raises KeyError on the very first row access. The
    # project has already been bitten by exactly this (the BOM in
    # outputs/tables/dataset_summary.csv broke the 7_1 QC's column lookup).
    # utf-8-sig strips the BOM when present and is identical otherwise.
    with open(SRC / name, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _save(fig, stem: str) -> list[str]:
    written = []
    for ext in FORMATS:
        p = OUT / f"{stem}.{ext}"
        # TIFF is written UNCOMPRESSED by matplotlib, and a 180 mm 600-dpi
        # figure lands at ~57 MB. LZW compression is lossless and is accepted
        # by every journal that asks for TIFF, so use it: the project already
        # carries ~590 MB of uncompressed TIFF across the figure set, which is
        # a submission-portal hazard rather than a quality feature.
        kw = {"pil_kwargs": {"compression": "tiff_lzw"}} if ext == "tiff" else {}
        fig.savefig(p, dpi=DPI, bbox_inches="tight", facecolor="white", **kw)
        written.append(p.name)
    plt.close(fig)
    return written


def render_figure8() -> list[str]:
    rows = _read("figure8_cohort_transportability.csv")
    plt.rcParams.update({"font.family": "Arial", "font.size": 7,
                         "axes.linewidth": 0.8})

    fig = plt.figure(figsize=(180 * MM, 150 * MM))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 4.2], hspace=0.55)

    # ---- panel A: three-state composition per rule (counts of cohorts) -----
    axA = fig.add_subplot(gs[0])
    rules, seen = [], set()
    for r in rows:
        if r["case_id"] not in seen:
            seen.add(r["case_id"])
            rules.append(r["case_id"])
    tally = {ru: {s: 0 for s in STATE_ORDER} for ru in rules}
    for r in rows:
        tally[r["case_id"]][r["layer"]] += 1
    ypos = range(len(rules))
    left = [0.0] * len(rules)
    for state in STATE_ORDER:
        vals = [tally[ru][state] for ru in rules]
        axA.barh(list(ypos), vals, left=left, height=0.62,
                 color=STATE_COLOR[state], edgecolor="white", linewidth=0.6,
                 label=state)
        left = [a + b for a, b in zip(left, vals)]
    axA.set_yticks(list(ypos))
    axA.set_yticklabels(rules, fontsize=6)
    axA.invert_yaxis()
    axA.set_xlabel("number of cohorts", fontsize=6.5)
    axA.tick_params(axis="x", labelsize=6)
    for s in ("top", "right"):
        axA.spines[s].set_visible(False)
    axA.legend(fontsize=5.5, frameon=False, ncol=3,
               loc="lower right", bbox_to_anchor=(1.0, -0.62))
    axA.set_title("a  three-state composition per rule", fontsize=7,
                  loc="left", pad=4)

    # ---- panel B: forest, LOG axis, null line at OR = 1 --------------------
    axB = fig.add_subplot(gs[1])
    labels = [f'{r["state_label"]} · {r["rule"]} · {r["cohort"]}' for r in rows]
    est = [float(r["estimate"]) for r in rows]
    lo = [float(r["ci_low"]) for r in rows]
    hi = [float(r["ci_high"]) for r in rows]
    colors = [STATE_COLOR[r["state_label"]] for r in rows]

    y = list(range(len(labels)))[::-1]
    for yi, e, l, h, c in zip(y, est, lo, hi, colors):
        axB.plot([l, h], [yi, yi], color=c, lw=1.0, solid_capstyle="butt")
        axB.plot(e, yi, marker="o", ms=3.4, color=c, mec="white", mew=0.4)
    axB.set_xscale("log")
    axB.axvline(1.0, color="#555555", ls="--", lw=0.8, alpha=0.9, zorder=0)
    axB.set_yticks(y)
    axB.set_yticklabels(labels, fontsize=5.4)
    axB.set_xlabel("odds ratio (log scale), cluster-robust 95% CI", fontsize=6.5)
    axB.tick_params(axis="x", labelsize=6)
    ticks = [0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
    axB.set_xticks(ticks)
    axB.set_xticklabels([f"{t:g}" for t in ticks])
    axB.set_xlim(0.45, 5.6)
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)
    axB.set_title("b  odds ratio per (rule, cohort) pair", fontsize=7,
                  loc="left", pad=4)
    axB.legend(handles=[Line2D([], [], color="#555555", ls="--", lw=0.8,
                               label="null (OR = 1)")],
               fontsize=5.5, frameon=False, loc="lower right")

    return _save(fig, "figure8_cohort_transportability")


# ---------------------------------------------------------------------------
# figure7 — power / MDE. Also needs the local renderer, for a different reason
# than figure8: this one plots the minimum detectable OR (x) against the
# OBSERVED OR (y), so its entire interpretation rests on the IDENTITY line
# y = x. A point ABOVE the line means the study could have detected its own
# observed effect; a point BELOW means it could not. `make_scatter` accepts only
# a single vertical-or-horizontal `reference_line`, so a diagonal cannot be
# expressed through the contract, and the shared renderer draws neither the
# diagonal nor the null lines on the two axes. Ranges: MDE 1.10-2.27, observed
# OR 0.60-15.14 -- on linear axes everything collapses into one corner.
# ---------------------------------------------------------------------------
LAYER_COLOR = {
    "NHANES · replicated": "#9D2933",
    "KNHANES · replicated": "#C97B84",
    "NHANES · uninformative": "#8C8C8C",
    "KNHANES · uninformative": "#CFCFCF",
}


def render_figure7() -> list[str]:
    rows = _read("figure7_power_mde.csv")
    plt.rcParams.update({"font.family": "Arial", "font.size": 7,
                         "axes.linewidth": 0.8})
    fig, ax = plt.subplots(figsize=(180 * MM, 130 * MM))

    seen, order = set(), []
    for r in rows:
        if r["layer_gold"] not in seen:
            seen.add(r["layer_gold"])
            order.append(r["layer_gold"])

    lo, hi = 0.45, 17.0
    ax.plot([lo, hi], [lo, hi], ls="--", lw=0.9, color="#333333", zorder=1)
    # The label must SIT ON the diagonal. Placing it at a fixed data coordinate
    # (the first attempt used (9, 11)) parks it in empty space because the
    # visible segment of y = x only spans the x limit -- the label then points
    # at nothing. Anchor it just past the line's visible end and rotate it to
    # the line's on-screen slope. On a log-log plot with independent ranges that
    # slope is (H/W) * (log x2 - log x1) / (log y2 - log y1) in data terms, so
    # it is NOT 45 degrees and cannot be hard-coded.
    import math
    _sx = (math.log10(2.6) - math.log10(0.95))
    _sy = (math.log10(17.0) - math.log10(0.45))
    _ang = math.degrees(math.atan2((10.0 / 16.0) * _sx / _sy, 1.0))
    ax.text(2.28, 2.62, "y = x", fontsize=6, color="#333333",
            rotation=_ang, rotation_mode="anchor", ha="left", va="bottom")
    # The contract declares a vertical reference at 1.5, and the powered-null
    # definition in the same contract uses MDE-OR <= 2.0 -- so both lines are
    # part of what the figure is supposed to show. The first local render drew
    # only OR = 1, while the legend text (correctly, per the contract) described
    # 1.0 / 1.5 / 2.0. A legend that describes a line the render omits is a
    # defect in whichever of the two is wrong; here the renderer was wrong, so
    # it is brought up to the contract rather than the legend being weakened.
    ax.axvline(1.0, color="#999999", lw=0.7, ls=":", zorder=0)
    ax.axhline(1.0, color="#999999", lw=0.7, ls=":", zorder=0)
    for _v, _lab in ((1.5, "1.5x"), (2.0, "2.0x")):
        ax.axvline(_v, color="#BBBBBB", lw=0.7, ls="-.", zorder=0)
        ax.text(_v, 0.52, _lab, fontsize=5.2, color="#777777",
                ha="center", va="bottom")

    for layer in order:
        sub = [r for r in rows if r["layer_gold"] == layer]
        ax.scatter([float(r["mde_or_80"]) for r in sub],
                   [float(r["odds_ratio"]) for r in sub],
                   s=22, alpha=0.85, edgecolors="black", linewidths=0.35,
                   color=LAYER_COLOR.get(layer, "#8C8C8C"), label=layer,
                   zorder=3)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.95, 2.6)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("minimum detectable odds ratio (80% power)", fontsize=6.5)
    ax.set_ylabel("observed odds ratio", fontsize=6.5)
    ax.tick_params(labelsize=6)
    # Explicit ticks with plain labels. On a log axis spanning less than one
    # decade, matplotlib labels the MINOR ticks via LogFormatterSciNotation,
    # which renders 1.2 as "1.2 x 10^0". Setting only the major formatter does
    # not suppress that; the minor formatter has to be silenced too.
    _xt = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]
    ax.set_xticks(_xt)
    ax.set_xticklabels([f"{t:g}" for t in _xt])
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=5.6, frameon=False, loc="upper left", ncol=2)
    ax.set_title("power to detect each pair's own observed effect",
                 fontsize=7, loc="left", pad=4)
    return _save(fig, "figure7_power_mde")


# ---------------------------------------------------------------------------
# figure1 — system architecture. Rendered locally because the shared renderer
# cannot draw it at all: its three panels declare NO plot_type, so the renderer
# writes "[panel_x: plot_type=\"\" not auto-rendered]" and returns. The 7_1 QC
# passed that blank page, because its checks (contract parses, source_data
# exists, N panels parsed, N files rendered) are all true of a placeholder.
#
# This draws the three things the contract says panel a/b/c should show, as one
# coherent flowchart rather than three separate panels, because an architecture
# figure is read as a single object: the pipeline on top, the layer each step
# belongs to beneath it, and the outputs it produces at the end.
# ---------------------------------------------------------------------------
PIPE_STEPS = [
    ("User input", "rule"),
    ("Entity\nnormalisation", "rule"),
    ("Rule engine\n(21 YAML rules)", "rule"),
    ("Risk-guided\nLightRAG retrieval", "kg"),
    ("Evidence\ncompression", "kg"),
    ("LLM arbiter\n(risk grading)", "llm"),
    ("Structured report\n+ trace", "llm"),
]
LAYER_COLOR = {"rule": "#4C6EA8", "kg": "#5AA88C", "llm": "#B0713F"}
OUTPUTS = ["Clinician card", "Patient handout", "Research table", "Policy brief"]


def render_figure1() -> list[str]:
    plt.rcParams.update({"font.family": "Arial", "font.size": 7,
                         "axes.linewidth": 0.8})
    fig = plt.figure(figsize=(180 * MM, 92 * MM))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 52)
    ax.axis("off")

    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    # ---- (a) the pipeline --------------------------------------------------
    n = len(PIPE_STEPS)
    bw, gap = 12.0, 2.3
    x0 = 1.0
    ytop, bh = 30.0, 13.0
    for i, (label, layer) in enumerate(PIPE_STEPS):
        x = x0 + i * (bw + gap)
        ax.add_patch(FancyBboxPatch(
            (x, ytop), bw, bh, boxstyle="round,pad=0.35,rounding_size=0.8",
            linewidth=0.7, edgecolor=LAYER_COLOR[layer], facecolor="white"))
        ax.text(x + bw / 2, ytop + bh / 2, label, ha="center", va="center",
                fontsize=5.6, linespacing=1.25)
        if i < n - 1:
            ax.add_patch(FancyArrowPatch(
                (x + bw, ytop + bh / 2), (x + bw + gap, ytop + bh / 2),
                arrowstyle="-|>", mutation_scale=5, linewidth=0.7,
                color="#555555"))
    ax.text(x0, ytop + bh + 2.6,
            "a  End-to-end pipeline: input \u2192 normalisation \u2192 rules \u2192 "
            "retrieval \u2192 compression \u2192 arbiter \u2192 report",
            fontsize=6.2, ha="left", va="bottom")

    # ---- (b) the three layers the steps belong to --------------------------
    ybar = 20.0
    for layer, name in (("rule", "Rule layer (deterministic YAML rules)"),
                        ("kg", "KG layer (LightRAG graph)"),
                        ("llm", "Arbiter layer (LLM)")):
        idx = [i for i, (_, L) in enumerate(PIPE_STEPS) if L == layer]
        xa = x0 + idx[0] * (bw + gap)
        xb = x0 + idx[-1] * (bw + gap) + bw
        ax.add_patch(FancyBboxPatch(
            (xa, ybar), xb - xa, 3.4,
            boxstyle="round,pad=0.2,rounding_size=0.6", linewidth=0.6,
            edgecolor=LAYER_COLOR[layer], facecolor=LAYER_COLOR[layer],
            alpha=0.16))
        ax.text(xa + (xb - xa) / 2, ybar + 1.7, name, ha="center", va="center",
                fontsize=5.4)
        # traceability: a dashed drop from the layer bar to the steps
        for i in idx:
            xc = x0 + i * (bw + gap) + bw / 2
            ax.add_patch(FancyArrowPatch(
                (xc, ytop), (xc, ybar + 3.4), arrowstyle="-",
                linestyle=(0, (1, 1.6)), linewidth=0.5, color="#999999"))
    ax.text(x0, ybar + 4.6, "b  Three-layer traceability: every step belongs to a "
                            "named layer, so an output can be followed back",
            fontsize=6.2, ha="left", va="bottom")

    # ---- (c) the four output views ----------------------------------------
    yc = 6.0
    for i, lab in enumerate(OUTPUTS):
        x = 76.0
        yy = yc + i * 4.0
        ax.add_patch(FancyBboxPatch(
            (x, yy), 22.0, 3.0, boxstyle="round,pad=0.2,rounding_size=0.5",
            linewidth=0.6, edgecolor="#888888", facecolor="#F2F2F2"))
        ax.text(x + 11.0, yy + 1.5, lab, ha="center", va="center", fontsize=5.4)
    ax.text(76.0, yc + 4 * 4.0 + 0.6,
            "c  Four output views,\none inference pass",
            fontsize=6.2, ha="left", va="bottom")
    ax.add_patch(FancyArrowPatch(
        (x0 + (n - 1) * (bw + gap) + bw, ytop + bh / 2), (75.6, 16.0),
        arrowstyle="-|>", mutation_scale=5, linewidth=0.7, color="#555555",
        connectionstyle="arc3,rad=-0.15"))

    return _save(fig, "figure1_architecture")


RENDERERS = {"figure1": render_figure1, "figure7": render_figure7,
             "figure8": render_figure8}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="comma-separated figure keys, e.g. figure8")
    args = ap.parse_args()
    keys = (list(RENDERERS) if not args.only
            else [k.strip() for k in args.only.split(",")])
    for k in keys:
        fn = RENDERERS.get(k)
        if fn is None:
            print(f"  {k}: no local renderer")
            continue
        names = fn()
        print(f"  {k}: emitted {len(names)} file(s) ({', '.join(FORMATS)})")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
