# Semantic screening validation report

Run `python3 scripts/validate_screening.py`; optionally add `--manual-file results/completed_validation.csv`. Original classifications are read only. Flags are review nominations, not corrected labels or confirmed errors. No full papers were read.

## Coverage and formal consistency

- Rows: 364; unique paper IDs: 364. Compared with merged_papers.csv: 364 expected unique IDs; missing decisions 0; unexpected IDs 0.
- Decision counts: INCLUDE: 162; MAYBE: 140; EXCLUDE: 62.
- Invalid decision labels: 0; invalid research roles: 0.
- Nonempty justifications of at most 25 words: 364/364. Maximum reason length: 19 words.
- Formal coverage/schema/decision-role-route errors: 0. Criterion IDs and full-text flags checked with the screening validator.

Formal validity does not prove semantic validity. Short reasons sometimes describe a mechanism without demonstrating its personal-data relevance. The checks below identify cases needing judgment, not ground-truth error rates.

## Questionable decisions and possible false negatives

30 distinct records have a non-informational review flag. 5 excluded records are nominated for possible false-negative checks. All flags, evidence terms and related IDs are in results/validation_flags.csv.

| Flag | Records/instances |
| --- | ---: |
| ABSTRACT_RELEVANCE_UNRESOLVED | 140 |
| FRAMEWORK_WITH_CONCRETE_PRIVACY_CUE | 2 |
| I1_SPECIFIC_PRIVACY_EVIDENCE_CHECK | 12 |
| POSSIBLE_FALSE_NEGATIVE_BODY | 2 |
| POSSIBLE_FALSE_NEGATIVE_KEYWORDS_ONLY | 2 |
| PRIORITY_FALSE_NEGATIVE_CHECK | 2 |
| PRIORITY_FRAMEWORK_APPLICATION_CHECK | 2 |
| PRIORITY_I1_EVIDENCE_CHECK | 4 |
| SIMILAR_TITLE_DIFFERENT_DECISION | 14 |

### Priority abstract-level findings

- `paper_8f6ebc486580519f9e8760b5914b9690` — Security Analysis of “SMAKA: Secure Many-to-Many Authentication and Key Agreement Scheme for Vehicular Networks” (EXCLUDE, OUT_OF_SCOPE): Excluded SMAKA critique demonstrates session hijacking of an included protocol. Check confidentiality/accountability relevance under I1/I3; impersonation alone does not prove privacy harm.
- `paper_bd1b85bdc25f5ad3b406ae88951b27a0` — SMAKA: Secure Many-to-Many Authentication and Key Agreement Scheme for Vehicular Networks (INCLUDE, MITIGATION): The abstract describes an anonymous CSP broadcast, not clearly anonymous vehicle users. Verify whether the rationale overstates vehicle-identity privacy; compare the excluded critique.
- `paper_0398c7540e02547b91fda85abb322e0b` — Bilateral Control for Secure Communication Against Replay Attack in ORAN-Based Vehicular Networks (INCLUDE, MITIGATION): Access rights and encrypted-data replay models are concrete, but the abstract does not identify personal or linkable information. Verify I1 beyond generic cryptographic security.
- `paper_545af238767053d8b6e07d75a81dd41f` — IBRS: An Efficient Identity-based Batch Verification Scheme for VANETs Based on Ring Signature (INCLUDE, MITIGATION): Conditional privacy and ring-member selection are described, but concrete privacy exposure is implicit. Compare the evidence threshold against similar MAYBE authentication studies.
- `paper_dc066cea496a5651a88607b397279d22` — Blockchain-Based SDN-Enabled Lightweight Authentication Protocol for IoV Using zk-SNARK (INCLUDE, MITIGATION): The abstract emphasizes zero-knowledge proof size, controller availability and efficiency. Verify that a concrete privacy property is analyzed rather than inferred from the primitive.
- `paper_1df08b18e84051c0ae0f4b5e7d9a0d7b` — A Large Language Model-Supported Threat Modeling Framework for Transportation Cyber-Physical Systems (MAYBE, FRAMEWORK_FOCUSED): FRAMEWORK_FOCUSED paper applies its method to a real transportation data-exfiltration incident. Check whether personal-data findings justify CORE or a secondary role; no such findings are yet confirmed.
- `paper_b940c5d8bb8b5e35ba2b8dd75a69d45c` — A Novel Scalable Hybrid Threat Analysis and Risk Assessment Engine for an Automotive Subsystem (MAYBE, FRAMEWORK_FOCUSED): FRAMEWORK_FOCUSED automotive TARA paper explicitly mentions extraction of user-sensitive information. Determine whether the Ethernet evaluation actually analyzes that threat.
- `paper_56c57304a653535eb51b93461910251e` — Security Analysis of an Efficient Authentication Scheme for Vehicular Ad Hoc Networks (EXCLUDE, OUT_OF_SCOPE): Excluded vehicular cryptanalysis explicitly names confidentiality/privacy, but demonstrates forgery. Check for a supporting threat-evidence use without assuming integrity failures are privacy failures.

