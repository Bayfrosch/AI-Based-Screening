# Literature overview

## Scope and evidence limits

This overview covers all 162 prioritized INCLUDE records: HIGH=38, MEDIUM=120, LOW=4. Only titles, supplied abstracts and keywords were used for content analysis; years identify sources. No full papers were read. Original semantic decisions, roles and priorities are preserved. The unresolved MAYBE queue is outside this overview, not evidence of irrelevance.

The authoritative scope is config/screening_criteria.md: identify and explain mobility privacy threats, affected data, adversaries and exposure conditions. Applied LINDDUN/STRIDE analyses qualify; general framework comparison is not the organizing question. Screening INCLUDE means advance to full text, not verified final eligibility.

**Abstract-supported** below means the source abstract explicitly reports a topic, method or result; its validity was not independently checked. **Interpretation** means a proposed seminar use, relationship or coverage gap. The matrix records exact metadata evidence for reviewed annotations and literal method cues for other papers. Method cues still need attribution checking: a mention of a technique can concern related work. No quantitative attack success rates or comparative effectiveness are inferred.

Counts describe this selected corpus only. They do not establish field-wide trends, completeness of retrieval or the absence of work elsewhere. Categories overlap. Domain subcategories use explicit title terms; the broad connected-vehicle label and four threat themes retain the earlier metadata assessment. Title-only subcategory counts are lower-bound indicators, not a full domain census.

## Mobility systems represented

| Metadata-supported system/architecture label | Papers |
| --- | ---: |
| Connected vehicles/V2X/VANETs | 157 |
| Fog/cloud/edge vehicular infrastructure | 37 |
| Vehicle sensing/learning/driver imagery | 8 |
| Vehicular social networks | 7 |
| Vehicular platooning | 4 |
| Road-condition monitoring | 3 |
| Electric-vehicle charging/grid/battery services | 3 |
| UAV/drone-assisted transportation | 3 |
| Advertising/proximity marketing | 2 |
| Navigation/location-based services | 2 |
| Vehicular crowdsensing | 2 |
| Intelligent transportation systems (service unspecified) | 2 |
| Electronic toll collection | 1 |
| Maritime transportation | 1 |

Connected vehicles/V2X are the dominant broad label (157/162). Specific services include electronic toll collection, road monitoring, navigation, vehicular crowdsensing, advertising and electric-vehicle services. Generic VANET/C-V2X papers should not be counted as studies of public transport or autonomous driving merely because the abstract mentions those applications. No dedicated public-transport/MaaS paper was identified by the existing thematic assessment.

## Privacy threats and protection topics

| Topic | Papers | Counting basis |
| --- | ---: | --- |
| Location tracking and surveillance | 25 | Reviewed thematic tag; risk or defense topic |
| Re-identification | 5 | Reviewed thematic tag; risk or defense topic |
| Trajectory linking and correlation | 8 | Reviewed thematic tag; risk or defense topic |
| Inference attacks | 1 | Reviewed thematic tag; risk or defense topic |
| Identity disclosure/anonymity (risk or protection topic) | 94 | Explicit metadata vocabulary; risk or protection, not an attack count |
| Data disclosure/confidentiality (risk or protection topic) | 36 | Explicit metadata vocabulary; risk or protection, not an attack count |
| Privacy exposure insufficiently specified in metadata | 31 | No indexed specific threat established; not an exclusion |
| Record/message linkability (not necessarily trajectory linking) | 17 | Explicit metadata vocabulary; risk or protection, not an attack count |
| Control over personal-data use/access | 6 | Explicit metadata vocabulary; risk or protection, not an attack count |

Among the four specific attack-related themes, tracking/surveillance has the largest count, followed by trajectory correlation, re-identification and inference. Broader identity/anonymity and message-linkability protection claims are common, but are not equivalent to empirical tracking, re-identification or inference evidence. Unauthorized data disclosure, consent/control and cross-stakeholder trust supply additional privacy perspectives. Authorized revocation/traceback is an accountability feature, not automatically surveillance.

