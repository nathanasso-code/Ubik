"""Normalize legacy RSS/Hacker News observations into the ingestion contract.

Adapters do not fetch, rank, publish or cluster anything.
"""
from .contracts import observation


def rss_to_observation(item):
    return observation(
        connector="rss", source_id=item["source_id"],
        external_id=str(item.get("external_id") or item.get("id") or item["url"]),
        title=item["title"], url=item["url"],
        discovered_from=item.get("discovered_from") or item["url"],
        published_raw=item.get("published_raw"),
        metadata={
            "publisher": item.get("publisher"),
            "authors": item.get("authors", []),
            "description": item.get("description"),
            "attribution_status": item.get("attribution_status", "feed_only_unverified"),
            "legacy_id": item.get("id"),
        },
    )


def hacker_news_to_observation(item):
    return observation(
        connector="hacker_news", source_id=item["source_id"],
        external_id=str(item.get("id") or item["original_url"]),
        title=item["title"], url=item["url"],
        discovered_from=item.get("original_url") or "https://news.ycombinator.com/",
        published_raw=item.get("published_raw"),
        metadata={
            "discussion_url": item.get("original_url"),
            "score_at_observation": item.get("score_at_observation"),
            "comments_at_observation": item.get("comments_at_observation"),
            "author": item.get("author"),
        },
    )
