#!/usr/bin/env python3
"""Conservative lexical triage; no LLM, network access or final eligibility labels."""

import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES_VERSION = "1.0"
SEP = r"[\s\-‐‑‒–—−]+"


def phrase_pattern(expression):
    return re.compile(r"(?<!\w)(?:" + expression.replace(" ", SEP) + r")(?!\w)", re.I)


# Broad positive vocabulary protects recall; it never proves final eligibility.
VOCABULARY = {
    "mobility_systems": [
        r"mobilit(?:y|ies)", r"vehicl(?:e|es|es')", r"vehicular", r"automotive", r"automobile(?:s)?",
        r"connected cars?", r"autonomous driving", r"self driving", r"V2[XPVIN]", r"C V2X",
        r"VANETs?", r"IoV", r"internet of vehicles", r"intelligent transport(?:ation)? systems?",
        r"transport(?:ation)?", r"public transit", r"transit systems?", r"buses", r"railways?",
        r"MaaS", r"ride shar(?:ing|e)", r"rideshar(?:ing|e)", r"ride hail(?:ing)?",
        r"car shar(?:ing|e)", r"carshar(?:ing|e)", r"shared fleets?", r"navigation",
        r"roadside units?", r"RSUs?", r"traffic", r"telematics", r"travel", r"trips?",
    ],
    "location_trajectory_data": [
        r"locations?", r"geolocat(?:ion|ions|ed)", r"geo locat(?:ion|ions)",
        r"trajector(?:y|ies)", r"GPS", r"GNSS", r"geospatial", r"spatiotemporal",
        r"spatio temporal", r"position(?:s|ing)?", r"movement(?:s)?", r"tracking",
        r"travel histor(?:y|ies)", r"trip records?", r"origin destination", r"probe data",
    ],
    "privacy_threats": [
        r"privac(?:y|ies)", r"personal data", r"personal information", r"sensitive (?:data|information|attributes?)",
        r"anonym(?:ity|ous|ization|isation|ize|ise)", r"pseudonym(?:ity|s|ous|ization|isation)?",
        r"unlinkab(?:ility|le)", r"linkab(?:ility|le)", r"re(?: )?identif(?:ication|y|ied)",
        r"de(?: )?anonym(?:ization|isation|ize|ise)", r"identifiab(?:ility|le)", r"identity linking",
        r"trajectory link(?:ing|age)", r"surveillance", r"profil(?:ing|e|es)",
        r"inference attacks?", r"membership inference", r"attribute inference", r"model inversion",
        r"information leak(?:age|s|ing)?", r"data leak(?:age|s|ing)?", r"disclos(?:ure|ures|ing)",
        r"confidential(?:ity)?", r"unauthori[sz]ed (?:access|collection|sharing|use)",
        r"excessive (?:data|collection|sharing)", r"data aggregation", r"data (?:sharing|collection)",
        r"differential privacy", r"k anonymity", r"identity exposure", r"identity protection",
        r"eavesdropp(?:ing|er|ers)", r"data protection", r"data minimization",
    ],
    "adversary_attack_models": [
        r"adversar(?:y|ies|ial)", r"attackers?", r"attack models?", r"attacks?", r"attack scenarios?",
        r"threat actors?", r"malicious", r"honest but curious", r"semi honest", r"collu(?:sion|ding)",
        r"eavesdropp(?:ing|er|ers)", r"insider(?:s)?", r"impersonation", r"Sybil",
        r"passive observer(?:s)?", r"inference attacks?", r"membership inference", r"model inversion",
    ],
    "threat_analysis": [
        r"threat model(?:s|ing|ling)?", r"threat analys(?:is|es)", r"threat identif(?:ication|y)",
        r"threat assessment(?:s)?", r"privacy risk(?:s)?", r"risk analys(?:is|es)",
        r"security analys(?:is|es)", r"attack surfaces?", r"attack trees?", r"attack paths?",
        r"trust boundar(?:y|ies)", r"data flows?", r"risk assessment(?:s)?",
        r"architectural analys(?:is|es)", r"LINDDUN", r"STRIDE", r"threats?",
    ],
    "supporting_concepts": [
        r"framework(?:s)?", r"taxonom(?:y|ies)", r"systematic reviews?", r"literature reviews?",
        r"stakeholders?", r"data brokers?", r"third parties", r"data subjects?", r"consent",
        r"purpose limitation", r"identit(?:y|ies)", r"authentication", r"encryption",
        r"cloud", r"sensor data", r"data governance", r"infrastructure as code",
    ],
}
PATTERNS = {group: [(expression, phrase_pattern(expression)) for expression in expressions]
            for group, expressions in VOCABULARY.items()}
