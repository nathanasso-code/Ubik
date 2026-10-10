"""AcquisitionStore implementation backed by the local SQLite ledger."""
import uuid

from .sqlite_ledger import acquire, commit_page, release
from .storage_contract import Lease


class SQLiteStore:
    def __init__(self, db, *, ttl=3600):
        if not 1 <= ttl <= 3600:
            raise ValueError("Invalid lease TTL")
        self.db = db
        self.ttl = ttl

    def acquire(self, scope_key):
        owner = uuid.uuid4().hex
        cursor = acquire(self.db, scope_key, owner, ttl=self.ttl)
        epoch = self.db.execute(
            "SELECT lease_epoch FROM ingestion_scopes WHERE scope_key=?",
            (scope_key,)
        ).fetchone()[0]
        return Lease(scope_key, owner, epoch, cursor)

    def commit(self, lease, snapshot, next_cursor):
        return commit_page(self.db, lease.scope_key, lease.owner, snapshot,
                           next_cursor, epoch=lease.epoch, ttl=self.ttl)

    def release(self, lease):
        release(self.db, lease.scope_key, lease.owner)