## Main research areas and their seminar use

### Applied privacy threat analysis (35 tagged papers)

Assets, data flows, threat agents and privacy attack assumptions; includes adversary analysis embedded in defenses.

- **A Threat Model for Soft Privacy on Smart Cars** (2023; `paper_1ac697087f1f5fb1bee01105125a065b`). **Abstract-supported:** Maps soft-privacy threats to automotive assets and threat agents. **Potential contribution:** Use a privacy-specific organizing model centered on control of personal data.
- **User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN** (2023; `paper_e4abc744a7f25dff9c93f5dc15b885a3`). **Abstract-supported:** Applies STRIDE/LINDDUN to a theoretical connected-vehicle architecture. **Potential contribution:** Explain user-facing exposure paths across devices, vehicles and cloud systems.
- **A baseline threat and mitigation model for automotive cybersecurity and privacy** (2026; `paper_c66d5051f881504287f45d8f7a825cdb`). **Abstract-supported:** Reports automotive assets, threats and mitigation/control mapping. **Potential contribution:** Connect threats to assets and controls; extract privacy-specific content.
- **Human-Artificial Intelligent Threat Modelling in the Automotive Domain** (2025; `paper_843c0c6527ce546caf6d5e078a8e3325`). **Abstract-supported:** Reports iterative human–AI automotive threat elicitation with privacy-oriented mitigation phases. **Potential contribution:** Check concrete privacy results and shared models; treat method novelty as supporting context.

### Tracking, identification and correlation (31 tagged papers)

Movement exposure, identity linkage and pseudonym/message correlation; anonymity claims alone are not re-identification experiments.

- **Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario** (2023; `paper_aaccc95774275d8dbe435e6f12eb3677`). **Abstract-supported:** Reports vehicle tracking despite five pseudonym-change strategies. **Potential contribution:** Explain how correlation undermines identifier changes.
- **A Secure and Privacy-Preserved Road Condition Monitoring System** (2020; `paper_517c3429051d52d78c620dd4b57a4610`). **Abstract-supported:** Reports colluding RSUs revealing trajectories and anonymity failures. **Potential contribution:** Show privacy consequences of cooperative infrastructure observers.
- **Dual Privacy-Preserving Lightweight Navigation System for Vehicular Networks** (2022; `paper_65688dd1e50258cebcab20ce0c147425`). **Abstract-supported:** Separates PII from origin/destination, route and location. **Potential contribution:** Explain the distinction between route secrecy and identity–route linkage.
- **A Conditional Privacy Protection Scheme Based on Ring Signcryption for Vehicular Ad Hoc Networks** (2021; `paper_ae49e51ea8bf587880def3526d61ddaf`). **Abstract-supported:** Connects identity exposure to targeted driver tracking by a stalker. **Potential contribution:** Illustrate privacy harm beyond a cryptographic property.

### Anonymous authentication and accountability (99 tagged papers)

Pseudonyms, unlinkability, revocation and authorized tracing; distinguish authority accountability from hostile surveillance.

- **Achieving Adaptive Linkability for Cellular V2X Group Communications in 5G** (2018; `paper_9aaa8de3af10531ba32bcee0dd4ce7fa`). **Abstract-supported:** Introduces user-controlled linking in C-V2X group communication. **Potential contribution:** Discuss who controls linkability and its service-specific necessity.
- **Privacy-enhanced capabilities for VANETs using direct anonymous attestation** (2017; `paper_5832900a48695c129790ad4eb98aebf2`). **Abstract-supported:** Analyzes pseudonym reuse/revocation limitations and shifting trust toward vehicles. **Potential contribution:** Contrast privacy assumptions of infrastructure and vehicle-controlled credentials.
- **Post-Quantum Anonymous, Traceable and Linkable Authentication Scheme Based on Blockchain for Intelligent Vehicular Transportation Systems** (2024; `paper_20b078a101d9585393662ec073f59186`). **Abstract-supported:** Explicitly describes conflicts between tracing/linking and sender identity privacy. **Potential contribution:** Use the accountability trade-off; avoid a general post-quantum comparison.
- **SWATS: A Lightweight VANET Anonymous Traceback System Based on Random Superposition Watermarking** (2018; `paper_82db1b521cd15a33a9df39b884cdfc5e`). **Abstract-supported:** Uses watermarking to reconstruct paths for controlled traceback. **Potential contribution:** Ask when authorized tracing becomes an exposure risk.

