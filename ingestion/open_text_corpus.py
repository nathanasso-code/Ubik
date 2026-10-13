"""Fetch a bounded, open-license Wikinews corpus for Ubik's real-text experiment.

Wikinews articles are generally CC BY 2.5; verify page-specific attribution,
copyright exceptions and media before any republication. Text is processed for
research, never published verbatim. API-only, no login, no paywall bypass.
"""
import argparse,hashlib,html,json,re,time,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path

API="https://en.wikinews.org/w/api.php"
USER_AGENT="UbikResearchBot/0.1 (research; ubik.research@gmail.com)"
class PlainText(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","table","sup"):self.skip+=1
        if tag in ("p","li","h2","h3") and not self.skip:self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in ("script","style","table","sup") and self.skip:self.skip-=1
        if tag in ("p","li","h2","h3") and not self.skip:self.parts.append("\n")
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
def api(params,*,transport=None):
    params=dict(params,format="json",formatversion="2")
    url=API+"?"+urllib.parse.urlencode(params)
    if transport:return transport(params)
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=12) as response:
        if response.status!=200:raise RuntimeError("API error")
        data=response.read(2_000_001)
        if len(data)>2_000_000:raise RuntimeError("Oversized API response")
        return json.loads(data)
def collect(*,limit=60,transport=None):
    if not 1<=limit<=120:raise ValueError("Invalid article budget")
    results=[];seen=set();continuation={}
    while len(results)<limit:
        query={"action":"query","list":"categorymembers","cmtitle":"Category:Published",
               "cmtype":"page","cmlimit":min(50,limit-len(results)+15),
               "cmsort":"timestamp","cmdir":"desc"}
        query.update(continuation)
        listing=api(query,transport=transport)
        members=listing.get("query",{}).get("categorymembers",[])
        for entry in members:
            if len(results)>=limit:break
            pageid=entry.get("pageid");title=entry.get("title","")
            if not isinstance(pageid,int) or pageid in seen or not title or title.startswith(("Category:","Template:")):continue
            seen.add(pageid)
            try:
                doc=api({"action":"parse","pageid":pageid,"prop":"text|displaytitle|revid"},transport=transport).get("parse",{})
                markup=doc.get("text","")
                if not isinstance(markup,str):continue
                parser=PlainText();parser.feed(markup)
                text="\n".join(" ".join(p.split()) for p in "".join(parser.parts).splitlines() if len(p.strip())>25)
                if len(text)<400:continue
                url="https://en.wikinews.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe="/:()")
                results.append({"url":url,"title":html.unescape(title),"publisher":"Wikinews",
                                "source_pageid":pageid,"source_revision":doc.get("revid"),
                                "text":text[:35000],"sha256":hashlib.sha256(text[:35000].encode()).hexdigest(),
                                "license_note":"Wikinews generally CC BY 2.5; page-specific review required",
                                "license_verified_per_page":False,
                                "body_source":"MediaWiki parse API","published":False})
            except (ValueError,RuntimeError,urllib.error.URLError,TimeoutError) as error:
                continue
        continuation=listing.get("continue",{})
        if not continuation or not members:break
        if not transport:time.sleep(0.4)
    return {"schema_version":1,"requested":limit,"acquired":len(results),
            "source":"Wikinews MediaWiki public API","documents":results,
            "publication_approved":False,
            "limitations":["Category membership and date coverage are not guaranteed.",
                           "License and third-party quotations require page-specific review.",
                           "Extracted HTML may contain navigation or other non-article text."]}
def main():
    p=argparse.ArgumentParser();p.add_argument("--limit",type=int,default=60)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();r=collect(limit=a.limit)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"requested":r["requested"],"acquired":r["acquired"]}))
if __name__=="__main__":main()
