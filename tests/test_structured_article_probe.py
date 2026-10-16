import unittest
from ingestion.live_get_text_probe import Extractor,jsonld_article_lengths

class StructuredArticleTests(unittest.TestCase):
    def test_article_jsonld_signal(self):
        html='<script type="application/ld+json">{"@type":"NewsArticle","articleBody":"Evidence from publisher"}</script><article><p>Body</p></article>'
        parser=Extractor();parser.feed(html)
        self.assertEqual(jsonld_article_lengths(parser.jsonld_blocks),[23])
        self.assertIn('Body',''.join(parser.article))
        self.assertNotIn('Evidence from publisher',''.join(parser.text))
    def test_graph_and_malformed(self):
        self.assertEqual(jsonld_article_lengths(['invalid','{"@graph":[{"@type":"Article","articleBody":"Hello world"}]}']),[11])
    def test_no_article_type(self):
        self.assertEqual(jsonld_article_lengths(['{"@type":"WebPage","articleBody":"Not an article"}']),[])

if __name__=='__main__':unittest.main()
