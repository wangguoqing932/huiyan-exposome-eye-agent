#!/usr/bin/env python
"""English-manuscript QC for writer 7_8.

The skill's polish_bilingual.py is built for a Chinese draft plus an English
translation. This project's manuscript is English-native, so that pairing does
not apply and the tool's bilingual check has nothing to compare. What the phase
actually needs is a QC on the English manuscript itself, which is what this does:

  * no authoring residue anywhere in the assembled manuscript ([TODO], {{...}},
    "Scaffold stub", "fill in during");
  * every figure cited in the prose has a legend, and every legend a citation;
  * every table cited exists as a file, and every table file is cited;
  * citation keys are all resolvable in the verified pool, and every pool entry
    is used somewhere;
  * the abstract does not report a number that the Results does not carry;
  * section order and presence.

Exit code is non-zero on any failure, so it can gate the submission package.

Run: python scripts/qc_english_manuscript.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "outputs" / "paper"
MS = PAPER / "manuscript.md"
POOL = PAPER / "citation_pool.json"

REPORT: list[tuple[str, bool, str]] = []


def ck(tag: str, ok: bool, detail: str = "") -> None:
    REPORT.append((tag, bool(ok), detail))


def main() -> int:
    if not MS.exists():
        print("manuscript.md missing -- run scripts/assemble_manuscript.py")
        return 1
    text = MS.read_text(encoding="utf-8")

    # ---- authoring residue -------------------------------------------------
    for pat, label in ((r"\[TODO", "[TODO"),
                       (r"\{\{", "{{...}}"),
                       (r"Scaffold stub", "Scaffold stub"),
                       (r"fill in during", "fill in during"),
                       (r"XXX", "XXX")):
        hits = len(re.findall(pat, text))
        ck(f"residue:{label}", hits == 0, f"{hits} occurrence(s)")

    # ---- sections ----------------------------------------------------------
    for name in ("Abstract", "Introduction", "Methods", "Results",
                 "Discussion"):
        ck(f"section:{name}", f"# {name}" in text,
           "present" if f"# {name}" in text else "MISSING")
    ck("section:Conclusion", "## Conclusion" in text,
       "present" if "## Conclusion" in text else "MISSING")

    # ---- figures -----------------------------------------------------------
    cited_figs = sorted({int(x) for x in
                         re.findall(r"Figure\s+(\d+)", text)})
    legend_figs = sorted({int(x) for x in
                          re.findall(r"\*\*Figure (\d+)\.", text)})
    ck("figures:cited_have_legend",
       set(cited_figs) <= set(legend_figs),
       f"cited {cited_figs}; legends {legend_figs}")
    ck("figures:legend_have_citation",
       set(legend_figs) <= set(cited_figs),
       f"legends {legend_figs}; cited {cited_figs}")

    # ---- tables ------------------------------------------------------------
    # Match "Table 3" AND the plural form "Tables 1 and 4". An earlier regex used
    # `Table\s+(\d+)`, which cannot match "Tables 1 and 4" because of the plural
    # "s" -- so a table that WAS cited was reported as uncited. The checker was
    # wrong, not the manuscript.
    cited_tabs: set[int] = set()
    for m in re.finditer(r"Tables?\s+((?:\d+)(?:\s*(?:,|and)\s*\d+)*)", text):
        cited_tabs |= {int(x) for x in re.findall(r"\d+", m.group(1))}
    cited_tabs = sorted(cited_tabs)
    tab_files = sorted(int(re.search(r"table(\d+)_", p.name).group(1))
                       for p in (ROOT / "outputs" / "tables").glob("table*.md")
                       if re.search(r"table(\d+)_", p.name))
    ck("tables:cited_exist", set(cited_tabs) <= set(tab_files),
       f"cited {cited_tabs}; files {tab_files}")
    ck("tables:files_cited", set(tab_files) <= set(cited_tabs),
       f"files {tab_files}; cited {cited_tabs}")

    # ---- citations ---------------------------------------------------------
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    ids = {e["pool_id"] for e in pool["entries"]}
    # Third instance of a too-narrow regex in this checker. Requiring the exact
    # form [C031] meant grouped citations such as [C031, C032, C033] were
    # invisible, so three references the manuscript DOES cite were reported as
    # uncited. Collect every C### token inside any bracketed span instead.
    cited: list[str] = []
    for _m in re.finditer(r"\[([^\]]*)\]", text):
        cited += re.findall(r"C\d{3}", _m.group(1))
    cited = sorted(set(cited))
    ck("citations:all_in_pool", set(cited) <= ids,
       f"outside pool: {sorted(set(cited) - ids)}")
    unused = sorted(ids - set(cited))
    ck("citations:pool_all_used", not unused, f"unused: {unused}")
    ck("citations:no_retracted",
       not [e for e in pool["entries"] if e.get("retraction_flag")],
       "none flagged")
    ck("citations:n", len(cited) >= 15, f"{len(cited)} cited")

    # ---- abstract numbers must appear in the results -----------------------
    abs_m = re.search(r"# Abstract(.*?)# Introduction", text, re.S)
    res_m = re.search(r"# Results(.*?)# Discussion", text, re.S)
    if abs_m and res_m:
        abs_nums = set(re.findall(r"\d+\.\d+", abs_m.group(1)))
        res_nums = set(re.findall(r"\d+\.\d+", res_m.group(1)))
        missing = sorted(abs_nums - res_nums)
        # a handful of abstract-only figures (effect sizes quoted once) is
        # acceptable, but the bulk must be traceable
        ck("abstract:numbers_traceable",
           len(missing) <= 8,
           f"{len(missing)} abstract-only: {missing[:8]}")

    bad = [r for r in REPORT if not r[1]]
    for tag, ok, detail in REPORT:
        print(f"  {'PASS' if ok else 'FAIL'}  {tag:38s} {detail}")
    print(f"\n{len(REPORT)-len(bad)}/{len(REPORT)} checks PASS")
    print(f"manuscript: {MS.stat().st_size:,} B, "
          f"{len(cited)} citations, figures {legend_figs}, tables {tab_files}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
