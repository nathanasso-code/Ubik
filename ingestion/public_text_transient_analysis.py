"""Analyze publicly accessible article text transiently; never persist article bodies."""
import argparse,collections,hashlib,json,re
from pathlib import Path
from urllib.parse import urlsplit
from ingestion.live_get_text_probe import Extractor
from ingestion.approved_https_fetch import fetch_one,USER_AGENT
from urllib.robotparser import RobotFileParser
from ingestion.abstract_evidence_adequacy import qualify
STOP={'the','and','for','with','from','this','that','have','been','were','are','was','una','della','delle','degli','per','con','che','del','alla'}
def analyze(snapshot,*,limit=150,per_host=12,fetch=fetch_one):
 results=[];counts=collections.Counter();seen=set()
 for item in snapshot.get('items',[]):
  url=item.get('url','')
  p=urlsplit(url);host=p.hostname
  if not host or p.scheme!='https' or url in seen or counts[host]>=per_host:continue
  if len(results)>=limit:break
  seen.add(url);counts[host]+=1
  row={'url':url,'source_id':item.get('source_id')}
  try:
   robots=fetch('https://'+host+'/robots.txt',{host},timeout=6)
   rp=RobotFileParser();rp.parse(robots.splitlines())
   if not rp.can_fetch(USER_AGENT,url):
    row['status']='robots_disallowed';results.append(row);continue
   page=fetch(url,{host},timeout=9)
   ext=Extractor();ext.feed(page)
   article=' '.join(''.join(ext.article).split())
   visible=' '.join(''.join(ext.text).split())
   text=article if len(article)>=400 else visible
   words=re.findall(r'\b[^\W\d_][\w-]{3,}\b',text.lower())
   frequent=[{'term':term,'count':n} for term,n in collections.Counter(w for w in words if w not in STOP).most_common(15)]
   adequacy=qualify(text,kind='transient_public_body')
   # Do not retain source excerpts from non-licensed article bodies.
   claim_signals={'adequacy_level':adequacy['level'],'source_sentence_candidates':len(adequacy['claim_candidates']),
    'method_signal':adequacy['signals']['method'],'result_signal':adequacy['signals']['result'],
    'numeric_signal':adequacy['signals']['numeric'],'uncertainty_signal':adequacy['signals']['uncertainty']}
   row.update({'claim_evidence_signals':claim_signals,'status':'analyzed_in_memory','text_chars':len(text),'word_count':len(words),
    'article_element_chars':len(article),'sha256':hashlib.sha256(text.encode()).hexdigest(),
    'semantic_term_candidates':frequent,'full_text_persisted':False,
    'complete_article_verified':False,'republication_rights_verified':False})
  except (ValueError,OSError,TimeoutError,PermissionError) as e:
   row.update({'status':'fetch_failed','error_type':type(e).__name__})
  results.append(row)
 return {'schema_version':1,'purpose':'public_article_transient_text_analysis',
  'coverage':{'attempted':len(results),'analyzed':sum(x['status']=='analyzed_in_memory' for x in results),
   'substantial_text':sum(x.get('text_chars',0)>=1200 for x in results),
   'body_level_A':sum(x.get('claim_evidence_signals',{}).get('adequacy_level')=='A' for x in results),
   'body_level_B':sum(x.get('claim_evidence_signals',{}).get('adequacy_level')=='B' for x in results),
   'body_claim_sentence_candidates':sum(x.get('claim_evidence_signals',{}).get('source_sentence_candidates',0) for x in results)},
  'documents':results,'limitations':['No paywall bypass or login.','No article text retained.',
   'Term frequencies and transient sentence indicators are preliminary signals, not verified claims or validated topic assignments.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',type=int,default=150)
 a=p.parse_args();r=analyze(json.loads(a.snapshot.read_text()),limit=a.limit)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(r['coverage']))
if __name__=='__main__':main()
