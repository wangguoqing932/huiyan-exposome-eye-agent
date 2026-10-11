#!/usr/bin/env python
"""Entity A（暴露）注册表构建。

审核 150 / WO-25：本脚本名为 build_*，但**从未写出任何产物**——
只读取 data/seed/entities_a.csv 并打印统计，然后 return 0。
退出码 0 会被编排记为"成功"，这正是审核 150 指出的静默成功模式。

实现验收标准（WO-25）：
  - 从原始数据源（NHANES/KNHANES 变量字典）生成 entities_a.csv，而非读它
  - 每行写入可核验的 evidence_sources 与派生算法（当前 12 行标注"预注册算法"但无算法正文）
  - 校验 flags 与校验和，不一致时非零退出
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "entities_a.csv"


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[build_a] 注册表不存在: {SRC}\n")
        return 1
    rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    flags = set()
    for r in rows:
        flags.update(f.strip() for f in r.get("flags", "").split(";") if f.strip())
    sys.stderr.write(
        f"[build_a] 尚未实现：只读诊断，未写出任何产物。\n"
        f"  现有 {len(rows)} 行暴露，{len(flags)} 个唯一 flag（名不副实：{len(rows)} 行 → {len(flags)} flag）。\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
