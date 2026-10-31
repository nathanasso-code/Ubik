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
    p_comp, h_comp = prompt(os.getenv("MATRIX_COMPOSE", "compose"), nucleus)
    p_rev, h_rev = prompt("revise", nucleus)
    p_fid, h_fid = prompt("fidelity", nucleus)
    notes_path = out_dir / "notes.json"
    notes = {"prompt_sha256": h_note, "model": DEEPSEEK, "notes": {}, "cost": 0.0, "errors": []}
    if notes_path.exists():
        prev = json.loads(notes_path.read_text())
        if prev.get("prompt_sha256") == h_note:
            notes = prev
    todo = [i for i in items if i not in notes["notes"]]
    out = {"version": "matrix-v1", "arm": arm, "model": MODELS[arm], "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"nota": h_note, "compose": h_comp, "revise": h_rev, "fidelity": h_fid}, "nucleus": nucleus, "preflight": [], "pages": [],
           "errors": [], "calls": [], "cost": {"compose": 0.0}}
    tag = os.getenv("MATRIX_TAG", "")
    path = out_dir / f"matrix-{arm}{tag}.json"

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
        if n.get("relevance") == "no" or iid not in items:  # notes of items no longer selected (e.g. duplicates)
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
        out["pages"].append(page)
        save()  # a paid page is never lost, whatever happens below
        try:
            revise(page, arm, p_rev, notes["notes"], out, run)
            page["violations"] = rule_violations(page, notes["notes"])
            page["controls"] = controls(page, notes["notes"], items)
            first = page["controls"]["repairs"]
            fidelity(page, notes["notes"], out, run, p_fid)
            page["controls"] = controls(page, notes["notes"], items)
            page["controls"]["repairs"] = first + page["controls"]["repairs"]
            page["controls"]["summary"]["repairs"] = len(page["controls"]["repairs"])
            (out_dir / f"matrix-{arm}{tag}-{run}.html").write_text(render(page, notes["notes"], items))
        except Exception:
            import traceback
            out["errors"].append({"run": run, "stage": "post", "error": traceback.format_exc()[-1500:]})
        save()
    out["notes_cost"] = notes["cost"]
    out["total_cost_usd"] = notes["cost"] + out["cost"]["compose"]
    out["status"] = "completed"
    save()
    print(json.dumps({"arm": arm, "notes": len(notes["notes"]), "relevant": len(listing), "notes_cost": notes["cost"],
                      "compose_cost": out["cost"]["compose"], "controls": [p["controls"]["summary"] for p in out["pages"]],
                      "violations": [[len(p["violations_before_revision"]), len(p["violations"])] for p in out["pages"]]}))


def card_body(c):
    """All the text of a card: a single card, or the intro and the sides of a comparison."""
    if c.get("type") == "confronto":
        return " ".join([c.get("intro") or ""] + [(x.get("label") or "") + " " + (x.get("text") or "")
                                                  for x in (c.get("sides") or []) if isinstance(x, dict)])
    return c.get("text") or ""


ACRONYM_OK = {"UE", "USA", "GDPR", "IA"}
ACRONYM = re.compile(r"\b(?:[A-Z]{2,}[a-z]?[A-Z]*|[A-Z]+&[A-Z]+)\b")
LEGAL = re.compile(r"\b(?:articol[oi]|art\.|allegat[oi])\s+[\dIVX]+", re.I)