### Data sharing, aggregation and stakeholder trust (23 tagged papers)

Outsourcing, access policies, continuous collection and protection across organizational boundaries.

- **Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy** (2025; `paper_ddd332dd15385498b54d3b3a2f989719`). **Abstract-supported:** Evaluates persistent access policies across organizations under a semi-honest model. **Potential contribution:** Analyze privacy after data crosses organizational boundaries.
- **A Sanitizable Access Control With Policy-Protection for Vehicular Social Networks** (2024; `paper_0b8c8127b259527fa88bc12adba3b5c3`). **Abstract-supported:** Addresses malicious publishers and sensitive access-policy attribute values. **Potential contribution:** Expose privacy risks carried by metadata and authorization policy.
- **A Privacy-Preserving Data Sharing Scheme Based on Blockchain for Vehicular Edge Networks** (2023; `paper_8634f94e8b445464bba30b58ddb29e36`). **Abstract-supported:** Reports owner-consent access control and tracking of illegal transfers. **Potential contribution:** Discuss control over sharing and recipient responsibilities.
- **P2BA: A Privacy-Preserving Protocol With Batch Authentication Against Semi-Trusted RSUs in Vehicular Ad Hoc Networks** (2021; `paper_06633fe9993854879674223304e94422`). **Abstract-supported:** Names data association/privacy mining by adversaries and semi-trusted RSUs. **Potential contribution:** Introduce stakeholder misuse beyond an external network attacker.

### Learning, behavioral and visual data privacy (10 tagged papers)

Driver features, images and collaborative learning; separate privacy-attack evaluation from task accuracy or runtime tests.

- **A Secure Object Detection Technique for Intelligent Transportation Systems** (2024; `paper_5df36478f1b154678e46ecf6a565ab0c`). **Abstract-supported:** Evaluates a federated object-detection defense against inference and poisoning on named datasets. **Potential contribution:** Distinguish inference privacy risks from model integrity attacks.
- **Lightweight and Provably Secure Privacy-Preserving Implicit Authentication Protocol Using Weighted-MinHash for IoV Environment** (2025; `paper_0e49ffacf5dd568b922a259f06945c16`). **Abstract-supported:** Protects behavioral authentication features under a semi-honest non-colluding dual-cloud assumption. **Potential contribution:** Show sensitivity of driver features and the importance of collusion assumptions.
- **GAN-based Deidentification of Drivers’ Face Videos: An Assessment of Human Factors Implications in NDS Data** (2023; `paper_d9810e2960f2526983466dc6915112d1`). **Abstract-supported:** Evaluates driver-face swapping on driving datasets while retaining research attributes. **Potential contribution:** Discuss data sharing and privacy–utility questions without claiming demonstrated anonymity.
- **Privacy-Preserving Continuous Data Collection for Predictive Maintenance in Vehicular Fog-Cloud** (2021; `paper_4d9c36fb75ed5c5e94bde3969fb8b428`). **Abstract-supported:** Analyzes continuous sensing with aggregation and differential-privacy error. **Potential contribution:** Discuss repeated collection and the utility cost of privacy protection.

### Service-specific privacy exposures (21 tagged papers)

Tolls, navigation, crowdsensing, advertising, charging, platooning and maritime examples anchor abstract threats in services.

