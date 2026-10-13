"""Global public API metadata collection, separate from RSS."""
import argparse,json,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
A='{http://www.w3.org/2005/Atom}'
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'UbikResearchBot/0.1 (ubik.research@gmail.com)'})
 with urllib.request.urlopen(req,timeout=12) as r:return r.read(900000)
def collect():
 sources=[
 ('arxiv','https://export.arxiv.org/api/query?search_query=all%3Aclimate&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending'),
 ('europepmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=OPEN_ACCESS%3AY&format=json&pageSize=25'),
 ('wikinews-en','https://en.wikinews.org/w/api.php?action=query&list=allpages&apnamespace=0&aplimit=25&format=json'),
 ('wikinews-it','https://it.wikinews.org/w/api.php?action=query&list=allpages&apnamespace=0&aplimit=25&format=json')]
 items=[];reports=[]
 for name,url in sources:
  try:
   raw=get(url);found=[]
   if name=='arxiv':
    for e in ET.fromstring(raw).findall(A+'entry'):
     link=e.findtext(A+'id') or ''
     if link.startswith('https://arxiv.org/abs/'):
      found.append({'url':link,'title':' '.join((e.findtext(A+'title') or '').split()),'description':' '.join((e.findtext(A+'summary') or '').split())})
   elif name=='europepmc':
    for e in json.loads(raw).get('resultList',{}).get('result',[]):
     if e.get('pmcid'):found.append({'url':'https://europepmc.org/articles/'+e['pmcid'],'title':e.get('title',''),'description':e.get('authorString','')})
   else:
    host='en.wikinews.org' if name.endswith('en') else 'it.wikinews.org'
    for e in json.loads(raw).get('query',{}).get('allpages',[]):
     found.append({'url':'https://'+host+'/wiki/'+urllib.parse.quote(e['title'].replace(' ','_')),'title':e['title'],'description':''})
   for d in found:d.update({'source_id':name,'topic_ids':[],'discovery_mode':'global_api_unassigned'})
   items.extend(found);reports.append({'source_id':name,'status':'ok' if found else 'empty','items':len(found)})
  except Exception as e:reports.append({'source_id':name,'status':'error','error_type':type(e).__name__,'items':0})
 return {'schema_version':1,'purpose':'global_api_document_discovery','items':items,'source_reports':reports,
  'coverage':{'configured_sources':len(sources),'observations':len(items),'nonempty_sources':sum(x['items']>0 for x in reports)}}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 d=collect();a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(d['coverage']))
if __name__=='__main__':main()