### Interpretation against the criteria

The main audit concern is uneven I1 evidence thresholds: some included authentication schemes rely on conditional-privacy or cryptographic-mechanism claims while similar schemes remain MAYBE. Confirm a specific privacy harm, affected data/identity relationship or tested privacy property; do not equate encryption, zero-knowledge proofs or signature correctness alone with substantive mobility privacy analysis.

The excluded SMAKA critique is a priority potential false negative because its original protocol is included. The alternative explanation is an overly generous inclusion of the original: the abstract describes an anonymous CSP broadcast rather than clearly anonymous vehicle users. Reviewing the pair must not automatically promote the critique or infer a privacy attack from impersonation alone.

Excluded papers containing privacy terms or keywords warrant inspection but may correctly satisfy E1 when the analyzed harm is exclusively forgery, integrity, availability or safety. Consider I2/I3 supporting use explicitly. This lexical check neither proves an exclusion wrong nor clears unflagged exclusions.

Exclusion criterion counts: {"E1":62,"E4":3}. Concentration on E1 merits a consistent check of supporting routes, but is not itself an error or an imposed target for label changes.

## Abstract completeness and adequacy

- Mechanically missing, short or ellipsis-ended abstracts: 0.
- Existing MAYBE records whose metadata remains insufficient to resolve eligibility: 140. This is conceptual insufficiency, not missing bibliographic data.
- Length checks use <100 characters or <20 whitespace-separated words. These are review signals, never relevance exclusions. A complete-looking abstract may still omit decisive methods, adversary assumptions or privacy results.

## Similar papers with differing classifications

7 title-similar pairs with different decisions were found. Full pair list: results/similar_screening_pairs.csv.

- `paper_32401c5eea69516fbee23bcc315dfa8e` (INCLUDE) ↔ `paper_ea8421df59c45353be7dbe4081fd1a5c` (MAYBE): title ratio 0.912, informative-token Jaccard 0.875.
- `paper_8f6ebc486580519f9e8760b5914b9690` (EXCLUDE) ↔ `paper_bd1b85bdc25f5ad3b406ae88951b27a0` (INCLUDE): title ratio 0.886, informative-token Jaccard 0.800.
- `paper_5889fb4bf0745197bd8250b29f308d1f` (INCLUDE) ↔ `paper_9210ece2d90259d4ae5e2172ea9618d0` (MAYBE): title ratio 0.876, informative-token Jaccard 0.600.
- `paper_878a14b905cf5ae09460729b02128196` (INCLUDE) ↔ `paper_e7a70a9e7e255e6b832626cbdf89d9ba` (MAYBE): title ratio 0.838, informative-token Jaccard 0.750.
- `paper_8a6f32fe2bb05a8aa67c405fc98fa3c6` (INCLUDE) ↔ `paper_9210ece2d90259d4ae5e2172ea9618d0` (MAYBE): title ratio 0.835, informative-token Jaccard 0.500.
- `paper_2713da386a9a5ff8b320350761f5071f` (MAYBE) ↔ `paper_98d3514f57505a8c955c4dff29aa739f` (INCLUDE): title ratio 0.804, informative-token Jaccard 0.714.
- `paper_5ca39c963bba50258c751e8705ccd200` (INCLUDE) ↔ `paper_9210ece2d90259d4ae5e2172ea9618d0` (MAYBE): title ratio 0.667, informative-token Jaccard 0.750.

