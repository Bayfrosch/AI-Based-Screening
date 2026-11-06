# Preliminary screening report

Run `python3 scripts/preliminary_screening.py` (Python 3, standard library only). No LLM, API, network, full-text evaluation or target retention count is used. This is lexical triage, not final INCLUDE/MAYBE/EXCLUDE assessment or research-role assignment.

Rules version: 1.0; screening protocol: 1.0; input records: **364**; output records: **364**; deleted records: **0**.

| Category | Records |
| --- | ---: |
| POTENTIALLY_RELEVANT | 270 |
| UNCERTAIN | 94 |
| CLEARLY_IRRELEVANT | 0 |

## Clear exclusions

None. No record satisfied the affirmative evidence requirements for automatic exclusion; no keyword absence was treated as irrelevance.

## Rules and safeguards

Missing/short abstracts (under 100 characters or 20 whitespace-separated words), ellipsis endings, missing titles, upstream quality flags or conflicting screening metadata force UNCERTAIN. All populated title/abstract/keyword variants are checked. These completeness thresholds are retention safeguards, not quality or eligibility exclusions.

P1: privacy-equivalent terms plus mobility, location, adversary/attack or threat-analysis cues → POTENTIALLY_RELEVANT. P2: location/trajectory cues plus attack or analysis cues → POTENTIALLY_RELEVANT. Co-occurrence can occur across fields and does not prove a semantic relationship. Foundational/privacy evidence can be retained without an explicit mobility term. Generic mobility/security terminology alone remains UNCERTAIN.

Other matches → UNCERTAIN; no matches → UNCERTAIN. Positive keywords are broad retention cues, not proofs of privacy harms. Generic framework terminology is never an exclusion reason. Supporting/foundational transfer still needs later assessment under I2/I3. Rules only operationalize extremely narrow E1/E5 cases; E2–E4 cannot be established safely from vocabulary alone.

Enabled automatic exclusions (applied only after all completeness guards pass):

- `X1_EXPLICIT_NONPRIVACY_SCOPE`: E1: explicit privacy-out-of-scope statement plus exclusive technical focus corroborated by the title; no remaining privacy, location, attack, threat-analysis or supporting signals.
- `X2_PUBLICATION_ARTIFACT`: E5: exact publication-artifact title plus an explicit no-research statement in a sufficiently complete abstract; no relevance signals.

X1 additionally requires the privacy disclaimer to start a sentence, an exclusive focus on one of the configured technical metrics, that same metric in the title, and no contrast/negation ambiguity markers. After removing privacy-disclaimer phrases, any privacy, location, attacker, analysis or supporting-concept match in any field vetoes X1. X2 requires an exact artifact title and affirmative no-research text; any relevance-group match vetoes it. Technical subject words and lack of privacy words alone never cause exclusion.

Each exclusion logs the rule and exact source substrings with field paths and character offsets (Python string indices, zero-based, end-exclusive). For keyword variants, paths point to values in the retained original JSON cells. matched_terms_json records each configured pattern's first match per distinct text value; it is not an exhaustive list of occurrences. The original fields and all provenance columns are unchanged. Every row remains available for later review, including CLEARLY_IRRELEVANT.

## Rule counts

| Rule | Records |
| --- | ---: |
| P1_PRIVACY_WITH_CONTEXT | 265 |
| P2_LOCATION_WITH_ATTACK_OR_ANALYSIS | 5 |
| U2_AMBIGUOUS_LEXICAL_EVIDENCE | 94 |

## Vocabulary coverage

| Group | Records with a match |
| --- | ---: |
| mobility_systems | 361 |
| location_trajectory_data | 47 |
| privacy_threats | 265 |
| adversary_attack_models | 243 |
| threat_analysis | 294 |
| supporting_concepts | 295 |

Patterns are case-insensitive, use word boundaries, and accept whitespace or common Unicode hyphens between phrase tokens. Pattern definitions and synonyms are versioned in scripts/preliminary_screening.py. Overlapping groups are intentional. General authentication, encryption, identity, frameworks and data-governance terms also protect potentially transferable support from exclusion.

## Reproducibility and limitations

- merged_papers.csv SHA-256: `a9a5b897a646680d3227c8b27914e2134cf0d0c360211566228f7a5fc17bd45d`.
- screening_criteria.md SHA-256: `e09d7dad23e6afdd1b44d4b81a1d1e86178316b8cd87fa6ec3239cd2ff0ae7a6`.
- preliminary_screening.py SHA-256: `b407c7e0693f88fbd3cdee72a412aa206e57fbcfbc6022b7dc7c76131e9ed947`.
- Output order matches the input; unchanged inputs and script produce byte-identical results. Only the two preliminary outputs are overwritten.
- The Markdown criteria are read, version-checked and fingerprinted; their prose is not automatically converted into semantic rules. Review these coded rules if the criteria change.
- English lexical rules can miss synonyms, other languages and implicit relationships. Unmatched or ambiguous papers remain available. Lexical positives may include irrelevant work; that is intentional.
- No final reviewer decisions, role labels or foundational transfer claims are inferred. The protocol's human calibration, exclusion verification and adjudication remain for the subsequent substantive screening stage. Review clear-exclusion evidence before using it as a final eligibility decision.
