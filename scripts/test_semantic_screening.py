"""Validate resumability, decision consistency, and lossless semantic exports."""
import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import semantic_screening as semantic


def decision(paper_id="p1", **changes):
    item = {"paper_id": paper_id, "decision": "INCLUDE", "research_role": "MITIGATION",
            "matched_criteria": ["I1"], "reason": "Analyzes location disclosure during vehicle authentication.",
            "needs_full_text_review": True}
    item.update(changes)
    return item


class SemanticTests(unittest.TestCase):
    def test_schema_and_consistency(self):
        semantic.validate(decision())
        semantic.validate(decision(decision="MAYBE", research_role="BACKGROUND", matched_criteria=["I2"]))
        semantic.validate(decision(decision="EXCLUDE", research_role="OUT_OF_SCOPE", matched_criteria=["E1"], needs_full_text_review=False))
        for changes in [
            {"decision": "UNKNOWN"}, {"reason": "word " * 26}, {"reason": ""},
            {"needs_full_text_review": "true"}, {"matched_criteria": ["E1"]},
            {"research_role": "OUT_OF_SCOPE"}, {"matched_criteria": ["I1", "I1"]},
            {"decision": "EXCLUDE", "research_role": "CORE", "matched_criteria": ["E1"]},
        ]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                semantic.validate(decision(**changes))

    def test_checkpoint_resume_and_metadata_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir()
            (root / "results").mkdir()
            (root / "config/screening_criteria.md").write_text("Protocol version: 1.0.\n")
            rows = [{"paper_id": f"p{i}", "title": f"Vehicle privacy {i}", "abstract": "Abstract text.",
                     "keywords_json": '["location privacy"]', "publication_year": "2025",
                     "extra_metadata": 'Preserved, "exactly"\nwith newlines.'} for i in range(3)]
            for name in ("merged_papers.csv", "preliminary_screening.csv"):
                with (root / "results" / name).open("w", newline="", encoding="utf8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
            with patch.object(semantic, "ROOT", root), patch.object(semantic, "BATCH_SIZE", 2), redirect_stdout(io.StringIO()):
                source, pre, done, fingerprints = semantic.load()
                self.assertEqual(len(semantic.pending(source, done)), 2)
                with patch("sys.stdin", io.StringIO(json.dumps([[1, "I", "M", "I1", "Analyzes location disclosure."], [2, "M", "B", "I2", "Privacy context requires clarification."]]))):
                    semantic.save(source, done)
                source, pre, done, fingerprints = semantic.load()
                self.assertEqual([r["paper_id"] for r in semantic.pending(source, done)], ["p2"])
                semantic.export(source, pre, done, fingerprints)
                with patch("sys.stdin", io.StringIO(json.dumps([[1, "E", "O", "E1", "Analyzes message integrity without a privacy contribution."]]))):
                    semantic.save(source, done)
                source, pre, done, fingerprints = semantic.load()
                self.assertEqual(semantic.pending(source, done), [])
                semantic.export(source, pre, done, fingerprints)
                outputs = [root / "results" / n for n in ("semantic_screening.csv", "included.csv", "maybe.csv", "excluded.csv", "semantic_screening_report.md")]
                before = {p: p.read_bytes() for p in outputs}
                semantic.export(source, pre, done, fingerprints)
                self.assertEqual(before, {p: p.read_bytes() for p in outputs})
                with outputs[0].open(newline="", encoding="utf8") as handle:
                    saved = list(csv.DictReader(handle))
                self.assertEqual([{k: r[k] for k in rows[0]} for r in saved], rows)
                for path in outputs[1:4]:
                    with path.open(newline="", encoding="utf8") as handle:
                        self.assertEqual(len(list(csv.DictReader(handle))), 1)
                with self.assertRaises(ValueError):
                    semantic.save(source, done)
                (root / "config/screening_criteria.md").write_text("Changed criteria\n")
                with self.assertRaises(ValueError):
                    semantic.load()


if __name__ == "__main__":
    unittest.main()
