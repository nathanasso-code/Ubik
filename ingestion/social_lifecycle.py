"""Conservative social retention/reconciliation planning (no deletion or network calls).

This is an operational policy model, not proof of consent or platform compliance.
"""
from datetime import datetime, timedelta, timezone

SOCIAL_CONNECTORS = frozenset({"bluesky", "mastodon"})


def retention_decision(observation, *, now=None, max_age_days=30, removed_ids=()):
    if not isinstance(observation, dict):
        raise ValueError("Expected observation")
    if not isinstance(max_age_days, int) or not 1 <= max_age_days <= 365:
        raise ValueError("Invalid retention horizon")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Timezone-aware clock required")
    connector = observation.get("connector")
    if connector not in SOCIAL_CONNECTORS:
        return {"action": "not_applicable", "reason": "non_social_connector"}
    external_id = observation.get("external_id")
    if not isinstance(external_id, str) or not external_id:
        return {"action": "quarantine", "reason": "missing_external_id"}
    if external_id in removed_ids:
        return {"action": "purge_candidate", "reason": "verified_removal_signal"}
    raw = observation.get("collected_at")
    if not isinstance(raw, str):
        return {"action": "review", "reason": "collection_time_unknown"}
    try:
        collected = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return {"action": "quarantine", "reason": "invalid_collection_time"}
    if collected.tzinfo is None:
        return {"action": "quarantine", "reason": "naive_collection_time"}
    if collected > now:
        return {"action": "review", "reason": "future_collection_time"}
    if now - collected >= timedelta(days=max_age_days):
        return {"action": "purge_candidate", "reason": "retention_window_elapsed"}
    return {"action": "retain_temporarily", "reason": "within_retention_window"}


def reconciliation_plan(observations, *, removed_ids=(), now=None, max_age_days=30):
    actions = {}
    for item in observations:
        result = retention_decision(item, now=now, removed_ids=removed_ids,
                                    max_age_days=max_age_days)
        action = result["action"]
        actions[action] = actions.get(action, 0) + 1
    return {"counts": actions, "automatic_deletion_performed": False,
            "warning": "Deletion signals must be verified; propagation to archives, backups and derivatives requires separate implementation."}
