"""Bounded original-article text acquisition for frozen Qwen-reviewed cases.

Never bypass paywalls, login or robots restrictions. No invented text; retain
provenance, access status and source IDs. Results are research-only.
"""
import argparse,collections,ipaddress,json,re,socket,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from html.parser import HTMLParser

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__();self.depth=0;self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","nav","footer","header","aside","form","svg"):self.skip+=1
        if tag in ("p","h1","h2","h3","article","main","blockquote") and not self.skip:self.parts.append(" ")
    def handle_endtag(self,tag):
        if tag in ("script","style","nav","footer","header","aside","form","svg"):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)

def public_host(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.port not in (None,443):return False
    try:
        addrs=socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
        return bool(addrs) and all(ipaddress.ip_address(a[4][0]).is_global for a in addrs)
    except (socket.gaierror,ValueError,OSError):return False

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def fetch_text(url,max_bytes=900_000):
    if not public_host(url):return {"status":"blocked_url"}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"UbikResearchPilot/0.1","Accept":"text/html,application/xhtml+xml"})
        with urllib.request.build_opener(NoRedirect).open(req,timeout=12) as response:
            kind=response.headers.get("Content-Type","").lower()
            if "text/html" not in kind and "application/xhtml+xml" not in kind:return {"status":"unsupported_content"}
            raw=response.read(max_bytes+1)
            if len(raw)>max_bytes:return {"status":"oversize"}
            charset=response.headers.get_content_charset() or "utf-8"
            parser=Extractor();parser.feed(raw.decode(charset,errors="replace"))
            cleaned=re.sub(r"\s+"," "," ".join(parser.parts)).strip()
            if len(cleaned)<300:return {"status":"insufficient_text","characters":len(cleaned)}
            return {"status":"extracted_unverified","text":cleaned[:11000],"characters":len(cleaned)}
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError,ValueError,UnicodeError) as exc:
        return {"status":"fetch_unavailable","error_type":type(exc).__name__}

def run(graph,reviews,limit=50):
    byid={s["id"]:s for s in graph["sources"]}
    ordered=[];seen=set()
    for r in reviews["reviews"]:
        for sid in r["source_ids"]:
            if sid not in seen:seen.add(sid);ordered.append(sid)
    results=[]
    for sid in ordered[:limit]:
        d=byid[sid];item=fetch_text(d["url"])
        results.append({"source_id":sid,"url":d["url"],"title":d["title"],
            "rss_description":d.get("description",""),"published_at":d.get("published_at",""),
            **item})
    counts=dict(collections.Counter(x["status"] for x in results))
    return {"summary":{"reviewed_source_ids":len(ordered),"attempted":len(results),
        "remaining":max(0,len(ordered)-len(results)),"statuses":counts,
        "texts_800_plus":sum(len(x.get("text",""))>=800 for x in results)},
        "sources":results,"limitations":["HTML extraction is noisy and not yet evidence validation.",
          "No paywall bypass; HTTP redirects deliberately disabled.",
          "Source text may contain navigation or unrelated content; manual inspection needed.",
          "No automatic card publication."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("graph",type=Path);p.add_argument("reviews",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--limit",type=int,default=50)
    a=p.parse_args()
    out=run(json.loads(a.graph.read_text()),json.loads(a.reviews.read_text()),max(1,min(100,a.limit)))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("TEXT_ACQUISITION",json.dumps(out["summary"]))
if __name__=="__main__":main()
