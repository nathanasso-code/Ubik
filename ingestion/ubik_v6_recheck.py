"""Re-apply the current code controls (repair, controls, gate, display rule) to pages already composed and paid for.
No model calls. Writes RUN-recheck.json next to the run and prints what changed in the highlighted facts.

Usage: python -m ingestion.ubik_v6_recheck RUN.json SELECTION.json
"""
import json
import sys
from pathlib import Path

from ingestion.ubik_v6_editorial import controls, date_and_duplicate_checks, gate, rank_facts, render, repair


def main(run_path, selection_path):
    run = json.loads(Path(run_path).read_text())
    items = {i["item_id"]: i for i in json.loads(Path(selection_path).read_text())["items"]}
    schede = run["schede"]
    report, done_runs = [], set()
    for page in run["pages"]:
        if "error" in page.get("controls", {}):
            continue
        before = {f["id"]: (f.get("highlight"), f.get("independent_count"), f.get("status")) for f in page["facts"]}
        earlier = page.get("repairs", [])
        repair(page, schede, items)
        page["repairs"] = earlier + [r for r in page["repairs"] if r not in earlier and r.get("added") != "excluded_non_valutato"]
        page["controls"] = controls(page, schede, items)
        page["controls"].update(date_and_duplicate_checks(page, schede, items))
        page["rejected_by_gate"] = gate(page)
        was = page.get("accepted")
        # as in production: the first attempt that passes the gate is the run's page, later attempts are moot
        page["accepted"] = not page["rejected_by_gate"] and page["run"] not in done_runs
        if page["accepted"]:
            done_runs.add(page["run"])
        rank_facts(page, (run.get("window") or [None])[0])
        after = {f["id"]: (f.get("highlight"), f.get("independent_count"), f.get("status")) for f in page["facts"]}
        report.append({"run": page["run"], "attempt": page["attempt"], "accepted_before": was, "accepted_after": page["accepted"],
                       "gate": page["rejected_by_gate"],
                       "removed_facts": sorted(set(before) - set(after)),
                       "changed": {k: {"before": before[k], "after": after[k]} for k in after if before.get(k) != after[k]},
                       "highlight": [f["id"] for f in page["facts"] if f.get("highlight")]})
    run["recheck"] = report
    out = Path(run_path).with_name(Path(run_path).stem + "-recheck.json")
    out.write_text(json.dumps(run, ensure_ascii=False, indent=1) + "\n")
    for page in run["pages"]:
        if page.get("accepted"):
            Path(run_path).with_name(Path(run_path).stem + f"-recheck-page{page['run']}.md").write_text(
                render(page, items, run["arm"], page["run"]))
            break
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
