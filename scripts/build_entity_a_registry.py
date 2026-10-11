#!/usr/bin/env python
"""Build Entity A registry. B9 fix."""
import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/"data"/"seed"/"entities_a.csv"
def main():
    rows=list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    flags=set()
    for r in rows: flags.update(f.strip() for f in r.get("flags","").split(";") if f.strip())
    print(f"[build_a] {len(rows)} exposures, {len(flags)} unique flags")
    return 0
if __name__=="__main__": sys.exit(main())
