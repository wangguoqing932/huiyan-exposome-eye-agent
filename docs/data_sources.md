# Data Sources — huiyan

## Primary validation databases (local, read-only)

| Source | Path | Role | Verified |
|---|---|---|---|
| NHANES 2005-2008 | E:/BaiduNetdiskDownload/所有数据库/16.NHANES | Internal validation (VIX/OPXRET/VIQ + BIOPRO/DR1TOT/PBCD/CRP) | 2026-10-11 |
| KNHANES 2008-2021 | E:/BaiduNetdiskDownload/所有数据库/11. KNHANES | External validation (眼科检查 + 生化 + 营养) | 2026-10-11 |
| CHARLS 2011 | E:/BaiduNetdiskDownload/所有数据库/01. CHARLS | Cohort layer (da035/036/037 + biomarkers) | 2026-10-11 |
| 9 aging cohorts | E:/BaiduNetdiskDownload/所有数据库/01-09 | Cohort layer (self-report outcomes) | 2026-10-11 |
| GBD vision 2023 | E:/BaiduNetdiskDownload/所有数据库/15/17/18 | Burden context | 2026-10-11 |

## Evidence sources (literature)

| Source | Access | Purpose |
|---|---|---|
| PubMed E-utilities | NCBI_API_KEY (10 req/s) | Rule citations, evidence base |
| AAO PPP (POAG/AMD/DR) | Proxy download | Level A evidence |
| Crossref + OpenAlex | Public API | DOI dual-source verification |

## Registry sources

| Registry | File | Count |
|---|---|---|
| Entity A (exposures) | data/seed/entities_a.csv | 41 |
| Entity B (eye diseases) | data/seed/entities_b.csv | 15 (1 no-source) |
| Evidence chunks | data/seed/evidence_chunks.jsonl | 521 |
| Rules | configs/rules.yaml | 20 (r15 revoked) |