- **A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems** (2023; `paper_108e36360e5b5ac9bafdb4bcce2220fd`). **Abstract-supported:** Surveys toll systems, location tracking, collusion and physical attacks. **Potential contribution:** Anchor the review in a service where repeated observation has a clear mobility meaning.
- **Achieving Efficient and Privacy-Preserving Worker Selection With Arbitrary Spatial Ranges for Vehicular Crowdsensing** (2024; `paper_6d7068f463c35c2698ef5c000ca34c95`). **Abstract-supported:** Identifies future-trajectory disclosure to a not-fully-trusted task platform. **Potential contribution:** Compare participant/query-user exposures and service-specific trust boundaries.
- **Efficient and Privacy-Preserving Ad Conversion for V2X-Assisted Proximity Marketing** (2018; `paper_44108b65f1f759118cf68a911eeb1787`). **Abstract-supported:** Allows advertising parties to deviate maliciously from the protocol. **Potential contribution:** Contrast semi-honest and malicious assumptions in commercial mobility services.
- **Ultra-Lightweight and Secure Blockchain-Assisted Charging Scheduling Scheme for Vehicular Edge Networks by Utilization of NanoPi NEO** (2022; `paper_cdfa597ef0f855cea5377e091e16f70f`). **Abstract-supported:** Addresses honest-but-curious edge nodes during charging communication. **Potential contribution:** Test whether threat dimensions transfer from messaging to charging services.
- **Design of a Provable Secure ECC and HMAC-Based Robust and Efficient Authentication Scheme for Maritime Transportation System** (2025; `paper_69d6c52c7b355f1ebf8fd342ab55b81c`). **Abstract-supported:** Names vessel-location tracking and proposes anonymous authentication. **Potential contribution:** Offer a complementary transport-domain example without implying broad maritime coverage.

### Supplementary or unresolved privacy mechanisms (23 tagged papers)

Retained literature whose central privacy usefulness needs clarification; no eligibility decision is changed.

- **Attack Identification and Classification in V2X Scenarios** (2024; `paper_f361231c25105a2ea7ad0df89379bdbf`). **Abstract-supported:** Mentions interception/eavesdropping in position-bearing V2X exchanges. **Potential contribution:** Use only if full text supplies privacy-specific attack classification detail.
- **Advancing IoT-Driven Transportation Security: A Comprehensive Review of Privacy-Preserving Identity-Based Encryption With Quantum Enhancements** (2026; `paper_5a98bfb6b0335f888eee7fe3f269bb9f`). **Abstract-supported:** Synthesizes encryption/key-escrow limitations in transportation contexts. **Potential contribution:** Support the authority-trust discussion rather than cryptographic benchmarking.
- **Bilateral Control for Secure Communication Against Replay Attack in ORAN-Based Vehicular Networks** (2025; `paper_0398c7540e02547b91fda85abb322e0b`). **Abstract-supported:** Reports access control against replay in vehicular networks. **Potential contribution:** Retain as LOW until full text clarifies personal-privacy relevance.

## Concrete threat models and adversary assumptions

A targeted abstract review identifies 6 papers explicitly reporting a mobility privacy or mixed security/privacy model. These are positive identifications, not an exhaustive full-text model census. Another 20 annotated papers describe concrete privacy-relevant adversaries, exposures or attack scenarios without establishing a complete formal privacy model. Other rows remain NOT_ESTABLISHED rather than being labeled model-free.

