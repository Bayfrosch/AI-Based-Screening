"""Check evidence boundaries and deterministic, lossless literature indexing."""
import csv
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import build_literature_overview as overview


class OverviewTests(unittest.TestCase):
    def test_performance_experiment_does_not_become_privacy_attack_evidence(self):
        row = {
            "paper_id": "p", "title": "Anonymous authentication for VANETs",
            "abstract": "We propose anonymous authentication. Our experiments measure runtime. Public transport is a possible future application.",
            "keywords_json": '[]', "thematic_categories": '["Connected vehicles and V2X"]',
            "publication_year": "2016", "research_role": "MITIGATION", "priority": "MEDIUM",
            "priority_reason": "Supports identity privacy.", "contribution_focus": "GENERAL_PRIVACY_MITIGATION",
        }
        result = overview.matrix_row(row, {})
        self.assertIn("Experiments/evaluation", result["research_methodology"])
        self.assertEqual(result["empirical_privacy_evidence_status"], "NOT_ESTABLISHED")
        self.assertEqual(result["threat_model_status"], "NOT_ESTABLISHED")
        self.assertNotIn("Re-identification", result["privacy_threat_categories"])
        self.assertNotIn("Public transportation", result["mobility_domain"])
        self.assertEqual(result["full_text_review_needed"], "true")

    def test_related_work_and_negated_proof_are_not_reported_as_own_method(self):
        evidence = overview.method_cues("Prior work conducted experiments. We propose a scheme without formal security proof.")
        self.assertNotIn("Formal security analysis/proof", evidence)
        self.assertNotIn("Experiments/evaluation (target not automatically privacy)", evidence)

    def test_full_export_preserves_ids_roles_priorities_and_repeats_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ("results/prioritized_papers.csv", "config/screening_criteria.md", "config/literature_overview_annotations.json"):
                target = root / relative
                target.parent.mkdir(exist_ok=True)
                shutil.copyfile(overview.ROOT / relative, target)
            source = root / "results/prioritized_papers.csv"
            original_bytes = source.read_bytes()
            with source.open(encoding="utf-8", newline="") as handle:
                original = {r["paper_id"]: r for r in csv.DictReader(handle)}
            with patch.object(overview, "ROOT", root), redirect_stdout(io.StringIO()):
                overview.build()
                outputs = [root / "results" / name for name in ("literature_matrix.csv", "literature_overview.md", "paper_outline.md")]
                first = [p.read_bytes() for p in outputs]
                overview.build()
                self.assertEqual(first, [p.read_bytes() for p in outputs])
                self.assertEqual(source.read_bytes(), original_bytes)
                with outputs[0].open(encoding="utf-8", newline="") as handle:
                    matrix = list(csv.DictReader(handle))
                self.assertEqual(len(matrix), len(original))
                self.assertEqual({r["paper_id"] for r in matrix}, set(original))
                for row in matrix:
                    for field in ("title", "research_role", "priority", "contribution_focus"):
                        self.assertEqual(row[field], original[row["paper_id"]][field])
                    self.assertEqual(row["year"], original[row["paper_id"]]["publication_year"])
                    self.assertEqual(row["full_text_review_needed"], "true")
                    for sentence in json.loads(row["methodology_evidence_json"]).values():
                        self.assertIn(sentence, original[row["paper_id"]]["abstract"])
                # Reject stale source/criteria and unsupported evidence before replacing outputs.
                criteria = root / "config/screening_criteria.md"
                criteria.write_text(criteria.read_text() + "Changed protocol")
                with self.assertRaisesRegex(ValueError, "Criteria changed"):
                    overview.build()
                self.assertEqual(first, [p.read_bytes() for p in outputs])
                shutil.copyfile(Path(__file__).resolve().parents[1] / "config/screening_criteria.md", criteria)
                config_path = root / "config/literature_overview_annotations.json"
                config = json.loads(config_path.read_text())
                next(iter(config["papers"].values()))["evidence"] = ["Invented metadata assertion"]
                config_path.write_text(json.dumps(config))
                with self.assertRaisesRegex(ValueError, "evidence not present"):
                    overview.build()
                self.assertEqual(first, [p.read_bytes() for p in outputs])


if __name__ == "__main__":
    unittest.main()
