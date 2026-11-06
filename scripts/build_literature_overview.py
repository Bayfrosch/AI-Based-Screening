#!/usr/bin/env python3
"""Rebuild a metadata-only literature matrix and synthesis; never change screening."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0"
NOT_ESTABLISHED = "Not established from metadata; full-text verification required"
DOMAINS = {
    "Fog/cloud/edge vehicular infrastructure": r"fog|cloud|edge|cybertwin",
    "Vehicular social networks": r"vehicular social|social networking",
    "Road-condition monitoring": r"road condition monitoring",
    "Electronic toll collection": r"toll collection",
    "Navigation/location-based services": r"navigation|location-based service",
    "Vehicular crowdsensing": r"crowdsensing",
    "Electric-vehicle charging/grid/battery services": r"charging|vehicle.to.grid|battery swapping",
    "Advertising/proximity marketing": r"ad dissemination|ad conversion|proximity marketing",
    "Vehicular platooning": r"platoon",
    "UAV/drone-assisted transportation": r"uav|drone",
    "Maritime transportation": r"maritime",
    "Vehicle sensing/learning/driver imagery": r"face videos|object detection|implicit authentication|predictive maintenance|federated learning|perception data|vehicular congestion|image encryption",
}
AREA_DESCRIPTIONS = {
    "Applied privacy threat analysis": "Assets, data flows, threat agents and privacy attack assumptions; includes adversary analysis embedded in defenses.",
    "Tracking, identification and correlation": "Movement exposure, identity linkage and pseudonym/message correlation; anonymity claims alone are not re-identification experiments.",
    "Anonymous authentication and accountability": "Pseudonyms, unlinkability, revocation and authorized tracing; distinguish authority accountability from hostile surveillance.",
    "Data sharing, aggregation and stakeholder trust": "Outsourcing, access policies, continuous collection and protection across organizational boundaries.",
    "Learning, behavioral and visual data privacy": "Driver features, images and collaborative learning; separate privacy-attack evaluation from task accuracy or runtime tests.",
    "Service-specific privacy exposures": "Tolls, navigation, crowdsensing, advertising, charging, platooning and maritime examples anchor abstract threats in services.",
    "Supplementary or unresolved privacy mechanisms": "Retained literature whose central privacy usefulness needs clarification; no eligibility decision is changed.",
}
THREAT_THEMES = ["Location tracking and surveillance", "Re-identification", "Trajectory linking and correlation", "Inference attacks"]
IDENTITY = r"anonym\w*|pseudonym\w*|identity privacy|identity protection|identity disclosure|identit(?:y|ies).{0,35}(?:leak|expos)|(?:leak|expos).{0,35}identit(?:y|ies)"
METHODS = {
    "Protocol/mechanism design": r"we (?:propose|present|design|introduce|construct)|this (?:paper|study) (?:proposes|presents|designs)|protocol.*is proposed",
    "Formal security analysis/proof": r"formal (?:security )?(?:analysis|verification|proof)|security proof|random oracle|real.or.random|\bROR\b|provably|we prove|is proven",
    "Informal/analytical security analysis": r"(?:security|privacy)(?: and (?:security|privacy))? (?:analys(?:is|es)|arguments)|cryptanalysis|analysis of security",
    "Simulation": r"simulat\w*|\bNS[- ]?[23]\b|OMNeT|Vissim|SUMO",
    "Experiments/evaluation (target not automatically privacy)": r"experiment\w*|performance evaluat\w*|performance analysis|performance analyses|performance results|evaluated qualitatively|comparative analysis|efficiency validation|computational and communication cost analysis",
    "Implementation/prototype": r"implement\w*|prototype|proof of concept",
    "Dataset-based evaluation": r"dataset|data set|naturalistic driving study data",
    "Automated protocol verification": r"AVISPA|Scyther|ProVerif|BAN logic|burrows.abadi.needham",
}


def contains(pattern, text):
    return re.search(pattern, text, re.I) is not None


def method_cues(abstract):
    """Extract auditable method clues, without treating experiments as attack evidence."""
    sentences = re.split(r"(?<=[.!?])\s+", abstract)
    own = [s for s in sentences if contains(
        r"\bwe\b|\bour\b|proposed|this (?:paper|study|article)|^(?:(?:the|a|both|thorough|through|formal|informal|extensive|rigorous|comprehensive|theoretical) )*(?:security|simulation|experimental|performance|experiments|formal|analysis of security)|^(?:finally|additionally|in addition|according to|verification using)", s)]
    evidence = {}
    for label, pattern in METHODS.items():
        for sentence in own:
            if contains(pattern, sentence) and not contains(r"\b(?:no|without|not)\b.{0,15}(?:formal|security proof|random oracle)", sentence):
                evidence[label] = sentence.strip()
                break
    return evidence


def matrix_row(row, note):
    title, abstract = row["title"], row["abstract"]
    text = " ".join([title, abstract, " ".join(json.loads(row["keywords_json"]))])
    themes = json.loads(row["thematic_categories"])
    domains = []
    domain_evidence = {}
    if "Connected vehicles and V2X" in themes:
        domains.append("Connected vehicles/V2X/VANETs")
        domain_evidence[domains[-1]] = "Existing metadata-based thematic assessment"
    for label, pattern in DOMAINS.items():
        if contains(pattern, title):
            domains.append(label)
            domain_evidence[label] = "Title: " + title
    if not domains:
        domains = ["Intelligent transportation systems (service unspecified)"]
        domain_evidence[domains[0]] = "Title/abstract; no narrower system established"
    threats = [label for label in THREAT_THEMES if label in themes]
    if contains(IDENTITY, text):
        threats.append("Identity disclosure/anonymity (risk or protection topic)")
    if contains(r"\b(?:un)?linkabil\w*|\b(?:un)?linkable\b", text):
        threats.append("Record/message linkability (not necessarily trajectory linking)")
    if contains(r"(?:unauthori[sz]ed|sensitive|private|personal|data).{0,65}(?:disclos|leak|breach|expos)|(?:disclos|leak|breach|expos).{0,65}(?:private|personal|sensitive|information)|confidentiality", text):
        threats.append("Data disclosure/confidentiality (risk or protection topic)")
    if contains(r"consent|user.defined access|control over|full control|data minimisation|data minimization|policy.protection|polic(?:y|ies).{0,35}priv", text):
        threats.append("Control over personal-data use/access")
    if not threats:
        threats = ["Privacy exposure insufficiently specified in metadata"]
    areas = []
    if "Mobility-specific threat modeling" in themes:
        areas.append("Applied privacy threat analysis")
    if any(t in themes for t in THREAT_THEMES[:3]) or contains(r"pseudonym", title):
        areas.append("Tracking, identification and correlation")
    if contains(r"authenticat|signature|signcryption|attestation|pseudonym|anonymous|anonymity|traceback", title):
        areas.append("Anonymous authentication and accountability")
    if contains(r"data shar|data exchange|data collection|aggregation|access control|outsourc|deduplication|sticky|feedback", title):
        areas.append("Data sharing, aggregation and stakeholder trust")
    if contains(r"learning|implicit authentication|face videos|congestion.*perceptron|image encryption|biometric|object detection|perception data|predictive maintenance", title):
        areas.append("Learning, behavioral and visual data privacy")
    if any(d in domains for d in list(DOMAINS)[2:11]):
        areas.append("Service-specific privacy exposures")
    if row["priority"] == "LOW" or not areas:
        areas.append("Supplementary or unresolved privacy mechanisms")
    areas += [area for area in note.get("research_areas", []) if area not in areas]
    evidence = method_cues(abstract)
    method = note.get("methodology") or ("Abstract method cues: " + "; ".join(evidence) if evidence else NOT_ESTABLISHED)
    return {
        "paper_id": row["paper_id"], "title": title, "year": row["publication_year"],
        "research_role": row["research_role"], "priority": row["priority"],
        "mobility_domain": "; ".join(domains), "privacy_threat_categories": "; ".join(threats),
        "research_methodology": method, "potential_contribution_to_seminar": note.get("contribution", row["priority_reason"]),
        "full_text_review_needed": "true", "research_areas": "; ".join(areas),
        "contribution_focus": row["contribution_focus"],
        "threat_model_status": note.get("model_status", "NOT_ESTABLISHED"),
        "threat_model_or_adversary_notes": note.get("model_note", NOT_ESTABLISHED),
        "empirical_privacy_evidence_status": note.get("empirical_status", "NOT_ESTABLISHED"),
        "empirical_evidence_notes": note.get("empirical_note", "Experiments, simulations or proofs alone do not establish an empirical privacy attack."),
        "methodology_evidence_status": "ABSTRACT_SUPPORTED_REVIEWER_SUMMARY" if note.get("methodology") else "LITERAL_METHOD_CUES_REQUIRING_ATTRIBUTION_CHECK",
        "methodology_evidence_json": json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
        "domain_evidence_json": json.dumps(domain_evidence, ensure_ascii=False, separators=(",", ":")),
        "reviewer_annotation_evidence_json": json.dumps(note.get("evidence", []), ensure_ascii=False, separators=(",", ":")),
        "interpretation_limit": "Themes and protection goals are not verified attacks; potential seminar contribution is a reviewer interpretation.",
        "evidence_basis": "title; abstract; keywords only; original research role and priority retained",
    }


def citation(key, annotations, lookup):
    row = lookup[annotations["references"][key]]
    return f"**{row['title']}** ({row['publication_year']}; `{row['paper_id']}`)"


def build():
    source = ROOT / "results/prioritized_papers.csv"
    criteria = ROOT / "config/screening_criteria.md"
    annotations_path = ROOT / "config/literature_overview_annotations.json"
    annotations = json.loads(annotations_path.read_text(encoding="utf-8"))
    if annotations["source_sha256"] != hashlib.sha256(source.read_bytes()).hexdigest():
        raise ValueError("Prioritized input changed; review synthesis annotations before rebuilding")
    if annotations["criteria_sha256"] != hashlib.sha256(criteria.read_bytes()).hexdigest():
        raise ValueError("Criteria changed; review synthesis annotations before rebuilding")
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    lookup = {r["paper_id"]: r for r in rows}
    if not rows or len(lookup) != len(rows) or any(r["decision"] != "INCLUDE" for r in rows):
        raise ValueError("Require unique INCLUDE papers")
    if not set(annotations["papers"]) <= set(lookup) or not set(annotations["references"].values()) <= set(lookup):
        raise ValueError("Unknown annotated paper ID")
    for paper_id, note in annotations["papers"].items():
        for quote in note.get("evidence", []):
            if not any(quote in lookup[paper_id][field] for field in ("title", "abstract", "keywords_json")):
                raise ValueError(f"Annotation evidence not present in metadata: {paper_id}")
    reviewed_areas = {}
    for area, examples in annotations["area_examples"].items():
        if area not in AREA_DESCRIPTIONS:
            raise ValueError("Unknown research area")
        for key, supported, contribution in examples:
            paper_id = annotations["references"][key]
            reviewed_areas.setdefault(paper_id, []).append(area)
    matrix = [matrix_row(r, {**annotations["papers"].get(r["paper_id"], {}),
                             "research_areas": reviewed_areas.get(r["paper_id"], [])}) for r in rows]
    with (ROOT / "results/literature_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(matrix[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(matrix)
    cite = lambda key: citation(key, annotations, lookup)
    counts = Counter(r["priority"] for r in matrix)
    roles = Counter(r["research_role"] for r in matrix)
    themes = Counter(t for r in rows for t in json.loads(r["thematic_categories"]))
    domains = Counter(d for r in matrix for d in r["mobility_domain"].split("; "))
    areas = Counter(a for r in matrix for a in r["research_areas"].split("; "))
    threats = Counter(t for r in matrix for t in r["privacy_threat_categories"].split("; "))
    focus = Counter(r["contribution_focus"] for r in matrix)
    model_rows = [r for r in matrix if r["threat_model_status"] == "EXPLICIT_PRIVACY_MODEL_REPORTED"]
    scenario_rows = [r for r in matrix if r["threat_model_status"] == "CONCRETE_ADVERSARY_OR_SCENARIO_REPORTED"]
    lines = ["# Literature overview", "", "## Scope and evidence limits", "",
             f"This overview covers all {len(rows)} prioritized INCLUDE records: HIGH={counts['HIGH']}, MEDIUM={counts['MEDIUM']}, LOW={counts['LOW']}. Only titles, supplied abstracts and keywords were used for content analysis; years identify sources. No full papers were read. Original semantic decisions, roles and priorities are preserved. The unresolved MAYBE queue is outside this overview, not evidence of irrelevance.", "",
             "The authoritative scope is config/screening_criteria.md: identify and explain mobility privacy threats, affected data, adversaries and exposure conditions. Applied LINDDUN/STRIDE analyses qualify; general framework comparison is not the organizing question. Screening INCLUDE means advance to full text, not verified final eligibility.", "",
             "**Abstract-supported** below means the source abstract explicitly reports a topic, method or result; its validity was not independently checked. **Interpretation** means a proposed seminar use, relationship or coverage gap. The matrix records exact metadata evidence for reviewed annotations and literal method cues for other papers. Method cues still need attribution checking: a mention of a technique can concern related work. No quantitative attack success rates or comparative effectiveness are inferred.", "",
             "Counts describe this selected corpus only. They do not establish field-wide trends, completeness of retrieval or the absence of work elsewhere. Categories overlap. Domain subcategories use explicit title terms; the broad connected-vehicle label and four threat themes retain the earlier metadata assessment. Title-only subcategory counts are lower-bound indicators, not a full domain census.", "",
             "## Mobility systems represented", "", "| Metadata-supported system/architecture label | Papers |", "| --- | ---: |"]
    lines += [f"| {label} | {count} |" for label, count in domains.most_common()]
    lines += ["", f"Connected vehicles/V2X are the dominant broad label ({themes['Connected vehicles and V2X']}/{len(rows)}). Specific services include electronic toll collection, road monitoring, navigation, vehicular crowdsensing, advertising and electric-vehicle services. Generic VANET/C-V2X papers should not be counted as studies of public transport or autonomous driving merely because the abstract mentions those applications. No dedicated public-transport/MaaS paper was identified by the existing thematic assessment.", "",
              "## Privacy threats and protection topics", "", "| Topic | Papers | Counting basis |", "| --- | ---: | --- |"]
    lines += [f"| {t} | {themes[t]} | Reviewed thematic tag; risk or defense topic |" for t in THREAT_THEMES]
    for topic, count in threats.most_common():
        if topic not in THREAT_THEMES:
            basis = "No indexed specific threat established; not an exclusion" if topic == "Privacy exposure insufficiently specified in metadata" else "Explicit metadata vocabulary; risk or protection, not an attack count"
            lines.append(f"| {topic} | {count} | {basis} |")
    lines += ["", "Among the four specific attack-related themes, tracking/surveillance has the largest count, followed by trajectory correlation, re-identification and inference. Broader identity/anonymity and message-linkability protection claims are common, but are not equivalent to empirical tracking, re-identification or inference evidence. Unauthorized data disclosure, consent/control and cross-stakeholder trust supply additional privacy perspectives. Authorized revocation/traceback is an accountability feature, not automatically surveillance.", "",
              "## Main research areas and their seminar use", ""]
    for area, description in AREA_DESCRIPTIONS.items():
        lines += [f"### {area} ({areas[area]} tagged papers)", "", description, ""]
        for key, supported, contribution in annotations["area_examples"][area]:
            lines += [f"- {cite(key)}. **Abstract-supported:** {supported} **Potential contribution:** {contribution}"]
        lines.append("")
    lines += ["## Concrete threat models and adversary assumptions", "",
              f"A targeted abstract review identifies {len(model_rows)} papers explicitly reporting a mobility privacy or mixed security/privacy model. These are positive identifications, not an exhaustive full-text model census. Another {len(scenario_rows)} annotated papers describe concrete privacy-relevant adversaries, exposures or attack scenarios without establishing a complete formal privacy model. Other rows remain NOT_ESTABLISHED rather than being labeled model-free.", "",
              "| Paper | Model reported in abstract | Verification needed |", "| --- | --- | --- |"]
    for row in model_rows:
        lines += [f"| {row['title']} (`{row['paper_id']}`) | {row['threat_model_or_adversary_notes']} | Assets, data flows, adversary powers, scope and privacy-specific results |"]
    lines += ["", "Concrete scenario/adversary examples:", ""]
    for key in annotations["adversary_examples"]:
        row = next(r for r in matrix if r["paper_id"] == annotations["references"][key])
        lines += [f"- {cite(key)}: {row['threat_model_or_adversary_notes']}"]
    lines += ["", "A random-oracle, Real-or-Random or eCK protocol-security model is not automatically a comprehensive privacy model. Check which secrets and privacy properties it formalizes and whether it covers tracking, collusion, legitimate data recipients and inference. The matrix does not promote every formal-proof paper to concrete threat-model evidence.", "",
              "## Empirical threat evidence versus analysis and mitigation tests", ""]
    for key in annotations["evidence_examples"]:
        row = next(r for r in matrix if r["paper_id"] == annotations["references"][key])
        lines += [f"- {cite(key)} — **{row['empirical_privacy_evidence_status']}**: {row['empirical_evidence_notes']}"]
    lines += ["", "The pseudonym-tracking experiment is the clearest directly reported empirical tracking example in this metadata review. Analytical counterexamples, surveys of attacks, privacy-defense datasets and runtime benchmarks are different evidence types. Dataset names alone do not demonstrate a privacy attack, real-world deployment or representative attack success. Full-text checks should separate synthetic/simulated traffic, recorded traces, physical deployments and human participants.", "",
              "## Mitigation-oriented literature", "",
              f"Original roles: CORE={roles['CORE']}, THREAT_EVIDENCE={roles['THREAT_EVIDENCE']}, MITIGATION={roles['MITIGATION']}. The later reading-purpose assessment distinguishes DIRECT_THREAT_ANALYSIS={focus['DIRECT_THREAT_ANALYSIS']}, THREAT_SPECIFIC_MITIGATION={focus['THREAT_SPECIFIC_MITIGATION']}, GENERAL_PRIVACY_MITIGATION={focus['GENERAL_PRIVACY_MITIGATION']}. These fields answer different questions and must not be interchanged. A MITIGATION source can also contain a valuable threat scenario.", "",
              "The matrix identifies every primarily defensive paper using the unchanged research_role and contribution_focus. Representative mechanisms include conditional anonymity/pseudonyms, anonymous authentication, user-controlled linkability, access-control/proxy re-encryption, privacy-preserving aggregation, differential privacy, federated-learning protection and face deidentification. Use these sources to explain addressed exposures, assumptions and residual questions; avoid turning the seminar into a protocol-efficiency catalog. No mitigation is treated as effective merely because its abstract asserts security.", "",
              "## Relationships between themes — synthesis hypotheses", "",
              "These connections organize the seminar; they are reviewer interpretations to test against full text:", "",
              "1. **Assets/data flows → observers → exposures.** Start from vehicle-to-device/cloud/infrastructure interactions, then locate identities, routes, behavior and access-policy data at trust boundaries.",
              "2. **Anonymity → correlation → identification.** Pseudonyms hide explicit identifiers, yet message timing, movement patterns or colluding observers may restore linkage. Linkage is an enabling condition; it is not necessarily proof of real-identity recovery.",
              "3. **Security monitoring/accountability ↔ privacy.** Misbehavior feedback, traceability and revocation create useful safety/security controls while raising questions about who may link identities or reconstruct trips.",
              "4. **Cloud/edge outsourcing → stakeholder power.** Honest-but-curious providers, colluding RSUs and compromised authorities require different assumptions; encryption alone does not establish appropriate downstream data use.",
              "5. **Data utility ↔ exposure.** Learning, maintenance and human-factors data motivate collection; differential privacy, aggregation and deidentification provide different protection goals and utility questions.", "",
              "## Apparent gaps and full-text questions", "",
              "The following are gaps in the selected metadata coverage or unresolved evidence questions, not established research gaps across the field:", "",
              "- **Mobility breadth:** no dedicated public-transport/MaaS theme; ride-sharing, multi-operator travel apps and longitudinal cross-service trip data have little explicit representation. Extend retrieval and revisit MAYBE records before claiming absence.",
              f"- **Threat breadth:** inference ({themes['Inference attacks']} tagged paper) and explicit re-identification ({themes['Re-identification']}) have limited coverage compared with identity-protection protocols. Profiling, aggregation harms and excessive legitimate collection need targeted full-text checks rather than being assumed absent.",
              "- **Evidence breadth:** few clearly described empirical privacy-attack evaluations; many abstracts report proofs, security analyses or efficiency experiments. Extract attack conditions, adversary access and what was actually measured before comparing findings.",
              "- **Organizational/lifecycle coverage:** consent, cross-boundary reuse and semi-honest stakeholders appear in some sources, but coverage of retention, downstream sharing, actor collusion and multi-service composition remains unresolved.",
              "- **Model adequacy:** mixed security/privacy models can emphasize assets and cryptographic correctness. Check whether the privacy claims address affected people, legitimate recipients and inference beyond network attackers.",
              "- **Evidence independence:** the SCAR baseline and human–AI automotive-model papers have related subject matter; check shared authors, models and versions before treating them as independent findings. Similarly, cryptanalysis and improved-scheme papers may discuss the same predecessor. Surveys provide secondary evidence, not additional independent attacks.",
              "- **Selection uncertainty:** LOW still means INCLUDE pending full-text eligibility checks. Prior roles and priorities are inherited judgments, not validation labels. This overview does not resolve earlier manual-validation flags or examine the MAYBE queue.", "",
              "## Recommended reading order", "",
              "Read for argument structure and threat coverage, not publication year. This sequence is a starting path, not a limit on the HIGH queue; all remaining HIGH papers remain candidates for full-text review.", ""]
    for n, (key, purpose) in enumerate(annotations["reading_order"], 1):
        lines += [f"{n}. {cite(key)} — {purpose}"]
    lines += ["", "Then follow the matrix into navigation, crowdsensing, malicious advertising parties, driver-feature/face privacy, and charging services to test whether the threat dimensions transfer across data and stakeholders. Consult the human–AI automotive paper for its applied findings; framework usability/comparison is supporting context only.", "",
              "## Matrix and reproducibility", "",
              "results/literature_matrix.csv contains one row per prioritized paper, with paper ID, title, year, inherited role/priority, mobility domain, privacy threats/protection topics, methods, proposed seminar contribution and full_text_review_needed=true. Additional fields distinguish model/scenario evidence, empirical evidence type and unverified method cues. Multiple labels are separated by semicolons; evidence JSON preserves exact source sentences/phrases for inspection. All source metadata remains in results/prioritized_papers.csv and is not modified.", "",
              "Regenerate with `python3 scripts/build_literature_overview.py`. The script checks unique identities, annotation references, exact evidence substrings and input fingerprints before exporting. Reviewed annotations and source hashes are in config/literature_overview_annotations.json. Generic domain/threat/method rules are transparent in the script; they provide conservative topic indexing, not a new screening stage. Interpretation remains subject to full-text revision.", "",
              f"Synthesis version: {VERSION}. Source SHA-256: `{annotations['source_sha256']}`. Criteria SHA-256: `{annotations['criteria_sha256']}`.", ""]
    (ROOT / "results/literature_overview.md").write_text("\n".join(lines), encoding="utf-8")
    outline = ["# Preliminary seminar-paper outline", "", "## Suggested research question", "",
               "**Which privacy threats arise from the collection, communication and cross-stakeholder use of mobility data, how do existing studies model the relevant adversaries and exposure conditions, and where do their assumptions limit the protection of affected people?**", "",
               "Working title: Threat Modeling with Regard to the Mobility Domain. The conceptual scope includes multiple mobility services; the present evidence base is predominantly connected vehicles/V2X. Disclose this imbalance or explicitly narrow the final question after full-text review; do not imply all mobility domains are equally covered.", "",
               "Supporting questions: (1) Which data, actors and trust boundaries enable tracking, linkage, identification, inference or disclosure? (2) What evidence supports the identified threats? (3) What assumptions and trade-offs remain in threat-specific mitigations?", "",
               "## Preliminary chapter structure", ""]
    for chapter in annotations["chapters"]:
        outline += [f"### {chapter['title']}", "", chapter["purpose"], "", "Relevant literature:", ""]
        for key, use in chapter["papers"]:
            outline += [f"- {cite(key)} — {use}"]
        outline.append("")
    outline += ["## Evidence extraction during full-text reading", "",
                "For each retained source, extract: studied system and data flow; affected people and data; observer/stakeholder; adversary capabilities and collusion; trust boundaries; privacy harm and attack mechanism; reported evidence/method; assumptions; mitigation and residual exposure; source section/page. Distinguish source findings from your cross-paper interpretation. Mark secondary evidence and overlapping models to avoid double counting. Record unreported details as unknown.", "",
                "Use the four LOW papers only if full text clarifies their personal-privacy contribution. Resolve the separate MAYBE and validation queues before treating the final corpus as settled. The matrix is a planning tool, not a completed full-text extraction table.", "",
                "## Topics outside the main scope", "",
                "- Generic STRIDE-versus-LINDDUN comparisons, framework catalogs, framework usability benchmarking or new framework development. Mention methods briefly when needed to explain a concrete mobility privacy result.",
                "- Pure authentication/signature security, integrity, availability, routing, congestion or mechanical safety without a substantive personal-privacy connection.",
                "- Exhaustive cryptographic performance/post-quantum/blockchain comparisons. Include a mechanism only to explain the privacy threat, assumptions or residual risk.",
                "- General privacy law/compliance surveys; use legal requirements as context where they illuminate data control and stakeholder obligations, not as unsupported legal conclusions.",
                "- Claims of field-wide research trends, universal domain coverage or verified mitigation effectiveness based on this selected, abstract-only corpus.",
                "- Full treatment of infrastructure-as-code/process-centric modeling unless the final research question is explicitly amended; the current screening criteria do not make those approaches a requirement.", "",
                "All proposed chapter claims and source placements are tentative. No full papers were read for this outline. Applied framework papers remain central where they produce mobility privacy analysis.", ""]
    (ROOT / "results/paper_outline.md").write_text("\n".join(outline), encoding="utf-8")
    print(f"Built matrix/overview/outline for {len(matrix)} papers; {len(model_rows)} explicit models and {len(scenario_rows)} concrete scenario annotations.")


if __name__ == "__main__":
    build()
