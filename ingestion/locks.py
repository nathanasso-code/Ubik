"""Advisory single-writer lock for local POSIX ingestion workers."""
import fcntl
from contextlib import contextmanager
from pathlib import Path

class SourceBusyError(RuntimeError):
    pass

@contextmanager
def source_lock(directory, key):
    from .checkpoints import _validate_key
    _validate_key(key)
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    # Never unlink a lock file: concurrent workers must lock the same inode.
    with (root / (key + ".lock")).open("a+b") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SourceBusyError("Source scope already has an active worker") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
