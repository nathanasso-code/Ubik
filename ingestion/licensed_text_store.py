"""Store article text only after explicit per-document reuse rights verification."""
import hashlib,json
from pathlib import Path
from ingestion.document_rights_registry import rights
def store_text(url,text,permission,*,directory):
    if not isinstance(text,str) or not text.strip():raise ValueError('Empty text')
    if permission.get('url')!=url or not permission.get('store_full_text') or not permission.get('display_full_text'):
        raise PermissionError('Verified document-specific storage and display rights required')
    if not permission.get('license_evidence_url') or not permission.get('license_verified'):
        raise PermissionError('Missing verified license evidence')
    key=hashlib.sha256(url.encode()).hexdigest()
    folder=Path(directory);folder.mkdir(parents=True,exist_ok=True)
    path=folder/(key+'.json')
    payload={'url':url,'text':text,'license_id':permission['license_id'],
      'license_evidence_url':permission['license_evidence_url'],
      'attribution_required':permission.get('attribution_required',False),
      'sha256':hashlib.sha256(text.encode()).hexdigest()}
    path.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    return {'stored':True,'path':str(path),'sha256':payload['sha256']}
