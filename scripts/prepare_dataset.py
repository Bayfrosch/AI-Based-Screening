#!/usr/bin/env python3
"""Prepare bibliographic CSVs, retaining original metadata and merge decisions.

Run from any directory: python3 /path/to/scripts/prepare_dataset.py
Uses config/dataset_inspection.json and the Python standard library only.
"""

import csv
import hashlib
import io
import json
import re
import unicodedata
import uuid
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

from inspect_datasets import DOI, normalize_doi, normalize_title


ROOT = Path(__file__).resolve().parents[1]
# Thresholds are deliberately fixed and recorded in the report for reproducibility.
FUZZY_RATIO = 0.95
FUZZY_TOKEN_OVERLAP = 0.80
ALIASES = {
    "document_title": "title", "paper_title": "title",
    "author": "authors", "author_names": "authors",
    "year": "publication_year", "pub_year": "publication_year",
    "publication_title": "publication_venue", "venue": "publication_venue",
    "journal": "publication_venue", "journal_title": "publication_venue",
    "digital_object_identifier": "doi", "doi_link": "doi",
    "abstract_note": "abstract", "url": "url", "document_url": "url",
}
KEYWORD_FIELDS = ("keywords", "author_keywords", "ieee_terms", "mesh_terms", "index_keywords")
URL_FIELDS = ("url", "pdf_link", "document_link", "abstract_url")


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def column_name(value):
    key = re.sub(r"[^\w]+", "_", unicodedata.normalize("NFKC", value).strip().casefold()).strip("_")
    return ALIASES.get(key, key)


def clean(value, missing_values):
    # Original whitespace and placeholder strings remain in source_records_json.
    value = unicodedata.normalize("NFC", value).strip()
    return "" if value.casefold() in missing_values else value


def repair_funding_quotes(text, header, dialect):
    """Escape only illegal interior quotes in the known funding column.

    Reject other corruption instead of guessing field positions or losing records.
    The caller retains the exact original CSV text alongside the repaired fields.
    """
    if "Funding Information" not in header:
        raise ValueError("Malformed CSV has no supported funding-field repair")
    funding_index = header.index("Funding Information")
    output, column, in_quotes, at_start, count = [], 0, False, True, 0
    i = 0
    while i < len(text):
        char = text[i]
        following = text[i + 1:i + 2]
        if in_quotes and char == '"':
            if following == '"':
                output.append('""')
                i += 2
                continue
            if following and following not in (dialect["delimiter"], "\r", "\n"):
                if column != funding_index:
                    raise ValueError("Unexpected unescaped quote outside Funding Information")
                output.append('""')
                count += 1
                i += 1
                continue
            in_quotes = False
        elif not in_quotes:
            if at_start and char == '"':
                in_quotes = True
            elif char == dialect["delimiter"]:
                column += 1
                at_start = True
                output.append(char)
                i += 1
                continue
            at_start = False
        output.append(char)
        i += 1
    rows = list(csv.reader(io.StringIO("".join(output), newline=""), strict=True, **dialect))
    if not count or len(rows) != 1 or len(rows[0]) != len(header):
        raise ValueError("Malformed CSV could not be recovered unambiguously")
    return rows[0], f"Escaped {count} unescaped interior quotes in Funding Information; original CSV retained"


