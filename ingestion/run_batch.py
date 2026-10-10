"""Opt-in bounded, resumable acquisition runner.

One configured provider per run; provider failures never advance checkpoints.
No background scheduler, ranking, publication or clustering.
"""
import argparse
import hashlib
import json
import time
import uuid
from datetime import date
from pathlib import Path

from .archive import archive_snapshot
from .budgets import SourceBudget
from .checkpoints import read_checkpoint, write_checkpoint
from .locks import source_lock
from .sqlite_ledger import connect as connect_ledger
from .sqlite_store import SQLiteStore
from .public_adapters import (bluesky_collect, crossref_collect,
                              mastodon_collect, openalex_collect)


def _run_pages_unlocked(provider, *, source, archive_dir, checkpoint_dir, max_pages=2,
              page_size=20, from_date=None, to_date=None, pause_seconds=1,
              fetchers=None, sleep=time.sleep, ledger=None, initial_cursor=None, store=None, lease=None):
    if provider not in {"bluesky", "mastodon", "openalex", "crossref"}:
        raise ValueError("Unsupported provider")
    if not isinstance(source, str) or not source:
        raise ValueError("Source must be provided")
    if type(max_pages) is not int or not 1 <= max_pages <= 20:
        raise ValueError("max_pages must be 1..20")
    if type(page_size) is not int or not 1 <= page_size <= 20:
        raise ValueError("page_size must be 1..20")
    if pause_seconds < 0.5:
        raise ValueError("Minimum inter-page pause is 0.5 seconds")
    if provider in {"openalex", "crossref"}:
        if not from_date or not to_date:
            raise ValueError("Scholarly sources require explicit date window")
        if date.fromisoformat(from_date) > date.fromisoformat(to_date):
            raise ValueError("Invalid date window")
    scope = {"provider": provider, "source": source,
             "from_date": from_date if provider in {"openalex", "crossref"} else None,
             "to_date": to_date if provider in {"openalex", "crossref"} else None}
    key = provider + "-" + hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()[:24]
    checkpoint = read_checkpoint(checkpoint_dir, key) if ledger is None and store is None else None
    cursor = checkpoint["cursor"] if checkpoint else initial_cursor
    if checkpoint and cursor is None and provider in {"openalex", "crossref"}:
        return {"provider": provider, "source": source, "pages": 0,
                "observations": 0, "status": "completed", "checkpoint": key}
    budget = SourceBudget(source, max_requests=max_pages, max_observations=max_pages * page_size)
    fetchers = fetchers or {}
    archived = []
    status = "budget_exhausted"
    for page in range(max_pages):
        if not budget.may_request():
            break
        budget.record_request()
        if provider == "bluesky":
            call = fetchers.get(provider, bluesky_collect)
            result = call(source, limit=page_size, cursor=cursor)
            next_cursor = result.get("next_cursor")
        elif provider == "mastodon":
            call = fetchers.get(provider, mastodon_collect)
            result = call(source, limit=page_size, max_id=cursor)
            next_cursor = result.get("next_max_id")
        elif provider == "openalex":
            call = fetchers.get(provider, openalex_collect)
            result = call(from_date, to_date, per_page=page_size, cursor=cursor or "*")
            next_cursor = result.get("next_cursor")
        else:
            call = fetchers.get(provider, crossref_collect)
            result = call(from_date, to_date, rows=page_size, cursor=cursor or "*")
            next_cursor = result.get("next_cursor")
        records = result.get("observations")
        if not isinstance(records, list) or len(records) > page_size:
            raise ValueError("Unexpected provider page size")
        budget.record_result(len(records))
        # Cursor-based APIs can supply a cursor even on a short/empty final page.
        # An empty page is terminal; a short Crossref page ends the interval.
        if not records and not result.get("next_cursor") and not result.get("next_max_id"):
            next_cursor = None
        if provider == "crossref" and len(records) < page_size and result.get("invalid", 0) == 0:
            next_cursor = None
        if next_cursor == cursor and next_cursor is not None:
            next_cursor = None
        if store is not None:
            saved = store.commit(lease, result, next_cursor)
            archive = {"page_id": saved["page_id"], "sha256": saved["sha256"],
                       "observations": saved["observations"], "new_page": saved["new_page"]}
        elif ledger is None:
            archive = archive_snapshot(result, archive_dir)
            write_checkpoint(checkpoint_dir, key, cursor=next_cursor,
                             archive_sha256=archive["sha256"], archive_path=archive["path"])
        archived.append(archive)
        if not next_cursor or next_cursor == cursor:
            status = "completed"
            break
        cursor = next_cursor
        if page + 1 < max_pages:
            sleep(pause_seconds)
    return {"provider": provider, "source": source, "pages": len(archived),
            "observations": budget.observations, "status": status,
            "checkpoint": key, "archives": archived, "budget": budget.report()}


