#!/usr/bin/env python
import sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"src"))
def main():
    from huiyan_agent.normalize import resolve_entity_a,resolve_entity_b
    from huiyan_agent.risk_rules import load_rules,match_rules,assess
    rules=load_rules()
    for aid,bid in [("current_smoking","amd_late"),("hba1c_elevated","retinopathy_any"),("blood_mercury","cataract_any")]:
        a=resolve_entity_a(aid); b=resolve_entity_b(bid)
        if not a or not b: continue
        sigs=match_rules(rules,a,b); r=assess(sigs)
        print(f"[demo] {a.primary_name} x {b.generic_name}: {r.risk_level.value} ({len(sigs)} sigs)")
    return 0
if __name__=="__main__": sys.exit(main())
