# Preliminary seminar-paper outline

## Suggested research question

**Which privacy threats arise from the collection, communication and cross-stakeholder use of mobility data, how do existing studies model the relevant adversaries and exposure conditions, and where do their assumptions limit the protection of affected people?**

Working title: Threat Modeling with Regard to the Mobility Domain. The conceptual scope includes multiple mobility services; the present evidence base is predominantly connected vehicles/V2X. Disclose this imbalance or explicitly narrow the final question after full-text review; do not imply all mobility domains are equally covered.

Supporting questions: (1) Which data, actors and trust boundaries enable tracking, linkage, identification, inference or disclosure? (2) What evidence supports the identified threats? (3) What assumptions and trade-offs remain in threat-specific mitigations?

## Preliminary chapter structure

### 1. Introduction and review approach

Motivate privacy in mobility, delimit the neighboring framework topic, state the research question and document retrieval/screening/priority stages. Report the selected-corpus and abstract-only limits. Use the local screening criteria and workflow reports for the review method; the papers below only motivate the problem.

Relevant literature:

- **A Threat Model for Soft Privacy on Smart Cars** (2023; `paper_1ac697087f1f5fb1bee01105125a065b`) — motivation and privacy-control framing
- **A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems** (2023; `paper_108e36360e5b5ac9bafdb4bcce2220fd`) — service-based privacy motivation

### 2. Mobility systems, personal data and stakeholders

Describe a reference vehicle–device–RSU–cloud–service data flow, affected people, identities, location/trajectory and behavioral data. Separate architectures from specific services and disclose the vehicle-heavy evidence base.

Relevant literature:

- **User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN** (2023; `paper_e4abc744a7f25dff9c93f5dc15b885a3`) — vehicle/device/cloud interactions
- **Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy** (2025; `paper_ddd332dd15385498b54d3b3a2f989719`) — third-party sharing and policy boundaries
- **Dual Privacy-Preserving Lightweight Navigation System for Vehicular Networks** (2022; `paper_65688dd1e50258cebcab20ce0c147425`) — identity versus route data
- **Ultra-Lightweight and Secure Blockchain-Assisted Charging Scheduling Scheme for Vehicular Edge Networks by Utilization of NanoPi NEO** (2022; `paper_cdfa597ef0f855cea5377e091e16f70f`) — charging-service observer

### 3. Privacy threats and supporting evidence

Organize by exposure mechanism: tracking/surveillance; identity and trajectory correlation; data disclosure/control; inference. Tie each claim to an adversary and harm. Distinguish primary experiments, analytical failures, secondary surveys and defense evaluations.

Relevant literature:

- **Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario** (2023; `paper_aaccc95774275d8dbe435e6f12eb3677`) — experimental tracking despite pseudonyms
- **A Secure and Privacy-Preserved Road Condition Monitoring System** (2020; `paper_517c3429051d52d78c620dd4b57a4610`) — analytical trajectory disclosure through RSU collusion
- **A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems** (2023; `paper_108e36360e5b5ac9bafdb4bcce2220fd`) — secondary synthesis of service-specific threats
- **Secure Resource Allocation for LTE-Based V2X Service** (2018; `paper_9c675835c4495d9fbc5c1e887de01cf9`) — resource-allocation location exposure
- **A Secure Object Detection Technique for Intelligent Transportation Systems** (2024; `paper_5df36478f1b154678e46ecf6a565ab0c`) — learning-related inference; attack/defense metrics need verification
- **A Sanitizable Access Control With Policy-Protection for Vehicular Social Networks** (2024; `paper_0b8c8127b259527fa88bc12adba3b5c3`) — sensitive access-policy information

### 4. Concrete threat models and their assumptions

Compare the modeled systems, data, observers, capabilities, trust boundaries and privacy properties. Use framework names only to explain how a paper derived concrete threats. Examine semi-honest versus malicious behavior, collusion, insider/authority compromise and physical access.

Relevant literature:

- **A Threat Model for Soft Privacy on Smart Cars** (2023; `paper_1ac697087f1f5fb1bee01105125a065b`) — privacy assets/threat agents
- **User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN** (2023; `paper_e4abc744a7f25dff9c93f5dc15b885a3`) — applied user-centric threat model
- **A baseline threat and mitigation model for automotive cybersecurity and privacy** (2026; `paper_c66d5051f881504287f45d8f7a825cdb`) — automotive asset/threat/control mapping
- **Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy** (2025; `paper_ddd332dd15385498b54d3b3a2f989719`) — semi-honest cross-organization model
- **Blockchain-Based One-Time Authentication for Secure V2X Communication Against Insiders and Authority Compromise Attacks** (2023; `paper_d6bfc521f64b565ba00636fbf9a668b6`) — insider and compromised-authority scenario
- **Efficient and Privacy-Preserving Ad Conversion for V2X-Assisted Proximity Marketing** (2018; `paper_44108b65f1f759118cf68a911eeb1787`) — malicious-party assumption
- **Physically Secure Lightweight and Privacy-Preserving Message Authentication Protocol for VANET in Smart City** (2021; `paper_f22e9e553f2a5009bd811ea285c3743c`) — physical compromise and linked safety messages
- **Human-Artificial Intelligent Threat Modelling in the Automotive Domain** (2025; `paper_843c0c6527ce546caf6d5e078a8e3325`) — supporting applied-model extension; verify privacy outputs and evidence overlap

