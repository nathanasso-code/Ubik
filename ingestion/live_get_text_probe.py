"""Bounded live GET evidence for article text accessibility; not publication rights.

Per-host sample, robots.txt review, pinned HTTPS, no redirects or bypasses.
Outputs extracted text lengths and hashes, not full copyrighted bodies.
"""
import argparse,collections,hashlib,html,json,re,time,random
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import fetch_one,USER_AGENT

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__();self.depth=0;self.skip=0;self.text=[];self.in_article=0;self.article=[];self.meta=[];self.jsonld_blocks=[];self.in_jsonld=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('type','').lower()=='application/ld+json':
            self.in_jsonld=True
            self.jsonld_blocks.append('')
        if tag in ('script','style','nav','footer','header','aside','noscript','svg'):self.skip+=1
        if tag=='article':self.in_article+=1
        if tag=='meta' and (a.get('name','').lower() in ('description','twitter:description') or a.get('property','').lower() in ('og:description','article:description')):
            self.meta.append(a.get('content',''))
        if tag in ('p','h1','h2','h3','li'):self.text.append(' ');self.article.append(' ')
    def handle_endtag(self,tag):
        if tag in ('script','style','nav','footer','header','aside','noscript','svg'):self.skip=max(0,self.skip-1)
        if tag=='article':self.in_article=max(0,self.in_article-1)
        if tag=='script':self.in_jsonld=False
    def handle_data(self,data):
        if self.in_jsonld and self.jsonld_blocks:self.jsonld_blocks[-1]+=data
        if self.skip:return
        t=data.strip()
        if t:self.text.append(t+' ')
        if t and self.in_article:self.article.append(t+' ')

def jsonld_article_lengths(blocks):
    lengths=[]
    def visit(node,depth=0):
        if depth>8:return
        if isinstance(node,list):
            for item in node[:40]:visit(item,depth+1)
        elif isinstance(node,dict):
            types=node.get('@type',[])
            if isinstance(types,str):types=[types]
            if isinstance(types,list) and any(t in ('Article','NewsArticle','ScholarlyArticle') for t in types):
                body=node.get('articleBody')
                if isinstance(body,str):lengths.append(len(' '.join(body.split())))
            if '@graph' in node:visit(node['@graph'],depth+1)
    for block in blocks[:20]:
        if len(block)>200000:continue
        try:visit(json.loads(block))
        except (ValueError,TypeError,RecursionError):continue
    return lengths

def inspect(url,*,fetch=fetch_one):
    p=urlsplit(url);host=(p.hostname or '').lower()
    if p.scheme!='https' or not host or p.username or p.password or p.port not in (None,443):
        return {'status':'invalid_url'}
    try:
        try:robots=fetch('https://'+host+'/robots.txt',{host},timeout=5)
        except ValueError as e:
            return {'status':'robots_unavailable','error_type':type(e).__name__}
        parser=RobotFileParser();parser.parse(robots.splitlines())
        if not parser.can_fetch(USER_AGENT,url):return {'status':'robots_disallowed'}
        raw=fetch(url,{host},timeout=7)
        ext=Extractor();ext.feed(raw)
        article=' '.join(''.join(ext.article).split())
        visible=' '.join(''.join(ext.text).split())
        meta=' '.join(' '.join(ext.meta).split())
        structured=jsonld_article_lengths(ext.jsonld_blocks)
        # Only article-tag text is treated as strong evidence. Full text is never assumed.
        evidence=article if len(article)>=250 else visible
        words=len(evidence.split())
        if len(article)>=1200 and len(article.split())>=180:
            tier='substantial_article_text_accessible'
        elif words>=180 and len(evidence)>=1200:
            tier='substantial_page_text_unverified_article'
        elif len(meta)>=160:tier='long_abstract_metadata'
        elif len(meta)>=60:tier='short_abstract_metadata'
        else:tier='insufficient_text_evidence'
        return {'status':'get_success','content_tier':tier,
            'article_element_chars':len(article),'page_visible_chars':len(visible),
            'page_visible_words':len(visible.split()),'metadata_description_chars':len(meta),
            'article_text_sha256':hashlib.sha256(article.encode()).hexdigest() if article else None,
            'structured_article_max_chars':max(structured,default=0),
            'structured_article_candidates':len(structured),
            'body_fetched':True,'complete_article_verified':False,
            'robots_allowed':True,'republication_rights_verified':False}
    except (OSError,TimeoutError,ValueError,PermissionError) as e:
        return {'status':'get_failed','error_type':type(e).__name__,
                'error_message':str(e)[:100]}

