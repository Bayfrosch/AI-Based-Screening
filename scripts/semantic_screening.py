#!/usr/bin/env python3
"""Resumable, locally reviewed semantic batches; no automatic model connection.

next: show at most 20 unclassified records using only permitted metadata.
save: read compact JSON decisions from stdin, validate, checkpoint, export.
export: revalidate checkpoints and regenerate all derived CSVs and report.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_SIZE = 20
DECISIONS = {"I": "INCLUDE", "M": "MAYBE", "E": "EXCLUDE"}
ROLES = {"C": "CORE", "T": "THREAT_EVIDENCE", "B": "BACKGROUND", "M": "MITIGATION", "F": "FRAMEWORK_FOCUSED", "O": "OUT_OF_SCOPE"}
CODES = {"I1", "I2", "I3", "E1", "E2", "E3", "E4", "E5"}
KEYS = {"paper_id", "decision", "research_role", "matched_criteria", "reason", "needs_full_text_review"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load():
    results = ROOT / "results"
    paths = [results / "merged_papers.csv", results / "preliminary_screening.csv", ROOT / "config/screening_criteria.md"]
    raw = [p.read_bytes() for p in paths]
    source = list(csv.DictReader(io.StringIO(raw[0].decode("utf-8"), newline=""), strict=True))
    preliminary = list(csv.DictReader(io.StringIO(raw[1].decode("utf-8"), newline=""), strict=True))
    ids = [r["paper_id"] for r in source]
    if len(set(ids)) != len(ids) or set(ids) != {r["paper_id"] for r in preliminary} or len(source) != len(preliminary):
        raise ValueError("Input identity mismatch")
    for a, b in zip(source, preliminary):
        if any(b.get(k) != v for k, v in a.items()):
            raise ValueError("Preliminary input differs from source metadata/order")
    fingerprint = {p.name: digest(b) for p, b in zip(paths, raw)}
    directory = results / "semantic_batches"
    directory.mkdir(exist_ok=True)
    manifest = directory / "manifest.json"
    if manifest.exists() and json.loads(manifest.read_text()) != fingerprint:
        raise ValueError("Inputs changed: preserve old checkpoints and explicitly start a new run")
    if not manifest.exists():
        manifest.write_text(json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8")
    classified = {}
    for path in sorted(directory.glob("batch_*.json")):
        batch = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(batch, list) or not 1 <= len(batch) <= BATCH_SIZE:
            raise ValueError(f"Invalid batch size: {path}")
        for item in batch:
            validate(item)
            if item["paper_id"] in classified or item["paper_id"] not in ids:
                raise ValueError(f"Duplicate/unknown checkpoint ID: {item['paper_id']}")
            classified[item["paper_id"]] = item
    return source, preliminary, classified, fingerprint


def validate(item):
    if not isinstance(item, dict) or set(item) != KEYS:
        raise ValueError("Classification must have exactly the six schema fields")
    if not isinstance(item["paper_id"], str) or not item["paper_id"]:
        raise ValueError("Invalid paper ID")
    if item["decision"] not in DECISIONS.values() or item["research_role"] not in ROLES.values():
        raise ValueError("Unknown decision or role")
    codes = item["matched_criteria"]
    if not isinstance(codes, list) or not codes or len(set(codes)) != len(codes) or any(c not in CODES for c in codes):
        raise ValueError("Invalid criterion list")
    if not isinstance(item["reason"], str) or not 1 <= len(item["reason"].split()) <= 25:
        raise ValueError("Reason must contain 1–25 whitespace-separated words")
    if type(item["needs_full_text_review"]) is not bool:
        raise ValueError("Full-text flag must be a Boolean")
    decision, role = item["decision"], item["research_role"]
    if decision == "EXCLUDE":
        if any(not c.startswith("E") for c in codes) or role not in ("OUT_OF_SCOPE", "FRAMEWORK_FOCUSED") or item["needs_full_text_review"]:
            raise ValueError("Exclusion must be evidenced, outside scope, and resolved at abstract stage")
    elif any(not c.startswith("I") for c in codes) or role == "OUT_OF_SCOPE" or not item["needs_full_text_review"]:
        raise ValueError("Retained papers need an inclusion route (provisional for MAYBE) and later full-text review")


def pending(source, classified):
    return [r for r in source if r["paper_id"] not in classified][:BATCH_SIZE]


def show_next(source, classified):
    for n, row in enumerate(pending(source, classified), 1):
        print(json.dumps({"n": n, **{k: row[k] for k in ("paper_id", "title", "abstract", "publication_year")},
                          "keywords": json.loads(row["keywords_json"])}, ensure_ascii=False, separators=(",", ":")))
    print(f"Progress: {len(classified)}/{len(source)}", file=sys.stderr)


def save(source, classified):
    batch = pending(source, classified)
    if not batch:
        raise ValueError("No unclassified records remain; existing checkpoints will not be overwritten")
    # Compact session input: [1-based batch position, I/M/E, C/T/B/M/F/O, criterion, <=25-word reason].
    compact = json.load(sys.stdin)
    if not isinstance(compact, list) or len(compact) != len(batch):
        raise ValueError("Supply one decision for every record in the current batch")
    positions, items = set(), []
    for entry in compact:
        if not isinstance(entry, list) or len(entry) != 5:
            raise ValueError("Invalid compact decision")
        position, decision, role, criteria, reason = entry
        if type(position) is not int or not 1 <= position <= len(batch) or position in positions:
            raise ValueError("Duplicate/out-of-range batch position")
        positions.add(position)
        item = {"paper_id": batch[position - 1]["paper_id"], "decision": DECISIONS[decision], "research_role": ROLES[role],
                "matched_criteria": criteria.split(","), "reason": reason, "needs_full_text_review": decision != "E"}
        validate(item)
        items.append(item)
    items.sort(key=lambda item: next(i for i, r in enumerate(batch) if r["paper_id"] == item["paper_id"]))
    directory = ROOT / "results/semantic_batches"
    path = directory / f"batch_{len(list(directory.glob('batch_*.json'))) + 1:03d}.json"
    # Exclusive creation prevents accidental checkpoint overwrites.
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {path.name}: {len(items)} decisions")


def export(source, preliminary, classified, fingerprint):
    rows = []
    for row, pre in zip(source, preliminary):
        if row["paper_id"] not in classified:
            continue
        decision = classified[row["paper_id"]]
        attached = {**row, **{k: v for k, v in pre.items() if k not in row}, **decision}
        attached["matched_criteria"] = json.dumps(decision["matched_criteria"], separators=(",", ":"))
        attached["needs_full_text_review"] = str(decision["needs_full_text_review"]).lower()
        attached["synthesis_set"] = ("UNRESOLVED" if decision["decision"] == "MAYBE" else
                                     "NOT_SELECTED" if decision["decision"] == "EXCLUDE" else
                                     "PRIMARY" if "I1" in decision["matched_criteria"] else "SUPPORTING")
        attached["screening_stage"] = "title_abstract"
        attached["screening_method"] = "Codex session; no API; no full text"
        attached["semantic_protocol_version"] = "1.0"
        attached["semantic_reviewer"] = "Codex session (single reviewer)"
        attached["assessment_date"] = "2026-10-28"
        rows.append(attached)
    columns = list(rows[0]) if rows else list(preliminary[0]) + sorted(KEYS - {"paper_id"})
    outputs = {"semantic_screening.csv": rows, "included.csv": [r for r in rows if r["decision"] == "INCLUDE"],
               "maybe.csv": [r for r in rows if r["decision"] == "MAYBE"], "excluded.csv": [r for r in rows if r["decision"] == "EXCLUDE"]}
    for name, subset in outputs.items():
        with (ROOT / "results" / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(subset)
    counts = Counter(r["decision"] for r in rows)
    roles = Counter(r["research_role"] for r in rows)
    reasons = Counter(code for r in rows if r["decision"] == "EXCLUDE" for code in json.loads(r["matched_criteria"]))
    report = ["# Semantic screening report", "", f"Status: {'complete' if len(rows) == len(source) else 'in progress'}. Screened **{len(rows)}/{len(source)}** unique papers; original source metadata and preliminary annotations retained in every output.", "",
              "## Decisions", "", "| Decision | Papers |", "| --- | ---: |"]
    report += [f"| {key} | {counts[key]} |" for key in DECISIONS.values()]
    report += ["", "## Research roles", "", "| Role | INCLUDE | MAYBE | EXCLUDE | Total |", "| --- | ---: | ---: | ---: | ---: |"]
    report += [f"| {key} | " + " | ".join(str(sum(r['research_role'] == key and r['decision'] == decision for r in rows)) for decision in DECISIONS.values()) + f" | {roles[key]} |" for key in ROLES.values()]
    report += ["", "## Main exclusion reasons", ""]
    explanations = {"E1": "Clearly security/safety/performance-focused without substantive privacy analysis or supporting privacy content.",
                    "E2": "No substantive mobility connection or defensible foundational transfer.", "E3": "No substantive threat contribution or specific supporting use.",
                    "E4": "Generic framework contribution without an established supporting use.", "E5": "Publication artifact rather than substantive research."}
    report += [f"- {key}: **{count}**. {explanations[key]}" for key, count in sorted(reasons.items())] or ["None."]
    report += ["", "## Method and interpretation", "",
               "The available Codex session performed semantic judgments directly; no model API connection was assumed or used. Only paper ID, title, full supplied abstract, keywords and publication year were exposed for semantic assessment. No full papers, authors, venues, DOI information or preliminary keyword scores were used to infer relevance. Local Python joined preserved metadata without using it as semantic evidence.", "",
               "Every unique source paper is assessed; preliminary categories do not determine final eligibility. In this corpus preliminary screening excluded none. Records are processed in source CSV order, in batches of at most 20. The first 20 constitute the fixed calibration sample (IDs in batch_001.json); labels distinguish concrete threat analysis, empirical evidence, explicit privacy mitigation, supporting context and ambiguous claims. No selection quota or new date/venue restriction was applied.", "",
               "INCLUDE requires an evidenced I1/I2/I3 route. Concrete mobility privacy mitigation and empirical attacks remain eligible without a formal threat-modeling framework. Generic security/integrity/availability studies with no substantive privacy contribution are excluded only when the abstract clearly establishes their different focus. Generic privacy mentions, uncertain confidentiality claims and potential foundations are retained as MAYBE when relevance remains unresolved. Framework papers are not automatically core evidence.", "",
               "MAYBE criterion IDs denote provisional inclusion routes, not confirmed fulfillment. Their roles are provisional. INCLUDE advances to full-text verification; both INCLUDE and MAYBE therefore set needs_full_text_review=true. Abstract-resolved EXCLUDE sets false; that flag does not prevent a reviewer from auditing or reversing the exclusion. All rows, including excluded records, preserve original metadata and provenance. No paper content or findings were invented.", "",
               "Synthesis placement is PRIMARY for included I1 papers, SUPPORTING for included I2/I3 papers, UNRESOLVED for MAYBE and NOT_SELECTED for EXCLUDE. Reasons contain at most 25 whitespace-separated words. Outputs are abstract-stage recommendations, not independently verified full-text eligibility decisions.", "",
               "## Reproduce, resume and audit", "",
               "- python3 scripts/semantic_screening.py next: prints only the next unclassified batch's allowed metadata. Never requests completed batches again.",
               "- python3 scripts/semantic_screening.py save: accepts compact JSON decisions on stdin, validates and immediately saves a batch checkpoint, then regenerates outputs.",
               "- python3 scripts/semantic_screening.py export: validates saved classifications and regenerates all five outputs without model calls.",
               "- config/semantic_screening_schema.json defines the persisted six-field decision schema; the Python validator enforces types, enums, reasons, identity uniqueness and decision/role/criterion consistency.",
               "- results/semantic_batches/batch_*.json contain independent validated decisions. manifest.json fingerprints all inputs and prevents mixing decisions after an input change. Preserve checkpoints before starting a revised protocol run.",
               "- Re-running export is deterministic; semantic judgments themselves are recorded session decisions, not a claim of deterministic model inference. No original data or preliminary classifications are modified.", "",
               "## Limitations and remaining review", "",
               "One Codex session supplied these judgments. No independent second reviewer or human adjudication has been completed; the criteria's preferred independent exclusion review remains outstanding. A second pass within this session may correct internal inconsistencies but does not provide independent validation. Review uncertain papers and audit exclusions before treating these recommendations as final study selection. Supporting claims and empirical/secondary-source overlap require full-text assessment. Missing details in otherwise plausible abstracts lead to MAYBE rather than assumed irrelevance.", "",
               "## Input fingerprints", ""]
    report += [f"- {name}: `{value}`." for name, value in fingerprint.items()]
    (ROOT / "results/semantic_screening_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Saved {len(rows)}/{len(source)}: " + "; ".join(f"{key}={counts[key]}" for key in DECISIONS.values()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("next", "save", "export"))
    command = parser.parse_args().command
    source, preliminary, classified, fingerprint = load()
    if command == "next":
        show_next(source, classified)
    else:
        if command == "save":
            save(source, classified)
            source, preliminary, classified, fingerprint = load()
        export(source, preliminary, classified, fingerprint)


if __name__ == "__main__":
    main()
