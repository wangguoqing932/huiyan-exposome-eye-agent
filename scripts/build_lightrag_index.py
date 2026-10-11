#!/usr/bin/env python
import sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"src"))
os.environ.setdefault("PYTHONUTF8","1")
from dotenv import load_dotenv
load_dotenv(ROOT/".env")
def main():
    from huiyan_agent.lightrag_adapter import LightRAGAdapter
    a=LightRAGAdapter()
    stats=a.build_from_jsonl(str(ROOT/"data"/"seed"/"evidence_chunks.jsonl"))
    print(f"[lightrag] {stats}")
    return 0
if __name__=="__main__": sys.exit(main())
