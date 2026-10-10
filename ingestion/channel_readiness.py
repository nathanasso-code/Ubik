"""Explain acquisition coverage without turning provider failures into missing news."""
from collections import Counter


def assess_channels(inventory, *, live_evidence=None):
    evidence = live_evidence or {}
    declared = inventory["capabilities"]
    result = []
    for provider in declared:
        name = provider["provider"]
        recorded = evidence.get(name, provider.get("live_evidence"))
        status = (recorded or {}).get("status", "not_tested")
        result.append({
            "provider": name,
            "adapter_present": provider["implementation_present"],
            "last_evidence_status": status,
            "sample_observations": (recorded or {}).get("observations"),
            "sampling_scope": provider["coverage_limit"],
            "continuous_coverage_verified": False,
            "next_verification": (
                "investigate_http_422_within_instance_policy" if name == "mastodon" else
                "run_bounded_provider_specific_live_test" if status == "not_tested" else
                "verify_freshness_and_provider_specific_scope"),
        })
    return {
        "schema_version": 1,
        "scope": "provider_capability_not_global_news_recall",
        "channels": result,
        "not_yet_implemented": inventory["unrepresented_channels"],
        "warnings": [
            "Historic one-time smoke tests are not continuous coverage.",
            "An API failure is not proof of no available content.",
            "No automatic social archival or deletion reconciliation is enabled.",
        ],
    }
