# G3 / G4 / G5 code paths — archived, not deleted

Per `AGENT_V2_MUSTFIX_2026-10-16.md` **M8 (禁止)**: stop investing in
retrieval / embedding / prompt / arbiter enhancements, and archive or delete the
G3/G4/G5 code paths. The negative results are kept here rather than discarded.

## What was archived

| File | Variant | Result |
|---|---|---|
| `run_fused_system_v2.py` | G3, G4 | G3 was a no-op; G4 was **harmful** (0.500 → 0.417) |
| `run_fused_system_v3.py` | G5a, G5b | G5a no gain; G5b never triggered |

Evidence (E6): G2 vs G0 p = 0.50; the retrieval layer is not the bottleneck.

## Why archive rather than delete

The instruction allows either. Archiving was chosen because these files are the
only executable record of the negative results, and a negative result that cannot
be re-run tends to get re-attempted. Anyone reaching this directory can run them
again and see for themselves.

## Why this is safe

Verified before moving: no script imports them. The only references anywhere in
the tree were each file's own `Usage:` docstring line, and the default pipeline
(`scripts/run_all.py`, `scripts/evaluate.py`) does not mention them.

## What is NOT allowed now

Any performance claim for a modified pipeline must come from the M1 evaluation
surface. Reporting an "improvement" against the old 80-pair gold set is
forbidden — that set has five informative pairs and cannot resolve architecture
differences.
