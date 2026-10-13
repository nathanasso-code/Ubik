"""Evidence-tier qualification for document-level topic routing."""
import argparse,collections,json,re
from pathlib import Path
def assess(doc):
    descriptions=doc.get('descriptions') or []
    description=max((str(x) for x in descriptions),key=len,default='')
    title=max((str(x) for x in doc.get('titles',[]) or []),key=len,default='')
    access=doc.get('access_tests') or []
    strong=any(x.get('content_tier')=='substantial_article_text_accessible' for x in access)
    page=any(x.get('content_tier')=='substantial_page_text_unverified_article' for x in access)
    length=len(' '.join(description.split()))
    if strong:tier='article_text_evidence'
    elif length>=160:tier='long_description'
    elif length>=60:tier='short_description'
    elif page:tier='page_text_unverified'
    else:tier='metadata_only'
    # Semantic routing uses only stored title/description; body GET was measured, not retained.
    eligible=bool(title and length>=60)
    return {'url':doc['url'],'title':title,'description':description[:1600],
        'evidence_tier':tier,'semantic_input_chars':len(title)+length,
        'routing_eligible':eligible,'reason':'title_and_description' if eligible else 'insufficient_stored_text',
        'social_providers':doc.get('social_providers',[]),'rss_sources':doc.get('rss_sources',[]),
        'article_body_retained':False}
def qualify(ledger):
    rows=[assess(d) for d in ledger.get('documents',[])]
    return {'schema_version':1,'purpose':'topic_routing_input_quality',
        'coverage':{'documents':len(rows),'routing_eligible':sum(x['routing_eligible'] for x in rows),
        'evidence_tiers':dict(collections.Counter(x['evidence_tier'] for x in rows))},
        'documents':rows,'limitations':['GET body text is not retained, so it cannot currently contribute to semantic embeddings.',
        'Sufficient text for classification is not proof of topical correctness.',
        'A social URL without title and description must abstain.']}
def main():
    p=argparse.ArgumentParser();p.add_argument('ledger',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=qualify(json.loads(a.ledger.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(r['coverage']))
if __name__=='__main__':main()
