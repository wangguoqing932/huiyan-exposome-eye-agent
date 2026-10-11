#!/usr/bin/env python
import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/"data"/"seed"/"entities_b.csv"
def main():
    rows=list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    ns=[r["entity_b_id"] for r in rows if "无源" in r.get("judged_in","")]
    print(f"[build_b] {len(rows)} items, no-source: {ns}")
    return 0
if __name__=="__main__": sys.exit(main())
