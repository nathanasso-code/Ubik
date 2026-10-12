"""Read-only public thread metadata retrieval for exploratory debate discovery.

Never interpret reply counts as argument quality. No post text is persisted.
Callers must obey provider limits and only request public threads.
"""
from urllib.parse import urlencode, urlsplit
from .transport import get_json


def bluesky_thread_url(at_uri, depth=4, parent_height=0):
    if not isinstance(at_uri, str) or not at_uri.startswith("at://") or "/app.bsky.feed.post/" not in at_uri:
        raise ValueError("Expected Bluesky post AT URI")
    if type(depth) is not int or not 0 <= depth <= 100 or type(parent_height) is not int or not 0 <= parent_height <= 100:
        raise ValueError("Invalid thread depth")
    return "https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread?" + urlencode(
        {"uri": at_uri, "depth": depth, "parentHeight": parent_height})


def bluesky_thread(at_uri, *, depth=4, fetch=get_json):
    payload = fetch(bluesky_thread_url(at_uri, depth=depth))
    root = payload.get("thread") or {}
    items, seen = [], set()
    def walk(node, level):
        if not isinstance(node, dict):
            return
        post = node.get("post")
        if not isinstance(post, dict):
            return
        uri = post.get("uri")
        author = (post.get("author") or {}).get("did")
        if not isinstance(uri, str) or uri in seen:
            return
        seen.add(uri)
        items.append({"at_uri": uri, "author_did": author,
                      "reply_count_reported": post.get("replyCount"),
                      "like_count_reported": post.get("likeCount"),
                      "repost_count_reported": post.get("repostCount"),
                      "depth": level, "text_stored": False,
                      "public_url": "https://bsky.app/profile/" + str(author) + "/post/" + uri.rsplit("/",1)[-1]
                      if author and "/app.bsky.feed.post/" in uri else None})
        if level < depth:
            for child in node.get("replies") or []:
                walk(child, level+1)
    walk(root, 0)
    return {"platform": "bluesky", "root": at_uri, "posts_visible": len(items),
            "unique_authors_visible": len({x["author_did"] for x in items if x["author_did"]}),
            "items": items, "coverage": "public thread snapshot; may be incomplete",
            "quality": "not_assessed"}


def mastodon_context_url(status_url):
    if not isinstance(status_url, str):
        raise ValueError("Expected Mastodon status URL")
    parsed = urlsplit(status_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Invalid status URL")
    if parsed.hostname.lower() in ("localhost", "127.0.0.1") or "." not in parsed.hostname:
        raise ValueError("Invalid public instance")
    parts = parsed.path.strip("/").split("/")
    status_id = parts[-1]
    if not status_id.isdigit():
        raise ValueError("Mastodon numeric status ID required")
    return "https://" + parsed.hostname + "/api/v1/statuses/" + status_id + "/context"


def mastodon_context(status_url, *, fetch=get_json):
    payload = fetch(mastodon_context_url(status_url))
    descendants = payload.get("descendants") or []
    ancestors = payload.get("ancestors") or []
    def simplify(status):
        account = status.get("account") or {}
        return {"id": str(status.get("id")), "url": status.get("url"),
                "author_id": account.get("acct") or account.get("id"),
                "in_reply_to_id": status.get("in_reply_to_id"),
                "replies_count_reported": status.get("replies_count"),
                "text_stored": False}
    return {"platform": "mastodon", "root": status_url,
            "ancestors": [simplify(x) for x in ancestors if isinstance(x, dict)],
            "replies": [simplify(x) for x in descendants if isinstance(x, dict)],
            "coverage": "instance-local federation view, not global thread census",
            "quality": "not_assessed"}