def load_records(paths, config):
    dialect = {k: config[k] for k in ("delimiter", "quotechar", "doublequote")}
    if dialect != {"delimiter": ",", "quotechar": '"', "doublequote": True}:
        raise ValueError("This importer requires standard comma/doubled-quote CSV")
    missing_values = set(config["missing_values"])
    records, inputs = [], []
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode(config["encoding"], errors="strict")
        physical = text.splitlines(keepends=True)
        reader = csv.reader(io.StringIO(text, newline=""), **dialect)
        header = next(reader)
        if len(set(header)) != len(header) or any(not h.strip() for h in header):
            raise ValueError(f"Empty or duplicate column names in {path}")
        end = reader.line_num
        count = 0
        for number, permissive_row in enumerate(reader, 1):
            count += 1
            start, end = end + 1, reader.line_num
            original_text = "".join(physical[start - 1:end])
            note = ""
            try:
                parsed = list(csv.reader(io.StringIO(original_text, newline=""), strict=True, **dialect))
                if len(parsed) != 1 or len(parsed[0]) != len(header):
                    raise ValueError("Unexpected CSV row width")
                row = parsed[0]
            except (csv.Error, ValueError):
                try:
                    row, note = repair_funding_quotes(original_text, header, dialect)
                except (csv.Error, ValueError) as error:
                    raise ValueError(f"Cannot safely parse {path.name} record {number}: {error}") from error
            original = dict(zip(header, row))
            metadata = defaultdict(list)
            for name, value in original.items():
                value = clean(value, missing_values)
                if value and value not in metadata[column_name(name)]:
                    metadata[column_name(name)].append(value)
            canonical = {k: values[0] for k, values in metadata.items()}
            doi = normalize_doi(canonical.get("doi", ""))
            flags = []
            if doi and not DOI.fullmatch(doi):
                flags.append("invalid_doi_syntax")
                doi = ""
            year = canonical.get("publication_year", "")
            if year and (not re.fullmatch(r"\d{4}", year) or not 1800 <= int(year) <= config["reference_year"]):
                flags.append("invalid_publication_year")
            source = {
                "source_file": path.relative_to(ROOT).as_posix(), "source_row": number,
                "physical_start_line": start, "physical_end_line": end,
                "original_fields": original, "repair": note,
            }
            if note:
                source["original_csv_record"] = original_text
            records.append({
                "source": source, "key": f"{source['source_file']}#{number:08d}",
                "metadata": dict(metadata), "canonical": canonical,
                "doi": doi, "title_key": normalize_title(canonical.get("title", "")),
                "flags": flags,
            })
        inputs.append({"file": path.relative_to(ROOT).as_posix(), "records": count, "sha256": hashlib.sha256(raw).hexdigest()})
    return sorted(records, key=lambda r: r["key"]), inputs


def author_keys(record):
    return {normalize_title(name) for name in record["canonical"].get("authors", "").split(";") if normalize_title(name)}


def title_corroborated(a, b):
    year_a = a["canonical"].get("publication_year", "")
    year_b = b["canonical"].get("publication_year", "")
    return (len(a["title_key"]) >= 20 and len(a["title_key"].split()) >= 4
            and re.fullmatch(r"\d{4}", year_a) is not None and year_a == year_b
            and "invalid_publication_year" not in a["flags"] and "invalid_publication_year" not in b["flags"]
            and bool(author_keys(a) & author_keys(b)))


def fuzzy_score(title_a, title_b):
    if title_a == title_b or min(len(title_a), len(title_b)) < 30:
        return None
    tokens_a, tokens_b = set(title_a.split()), set(title_b.split())
    if min(len(tokens_a), len(tokens_b)) < 5:
        return None
    if len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b)) < FUZZY_TOKEN_OVERLAP:
        return None
    matcher = SequenceMatcher(None, title_a, title_b, autojunk=False)
    if matcher.real_quick_ratio() < FUZZY_RATIO or matcher.quick_ratio() < FUZZY_RATIO:
        return None
    score = matcher.ratio()
    return score if score >= FUZZY_RATIO else None


def deduplicate(records):
    parents = list(range(len(records)))

    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    def join(a, b):
        parents[max(find(a), find(b))] = min(find(a), find(b))

    doi_groups, title_groups = defaultdict(list), defaultdict(list)
    confirmed, possible = [], []
    for i, record in enumerate(records):
        if record["doi"]:
            doi_groups[record["doi"]].append(i)
        if record["title_key"]:
            title_groups[record["title_key"]].append(i)
    for key, group in sorted(doi_groups.items()):
        for i in group[1:]:
            join(group[0], i)
            confirmed.append((group[0], i, "exact_doi", key))
    for title, group in sorted(title_groups.items()):
        # A title shared by different DOIs is ambiguous, including DOI-free bridges.
        roots = {find(i) for i in group}
        cluster_records = [r for i, r in enumerate(records) if find(i) in roots]
        dois = {r["doi"] for r in cluster_records if r["doi"]}
        years = {r["canonical"].get("publication_year", "") for r in cluster_records} - {""}
        for a, b in combinations(group, 2):
            if find(a) == find(b):
                continue
            if len(dois) > 1:
                possible.append((a, b, "exact_title_conflicting_dois", 1.0))
            elif len(years) > 1:
                possible.append((a, b, "exact_title_conflicting_years", 1.0))
            elif title_corroborated(records[a], records[b]):
                join(a, b)
                confirmed.append((a, b, "exact_title_author_year", title))
            else:
                possible.append((a, b, "exact_title_insufficient_corroboration", 1.0))
    # shortcut: all-pairs title comparison fits this ~400-record corpus; add blocking for tens of thousands.
    for a, b in combinations(range(len(records)), 2):
        if find(a) == find(b):
            continue
        score = fuzzy_score(records[a]["title_key"], records[b]["title_key"])
        if score is not None:
            possible.append((a, b, "fuzzy_title", score))
    groups = defaultdict(list)
    for i in range(len(records)):
        groups[find(i)].append(i)
    # Postcondition prevents title chains from introducing conflicting DOI identities.
    for group in groups.values():
        if len({records[i]["doi"] for i in group} - {""}) > 1:
            raise ValueError("Unsafe merge: multiple DOI identities in one paper")
    return list(groups.values()), confirmed, possible


