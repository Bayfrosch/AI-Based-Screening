# Reading prioritization report

Status: complete. Assessed 162/162 INCLUDE papers. All original metadata, semantic decisions and roles remain unchanged.

## Priorities

| Priority | Papers |
| --- | ---: |
| HIGH | 38 |
| MEDIUM | 120 |
| LOW | 4 |

## Method

The Codex session assessed each paper using its title, supplied abstract and keywords in batches of at most 20. No full papers, publication-year scores, venues, citation counts or automatic role-based rankings were used. Six 0–2 evidence dimensions are defined in config/prioritization_rubric.json: direct privacy threat analysis, mobility-specific privacy, adversary depth, system specificity, explanatory usefulness, and limitations/open challenges. Zero means not established by this metadata, not poor study quality.

HIGH: direct threat analysis=2, mobility relevance>=1, explanatory usefulness=2, and adversary depth>=1; alternatively, mobility relevance=2, adversary depth=2, explanatory usefulness=2 and a specified system. This second route recognizes threat-specific defenses that explain concrete mobility exposures. MEDIUM: otherwise a mobility privacy connection and a concrete privacy property/protection concept are both established. LOW: supplementary or insufficiently specified privacy usefulness. LOW does not reverse INCLUDE or remove the need for full-text eligibility verification.

There is no quota on HIGH. A cryptographic proof, scheme efficiency, generic framework name or a recent publication date alone cannot establish high priority. Applied STRIDE/LINDDUN privacy analyses are assessed by their threats and findings. Generic framework evaluation is distinguished from applied analysis in contribution_focus; no framework penalty is applied. Within tiers, deterministic ordering favors direct analysis, explanatory value, adversary depth, limitations, system specificity and mobility-specific privacy, followed by paper ID. Publication year is never used.

Each assessment retains all six ordinal scores, one or more supplied thematic categories and a reason of at most 25 words. These are reading recommendations from metadata, not claims that full-text findings have been verified. Scores make the judgments inspectable; deterministic export does not imply independently reproducible model inference.

## Research areas represented

| Theme | All prioritized papers | HIGH |
| --- | ---: | ---: |
| Location tracking and surveillance | 25 | 16 |
| Re-identification | 5 | 3 |
| Trajectory linking and correlation | 8 | 8 |
| Inference attacks | 1 | 1 |
| Connected vehicles and V2X | 157 | 38 |
| Public transportation and MaaS | 0 | 0 |
| Mobility-specific threat modeling | 35 | 34 |
| Privacy risk mitigation | 159 | 36 |
| Other relevant topics | 46 | 12 |

Thematic counts overlap because papers can receive multiple categories. Connected-vehicle/V2X protocols and privacy risk mitigation dominate this retrieved set. Pseudonyms, conditional anonymity, identity accountability, cloud/edge sharing and cryptographic access control recur. Higher-priority uses include explaining stakeholder trust, location/trajectory disclosure, linking attacks, compromised authorities, sensitive driver data and limitations of privacy mechanisms.

Theme safeguards: authorized tracing of malicious vehicles is not automatically location surveillance. Generic unlinkability is not automatically trajectory correlation. Ordinary anonymity or direct identity disclosure does not by itself demonstrate re-identification. Re-identification tags cover identity guessing/linkage, tracking across changing pseudonyms and face deidentification, not a count of demonstrated attacks. Generic ITS is not automatically public transport/MaaS. Categories reflect explicit study topics, risks or protections, including attempts to prevent a threat; they do not assert a successful attack.

The Mobility-specific threat modeling theme includes privacy-relevant adversary/scenario analysis within mitigation studies. The separate DIRECT_THREAT_ANALYSIS contribution count identifies papers organized primarily around threat/attack analysis. Do not interpret every thematic match as a dedicated modeling-method paper.

### Contribution focus

| Focus | Papers |
| --- | ---: |
| DIRECT_THREAT_ANALYSIS | 8 |
| THREAT_SPECIFIC_MITIGATION | 113 |
| GENERAL_PRIVACY_MITIGATION | 41 |
| FRAMEWORK_EVALUATION | 0 |
| SUPPORTING_CONTEXT | 0 |

## Suggested first full-text readings

