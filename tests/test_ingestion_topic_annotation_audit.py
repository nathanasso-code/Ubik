import unittest
from ingestion.topic_annotation_audit import validate


class AnnotationAuditTests(unittest.TestCase):
    def test_unreviewed_worksheet_remains_pending(self):
        rows = [{"url": "https://example.org/a", "title": "A", "feed_decision": "",
                 "central_message": ""}]
        report = validate(rows, known_urls=["https://example.org/a"])
        self.assertTrue(report["valid"])
        self.assertEqual(report["pending_rows"], 1)
        self.assertEqual(report["publication_approvals"], 0)

    def test_complete_valid_review(self):
        row = {"url": "https://example.org/a", "title": "A",
               "topic_relevance": "yes", "content_kind": "research",
               "central_message": "Study reports improved scores",
               "central_message_evidence": "Study reports improved scores in the abstract",
               "original_contribution": "yes",
               "importance_reason": "A new benchmark is described",
               "same_event_with_url": "", "independent_origin": "unknown",
               "feed_decision": "defer"}
        report = validate([row], known_urls=[row["url"]])
        self.assertTrue(report["valid"])
        self.assertEqual(report["completed_rows"], 1)

    def test_reject_off_topic_inclusion_and_untraceable_relation(self):
        row = {"url": "https://example.org/a", "title": "A",
               "topic_relevance": "no", "content_kind": "other",
               "central_message": "Off-topic", "central_message_evidence": "Off-topic",
               "original_contribution": "uncertain", "importance_reason": "Not related",
               "same_event_with_url": "https://outside.org/other",
               "independent_origin": "unknown", "feed_decision": "include"}
        report = validate([row], known_urls=[row["url"]])
        self.assertFalse(report["valid"])
        self.assertEqual(len(report["errors"]), 2)

    def test_partial_label_does_not_count_as_pending(self):
        report = validate([{"url": "https://example.org/a", "topic_relevance": "yes"}])
        self.assertFalse(report["valid"])


if __name__ == "__main__":
    unittest.main()
