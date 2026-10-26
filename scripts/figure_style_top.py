"""Shared top-journal figure style for the huiyan manuscript.

One palette, one type scale, one set of axis rules. Imported by
scripts/render_top_figures.py so all eight figures look like one family.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import NullFormatter, ScalarFormatter

MM = 1 / 25.4
FULL = 180 * MM          # double-column width
MID = 140 * MM
SINGLE = 90 * MM

# muted, colour-blind-safe family
NAVY = "#1F3A5F"
BLUE = "#2E6FA7"
TEAL = "#3E8E7E"
AMBER = "#D9A441"
AMBER_DARK = "#A9711B"
BRICK = "#B5543F"
PLUM = "#7B5A8C"
GREY = "#7A7F87"
LIGHT = "#EDF1F6"
PALE = "#F7F9FB"
GRID = "#E1E5EA"
WHITE = "#FFFFFF"

# method colours (Figure 2)
METHOD = {"full_system": NAVY, "lightrag": TEAL, "pure_llm": AMBER,
          "naive_rag": BRICK}
METHOD_LABEL = {"full_system": "Full system", "lightrag": "LightRAG",
                "pure_llm": "Pure LLM", "naive_rag": "Naive RAG"}

# three-state colours (Figures 3, 6, 5, S2)
NEUTRAL = "#8E949C"
STATE = {"replicated": NAVY, "uninformative": NEUTRAL,
         "contradicted": BRICK}


def apply() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "axes.linewidth": 0.8,
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#222222",
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 1.6,
        "ytick.minor.size": 1.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "legend.handlelength": 1.1,
        "legend.handletextpad": 0.5,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


def panel(ax, letter: str, title: str = "", *, dx: float = -0.085,
          dy: float = 1.045, size: float = 10.5) -> None:
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=size,
            fontweight="bold", va="bottom", ha="left", color="#111111")
    if title:
        ax.text(dx + 0.085, dy - 0.005, title, transform=ax.transAxes,
                fontsize=8.8, va="bottom", ha="left", color="#111111")


def clean(ax, grid: str = "y") -> None:
    if grid in ("y", "both"):
        ax.yaxis.grid(True, zorder=0)
    if grid in ("x", "both"):
        ax.xaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)


def box(ax, x, y, w, h, text, *, edge=BLUE, face=WHITE, size=7.6,
        bold=False, radius=0.15, lw=0.9, color="#222222", va="center"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=lw, edgecolor=edge, facecolor=face, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va=va,
            fontsize=size, color=color,
            fontweight="bold" if bold else "normal", zorder=3, linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, *, color=GREY, lw=0.9, rad=0.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=7,
        linewidth=lw, color=color, zorder=1,
        connectionstyle=f"arc3,rad={rad}"))


def plain_log(ax, axis: str, ticks: list[float], labels: list[str] | None = None):
    getattr(ax, f"set_{axis}scale")("log")
    getattr(ax, f"set_{axis}ticks")(ticks)
    if labels:
        getattr(ax, f"set_{axis}ticklabels")(labels)
    fmt = ScalarFormatter()
    fmt.set_scientific(False)
    getattr(ax, f"{axis}axis").set_major_formatter(fmt)
    getattr(ax, f"{axis}axis").set_minor_formatter(NullFormatter())


def forest(ax) -> None:
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
