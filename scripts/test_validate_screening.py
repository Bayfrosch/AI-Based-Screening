"""Audit regression checks, including synthetic reference-label metrics."""
import csv
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import validate_screening as audit


def row(number, decision="INCLUDE", **changes):
    result = {"paper_id": f"p{number}", "title": "Anonymous cross-domain group key agreement for vehicle networks",
              "abstract": "Vehicles exchange location information. An anonymous authentication mechanism protects personal data against tracking and disclosure over public channels while allowing authorized investigation of malicious participants.",
              "keywords_json": '["privacy"]', "publication_year": "2025", "decision": decision,
              "research_role": "OUT_OF_SCOPE" if decision == "EXCLUDE" else "MITIGATION",
              "matched_criteria": '["E1"]' if decision == "EXCLUDE" else '["I1"]',
              "reason": "Analyzes location disclosure during vehicular authentication." if decision != "EXCLUDE" else "Analyzes message integrity without substantive privacy findings.",
              "needs_full_text_review": "false" if decision == "EXCLUDE" else "true",
              "screening_criteria_sha256": "test-hash"}
    result.update(changes)
    return result


def manual_file(path, entries):
    audit.write_csv(path, entries, ["paper_id", "my_classification", "my_research_role"])


class ValidationTests(unittest.TestCase):
    def test_sample_is_stratified_unique_and_order_independent(self):
        rows = [row(f"{label}{n}", label) for label in audit.DECISION_LABELS for n in range(15)]
        sample = audit.sample_rows(rows, [])
        self.assertEqual(len(sample), 30)
        self.assertEqual(len({r["paper_id"] for r in sample}), 30)
        self.assertEqual(sample, audit.sample_rows(list(reversed(rows)), []))
        self.assertTrue(all(sum(r["automated_decision"] == label for r in sample) == 10 for label in audit.DECISION_LABELS))
        self.assertTrue(all(not r[k] for r in sample for k in ("my_classification", "my_research_role", "my_comments")))

    def test_missing_abstract_and_terminology_exclusion_are_flagged(self):
        rows = [row(1, "EXCLUDE", abstract="", reason="No explicit threat modeling is present.")]
        flags, _, _ = audit.audit(rows, "test-hash", [])
        self.assertTrue({"MISSING_SHORT_OR_TRUNCATED_ABSTRACT", "THREAT_MODEL_TERM_REQUIRED_IN_REASON"} <= {f["flag_code"] for f in flags})

    def test_false_negative_framework_and_similarity_checks(self):
        rows = [row(1), row(2, "EXCLUDE"), row(3, "MAYBE", research_role="FRAMEWORK_FOCUSED")]
        flags, pairs, errors = audit.audit(rows, "test-hash", [])
        self.assertEqual(errors, [])
        self.assertTrue(pairs)
        self.assertIn("POSSIBLE_FALSE_NEGATIVE_BODY", {f["flag_code"] for f in flags})
        self.assertIn("FRAMEWORK_WITH_CONCRETE_PRIVACY_CUE", {f["flag_code"] for f in flags})

    def test_invalid_decision_is_reported(self):
        flags, _, errors = audit.audit([row(1, decision="UNKNOWN")], "test-hash", [])
        self.assertTrue(errors)
        self.assertIn("INVALID_CLASSIFICATION", {f["flag_code"] for f in flags})

    def test_no_reference_labels_means_no_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manual.csv"
            manual_file(path, [{"paper_id": "p1", "my_classification": "", "my_research_role": ""}])
            metrics = audit.compare_manual([row(1)], [path])
            self.assertEqual(metrics["labeled_decisions"], 0)
            self.assertNotIn("agreement", metrics)
            self.assertNotIn("include_recall", metrics)
            self.assertNotIn("retention_recall", metrics)

    def test_synthetic_reference_agreement_and_recall_denominators(self):
        rows = [row(1), row(2, "EXCLUDE"), row(3, "MAYBE"), row(4, "MAYBE")]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manual.csv"
            manual_file(path, [{"paper_id": f"p{i}", "my_classification": label, "my_research_role": ""} for i, label in enumerate(["INCLUDE", "INCLUDE", "EXCLUDE", "INCLUDE"], 1)])
            metrics = audit.compare_manual(rows, [path])
            self.assertEqual(metrics["labeled_decisions"], 4)
            self.assertEqual(metrics["agreement"], 0.25)
            self.assertAlmostEqual(metrics["kappa"], 0)
            self.assertAlmostEqual(metrics["include_recall"], 1 / 3)
            self.assertAlmostEqual(metrics["retention_recall"], 2 / 3)

    def test_reference_without_positives_cannot_support_recall(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manual.csv"
            manual_file(path, [{"paper_id": "p1", "my_classification": "EXCLUDE", "my_research_role": "OUT_OF_SCOPE"}])
            metrics = audit.compare_manual([row(1)], [path])
            self.assertIn("agreement", metrics)
            self.assertNotIn("include_recall", metrics)

    def test_conflicting_and_contradictory_reference_labels_are_not_scored(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a.csv", Path(directory) / "b.csv"
            manual_file(a, [{"paper_id": "p1", "my_classification": "INCLUDE", "my_research_role": ""},
                            {"paper_id": "p2", "my_classification": "INCLUDE", "my_research_role": "OUT_OF_SCOPE"}])
            manual_file(b, [{"paper_id": "p1", "my_classification": "EXCLUDE", "my_research_role": ""}])
            metrics = audit.compare_manual([row(1), row(2)], [a, b])
            self.assertEqual(metrics["labeled_decisions"], 0)
            self.assertEqual(len(metrics["problems"]), 2)

    def test_rerun_preserves_manual_file_and_source_and_detects_missing_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir()
            (root / "results").mkdir()
            criteria = b"Protocol version: 1.0.\n"
            (root / "config/screening_criteria.md").write_bytes(criteria)
            rows = [row(1, screening_criteria_sha256=hashlib.sha256(criteria).hexdigest()), row(2, "MAYBE", screening_criteria_sha256=hashlib.sha256(criteria).hexdigest())]
            source = root / "results/semantic_screening.csv"
            audit.write_csv(source, rows, list(rows[0]))
            audit.write_csv(root / "results/merged_papers.csv", rows + [row(3)], list(rows[0]))
            original = source.read_bytes()
            with redirect_stdout(io.StringIO()):
                result = audit.run(root)
                self.assertTrue(any("Missing semantic record: p3" in e for e in result["errors"]))
                path = root / "results/manual_validation_sample.csv"
                sample = audit.read_csv(path)
                sample[0]["my_comments"] = "Keep this comment exactly."
                audit.write_csv(path, sample, list(sample[0]))
                manual_bytes = path.read_bytes()
                audit.run(root)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(path.read_bytes(), manual_bytes)


if __name__ == "__main__":
    unittest.main()
