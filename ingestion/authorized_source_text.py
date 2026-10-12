"""Offline-first source-body capture adapter with explicit network boundary.

Network fetches are disabled here. Feed this adapter independently retrieved,
authorized HTML only. Future HTTP implementation must pin validated DNS IP,
reject private destinations and redirects, enforce robots/access policy.
"""
import argparse,hashlib,html,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

class _ArticleText(HTMLParser):
    BLOCK={"p","h1","h2","h3","h4","li","blockquote"}
    SKIP={"script","style","nav","footer","header","aside","form","noscript","svg"}
    def __init__(self):
        super().__init__(convert_charrefs=True);self.skip_stack=[];self.current=[];self.paragraphs=[];self.active=0
    def handle_starttag(self,tag,attrs):
        if self.skip_stack:
            self.skip_stack.append(tag);return
        if tag in self.SKIP:
            self.skip_stack.append(tag);return
        if tag in self.BLOCK:
            self.active+=1
            if self.active==1:self.current=[]
    def handle_endtag(self,tag):
        if self.skip_stack:
            if tag==self.skip_stack[-1]:self.skip_stack.pop()
            return
        if tag in self.BLOCK and self.active:
            self.active-=1
            if self.active==0:
                value=" ".join("".join(self.current).split())
                if len(value)>=35:self.paragraphs.append(value)
                self.current=[]
    def handle_data(self,data):
        if not self.skip_stack and self.active:self.current.append(data)

def capture_authorized_html(url,html_text,*,access_authorized=False,max_chars=100000):
    parts=urlsplit(url)
    if parts.scheme!="https" or not parts.hostname or parts.username or parts.password or parts.port not in (None,443):
        raise ValueError("Only canonical public HTTPS source URLs without credentials or custom ports are accepted")
    if not access_authorized:raise PermissionError("Source access/usage authorization must be established externally")
    if not isinstance(html_text,str) or len(html_text)>1_000_000:raise ValueError("Invalid or oversized input")
    parser=_ArticleText();parser.feed(html_text)
    text="\n".join(parser.paragraphs)[:max_chars]
    if len(text)<100:raise ValueError("Insufficient accessible article text; do not substitute title")
    return {"url":url,"text":text,"sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "extraction":"offline_authorized_html_v1","access_authorized":True,
            "article_completeness":"unknown","claim_verification":"not_performed",
            "network_requests":0,"paragraph_count":len(parser.paragraphs)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url",required=True);p.add_argument("--html-file",type=Path,required=True)
    p.add_argument("--authorized",action="store_true")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=capture_authorized_html(a.url,a.html_file.read_text(encoding="utf-8"),
                                   access_authorized=a.authorized)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({a.url:result},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"paragraphs":result["paragraph_count"],"characters":len(result["text"]),
                      "network_requests":0}))
if __name__=="__main__":main()
