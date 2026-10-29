"""Bounded Mastodon discovery pilot. Public metadata only; no editorial selection.

Use only operator-approved instances. No automatic instance expansion, login,
scraping, or retention of status HTML. Live mode is explicit.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import quote, urlencode, urlsplit

from .archive import archive_snapshot
from .contracts import observation
from .public_adapters import mastodon_url, fetch_json
from .transport import get_json


def discovery_url(instance, mode="local", *, tag=None, account_id=None, limit=20, max_id=None):
    # Reuse the existing instance and numeric limit validation.
    mastodon_url(instance, limit=limit, max_id=max_id)
    host = urlsplit(instance if "://" in instance else "https://" + instance).hostname
    if mode not in {"local", "federated", "tag", "account"}:
        raise ValueError("Unsupported Mastodon discovery mode")
    if mode == "tag":
        if not tag or len(tag) > 100 or any(c in tag for c in "/?#\\"):
            raise ValueError("Expected a single hashtag")
        path = "/api/v1/timelines/tag/" + quote(tag.lstrip("#"), safe="")
    elif mode == "account":
        if not account_id or not str(account_id).isdigit():
            raise ValueError("Expected numeric instance-local account ID")
        path = "/api/v1/accounts/" + str(account_id) + "/statuses"
    else:
        path = "/api/v1/timelines/public"
    params = {"limit": limit}
    if mode == "local":
        params["local"] = "true"
    elif mode == "federated":
        params["remote"] = "true"
    elif mode == "account":
        params["exclude_reblogs"] = "true"
    if max_id:
        params["max_id"] = max_id
    return "https://" + host + path + "?" + urlencode(params)


def collect(instance, mode="local", *, tag=None, account_id=None, limit=20,
            max_id=None, fetch=fetch_json):
    url = discovery_url(instance, mode, tag=tag, account_id=account_id,
                        limit=limit, max_id=max_id)
    statuses = fetch(url)
    if not isinstance(statuses, list) or len(statuses) > limit:
        raise ValueError("Unexpected Mastodon API page")
    records, invalid, skipped = [], 0, 0
    for status in statuses:
        try:
            if status.get("visibility") != "public" or status.get("reblog"):
                skipped += 1
                continue
            author = status["account"]["url"]
            canonical = status["url"]
            if not (isinstance(canonical, str) and canonical.startswith("https://")
                    and isinstance(author, str) and author.startswith("https://")):
                raise ValueError("Invalid status URL")
            # A remote status can have a different local ID on every instance.
            stable_id = status.get("uri") or canonical
            if not isinstance(stable_id, str) or not stable_id.startswith("https://"):
                raise ValueError("Invalid ActivityPub URI")
            records.append(observation(
                connector="mastodon", source_id=author, external_id=stable_id,
                title="Public Mastodon status", url=canonical,
                discovered_from=url, published_raw=status.get("created_at"),
                metadata={"instance": urlsplit(url).hostname, "mode": mode,
                          "content_type": "social_post_reference",
                          "account_url": author, "edited_at": status.get("edited_at"),
                          "language": status.get("language"),
                          "tags": [t.get("name") for t in status.get("tags", [])
                                   if isinstance(t, dict) and isinstance(t.get("name"), str)][:20]}))
        except (KeyError, TypeError, ValueError):
            invalid += 1
    next_id = str(statuses[-1]["id"]) if statuses and statuses[-1].get("id") else None
    return {"schema_version": 1, "connector": "mastodon", "instance": instance,
            "mode": mode, "observations": records, "invalid": invalid,
            "skipped": skipped, "next_max_id": next_id,
            "coverage_warning": "Instance-visible public posts only; not a fediverse census."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instance", required=True)
    p.add_argument("--approved-instances", type=Path, required=True,
                   help="JSON list of explicitly approved instance hostnames")
    p.add_argument("--mode", choices=("local", "federated", "tag", "account"), default="local")
    p.add_argument("--tag")
    p.add_argument("--account-id")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--max-id")
    p.add_argument("--archive-dir", type=Path, default=Path("data/discovery/runs"))
    p.add_argument("--live", action="store_true")
    p.add_argument("--token-env", default="UBIK_MASTODON_TOKEN",
                   help="Environment variable for optional read-only API token")
    args = p.parse_args()
    endpoint = discovery_url(args.instance, args.mode, tag=args.tag,
                             account_id=args.account_id, limit=args.limit,
                             max_id=args.max_id)
    host = urlsplit(endpoint).hostname
    approved = json.loads(args.approved_instances.read_text(encoding="utf-8"))
    if not isinstance(approved, list) or host not in approved:
        raise ValueError("Instance not in operator-approved allowlist")
    if not args.live:
        print(json.dumps({"dry_run": True, "endpoint": endpoint}))
        return
    token = os.environ.get(args.token_env)
    if token:
        # Transport owns retry, byte limits and timeouts. Never log token.
        from urllib.request import build_opener, HTTPRedirectHandler
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        client = build_opener(NoRedirect)
        def authorized_fetch(url):
            def opener(request, timeout):
                request.add_header("Authorization", "Bearer " + token)
                return client.open(request, timeout=timeout)
            return get_json(url, opener=opener)
        fetcher = authorized_fetch
    else:
        fetcher = fetch_json
    result = collect(args.instance, args.mode, tag=args.tag,
                     account_id=args.account_id, limit=args.limit,
                     max_id=args.max_id, fetch=fetcher)
    archived = archive_snapshot(result, args.archive_dir)
    print(json.dumps({"observations": len(result["observations"]),
                      "skipped": result["skipped"], "invalid": result["invalid"],
                      "next_max_id": result["next_max_id"],
                      "archive_sha256": archived["sha256"]}))


if __name__ == "__main__":
    main()
