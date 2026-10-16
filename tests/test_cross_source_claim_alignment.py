import unittest
from ingestion.cross_source_claim_alignment import compare,analyze
class AlignmentTests(unittest.TestCase):
    def test_numeric_mismatch_is_candidate_not_verdict(self):
        a={"claims":[{"excerpt":"The school collapse killed 33 students and a teacher in Pakistan after the roof failed.","numbers":["33"]}]}
        b={"claims":[{"excerpt":"The school collapse killed 32 students and a teacher in Pakistan when the roof failed.","numbers":["32"]}]}
        matches=compare(a,b)
        self.assertTrue(matches)
        self.assertTrue(matches[0]["numeric_mismatch_candidate"])
    def test_different_topics_abstain(self):
        a={"claims":[{"excerpt":"The satellite traveled 900 kilometers above Earth during the scientific mission.","numbers":["900"]}]}
        b={"claims":[{"excerpt":"The local election drew 700 voters after the city announced new rules.","numbers":["700"]}]}
        self.assertFalse(compare(a,b))
    def test_pair_relation_unverified(self):
        p={"left":{"url":"https://a.example/1"},"right":{"url":"https://b.example/2"},"both_800_100":True}
        def fake(u):
            return {"status":"text_available","claims":[{"excerpt":"The school collapse killed 33 students and a teacher in Pakistan after the roof failed.","numbers":["33"]}]}
        r=analyze({"pairs":[p]},checker=fake)
        self.assertEqual(r["pairs"][0]["relation"],"unverified")
        self.assertEqual(r["summary"]["pairs_both_available"],1)
if __name__=="__main__":unittest.main()
