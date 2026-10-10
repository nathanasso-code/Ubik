"""Offline policy checks for bounded acquisition experiments.

No external network calls. This file deliberately keeps network permission
separate from content selection or epistemic evaluation.
"""
from datetime import date
from urllib.parse import urlsplit


ALLOWED_PROVIDERS = frozenset({"bluesky", "mastodon", "openalex", "crossref"})


def validate_plan(plan):
    if not isinstance(plan, dict) or not isinstance(plan.get("sources"), list):
        raise ValueError("Plan must contain a sources list")
    if len(plan["sources"]) > 24:
        raise ValueError("At most 24 sources per experiment")
    seen = set()
    result = []
    for index, item in enumerate(plan["sources"]):
        if not isinstance(item, dict):
            raise ValueError(f"Source {index} must be an object")
        provider, source = item.get("provider"), item.get("source")
        if provider not in ALLOWED_PROVIDERS or not isinstance(source, str) or not source.strip():
            raise ValueError(f"Invalid source at index {index}")
        if provider == "bluesky":
            if "/" in source or "://" in source or len(source) > 255:
                raise ValueError("Invalid Bluesky actor")
        elif provider == "mastodon":
            from .public_adapters import mastodon_url
            mastodon_url(source)
        elif source not in {"openalex-works", "crossref-works"}:
            raise ValueError("Scientific source must be a fixed registry identifier")
        pages, size = item.get("max_pages", 2), item.get("page_size", 20)
        if type(pages) is not int or not 1 <= pages <= 10 or type(size) is not int or not 1 <= size <= 20:
            raise ValueError("Invalid per-source acquisition budget")
        start, end = item.get("from_date"), item.get("to_date")
        if provider in {"openalex", "crossref"}:
            if not isinstance(start, str) or not isinstance(end, str):
                raise ValueError("Scientific sources require explicit date range")
            if date.fromisoformat(start) > date.fromisoformat(end):
                raise ValueError("Invalid date range")
        else:
            if start is not None or end is not None:
                raise ValueError("Social sources do not accept publication date filters")
        identity = (provider, source, start, end)
        if identity in seen:
            raise ValueError("Duplicate source scope")
        seen.add(identity)
        result.append({"provider": provider, "source": source, "max_pages": pages,
                       "page_size": size, "from_date": start, "to_date": end})
    if not result:
        raise ValueError("At least one source required")
    return result
