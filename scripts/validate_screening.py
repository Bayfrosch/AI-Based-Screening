#!/usr/bin/env python3
"""Audit recommendations without changing labels; preserve editable manual samples.

Run: python3 scripts/validate_screening.py [--manual-file results/completed.csv]
Standard library only. Heuristic flags nominate review, never correct decisions.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

from semantic_screening import DECISIONS, ROLES, validate

ROOT = Path(__file__).resolve().parents[1]
SEED = "mobility-privacy-validation-v1"
DECISION_LABELS = list(DECISIONS.values())
ROLE_LABELS = list(ROLES.values())
STOP = set("a an the and of for in to with on based using scheme protocol efficient secure security authentication vehicular networks network vanets vanet vehicles vehicle".split())
PRIVACY = re.compile(r"\b(?:privac\w*|anonym\w*|pseudonym\w*|unlink\w*|linkab\w*|confidential\w*|personal\s+(?:data|information)|sensitive\s+(?:data|information)|disclos\w*|eavesdropp\w*|re[- ]?identif\w*|inference\s+attacks?|profiling|surveillance)\b", re.I)
SPECIFIC = re.compile(r"\b(?:anonym\w*|pseudonym\w*|pseudo[- ]?id\w*|unlink\w*|linkab\w*|untraceab\w*|identit\w*|locations?|trajector\w*|tracking|personal\s+(?:data|information)|sensitive\s+(?:data|information)|confidential\w*|disclos\w*|leak\w*|inference\s+attacks?|profiling|surveillance|unobservability|individual\s+feedback|data\s+exfiltration|de[- ]?identif\w*|original\s+data|intermediate\s+(?:training\s+)?values|content\w*\s+(?:are\s+)?kept\s+secret|conditional\s+trac\w*)\b", re.I)
MOBILITY = re.compile(r"\b(?:vehicl\w*|vehicular|automotiv\w*|transport\w*|V2X|IoV|VANETs?|navigation|trajector\w*|location[- ]based|traffic)\b", re.I)
FRAMEWORK_PRIVACY = re.compile(r"\b(?:user[- ]sensitive\s+information|personal\s+(?:data|information)|data\s+exfiltration|location\s+(?:privacy|tracking)|identity\s+(?:privacy|disclosure)|re[- ]?identification|trajectory\s+linking)\b", re.I)
MODEL_ABSENCE_REASON = re.compile(r"(?:\b(?:no|without|lack\w*|missing|absence|does\s+not)\b.{0,65}\b(?:threat[- ]modell?ing|formal\s+(?:threat|adversary)\s+model))|(?:\bthreat[- ]modell?ing\b.{0,45}\b(?:absent|missing|required)\b)", re.I)


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Invalid CSV headers: {path}")
        rows = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError(f"Invalid CSV row width: {path}")
        return rows


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def evidence(pattern, text):
    return sorted(set(match.group() for match in pattern.finditer(text)))


def similarity_pairs(rows):
    pairs = []
    for a, b in combinations(rows, 2):
        if a["decision"] == b["decision"]:
            continue
        ta = set(re.findall(r"\w+", a["title"].casefold())) - STOP
        tb = set(re.findall(r"\w+", b["title"].casefold())) - STOP
        if len(ta & tb) < 3:
            continue
        jaccard = len(ta & tb) / len(ta | tb)
        if jaccard < 0.50:
            continue
        ratio = SequenceMatcher(None, a["title"].casefold(), b["title"].casefold(), autojunk=False).ratio()
        if jaccard >= 0.65 or ratio >= 0.82:
            pairs.append({"paper_id_a": a["paper_id"], "paper_id_b": b["paper_id"], "decision_a": a["decision"], "decision_b": b["decision"],
                          "title_a": a["title"], "title_b": b["title"], "title_ratio": round(ratio, 6), "informative_token_jaccard": round(jaccard, 6),
                          "review_note": "Different abstracts can justify different decisions; inspect the privacy-evidence threshold, not title similarity alone."})
    return sorted(pairs, key=lambda p: (-max(p["title_ratio"], p["informative_token_jaccard"]), p["paper_id_a"], p["paper_id_b"]))


def audit(rows, criteria_hash, notes):
    flags, errors = [], []

    def flag(row, code, priority, note, proof=None, related=None):
        flags.append({"paper_id": row["paper_id"], "title": row["title"], "decision": row["decision"], "research_role": row["research_role"],
                      "flag_code": code, "priority": priority, "review_note": note, "evidence_json": packed(proof or []), "related_paper_ids_json": packed(related or [])})

    by_id = {r["paper_id"]: r for r in rows}
    for paper_id, n in Counter(r["paper_id"] for r in rows).items():
        if not paper_id or n > 1:
            errors.append(f"Missing/duplicate paper_id {paper_id!r}: {n} rows")
    for row in rows:
        try:
            codes = json.loads(row["matched_criteria"])
            if row["needs_full_text_review"] not in ("true", "false"):
                raise ValueError("invalid needs_full_text_review")
            validate({"paper_id": row["paper_id"], "decision": row["decision"], "research_role": row["research_role"], "matched_criteria": codes,
                      "reason": row["reason"], "needs_full_text_review": row["needs_full_text_review"] == "true"})
        except (ValueError, TypeError, KeyError) as error:
            errors.append(f"{row['paper_id']}: {error}")
            flag(row, "INVALID_CLASSIFICATION", 4, str(error))
            codes = []
        if row.get("screening_criteria_sha256") != criteria_hash:
            flag(row, "CRITERIA_FINGERPRINT_MISMATCH", 3, "Recorded screening-criteria hash differs from the current protocol; check whether reassessment is needed.")
        abstract = row["abstract"].strip()
        if not abstract or len(abstract) < 100 or len(abstract.split()) < 20 or abstract.endswith(("...", "…")):
            flag(row, "MISSING_SHORT_OR_TRUNCATED_ABSTRACT", 3 if row["decision"] == "EXCLUDE" else 2, "Missing, short (<100 characters or <20 words), or ellipsis-ended abstract; review evidence completeness.")
        if row["decision"] == "MAYBE":
            flag(row, "ABSTRACT_RELEVANCE_UNRESOLVED", 0, "Existing justification identifies unresolved eligibility; metadata is not necessarily missing or truncated.")
        if row["decision"] == "INCLUDE":
            if row["research_role"] in ("BACKGROUND", "FRAMEWORK_FOCUSED") and "I1" in codes:
                flag(row, "ROLE_ROUTE_CONFLICT", 3, "Background/generic-framework role is assigned primary I1 evidence; check role or supporting route.")
            if not SPECIFIC.search(abstract):
                flag(row, "I1_SPECIFIC_PRIVACY_EVIDENCE_CHECK", 1, "No configured specific privacy cue in the abstract. Verify I1 without inferring threats from cryptographic primitives alone; lexical absence is not proof of error.")
        if row["decision"] == "EXCLUDE":
            body_terms = evidence(PRIVACY, row["title"] + " " + abstract)
            keywords = " ".join(json.loads(row.get("keywords_json") or "[]"))
            if body_terms:
                flag(row, "POSSIBLE_FALSE_NEGATIVE_BODY", 2, "Excluded paper explicitly mentions privacy-equivalent concepts. Check whether substantive I1/I2/I3 content was overlooked; introductory mentions can still justify E1.", body_terms)
            elif PRIVACY.search(keywords):
                flag(row, "POSSIBLE_FALSE_NEGATIVE_KEYWORDS_ONLY", 1, "Privacy-equivalent keyword warrants a check; a keyword alone does not invalidate exclusion.", evidence(PRIVACY, keywords))
            if MODEL_ABSENCE_REASON.search(row["reason"]):
                flag(row, "THREAT_MODEL_TERM_REQUIRED_IN_REASON", 3, "Exclusion justification appears to require explicit threat modeling/formal models, contrary to I1 safeguards.", evidence(MODEL_ABSENCE_REASON, row["reason"]))
        if row["research_role"] == "FRAMEWORK_FOCUSED" and MOBILITY.search(abstract) and FRAMEWORK_PRIVACY.search(abstract):
            flag(row, "FRAMEWORK_WITH_CONCRETE_PRIVACY_CUE", 2, "Framework paper contains a concrete mobility privacy/data-exfiltration cue; inspect whether findings support CORE/THREAT_EVIDENCE or a secondary role. A cue does not establish substantive analysis.", evidence(FRAMEWORK_PRIVACY, abstract))
    pairs = similarity_pairs(rows)
    for pair in pairs:
        for side, other in (("a", "b"), ("b", "a")):
            row = by_id[pair[f"paper_id_{side}"]]
            flag(row, "SIMILAR_TITLE_DIFFERENT_DECISION", 2 if "EXCLUDE" in (pair["decision_a"], pair["decision_b"]) else 1,
                 pair["review_note"], [{"title_ratio": pair["title_ratio"], "token_jaccard": pair["informative_token_jaccard"]}], [pair[f"paper_id_{other}"]])
    for note in notes:
        if note["paper_id"] in by_id:
            flag(by_id[note["paper_id"]], note["code"], note["priority"], note["note"])
        else:
            errors.append(f"Unknown paper in validation_review_notes.json: {note['paper_id']}")
    return sorted(flags, key=lambda f: (-f["priority"], f["paper_id"], f["flag_code"])), pairs, errors


def sample_rows(rows, flags):
    by_id = defaultdict(list)
    for flag in flags:
        by_id[flag["paper_id"]].append(flag)
    rank = lambda r: hashlib.sha256(f"{SEED}|{r['paper_id']}".encode()).hexdigest()
    selected = []
    for decision in DECISION_LABELS:
        pool = sorted([r for r in rows if r["decision"] == decision], key=rank)
        scores = {r["paper_id"]: max((f["priority"] for f in by_id[r["paper_id"]]), default=0) for r in pool}
        priority = sorted([r for r in pool if scores[r["paper_id"]] > 0], key=lambda r: (-scores[r["paper_id"]], rank(r)))[:6]
        chosen = {r["paper_id"] for r in priority}
        baseline = [r for r in pool if r["paper_id"] not in chosen][:10 - len(priority)]
        for row in priority + baseline:
            paper_flags = by_id[row["paper_id"]]
            selected.append({**{k: row[k] for k in ("paper_id", "title", "abstract", "keywords_json", "publication_year")},
                             "automated_decision": row["decision"], "automated_research_role": row["research_role"], "matched_criteria": row["matched_criteria"], "automated_reason": row["reason"],
                             "review_flags_json": packed(sorted({f["flag_code"] for f in paper_flags})),
                             "review_notes_json": packed([f["review_note"] for f in paper_flags if f["priority"] > 0]),
                             "related_paper_ids_json": packed(sorted({other for f in paper_flags for other in json.loads(f["related_paper_ids_json"])})),
                             "sample_selection": "priority_review" if row["paper_id"] in chosen else "hash_baseline",
                             "my_classification": "", "my_research_role": "", "my_comments": ""})
    return selected


def compare_manual(rows, paths):
    by_id = {r["paper_id"]: r for r in rows}
    collected = defaultdict(list)
    problems = []
    for path in paths:
        for item in read_csv(path):
            if "my_classification" not in item:
                continue
            label, role = item["my_classification"].strip().upper(), item.get("my_research_role", "").strip().upper()
            if not label and not role:
                continue
            paper_id = item.get("paper_id", "")
            if paper_id not in by_id or (label and label not in DECISION_LABELS) or (role and role not in ROLE_LABELS):
                problems.append(f"{path.name}: invalid manual ID/label/role for {paper_id!r}; not scored")
                continue
            if label and role and ((label != "EXCLUDE" and role == "OUT_OF_SCOPE") or (label == "EXCLUDE" and role not in ("OUT_OF_SCOPE", "FRAMEWORK_FOCUSED"))):
                problems.append(f"{path.name}: contradictory manual decision/role for {paper_id}; not scored")
                continue
            if item.get("automated_decision", by_id[paper_id]["decision"]) != by_id[paper_id]["decision"]:
                problems.append(f"{path.name}: stale automated decision for {paper_id}; not scored")
                continue
            collected[paper_id].append((label, role))
    labels, role_pairs = [], []
    for paper_id, entries in sorted(collected.items()):
        decisions = {label for label, _ in entries if label}
        roles = {role for _, role in entries if role}
        if len(decisions) > 1 or len(roles) > 1:
            problems.append(f"Conflicting manual reference labels for {paper_id}; not scored")
            continue
        if decisions:
            labels.append((by_id[paper_id]["decision"], next(iter(decisions))))
        if roles:
            role_pairs.append((by_id[paper_id]["research_role"], next(iter(roles))))
    result = {"labeled_decisions": len(labels), "labeled_roles": len(role_pairs), "problems": problems}
    if labels:
        matrix = Counter(labels)
        observed = sum(a == b for a, b in labels) / len(labels)
        auto, reference = Counter(a for a, _ in labels), Counter(b for _, b in labels)
        expected = sum(auto[c] * reference[c] for c in DECISION_LABELS) / len(labels) ** 2
        result.update({"agreement": observed, "kappa": (observed - expected) / (1 - expected) if expected < 1 else None,
                       "confusion": [[matrix[(a, b)] for b in DECISION_LABELS] for a in DECISION_LABELS]})
        positives = [(a, b) for a, b in labels if b == "INCLUDE"]
        if positives:
            result["reference_includes"] = len(positives)
            result["include_recall"] = sum(a == "INCLUDE" for a, _ in positives) / len(positives)
            result["retention_recall"] = sum(a != "EXCLUDE" for a, _ in positives) / len(positives)
    if role_pairs:
        result["role_agreement"] = sum(a == b for a, b in role_pairs) / len(role_pairs)
    return result


def run(root=ROOT, manual_files=()):
    source_path, criteria_path = root / "results/semantic_screening.csv", root / "config/screening_criteria.md"
    original, criteria = source_path.read_bytes(), criteria_path.read_bytes()
    rows = read_csv(source_path)
    notes_path = root / "config/validation_review_notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf8")) if notes_path.exists() else []
    flags, pairs, errors = audit(rows, hashlib.sha256(criteria).hexdigest(), notes)
    by_id = {r["paper_id"]: r for r in rows}
    merged_path = root / "results/merged_papers.csv"
    coverage = "No independent input registry available: completeness can only be checked within semantic_screening.csv."
    if merged_path.exists():
        expected = {r["paper_id"] for r in read_csv(merged_path)}
        missing, unexpected = sorted(expected - set(by_id)), sorted(set(by_id) - expected)
        coverage = f"Compared with merged_papers.csv: {len(expected)} expected unique IDs; missing decisions {len(missing)}; unexpected IDs {len(unexpected)}."
        errors += [f"Missing semantic record: {paper_id}" for paper_id in missing] + [f"Unexpected semantic record: {paper_id}" for paper_id in unexpected]
    counts, flag_counts = Counter(r["decision"] for r in rows), Counter(f["flag_code"] for f in flags)
    sample_path = root / "results/manual_validation_sample.csv"
    if not sample_path.exists():
        sample = sample_rows(rows, flags)
        write_csv(sample_path, sample, list(sample[0]))
    sample_status = "The sample is created only when absent; existing membership and reviewer entries are preserved byte-for-byte on reruns."
    sample = read_csv(sample_path)
    discovered = []
    for path in (root / "results").glob("*validation*.csv"):
        if path == sample_path:
            continue
        with path.open(encoding="utf-8-sig", newline="") as handle:
            if "my_classification" in next(csv.reader(handle), []):
                discovered.append(path)
    paths = sorted({sample_path, *manual_files, *discovered})
    manual = compare_manual(rows, paths)
    write_csv(root / "results/validation_flags.csv", flags, ["paper_id", "title", "decision", "research_role", "flag_code", "priority", "review_note", "evidence_json", "related_paper_ids_json"])
    write_csv(root / "results/similar_screening_pairs.csv", pairs, ["paper_id_a", "paper_id_b", "decision_a", "decision_b", "title_a", "title_b", "title_ratio", "informative_token_jaccard", "review_note"])
    negative_ids = {f["paper_id"] for f in flags if f["flag_code"].startswith("POSSIBLE_FALSE_NEGATIVE") or f["flag_code"] == "PRIORITY_FALSE_NEGATIVE_CHECK"}
    questionable_ids = {f["paper_id"] for f in flags if f["priority"] > 0}
    structurally_valid_reasons = sum(bool(r["reason"].strip()) and len(r["reason"].split()) <= 25 for r in rows)
    report = ["# Semantic screening validation report", "",
              "Run `python3 scripts/validate_screening.py`; optionally add `--manual-file results/completed_validation.csv`. Original classifications are read only. Flags are review nominations, not corrected labels or confirmed errors. No full papers were read.", "",
              "## Coverage and formal consistency", "",
              f"- Rows: {len(rows)}; unique paper IDs: {len(by_id)}. {coverage}",
              f"- Decision counts: " + "; ".join(f"{label}: {counts[label]}" for label in DECISION_LABELS) + ".",
              f"- Invalid decision labels: {sum(r['decision'] not in DECISION_LABELS for r in rows)}; invalid research roles: {sum(r['research_role'] not in ROLE_LABELS for r in rows)}.",
              f"- Nonempty justifications of at most 25 words: {structurally_valid_reasons}/{len(rows)}. Maximum reason length: {max((len(r['reason'].split()) for r in rows), default=0)} words.",
              f"- Formal coverage/schema/decision-role-route errors: {len(errors)}. Criterion IDs and full-text flags checked with the screening validator.", "",
              "Formal validity does not prove semantic validity. Short reasons sometimes describe a mechanism without demonstrating its personal-data relevance. The checks below identify cases needing judgment, not ground-truth error rates.", ""]
    report += [f"- {error}" for error in errors]
    report += ["## Questionable decisions and possible false negatives", "",
               f"{len(questionable_ids)} distinct records have a non-informational review flag. {len(negative_ids)} excluded records are nominated for possible false-negative checks. All flags, evidence terms and related IDs are in results/validation_flags.csv.", "",
               "| Flag | Records/instances |", "| --- | ---: |"]
    report += [f"| {code} | {count} |" for code, count in sorted(flag_counts.items())]
    report += ["", "### Priority abstract-level findings", ""]
    for note in notes:
        if note["paper_id"] in by_id:
            row = by_id[note["paper_id"]]
            report.append(f"- `{note['paper_id']}` — {row['title']} ({row['decision']}, {row['research_role']}): {note['note']}")
    report += ["", "### Interpretation against the criteria", "",
               "The main audit concern is uneven I1 evidence thresholds: some included authentication schemes rely on conditional-privacy or cryptographic-mechanism claims while similar schemes remain MAYBE. Confirm a specific privacy harm, affected data/identity relationship or tested privacy property; do not equate encryption, zero-knowledge proofs or signature correctness alone with substantive mobility privacy analysis.", "",
               "The excluded SMAKA critique is a priority potential false negative because its original protocol is included. The alternative explanation is an overly generous inclusion of the original: the abstract describes an anonymous CSP broadcast rather than clearly anonymous vehicle users. Reviewing the pair must not automatically promote the critique or infer a privacy attack from impersonation alone.", "",
               "Excluded papers containing privacy terms or keywords warrant inspection but may correctly satisfy E1 when the analyzed harm is exclusively forgery, integrity, availability or safety. Consider I2/I3 supporting use explicitly. This lexical check neither proves an exclusion wrong nor clears unflagged exclusions.", "",
               "Exclusion criterion counts: " + packed(dict(Counter(code for row in rows if row['decision']=='EXCLUDE' for code in json.loads(row['matched_criteria'])))) + ". Concentration on E1 merits a consistent check of supporting routes, but is not itself an error or an imposed target for label changes.", "",
               "## Abstract completeness and adequacy", "",
               f"- Mechanically missing, short or ellipsis-ended abstracts: {flag_counts['MISSING_SHORT_OR_TRUNCATED_ABSTRACT']}.",
               f"- Existing MAYBE records whose metadata remains insufficient to resolve eligibility: {counts['MAYBE']}. This is conceptual insufficiency, not missing bibliographic data.",
               "- Length checks use <100 characters or <20 whitespace-separated words. These are review signals, never relevance exclusions. A complete-looking abstract may still omit decisive methods, adversary assumptions or privacy results.", "",
               "## Similar papers with differing classifications", "",
               f"{len(pairs)} title-similar pairs with different decisions were found. Full pair list: results/similar_screening_pairs.csv.", ""]
    report += [f"- `{p['paper_id_a']}` ({p['decision_a']}) ↔ `{p['paper_id_b']}` ({p['decision_b']}): title ratio {p['title_ratio']:.3f}, informative-token Jaccard {p['informative_token_jaccard']:.3f}." for p in pairs]
    report += ["", "Comparison uses lowercased title words minus a fixed domain/boilerplate stoplist, at least three shared informative tokens, Jaccard >=0.50, and then either Jaccard >=0.65 or SequenceMatcher ratio >=0.82 (autojunk disabled). Similarity is not duplicate identity or evidence that labels must agree. Original protocols and cryptanalytic comments can legitimately have different privacy contributions; differing abstract specificity can also justify INCLUDE versus MAYBE.", "",
               "## Exclusion due to missing threat-model terminology", "",
               f"Exclusion reasons explicitly suggesting a required formal model or explicit threat-modeling terminology: {flag_counts['THREAT_MODEL_TERM_REQUIRED_IN_REASON']}.",
               f"Excluded records without a threat-modeling phrase in title/abstract: {sum(r['decision']=='EXCLUDE' and not re.search(r'threat[- ]modell?ing',r['title']+' '+r['abstract'],re.I) for r in rows)}. Absence is descriptive, not evidence of the cause of exclusion.",
               "No hidden reasoning can be reconstructed from a short justification. The recorded reasons are the auditable evidence; where no terminology requirement is found, this audit cannot prove that implicit bias never occurred. Neither the criteria nor the validation rules require that phrase.", "",
               "## Framework-focused papers containing concrete privacy cues", "",
               f"Flagged framework-focused records: {flag_counts['FRAMEWORK_WITH_CONCRETE_PRIVACY_CUE']}. The TARA engine mentioning sensitive-information extraction and TraCR-TMF's data-exfiltration case deserve specific attention.",
               "These abstracts establish a concrete privacy-related cue, not necessarily a demonstrated mobility privacy analysis. Check whether their evaluated results support CORE/THREAT_EVIDENCE, a secondary role, or FRAMEWORK_FOCUSED supporting literature. Applying STRIDE/LINDDUN is not itself grounds for framework-focused placement or exclusion. No confirmed role changes are made.", "",
               "## Manual validation sample", "",
               sample_status,
               f"Sample size: {len(sample)}; strata: " + "; ".join(f"{label}: {sum(r['automated_decision']==label for r in sample)}" for label in DECISION_LABELS) + ".",
               f"Initial selection seed: `{SEED}`. Per decision stratum: up to six records with positive-priority flags, ordered by highest priority then SHA-256(seed|paper_id), followed by hash-ranked remaining records to reach ten. If fewer than ten exist, retain all. Flag definitions, thresholds and curated review notes are versioned with the script and config/validation_review_notes.json.",
               "This is a balanced, risk-enriched sample rather than a representative probability sample. Metrics describe only the labeled sample. Do not extrapolate population recall or error rates from it.",
               "Fill my_classification (INCLUDE/MAYBE/EXCLUDE), my_research_role (one permitted role) and my_comments in results/manual_validation_sample.csv, then rerun the audit. Keep paper_id unchanged. For a less anchored first judgment, hide automated-label/reason and flag columns until recording your own decision. A MAYBE reference label remains unresolved, not a confirmed positive.",
               "Existing sample files are never overwritten. Additional completed *validation*.csv files with my_classification are discovered in results/; --manual-file supports another filename. Duplicate reference labels are consolidated by paper ID; conflicts, unknown IDs and invalid labels are reported and not scored.", "",
               "## Manual-reference comparison", ""]
    report += [f"Manual files inspected: " + ", ".join(f"`{p.name}`" for p in paths) + ".",
               f"Valid manually labeled decisions: {manual['labeled_decisions']}; valid manually labeled roles: {manual['labeled_roles']}."]
    if manual["labeled_decisions"]:
        report += [f"Exact three-class agreement: {manual['agreement']:.3f}; Cohen's kappa: " + (f"{manual['kappa']:.3f}" if manual['kappa'] is not None else "undefined (expected agreement is one)") + ".", "",
                   "Confusion matrix: rows automated, columns manual.", "", "| Automated / Manual | INCLUDE | MAYBE | EXCLUDE |", "| --- | ---: | ---: | ---: |"]
        report += [f"| {label} | " + " | ".join(map(str, values)) + " |" for label, values in zip(DECISION_LABELS, manual["confusion"])]
    else:
        report.append("No manual reference decisions are available. Agreement, kappa and recall were not calculated; automated labels and audit suggestions are not reference truth.")
    if "include_recall" in manual:
        report += [f"Sample INCLUDE recall: {manual['include_recall']:.3f}; sample retention recall: {manual['retention_recall']:.3f}; denominator: {manual['reference_includes']} manually confirmed INCLUDE records.",
                   "INCLUDE recall = automated INCLUDE / manual INCLUDE; retention recall = automated INCLUDE or MAYBE / manual INCLUDE. Manual MAYBE and unlabeled records are excluded from these denominators; incomplete labels restrict claims to the scored subset."]
    elif manual["labeled_decisions"]:
        report.append("Recall not calculated: no manually confirmed INCLUDE reference positives exist in the scored subset.")
    if "role_agreement" in manual:
        report.append(f"Research-role exact agreement: {manual['role_agreement']:.3f}.")
    report += [f"- {problem}" for problem in manual["problems"]]
    report += ["", "## Audit trail and limitations", "",
               f"- semantic_screening.csv SHA-256: `{hashlib.sha256(original).hexdigest()}`.",
               f"- screening_criteria.md SHA-256: `{hashlib.sha256(criteria).hexdigest()}`.",
               f"- validation_review_notes.json SHA-256: `{hashlib.sha256(notes_path.read_bytes()).hexdigest()}`." if notes_path.exists() else "- No curated review notes supplied.",
               f"- validate_screening.py SHA-256: `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`.",
               "- The current Codex session inspected priority abstracts and generated explicit audit notes, not human reference labels. Re-running Python reproduces flags and sample selection for unchanged inputs; it does not rerun semantic judgment or change automated labels.",
               "- Priority 3–4 means urgent review/formal error, 2 means targeted review, 1 means a weaker lexical/similarity check, and 0 marks existing unresolved abstracts. None represents a measured probability of error.",
               "- M/P/C/T dimension judgments and supporting-transfer rationales were not separately stored by the original six-field semantic schema. Matched I1 codes and short reasons do not constitute an independently auditable dimensional assessment. Record that detail during manual review.",
               "- Independent human adjudication remains necessary. No full-text eligibility, corpus-wide recall or automatic classification corrections are claimed.", ""]
    if source_path.read_bytes() != original or criteria_path.read_bytes() != criteria:
        raise ValueError("A read-only input changed during validation")
    (root / "results/validation_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Audited {len(rows)} records; formal errors {len(errors)}; review-flagged records {len(questionable_ids)}; possible false-negative checks {len(negative_ids)}; manual sample {len(sample)}; manual reference decisions {manual['labeled_decisions']}.")
    return {"flags": flags, "pairs": pairs, "errors": errors, "manual": manual}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual-file", action="append", type=Path, default=[])
    arguments = parser.parse_args()
    run(manual_files=arguments.manual_file)
