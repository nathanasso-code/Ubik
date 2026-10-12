import unittest
from ingestion.global_cards import build_cards,render_markdown

def doc(url,title):
    return {"url":url,"title":title,"source_id":url.split("/")[2],
            "published_raw":"2026-10-12T12:00:00Z"}

class GlobalCardsTests(unittest.TestCase):
    def test_source_cards_are_literal_feed_titles(self):
        r=build_cards({"items":[doc("https://one.example/a","Publisher title A")]},
                      {"candidate_pairs":[]})
        self.assertEqual(r["cards"][0]["heading"],"Publisher title A")
        self.assertFalse(r["automated_summaries"])
        self.assertIn("https://one.example/a",render_markdown(r))
    def test_pair_requires_both_real_documents(self):
        a=doc("https://one.example/a","Riyadh airport damaged")
        b=doc("https://two.example/b","Riyadh airport reports")
        pair={"documents":[a,b],"shared_title_terms":["riyadh","airport"]}
        r=build_cards({"items":[a,b]},{"candidate_pairs":[pair]})
        self.assertEqual(r["cards"][0]["type"],"possible_shared_event")
        self.assertEqual(r["cards"][0]["review_status"],"unverified")
        self.assertFalse(r["verified_events"])
        r2=build_cards({"items":[a]},{"candidate_pairs":[pair]})
        self.assertEqual(r2["cards"][0]["type"],"source_document")
    def test_duplicate_url_not_multiple_cards(self):
        a=doc("https://one.example/a","First")
        self.assertEqual(len(build_cards({"items":[a,a]},{"candidate_pairs":[]})["cards"]),1)
if __name__=="__main__":unittest.main()
