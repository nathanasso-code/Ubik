import hashlib,unittest
from unittest.mock import patch
from urllib.error import HTTPError
from ingestion.open_text_corpus import collect
from ingestion.open_corpus_analysis import analyze
def fake_api(params):
    if params["action"]=="query":
        return {"query":{"categorymembers":[{"pageid":1,"title":"Major storm strikes city"},{"pageid":2,"title":"Major storm damages city"},{"pageid":3,"title":"Unrelated parliamentary debate"}]}}
    i=params["pageid"]
    text={1:"The coastal storm caused widespread flooding in the city and damaged many buildings. Local authorities reported several residents evacuated after the storm. ",
          2:"The storm damaged several buildings in the city and caused flooding near the coast. Local officials reported that residents moved to shelters. ",
          3:"The national parliament debated a new budget in a lengthy meeting. Officials discussed the proposal and a future vote. "}[i]*5
    return {"parse":{"text":"<article><p>"+text+"</p></article>","revid":100+i}}
class CorpusTests(unittest.TestCase):
    def test_real_text_transport_shape_and_end_to_end(self):
        c=collect(limit=3,transport=fake_api)
        self.assertEqual(c["acquired"],3)
        r=analyze(c)
        self.assertEqual(r["documents_acquired"],3)
        self.assertGreater(r["claim_candidate_count"],0)
        self.assertFalse(r["automatic_publication"])
        self.assertTrue(all(not x["claims_verified"] for x in r["cards"]))
    def test_distinct_real_world_events_never_merge_from_title_overlap(self):
        titles=["Caloundra win round 3 game in Australian soccer league", "Caloundra lose round 2 game in Australian soccer league", "Mamdani wins New York City mayoral election", "Cuomo concedes to Mamdani in Democratic primary election for New York City mayor"]
        d=[{"url":f"https://example.org/{i}", "title":t, "text":(t+". The report records an event and quotes several witnesses. ")*15} for i,t in enumerate(titles)]
        for item in d:item["sha256"]=hashlib.sha256(item["text"].encode()).hexdigest()
        r=analyze({"documents":d})
        self.assertTrue(all(c["source_count"]==1 for c in r["cards"]))
        self.assertFalse(r["automatic_publication"])
    def test_rate_limit_returns_partial_status_without_fabricating_docs(self):
        with patch("ingestion.open_text_corpus.api",side_effect=RuntimeError("Public API rate-limited (HTTP 429)")):
            c=collect(limit=3)
        self.assertEqual(c["acquired"],0)
        self.assertEqual(c["collection_status"],"partial")
        self.assertIn("429",c["stop_reason"])
    def test_invalid_budget(self):
        with self.assertRaises(ValueError):collect(limit=121,transport=fake_api)
if __name__=="__main__":unittest.main()
