"""Ubik daily matrici v2 (prototype): the source is the unit. Each item becomes a card (source, original title, kind,
two-sentence summary of what it says). A matrice gathers the cards whose main referent is the same specific thing;
items with no companion stay single cards. The model never splits an article into facts.

  1. note     cheap model, one call per item: main referent, kind, Italian summary, verbatim quote
  2. group    one compact call: groups of item ids sharing the same main referent
  3. write    one short call per matrice: neutral title and essence built only from its cards' summaries
  4. code     valid ids, one group per item, at least two items, numbers in the header must appear in the summaries,
              independent outlets, strong sources, ranking

Usage: python -m ingestion.ubik_daily2 SELECTION.json OUT_DIR
"""
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
from pathlib import Path

from ingestion.ubik_cost_guard import OverBudget, preflight
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_matrix import CSS, LANG, data_it
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_v6_editorial import PERIMETER, norm, parse_json

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "daily-v2"
TEXT_CHARS = 8000
CEILING = 0.40
STRONG = ("approved", "primary")


def prompt(name):
    raw = (PROMPTS / f"{name}.txt").read_text()
    return raw.replace("{PERIMETER}", PERIMETER), hashlib.sha256(raw.encode()).hexdigest()


def main(selection_path, out_dir):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (p_note, h_note), (p_group, h_group), (p_write, h_write) = prompt("nota"), prompt("group"), prompt("write")
    notes_path, path = out_dir / "notes-v2.json", out_dir / "daily-v2.json"
    notes = {"prompt_sha256": h_note, "notes": {}, "cost": 0.0, "errors": []}
    if notes_path.exists() and json.loads(notes_path.read_text()).get("prompt_sha256") == h_note:
        notes = json.loads(notes_path.read_text())
    out = {"version": "daily-v2", "window": sel.get("window"), "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"nota": h_note, "group": h_group, "write": h_write}, "preflight": [], "errors": [], "cost": {}}

    def save():
        notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    todo = [i for i in items if i not in notes["notes"]]
    try:
        preflight("daily matrici v2", len(todo) * 0.0009 + 0.02 + 0.03, CEILING, out["preflight"])
    except OverBudget as exc:
        out["status"] = "refused_preflight"
        save()
        raise SystemExit(str(exc))
    for iid in todo:
        it = items[iid]
        payload = {"item_id": iid, "source": it.get("publisher"), "date": (it.get("published") or "")[:10],
                   "title": it.get("title") or "", "text": it["text"][:TEXT_CHARS]}
        for attempt in (1, 2):
            try:
                raw, cost, _ = call(DEEPSEEK, p_note, payload, max_tokens=1500)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
                notes["errors"].append({"item": iid, "error": str(exc)[:200]})
                continue
            notes["cost"] += cost
            try:
                n = parse_json(raw["choices"][0]["message"]["content"])
                assert n.get("item_id") == iid and n.get("summary")
            except Exception as exc:
                notes["errors"].append({"item": iid, "error": str(exc)[:200]})
                continue
            q = norm(n.get("quote"))
            n["quote_verified"] = bool(q) and q in norm((it.get("title") or "") + " " + it["text"][:TEXT_CHARS])
            notes["notes"][iid] = n
            break
        if notes["cost"] > CEILING:
            save()
            raise SystemExit("Cost ceiling exceeded (notes)")
    save()

    keep = {iid: n for iid, n in notes["notes"].items() if iid in items and n.get("in_perimeter") in ("yes", "partial")
            and n.get("kind") != "rilancio"}
    listing = [{"id": iid, "source": items[iid].get("publisher"), "origin": items[iid]["origin"], "date": (items[iid].get("published") or "")[:10],
                "title": items[iid].get("title") or "", "kind": n.get("kind"), "main_referent": n.get("main_referent"),
                "summary": n.get("summary")} for iid, n in keep.items()]
    out["items_in"] = len(listing)
    try:
        raw, cost, _ = call(DEEPSEEK, p_group, {"items": listing}, max_tokens=8000)
        out["cost"]["group"] = cost
        groups = parse_json(raw["choices"][0]["message"]["content"]).get("matrici", [])
    except Exception as exc:
        out["errors"].append({"stage": "group", "error": f"{type(exc).__name__}: {exc}"[:300]})
        save()
        raise SystemExit("group failed")

    # code controls on the groups
    used, log, matrici = set(), [], []
    for g in groups:
        ids = []
        for iid in g.get("items") or []:
            if iid not in keep:
                log.append({"dropped": "unknown_or_out_of_perimeter", "matrice": g.get("id"), "item": iid})
            elif iid in used:
                log.append({"dropped": "already_grouped", "matrice": g.get("id"), "item": iid})
            elif keep[iid].get("kind") == "rassegna":
                log.append({"dropped": "roundup", "matrice": g.get("id"), "item": iid})
            else:
                ids.append(iid)
        if len(ids) < 2:
            log.append({"dissolved": g.get("id"), "items": ids})
            continue
        used.update(ids)
        ids.sort(key=lambda i: (items[i].get("published") or ""))
        matrici.append({"id": g.get("id"), "referent": g.get("referent"), "items": ids,
                        "origins": sorted({items[i]["origin"] for i in ids}),
                        "strong": any(items[i].get("tier", "approved") in STRONG for i in ids),
                        "date": max((items[i].get("published") or "")[:10] for i in ids)})
    matrici.sort(key=lambda m: (not m["strong"], -len(m["origins"]), -len(m["items"]), m["date"]))
    out["cost"]["write"] = 0.0
    for m in matrici:
        payload = {"referent": m["referent"], "cards": [{"source": items[i].get("publisher"), "kind": keep[i].get("kind"),
                                                         "summary": keep[i].get("summary")} for i in m["items"]]}
        try:
            raw, cost, _ = call(DEEPSEEK, p_write, payload, max_tokens=1500)
            out["cost"]["write"] += cost
            w = parse_json(raw["choices"][0]["message"]["content"])
            m["title"], m["essence"] = w.get("title", ""), w.get("essence", "")
        except Exception as exc:
            out["errors"].append({"stage": "write", "matrice": m["id"], "error": str(exc)[:200]})
            m["title"], m["essence"] = m["referent"], ""
        hay = norm(" ".join(keep[i].get("summary", "") for i in m["items"]))
        m["unsupported_numbers"] = sorted({x for x in re.findall(r"\d[\d.,]*\d|\d", m["title"] + " " + m["essence"])
                                           if x.replace(".", "").replace(",", "") not in hay.replace(".", "").replace(",", "")})
    singles = [iid for iid, n in keep.items() if iid not in used and n.get("in_perimeter") == "yes"]
    singles.sort(key=lambda i: (items[i].get("tier", "approved") not in STRONG, (items[i].get("published") or "")), reverse=False)
    out["matrici"], out["singles"], out["controls"] = matrici, singles, {"log": log}
    out["summary"] = {"items_in": len(listing), "matrici": len(matrici), "items_in_matrici": len(used),
                      "multi_outlet": sum(len(m["origins"]) >= 2 for m in matrici), "singles": len(singles),
                      "headers_with_unsupported_numbers": sum(bool(m["unsupported_numbers"]) for m in matrici)}
    out["cost"]["notes"] = notes["cost"]
    out["total_cost_usd"] = sum(out["cost"].values())
    out["status"] = "completed"
    save()
    (out_dir / "daily-v2.html").write_text(render(out, keep, items))
    print(json.dumps({"summary": out["summary"], "cost": out["cost"]}))


KIND = {"cronaca": "Cronaca", "reazione": "Reazione", "analisi": "Analisi", "commento": "Commento", "documento": "Documento",
        "rassegna": "Rassegna", "altro": "Notizia"}


def card(iid, n, items, e, k=None):
    it = items[iid]
    num = f"<b>N{k}</b>" if k else ""
    return (f'<div class="sc"><div class="sh">{num}<span class="kd">{e(KIND.get(n.get("kind"), "Notizia"))}</span>'
            f'<a href="{e(it["url"])}">{e(it.get("publisher") or it["source_id"])}</a>'
            f'<span class="when">{e(data_it((it.get("published") or "")[:10]))} · {e(LANG.get(it["language"], it["language"]))}'
            f'{" · testo parziale" if it.get("text_partial") else ""}</span></div>'
            f'<div class="ot">«{e(it.get("title") or "")}»</div><p>{e(n.get("summary", ""))}</p>{quote(n, e)}</div>')


def quote(n, e):
    """The verbatim quote, only when the code found it in the text, with its Italian translation when there is one."""
    if not (n.get("quote_verified") and n.get("quote")):
        return ""
    tr = f'<span class="tr">{e(n["quote_it"])}</span>' if n.get("quote_it") else ""
    return f'<blockquote><q>«{e(n["quote"])}»</q>{tr}</blockquote>'


def render(out, keep, items):
    e = html.escape
    css = CSS.read_text() + """
.feed{display:grid;gap:14px}
.mx{background:var(--sheet);border:1px solid var(--rule);border-left:5px solid var(--mark)}
.mx.weak{border-left-color:var(--rule)}
.mx>summary{list-style:none;cursor:pointer;display:grid;gap:6px;padding:14px 18px}
.mx>summary::-webkit-details-marker{display:none}
.meta{font-family:var(--mono);font-size:12px;color:var(--muted)}
.mx .ttl{font-family:var(--display);font-size:20px;font-weight:600;line-height:1.2}
.mx .ess{font-size:16px}
.mx .open{font-family:var(--display);font-size:13.5px;font-weight:600;color:var(--mark)}
.mx[open] .open{display:none}
.mx .in{display:grid;gap:10px;padding:0 18px 16px;border-top:1px dashed var(--rule);padding-top:12px}
.sc{display:grid;gap:3px;border-left:2px solid var(--rule);padding-left:10px}
.sh{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;font-size:14.5px}
.sh a{font-family:var(--display);font-weight:600;color:var(--ink)}
.sh b{font-family:var(--mono);font-weight:500;color:var(--muted)}
.kd{font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--mark)}
.ot{font-size:14.5px;font-style:italic;color:var(--muted)}
.sc p{font-size:15.5px}
.single{background:var(--sheet);border:1px solid var(--rule);padding:12px 16px}
"""
    w = out.get("window") or ["", ""]
    s = out["summary"]
    parts = ["<title>Ubik attualità</title>", '<meta name="claude:viewport-fit-sides" content="cover">',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
             f"<style>{css}</style>",
             '<nav class="mnav"><a href="#matrici">Matrici</a><a href="#notizie">Altre notizie</a></nav>', '<div class="wrap">', "<header>",
             f'<div class="eyebrow">UBIK · REGOLE SULL\'IA · DAL {e(data_it(w[0]))} AL {e(data_it(w[1]))} · PROTOTIPO V2</div>',
             "<h1>Le Matrici della settimana</h1>",
             f'<div class="lead"><p>{s["matrici"]} Matrici riuniscono {s["items_in_matrici"]} articoli che parlano della stessa cosa; '
             f'{s["multi_outlet"]} hanno più testate indipendenti. Ogni card è un solo articolo, con il suo titolo originale e due frasi su cosa dice. '
             f'Sotto, {s["singles"]} notizie senza compagni.</p></div>', "</header>", '<section id="matrici"><h2>Le Matrici</h2><div class="feed">']
    for m in out["matrici"]:
        no = len(m["origins"])
        parts.append(f'<details class="mx{"" if m["strong"] else " weak"}"><summary>'
                     f'<span class="meta">{e(data_it(m["date"]))} · {len(m["items"])} articoli · {no} {"testata" if no == 1 else "testate"}</span>'
                     f'<span class="ttl">{e(m.get("title", ""))}</span><span class="ess">{e(m.get("essence", ""))}</span>'
                     '<span class="open">Apri la Matrice</span></summary><div class="in">'
                     + "".join(card(i, keep[i], items, e, k + 1) for k, i in enumerate(m["items"])) + "</div></details>")
    parts.append('</div></section><section id="notizie"><h2>Altre notizie</h2><div class="feed">')
    parts += [f'<div class="single">{card(i, keep[i], items, e)}</div>' for i in out["singles"][:40]]
    parts.append(f'</div></section><section class="method"><p>Prototipo v2: una nota per articolo e un raggruppamento per referente principale '
                 f'con DeepSeek, controlli nel codice. Costo {out.get("total_cost_usd", 0):.3f} $.</p></section></div>')
    return "\n".join(parts)


if __name__ == "__main__":
    main(*sys.argv[1:3])
