"""Offline diagnostics for individual RSS source failures.

This never retries 403 responses, removes safety limits, or fetches websites.
"""
from urllib.parse import urlsplit


def triage_feed_reports(reports):
    if not isinstance(reports, list):
        raise ValueError("Expected source reports")
    issues = []
    for row in reports:
        if not isinstance(row, dict) or not isinstance(row.get("source_id"), str):
            raise ValueError("Invalid feed report")
        if row.get("status") == "ok":
            if row.get("raw_entries") == 0:
                issues.append({
                    "source_id": row["source_id"], "issue": "upstream_zero_entries",
                    "action": "verify_official_endpoint_and_publication_cadence",
                    "access_change_authorized": False,
                })
            elif isinstance(row.get("raw_entries"), int) and isinstance(row.get("seen"), int) and row["raw_entries"] > row["seen"]:
                issues.append({
                    "source_id": row["source_id"], "issue": "normalization_loss",
                    "lost": row["raw_entries"] - row["seen"],
                    "action": "inspect_feed_format_and_invalid_entry_reasons",
                    "access_change_authorized": False,
                })
            continue
        error = str(row.get("error") or "")
        issue = ("http_403" if "403" in error else
                 "payload_limit" if "exceeds limit" in error else
                 "http_429" if "429" in error else "fetch_or_parse_error")
        action = {
            "http_403": "review_provider_terms_and_official_public_alternative_no_bypass",
            "payload_limit": "review_bounded_streaming_or_official_pagination_keep_byte_cap",
            "http_429": "respect_retry_after_and_lower_request_frequency",
            "fetch_or_parse_error": "inspect_endpoint_and_error_without_disabling_safeguards",
        }[issue]
        issues.append({"source_id": row["source_id"], "issue": issue,
                       "action": action, "access_change_authorized": False})
    return {"schema_version": 1, "issues": issues, "issue_count": len(issues),
            "selection_applied": False}
