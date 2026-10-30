"""Ubik v6 matrices (code, no model): chain weekly facts linked by "continues" into running stories (vicende).

Usage: python -m ingestion.ubik_v6_matrices OUT.md WEEK1.json WEEK2.json ...  (oldest first)
Each week file is a v6 run; its first accepted page is used.
"""
import json
import sys
from pathlib import Path


def main(out_path, *week_files):
    nodes, edges = {}, []
    for wf in week_files:
        d = json.loads(Path(wf).read_text())
        page = next((p for p in d.get("pages", []) if p.get("accepted")), None)
        if not page:
            continue
        wk = (d.get("window") or ["?"])[0]
        for f in page["facts"]:
            fid = f"{wk}:{f.get('id')}"
            nodes[fid] = {"week": wk, "statement": f.get("statement"), "date": f.get("date"), "status": f.get("status"),
                          "type": f.get("type"), "sources": sorted({r.get("item_id") for r in f.get("items", [])})}
            if f.get("continues"):
                edges.append((f["continues"], fid))
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    groups = {}
    for n in nodes:
        groups.setdefault(find(n), []).append(n)
    vicende = [sorted(g, key=lambda n: (nodes[n]["week"], nodes[n]["date"] or "")) for g in groups.values() if len(g) > 1]
    lines = ["# Vicende in corso (matrici v6)", "",
             f"{len(nodes)} fatti in {len(week_files)} settimane; {len(edges)} collegamenti \"prosegue\"; {len(vicende)} vicende.", ""]
    for i, v in enumerate(vicende, 1):
        lines += [f"## Vicenda {i}", ""]
        for n in v:
            x = nodes[n]
            lines.append(f"- **{x['week']}** — {x['statement']} ({x['date'] or 's.d.'}; {x['status']}; fonti: {len(x['sources'])})")
        lines.append("")
    Path(out_path).write_text("\n".join(lines) + "\n")
    Path(out_path).with_suffix(".json").write_text(json.dumps({"nodes": nodes, "edges": edges, "vicende": vicende}, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"facts": len(nodes), "links": len(edges), "vicende": len(vicende)}))


if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])
