"""Focused checks for lossless recovery and conservative duplicate resolution.

Run: python3 -m unittest discover -s scripts -p 'test_prepare_dataset.py'
"""

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_dataset as prep


TITLE = "Privacy threats in connected vehicle communication systems"


def record(number, title=TITLE, doi="", year="2025", authors="A. Example"):
    values = {"title": title, "doi": doi, "publication_year": year, "authors": authors}
    return {
        "key": f"papers/example.csv#{number:08d}",
        "source": {"source_file": "papers/example.csv", "source_row": number,
                   "original_fields": dict(values), "repair": ""},
        "metadata": {k: [v] for k, v in values.items() if v}, "canonical": values,
        "doi": doi, "title_key": prep.normalize_title(title), "flags": [],
    }


class PreparationTests(unittest.TestCase):
    def test_doi_title_and_column_normalization(self):
        self.assertEqual(prep.normalize_doi("https://doi.org/10.1234/ABC"), "10.1234/abc")
        self.assertEqual(prep.normalize_title("  Privacy: IN Mobility! "), "privacy in mobility")
        self.assertEqual(prep.column_name("Publication Title"), "publication_venue")
        self.assertEqual(prep.column_name("Document Title"), "title")

    def test_recovery_preserves_literal_quotes_and_alignment(self):
        header = ["Document Title", "Funding Information", "PDF Link"]
        dialect = {"delimiter": ",", "quotechar": '"', "doublequote": True}
        original = '"Paper","Grant for "quoted project" (2025), continued","https://example.org/pdf"\n'
        row, note = prep.repair_funding_quotes(original, header, dialect)
        self.assertEqual(row, ["Paper", 'Grant for "quoted project" (2025), continued', "https://example.org/pdf"])
        self.assertIn("Escaped 2", note)
        with self.assertRaises(ValueError):
            prep.repair_funding_quotes(original, ["Document Title", "Abstract", "PDF Link"], dialect)

    def test_loader_preserves_unknown_columns_and_normalized_alias_conflicts(self):
        config = {"delimiter": ",", "quotechar": '"', "doublequote": True,
                  "encoding": "utf-8-sig", "missing_values": ["", "n/a"], "reference_year": 2026}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "export.csv"
            buffer = io.StringIO(newline="")
            writer = csv.writer(buffer)
            writer.writerow(["Document Title", "Title", "DOI", "Publication Year", "Unexpected Field", "Abstract"])
            writer.writerow(["  Title A  ", "Title B", "https://doi.org/10.1234/ABC", "2025", " raw value ", "n/a"])
            writer.writerow(["Invalid identifier", "", "not a DOI", "unknown", "", ""])
            path.write_text(buffer.getvalue(), encoding="utf-8", newline="")
            with patch.object(prep, "ROOT", root):
                records, inputs = prep.load_records([path], config)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["doi"], "10.1234/abc")
            self.assertEqual(records[0]["metadata"]["title"], ["Title A", "Title B"])
            merged = prep.merge_group([0], records)
            self.assertEqual(json.loads(merged["metadata_json"])["unexpected_field"], "raw value")
            self.assertIn("title", json.loads(merged["metadata_conflicts_json"]))
            source = json.loads(merged["source_records_json"])[0]
            self.assertEqual(source["original_fields"]["Document Title"], "  Title A  ")
            self.assertEqual(source["original_fields"]["Abstract"], "n/a")
            self.assertEqual(set(records[1]["flags"]), {"invalid_doi_syntax", "invalid_publication_year"})
            self.assertEqual(records[1]["doi"], "")
            self.assertEqual(inputs[0]["records"], 2)

    def test_same_doi_merges_and_keeps_all_conflicting_metadata(self):
        a, b = record(1, doi="10.1234/x"), record(2, title=TITLE + " revised", doi="10.1234/x", year="2024")
        a["metadata"]["abstract"] = ["Original abstract"]
        b["metadata"]["abstract"] = ["Different abstract"]
        a["metadata"]["author_keywords"] = ["Privacy;Vehicles"]
        b["metadata"]["ieee_terms"] = ["Vehicles;Security"]
        merged, duplicates, possible = prep.build_outputs([a, b])
        self.assertEqual((len(merged), len(duplicates), len(possible)), (1, 1, 0))
        self.assertEqual(duplicates[0]["match_method"], "exact_doi")
        self.assertEqual(merged[0]["abstract"], "Original abstract")
        self.assertEqual(json.loads(merged[0]["keywords_json"]), ["Privacy", "Vehicles", "Security"])
        self.assertEqual(len(json.loads(merged[0]["source_records_json"])), 2)
        self.assertEqual(len(json.loads(merged[0]["metadata_conflicts_json"])["abstract"]["alternatives"]), 2)

    def test_exact_title_needs_author_year_corroboration(self):
        merged, duplicates, possible = prep.build_outputs([record(1), record(2, doi="10.1234/x")])
        self.assertEqual((len(merged), len(duplicates), len(possible)), (1, 1, 0))
        self.assertEqual(duplicates[0]["match_method"], "exact_title_author_year")
        for second in [record(2, year=""), record(2, year="2024"), record(2, authors="B. Other")]:
            merged, duplicates, possible = prep.build_outputs([record(1), second])
            self.assertEqual((len(merged), len(duplicates), len(possible)), (2, 0, 1))

    def test_conflicting_dois_cannot_merge_through_missing_doi(self):
        records = [record(1, doi="10.1234/x"), record(2), record(3, doi="10.1234/y")]
        merged, duplicates, possible = prep.build_outputs(records)
        self.assertEqual((len(merged), len(duplicates), len(possible)), (3, 0, 3))
        self.assertTrue(all("exact_title_conflicting_dois" in row["reasons_json"] for row in possible))

    def test_fuzzy_matches_are_only_reviewed_and_include_source_evidence(self):
        records = [record(1, doi="10.1234/x"), record(2, title=TITLE[:-1], doi="10.1234/y")]
        merged, duplicates, possible = prep.build_outputs(records)
        self.assertEqual((len(merged), len(duplicates), len(possible)), (2, 0, 1))
        self.assertIn("fuzzy_title", possible[0]["reasons_json"])
        self.assertEqual(len(json.loads(possible[0]["evidence_json"])), 1)
        self.assertIsNone(prep.fuzzy_score("Privacy", "Privacys"))

    def test_unresolved_identical_identities_get_distinct_reproducible_ids(self):
        records = [record(1, year=""), record(2, year="")]
        first = prep.build_outputs(records)
        self.assertEqual(first, prep.build_outputs(records))
        self.assertEqual(len({r["paper_id"] for r in first[0]}), 2)
        self.assertEqual((len(first[1]), len(first[2])), (0, 1))

    def test_doi_identity_stays_stable_with_extra_source(self):
        a = prep.build_outputs([record(1, doi="10.1234/x")])[0][0]["paper_id"]
        b = prep.build_outputs([record(1, doi="10.1234/x"), record(2, doi="10.1234/x")])[0][0]["paper_id"]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
