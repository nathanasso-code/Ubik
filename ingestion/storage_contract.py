"""Provider-independent acquisition persistence protocol.

Implementations must guarantee that committing a page and advancing its cursor
is one atomic operation, guarded by an exclusive owner and fencing token.
"""
from typing import Any, Protocol


class AcquisitionStore(Protocol):
    def acquire(self, scope_key: str) -> "Lease":
        """Claim a scope or raise a busy error."""

    def commit(self, lease: "Lease", snapshot: dict[str, Any],
               next_cursor: str | None) -> dict[str, Any]:
        """Atomically store page + cursor; reject stale leases."""

    def release(self, lease: "Lease") -> None:
        """Release only the matching lease."""


class Lease:
    def __init__(self, scope_key: str, owner: str, epoch: int, cursor: str | None):
        self.scope_key = scope_key
        self.owner = owner
        self.epoch = epoch
        self.cursor = cursor
