"""Offline acquisition readiness summary, deliberately fail-closed for production."""
from pathlib import Path


def readiness(root):
    root = Path(root)
    required = [
        "ingestion/payload_codec.py",
        "ingestion/storage_contract.py",
        "ingestion/sqlite_store.py",
        "ingestion/audit_sqlite.py",
        "ingestion/social_lifecycle.py",
        "ingestion/postgres/schema.sql",
        "ingestion/postgres/transaction_templates.sql",
        "docs/INGESTION_PRODUCTION_READINESS.md",
    ]
    present = {path: (root / path).is_file() for path in required}
    blocking = [
        "postgres_adapter_not_implemented_or_integration_tested",
        "distributed_lease_renewal_and_fencing_not_verified",
        "social_erasure_and_backup_propagation_not_implemented",
        "privacy_security_source_terms_not_approved",
        "unattended_scheduler_not_approved",
    ]
    return {"scope": "ingestion", "development_artifacts": present,
            "missing_development_artifacts": [p for p, ok in present.items() if not ok],
            "production_ready": False, "production_blockers": blocking,
            "network_calls": 0, "deployment_changes": 0}
