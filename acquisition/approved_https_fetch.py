"""Bounded, pinned-IP HTTPS transport for explicitly approved publisher sources.

Network use requires a publisher allowlist plus a positive rights/robots policy
assertion. No redirects, credentials, cookies, proxies, login or paywall bypass.
"""
import argparse,http.client,ipaddress,json,socket,ssl,time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

USER_AGENT="UbikResearchBot/0.1 (+contact: ubik.research@gmail.com)"
MAX_BYTES=1_000_000

def public_ip(address):
    try:
        ip=ipaddress.ip_address(address)
        return ip.is_global and not ip.is_multicast
    except ValueError:return False

def validate_url(url,approved_hosts):
    p=urlsplit(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.port not in (None,443) or p.fragment:
        raise ValueError("Only canonical HTTPS URLs with standard port and no credentials/fragments")
    host=p.hostname.lower().rstrip(".")
    if host not in approved_hosts:raise PermissionError("Publisher host is not explicitly approved")
    return host,p.path or "/",p.query

class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self,host,ip,timeout):
        super().__init__(host,port=443,timeout=timeout,context=ssl.create_default_context())
        self.pinned_ip=ip
    def connect(self):
        raw=socket.create_connection((self.pinned_ip,443),self.timeout)
        self.sock=self._context.wrap_socket(raw,server_hostname=self.host)

def fetch_one(url,approved_hosts,*,transport=None,timeout=8):
    host,path,query=validate_url(url,approved_hosts)
    # Reject the entire DNS answer if ANY result is non-public; prevents unsafe fallback.
    addresses={x[4][0] for x in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)}
    if not addresses or not all(public_ip(ip) for ip in addresses):raise PermissionError("Non-public DNS destination")
    ip=sorted(addresses)[0]
    connection=transport(host,ip,timeout) if transport else _PinnedHTTPS(host,ip,timeout)
    try:
        connection.request("GET",path+("?"+query if query else ""),headers={"Host":host,"User-Agent":USER_AGENT,"Accept":"text/html,text/plain"})
        response=connection.getresponse()
        if response.status!=200:raise ValueError(f"HTTP status {response.status}; redirects are forbidden")
        kind=response.getheader("Content-Type","").split(";")[0].lower()
        if kind not in ("text/html","text/plain"):raise ValueError("Unexpected content type")
        declared=response.getheader("Content-Length")
        if declared and int(declared)>MAX_BYTES:raise ValueError("Oversized response")
        data=response.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES:raise ValueError("Oversized response")
        return data.decode("utf-8",errors="replace")
    finally:connection.close()

def fetch_authorized(url,policy,*,transport=None):
    host,_,_=validate_url(url,policy.get("approved_hosts",[]))
    if not policy.get("rights_confirmed") or not policy.get("robots_review_confirmed"):
        raise PermissionError("Rights and robots policy must be explicitly approved before network access")
    # Fetch robots.txt with same DNS/IP pinning and no redirects.
    robots_url=f"https://{host}/robots.txt"
    robots=fetch_one(robots_url,policy["approved_hosts"],transport=transport)
    parser=RobotFileParser();parser.parse(robots.splitlines())
    if not parser.can_fetch(USER_AGENT,url):raise PermissionError("robots.txt disallows this path")
    return {"url":url,"html":fetch_one(url,policy["approved_hosts"],transport=transport),
            "robots_checked":True,"rights_confirmed_by_operator":True,
            "redirects_followed":0,"retrieved_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url",required=True)
    p.add_argument("--policy",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=fetch_authorized(a.url,json.loads(a.policy.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"retrieved":True,"url":a.url,"robots_checked":True}))
if __name__=="__main__":main()
