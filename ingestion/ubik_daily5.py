"""Ubik daily matrici v5 (prototype): one macro topic (artificial intelligence), several sub-topics, one note per item.

The note (prompts/daily-v5/nota.txt) is v4's note plus a topic assignment: for every sub-topic, yes / partial / no.
Each sub-topic then runs v4's pipeline on its own items (model proposes, code confirms, merge pass, titles), with
its own perimeter. An item can appear in several sub-topics. Cards say when the text we hold is partial.

Usage: python -m ingestion.ubik_daily5 SELECTION.json OUT_DIR
"""
import hashlib
import html
import json
import os
import sys
import threading
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ingestion import ubik_daily3 as v3
from ingestion import ubik_daily4 as d4
from ingestion.ubik_cost_guard import OverBudget, preflight
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_v6_editorial import PERIMETER as RULES_PERIMETER, norm, parse_json

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "daily-v5"
TOPICS = {
    "regole": ("Regole sull'IA", RULES_PERIMETER),
    "lavoro": ("Lavoro e IA", "Artificial intelligence and work: effects of AI on jobs, wages, hiring and layoffs, professions "
               "and skills, AI used to manage or monitor workers, unions and collective bargaining, labour law and court cases "
               "about AI at work, in Europe, the United States and elsewhere."),
    "energia": ("Data center, energia e territorio", "The physical footprint of AI: data centers and their electricity demand, "
                "power grids and energy sources, water, emissions, land use, permits and moratoria, local conflicts, the "
                "communities and workers around data centers."),
    "copyright": ("Diritto d'autore, editori e dati di addestramento", "AI, copyright and training data: lawsuits and rulings "
                  "on training and on outputs, licensing deals between AI companies and publishers, authors, musicians and "
                  "artists, opt-outs and scraping, and the effects of AI on journalism and publishing."),
}
TEXT_CHARS = 8000
BUDGET = float(os.getenv("DAILY_BUDGET", "1.20"))


def note_prompt():
    raw = (PROMPTS / "nota.txt").read_text()
    topics = "\n".join(f'- "{k}": {p}' for k, (_, p) in TOPICS.items())
    return raw.replace("{TOPICS}", topics), hashlib.sha256((raw + topics).encode()).hexdigest()


def partial_text(it):
    return it.get("text_access") == "partial" or it.get("text_source") == "feed" and len(it["text"].split()) < 300 \
        or len(it["text"].split()) < 200


def admits(keep):
    """A matrice stays in a sub-topic only if at least two of its items, and at least half, are mainly about that
    sub-topic ("yes"). Items only partly about the sub-topic can join a matrice but cannot carry one. Applied inside the
    build, before the titles, so refused matrici cost nothing to write."""
    def ok(m):
        ys = sum(keep[i]["in_perimeter"] == "yes" for i in m["items"])
        return ys >= 2 and ys * 2 >= len(m["items"])
    return ok


STRONG_TIERS = ("approved", "primary")


def strong_only(out, items):
    """A Matrice needs at least one approved or primary source: sources in probation never confirm each other
    (registry rule). A Matrice made only of them is dissolved and its items go back to the single cards."""
    kept, gone = [], []
    for m in out["matrici"]:
        if any(items.get(i, {}).get("tier", "approved") in STRONG_TIERS for i in m["items"]):
            kept.append(m)
        else:
            gone.append(m["title"])
            out["singles"] += [i for i in m["items"] if i in items]
    out["matrici"] = kept
    out.setdefault("log", []).extend({"stage": "strong_only", "dissolved": t} for t in gone)
    out["summary"]["dissolved_probation_only"] = len(gone)


def topic_filter(out, keep, items):
    """Summary after the sub-topic filter (already applied by the build); single cards mainly about the sub-topic first."""
    strong_only(out, items)
    out["singles"] = list(dict.fromkeys(out["singles"]))
    out["singles"].sort(key=lambda i: (keep[i].get("in_perimeter") != "yes", items[i].get("published") or ""))
    out.setdefault("topic_filter", [])
    s = out["summary"]
    s.update({"matrici_before_topic_filter": out.get("matrici_before_admit", s["matrici"]), "matrici": len(out["matrici"]),
              "items_in_matrici": sum(len(m["items"]) for m in out["matrici"]), "singles": len(out["singles"]),
              "multi_source_cards": sum(len(c["items"]) > 1 for m in out["matrici"] for c in m["cards"]),
              "singles_partial": sum(keep[i].get("in_perimeter") != "yes" for i in out["singles"])})


def render(out, keep, items, name):
    """v3 page; single cards mainly about the sub-topic in the feed, those only partly about it folded below."""
    main = [i for i in out["singles"] if keep[i].get("in_perimeter") == "yes"]
    side = [i for i in out["singles"] if keep[i].get("in_perimeter") != "yes"]
    page = v3.render({**out, "singles": main}, keep, items)
    if side:
        e = html.escape
        fold = (f'<details class="side"><summary>Collegate al tema ({len(side)})</summary><div class="feed">'
                + "".join(f'<div class="single">{v3.v2.card(i, keep[i], items, e)}</div>' for i in side[:120]) + "</div></details>")
        page = page.replace('</div></section><section class="method">', fold + '</div></section><section class="method">', 1)
        page = page.replace("</style>", ".side>summary{cursor:pointer;font-family:var(--display);font-weight:600;color:var(--mark);"
                            "padding:10px 0}.side .feed{margin-top:8px}</style>", 1)
    return page.replace("REGOLE SULL\'IA", html.escape(name.upper())).replace(
        "REGOLE SULL'IA", html.escape(name.upper())).replace("PROTOTIPO V3", "PROTOTIPO V5").replace(
        "Il controllo ha tolto", "Il codice ha escluso").replace("articoli non pertinenti", "articoli che non poteva confermare").replace(
        "Prototipo v3", "Prototipo v5")


