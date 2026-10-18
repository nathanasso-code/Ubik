"""Standalone HTML comparison of retrieval, metadata-Qwen and text-Qwen.

Comparison uses identical eligible pairs; no ground-truth accuracy is implied.
"""
import argparse,html,json,collections
from pathlib import Path
def esc(x):return html.escape(str(x),quote=True)
def pairset(cards):
    out=set()
    for c in cards:
        ids=sorted(c["source_ids"])
        for i,a in enumerate(ids):
            for b in ids[i+1:]:out.add((a,b))
    return out
def report(graph,metadata,texts,textreview):
    docs={x["id"]:x for x in graph["sources"]}
    original={x["source_id"]:x for x in texts["sources"]}
    candidate={tuple(sorted((e["a"],e["b"]))):e for e in graph["candidate_pairs"]}
    m={frozenset(r["source_ids"]):r for r in metadata["reviews"]}
    comparisons=[];tot=collections.Counter()
    for r in textreview["reviews"]:
        ids=set(r["source_ids"]);meta=m.get(frozenset(r["original_case_ids"]))
        if meta is None:continue
        edges={p for p in candidate if set(p)<=ids}
        mp=pairset(meta["cards"]);tp=pairset(r["cards"])
        for p in sorted(edges):
            a,b=p
            row={"a":a,"b":b,"title_a":docs[a]["title"],"title_b":docs[b]["title"],
                "url_a":docs[a]["url"],"url_b":docs[b]["url"],
                "method":candidate[p].get("method","tfidf"),"score":candidate[p].get("score",0),
                "algorithms":"candidate","metadata_qwen":"merge" if p in mp else "separate",
                "text_qwen":"merge" if p in tp else "separate",
                "chars_a":len(original[a].get("text","")),"chars_b":len(original[b].get("text",""))}
            comparisons.append(row)
            tot["pairs"]+=1;tot["metadata_merges"]+=p in mp;tot["text_merges"]+=p in tp
            tot["changed"]+=(p in mp)!=(p in tp)
            tot["metadata_only"]+=p in mp and p not in tp
            tot["text_only"]+=p in tp and p not in mp
    summary={"corpus_sources":len(graph["sources"]),"retrieval_candidates":len(candidate),
      "metadata_reviewed_cases":len(metadata["reviews"]),"metadata_cards":sum(len(r["cards"]) for r in metadata["reviews"]),
      "text_sources_attempted":texts["summary"]["attempted"],"text_sources_800_plus":texts["summary"]["texts_800_plus"],
      "text_reviewed_cases":len(textreview["reviews"]),"text_cards":sum(len(r["cards"]) for r in textreview["reviews"]),**tot}
    js=json.dumps(comparisons,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    cards=''.join(f'<div class="stat"><small>{esc(k.replace("_"," "))}</small><strong>{v}</strong></div>' for k,v in summary.items())
    page='''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ubik · Confronto dei tre esperimenti</title>
<style>:root{font-family:system-ui,-apple-system,sans-serif;color:#e9edf5;background:#10131b}body{max-width:1260px;margin:auto;padding:38px 24px}h1{font-size:clamp(30px,5vw,56px);letter-spacing:-.045em}h2{margin-top:38px}.muted,small{color:#9ba5b6}p{line-height:1.6;max-width:920px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:10px}.stat{border:1px solid #343c4d;border-radius:14px;padding:16px;display:grid;gap:8px}.stat strong{font-size:30px}.method{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.method article{padding:20px;border:1px solid #343c4d;border-radius:14px}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px;border-bottom:1px solid #343c4d;vertical-align:top}a{color:#93c5fd}input,select{background:#1d2532;border:1px solid #455066;color:white;padding:12px;border-radius:8px;max-width:100%}.toolbar{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}code{color:#b4e1cf}.changed{color:#ffcb88}.same{color:#a9e7ba}.scroll{overflow:auto}details{max-width:900px}summary{cursor:pointer}@media(max-width:760px){.method{grid-template-columns:1fr}}</style></head><body>
<p class="muted">UBIK / LABORATORIO · Corpus congelato · Nessuna pubblicazione automatica</p>
<h1>Tre metodi, le stesse fonti</h1>
<p>Confronto sperimentale: recupero algoritmico, giudizio Qwen sui metadati e giudizio Qwen sui testi originali. Il confronto per coppia include <b>soltanto le fonti con testi sostanziali effettivamente riesaminate</b>; gli altri casi non sono classificati come negativi.</p>
<div class="method"><article><h3>01 · Algoritmi</h3><p>TF-IDF + embedding multilingue. Propongono coppie candidate; <b>non dichiarano</b> che due articoli descrivano lo stesso evento.</p></article><article><h3>02 · Qwen / metadati</h3><p>Qwen decide quali fonti raggruppare leggendo titoli, descrizioni RSS, editori e date.</p></article><article><h3>03 · Qwen / testi</h3><p>Qwen decide su testi HTML recuperati, con estratti letterali obbligatori. Rimangono proposte provvisorie.</p></article></div>
<h2>Copertura e differenze</h2><div class="stats">__CARDS__</div>
<h2>Decisioni, coppia per coppia</h2><p class="muted">“Candidato” indica soltanto che gli algoritmi hanno proposto il confronto. “Unisci” e “Separa” sono decisioni di Qwen, non giudizi indipendenti di verità.</p>
<div class="toolbar"><input id="search" placeholder="Cerca nei titoli"><select id="filter"><option value="all">Tutte le coppie</option><option value="changed">Solo decisioni cambiate</option><option value="metadata_only">Unite solo sui metadati</option><option value="text_only">Unite solo sui testi</option></select><select id="method"><option value="all">TF-IDF ed embedding</option><option value="tfidf">Solo TF-IDF</option><option value="multilingual_embedding">Solo embedding</option></select></div>
<p id="count" class="muted"></p><div class="scroll"><table><thead><tr><th>Fonti originali</th><th>Recupero</th><th>Qwen metadati</th><th>Qwen testi</th></tr></thead><tbody id="rows"></tbody></table></div>
<h2>Come interpretare i risultati</h2><p>Le variazioni indicano quanto il contenuto più ricco modifica le decisioni. Non dimostrano che il terzo metodo sia più accurato. I testi HTML possono essere rumorosi, e l'evidenza letterale dimostra che una frase è presente nel materiale estratto, non che la notizia sia vera. Per stimare la precisione servirebbe una revisione indipendente delle coppie.</p>
<p>La copertura non è identica fra i tre stadi: il recupero riguarda l'intero corpus; Qwen sui metadati solo 20 contesti; Qwen sui testi soltanto i contesti con almeno due testi sufficienti. Le percentuali devono usare denominatori comparabili.</p>
<details><summary>Provenienza e riproducibilità</summary><p>Corpus e grafi: GitHub Actions 39075100154. Revisione metadati: 39076957811. Acquisizione testi: 39107689997. Revisione testi: workflow dedicato. Nessuna etichetta di Qwen è usata come ground truth.</p></details>
<script>const data=__DATA__;const q=document.getElementById('search'),f=document.getElementById('filter'),m=document.getElementById('method'),body=document.getElementById('rows');function render(){let x=data.filter(r=>(r.title_a+' '+r.title_b).toLowerCase().includes(q.value.toLowerCase())&&(m.value==='all'||r.method===m.value)&&(f.value==='all'||(f.value==='changed'&&r.metadata_qwen!==r.text_qwen)||(f.value==='metadata_only'&&r.metadata_qwen==='merge'&&r.text_qwen==='separate')||(f.value==='text_only'&&r.metadata_qwen==='separate'&&r.text_qwen==='merge')));document.getElementById('count').textContent=x.length+' coppie visualizzate su '+data.length;body.replaceChildren();for(const r of x){const tr=document.createElement('tr');const td=document.createElement('td');for(const [t,u] of [[r.title_a,r.url_a],[r.title_b,r.url_b]]){const a=document.createElement('a');a.textContent=t;a.href=u;a.target='_blank';a.rel='noopener noreferrer';td.append(a,document.createElement('br'))}tr.append(td);for(const val of [r.method+' · '+Number(r.score).toFixed(3),r.metadata_qwen==='merge'?'Unisci':'Separa',r.text_qwen==='merge'?'Unisci':'Separa']){const c=document.createElement('td');c.textContent=val;tr.append(c)}if(r.metadata_qwen!==r.text_qwen)tr.className='changed';body.append(tr)}}q.addEventListener('input',render);f.addEventListener('change',render);m.addEventListener('change',render);render()</script></body></html>'''
    return page.replace("__CARDS__",cards).replace("__DATA__",js),summary
def main():
    p=argparse.ArgumentParser()
    for x in ("graph","metadata","texts","textreview"):p.add_argument(x,type=Path)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--json-output",type=Path,required=True);a=p.parse_args()
    page,summary=report(*[json.loads(getattr(a,k).read_text()) for k in ("graph","metadata","texts","textreview")])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(page,encoding="utf-8")
    a.json_output.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print("THREE_WAY_COMPARISON",json.dumps(summary))
if __name__=="__main__":main()
