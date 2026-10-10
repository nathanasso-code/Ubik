"""Independent metadata-only adapters for public social/scientific APIs.

No publication, ranking, or clustering. No social text bodies retained.
Network access is performed only by an explicit caller.
"""
from html import unescape
import ipaddress
from urllib.parse import urlencode, urlsplit

from .contracts import observation
from .transport import get_json


def fetch_json(url, timeout=15):
    return get_json(url, timeout=timeout)

def bluesky_url(actor, limit=30, cursor=None):
    if not isinstance(actor, str) or not actor.strip() or "/" in actor or len(actor) > 255:
        raise ValueError("Expected a Bluesky actor handle or DID")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Bluesky limit must be 1..100")
    params = {"actor": actor, "limit": limit, "filter": "posts_no_replies"}
    if cursor:
        params["cursor"] = cursor
    return "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?" + urlencode(params)


def bluesky_collect(actor, limit=30, cursor=None, fetch=fetch_json):
    payload = fetch(bluesky_url(actor, limit, cursor))
    results, invalid = [], 0
    for item in payload.get("feed", []):
        try:
            post = item["post"]
            uri = post["uri"]
            author = post["author"]
            rkey = uri.rsplit("/", 1)[-1]
            did = author["did"]
            if not uri.startswith("at://") or not did.startswith("did:") or not rkey:
                raise ValueError("Invalid AT URI")
            record = post.get("record") or {}
            title = " ".join(str(record.get("text", "")).split())[:500]
            if not title:
                continue
            results.append(observation(
                connector="bluesky", source_id=did, external_id=uri,
                title=title, url=f"https://bsky.app/profile/{did}/post/{rkey}",
                discovered_from=f"https://bsky.app/profile/{actor}",
                published_raw=record.get("createdAt"),
                metadata={"at_uri": uri, "author_did": did,
                          "content_type": "social_post_metadata_preview",
                          "repost_reason": bool(item.get("reason"))}))
        except (KeyError, TypeError, ValueError):
            invalid += 1
    return {"schema_version": 1, "connector": "bluesky", "actor": actor,
            "observations": results, "invalid": invalid, "next_cursor": payload.get("cursor"),
            "coverage_warning": "Author feed only, not a network-wide census."}


def mastodon_url(instance, limit=20, max_id=None):
    parsed = urlsplit(instance if "://" in instance else "https://" + instance)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port or parsed.path not in ("", "/"):
        raise ValueError("Expected HTTPS Mastodon instance hostname")
    host = parsed.hostname.lower()
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")) or "." not in host:
        raise ValueError("Mastodon instance must be a public hostname")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("IP-address instance targets are not allowed")
    if type(limit) is not int or not 1 <= limit <= 40:
        raise ValueError("Mastodon limit must be 1..40")
    params = {"limit": limit, "local": "true"}
    if max_id:
        params["max_id"] = max_id
    return f"https://{parsed.hostname}/api/v1/timelines/public?" + urlencode(params)


def mastodon_collect(instance, limit=20, max_id=None, fetch=fetch_json):
    payload = fetch(mastodon_url(instance, limit, max_id))
    if not isinstance(payload, list):
        raise ValueError("Unexpected Mastodon timeline")
    results, invalid = [], 0
    for status in payload:
        try:
            if status.get("visibility") != "public" or status.get("reblog"):
                continue
            account = status["account"]
            url = status["url"]
            title = unescape(str(status.get("spoiler_text") or "")).strip()
            if not title:
                title = "Public Mastodon post " + str(status["id"])
            results.append(observation(
                connector="mastodon", source_id=account["url"],
                external_id=str(status["id"]), title=title, url=url,
                discovered_from=mastodon_url(instance, limit, max_id),
                published_raw=status.get("created_at"),
                metadata={"instance": urlsplit(mastodon_url(instance)).hostname,
                          "content_type": "social_post_reference",
                          "account_url": account["url"]}))
        except (KeyError, TypeError, ValueError):
            invalid += 1
    return {"schema_version": 1, "connector": "mastodon", "instance": instance,
            "observations": results, "invalid": invalid,
            "next_max_id": str(payload[-1]["id"]) if payload and "id" in payload[-1] else None,
            "coverage_warning": "One instance's public local timeline; some servers require auth."}


def openalex_url(from_date, to_date, per_page=50, cursor="*"):
    import datetime
    for date in (from_date, to_date):
        datetime.date.fromisoformat(date)
    if from_date > to_date or type(per_page) is not int or not 1 <= per_page <= 100:
        raise ValueError("Invalid bounded date range or page size")
    return "https://api.openalex.org/works?" + urlencode({
        "filter": f"from_publication_date:{from_date},to_publication_date:{to_date}",
        "per_page": per_page, "cursor": cursor,
        "select": "id,doi,display_name,publication_date,primary_location,type"})


def openalex_collect(from_date, to_date, per_page=50, cursor="*", fetch=fetch_json):
    payload = fetch(openalex_url(from_date, to_date, per_page, cursor))
    results, invalid = [], 0
    for work in payload.get("results", []):
        try:
            url = work.get("doi") or work["id"]
            results.append(observation(
                connector="openalex", source_id="openalex-works",
                external_id=work["id"], title=work["display_name"],
                url=url, discovered_from="https://api.openalex.org/works",
                published_raw=work.get("publication_date"),
                metadata={"openalex_id": work["id"], "doi": work.get("doi"),
                          "work_type": work.get("type"), "content_type": "bibliographic_metadata"}))
        except (KeyError, ValueError, TypeError):
            invalid += 1
    return {"schema_version": 1, "connector": "openalex",
            "observations": results, "invalid": invalid,
            "next_cursor": payload.get("meta", {}).get("next_cursor"),
            "coverage_warning": "Date-bounded works page; cursor needed for complete interval."}


def crossref_url(from_date, to_date, rows=50, cursor="*"):
    import datetime
    for date in (from_date, to_date):
        datetime.date.fromisoformat(date)
    if from_date > to_date or type(rows) is not int or not 1 <= rows <= 100:
        raise ValueError("Invalid Crossref date window or page size")
    return "https://api.crossref.org/works?" + urlencode({
        "filter": f"from-pub-date:{from_date},until-pub-date:{to_date}",
        "rows": rows, "cursor": cursor,
        "select": "DOI,title,published,URL,type,publisher",
    })


def crossref_collect(from_date, to_date, rows=50, cursor="*", fetch=fetch_json):
    payload = fetch(crossref_url(from_date, to_date, rows, cursor))
    message = payload.get("message", {})
    results, invalid = [], 0
    for work in message.get("items", []):
        try:
            doi = work["DOI"]
            title = work["title"][0]
            results.append(observation(
                connector="crossref", source_id="crossref-works",
                external_id=doi, title=title,
                url="https://doi.org/" + doi, discovered_from="https://api.crossref.org/works",
                published_raw=None,
                metadata={"doi": doi, "publisher": work.get("publisher"),
                          "work_type": work.get("type"),
                          "content_type": "bibliographic_metadata"}))
        except (KeyError, ValueError, TypeError, IndexError):
            invalid += 1
    return {"schema_version": 1, "connector": "crossref",
            "observations": results, "invalid": invalid,
            "next_cursor": message.get("next-cursor"),
            "coverage_warning": "Date-bounded Crossref page, not complete scholarly corpus."}
