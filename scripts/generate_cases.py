#!/usr/bin/env python
"""生成各数据集的 cases.jsonl。

审核 150 / WO-25：本脚本此前只统计每个 cases.jsonl 的行数并 `return 0`——
四个文件都是 0 字节，脚本却报"成功"。
审核 100 / WO-22：确证管线必须真正消费 cases.jsonl，因此本脚本是前置阻塞项。

实现验收标准（WO-22）：
  - 从实体注册表 + 规则生成 cases.jsonl（每行含 provenance：变量映射/纳入排除/每步 N）
  - 生成后校验非空，空则非零退出
  - evaluate.py 在 cases.jsonl 缺失或为空时抛错（当前完全无 I/O）
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = [
    "dev-exposure-disease-pairs",
    "intval-nhanes",
    "extval-knhanes",
    "extval-cohorts-9",
]


def main() -> int:
    lines = ["[cases] 尚未实现：未生成任何 case。当前四个 cases.jsonl 均为 0 字节。"]
    for ds in DATASETS:
        p = ROOT / "data" / "datasets" / ds / "cases.jsonl"
        n = sum(1 for _ in p.open(encoding="utf-8")) if p.exists() else 0
        lines.append(f"  {ds}: {n} cases")
    sys.stderr.write("\n".join(lines) + "\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
