import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("discovery", Path(__file__).resolve().parents[1] / "scripts/discover_ai_sources.py")
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)

class MetadataEnrichmentTests(unittest.TestCase):
    def test_rss_description_and_collective_author(self):
        xml = b'''<rss xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><item>
        <title>Research update</title><link>https://example.org/research</link>
        <dc:creator>Editorial Team</dc:creator>
        <description>&lt;p&gt;Artificial intelligence &amp;amp; economics&lt;/p&gt;</description>
        </item></channel></rss>'''
        item = discovery.parse_feed(xml, {"id":"research","name":"Research Journal"})[0]
        self.assertEqual(item["attribution_type"], "collective_or_institutional_candidate")
        self.assertEqual(item["description"], "Artificial intelligence & economics")
        self.assertEqual(item["attribution_status"], "feed_only_unverified")

    def test_atom_summary_and_no_author(self):
        xml = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <title>Analysis</title><link href="https://example.org/analysis"/>
        <summary>Neuroscience and machine learning</summary></entry></feed>'''
        item = discovery.parse_feed(xml, {"id":"journal","name":"Journal"})[0]
        self.assertEqual(item["description"], "Neuroscience and machine learning")
        self.assertEqual(item["attribution_type"], "not_specified_in_feed")
        self.assertEqual(item["authors"], [])

    def test_existing_record_enriched_without_duplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "registry.json"
            output = Path(tmp) / "discovery.json"
            registry.write_text(json.dumps({"topic_id":"ai-models","sources":[
                {"id":"journal","name":"Journal","kind":"rss","enabled":True,"url":"https://example.org/feed"}]}))
            xmls = [
                b'<rss><channel><item><title>AI</title><link>https://example.org/a</link></item></channel></rss>',
                b'<rss xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><item><title>AI</title><link>https://example.org/a</link><dc:creator>Researcher</dc:creator><description>Machine learning in economics</description></item></channel></rss>'
            ]
            discovery.run(registry, output, lambda _: xmls[0])
            result = discovery.run(registry, output, lambda _: xmls[1])
            self.assertEqual(result["coverage"]["stored_items"], 1)
            item = result["items"][0]
            self.assertEqual(item["authors"], ["Researcher"])
            self.assertEqual(item["description"], "Machine learning in economics")
            self.assertEqual(result["source_reports"][0]["new"], 0)

if __name__ == "__main__":
    unittest.main()
