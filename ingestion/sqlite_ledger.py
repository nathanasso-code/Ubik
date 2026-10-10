"""Local SQLite transactional ingestion ledger; no network or editorial decisions.

Designed for a single shared SQLite database, not distributed cloud storage.
"""
import hashlib
import json
import sqlite3
import time
from pathlib import Path


class LeaseBusyError(RuntimeError):
    pass


def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    db.execute("PRAGMA busy_timeout=5000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS ingestion_scopes (
            scope_key TEXT PRIMARY KEY,
            cursor TEXT,
            archive_sha256 TEXT,
            lease_owner TEXT,
            lease_until REAL NOT NULL DEFAULT 0,
            lease_epoch INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS ingestion_pages (
            id INTEGER PRIMARY KEY,
            scope_key TEXT NOT NULL REFERENCES ingestion_scopes(scope_key),
            payload_sha256 TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            observed_at REAL NOT NULL,
            UNIQUE(scope_key, payload_sha256)
        );
        CREATE TABLE IF NOT EXISTS ingestion_observations (
            page_id INTEGER NOT NULL REFERENCES ingestion_pages(id),
            position INTEGER NOT NULL,
            connector TEXT NOT NULL,
            source_id TEXT NOT NULL,
            external_id TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY(page_id, position)
        );
        CREATE INDEX IF NOT EXISTS observation_identity
            ON ingestion_observations(connector, source_id, external_id);
    """)
    columns = {row[1] for row in db.execute("PRAGMA table_info(ingestion_scopes)")}
    if "lease_epoch" not in columns:
        db.execute("ALTER TABLE ingestion_scopes ADD COLUMN lease_epoch INTEGER NOT NULL DEFAULT 0")
    return db


def acquire(db, scope_key, owner, *, now=None, ttl=120):
    if not scope_key or not owner or not 1 <= ttl <= 3600:
        raise ValueError("Invalid lease")
    now = time.time() if now is None else now
    db.execute("BEGIN IMMEDIATE")
    try:
        db.execute("INSERT OR IGNORE INTO ingestion_scopes(scope_key) VALUES (?)", (scope_key,))
        row = db.execute("SELECT lease_owner, lease_until, cursor FROM ingestion_scopes WHERE scope_key=?",
                         (scope_key,)).fetchone()
        if row[0] is not None and row[1] > now:
            raise LeaseBusyError("Acquisition scope has an active lease")
        db.execute("UPDATE ingestion_scopes SET lease_owner=?, lease_until=?, lease_epoch=lease_epoch+1 WHERE scope_key=?",
                   (owner, now + ttl, scope_key))
        db.execute("COMMIT")
        return row[2]
    except BaseException:
        db.execute("ROLLBACK")
        raise


def commit_page(db, scope_key, owner, snapshot, next_cursor, *, now=None, ttl=120, epoch=None):
    """Atomically persist a raw page and advance cursor under a valid lease."""
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("observations"), list):
        raise ValueError("Expected snapshot with observations")
    if epoch is not None and (type(epoch) is not int or epoch < 1):
        raise ValueError("Invalid fencing epoch")
    if next_cursor is not None and not isinstance(next_cursor, str):
        raise ValueError("Invalid cursor")
    now = time.time() if now is None else now
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    rows = []
    for position, item in enumerate(snapshot["observations"]):
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k]
            for k in ("connector", "source_id", "external_id")):
            raise ValueError("Observation missing provider identity")
        rows.append((position, item["connector"], item["source_id"],
                     item["external_id"], json.dumps(item, sort_keys=True, ensure_ascii=False)))
    db.execute("BEGIN IMMEDIATE")
    try:
        lease = db.execute("SELECT lease_owner, lease_until, lease_epoch FROM ingestion_scopes WHERE scope_key=?",
                           (scope_key,)).fetchone()
        if not lease or lease[0] != owner or lease[1] <= now or (epoch is not None and lease[2] != epoch):
            raise LeaseBusyError("Missing, expired, or superseded lease")
        cursor = db.execute("INSERT OR IGNORE INTO ingestion_pages(scope_key,payload_sha256,payload_json,observed_at) VALUES (?,?,?,?)",
                            (scope_key, digest, payload, now))
        page_id = db.execute("SELECT id FROM ingestion_pages WHERE scope_key=? AND payload_sha256=?",
                             (scope_key, digest)).fetchone()[0]
        if cursor.rowcount:
            db.executemany("INSERT INTO ingestion_observations VALUES (?,?,?,?,?,?)",
                           [(page_id, *r) for r in rows])
        db.execute("UPDATE ingestion_scopes SET cursor=?, archive_sha256=?, lease_until=? WHERE scope_key=?",
                   (next_cursor, digest, now + ttl, scope_key))
        db.execute("COMMIT")
        return {"page_id": page_id, "sha256": digest, "new_page": bool(cursor.rowcount),
                "observations": len(rows)}
    except BaseException:
        db.execute("ROLLBACK")
        raise


def release(db, scope_key, owner):
    db.execute("UPDATE ingestion_scopes SET lease_owner=NULL, lease_until=0 WHERE scope_key=? AND lease_owner=?",
               (scope_key, owner))


def metrics(db):
    pages = db.execute("SELECT COUNT(*) FROM ingestion_pages").fetchone()[0]
    total = db.execute("SELECT COUNT(*) FROM ingestion_observations").fetchone()[0]
    distinct = db.execute("""SELECT COUNT(*) FROM (
        SELECT connector, source_id, external_id FROM ingestion_observations
        GROUP BY connector, source_id, external_id)""").fetchone()[0]
    return {"pages": pages, "observations": total,
            "unique_provider_identities": distinct, "repeated_observations": total - distinct}
