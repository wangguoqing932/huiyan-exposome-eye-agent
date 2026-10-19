#!/usr/bin/env python
"""Extract the CRELES raw .dta files out of the eight distributed zips.

CRELES is the only one of the eight ageing cohorts that ships as zip archives,
so it needs an unpacking step before any codebook work.

Two things the naive unpacking gets wrong and this script handles:
  * each zip carries a parallel `__MACOSX/._*` tree of AppleDouble metadata
    (145 entries across the eight zips) which doubles the apparent file count
    and is not data;
  * file names collide across cohorts/waves (`DS1 Main form ...`), so each
    output is prefixed with a truncated zip stem to stay unique.

Output: data/raw/creles/<zipstem28>__<basename>.dta

Run: PYTHONUTF8=1 python scripts/extract_creles.py
"""
from __future__ import annotations

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(
    r"E:\BaiduNetdiskDownload\所有数据库\08. CRELES 哥斯达黎加老龄化健康研究\Raw_data")
OUT = ROOT / "data" / "raw" / "creles"


def main() -> int:
    if not SRC.exists():
        print(f"source missing: {SRC}")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    written = skipped_meta = existed = 0
    for z in sorted(SRC.glob("*.zip")):
        with zipfile.ZipFile(z) as f:
            for member in f.namelist():
                base = pathlib.Path(member).name
                if (member.startswith("__MACOSX") or "/._" in member
                        or base.startswith("._") or member.endswith("/")):
                    skipped_meta += 1
                    continue
                if not member.lower().endswith(".dta"):
                    continue
                tgt = OUT / f"{z.stem[:28]}__{base}"
                if tgt.exists():
                    existed += 1
                    continue
                with f.open(member) as s, open(tgt, "wb") as d:
                    d.write(s.read())
                written += 1

    total = len(list(OUT.glob("*.dta")))
    print(f"extracted={written} already_present={existed} "
          f"skipped_macos_metadata={skipped_meta} total_dta={total}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