| Paper | Model reported in abstract | Verification needed |
| --- | --- | --- |
| Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario (`paper_aaccc95774275d8dbe435e6f12eb3677`) | A realistic attacker monitors and correlates multiple messages to track vehicles across pseudonym changes; exact observation powers need full text. | Assets, data flows, adversary powers, scope and privacy-specific results |
| Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy (`paper_ddd332dd15385498b54d3b3a2f989719`) | Semi-honest threat model for vehicle data shared with clouds, RSUs and third parties; sticky user policies persist across organizational boundaries. | Assets, data flows, adversary powers, scope and privacy-specific results |
| A Threat Model for Soft Privacy on Smart Cars (`paper_1ac697087f1f5fb1bee01105125a065b`) | Soft-privacy threat model considers threat agents and maps domain-independent threats to automotive assets; abstract reports 17 threats and 41 assets. | Assets, data flows, adversary powers, scope and privacy-specific results |
| User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN (`paper_e4abc744a7f25dff9c93f5dc15b885a3`) | User-centric model examines V2V, vehicle-to-cloud and vehicle-to-device interactions and personal-data disclosure/unauthorized access. | Assets, data flows, adversary powers, scope and privacy-specific results |
| A baseline threat and mitigation model for automotive cybersecurity and privacy (`paper_c66d5051f881504287f45d8f7a825cdb`) | Mixed cybersecurity/privacy baseline maps high-level and fine-grained automotive assets, threats and mitigations; privacy-specific findings need full text. | Assets, data flows, adversary powers, scope and privacy-specific results |
| Human-Artificial Intelligent Threat Modelling in the Automotive Domain (`paper_843c0c6527ce546caf6d5e078a8e3325`) | Automotive threat model with system/asset/threat refinement and pseudonymisation/data minimisation; abstract does not enumerate concrete privacy outcomes. | Assets, data flows, adversary powers, scope and privacy-specific results |

Concrete scenario/adversary examples:

- **A Secure and Privacy-Preserved Road Condition Monitoring System** (2020; `paper_517c3429051d52d78c620dd4b57a4610`): Trusted-but-curious RSUs can collude and reveal vehicle trajectories; anonymity and unlinkability failures are reported.
- **Blockchain-Based One-Time Authentication for Secure V2X Communication Against Insiders and Authority Compromise Attacks** (2023; `paper_d6bfc521f64b565ba00636fbf9a668b6`): Insider vehicles exploit network/member communication; compromised registration authorities leak identity, location and membership.
- **An Unlinkable Authenticated Key Agreement With Collusion Resistant for VANETs** (2021; `paper_6839e29e40785a81a849ce7166a564e6`): Colluding RSUs or vehicles link blockchain-retrieved records and defeat anonymity; V2R/V2V unlinkability is the defense goal.
- **Efficient and Privacy-Preserving Ad Conversion for V2X-Assisted Proximity Marketing** (2018; `paper_44108b65f1f759118cf68a911eeb1787`): Ad networks and merchants may arbitrarily deviate from the protocol; customer inputs and unlinkability are privacy goals.
- **A Sanitizable Access Control With Policy-Protection for Vehicular Social Networks** (2024; `paper_0b8c8127b259527fa88bc12adba3b5c3`): Malicious data publishers cause breaches; access-policy attribute values reveal receiver private information.
- **Lightweight and Provably Secure Privacy-Preserving Implicit Authentication Protocol Using Weighted-MinHash for IoV Environment** (2025; `paper_0e49ffacf5dd568b922a259f06945c16`): Sensitive behavioral authentication features are processed in a semi-honest, non-colluding dual-cloud environment; assumptions need full-text scrutiny.
- **Dual Privacy-Preserving Lightweight Navigation System for Vehicular Networks** (2022; `paper_65688dd1e50258cebcab20ce0c147425`): RSUs and the navigation provider must not link location, origin/destination and route to PII; exact collusion powers need full text.
- **Achieving Efficient and Privacy-Preserving Worker Selection With Arbitrary Spatial Ranges for Vehicular Crowdsensing** (2024; `paper_6d7068f463c35c2698ef5c000ca34c95`): Workers upload future trajectories to a not-fully-trusted platform; platform/fog-server interactions and query-user location are privacy concerns.
- **Ultra-Lightweight and Secure Blockchain-Assisted Charging Scheduling Scheme for Vehicular Edge Networks by Utilization of NanoPi NEO** (2022; `paper_cdfa597ef0f855cea5377e091e16f70f`): Honest-but-curious edge nodes observe electric-vehicle charging communication; anonymity and accountability are explicit goals.
- **A Privacy-Preserving Misbehavior Detection System in Vehicular Communication Networks** (2021; `paper_ef081d1fd5ee5cfaabe0e6c9d3a3c48a`): Misbehavior-detection trust and feedback scores may expose location, trajectory or identity; trusted authority decrypts aggregate feedback.

