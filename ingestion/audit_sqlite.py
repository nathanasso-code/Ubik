"""Read-only integrity checks for the experimental SQLite ingestion ledger."""
import hashlib
import json


def audit_ledger(db):
    invalid = []
    pages = db.execute(
        "SELECT id, scope_key, payload_sha256, payload_json FROM ingestion_pages ORDER BY id"
    ).fetchall()
    for page_id, scope, digest, raw in pages:
        try:
            if hashlib.sha256(raw.encode("utf-8")).hexdigest() != digest:
                raise ValueError("Digest mismatch")
            payload = json.loads(raw)
            records = payload["observations"]
            if not isinstance(records, list):
                raise ValueError("Missing observations")
            stored = db.execute(
                "SELECT position, connector, source_id, external_id, payload_json "
                "FROM ingestion_observations WHERE page_id=? ORDER BY position", (page_id,)
            ).fetchall()
            if len(stored) != len(records):
                raise ValueError("Observation count mismatch")
            for index, row in enumerate(stored):
                position, connector, source, external, item_json = row
                item = json.loads(item_json)
                if position != index or item != records[index] or (
                    connector, source, external
                ) != (item.get("connector"), item.get("source_id"), item.get("external_id")):
                    raise ValueError("Observation content mismatch")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            invalid.append({"page_id": page_id, "scope_key": scope,
                            "error": type(exc).__name__})
    scopes = db.execute(
        "SELECT scope_key, archive_sha256 FROM ingestion_scopes "
        "WHERE archive_sha256 IS NOT NULL"
    ).fetchall()
    missing_heads = [scope for scope, digest in scopes if not db.execute(
        "SELECT 1 FROM ingestion_pages WHERE scope_key=? AND payload_sha256=?",
        (scope, digest)
    ).fetchone()]
    return {"pages_checked": len(pages), "invalid_pages": invalid,
            "scopes_with_missing_head": missing_heads,
            "integrity_ok": not invalid and not missing_heads}
