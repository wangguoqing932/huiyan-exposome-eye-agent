#!/usr/bin/env python
"""Turn ``[Cxxx]`` citation-pool markers into a Vancouver reference list.

The writer pipeline cites verified papers by their stable pool id
(``[C001]`` ... ``[C033]``) while a section is being drafted, and defers the
numeric renumbering to assembly time.  This script performs that step:

1. scan a Markdown file for bracket markers that contain one or more pool ids
   (``[C016]``, ``[C001, C002]``, ``[C001-C003]``), in document order;
2. keep only pool entries that are citable -- ``cross_verified`` and not
   retracted (writer citation discipline, kuku-paper-lookup Rules 3 and 4);
3. assign numbers ``1..N`` by first appearance (Vancouver / ICMJE sequential
   numbering) and replace every marker with its number(s);
4. render a ``# References`` section in Vancouver style, with a hidden HTML
   comment on each entry carrying the pool id so the mapping stays auditable;
5. by default (``--dry-run``) print statistics, the numbering map and sample
   entries and write nothing; ``--write`` writes a *new* file and refuses to
   overwrite the source manuscript.

Optional metadata enrichment
----------------------------
``citation_pool.json`` stores DOI/title/journal/year and (often) only the first
author.  Full author lists, volume, issue and pages live in the raw OpenAlex
responses under ``outputs/paper/citation_raw/openalex_*.json``.  When that
directory is available the script fills only the fields the pool lacks; the
pool always wins.  Nothing is invented: a field that is absent everywhere is
simply omitted from the reference and counted in the dry-run report.

Position in the pipeline
------------------------
Run this after Phase 7_8 has assembled the body (title, abstract, IMRaD,
declarations) and before the figure legends are appended -- or call
``assemble_with_references()`` from the 7_8 assembler.  ``# References`` belongs
after Declarations and before Figure Legends / Tables (ICMJE order).

Usage
-----
    python scripts/build_references.py --manuscript outputs/paper/manuscript.md
    python scripts/build_references.py --manuscript outputs/paper/manuscript.md \
        --write --out /tmp/manuscript.numbered.md \
        --references-out /tmp/references.md --audit-json /tmp/refs_audit.json

Exit codes
----------
0  success (dry-run validations passed, or file written)
2  hard failure: missing input, pool-external / non-citable citation, no
   markers, existing ``# References`` section, or unsafe output path
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

VERSION = "1.0.0"

# A marker is a bracket group made only of C-codes joined by commas,
# semicolons or dashes: [C001], [C001, C002], [C001-C003].
MARKER_RE = re.compile(
    r"\[(C\d{3}(?:\s*[-\u2013\u2014,;]\s*C\d{3})*)\]"
)
CODE_RE = re.compile(r"C\d{3}")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*\r?$", re.MULTILINE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
NUMERIC_MARKER_RE = re.compile(r"\[\d+(?:\s*[-,]\s*\d+)*\]")
BARE_CODE_RE = re.compile(r"(?<!\[)\bC\d{3}\b(?!\])")
DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)

FIGURE_HEADING_NAMES = ("figure legends", "figure legend")
TABLE_HEADING_RE = re.compile(r"^table\b", re.IGNORECASE)


class BuildError(Exception):
    """Expected failure; carries one message per problem for fail-loud output."""

    def __init__(self, problems: Iterable[str]):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #
def clean_text(value: object) -> str:
    """Unescape entities, drop HTML tags, normalise dashes and whitespace."""
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = HTML_TAG_RE.sub("", text)
    text = text.replace("\u2010", "-").replace("\u2011", "-")
    return WS_RE.sub(" ", text).strip()


def fold(value: str) -> str:
    """Case- and diacritic-insensitive key for matching names / headings."""
    decomposed = unicodedata.normalize("NFKD", value)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.casefold().strip()


def strip_doi_prefix(value: object) -> str:
    """Drop a resolver prefix but keep the DOI's original case for display."""
    if not value:
        return ""
    doi = DOI_PREFIX_RE.sub("", str(value).strip())
    return doi.strip().strip(".")


def normalize_doi(value: object) -> str:
    return strip_doi_prefix(value).lower()


def _looks_like_initials(token: str) -> bool:
    bare = token.replace(".", "")
    if not bare or len(bare) > 3:
        return False
    return token.endswith(".") or bare.isupper()


def _initials(given: str) -> str:
    parts = re.findall(r"[^\W\d_]+", given, flags=re.UNICODE)
    return "".join(part[0].upper() for part in parts if part)


def _render_author(family: str, given: str) -> str:
    family = clean_text(family)
    given = clean_text(given)
    if family.isupper() and len(family) > 3:
        family = family.title()
    initials = _initials(given)
    return f"{family} {initials}".strip() if initials else family


def _is_corporate(name: str) -> bool:
    """Corporate/group authorship must not be split into family + initials."""
    keywords = (
        "group", "consortium", "collaboration", "collaborators", "committee",
        "investigators", "team", "society", "organization", "organisation",
        "association", "network", "task force", "panel", "board", "foundation",
        "institute", "centers", "centres", "programme", "program", "collaborative",
    )
    lowered = f" {name.casefold()} "
    return any(f" {word} " in lowered or lowered.endswith(f" {word}s ")
               for word in keywords)


