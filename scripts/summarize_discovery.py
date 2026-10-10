#!/usr/bin/env python3
"""Readable summary of exploratory discovery artifacts; no endorsement or auto-promotion."""
import json
import sys
from pathlib import Path

def summarize(folder):
    folder = Path(folder)
    lines = ["## Ubik — exploratory source discovery", "", "All results are candidates, not verified expertise or approved publications.", ""]
    files = [
        ("ai-models.json", "RSS/Atom acquisition"),
        ("ai-author-candidates.json", "Author names"),
        ("italian-feed-candidates.json", "Italian site feed autodiscovery"),
        ("social-author-candidates.json", "Bluesky and Mastodon profile search"),
        ("ai-relevance-review.json", "Feed title and description relevance review"),
        ("article-attribution-audit.json", "Article page authorship sample")
    ]
    for filename, label in files:
        path = folder / filename
        if not path.exists():
            lines.append(f"- **{label}:** report not generated")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if filename == "ai-models.json":
                c = data.get("coverage", {})
                detail = f"{c.get('successful_feeds', 0)}/{c.get('enabled_feeds', 0)} feeds working; {c.get('stored_items', 0)} source observations; {c.get('unique_article_urls', len({item.get('url') for item in data.get('items', []) if item.get('url')}))} unique article URLs; {c.get('items_with_named_author', 0)} observations with bylines"
            elif filename == "ai-author-candidates.json":
                detail = f"{data.get('candidate_count', 0)} name-based candidates (identity unverified)"
            elif filename == "italian-feed-candidates.json":
                rows = data.get("results", [])
                counts = {s: sum(x.get("status") == s for x in rows) for s in ("found", "not_advertised", "error")}
                detail = f"{len(rows)} sites checked; {counts['found']} advertise feeds; {counts['not_advertised']} without advertised feeds; {counts['error']} errors"
            elif filename == "social-author-candidates.json":
                rows = data.get("candidates", [])
                counts = {s: sum(x.get("platform") == s for x in rows) for s in ("bluesky", "mastodon")}
                detail = f"{counts['bluesky']} Bluesky + {counts['mastodon']} Mastodon candidate profiles; {len(data.get('errors', []))} search errors"
            elif filename == "article-attribution-audit.json":
                rows = data.get("results", [])
                statuses = ("page_author_candidate", "not_found_in_page_metadata", "fetch_error")
                detail = f"{len(rows)} pages sampled; " + ", ".join(f"{s}: {sum(r.get('status') == s for r in rows)}" for s in statuses)
                by_source = {}
                for row in rows:
                    source = row.get("source_id", "unknown")
                    by_source.setdefault(source, {s: 0 for s in statuses})
                    if row.get("status") in statuses:
                        by_source[source][row["status"]] += 1
                lines.append("")
                lines.append("| Source | Sample | Page byline candidate | Not in metadata | Fetch error |")
                lines.append("|---|---:|---:|---:|---:|")
                for source, counts in sorted(by_source.items()):
                    safe_source = str(source).replace("|", "/").replace("\\n", " ")
                    lines.append(f"| {safe_source} | {sum(counts.values())} | {counts['page_author_candidate']} | {counts['not_found_in_page_metadata']} | {counts['fetch_error']} |")
                lines.append("")
            else:
                detail = ", ".join(f"{k}: {v}" for k, v in data.get("counts", {}).items())
            lines.append(f"- **{label}:** {detail}")
        except (ValueError, OSError) as exc:
            lines.append(f"- **{label}:** unreadable ({type(exc).__name__})")
    lines += ["", "A successful workflow does not imply every feed or social API worked. Inspect individual error reports in the downloadable artifact."]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    print(summarize(sys.argv[1] if len(sys.argv) > 1 else "data/discovery"))