FOCUS_TERMS = [
    "energy efficiency", "fuel consumption", "battery degradation", "traffic throughput",
    "routing performance", "control stability", "mechanical reliability", "engine emissions",
    "packet delivery", "communication latency",
]
FOCUS = "(?:" + "|".join(FOCUS_TERMS) + ")"
SCOPE_STATEMENT = phrase_pattern(
    r"(?:privacy|personal data protection|location privacy|data privacy) (?:is|are) (?:explicitly )?(?:outside|beyond) (?:the )?scope"
)
EXCLUSIVE_FOCUS = phrase_pattern(
    r"(?:this (?:paper|study|work) (?:focuses|concentrates)|we (?:focus|concentrate)) (?:only|exclusively|solely) on " + FOCUS
)
ARTIFACT_TITLES = {"table of contents", "author index", "subject index", "list of reviewers", "editorial board"}
NO_RESEARCH = phrase_pattern(r"(?:contains? no original research|does not (?:present|contain) (?:original )?research|publication metadata only)")
AMBIGUITY = phrase_pattern(r"(?:although|however|but|except|despite|nevertheless|not only|rather than|not true|not the case)")
EXCLUSION_RULES = {
    "X1_EXPLICIT_NONPRIVACY_SCOPE": "E1: explicit privacy-out-of-scope statement plus exclusive technical focus corroborated by the title; no remaining privacy, location, attack, threat-analysis or supporting signals.",
    "X2_PUBLICATION_ARTIFACT": "E5: exact publication-artifact title plus an explicit no-research statement in a sufficiently complete abstract; no relevance signals.",
}
EXTRA_COLUMNS = [
    "preliminary_category", "preliminary_rule_id", "preliminary_reason", "matched_terms_json",
    "exclusion_evidence_json", "preliminary_flags_json", "preliminary_rules_version", "screening_criteria_sha256",
]


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(row, key, expected_type):
    value = json.loads(row.get(key) or ("[]" if expected_type is list else "{}"))
    if not isinstance(value, expected_type):
        raise ValueError(f"{row.get('paper_id')}: unexpected JSON type in {key}")
    return value


def text_fields(row):
    fields, seen = [], set()

    def add(field, text):
        if not isinstance(text, str):
            raise ValueError(f"Non-text screening metadata for {row.get('paper_id')}")
        if text.strip() and text not in seen:
            seen.add(text)
            fields.append((field, text))

    for name in ("title", "abstract"):
        add(name, row.get(name, ""))
    for index, keyword in enumerate(read_json(row, "keywords_json", list)):
        add(f"keywords_json[{index}]", keyword)
    variants = read_json(row, "metadata_variants_json", dict)
    for name in ("title", "abstract", "keywords", "author_keywords", "ieee_terms", "mesh_terms", "index_keywords"):
        for index, variant in enumerate(variants.get(name, [])):
            add(f"metadata_variants_json.{name}[{index}].value", variant["value"])
    return fields


def find_matches(fields):
    matches = []
    for group, patterns in PATTERNS.items():
        for expression, pattern in patterns:
            for field, text in fields:
                match = pattern.search(text)
                if match:
                    matches.append({"group": group, "pattern": expression, "field": field,
                                    "match": match.group(), "start": match.start(), "end": match.end()})
    return matches


def evidence(field, match):
    return {"field": field, "match": match.group(), "start": match.start(), "end": match.end()}


