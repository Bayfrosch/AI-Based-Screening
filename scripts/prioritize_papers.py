#!/usr/bin/env python3
"""Checkpoint metadata assessments and deterministically export reading priorities.

next displays at most 20 pending titles/abstracts/keywords; save accepts compact
JSON assessments on stdin; export regenerates artifacts without model calls.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_SIZE = 20


def read_csv(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("Missing or duplicate CSV column names")
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("Malformed CSV row")
    return rows


def priority(scores):
    direct, mobility, depth, system, explanatory, limitations = scores
    if ((direct == 2 and mobility >= 1 and explanatory == 2 and depth >= 1)
            or (mobility == 2 and depth == 2 and explanatory == 2 and system >= 1)):
        return "HIGH"
    return "MEDIUM" if mobility >= 1 and explanatory >= 1 else "LOW"


def validate(item, rubric):
    if set(item) != {"paper_id", "scores", "theme_codes", "contribution_focus", "priority_reason"}:
        raise ValueError("Unexpected assessment fields")
    if not isinstance(item["paper_id"], str) or not item["paper_id"]:
        raise ValueError("Invalid paper ID")
    scores = item["scores"]
    if not isinstance(scores, list) or len(scores) != 6 or any(type(v) is not int or not 0 <= v <= 2 for v in scores):
        raise ValueError("Scores must be six integers in 0..2")
    themes = item["theme_codes"]
    if not isinstance(themes, list) or not themes or len(set(themes)) != len(themes) or any(code not in rubric["themes"] for code in themes):
        raise ValueError("Invalid thematic categories")
    if item["contribution_focus"] not in rubric["contribution_focus"]:
        raise ValueError("Invalid contribution focus")
    if not isinstance(item["priority_reason"], str) or not 1 <= len(item["priority_reason"].split()) <= 25:
        raise ValueError("Reason must be 1–25 words")


def load():
    names = ["results/included.csv", "results/maybe.csv", "config/screening_criteria.md", "config/prioritization_rubric.json"]
    raw = {name: (ROOT / name).read_bytes() for name in names}
    included, maybe = read_csv(raw[names[0]]), read_csv(raw[names[1]])
    rubric = json.loads(raw[names[3]])
    if rubric["version"] != "1.0":
        raise ValueError("Unsupported rubric version")
    ids = [r["paper_id"] for r in included]
    maybe_ids = [r["paper_id"] for r in maybe]
    if len(set(ids)) != len(ids) or len(set(maybe_ids)) != len(maybe_ids) or set(ids) & set(maybe_ids):
        raise ValueError("Duplicate/overlapping source identities")
    if any(r["decision"] != "INCLUDE" for r in included) or any(r["decision"] != "MAYBE" for r in maybe):
        raise ValueError("Input decisions do not match the intended queues")
    directory = ROOT / "results/prioritization_batches"
    directory.mkdir(exist_ok=True)
    manifest = directory / "manifest.json"
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in raw.items()}
    if manifest.exists() and json.loads(manifest.read_text()) != hashes:
        raise ValueError("Inputs/rubric changed; preserve old checkpoints before explicitly starting a revised run")
    if not manifest.exists():
        manifest.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    done = {}
    for path in sorted(directory.glob("batch_*.json")):
        batch = json.loads(path.read_text(encoding="utf-8"))
        if not 1 <= len(batch) <= BATCH_SIZE:
            raise ValueError("Invalid batch size")
        for item in batch:
            validate(item, rubric)
            if item["paper_id"] not in ids or item["paper_id"] in done:
                raise ValueError("Unknown or duplicate checkpoint ID")
            done[item["paper_id"]] = item
    return included, maybe, rubric, done, hashes


def pending(rows, done):
    return [r for r in rows if r["paper_id"] not in done][:BATCH_SIZE]


def save(rows, done, rubric):
    batch = pending(rows, done)
    if not batch:
        raise ValueError("No papers remain pending")
    # [batch position, six scores, theme-code string, contribution code, <=25-word reason]
    compact = json.load(sys.stdin)
    if not isinstance(compact, list) or len(compact) != len(batch):
        raise ValueError("Supply one assessment per current batch record")
    items, positions = [], set()
    for entry in compact:
        position, scores, themes, focus, reason = entry
        if type(position) is not int or not 1 <= position <= len(batch) or position in positions:
            raise ValueError("Invalid/duplicate batch position")
        positions.add(position)
        item = {"paper_id": batch[position - 1]["paper_id"], "scores": scores, "theme_codes": list(themes), "contribution_focus": focus, "priority_reason": reason}
        validate(item, rubric)
        items.append(item)
    items.sort(key=lambda r: next(i for i, b in enumerate(batch) if b["paper_id"] == r["paper_id"]))
    directory = ROOT / "results/prioritization_batches"
    path = directory / f"batch_{len(list(directory.glob('batch_*.json'))) + 1:03d}.json"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {path.name}: {len(items)} assessments")


def export(included, maybe, rubric, done, hashes):
    rows = []
    for original in included:
        if original["paper_id"] not in done:
            continue
        assessment = done[original["paper_id"]]
        row = {**original, "priority": priority(assessment["scores"]), "priority_reason": assessment["priority_reason"],
               "thematic_categories": json.dumps([rubric["themes"][code] for code in assessment["theme_codes"]], ensure_ascii=False, separators=(",", ":")),
               "contribution_focus": rubric["contribution_focus"][assessment["contribution_focus"]],
               "priority_scores_json": json.dumps(dict(zip(rubric["dimensions"], assessment["scores"])), separators=(",", ":")),
               "prioritization_version": rubric["version"], "prioritization_evidence": "title; abstract; keywords only",
               "priority_review_note": "Privacy-specific usefulness is unclear from metadata; original INCLUDE remains unchanged." if priority(assessment["scores"]) == "LOW" else "Verify abstract-level usefulness and assumptions during full-text reading."}
        rows.append(row)
    scores = lambda r: done[r["paper_id"]]["scores"]
    # Within a priority tier, favor direct analysis, explanatory value and adversary detail; never year.
    rows.sort(key=lambda r: (("HIGH", "MEDIUM", "LOW").index(r["priority"]), -scores(r)[0], -scores(r)[4], -scores(r)[2], -scores(r)[5], -scores(r)[3], -scores(r)[1], r["paper_id"]))
    if not rows:
        raise ValueError("No saved assessments to export")
    outputs = {"prioritized_papers.csv": rows, **{f"{label.lower()}_priority.csv": [r for r in rows if r["priority"] == label] for label in ("HIGH", "MEDIUM", "LOW")}}
    for name, subset in outputs.items():
        with (ROOT / "results" / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(subset)
    # Keep unresolved eligibility entirely separate, preserving the existing MAYBE file byte-for-byte.
    (ROOT / "results/maybe_for_further_review.csv").write_bytes((ROOT / "results/maybe.csv").read_bytes())
    counts = Counter(r["priority"] for r in rows)
    theme_counts = Counter(theme for r in rows for theme in json.loads(r["thematic_categories"]))
    high_counts = Counter(theme for r in rows if r["priority"] == "HIGH" for theme in json.loads(r["thematic_categories"]))
    focus_counts = Counter(r["contribution_focus"] for r in rows)
    report = ["# Reading prioritization report", "", f"Status: {'complete' if len(rows)==len(included) else 'in progress'}. Assessed {len(rows)}/{len(included)} INCLUDE papers. All original metadata, semantic decisions and roles remain unchanged.", "",
              "## Priorities", "", "| Priority | Papers |", "| --- | ---: |"]
    report += [f"| {label} | {counts[label]} |" for label in ("HIGH", "MEDIUM", "LOW")]
    report += ["", "## Method", "",
               "The Codex session assessed each paper using its title, supplied abstract and keywords in batches of at most 20. No full papers, publication-year scores, venues, citation counts or automatic role-based rankings were used. Six 0–2 evidence dimensions are defined in config/prioritization_rubric.json: direct privacy threat analysis, mobility-specific privacy, adversary depth, system specificity, explanatory usefulness, and limitations/open challenges. Zero means not established by this metadata, not poor study quality.", "",
               "HIGH: direct threat analysis=2, mobility relevance>=1, explanatory usefulness=2, and adversary depth>=1; alternatively, mobility relevance=2, adversary depth=2, explanatory usefulness=2 and a specified system. This second route recognizes threat-specific defenses that explain concrete mobility exposures. MEDIUM: otherwise a mobility privacy connection and a concrete privacy property/protection concept are both established. LOW: supplementary or insufficiently specified privacy usefulness. LOW does not reverse INCLUDE or remove the need for full-text eligibility verification.", "",
               "There is no quota on HIGH. A cryptographic proof, scheme efficiency, generic framework name or a recent publication date alone cannot establish high priority. Applied STRIDE/LINDDUN privacy analyses are assessed by their threats and findings. Generic framework evaluation is distinguished from applied analysis in contribution_focus; no framework penalty is applied. Within tiers, deterministic ordering favors direct analysis, explanatory value, adversary depth, limitations, system specificity and mobility-specific privacy, followed by paper ID. Publication year is never used.", "",
               "Each assessment retains all six ordinal scores, one or more supplied thematic categories and a reason of at most 25 words. These are reading recommendations from metadata, not claims that full-text findings have been verified. Scores make the judgments inspectable; deterministic export does not imply independently reproducible model inference.", "",
               "## Research areas represented", "", "| Theme | All prioritized papers | HIGH |", "| --- | ---: | ---: |"]
    report += [f"| {theme} | {theme_counts[theme]} | {high_counts[theme]} |" for theme in rubric["themes"].values()]
    report += ["", "Thematic counts overlap because papers can receive multiple categories. Connected-vehicle/V2X protocols and privacy risk mitigation dominate this retrieved set. Pseudonyms, conditional anonymity, identity accountability, cloud/edge sharing and cryptographic access control recur. Higher-priority uses include explaining stakeholder trust, location/trajectory disclosure, linking attacks, compromised authorities, sensitive driver data and limitations of privacy mechanisms.", "",
               "Theme safeguards: authorized tracing of malicious vehicles is not automatically location surveillance. Generic unlinkability is not automatically trajectory correlation. Ordinary anonymity or direct identity disclosure does not by itself demonstrate re-identification. Re-identification tags cover identity guessing/linkage, tracking across changing pseudonyms and face deidentification, not a count of demonstrated attacks. Generic ITS is not automatically public transport/MaaS. Categories reflect explicit study topics, risks or protections, including attempts to prevent a threat; they do not assert a successful attack.", "",
               "The Mobility-specific threat modeling theme includes privacy-relevant adversary/scenario analysis within mitigation studies. The separate DIRECT_THREAT_ANALYSIS contribution count identifies papers organized primarily around threat/attack analysis. Do not interpret every thematic match as a dedicated modeling-method paper.", "",
               "### Contribution focus", "", "| Focus | Papers |", "| --- | ---: |"]
    report += [f"| {focus} | {focus_counts[focus]} |" for focus in rubric["contribution_focus"].values()]
    report += ["", "## Suggested first full-text readings", ""]
    report += [f"- `{r['paper_id']}` — {r['title']}: {r['priority_reason']}" for r in rows if r["priority"] == "HIGH"]
    report += ["", "## Topics with limited coverage", ""]
    report += [f"- {theme}: {theme_counts[theme]} paper(s) in the prioritized set; {high_counts[theme]} HIGH." for code, theme in rubric["themes"].items() if code in ("L", "R", "T", "I", "P", "M")]
    report += ["", "Small or zero counts indicate limited coverage in these included metadata records, not an absence of research in the field. Public-transport/MaaS, ride-sharing and cross-service trip histories need particular attention during further retrieval if absent here. Explicit re-identification and inference attacks should be distinguished from abundant anonymous-authentication protocols. Few direct modeling or empirical attack studies can coexist with many mitigation papers. Full-text reading should check assumed trust/collusion, whether linkability follows users across services, and which data flows the model omits; metadata does not establish those limitations for every paper.", "",
               "## Preserved unresolved literature", "",
               f"All {len(maybe)} MAYBE records are retained separately and unchanged in results/maybe.csv, with an exact copy in results/maybe_for_further_review.csv. They were not promoted, excluded or assigned priorities in this run. Their full-text assessment may change apparent coverage gaps. This report describes the INCLUDE set, not all retrieved literature.", "",
               "## Reproduce and resume", "",
               "- python3 scripts/prioritize_papers.py next: display the next unassessed batch using only title, abstract, keywords and paper ID.",
               "- python3 scripts/prioritize_papers.py save: validate compact session assessments, immediately save results/prioritization_batches/batch_*.json, and regenerate outputs.",
               "- python3 scripts/prioritize_papers.py export: validate saved assessments and deterministically regenerate the CSVs and report without model calls.",
               "- The manifest fingerprints inputs and rubric; input changes require an explicitly revised run. Never replace the original semantic classifications with priorities.", "",
               "## Input fingerprints", ""]
    report += [f"- {name}: `{digest}`." for name, digest in hashes.items()]
    (ROOT / "results/prioritization_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Prioritized {len(rows)}/{len(included)}: " + "; ".join(f"{label}={counts[label]}" for label in ("HIGH", "MEDIUM", "LOW")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("next", "save", "export"))
    command = parser.parse_args().command
    included, maybe, rubric, done, hashes = load()
    if command == "next":
        for n, row in enumerate(pending(included, done), 1):
            print(json.dumps({"n": n, **{k: row[k] for k in ("paper_id", "title", "abstract")}, "keywords": json.loads(row["keywords_json"])}, ensure_ascii=False, separators=(",", ":")))
        print(f"Progress: {len(done)}/{len(included)}", file=sys.stderr)
    else:
        if command == "save":
            save(included, done, rubric)
            included, maybe, rubric, done, hashes = load()
        export(included, maybe, rubric, done, hashes)


if __name__ == "__main__":
    main()
