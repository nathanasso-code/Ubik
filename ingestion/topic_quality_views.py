"""Three progressive topic feed views over one shared source catalogue.

Conservative gates: attention is not validation; essential requires explicit
documentary review. No data fetch, writes, or automatic publication.
"""
from .contracts import canonical_url_hint


def topic_views(documents, *, topic_id, explore_limit=100, relevant_limit=30, essential_limit=12):
    if not topic_id or any(type(n) is not int or n < 1 for n in (explore_limit, relevant_limit, essential_limit)):
        raise ValueError("Invalid topic or limits")
    seen, candidates = set(), []
    for doc in documents:
        url = doc.get("url")
        if not url:
            continue
        try:
            key = canonical_url_hint(url)
        except ValueError:
            continue
        if key in seen:
            continue
        seen.add(key)
        if topic_id not in doc.get("topic_ids", []):
            continue
        if doc.get("editorial_exclusion") is True:
            continue
        attention = doc.get("attention") or {}
        channels = set(doc.get("discovery_channels") or [])
        social_accounts = doc.get("distinct_social_accounts", 0)
        if type(social_accounts) is not int or social_accounts < 0:
            social_accounts = 0
        # No ungrounded score or fabricated follower/verification signal.
        qualified = bool(attention.get("qualified_signal_reviewed"))
        substantive = bool(attention.get("substantive_debate_reviewed"))
        relevant = social_accounts >= 2 or qualified or substantive or bool(doc.get("editorial_relevance_reviewed"))
        essential = (doc.get("documentary_validation") == "reviewed"
                     and doc.get("editorial_essential_approved") is True)
        candidates.append({**doc, "url": key, "eligible_relevant": relevant,
                           "eligible_essential": essential,
                           "discovery_channels": sorted(channels)})
    # Explicit review and multiple channels take priority; stable tie break.
    candidates.sort(key=lambda x: (
        -int(x["eligible_essential"]), -int(x["eligible_relevant"]),
        -int("mastodon" in x["discovery_channels"]),
        -len(x["discovery_channels"]), -int(x.get("distinct_social_accounts") or 0), x["url"]))
    explore = candidates[:explore_limit]
    relevant = [x for x in candidates if x["eligible_relevant"] or x["eligible_essential"]][:relevant_limit]
    essential = [x for x in candidates if x["eligible_essential"]][:essential_limit]
    # Essentials stay discoverable in other views even under tight limits.
    essential_keys = {x["url"] for x in essential}
    relevant = list({x["url"]:x for x in relevant + essential}.values())
    explore = list({x["url"]:x for x in explore + relevant}.values())
    return {"schema_version": 1, "topic_id": topic_id,
            "views": {"esplora": explore, "rilevanti": relevant, "essenziali": essential},
            "counts": {"esplora":len(explore), "rilevanti":len(relevant), "essenziali":len(essential)},
            "publication": "review_only", "validation": "independent_of_attention",
            "note": "Limits are soft when needed to retain the progressive inclusion property."}