def exclusion(row, fields):
    abstract = row.get("abstract", "")
    # Scope negation alone cannot establish that foundational/supporting content is absent.
    scope = SCOPE_STATEMENT.search(abstract)
    focus = EXCLUSIVE_FOCUS.search(abstract)
    if scope and focus and not AMBIGUITY.search(abstract):
        sentence_start = max(abstract.rfind(char, 0, scope.start()) for char in ".!?\n") + 1
        # Reject embedded or negated claims such as 'It is not true that privacy is outside scope'.
        direct = not abstract[sentence_start:scope.start()].strip()
        remaining = [(field, SCOPE_STATEMENT.sub(" ", text)) for field, text in fields]
        protected = {m["group"] for m in find_matches(remaining)} - {"mobility_systems"}
        title_focus = next((phrase_pattern(term).search(row.get("title", "")) for term in FOCUS_TERMS
                            if phrase_pattern(term).search(focus.group())), None)
        if direct and title_focus and not protected:
            return "X1_EXPLICIT_NONPRIVACY_SCOPE", [evidence("abstract", scope), evidence("abstract", focus), evidence("title", title_focus)]
    title = " ".join(row.get("title", "").casefold().strip().rstrip(".").split())
    no_research = NO_RESEARCH.search(abstract)
    if title in ARTIFACT_TITLES and no_research and not find_matches(fields) and not AMBIGUITY.search(abstract):
        return "X2_PUBLICATION_ARTIFACT", [{"field": "title", "match": row["title"], "start": 0, "end": len(row["title"])}, evidence("abstract", no_research)]
    return None, []


def classify(row, criteria_hash):
    fields = text_fields(row)
    matches = find_matches(fields)
    groups = {m["group"] for m in matches}
    flags = []
    abstract = row.get("abstract", "").strip()
    if not abstract:
        flags.append("missing_abstract")
    elif len(abstract) < 100 or len(abstract.split()) < 20:
        flags.append("short_abstract")
    if abstract.endswith(("...", "…")):
        flags.append("possibly_truncated_abstract")
    if not row.get("title", "").strip():
        flags.append("missing_title")
    if read_json(row, "quality_flags_json", list):
        flags.append("upstream_quality_flags")
    conflicts = read_json(row, "metadata_conflicts_json", dict)
    if any(name in conflicts for name in ("title", "abstract", "keywords", "author_keywords", "ieee_terms", "mesh_terms", "index_keywords")):
        flags.append("conflicting_screening_metadata")
    rule, proof = (None, []) if flags else exclusion(row, fields)
    if rule:
        category, reason = "CLEARLY_IRRELEVANT", EXCLUSION_RULES[rule]
    elif flags:
        category, rule, reason = "UNCERTAIN", "U1_INCOMPLETE_OR_CONFLICTING_METADATA", "Retained: incomplete or conflicting metadata requires inspection."
    elif "privacy_threats" in groups and groups & {"mobility_systems", "location_trajectory_data", "adversary_attack_models", "threat_analysis"}:
        category, rule, reason = "POTENTIALLY_RELEVANT", "P1_PRIVACY_WITH_CONTEXT", "Privacy-equivalent terminology co-occurs with mobility, location, attack or analysis cues; eligibility and transfer remain unverified."
    elif "location_trajectory_data" in groups and groups & {"adversary_attack_models", "threat_analysis"}:
        category, rule, reason = "POTENTIALLY_RELEVANT", "P2_LOCATION_WITH_ATTACK_OR_ANALYSIS", "Location/trajectory terminology co-occurs with attack or analysis cues; retain possible privacy evidence without requiring the word privacy."
    elif groups:
        category, rule, reason = "UNCERTAIN", "U2_AMBIGUOUS_LEXICAL_EVIDENCE", "Some relevant terminology is present, but privacy relevance or a supporting route cannot be established lexically."
    else:
        category, rule, reason = "UNCERTAIN", "U3_NO_KEYWORD_MATCH", "No configured terms matched; vocabulary absence is not exclusion evidence."
    return {
        "preliminary_category": category, "preliminary_rule_id": rule, "preliminary_reason": reason,
        "matched_terms_json": packed(matches), "exclusion_evidence_json": packed(proof),
        "preliminary_flags_json": packed(flags), "preliminary_rules_version": RULES_VERSION,
        "screening_criteria_sha256": criteria_hash,
    }


