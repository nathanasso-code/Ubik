"""Read-only command line audit of a local SQLite ingestion ledger."""
import argparse
import json
import sqlite3
from pathlib import Path

from .audit_sqlite import audit_ledger
from .sqlite_ledger import metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error("SQLite database does not exist")
    # SQLite URI mode=ro avoids silently creating a missing database.
    db = sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        result = {"storage": "sqlite", "metrics": metrics(db),
                  "integrity": audit_ledger(db)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        db.close()


if __name__ == "__main__":
    main()
