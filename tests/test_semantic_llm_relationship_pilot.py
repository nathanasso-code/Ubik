import unittest
from ingestion.semantic_llm_relationship_pilot import classify

class SemanticLLMRelationshipTests(unittest.TestCase):
    def test_distinguishes_topic_from_card(self):
        pairs=[{"similarity":0.9,"left":{"url":"https://a.test/a","title":"One"},
                "right":{"url":"https://b.test/b","title":"Two"}}]
        text="This is a sufficiently detailed example passage for a substantial article. "*20
        def requester(messages,endpoint,model,key):
            return {"relation":"topic_only","reason":"Same topic but different research",
                    "evidence_a_id":"A1","evidence_b_id":"B1","confidence":"medium"},{}
        out=classify(pairs,acquirer=lambda _:text,requester=requester,limit=5)
        self.assertEqual(out["summary"]["labels"]["topic_only"],1)
        self.assertEqual(out["summary"]["accepted_for_review"],1)
    def test_inaccessible_text_excluded(self):
        pairs=[{"left":{"url":"https://a.test/a","title":"One"},
                "right":{"url":"https://b.test/b","title":"Two"}}]
        def acquirer(url):
            if "b.test" in url:raise ValueError("insufficient text")
            return "a"*900
        out=classify(pairs,acquirer=acquirer,requester=lambda *args:None)
        self.assertEqual(out["summary"]["analyzed"],0)
        self.assertEqual(out["summary"]["unique_urls_accessed"],2)
    def test_invalid_passage_id_not_accepted(self):
        pairs=[{"left":{"url":"https://a.test/a","title":"One"},
                "right":{"url":"https://b.test/b","title":"Two"}}]
        def requester(*args):
            return {"relation":"same_news_development","evidence_a_id":"A999","evidence_b_id":"B1"},{}
        out=classify(pairs,acquirer=lambda _:("Substantial article text with details. "*40),requester=requester)
        self.assertEqual(out["summary"]["accepted_for_review"],0)
if __name__=="__main__":unittest.main()
