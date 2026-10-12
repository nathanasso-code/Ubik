import unittest
from ingestion.source_expansion_candidates import expand
from ingestion.issue_attention_triage import triage

class SourceExpansionTests(unittest.TestCase):
    def test_author_and_domain_candidates_are_unverified(self):
        dossier={"topic":"ai", "sources":[
            {"url":"https://example.org/a","posts":[{"author":"a.bsky.social","url":"https://bsky.app/profile/a.bsky.social/post/1"}]},
            {"url":"https://example.org/b","posts":[{"author":"a.bsky.social","url":"https://bsky.app/profile/a.bsky.social/post/2"}]}]}
        result=expand(dossier)
        self.assertEqual(len(result["authors"]),1)
        self.assertEqual(len(result["publishers"]),1)
        self.assertFalse(result["authors"][0]["independence_verified"])
        self.assertEqual(len(result["authors"][0]["post_urls"]),2)

    def test_raw_shares_not_verified_convergence(self):
        doc={"url":"https://example.org/a","social_mentions":[{"author":"a"},{"author":"b"},{"author":"c"}]}
        row=triage([doc])["items"][0]
        self.assertEqual(row["priority"],"unassessed")
        self.assertEqual(row["distinct_handles_observed"],3)

    def test_reviewed_independent_groups_and_substantive_debate(self):
        doc={"url":"https://example.org/a","social_mentions":[
            {"author":"a","independence_reviewed":True,"independent_origin_group":"group1"},
            {"author":"b","independence_reviewed":True,"independent_origin_group":"group2"}],
            "debate_evidence":[{"url":"https://example.org/reply","reviewed":True,"substantive":True,"reason":"Original counterdata"}]}
        row=triage([doc])["items"][0]
        self.assertEqual(row["priority"],"high_review")
        self.assertEqual(row["substantive_contributions_reviewed"],1)

if __name__=="__main__":
    unittest.main()
