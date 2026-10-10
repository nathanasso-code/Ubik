"""Atomic, resumable checkpoints for independent ingestion.

A checkpoint advances only after its corresponding snapshot has been durably
archived. No editorial state is stored here.
"""
import json
import os
import tempfile
from pathlib import Path


def _validate_key(key):
    if not isinstance(key, str) or not key or len(key) > 160 or not all(
        c.isascii() and (c.isalnum() or c in "-_.") for c in key
    ) or key.startswith("."):
        raise ValueError("Invalid checkpoint key")


def read_checkpoint(directory, key):
    _validate_key(key)
    path = Path(directory) / (key + ".json")
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("key") != key:
        raise ValueError("Checkpoint mismatch")
    return data


def write_checkpoint(directory, key, *, cursor, archive_sha256, archive_path):
    _validate_key(key)
    if cursor is not None and not isinstance(cursor, str):
        raise ValueError("Cursor must be a string or None")
    if not isinstance(archive_sha256, str) or len(archive_sha256) != 64 or any(
        c not in "0123456789abcdef" for c in archive_sha256
    ):
        raise ValueError("Invalid archive digest")
    if not isinstance(archive_path, str) or not archive_path:
        raise ValueError("Missing archive path")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (key + ".json")
    data = {"schema_version": 1, "key": key, "cursor": cursor,
            "archive_sha256": archive_sha256, "archive_path": archive_path}
    fd, temp_name = tempfile.mkstemp(prefix=".checkpoint-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return data