A random-oracle, Real-or-Random or eCK protocol-security model is not automatically a comprehensive privacy model. Check which secrets and privacy properties it formalizes and whether it covers tracking, collusion, legitimate data recipients and inference. The matrix does not promote every formal-proof paper to concrete threat-model evidence.

## Empirical threat evidence versus analysis and mitigation tests

- **Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario** (2023; `paper_aaccc95774275d8dbe435e6f12eb3677`) — **EMPIRICAL_PRIVACY_ATTACK_EVALUATION_REPORTED**: The abstract reports five pseudonym-change mechanisms and reliable multi-vehicle tracking by a realistic attacker. Traffic source, simulation/deployment setting and success metrics are unspecified.
- **Security Analysis on an Efficient and Provably Secure Authenticated Key Agreement Protocol for Fog-Based Vehicular Ad-Hoc Networks** (2021; `paper_32401c5eea69516fbee23bcc315dfa8e`) — **ANALYTICAL_PRIVACY_FAILURE_REPORTED**: The abstract reports identity/anonymity and secret-key failures of a predecessor protocol. It does not establish a measured empirical privacy attack.
- **A Secure and Privacy-Preserved Road Condition Monitoring System** (2020; `paper_517c3429051d52d78c620dd4b57a4610`) — **ANALYTICAL_PRIVACY_FAILURE_REPORTED**: The abstract reports collusion-induced trajectory disclosure and anonymity failures; no empirical attack measurement or deployment is specified.
- **A Secure Object Detection Technique for Intelligent Transportation Systems** (2024; `paper_5df36478f1b154678e46ecf6a565ab0c`) — **DATASET_BASED_PRIVACY_ATTACK_DEFENSE_EVALUATION_REPORTED**: Evaluates a defense against model replacement and inference attacks on named datasets. Abstract does not separate inference-attack success, task utility or real-vehicle deployment.
- **GAN-based Deidentification of Drivers’ Face Videos: An Assessment of Human Factors Implications in NDS Data** (2023; `paper_d9810e2960f2526983466dc6915112d1`) — **DATASET_BASED_DEIDENTIFICATION_UTILITY_EVALUATION_REPORTED**: Experiments assess face swapping and preservation of eye/head/mouth attributes in driving data. The abstract does not demonstrate a re-identification attack or establish residual anonymity guarantees.
- **Security Analysis of an Identity-Based Signature From Factorization Problem** (2020; `paper_8bc2f5637091514d9ff00f30f0dc75d9`) — **EXPERIMENTAL_SECURITY_FAILURE_REPORTED_PRIVACY_IMPACT_UNRESOLVED**: Key disclosure is analyzed theoretically and experimentally. The abstract motivates sensitive VANET data but does not measure a personal-data privacy attack.
- **Ultra-Lightweight and Secure Blockchain-Assisted Charging Scheduling Scheme for Vehicular Edge Networks by Utilization of NanoPi NEO** (2022; `paper_cdfa597ef0f855cea5377e091e16f70f`) — **IMPLEMENTATION_BENCHMARK_REPORTED_NOT_ATTACK_EVIDENCE**: ARM and blockchain implementations establish a reported engineering evaluation; the abstract does not report measured privacy leakage or attack success.
- **A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems** (2023; `paper_108e36360e5b5ac9bafdb4bcce2220fd`) — **SECONDARY_ATTACK_EVIDENCE**: Reviews schemes and attack resistance; not a new primary empirical attack study. Follow original sources before counting attack evidence.

