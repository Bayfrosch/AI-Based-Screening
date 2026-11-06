"""Regression tests for conservative exclusions and complete metadata retention."""

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import preliminary_screening as screen


LONG_UNRELATED = ("We investigate the mathematical properties of a class of algebraic structures. "
                  "The results establish several bounds and provide proofs for the propositions under consideration.")
FOCUSED_ABSTRACT = ("This paper focuses exclusively on fuel consumption. "
                    "Privacy is outside the scope of this work. "
                    "The experiments compare engine settings using a mechanical test bench and report the measured efficiency for each operating condition.")


def paper(**changes):
    row = {"paper_id": "p1", "title": "An investigation of algebraic structures", "abstract": LONG_UNRELATED,
           "keywords_json": "[]", "metadata_variants_json": "{}", "metadata_conflicts_json": "{}",
           "quality_flags_json": "[]", "source_records_json": '[{"source_file":"example.csv","source_row":1}]'}
    row.update(changes)
    return row


def result(**changes):
    return screen.classify(paper(**changes), "test-hash")


class ScreeningTests(unittest.TestCase):
    def test_no_matches_is_uncertain(self):
        assessed = result()
        self.assertEqual(assessed["preliminary_category"], "UNCERTAIN")
        self.assertEqual(assessed["preliminary_rule_id"], "U3_NO_KEYWORD_MATCH")
        self.assertEqual(json.loads(assessed["exclusion_evidence_json"]), [])

    def test_missing_short_and_truncated_abstracts_are_never_excluded(self):
        for abstract in ("", "An incomplete summary.", FOCUSED_ABSTRACT + "..."):
            assessed = result(title="Fuel consumption", abstract=abstract)
            self.assertEqual(assessed["preliminary_category"], "UNCERTAIN")
            self.assertTrue(json.loads(assessed["preliminary_flags_json"]))

    def test_synonyms_without_explicit_privacy_mobility_or_threat_model(self):
        for title in ("Reidentification of GPS trajectories by passive observers",
                      "Re-identification of GPS trajectories by passive observers",
                      "Linkability and inference attacks against V2X pseudonyms"):
            assessed = result(title=title)
            self.assertEqual(assessed["preliminary_category"], "POTENTIALLY_RELEVANT")

    def test_phrase_hyphens_boundaries_and_keywords(self):
        assessed = result(title="Architecture of connected–vehicle systems", keywords_json='["location privacy"]')
        self.assertEqual(assessed["preliminary_category"], "POTENTIALLY_RELEVANT")
        groups = {m["group"] for m in screen.find_matches([("title", "business affairs")])}
        self.assertNotIn("mobility_systems", groups)

    def test_generic_security_does_not_imply_privacy_or_exclusion(self):
        assessed = result(title="Vehicular denial of service attack analysis")
        self.assertEqual(assessed["preliminary_category"], "UNCERTAIN")

    def test_foundational_and_framework_support_is_retained(self):
        for title in ("A framework for privacy risk analysis", "Membership inference attacks against neural networks"):
            self.assertEqual(result(title=title)["preliminary_category"], "POTENTIALLY_RELEVANT")

    def test_explicit_technical_scope_requires_affirmative_evidence(self):
        row = paper(title="Fuel consumption under different engine settings", abstract=FOCUSED_ABSTRACT)
        assessed = screen.classify(row, "test-hash")
        self.assertEqual(assessed["preliminary_category"], "CLEARLY_IRRELEVANT")
        self.assertEqual(assessed["preliminary_rule_id"], "X1_EXPLICIT_NONPRIVACY_SCOPE")
        for proof in json.loads(assessed["exclusion_evidence_json"]):
            self.assertEqual(row[proof["field"]][proof["start"]:proof["end"]], proof["match"])
        for abstract in (FOCUSED_ABSTRACT.replace("Privacy is outside the scope of this work. ", ""),
                         FOCUSED_ABSTRACT.replace("exclusively ", ""),
                         FOCUSED_ABSTRACT.replace("Privacy is", "It is not true that privacy is")):
            self.assertNotEqual(result(title=row["title"], abstract=abstract)["preliminary_category"], "CLEARLY_IRRELEVANT")

    def test_relevant_terms_and_variants_veto_exclusion(self):
        for changes in (
            {"keywords_json": '["anonymity"]'},
            {"keywords_json": '["GPS"]'},
            {"keywords_json": '["authentication"]'},
            {"metadata_variants_json": json.dumps({"abstract": [{"value": "A study of trajectory linking and reidentification.", "sources": []}]})},
            {"metadata_conflicts_json": '{"abstract":{"alternatives":[]}}'},
            {"quality_flags_json": '["invalid_doi_syntax"]'},
        ):
            row = paper(title="Fuel consumption", abstract=FOCUSED_ABSTRACT, **changes)
            self.assertNotEqual(screen.classify(row, "test-hash")["preliminary_category"], "CLEARLY_IRRELEVANT")

    def test_artifact_needs_explicit_no_research_abstract(self):
        abstract = ("This document contains the table of contents for the current issue. "
                    "It contains no original research and serves solely as a list of article entries and page numbers.")
        assessed = result(title="Table of Contents", abstract=abstract)
        self.assertEqual(assessed["preliminary_rule_id"], "X2_PUBLICATION_ARTIFACT")
        self.assertNotEqual(result(title="Table of Contents", abstract="")["preliminary_category"], "CLEARLY_IRRELEVANT")
        self.assertNotEqual(result(title="Table of Contents", abstract=abstract, keywords_json='["privacy"]')["preliminary_category"], "CLEARLY_IRRELEVANT")

    def test_pipeline_preserves_all_fields_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "results").mkdir()
            (root / "config").mkdir()
            criteria = root / "config/screening_criteria.md"
            criteria.write_text("Protocol version: 1.0.\n", encoding="utf-8")
            rows = [paper(), paper(paper_id="p2", title="Fuel consumption", abstract=FOCUSED_ABSTRACT)]
            for row in rows:
                row["custom_metadata"] = 'Original, text with "quotes"\nand newlines.'
            source = root / "results/merged_papers.csv"
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            original = source.read_bytes()
            with redirect_stdout(io.StringIO()):
                screen.run(root)
                first = {p.name: p.read_bytes() for p in (root / "results").glob("preliminary_*")}
                screen.run(root)
            self.assertEqual(first, {p.name: p.read_bytes() for p in (root / "results").glob("preliminary_*")})
            self.assertEqual(original, source.read_bytes())
            with (root / "results/preliminary_screening.csv").open(encoding="utf-8", newline="") as handle:
                output = list(csv.DictReader(handle, strict=True))
            self.assertEqual([{k: r[k] for k in rows[0]} for r in output], rows)
            self.assertEqual([r["preliminary_category"] for r in output], ["UNCERTAIN", "CLEARLY_IRRELEVANT"])


if __name__ == "__main__":
    unittest.main()