def run_pages(provider, *, source, archive_dir, checkpoint_dir, max_pages=2,
              page_size=20, from_date=None, to_date=None, pause_seconds=1,
              fetchers=None, sleep=time.sleep, ledger=None, store=None):
    """Serialize the entire read/fetch/archive/checkpoint transaction by scope."""
    scope = {"provider": provider, "source": source,
             "from_date": from_date if provider in {"openalex", "crossref"} else None,
             "to_date": to_date if provider in {"openalex", "crossref"} else None}
    key = str(provider) + "-" + hashlib.sha256(
        json.dumps(scope, sort_keys=True).encode()).hexdigest()[:24]
    args = dict(source=source, archive_dir=archive_dir, checkpoint_dir=checkpoint_dir,
                max_pages=max_pages, page_size=page_size, from_date=from_date,
                to_date=to_date, pause_seconds=pause_seconds, fetchers=fetchers, sleep=sleep)
    if ledger is not None and store is not None:
        raise ValueError("Choose either ledger or store")
    if ledger is None and store is None:
        with source_lock(checkpoint_dir, key):
            return _run_pages_unlocked(provider, **args)
    storage = store if store is not None else SQLiteStore(ledger)
    lease = storage.acquire(key)
    try:
        if provider in {"crossref", "openalex"} and lease.cursor is None:
            # A completed scientific window has a committed page but no cursor.
            db = getattr(storage, "db", None)
            if db is not None:
                previous = db.execute(
                    "SELECT archive_sha256 FROM ingestion_scopes WHERE scope_key=?", (key,)
                ).fetchone()
                if previous and previous[0] is not None:
                    return {"provider": provider, "source": source, "pages": 0,
                            "observations": 0, "status": "completed", "checkpoint": key}
        return _run_pages_unlocked(provider, **args, ledger=ledger,
                                   initial_cursor=lease.cursor, store=storage, lease=lease)
    finally:
        storage.release(lease)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("provider", choices=("bluesky", "mastodon", "openalex", "crossref"))
    p.add_argument("--source", required=True, help="Actor, instance or scholarly registry label")
    p.add_argument("--from-date")
    p.add_argument("--to-date")
    p.add_argument("--max-pages", type=int, default=2)
    p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--archive-dir", type=Path, default=Path("data/discovery/runs"))
    p.add_argument("--checkpoint-dir", type=Path, default=Path("data/discovery/checkpoints"))
    p.add_argument("--live", action="store_true")
    p.add_argument("--sqlite-ledger", type=Path, help="Opt-in local transactional SQLite storage")
    args = p.parse_args()
    if not args.live:
        print("Dry run: add --live to acquire public metadata.")
        return
    db = connect_ledger(args.sqlite_ledger) if args.sqlite_ledger else None
    try:
        report = run_pages(args.provider, source=args.source, archive_dir=args.archive_dir,
                           checkpoint_dir=args.checkpoint_dir, max_pages=args.max_pages,
                           page_size=args.page_size, from_date=args.from_date, to_date=args.to_date,
                           ledger=db)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    main()
