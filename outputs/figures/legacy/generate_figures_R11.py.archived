#!/usr/bin/env python
"""Regenerate the manuscript figures from the R11 (post-correction) results.

The pre-existing figures were rendered from source_data CSVs built BEFORE the
variable-operationalisation corrections and must not be used (the manuscript
says so explicitly).  This script reads only the R11 result files.

Run with the SYSTEM python (it has matplotlib; the project venv does not):
  C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python310\\python.exe \
      scripts/generate_figures_R11.py
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy.stats import beta as _beta

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "outputs" / "confirmatory"
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "figure.dpi": 300,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.05,
})

C_REP, C_UNI, C_CON = "#2b6cb0", "#c9ccd1", "#c53030"
LAYERS = [("nhanes", "NHANES\n(internal)"), ("knhanes", "KNHANES\n(external)")]


def load(f):
    try:
        return pd.read_csv(CONF / f)
    except Exception:
        return None


def cp_ci(k, n):
    lo = _beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = _beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return lo, hi


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{name}.{ext}", format=ext)
    plt.close(fig)
    print(f"  wrote outputs/figures/{name}.png / .pdf")


# --------------------------------------------------------------------------
def figure2():
    """Three-state distribution, dual precision, and replication by evidence level."""
    fig = plt.figure(figsize=(7.2, 2.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.15], wspace=0.42)

    # (a) three-state distribution
    ax = fig.add_subplot(gs[0, 0])
    states = ["replicated", "contradicted", "uninformative"]
    cols = [C_REP, C_CON, C_UNI]
    ypos = np.arange(len(LAYERS))
    left = np.zeros(len(LAYERS))
    for st, c in zip(states, cols):
        vals = []
        for key, _ in LAYERS:
            d = load(f"{key}_confirmatory.csv")
            if d is None:
                vals.append(0); continue
            t = d[(d.status == "tested") & (d.predicted.fillna(False).astype(bool))]
            vals.append(int((t.gold3 == st).sum()))
        vals = np.array(vals, dtype=float)
        ax.barh(ypos, vals, left=left, color=c, height=0.55,
                edgecolor="white", linewidth=0.6)
        for y, (v, l) in enumerate(zip(vals, left)):
            if v >= 2:
                ax.text(l + v / 2, y, f"{int(v)}", ha="center", va="center",
                        fontsize=7, color="white" if st != "uninformative" else "#333")
        left += vals
    ax.set_yticks(ypos); ax.set_yticklabels([n for _, n in LAYERS])
    ax.set_xlabel("rule-relevant testable pairs")
    ax.set_xlim(0, max(left) * 1.06)
    ax.set_title("a  Three-state outcome", loc="left", fontsize=8, fontweight="bold")
    ax.legend(handles=[Patch(color=c, label=s) for s, c in zip(states, cols)],
              fontsize=6, frameon=False, loc="lower right", ncol=1,
              bbox_to_anchor=(1.02, -0.02))

    # (b) dual precision with CP CIs
    ax = fig.add_subplot(gs[0, 1])
    x = np.arange(len(LAYERS)); w = 0.34
    decl, decl_ci, cons, cons_ci = [], [], [], []
    for key, _ in LAYERS:
        d = load(f"{key}_confirmatory.csv")
        t = d[(d.status == "tested") & (d.predicted.fillna(False).astype(bool))] if d is not None else pd.DataFrame()
        rep = int((t.gold3 == "replicated").sum()) if len(t) else 0
        con = int((t.gold3 == "contradicted").sum()) if len(t) else 0
        n = len(t)
        decl.append(rep / (rep + con) if rep + con else 0.0)
        decl_ci.append(cp_ci(rep, rep + con) if rep + con else (0, 1))
        cons.append(rep / n if n else 0.0)
        cons_ci.append(cp_ci(rep, n) if n else (0, 1))
    for i, (v, ci, c, lab) in enumerate([(decl, decl_ci, "#2f855a", "declared domain\n(rep/(rep+con))"),
                                         (cons, cons_ci, "#b7791f", "conservative\n(rep/all tested)")]):
        lo = [max(0, vv - cci[0]) for vv, cci in zip(v, ci)]
        hi = [max(0, cci[1] - vv) for vv, cci in zip(v, ci)]
        ax.bar(x + (i - 0.5) * w, v, w, color=c, label=lab, yerr=[lo, hi],
               capsize=2.5, error_kw=dict(lw=0.8, ecolor="#444"))
        for xi, vv in zip(x + (i - 0.5) * w, v):
            ax.text(xi, vv + 0.045, f"{vv:.2f}", ha="center", fontsize=6.5)
    ax.set_xticks(x); ax.set_xticklabels([n for _, n in LAYERS], fontsize=7)
    ax.set_ylim(0, 1.30); ax.set_ylabel("rule precision (95% CI)")
    ax.set_title("b  Both precision conventions", loc="left", fontsize=8, fontweight="bold")
    ax.legend(fontsize=5.6, frameon=False, loc="lower center", ncol=2,
              bbox_to_anchor=(0.5, -0.42), columnspacing=0.8, handlelength=1.2)

    # (c) replication by evidence level
    ax = fig.add_subplot(gs[0, 2])
    hs = pd.read_csv(TAB / "headline_sensitivity.csv", encoding="utf-8-sig")
    groups = [("A_level_only", "A"), ("A_and_B_level_only", "A+B"), ("all_rules (current)", "all")]
    x = np.arange(len(groups)); w = 0.36
    for i, (layer, lab) in enumerate(LAYERS):
        ds_name = lab.split("\n")[0]
        rep, tested = [], []
        for rs, _ in groups:
            # NOTE: do not reuse `key` here — it is the LAYER key in LAYERS and
            # shadowing it silently matched no rule_set rows (all bars 0/0).
            r = hs[(hs.rule_set == rs) & (hs.dataset == ds_name)]
            rep.append(int(r.replicated.iloc[0]) if len(r) else 0)
            tested.append(int(r.rule_pairs_tested.iloc[0]) if len(r) else 0)
        ax.bar(x + (i - 0.5) * w, rep, w, color=["#2b6cb0", "#dd6b20"][i],
               label=lab.replace("\n", " "))
        for xi, rr, tt in zip(x + (i - 0.5) * w, rep, tested):
            ax.text(xi, rr + 0.15, f"{rr}/{tt}", ha="center", fontsize=6.5)
    ax.set_xticks(x); ax.set_xticklabels([g[1] for g in groups])
    ax.set_xlabel("evidence level"); ax.set_ylabel("replicated rules")
    ax.set_ylim(0, 9)
    ax.axhline(0, color="#999", lw=0.6)
    ax.set_title("c  Replication by evidence level", loc="left", fontsize=8, fontweight="bold")
    ax.legend(fontsize=6, frameon=False, loc="upper right")

    fig.suptitle("Figure 2 · Rule-level evaluation after the R11 variable corrections",
                 fontsize=9, fontweight="bold", x=0.02, ha="left", y=1.06)
    save(fig, "figure2_rule_evaluation_R11")


# --------------------------------------------------------------------------
def figure3():
    """Minimum detectable OR vs observed OR — makes the nulls interpretable."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), sharex=True, sharey=True)
    for ax, (key, lab) in zip(axes, LAYERS):
        d = load(f"power_analysis_{key}.csv")
        if d is None:
            ax.set_visible(False); continue
        d = d[d.predicted.fillna(False).astype(bool)].copy()
        d = d[d.mde_or_80.notna()]
        col = {"replicated": C_REP, "uninformative": "#f0a020", "contradicted": C_CON}
        for st in ["uninformative", "replicated", "contradicted"]:
            s = d[d.gold3 == st]
            if not len(s):
                continue
            ax.scatter(s.mde_or_80, s["or"].clip(0.2, 20), s=26,
                       facecolor=col.get(st, "#999"),
                       edgecolor="white", linewidth=0.5, label=st, zorder=3)
        for y, style, txt in [(1.0, "-", ""), (1.5, "--", "1.5×"), (2.0, ":", "2.0×")]:
            ax.axhline(y, color="#888", lw=0.7, ls=style, zorder=1)
            ax.axvline(y, color="#888", lw=0.7, ls=style, zorder=1)
        ax.plot([0.5, 20], [0.5, 20], color="#bbb", lw=0.6, zorder=1)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(0.9, 8); ax.set_ylim(0.25, 20)
        from matplotlib.ticker import FixedLocator, NullLocator, FixedFormatter
        ax.xaxis.set_major_locator(FixedLocator([1, 1.5, 2, 3, 5, 8]))
        ax.xaxis.set_major_formatter(FixedFormatter(["1", "1.5", "2", "3", "5", "8"]))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_major_locator(FixedLocator([0.5, 1, 2, 5, 10, 20]))
        ax.yaxis.set_major_formatter(FixedFormatter(["0.5", "1", "2", "5", "10", "20"]))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.set_xlabel("minimum detectable OR (80% power)")
        ax.set_title(lab.replace("\n", " "), loc="left", fontsize=8, fontweight="bold")
    axes[0].set_ylabel("observed OR")
    axes[0].legend(fontsize=6, frameon=False, loc="upper left")
    axes[0].text(0.97, 0.03,
                 "points left of the 1.5× line:\nadequately powered to exclude 1.5×",
                 transform=axes[0].transAxes, fontsize=6, ha="right", va="bottom",
                 color="#444")
    fig.suptitle("Figure 3 · Each null is only interpretable against the effect the design could detect",
                 fontsize=9, fontweight="bold", x=0.02, ha="left", y=1.02)
    save(fig, "figure3_power_mde_R11")


