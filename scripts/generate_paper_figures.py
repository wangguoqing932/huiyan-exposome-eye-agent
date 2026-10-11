#!/usr/bin/env python
"""按图件契约渲染 5 张论文图。

审核 150 / WO-25：本脚本此前只数 source_data 目录下的 CSV 个数并 `return 0`
（且用 chr() 拼接字面量，规避了基于文本的桩函数检测）。

实现验收标准（WO-24）：读取 outputs/figures/contracts/figure{1..5}_*.yaml，
以 outputs/figures/source_data/figure{1..5}_*.csv 为数据源渲染图，
产出 outputs/figures/ 下的 png/pdf。当前 source_data 全部是占位行。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    sd = ROOT / "outputs" / "figures" / "source_data"
    csvs = sorted(p.name for p in sd.glob("*.csv"))
    sys.stderr.write(
        f"[figures] 尚未实现：未渲染任何图。source_data 现有 {len(csvs)} 个 CSV：\n"
        + "".join(f"  {n}\n" for n in csvs)
        + "  当前内容均为占位行 placeholder,pending,confirmatory_run。\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