def rule_violations(page, notes):
    """Writing rules of docs/matrix-spec.md checked in code; the list feeds one revision call."""
    v = []
    full = " ".join([page.get("title", ""), page.get("summary_short", "")] + (page.get("summary_long") or []) +
                    [k.get("heading", "") + " " + k.get("text", "") for k in page.get("key_points", [])] +
                    [c.get("title", "") + " " + card_body(c) for c in page.get("cards", [])] +
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
        check(f"cards[{i}]", c.get("title", "") + " " + card_body(c))
        if words(card_body(c)) > LIMITS["card_text"] + (40 if c.get("type") == "confronto" else 0) or words(c.get("title")) > LIMITS["card_title"]:
            v.append({"field": f"cards[{i}]", "rule": "length", "words": [words(c.get("title")), words(c.get("text"))]})
        refs = (c.get("support") or []) + [r for x in (c.get("sides") or []) if isinstance(x, dict) for r in (x.get("support") or [])]
        if not any(notes.get(r.split(":")[0], {}).get("relevance") == "core" for r in refs):
            v.append({"field": f"cards[{i}]", "rule": "off_core"})
    for i, t in enumerate(page.get("timeline", [])):
        check(f"timeline[{i}]", t.get("text"))
    if words(page.get("title")) > LIMITS["title"]:
        v.append({"field": "title", "rule": "length", "words": words(page.get("title"))})
    if words(page.get("summary_short")) > LIMITS["summary_short"]:
        v.append({"field": "summary_short", "rule": "length", "words": words(page.get("summary_short"))})
    return v


FIELDS = ("title", "summary_short", "summary_long", "key_points", "cards", "timeline", "left_out")


def revise(page, arm, p_rev, notes, out, run):
    """One revision call for the fields that break the writing rules. The model may return the whole page, the page
    wrapped in {"page": ...}, or only the changed fields: all three are merged; anything else is logged."""
    viol = rule_violations(page, notes)
    page["violations_before_revision"] = viol
    if not viol:
        return
    draft = {k: page[k] for k in FIELDS if k in page}
    try:
        raw, cost, secs = call(MODELS[arm], p_rev, {"page": draft, "violations": viol}, max_tokens=20000,
                               extra={"reasoning": {"effort": "low"}} if arm == "sonnet" else None)
    except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
        out["errors"].append({"run": run, "stage": "revise", "error": f"{type(exc).__name__}: {exc}"[:300]})
        return
    out["cost"]["compose"] += cost
    out["calls"].append({"run": run, "stage": "revise", "cost_usd": cost, "seconds": secs})
    content = raw["choices"][0]["message"].get("content") or ""
    try:
        rev = parse_json(content)
        if isinstance(rev, dict) and isinstance(rev.get("page"), dict):
            rev = rev["page"]
        rev = {k: v for k, v in rev.items() if k in FIELDS}
        if "cards" in rev and not isinstance(rev["cards"], list):
            raise ValueError("cards is not a list")
        if not rev:
            raise ValueError("no known field returned")
        # keep references the model must not change
        for key in ("key_points", "cards", "timeline"):
            if key in rev and len(rev[key]) == len(draft.get(key, [])):
                for new, old in zip(rev[key], draft[key]):
                    new.setdefault("support", old.get("support"))
                    if key == "cards":
                        new.setdefault("quote", old.get("quote"))
        page.update(rev)
        page["revised_fields"] = sorted(rev)
    except Exception as exc:
        out["errors"].append({"run": run, "stage": "revise", "error": f"{type(exc).__name__}: {exc}"[:200], "content_head": content[:400]})


def fidelity(page, notes, out, run, p_fid):
    """Sentence-by-sentence check of what we wrote against the claims cited in support (cheap model, one call).
    Corrections replace the sentence; a sentence with no correction is removed. Every check is logged."""
    def claims(refs):
        return [{k: (claim(notes, r)[1] or {}).get(k) for k in ("who", "statement", "date", "quote")} for r in refs]
    every = list(dict.fromkeys(r for x in (page.get("cards") or []) + (page.get("key_points") or [])
                               for r in (x.get("support") or [])))
    stmts = [{"id": "title", "text": page.get("title", ""), "claims": claims(every)},
             {"id": "summary_short", "text": page.get("summary_short", ""), "claims": claims(every)}]
    for i, k in enumerate(page.get("key_points", [])):
        stmts.append({"id": f"key_points[{i}].text", "text": k.get("text", ""), "claims": claims(k.get("support", []))})
    for i, c in enumerate(page.get("cards", [])):
        stmts.append({"id": f"cards[{i}].title", "text": c.get("title", ""), "claims": claims(c.get("support", []))})
        if c.get("type") == "confronto":
            for j, x in enumerate(c.get("sides", [])):
                stmts.append({"id": f"cards[{i}].sides[{j}].text", "text": x.get("text", ""), "claims": claims(x.get("support", []))})
        else:
            stmts.append({"id": f"cards[{i}].text", "text": c.get("text", ""), "claims": claims(c.get("support", []))})
    for i, t in enumerate(page.get("timeline", [])):
        stmts.append({"id": f"timeline[{i}].text", "text": t.get("text", ""), "claims": claims(t.get("support", []))})
    try:
        raw, cost, secs = call(DEEPSEEK, p_fid, {"statements": stmts}, max_tokens=6000)
        checks = parse_json(raw["choices"][0]["message"]["content"]).get("checks", [])
    except Exception as exc:
        out["errors"].append({"run": run, "stage": "fidelity", "error": f"{type(exc).__name__}: {exc}"[:300]})
        return
    out["cost"]["compose"] += cost
    out["calls"].append({"run": run, "stage": "fidelity", "cost_usd": cost, "seconds": secs})

    def locate(path):
        obj = page
        for part in re.findall(r"[a-z_]+|\[\d+\]", path):
            obj = obj[int(part[1:-1])] if part.startswith("[") else obj if part in ("text", "title") else obj[part]
        return obj
    applied, unapplied = [], []
    for ch in checks:
        if ch.get("verdict") in (None, "ok") or not ch.get("sentence"):
            continue
        cid = ch.get("id", "")
        try:
            if cid in ("title", "summary_short"):
                obj, key = page, cid
            else:
                field = cid.rsplit(".", 1)
                obj, key = locate(field[0]), field[1]
        except Exception:
            unapplied.append(ch)
            continue
        old = obj.get(key, "")
        new = ch.get("fix")
        if ch["sentence"] in old and (new or key in ("text", "summary_short")):
            obj[key] = re.sub(r"\s{2,}", " ", old.replace(ch["sentence"], new or "")).strip()
            applied.append(ch)
        else:
            unapplied.append(ch)
    page["fidelity"] = {"checked": len(stmts), "flagged": len([c for c in checks if c.get("verdict") not in (None, "ok")]),
                        "applied": applied, "unapplied": unapplied}


def revise_existing(selection_path, out_dir, arm):
    """Revision only, on pages already composed (no new composition): the cleanest before/after comparison."""
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    out_dir = Path(out_dir)
    path = out_dir / f"matrix-{arm}.json"
    out = json.loads(path.read_text())
    notes = json.loads((out_dir / "notes.json").read_text())["notes"]
    p_rev, h_rev = prompt("revise", sel["nucleus"])
    out["prompt_sha256"]["revise"] = h_rev
    try:
        preflight(f"matrix revise {arm}", len(out["pages"]) * EST[arm] / 2, CEILING_USD[arm], out["preflight"])
    except OverBudget as exc:
        raise SystemExit(str(exc))
    for page in out["pages"]:
        page.pop("violations", None)
        revise(page, arm, p_rev, notes, out, page["run"])
        page["violations"] = rule_violations(page, notes)
        page["controls"] = controls(page, notes, items)
        (out_dir / f"matrix-{arm}-{page['run']}.html").write_text(render(page, notes, items))
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"arm": arm, "violations": [[len(p["violations_before_revision"]), len(p["violations"])] for p in out["pages"]],
                      "errors": out["errors"][-2:]}))