def merge_group(group, records):
    members = [records[i] for i in group]
    variants = defaultdict(list)
    for record in members:
        for field, values in record["metadata"].items():
            for value in values:
                existing = next((v for v in variants[field] if v["value"] == value), None)
                if existing is None:
                    existing = {"value": value, "sources": []}
                    variants[field].append(existing)
                existing["sources"].append({"source_file": record["source"]["source_file"], "source_row": record["source"]["source_row"]})
    selected = {field: values[0]["value"] for field, values in variants.items()}
    conflicts = {field: {"selected": selected[field], "alternatives": values, "policy": "first_nonempty_in_source_order"}
                 for field, values in variants.items() if len(values) > 1}
    keywords, urls = [], []
    for field in KEYWORD_FIELDS:
        for variant in variants.get(field, []):
            for keyword in variant["value"].split(";"):
                keyword = keyword.strip()
                if keyword and keyword not in keywords:
                    keywords.append(keyword)
    for field in URL_FIELDS:
        for variant in variants.get(field, []):
            if variant["value"] not in urls:
                urls.append(variant["value"])
    doi = next((r["doi"] for r in members if r["doi"]), "")
    title = selected.get("title", "")
    # Identity is independent of iteration order and Python's randomized hash().
    identity = "doi:" + doi if doi else "metadata:" + packed([
        normalize_title(title), selected.get("publication_year", ""),
        normalize_title(selected.get("authors", "")), normalize_title(selected.get("publication_venue", "")),
    ])
    if not normalize_title(title) and not doi:
        identity = "source:" + min(r["key"] for r in members)
    output = {
        "paper_id": "paper_" + uuid.uuid5(uuid.NAMESPACE_URL, "mobility-literature/" + identity).hex,
        "title": title, "normalized_title": normalize_title(title),
        "abstract": selected.get("abstract", ""), "authors": selected.get("authors", ""),
        "publication_year": selected.get("publication_year", ""), "doi": doi,
        "keywords_json": packed(keywords), "publication_venue": selected.get("publication_venue", ""),
        "urls_json": packed(urls), "source_count": len(members),
        "source_records_json": packed([r["source"] for r in members]),
        "metadata_json": packed(selected), "metadata_variants_json": packed(variants),
        "metadata_conflicts_json": packed(conflicts),
        "quality_flags_json": packed(sorted({flag for r in members for flag in r["flags"]})),
    }
    return output


def source_reference(record):
    return {k: record["source"][k] for k in ("source_file", "source_row")}


