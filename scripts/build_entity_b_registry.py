#!/usr/bin/env python
"""Entity B（眼病结局）注册表完整性校验（R10 2026-10-15 实装）。

审计结论：与 entities_a 同理，entities_b.csv 是 planner 阶段规范产物，
不可从仓库源重建。本脚本实现为 fail-loud 校验器。

校验项：
  B1 行数 == planner entities.b.target_count
  B2 唯一 flag 集合 == planner entities.b.example_flags
  B3 entity_b_id 唯一、generic_name 非空
  B4 rules.yaml 全部 entity_b_flag ⊆ 注册表 flag 集
  B5 三个布尔 judgeable 列（nhanes_/knhanes_/cohort_）取值仅 true/false
     且与运行期 get_judgeable_b_items 的解析约定一致（"true" 小写）；
     打印各库 judgeable 计数供人工复核（evaluate.py D5 修复的口径来源）
  B6 judged_in 为中文散文文档列：运行期不被消费（normalize.py:87-88 按
     1/true/yes/y 解析恒为 False，审核 101 已记录）——校验其存在并提示
     机器可判信息以 *_judgeable 布尔列为准，防止未来误用

Run: PYTHONUTF8=1 python scripts/build_entity_b_registry.py
"""
from __future__ import annotations
import ast
import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "entities_b.csv"


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[check_b] 注册表不存在: {SRC}\n")
        return 1
    rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    planner = json.loads((ROOT / ".planner.config.json").read_text(encoding="utf-8"))
    rules = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    rules = rules["rules"] if isinstance(rules, dict) and "rules" in rules else rules

    flags: set[str] = set()
    for r in rows:
        flags.update(f.strip() for f in r.get("flags", "").split(";") if f.strip())
    errs: list[str] = []

    target = planner["entities"]["b"]["target_count"]  # B1
    if len(rows) != target:
        errs.append(f"B1 行数 {len(rows)} != planner target_count {target}")
    planner_flags = set(planner["entities"]["b"]["example_flags"])  # B2
    if flags != planner_flags:
        errs.append(f"B2 flag 集合与 planner example_flags 不一致："
                    f"仅注册表有 {sorted(flags - planner_flags)}；"
                    f"仅 planner 有 {sorted(planner_flags - flags)}")
    ids = [r["entity_b_id"] for r in rows]  # B3
    if len(set(ids)) != len(ids):
        errs.append("B3 entity_b_id 重复")
    if any(not r.get("generic_name", "").strip() for r in rows):
        errs.append("B3 存在 generic_name 为空的行")
    rule_b_flags = set()  # B4
    for r in rules:
        rule_b_flags.update(ast.literal_eval(str(r["entity_b_flags"])))
    orphan = rule_b_flags - flags
    if orphan:
        errs.append(f"B4 rules.yaml 引用了注册表外的 B flag: {sorted(orphan)}")

    counts = {}  # B5
    for col in ("nhanes_judgeable", "knhanes_judgeable", "cohort_judgeable"):
        vals = {r.get(col, "").strip().lower() for r in rows}
        if not vals <= {"true", "false"}:
            errs.append(f"B5 {col} 存在非 true/false 取值: {sorted(vals)}")
        counts[col] = sum(1 for r in rows if r.get(col, "").strip().lower() == "true")
    if "judged_in" not in rows[0]:  # B6
        errs.append("B6 缺 judged_in 文档列")

    no_source = [r["entity_b_id"] for r in rows if "无源" in r.get("judged_in", "")]
    print(f"[check_b] {len(rows)} 条结局 / {len(flags)} 个唯一 flag；"
          f"各库 judgeable: {counts}")
    print(f"[check_b] judged_in 声明无源可判的（文档性信息）: {no_source or '无'}")
    print(f"[check_b] rules.yaml 引用 B flag {len(rule_b_flags)} 个"
          f"{'，全部在注册表内' if not orphan else '，孤立: ' + str(sorted(orphan))}")
    if errs:
        for e in errs:
            sys.stderr.write(f"[check_b] FAIL {e}\n")
        return 1
    print("[check_b] B1-B6 全部通过（机器可判口径以 *_judgeable 布尔列为准，"
          "judged_in 散文仅作文档；注册表为 planner 规范产物，本脚本只校验不重建）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
