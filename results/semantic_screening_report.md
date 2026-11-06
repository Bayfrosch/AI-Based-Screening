# Semantic screening report

Status: complete. Screened **364/364** unique papers; original source metadata and preliminary annotations retained in every output.

## Decisions

| Decision | Papers |
| --- | ---: |
| INCLUDE | 162 |
| MAYBE | 140 |
| EXCLUDE | 62 |

## Research roles

| Role | INCLUDE | MAYBE | EXCLUDE | Total |
| --- | ---: | ---: | ---: | ---: |
| CORE | 7 | 22 | 0 | 29 |
| THREAT_EVIDENCE | 2 | 6 | 0 | 8 |
| BACKGROUND | 0 | 16 | 0 | 16 |
| MITIGATION | 153 | 81 | 0 | 234 |
| FRAMEWORK_FOCUSED | 0 | 15 | 4 | 19 |
| OUT_OF_SCOPE | 0 | 0 | 58 | 58 |

## Main exclusion reasons

- E1: **62**. Clearly security/safety/performance-focused without substantive privacy analysis or supporting privacy content.
- E4: **3**. Generic framework contribution without an established supporting use.

## Method and interpretation

The available Codex session performed semantic judgments directly; no model API connection was assumed or used. Only paper ID, title, full supplied abstract, keywords and publication year were exposed for semantic assessment. No full papers, authors, venues, DOI information or preliminary keyword scores were used to infer relevance. Local Python joined preserved metadata without using it as semantic evidence.

Every unique source paper is assessed; preliminary categories do not determine final eligibility. In this corpus preliminary screening excluded none. Records are processed in source CSV order, in batches of at most 20. The first 20 constitute the fixed calibration sample (IDs in batch_001.json); labels distinguish concrete threat analysis, empirical evidence, explicit privacy mitigation, supporting context and ambiguous claims. No selection quota or new date/venue restriction was applied.

INCLUDE requires an evidenced I1/I2/I3 route. Concrete mobility privacy mitigation and empirical attacks remain eligible without a formal threat-modeling framework. Generic security/integrity/availability studies with no substantive privacy contribution are excluded only when the abstract clearly establishes their different focus. Generic privacy mentions, uncertain confidentiality claims and potential foundations are retained as MAYBE when relevance remains unresolved. Framework papers are not automatically core evidence.

MAYBE criterion IDs denote provisional inclusion routes, not confirmed fulfillment. Their roles are provisional. INCLUDE advances to full-text verification; both INCLUDE and MAYBE therefore set needs_full_text_review=true. Abstract-resolved EXCLUDE sets false; that flag does not prevent a reviewer from auditing or reversing the exclusion. All rows, including excluded records, preserve original metadata and provenance. No paper content or findings were invented.

Synthesis placement is PRIMARY for included I1 papers, SUPPORTING for included I2/I3 papers, UNRESOLVED for MAYBE and NOT_SELECTED for EXCLUDE. Reasons contain at most 25 whitespace-separated words. Outputs are abstract-stage recommendations, not independently verified full-text eligibility decisions.

## Reproduce, resume and audit

- python3 scripts/semantic_screening.py next: prints only the next unclassified batch's allowed metadata. Never requests completed batches again.
- python3 scripts/semantic_screening.py save: accepts compact JSON decisions on stdin, validates and immediately saves a batch checkpoint, then regenerates outputs.
- python3 scripts/semantic_screening.py export: validates saved classifications and regenerates all five outputs without model calls.
- config/semantic_screening_schema.json defines the persisted six-field decision schema; the Python validator enforces types, enums, reasons, identity uniqueness and decision/role/criterion consistency.
- results/semantic_batches/batch_*.json contain independent validated decisions. manifest.json fingerprints all inputs and prevents mixing decisions after an input change. Preserve checkpoints before starting a revised protocol run.
- Re-running export is deterministic; semantic judgments themselves are recorded session decisions, not a claim of deterministic model inference. No original data or preliminary classifications are modified.

## Limitations and remaining review

One Codex session supplied these judgments. No independent second reviewer or human adjudication has been completed; the criteria's preferred independent exclusion review remains outstanding. A second pass within this session may correct internal inconsistencies but does not provide independent validation. Review uncertain papers and audit exclusions before treating these recommendations as final study selection. Supporting claims and empirical/secondary-source overlap require full-text assessment. Missing details in otherwise plausible abstracts lead to MAYBE rather than assumed irrelevance.

## Input fingerprints

- merged_papers.csv: `a9a5b897a646680d3227c8b27914e2134cf0d0c360211566228f7a5fc17bd45d`.
- preliminary_screening.csv: `0f96d500aab767d6f6b1d99672f806df171e475f2d740e99540dc5b32904ebb9`.
- screening_criteria.md: `e09d7dad23e6afdd1b44d4b81a1d1e86178316b8cd87fa6ec3239cd2ff0ae7a6`.
