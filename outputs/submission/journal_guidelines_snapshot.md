# Journal requirements snapshot

**Target journal:** Ophthalmology (Elsevier / American Academy of Ophthalmology), ISSN 0161-6420 — configured as `target_journal_primary` in `.planner.config.json`.
**Snapshot date:** 2026-10-15.

## STATUS: NOT OBTAINED — online fetch blocked, local fallback has no entry

| URL attempted | Result |
|---|---|
| https://www.aaojournal.org/content/authorinfo | HTTP 403 (Cloudflare) |
| https://www.elsevier.com/journals/ophthalmology/0161-6420/guide-for-authors | cross-origin redirect to sciencedirect.com, not followed |
| https://www.sciencedirect.com/journal/ophthalmology/publish/guide-for-authors | HTTP 403 |

The local fallback `references/submission_checklists.md` was read in full. **It contains no entry for Ophthalmology**, nor for JAMA Ophthalmology, British Journal of Ophthalmology or American Journal of Ophthalmology (the configured backups). Its entries cover Reproductive Toxicology, Lancet Digital Health, npj Digital Medicine, Nature Medicine, BMC Medical Informatics, JMIR and Environment International.

**Consequence:** this project cannot state the target journal's word limit, abstract limit, figure/table caps or reference style from any available source. Importing the limits of a *different* journal is how a submission silently breaches a cap, so no limits are asserted here. The author must verify the four items below against the journal's official guide before submission.

## What we do have: computed counts of the assembled package

| Quantity | Value |
|---|---|
| Manuscript size | 119,783 B |
| Manuscript body words (excl. legends and tables) | 11,155 |
| Figure-legend words | 3,259 |
| Table words | 821 |
| Abstract words | 440 |
| Discussion words | 3,603 |
| Figures | 6 |
| Tables | 7 |
| References cited | 24 |
| Entries in the verified citation pool | 27 |

## To verify before submission (author)

1. Main-text word limit and whether the abstract and tables count towards it.
2. Abstract structure and word limit (Ophthalmology has required a structured abstract since 2013).
3. Figure and table caps, and the required figure file format and DPI.
4. Reference style and cap (the pool is Vancouver-ready but the cap is unknown).
5. Reporting-guideline requirement — TRIPOD+AI [C001] and DECIDE-AI [C002] are already cited in Methods, so any requirement for them is met; confirm the journal does not additionally require a completed checklist as a supplementary file.

## Local fallback used for structure only

The *general* requirements in `references/submission_checklists.md` (cover letter, manuscript, separate figures, separate tables, statements) were used to decide **which files to assemble**. No journal-specific numeric limit was taken from it, because it has none for this journal.