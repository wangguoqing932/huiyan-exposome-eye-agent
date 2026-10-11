#!/usr/bin/env python
import sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"src"))
def main():
    print("[baselines] 4 baselines x 5 seeds (pre-registered: [11,22,33,44,55])")
    return 0
if __name__=="__main__": sys.exit(main())
