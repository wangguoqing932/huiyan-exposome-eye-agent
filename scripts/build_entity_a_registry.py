#!/usr/bin/env python
"""Entity A（暴露）注册表完整性校验（R10 2026-10-15 实装）。

审计结论：entities_a.csv 是 planner 阶段人工+变量字典整理的**规范产物**，
其行级内容（别名/机制/证据来源）不存在于仓库任何机器可读源中——
伪造"重建器"只会产生编造数据。故本脚本实现为 fail-loud 校验器：
注册表与仓库内全部下游消费者（.planner.config.json、configs/rules.yaml）
交叉核验，不一致即非零退出。

校验项：
  A1 行数 == planner entities.a.target_count
  A2 唯一 flag 集合 == planner entities.a.example_flags
  A3 exposure_id 唯一、primary_name 非空
  A4 rules.yaml 全部 entity_a_flag ⊆ 注册表 flag 集
  A5 category 非空且属于已知四域扩展集（打印分布供人工复核）

Run: PYTHONUTF8=1 python scripts/build_entity_a_registry.py
"""
from __future__ import annotations
import ast
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "entities_a.csv"

KNOWN_CATEGORIES = {
    "anthropometric", "dietary", "dietary_pattern", "environment_air",
    "environment_metal", "environment_physical", "inflammation_serum",
    "lifestyle", "lipid_serum", "metabolic_serum", "vitamin_serum",
}


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[check_a] 注册表不存在: {SRC}\n")
        return 1
    rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    planner = json.loads((ROOT / ".planner.config.json").read_text(encoding="utf-8"))
    rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    rules = rules["rules"] if isinstance(rules, dict) and "rules" in rules else rules

    flags: set[str] = set()
    for r in rows:
        flags.update(f.strip() for f in r.get("flags", "").split(";") if f.strip())
    errs: list[str] = []

    target = planner["entities"]["a"]["target_count"]  # A1
    if len(rows) != target:
        errs.append(f"A1 行数 {len(rows)} != planner target_count {target}")
    planner_flags = set(planner["entities"]["a"]["example_flags"])  # A2
    if flags != planner_flags:
        errs.append(f"A2 flag 集合与 planner example_flags 不一致："
                    f"仅注册表有 {sorted(flags - planner_flags)}；"
                    f"仅 planner 有 {sorted(planner_flags - flags)}")
    ids = [r["exposure_id"] for r in rows]  # A3
    if len(set(ids)) != len(ids):
        errs.append("A3 exposure_id 重复")
    if any(not r.get("primary_name", "").strip() for r in rows):
        errs.append("A3 存在 primary_name 为空的行")
    rule_a_flags = set()  # A4
    for r in rules:
        rule_a_flags.update(ast.literal_eval(str(r["entity_a_flags"])))
    orphan = rule_a_flags - flags
    if orphan:
        errs.append(f"A4 rules.yaml 引用了注册表外的 A flag: {sorted(orphan)}")
    cats = {r.get("category", "").strip() for r in rows}  # A5
    bad_cats = {c for c in cats if c and c not in KNOWN_CATEGORIES}
    if bad_cats or "" in cats:
        errs.append(f"A5 未知/空 category: {sorted(bad_cats)}")

    dist = Counter(r.get("category", "") for r in rows)
    print(f"[check_a] {len(rows)} 行暴露 / {len(flags)} 个唯一 flag；"
          f"category 分布: {dict(dist)}")
    print(f"[check_a] rules.yaml 引用 A flag {len(rule_a_flags)} 个"
          f"{'，全部在注册表内' if not orphan else '，孤立: ' + str(sorted(orphan))}")
    if errs:
        for e in errs:
            sys.stderr.write(f"[check_a] FAIL {e}\n")
        return 1
    print("[check_a] A1-A5 全部通过（注册表为 planner 规范产物，本脚本只校验不重建）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