def format_author(name: str, *, family_first: bool = False) -> str:
    """Render one display name as ``Family Initials`` (Vancouver).

    ``family_first`` is for pool strings such as ``"Cohen Jérémie F"``; the
    default treats the last token as the family name (``"Jérémie F. Cohen"``),
    which is how OpenAlex usually stores display names.  Group authors are
    returned unchanged; pool strings are family-first, but some OpenAlex
    records are too, so the caller matches surnames before choosing.
    """
    name = clean_text(name)
    if not name:
        return ""
    if _is_corporate(name):
        return name
    if "," in name:  # "Smith, John"
        family, given = name.split(",", 1)
        return _render_author(family, given)
    tokens = name.split()
    if len(tokens) == 1:
        return _render_author(tokens[0], "")
    if family_first:
        return _render_author(tokens[0], " ".join(tokens[1:]))
    if _looks_like_initials(tokens[-1]):
        return _render_author(tokens[0], " ".join(tokens[1:]))
    return _render_author(tokens[-1], " ".join(tokens[:-1]))


def _families_match(pool_name: str, oa_name: str) -> bool:
    """True when the pool author and the OpenAlex author share a surname.

    OpenAlex display names are inconsistent about name order, so the pool's
    family name (first token) is compared with both ends of the OpenAlex name.
    """
    pool_name, oa_name = clean_text(pool_name), clean_text(oa_name)
    if not pool_name or not oa_name:
        return False
    pool_family = pool_name.replace(",", " ").split()[0]
    tokens = oa_name.replace(",", " ").split()
    if not tokens:
        return False
    candidates = {fold(tokens[0]), fold(tokens[-1])}
    return fold(pool_family) in candidates


# --------------------------------------------------------------------------- #
# data model
# --------------------------------------------------------------------------- #
@dataclass
class Enrichment:
    authors: list[str] = field(default_factory=list)
    volume: str = ""
    issue: str = ""
    pages: str = ""
    journal: str = ""
    year: str = ""
    resource_type: str = ""


@dataclass
class Entry:
    code: str
    title: str = ""
    journal: str = ""
    year: str = ""
    doi: str = ""
    url: str = ""
    pool_first_author: str = ""
    authors: list[str] = field(default_factory=list)
    volume: str = ""
    issue: str = ""
    pages: str = ""
    resource_type: str = ""
    status: str = ""
    cross_verified: bool = False
    retracted: bool = True
    retraction_known: bool = False
    retraction_checked_on: str = ""
    abstract_retrieved: bool = False
    verified_in: list[str] = field(default_factory=list)
    metadata_source: str = "pool"

    @property
    def citable(self) -> bool:
        return self.cross_verified and self.retraction_known and not self.retracted

    @property
    def not_citable_reason(self) -> str:
        if not self.retraction_known:
            return "retraction status unknown (neither retracted nor retraction_flag)"
        if self.retracted:
            return "retracted=true"
        if not self.cross_verified:
            label = self.status or "missing"
            return f"verification_status={label} (only cross_verified may be cited)"
        return ""


@dataclass
class Marker:
    start: int
    end: int
    codes: tuple[str, ...]
    line: int


@dataclass
class Insertion:
    offset: int
    line: int
    before_heading: str
    previous_heading: str
    last_subheading: str
    policy: str


@dataclass
class ProcessedText:
    """Result of renumbering one document; the 7_8 assembler consumes this."""

    text: str
    references: str
    order: list[str]
    mapping: dict[str, int]
    markers: list[Marker]
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# pool loading
# --------------------------------------------------------------------------- #
def _authors_from_pool(raw: dict) -> list[str]:
    authors = raw.get("authors")
    out: list[str] = []
    if isinstance(authors, list):
        for item in authors:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
            elif isinstance(item, dict):
                name = item.get("name")
                if not name:
                    name = " ".join(
                        part for part in (item.get("given"), item.get("family")) if part
                    )
                if name and str(name).strip():
                    out.append(str(name).strip())
    elif isinstance(authors, str):
        out = [part.strip() for part in re.split(r";|\band\b", authors) if part.strip()]
    return out


