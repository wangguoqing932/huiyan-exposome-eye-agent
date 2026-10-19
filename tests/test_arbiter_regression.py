# -*- coding: utf-8 -*-
"""Arbiter-layer regression test (opt-in).

The rule layer has always had a determinism test. The arbiter layer had none,
which is why three wording variants of the same JSON field list could move one
pair from "high once in twelve" to "high six times in six" to "high never in
twelve" without anything failing.

This wrapper exists so the check is discoverable from `pytest tests/`, but it is
skipped by default: it makes about thirty LLM calls and needs network access,
while the rest of the suite runs in well under a second.

Run it explicitly:

    ARBITER_REGRESSION=1 python -m pytest tests/test_arbiter_regression.py -q

Re-record the baseline after a deliberate prompt or model change:

    python scripts/arbiter_regression.py --update
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

pytestmark = pytest.mark.skipif(
    os.getenv("ARBITER_REGRESSION") != "1",
    reason="opt-in: makes ~30 LLM calls; set ARBITER_REGRESSION=1 to run",
)


def test_rule_layer_invariant_and_arbiter_within_tolerance():
    import arbiter_regression as ar

    base_path = ROOT / "tests" / "data" / "arbiter_baseline.json"
    assert base_path.exists(), (
        "no baseline; record one with: python scripts/arbiter_regression.py --update")

    cur = ar.collect(ar.REPEATS)
    base = json.loads(base_path.read_text(encoding="utf-8"))
    problems = ar.compare(cur, base, tolerance=0.34)

    # Report every probe, not just the failures, so a passing run still shows
    # what the arbiter actually did.
    for key, v in cur["probes"].items():
        print(f"{key:52s} tiers={v['tiers']} rule={v['rule_tiers']} "
              f"conf={v['arbiter_conf']}")
    assert not problems, "arbiter regression:\n  " + "\n  ".join(problems)
