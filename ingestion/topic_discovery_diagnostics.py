"""Quality diagnostics for bounded topic-led discovery runs.

These metrics describe *coverage and drift*, not truth, newsworthiness,
political bias or the relevance of any individual story.
"""
from collections import Counter
from urllib.parse import urlsplit

def diagnose(result):
    documents=result.get("documents") or []
    events=result.get("event_candidates") or []
    expansion=result.get("expansion") or []
    doc_expansion=result.get("document_expansion") or []
    hosts=Counter(urlsplit(d.get("url","")).hostname for d in documents)
    multi=[d for d in documents if d.get("distinct_accounts_observed",0)>=2]
    repeated=[e for e in events if e.get("document_count",0)>1]
    queries=len(result.get("queries") or [])+len(expansion)+len(doc_expansion)
    return {
        "topic":result.get("topic"),
        "posts":result.get("posts",0),
        "seed_posts":result.get("seed_posts"),
        "additional_posts":max(0,result.get("posts",0)-(result.get("seed_posts") or 0)),
        "query_terms_requested":queries,
        "expanded_hashtag_terms":[x["term"] for x in expansion],
        "expanded_document_terms":[x["term"] for x in doc_expansion],
        "external_url_hints":len(documents),
        "urls_with_two_or_more_observed_accounts":len(multi),
        "candidate_multidocument_event_groups":len(repeated),
        "unique_document_hosts":len(hosts),
        "top_document_hosts":hosts.most_common(10),
        "acquisition_errors":result.get("errors") or [],
        "limitations":[
            "No baseline topic relevance labels; expansion may drift from the topic.",
            "Observed accounts are not proven independent human origins.",
            "URL slug grouping is not multilingual semantic event matching.",
            "No historical completeness or time-series acceleration measurement.",
            "Social post text and URL hints do not verify linked article claims."
        ]
    }