The pseudonym-tracking experiment is the clearest directly reported empirical tracking example in this metadata review. Analytical counterexamples, surveys of attacks, privacy-defense datasets and runtime benchmarks are different evidence types. Dataset names alone do not demonstrate a privacy attack, real-world deployment or representative attack success. Full-text checks should separate synthetic/simulated traffic, recorded traces, physical deployments and human participants.

## Mitigation-oriented literature

Original roles: CORE=7, THREAT_EVIDENCE=2, MITIGATION=153. The later reading-purpose assessment distinguishes DIRECT_THREAT_ANALYSIS=8, THREAT_SPECIFIC_MITIGATION=113, GENERAL_PRIVACY_MITIGATION=41. These fields answer different questions and must not be interchanged. A MITIGATION source can also contain a valuable threat scenario.

The matrix identifies every primarily defensive paper using the unchanged research_role and contribution_focus. Representative mechanisms include conditional anonymity/pseudonyms, anonymous authentication, user-controlled linkability, access-control/proxy re-encryption, privacy-preserving aggregation, differential privacy, federated-learning protection and face deidentification. Use these sources to explain addressed exposures, assumptions and residual questions; avoid turning the seminar into a protocol-efficiency catalog. No mitigation is treated as effective merely because its abstract asserts security.

## Relationships between themes — synthesis hypotheses

These connections organize the seminar; they are reviewer interpretations to test against full text:

1. **Assets/data flows → observers → exposures.** Start from vehicle-to-device/cloud/infrastructure interactions, then locate identities, routes, behavior and access-policy data at trust boundaries.
2. **Anonymity → correlation → identification.** Pseudonyms hide explicit identifiers, yet message timing, movement patterns or colluding observers may restore linkage. Linkage is an enabling condition; it is not necessarily proof of real-identity recovery.
3. **Security monitoring/accountability ↔ privacy.** Misbehavior feedback, traceability and revocation create useful safety/security controls while raising questions about who may link identities or reconstruct trips.
4. **Cloud/edge outsourcing → stakeholder power.** Honest-but-curious providers, colluding RSUs and compromised authorities require different assumptions; encryption alone does not establish appropriate downstream data use.
5. **Data utility ↔ exposure.** Learning, maintenance and human-factors data motivate collection; differential privacy, aggregation and deidentification provide different protection goals and utility questions.

## Apparent gaps and full-text questions

The following are gaps in the selected metadata coverage or unresolved evidence questions, not established research gaps across the field:

- **Mobility breadth:** no dedicated public-transport/MaaS theme; ride-sharing, multi-operator travel apps and longitudinal cross-service trip data have little explicit representation. Extend retrieval and revisit MAYBE records before claiming absence.
- **Threat breadth:** inference (1 tagged paper) and explicit re-identification (5) have limited coverage compared with identity-protection protocols. Profiling, aggregation harms and excessive legitimate collection need targeted full-text checks rather than being assumed absent.
- **Evidence breadth:** few clearly described empirical privacy-attack evaluations; many abstracts report proofs, security analyses or efficiency experiments. Extract attack conditions, adversary access and what was actually measured before comparing findings.
- **Organizational/lifecycle coverage:** consent, cross-boundary reuse and semi-honest stakeholders appear in some sources, but coverage of retention, downstream sharing, actor collusion and multi-service composition remains unresolved.
- **Model adequacy:** mixed security/privacy models can emphasize assets and cryptographic correctness. Check whether the privacy claims address affected people, legitimate recipients and inference beyond network attackers.
- **Evidence independence:** the SCAR baseline and human–AI automotive-model papers have related subject matter; check shared authors, models and versions before treating them as independent findings. Similarly, cryptanalysis and improved-scheme papers may discuss the same predecessor. Surveys provide secondary evidence, not additional independent attacks.
- **Selection uncertainty:** LOW still means INCLUDE pending full-text eligibility checks. Prior roles and priorities are inherited judgments, not validation labels. This overview does not resolve earlier manual-validation flags or examine the MAYBE queue.

