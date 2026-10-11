import unittest
from ingestion.six_stage_pilot import pipeline, fingerprint


class SixStagePilotTests(unittest.TestCase):
    def test_six_phases_never_fabricate_popularity_or_merge(self):
        report = pipeline({"items": [
            {"url": "https://arxiv.org/abs/2610.12345v1", "title": "A study of AI model safety",
             "authors": ["Researcher"], "publisher": "arXiv",
             "description": "We report a measured result about model safety in our experiment.",
             "source_ids": ["arxiv"], "relevance_hint": "explicit_ai_signal"},
            {"url": "https://example.com/a", "title": "Unrelated source",
             "description": "", "source_ids": ["press"],
             "relevance_hint": "needs_topic_review"}]})
        self.assertEqual(report["phase1"]["acquired_documents"], 2)
        self.assertEqual(len(report["phase2"]["messages"]), 1)
        self.assertEqual(report["phase2"]["messages"][0]["authors"], ["Researcher"])
        self.assertFalse(report["phase2"]["messages"][0]["verified_claim"])
        self.assertIsNone(report["phase3"]["relevance_evidence"][0]["external_mentions"])
        self.assertEqual(report["phase4"]["verified_merges"], 0)
        self.assertEqual(report["phase5"]["verified_discussions"], 0)
        self.assertEqual(report["phase6"]["excluded_for_low_popularity"], 0)

    def test_title_only_does_not_invent_message(self):
        report = pipeline({"items": [{"url": "https://example.org/x", "title": "AI agent",
                         "description": "", "relevance_hint": "explicit_ai_signal"}]})
        self.assertIsNone(report["phase2"]["messages"][0]["central_message"])
        self.assertEqual(report["phase2"]["messages"][0]["message_basis"], "title_only")

    def test_arxiv_version_is_same_work_not_same_event(self):
        self.assertEqual(fingerprint("https://arxiv.org/abs/2610.12345v2"),
                         fingerprint("https://arxiv.org/abs/2610.12345v1"))


if __name__ == "__main__":
    unittest.main()
