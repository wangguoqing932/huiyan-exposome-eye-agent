#!/usr/bin/env python
"""Build the submission-ready Word manuscript (all parts in one .docx).

Source of truth: outputs/paper/manuscript.md (R21 assembly). The Markdown is
parsed block by block so that nothing is pasted as raw Markdown:

  * title page (authors and affiliations read from
    configs/submission_authors.json);
  * Abstract through Discussion, with inline bold/italic/code preserved;
  * Declarations;
  * the 27 numbered references (hidden audit comments stripped);
  * Figure legends (English; the Chinese mirror is intentionally excluded);
  * the 9 tables as editable Word tables, in landscape pages;
  * the 8 figures (6 main + S1/S2) embedded at 600-dpi PNG.

Formatting: A4, Times New Roman 12 pt, 1.5 line spacing, first-line indent,
continuous line numbers on the main text, page numbers, three-line tables.

Run: python scripts/build_manuscript_docx.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "outputs" / "paper" / "manuscript.md"
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
OUT = ROOT / "outputs" / "paper" / "manuscript_agent_first.docx"

BODY_FONT = "Times New Roman"
CJK_FONT = "宋体"
HEAD_FONT = "Arial"
CODE_FONT = "Courier New"
BLACK = RGBColor(0, 0, 0)
GREY = RGBColor(0x44, 0x44, 0x44)

FIG_FILES = [
    ("Figure 1", "figure1_architecture.png"),
    ("Figure 2", "figure2_performance.png"),
    ("Figure 3", "figure3_rule_evaluation.png"),
    ("Figure 4", "figure6_dose_response.png"),
    ("Figure 5", "figure7_power_mde.png"),
    ("Figure 6", "figure8_cohort_transportability.png"),
]

TABLE_FILES = [
    "table1_registry.md",
    "table2_rules.md",
    "table3_performance_by_dataset.md",
    "table4_transportability.md",
]

# --------------------------------------------------------------------------- #
# small XML helpers
# --------------------------------------------------------------------------- #
def set_run_font(run, size: float, *, bold: bool = False, italic: bool = False,
                 latin: str = BODY_FONT, east_asia: str = CJK_FONT,
                 color: RGBColor = BLACK) -> None:
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = latin
    run.font.color.rgb = color
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), east_asia)


def add_field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    for kind, text in (("begin", None), ("instr", instruction),
                       ("separate", None), ("text", "1"), ("end", None)):
        if kind == "instr":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = text
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run._r.append(el)


def add_line_numbers(section) -> None:
    ln = OxmlElement("w:lnNumType")
    ln.set(qn("w:countBy"), "1")
    ln.set(qn("w:restart"), "continuous")
    section._sectPr.append(ln)


def shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_table_three_line(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge, val in (("top", "single"), ("bottom", "single"),
                      ("left", "nil"), ("right", "nil"),
                      ("insideH", "nil"), ("insideV", "nil")):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), val)
        if val == "single":
            el.set(qn("w:sz"), "12")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "000000")
        borders.append(el)
    tbl_pr.append(borders)

    mar = OxmlElement("w:tblCellMar")
    for side, width in (("top", "0"), ("bottom", "0"),
                        ("left", "50"), ("right", "50")):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), width)
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tbl_pr.append(mar)


def header_bottom_border(row) -> None:
    for cell in row.cells:
        tc_pr = cell._tc.get_or_add_tcPr()
        borders = OxmlElement("w:tcBorders")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "0")
        bottom.set(qn("w:color"), "000000")
        borders.append(bottom)
        tc_pr.append(borders)


def repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def cant_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


# --------------------------------------------------------------------------- #
# inline Markdown
# --------------------------------------------------------------------------- #
INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\n]+\*|\\\*)")


def add_inline(paragraph, text: str, size: float, *,
               latin: str = BODY_FONT, color: RGBColor = BLACK) -> None:
    text = text.replace("<!--", "").replace("-->", "")
    text = re.sub(r"<!--.*?-->", "", text)
    for token in INLINE_RE.split(text):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**") and len(token) > 4:
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, size, bold=True, latin=latin, color=color)
        elif token.startswith("`") and token.endswith("`") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size - 0.5, latin=CODE_FONT, color=color)
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size, italic=True, latin=latin, color=color)
        elif token == "\\*":
            run = paragraph.add_run("*")
            set_run_font(run, size, latin=latin, color=color)
        else:
            run = paragraph.add_run(token)
            set_run_font(run, size, latin=latin, color=color)


# --------------------------------------------------------------------------- #
# block parsing
# --------------------------------------------------------------------------- #
def is_table_sep(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells)


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def parse_pipe_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = split_row(lines[i])
        if not is_table_sep(cells):
            rows.append(cells)
        i += 1
    width = max((len(r) for r in rows), default=0)
    for row in rows:
        row.extend([""] * (width - len(row)))
    return rows, i


def is_block_start(line: str) -> bool:
    s = line.strip()
    return (not s or s == "---" or s.startswith("#") or s.startswith("|")
            or re.match(r"^[-*] ", s) is not None
            or re.match(r"^\d+\. ", s) is not None)


def add_table(doc, rows: list[list[str]], font_size: float,
              total_width_cm: float = 24.0) -> None:
    if not rows:
        return
    cols = len(rows[0])
    table = doc.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_three_line(table)
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.width = Cm(total_width_cm / cols)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            add_inline(p, value, font_size,
                       latin=HEAD_FONT if i == 0 and False else BODY_FONT)
            if i == 0:
                for run in p.runs:
                    run.font.bold = True
        if i == 0:
            shade_cell_row(table.rows[0])
            header_bottom_border(table.rows[0])
            repeat_header(table.rows[0])
        cant_split(table.rows[i])


def shade_cell_row(row) -> None:
    for cell in row.cells:
        shade_cell(cell, "F2F2F2")


def add_heading(doc, text: str, level: int, *,
                page_break_before: bool = False) -> None:
    sizes = {1: 14.0, 2: 12.5, 3: 11.5}
    p = doc.add_paragraph()
    pf = p.paragraph_format
    if page_break_before:
        pf.page_break_before = True
    pf.space_before = Pt(14 if level == 1 else 10)
    pf.space_after = Pt(6 if level == 1 else 4)
    pf.keep_with_next = True
    pf.line_spacing = 1.3
    run = p.add_run(text)
    set_run_font(run, sizes[level], bold=True, latin=HEAD_FONT)
    # Mark the paragraph as a real heading so postcheck/TOC see the hierarchy.
    p.style = doc.styles[f"Heading {level}"]
    for r in p.runs:
        set_run_font(r, sizes[level], bold=True, latin=HEAD_FONT)


def add_body_paragraph(doc, text: str, *, indent: bool = True,
                       size: float = 12.0) -> None:
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)
    if indent:
        pf.first_line_indent = Cm(0.85)
    add_inline(p, text, size)


def add_list(doc, items: list[str], ordered: bool) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number" if ordered else "List Bullet")
        pf = p.paragraph_format
        pf.line_spacing = 1.5
        pf.space_after = Pt(0)
        add_inline(p, item, 12.0)


def render_body_blocks(doc, lines: list[str]) -> None:
    i = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith("# "):
            heading_text = s[2:].strip()
            add_heading(doc, heading_text, 1)
            i += 1
            continue
        if s.startswith("## "):
            add_heading(doc, s[3:].strip(), 2)
            i += 1
            continue
        if s.startswith("### "):
            add_heading(doc, s[4:].strip(), 3)
            i += 1
            continue
        if s.startswith("|"):
            rows, i = parse_pipe_table(lines, i)
            add_table(doc, rows, 8.0 if len(rows[0]) <= 6 else 7.0, total_width_cm=15.5)
            continue
        if re.match(r"^[-*] ", s):
            items: list[list[str]] = []
            while i < len(lines) and lines[i].strip():
                line = lines[i].strip()
                if re.match(r"^[-*] ", line):
                    items.append([line[2:].strip()])
                elif items and not is_block_start(line):
                    items[-1].append(line)
                else:
                    break
                i += 1
            add_list(doc, [" ".join(x) for x in items], ordered=False)
            continue
        if re.match(r"^\d+\. ", s):
            items = []
            while i < len(lines) and lines[i].strip():
                line = lines[i].strip()
                if re.match(r"^\d+\. ", line):
                    items.append([re.sub(r"^\d+\.\s+", "", line)])
                elif items and not is_block_start(line):
                    items[-1].append(line)
                else:
                    break
                i += 1
            add_list(doc, [" ".join(x) for x in items], ordered=True)
            continue
        para: list[str] = [s]
        i += 1
        while i < len(lines) and not is_block_start(lines[i]):
            para.append(lines[i].strip())
            i += 1
        add_body_paragraph(doc, " ".join(para))


# --------------------------------------------------------------------------- #
# section setup
# --------------------------------------------------------------------------- #
def setup_section(section, *, landscape: bool = False, line_numbers: bool = True,
                  header_text: str | None = None, count: int = 1) -> None:
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = Cm(29.7), Cm(21.0)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(1.5)
    section.footer_distance = Cm(1.75)
    if line_numbers:
        add_line_numbers(section)

    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    hp = section.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.text = ""
    if header_text:
        hr = hp.add_run(header_text)
        set_run_font(hr, 9, latin=HEAD_FONT, color=GREY)

    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.text = ""
    r = fp.add_run("Page ")
    set_run_font(r, 9, color=GREY)
    add_field(fp, "PAGE")
    r = fp.add_run(" of ")
    set_run_font(r, 9, color=GREY)
    add_field(fp, "NUMPAGES")


# --------------------------------------------------------------------------- #
# document parts
# --------------------------------------------------------------------------- #
def add_title_page(doc, title: str, running: str, main_words: int, abstract_words: int) -> None:
    auth = json.loads((ROOT / "configs" / "submission_authors.json")
                      .read_text(encoding="utf-8"))

    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run(title)
    set_run_font(r, 18, bold=True, latin=BODY_FONT)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run("Running title: " + running)
    set_run_font(r, 11, italic=True, latin=BODY_FONT)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(28)
    # Authors with superscript affiliation markers, rendered as Unicode.
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_line = ", ".join(
        f"{a['name']}\u00b9,\u00b2" + (",*" if a.get("corresponding") else "")
        for a in auth["authors"])
    r = p.add_run(author_line)
    set_run_font(r, 11.5, bold=False, latin=BODY_FONT)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run("Affiliations")
    set_run_font(r, 10.5, bold=True, latin=HEAD_FONT)
    for i, aff in enumerate(auth["affiliations"], 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(f"{i}. {aff}")
        set_run_font(r, 10, latin=BODY_FONT)

    corr = next(a for a in auth["authors"] if a.get("corresponding"))
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run("*Corresponding author")
    set_run_font(r, 10.5, bold=True, latin=HEAD_FONT)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(f"{corr['name']}, {corr['degree']}, {auth['corresponding_address']}. "
                  f"Email: {corr['email']}. ORCID: {corr['orcid']}.")
    set_run_font(r, 10, latin=BODY_FONT)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    r = p.add_run("ORCID: " + "; ".join(
        f"{a['name']} {a['orcid']}" for a in auth["authors"]) + ".")
    set_run_font(r, 10, latin=BODY_FONT)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.line_spacing = 1.4
    meta = [
        "Manuscript type: Original research",
        f"Main text: {main_words:,} words (Introduction\u2013Discussion); abstract {abstract_words} words",
        "Tables: 4; Figures: 6 main + 2 supplementary",
        "Keywords: " + "; ".join(auth["keywords"]),
        "Funding: none. Competing interests: none.",
        "Data: publicly available cohort and survey data; no human-subjects involvement",
        "Prepared: " + date.today().isoformat(),
    ]
    for line in meta:
        r = p.add_run(line + "\n")
        set_run_font(r, 10.5, latin=BODY_FONT)

    for para in doc.paragraphs:
        ppr = para._p.get_or_add_pPr()
        if ppr.find(qn("w:suppressLineNumbers")) is None:
            ppr.append(OxmlElement("w:suppressLineNumbers"))


def add_references(doc, lines: list[str]) -> None:
    for line in lines:
        m = re.match(r"^(\d+)\.\s+(.*?)\s*<!--.*?-->$", line.strip())
        text = m.group(2).strip() if m else line.strip()
        if not text or text in ("---", "."):
            continue
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(0.85)
        pf.first_line_indent = Cm(-0.85)
        pf.tab_stops.add_tab_stop(Cm(0.85))
        pf.line_spacing = 1.15
        pf.space_after = Pt(3)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        number = m.group(1) if m else ""
        r = p.add_run(f"{number}.\t")
        set_run_font(r, 10.5)
        add_inline(p, text, 10.5)


def add_legends(doc, lines: list[str]) -> None:
    for raw in lines:
        s = raw.strip()
        if not s or s == "---":
            continue
        if s.startswith("**Figure"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            add_inline(p, s, 11.0)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_inline(p, s, 10.5)


def add_table_page(doc, md_path: Path, first: bool) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    pending_break = not first
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("# "):
            p = doc.add_paragraph()
            if pending_break:
                p.paragraph_format.page_break_before = True
                pending_break = False
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            add_inline(p, s[2:].strip(), 10.0)
            for r in p.runs:
                r.font.bold = True
            i += 1
            continue
        if s.startswith("## ") or s.startswith("### "):
            level = 2 if s.startswith("## ") else 3
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(s[level + 1:].strip())
            set_run_font(r, 9.5, bold=True, latin=HEAD_FONT)
            i += 1
            continue
        if s.startswith("|"):
            rows, i = parse_pipe_table(lines, i)
            cols = len(rows[0]) if rows else 0
            add_table(doc, rows, 6.5 if cols >= 8 else 7.5, total_width_cm=24.2)
            continue
        para: list[str] = [s]
        i += 1
        while i < len(lines) and not is_block_start(lines[i]):
            para.append(lines[i].strip())
            i += 1
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline(p, " ".join(para), 8.0)


def figure_captions(legend_lines: list[str]) -> dict[str, str]:
    captions: dict[str, str] = {}
    for line in legend_lines:
        m = re.match(r"^\*\*(Figure (?:S)?\d+)\.\s*(.+?)\*\*$", line.strip())
        if m:
            captions[m.group(1)] = m.group(2).strip()
    return captions


def add_figure_pages(doc, captions: dict[str, str]) -> None:
    for idx, (label, filename) in enumerate(FIG_FILES):
        p = doc.add_paragraph()
        if idx:
            p.paragraph_format.page_break_before = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(label)
        set_run_font(r, 11, bold=True, latin=HEAD_FONT)

        img = FIG / filename
        if img.exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(str(img), width=Cm(15.4))
        else:
            p = doc.add_paragraph()
            r = p.add_run(f"[missing image: {filename}]")
            set_run_font(r, 9, italic=True, color=GREY)

        caption = captions.get(label, "")
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(f"{label}. ")
        set_run_font(r, 9.5, bold=True)
        add_inline(p, caption, 9.5)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    out_path = Path(args.out)

    lines = MD.read_text(encoding="utf-8").splitlines()
    title = lines[0][2:].strip()
    running = next(l.split("**Running title:**")[1].strip()
                   for l in lines[:5] if "**Running title:**" in l)

    abstract_i = lines.index("# Abstract")
    introduction_i = lines.index("# Introduction")
    refs_i = lines.index("# References")
    legends_i = lines.index("# Figure Legends")
    table1_i = lines.index("# Table 1")
    # The assembled submission manuscript is English-only: the Chinese legend
    # mirror is no longer part of manuscript.md. Fall back to the table marker.
    chinese_i = (lines.index("# 图例（中文）")
                 if "# 图例（中文）" in lines else table1_i)

    body_lines = lines[abstract_i:refs_i]
    ref_lines = lines[refs_i + 1:legends_i]
    legend_lines = lines[legends_i + 1:chinese_i]

    body_text = "\n".join(body_lines)
    abstract_text = "\n".join(lines[abstract_i:introduction_i])
    def word_count(text: str) -> int:
        # Microsoft Word-style: strip markdown marks, count whitespace tokens.
        return len(re.sub(r"[#*_`>|]+", " ", text).split())

    body_words = word_count(body_text)
    abstract_words = word_count(abstract_text)
    main_words = 0
    for name in ("introduction", "methods", "results", "discussion"):
        main_words += word_count(
            (ROOT / "outputs" / "paper" / "sections" / f"{name}.md")
            .read_text(encoding="utf-8"))

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), CJK_FONT)

    # Section 1: title page (no line numbers, no header)
    setup_section(doc.sections[0], landscape=False, line_numbers=False,
                  header_text=None)
    add_title_page(doc, title, running, main_words, abstract_words)

    # Section 2: main text + references + legends
    doc.add_section(WD_SECTION.NEW_PAGE)
    setup_section(doc.sections[-1], landscape=False, line_numbers=True,
                  header_text="Manuscript · Explainable rule-KG-LLM agent for exposome-eye risk stratification")
    render_body_blocks(doc, body_lines)

    add_heading(doc, "References", 1)
    add_references(doc, ref_lines)

    add_heading(doc, "Figure Legends", 1)
    add_legends(doc, legend_lines)

    # Section 3: tables (JMIR: portrait orientation only)
    doc.add_section(WD_SECTION.NEW_PAGE)
    setup_section(doc.sections[-1], landscape=False, line_numbers=False,
                  header_text="Tables")
    for idx, fname in enumerate(TABLE_FILES):
        add_table_page(doc, TAB / fname, first=(idx == 0))

    # Section 4: figures, portrait
    doc.add_section(WD_SECTION.NEW_PAGE)
    setup_section(doc.sections[-1], landscape=False, line_numbers=False,
                  header_text="Figures")
    add_figure_pages(doc, figure_captions(legend_lines))

    doc.save(out_path)
    print(f"[manuscript_agent_first.docx] {out_path}")
    print(f"  title page + body {body_words:,} words + references {len(ref_lines)} lines")
    print(f"  tables {len(TABLE_FILES)} + figures {len(FIG_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
