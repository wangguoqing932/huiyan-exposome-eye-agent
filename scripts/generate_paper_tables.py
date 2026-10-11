#!/usr/bin/env python
"""生成 Executor 交付的 6 张表。

审核 150 / WO-25：本脚本此前只检查 6 个文件是否存在并 `return 0`
（且用 chr() 拼接字面量）——文件存在不等于内容合格。
审核 56 / WO-26：performance_by_dataset.csv 的表头与契约不符且 ci 列全空。

实现验收标准（WO-24/26）：
  - registry_summary.csv / rule_list.csv / performance_matrix.csv /
    validation_distribution.csv / dataset_summary.csv / performance_by_dataset.csv
  - performance_by_dataset.csv 表头须为
    dataset_id,dataset_role,method,metric,mean,std,n_cases,n_seeds，并含 gap_ 行
  - validate_handoff.py --transition executor-to-writer 返回 OK
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLES = [
    "registry_summary.csv",
    "rule_list.csv",
    "performance_matrix.csv",
    "validation_distribution.csv",
    "dataset_summary.csv",
    "performance_by_dataset.csv",
]


def main() -> int:
    out = ROOT / "outputs" / "tables"
    lines = ["[tables] 尚未实现：未生成或校验任何表内容。"]
    for f in TABLES:
        lines.append(f"  {f}: {'存在' if (out / f).exists() else '缺失'}")
    lines.append("  存在性不等于契约合规；请按 WO-24/26 校验表头与内容。")
    sys.stderr.write("\n".join(lines) + "\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
