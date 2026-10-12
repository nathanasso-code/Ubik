import unittest
from ingestion.authorized_source_text import capture_authorized_html
class AuthorizedSourceTests(unittest.TestCase):
    HTML="""<html><header><p>Navigation text not evidence</p></header><article>
    <h1>Power demand rises after installation of industrial equipment</h1>
    <p>The regulator measured a significant increase in electricity demand after the facility opened.</p>
    <aside><p>Sponsored material must not appear in source evidence.</p></aside>
    <p>A second independent observation is needed before drawing any causal conclusion.</p>
    </article><script>ignored()</script></html>"""
    def test_extract_authorized_without_network(self):
        r=capture_authorized_html("https://example.org/article",self.HTML,access_authorized=True)
        self.assertIn("regulator measured",r["text"])
        self.assertNotIn("Sponsored material",r["text"])
        self.assertNotIn("Navigation text",r["text"])
        self.assertEqual(r["network_requests"],0)
        self.assertEqual(len(r["sha256"]),64)
    def test_no_permission(self):
        with self.assertRaises(PermissionError):
            capture_authorized_html("https://example.org/article",self.HTML)
    def test_reject_local_or_non_https(self):
        for url in ["http://example.org/a","https://user:pass@example.org/a","https://example.org:8080/a"]:
            with self.subTest(url=url),self.assertRaises(ValueError):
                capture_authorized_html(url,self.HTML,access_authorized=True)
    def test_insufficient_text_not_promoted(self):
        with self.assertRaises(ValueError):
            capture_authorized_html("https://example.org/a","<p>Headline</p>",access_authorized=True)
if __name__=="__main__":unittest.main()
