"""Evidence adequacy gate for abstracts, descriptions and substantial text.

Do not mistake length for completeness. This is a conservative candidate
qualification, not factual verification or an LLM claim extractor.
"""
import argparse,json,re
from pathlib import Path
NUMBER=re.compile(r'(?<!\w)\d+(?:[.,]\d+)?\s*(?:%|percent|patients|participants|cases|years|months|mg|kg|million|billion|mila|milioni)?\b',re.I)
METHOD=re.compile(r'\b(?:study|trial|survey|analysis|dataset|sample|cohort|experiment|randomized|review|methods?|studio|analisi|campione|esperimento|ricerca|metodo|pazienti)\b',re.I)
RESULT=re.compile(r'\b(?:found|findings|results?|increased|decreased|associated|significant|showed|demonstrated|reported|risultati?|aumentat[oaie]|diminuit[oaie]|associat[oaie]|dimostrat[oaie]|rilevat[oaie]|emerge)\b',re.I)
UNCERTAIN=re.compile(r'\b(?:may|might|could|suggests?|limitations?|uncertain|possibly|potrebbe|possibile|limiti|incerto|suggerisce)\b',re.I)
SENTENCES=re.compile(r'(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9])')
def qualify(text,*,kind='description'):
 clean=' '.join((text or '').split())
 words=len(clean.split())
 sentences=[s.strip() for s in SENTENCES.split(clean) if len(s.split())>=7]
 has_method=bool(METHOD.search(clean));has_result=bool(RESULT.search(clean))
 has_number=bool(NUMBER.search(clean));has_uncertainty=bool(UNCERTAIN.search(clean))
 anchors=sum((has_method,has_result,has_number,has_uncertainty))
 # Specific claims need context: avoid upgrading an abstract just for length.
 if words>=25 and len(sentences)>=2 and (has_result and (has_method or has_number)):
  level='A'
 elif words>=25 and len(sentences)>=2 and anchors>=1:
  level='B'
 else:level='C'
 # Only source sentences, not invented paraphrases; conservative review candidates.
 candidates=[]
 if level=='A':
  for i,s in enumerate(sentences):
   if RESULT.search(s) and (NUMBER.search(s) or METHOD.search(s) or len(s.split())>=12):
    candidates.append({'sentence_index':i,'evidence_excerpt':s[:160],
     'status':'source_sentence_candidate_not_verified'})
 return {'level':level,'kind':kind,'word_count':words,'sentence_count':len(sentences),
  'signals':{'method':has_method,'result':has_result,'numeric':has_number,'uncertainty':has_uncertainty},
  'claim_candidates':candidates[:8],'claim_extraction_verified':False}
def analyze(snapshot):
 results=[]
 for d in snapshot.get('items',[]):
  text=d.get('description') or d.get('summary') or ''
  kind='abstract_or_description_unverified'
  q=qualify(text,kind=kind)
  results.append({'url':d.get('url'),'source_id':d.get('source_id'),
   'title':d.get('title',''),'adequacy':q})
 return {'schema_version':1,'purpose':'abstract_and_description_evidence_adequacy',
  'coverage':{'documents':len(results),'level_A':sum(r['adequacy']['level']=='A' for r in results),
   'level_B':sum(r['adequacy']['level']=='B' for r in results),
   'level_C':sum(r['adequacy']['level']=='C' for r in results),
   'claim_sentence_candidates':sum(len(r['adequacy']['claim_candidates']) for r in results)},
  'documents':results,'limitations':['Heuristic English/Italian cues only; requires labeled evaluation.',
   'RSS description is not assumed to be a scientific abstract.',
   'Evidence excerpts are bounded to 160 characters and are not verified factual claims.',
   'Levels express text suitability, not source truthfulness.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=analyze(json.loads(a.snapshot.read_text()))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out['coverage']))
if __name__=='__main__':main()
