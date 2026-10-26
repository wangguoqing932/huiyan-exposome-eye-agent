# Archive 2026-10-23 (R21 compliance cleanup)

Moved here rather than deleted so the audit trail survives. Nothing in this
folder is an input to the current manuscript, figures, or gates.

| Item | Why archived |
|---|---|
| `figure3_expert_agreement.yaml.superseded_R11` | Superseded figure-3 contract. It must not sit in `outputs/figures/contracts/`: the QC/rendering globs live there and the file is not a live contract. |
| `manuscript_R11.md` | R11-era manuscript draft (48 KB), superseded by the R11-corrected / dual-generation manuscript. |
| `figure_legends.md.bak` | Pre-R11 legend backup. |
| `figure_visual_inspection.md` | Source of the manual visual-inspection section. Its content is now appended to `outputs/paper/figure_table_qc_report.md` (that report is rewritten on every QC run, so the section is re-appended). |
| `expert_review_2026-10-21.html` | One-off expert-review page, not referenced by any manuscript or submission artifact. |
| `captcha.jpg`, `captcha3.jpg` | Captcha screenshots captured while building the library/VPN channels; no evidential value. |
| `audit_tmp_20261015/` | R5-era audit scratch files, including `evidence_chunks_pre_levelfix_20261015-221335.jsonl` (pre-fix evidence snapshot kept as an audit backup). |

Also removed in this cleanup (regenerable, not evidence): ten `pip-*` temp
directories (~10 MB), empty `.tmp/`, `.pytest_cache/`, `data-gym-cache/`
(3.6 MB opaque cache blob), and the original `.audit_tmp/`.

Live files deliberately kept:

- `outputs/figures/source_data/figure3_expert_agreement.csv` — the
  `NOT_COLLECTABLE` sentinel that `scripts/generate_paper_figures.py` reads to
  refuse rendering a fabricated expert-agreement figure. It is an active
  anti-fabrication guard, not a stale artifact.
- `outputs/_rerun_backup_20261015/`, `baseline_predictions_preR5_archive.jsonl`,
  `baseline_predictions_R5_round1.jsonl` — documented prediction archives.
- `docs/history/R14..R20_FIXLOG*.md` — round-by-round audit records.
