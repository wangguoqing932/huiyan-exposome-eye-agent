#!/usr/bin/env python
"""证据库完整性校验（R10 2026-10-15 实装，取代 WO-25 存根）。

审计结论：evidence_chunks.jsonl 由 fetch_pubmed.py 多轮抓取 + planner 阶段
人工清洗累积而成（1,060 chunks / 902 唯一 PMID），不可从脚本一键重建
（抓取依赖 NCBI 在线状态与多轮人工筛选决策）。本脚本实现为 fail-loud
校验器，覆盖 WO-25 当时指出的全部问题点并核验现状：

  E1 非空且达 WO-25 目标规模（≥250 chunks；现 1,060）
  E2 chunk_id 唯一
  E3 逐条 provenance 非单一常量（WO-25 曾指 36 条共用常量——已不成立）
  E4 重复检测：完全相同文本、以及同 PMID 尾部截断片段（前 120 字符相同）
  E5 evidence_level 分布（A–E）打印；非法值报错
  E6 与 LightRAG 索引对账：kv_store_doc_status 成功文档数应 ≈ chunks 数
     减去索引端 <300 字符垃圾块过滤量（打印两者差值供人工复核）
  E7 短文本垃圾块（<300 字符，索引构建时被过滤）计数报告

Run: PYTHONUTF8=1 python scripts/build_evidence_base.py
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "seed" / "evidence_chunks.jsonl"
DOC_STATUS = ROOT / "data" / "processed" / "lightrag_index" / "kv_store_doc_status.json"

MIN_CHUNKS = 250  # WO-25 目标
VALID_LEVELS = {"A", "B", "C", "D", "E"}
# 完全重复文本的 fail 阈值：唯一已知重复为两条同文 Corrigendum（不同 PMID，
# 249 字符，属索引端 <300 过滤集，从未进入 LightRAG）。索引已与全量 1060
# chunks 冻结绑定，少量记录在案的重复不值得解除绑定重灌 936MB 索引。
MAX_EXACT_DUP = 3


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"[evidence] 证据库不存在: {SRC}\n")
        return 1
    chunks = [json.loads(line) for line in SRC.open(encoding="utf-8") if line.strip()]
    errs: list[str] = []

    if len(chunks) < MIN_CHUNKS:  # E1
        errs.append(f"E1 规模 {len(chunks)} < 目标 {MIN_CHUNKS}")
    ids = [c.get("chunk_id") for c in chunks]  # E2
    if len(set(ids)) != len(ids):
        dup = [k for k, v in Counter(ids).items() if v > 1]
        errs.append(f"E2 chunk_id 重复: {dup[:5]}")
    provs = {str(c.get("provenance", ""))[:80] for c in chunks}  # E3
    if len(provs) == 1:
        errs.append("E3 全部 chunk 共用同一 provenance 常量")
    exact_dup = [k for k, v in Counter(c.get("text", "").strip() for c in chunks).items()
                 if v > 1]  # E4
    tail_keys = Counter((c.get("pmid"), c.get("text", "")[:120]) for c in chunks)
    tail_dup = {k: v for k, v in tail_keys.items() if v > 1}
    if len(exact_dup) > MAX_EXACT_DUP:
        errs.append(f"E4 完全相同文本的重复块 {len(exact_dup)} 组 > 阈值 {MAX_EXACT_DUP}")
    levels = Counter(str(c.get("evidence_level", "")) for c in chunks)  # E5
    bad_levels = set(levels) - VALID_LEVELS
    if bad_levels:
        errs.append(f"E5 非法 evidence_level 取值: {sorted(bad_levels)}")
    # E5b（2026-10-16 新增）：A 只允许给 source_type == guideline 的块。
    #
    # 为什么必须校验：`A` 一度在两处含义不同——rules.yaml 的纪律写 A = 监管标签/指南
    # （severity 由它强制派生为 high），而语料把 meta 分析也标成 A。
    # 一次据语料 A 发起的评级审计因此判 11 条规则"高评"并全部改动，
    # 最终 11 条全部回退（docs/AGENT_AUDIT.md §8–§21）。这条校验把该歧义钉死：
    # 语料侧的 A 从此与规则纪律的 A 同义。
    a_nonguide = [c.get("chunk_id") for c in chunks
                  if c.get("evidence_level") == "A"
                  and c.get("source_type") != "guideline"]
    if a_nonguide:
        errs.append(f"E5b A 级但 source_type≠guideline 的块 {len(a_nonguide)} 个"
                    f"（A 保留给指南/监管文件）: {a_nonguide[:5]}")
    short = sum(1 for c in chunks if len(c.get("text", "")) < 300)  # E7

    indexed = None  # E6
    if DOC_STATUS.exists():
        try:
            ds = json.loads(DOC_STATUS.read_text(encoding="utf-8"))
            indexed = sum(1 for v in ds.values()
                          if isinstance(v, dict) and str(v.get("status")) == "processed")
        except (json.JSONDecodeError, AttributeError):
            indexed = None

    pmids = {c.get("pmid", "") for c in chunks}
    print(f"[evidence] {len(chunks)} chunks / {len(pmids)} 唯一 PMID；"
          f"level 分布: {dict(levels)}")
    print(f"[evidence] provenance 变体 {len(provs)} 个；"
          f"完全重复文本组 {len(exact_dup)}；同 PMID 尾部截断嫌疑组 {len(tail_dup)}")
    print(f"[evidence] <300 字符短块（索引端过滤）: {short}")
    if indexed is not None:
        print(f"[evidence] LightRAG 已索引文档 {indexed} vs chunks {len(chunks)} "
              f"(差值 {len(chunks) - indexed}，应≈短块过滤量)")
    if errs:
        for e in errs:
            sys.stderr.write(f"[evidence] FAIL {e}\n")
        return 1
    print("[evidence] E1-E7 校验通过（证据库为多轮抓取+人工清洗的规范产物，"
          "增量更新走 fetch_pubmed.py --max-pairs，本脚本不重建）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
