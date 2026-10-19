#!/usr/bin/env python
"""Rebuild KNHANES analysis frames from the raw Rdata collection.

Why this wrapper exists
-----------------------
This machine's R cannot open connections on paths containing non-ASCII
characters (the repo path is Chinese, as is the raw-data path). We verified
that file.exists() succeeds but gzfile()/load() fail with
"Illegal byte sequence" under every locale and every encoding variant.
Workaround: stage the .Rdata files into an ASCII directory, let R read/write
there, then move the results into the repo.

Usage
-----
    python scripts/build_knhanes_frames.py \
        --rdata-dir "E:\\BaiduNetdiskDownload\\所有数据库\\11. KNHANES 韩国国民健康与营养调查\\Rdata" \
        --out data/raw/knhanes_frames_v2

Notes
-----
* Staging defaults to <repo>/.kn_staging (gitignored). It is reused across
  runs, so a rebuild costs nothing after the first.
* The column map lives in configs/variable_map.yaml; edits belong there.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RDATA = Path(
    r"E:\BaiduNetdiskDownload\所有数据库\11. KNHANES 韩国国民健康与营养调查\Rdata"
)


def _ascii_staging_root() -> Path:
    """R cannot open non-ASCII paths on this host, so the staging area must be
    ASCII-only. <repo> is Chinese, so default to the system temp dir and verify."""
    for cand in (Path(tempfile.gettempdir()) / "huiyan_kn_staging",
                 Path("C:/Windows/Temp/huiyan_kn_staging")):
        try:
            if all(ord(c) < 128 for c in str(cand)):
                return cand
        except Exception:
            continue
    raise SystemExit(
        "no ASCII-safe staging directory available; pass --staging with an ASCII path"
    )


STAGING = _ascii_staging_root()
STAGING_IN = STAGING / "rdata"
STAGING_OUT = STAGING / "out"
RDATA_FILES = [
    "KNHANES 1998-2005.Rdata",
    "KNHANES 2007-2010.Rdata",
    "KNHANES 2011-2015.Rdata",
    "KNHANES 2016-2020.Rdata",
    "KNHANES 2021-2024.Rdata",
]
# the R script only needs these four
NEEDED = RDATA_FILES[1:]


def find_rscript() -> str:
    exe = shutil.which("Rscript")
    if exe:
        return exe
    for cand in sorted(Path(r"C:\Program Files\R").glob("R-*/bin/x64/Rscript.exe")):
        return str(cand)
    for cand in sorted(Path(r"D:\software\R-*").glob("bin/x64/Rscript.exe")):
        return str(cand)
    raise SystemExit("Rscript not found; pass --rscript")


def stage(rdata_dir: Path, force: bool) -> None:
    STAGING_IN.mkdir(parents=True, exist_ok=True)
    for name in NEEDED:
        src = rdata_dir / name
        dst = STAGING_IN / name
        if not src.exists():
            raise SystemExit(f"missing raw file: {src}")
        if force or not dst.exists() or dst.stat().st_size != src.stat().st_size:
            print(f"[stage] copying {name} ({src.stat().st_size / 1e6:.0f} MB)")
            shutil.copy2(src, dst)
        else:
            print(f"[stage] cached {name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rdata-dir", type=Path, default=DEFAULT_RDATA)
    ap.add_argument("--out", type=Path, default=ROOT / "data/raw/knhanes_frames_v2")
    ap.add_argument("--rscript", default=None)
    ap.add_argument("--staging", type=Path, default=None,
                    help="ASCII-only staging dir (default: <system temp>/huiyan_kn_staging)")
    ap.add_argument("--force-stage", action="store_true")
    ap.add_argument("--keep-staging", action="store_true")
    args = ap.parse_args()

    global STAGING_IN, STAGING_OUT
    if args.staging is not None:
        if any(ord(c) >= 128 for c in str(args.staging)):
            raise SystemExit(f"--staging must be ASCII-only (R limitation): {args.staging}")
        STAGING_IN = args.staging / "rdata"
        STAGING_OUT = args.staging / "out"

    rscript = args.rscript or find_rscript()
    print(f"[env] Rscript = {rscript}")
    print(f"[env] repo    = {ROOT}")
    print(f"[env] staging = {STAGING_IN.parent}")

    stage(args.rdata_dir, args.force_stage)
    STAGING_OUT.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["KN_DIR"] = str(STAGING_IN)
    env["KN_OUT"] = str(STAGING_OUT)
    env["PYTHONUTF8"] = "1"
    rscript_path = ROOT / "scripts" / "build_knhanes_frames.R"
    # R cannot read the Chinese repo path either -> copy the script to staging
    staged_script = STAGING_OUT / "build_knhanes_frames.R"
    shutil.copy2(rscript_path, staged_script)

    print("[run] Rscript build_knhanes_frames.R")
    proc = subprocess.run([rscript, "--vanilla", str(staged_script)],
                          env=env, capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    sys.stdout.write(proc.stdout or "")
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        print(f"[fail] Rscript exit={proc.returncode}")
        return proc.returncode

    args.out.mkdir(parents=True, exist_ok=True)
    moved = 0
    for f in sorted(STAGING_OUT.glob("knhanes_*.csv")) + \
             sorted(STAGING_OUT.glob("build_report.csv")) + \
             sorted(STAGING_OUT.glob("codebook_used.csv")):
        shutil.copy2(f, args.out / f.name)
        moved += 1
    print(f"[done] {moved} files -> {args.out}")

    if not args.keep_staging and STAGING_OUT.exists():
        for f in STAGING_OUT.iterdir():
            f.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
