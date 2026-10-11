#!/usr/bin/env python
"""Entity B（眼病结局）注册表构建。

审核 150 / WO-25：本脚本名为 build_*，但只读取 data/seed/entities_b.csv 并打印
无源条目，然后 return 0——从未写出任何产物。

实现验收标准（WO-25）：
  - 从各库变量字典生成 entities_b.csv
  - `judged_in` 必须写成机器可解析形式（审核 101：现为中文散文，
    normalize.py:87-88 按 "1/true/yes/y" 解析 → 15/15 全为 False 且无人读取）
  - 补齐 schemas.EntityB 期望的 pathology / grading_source 两列
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "entities_b.csv"


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[build_b] 注册表不存在: {SRC}\n")
        return 1
    rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    no_source = [r["entity_b_id"] for r in rows if "无源" in r.get("judged_in", "")]
    sys.stderr.write(
        f"[build_b] 尚未实现：只读诊断，未写出任何产物。\n"
        f"  现有 {len(rows)} 条结局；声明为无源可判的: {no_source}\n"
        f"  judged_in 目前是散文，运行期全部解析为 False（审核 101）。\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
