import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("relevance", Path(__file__).resolve().parents[1] / "scripts/review_ai_relevance.py")
relevance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relevance)

class RelevanceTests(unittest.TestCase):
    def test_italian_direct(self):
        self.assertEqual(relevance.assess({"title":"L'intelligenza artificiale e il lavoro"})["relevance_status"], "likely_ai")
    def test_economic_context_needs_review(self):
        self.assertEqual(relevance.assess({"title":"La produttività del lavoro"})["relevance_status"], "review_context")
    def test_unrelated_is_unknown_not_rejected(self):
        self.assertEqual(relevance.assess({"title":"La storia di Roma"})["relevance_status"], "unknown")
    def test_authorship_is_preserved(self):
        item = {"title":"Machine learning research", "authors":["A. Researcher"], "attribution_basis":"entry"}
        result = relevance.assess(item)
        self.assertEqual(result["original_authors"], ["A. Researcher"])
        self.assertEqual(result["basis"], "title_keywords_only")

if __name__ == "__main__":
    unittest.main()
