"""Bounded Wikinews article-text acquisition for semantic analysis.

Only public MediaWiki pages from an explicit host allowlist. Full text stays in
RAM and is never saved without separate document-specific rights verification.
"""
import argparse,hashlib,html,json,re,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path
HOSTS={'en.wikinews.org','it.wikinews.org'}
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in {'script','style','nav','footer','header','aside'}:self.skip+=1
  if tag in {'p','h1','h2','li'}:self.parts.append(' ')
 def handle_endtag(self,tag):
  if tag in {'script','style','nav','footer','header','aside'}:self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip:self.parts.append(data+' ')
def fetch_page(url,*,timeout=10):
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or p.hostname not in HOSTS or p.username or p.password:raise ValueError('Unapproved wiki host')
 title=urllib.parse.unquote(p.path.removeprefix('/wiki/'))
 if not p.path.startswith('/wiki/') or not title:raise ValueError('Not a wiki article')
 api='https://'+p.hostname+'/w/api.php?'+urllib.parse.urlencode({
   'action':'parse','page':title,'prop':'text','format':'json','formatversion':'2'})
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):raise ValueError('Redirect blocked')
 opener=urllib.request.build_opener(NoRedirect)
 with opener.open(urllib.request.Request(api,headers={'User-Agent':'UbikResearchBot/0.1 (ubik.research@gmail.com)'}),timeout=timeout) as response:
  if response.status!=200:raise ValueError('Non-200')
  data=response.read(750001)
  if len(data)>750000:raise ValueError('Response too large')
 obj=json.loads(data)
 if 'error' in obj or 'parse' not in obj:raise ValueError('MediaWiki parse error')
 parser=Text();parser.feed(obj['parse']['text'])
 return ' '.join(''.join(parser.parts).split())
def acquire(snapshot,*,limit=12,fetch=fetch_page):
 items=[x for x in snapshot.get('items',[]) if urllib.parse.urlsplit(x.get('url','')).hostname in HOSTS]
 seen=set();outcomes=[]
 for item in items:
  url=item['url']
  if url in seen:continue
  seen.add(url)
  if len(outcomes)>=limit:break
  try:
   text=fetch(url)
   outcomes.append({'url':url,'status':'text_acquired_in_memory' if len(text)>=500 else 'short_text',
    'characters':len(text),'words':len(text.split()),'sha256':hashlib.sha256(text.encode()).hexdigest(),
    'stored':False,'reuse_rights_verified':False})
  except (OSError,ValueError,TimeoutError,KeyError) as exc:
   outcomes.append({'url':url,'status':'fetch_failed','error_type':type(exc).__name__})
 return {'schema_version':1,'purpose':'wikinews_full_text_access_pilot',
  'coverage':{'wiki_links_in_snapshot':len(items),'attempted':len(outcomes),
   'substantial_text_in_memory':sum(x.get('characters',0)>=500 for x in outcomes)},
  'outcomes':outcomes,'full_text_persisted':False,
  'limitations':['Text extraction alone does not verify republication rights.',
   'Only lengths and hashes are persisted; extracted text stays in RAM.',
   'Article-level license and attribution review is needed before storage.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--rss',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=acquire(json.loads(a.rss.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['coverage']))
if __name__=='__main__':main()
