"""Render a source-linked empirical shortlist without assigning unverified truth labels."""
import argparse,json,re
from pathlib import Path

def numbers(title):
    return set(re.findall(r"\b\d+\b",title))
def render(data):
    out=["# Ubik — coppie candidate fra fonti diverse","",
         f"Documenti distinti: **{data['documents']}**. Coppie con similarità lessicale non nulla: **{data['cross_publisher_pairs_scored']}**.","",
         "Metodo: TF-IDF sparso su titoli e descrizioni RSS, con peso maggiore ai titoli; confronto fra domini diversi. **Nessuna etichetta di equivalenza o contraddizione è stata verificata.**","",
         "| # | Similarità | Fonte A | Fonte B | Divergenza numerica nei titoli? |",
         "|---:|---:|---|---|---|"]
    for idx,p in enumerate(data["top_pairs"][:40],1):
        a,b=p["left"],p["right"]
        na,nb=numbers(a["title"]),numbers(b["title"])
        numeric="Sì, da verificare" if na and nb and na!=nb else "Non rilevata"
        def link(x):
            title=x["title"].replace("|","/").replace("[","(").replace("]",")")
            return f"[{title}]({x['url']})"
        out.append(f"| {idx} | {p['score']:.3f} | {link(a)} | {link(b)} | {numeric} |")
    out+=["","## Lettura corretta",
          "Le coppie in tabella sono **candidati per revisione**, non card finali. Similarità alta non garantisce stesso evento; similarità bassa non esclude parafrasi o notizie correlate. Una differenza numerica nei titoli è soltanto un allarme: potrebbe riflettere aggiornamenti temporali, definizioni diverse o eventi distinti.",
          "Per decidere accorpamento, separazione e contraddizione occorre confrontare le affermazioni nei testi effettivi e mantenere provenienza e data di ogni dettaglio.",""]
    return "\n".join(out)
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(render(json.loads(a.input.read_text())),encoding="utf-8")
    print("Review report written:",a.output)
if __name__=="__main__":main()
