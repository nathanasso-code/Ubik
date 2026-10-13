"""Mandatory multi-channel coverage audit for every global Ubik refresh."""
import argparse,json
from pathlib import Path
REQUIRED={'editorial_rss':{'bbc-world','guardian-world','nature'},
          'scientific_preprints':{'arxiv-cs-ai','arxiv-cs-lg'},
          'open_collaborative_news':{'wikinews-en','wikinews-it'},
          'public_institutions':{'eea-news'}}
def audit(registry,snapshot,*,social=None):
    sources={s['id']:s for s in registry.get('sources',[]) if s.get('enabled')}
    reports={r['source_id']:r for r in snapshot.get('source_reports',[])}
    channels={}
    for channel,ids in REQUIRED.items():
        entries=[]
        for source_id in sorted(ids):
            config=sources.get(source_id)
            observed=reports.get(source_id)
            entries.append({'source_id':source_id,
              'configured':config is not None,'attempted':observed is not None,
              'status':observed.get('status') if observed else 'not_attempted',
              'items':observed.get('items',0) if observed else 0})
        channels[channel]=entries
    return {'schema_version':1,'purpose':'global_refresh_coverage_contract',
      'channels':channels,'social_discovery_present':bool(social and social.get('documents')),
      'configured_sources':len(sources),
      'sources_attempted':len(reports),
      'missing_required':[x['source_id'] for group in channels.values() for x in group if not x['configured'] or not x['attempted']],
      'failed_required':[x['source_id'] for group in channels.values() for x in group if x['status']=='error'],
      'limitations':['A source being attempted does not imply successful acquisition.',
        'Registry coverage is extensible, not a claim of exhaustive global information.',
        'Social channel success requires independent examination of social reports.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--registry',type=Path,required=True)
    p.add_argument('--rss',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=audit(json.loads(a.registry.read_text()),json.loads(a.rss.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'attempted':r['sources_attempted'],'missing':r['missing_required'],'failed':r['failed_required']}))
    if r['missing_required']:raise SystemExit('Mandatory channels missing from global refresh')
if __name__=='__main__':main()
