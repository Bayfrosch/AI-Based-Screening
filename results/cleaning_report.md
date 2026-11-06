# Dataset cleaning report

Run `python3 scripts/prepare_dataset.py` (Python 3, standard library only). Inputs and missing-value settings come from `config/dataset_inspection.json`. Source CSVs are read only; no relevance classification is performed.

## Counts

- Initial source records: **382**.
- Confirmed duplicate copies merged: **18**, in **18** groups.
- Possible duplicate pairs requiring review: **0** (kept separate).
- Resulting unique records under these rules: **364**.
- Recovered malformed records: **1**; discarded records: **0**.
- Merged records with metadata variants/conflicts: **0**.

## Inputs

| File | Records | SHA-256 |
| --- | ---: | --- |
| `papers/export2026.10.28-09.16.13.csv` | 82 | `20a68ad1d68cdddd5a3ea7c835a7111a30e50ba2d32df0abc9325cfa0933a87e` |
| `papers/export2026.10.28-09.24.35.csv` | 100 | `469362d470fa34ffbb5691494f55e4950d24c683b5c0f3f569e067272b71cb1d` |
| `papers/export2026.10.28-09.24.57.csv` | 100 | `8ba37a60122f39517ef3613c544b8d8d03d10ca76ecbc3c0c10c28897d2e810e` |
| `papers/export2026.10.28-09.25.19.csv` | 100 | `129972b1ea63ea00622a5a2f91de492a3a0b2c8da431ddbe1a1ae181a8a17193` |

## Cleaning and recovery

Column names are converted to snake_case and equivalent fields mapped to title, authors, publication_year, doi, abstract, publication_venue and URL fields. Every input column survives in original_fields and normalized metadata variants, including optional fields and unmapped columns. Scalars have surrounding whitespace removed and Unicode NFC applied. Configured missing markers become blank only in derived metadata; original strings remain intact.

DOIs lose the DOI URL or doi: prefix and are case-folded; only syntax-valid values are used as identity keys. Invalid raw DOI values remain in metadata, with a quality flag. Titles use Unicode NFKC, case-folding, punctuation removal and collapsed whitespace for matching; display titles preserve original wording. Years are retained as strings and invalid years flagged. Semicolon-separated keyword fields are combined without discarding the original fields; supplied URLs are unioned without fabricating links.

- `papers/export2026.10.28-09.25.19.csv#100`: Escaped 2 unescaped interior quotes in Funding Information; original CSV retained.

Malformed rows are repaired only when illegal interior quotes are confined to Funding Information and strict reparsing yields exactly the header width. Other malformed rows stop the run rather than being skipped. Repaired records include original_csv_record as lossless recovery evidence.

## Duplicate rules and resolution

1. Same valid normalized DOI: automatic merge. Conflicting metadata is retained even when the DOI matches.
2. Same normalized title: automatic merge only for titles of at least 20 characters and four words, equal valid populated publication years, and at least one shared full normalized author name (semicolon-separated). A title bucket and its existing DOI clusters must contain no conflicting populated DOI or year. Missing corroboration, differing years or differing DOIs require review. A DOI-free record cannot bridge two DOI identities.
3. Fuzzy titles: SequenceMatcher with autojunk disabled, ratio >= 0.95, at least 30 characters and five distinct words in each title, and shared words / smaller word-set size >= 0.80. These are review candidates only, including when DOIs or years conflict. All original title variants are checked. Different source-pair evidence is consolidated into one review row per final paper pair.

Merge policy: first nonmissing scalar value in sorted source filename / numeric record order. Exact source values, their origins, all alternatives and conflicts remain in source_records_json, metadata_variants_json and metadata_conflicts_json. keywords_json and urls_json combine values; original keyword categories remain in metadata. Canonical DOI is the normalized valid identity value. duplicates.csv logs each successful merge edge (one row per redundant source copy), the matching rule and resulting paper ID; its edges describe a merge graph, not necessarily a single retained source row.

## Output schema and identifiers

merged_papers.csv contains paper_id, title, normalized_title, abstract, authors, publication_year, doi, keywords_json, publication_venue, urls_json, source_count, source_records_json, metadata_json, metadata_variants_json, metadata_conflicts_json and quality_flags_json. JSON columns are standard JSON strings inside quoted CSV fields. Source rows are 1-based data-record numbers excluding the header; physical line ranges are also preserved. metadata_json retains all normalized source fields; authoritative normalized DOI and combined keywords/URLs are the dedicated columns.

Paper IDs use deterministic UUIDv5: normalized DOI when available; otherwise normalized title, year, authors and venue. Records without an identity title/DOI fall back to source location; unresolved identical identity tuples are disambiguated by source location. IDs and output bytes are stable for unchanged input and independent of the working directory. Correcting identity metadata, changing a DOI-free representative or moving/reordering fallback source records can change IDs; IDs are not a persistent registry across edits.

possible_duplicates.csv is a review queue, not a merge instruction; the automated script does not consume manual decisions. Empty audit queues still contain column headers. Re-running overwrites only the four derived outputs. Source hashes and complete provenance make the run auditable. Fuzzy thresholds are conservative and may miss paraphrased titles. DOI resolution and semantic relevance are not checked.
