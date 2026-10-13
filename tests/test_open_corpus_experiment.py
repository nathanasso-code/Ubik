import hashlib,unittest
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
    def test_invalid_budget(self):
        with self.assertRaises(ValueError):collect(limit=121,transport=fake_api)
if __name__=="__main__":unittest.main()
