#!/usr/bin/env python3
"""Inspect source CSVs without changing them; Python standard library only."""

import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/dataset_inspection.json"
DOI = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)


def normalize_doi(value):
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).casefold()


def normalize_title(value):
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join("".join(c if c.isalnum() else " " for c in value).split())


def inferred_type(values):
    if not values:
        return "empty"
    if all(re.fullmatch(r"[+-]?\d+", v) for v in values):
        return "integer"
    try:
        for value in values:
            float(value)
        return "number"
    except ValueError:
        return "text"


def inspect(path, config):
    raw = path.read_bytes()
    decoded = raw.decode(config["encoding"], errors="strict")
    physical_lines = decoded.splitlines(keepends=True)
    dialect = {k: config[k] for k in ("delimiter", "quotechar", "doublequote")}
    reader = csv.reader(io.StringIO(decoded, newline=""), **dialect)
    header = next(reader)
    assert len(set(header)) == len(header), f"Duplicate headers: {path}"
    records, malformed = [], []
    last_line = reader.line_num
    total = 0
    for number, row in enumerate(reader, 1):
        total += 1
        end_line = reader.line_num
        record_text = "".join(physical_lines[last_line:end_line])
        problem = None
        try:
            strict_rows = list(csv.reader(io.StringIO(record_text, newline=""), strict=True, **dialect))
            if len(strict_rows) != 1 or len(row) != len(header):
                problem = f"{len(row)} fields; expected {len(header)}"
        except csv.Error as error:
            problem = f"strict CSV error: {error}; permissive parser yields {len(row)} fields (expected {len(header)})"
        if problem:
            malformed.append((number, last_line + 1, end_line, problem))
        else:
            records.append({"location": f"{path.name}#{number}", "values": dict(zip(header, row)), "raw": tuple(row)})
        last_line = end_line
    assert total == len(records) + len(malformed)
    return {
        "path": path, "raw": raw, "sha256": hashlib.sha256(raw).hexdigest(),
        "header": header, "records": records, "malformed": malformed, "total": total,
        "bom": raw.startswith(b"\xef\xbb\xbf"), "crlf": raw.count(b"\r\n"),
        "lf": raw.count(b"\n") - raw.count(b"\r\n"),
        "replacement": decoded.count("\ufffd"),
    }


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    paths = sorted((ROOT / config["input_directory"]).glob(config["file_pattern"]))
    if not paths:
        raise SystemExit("No input CSV files match the inspection configuration")
    fields = config["fields"]
    missing_values = set(config["missing_values"])

    def missing(value):
        return value.strip().casefold() in missing_values

    datasets = [inspect(path, config) for path in paths]
    all_records = [r for d in datasets for r in d["records"]]
    total = sum(d["total"] for d in datasets)
    bad_count = sum(len(d["malformed"]) for d in datasets)
    lines = [
        "# Dataset inspection report", "",
        "Scope: structural inspection for the mobility privacy literature review described in `notes.md`. No semantic screening or source changes.", "",
        "## Reproduce", "",
        "Run `python3 scripts/inspect_datasets.py` from the project root (Python 3, standard library only). Settings and field mapping: `config/dataset_inspection.json`.", "",
        "The requested `data/` directory is absent; the four source exports are in `papers/`. The configuration uses that existing location.", "",
        f"**{total} source records across {len(datasets)} files; {len(all_records)} structurally valid; {bad_count} malformed.** Record numbers below are 1-based, excluding the header.", "",
        "Malformed records are excluded from field statistics and duplicate checks to prevent shifted columns from corrupting results. Their fields remain unassessed; all denominators below count structurally valid records only.", "",
        "## Files and CSV structure", "",
        "| File | Source records | Valid | Malformed | Columns | Bytes |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for d in datasets:
        lines.append(f"| `{d['path'].name}` | {d['total']} | {len(d['records'])} | {len(d['malformed'])} | {len(d['header'])} | {len(d['raw'])} |")
    same_headers = all(d["header"] == datasets[0]["header"] for d in datasets)
    lines += ["", f"Headers and order identical: **{'yes' if same_headers else 'no'}**. All inputs decode strictly as UTF-8; BOM presence and newline counts are recorded below. Comma delimiter, double-quote quoting, doubled embedded quotes; no automatic dialect guessing.", "",
              "| File | UTF-8 BOM | LF / CRLF | Replacement characters | SHA-256 |",
              "| --- | --- | ---: | ---: | --- |"]
    for d in datasets:
        lines.append(f"| `{d['path'].name}` | {'yes' if d['bom'] else 'no'} | {d['lf']} / {d['crlf']} | {d['replacement']} | `{d['sha256']}` |")
    lines += ["", "### Structural problems", ""]
    for d in datasets:
        for number, start, end, problem in d["malformed"]:
            lines.append(f"- `{d['path'].name}#{number}` (physical lines {start}–{end}): {problem}. Manual inspection locates unescaped embedded quotes in Funding Information; a comma then splits that field and shifts subsequent columns. Re-export or explicitly repair a derived copy before using this record.")
    lines += ["", "Python's `csv.Sniffer` inferred `doublequote=False` on these exports, which creates spurious overflow fields on otherwise valid rows. The configured standard doubled-quote parser avoids that inference error; strict parsing still flags the genuine malformed row.", "",
              "## Required metadata availability", "",
              "Counts are populated / structurally valid records. Missing values include blanks and configured placeholder strings. Keyword availability means at least one of Author Keywords, IEEE Terms, or Mesh_Terms is populated.", "",
              "| File | Titles | Abstracts | Authors | Years | DOIs | Any keywords | Author keywords |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for d in datasets:
        rows = [r["values"] for r in d["records"]]
        n = len(rows)
        counts = [sum(not missing(r.get(fields[k], "")) for r in rows) for k in ("title", "abstract", "authors", "year", "doi")]
        counts += [sum(any(not missing(r.get(k, "")) for k in fields["keywords"]) for r in rows), sum(not missing(r.get("Author Keywords", "")) for r in rows)]
        lines.append(f"| `{d['path'].name}` | " + " | ".join(f"{c}/{n}" for c in counts) + " |")
    lines += ["", "## Columns, inferred types and missing fields", "",
              "CSV has no declared types: values are loaded as text. Cells below show inferred type and missing count, without converting sources. Numeric identifiers and page numbers should remain text in later imports. All-null columns are marked empty. Files A–D follow the order in the file table; valid denominators are 82, 100, 100 and 99.", "",
              "| Column | A: type; missing | B: type; missing | C: type; missing | D: type; missing |",
              "| --- | --- | --- | --- | --- |"]
    columns = list(dict.fromkeys(column for d in datasets for column in d["header"]))
    for column in columns:
        cells = []
        for d in datasets:
            if column not in d["header"]:
                cells.append("absent")
                continue
            values = [r["values"][column].strip() for r in d["records"] if not missing(r["values"][column])]
            cells.append(f"{inferred_type(values)}; {len(d['records']) - len(values)}")
        lines.append(f"| {column} | " + " | ".join(cells) + " |")
    lines += ["", "## Incomplete or suspicious metadata", ""]
    for d in datasets:
        rows = [r["values"] for r in d["records"]]
        years = Counter(r[fields["year"]].strip() for r in rows if not missing(r[fields["year"]]))
        invalid_years = sum(not re.fullmatch(r"\d{4}", y) or not 1800 <= int(y) <= config["reference_year"] for y in years for _ in range(years[y]))
        invalid_dois = sum(not DOI.fullmatch(normalize_doi(r[fields["doi"]])) for r in rows if not missing(r[fields["doi"]]))
        short_abstracts = sum(0 < len(r[fields["abstract"]].strip()) < 100 for r in rows)
        ellipses = sum(r[fields["abstract"]].rstrip().endswith(("...", "…")) for r in rows)
        short_titles = sum(0 < len(r[fields["title"]].strip()) < 10 for r in rows)
        lines.append(f"- `{d['path'].name}`: year distribution " + ", ".join(f"{y}: {n}" for y, n in sorted(years.items())) + f"; invalid years {invalid_years}; populated DOIs failing syntax check {invalid_dois}; abstracts under 100 characters {short_abstracts}; abstracts ending in ellipsis {ellipses}; titles under 10 characters {short_titles}.")
    lines += ["", "These are mechanical flags, not evidence of irrelevance or confirmed truncation. DOI syntax checks do not verify resolution; author and abstract completeness cannot be established from nonempty strings alone. Optional volume, issue, ISBN, funding and date fields may be legitimately absent.", "",
              "## Potential duplicates", "",
              "Checks: exact parsed rows; normalized DOI (case and DOI URL/prefix); normalized title (Unicode NFKC, case, punctuation and whitespace). Blank keys are ignored. No fuzzy or semantic matching; candidates are not automatically merged.", "",
              "| Check | Groups | Records involved | Excess records within groups | Within-file pairs | Cross-file pairs |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    candidate_pairs = set()
    group_details = defaultdict(list)
    for label, key in (
        ("Exact row", lambda r: r["raw"]),
        ("DOI", lambda r: normalize_doi(r["values"][fields["doi"]]) if not missing(r["values"][fields["doi"]]) else ""),
        ("Title", lambda r: normalize_title(r["values"][fields["title"]]) if not missing(r["values"][fields["title"]]) else ""),
    ):
        groups = defaultdict(list)
        for index, record in enumerate(all_records):
            value = key(record)
            if value:
                groups[value].append(index)
        groups = [g for g in groups.values() if len(g) > 1]
        pairs = {pair for group in groups for pair in combinations(group, 2)}
        candidate_pairs.update(pairs)
        within = sum(all_records[a]["location"].split("#")[0] == all_records[b]["location"].split("#")[0] for a, b in pairs)
        lines.append(f"| {label} | {len(groups)} | {sum(map(len, groups))} | {sum(len(g)-1 for g in groups)} | {within} | {len(pairs)-within} |")
        for group in groups:
            group_details[tuple(group)].append(label)
    parents = list(range(len(all_records)))

    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    for a, b in candidate_pairs:
        parents[find(a)] = find(b)
    components = Counter(find(i) for i in range(len(all_records)))
    lines += ["", f"Combined candidate components: {sum(n > 1 for n in components.values())}; {sum(n for n in components.values() if n > 1)} records involved; {len(all_records) - len(components)} potential redundant copies. Counts from the individual checks overlap and must not be added. These are candidate counts, not a verified unique-paper total.", ""]
    lines += [f"- {', '.join(labels)}: " + "; ".join(f"`{all_records[i]['location']}`" for i in group) for group, labels in group_details.items()] or ["No candidates among structurally valid records."]
    lines += ["", "## Preparation for screening", "",
              "- Preserve `papers/` as immutable source exports; hashes above identify the inspected versions.",
              "- Resolve the flagged CSV row in a derived copy or by re-export; rerun inspection before normalization and screening.",
              "- Retain source filename and record number as provenance; review duplicate candidates before merging metadata.",
              "- Confirm search provenance: `notes.md` documents an 82-result search and a 1,469-result search, but does not map the three 100-record exports to query, sorting or export ranges. The available files do not establish exhaustive retrieval of those 1,469 results.",
              "- No semantic eligibility decisions, relevance labels, deduplicated dataset or screening rules have been created.", ""]
    for d in datasets:
        assert hashlib.sha256(d["path"].read_bytes()).hexdigest() == d["sha256"], "Source changed during inspection"
    output = ROOT / "results/dataset_report.md"
    output.parent.mkdir(exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Inspected {len(datasets)} files: {total} records, {bad_count} malformed. Report: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    assert normalize_doi("https://doi.org/10.1234/ABC") == "10.1234/abc"
    assert normalize_title("  Privacy: In Mobility! ") == "privacy in mobility"
    assert inferred_type(["2020", "2026"]) == "integer"
    # A strict parser must reject the same class of unescaped-quote corruption found in the export.
    try:
        list(csv.reader(io.StringIO('"a","funding "quote", more","b"\n'), strict=True))
    except csv.Error:
        pass
    else:
        raise AssertionError("Malformed quote self-check failed")
    main()
