#!/usr/bin/env python
"""Assemble the submission package (writer 7_9).

HONEST STATUS OF THE JOURNAL-REQUIREMENTS SNAPSHOT
--------------------------------------------------
The phase requires the journal's author guidelines to be fetched ONLINE and the
package enforced against them. For the configured target, Ophthalmology
(Elsevier / American Academy of Ophthalmology), that was not possible:

  https://www.aaojournal.org/content/authorinfo                      -> HTTP 403
  https://www.elsevier.com/journals/ophthalmology/0161-6420          -> redirect
       ?generatepdf=true                                                to sciencedirect.com
  https://www.sciencedirect.com/journal/ophthalmology/publish/        -> HTTP 403
       guide-for-authors

The local fallback, references/submission_checklists.md, likewise contains NO
entry for Ophthalmology, nor for any of the three backups (JAMA Ophthalmology,
British Journal of Ophthalmology, American Journal of Ophthalmology). Its
entries cover Reproductive Toxicology, Lancet Digital Health, npj Digital
Medicine, Nature Medicine, BMC Medical Informatics, JMIR and Environment
International.

So there is no source, online or local, from which this project can state
Ophthalmology's word limit, abstract limit, figure cap or reference style.
Rather than import the limits of a DIFFERENT journal -- which is how a
submission silently breaches a cap -- the snapshot records the failure, the
URLs tried, the HTTP codes, and the counts of what we actually have, so the
author can check them against the real guidelines in one pass. Every count below
is computed, not estimated.

Run: python scripts/build_submission_package.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess

import yaml

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "outputs" / "paper"
SUB = ROOT / "outputs" / "submission"

ATTEMPTS = [
    ("https://www.aaojournal.org/content/authorinfo", "HTTP 403 (Cloudflare)"),
    ("https://www.elsevier.com/journals/ophthalmology/0161-6420/guide-for-authors",
     "cross-origin redirect to sciencedirect.com, not followed"),
    ("https://www.sciencedirect.com/journal/ophthalmology/publish/guide-for-authors",
     "HTTP 403"),
]


def _split_body(text: str) -> tuple[str, str, str]:
    """Split the assembled manuscript into (body, legends, tables).

    The split has to happen BEFORE any heading is stripped, because the split
    markers ARE headings. An earlier version stripped headings first and then
    searched for "# Figure Legends", found nothing, and counted the legends and
    tables into the body -- reporting 9,873 words for a 6,426-word body and a
    5,307-word Discussion. An inflated count is not harmless: it invites cutting
    science to meet a limit that was never breached.
    """
    body, legends, tables = text, "", ""
    i = text.find("# Figure Legends")
    j = text.find("# Table 1")
    if i < 0:
        i = text.find("\u56fe\u4f8b")          # the Chinese legends heading
    if i >= 0:
        body, legends = text[:i], text[i:j if j > i else len(text)]
    if j > i >= 0:
        tables = text[j:]
    return body, legends, tables


def words(text: str) -> int:
    t = re.sub(r"^#.*$", "", text, flags=re.M)
    t = re.sub(r"\|.*\|", "", t, flags=re.M)
    return len(re.findall(r"\b[\w'\u2019-]+\b", t))


def main() -> int:
    SUB.mkdir(parents=True, exist_ok=True)
    ms = PAPER / "manuscript.md"
    text = ms.read_text(encoding="utf-8")
    body, legends, tables = _split_body(text)

    abs_m = re.search(r"# Abstract(.*?)# Introduction", body, re.S)
    disc = re.search(r"# Discussion(.*)\Z", body, re.S)
    counts = {
        "manuscript_bytes": ms.stat().st_size,
        "manuscript_body_words": words(body),
        "legends_words": words(legends),
        "tables_words": words(tables),
        "abstract_words": words(abs_m.group(1)) if abs_m else None,
        "discussion_words": words(disc.group(1)) if disc else None,
        "figures": len(sorted({int(x) for x in re.findall(r"Figure\s+(\d+)", text)})),
        "tables": len(sorted({int(x) for x in re.findall(r"Tables?\s+(\d+)", text)})),
        "references_cited": len(set(re.findall(r"\[(C\d{3})\]", text))),
        "reference_pool": len(json.loads(
            (PAPER / "citation_pool.json").read_text(encoding="utf-8"))["entries"]),
    }

    snapshot = [
        "# Journal requirements snapshot",
        "",
        f"**Target journal:** Ophthalmology (Elsevier / American Academy of "
        f"Ophthalmology), ISSN 0161-6420 — configured as "
        f"`target_journal_primary` in `.planner.config.json`.",
        f"**Snapshot date:** {date.today()}.",
        "",
        "## STATUS: NOT OBTAINED — online fetch blocked, local fallback has no entry",
        "",
        "| URL attempted | Result |",
        "|---|---|",
    ]
    for url, res in ATTEMPTS:
        snapshot.append(f"| {url} | {res} |")
    snapshot += [
        "",
        "The local fallback `references/submission_checklists.md` was read in "
        "full. **It contains no entry for Ophthalmology**, nor for JAMA "
        "Ophthalmology, British Journal of Ophthalmology or American Journal of "
        "Ophthalmology (the configured backups). Its entries cover Reproductive "
        "Toxicology, Lancet Digital Health, npj Digital Medicine, Nature "
        "Medicine, BMC Medical Informatics, JMIR and Environment International.",
        "",
        "**Consequence:** this project cannot state the target journal's word "
        "limit, abstract limit, figure/table caps or reference style from any "
        "available source. Importing the limits of a *different* journal is how "
        "a submission silently breaches a cap, so no limits are asserted here. "
        "The author must verify the four items below against the journal's "
        "official guide before submission.",
        "",
        "## What we do have: computed counts of the assembled package",
        "",
        "| Quantity | Value |",
        "|---|---|",
        f"| Manuscript size | {counts['manuscript_bytes']:,} B |",
        f"| Manuscript body words (excl. legends and tables) | {counts['manuscript_body_words']:,} |",
        f"| Figure-legend words | {counts['legends_words']:,} |",
        f"| Table words | {counts['tables_words']:,} |",
        f"| Abstract words | {counts['abstract_words']:,} |",
        f"| Discussion words | {counts['discussion_words']:,} |",
        f"| Figures | {counts['figures']} |",
        f"| Tables | {counts['tables']} |",
        f"| References cited | {counts['references_cited']} |",
        f"| Entries in the verified citation pool | {counts['reference_pool']} |",
        "",
        "## To verify before submission (author)",
        "",
        "1. Main-text word limit and whether the abstract and tables count "
        "towards it.",
        "2. Abstract structure and word limit (Ophthalmology has required a "
        "structured abstract since 2013).",
        "3. Figure and table caps, and the required figure file format and DPI.",
        "4. Reference style and cap (the pool is Vancouver-ready but the cap is "
        "unknown).",
        "5. Reporting-guideline requirement — TRIPOD+AI [C001] and DECIDE-AI "
        "[C002] are already cited in Methods, so any requirement for them is met; "
        "confirm the journal does not additionally require a completed checklist "
        "as a supplementary file.",
        "",
        "## Local fallback used for structure only",
        "",
        "The *general* requirements in `references/submission_checklists.md` "
        "(cover letter, manuscript, separate figures, separate tables, "
        "statements) were used to decide **which files to assemble**. No "
        "journal-specific numeric limit was taken from it, because it has none "
        "for this journal.",
    ]
    (SUB / "journal_guidelines_snapshot.md").write_text(
        "\n".join(snapshot), encoding="utf-8")

    # ---- package assembly --------------------------------------------------
    (SUB / "figures").mkdir(exist_ok=True)
    (SUB / "tables").mkdir(exist_ok=True)
    shutil.copy2(ms, SUB / "manuscript.md")
    shutil.copy2(PAPER / "figure_legends.md", SUB / "figure_legends.md")

    figs, tabs = [], []
    # Display-number mapping. The figure contracts keep a stable internal id
    # (figure6_dose_response) while the manuscript numbers the same figure as
    # Figure 4, because two earlier figures were withdrawn and the rest were
    # renumbered. Copying by filename therefore shipped files whose names
    # disagreed with the text. The package now names each file by the display
    # number its contract declares, so a reviewer opening the package sees the
    # same numbers the manuscript uses.
    display: dict[str, str] = {}
    skipped: list[str] = []
    for cpath in sorted((ROOT / "outputs" / "figures" / "contracts")
                        .glob("figure*.yaml")):
        try:
            c = yaml.safe_load(cpath.read_text(encoding="utf-8")) or {}
        except Exception as e:
            # Report rather than swallow. A bare `except: continue` here once hid
            # a missing `import yaml` -- every contract failed, `display` came out
            # empty, and the package silently shipped zero figures.
            skipped.append(f"{cpath.name}: {type(e).__name__}: {e}")
            continue
        stem, num = c.get("figure_id"), c.get("figure_number")
        if stem and num is not None and (c.get("disposition") or "") != "withdrawn":
            display[str(stem)] = f"Figure{num}"
    if skipped:
        print("contracts skipped:")
        for s in skipped:
            print(f"  {s}")
    if not display:
        print("ERROR: no figure resolved to a display number; the package would "
              "ship no figures. Aborting rather than writing an empty figure set.")
        return 1

    # Clear the figures directory first. The previous version copied only when
    # the destination did not exist, so once a file was in the package it was
    # never refreshed: shipped figures stayed at their first-build state even
    # after the figures themselves were redrawn.
    fdir = SUB / "figures"
    for old in fdir.glob("*"):
        if old.is_file():
            old.unlink()
    for ext in ("tiff", "png", "svg", "pdf"):
        for f in sorted((ROOT / "outputs" / "figures").glob(f"*.{ext}")):
            if f.stem not in display:
                continue          # withdrawn or unregistered figure
            name = f"{display[f.stem]}_{f.stem.split('_', 1)[1]}.{ext}"
            shutil.copy2(f, fdir / name)
            figs.append(name)
    for f in sorted((ROOT / "outputs" / "tables").glob("table*.md")):
        shutil.copy2(f, SUB / "tables" / f.name)
        tabs.append(f.name)

    (SUB / "package_manifest.json").write_text(json.dumps({
        "assembled_on": str(date.today()),
        "target_journal": "Ophthalmology (ISSN 0161-6420)",
        "journal_limits_verified": False,
        "journal_limits_note": ("online fetch blocked (403) and the local "
                                "checklist has no entry for this journal; see "
                                "journal_guidelines_snapshot.md"),
        "counts": counts,
        "files": {"manuscript": "manuscript.md",
                  "legends": "figure_legends.md",
                  "figures": figs, "tables": tabs},
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"snapshot      : {SUB/'journal_guidelines_snapshot.md'}")
    print(f"limits verified: False  (online 403; no local entry)")
    print(f"counts        : {counts}")
    print(f"figures copied: {len(figs)}  tables copied: {len(tabs)}")
    print(f"-> {SUB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