def make_queries(selection_path, out_path):
    """Search queries in five languages for what the corpus lacks about the nucleus (one cheap call).
    MATRIX_QUERIES=queries-specialist asks for primary documents and specialist analyses instead of news."""
    sel = json.loads(Path(selection_path).read_text())
    p_q, h_q = prompt(os.getenv("MATRIX_QUERIES", "queries"), sel["nucleus"])
    have = [{"source": i["publisher"], "date": (i.get("published") or "")[:10], "title": i.get("title") or ""} for i in sel["items"]]
    raw, cost, secs = call(DEEPSEEK, p_q, {"items_already_collected": have}, max_tokens=3000)
    q = parse_json(raw["choices"][0]["message"]["content"])
    Path(out_path).write_text(json.dumps({"prompt_sha256": h_q, "model": DEEPSEEK, "cost_usd": cost, **q}, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"queries": len(q.get("queries", [])), "cost": cost}))


def claim(notes, ref):
    iid, _, cid = (ref or "").partition(":")
    c = next((x for x in notes.get(iid, {}).get("claims", []) if x.get("id") == cid), None)
    return iid, c


def controls(page, notes, items):
    """Remove what has no valid support, verify quotes, flag numbers without support and length overruns."""
    log, flags = [], []

    def valid(refs):
        return [r for r in (refs or []) if claim(notes, r)[1] is not None]

    for c in page.get("cards") or []:
        if c.get("type") != "confronto":
            continue
        sides = []
        for x in c.get("sides") or []:
            x["support"] = valid(x.get("support"))
            if x["support"]:
                sides.append(x)
            else:
                log.append({"removed": "side", "card": c.get("title"), "label": x.get("label")})
        c["sides"] = sides
        c["support"] = list(dict.fromkeys(r for x in sides for r in x["support"]))
        if len(sides) == 1:  # a comparison with one side left is an ordinary card
            c.update({"type": "posizioni", "text": sides[0].get("text", ""), "sides": []})
            log.append({"changed": "comparison_to_card", "card": c.get("title")})
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
        c["single_source"] = len(origins) == 1 and c.get("type") != "confronto"
        # numbers in our text must appear in the cited claims or cited texts
        hay = norm(" ".join([(claim(notes, r)[1] or {}).get("statement", "") + " " + (claim(notes, r)[1] or {}).get("quote", "")
                             for r in c["support"]] + [items[r.split(":")[0]]["text"] for r in c["support"] if r.split(":")[0] in items]))
        for num in set(re.findall(r"\d[\d.,]*\d|\d", c.get("title", "") + " " + card_body(c))):
            if num.replace(".", "").replace(",", "") not in hay.replace(".", "").replace(",", ""):
                flags.append({"card": c.get("title"), "unsupported_number": num})
    over = []
    for k, v in (("title", page.get("title")), ("summary_short", page.get("summary_short")),
                 ("summary_long", " ".join(page.get("summary_long") or []))):
        if words(v) > LIMITS[k]:
            over.append({k: words(v)})
    for c in page["cards"]:
        if words(card_body(c)) > LIMITS["card_text"] + (40 if c.get("type") == "confronto" else 0) or words(c.get("title")) > LIMITS["card_title"]:
            over.append({"card": c.get("title"), "words": words(card_body(c))})
    return {"repairs": log, "flags": flags, "over_length": over,
            "summary": {"cards": len(page["cards"]), "key_points": len(page.get("key_points") or []), "timeline": len(page.get("timeline") or []),
                        "single_source_cards": sum(bool(c.get("single_source")) for c in page["cards"]), "repairs": len(log),
                        "unsupported_numbers": len(flags), "over_length": len(over),
                        "quotes": sum(1 for c in page["cards"] if c.get("quote"))}}


MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def data_it(d):
    m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?", d or "")
    if not m:
        return d or ""
    y, mo, dd = m.groups()
    return (f"{int(dd)} " if dd else "") + f"{MESI[int(mo) - 1]} {y}"


TAG = {"confronto": "t-cmp", "documento": "t-fact", "fatto": "t-fact", "posizioni": "t-pos", "dato": "t-data", "inchiesta": "t-inq"}
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
        if c.get("type") == "confronto":
            parts.append('<span class="tag">confronto</span>')
        elif c["single_source"]:
            it = items[iids[0]]
            role = notes.get(iids[0], {}).get("source_role") or ""
            parts.append(f'<div class="one"><div class="top"><span class="tag">{e(c.get("type", ""))}</span>'
                         f'<span class="out">{e(it["publisher"])} <span>{e(role)} · {data_it((it.get("published") or "")[:10])}</span></span></div>'
                         f'<div class="orig"><a href="{e(it["url"])}">«{e(it.get("title") or it["url"])}»</a></div></div>')
        else:
            parts.append(f'<span class="tag">{e(c.get("type", ""))}</span>')
        if c.get("type") == "confronto":
            parts.append(f"<h3>{e(c.get('title', ''))}</h3><p>{e(c.get('intro', ''))}</p><div class=\"sides\">")
            for x in c.get("sides", []):
                sids = list(dict.fromkeys(r.split(":")[0] for r in x.get("support", [])))
                srcs = " ".join(f'<a href="{e(items[i]["url"])}">{e(items[i]["publisher"])}</a>' for i in sids if i in items)
                parts.append(f'<div class="side"><div class="who">{e(x.get("label", ""))}</div><p>{e(x.get("text", ""))}</p>'
                             f'<div class="src">{srcs}</div></div>')
            parts.append("</div></article>")
            continue
        parts.append(f"<h3>{e(c.get('title', ''))}</h3><p>{e(c.get('text', ''))}</p>")
        if c.get("quote"):
            _, cl = claim(notes, c["quote"])
            tr = f'<span class="tr">«{e(c["quote_translation"])}»</span>' if c.get("quote_translation") else ""
            parts.append(f"<blockquote><q>{e(cl['quote'])}</q>{tr}</blockquote>")
        if not c["single_source"]:
            parts.append('<div class="src">' + " ".join(
                f'<a href="{e(items[i]["url"])}">{e(items[i]["publisher"])}, {data_it((items[i].get("published") or "")[:10])}</a> · {LANG.get(items[i]["language"], items[i]["language"])}'
                for i in iids if i in items) + "</div>")
        parts.append("</article>")
    parts.append("</div></section>")
    if page.get("timeline"):
        parts.append('<section><h2>I passaggi</h2><div class="tl">' + "".join(
            f'<div class="ev"><time>{e(data_it(t.get("date", "")))}</time><p>{e(t.get("text", ""))}</p></div>' for t in page["timeline"]) +
            "</div></section>")
    used = sorted({items[r.split(":")[0]]["publisher"] for c in page["cards"] for r in c["support"] if r.split(":")[0] in items})
    parts.append(f'<section class="sources"><h2>Le fonti</h2><p><b>Usate nelle schede:</b> {e(", ".join(used))}.</p>'
                 f'<p><b>Lasciate fuori:</b> {e(page.get("left_out", ""))}</p></section>')
    ctl = page["controls"]["summary"]
    parts.append(f'<section class="method"><p>Controlli: {ctl["repairs"]} correzioni per rimozione, '
                 f'{ctl["unsupported_numbers"]} numeri senza riscontro, {ctl["over_length"]} testi oltre i limiti.</p></section></div>')
    return "\n".join(parts)


if __name__ == "__main__":
    if os.getenv("MATRIX_MODE") == "queries":
        make_queries(sys.argv[1], sys.argv[2])
    elif os.getenv("MATRIX_MODE") == "revise":
        revise_existing(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2)
