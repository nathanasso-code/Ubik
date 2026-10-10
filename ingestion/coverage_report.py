"""Non-editorial acquisition coverage audit from real source reports and observations.

Never treat zero records from a failed source as zero published records.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone

from .audit import _parse_date
from .duplicates import duplicate_report


def evaluate_coverage(inventory, *, discovery=None, federated=None, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Timezone-aware now required")
    discovery = discovery or {}
    federated = federated or {"observations": []}
    if not isinstance(discovery.get("source_reports", []), list):
        raise ValueError("Invalid source reports")
    observations = federated.get("observations")
    if not isinstance(observations, list):
        raise ValueError("Invalid federated observations")
    reports = {x["source_id"]: x for x in discovery.get("source_reports", [])
               if isinstance(x, dict) and isinstance(x.get("source_id"), str)}
    per_source = Counter()
    missing_ids = Counter()
    missing_dates = Counter()
    freshness = Counter()
    languages = Counter()
    missing_urls = Counter()
    missing_titles = Counter()
    observed_dates = defaultdict(list)
    for item in observations:
        if not isinstance(item, dict):
            raise ValueError("Invalid observation")
        key = (item.get("connector") or "unknown", item.get("source_id") or "unknown")
        per_source[key] += 1
        metadata = item.get("metadata")
        language = item.get("language") or (metadata.get("language") if isinstance(metadata, dict) else None)
        languages[language if isinstance(language, str) and language.strip() else "unknown"] += 1
        if not item.get("url"):
            missing_urls[key] += 1
        if not item.get("title"):
            missing_titles[key] += 1
        if not item.get("external_id"):
            missing_ids[key] += 1
        published = _parse_date(item.get("published_raw"))
        if published is None:
            missing_dates[key] += 1
        else:
            observed_dates[key].append(published)
            age = (now - published).total_seconds() / 3600
            freshness["future_timestamp" if age < 0 else
                      "within_24h" if age <= 24 else
                      "within_7d" if age <= 168 else "older_than_7d"] += 1
    feed_rows = []
    for source in inventory["registry"]:
        if source["kind"] != "rss" or not source["configured_enabled"]:
            continue
        report = reports.get(source["id"])
        status = "not_tested" if report is None else report.get("status", "unknown")
        feed_rows.append({
            "source_id": source["id"], "status": status,
            "seen": report.get("seen") if report else None,
            "stored": report.get("stored") if report else None,
            "error": report.get("error") if report else None,
            "note": "cumulative_stored_not_current_fetch" if report else "no_run_report",
        })
    source_rows = [{
        "connector": connector, "source_id": source, "observations": count,
        "missing_external_ids": missing_ids[(connector, source)],
        "missing_publication_dates": missing_dates[(connector, source)],
        "missing_urls": missing_urls[(connector, source)],
        "missing_titles": missing_titles[(connector, source)],
        "oldest_published": min(observed_dates[(connector, source)]).isoformat()
            if observed_dates[(connector, source)] else None,
        "newest_published": max(observed_dates[(connector, source)]).isoformat()
            if observed_dates[(connector, source)] else None,
    } for (connector, source), count in sorted(per_source.items())]
    duplicates = duplicate_report(federated)
    return {
        "schema_version": 1, "scope": "acquisition_quality_not_editorial_selection",
        "enabled_feed_count": len(feed_rows),
        "tested_feed_count": sum(x["status"] != "not_tested" for x in feed_rows),
        "successful_feed_count": sum(x["status"] == "ok" for x in feed_rows),
        "failed_feed_count": sum(x["status"] == "error" for x in feed_rows),
        "feed_status": feed_rows,
        "observations_audited": len(observations),
        "source_observations": source_rows,
        "freshness": dict(freshness),
        "languages_explicitly_declared": dict(sorted(languages.items())),
        "duplicate_diagnostics": duplicates,
        "warnings": [
            "Feed reports are historical observations, not live availability checks.",
            "Cumulative stored counts are not per-run throughput.",
            "Duplicate provider observations do not imply independent corroboration.",
            "No complete expected universe is known; recall/completeness cannot be computed.",
            "Language is counted only when explicitly declared; no language inference is performed.",
            "No editorial ranking, topic selection, card assignment or nuclei generation.",
        ],
    }
