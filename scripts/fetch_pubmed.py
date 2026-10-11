#!/usr/bin/env python
"""PubMed 摘要抓取（证据库扩容）。

审核 150 / WO-25：`fetch()` 是真实实现，但 `main()` 只打印一行并 `return 0`，
从未抓取任何记录——证据库因此停在 36 条（目标 250+）。

实现验收标准（WO-25）：
  - main() 按检索式批量抓取并**追加**到 data/seed/evidence_chunks.jsonl
  - 每条记录写入可复现的 provenance（检索式/日期/参数），当前 36 条全部是
    同一个常量字符串 "PubMed efetch 2026-10-11 huiyan phase2"，不可复现
  - 抓取结果为 0 条时必须非零退出
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fetch(pmid: str, key: str = ""):
    """按 PMID 取 PubMed XML（保留原实现）。失败返回 None。"""
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pubmed&id={pmid}&retmode=xml"
    )
    if key:
        url += f"&api_key={key}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "huiyan/1.0"})
        return urllib.request.urlopen(req, timeout=30).read().decode()
    except Exception:
        return None


def main() -> int:
    sys.stderr.write(
        "[fetch] 尚未实现：未抓取任何记录（fetch() 可用但 main() 未调用它）。\n"
        "  证据库当前 36 条，目标 250+。\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