## Recommended reading order

Read for argument structure and threat coverage, not publication year. This sequence is a starting path, not a limit on the HIGH queue; all remaining HIGH papers remain candidates for full-text review.

1. **A Threat Model for Soft Privacy on Smart Cars** (2023; `paper_1ac697087f1f5fb1bee01105125a065b`) — Establish privacy harms, threat agents and automotive assets.
2. **User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN** (2023; `paper_e4abc744a7f25dff9c93f5dc15b885a3`) — Map user-oriented threats onto connected-vehicle data flows.
3. **A baseline threat and mitigation model for automotive cybersecurity and privacy** (2026; `paper_c66d5051f881504287f45d8f7a825cdb`) — Inspect the asset–threat–control baseline; check relation to the human–AI model paper.
4. **A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems** (2023; `paper_108e36360e5b5ac9bafdb4bcce2220fd`) — Add a concrete service and structured secondary attack evidence.
5. **Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario** (2023; `paper_aaccc95774275d8dbe435e6f12eb3677`) — Ground linkability/tracking claims in an explicitly reported attack experiment.
6. **A Secure and Privacy-Preserved Road Condition Monitoring System** (2020; `paper_517c3429051d52d78c620dd4b57a4610`) — Examine infrastructure collusion and broken anonymity assumptions.
7. **Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy** (2025; `paper_ddd332dd15385498b54d3b3a2f989719`) — Extend analysis to data control and organizational boundaries.
8. **Secure Resource Allocation for LTE-Based V2X Service** (2018; `paper_9c675835c4495d9fbc5c1e887de01cf9`) — Check privacy leakage outside the layers covered by conventional message protection.
9. **A Privacy-Preserving Misbehavior Detection System in Vehicular Communication Networks** (2021; `paper_ef081d1fd5ee5cfaabe0e6c9d3a3c48a`) — Analyze privacy exposure introduced by a security-monitoring function.
10. **A Secure Object Detection Technique for Intelligent Transportation Systems** (2024; `paper_5df36478f1b154678e46ecf6a565ab0c`) — Add the distinct case of inference risks in collaborative learning; verify what the experiments measure.

Then follow the matrix into navigation, crowdsensing, malicious advertising parties, driver-feature/face privacy, and charging services to test whether the threat dimensions transfer across data and stakeholders. Consult the human–AI automotive paper for its applied findings; framework usability/comparison is supporting context only.

## Matrix and reproducibility

results/literature_matrix.csv contains one row per prioritized paper, with paper ID, title, year, inherited role/priority, mobility domain, privacy threats/protection topics, methods, proposed seminar contribution and full_text_review_needed=true. Additional fields distinguish model/scenario evidence, empirical evidence type and unverified method cues. Multiple labels are separated by semicolons; evidence JSON preserves exact source sentences/phrases for inspection. All source metadata remains in results/prioritized_papers.csv and is not modified.

Regenerate with `python3 scripts/build_literature_overview.py`. The script checks unique identities, annotation references, exact evidence substrings and input fingerprints before exporting. Reviewed annotations and source hashes are in config/literature_overview_annotations.json. Generic domain/threat/method rules are transparent in the script; they provide conservative topic indexing, not a new screening stage. Interpretation remains subject to full-text revision.

Synthesis version: 1.0. Source SHA-256: `8e24c0fafb86e6fa1021da44c8ad895e02fe75708f66ce88d6b3bc07d2a67e04`. Criteria SHA-256: `e09d7dad23e6afdd1b44d4b81a1d1e86178316b8cd87fa6ec3239cd2ff0ae7a6`.
