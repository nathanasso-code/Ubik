"""Static review UI for topic-feed candidates. No automatic publication."""
import argparse
import html
import json
from collections import Counter
from pathlib import Path


def render(report):
    rows = report.get("visible", [])
    esc = lambda v: html.escape(str(v if v is not None else ""), quote=True)
    areas = Counter(area for row in rows for area in row.get("area_ids", []))
    cards = []
    for index, row in enumerate(rows, 1):
        tags = " ".join(f"<span class='tag'>{esc(a)}</span>" for a in row.get("area_ids", []))
        cards.append(
            f"<article><small>#{index} · {esc(row.get('publisher'))} · {esc(row.get('published_raw') or 'data sconosciuta')}</small>"
            f"<h3><a href='{esc(row['url'])}' rel='noopener noreferrer' target='_blank'>{esc(row['title'])}</a></h3>"
            f"<p>{tags or '<span class=tag>area incerta</span>'}</p>"
            f"<small>Fonti di acquisizione: {esc(', '.join(row.get('source_ids', [])))} · "
            "Documento singolo provvisorio · Nessuna verifica di evento, tendenza o credibilità</small></article>"
        )
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ubik · Revisione topic AI</title><style>
:root{{font-family:system-ui,-apple-system,sans-serif;color-scheme:light dark}}
body{{max-width:1080px;margin:0 auto;padding:24px;line-height:1.5}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
article{{padding:18px;border:1px solid #8885;border-radius:12px}}
.tag{{display:inline-block;border:1px solid #8885;border-radius:30px;padding:2px 8px;margin:3px;font-size:.8rem}}
small{{opacity:.75}}a{{color:inherit}}
</style></head><body><h1>Ubik · {esc(report.get('topic', {}).get('name', 'Topic AI'))}</h1>
<p>{esc(report.get('candidate_documents', 0))} documenti candidati · {len(rows)} nel campione · limite {esc(report.get('feed_limit'))}</p>
<p>Anteprima per revisione: nessuna pubblicazione automatica, nessuna card multi-fonte convalidata.
I tag sono euristici; i documenti sono singoli fino alla verifica dello stesso evento.</p>
<h2>Aree presenti nel campione</h2><p>{' · '.join(f'{esc(k)} ({v})' for k,v in areas.most_common()) or 'Nessuna'}</p>
<div class="grid">{''.join(cards)}</div></body></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.report.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    print(f"Topic review HTML: {len(data.get('visible', []))} items")


if __name__ == "__main__":
    main()