- `paper_108e36360e5b5ac9bafdb4bcce2220fd` — A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems: Directly reviews toll-based location tracking, collusion, physical attacks, protection weaknesses, and open research directions.
- `paper_517c3429051d52d78c620dd4b57a4610` — A Secure and Privacy-Preserved Road Condition Monitoring System: Demonstrates colluding roadside units exposing trajectories and defeating anonymity/unlinkability, directly informing privacy threats and trust assumptions.
- `paper_9c675835c4495d9fbc5c1e887de01cf9` — Secure Resource Allocation for LTE-Based V2X Service: Identifies location leakage from resource-allocation patterns despite secured higher layers, illustrating cross-layer privacy-model limitations.
- `paper_aaccc95774275d8dbe435e6f12eb3677` — Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario: Experimentally tests pseudonym-change defenses against realistic vehicle tracking, directly exposing correlation risks and privacy-protection limitations.
- `paper_d6bfc521f64b565ba00636fbf9a668b6` — Blockchain-Based One-Time Authentication for Secure V2X Communication Against Insiders and Authority Compromise Attacks: Explicitly analyzes insiders and compromised authorities leaking identities, locations and membership, directly supporting stakeholder threat modeling.
- `paper_ddd332dd15385498b54d3b3a2f989719` — Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy: Models semi-honest stakeholders and persistent cross-organization control over routes and driving habits, directly supporting data-flow privacy analysis.
- `paper_f22e9e553f2a5009bd811ea285c3743c` — Physically Secure Lightweight and Privacy-Preserving Message Authentication Protocol for VANET in Smart City: Directly analyzes tracking through linked safety messages and physical key extraction, clarifying privacy assumptions under compromised infrastructure.
- `paper_263db630aa99536eb27016190cdf9fab` — iVFAS: An Improved Vehicle-to-Fog Authentication System for Secure and Efficient Fog-Based Road Condition Monitoring: Identifies traceability and leakage failures under semi-trusted infrastructure, useful for explaining why claimed protocol security may not ensure privacy.
- `paper_6839e29e40785a81a849ce7166a564e6` — An Unlinkable Authenticated Key Agreement With Collusion Resistant for VANETs: Explains how colluding roadside units link authentication records and defeat anonymity, making trust assumptions and protocol limitations explicit.
- `paper_32401c5eea69516fbee23bcc315dfa8e` — Security Analysis on an Efficient and Provably Secure Authenticated Key Agreement Protocol for Fog-Based Vehicular Ad-Hoc Networks: Demonstrates failed anonymity and key disclosure in an allegedly secure fog protocol, directly supporting limitations and adversarial analysis.
- `paper_6d1cc4a712575c69ae862ea45abe926d` — Dynamic Anonymous Hierarchical Edge-Assisted Batch Verifiable Authentication for VANETs: Identifies anonymity-exposure attacks in an existing vehicular protocol, providing direct evidence for privacy-assurance limitations.
- `paper_8a83fb00cc975a24ae9f30910c4f486b` — AnonMAKE: Toward Secure and Anonymous Mutually Authenticated Key Exchange Protocol for Vehicular Communications: Shows failed anonymity and key disclosure in prior vehicular authentication, directly supporting limitations of claimed privacy guarantees.
- `paper_1ac697087f1f5fb1bee01105125a065b` — A Threat Model for Soft Privacy on Smart Cars: Directly models automotive personal-data control, threat agents, and domain-specific assets; central evidence for mobility privacy threat modeling.
- `paper_e4abc744a7f25dff9c93f5dc15b885a3` — User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN: Directly applies STRIDE/LINDDUN to connected-vehicle users and device/cloud interactions, explaining personal-data disclosure and unauthorized access.
- `paper_c66d5051f881504287f45d8f7a825cdb` — A baseline threat and mitigation model for automotive cybersecurity and privacy: Applies STRIDE/LINDDUN to automotive privacy assets and mitigations, directly supporting threat-to-control mapping rather than generic framework comparison.
- `paper_843c0c6527ce546caf6d5e078a8e3325` — Human-Artificial Intelligent Threat Modelling in the Automotive Domain: Automotive threat elicitation integrates pseudonymization and data minimization; useful applied-model example whose detailed privacy findings need full-text verification.
- `paper_44108b65f1f759118cf68a911eeb1787` — Efficient and Privacy-Preserving Ad Conversion for V2X-Assisted Proximity Marketing: Models malicious advertising stakeholders and sensitive customer disclosure, exposing limitations of honest-party assumptions in mobility services.
- `paper_4d9c36fb75ed5c5e94bde3969fb8b428` — Privacy-Preserving Continuous Data Collection for Predictive Maintenance in Vehicular Fog-Cloud: Explains location/identity exposure from continuous maintenance sensing and the privacy-error trade-off introduced by differential privacy.
- `paper_5af29268414850418a556d8d097c7dcc` — Conditional Anonymity enabled Blockchain-based Ad Dissemination in Vehicular Ad-hoc Network: Explains anonymity abuse and behavioral privacy leakage in advertising, highlighting stakeholder accountability and pseudonym-change trade-offs.
- `paper_98d3514f57505a8c955c4dff29aa739f` — An Efficient and Physically Secure Privacy-Preserving Authentication Scheme for Vehicular Ad-hoc NETworks (VANETs): Explicitly analyzes anonymity and unlinkability despite onboard-device compromise, exposing practical trust boundaries for privacy guarantees.
- `paper_9aaa8de3af10531ba32bcee0dd4ce7fa` — Achieving Adaptive Linkability for Cellular V2X Group Communications in 5G: Explicitly analyzes anonymity versus message-linkability requirements and user control across V2X use cases.
- `paper_20b078a101d9585393662ec073f59186` — Post-Quantum Anonymous, Traceable and Linkable Authentication Scheme Based on Blockchain for Intelligent Vehicular Transportation Systems: Explicitly analyzes conflicts between sender identity privacy and adversarial tracing/linking, supporting privacy-accountability trade-offs.
- `paper_5832900a48695c129790ad4eb98aebf2` — Privacy-enhanced capabilities for VANETs using direct anonymous attestation: Analyzes pseudonym-reuse limitations, revocation, infrastructure trust, and user-controlled linkability; directly supports privacy-design trade-offs.
- `paper_82db1b521cd15a33a9df39b884cdfc5e` — SWATS: A Lightweight VANET Anonymous Traceback System Based on Random Superposition Watermarking: Explicitly examines anonymity-abuse and traceback trade-offs, including reconstructed vehicle path information.
- `paper_06633fe9993854879674223304e94422` — P2BA: A Privacy-Preserving Protocol With Batch Authentication Against Semi-Trusted RSUs in Vehicular Ad Hoc Networks: Explains privacy mining and data association by semi-trusted roadside infrastructure, supporting concrete adversarial stakeholder analysis.
- `paper_0b8c8127b259527fa88bc12adba3b5c3` — A Sanitizable Access Control With Policy-Protection for Vehicular Social Networks: Explains malicious publishers and receiver-attribute disclosure through access policies, offering concrete stakeholder and data-flow risks.
- `paper_0e49ffacf5dd568b922a259f06945c16` — Lightweight and Provably Secure Privacy-Preserving Implicit Authentication Protocol Using Weighted-MinHash for IoV Environment: Connects sensitive driver behavioral features to semi-honest cloud assumptions, useful for explaining privacy exposure and trust limitations.
- `paper_5876a6eb2f6a53008907e6abc4fcee20` — FastTrust: Fast and Anonymous Spatial-Temporal Trust for Connected Cars on Expressways: Explains disclosure through spatial-temporal broadcasts and unlinkability protections on expressways, offering concrete mobility privacy examples.
- `paper_5df36478f1b154678e46ecf6a565ab0c` — A Secure Object Detection Technique for Intelligent Transportation Systems: Evaluates inference attacks against collaborative vehicular object detection, providing a concrete learning-related privacy threat and defense example.
- `paper_65688dd1e50258cebcab20ce0c147425` — Dual Privacy-Preserving Lightweight Navigation System for Vehicular Networks: Explicitly models roadside/navigation-provider exposure and linking of routes, locations and PII, supporting concrete stakeholder privacy analysis.
- `paper_6d7068f463c35c2698ef5c000ca34c95` — Achieving Efficient and Privacy-Preserving Worker Selection With Arbitrary Spatial Ranges for Vehicular Crowdsensing: Makes trajectory disclosure to an untrusted crowdsensing platform explicit, including workers, query users and collaborating fog infrastructure.
- `paper_8634f94e8b445464bba30b58ddb29e36` — A Privacy-Preserving Data Sharing Scheme Based on Blockchain for Vehicular Edge Networks: Connects location/identifier leakage, consent and illegal cross-stakeholder transfers, useful for concrete vehicular data-flow privacy analysis.
- `paper_cdfa597ef0f855cea5377e091e16f70f` — Ultra-Lightweight and Secure Blockchain-Assisted Charging Scheduling Scheme for Vehicular Edge Networks by Utilization of NanoPi NEO: Explicitly models honest-but-curious charging edge nodes, linking electric-vehicle services to stakeholder anonymity and accountability risks.
- `paper_e1088cabd0ec55d5a2852bc3a806a86e` — A Blockchain-Assisted Road Condition Monitoring Scheme With Privacy-Preserving for VANETs: Explains sensitive vehicle/driver disclosure through untrusted cloud servers, with explicit stakeholder behavior and protective controls.
- `paper_ef081d1fd5ee5cfaabe0e6c9d3a3c48a` — A Privacy-Preserving Misbehavior Detection System in Vehicular Communication Networks: Explains location, trajectory and identity exposure through misbehavior feedback, illustrating privacy costs of security monitoring.
- `paper_2294f6b8f3a25f65a91686756079f281` — Proof of Pseudonym: Blockchain-Based Privacy Preserving Protocol for Intelligent Transport System: Connects safety-message identity disclosure and pseudonym linking to internal/external attacks; useful concrete privacy-threat examples.
- `paper_3c3bcff86be958f0af85e7396b7e736d` — CACPPA: A Cloud-Assisted Conditional Privacy Preserving Authentication Protocol for VANET: Explicitly links stolen owner identity and location to attacker scenarios, supporting concrete vehicular privacy-threat explanation.
- `paper_ae49e51ea8bf587880def3526d61ddaf` — A Conditional Privacy Protection Scheme Based on Ring Signcryption for Vehicular Ad Hoc Networks: Explicitly connects identity disclosure to driver stalking and tracking, supplying concrete privacy-harm examples alongside ring-signcryption protection.

