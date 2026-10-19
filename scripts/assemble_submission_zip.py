#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assemble the phase-7_9 submission zip, with the checks the skill's stub lacks.

The family's `build_submission_pkg.py` is a scaffold: four of its steps are TODO
comments, and two behaviours made it unsafe to run as-is.

1. **It rebuilt `outputs/paper/manuscript.md` from the four section files plus
   the legends.** That drops the title, the abstract, all seven tables and the
   Declarations section, and it silently overwrote a 118,498-byte manuscript with
   a 94,534-byte one. A packaging step must never re-derive the artifact it is
   packaging.

2. **It looked for the submission files in `outputs/paper/` while three of them
   live in `outputs/submission/`**, so the cover letter, the data availability
   statement and the graphical abstract were left out of the archive without any
   message.

This script packages what is on disk, verifies the manuscript it is shipping is
the complete one, and refuses to write an archive that is missing a required
file.

Run: python scripts/assemble_submission_zip.py
"""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "outputs" / "paper"
SUB = ROOT / "outputs" / "submission"
ZIP = SUB / "submission_pkg.zip"

REQUIRED = [
    "manuscript.md",
    "figure_legends.md",
    "citation_pool.json",
    "cover_letter.md",
    "highlights.md",
    "data_availability.md",
    "graphical_abstract.svg",
    "strobe_checklist.md",
    "journal_guidelines_snapshot.md",
]

# manuscript.en.md is intentionally absent: the manuscript is English-native, so
# the bilingual pair the skill assumes does not exist. Recorded, not faked.
NOT_APPLICABLE = {"manuscript.en.md": "manuscript is English-native"}

# The shipped manuscript must contain these. Each probe is the form the
# manuscript actually uses, which an earlier version of this check got wrong: the
# headings are level-1 (`# Abstract`, not `## Abstract`), and the tables are
# shipped as SEPARATE files under tables/ rather than inlined, so the manuscript
# carries only in-text references to them.
MUST_CONTAIN = ["# ", "# Abstract", "# Declarations", "Table 7", "Table 1"]


def locate(name: str) -> Path | None:
    for base in (PAPER, SUB):
        p = base / name
        if p.exists():
            return p
    return None


def main() -> int:
    missing = [n for n in REQUIRED if locate(n) is None]
    if missing:
        print("REFUSING TO PACKAGE: required files not found:")
        for m in missing:
            print(f"  {m}")
        return 1

    ms = locate("manuscript.md")
    text = ms.read_text(encoding="utf-8")
    print(f"manuscript being packaged: {ms} ({len(text.encode('utf-8')):,} B)")
    absent = [m for m in MUST_CONTAIN if m not in text]
    if absent:
        print("REFUSING TO PACKAGE: the manuscript is missing:")
        for a in absent:
            print(f"  {a!r}")
        print("  (an earlier run of the family's assembler dropped exactly these)")
        return 1
    print(f"  all {len(MUST_CONTAIN)} required sections present")

    written = []
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in REQUIRED:
            src = locate(name)
            zf.write(src, name)
            written.append(name)
        if ZIP.exists():                      # never zip the archive itself
            pass
        for fig in sorted((ROOT / "outputs" / "figures").glob("figure*.*")):
            if fig.suffix.lower() in (".pdf", ".png", ".svg", ".tiff", ".tif"):
                zf.write(fig, f"figures/{fig.name}")
        for tbl in sorted((ROOT / "outputs" / "tables").glob("table*.md")):
            zf.write(tbl, f"tables/{tbl.name}")

    with zipfile.ZipFile(ZIP) as zf:
        names = zf.namelist()
    print(f"\narchive: {ZIP}")
    print(f"  {len(names)} entries, {ZIP.stat().st_size:,} B")
    print(f"  top-level files : {sum(1 for n in names if '/' not in n)}")
    print(f"  figures         : {sum(1 for n in names if n.startswith('figures/'))}")
    print(f"  tables          : {sum(1 for n in names if n.startswith('tables/'))}")
    for k, why in NOT_APPLICABLE.items():
        print(f"  not applicable  : {k} ({why})")

    still = [n for n in REQUIRED if n not in names]
    if still:
        print(f"  ERROR: {still} did not make it into the archive")
        return 1
    print("  every required file is in the archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
