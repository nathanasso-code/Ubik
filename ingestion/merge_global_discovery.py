"""Merge RSS and API discovery before all downstream stages."""
import argparse,json
from pathlib import Path
def merge(rss,api):
 result=dict(rss)
 result['items']=rss.get('items',[])+api.get('items',[])
 result['source_reports']=rss.get('source_reports',[])+api.get('source_reports',[])
 result['coverage']={'configured_sources':len(result['source_reports']),
 'successful_sources':sum(x.get('status')=='ok' and x.get('items',0)>0 for x in result['source_reports']),
 'empty_sources':sum(x.get('items',0)==0 for x in result['source_reports']),
 'observations':len(result['items']),
 'distinct_url_hints':len({x['url'] for x in result['items']})}
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--rss',type=Path,required=True)
 p.add_argument('--api',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();r=merge(json.loads(a.rss.read_text()),json.loads(a.api.read_text()))
 a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(r['coverage']))
if __name__=='__main__':main()