def select_urls(snapshot, *, max_urls=100, per_host=5, seed=42, method="stratified"):
    """Reproducible publisher-stratified sample, independent of feed ordering."""
    if max_urls < 1 or per_host < 1:
        raise ValueError("Sample and host budgets must be positive")
    if method not in ("stratified", "ordered"):
        raise ValueError("Unknown selection method")
    buckets=collections.defaultdict(list);seen=set()
    for x in snapshot.get("items",[]):
        u=x.get("url","")
        if not isinstance(u,str) or u in seen:continue
        p=urlsplit(u)
        if p.scheme!="https" or not p.hostname:continue
        seen.add(u)
        buckets[p.hostname.lower()].append({"url":u,"source_id":x.get("source_id"),"publisher":x.get("publisher")})
    if method=="ordered":
        selected=[];counts=collections.Counter()
        for x in snapshot.get("items",[]):
            u=x.get("url","");host=urlsplit(u).hostname if isinstance(u,str) else None
            if not host or counts[host]>=per_host or u not in seen:continue
            selected.append(next(r for r in buckets[host.lower()] if r["url"]==u))
            counts[host]+=1;seen.remove(u)
            if len(selected)>=max_urls:break
        return selected
    rng=random.Random(seed)
    for host in sorted(buckets):
        rng.shuffle(buckets[host])
    hosts=sorted(buckets)
    rng.shuffle(hosts)
    selected=[];counts=collections.Counter()
    while len(selected)<max_urls:
        progressed=False
        for host in hosts:
            if len(selected)>=max_urls:break
            if counts[host]>=per_host or not buckets[host]:continue
            selected.append(buckets[host].pop())
            counts[host]+=1;progressed=True
        if not progressed:break
    return selected

def probe(snapshot,*,max_urls=100,per_host=5,checker=inspect,seed=42,method="stratified"):
    selected=select_urls(snapshot,max_urls=max_urls,per_host=per_host,seed=seed,method=method)
    for row in selected:row.update(checker(row["url"]))
    summary=collections.Counter(x.get("content_tier") or x["status"] for x in selected)
    return {"schema_version":2,"purpose":"live_get_text_accessibility_sample",
      "sampling":{"method":method,"seed":seed if method=="stratified" else None,
                  "per_host_limit":per_host,"max_urls":max_urls},
      "coverage":{"tested_urls":len(selected),"outcomes":dict(summary),
       "get_success":sum(x["status"]=="get_success" for x in selected),
       "article_text_detected":sum(x.get("content_tier")=="substantial_article_text_accessible" for x in selected),
       "full_articles_completeness_verified":0},
      "probes":selected,"limitations":[
       "Publisher-stratified bounded sample, not a probability-weighted estimate of all news.",
       "Article-tag text is evidence of substantial accessible text, not verified completeness.",
       "Visible page text can include boilerplate and does not establish article access.",
       "No paywall bypass, redirects, login or copyrighted article text stored.",
       "Publisher robots policies are checked before article GET; inaccessible robots lead to abstention."]}

def main():
    p=argparse.ArgumentParser();p.add_argument('rss',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-urls',type=int,default=100)
    p.add_argument('--per-host',type=int,default=5)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--method',choices=('stratified','ordered'),default='stratified')
    a=p.parse_args()
    result=probe(json.loads(a.rss.read_text()),max_urls=a.max_urls,per_host=a.per_host,seed=a.seed,method=a.method)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['coverage']))
if __name__=='__main__':main()
