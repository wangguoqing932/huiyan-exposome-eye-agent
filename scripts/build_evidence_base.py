#!/usr/bin/env python
"""证据库构建。

审核 150 / WO-25：本脚本名为 build_*，但只读取 data/seed/evidence_chunks.jsonl
并打印统计，然后 return 0——从未写出任何产物。

实现验收标准（WO-25）：
  - 按检索式抓取并构建证据块，写入逐条可复现的 provenance
    （当前 36 条的 provenance 是同一个常量，不含检索式/参数）
  - 去重：现有 6 组重复来源（12/36 = 33% 是同一文献的截断尾部片段）
  - 目标 250+ 条；当前 36 条
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "evidence_chunks.jsonl"


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[evidence] 证据库不存在: {SRC}\n")
        return 1
    chunks = [json.loads(line) for line in SRC.open(encoding="utf-8") if line.strip()]
    pmids = {c.get("pmid", "") for c in chunks}
    sys.stderr.write(
        f"[evidence] 尚未实现：只读诊断，未写出任何产物。\n"
        f"  现有 {len(chunks)} chunks / {len(pmids)} 唯一 PMID / 目标 250+。\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
