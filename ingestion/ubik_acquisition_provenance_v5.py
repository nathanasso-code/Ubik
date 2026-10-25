"""Deterministic acquisition metadata for Ubik v5. No model calls."""
from urllib.parse import urlsplit

TYPES = {"primary", "news_outlet", "analysis", "social", "unknown"}
LEVELS = {"unrated", "review_pending", "reviewed_low", "reviewed_medium", "reviewed_high"}

def enrich(item, registry):
    """Attach provenance from exact feed source_id; do not infer trust from domains."""
    row = dict(item)
    source = registry.get(row.get("source_id"))
    if source is None:
        row["source_type"] = "unknown"
        row["provenance"] = {
            "publisher_id": row.get("source_id"),
            "publisher_name": row.get("publisher"),
            "authors": row.get("authors", []),
            "curated_registry_member": False,
            "reliability_level": "unrated",
            "reliability_basis": None,
            "registry_status": "unmatched",
            "editorial_group_id": None,
            "content_origin": {"type":"unknown","name":None,"id":None},
        }
        return row
    category = source.get("category")
    source_type = source.get("source_type")
    if source_type is None:
        if source.get("kind") in ("social", "social-api") or category == "social":
            source_type = "social"
        elif category in ("lab", "research", "developer-primary"):
            source_type = "primary"
        elif category in ("analysis", "independent-expert", "academic-blog", "industry-research"):
            source_type = "analysis"
        elif category == "journalism" or source.get("id", "").startswith(("bbc-", "nyt-", "guardian-")):
            source_type = "news_outlet"
        else:
            source_type = "unknown"
    if source_type not in TYPES:
        raise ValueError("Invalid source_type")
    reliability = source.get("reliability_level", "unrated")
    if reliability not in LEVELS:
        raise ValueError("Invalid reliability_level")
    if reliability.startswith("reviewed_") and not source.get("reliability_basis"):
        raise ValueError("Reviewed reliability needs documented basis")
    row["source_type"] = source_type
    row["provenance"] = {
        "publisher_id": source["id"],
        "publisher_name": source["name"],
        "authors": row.get("authors", []),
        "curated_registry_member": True,
        "reliability_level": reliability,
        "reliability_basis": source.get("reliability_basis"),
        "registry_status": "matched",
        "editorial_group_id": source.get("editorial_group_id"),
        "content_origin": source.get("content_origin", {"type":"unknown","name":None,"id":None}),
    }
    return row
