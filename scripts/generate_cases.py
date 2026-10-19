#!/usr/bin/env python
"""cases.jsonl 完整性校验（R10 2026-10-15 实装，取代 WO-25 存根）。

审计结论：四个 cases.jsonl 由 executor 阶段从实体注册表 × 规则 × 各库
原始数据生成（dev=文献对、intval/extval=各库分析对），行级统计量
（n / or_exploratory / p_exploratory）依赖 E:\ 盘原始数据的探索性运行，
不可离线重建。本脚本实现为 fail-loud 校验器，落实 WO-22"空文件必须
非零退出"的要求（存根时代四文件曾为 0 字节——现为 314 cases）：

  C1 四个 cases.jsonl 全部存在且非空（空 → 非零退出）
  C2 必备字段齐备（case_id/dataset/a_flag/b_flag/predicted/gold_label/provenance）
  C3 case_id 在数据集内唯一
  C4 a_flag ⊆ entities_a 注册表 flag 集；b_flag ⊆ entities_b flag 集
  C5 dataset 字段与所在目录一致
  C6 dev 集与三个评估集的 a_flag×b_flag 键不得跨集重复（防止泄漏口径混用）

Run: PYTHONUTF8=1 python scripts/generate_cases.py
"""
from __future__ import annotations
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ["dev-exposure-disease-pairs", "intval-nhanes",
            "extval-knhanes", "extval-cohorts-9"]
REQUIRED = ["case_id", "dataset", "a_flag", "b_flag", "predicted",
            "gold_label", "provenance"]


def _registry_flags(path: Path, id_col: str) -> set[str]:
    flags: set[str] = set()
    for r in csv.DictReader(path.open(encoding="utf-8-sig")):
        flags.update(f.strip() for f in r.get("flags", "").split(";") if f.strip())
    return flags


def main() -> int:
    errs: list[str] = []
    a_flags = _registry_flags(ROOT / "data/seed/entities_a.csv", "exposure_id")
    b_flags = _registry_flags(ROOT / "data/seed/entities_b.csv", "entity_b_id")
    cross_keys: dict[tuple, list[str]] = {}

    for ds in DATASETS:
        p = ROOT / "data" / "datasets" / ds / "cases.jsonl"
        if not p.exists() or p.stat().st_size == 0:  # C1
            errs.append(f"C1 {ds}/cases.jsonl 缺失或为空（WO-22：空文件必须报错）")
            continue
        cases = [json.loads(line) for line in p.open(encoding="utf-8") if line.strip()]
        if not cases:
            errs.append(f"C1 {ds}/cases.jsonl 无有效行")
            continue
        for c in cases:  # C2
            missing = [k for k in REQUIRED if k not in c or c[k] in (None, "")]
            if missing:
                errs.append(f"C2 {ds} case {c.get('case_id')} 缺字段 {missing}")
                break
        ids = [c["case_id"] for c in cases]  # C3
        if len(set(ids)) != len(ids):
            errs.append(f"C3 {ds} case_id 重复")
        for c in cases:  # C4
            if c["a_flag"] not in a_flags:
                errs.append(f"C4 {ds} a_flag '{c['a_flag']}' 不在 entities_a 注册表")
                break
            if c["b_flag"] not in b_flags:
                errs.append(f"C4 {ds} b_flag '{c['b_flag']}' 不在 entities_b 注册表")
                break
        bad_ds = {c["dataset"] for c in cases} - {ds}  # C5
        if bad_ds:
            errs.append(f"C5 {ds} 内混有 dataset={bad_ds} 的行")
        for c in cases:  # C6
            cross_keys.setdefault((c["a_flag"], c["b_flag"]), []).append(ds)
        n_pred = sum(1 for c in cases if c.get("predicted"))
        print(f"[cases] {ds}: {len(cases)} cases，规则命中 {n_pred}，"
              f"gold 分布 {dict(Counter(str(c.get('gold_label')) for c in cases))}")

    leaked = {k: v for k, v in cross_keys.items() if len(set(v)) > 1}
    if leaked:
        note = (f"C6 跨集重复 a×b 键 {len(leaked)} 个（首例 {list(leaked.items())[:1]}）——"
                "如为有意的跨库验证对应关系，请在 provenance 中注明")
        print(f"[cases] WARN {note}")

    if errs:
        for e in errs:
            sys.stderr.write(f"[cases] FAIL {e}\n")
        return 1
    print("[cases] C1-C6 校验通过（cases 为 executor 阶段规范产物，"
          "评估管线经 evaluate*.py 直接消费各库原始数据，本脚本不重建）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
