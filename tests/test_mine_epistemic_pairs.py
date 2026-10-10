import unittest
from scripts.mine_epistemic_pairs import mine


class FullArchivePairMiningTests(unittest.TestCase):
    def test_cross_source_pairs_without_claiming_same_event(self):
        data = {"items": [
            {"id": "a", "source_id": "one", "url": "https://one.example/a", "title": "Orion launch reaches public beta"},
            {"id": "b", "source_id": "two", "url": "https://two.example/b", "title": "Orion launch enters public beta"},
            {"id": "c", "source_id": "one", "url": "https://one.example/c", "title": "Orion launch public beta overview"},
            {"id": "d", "source_id": "three", "url": "https://three.example/d", "title": "Cognitive neuroscience conference"},
        ]}
        result = mine(data)
        self.assertEqual(result["coverage"]["input_observations"], 4)
        self.assertTrue(result["items"])
        self.assertTrue(all(x["left_source"] != x["right_source"] for x in result["items"]))
        self.assertTrue(all(x["same_event_label"] is None and x["review_status"] == "unreviewed" for x in result["items"]))
        self.assertEqual(result, mine({"items": list(reversed(data["items"]))}))

    def test_empty_and_invalid_limits(self):
        self.assertEqual(mine({})["coverage"]["selected_pairs"], 0)
        with self.assertRaises(ValueError):
            mine({}, limit=0)


if __name__ == "__main__":
    unittest.main()
