"""Canonical JSON payload encoding shared by ingestion persistence adapters."""
import hashlib
import json


def canonical_payload(snapshot):
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("observations"), list):
        raise ValueError("Expected observation snapshot")
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return payload, hashlib.sha256(payload).hexdigest()
