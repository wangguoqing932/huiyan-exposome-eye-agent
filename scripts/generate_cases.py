#!/usr/bin/env python
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def main():
    for ds in ["dev-exposure-disease-pairs","intval-nhanes","extval-knhanes","extval-cohorts-9"]:
        p=ROOT/"data"/"datasets"/ds/"cases.jsonl"
        n=sum(1 for _ in p.open()) if p.exists() else 0
        print(f"[cases] {ds}: {n} cases")
    return 0
if __name__=="__main__": sys.exit(main())
