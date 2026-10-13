"""Offline, escaped HTML editorial feed from the frozen transparent catalog."""
import argparse,html,json
from pathlib import Path

STYLE="""body{margin:0;background:#0d111b;color:#e7eefa;font:15px/1.5 system-ui,sans-serif}header{background:#151c29;border-bottom:1px solid #313b50;padding:25px max(20px,calc((100vw - 1180px)/2))}h1{margin:0;font-size:30px}main{max-width:1180px;margin:auto;padding:25px 20px}.muted{color:#a3b1c7}.stats,.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.stat,.card,.note{background:#161f2e;border:1px solid #344057;border-radius:12px;padding:16px}.stat b{display:block;font-size:25px}.cards{grid-template-columns:repeat(3,minmax(0,1fr))}.card h3{font-size:17px;line-height:1.3}.card a{color:#a4d4ff}.tag{color:#89e4be;font-size:12px}input,select{background:#151d2b;border:1px solid #45526a;color:white;border-radius:9px;padding:12px;font:inherit}input{flex:1}.controls{display:flex;gap:10px;margin:24px 0}.note{margin:22px 0}.card p{color:#b5c1d2}.footer{border-top:1px solid #344057;padding-top:10px}@media(max-width:900px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){.cards{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.controls{flex-direction:column}}"""
def render(catalog,probe=None):
    docs=catalog["documents"];groups=catalog["multi_source_candidates"]
    grouped={u for g in groups for u in g["source_urls"]}
    group_by_url={u:g for g in groups for u in g["source_urls"]}
    probes={x["url"]:x for x in (probe or {}).get("probes",[])}
    data=[]
    for d in docs:
        p=probes.get(d["url"])
        g=group_by_url.get(d["url"])
        data.append({"title":d.get("title") or "Senza titolo","url":d["url"],
           "publisher":d.get("publisher") or d.get("source_id") or "Fonte",
           "description":d.get("description") or "",
           "tier":d["content_tier"],"kind":"candidate" if g else "single",
           "related":next((u for u in g["source_urls"] if u!=d["url"]),None) if g else None,
           "http":p.get("http_status") if p else None,"tested":bool(p)})
    count=catalog["coverage"]
    safe=json.dumps(data,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    page="""<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ubik — Catalogo sperimentale</title><style>"""+STYLE+"""</style><header><h1>Ubik <span style="color:#89e4be">/ Research Feed</span></h1><div class="muted">Corpus sperimentale di fonti RSS · stato di accesso documentato</div></header><main><div class="stats"><div class="stat"><b>"""+str(len(docs))+"""</b>URL distinti</div><div class="stat"><b>"""+str(len(groups))+"""</b>Accorpamenti candidati</div><div class="stat"><b>"""+str(len(docs)-len(grouped))+"""</b>Fonti singole</div><div class="stat"><b>"""+str((probe or {}).get("coverage",{}).get("url_probes",0))+"""</b>HEAD testati</div></div><div class="note"><b>Nota metodologica.</b> Le descrizioni sono tratte dai feed degli editori. Nessuna card è una sintesi verificata; i raggruppamenti sono suggerimenti di similarità dei titoli. I test HTTP HEAD, dove presenti, non dimostrano accessibilità del corpo o diritti di ripubblicazione. Zero testi integrali acquisiti e zero affermazioni verificate. I link aprono le fonti originali.</div><div class="controls"><input id="q" placeholder="Cerca titolo, editore, descrizione..."><select id="kind"><option value="all">Tutte le fonti</option><option value="candidate">Possibili accorpamenti</option><option value="single">Fonti singole</option></select><select id="tier"><option value="all">Tutti i livelli</option><option value="rss_extended_description">Descrizione estesa RSS</option><option value="rss_short_description">Descrizione breve RSS</option><option value="metadata_only">Solo metadati</option></select></div><p class="muted" id="count"></p><div class="cards" id="cards"></div></main><script type="application/json" id="payload">"""+safe+"""</script><script>const data=JSON.parse(document.getElementById('payload').textContent);const q=document.getElementById('q'),kind=document.getElementById('kind'),tier=document.getElementById('tier');function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function draw(){const query=q.value.toLowerCase();const rows=data.filter(x=>(kind.value==='all'||x.kind===kind.value)&&(tier.value==='all'||x.tier===tier.value)&&(x.title+' '+x.publisher+' '+x.description).toLowerCase().includes(query));document.getElementById('count').textContent=rows.length+' fonti visualizzate';document.getElementById('cards').innerHTML=rows.slice(0,600).map(x=>'<article class="card"><div class="tag">'+(x.kind==='candidate'?'POSSIBILE ACCORPAMENTO · NON VERIFICATO':'FONTE ORIGINALE')+'</div><h3>'+esc(x.title)+'</h3><small>'+esc(x.publisher)+'</small><p>'+esc(x.description.slice(0,300)||'Nessuna descrizione disponibile')+'</p><div class="footer"><small>Contenuto: '+esc(x.tier)+' · HTTP: '+(x.tested?esc(x.http||'errore'):'non testato')+'</small><p><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer">Apri articolo ↗</a>'+(x.related?' · <a href="'+esc(x.related)+'" target="_blank" rel="noopener noreferrer">Fonte associata ↗</a>':'')+'</p></div></article>').join('')};[q,kind,tier].forEach(x=>x.addEventListener(x===q?'input':'change',draw));draw()</script></html>"""
    return page

def main():
    p=argparse.ArgumentParser();p.add_argument("catalog",type=Path)
    p.add_argument("--probe",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();d=json.loads(a.catalog.read_text())
    pr=json.loads(a.probe.read_text()) if a.probe and a.probe.exists() else None
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(render(d,pr),encoding="utf-8")
    print(json.dumps({"html_bytes":a.output.stat().st_size,"documents":len(d["documents"])}))
if __name__=="__main__":main()