def build_outputs(records):
    groups, confirmed, possible = deduplicate(records)
    merged = [merge_group(group, records) for group in groups]
    # Identical DOI-free metadata can remain separate under conservative rules.
    id_counts = defaultdict(list)
    for group, row in zip(groups, merged):
        id_counts[row["paper_id"]].append((group, row))
    for collisions in id_counts.values():
        if len(collisions) > 1:
            for group, row in collisions:
                row["paper_id"] = "paper_" + uuid.uuid5(uuid.NAMESPACE_URL, row["paper_id"] + records[min(group)]["key"]).hex
    index_to_row = {i: row for group, row in zip(groups, merged) for i in group}
    duplicates = []
    for a, b, method, match_key in confirmed:
        row = index_to_row[a]
        duplicates.append({
            "paper_id": row["paper_id"], "source_file_a": records[a]["source"]["source_file"],
            "source_row_a": records[a]["source"]["source_row"], "source_file_b": records[b]["source"]["source_file"],
            "source_row_b": records[b]["source"]["source_row"], "match_method": method, "match_key": match_key,
            "resolution": "merged; scalar fields first nonempty in source order; keywords/URLs union; all originals and variants retained",
            "metadata_conflicts_json": row["metadata_conflicts_json"],
        })
    review = defaultdict(lambda: {"reasons": set(), "evidence": [], "score": 0.0})
    for a, b, reason, score in possible:
        id_a, id_b = index_to_row[a]["paper_id"], index_to_row[b]["paper_id"]
        if id_a == id_b:
            continue
        pair = tuple(sorted((id_a, id_b)))
        item = review[pair]
        item["reasons"].add(reason)
        item["score"] = max(item["score"], score)
        item["evidence"].append({"source_a": source_reference(records[a]), "source_b": source_reference(records[b]), "reason": reason, "score": round(score, 6)})
    by_id = {row["paper_id"]: row for row in merged}
    possible_rows = []
    for (id_a, id_b), item in sorted(review.items()):
        a, b = by_id[id_a], by_id[id_b]
        possible_rows.append({
            "paper_id_a": id_a, "paper_id_b": id_b, "title_a": a["title"], "title_b": b["title"],
            "doi_a": a["doi"], "doi_b": b["doi"], "year_a": a["publication_year"], "year_b": b["publication_year"],
            "reasons_json": packed(sorted(item["reasons"])), "max_title_similarity": f"{item['score']:.6f}",
            "evidence_json": packed(item["evidence"]), "resolution": "pending_review; kept_separate",
        })
    if len(duplicates) != len(records) - len(merged):
        raise ValueError("Duplicate accounting failed")
    if len(by_id) != len(merged) or sum(row["source_count"] for row in merged) != len(records):
        raise ValueError("Paper ID uniqueness or source accounting failed")
    return sorted(merged, key=lambda r: r["paper_id"]), duplicates, possible_rows


