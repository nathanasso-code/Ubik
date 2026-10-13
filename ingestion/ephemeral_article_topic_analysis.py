"""Ephemeral article text classification: no HTML or article text written to disk."""
import argparse,collections,json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from ingestion.approved_https_fetch import fetch_one,USER_AGENT
from ingestion.live_get_text_probe import Extractor
from ingestion.dual_topic_router import route
from ingestion.topic_evidence_qualification import qualify
from ingestion.semantic_topic_router import MODEL

def ephemeral_analysis(ledger,catalog,embed,*,max_urls=40,per_host=3,fetch=fetch_one):
    selected=[];counts=collections.Counter();outcomes=[]
    for d in ledger.get('documents',[]):
        url=d.get('url','');host=urlsplit(url).hostname
        if not host or urlsplit(url).scheme!='https' or counts[host]>=per_host:continue
        counts[host]+=1;selected.append(d)
        if len(selected)>=max_urls:break
    candidates=[]
    for d in selected:
        url=d['url'];host=urlsplit(url).hostname
        try:
            robots=fetch('https://'+host+'/robots.txt',{host},timeout=5)
            parser=RobotFileParser();parser.parse(robots.splitlines())
            if not parser.can_fetch(USER_AGENT,url):
                outcomes.append({'url':url,'status':'robots_disallowed'});continue
            raw=fetch(url,{host},timeout=7)
            extractor=Extractor();extractor.feed(raw)
            article=' '.join(''.join(extractor.article).split())
            if len(article)<1200 or len(article.split())<180:
                outcomes.append({'url':url,'status':'insufficient_article_text','article_chars':len(article)});continue
            # In-memory only: content flows into embeddings, not output artifacts.
            title=(d.get('titles') or [''])[0]
            candidates.append({'url':url,'title':title,'description':article[:8000],
                'routing_eligible':True,'evidence_tier':'ephemeral_article_text'})
            outcomes.append({'url':url,'status':'analyzed_ephemerally','article_chars':len(article)})
        except (ValueError,OSError,TimeoutError,PermissionError) as e:
            outcomes.append({'url':url,'status':'fetch_failed','error_type':type(e).__name__})
    result=route({'documents':candidates},catalog,embed)
    return {'schema_version':1,'purpose':'ephemeral_full_article_semantic_routing',
        'coverage':{'attempted':len(selected),'ephemeral_article_inputs':len(candidates),
            **result['coverage']},'outcomes':outcomes,
        'curated_proposals':result['curated_proposals'],
        'abstentions':result['abstentions'],
        'emergent_keyword_candidates':result['emergent_keyword_candidates'],
        'article_text_retained':False,
        'limitations':['Fetched HTML and article text are not serialized or persisted.',
          'Embedding model may process the text in RAM; no third-party text API is used.',
          'Rights to reproduce article text are not inferred from public access.',
          'Article element text is not necessarily complete article content.',
          'Semantic assignments remain review-only.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--catalog',type=Path,default=Path('data/catalog.json'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-urls',type=int,default=40)
    a=p.parse_args()
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer(MODEL)
    result=ephemeral_analysis(json.loads(a.ledger.read_text()),json.loads(a.catalog.read_text()),
       lambda texts:model.encode(texts,normalize_embeddings=True,batch_size=16).tolist(),max_urls=a.max_urls)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['coverage']))
if __name__=='__main__':main()