# --------------------------------------------------------------------------
def figure4():
    """Continuous per-SD matrix for rule-relevant pairs (dose-response layer)."""
    d = load("dose_response_matrix.csv")
    if d is None:
        print("  dose_response_matrix.csv missing — figure4 skipped")
        return
    d = d[d.is_rule_pair.fillna(False).astype(bool)]
    frames = []
    for key, lab in (("nhanes", "NHANES"), ("knhanes", "KNHANES")):
        s = d[d.dataset == key]
        if len(s):
            frames.append(s.assign(layer=lab))
    if not frames:
        print("  no rule-relevant continuous pairs — figure4 skipped")
        return
    a = pd.concat(frames, ignore_index=True)
    a["key"] = a.a_flag + "  ·  " + a.b_item

    # NOTE: do NOT share the y-axis here.  The two datasets have different
    # numbers of rule-relevant pairs, and with sharey=True the second panel's
    # tick labels overwrite the first's, placing KNHANES bars next to NHANES
    # pair names — a figure that actively misleads.  Each panel gets its own
    # labels.
    n_max = max(len(a[a.layer == lab]) for lab in ["NHANES", "KNHANES"]) or 1
    fig, axes = plt.subplots(1, 2, figsize=(8.6, max(2.8, 0.30 * n_max + 1.6)),
                             gridspec_kw=dict(wspace=0.55))
    for ax, lab in zip(axes, ["NHANES", "KNHANES"]):
        s = a[a.layer == lab].sort_values("odds_ratio")
        if not len(s):
            ax.set_visible(False); continue
        x = np.arange(len(s))
        colors = ["#c53030" if v < 1 else "#2b6cb0" for v in s.odds_ratio]
        ax.barh(x, s.odds_ratio - 1, left=1, color=colors, height=0.62,
                edgecolor="white", linewidth=0.4)
        ax.errorbar(s.odds_ratio, x, xerr=[s.odds_ratio - s.ci_lo, s.ci_hi - s.odds_ratio],
                    fmt="none", ecolor="#333", elinewidth=0.7, capsize=1.8)
        for xi, (_, r) in zip(x, s.iterrows()):
            star = "*" if r.q_primary < 0.05 else ""
            ax.text(max(r.ci_hi, r.odds_ratio) + 0.035, xi,
                    f"{r.odds_ratio:.2f}{star}", va="center", fontsize=6)
        ax.axvline(1, color="#666", lw=0.8)
        ax.set_yticks(x)
        ax.set_yticklabels([f"{r.a_flag} · {r.b_item}" for _, r in s.iterrows()],
                           fontsize=6)
        ax.set_ylim(-0.8, len(s) - 0.2)
        ax.set_xlabel("OR per 1 SD (95% CI)")
        ax.set_title(f"{lab}  (n={len(s)})", loc="left", fontsize=8, fontweight="bold")
        ax.set_xlim(0.4, max(2.6, float(s.ci_hi.max()) * 1.25))
    fig.suptitle("Figure 4 · Continuous (per-SD) dose-response for rule-relevant pairs "
                 "(* q<0.05; red = opposite to the rule)",
                 fontsize=8.5, fontweight="bold", x=0.02, ha="left", y=1.03)
    save(fig, "figure4_dose_response_R11")


def main() -> int:
    print("Regenerating R11 figures (post-correction numbers only)")
    figure2()
    figure3()
    figure4()
    print("\nNote: the pre-R11 outputs/figures/figure2_performance.* are STALE and "
          "must not be used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
