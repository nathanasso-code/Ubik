"""Ubik claim representation v1: source-grounded, abstention-first.

Structural extraction is intentionally conservative; no fabricated entities.
A candidate is NOT a verified claim and no semantic entailment is asserted.
"""
import argparse,hashlib,json,re
from pathlib import Path
from ingestion.abstract_evidence_adequacy import qualify
NUM=re.compile(r'(?<!\w)(\d+(?:[.,]\d+)?)\s*(%|percent|patients|participants|cases|years|months|weeks|mg|kg|pazienti|settimane|mesi|anni)?',re.I)
NEG=re.compile(r'\b(?:not|no|never|without|non|nessun[oa]?)\b',re.I)
UNC=re.compile(r'\b(?:may|might|could|suggests?|possible|possibly|potrebbe|possibile|suggerisce)\b',re.I)
PATTERNS=[
 ('decrease',re.compile(r'\b(?:reduced?|reduction|decreased?|declined?|lowered?|ridott[oaie]|riduzione|diminuit[oaie]|diminuzione)\b',re.I)),
 ('increase',re.compile(r'\b(?:increased?|increase|raised?|rose|growth|aumentat[oaie]|aumento|crescit[ae])\b',re.I)),
 ('association',re.compile(r'\b(?:associated?|correlated?|linked?|associat[oaie]|correlat[oaie])\b',re.I)),
 ('finding',re.compile(r'\b(?:found|showed|demonstrated|reported|rilevat[oaie]|dimostrat[oaie]|riscontrat[oaie])\b',re.I))]
def fingerprint(s):return hashlib.sha256(' '.join(s.casefold().split()).encode()).hexdigest()
def extract_sentence(sentence,*,url,source_id,kind,idx,level,retain_excerpt=True):
 clean=' '.join(sentence.split())
 if len(clean.split())<7:return None
 hits=[(m.start(),label,m) for label,pat in PATTERNS for m in pat.finditer(clean)]
 if not hits:return None
 pos,relation,match=min(hits,key=lambda x:x[0])
 numbers=[{'value':m.group(1),'unit':m.group(2)} for m in NUM.finditer(clean)][:12]
 # Do not pretend grammatical subject/object can be inferred reliably by regex.
 return {'id':fingerprint(url+'|'+str(idx)+'|'+clean)[:24],
  'document_url':url,'source_id':source_id,'evidence_kind':kind,
  'evidence_level':level,'sentence_index':idx,'evidence_sha256':fingerprint(clean),
  'evidence_excerpt':clean[:160] if retain_excerpt else None,
  'subject':None,'predicate_candidate':relation,'object':None,
  'quantities':numbers,'polarity':'negative_marker_present' if NEG.search(clean) else 'unmarked',
  'modality':'hedged' if UNC.search(clean) else 'unmarked',
  'population':None,'timeframe':None,'location':None,'study_id':None,
  'status':'structured_candidate_unverified',
  'missing_fields':['subject','object','population','timeframe','location','study_id'],
  'limits':['Numbers are unbound: no assertion of which measure they describe.',
   'Negation marker does not identify its scope.',
   'Predicate is a lexical candidate, not a semantic interpretation.']}
def from_adequacy(data):
 claims=[]
 for d in data.get('documents',[]):
  q=d.get('adequacy',{})
  if q.get('level')!='A':continue
  for c in q.get('claim_candidates',[]):
   x=extract_sentence(c.get('evidence_excerpt',''),url=d.get('url',''),
    source_id=d.get('source_id'),kind=q.get('kind','description'),
    idx=c.get('sentence_index',0),level=q['level'])
   if x:claims.append(x)
 return {'schema_version':1,'purpose':'source_grounded_claim_representation',
  'coverage':{'documents_examined':len(data.get('documents',[])),
   'claim_candidates':len(claims),'verified_claims':0,'fully_resolved_claims':0},
  'claims':claims,'limitations':['Lexical structural candidates only; not full semantic extraction.',
  'Unresolved subject/object and quantity attachment require contextual model and human evaluation.',
  'No cross-document entailment, same-study identity or contradiction proven.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--adequacy',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=from_adequacy(json.loads(a.adequacy.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out['coverage']))
if __name__=='__main__':main()