def load_pool(path: Path) -> tuple[dict[str, Entry], str]:
    """Read citation_pool.json (v3 schema, with tolerant aliases)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise BuildError([f"cannot read citation pool {path}: {exc}"]) from exc

    if isinstance(data, list):
        raw_entries, schema = data, "unknown"
    elif isinstance(data, dict) and isinstance(data.get("entries"), list):
        raw_entries, schema = data["entries"], str(data.get("schema_version", "unknown"))
    else:
        raise BuildError([f"citation pool {path} has no 'entries' list"])

    pool: dict[str, Entry] = {}
    problems: list[str] = []
    for index, raw in enumerate(raw_entries, 1):
        if not isinstance(raw, dict):
            problems.append(f"entry #{index} is not an object")
            continue
        code = str(raw.get("pool_id") or raw.get("code") or raw.get("c_code") or "").strip().upper()
        if not CODE_RE.fullmatch(code):
            problems.append(f"entry #{index} has no valid C-code (got {code!r})")
            continue
        if code in pool:
            problems.append(f"duplicate pool entry {code}")
            continue

        status = clean_text(raw.get("verification_status") or raw.get("status"))
        flag = raw.get("cross_verified")
        if isinstance(flag, bool):
            cross_verified = flag and status.lower() in ("", "cross_verified", "cross-verified")
        else:
            cross_verified = status.lower() in ("cross_verified", "cross-verified")

        if "retracted" in raw:
            retracted, retraction_known = bool(raw.get("retracted")), True
        elif "retraction_flag" in raw:
            retracted, retraction_known = bool(raw.get("retraction_flag")), True
        else:
            retracted, retraction_known = True, False

        authors = _authors_from_pool(raw)
        entry = Entry(
            code=code,
            title=clean_text(raw.get("title") or raw.get("display_name")),
            journal=clean_text(raw.get("journal") or raw.get("container_title")),
            year=str(raw.get("year") or raw.get("publication_year") or "").strip(),
            doi=strip_doi_prefix(raw.get("doi")),
            url=clean_text(raw.get("url")),
            pool_first_author=clean_text(raw.get("first_author")),
            authors=authors,
            resource_type=clean_text(raw.get("resource_type") or raw.get("type")),
            status=status,
            cross_verified=cross_verified,
            retracted=retracted,
            retraction_known=retraction_known,
            retraction_checked_on=clean_text(raw.get("retraction_checked_on")),
            abstract_retrieved=bool(raw.get("abstract_retrieved")),
            verified_in=[clean_text(v) for v in (raw.get("verified_in") or []) if clean_text(v)],
        )
        if not entry.authors and entry.pool_first_author:
            entry.authors = [entry.pool_first_author]
        pool[code] = entry

    return pool, schema


# --------------------------------------------------------------------------- #
# optional OpenAlex enrichment
# --------------------------------------------------------------------------- #
def _walk_works(node: object) -> Iterable[dict]:
    """Yield dicts that look like an OpenAlex work (have authorships / biblio)."""
    if isinstance(node, dict):
        if "authorships" in node or "biblio" in node or "primary_location" in node:
            yield node
        for value in node.values():
            yield from _walk_works(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_works(value)


def load_enrichment(raw_dir: Path | None) -> dict[str, Enrichment]:
    """Index raw OpenAlex JSON by DOI; ignore malformed files rather than fail."""
    if raw_dir is None or not raw_dir.is_dir():
        return {}
    index: dict[str, Enrichment] = {}
    for path in sorted(raw_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        for work in _walk_works(data):
            doi = normalize_doi(work.get("doi") or (work.get("ids") or {}).get("doi"))
            if not doi or doi in index:
                continue
            biblio = work.get("biblio") or {}
            first = clean_text(biblio.get("first_page"))
            last = clean_text(biblio.get("last_page"))
            pages = first if (not last or last == first) else f"{first}-{last}"
            source = (work.get("primary_location") or {}).get("source") or {}
            names: list[str] = []
            for authorship in work.get("authorships") or []:
                author = authorship.get("author") or {}
                name = clean_text(author.get("display_name") or authorship.get("raw_author_name"))
                if name:
                    names.append(name)
            index[doi] = Enrichment(
                authors=names,
                volume=clean_text(biblio.get("volume")),
                issue=clean_text(biblio.get("issue")),
                pages=pages,
                journal=clean_text(source.get("display_name")),
                year=str(work.get("publication_year") or "").strip(),
                resource_type=clean_text(work.get("type")),
            )
    return index


def enrich_pool(pool: dict[str, Entry], index: dict[str, Enrichment]) -> int:
    """Fill missing fields only; return the number of entries enriched."""
    enriched = 0
    for entry in pool.values():
        extra = index.get(normalize_doi(entry.doi))
        if not extra:
            continue
        changed = False
        if not entry.authors and extra.authors:
            entry.authors = list(extra.authors)
            changed = True
        if not entry.volume and extra.volume:
            entry.volume = extra.volume
            changed = True
        if not entry.issue and extra.issue:
            entry.issue = extra.issue
            changed = True
        if not entry.pages and extra.pages:
            entry.pages = extra.pages
            changed = True
        if not entry.journal and extra.journal:
            entry.journal = extra.journal
            changed = True
        if not entry.year and extra.year:
            entry.year = extra.year
            changed = True
        if not entry.resource_type and extra.resource_type:
            entry.resource_type = extra.resource_type
        if changed:
            entry.metadata_source = "pool+openalex"
            enriched += 1
    return enriched


# --------------------------------------------------------------------------- #
# marker scanning / numbering
# --------------------------------------------------------------------------- #
def _expand_group(group: str) -> tuple[str, ...]:
    """``C001, C002`` -> (C001, C002); ``C001-C003`` -> (C001, C002, C003)."""
    codes: list[str] = []
    for token in re.split(r"\s*[,;]\s*", group.strip()):
        if not token:
            continue
        range_match = re.fullmatch(
            r"(C\d{3})\s*[-\u2013\u2014]\s*(C\d{3})", token
        )
        if range_match:
            start, end = range_match.group(1), range_match.group(2)
            lo, hi = int(start[1:]), int(end[1:])
            if lo > hi:
                lo, hi = hi, lo
            if hi - lo > 50:
                raise BuildError([f"citation range {token} is implausibly large"])
            codes.extend(f"C{number:03d}" for number in range(lo, hi + 1))
        elif CODE_RE.fullmatch(token):
            codes.append(token)
        else:
            raise BuildError([f"malformed citation group: [{group}]"])
    # preserve order, drop duplicates inside one bracket
    seen: set[str] = set()
    unique: list[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique.append(code)
    return tuple(unique)


def scan_markers(text: str) -> list[Marker]:
    markers: list[Marker] = []
    for match in MARKER_RE.finditer(text):
        codes = _expand_group(match.group(1))
        line = text.count("\n", 0, match.start()) + 1
        markers.append(Marker(match.start(), match.end(), codes, line))
    return markers


def validate_citations(
    markers: Sequence[Marker], pool: dict[str, Entry]
) -> tuple[list[str], list[str]]:
    """Return (hard problems, warning notes). Hard problems block generation."""
    problems: list[str] = []
    warnings: list[str] = []
    cited: list[str] = []
    for marker in markers:
        for code in marker.codes:
            if code not in cited:
                cited.append(code)
    for code in cited:
        entry = pool.get(code)
        if entry is None:
            problems.append(f"{code}: not found in pool (pool-external citation)")
        elif not entry.citable:
            problems.append(f"{code}: {entry.not_citable_reason}")
    for code, entry in pool.items():
        if code not in cited and not entry.citable:
            warnings.append(f"{code} is not citable but is not cited ({entry.not_citable_reason})")
    return problems, warnings


def build_mapping(markers: Sequence[Marker]) -> tuple[list[str], dict[str, int]]:
    order: list[str] = []
    for marker in markers:
        for code in marker.codes:
            if code not in order:
                order.append(code)
    return order, {code: number for number, code in enumerate(order, 1)}


def _compress_numbers(numbers: Sequence[int]) -> str:
    values = sorted(set(numbers))
    if not values:
        return ""
    parts: list[str] = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        parts.append(f"{start}-{previous}" if previous - start >= 2 else
                     ",".join(str(v) for v in range(start, previous + 1)))
        start = previous = value
    parts.append(f"{start}-{previous}" if previous - start >= 2 else
                 ",".join(str(v) for v in range(start, previous + 1)))
    return ",".join(parts)


def renumber_text(
    text: str, mapping: dict[str, int]
) -> tuple[str, list[tuple[int, int]]]:
    """Replace [Cxxx] markers with [n]; return text and (offset, delta) list."""
    pieces: list[str] = []
    cursor = 0
    edits: list[tuple[int, int]] = []
    for match in MARKER_RE.finditer(text):
        codes = _expand_group(match.group(1))
        replacement = "[" + _compress_numbers([mapping[c] for c in codes]) + "]"
        pieces.append(text[cursor:match.start()])
        pieces.append(replacement)
        edits.append((match.start(), len(replacement) - (match.end() - match.start())))
        cursor = match.end()
    pieces.append(text[cursor:])
    return "".join(pieces), edits


# --------------------------------------------------------------------------- #
# reference rendering
# --------------------------------------------------------------------------- #
def _dedupe_names(names: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        key = fold(clean_text(name))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(clean_text(name))
    return out


def format_authors(entry: Entry, max_authors: int = 6) -> str:
    names = _dedupe_names(entry.authors)
    rendered: list[str] = []
    if names:
        if entry.pool_first_author and _families_match(entry.pool_first_author, names[0]):
            rendered.append(format_author(entry.pool_first_author, family_first=True))
        else:
            rendered.append(format_author(names[0]))
        for name in names[1:max_authors]:
            rendered.append(format_author(name))
        if len(names) > max_authors:
            rendered.append("et al.")
    elif entry.pool_first_author:
        # No author list anywhere: cite the one author we can verify, without
        # adding "et al." (which would assert a co-author set we do not have).
        rendered.append(format_author(entry.pool_first_author, family_first=True))
    return ", ".join(part for part in rendered if part)


def format_reference(entry: Entry, max_authors: int = 6) -> str:
    parts: list[str] = []
    authors = format_authors(entry, max_authors)
    if authors:
        parts.append(authors if authors.endswith(".") else authors + ".")
    title = clean_text(entry.title)
    if title:
        title = title.rstrip(".")
        parts.append(title + ("" if title.endswith(("?", "!")) else "."))
    journal = clean_text(entry.journal).rstrip(".")
    if journal:
        parts.append(journal + ".")
    year = clean_text(entry.year)
    location = ""
    if year:
        location = year
        if entry.volume:
            location += f";{entry.volume}"
            if entry.issue:
                location += f"({entry.issue})"
            if entry.pages:
                location += f":{entry.pages}"
        elif entry.pages:
            location += f":{entry.pages}"
        location += "."
    if location:
        parts.append(location)
    if entry.doi:
        parts.append(f"doi:{entry.doi}.")
    elif entry.url:
        parts.append(f"{entry.url}.")
    return " ".join(parts)


def audit_comment(number: int, entry: Entry) -> str:
    flags = [
        entry.code,
        f"n={number}",
        entry.status or "status=missing",
        "retracted=" + ("yes" if entry.retracted else "no"),
    ]
    if not entry.retraction_known:
        flags.append("retraction=unknown")
    flags.append("abstract=" + ("yes" if entry.abstract_retrieved else "no"))
    flags.append("vol/pages=" + ("yes" if (entry.volume or entry.pages) else "no"))
    flags.append("authors=" + entry.metadata_source)
    if entry.verified_in:
        flags.append("sources=" + "+".join(entry.verified_in))
    if entry.doi:
        flags.append("doi:" + entry.doi)
    return "<!-- " + " | ".join(flags) + " -->"


def render_references(
    order: Sequence[str],
    pool: dict[str, Entry],
    *,
    max_authors: int = 6,
    audit_comments: bool = True,
) -> str:
    lines = ["# References", ""]
    for number, code in enumerate(order, 1):
        line = f"{number}. {format_reference(pool[code], max_authors=max_authors)}"
        if audit_comments:
            line += " " + audit_comment(number, pool[code])
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def process_text(
    text: str,
    pool: dict[str, Entry],
    *,
    max_authors: int = 6,
    audit_comments: bool = True,
    source: str = "manuscript",
) -> ProcessedText:
    """Validate, renumber and render one document's citations in memory.

    This is the integration point for the Phase 7_8 assembler: call it on the
    concatenated body *before* the figure legends are appended, then emit
    ``result.text``, the References block and the separator.
    """
    markers = scan_markers(text)
    if not markers:
        raise BuildError(
            [f"no [Cxxx] markers found in {source} — nothing to renumber "
             "(already processed?)"]
        )
    problems, warnings = validate_citations(markers, pool)
    if problems:
        raise BuildError(problems)
    order, mapping = build_mapping(markers)
    numbered, _edits = renumber_text(text, mapping)
    references = render_references(
        order, pool, max_authors=max_authors, audit_comments=audit_comments
    )
    return ProcessedText(
        text=numbered,
        references=references,
        order=order,
        mapping=mapping,
        markers=markers,
        warnings=warnings,
    )


# --------------------------------------------------------------------------- #
# insertion point
# --------------------------------------------------------------------------- #
def find_insertion(text: str, explicit_heading: str | None) -> Insertion:
    headings = [
        (match.start(), match.group(2).strip(), match.group(1))
        for match in HEADING_RE.finditer(text)
    ]

    def context(pos: int) -> tuple[str, str]:
        before = [(start, title, level) for start, title, level in headings if start < pos]
        top = [f"{level} {title}" for _start, title, level in before if level == "#"]
        last = f"{before[-1][2]} {before[-1][1]}" if before else ""
        return (top[-1] if top else last), last

    if explicit_heading:
        target = fold(explicit_heading.lstrip("# "))
        for pos, title, _level in headings:
            if fold(title) == target:
                line = text.count("\n", 0, pos) + 1
                previous, last = context(pos)
                return Insertion(pos, line, f"# {title}", previous, last, "explicit")
        raise BuildError([f"insertion heading not found: {explicit_heading!r}"])

    for pos, title, _level in headings:
        if fold(title) in FIGURE_HEADING_NAMES:
            line = text.count("\n", 0, pos) + 1
            previous, last = context(pos)
            return Insertion(pos, line, f"# {title}", previous, last, "default")

    for pos, title, level in headings:
        if level == "#" and TABLE_HEADING_RE.match(title):
            line = text.count("\n", 0, pos) + 1
            previous, last = context(pos)
            return Insertion(pos, line, f"# {title}", previous, last, "default")

    previous, last = context(len(text))
    return Insertion(
        len(text),
        text.count("\n") + 1,
        "<end of file>",
        previous,
        last,
        "default",
    )


def insert_references(text: str, insertion: Insertion, block: str) -> str:
    before, after = text[: insertion.offset], text[insertion.offset :]
    if not before.endswith("\n"):
        before += "\n"
    if not before.endswith("\n\n"):
        before += "\n"
    tail = "\n" if insertion.before_heading == "<end of file>" else "\n\n---\n\n"
    return before + block.rstrip() + tail + after


# --------------------------------------------------------------------------- #
# style audit
# --------------------------------------------------------------------------- #
def analyse_style(text: str, markers: Sequence[Marker]) -> dict:
    kinds: Counter[str] = Counter()
    exceptions: list[dict] = []
    for marker in markers:
        tail = text[marker.end : marker.end + 60]
        following = tail.lstrip("\r\n \t")
        first = following[:1]
        if first in (".", "!", "?"):
            kind = "sentence_final"
        elif first in (",", ";", ")", "]"):
            kind = "before_punctuation"
        elif first in ("\u2014", "\u2013", "-"):
            kind = "before_dash"
        elif re.match(r"(?:and|or|but)\b", following, re.IGNORECASE):
            kind = "conjunction"
        elif first == "":
            kind = "sentence_final"
        else:
            kind = "mid_clause"
        kinds[kind] += 1
        if kind in ("conjunction", "mid_clause"):
            context = WS_RE.sub(" ", text[max(0, marker.start - 55) : marker.end + 45]).strip()
            exceptions.append(
                {
                    "code": marker.codes[-1],
                    "line": marker.line,
                    "kind": kind,
                    "followed_by": following[:18],
                    "context": context,
                }
            )

    citations: Counter[str] = Counter()
    for marker in markers:
        citations.update(marker.codes)

    # Mask marker spans before looking for codes that leaked outside brackets.
    masked = list(text)
    for marker in markers:
        for index in range(marker.start, marker.end):
            masked[index] = " "
    bare_codes = [m.group(0) for m in BARE_CODE_RE.finditer("".join(masked))]

    return {
        "kinds": kinds,
        "exceptions": exceptions,
        "duplicates": {code: count for code, count in citations.items() if count > 1},
        "unique": len(citations),
        "occurrences": sum(citations.values()),
        "numeric_markers": len(NUMERIC_MARKER_RE.findall(text)),
        "bare_codes": bare_codes,
        "supplementary": len(re.findall(r"Supplementary\s+S\d+", text, re.IGNORECASE)),
        "figures": len(re.findall(r"\bFigure\s+\d+", text, re.IGNORECASE)),
        "tables": len(re.findall(r"\bTable\s+\d+", text, re.IGNORECASE)),
    }


# --------------------------------------------------------------------------- #
# paths / reporting
# --------------------------------------------------------------------------- #
def resolve_pool(manuscript: Path, explicit: Path | None) -> Path:
    if explicit:
        if not explicit.is_file():
            raise BuildError([f"citation pool not found: {explicit}"])
        return explicit
    candidates = [
        manuscript.parent / "citation_pool.json",
        Path.cwd() / "outputs" / "paper" / "citation_pool.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise BuildError(
        [
            "citation pool not found; tried: "
            + ", ".join(str(c) for c in candidates)
            + " (pass --pool)"
        ]
    )


def resolve_raw_dir(manuscript: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        if not explicit.is_dir():
            raise BuildError([f"raw metadata directory not found: {explicit}"])
        return explicit
    candidates = [
        manuscript.parent / "citation_raw",
        Path.cwd() / "outputs" / "paper" / "citation_raw",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def _short(text: str, width: int) -> str:
    text = WS_RE.sub(" ", clean_text(text))
    return text if len(text) <= width else text[: width - 1] + "\u2026"


def _print_mapping(
    order: Sequence[str], pool: dict[str, Entry], title: str, start: int = 1
) -> None:
    if title:
        print(title)
    print(f"  {'n':>3}  code  year  {'first author':<22}  short title")
    for number, code in enumerate(order, start):
        entry = pool[code]
        authors = format_authors(entry)
        author = _short(authors.split(",")[0], 22) if authors else "-"
        print(f"  {number:>3}  {code}  {entry.year:<4}  {author:<22}  {_short(entry.title, 58)}")


def _print_sample(order: Sequence[str], pool: dict[str, Entry], count: int) -> None:
    print(f"REFERENCES SAMPLE (first {min(count, len(order))} of {len(order)})")
    for number, code in enumerate(order[:count], 1):
        print(f"  {number}. {format_reference(pool[code])}")
        print(f"     {audit_comment(number, pool[code])}")


def _summary(args: argparse.Namespace) -> int:
    manuscript = args.manuscript
    if not manuscript.is_file():
        raise BuildError([f"manuscript not found: {manuscript}"])
    try:
        text = manuscript.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise BuildError([f"cannot read manuscript {manuscript}: {exc}"]) from exc

    pool_path = resolve_pool(manuscript, args.pool)
    pool, schema = load_pool(pool_path)
    raw_dir = None if args.no_enrich else resolve_raw_dir(manuscript, args.raw_dir)
    index = load_enrichment(raw_dir)
    enriched = enrich_pool(pool, index)

    if not args.force and re.search(r"^#{1,6}[ \t]+References[ \t]*\r?$", text, re.MULTILINE | re.IGNORECASE):
        raise BuildError(["manuscript already contains a '# References' section (use --force to override)"])

    processed = process_text(
        text,
        pool,
        max_authors=args.max_authors,
        audit_comments=not args.no_audit_comments,
        source=str(manuscript),
    )
    markers = processed.markers
    order = processed.order
    mapping = processed.mapping
    numbered_text = processed.text
    references = processed.references
    pool_warnings = processed.warnings

    insertion = find_insertion(numbered_text, args.insert_before_heading)
    final_text = numbered_text
    if not args.no_insert:
        final_text = insert_references(numbered_text, insertion, references)

    style = analyse_style(text, markers)
    remaining = len(MARKER_RE.findall(final_text))
    no_volume = [code for code in order if not (pool[code].volume or pool[code].pages)]
    uncited = [code for code in pool if code not in mapping]
    uncited_citable = [code for code in uncited if pool[code].citable]
    pool_external = [code for code in order if code not in pool]
    cited_non_citable = [code for code in order if code in pool and not pool[code].citable]
    code_occurrences = sum(len(marker.codes) for marker in markers)

    print(f"[build_references {VERSION}] mode={'write' if args.write else 'dry-run'}")
    print(f"  manuscript : {manuscript} ({manuscript.stat().st_size:,} B)")
    print(f"  pool       : {pool_path} (schema {schema}, {len(pool)} entries)")
    if raw_dir:
        print(f"  raw dir    : {raw_dir} (enrichment applied to {enriched} pool entries)")
    else:
        print("  raw dir    : none (pool metadata only)")
    print(f"  insertion  : before {insertion.before_heading!r} line {insertion.line}; "
          f"preceding {insertion.previous_heading or '(none)'}"
          + (f" (last subheading {insertion.last_subheading})"
             if insertion.last_subheading and insertion.last_subheading != insertion.previous_heading else ""))
    print()

    print("CITATION STATISTICS")
    print(f"  bracket markers           : {len(markers)}")
    print(f"  code references           : {code_occurrences}")
    print(f"  unique cited C codes      : {len(order)}")
    print(f"  pool entries              : {len(pool)}")
    print(f"  pool entries uncited      : {len(uncited)}"
          + (f"  ({', '.join(uncited)})" if uncited else ""))
    print(f"  non-citable in pool       : {sum(1 for e in pool.values() if not e.citable)}")
    print(f"  cited but non-citable     : {len(cited_non_citable)}"
          + (f"  ({', '.join(cited_non_citable)})" if cited_non_citable else ""))
    print(f"  pool-external citations   : {len(pool_external)}"
          + (f"  ({', '.join(pool_external)})" if pool_external else ""))
    print(f"  numbering                 : {len(order)} codes -> 1..{len(order)}")
    print(f"  references to generate    : {len(order)}")
    print()

    print("NUMBERING (first 5)")
    _print_mapping(order[:5], pool, "")
    print("NUMBERING (last 5)")
    _print_mapping(order[-5:], pool, "", start=len(order) - 4)
    print()

    _print_sample(order, pool, args.sample)
    print()

    print("STYLE AUDIT")
    print(f"  sentence-final            : {style['kinds']['sentence_final']}/{len(markers)}")
    print(f"  before punctuation        : {style['kinds']['before_punctuation']}/{len(markers)}")
    print(f"  before dash               : {style['kinds']['before_dash']}/{len(markers)}")
    print(f"  mid-clause (and/or)       : {style['kinds']['conjunction']}/{len(markers)}")
    print(f"  mid-clause (other)        : {style['kinds']['mid_clause']}/{len(markers)}")
    for item in style["exceptions"]:
        print(f"    - line {item['line']} {item['code']} followed by {item['followed_by']!r}: "
              f"{_short(item['context'], 110)}")
    duplicates = style["duplicates"]
    print(f"  repeated citations        : "
          + (", ".join(f"{code} x{count}" for code, count in sorted(duplicates.items())) or "none")
          + " (same number reused: correct)")
    print(f"  non-C references          : Supplementary S4 x{style['supplementary']}, "
          f"Figure x{style['figures']}, Table x{style['tables']} (left untouched)")
    print(f"  bare C codes outside []   : {len(style['bare_codes'])}"
          + (f"  ({', '.join(style['bare_codes'])})" if style["bare_codes"] else ""))
    print(f"  pre-existing [n] markers  : {style['numeric_markers']}")
    print()

    print("VALIDATION")
    checks = [
        (len(markers) > 0,
         f"all {len(markers)} bracket markers / {code_occurrences} code references mapped"),
        (len(order) == len(set(order)), f"{len(order)} unique codes -> {len(order)} numbers"),
        (not pool_external, "0 pool-external citations"),
        (not cited_non_citable, "0 non-citable citations"),
        (remaining == 0, "replacement leaves 0 [Cxxx] markers"),
        (all(pool[code].doi or pool[code].url for code in order),
         "every reference carries a DOI or URL"),
        (insertion.offset >= 0, f"References inserted before {insertion.before_heading!r}"),
    ]
    for ok, message in checks:
        print(f"  [{'OK' if ok else 'FAIL'}] {message}")
    if no_volume:
        print(f"  [WARN] {len(no_volume)} reference(s) lack volume/pages: {', '.join(no_volume)}")
    else:
        print("  [OK] every reference has volume or page data")
    if uncited_citable:
        print(f"  [INFO] {len(uncited_citable)} citable pool entry(ies) not cited: "
              f"{', '.join(uncited_citable)}")
    for warning in pool_warnings:
        print(f"  [WARN] {warning}")

    if not all(ok for ok, _ in checks):
        raise BuildError(["dry-run validation failed; see FAIL lines above"])

    if not args.write:
        print("\n[dry-run] no files written (pass --write --out <path> to emit)")
        return 0

    # ---- write mode ----------------------------------------------------- #
    if args.out is None and args.references_out is None:
        raise BuildError(["--write needs --out <path> and/or --references-out <path>"])
    if args.out is not None:
        out = args.out
        if out.resolve() == manuscript.resolve():
            raise BuildError(["--out must not be the source manuscript (choose a new path)"])
        _write_text(out, final_text, args.force)
        print(f"\n[write] manuscript : {out} ({out.stat().st_size:,} B)")
    if args.references_out is not None:
        _write_text(args.references_out, references, args.force)
        print(f"[write] references : {args.references_out} "
              f"({args.references_out.stat().st_size:,} B)")
    if args.audit_json is not None:
        audit = {
            "generated_by": f"scripts/build_references.py v{VERSION}",
            "generated_on": str(date.today()),
            "manuscript": str(manuscript),
            "pool": str(pool_path),
            "pool_schema": schema,
            "n_markers": len(markers),
            "n_unique": len(order),
            "mapping": mapping,
            "insertion": {
                "before_heading": insertion.before_heading,
                "line": insertion.line,
                "previous_heading": insertion.previous_heading,
            },
            "entries": [
                {
                    "n": number,
                    "code": code,
                    "doi": pool[code].doi,
                    "title": pool[code].title,
                    "journal": pool[code].journal,
                    "year": pool[code].year,
                    "authors": pool[code].authors,
                    "volume": pool[code].volume,
                    "issue": pool[code].issue,
                    "pages": pool[code].pages,
                    "verification_status": pool[code].status,
                    "retracted": pool[code].retracted,
                    "abstract_retrieved": pool[code].abstract_retrieved,
                    "metadata_source": pool[code].metadata_source,
                }
                for number, code in enumerate(order, 1)
            ],
            "uncited": uncited,
        }
        _write_text(args.audit_json, json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
                    args.force)
        print(f"[write] audit json : {args.audit_json}")
    return 0


def _write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise BuildError([f"refusing to overwrite existing file: {path} (use --force)"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Renumber [Cxxx] citations in first-appearance order and render a "
            "Vancouver References section. Dry-run by default."
        )
    )
    parser.add_argument("--manuscript", required=True, type=Path,
                        help="Markdown file containing [Cxxx] markers")
    parser.add_argument("--pool", type=Path, default=None,
                        help="citation_pool.json (default: next to manuscript, then "
                             "outputs/paper/citation_pool.json)")
    parser.add_argument("--raw-dir", type=Path, default=None,
                        help="directory of raw OpenAlex JSON for volume/page/author "
                             "enrichment (default: next to manuscript, then "
                             "outputs/paper/citation_raw)")
    parser.add_argument("--no-enrich", action="store_true",
                        help="ignore raw OpenAlex metadata")
    parser.add_argument("--out", type=Path, default=None,
                        help="new manuscript path for --write (never the source path)")
    parser.add_argument("--references-out", type=Path, default=None,
                        help="optional path for the References block alone (useful to "
                             "feed the 7_8 assembler)")
    parser.add_argument("--audit-json", type=Path, default=None,
                        help="optional mapping audit JSON (only with --write)")
    parser.add_argument("--write", action="store_true",
                        help="write output files; default is a no-write dry run")
    parser.add_argument("--dry-run", action="store_true",
                        help="explicit dry run (the default)")
    parser.add_argument("--insert-before-heading", default=None,
                        help="insert References before this heading (default: "
                             "'Figure Legends', else the first '# Table', else EOF)")
    parser.add_argument("--no-insert", action="store_true",
                        help="only render the References block; do not insert it")
    parser.add_argument("--no-audit-comments", action="store_true",
                        help="omit the hidden <!-- Cxxx ... --> audit comments")
    parser.add_argument("--max-authors", type=int, default=6,
                        help="authors listed before 'et al.' (default: 6)")
    parser.add_argument("--sample", type=int, default=3,
                        help="number of sample references to print (default: 3)")
    parser.add_argument("--force", action="store_true",
                        help="allow overwriting outputs and an existing References section")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = build_parser().parse_args(argv)
    if args.dry_run and args.write:
        print("ERROR: --dry-run and --write are mutually exclusive", file=sys.stderr)
        return 2
    if args.audit_json is not None and not args.write:
        print("ERROR: --audit-json requires --write (dry-run writes nothing)", file=sys.stderr)
        return 2
    if args.write:
        if args.out is None and args.references_out is None:
            print("ERROR: --write needs --out <path> and/or --references-out <path>",
                  file=sys.stderr)
            return 2
        if (args.out is not None and args.manuscript.exists()
                and args.out.resolve() == args.manuscript.resolve()):
            print("ERROR: --out must not be the source manuscript; choose a new path",
                  file=sys.stderr)
            return 2
    try:
        return _summary(args)
    except BuildError as exc:
        print("ERROR: cannot build references:", file=sys.stderr)
        for problem in exc.problems:
            print(f"  - {problem}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
