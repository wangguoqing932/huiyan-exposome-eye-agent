#!/usr/bin/env python
"""多种子稳定性运行。

审核 150 / WO-25：本脚本此前只打印一行摘要并 `return 0`（静默成功）。
真正实现前一律以非零退出码失败。

实现验收标准（WO-25）：对每个数据集按 seeds [11,22,33,44,55] 重复确证管线，
输出各指标的 mean ± std（对应 performance_by_dataset.csv 的 mean/std/n_seeds 列）。
"""
import sys

SEEDS = [11, 22, 33, 44, 55]


def main() -> int:
    sys.stderr.write(
        "[multiseed] 尚未实现：未运行任何种子，未产出 mean/std/n_seeds。\n"
        f"  预注册 seeds: {SEEDS}\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
