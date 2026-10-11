#!/usr/bin/env python
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def main():
    out=ROOT/"outputs"/"tables"
    for f in ["registry_summary.csv","rule_list.csv","performance_matrix.csv","validation_distribution.csv","dataset_summary.csv","performance_by_dataset.csv"]:
        print(f"[tables] {f}: {(chr(10004) if (out/f).exists() else chr(10008))}")
    return 0
if __name__=="__main__": sys.exit(main())
