"""Conservative HTTP metadata accessibility probe (not an article text fetch).

Checks robots and HEAD status without retrieving article bodies, credentials,
cookies, redirects or private-network destinations. Never interprets HTTP 200
as copyright permission, full-text availability, or article completeness.
"""
import argparse,collections,json,socket
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import USER_AGENT,public_ip,_PinnedHTTPS

def head_status(url,timeout=5):
    p=urlsplit(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.port not in (None,443):
        return {"status":"invalid_url"}
    host=p.hostname
    try:
        addresses={x[4][0] for x in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)}
        if not addresses or not all(public_ip(x) for x in addresses):
            return {"status":"blocked_non_public_destination"}
        conn=_PinnedHTTPS(host,sorted(addresses)[0],timeout)
        try:
            conn.request("HEAD",(p.path or "/")+("?"+p.query if p.query else ""),
                         headers={"Host":host,"User-Agent":USER_AGENT,"Accept":"text/html"})
            response=conn.getresponse()
            return {"status":"http_response","http_status":response.status,
                    "content_type":(response.getheader("Content-Type") or "").split(";")[0],
                    "content_length_header":response.getheader("Content-Length"),
                    "redirect_not_followed":300<=response.status<400}
        finally:conn.close()
    except (OSError,TimeoutError,ValueError) as e:
        return {"status":"transport_error","error_type":type(e).__name__}

def probe(snapshot,*,per_host=3,max_urls=90,checker=head_status):
    if not 1<=per_host<=10 or not 1<=max_urls<=150:raise ValueError("Probe budget exceeded")
    rows=[];counts=collections.Counter();seen=set()
    for item in snapshot.get("items",[]):
        url=item.get("url","")
        host=urlsplit(url).hostname if isinstance(url,str) else None
        if not host or url in seen or counts[host]>=per_host:continue
        seen.add(url);counts[host]+=1
        rows.append({"url":url,"publisher":item.get("publisher"),"source_id":item.get("source_id")})
        if len(rows)>=max_urls:break
    for row in rows:
        row.update(checker(row["url"]))
        row.update({"article_body_fetched":False,"full_text_access_confirmed":False,
                    "robots_compliance_for_get_confirmed":False,
                    "rights_for_republication_confirmed":False})
    return {"schema_version":1,"purpose":"http_head_metadata_probe_only",
      "coverage":{"url_probes":len(rows),"http_2xx":sum(x.get("http_status",0)//100==2 for x in rows),
        "http_3xx":sum(x.get("http_status",0)//100==3 for x in rows),
        "http_4xx":sum(x.get("http_status",0)//100==4 for x in rows),
        "http_5xx":sum(x.get("http_status",0)//100==5 for x in rows),
        "transport_or_policy_failures":sum(x["status"]!="http_response" for x in rows),
        "full_article_bodies_acquired":0},"probes":rows,
      "limitations":["HEAD is metadata-only and does not establish readable article content.",
       "HEAD 200 does not establish robots permission for GET or rights to extract/republish.",
       "No redirects, credentials, login or paywall bypass; sampling is bounded per hostname."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("rss",type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--max-urls",type=int,default=90)
    a=p.parse_args()
    r=probe(json.loads(a.rss.read_text(encoding="utf-8")),max_urls=a.max_urls)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r["coverage"]))
if __name__=="__main__":main()
