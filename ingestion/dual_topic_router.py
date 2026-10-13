"""Dual-track topic routing: curated Ubik catalog and review-only emergent themes."""
import argparse,collections,json,re
from pathlib import Path
from ingestion.semantic_topic_router import existing_topics,_cos,MODEL
STOP=set('about after their from with this that have been were will into over under news says said more also when where what which while because come just than only della delle degli anche sono alla allo nelle negli come dopo prima sulle sulla degli stato stati dalla dalla sono questo questa quello degli'.split())
def terms(text):
    return {x for x in re.findall(r'[^\W\d_]{4,}',text.casefold(),re.UNICODE) if x not in STOP}
def route(quality,catalog,embed,*,threshold=0.79,margin=0.045):
    topics=existing_topics(catalog)
    docs=[x for x in quality.get('documents',[]) if x.get('routing_eligible')]
    texts=['query: '+t['context'] for t in topics]+[
        'passage: '+(d['title']+'; '+d['description'])[:1800] for d in docs]
    vectors=embed(texts) if texts else []
    if len(vectors)!=len(texts):raise ValueError('Embedding length mismatch')
    proposals=[];abstained=[]
    for i,d in enumerate(docs):
        ranked=sorted([(_cos(vectors[len(topics)+i],vectors[j]),t)
                       for j,t in enumerate(topics)],key=lambda x:-x[0])
        top=ranked[0] if ranked else None
        second=ranked[1][0] if len(ranked)>1 else 0
        # Minimal lexical anchor to reduce generic semantic false positives.
        overlap=sorted(terms(d['title']+' '+d['description']) & terms(top[1]['context'])) if top else []
        if top and top[0]>=threshold and (len(ranked)==1 or top[0]-second>=margin) and overlap:
            proposals.append({'url':d['url'],'topic_id':top[1]['id'],'topic_title':top[1]['title'],
                'similarity':round(top[0],4),'margin':round(top[0]-second,4),
                'lexical_anchors':overlap[:10],'evidence_tier':d['evidence_tier'],
                'status':'review_candidate_not_verified'})
        else:
            abstained.append({'url':d['url'],'reason':'low_score_ambiguity_or_missing_anchor',
               'best_topic':top[1]['id'] if top else None,'best_score':round(top[0],4) if top else None})
    # Emergent topics: descriptive frequent terms in documents not confidently routed;
    # never automatically create/publish topics.
    by_url={d['url']:d for d in docs}
    buckets=collections.defaultdict(list)
    for item in abstained:
        d=by_url[item['url']]
        for term in terms(d['title']):
            buckets[term].append(d['url'])
    emergent=[{'keyword':term,'document_urls':list(dict.fromkeys(urls))[:20],
       'document_count':len(set(urls)),'status':'emergent_keyword_candidate_not_topic'}
       for term,urls in buckets.items() if len(set(urls))>=3]
    emergent.sort(key=lambda x:(-x['document_count'],x['keyword']))
    return {'schema_version':1,'model':MODEL,'purpose':'curated_and_emergent_topic_proposals',
      'coverage':{'eligible_documents':len(docs),'curated_proposals':len(proposals),
        'curated_abstentions':len(abstained),'emergent_keyword_candidates':len(emergent)},
      'curated_proposals':proposals,'abstentions':abstained,
      'emergent_keyword_candidates':emergent[:100],
      'limitations':['Embedding scores are uncalibrated and thresholds require labeled evaluation.',
        'Lexical anchor is a conservative heuristic, not proof of relevance.',
        'Emergent keywords are NOT event clusters or created topics.',
        'Only stored title and description are embedded; article bodies were not retained.',
        'All proposals require editorial verification.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--quality',type=Path,required=True)
    p.add_argument('--catalog',type=Path,default=Path('data/catalog.json'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--live-model',action='store_true')
    a=p.parse_args()
    if not a.live_model:raise SystemExit('Specify --live-model for actual inference')
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer(MODEL)
    result=route(json.loads(a.quality.read_text()),json.loads(a.catalog.read_text()),
       lambda xs:model.encode(xs,normalize_embeddings=True,batch_size=16).tolist())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['coverage']))
if __name__=='__main__':main()
