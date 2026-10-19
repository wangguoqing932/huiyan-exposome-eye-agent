#!/usr/bin/env python
"""Stage 0 inventory for the scientific-figures refurbishment pipeline.

Lists every figure/table artifact with a format probe (pixels, DPI, physical
size, editable-text flag) plus every data CSV that could feed a figure. Reads
rendered files only — it makes no judgement about quality (that is Stage 1, and
it requires looking at the renders).

Run with the system python (matplotlib/PIL live there):
  C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python310\\python.exe \
      scripts/figure_inventory_stage0.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
PAPER = ROOT / "outputs" / "paper"


def png_probe(p: Path):
    """Return (w, h, dpi_x, dpi_y, phys_mm_w, phys_mm_h, mode)."""
    try:
        from PIL import Image
    except Exception:
        return None
    with Image.open(p) as im:
        w, h = im.size
        dpi = im.info.get("dpi") or (None, None)
        mode = im.mode
    dx, dy = (dpi + (None, None))[:2] if isinstance(dpi, tuple) else (None, None)
    mmw = (w / dx * 25.4) if dx else None
    mmh = (h / dy * 25.4) if dy else None
    return dict(px=[w, h], dpi=[dx, dy],
                mm=[round(mmw, 1) if mmw else None, round(mmh, 1) if mmh else None],
                mode=mode)


def pdf_probe(p: Path):
    """Page size in mm + whether the text is selectable (editable) or outlined."""
    try:
        from pypdf import PdfReader
    except Exception:
        try:
            from PyPDF2 import PdfReader
        except Exception:
            return None
    try:
        r = PdfReader(str(p))
        box = r.pages[0].mediabox
        w_mm, h_mm = float(box.width) * 25.4 / 72, float(box.height) * 25.4 / 72
        raw = p.read_bytes()
        # a PDF with real text carries /Font; outlined text does not
        has_font = b"/Font" in raw
        return dict(pages=len(r.pages), mm=[round(w_mm, 1), round(h_mm, 1)],
                    has_font_resource=has_font)
    except Exception:
        return None


def svg_probe(p: Path):
    txt = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'viewBox="([^"]+)"', txt)
    fonts = len(re.findall(r"<text", txt))
    return dict(viewBox=m.group(1) if m else None, text_elements=fonts,
                has_raster=("<image" in txt))


def main() -> int:
    print("=" * 100)
    print("STAGE 0 INVENTORY — scientific-figures refurbishment pipeline")
    print("=" * 100)

    print("\n-- A. rendered figure artifacts in outputs/figures ----------------------")
    figdir = sorted(p for p in FIG.iterdir() if p.is_file())
    current, stale = [], []
    for p in figdir:
        if p.suffix.lower() not in (".png", ".pdf", ".svg", ".tiff"):
            continue
        entry = {"file": p.name, "kb": round(p.stat().st_size / 1024, 1)}
        if p.suffix.lower() == ".png":
            entry.update(png_probe(p) or {})
        elif p.suffix.lower() == ".pdf":
            entry.update(pdf_probe(p) or {})
        elif p.suffix.lower() == ".svg":
            entry.update(svg_probe(p) or {})
        # R11 pipeline figures vs everything else
        if re.match(r"figure[1-6]_[a-z_]+\.(png|pdf|svg|tiff)$", p.name) and "_R11" not in p.name:
            current.append(entry)
        else:
            stale.append(entry)
    for lab, rows in (("PIPELINE (contract-rendered, R11)", current),
                      ("OTHER / legacy / superseded", stale)):
        print(f"\n  [{lab}]")
        for e in rows:
            extra = ""
            if "mm" in e and e["mm"][0]:
                extra = f"{e['mm'][0]}x{e['mm'][1]} mm"
            if "dpi" in e and e["dpi"][0]:
                extra += f"  {e['dpi'][0]} dpi"
            if "px" in e:
                extra += f"  {e['px'][0]}x{e['px'][1]} px"
            if "has_font_resource" in e:
                extra += f"  editable_text={'yes' if e['has_font_resource'] else 'NO'}"
            if "text_elements" in e:
                extra += f"  <text>={e['text_elements']}"
            print(f"    {e['file']:44s}{e['kb']:>9.1f} KB  {extra}")

    print("\n-- B. tables ------------------------------------------------------------")
    for pat, where in (("*.csv", TAB), ("table*.md", PAPER)):
        for p in sorted(where.glob(pat)):
            print(f"    {p.relative_to(ROOT)}  ({round(p.stat().st_size/1024,1)} KB)")

    print("\n-- C. data CSVs that could feed a figure --------------------------------")
    csds = []
    for base in (ROOT / "outputs" / "figures" / "source_data",
                 ROOT / "outputs" / "confirmatory",
                 ROOT / "outputs", ROOT / "data" / "processed"):
        if not base.exists():
            continue
        for p in sorted(base.glob("*.csv")):
            csds.append(p)
    seen = set()
    for p in csds:
        r = p.relative_to(ROOT)
        if str(r) in seen:
            continue
        seen.add(str(r))
        try:
            import csv as _csv
            with p.open(encoding="utf-8-sig", newline="") as fh:
                hdr = next(_csv.reader(fh), [])
                ncol = len(hdr)
        except Exception:
            ncol = "?"
        print(f"    {str(r):66s} cols={ncol}")

    print("\n-- D. contracts vs rendered output --------------------------------------")
    cdir = FIG / "contracts"
    for c in sorted(cdir.glob("figure*.yaml*")):
        status = "SUPERSEDED" if c.suffix.endswith("superseded_R11") else "active"
        print(f"    {c.name:52s} {status}")

    print("\n" + "=" * 100)
    print("STOP — Stage 0 requires author confirmation of this inventory before")
    print("Stage 1 (diagnosis) begins. Nothing has been edited.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
