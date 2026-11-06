# Recommended 20 papers for the question in notes.md

Research question: **How well do process-centric and infrastructure-as-code threat modeling approaches identify privacy threats in a connected automobile service?**

`nodes.md` was interpreted as `notes.md`, the existing project file. This shortlist prioritizes concrete privacy models, service data flows, stakeholders/adversary assumptions, attack evidence and privacy limitations. Ranking is a seminar reading recommendation, not a measure of scientific quality or a revision of screening. All 20 were previously INCLUDE/HIGH.

These papers support the privacy-threat evidence and evaluation scenarios for the question. They do not establish a comparison of process-centric and IaC tools. No record among the 364 semantic-screening records explicitly mentions infrastructure-as-code, IaC, Terraform or CloudFormation in its title, abstract or keywords. That metadata search is not proof of absence in full text or the wider field. No paper is excluded based on terminology. Separate method-specific literature and a stated evaluation procedure are still needed for the comparative question.

The selection is based on supplied metadata only. No full papers were read. Potential uses below are reviewer interpretations; reported results require full-text verification. Applied STRIDE/LINDDUN papers are retained for their automotive privacy content. Generic framework comparison and repetitive authentication-efficiency studies are not the organizing focus.

Read ranks 1–5 first, then use ranks 6–19 to develop concrete evaluation cases. Rank 20 is supporting process literature whose privacy-specific findings need particular verification.

