"""Ubik Matrice v1 (docs/matrix-spec.md): notes per item with a cheap model, one composition per Matrice,
mechanical controls, fixed rendering. Runs only in the private corpus repository (inputs are full texts).

Usage: python -m ingestion.ubik_matrix SELECTION.json OUT_DIR deepseek|sonnet [compose_runs]
Notes are always made with DeepSeek and reused across composition arms (same prompt hash).
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
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL as SONNET
from ingestion.ubik_v6_editorial import norm, parse_json

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "matrix-v1"
CSS = Path(__file__).resolve().parent / "templates" / "matrix.css"
MODELS = {"deepseek": DEEPSEEK, "sonnet": SONNET}
TEXT_CHARS = 9000
CEILING_USD = {"notes": 0.25, "deepseek": 0.08, "sonnet": 0.90}
EST = {"note": 0.0015, "deepseek": 0.012, "sonnet": 0.15}
LIMITS = {"title": 16, "summary_short": 80, "summary_long": 200, "key_point": 70, "card_title": 18, "card_text": 80,
          "timeline": 25}


def prompt(name, nucleus):
    raw = (PROMPTS / f"{name}.txt").read_text()
    return raw.replace("{NUCLEUS}", nucleus), hashlib.sha256(raw.encode()).hexdigest()


def words(s):
    return len((s or "").split())


def main(selection_path, out_dir, arm, compose_runs=2):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    nucleus = sel["nucleus"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    p_note, h_note = prompt("nota", nucleus)
    p_comp, h_comp = prompt("compose", nucleus)
    p_rev, h_rev = prompt("revise", nucleus)
    notes_path = out_dir / "notes.json"
    notes = {"prompt_sha256": h_note, "model": DEEPSEEK, "notes": {}, "cost": 0.0, "errors": []}
    if notes_path.exists():
        prev = json.loads(notes_path.read_text())
        if prev.get("prompt_sha256") == h_note:
            notes = prev
    todo = [i for i in items if i not in notes["notes"]]
    out = {"version": "matrix-v1", "arm": arm, "model": MODELS[arm], "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"nota": h_note, "compose": h_comp, "revise": h_rev}, "nucleus": nucleus, "preflight": [], "pages": [],
           "errors": [], "calls": [], "cost": {"compose": 0.0}}
    path = out_dir / f"matrix-{arm}.json"

    def save():
        notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    try:
        preflight("matrix notes", len(todo) * EST["note"], CEILING_USD["notes"], out["preflight"])
        preflight(f"matrix compose {arm}", compose_runs * EST[arm], CEILING_USD[arm], out["preflight"])
    except OverBudget as exc:
        out["status"] = "refused_preflight"
        save()
        raise SystemExit(str(exc))

    # 1. notes (cheap model, once)
    for iid in todo:
        it = items[iid]
        payload = {"item_id": iid, "source": it["publisher"], "language": it["language"], "date": (it.get("published") or "")[:10],
                   "title": it.get("title") or "", "text": it["text"][:TEXT_CHARS]}
        for attempt in (1, 2):
            try:
                raw, cost, secs = call(DEEPSEEK, p_note, payload, max_tokens=3000)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
                notes["errors"].append({"item": iid, "attempt": attempt, "error": str(exc)[:300]})
                continue
            notes["cost"] += cost
            if notes["cost"] > CEILING_USD["notes"]:
                save()
                raise SystemExit("Cost ceiling exceeded (notes)")
            try:
                n = parse_json(raw["choices"][0]["message"]["content"])
                assert n.get("item_id") == iid and isinstance(n.get("claims"), list)
            except Exception as exc:
                notes["errors"].append({"item": iid, "attempt": attempt, "error": str(exc)[:200]})
                continue
            src = norm((it.get("title") or "") + " " + it["text"][:TEXT_CHARS])
            for c in n["claims"]:
                q = norm(c.get("quote"))
                c["quote_verified"] = bool(q) and q in src
            notes["notes"][iid] = n
            break
        save()

    # 2. composition
    listing = []
    for iid, n in notes["notes"].items():
        if n.get("relevance") == "no":
            continue
        it = items[iid]
        listing.append({"item_id": iid, "source": it["publisher"], "source_role": n.get("source_role"), "language": it["language"],
                        "date": (it.get("published") or "")[:10], "original_title": it.get("title") or "", "relevance": n.get("relevance"),
                        "adds": n.get("adds"), "claims": [{k: c.get(k) for k in ("id", "type", "who", "statement", "date", "quote")}
                                                          for c in n["claims"]]})
    out["input_notes"] = len(listing)
    for run in range(1, compose_runs + 1):
        try:
            raw, cost, secs = call(MODELS[arm], p_comp, {"notes": listing}, max_tokens=20000,
                                   extra={"reasoning": {"effort": "low"}} if arm == "sonnet" else None)
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
            body = exc.read(500).decode("utf-8", "replace") if isinstance(exc, urllib.error.HTTPError) else ""
            out["errors"].append({"run": run, "error": f"{type(exc).__name__}: {exc} {body}"[:400]})
            save()
            continue
        out["cost"]["compose"] += cost
        u = raw.get("usage") or {}
        out["calls"].append({"run": run, "cost_usd": cost, "seconds": secs, "completion_tokens": u.get("completion_tokens"),
                             "finish_reason": raw["choices"][0].get("finish_reason")})
        if out["cost"]["compose"] > CEILING_USD[arm]:
            save()
            raise SystemExit("Cost ceiling exceeded (compose)")
        try:
            page = parse_json(raw["choices"][0]["message"]["content"])
            assert isinstance(page.get("cards"), list)
        except Exception as exc:
            out["errors"].append({"run": run, "error": str(exc)[:200],
                                  "content_tail": (raw["choices"][0]["message"].get("content") or "")[-300:]})
            save()
            continue
        page["run"], page["_arm"] = run, arm
        viol = rule_violations(page, notes["notes"])
        page["violations_before_revision"] = viol
        if viol:  # one revision call, only for the flagged fields
            draft = {k: page[k] for k in ("title", "summary_short", "summary_long", "key_points", "cards", "timeline", "left_out") if k in page}
            try:
                raw, cost, secs = call(MODELS[arm], p_rev, {"page": draft, "violations": viol}, max_tokens=20000,
                                       extra={"reasoning": {"effort": "low"}} if arm == "sonnet" else None)
                out["cost"]["compose"] += cost
                out["calls"].append({"run": run, "stage": "revise", "cost_usd": cost, "seconds": secs})
                rev = parse_json(raw["choices"][0]["message"]["content"])
                assert isinstance(rev.get("cards"), list)
                page.update(rev)
            except Exception as exc:
                out["errors"].append({"run": run, "stage": "revise", "error": str(exc)[:300]})
        page["violations"] = rule_violations(page, notes["notes"])
        page["controls"] = controls(page, notes["notes"], items)
        out["pages"].append(page)
        (out_dir / f"matrix-{arm}-{run}.html").write_text(render(page, notes["notes"], items))
        save()
    out["notes_cost"] = notes["cost"]
    out["total_cost_usd"] = notes["cost"] + out["cost"]["compose"]
    out["status"] = "completed"
    save()
    print(json.dumps({"arm": arm, "notes": len(notes["notes"]), "relevant": len(listing), "notes_cost": notes["cost"],
                      "compose_cost": out["cost"]["compose"], "controls": [p["controls"]["summary"] for p in out["pages"]],
                      "violations": [[len(p["violations_before_revision"]), len(p["violations"])] for p in out["pages"]]}))


ACRONYM_OK = {"UE", "USA", "GDPR", "IA"}
ACRONYM = re.compile(r"\b(?:[A-Z]{2,}[a-z]?[A-Z]*|[A-Z]+&[A-Z]+)\b")
LEGAL = re.compile(r"\b(?:articol[oi]|art\.|allegat[oi])\s+[\dIVX]+", re.I)


def rule_violations(page, notes):
    """Writing rules of docs/matrix-spec.md checked in code; the list feeds one revision call."""
    v = []
    full = " ".join([page.get("title", ""), page.get("summary_short", "")] + (page.get("summary_long") or []) +
                    [k.get("heading", "") + " " + k.get("text", "") for k in page.get("key_points", [])] +
                    [c.get("title", "") + " " + c.get("text", "") for c in page.get("cards", [])] +
                    [t.get("text", "") for t in page.get("timeline", [])])
    gdpr_ok = "protezione dei dati" in full.lower()

    def check(field, text):
        bad = sorted({a for a in ACRONYM.findall(text or "") if (a not in ACRONYM_OK or (a == "GDPR" and not gdpr_ok))
                      and not re.search(r"\(" + re.escape(a) + r"\)|\b" + re.escape(a) + r"\s*\(", full)})
        if bad:
            v.append({"field": field, "rule": "acronyms", "found": bad})
        if LEGAL.search(text or ""):
            v.append({"field": field, "rule": "legal_article_numbers", "found": LEGAL.findall(text)})
    check("title", page.get("title"))
    check("summary_short", page.get("summary_short"))
    for i, p in enumerate(page.get("summary_long") or []):
        check(f"summary_long[{i}]", p)
    for i, k in enumerate(page.get("key_points", [])):
        check(f"key_points[{i}]", k.get("heading", "") + " " + k.get("text", ""))
        if words(k.get("text")) > LIMITS["key_point"]:
            v.append({"field": f"key_points[{i}].text", "rule": "length", "words": words(k.get("text"))})
    for i, c in enumerate(page.get("cards", [])):
        check(f"cards[{i}]", c.get("title", "") + " " + c.get("text", ""))
        if words(c.get("text")) > LIMITS["card_text"] or words(c.get("title")) > LIMITS["card_title"]:
            v.append({"field": f"cards[{i}]", "rule": "length", "words": [words(c.get("title")), words(c.get("text"))]})
        if not any(notes.get(r.split(":")[0], {}).get("relevance") == "core" for r in c.get("support", [])):
            v.append({"field": f"cards[{i}]", "rule": "off_core"})
    for i, t in enumerate(page.get("timeline", [])):
        check(f"timeline[{i}]", t.get("text"))
    if words(page.get("title")) > LIMITS["title"]:
        v.append({"field": "title", "rule": "length", "words": words(page.get("title"))})
    if words(page.get("summary_short")) > LIMITS["summary_short"]:
        v.append({"field": "summary_short", "rule": "length", "words": words(page.get("summary_short"))})
    return v


def claim(notes, ref):
    iid, _, cid = (ref or "").partition(":")
    c = next((x for x in notes.get(iid, {}).get("claims", []) if x.get("id") == cid), None)
    return iid, c


def controls(page, notes, items):
    """Remove what has no valid support, verify quotes, flag numbers without support and length overruns."""
    log, flags = [], []

    def valid(refs):
        return [r for r in (refs or []) if claim(notes, r)[1] is not None]

    for key in ("key_points", "cards", "timeline"):
        keep = []
        for x in page.get(key) or []:
            x["support"] = valid(x.get("support"))
            if x["support"]:
                keep.append(x)
            else:
                log.append({"removed": key, "title": x.get("title") or x.get("heading") or x.get("text", "")[:60]})
        page[key] = keep
    for c in page["cards"]:
        iid, cl = claim(notes, c.get("quote"))
        if c.get("quote") and not (cl and cl.get("quote_verified")):
            log.append({"removed": "quote", "card": c.get("title"), "ref": c.get("quote")})
            c["quote"] = None
        origins = sorted({items[r.split(":")[0]]["origin"] for r in c["support"] if r.split(":")[0] in items})
        c["origins"] = origins
        c["single_source"] = len(origins) == 1
        # numbers in our text must appear in the cited claims or cited texts
        hay = norm(" ".join([(claim(notes, r)[1] or {}).get("statement", "") + " " + (claim(notes, r)[1] or {}).get("quote", "")
                             for r in c["support"]] + [items[r.split(":")[0]]["text"] for r in c["support"] if r.split(":")[0] in items]))
        for num in set(re.findall(r"\d[\d.,]*\d|\d", c.get("title", "") + " " + c.get("text", ""))):
            if num.replace(".", "").replace(",", "") not in hay.replace(".", "").replace(",", ""):
                flags.append({"card": c.get("title"), "unsupported_number": num})
    over = []
    for k, v in (("title", page.get("title")), ("summary_short", page.get("summary_short")),
                 ("summary_long", " ".join(page.get("summary_long") or []))):
        if words(v) > LIMITS[k]:
            over.append({k: words(v)})
    for c in page["cards"]:
        if words(c.get("text")) > LIMITS["card_text"] or words(c.get("title")) > LIMITS["card_title"]:
            over.append({"card": c.get("title"), "words": words(c.get("text"))})
    return {"repairs": log, "flags": flags, "over_length": over,
            "summary": {"cards": len(page["cards"]), "key_points": len(page["key_points"]), "timeline": len(page["timeline"]),
                        "single_source_cards": sum(c["single_source"] for c in page["cards"]), "repairs": len(log),
                        "unsupported_numbers": len(flags), "over_length": len(over),
                        "quotes": sum(1 for c in page["cards"] if c.get("quote"))}}


TAG = {"documento": "t-fact", "fatto": "t-fact", "posizioni": "t-pos", "dato": "t-data", "inchiesta": "t-inq"}
LANG = {"it": "italiano", "en": "inglese", "de": "tedesco", "fr": "francese", "es": "spagnolo"}


def render(page, notes, items):
    e = html.escape
    css = CSS.read_text()
    parts = [f"<title>Matrice — {e(page.get('title', ''))[:60]}</title>",
             '<meta name="claude:viewport-fit-sides" content="cover">',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">',
             f"<style>{css}</style>", '<div class="wrap">', "<header>",
             '<div class="eyebrow">MATRICE · GENERATA DA UBIK · ' + e(page.get("_arm", "")) + "</div>",
             f"<h1>{e(page.get('title', ''))}</h1>", '<div class="lead">', f"<p>{e(page.get('summary_short', ''))}</p>"]
    if page.get("summary_long"):
        parts.append('<details class="more"><summary>Leggi tutto</summary><div>' +
                     "".join(f"<p>{e(p)}</p>" for p in page["summary_long"]) + "</div></details>")
    parts += ["</div>", "</header>"]
    if page.get("key_points"):
        parts.append('<section><h2>Cosa c\'è da sapere</h2><div class="changes">' +
                     "".join(f"<div><h3>{e(k.get('heading', ''))}</h3><p>{e(k.get('text', ''))}</p></div>" for k in page["key_points"]) +
                     "</div></section>")
    parts.append('<section><h2>Le schede</h2><div class="cards">')
    for c in page["cards"]:
        iids = list(dict.fromkeys(r.split(":")[0] for r in c["support"]))
        cls = TAG.get(c.get("type"), "t-fact")
        parts.append(f'<article class="card {cls}">')
        if c["single_source"]:
            it = items[iids[0]]
            role = notes.get(iids[0], {}).get("source_role") or ""
            parts.append(f'<div class="one"><div class="top"><span class="tag">{e(c.get("type", ""))}</span>'
                         f'<span class="out">{e(it["publisher"])} <span>{e(role)} · {(it.get("published") or "")[:10]}</span></span></div>'
                         f'<div class="orig"><a href="{e(it["url"])}">«{e(it.get("title") or it["url"])}»</a></div></div>')
        else:
            parts.append(f'<span class="tag">{e(c.get("type", ""))}</span>')
        parts.append(f"<h3>{e(c.get('title', ''))}</h3><p>{e(c.get('text', ''))}</p>")
        if c.get("quote"):
            _, cl = claim(notes, c["quote"])
            tr = f'<span class="tr">«{e(c["quote_translation"])}»</span>' if c.get("quote_translation") else ""
            parts.append(f"<blockquote><q>{e(cl['quote'])}</q>{tr}</blockquote>")
        if not c["single_source"]:
            parts.append('<div class="src">' + " ".join(
                f'<a href="{e(items[i]["url"])}">{e(items[i]["publisher"])}, {(items[i].get("published") or "")[:10]}</a> · {LANG.get(items[i]["language"], items[i]["language"])}'
                for i in iids if i in items) + "</div>")
        parts.append("</article>")
    parts.append("</div></section>")
    if page.get("timeline"):
        parts.append('<section><h2>I passaggi</h2><div class="tl">' + "".join(
            f'<div class="ev"><time>{e(t.get("date", ""))}</time><p>{e(t.get("text", ""))}</p></div>' for t in page["timeline"]) +
            "</div></section>")
    used = sorted({items[r.split(":")[0]]["publisher"] for c in page["cards"] for r in c["support"] if r.split(":")[0] in items})
    parts.append(f'<section class="sources"><h2>Le fonti</h2><p><b>Usate nelle schede:</b> {e(", ".join(used))}.</p>'
                 f'<p><b>Lasciate fuori:</b> {e(page.get("left_out", ""))}</p></section>')
    ctl = page["controls"]["summary"]
    parts.append(f'<section class="method"><p>Controlli: {ctl["repairs"]} correzioni per rimozione, '
                 f'{ctl["unsupported_numbers"]} numeri senza riscontro, {ctl["over_length"]} testi oltre i limiti.</p></section></div>')
    return "\n".join(parts)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2)