### 5. Threat-specific mitigations and residual questions

Link defenses back to the threat assumptions: pseudonyms, anonymity/linkability controls, access policies, aggregation/differential privacy and data deidentification. Discuss accountability and utility trade-offs. Do not rank mechanisms by runtime or assume a security proof covers all privacy exposures.

Relevant literature:

- **Achieving Adaptive Linkability for Cellular V2X Group Communications in 5G** (2018; `paper_9aaa8de3af10531ba32bcee0dd4ce7fa`) — user-controlled linkability
- **Privacy-enhanced capabilities for VANETs using direct anonymous attestation** (2017; `paper_5832900a48695c129790ad4eb98aebf2`) — trust and revocation limitations
- **A Privacy-Preserving Misbehavior Detection System in Vehicular Communication Networks** (2021; `paper_ef081d1fd5ee5cfaabe0e6c9d3a3c48a`) — security-monitoring/privacy interaction
- **Privacy-Preserving Continuous Data Collection for Predictive Maintenance in Vehicular Fog-Cloud** (2021; `paper_4d9c36fb75ed5c5e94bde3969fb8b428`) — continuous collection and privacy error
- **GAN-based Deidentification of Drivers’ Face Videos: An Assessment of Human Factors Implications in NDS Data** (2023; `paper_d9810e2960f2526983466dc6915112d1`) — driver-video deidentification and utility
- **Lightweight and Provably Secure Privacy-Preserving Implicit Authentication Protocol Using Weighted-MinHash for IoV Environment** (2025; `paper_0e49ffacf5dd568b922a259f06945c16`) — non-colluding dual-cloud assumption
- **A Privacy-Preserving Data Sharing Scheme Based on Blockchain for Vehicular Edge Networks** (2023; `paper_8634f94e8b445464bba30b58ddb29e36`) — consent-based sharing

### 6. Cross-paper synthesis, limitations and open questions

Test whether reported models capture realistic stakeholder power, composition across services, repeated observations and downstream data use. State the limits of this review and identify targeted retrieval/full-text needs. Treat apparent domain/threat gaps as selected-corpus observations.

Relevant literature:

- **Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario** (2023; `paper_aaccc95774275d8dbe435e6f12eb3677`) — limits of pseudonym-only protection
- **An Unlinkable Authenticated Key Agreement With Collusion Resistant for VANETs** (2021; `paper_6839e29e40785a81a849ce7166a564e6`) — shared-record correlation under collusion
- **Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy** (2025; `paper_ddd332dd15385498b54d3b3a2f989719`) — persistence of control after sharing
- **A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems** (2023; `paper_108e36360e5b5ac9bafdb4bcce2220fd`) — reported service-specific limitations and future directions
- **Design of a Provable Secure ECC and HMAC-Based Robust and Efficient Authentication Scheme for Maritime Transportation System** (2025; `paper_69d6c52c7b355f1ebf8fd342ab55b81c`) — a complementary domain rather than a comprehensive survey of maritime privacy

### 7. Conclusion

Answer the research question using verified full-text evidence from preceding chapters. Separate established exposures, model-dependent claims and unresolved questions. Add no new effectiveness or field-wide trend claims.

Relevant literature:

- **A Threat Model for Soft Privacy on Smart Cars** (2023; `paper_1ac697087f1f5fb1bee01105125a065b`) — return to privacy harms and assets
- **Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario** (2023; `paper_aaccc95774275d8dbe435e6f12eb3677`) — recall empirical evidence limits
- **User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN** (2023; `paper_e4abc744a7f25dff9c93f5dc15b885a3`) — connect the conclusions to mobility data flows

## Evidence extraction during full-text reading

For each retained source, extract: studied system and data flow; affected people and data; observer/stakeholder; adversary capabilities and collusion; trust boundaries; privacy harm and attack mechanism; reported evidence/method; assumptions; mitigation and residual exposure; source section/page. Distinguish source findings from your cross-paper interpretation. Mark secondary evidence and overlapping models to avoid double counting. Record unreported details as unknown.

Use the four LOW papers only if full text clarifies their personal-privacy contribution. Resolve the separate MAYBE and validation queues before treating the final corpus as settled. The matrix is a planning tool, not a completed full-text extraction table.

## Topics outside the main scope

- Generic STRIDE-versus-LINDDUN comparisons, framework catalogs, framework usability benchmarking or new framework development. Mention methods briefly when needed to explain a concrete mobility privacy result.
- Pure authentication/signature security, integrity, availability, routing, congestion or mechanical safety without a substantive personal-privacy connection.
- Exhaustive cryptographic performance/post-quantum/blockchain comparisons. Include a mechanism only to explain the privacy threat, assumptions or residual risk.
- General privacy law/compliance surveys; use legal requirements as context where they illuminate data control and stakeholder obligations, not as unsupported legal conclusions.
- Claims of field-wide research trends, universal domain coverage or verified mitigation effectiveness based on this selected, abstract-only corpus.
- Full treatment of infrastructure-as-code/process-centric modeling unless the final research question is explicitly amended; the current screening criteria do not make those approaches a requirement.

All proposed chapter claims and source placements are tentative. No full papers were read for this outline. Applied framework papers remain central where they produce mobility privacy analysis.