## Topics with limited coverage

- Location tracking and surveillance: 25 paper(s) in the prioritized set; 16 HIGH.
- Re-identification: 5 paper(s) in the prioritized set; 3 HIGH.
- Trajectory linking and correlation: 8 paper(s) in the prioritized set; 8 HIGH.
- Inference attacks: 1 paper(s) in the prioritized set; 1 HIGH.
- Public transportation and MaaS: 0 paper(s) in the prioritized set; 0 HIGH.
- Mobility-specific threat modeling: 35 paper(s) in the prioritized set; 34 HIGH.

Small or zero counts indicate limited coverage in these included metadata records, not an absence of research in the field. Public-transport/MaaS, ride-sharing and cross-service trip histories need particular attention during further retrieval if absent here. Explicit re-identification and inference attacks should be distinguished from abundant anonymous-authentication protocols. Few direct modeling or empirical attack studies can coexist with many mitigation papers. Full-text reading should check assumed trust/collusion, whether linkability follows users across services, and which data flows the model omits; metadata does not establish those limitations for every paper.

## Preserved unresolved literature

All 140 MAYBE records are retained separately and unchanged in results/maybe.csv, with an exact copy in results/maybe_for_further_review.csv. They were not promoted, excluded or assigned priorities in this run. Their full-text assessment may change apparent coverage gaps. This report describes the INCLUDE set, not all retrieved literature.

## Reproduce and resume

- python3 scripts/prioritize_papers.py next: display the next unassessed batch using only title, abstract, keywords and paper ID.
- python3 scripts/prioritize_papers.py save: validate compact session assessments, immediately save results/prioritization_batches/batch_*.json, and regenerate outputs.
- python3 scripts/prioritize_papers.py export: validate saved assessments and deterministically regenerate the CSVs and report without model calls.
- The manifest fingerprints inputs and rubric; input changes require an explicitly revised run. Never replace the original semantic classifications with priorities.

## Input fingerprints

- results/included.csv: `66e8a55f3d9f3d467e1fe3925cb3cd0ad49d05b842ca2d0c6936457723aa12c2`.
- results/maybe.csv: `9a6efd94330bd717171635bd1f271dc236f7f00640144e7f14ee5dc7755514d9`.
- config/screening_criteria.md: `e09d7dad23e6afdd1b44d4b81a1d1e86178316b8cd87fa6ec3239cd2ff0ae7a6`.
- config/prioritization_rubric.json: `45475bd9c70e40faee6661964026d274904ad5ca852cfa3712c1c72f8fd35931`.
