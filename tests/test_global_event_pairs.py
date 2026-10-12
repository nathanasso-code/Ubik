import unittest
from ingestion.global_event_pairs import event_pair_candidates

def row(url,title,date="2026-10-12T12:00:00Z"):
    return {"url":url,"title":title,"published_raw":date,"source_id":url.split("/")[2]}

class GlobalEventPairTests(unittest.TestCase):
    def test_proposes_cross_publisher_specific_story(self):
        data={"items":[
            row("https://one.example/a","Riyadh airport damaged after Houthi drone attack"),
            row("https://two.example/b","Houthi drone attack damages Riyadh airport")]}
        result=event_pair_candidates(data)
        self.assertEqual(len(result["candidate_pairs"]),1)
        self.assertFalse(result["automatic_event_merges"])
        self.assertFalse(result["candidate_pairs"][0]["same_event_verified"])
    def test_does_not_merge_generic_topic(self):
        data={"items":[row("https://one.example/a","Ukraine government discusses economy"),
                       row("https://two.example/b","Ukraine government discusses education")]}
        self.assertEqual(event_pair_candidates(data)["candidate_pairs"],[])
    def test_time_window_blocks_old_event(self):
        data={"items":[row("https://one.example/a","Riyadh airport damaged after Houthi drone attack"),
                       row("https://two.example/b","Houthi drone attack damages Riyadh airport",
                           "2026-10-01T12:00:00Z")]}
        self.assertEqual(event_pair_candidates(data)["candidate_pairs"],[])
    def test_same_publisher_and_missing_dates_not_evidence(self):
        data={"items":[row("https://one.example/a","Riyadh airport damaged after Houthi drone attack"),
                       row("https://one.example/b","Houthi drone attack damages Riyadh airport"),
                       row("https://two.example/c","Houthi drone attack damages Riyadh airport",None)]}
        self.assertEqual(event_pair_candidates(data)["candidate_pairs"],[])
if __name__=="__main__":unittest.main()
