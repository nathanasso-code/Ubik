"""Create a static, local HTML preview of actually collected source metadata.

No LLM, clustering, ranking, remote scripts or editorial selection. Output is
plain escaped HTML, safe to open from a downloaded CI artifact.
"""
import argparse
import html
import json
from collections import Counter, deque
from pathlib import Path


def render(discovery, *, max_items=250):
    if not isinstance(discovery.get("items"), list):
        raise ValueError("Expected RSS discovery items")
    items = discovery["items"]
    counts = Counter(x.get("source_id", "unknown") for x in items)
    reports = {x["source_id"]: x for x in discovery.get("source_reports", [])}
    sources = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    def esc(value):
        return html.escape(str(value or ""), quote=True)
    source_rows = []
    for source, count in sources:
        report = reports.get(source, {})
        source_rows.append(f"<tr><td>{esc(source)}</td><td>{count}</td><td>{esc(report.get('status', 'unknown'))}</td></tr>")
    errors = []
    for row in discovery.get("source_reports", []):
        if row.get("status") != "ok":
            errors.append(f"<li><b>{esc(row.get('source_id'))}</b>: {esc(row.get('error', 'unknown error'))}</li>")
    cards = []
    # Presentation-only round-robin: do not let a large feed hide all others.
    # Acquisition data remains unchanged and no editorial scores are assigned.
    grouped = {}
    for item in items:
        grouped.setdefault(item.get("source_id", "unknown"), deque()).append(item)
    selected = []
    active = deque(sorted(grouped))
    while active and len(selected) < max_items:
        source = active.popleft()
        selected.append(grouped[source].popleft())
        if grouped[source]:
            active.append(source)
    for item in selected:
        url = str(item.get("url") or "")
        if not url.startswith(("https://", "http://")):
            continue
        cards.append(f'<article><small>{esc(item.get("publisher"))} · {esc(item.get("published_raw") or "data non indicata")}</small>'
                     f'<h3><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(item.get("title"))}</a></h3>'
                     f'<p>{esc(str(item.get("description") or "")[:300])}</p></article>')
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ubik · Anteprima raccolta fonti</title>
<style>
:root{{font-family:system-ui,-apple-system,sans-serif;color-scheme:light dark}}
body{{max-width:1060px;margin:0 auto;padding:28px;line-height:1.5}}
header{{border-bottom:1px solid #8886;padding-bottom:20px}}
small,.muted{{opacity:.7}} .stats{{font-size:1.25rem;font-weight:650}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}
article{{border:1px solid #8885;border-radius:14px;padding:18px}}
h3{{font-size:1.05rem}} a{{color:inherit}} table{{border-collapse:collapse;width:100%}}
td,th{{padding:7px 12px;border-bottom:1px solid #8884;text-align:left}}
</style></head><body>
<header><h1>Ubik · Materiale realmente raccolto</h1>
<p class="stats">{len(items):,} osservazioni · {len(sources)} fonti con risultati · {len(discovery.get("source_reports", []))} feed tentati</p>
<p class="muted">Acquisizione: {esc(discovery.get("retrieved_at"))}. Campione RSS/Atom del registro ai-models.
Anteprima bilanciata tra fonti di {min(len(items), max_items)} elementi, senza selezione per rilevanza.
Non è ancora la UI definitiva, né una copertura globale.</p></header>
<section><h2>Fonti e quantità</h2><table><thead><tr><th>Fonte</th><th>Osservazioni</th><th>Stato</th></tr></thead>
<tbody>{''.join(source_rows)}</tbody></table></section>
<section><h2>Problemi di acquisizione</h2><ul>{''.join(errors) or '<li>Nessun errore riportato</li>'}</ul></section>
<section><h2>Anteprima degli articoli</h2><div class="grid">{''.join(cards)}</div></section>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("discovery", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-items", type=int, default=250)
    args = parser.parse_args()
    if not 1 <= args.max_items <= 1000:
        parser.error("--max-items must be 1..1000")
    data = json.loads(args.discovery.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data, max_items=args.max_items), encoding="utf-8")
    print(f"Preview created: {args.output}; observations: {len(data['items'])}")


if __name__ == "__main__":
    main()
