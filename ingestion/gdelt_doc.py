"""GDELT DOC 2.0 ArtList discovery adapter, metadata only.

GDELT DOC is a *query-based* discovery index, not a complete firehose.
Callers must record their query, timespan, truncation and fetch status.
"""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .contracts import observation

ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
USER_AGENT = "Ubik-research-ingestion/0.1"


def request_url(query, *, timespan="1h", maxrecords=75):
    if not isinstance(query, str) or not query.strip() or len(query) > 500:
        raise ValueError("GDELT requires a bounded nonempty query")
    if not isinstance(timespan, str) or not timespan.endswith(("h", "min", "d")):
        raise ValueError("Use a documented bounded timespan, e.g. 1h, 30min, 1d")
    if type(maxrecords) is not int or not 1 <= maxrecords <= 250:
        raise ValueError("GDELT ArtList maxrecords must be 1..250")
    return ENDPOINT + "?" + urlencode({
        "query": query, "mode": "artlist", "format": "json",
        "timespan": timespan, "maxrecords": maxrecords,
        "sort": "datedesc",
    })


def parse_response(payload, *, query, timespan, maxrecords):
    if not isinstance(payload, dict):
        raise ValueError("Unexpected GDELT response")
    articles = payload.get("articles", [])
    if not isinstance(articles, list):
        raise ValueError("Unexpected GDELT article list")
    records, errors = [], []
    for index, article in enumerate(articles):
        if not isinstance(article, dict):
            errors.append(index)
            continue
        try:
            url = article["url"]
            record = observation(
                connector="gdelt_doc", source_id="gdelt-doc-artlist",
                external_id=url, title=article["title"], url=url,
                discovered_from=ENDPOINT, published_raw=article.get("seendate"),
                metadata={
                    "domain": article.get("domain"),
                    "language": article.get("language"),
                    "sourcecountry": article.get("sourcecountry"),
                    "query": query, "timespan": timespan,
                    "time_basis": "gdelt_seen_date_not_original_publication",
                })
            records.append(record)
        except (ValueError, KeyError, TypeError):
            errors.append(index)
    return {
        "schema_version": 1, "connector": "gdelt_doc",
        "query": query, "timespan": timespan, "maxrecords": maxrecords,
        "potentially_truncated": len(articles) >= maxrecords,
        "observations": records, "invalid_indices": errors,
        "coverage_warning": "Query-based results are not a complete census of news.",
    }


def collect(query, *, timespan="1h", maxrecords=75, timeout=15, fetch=None):
    url = request_url(query, timespan=timespan, maxrecords=maxrecords)
    if fetch is None:
        def fetch(target):
            with urlopen(Request(target, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/json"}),
                         timeout=timeout) as response:
                return json.load(response)
    return parse_response(fetch(url), query=query, timespan=timespan, maxrecords=maxrecords)
