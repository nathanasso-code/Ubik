"""Ubik daily matrici v3 (prototype). Items are never split.
  card    = one or more items covering the same specific aspect (a single item is a card of its own)
  matrice = the cards about the same specific event or referent
Steps: note per item (reused from v2: same prompt), one grouping call (matrici -> cards -> item ids), one verification
call per proposed matrice (drops items not about the same referent, splits cards that do not overlap), one writing
call per matrice (title, essence, card titles; text only for multi-source cards), code controls.

Usage: python -m ingestion.ubik_daily3 SELECTION.json OUT_DIR
"""
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path

from ingestion import ubik_daily2 as v2
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_matrix import CSS, data_it
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_v6_editorial import PERIMETER, norm, parse_json

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "daily-v3"


def prompt(name):
    raw = (PROMPTS / f"{name}.txt").read_text()
    return raw.replace("{PERIMETER}", PERIMETER), hashlib.sha256(raw.encode()).hexdigest()


def main(selection_path, out_dir):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    out_dir = Path(out_dir)
    v2.PROMPTS = PROMPTS  # same note prompt as v2: notes-v2.json is reused when the hash matches
    v2_notes = out_dir / "notes-v2.json"
    _, h_note = prompt("nota")
    if not (v2_notes.exists() and json.loads(v2_notes.read_text()).get("prompt_sha256") == h_note):
        raise SystemExit("v3 reuses the v2 notes: run ubik_daily2 first")
    notes = json.loads(v2_notes.read_text())["notes"]
    (p_group, h_group), (p_verify, h_verify), (p_write, h_write) = prompt("group"), prompt("verify"), prompt("write")
    out = {"version": "daily-v3", "window": sel.get("window"), "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"nota": h_note, "group": h_group, "verify": h_verify, "write": h_write}, "errors": [],
           "cost": {"group": 0.0, "verify": 0.0, "write": 0.0}, "log": []}
    path = out_dir / "daily-v3.json"
    keep = {iid: n for iid, n in notes.items() if iid in items and n.get("in_perimeter") in ("yes", "partial")
            and n.get("kind") not in ("rilancio",)}
    listing = [{"id": iid, "source": items[iid].get("publisher"), "origin": items[iid]["origin"],
                "date": (items[iid].get("published") or "")[:10], "title": items[iid].get("title") or "", "kind": n.get("kind"),
                "main_referent": n.get("main_referent"), "summary": n.get("summary")} for iid, n in keep.items()]
    byid = {x["id"]: x for x in listing}
    raw, cost, _ = call(DEEPSEEK, p_group, {"items": listing}, max_tokens=10000)
    out["cost"]["group"] = cost
    proposed = parse_json(raw["choices"][0]["message"]["content"]).get("matrici", [])
    out["proposed"] = proposed
    used, matrici = set(), []
    for k, m in enumerate(proposed):
        ids = [i for c in m.get("cards") or [] for i in (c.get("items") or [])]
        ids = [i for i in dict.fromkeys(ids) if i in keep and i not in used and keep[i].get("kind") != "rassegna"]
        if len(ids) < 2:
            out["log"].append({"dissolved_before_check": m.get("referent"), "items": ids})
            continue
        cards = [[i for i in (c.get("items") or []) if i in ids] for c in m.get("cards") or []]
        payload = {"referent": m.get("referent"), "items": [{k2: byid[i][k2] for k2 in ("id", "source", "date", "title", "summary")} for i in ids],
                   "cards": [c for c in cards if c]}
        try:
            raw, cost, _ = call(DEEPSEEK, p_verify, payload, max_tokens=2000)
            out["cost"]["verify"] += cost
            ver = parse_json(raw["choices"][0]["message"]["content"])
        except Exception as exc:
            out["errors"].append({"stage": "verify", "referent": m.get("referent"), "error": str(exc)[:200]})
            continue
        kept = [i for i in ver.get("keep") or [] if i in ids]
        seen, cards = set(), []
        for c in ver.get("cards") or []:
            cc = [i for i in c if i in kept and i not in seen]
            seen.update(cc)
            if cc:
                cards.append(cc)
        cards += [[i] for i in kept if i not in seen]  # anything the check kept but forgot becomes its own card
        removed = [i for i in ids if i not in kept]
        out["log"].append({"referent": m.get("referent"), "proposed": len(ids), "kept": len(kept), "removed": ver.get("why_removed", []),
                           "cards_before": len(payload["cards"]), "cards_after": len(cards)})
        if len(kept) < 2 or len({items[i]["origin"] for i in kept}) < 2:
            out["log"].append({"dissolved_single_outlet": m.get("referent"), "items": kept})
            continue  # a single outlet does not make a matrice: its articles stay single cards
        used.update(kept)
        cards.sort(key=lambda c: (-len(c), min((items[i].get("published") or "") for i in c)))
        matrici.append({"id": f"M{len(matrici) + 1}", "referent": m.get("referent"), "cards": [{"items": c} for c in cards],
                        "items": kept, "origins": sorted({items[i]["origin"] for i in kept}),
                        "strong": any(items[i].get("tier", "approved") in v2.STRONG for i in kept),
                        "date": max((items[i].get("published") or "")[:10] for i in kept), "removed": removed})
    matrici.sort(key=lambda m: (not m["strong"], -len(m["origins"]), -len(m["items"]), m["date"]))
    for m in matrici:
        payload = {"referent": m["referent"], "cards": [{"index": k, "items": [{"source": items[i].get("publisher"),
                                                                                 "kind": keep[i].get("kind"), "summary": keep[i].get("summary")}
                                                                                for i in c["items"]]} for k, c in enumerate(m["cards"])]}
        try:
            raw, cost, _ = call(DEEPSEEK, p_write, payload, max_tokens=2500)
            out["cost"]["write"] += cost
            w = parse_json(raw["choices"][0]["message"]["content"])
        except Exception as exc:
            out["errors"].append({"stage": "write", "matrice": m["id"], "error": str(exc)[:200]})
            w = {}
        m["title"], m["essence"] = w.get("title") or m["referent"], w.get("essence", "")
        for x in w.get("cards") or []:
            if isinstance(x.get("index"), int) and 0 <= x["index"] < len(m["cards"]):
                c = m["cards"][x["index"]]
                c["title"] = x.get("title", "")
                c["text"] = x.get("text", "") if len(c["items"]) > 1 else ""  # a single source speaks with its own summary
        hay = norm(" ".join(keep[i].get("summary", "") for i in m["items"]))
        own = m["title"] + " " + m["essence"] + " " + " ".join(c.get("text", "") for c in m["cards"])
        m["unsupported_numbers"] = sorted({x for x in re.findall(r"\d[\d.,]*\d|\d", own)
                                           if x.replace(".", "").replace(",", "") not in hay.replace(".", "").replace(",", "")})
    singles = [iid for iid, n in keep.items() if iid not in used and n.get("in_perimeter") == "yes"]
    singles.sort(key=lambda i: (items[i].get("tier", "approved") not in v2.STRONG, items[i].get("published") or ""))
    out.update({"matrici": matrici, "singles": singles})
    out["summary"] = {"items_in": len(listing), "proposed": len(proposed), "matrici": len(matrici), "items_in_matrici": len(used),
                      "removed_by_check": sum(len(x.get("removed", [])) for x in out["log"] if "removed" in x),
                      "multi_source_cards": sum(len(c["items"]) > 1 for m in matrici for c in m["cards"]),
                      "multi_outlet": sum(len(m["origins"]) >= 2 for m in matrici), "singles": len(singles),
                      "unsupported_numbers": sum(bool(m["unsupported_numbers"]) for m in matrici)}
    out["total_cost_usd"] = sum(out["cost"].values())
    out["status"] = "completed"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    (out_dir / "daily-v3.html").write_text(render(out, keep, items))
    print(json.dumps({"summary": out["summary"], "cost": out["cost"]}))


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
.mx .in{display:grid;gap:14px;padding:0 18px 16px;border-top:1px dashed var(--rule);padding-top:12px}
.cd3{display:grid;gap:6px;border-left:3px solid var(--rule);padding-left:12px}
.cd3 .ct{font-family:var(--display);font-size:16.5px;font-weight:600}
.cd3 .cx{font-size:15.5px}
.src3{display:grid;gap:6px}
.sc{display:grid;gap:2px}
.sh{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;font-size:14.5px}
.sh a{font-family:var(--display);font-weight:600;color:var(--ink)}
.sh b{font-family:var(--mono);font-weight:500;color:var(--muted)}
.kd{font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--mark)}
.ot{font-size:14.5px;font-style:italic;color:var(--muted)}
.sc p{font-size:15px}
.single{background:var(--sheet);border:1px solid var(--rule);padding:12px 16px}
"""
    w, s = out.get("window") or ["", ""], out["summary"]
    parts = ["<title>Ubik attualità</title>", '<meta name="claude:viewport-fit-sides" content="cover">',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
             f"<style>{css}</style>", '<nav class="mnav"><a href="#matrici">Matrici</a><a href="#notizie">Altre notizie</a></nav>',
             '<div class="wrap">', "<header>",
             f'<div class="eyebrow">UBIK · REGOLE SULL\'IA · DAL {e(data_it(w[0]))} AL {e(data_it(w[1]))} · PROTOTIPO V3</div>',
             "<h1>Le Matrici della settimana</h1>",
             f'<div class="lead"><p>{s["matrici"]} Matrici, {s["multi_source_cards"]} card con più fonti sovrapposte. Ogni card raccoglie gli articoli '
             f'che trattano lo stesso aspetto; una fonte da sola è una card. Il controllo ha tolto {s["removed_by_check"]} articoli non pertinenti '
             f'dalle Matrici proposte. Sotto, {s["singles"]} notizie senza compagni.</p></div>', "</header>",
             '<section id="matrici"><h2>Le Matrici</h2><div class="feed">']
    for m in out["matrici"]:
        no = len(m["origins"])
        parts.append(f'<details class="mx{"" if m["strong"] else " weak"}"><summary>'
                     f'<span class="meta">{e(data_it(m["date"]))} · {len(m["cards"])} card · {len(m["items"])} articoli · {no} {"testata" if no == 1 else "testate"}</span>'
                     f'<span class="ttl">{e(m["title"])}</span><span class="ess">{e(m.get("essence", ""))}</span>'
                     '<span class="open">Apri la Matrice</span></summary><div class="in">')
        k = 0
        for c in m["cards"]:
            srcs = []
            for i in c["items"]:
                k += 1
                body = "" if c.get("text") else f'<p>{e(keep[i].get("summary", ""))}</p>'
                srcs.append(v2.card(i, keep[i], items, e, k).replace("<p>" + e(keep[i].get("summary", "")) + "</p>", body))
            parts.append(f'<div class="cd3"><span class="ct">{e(c.get("title", ""))}</span>'
                         + (f'<span class="cx">{e(c["text"])}</span>' if c.get("text") else "")
                         + f'<div class="src3">{"".join(srcs)}</div></div>')
        parts.append("</div></details>")
    parts.append('</div></section><section id="notizie"><h2>Altre notizie</h2><div class="feed">')
    parts += [f'<div class="single">{v2.card(i, keep[i], items, e)}</div>' for i in out["singles"][:40]]
    parts.append(f'</div></section><section class="method"><p>Prototipo v3: note per articolo (riusate), raggruppamento, verifica per Matrice e titoli '
                 f'con DeepSeek; controlli nel codice. Costo di questo giro {out.get("total_cost_usd", 0):.3f} $.</p></section></div>')
    return "\n".join(parts)


if __name__ == "__main__":
    main(*sys.argv[1:3])
