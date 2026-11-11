"""Probe of the catalogued note (11 November 2026): the same items read with today's note and with the note that also
catalogues references, figures, names and credits (prompts/daily-v5/nota-extra.txt). Measures the extra cost per item,
how often the catalogued fields are found word for word in the text, and how the references compare with the separate
call of tools/week_refs.py on the same items (its cost is the saving if the note takes its place).

Usage: python -m ingestion.note_probe SELECTION.json OUT.json [N] [RIFERIMENTI.json]
"""
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ingestion import ubik_daily5 as D
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_v6_editorial import parse_json

CUE = re.compile(r"\b(stud(y|io|ie)|report|rapporto|survey|sondaggio|paper|research|ricerca|according to|secondo|laut|selon)\b", re.I)


def main(sel_path, out_path, n=50, refs_path=None):
    n = int(n)
    items = sorted(json.loads(Path(sel_path).read_text())["items"], key=lambda i: i["item_id"])
    cue = [i for i in items if CUE.search(i["text"][:8000])][: n // 2]
    rest = [i for i in items if i not in cue][: n - len(cue)]
    sample = cue + rest
    os.environ.pop("NOTE_EXTRA", None)
    base_p, _ = D.note_prompt()
    os.environ["NOTE_EXTRA"] = "1"
    extra_p, _ = D.note_prompt()
    refs = json.loads(Path(refs_path).read_text())["items"] if refs_path and Path(refs_path).exists() else {}

    def one(it):
        payload = {"item_id": it["item_id"], "source": it.get("publisher"), "date": (it.get("published") or "")[:10],
                   "title": it.get("title") or "", "text": it["text"][:D.TEXT_CHARS]}
        row = {"item_id": it["item_id"], "cue": it in cue, "words": len(it["text"].split())}
        for name, prompt in (("base", base_p), ("ricca", extra_p)):
            try:
                raw, cost, _ = call(DEEPSEEK, prompt, payload, max_tokens=2600)
                note = parse_json(raw["choices"][0]["message"]["content"])
                row[name] = {"costo": cost, "usage": raw.get("usage", {}), "ok": bool(note.get("summary"))}
                if name == "ricca":
                    D.verify_extra(note, (it.get("title") or "") + " " + it["text"][:D.TEXT_CHARS])
                    row["nota_ricca"] = note
            except Exception as exc:
                row[name] = {"errore": f"{type(exc).__name__}: {exc}"[:200]}
        r = refs.get(it["item_id"])
        if r:
            row["riferimenti_separati"] = {"costo": r.get("costo"), "n": len(r.get("riferimenti") or [])}
        return row
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(one, sample))
    ok = [r for r in rows if r.get("base", {}).get("ok") and r.get("ricca", {}).get("ok")]
    tot = lambda k: sum(r[k]["costo"] for r in ok)  # noqa: E731
    cifre = [c for r in ok for c in r["nota_ricca"].get("cifre") or [] if isinstance(c, dict)]
    pers = [p for r in ok for p in (r["nota_ricca"].get("nominati") or {}).get("persone") or [] if isinstance(p, dict)]
    orgs = [x for r in ok for x in (r["nota_ricca"].get("nominati") or {}).get("organizzazioni_nel_testo") or []]
    attr = [a for r in ok for a in r["nota_ricca"].get("attribuzioni") or [] if isinstance(a, dict)]
    rif = [x for r in ok for x in r["nota_ricca"].get("riferimenti") or [] if isinstance(x, dict)]
    sep = [r for r in ok if r.get("riferimenti_separati")]
    summary = {
        "articoli": len(rows), "letti_entrambi": len(ok),
        "costo_base": round(tot("base"), 5), "costo_ricca": round(tot("ricca"), 5),
        "costo_in_piu_per_articolo": round((tot("ricca") - tot("base")) / max(1, len(ok)), 6),
        "aumento_percentuale": round(100 * (tot("ricca") - tot("base")) / max(1e-9, tot("base")), 1),
        "cifre": len(cifre), "cifre_nel_testo": sum(1 for c in cifre if c.get("nel_testo")),
        "persone": len(pers), "persone_nel_testo": sum(1 for p in pers if p.get("nel_testo")),
        "organizzazioni": len(orgs), "organizzazioni_nel_testo": sum(orgs),
        "attribuzioni": len(attr), "attribuzioni_nel_testo": sum(1 for a in attr if a.get("nel_testo")),
        "riferimenti_nota": len(rif),
        "confronto_chiamata_separata": {"articoli": len(sep), "riferimenti_nota": sum(len(r["nota_ricca"].get("riferimenti") or []) for r in sep),
                                        "riferimenti_separati": sum(r["riferimenti_separati"]["n"] for r in sep),
                                        "costo_separato": round(sum(r["riferimenti_separati"]["costo"] or 0 for r in sep), 5),
                                        "costo_in_piu_della_nota": round(sum(r["ricca"]["costo"] - r["base"]["costo"] for r in sep), 5)},
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps({"riassunto": summary, "righe": rows}, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:])