def run(root=ROOT):
    input_path = root / "results/merged_papers.csv"
    criteria_path = root / "config/screening_criteria.md"
    input_raw, criteria_raw = input_path.read_bytes(), criteria_path.read_bytes()
    criteria = criteria_raw.decode("utf-8")
    version = re.search(r"Protocol version:\s*([\d.]+)", criteria)
    if not version or version.group(1).rstrip(".") != "1.0":
        raise ValueError("Review the lexical rules before using an unsupported screening protocol version")
    criteria_hash = hashlib.sha256(criteria_raw).hexdigest()
    reader = csv.DictReader(io.StringIO(input_raw.decode("utf-8-sig"), newline=""), strict=True)
    columns = reader.fieldnames
    if not columns or len(columns) != len(set(columns)) or not {"paper_id", "title", "abstract", "keywords_json"} <= set(columns):
        raise ValueError("Input needs unique headers and paper_id/title/abstract/keywords_json columns")
    if set(columns) & set(EXTRA_COLUMNS):
        raise ValueError("Input already has preliminary output columns")
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("Malformed input CSV row")
    if any(not row["paper_id"] for row in rows) or len({row["paper_id"] for row in rows}) != len(rows):
        raise ValueError("Missing or duplicate paper IDs")
    output = [{**row, **classify(row, criteria_hash)} for row in rows]
    counts = Counter(row["preliminary_category"] for row in output)
    exclusion_counts = Counter(row["preliminary_rule_id"] for row in output if row["preliminary_category"] == "CLEARLY_IRRELEVANT")
    rule_counts = Counter(row["preliminary_rule_id"] for row in output)
    group_counts = Counter(group for row in output for group in {m["group"] for m in json.loads(row["matched_terms_json"])})
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns + EXTRA_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    # Guard the output round-trip, including every original metadata cell and row order.
    roundtrip = list(csv.DictReader(io.StringIO(buffer.getvalue(), newline=""), strict=True))
    if len(roundtrip) != len(rows) or any({key: b[key] for key in columns} != a for a, b in zip(rows, roundtrip)):
        raise ValueError("Original metadata preservation check failed")
    report = [
        "# Preliminary screening report", "",
        "Run `python3 scripts/preliminary_screening.py` (Python 3, standard library only). No LLM, API, network, full-text evaluation or target retention count is used. This is lexical triage, not final INCLUDE/MAYBE/EXCLUDE assessment or research-role assignment.", "",
        f"Rules version: {RULES_VERSION}; screening protocol: {version.group(1).rstrip('.')}; input records: **{len(rows)}**; output records: **{len(output)}**; deleted records: **0**.", "",
        "| Category | Records |", "| --- | ---: |",
    ]
    for category in ("POTENTIALLY_RELEVANT", "UNCERTAIN", "CLEARLY_IRRELEVANT"):
        report.append(f"| {category} | {counts[category]} |")
    report += ["", "## Clear exclusions", ""]
    if exclusion_counts:
        report += [f"- `{rule}`: {count}. {EXCLUSION_RULES[rule]}" for rule, count in sorted(exclusion_counts.items())]
        report += ["", "Flagged paper IDs (all original rows remain in the CSV):"]
        report += [f"- `{row['paper_id']}`: `{row['preliminary_rule_id']}`." for row in output if row["preliminary_category"] == "CLEARLY_IRRELEVANT"]
    else:
        report.append("None. No record satisfied the affirmative evidence requirements for automatic exclusion; no keyword absence was treated as irrelevance.")
    report += ["", "## Rules and safeguards", "",
               "Missing/short abstracts (under 100 characters or 20 whitespace-separated words), ellipsis endings, missing titles, upstream quality flags or conflicting screening metadata force UNCERTAIN. All populated title/abstract/keyword variants are checked. These completeness thresholds are retention safeguards, not quality or eligibility exclusions.", "",
               "P1: privacy-equivalent terms plus mobility, location, adversary/attack or threat-analysis cues → POTENTIALLY_RELEVANT. P2: location/trajectory cues plus attack or analysis cues → POTENTIALLY_RELEVANT. Co-occurrence can occur across fields and does not prove a semantic relationship. Foundational/privacy evidence can be retained without an explicit mobility term. Generic mobility/security terminology alone remains UNCERTAIN.", "",
               "Other matches → UNCERTAIN; no matches → UNCERTAIN. Positive keywords are broad retention cues, not proofs of privacy harms. Generic framework terminology is never an exclusion reason. Supporting/foundational transfer still needs later assessment under I2/I3. Rules only operationalize extremely narrow E1/E5 cases; E2–E4 cannot be established safely from vocabulary alone.", "",
               "Enabled automatic exclusions (applied only after all completeness guards pass):", ""]
    report += [f"- `{rule}`: {description}" for rule, description in EXCLUSION_RULES.items()]
    report += ["", "X1 additionally requires the privacy disclaimer to start a sentence, an exclusive focus on one of the configured technical metrics, that same metric in the title, and no contrast/negation ambiguity markers. After removing privacy-disclaimer phrases, any privacy, location, attacker, analysis or supporting-concept match in any field vetoes X1. X2 requires an exact artifact title and affirmative no-research text; any relevance-group match vetoes it. Technical subject words and lack of privacy words alone never cause exclusion.", "",
               "Each exclusion logs the rule and exact source substrings with field paths and character offsets (Python string indices, zero-based, end-exclusive). For keyword variants, paths point to values in the retained original JSON cells. matched_terms_json records each configured pattern's first match per distinct text value; it is not an exhaustive list of occurrences. The original fields and all provenance columns are unchanged. Every row remains available for later review, including CLEARLY_IRRELEVANT.", "",
               "## Rule counts", "", "| Rule | Records |", "| --- | ---: |"]
    report += [f"| {rule} | {count} |" for rule, count in sorted(rule_counts.items())]
    report += ["", "## Vocabulary coverage", "", "| Group | Records with a match |", "| --- | ---: |"]
    report += [f"| {group} | {group_counts[group]} |" for group in VOCABULARY]
    report += ["", "Patterns are case-insensitive, use word boundaries, and accept whitespace or common Unicode hyphens between phrase tokens. Pattern definitions and synonyms are versioned in scripts/preliminary_screening.py. Overlapping groups are intentional. General authentication, encryption, identity, frameworks and data-governance terms also protect potentially transferable support from exclusion.", "",
               "## Reproducibility and limitations", "",
               f"- merged_papers.csv SHA-256: `{hashlib.sha256(input_raw).hexdigest()}`.",
               f"- screening_criteria.md SHA-256: `{criteria_hash}`.",
               f"- preliminary_screening.py SHA-256: `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`.",
               "- Output order matches the input; unchanged inputs and script produce byte-identical results. Only the two preliminary outputs are overwritten.",
               "- The Markdown criteria are read, version-checked and fingerprinted; their prose is not automatically converted into semantic rules. Review these coded rules if the criteria change.",
               "- English lexical rules can miss synonyms, other languages and implicit relationships. Unmatched or ambiguous papers remain available. Lexical positives may include irrelevant work; that is intentional.",
               "- No final reviewer decisions, role labels or foundational transfer claims are inferred. The protocol's human calibration, exclusion verification and adjudication remain for the subsequent substantive screening stage. Review clear-exclusion evidence before using it as a final eligibility decision.", ""]
    if input_path.read_bytes() != input_raw or criteria_path.read_bytes() != criteria_raw:
        raise ValueError("Input changed during screening")
    (root / "results/preliminary_screening.csv").write_text(buffer.getvalue(), encoding="utf-8", newline="")
    (root / "results/preliminary_screening_report.md").write_text("\n".join(report), encoding="utf-8", newline="")
    print("; ".join(f"{category}: {counts[category]}" for category in ("POTENTIALLY_RELEVANT", "UNCERTAIN", "CLEARLY_IRRELEVANT")))
    return counts


if __name__ == "__main__":
    run()
