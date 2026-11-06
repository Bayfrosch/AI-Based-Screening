"""Checks for priority boundaries, strict checkpoints and lossless exports."""
import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import prioritize_papers as ranking


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class PrioritizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubric = json.loads((ranking.ROOT / "config/prioritization_rubric.json").read_text())

    def test_priority_routes_and_no_quota(self):
        self.assertEqual(ranking.priority([2, 1, 1, 1, 2, 1]), "HIGH")
        self.assertEqual(ranking.priority([1, 2, 2, 2, 2, 1]), "HIGH")
        self.assertEqual(ranking.priority([1, 2, 1, 2, 2, 1]), "MEDIUM")
        self.assertEqual(ranking.priority([0, 0, 1, 2, 0, 1]), "LOW")
        self.assertEqual(sum(ranking.priority([2, 2, 2, 2, 2, 2]) == "HIGH" for _ in range(100)), 100)

    def test_framework_focus_does_not_change_score_priority(self):
        for focus in ("A", "D", "F"):
            item = {"paper_id": "p1", "scores": [2, 2, 1, 2, 2, 1], "theme_codes": ["V", "M"],
                    "contribution_focus": focus, "priority_reason": "Explains personal-data exposure across vehicle stakeholders."}
            ranking.validate(item, self.rubric)
            self.assertEqual(ranking.priority(item["scores"]), "HIGH")

    def test_bad_scores_themes_and_reasons_are_rejected(self):
        item = {"paper_id": "p1", "scores": [1] * 6, "theme_codes": ["V"],
                "contribution_focus": "D", "priority_reason": "Explains identity protection."}
        for changes in ({"scores": [True] * 6}, {"scores": [3] * 6}, {"scores": [1] * 5},
                        {"theme_codes": ["V", "V"]}, {"theme_codes": ["\u041e"]},
                        {"priority_reason": "word " * 26}, {"contribution_focus": "UNKNOWN"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                ranking.validate({**item, **changes}, self.rubric)

    def test_resumption_preservation_partitioning_and_repeated_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "results").mkdir()
            (root / "config").mkdir()
            (root / "config/screening_criteria.md").write_text("Protocol version: 1.0.\n")
            (root / "config/prioritization_rubric.json").write_text(json.dumps(self.rubric))
            rows = [{"paper_id": f"p{i}", "title": "Privacy study", "abstract": "Abstract.", "keywords_json": '["privacy"]',
                     "publication_year": "2015" if i == 0 else "2026", "decision": "INCLUDE",
                     "research_role": "MITIGATION", "extra_metadata": 'Preserved, "exactly"\nwith newlines.'} for i in range(3)]
            maybe = [{**rows[0], "paper_id": "q1", "decision": "MAYBE"}]
            source = root / "results/included.csv"
            unresolved = root / "results/maybe.csv"
            write_rows(source, rows)
            write_rows(unresolved, maybe)
            source_bytes, maybe_bytes = source.read_bytes(), unresolved.read_bytes()
            with patch.object(ranking, "ROOT", root), patch.object(ranking, "BATCH_SIZE", 2), redirect_stdout(io.StringIO()):
                included, queue, rubric, done, hashes = ranking.load()
                invalid = [[1, [1] * 6, "\u041e", "D", "Invalid category."], [2, [1] * 6, "V", "D", "Valid category."]]
                with patch("sys.stdin", io.StringIO(json.dumps(invalid))), self.assertRaises(ValueError):
                    ranking.save(included, done, rubric)
                self.assertEqual(list((root / "results/prioritization_batches").glob("batch_*.json")), [])
                initial = [[1, [2, 2, 2, 2, 2, 2], "VM", "A", "Explains privacy threats."],
                           [2, [1, 1, 1, 1, 1, 1], "VD", "D", "Provides supporting protection concepts."]]
                with patch("sys.stdin", io.StringIO(json.dumps(initial))):
                    ranking.save(included, done, rubric)
                included, queue, rubric, done, hashes = ranking.load()
                self.assertEqual([r["paper_id"] for r in ranking.pending(included, done)], ["p2"])
                with patch("sys.stdin", io.StringIO(json.dumps([[1, [0, 0, 0, 1, 0, 0], "V", "G", "Provides supplementary context."]]))):
                    ranking.save(included, done, rubric)
                included, queue, rubric, done, hashes = ranking.load()
                ranking.export(included, queue, rubric, done, hashes)
                paths = [root / "results" / name for name in ["prioritized_papers.csv", "high_priority.csv", "medium_priority.csv", "low_priority.csv", "prioritization_report.md", "maybe_for_further_review.csv"]]
                before = {p: p.read_bytes() for p in paths}
                ranking.export(included, queue, rubric, done, hashes)
                self.assertEqual(before, {p: p.read_bytes() for p in paths})
                with paths[0].open(encoding="utf8", newline="") as handle:
                    saved = list(csv.DictReader(handle))
                self.assertEqual([r["priority"] for r in saved], ["HIGH", "MEDIUM", "LOW"])
                self.assertEqual(saved[0]["publication_year"], "2015")
                self.assertEqual([{k: r[k] for k in rows[0]} for r in saved], rows)
                for path in paths[1:4]:
                    with path.open(encoding="utf8", newline="") as handle:
                        self.assertEqual(len(list(csv.DictReader(handle))), 1)
                self.assertEqual(paths[-1].read_bytes(), maybe_bytes)
                self.assertEqual(source.read_bytes(), source_bytes)
                self.assertEqual(unresolved.read_bytes(), maybe_bytes)
                self.assertEqual(ranking.pending(included, done), [])
                with self.assertRaises(ValueError):
                    ranking.save(included, done, rubric)
                (root / "config/screening_criteria.md").write_text("Changed protocol\n")
                with self.assertRaises(ValueError):
                    ranking.load()


if __name__ == "__main__":
    unittest.main()
