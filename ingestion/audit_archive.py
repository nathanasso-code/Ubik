"""Read-only audit pipeline for archived acquisition snapshots.

Does not call external APIs or select stories.
"""
import argparse
import hashlib
import re
import json
from pathlib import Path

from .audit import audit
from .federate import federate


def audit_directory(directory, *, output=None):
    root = Path(directory).resolve()
    files = sorted(root.glob("*.json"))
    snapshots, invalid_files = [], []
    for path in files:
        try:
            raw = path.read_bytes()
            match = re.fullmatch(r"\\d{8}T\\d{12}Z-[a-zA-Z0-9_]+-([0-9a-f]{12})\\.json", path.name)
            if match and hashlib.sha256(raw.rstrip(b"\\n")).hexdigest()[:12] != match.group(1):
                raise ValueError("Archive checksum mismatch")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Snapshot is not an object")
            snapshots.append((path.name, data))
        except (ValueError, OSError) as exc:
            invalid_files.append({"file": path.name, "error": type(exc).__name__})
    merged = federate(snapshots)
    report = audit(merged)
    report["snapshot_files"] = len(files)
    report["invalid_snapshot_files"] = invalid_files
    report["federation_errors"] = merged["errors"]
    if output is not None:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive_dir", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    print(json.dumps(audit_directory(args.archive_dir, output=args.output),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