Comparison uses lowercased title words minus a fixed domain/boilerplate stoplist, at least three shared informative tokens, Jaccard >=0.50, and then either Jaccard >=0.65 or SequenceMatcher ratio >=0.82 (autojunk disabled). Similarity is not duplicate identity or evidence that labels must agree. Original protocols and cryptanalytic comments can legitimately have different privacy contributions; differing abstract specificity can also justify INCLUDE versus MAYBE.

## Exclusion due to missing threat-model terminology

Exclusion reasons explicitly suggesting a required formal model or explicit threat-modeling terminology: 0.
Excluded records without a threat-modeling phrase in title/abstract: 58. Absence is descriptive, not evidence of the cause of exclusion.
No hidden reasoning can be reconstructed from a short justification. The recorded reasons are the auditable evidence; where no terminology requirement is found, this audit cannot prove that implicit bias never occurred. Neither the criteria nor the validation rules require that phrase.

## Framework-focused papers containing concrete privacy cues

Flagged framework-focused records: 2. The TARA engine mentioning sensitive-information extraction and TraCR-TMF's data-exfiltration case deserve specific attention.
These abstracts establish a concrete privacy-related cue, not necessarily a demonstrated mobility privacy analysis. Check whether their evaluated results support CORE/THREAT_EVIDENCE, a secondary role, or FRAMEWORK_FOCUSED supporting literature. Applying STRIDE/LINDDUN is not itself grounds for framework-focused placement or exclusion. No confirmed role changes are made.

## Manual validation sample

The sample is created only when absent; existing membership and reviewer entries are preserved byte-for-byte on reruns.
Sample size: 30; strata: INCLUDE: 10; MAYBE: 10; EXCLUDE: 10.
Initial selection seed: `mobility-privacy-validation-v1`. Per decision stratum: up to six records with positive-priority flags, ordered by highest priority then SHA-256(seed|paper_id), followed by hash-ranked remaining records to reach ten. If fewer than ten exist, retain all. Flag definitions, thresholds and curated review notes are versioned with the script and config/validation_review_notes.json.
This is a balanced, risk-enriched sample rather than a representative probability sample. Metrics describe only the labeled sample. Do not extrapolate population recall or error rates from it.
Fill my_classification (INCLUDE/MAYBE/EXCLUDE), my_research_role (one permitted role) and my_comments in results/manual_validation_sample.csv, then rerun the audit. Keep paper_id unchanged. For a less anchored first judgment, hide automated-label/reason and flag columns until recording your own decision. A MAYBE reference label remains unresolved, not a confirmed positive.
Existing sample files are never overwritten. Additional completed *validation*.csv files with my_classification are discovered in results/; --manual-file supports another filename. Duplicate reference labels are consolidated by paper ID; conflicts, unknown IDs and invalid labels are reported and not scored.

## Manual-reference comparison

Manual files inspected: `manual_validation_sample.csv`.
Valid manually labeled decisions: 0; valid manually labeled roles: 0.
No manual reference decisions are available. Agreement, kappa and recall were not calculated; automated labels and audit suggestions are not reference truth.

## Audit trail and limitations

- semantic_screening.csv SHA-256: `3cf3f5f8e80195ec76a99e4ec11c7d2b58d6c3c73a43220ab86d0ca70ac0d2e0`.
- screening_criteria.md SHA-256: `e09d7dad23e6afdd1b44d4b81a1d1e86178316b8cd87fa6ec3239cd2ff0ae7a6`.
- validation_review_notes.json SHA-256: `2ab0acb805b9142a4812799181d78f2b224436063d6d062e2c54490fd7fab43b`.
- validate_screening.py SHA-256: `357a34c22cb24d433988968ec6fa4e804b4e4282e3d6f0095f30e2d6d40fd889`.
- The current Codex session inspected priority abstracts and generated explicit audit notes, not human reference labels. Re-running Python reproduces flags and sample selection for unchanged inputs; it does not rerun semantic judgment or change automated labels.
- Priority 3–4 means urgent review/formal error, 2 means targeted review, 1 means a weaker lexical/similarity check, and 0 marks existing unresolved abstracts. None represents a measured probability of error.
- M/P/C/T dimension judgments and supporting-transfer rationales were not separately stored by the original six-field semantic schema. Matched I1 codes and short reasons do not constitute an independently auditable dimensional assessment. Record that detail during manual review.
- Independent human adjudication remains necessary. No full-text eligibility, corpus-wide recall or automatic classification corrections are claimed.
