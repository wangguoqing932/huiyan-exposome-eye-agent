#!/usr/bin/env python
"""4 基线 × 5 seeds 对比。

审核 150 / WO-25：本脚本此前只打印一行摘要并 `return 0`。
退出码 0 会被编排与状态机记为"成功"，因此比显式未实现更危险。
真正实现前一律以非零退出码失败。

实现验收标准（WO-25）：
  - 4 个基线各按 seeds [11,22,33,44,55] 运行
  - 写出 outputs/baseline_predictions.jsonl（4 基线 × 5 seeds × N 数据集）
  - lightrag / full_system 两个基线需要已构建的 LightRAG 索引
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

SEEDS = [11, 22, 33, 44, 55]


def main() -> int:
    sys.stderr.write(
        "[baselines] 尚未实现：未运行任何基线，未写出 outputs/baseline_predictions.jsonl。\n"
        f"  预注册 seeds: {SEEDS}\n"
        "  注意：当前 .venv 缺 statsmodels，且 data/processed/lightrag_index/ 不存在，\n"
        "  因此 lightrag / full_system 两个基线在环境补齐前不可能运行。\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
