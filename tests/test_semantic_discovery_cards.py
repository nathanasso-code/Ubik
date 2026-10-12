import unittest
from ingestion.semantic_discovery_cards import build_semantic_cards,render_markdown
class SemanticCardTests(unittest.TestCase):
    def test_source_grounded_unverified_cards(self):
        review={"selected":[{"frozen_rank":59,"similarity":.8815,
                 "left":{"url":"https://a.example/one","title":"Yandex data centre hit","host":"a.example"},
                 "right":{"url":"https://b.example/two","title":"Russian technology infrastructure attacked","host":"b.example"}}]}
        result=build_semantic_cards(review)
        self.assertEqual(len(result["cards"]),1)
        card=result["cards"][0]
        self.assertEqual(card["status"],"da_verificare")
        self.assertFalse(card["claims_verified"])
        self.assertFalse(card["automatic_topic_assignment"])
        self.assertFalse(result["published"])
        self.assertFalse(result["automatic_topic_creation"])
        self.assertIn("https://a.example/one",render_markdown(result))
    def test_no_card_without_original_source_title(self):
        result=build_semantic_cards({"selected":[{"left":{"url":"https://a.example/1","title":""},
                                                   "right":{"url":"https://b.example/2","title":"Two"}}]})
        self.assertEqual(result["cards"],[])
if __name__=="__main__":unittest.main()
