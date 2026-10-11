import unittest
from ingestion.topic_evidence import build, evidence


class TopicEvidenceTests(unittest.TestCase):
    def test_verbatim_arxiv_abstract_evidence_and_provenance(self):
        description = ("We evaluate a new benchmark for language model reasoning. "
                       "Our results suggest substantial differences between the evaluated systems.")
        discovery = {"items": [{"url": "https://arxiv.org/abs/1234.56789",
                                "title": "Reasoning benchmark", "description": description}]}
        topic = {"topic": {"id": "ai-models"}, "visible": [],
                 "all_candidates": [{"url": "https://arxiv.org/abs/1234.56789",
                                     "title": "Reasoning benchmark", "source_ids": ["arxiv-cs-ai"]}]}
        result = build(discovery, topic)
        self.assertEqual(result["candidate_count"], 1)
        row = result["items"][0]
        self.assertEqual(row["description_evidence"][0],
                         "Our results suggest substantial differences between the evaluated systems.")
        self.assertEqual(row["content_type_candidate"], "research_candidate")
        self.assertFalse(row["claim_verified"])
        self.assertFalse(row["full_text_accessed"])

    def test_title_only_does_not_invent_claim(self):
        row = evidence({"url": "https://example.org/a", "title": "AI model"})
        self.assertEqual(row["description_evidence"], [])
        self.assertEqual(row["message_status"], "insufficient_text")
        self.assertEqual(row["editorial_decision"], "review_required")

    def test_entire_candidate_pool_is_processed(self):
        report = {"all_candidates": [{"url": "https://a.test/1", "title": "A"},
                                     {"url": "https://b.test/2", "title": "B"}],
                  "visible": [{"url": "https://a.test/1", "title": "A"}]}
        self.assertEqual(build({"items": []}, report)["candidate_count"], 2)


if __name__ == "__main__":
    unittest.main()
