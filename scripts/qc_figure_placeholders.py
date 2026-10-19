#!/usr/bin/env python
"""Placeholder / blank-figure scan — the hole the 7_1 QC left open.

WHY
---
`verify_figures_tables.py` returned PASS for figure1, figure4 and figure5, all
three of which are blank or mostly blank pages carrying only the renderer's
placeholder text ("[panel_x: plot_type=\"\" not auto-rendered]", "[... missing
... col]"). Its four checks are: the contract parses, the source_data CSV
exists, N panels were parsed, N files were rendered. All four are TRUE for a
blank page, because the renderer writes the placeholder and returns normally.
The check verifies that the rendering pipeline ran, not that it produced
content.

WHAT THIS DOES
--------------
Two independent detections, so a placeholder cannot pass both by accident:

1. CONTRACT-LEVEL. Every panel must declare a `plot_type`, and it must be one
   the renderer implements. A panel with no plot_type is a placeholder by
   construction. This catches the cause.

2. PIXEL-LEVEL. Measure the fraction of non-white pixels in the rendered PNG.
   A figure with real content inks a substantial share of the canvas; a
   placeholder page inks almost none. This catches the symptom, so it still
   fires if a future placeholder arrives by a route the contract check does not
   foresee.

Exit code is non-zero if any figure fails either test, so it can gate 7_1.

Run: python scripts/qc_figure_placeholders.py
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "outputs" / "figures" / "contracts"
FIGS = ROOT / "outputs" / "figures"
OUT = ROOT / "outputs" / "review" / "figure_placeholder_scan.json"

# plot_types the shared renderer dispatch actually implements (read from
# build_figures.py: grouped_bar, forest, heatmap, scatter, horizontal_bar,
# stacked_bar, network). Anything else falls through to `_placeholder`.
SUPPORTED = {"grouped_bar", "forest", "heatmap", "scatter", "horizontal_bar",
             "bar_horizontal", "stacked_bar", "stacked_bar_horizontal",
             "network"}
# A figure with real content inks this share of its pixels at least. Placeholder
# pages measure well under 0.1%; the densest real figure here measures >3%.
MIN_INK = 0.004


def ink_fraction(png: Path) -> float:
    with Image.open(png) as im:
        im.load()
        g = im.convert("L")
        hist = g.histogram()
    total = sum(hist)
    non_white = total - hist[255]
    return non_white / total if total else 0.0


def main() -> int:
    findings = []
    for cpath in sorted(CONTRACTS.glob("figure*.yaml")):
        try:
            c = yaml.safe_load(cpath.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append({"figure": cpath.stem, "check": "contract",
                             "ok": False, "detail": f"unparseable: {e}"})
            continue
        stem = c.get("figure_id") or cpath.stem
        # A withdrawn figure is reported but does not fail the gate. It must stay
        # visible: a scan that cannot see a withdrawn figure cannot tell
        # withdrawal from repair. But a gate that can never pass is not a gate.
        withdrawn = (c.get("disposition") or "").strip() == "withdrawn"
        manual = bool((c.get("renderer") or "").strip())
        if manual:
            # A manually drawn figure declares a renderer instead of
            # plot_types, which is the project precedent set by figure7 and
            # figure8. Requiring plot_type here would flag every such figure.
            pass
        png = FIGS / f"{stem}.png"
        bad_panels, unsupported = [], []
        for p in c.get("panels") or []:
            pt = (p.get("plot_type") or "").strip()
            if not pt:
                bad_panels.append(p.get("id"))
            elif pt.lower() not in SUPPORTED:
                unsupported.append({"panel": p.get("id"), "plot_type": pt})
        ok_contract = withdrawn or manual or (not bad_panels and not unsupported)
        findings.append({
            "figure": stem, "check": "contract", "ok": ok_contract,
            "panels_without_plot_type": bad_panels,
            "panels_with_unsupported_plot_type": unsupported,
        })
        if png.exists():
            ink = ink_fraction(png)
            findings.append({
                "figure": stem, "check": "pixels", "png": png.name,
                "withdrawn": withdrawn,
                "ink_fraction": round(ink, 6),
                "min_required": MIN_INK, "ok": ink >= MIN_INK,
            })
        else:
            findings.append({"figure": stem, "check": "pixels", "ok": withdrawn,
                             "withdrawn": withdrawn,
                             "detail": "withdrawn: no rendered PNG" if withdrawn else "no rendered PNG"})

    failed = [f for f in findings if not f["ok"]]
    blank = [f for f in findings if f["check"] == "pixels" and not f["ok"]]
    placeholder_ct = [f for f in findings
                      if f["check"] == "contract" and not f["ok"]]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "why": ("verify_figures_tables.py passes a blank page because it only "
                "checks that the pipeline ran; this scan checks that it "
                "produced content"),
        "min_ink_fraction": MIN_INK,
        "n_findings": len(findings), "n_failed": len(failed),
        "blank_or_placeholder_figures": sorted(
            {f["figure"] for f in failed}),
        "findings": findings,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    for f in findings:
        flag = "PASS" if f["ok"] else "FAIL"
        if f.get("withdrawn"):
            flag = "WDRN"
        if f["check"] == "contract":
            det = (f"no plot_type: {f.get('panels_without_plot_type')}"
                   if f.get("panels_without_plot_type")
                   else f"unsupported: {f.get('panels_with_unsupported_plot_type')}"
                   if f.get("panels_with_unsupported_plot_type") else "all panels typed")
        else:
            det = (f"ink {f['ink_fraction']:.4%} (min {MIN_INK:.2%})"
                   if "ink_fraction" in f else f.get("detail", ""))
        print(f"  {flag}  {f['figure']:34s} {f['check']:9s} {det}")
    print(f"\n{len(findings)-len(failed)}/{len(findings)} checks PASS")
    withdrawn_figs = sorted({f["figure"] for f in findings if f.get("withdrawn")})
    if withdrawn_figs:
        print(f"WITHDRAWN (reported, not failing the gate): {withdrawn_figs}")
    if failed:
        print(f"BLANK OR PLACEHOLDER: {sorted({f['figure'] for f in failed})}")
    print(f"-> {OUT}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
