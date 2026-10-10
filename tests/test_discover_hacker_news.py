import unittest
from scripts.discover_hacker_news import collect, normalize_story


class HackerNewsConnectorTests(unittest.TestCase):
    def test_normalization_preserves_discussion_and_target(self):
        record = normalize_story({"id": 123, "type": "story", "title": "  An article  ",
                                  "url": "https://publisher.example/story", "time": 1700000000,
                                  "score": 3})
        self.assertEqual(record["original_url"], "https://news.ycombinator.com/item?id=123")
        self.assertEqual(record["url"], "https://publisher.example/story")
        self.assertEqual(record["validation"], "not_assessed")

    def test_deleted_stories_ignored(self):
        self.assertIsNone(normalize_story({"id": 1, "type": "story", "title": "A", "deleted": True}))
        self.assertIsNone(normalize_story({"id": 1, "type": "comment", "title": "A"}))

    def test_bounded_collection_and_error_isolation(self):
        def fetch(path):
            if path == "newstories.json":
                return [1, 2, 3]
            if path == "item/2.json":
                raise OSError("temporary")
            return {"id": int(path.split("/")[1].split(".")[0]), "type": "story", "title": "A"}
        result = collect(3, pause_seconds=0, fetch=fetch, sleep=lambda _: None)
        self.assertEqual(len(result["observations"]), 2)
        self.assertEqual(len(result["errors"]), 1)

    def test_limit_validation(self):
        with self.assertRaises(ValueError):
            collect(501, fetch=lambda _: [])


if __name__ == "__main__":
    unittest.main()
