"""Bounded live GET evidence for article text accessibility; not publication rights.

Per-host sample, robots.txt review, pinned HTTPS, no redirects or bypasses.
Outputs extracted text lengths and hashes, not full copyrighted bodies.
"""
import argparse,collections,hashlib,html,json,re,time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import fetch_one,USER_AGENT

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__();self.depth=0;self.skip=0;self.text=[];self.in_article=0;self.article=[];self.meta=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('script','style','nav','footer','header','aside','noscript','svg'):self.skip+=1
        if tag=='article':self.in_article+=1
        if tag=='meta' and (a.get('name','').lower() in ('description','twitter:description') or a.get('property','').lower() in ('og:description','article:description')):
            self.meta.append(a.get('content',''))
        if tag in ('p','h1','h2','h3','li'):self.text.append(' ');self.article.append(' ')
    def handle_endtag(self,tag):
        if tag in ('script','style','nav','footer','header','aside','noscript','svg'):self.skip=max(0,self.skip-1)
        if tag=='article':self.in_article=max(0,self.in_article-1)
    def handle_data(self,data):
        if self.skip:return
        t=data.strip()
        if t:self.text.append(t+' ')
        if t and self.in_article:self.article.append(t+' ')

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
            'body_fetched':True,'complete_article_verified':False,
            'robots_allowed':True,'republication_rights_verified':False}
    except (OSError,TimeoutError,ValueError,PermissionError) as e:
        return {'status':'get_failed','error_type':type(e).__name__,
                'error_message':str(e)[:100]}

def probe(snapshot,*,max_urls=100,per_host=5,checker=inspect):
    selected=[];count=collections.Counter();seen=set()
    for x in snapshot.get('items',[]):
        u=x.get('url','')
        if not isinstance(u,str) or u in seen:continue
        host=urlsplit(u).hostname
        if not host or count[host]>=per_host:continue
        seen.add(u);count[host]+=1
        selected.append({'url':u,'source_id':x.get('source_id'),'publisher':x.get('publisher')})
        if len(selected)>=max_urls:break
    for row in selected:row.update(checker(row['url']))
    summary=collections.Counter(x.get('content_tier') or x['status'] for x in selected)
    return {'schema_version':1,'purpose':'live_get_text_accessibility_sample',
      'coverage':{'tested_urls':len(selected),'outcomes':dict(summary),
       'get_success':sum(x['status']=='get_success' for x in selected),
       'article_text_detected':sum(x.get('content_tier')=='substantial_article_text_accessible' for x in selected),
       'full_articles_completeness_verified':0},
      'probes':selected,'limitations':[
       'Sampling per hostname; untested URLs remain unknown.',
       'Article-tag text is evidence of substantial accessible text, not verified completeness.',
       'Visible page text can include boilerplate and does not establish article access.',
       'No paywall bypass, redirects, login or copyrighted article text stored.',
       'Publisher robots policies are checked before article GET; inaccessible robots lead to abstention.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('rss',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-urls',type=int,default=100);a=p.parse_args()
    result=probe(json.loads(a.rss.read_text()),max_urls=a.max_urls)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['coverage']))
if __name__=='__main__':main()
