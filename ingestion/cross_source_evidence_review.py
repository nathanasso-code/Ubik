"""Conservative evidence sentence relations for editorial review, not NLI."""
import argparse,json,re,collections
from pathlib import Path
WORDS=re.compile(r'[^\W\d_]{4,}',re.U)
STOP=set('that this with from were have about study result results their which after before among between these those they into showed found della delle degli sono alla anche questo questa nello nella come dopo prima per gli una uno degli'.split())
NEG=re.compile(r'\b(?:not|no|never|without|non|nessun[oa]?|absence|absent)\b',re.I)
def terms(s):return set(w for w in WORDS.findall(s.casefold()) if w not in STOP)
def relate(a,b):
 x=terms(a);y=terms(b)
 shared=x&y;similar=len(shared)/max(1,len(x|y))
 if len(shared)<3 or similar<.20:return {'relation':'insufficient_overlap','score':round(similar,3),'anchors':sorted(shared)[:8]}
 # Polarity differences are only a review flag, not verified contradiction.
 if bool(NEG.search(a))!=bool(NEG.search(b)):
  label='possible_polarity_difference_review'
 elif similar>=.65:label='possible_redundancy_review'
 else:label='related_claims_review'
 return {'relation':label,'score':round(similar,3),'anchors':sorted(shared)[:8]}
def compare(adequacy,*,max_pairs=1000):
 docs=[x for x in adequacy.get('documents',[]) if x.get('adequacy',{}).get('level')=='A']
 pairs=[]
 for i,a in enumerate(docs):
  for b in docs[i+1:]:
   if a.get('url')==b.get('url') or a.get('source_id')==b.get('source_id'):continue
   aa=a['adequacy'].get('claim_candidates',[]);bb=b['adequacy'].get('claim_candidates',[])
   for ca in aa:
    for cb in bb:
     rel=relate(ca['evidence_excerpt'],cb['evidence_excerpt'])
     if rel['relation']!='insufficient_overlap':
      pairs.append({'source_a':a['url'],'source_b':b['url'],
       'evidence_a':ca['evidence_excerpt'],'evidence_b':cb['evidence_excerpt'],
       **rel,'status':'unverified_editorial_candidate'})
   if len(pairs)>=max_pairs:break
  if len(pairs)>=max_pairs:break
 return {'schema_version':1,'purpose':'cross_source_evidence_sentence_review',
 'coverage':{'level_A_documents':len(docs),'candidate_relations':len(pairs[:max_pairs])},
 'relations':pairs[:max_pairs],
 'limitations':['Token overlap is not entailment or contradiction detection.',
 'Same-event identity requires entity, time, location and claim-level validation.',
 'No automatic publication or fact-checking.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--adequacy',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=compare(json.loads(a.adequacy.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['coverage']))
if __name__=='__main__':main()
