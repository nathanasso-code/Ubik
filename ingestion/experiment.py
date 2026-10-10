"""Explicitly opt-in, bounded heterogeneous ingestion experiment runner."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .audit_archive import audit_directory
from .experiment_plan import validate_plan
from .run_batch import run_pages


def run_experiment(plan, *, archive_dir, checkpoint_dir, live=False, runner=run_pages):
    sources = validate_plan(plan)
    estimated_requests = sum(s["max_pages"] for s in sources)
    if not live:
        return {"status": "dry_run", "sources": sources,
                "maximum_page_requests": estimated_requests,
                "network_calls": 0}
    results = []
    for item in sources:
        try:
            result = runner(item["provider"], source=item["source"],
                            archive_dir=archive_dir, checkpoint_dir=checkpoint_dir,
                            max_pages=item["max_pages"], page_size=item["page_size"],
                            from_date=item["from_date"], to_date=item["to_date"])
            results.append({"provider": item["provider"], "source": item["source"],
                            "status": "ok", "result": result})
        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
            results.append({"provider": item["provider"], "source": item["source"],
                            "status": "error", "error_type": type(exc).__name__})
    report = audit_directory(archive_dir)
    return {"schema_version": 1, "status": "finished_with_errors" if any(
            x["status"] == "error" for x in results) else "finished",
            "sources": results, "maximum_page_requests": estimated_requests,
            "coverage": report, "completed_at": datetime.now(timezone.utc).isoformat()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--archive-dir", type=Path, default=Path("data/discovery/runs"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("data/discovery/checkpoints"))
    parser.add_argument("--report", type=Path, default=Path("data/discovery/experiment-report.json"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    result = run_experiment(plan, archive_dir=args.archive_dir,
                            checkpoint_dir=args.checkpoint_dir, live=args.live)
    if args.live:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
