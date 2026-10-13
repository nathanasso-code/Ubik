import unittest
from unittest.mock import patch
from ingestion.approved_https_fetch import public_ip,validate_url,fetch_one,fetch_authorized
class _Response:
    status=200
    def __init__(self,text):self.text=text
    def getheader(self,key,default=None):
        return {"Content-Type":"text/html","Content-Length":str(len(self.text))}.get(key,default)
    def read(self,n):return self.text.encode()[:n]
class _Connection:
    def __init__(self,host,ip,timeout):self.host=host;self.path=None
    def request(self,method,path,headers):self.path=path
    def getresponse(self):
        if self.path=="/robots.txt":return _Response("User-agent: *\nAllow: /\n")
        return _Response("<article><p>Authorized article content for controlled testing.</p></article>")
    def close(self):pass
class ApprovedHTTPSFetchTests(unittest.TestCase):
    def test_reject_non_public(self):
        for address in ["127.0.0.1","10.0.0.1","192.168.1.1","169.254.169.254","::1","fc00::1"]:
            self.assertFalse(public_ip(address))
    def test_allowlist_and_credentials(self):
        for url in ["https://localhost/a","http://example.org/a","https://user@example.org/a"]:
            with self.assertRaises((PermissionError,ValueError)):
                validate_url(url,["example.org"])
    @patch("ingestion.approved_https_fetch.socket.getaddrinfo",return_value=[(2,1,6,"",("93.184.215.14",443))])
    def test_authorized_fetch_with_robots(self,mock_dns):
        result=fetch_authorized("https://example.org/article",
                 {"approved_hosts":["example.org"],"rights_confirmed":True,"robots_review_confirmed":True},
                 transport=_Connection)
        self.assertTrue(result["robots_checked"])
        self.assertEqual(result["redirects_followed"],0)
    @patch("ingestion.approved_https_fetch.socket.getaddrinfo",return_value=[(2,1,6,"",("127.0.0.1",443))])
    def test_private_dns_denied(self,mock_dns):
        with self.assertRaises(PermissionError):
            fetch_one("https://example.org/a",["example.org"],transport=_Connection)
    def test_missing_rights_denied_before_network(self):
        with self.assertRaises(PermissionError):
            fetch_authorized("https://example.org/a",{"approved_hosts":["example.org"]},transport=_Connection)
if __name__=="__main__":unittest.main()
