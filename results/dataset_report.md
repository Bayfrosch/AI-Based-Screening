# Dataset inspection report

Scope: structural inspection for the mobility privacy literature review described in `notes.md`. No semantic screening or source changes.

## Reproduce

Run `python3 scripts/inspect_datasets.py` from the project root (Python 3, standard library only). Settings and field mapping: `config/dataset_inspection.json`.

The requested `data/` directory is absent; the four source exports are in `papers/`. The configuration uses that existing location.

**382 source records across 4 files; 381 structurally valid; 1 malformed.** Record numbers below are 1-based, excluding the header.

Malformed records are excluded from field statistics and duplicate checks to prevent shifted columns from corrupting results. Their fields remain unassessed; all denominators below count structurally valid records only.

## Files and CSV structure

| File | Source records | Valid | Malformed | Columns | Bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| `export2026.10.28-09.16.13.csv` | 82 | 82 | 0 | 28 | 216336 |
| `export2026.10.28-09.24.35.csv` | 100 | 100 | 0 | 28 | 261598 |
| `export2026.10.28-09.24.57.csv` | 100 | 100 | 0 | 28 | 264653 |
| `export2026.10.28-09.25.19.csv` | 100 | 99 | 1 | 28 | 267573 |

Headers and order identical: **yes**. All inputs decode strictly as UTF-8; BOM presence and newline counts are recorded below. Comma delimiter, double-quote quoting, doubled embedded quotes; no automatic dialect guessing.

| File | UTF-8 BOM | LF / CRLF | Replacement characters | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `export2026.10.28-09.16.13.csv` | no | 83 / 0 | 0 | `20a68ad1d68cdddd5a3ea7c835a7111a30e50ba2d32df0abc9325cfa0933a87e` |
| `export2026.10.28-09.24.35.csv` | no | 101 / 0 | 0 | `469362d470fa34ffbb5691494f55e4950d24c683b5c0f3f569e067272b71cb1d` |
| `export2026.10.28-09.24.57.csv` | no | 101 / 0 | 0 | `8ba37a60122f39517ef3613c544b8d8d03d10ca76ecbc3c0c10c28897d2e810e` |
| `export2026.10.28-09.25.19.csv` | no | 101 / 0 | 0 | `129972b1ea63ea00622a5a2f91de492a3a0b2c8da431ddbe1a1ae181a8a17193` |

### Structural problems

- `export2026.10.28-09.25.19.csv#100` (physical lines 101–101): strict CSV error: ',' expected after '"'; permissive parser yields 29 fields (expected 28). Manual inspection locates unescaped embedded quotes in Funding Information; a comma then splits that field and shifts subsequent columns. Re-export or explicitly repair a derived copy before using this record.

Python's `csv.Sniffer` inferred `doublequote=False` on these exports, which creates spurious overflow fields on otherwise valid rows. The configured standard doubled-quote parser avoids that inference error; strict parsing still flags the genuine malformed row.

## Required metadata availability

Counts are populated / structurally valid records. Missing values include blanks and configured placeholder strings. Keyword availability means at least one of Author Keywords, IEEE Terms, or Mesh_Terms is populated.

| File | Titles | Abstracts | Authors | Years | DOIs | Any keywords | Author keywords |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `export2026.10.28-09.16.13.csv` | 82/82 | 82/82 | 82/82 | 82/82 | 82/82 | 82/82 | 79/82 |
| `export2026.10.28-09.24.35.csv` | 100/100 | 100/100 | 100/100 | 100/100 | 99/100 | 99/100 | 99/100 |
| `export2026.10.28-09.24.57.csv` | 100/100 | 100/100 | 100/100 | 100/100 | 99/100 | 99/100 | 97/100 |
| `export2026.10.28-09.25.19.csv` | 99/99 | 99/99 | 99/99 | 99/99 | 99/99 | 99/99 | 99/99 |

## Columns, inferred types and missing fields

CSV has no declared types: values are loaded as text. Cells below show inferred type and missing count, without converting sources. Numeric identifiers and page numbers should remain text in later imports. All-null columns are marked empty. Files A–D follow the order in the file table; valid denominators are 82, 100, 100 and 99.

| Column | A: type; missing | B: type; missing | C: type; missing | D: type; missing |
| --- | --- | --- | --- | --- |
| Document Title | text; 0 | text; 0 | text; 0 | text; 0 |
| Authors | text; 0 | text; 0 | text; 0 | text; 0 |
| Author Affiliations | text; 0 | text; 1 | text; 0 | text; 0 |
| Publication Title | text; 0 | text; 0 | text; 0 | text; 0 |
| Date Added To Xplore | text; 0 | text; 1 | text; 1 | text; 1 |
| Publication Year | integer; 0 | integer; 0 | integer; 0 | integer; 0 |
| Volume | integer; 36 | integer; 43 | text; 34 | text; 34 |
| Issue | integer; 47 | integer; 60 | integer; 44 | integer; 43 |
| Start Page | integer; 0 | integer; 1 | integer; 0 | integer; 0 |
| End Page | integer; 0 | integer; 1 | integer; 0 | integer; 0 |
| Abstract | text; 0 | text; 0 | text; 0 | text; 0 |
| ISSN | text; 18 | text; 23 | text; 19 | text; 17 |
| ISBNs | text; 46 | text; 54 | text; 65 | text; 65 |
| DOI | text; 0 | text; 1 | text; 1 | text; 0 |
| Funding Information | text; 41 | text; 44 | text; 36 | text; 37 |
| PDF Link | text; 0 | text; 0 | text; 0 | text; 0 |
| Author Keywords | text; 3 | text; 1 | text; 3 | text; 0 |
| IEEE Terms | text; 0 | text; 1 | text; 1 | text; 0 |
| Mesh_Terms | empty; 82 | empty; 100 | empty; 100 | empty; 99 |
| Article Citation Count | integer; 11 | integer; 23 | integer; 15 | integer; 16 |
| Patent Citation Count | empty; 82 | empty; 100 | empty; 100 | empty; 99 |
| Reference Count | integer; 0 | integer; 1 | integer; 2 | integer; 1 |
| License | text; 0 | text; 2 | text; 2 | text; 0 |
| Online Date | text; 0 | text; 0 | text; 0 | text; 0 |
| Issue Date | text; 0 | text; 1 | text; 1 | text; 1 |
| Meeting Date | text; 46 | text; 55 | text; 65 | text; 65 |
| Publisher | text; 0 | text; 0 | text; 0 | text; 0 |
| Document Identifier | text; 0 | text; 0 | text; 0 | text; 0 |

