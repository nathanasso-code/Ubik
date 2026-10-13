"""Persistent, provenance-preserving Ubik discovery ledger.

Stores metadata and access measurements, not copyrighted article bodies.
Conservative URL canonicalization; social hints remain unverified.
"""
import argparse,collections,datetime,json,re
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
TRACK={'utm_source','utm_medium','utm_campaign','utm_term','utm_content','fbclid','gclid','at_medium','at_campaign','traffic_source'}
def canonical(url):
    if not isinstance(url,str):return None
    p=urlsplit(url.strip())
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:return None
    if p.port not in (None,80,443):return None
    host=p.hostname.lower().removeprefix('www.')
    query=urlencode([(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if k.lower() not in TRACK])
    return urlunsplit((p.scheme,host,p.path.rstrip('/') or '/',query,''))
def merge(previous,rss,hybrid,access,*,observed_at=None):
    observed_at=observed_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    docs={d['url']:dict(d) for d in previous.get('documents',[]) if d.get('url')}
    def ensure(url):
        key=canonical(url)
        if not key:return None
        if key not in docs:docs[key]={'url':key,'titles':[],'descriptions':[],
           'rss_sources':[],'social_providers':[],'social_post_urls':[],
           'discovery_origins':[],'original_urls':[],'access_tests':[],
           'first_seen':observed_at}
        return docs[key]
    def add(d,field,values,limit=50):
        d[field]=list(dict.fromkeys(d.get(field,[])+[v for v in values if v]))[:limit]
    for item in rss.get('items',[]):
        d=ensure(item.get('url'))
        if d is None:continue
        add(d,'original_urls',[item.get('url')])
        add(d,'titles',[item.get('title')])
        add(d,'descriptions',[item.get('description')],limit=5)
        add(d,'rss_sources',[item.get('source_id')])
        add(d,'discovery_origins',['publisher_rss'])
        d['last_seen']=observed_at
    for item in hybrid.get('documents',[]):
        d=ensure(item.get('url'))
        if d is None:continue
        add(d,'original_urls',[item.get('url')])
        for key in ('rss_sources','social_providers','social_post_urls','discovery_origins'):
            add(d,key,item.get(key) or [])
        add(d,'titles',item.get('publisher_titles') or [])
        d['last_seen']=observed_at
    for item in access.get('probes',[]):
        d=ensure(item.get('url'))
        if d is None:continue
        evidence={k:item.get(k) for k in ('status','content_tier','article_element_chars','page_visible_chars',
          'page_visible_words','metadata_description_chars','article_text_sha256','robots_allowed',
          'complete_article_verified','republication_rights_verified','error_type') if k in item}
        evidence['tested_at']=observed_at
        signature=(evidence.get('status'),evidence.get('content_tier'),evidence.get('article_text_sha256'))
        old=d.get('access_tests',[])
        if not any((x.get('status'),x.get('content_tier'),x.get('article_text_sha256'))==signature for x in old):
            d['access_tests']=(old+[evidence])[-10:]
    return {'schema_version':1,'purpose':'persistent_discovery_ledger',
      'generated_at':observed_at,'documents':list(docs.values()),
      'coverage':{'distinct_urls':len(docs),
         'with_social_discovery':sum('social_shared_url' in x.get('discovery_origins',[]) for x in docs.values()),
         'with_get_measurement':sum(bool(x.get('access_tests')) for x in docs.values()),
         'with_substantial_article_text_evidence':sum(any(t.get('content_tier')=='substantial_article_text_accessible' for t in x.get('access_tests',[])) for x in docs.values())},
      'limitations':['GET article-tag text is not proof of full-text completeness.',
        'Social shares are discovery hints, not confirmed editorial sources.',
        'Metadata retained across runs; editorial approval and event grouping are separate stages.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--previous',type=Path)
    p.add_argument('--rss',type=Path,required=True);p.add_argument('--hybrid',type=Path,required=True)
    p.add_argument('--access',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();read=lambda path:json.loads(path.read_text()) if path and path.exists() else {}
    result=merge(read(a.previous),read(a.rss),read(a.hybrid),read(a.access))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['coverage']))
if __name__=='__main__':main()
