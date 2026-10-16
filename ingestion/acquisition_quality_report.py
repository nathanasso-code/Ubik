import collections
from urllib.parse import urlsplit

def summarize(probes):
    by_host=collections.defaultdict(list)
    for item in probes:
        by_host[urlsplit(item.get('url','')).hostname or 'unknown'].append(item)
    return [{'host':host,'attempted':len(rows),'article_text':sum(x.get('content_tier')=='substantial_article_text_accessible' for x in rows),'page_text_unverified':sum(x.get('content_tier')=='substantial_page_text_unverified_article' for x in rows),'failed':sum(x.get('status')!='get_success' for x in rows)} for host,rows in sorted(by_host.items())]
