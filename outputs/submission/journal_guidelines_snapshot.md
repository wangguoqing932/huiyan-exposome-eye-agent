# Journal requirements snapshot

**Target journal:** undetermined. On 2026-10-19 the author deferred the journal choice for this round ("不用管哪家期刊，把文章做好了…：期刊不限制"), so no journal-specific limit is asserted here. The previously configured target (`.planner.config.json` → `target_journal_primary`) was **Ophthalmology** (Elsevier / American Academy of Ophthalmology), ISSN 0161-6420.

**Snapshot date:** 2026-10-19 (supersedes the 2026-10-15 snapshot).

## STATUS: NOT OBTAINED — online fetch blocked, and no journal has been fixed by the author

| URL attempted (2026-10-15) | Result |
|---|---|
| https://www.aaojournal.org/content/authorinfo | HTTP 403 (Cloudflare) |
| https://www.elsevier.com/journals/ophthalmology/0161-6420/guide-for-authors | cross-origin redirect to sciencedirect.com, not followed |
| https://www.sciencedirect.com/journal/ophthalmology/publish/guide-for-authors | HTTP 403 |

The local fallback `references/submission_checklists.md` was read in full. **It contains no entry for Ophthalmology**, nor for JAMA Ophthalmology, British Journal of Ophthalmology or American Journal of Ophthalmology (the configured backups). Its entries cover Reproductive Toxicology, Lancet Digital Health, npj Digital Medicine, Nature Medicine, BMC Medical Informatics, JMIR and Environment International.

**Consequence:** this project cannot state the target journal's word limit, abstract limit, figure/table caps or reference style from any available source, and the author has not fixed a target. No limits are asserted here, and packaging records them as unchecked rather than satisfied.

## Computed counts of the assembled package (2026-10-19)

| Quantity | Value |
|---|---|
| Manuscript size | 137,288 B |
| Abstract words | 440 |
| Main text words (Introduction through Declarations) | 10,477 |
| Discussion words | 2,877 |
| Figures | 8 (6 main + 2 supplementary) |
| Tables | 9 |
| References | 27 (all cross-verified, none retracted) |

## To verify before submission (author)

1. Fix the target journal, then its main-text word limit and whether the abstract and tables count towards it.
2. Abstract structure and word limit (Ophthalmology has required a structured abstract since 2013).
3. Figure and table caps, and the required figure file format and DPI.
4. Reference style and cap (the generated list is Vancouver-order ready).
5. Reporting-guideline requirement — STROBE is used; TRIPOD+AI and DECIDE-AI are explicitly cited as considered but **not claimed** in Methods and Declarations, so no checklist for them is supplied.