## Incomplete or suspicious metadata

- `export2026.10.28-09.16.13.csv`: year distribution 2015: 1, 2016: 2, 2017: 1, 2018: 8, 2019: 6, 2020: 4, 2021: 6, 2022: 11, 2023: 11, 2024: 14, 2025: 11, 2026: 7; invalid years 0; populated DOIs failing syntax check 0; abstracts under 100 characters 0; abstracts ending in ellipsis 0; titles under 10 characters 0.
- `export2026.10.28-09.24.35.csv`: year distribution 2020: 8, 2021: 10, 2022: 13, 2023: 13, 2024: 20, 2025: 25, 2026: 11; invalid years 0; populated DOIs failing syntax check 0; abstracts under 100 characters 0; abstracts ending in ellipsis 0; titles under 10 characters 0.
- `export2026.10.28-09.24.57.csv`: year distribution 2020: 14, 2021: 10, 2022: 10, 2023: 12, 2024: 27, 2025: 21, 2026: 6; invalid years 0; populated DOIs failing syntax check 0; abstracts under 100 characters 0; abstracts ending in ellipsis 0; titles under 10 characters 0.
- `export2026.10.28-09.25.19.csv`: year distribution 2020: 16, 2021: 14, 2022: 10, 2023: 16, 2024: 14, 2025: 17, 2026: 12; invalid years 0; populated DOIs failing syntax check 0; abstracts under 100 characters 0; abstracts ending in ellipsis 0; titles under 10 characters 0.

These are mechanical flags, not evidence of irrelevance or confirmed truncation. DOI syntax checks do not verify resolution; author and abstract completeness cannot be established from nonempty strings alone. Optional volume, issue, ISBN, funding and date fields may be legitimately absent.

## Potential duplicates

Checks: exact parsed rows; normalized DOI (case and DOI URL/prefix); normalized title (Unicode NFKC, case, punctuation and whitespace). Blank keys are ignored. No fuzzy or semantic matching; candidates are not automatically merged.

| Check | Groups | Records involved | Excess records within groups | Within-file pairs | Cross-file pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Exact row | 18 | 36 | 18 | 0 | 18 |
| DOI | 18 | 36 | 18 | 0 | 18 |
| Title | 18 | 36 | 18 | 0 | 18 |

Combined candidate components: 18; 36 records involved; 18 potential redundant copies. Counts from the individual checks overlap and must not be added. These are candidate counts, not a verified unique-paper total.

- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#5`; `export2026.10.28-09.25.19.csv#45`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#7`; `export2026.10.28-09.25.19.csv#53`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#9`; `export2026.10.28-09.24.35.csv#39`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#10`; `export2026.10.28-09.24.35.csv#71`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#14`; `export2026.10.28-09.24.35.csv#7`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#15`; `export2026.10.28-09.24.35.csv#29`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#17`; `export2026.10.28-09.24.57.csv#73`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#19`; `export2026.10.28-09.24.57.csv#30`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#26`; `export2026.10.28-09.24.35.csv#22`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#42`; `export2026.10.28-09.24.57.csv#95`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#50`; `export2026.10.28-09.24.57.csv#87`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#52`; `export2026.10.28-09.24.57.csv#8`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#56`; `export2026.10.28-09.24.35.csv#21`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#63`; `export2026.10.28-09.24.35.csv#67`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#64`; `export2026.10.28-09.24.57.csv#53`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#65`; `export2026.10.28-09.24.57.csv#35`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#73`; `export2026.10.28-09.24.35.csv#45`
- Exact row, DOI, Title: `export2026.10.28-09.16.13.csv#75`; `export2026.10.28-09.24.57.csv#67`

## Preparation for screening

- Preserve `papers/` as immutable source exports; hashes above identify the inspected versions.
- Resolve the flagged CSV row in a derived copy or by re-export; rerun inspection before normalization and screening.
- Retain source filename and record number as provenance; review duplicate candidates before merging metadata.
- Confirm search provenance: `notes.md` documents an 82-result search and a 1,469-result search, but does not map the three 100-record exports to query, sorting or export ranges. The available files do not establish exhaustive retrieval of those 1,469 results.
- No semantic eligibility decisions, relevance labels, deduplicated dataset or screening rules have been created.