def make_notes(items, out_dir):
    p_note, h_note = note_prompt()
    path = out_dir / "notes-v5.json"
    notes = {"prompt_sha256": h_note, "notes": {}, "cost": 0.0, "errors": [], "preflight": []}
    if path.exists() and json.loads(path.read_text()).get("prompt_sha256") == h_note:
        notes = json.loads(path.read_text())
    todo = [i for i in items if i not in notes["notes"]]
    try:
        preflight("daily matrici v5 notes", len(todo) * 0.0008 + 0.02, BUDGET, notes["preflight"])
    except OverBudget as exc:
        path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
        raise SystemExit(str(exc))
    lock = threading.Lock()

    def one(iid):
        it = items[iid]
        payload = {"item_id": iid, "source": it.get("publisher"), "date": (it.get("published") or "")[:10],
                   "title": it.get("title") or "", "text": it["text"][:TEXT_CHARS]}
        for _ in (1, 2):
            try:
                raw, cost, _ = call(DEEPSEEK, p_note, payload, max_tokens=1600)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
                with lock:
                    notes["errors"].append({"item": iid, "error": str(exc)[:200]})
                continue
            with lock:
                notes["cost"] += cost
            try:
                n = parse_json(raw["choices"][0]["message"]["content"])
                assert n.get("item_id") == iid and n.get("summary")
            except Exception as exc:
                with lock:
                    notes["errors"].append({"item": iid, "error": str(exc)[:200]})
                continue
            q = norm(n.get("quote"))
            n["quote_verified"] = bool(q) and q in norm((it.get("title") or "") + " " + it["text"][:TEXT_CHARS])
            with lock:
                notes["notes"][iid] = n
                if len(notes["notes"]) % 50 == 0:
                    path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
            return
    with ThreadPoolExecutor(max_workers=int(os.getenv("DAILY_WORKERS", "6"))) as pool:
        list(pool.map(one, todo))
    path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
    return notes


def main(selection_path, out_dir):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    for it in items.values():
        it["text_partial"] = partial_text(it)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    notes = make_notes(items, out_dir)
    (p_group, h_group), (p_write, h_write) = (None, None), (None, None)
    index = {"version": "daily-v5", "window": sel.get("window"), "code_commit": os.getenv("UBIK_COMMIT"), "items": len(items),
             "notes_cost": notes["cost"], "note_errors": len(notes["errors"]), "topics": {}}
    about_ai = {i: n for i, n in notes["notes"].items() if n.get("in_perimeter") in ("yes", "partial")}
    index["about_ai"] = len(about_ai)
    index["no_topic"] = sum(not any(v in ("yes", "partial") for v in (n.get("topics") or {}).values()) for n in about_ai.values())
    for key, (name, perimeter) in TOPICS.items():
        d4.PERIMETER = perimeter
        (p_group, h_group), (p_write, h_write) = d4.prompt("group"), d4.prompt("write")
        path = out_dir / f"daily-v5-{key}.json"
        old = json.loads(path.read_text()) if path.exists() else {}
        out = {"version": "daily-v5", "topic": key, "topic_name": name, "perimeter": perimeter, "window": sel.get("window"),
               "code_commit": os.getenv("UBIK_COMMIT"), "prompt_sha256": {"nota": notes["prompt_sha256"], "group": h_group, "write": h_write},
               "errors": [], "cost": {"group": 0.0, "merge": 0.0, "write": 0.0}, "log": []}
        keep = {}
        for iid, n in about_ai.items():
            t = (n.get("topics") or {}).get(key, "no")
            if iid in items and t in ("yes", "partial") and n.get("kind") != "rilancio":
                keep[iid] = {**n, "in_perimeter": t}
        if len(keep) < 2:
            continue
        try:
            d4.build(keep, items, out, old, p_group, h_group, p_write, admit=admits(keep))
        except Exception as exc:
            out["errors"].append({"stage": "build", "error": f"{type(exc).__name__}: {exc}"[:300]})
            path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
            continue
        topic_filter(out, keep, items)
        out["total_cost_usd"] = sum(out["cost"].values())
        out["status"] = "completed"
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        page = render(out, keep, items, name)
        (out_dir / f"daily-v5-{key}.html").write_text(page)
        index["topics"][key] = {"name": name, "items": len(keep), "yes": sum(n["in_perimeter"] == "yes" for n in keep.values()),
                                "summary": out["summary"], "cost": out["cost"],
                                "matrici": [{"title": m["title"], "items": len(m["items"]), "origins": len(m["origins"])} for m in out["matrici"]]}
    index["total_cost_usd"] = notes["cost"] + sum(sum(t["cost"].values()) for t in index["topics"].values())
    (out_dir / "daily-v5.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: v for k, v in index.items() if k != "topics"} | {"topics": {k: t["summary"] for k, t in index["topics"].items()}}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
