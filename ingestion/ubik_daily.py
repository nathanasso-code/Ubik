"""Ubik daily matrici (prototype): the news of a period grouped by SPECIFIC referent (a decision, a ruling, a study...),
each matrice with cards for the fact, the reactions and the analyses, and under each card the news items N1, N2...
that report it. A long-running story (vicenda) gets a short "state as of" updated from its new matrici.

  1. note     cheap model, one call per item: claims with referent and relation (reports, reacts_to, updates...)
  2. group    one call: matrici and cards over all claims of the period
  3. controls code: valid refs, verified quotes, independent outlets per card and matrice, strong sources, ranking
  4. state    one call per open vicenda: new state, previous cards superseded by new ones

Usage: python -m ingestion.ubik_daily SELECTION.json OUT_DIR [VICENDE.json]
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

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "daily-v1"
TEXT_CHARS = 8000
CEILING = 0.40
EST = {"note": 0.0012, "group": 0.03, "state": 0.005, "write": 0.06}
STRONG = ("approved", "primary")
MAX_WRITTEN = 30


def prompt(name, **kw):
    raw = (PROMPTS / f"{name}.txt").read_text()
    text = raw.replace("{PERIMETER}", PERIMETER)
    for k, v in kw.items():
        text = text.replace("{" + k + "}", v)
    return text, hashlib.sha256(raw.encode()).hexdigest()


def main(selection_path, out_dir, vicende_path=None):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    vicende = json.loads(Path(vicende_path).read_text()) if vicende_path else []
    p_note, h_note = prompt("nota")
    p_group, h_group = prompt("group", VICENDE=json.dumps([{"id": v["id"], "description": v["description"]} for v in vicende],
                                                           ensure_ascii=False) or "[]")
    p_state, h_state = prompt("state")
    p_write, h_write = prompt("write")
    notes_path, path = out_dir / "notes.json", out_dir / "daily.json"
    notes = {"prompt_sha256": h_note, "notes": {}, "cost": 0.0, "errors": []}
    if notes_path.exists() and json.loads(notes_path.read_text()).get("prompt_sha256") == h_note:
        notes = json.loads(notes_path.read_text())
    out = {"version": "daily-v1", "window": sel.get("window"), "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"nota": h_note, "group": h_group, "state": h_state, "write": h_write}, "preflight": [], "errors": [], "cost": {}}

    def save():
        notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    todo = [i for i in items if i not in notes["notes"]]
    try:
        preflight("daily matrici", len(todo) * EST["note"] + EST["group"] + EST["write"] + len(vicende) * EST["state"], CEILING, out["preflight"])
    except OverBudget as exc:
        out["status"] = "refused_preflight"
        save()
        raise SystemExit(str(exc))

    # 1. notes
    for iid in todo:
        it = items[iid]
        payload = {"item_id": iid, "source": it.get("publisher") or it["source_id"], "date": (it.get("published") or "")[:10],
                   "title": it.get("title") or "", "text": it["text"][:TEXT_CHARS]}
        for attempt in (1, 2):
            try:
                raw, cost, _ = call(DEEPSEEK, p_note, payload, max_tokens=3000)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
                notes["errors"].append({"item": iid, "error": str(exc)[:200]})
                continue
            notes["cost"] += cost
            try:
                n = parse_json(raw["choices"][0]["message"]["content"])
                assert n.get("item_id") == iid and isinstance(n.get("claims"), list)
            except Exception as exc:
                notes["errors"].append({"item": iid, "error": str(exc)[:200]})
                continue
            src = norm((it.get("title") or "") + " " + it["text"][:TEXT_CHARS])
            for c in n["claims"]:
                c["quote_verified"] = bool(norm(c.get("quote"))) and norm(c.get("quote")) in src
            notes["notes"][iid] = n
            break
        if notes["cost"] > CEILING:
            save()
            raise SystemExit("Cost ceiling exceeded (notes)")
    save()

    # 2. group
    claims = []
    for iid, n in notes["notes"].items():
        if iid not in items or n.get("in_perimeter") == "no":
            continue
        it = items[iid]
        for c in n["claims"]:
            claims.append({"ref": f"{iid}:{c.get('id')}", "source": it.get("publisher") or it["source_id"], "origin": it["origin"],
                           "source_tier": it.get("tier", "approved"), "date": c.get("date") or (it.get("published") or "")[:10],
                           "title": it.get("title") or "", **{k: c.get(k) for k in ("who", "type", "statement", "referent", "relation")}})
    out["claims_in"] = len(claims)
    try:
        raw, cost, _ = call(DEEPSEEK, p_group, {"claims": claims}, max_tokens=24000)
        out["cost"]["group"] = cost
        page = parse_json(raw["choices"][0]["message"]["content"])
        assert isinstance(page.get("matrici"), list)
    except Exception as exc:
        out["errors"].append({"stage": "group", "error": f"{type(exc).__name__}: {exc}"[:300]})
        save()
        raise SystemExit("group failed")
    out["page"] = page
    controls(page, notes["notes"], items)
    save()

    # 2b. one short writing call per matrice (titles, essence, card texts), strongest first
    out["cost"]["write"] = 0.0
    for m in page["matrici"][:MAX_WRITTEN]:
        payload = {"referent": m.get("referent"), "cards": [
            {"index": i, "kind": c.get("kind"), "who": c.get("who"),
             "claims": [{**{k: cl.get(k) for k in ("who", "statement", "quote", "date")},
                         "source": items[r.split(":")[0]].get("publisher")} for r in c["claims"]
                        for cl in [next(x for x in notes["notes"][r.split(":")[0]]["claims"] if x.get("id") == r.split(":")[1])]]}
            for i, c in enumerate(m["cards"])]}
        try:
            raw, cost, _ = call(DEEPSEEK, p_write, payload, max_tokens=4000)
            out["cost"]["write"] += cost
            w = parse_json(raw["choices"][0]["message"]["content"])
            m["title"], m["essence"] = w.get("title", ""), w.get("essence", "")
            for x in w.get("cards", []):
                if isinstance(x.get("index"), int) and 0 <= x["index"] < len(m["cards"]):
                    m["cards"][x["index"]].update({"title": x.get("title", ""), "text": x.get("text", "")})
        except Exception as exc:
            out["errors"].append({"stage": "write", "matrice": m.get("id"), "error": f"{type(exc).__name__}: {exc}"[:200]})
    page["matrici"] = [m for m in page["matrici"][:MAX_WRITTEN] if m.get("title")]
    page["summary"]["shown"] = len(page["matrici"])
    save()

    # 4. vicende
    out["vicende"] = []
    for v in vicende:
        new = [m for m in page["matrici"] if m.get("vicenda") == v["id"]]
        if not new:
            out["vicende"].append({"id": v["id"], "state": v.get("state"), "new_matrici": [], "superseded": []})
            continue
        payload = {"previous": {"state": v.get("state"), "cards": v.get("cards", [])},
                   "new_matrici": [{"id": m["id"], "title": m.get("title"), "cards": [{"index": i, "kind": c.get("kind"), "who": c.get("who"),
                                                                                       "title": c.get("title"), "text": c.get("text")}
                                                                                      for i, c in enumerate(m["cards"])]} for m in new]}
        try:
            raw, cost, _ = call(DEEPSEEK, p_state, payload, max_tokens=4000)
            out["cost"]["state_" + v["id"]] = cost
            st = parse_json(raw["choices"][0]["message"]["content"])
        except Exception as exc:
            out["errors"].append({"stage": "state", "vicenda": v["id"], "error": str(exc)[:200]})
            continue
        out["vicende"].append({"id": v["id"], "title": v.get("title"), "previous_state": v.get("state"), "state": st.get("state"),
                               "superseded": st.get("superseded", []), "unchanged": st.get("unchanged"),
                               "new_matrici": [m["id"] for m in new], "previous_cards": v.get("cards", [])})
    out["cost"]["notes"] = notes["cost"]
    out["total_cost_usd"] = sum(out["cost"].values())
    out["status"] = "completed"
    save()
    (out_dir / "daily.html").write_text(render(out, notes["notes"], items))
    print(json.dumps({"matrici": len(page["matrici"]), "cost": out["cost"], "summary": page["summary"]}))


def controls(page, notes, items):
    """Code checks: refs must exist, a claim belongs to one card only; independent outlets per card and matrice;
    a matrice needs at least one approved or primary source; ranking by independent outlets, strong sources, recency."""
    seen, log = set(), []

    def claim(ref):
        iid, _, cid = (ref or "").partition(":")
        return iid, next((c for c in notes.get(iid, {}).get("claims", []) if c.get("id") == cid), None)
    for m in page["matrici"]:
        cards = []
        for c in m.get("cards") or []:
            refs = []
            for r in c.get("claims") or []:
                iid, cl = claim(r)
                if cl is None or iid not in items:
                    log.append({"removed": "ref", "matrice": m.get("id"), "ref": r})
                elif r in seen:
                    log.append({"removed": "duplicate_ref", "matrice": m.get("id"), "ref": r})
                else:
                    seen.add(r)
                    refs.append(r)
            c["claims"] = refs
            if refs:
                c["items"] = list(dict.fromkeys(r.split(":")[0] for r in refs))
                c["origins"] = sorted({items[i]["origin"] for i in c["items"]})
                c["strong"] = any(items[i].get("tier", "approved") in STRONG for i in c["items"])
                cards.append(c)
            else:
                log.append({"removed": "card", "matrice": m.get("id"), "title": c.get("title")})
        m["cards"] = cards
        its = list(dict.fromkeys(i for c in cards for i in c["items"]))
        m["items"] = its
        m["origins"] = sorted({items[i]["origin"] for i in its})
        m["strong"] = any(c["strong"] for c in cards)
        m["date"] = max(((items[i].get("published") or "")[:10] for i in its), default="")
    page["matrici"] = [m for m in page["matrici"] if m["cards"]]
    weak = [m["id"] for m in page["matrici"] if not m["strong"]]
    page["matrici"].sort(key=lambda m: (not m["strong"], -len(m["origins"]), -len(m["cards"]), m["date"]), reverse=False)
    page["controls"] = {"repairs": log, "weak_matrici": weak}
    page["summary"] = {"matrici": len(page["matrici"]), "multi_outlet": sum(len(m["origins"]) >= 2 for m in page["matrici"]),
                       "cards": sum(len(m["cards"]) for m in page["matrici"]), "weak": len(weak), "repairs": len(log)}
    return page


KIND = {"fatto": "Fatto", "reazione": "Reazione", "analisi": "Analisi", "aggiornamento": "Aggiornamento", "smentita": "Smentita"}


def render(out, notes, items):
    e = html.escape
    page = out["page"]
    css = CSS.read_text() + """
