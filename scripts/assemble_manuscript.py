#!/usr/bin/env python
"""Assemble outputs/paper/manuscript.md from the confirmed section files.

Section order is IMRaD with the abstract first and the figure legends and tables
after the Discussion, which is the layout the target journals use. No prose is
rewritten here: this script only concatenates what the author gate has already
confirmed, so that the assembled manuscript cannot silently diverge from the
sections that were reviewed.

It also writes an assembly manifest recording, for each section, its byte size
and the SHA-256 of the file that went in, so any later divergence between a
section and the manuscript is detectable rather than assumed away.

Run: python scripts/assemble_manuscript.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SEC = ROOT / "outputs" / "paper" / "sections"
PAPER = ROOT / "outputs" / "paper"

TITLE = (
    "An explainable rule-knowledge-graph-LLM agent for exposome-eye risk "
    "stratification: external gains, a development-informed benchmark, and "
    "rules that do not transport"
)

ORDER = [
    ("abstract", "Abstract"),
    ("introduction", "Introduction"),
    ("methods", "Methods"),
    ("results", "Results"),
    ("discussion", "Discussion"),
    # Declarations was absent from this list entirely, so the assembled
    # manuscript shipped with no ethics, data-availability, code-availability,
    # funding, competing-interest or CRediT statement -- a desk-reject item at
    # any ICMJE journal. The earlier R11 manuscript had a Declarations block; it
    # was lost when the section list was rewritten for the cohort layer.
    ("declarations", "Declarations"),
]

TABLES = [
    ("table1_registry.md", "Table 1"),
    ("table2_rules.md", "Table 2"),
    ("table3_performance_by_dataset.md", "Table 3"),
    ("table4_transportability.md", "Table 4"),
]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def strip_h1(text: str) -> str:
    """Drop a section file's own '# Heading' so it does not duplicate ours."""
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def main() -> int:
    body = [f"# {TITLE}", "",
            "**Running title:** Transportability of exposome rules for eye disease",
            "", "---", ""]
    manifest = {"assembled_on": str(date.today()), "title": TITLE,
                "sections": [], "tables": [], "missing": []}

    for key, heading in ORDER:
        fp = SEC / f"{key}.md"
        if not fp.exists():
            manifest["missing"].append(key)
            continue
        text = strip_h1(fp.read_text(encoding="utf-8"))
        # ALWAYS emit the section heading. An earlier version tested
        # `text.startswith("#")` to decide whether one was needed; after
        # strip_h1 the body begins with "## Subsection", which also satisfies
        # that test, so the Methods and Discussion headings silently vanished
        # from the assembled manuscript. The QC caught it.
        body += [f"# {heading}", "", text, "", "---", ""]
        manifest["sections"].append(
            {"section": key, "bytes": fp.stat().st_size, "sha256_16": sha(fp)})

    # Citations live as [Cxxx] codes in the section files. Renumber them in
    # first-appearance order and render the Vancouver block here, in memory,
    # so that re-assembly cannot ship uncited codes or drop the References
    # section. build_references.py documents this as the 7_8 integration point.
    prose = "\n".join(body).rstrip() + "\n"
    if "--no-references" not in sys.argv:
        import build_references as br  # scripts/ is on sys.path
        pool_path = br.resolve_pool(PAPER / "manuscript.md", None)
        pool, _schema = br.load_pool(pool_path)
        raw_dir = br.resolve_raw_dir(PAPER / "manuscript.md", None)
        br.enrich_pool(pool, br.load_enrichment(raw_dir))
        processed = br.process_text(prose, pool, max_authors=6,
                                    audit_comments=True,
                                    source="assemble_manuscript.py")
        prose = (processed.text.rstrip() + "\n\n"
                 + processed.references.rstrip() + "\n\n---\n\n")
        refs = processed.references.rstrip() + "\n"
        manifest["sections"].append(
            {"section": "references", "bytes": len(refs.encode("utf-8")),
             "sha256_16": hashlib.sha256(refs.encode("utf-8")).hexdigest()[:16]})
    parts = [prose]

    lg = PAPER / "figure_legends_main.md"
    if lg.exists():
        # KEEP the legends heading. strip_h1 was applied here too, which removed
        # "# Figure Legends" from the assembled manuscript and left the
        # Discussion running straight into the legends with no structural
        # separator -- a journal needs the boundary, and it also made the word
        # count unable to tell prose from legends.
        # The Chinese mirror in figure_legends.md is an internal reading aid,
        # not part of the submission manuscript. Keep the assembled paper
        # English-only.
        lg_text = lg.read_text(encoding="utf-8").split("# 图例（中文）")[0]
        parts += ["# Figure Legends", "",
                  strip_h1(lg_text), "", "---", ""]
        manifest["sections"].append(
            {"section": "figure_legends", "bytes": lg.stat().st_size,
             "sha256_16": sha(lg)})

    for fname, label in TABLES:
        tp = ROOT / "outputs" / "tables" / fname
        if not tp.exists():
            manifest["missing"].append(fname)
            continue
        # Same reasoning as the legends: keep an explicit "# Table N" heading so
        # the tables are separable from the prose.
        parts += [f"# {label}", "",
                  strip_h1(tp.read_text(encoding="utf-8")), "", "---", ""]
        manifest["tables"].append({"table": label, "file": fname,
                                   "bytes": tp.stat().st_size,
                                   "sha256_16": sha(tp)})

    out = PAPER / "manuscript.md"
    out.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    manifest["assembled_bytes"] = out.stat().st_size
    (PAPER / "manuscript_assembly_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"title    : {TITLE[:78]}...")
    for s in manifest["sections"]:
        print(f"  section {s['section']:16s} {s['bytes']:>7,} B  {s['sha256_16']}")
    for t in manifest["tables"]:
        print(f"  table   {t['table']:16s} {t['bytes']:>7,} B  {t['sha256_16']}")
    if manifest["missing"]:
        print(f"  MISSING: {manifest['missing']}")
    print(f"\n-> {out}  ({out.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