| Rank | Paper | Year | Why it fits |
| ---: | --- | ---: | --- |
| 1 | [A Threat Model for Soft Privacy on Smart Cars](https://doi.org/10.1109/eurospw59978.2023.00005) | 2023 | Defines automotive privacy assets, threat agents, and threats to control over personal data. |
| 2 | [User-Centric Security and Privacy Threats in Connected Vehicles: A Threat Modeling Analysis Using STRIDE and LINDDUN](https://doi.org/10.1109/dasc/picom/cbdcom/cy59711.2023.10361381) | 2023 | Maps privacy threats to vehicle, cloud and device interactions; useful for modeling service data flows. |
| 3 | [Sticky-PRE: A Sticky Proxy Re-Encryption Protocol for Persistent Vehicle Data Privacy](https://doi.org/10.1109/iv64158.2025.11097565) | 2025 | Offers cases for testing whether models capture persistent access policies and downstream data use. |
| 4 | [Are VANETs pseudonyms effective? An experimental evaluation of pseudonym tracking in adversarial scenario](https://doi.org/10.1109/vtc2023-fall60731.2023.10333561) | 2023 | Reports experimental tracking across pseudonym changes; tests whether a model captures correlation beyond identifiers. |
| 5 | [A baseline threat and mitigation model for automotive cybersecurity and privacy](https://doi.org/10.1109/iccworkshops63917.2026.11586233) | 2026 | Provides an automotive baseline for checking modeled assets, privacy threats and proposed controls. |
| 6 | [A Secure and Privacy-Preserved Road Condition Monitoring System](https://doi.org/10.1109/comsnets48256.2020.9027482) | 2020 | Identifies trajectory disclosure through colluding roadside units and failures of anonymity and unlinkability. |
| 7 | [Dual Privacy-Preserving Lightweight Navigation System for Vehicular Networks](https://doi.org/10.1109/access.2022.3222302) | 2022 | Separates identity, location, origin/destination and route privacy across roadside units and navigation providers. |
| 8 | [A Survey on Privacy-Preserving Electronic Toll Collection Schemes for Intelligent Transportation Systems](https://doi.org/10.1109/tits.2023.3266828) | 2023 | Surveys a concrete mobility service, including tracking, collusion, physical attacks and protection limitations. |
| 9 | [Secure Resource Allocation for LTE-Based V2X Service](https://doi.org/10.1109/tvt.2018.2868609) | 2018 | Identifies location leakage from resource-allocation patterns despite protection of other communication layers. |
| 10 | [Blockchain-Based One-Time Authentication for Secure V2X Communication Against Insiders and Authority Compromise Attacks](https://doi.org/10.1109/jiot.2022.3224465) | 2023 | Addresses insiders and compromised authorities leaking identity, location and membership information. |
| 11 | [P2BA: A Privacy-Preserving Protocol With Batch Authentication Against Semi-Trusted RSUs in Vehicular Ad Hoc Networks](https://doi.org/10.1109/tifs.2021.3098971) | 2021 | Discusses privacy mining and data association by semi-trusted roadside infrastructure. |
| 12 | [A Privacy-Preserving Data Sharing Scheme Based on Blockchain for Vehicular Edge Networks](https://doi.org/10.1109/globecom54140.2023.10437310) | 2023 | Connects sensitive vehicle data, owner consent and unauthorized transfers across sharing participants. |
| 13 | [A Sanitizable Access Control With Policy-Protection for Vehicular Social Networks](https://doi.org/10.1109/tits.2023.3285623) | 2024 | Explains malicious publishers and sensitive receiver attributes exposed through access policies. |
| 14 | [A Privacy-Preserving Misbehavior Detection System in Vehicular Communication Networks](https://doi.org/10.1109/tvt.2021.3079385) | 2021 | Shows why trust scores and feedback used for security monitoring can expose location, trajectory or identity. |
| 15 | [Lightweight and Provably Secure Privacy-Preserving Implicit Authentication Protocol Using Weighted-MinHash for IoV Environment](https://doi.org/10.1109/tits.2025.3605156) | 2025 | Addresses driver-feature exposure under semi-honest, non-colluding dual-cloud assumptions. |
| 16 | [Privacy-Preserving Continuous Data Collection for Predictive Maintenance in Vehicular Fog-Cloud](https://doi.org/10.1109/tits.2020.3011931) | 2021 | Connects continuous sensor collection to location/identity exposure and differential-privacy error. |
| 17 | [Efficient and Privacy-Preserving Ad Conversion for V2X-Assisted Proximity Marketing](https://doi.org/10.1109/mass.2018.00014) | 2018 | Analyzes customer-data privacy when advertising networks and merchants may deviate from the protocol. |
| 18 | [Achieving Efficient and Privacy-Preserving Worker Selection With Arbitrary Spatial Ranges for Vehicular Crowdsensing](https://doi.org/10.1109/tvt.2024.3394909) | 2024 | Identifies future-trajectory disclosure to a not-fully-trusted platform during worker selection. |
| 19 | [A Secure Object Detection Technique for Intelligent Transportation Systems](https://doi.org/10.1109/ojits.2024.3440876) | 2024 | Adds inference risks in collaborative vehicular learning; distinguish attack measurements from defense/task performance. |
| 20 | [Human-Artificial Intelligent Threat Modelling in the Automotive Domain](https://doi.org/10.1109/iolts65288.2025.11117134) | 2025 | Describes automotive model refinement; concrete privacy outcomes need full-text verification. |

## How to use this shortlist

Build an extraction table with system/data flow, affected person/data, observer, capabilities/collusion, exposure, privacy harm, reported evidence, mitigation and assumptions. For your own case study, map which of these elements each approach can represent or derive. Treat the expected comparison as a hypothesis to test, not as a finding of these sources. A source analyzing data flows is not thereby an evaluated implementation of a process-centric tool. A cloud-related source is not thereby IaC research.

Check whether the SCAR baseline and human–AI model paper share evidence/models before counting them as independent findings. Treat the toll survey as secondary evidence and trace important attack claims to their primary sources. For the learning paper, distinguish inference-attack evaluation from task accuracy and runtime.

All original screening, prioritization and MAYBE files remain unchanged. The reproducible record of this fixed shortlist is results/recommended_20.csv, including stable IDs and DOIs.

Source SHA-256: `8e24c0fafb86e6fa1021da44c8ad895e02fe75708f66ce88d6b3bc07d2a67e04`. Notes SHA-256: `3d344993bf85576a28145dde224536493a2158e5e56f7afb247266be286e0999`.
