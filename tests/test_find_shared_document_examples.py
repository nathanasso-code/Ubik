import unittest
from scripts.find_shared_document_examples import same_document_examples


class SharedDocumentExamplesTests(unittest.TestCase):
    def test_same_url_multiple_feeds_not_independent(self):
        items = [
            {"id": "a", "source_id": "feed-a", "url": "https://example.org/paper", "title": "Paper"},
            {"id": "b", "source_id": "feed-b", "url": "https://example.org/paper", "title": "Paper"},
            {"id": "c", "source_id": "feed-a", "url": "https://example.org/paper", "title": "Paper"},
            {"id": "d", "source_id": "feed-c", "url": "https://example.org/other", "title": "Other"},
        ]
        result = same_document_examples({"items": items})
        self.assertEqual(result["coverage"]["shared_document_groups"], 1)
        group = result["groups"][0]
        self.assertEqual(len(group["observations"]), 2)
        self.assertFalse(group["independent_corroboration"])
        self.assertIsNone(group["same_event_label"])
        self.assertEqual(result, same_document_examples({"items": list(reversed(items))}))

    def test_empty_and_invalid_limit(self):
        self.assertEqual(same_document_examples({})["groups"], [])
        with self.assertRaises(ValueError):
            same_document_examples({}, 0)


if __name__ == "__main__":
    unittest.main()
