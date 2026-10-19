#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fetch the target journal's author guidelines for writer phase 7_9.

Phase 7_9 requires the journal's requirements to be fetched ONLINE at packaging
time, with a snapshot recording URL, access date and the key limits. The earlier
attempt recorded a bare 403 and fell back to the static checklist, which is
allowed only when the site is genuinely unreachable -- a policy denial is not the
same thing as an unreachable site.

The family's own infrastructure note (medical-agent/references/network_and_proxy.md)
documents two things this script applies:

  * Python does NOT inherit the system proxy, so a ProxyHandler is required. A
    bare urllib call without it can fail for reasons that have nothing to do with
    the site, which is exactly how a "the site is down" conclusion gets reached
    wrongly.
  * aaojournal.org returns 403 through Cloudflare EVEN VIA THE PROXY. So if the
    target is the AAO journal, the fallback is legitimate and must be recorded as
    a documented limitation rather than as a transient error.

This script probes the proxy, then tries each candidate URL in order and reports
what actually happened for each, so the snapshot can say which source was reached
and which was refused.

Run: python scripts/fetch_journal_guidelines.py
"""
from __future__ import annotations

import json
import re
import socket
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "submission" / "journal_guidelines_snapshot.md"
CACHE = ROOT / "outputs" / "submission" / "_journal_pages"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

PROXY_PORTS = (7897, 7890, 10809)

SOURCES = [
    ("Ophthalmology — Elsevier guide for authors",
     "https://www.elsevier.com/journals/ophthalmology/0161-6420/guide-for-authors"),
    ("Ophthalmology — ScienceDirect guide for authors",
     "https://www.sciencedirect.com/journal/ophthalmology/publish/guide-for-authors"),
    ("Ophthalmology — AAO journal author information",
     "https://www.aaojournal.org/content/authorinfo"),
    ("Ophthalmology — AAO journal instructions",
     "https://www.aaojournal.org/content/instructions-for-authors"),
]


def find_proxy() -> str | None:
    for p in PROXY_PORTS:
        s = socket.socket()
        s.settimeout(1.5)
        try:
            if s.connect_ex(("127.0.0.1", p)) == 0:
                return f"http://127.0.0.1:{p}"
        finally:
            s.close()
    return None


def fetch(url: str, proxy: str | None) -> tuple[str, str, str]:
    """Return (status, detail, body_head)."""
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy,
                                                     "https": proxy}))
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers=UA)
    try:
        with opener.open(req, timeout=45) as r:
            head = r.read(4096)
            return (f"HTTP {r.status}", r.headers.get("Content-Type", "?"),
                    head.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return (f"HTTP {e.code}", e.reason or "", "")
    except Exception as e:
        return (type(e).__name__, str(e)[:120], "")


LIMIT_PATTERNS = {
    "abstract": r"(?:abstract|structured abstract)[^.\n]{0,80}?"
                r"(\d{2,4})\s*words",
    "main text": r"(?:main text|manuscript|word limit|maximum of)"
                 r"[^.\n]{0,60}?(\d{2,4}[,.]?\d{0,3})\s*words",
    "references": r"(?:references|bibliography)[^.\n]{0,60}?"
                  r"(\d{1,4})\s*(?:references|refs)",
    "figures/tables": r"(?:figures?|tables?)[^.\n]{0,60}?(\d{1,3})\s*"
                      r"(?:figures?|tables?)",
}


def extract(body: str) -> dict[str, str]:
    text = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    out = {}
    for k, pat in LIMIT_PATTERNS.items():
        m = re.search(pat, text, re.I)
        if m:
            out[k] = m.group(1)
    return out


def main() -> int:
    proxy = find_proxy()
    print(f"proxy: {proxy or 'NOT RUNNING on any of ' + str(PROXY_PORTS)}")
    CACHE.mkdir(parents=True, exist_ok=True)
    results = []
    for label, url in SOURCES:
        status, detail, head = fetch(url, proxy)
        ok = status.startswith("HTTP 2")
        results.append({"label": label, "url": url, "status": status,
                        "detail": detail, "reached": ok,
                        "limits": extract(head) if ok else {}})
        print(f"  {status:>16s}  {label}")
        if ok:
            (CACHE / (re.sub(r'\W+', '_', label)[:50] + ".html")).write_text(
                head, encoding="utf-8")

    reached = [r for r in results if r["reached"]]
    lines = [
        "# Journal guidelines snapshot (writer phase 7_9)",
        "",
        f"**Access date:** {date.today().isoformat()}  ",
        f"**Proxy:** {proxy or 'none detected on ' + str(PROXY_PORTS)}  ",
        "**Target journal:** Ophthalmology (ISSN 0161-6420), "
        "per `.planner.config.json` → `project.target_journal_primary`",
        "",
        "## What was attempted",
        "",
        "| Source | Result |",
        "|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['label']} | {r['status']}"
                     + (f" ({r['detail']})" if r["detail"] else "") + " |")
    lines += [
        "",
        "## Outcome",
        "",
    ]
    if reached:
        lines += ["At least one source was reached; extracted limits:", ""]
        for r in reached:
            lines.append(f"* **{r['label']}** → {r['limits'] or 'no numeric limit matched'}")
        lines += ["", "**Verify these against the page before relying on them** — "
                  "they are regex extractions from a partial fetch, not a reading."]
    else:
        lines += [
            "**No source was reachable.** This is a documented limitation, not a "
            "transient failure: `medical-agent/references/network_and_proxy.md` "
            "records that `aaojournal.org` returns 403 through Cloudflare even via "
            "the proxy, and the Elsevier/ScienceDirect guide pages did not "
            "respond either.",
            "",
            "**Fallback applied** (per the skill's phase 7_9 instruction): the "
            "package is validated against the static "
            "`medical-agent-writer/references/submission_checklists.md` instead, "
            "and **this snapshot does not assert any numeric limit** — the "
            "project cannot state the journal's word or figure caps from an "
            "authoritative source.",
            "",
            "**Consequence for the author:** the limits must be checked by hand "
            "against the real guidelines in one pass before upload. Anything "
            "derived from the static checklist is a general norm, not this "
            "journal's rule.",
        ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nreached: {len(reached)} of {len(results)}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
