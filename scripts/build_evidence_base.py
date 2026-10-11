#!/usr/bin/env python
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/"data"/"seed"/"evidence_chunks.jsonl"
def main():
    chunks=[json.loads(l) for l in SRC.open(encoding="utf-8")]
    pmids=set(c.get("pmid","") for c in chunks)
    print(f"[evidence] {len(chunks)} chunks / {len(pmids)} PMIDs / target 250+")
    return 0
if __name__=="__main__": sys.exit(main())
