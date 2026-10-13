"""Document-level reuse permission gate; unknown licenses always abstain."""
import datetime
from urllib.parse import urlsplit
OPEN={'CC0-1.0','CC-BY-4.0','CC-BY-2.5','CC-BY-SA-4.0'}
def rights(url,*,license_id=None,license_evidence_url=None,verified=False,
           analysis_permission=False,restrictions=None):
    host=(urlsplit(url).hostname or '').lower()
    restrictions=restrictions or []
    license_ok=bool(verified and license_id in OPEN and license_evidence_url)
    # Domain is merely a discovery hint, never permission.
    candidates=('wikinews.org' in host or host.endswith('arxiv.org'))
    return {'url':url,'license_id':license_id or 'UNKNOWN',
      'license_evidence_url':license_evidence_url,
      'license_verified':bool(verified),'analysis_permission_confirmed':bool(analysis_permission),
      'store_full_text':license_ok and not restrictions,
      'display_full_text':license_ok and not restrictions,
      'candidate_for_license_review':candidates and not license_ok,
      'restrictions':restrictions,'attribution_required':license_id in {'CC-BY-4.0','CC-BY-2.5','CC-BY-SA-4.0'},
      'rights_status':'verified_reuse' if license_ok and not restrictions else 'review_required',
      'note':'Per-item verification required; public accessibility does not grant republication rights.'}
def review_corpus(ledger):
    results=[rights(d['url']) for d in ledger.get('documents',[])]
    return {'schema_version':1,'purpose':'per_document_license_review_queue',
      'coverage':{'documents':len(results),'license_review_candidates':sum(r['candidate_for_license_review'] for r in results),
        'verified_full_text_display_permissions':0},
      'reviews':results,'automatic_full_text_storage_enabled':False}
