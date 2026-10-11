"""Human-readable, searchable full acquisition catalogue; no editorial deletions."""
import argparse
import html
import json
from pathlib import Path


def render(report):
    items = report.get("items", [])
    cards = []
    for row in items:
        title = html.escape(row.get("title") or "")
        url = html.escape(row.get("url") or "", quote=True)
        source = html.escape(", ".join(row.get("source_ids") or []))
        publisher = html.escape(row.get("publisher") or "")
        date = html.escape(row.get("published_raw") or "Data non disponibile")
        description = html.escape((row.get("description") or "")[:800])
        hint = html.escape(row.get("relevance_hint") or "")
        search = html.escape(" ".join((title, publisher, source, description)).casefold(), quote=True)
        cards.append(f'<article class="entry" data-hint="{hint}" data-search="{search}"><h2><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h2><p class="meta">{publisher} · {source} · {date}</p><p>{description}</p><small>{hint} · Fonte originale, non verificata editorialmente</small></article>')
    return """<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ubik · Catalogo completo delle fonti</title><style>
:root{font-family:system-ui,sans-serif;color-scheme:light dark}body{max-width:1050px;margin:auto;padding:2rem 1rem;line-height:1.55}h1{font-size:2rem}header{position:sticky;top:0;background:Canvas;padding:1rem 0;border-bottom:1px solid #8885}input,select{font:inherit;padding:.65rem;border-radius:.5rem;border:1px solid #8888;max-width:100%}input{width:65%}.entry{padding:1rem 0;border-bottom:1px solid #8885}.entry h2{font-size:1.08rem;margin:0}.entry p{margin:.5rem 0}.meta,small{opacity:.7}a{color:LinkText}#count{font-weight:bold}
</style></head><body><h1>Ubik · Catalogo delle fonti raccolte</h1><p>Archivio di documenti originali, non selezione editoriale. La presenza di un segnale AI non dimostra la pertinenza. Nessun documento è approvato automaticamente.</p><header><label for="q">Cerca titoli, fonti, descrizioni</label><p><input id="q" type="search" placeholder="Parola o autore"><select id="hint"><option value="">Tutte le fonti</option><option value="explicit_ai_signal">Con segnale AI</option><option value="needs_topic_review">Da valutare</option></select></p><span id="count"></span></header><main id="entries">""" + "\n".join(cards) + """</main><script>
const rows=Array.from(document.querySelectorAll('.entry')),q=document.getElementById('q'),hint=document.getElementById('hint'),count=document.getElementById('count');
function update(){const terms=q.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);let n=0;for(const row of rows){const show=(!hint.value||row.dataset.hint===hint.value)&&terms.every(term=>row.dataset.search.includes(term));row.hidden=!show;if(show)n++;}count.textContent=n+' di '+rows.length+' documenti';}q.addEventListener('input',update);hint.addEventListener('change',update);update();
</script></body></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.catalog.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(report), encoding="utf-8")
    print(json.dumps({"html_catalogue_documents": len(report.get("items", []))}))


if __name__ == "__main__":
    main()
