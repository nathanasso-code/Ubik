"""Minimal, provider-agnostic ingestion contract. No editorial classification."""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid", "igshid"}


def canonical_url_hint(url):
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        raise ValueError("Expected absolute HTTP(S) URL")
    params = sorted((k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
                    if not k.lower().startswith("utm_") and k.lower() not in TRACKING)
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(),
                       parsed.path or "/", urlencode(params), ""))


def observation(*, connector, source_id, external_id, title, url, discovered_from,
                published_raw=None, metadata=None):
    if not all(isinstance(x, str) and x.strip() for x in
               (connector, source_id, external_id, title, discovered_from)):
        raise ValueError("Missing required observation metadata")
    hint = canonical_url_hint(url)
    return {
        "schema_version": 1, "connector": connector, "source_id": source_id,
        "id": f"{connector}:{source_id}:{external_id}", "external_id": external_id,
        "title": title.strip()[:500], "url": url, "canonical_url_hint": hint,
        "discovered_from": discovered_from, "published_raw": published_raw,
        "metadata": metadata or {}, "status": "discovered",
        "validation": "not_assessed", "editorial_selection": "not_assessed",
        "event_identity": "not_assessed",
    }
