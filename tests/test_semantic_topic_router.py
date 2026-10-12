import unittest
from ingestion.semantic_topic_router import route,existing_topics

def post(i,tag,text):
    return {"url":f"https://social.example/{i}","source_id":f"account{i}",
            "title":text,"metadata":{"hashtags":[tag],"text_preview":text,
                                     "linked_documents":[f"https://news.example/{i}"]}}

class SemanticTopicRouterTests(unittest.TestCase):
    def setUp(self):
        self.topics=[{"id":"energy","title":"Energia","context":"rete elettrica e infrastrutture"},
                     {"id":"health","title":"Salute","context":"medicina e ospedali"}]
        self.posts=[post(1,"gridfailure","blackout on the electrical network"),
                    post(2,"gridfailure","interruzione della rete elettrica")]
    def test_closed_catalog_and_provenance(self):
        def embed(texts):
            self.assertTrue(all(x.startswith("query: ") for x in texts))
            return [[1.,0.],[0.,1.],[.98,.2]]
        r=route(self.posts,self.topics,embed,threshold=.8,margin=.1)
        self.assertEqual(r["proposals"][0]["topic_id"],"energy")
        self.assertEqual(len(r["proposals"][0]["supporting_posts"]),2)
        self.assertEqual(r["created_topics"],[])
        self.assertEqual(r["created_hashtag_sections"],[])
        self.assertFalse(r["automatic_publication"])
    def test_ambiguous_scores_abstain(self):
        r=route(self.posts,self.topics,lambda t:[[1,0],[.99,.1],[1,0]],
                threshold=.7,margin=.06)
        self.assertFalse(r["proposals"])
        self.assertEqual(len(r["abstentions"]),1)
    def test_insufficient_independent_accounts_abstain(self):
        posts=[self.posts[0],dict(self.posts[1],source_id="account1")]
        r=route(posts,self.topics,lambda t:[[1,0],[0,1]])
        self.assertEqual(r["eligible_groups"],0)
    def test_only_existing_catalog_topics(self):
        t=existing_topics({"topics":[{"id":"a","title":"AI","description":"modelli"},
                                      {"id":"a","title":"Duplicate"}]})
        self.assertEqual(len(t),1)
if __name__=="__main__":unittest.main()