.feed{display:grid;gap:14px}
.mx{background:var(--sheet);border:1px solid var(--rule);border-left:5px solid var(--mark)}
.mx.weak{border-left-color:var(--rule)}
.mx>summary{list-style:none;cursor:pointer;display:grid;gap:6px;padding:14px 18px}
.mx>summary::-webkit-details-marker{display:none}
.mx .meta{font-family:var(--mono);font-size:12px;color:var(--muted)}
.mx .ttl{font-family:var(--display);font-size:20px;font-weight:600;line-height:1.2}
.mx .ess{font-size:16px}
.mx .open{font-family:var(--display);font-size:13.5px;font-weight:600;color:var(--mark)}
.mx[open] .open{display:none}
.mx .cards2{display:grid;gap:12px;padding:0 18px 16px;border-top:1px dashed var(--rule);padding-top:12px}
.cd{display:grid;gap:4px}
.cd .k{font-family:var(--display);font-size:12.5px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.cd .t{font-family:var(--display);font-size:16.5px;font-weight:600}
.cd p{font-size:15.5px}
.ns{font-size:14px;color:var(--muted);display:grid;gap:2px;margin-top:2px}
.ns a{color:var(--ink)}
.ns b{font-family:var(--mono);font-weight:500;color:var(--muted);margin-right:6px}
.vic{background:var(--sheet);border:1px solid var(--rule);padding:16px 18px;display:grid;gap:8px}
.vic .old{font-size:14.5px;color:var(--muted)}
.vic s{color:var(--muted)}
"""
    w = out.get("window") or ["", ""]
    parts = [f"<title>Ubik attualità</title>", '<meta name="claude:viewport-fit-sides" content="cover">',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
             f"<style>{css}</style>", '<div class="wrap">', "<header>",
             f'<div class="eyebrow">UBIK · REGOLE SULL\'IA · MATRICI DAL {e(data_it(w[0]))} AL {e(data_it(w[1]))} · PROTOTIPO</div>',
             "<h1>Le Matrici della settimana</h1>",
             f'<div class="lead"><p>{page["summary"]["matrici"]} Matrici, {page["summary"]["multi_outlet"]} coperte da più testate indipendenti. '
             "Ogni Matrice riunisce ciò che riguarda una sola decisione, causa, studio o dichiarazione; dentro, le card separano il fatto dalle reazioni, "
             "e sotto ogni card ci sono le notizie che lo riportano, con il loro titolo originale.</p></div>", "</header>"]
    for v in out.get("vicende", []):
        if not v.get("new_matrici"):
            continue
        sup = {s.get("old_card"): s for s in v.get("superseded", [])}
        olds = "".join(f'<li>{"<s>" if c["id"] in sup else ""}{e(c["title"])}{"</s>" if c["id"] in sup else ""}'
                       + (f' — <i>{e(sup[c["id"]].get("why", ""))}</i>' if c["id"] in sup else "") + "</li>" for c in v.get("previous_cards", []))
        parts.append(f'<section><h2>Vicenda: {e(v.get("title") or v["id"])}</h2><div class="vic">'
                     f'<p><b>Stato al {e(data_it(w[1]))}.</b> {e(v.get("state") or "")}</p>'
                     f'<p class="old">Nuove Matrici collegate: {e(", ".join(v["new_matrici"]))}. {e(v.get("unchanged") or "")}</p>'
                     f'<details class="more"><summary>Card precedenti</summary><div><ul>{olds}</ul></div></details></div></section>')
    parts.append('<section><h2>Le Matrici</h2><div class="feed">')
    for m in page["matrici"]:
        n_out = len(m["origins"])
        parts.append(f'<details class="mx{"" if m["strong"] else " weak"}" id="{e(m["id"])}"><summary>'
                     f'<span class="meta">{e(m["id"])} · {e(data_it(m["date"]))} · {n_out} {"testata" if n_out == 1 else "testate"} · '
                     f'{len(m["cards"])} card{" · vicenda " + e(m["vicenda"]) if m.get("vicenda") else ""}</span>'
                     f'<span class="ttl">{e(m.get("title", ""))}</span><span class="ess">{e(m.get("essence", ""))}</span>'
                     '<span class="open">Apri la Matrice</span></summary><div class="cards2">')
        for c in m["cards"]:
            news = "".join(f'<div><b>N{k + 1}</b><a href="{e(items[i]["url"])}">{e(items[i].get("publisher") or items[i]["source_id"])}</a> — '
                           f'«{e(items[i].get("title") or "")}» <span class="when">{e(data_it((items[i].get("published") or "")[:10]))} · '
                           f'{e(LANG.get(items[i]["language"], items[i]["language"]))}</span></div>' for k, i in enumerate(c["items"]))
            parts.append(f'<div class="cd"><span class="k">{e(KIND.get(c.get("kind"), c.get("kind", "")))} · {e(c.get("who", ""))}</span>'
                         f'<span class="t">{e(c.get("title", ""))}</span><p>{e(c.get("text", ""))}</p><div class="ns">{news}</div></div>')
        parts.append("</div></details>")
    parts.append(f'</div></section><section class="method"><p>Prototipo: note e raggruppamento con DeepSeek, controlli nel codice. '
                 f'Costo {out.get("total_cost_usd", 0):.3f} $. Matrici senza fonti approvate o primarie in fondo, bordo grigio.</p></section></div>')
    return "\n".join(parts)


if __name__ == "__main__":
    main(*sys.argv[1:4])
