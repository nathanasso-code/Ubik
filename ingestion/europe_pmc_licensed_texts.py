"""Fetch Europe PMC open-access XML and retain text only for explicitly licensed papers."""
import argparse,hashlib,json,re,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
ALLOW={'CC BY','CC-BY','CC BY 4.0','CC-BY-4.0','CC0','CC0-1.0','CC BY-SA 4.0','CC-BY-SA-4.0'}
def acquire(snapshot,output_dir,*,max_items=12):
 rows=[x for x in snapshot.get('items',[]) if x.get('source_id')=='europepmc']
 reports=[];stored=0
 for item in rows[:max_items]:
  pmcid=item['url'].rsplit('/',1)[-1]
  try:
   url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML'
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'UbikResearchBot/0.1 (ubik.research@gmail.com)'}),timeout=15) as r:
    raw=r.read(2000001)
   if len(raw)>2000000:raise ValueError('oversize')
   root=ET.fromstring(raw)
   licenses=[' '.join(x.itertext()).strip() for x in root.findall('.//license')]
   accepted=any(('creativecommons.org/licenses/by/4.0/' in lic.lower() or 'creativecommons.org/publicdomain/zero/1.0/' in lic.lower() or 'creativecommons.org/licenses/by-sa/4.0/' in lic.lower()) and not re.search(r'non.?commercial|no.?derivatives|by-nc|by-nd',lic,re.I) for lic in licenses)
   body=root.find('.//body')
   text=' '.join(' '.join(body.itertext()).split()) if body is not None else ''
   status='text_read_not_stored'
   if accepted and len(text)>1000:
    path=Path(output_dir);path.mkdir(parents=True,exist_ok=True)
    target=path/(pmcid+'.json')
    target.write_text(json.dumps({'url':item['url'],'pmcid':pmcid,'title':item.get('title',''),
      'text':text,'license_evidence':licenses,'license_source':url,
      'attribution':'Original article authors and Europe PMC source; inspect before public display'},ensure_ascii=False))
    stored+=1;status='licensed_text_stored_for_review'
   reports.append({'url':item['url'],'status':status,'chars':len(text),'license_detected':bool(licenses),
    'license_accepted_for_review':accepted,'sha256':hashlib.sha256(text.encode()).hexdigest()})
  except Exception as exc:reports.append({'url':item['url'],'status':'error','error_type':type(exc).__name__})
 return {'coverage':{'attempted':len(reports),'licensed_texts_stored_for_review':stored},'outcomes':reports,
  'limitations':['License string matching is preliminary; human legal and attribution review required before publication.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--api',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--texts',type=Path,required=True);a=p.parse_args()
 r=acquire(json.loads(a.api.read_text()),a.texts);a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r['coverage']))
if __name__=='__main__':main()
