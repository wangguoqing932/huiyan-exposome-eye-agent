#!/usr/bin/env python
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def main():
    sd=ROOT/"outputs"/"figures"/"source_data"
    print(f"[figures] {len(list(sd.glob(chr(42)+chr(46)+chr(99)+chr(115)+chr(118))))} source CSVs")
    return 0
if __name__=="__main__": sys.exit(main())
