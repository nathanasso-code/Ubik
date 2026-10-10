"""Append-only local snapshot archive for opt-in ingestion experiments.

A snapshot is immutable once written. Explicit file paths are required to avoid
accidental overwrite; storage does not invoke network or editorial consumers.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def archive_snapshot(snapshot, directory, *, collected_at=None):
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("observations"), list):
        raise ValueError("Expected connector snapshot with observations")
    connector = snapshot.get("connector")
    if not isinstance(connector, str) or not connector.replace("_", "").isalnum():
        raise ValueError("Invalid connector")
    when = collected_at or datetime.now(timezone.utc)
    if when.tzinfo is None:
        raise ValueError("Timestamp must have timezone")
    timestamp = when.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{timestamp}-{connector}-{digest[:12]}.json"
    with target.open("xb") as out:
        out.write(payload + b"\n")
    return {"path": str(target), "sha256": digest, "observations": len(snapshot["observations"]),
            "connector": connector, "collected_at": when.isoformat()}