def csv_text(rows, columns):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main():
    config = json.loads((ROOT / "config/dataset_inspection.json").read_text(encoding="utf-8"))
    paths = sorted((ROOT / config["input_directory"]).glob(config["file_pattern"]))
    if not paths:
        raise SystemExit("No source files match the inspection configuration")
    records, inputs = load_records(paths, config)
    merged, duplicates, possible = build_outputs(records)
    repairs = [r for r in records if r["source"]["repair"]]
    conflicts = sum(row["metadata_conflicts_json"] != "{}" for row in merged)
    report = [
        "# Dataset cleaning report", "",
        "Run `python3 scripts/prepare_dataset.py` (Python 3, standard library only). Inputs and missing-value settings come from `config/dataset_inspection.json`. Source CSVs are read only; no relevance classification is performed.", "",
        "## Counts", "",
        f"- Initial source records: **{len(records)}**.",
        f"- Confirmed duplicate copies merged: **{len(duplicates)}**, in **{sum(r['source_count'] > 1 for r in merged)}** groups.",
        f"- Possible duplicate pairs requiring review: **{len(possible)}** (kept separate).",
        f"- Resulting unique records under these rules: **{len(merged)}**.",
        f"- Recovered malformed records: **{len(repairs)}**; discarded records: **0**.",
        f"- Merged records with metadata variants/conflicts: **{conflicts}**.", "",
        "## Inputs", "", "| File | Records | SHA-256 |", "| --- | ---: | --- |",
    ]
    report += [f"| `{item['file']}` | {item['records']} | `{item['sha256']}` |" for item in inputs]
    report += ["", "## Cleaning and recovery", "",
               "Column names are converted to snake_case and equivalent fields mapped to title, authors, publication_year, doi, abstract, publication_venue and URL fields. Every input column survives in original_fields and normalized metadata variants, including optional fields and unmapped columns. Scalars have surrounding whitespace removed and Unicode NFC applied. Configured missing markers become blank only in derived metadata; original strings remain intact.", "",
               "DOIs lose the DOI URL or doi: prefix and are case-folded; only syntax-valid values are used as identity keys. Invalid raw DOI values remain in metadata, with a quality flag. Titles use Unicode NFKC, case-folding, punctuation removal and collapsed whitespace for matching; display titles preserve original wording. Years are retained as strings and invalid years flagged. Semicolon-separated keyword fields are combined without discarding the original fields; supplied URLs are unioned without fabricating links.", ""]
    report += [f"- `{r['source']['source_file']}#{r['source']['source_row']}`: {r['source']['repair']}." for r in repairs]
    report += ["", "Malformed rows are repaired only when illegal interior quotes are confined to Funding Information and strict reparsing yields exactly the header width. Other malformed rows stop the run rather than being skipped. Repaired records include original_csv_record as lossless recovery evidence.", "",
               "## Duplicate rules and resolution", "",
               "1. Same valid normalized DOI: automatic merge. Conflicting metadata is retained even when the DOI matches.",
               "2. Same normalized title: automatic merge only for titles of at least 20 characters and four words, equal valid populated publication years, and at least one shared full normalized author name (semicolon-separated). A title bucket and its existing DOI clusters must contain no conflicting populated DOI or year. Missing corroboration, differing years or differing DOIs require review. A DOI-free record cannot bridge two DOI identities.",
               f"3. Fuzzy titles: SequenceMatcher with autojunk disabled, ratio >= {FUZZY_RATIO:.2f}, at least 30 characters and five distinct words in each title, and shared words / smaller word-set size >= {FUZZY_TOKEN_OVERLAP:.2f}. These are review candidates only, including when DOIs or years conflict. All original title variants are checked. Different source-pair evidence is consolidated into one review row per final paper pair.", "",
               "Merge policy: first nonmissing scalar value in sorted source filename / numeric record order. Exact source values, their origins, all alternatives and conflicts remain in source_records_json, metadata_variants_json and metadata_conflicts_json. keywords_json and urls_json combine values; original keyword categories remain in metadata. Canonical DOI is the normalized valid identity value. duplicates.csv logs each successful merge edge (one row per redundant source copy), the matching rule and resulting paper ID; its edges describe a merge graph, not necessarily a single retained source row.", "",
               "## Output schema and identifiers", "",
               "merged_papers.csv contains paper_id, title, normalized_title, abstract, authors, publication_year, doi, keywords_json, publication_venue, urls_json, source_count, source_records_json, metadata_json, metadata_variants_json, metadata_conflicts_json and quality_flags_json. JSON columns are standard JSON strings inside quoted CSV fields. Source rows are 1-based data-record numbers excluding the header; physical line ranges are also preserved. metadata_json retains all normalized source fields; authoritative normalized DOI and combined keywords/URLs are the dedicated columns.", "",
               "Paper IDs use deterministic UUIDv5: normalized DOI when available; otherwise normalized title, year, authors and venue. Records without an identity title/DOI fall back to source location; unresolved identical identity tuples are disambiguated by source location. IDs and output bytes are stable for unchanged input and independent of the working directory. Correcting identity metadata, changing a DOI-free representative or moving/reordering fallback source records can change IDs; IDs are not a persistent registry across edits.", "",
               "possible_duplicates.csv is a review queue, not a merge instruction; the automated script does not consume manual decisions. Empty audit queues still contain column headers. Re-running overwrites only the four derived outputs. Source hashes and complete provenance make the run auditable. Fuzzy thresholds are conservative and may miss paraphrased titles. DOI resolution and semantic relevance are not checked.", ""]
    for path, item in zip(paths, inputs):
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Source changed during preparation: {path}")
    result_dir = ROOT / "results"
    result_dir.mkdir(exist_ok=True)
    outputs = {
        "merged_papers.csv": csv_text(merged, list(merged[0]) if merged else ["paper_id", "title", "source_records_json"]),
        "duplicates.csv": csv_text(duplicates, ["paper_id", "source_file_a", "source_row_a", "source_file_b", "source_row_b", "match_method", "match_key", "resolution", "metadata_conflicts_json"]),
        "possible_duplicates.csv": csv_text(possible, ["paper_id_a", "paper_id_b", "title_a", "title_b", "doi_a", "doi_b", "year_a", "year_b", "reasons_json", "max_title_similarity", "evidence_json", "resolution"]),
        "cleaning_report.md": "\n".join(report),
    }
    for name, content in outputs.items():
        (result_dir / name).write_text(content, encoding="utf-8", newline="")
    print(f"Initial records: {len(records)}; confirmed duplicate copies: {len(duplicates)}; possible duplicate pairs: {len(possible)}; unique records: {len(merged)}; repaired rows: {len(repairs)}")


if __name__ == "__main__":
    main()
