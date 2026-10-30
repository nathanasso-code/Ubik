"""Ubik v6 (experimental): reading notes per item, one editorial composition per week, mechanical controls.

  1. scheda     one call per item: kind, perimeter, up to 4 facts and 3 theses, each with a verbatim quote
  2. compose    one call per week over all notes: facts (cards), comments, analyses, excluded with reasons
  3. controls   no model: quotes found verbatim in the text, every item accounted for, references valid,
                independent origins per fact (an outlet's feeds count once)
Notes are made once per model; the composition runs N times to measure stability.
Runs only in the private corpus repository (inputs are full texts).

Usage: python -m ingestion.ubik_v6_editorial SELECTION.json OUT_DIR deepseek|sonnet [compose_runs]
"""
import hashlib
import json
import urllib.error
import os
import re
import sys
import unicodedata
from pathlib import Path

from ingestion.ubik_cost_guard import OverBudget, preflight
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_ukraine_v5_model_audit import EXPECTED_MODEL as SONNET

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "v6"
MODELS = {"deepseek": DEEPSEEK, "sonnet": SONNET}
PERIMETER = ("Rules for AI in Europe and the United States: laws, regulation, enforcement, courts, governance and "
             "public policy on AI, including how governments use or restrict AI. Elsewhere in the world only when "
             "it directly concerns European or US rules.")
TEXT_CHARS = 8000
CEILING_USD = {"deepseek": 0.30, "sonnet": 1.20}
EST_PER_CALL = {"deepseek": {"scheda": 0.0015, "compose": 0.01}, "sonnet": {"scheda": 0.012, "compose": 0.12}}


def prompt(name, variant="base"):
    folder = {"v62": PROMPTS.parent / "v6.2", "v63": PROMPTS.parent / "v6.3"}.get(variant, PROMPTS)
    raw = (folder / f"{name}.txt").read_text()
    return raw.replace("{PERIMETER}", PERIMETER), hashlib.sha256(raw.encode()).hexdigest()


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def parse_json(content):
    # strict=False accepts raw newlines and tabs inside strings, which Sonnet emits in long Italian text
    return json.loads((content or "").strip().removeprefix("```json").removesuffix("```").strip(), strict=False)


MONTHS = {m: i for i, names in enumerate([
    ("january", "gennaio", "enero", "januar", "janvier"), ("february", "febbraio", "febrero", "februar", "février"),
    ("march", "marzo", "marzo", "märz", "mars"), ("april", "aprile", "abril", "april", "avril"),
    ("may", "maggio", "mayo", "mai", "mai"), ("june", "giugno", "junio", "juni", "juin"),
    ("july", "luglio", "julio", "juli", "juillet"), ("august", "agosto", "agosto", "august", "août"),
    ("september", "settembre", "septiembre", "september", "septembre"), ("october", "ottobre", "octubre", "oktober", "octobre"),
    ("november", "novembre", "noviembre", "november", "novembre"), ("december", "dicembre", "diciembre", "dezember", "décembre")], 1)
    for m in names}


GATE = {"max_linkage_mismatch": 2, "attempts": 3, "max_repairs": 5}


STOP_NAMES = {"il", "lo", "la", "i", "gli", "le", "un", "una", "uno", "secondo", "dopo", "con", "per", "nel", "nella", "dal", "dalla"}


def proper_names(statement):
    """Capitalised words after the first one (names of people, bodies, places), language-neutral enough to be
    checked against an English or German source by a five-letter prefix."""
    words = re.findall(r"[A-Za-zÀ-ÿ][\wÀ-ÿ'’-]*", statement or "")
    return {w.lower()[:5] for w in words[1:] if w[0].isupper() and len(w) >= 3 and w.lower() not in STOP_NAMES}


def names_found(names, items, schede, ref):
    """A page fact must share at least one name with the note and text it cites; otherwise the reference is wrong."""
    iid = ref.get("item_id")
    nf = next((x for x in schede.get(iid, {}).get("facts", []) if x.get("id") == ref.get("fact_ref")), {})
    hay = norm(" ".join([nf.get("statement") or "", nf.get("quote") or "", nf.get("according_to") or "",
                         items.get(iid, {}).get("title") or "", items.get(iid, {}).get("text") or ""]))
    return any(re.search(r"\b" + re.escape(n), hay) for n in names)


def repair(page, schede, items):
    """Repair by removal (code, no model): references to notes that do not exist are removed, entries for unknown
    items are dropped, items the composition forgot are listed as excluded "non_valutato". Every repair is logged
    and shown; nothing is added that the model did not write."""
    log = []
    def fact_ok(iid, ref):
        return any(x.get("id") == ref for x in schede.get(iid, {}).get("facts", []))
    def thesis_ok(iid, ref):
        return any(x.get("id") == ref for x in schede.get(iid, {}).get("theses", []))
    for f in page["facts"]:
        keep = [r for r in f["items"] if r.get("item_id") in schede and fact_ok(r["item_id"], r.get("fact_ref"))]
        for r in f["items"]:
            if r not in keep:
                log.append({"removed": "fact_source", "fact": f.get("id"), "item": r.get("item_id"), "ref": r.get("fact_ref")})
        names = proper_names(f.get("statement"))
        if len(names) >= 2:
            ok = [r for r in keep if names_found(names, items, schede, r)]
            for r in keep:
                if r not in ok:
                    log.append({"removed": "fact_source_mismatch", "fact": f.get("id"), "item": r.get("item_id"), "ref": r.get("fact_ref"),
                                "names": sorted(names)})
            keep = ok
        f["items"] = keep
    dropped = [f.get("id") for f in page["facts"] if not f["items"]]
    for fid in dropped:
        log.append({"removed": "fact_without_valid_source", "fact": fid})
    page["facts"] = [f for f in page["facts"] if f["items"]]
    for key in ("comments", "analyses"):
        keep = []
        for c in page[key]:
            if c.get("item_id") in schede and thesis_ok(c["item_id"], c.get("thesis_ref")):
                keep.append(c)
            else:
                log.append({"removed": key[:-1], "item": c.get("item_id"), "ref": c.get("thesis_ref")})
        page[key] = keep
    page["excluded"] = [e for e in page["excluded"] if e.get("item_id") in schede or log.append({"removed": "excluded_unknown", "item": e.get("item_id")})]
    seen = {r["item_id"] for f in page["facts"] for r in f["items"]} | {c["item_id"] for c in page["comments"] + page["analyses"]} | \
           {e["item_id"] for e in page["excluded"]}
    for iid in schede:
        if iid not in seen:
            page["excluded"].append({"item_id": iid, "reason": "non_valutato", "redundant_with": None})
            log.append({"added": "excluded_non_valutato", "item": iid})
    page["repairs"] = log
    return log
HIGHLIGHT = 5


def gate(page):
    """Acceptance gate (code, no model): a page that loses or invents items, cites missing notes, repeats entries
    or duplicates facts is rejected and recomposed."""
    c = page.get("controls", {})
    if "error" in c:
        return ["control_error"]
    s, why = c["summary"], []
    for k in ("missing", "unknown", "bad_refs"):
        if s.get(k):
            why.append(k)
    if len(page.get("repairs", [])) > GATE["max_repairs"]:
        why.append("too_many_repairs")
    if s.get("comment_linkage_mismatch", 0) > GATE["max_linkage_mismatch"]:
        why.append("linkage")
    if c.get("possible_duplicate_facts"):
        why.append("duplicate_facts")
    entries = [(x.get("item_id"), x.get("thesis_ref")) for x in page["comments"] + page["analyses"]]
    if len(entries) != len(set(entries)):
        why.append("repeated_entries")
    return why


def rank_facts(page, window_start=None):
    """Display rule (code): independent confirmations first, then official source, then distinct outlets, then
    distinct items (not references: several notes of one item merged into a fact must not push it up)."""
    # window_start is kept for the signature; a staleness rule on note dates was tried on 30 Oct and dropped:
    # the notes get the year wrong (Texas and Nvidia, both of the week, dated 2025), so it hid real facts.
    def key(f):
        valid = f.get("type") in ("event", "report")
        return (not valid, -f.get("independent_count", 1), not f.get("official"), -len(f.get("independent_origins", [])),
                -len({r.get("item_id") for r in f.get("items", [])}))
    order = sorted(page["facts"], key=key)
    for i, f in enumerate(order):
        f["highlight"] = i < HIGHLIGHT
    page["facts"] = order


def main(selection_path, out_dir, arm, compose_runs=2, variant="base", previous_path=None):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    model = MODELS[arm]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    p_scheda, h_scheda = prompt("scheda", variant)
    p_compose, h_compose = prompt("compose", variant)
    out = {"version": "v6-experimental", "arm": arm, "model": model, "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"scheda": h_scheda, "compose": h_compose}, "window": sel.get("window"),
           "preflight": [], "errors": [], "calls": [], "schede": {}, "pages": [], "cost": {"scheda": 0.0, "compose": 0.0}}
    out["variant"] = variant
    path = out_dir / ((f"v6-{arm}.json" if variant == "base" else f"v6-{arm}-{variant}.json") if previous_path is None
                      else f"v6-{arm}-{variant}-{(sel.get('window') or ['x'])[0]}.json")
    for notes_from in [path] + sorted(out_dir.glob(f"v6-{arm}*.json")):  # resume notes already paid for
        if not notes_from.exists():
            continue
        prev = json.loads(notes_from.read_text())
        if (prev.get("prompt_sha256", {}).get("scheda") == h_scheda and prev.get("model") == model
                and prev.get("window") == sel.get("window") and prev.get("schede")):
            out["schede"], out["cost"]["scheda"] = prev["schede"], prev.get("cost", {}).get("scheda", 0.0)
            out["resumed_notes_from"] = notes_from.name
            break

    def save():
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")

    def spend(stage, cost, extra):
        out["cost"][stage] += cost
        out["calls"].append({"stage": stage, "cost_usd": cost, **extra})
        if sum(out["cost"].values()) > CEILING_USD[arm]:
            out["status"] = "aborted_cost_ceiling"
            save()
            raise SystemExit("Cost ceiling exceeded")

    est = out["cost"]["scheda"] + len(set(items) - set(out["schede"])) * EST_PER_CALL[arm]["scheda"] + compose_runs * EST_PER_CALL[arm]["compose"]
    try:
        preflight(f"v6 {arm}", est, CEILING_USD[arm], out["preflight"])
    except OverBudget as exc:
        out["status"] = "refused_preflight"
        save()
        raise SystemExit(str(exc))

    # 1. notes
    for iid, it in items.items():
        if iid in out["schede"]:
            continue
        payload = {"item_id": iid, "kind_hint": it["kind"], "source": it["source_id"], "language": it["language"],
                   "title": it.get("title") or "", "text": it["text"][:TEXT_CHARS]}
        for attempt in (1, 2):
            try:
                raw, cost, secs = call(model, p_scheda, payload)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
                body = exc.read(500).decode("utf-8", "replace") if isinstance(exc, urllib.error.HTTPError) else ""
                out["errors"].append({"stage": "scheda", "item": iid, "attempt": attempt, "error": f"{type(exc).__name__}: {exc} {body}"[:400]})
                save()
                continue
            spend("scheda", cost, {"item": iid, "attempt": attempt, "seconds": secs})
            try:
                note = parse_json(raw["choices"][0]["message"]["content"])
                assert note.get("item_id") == iid and isinstance(note.get("facts"), list) and isinstance(note.get("theses"), list)
            except Exception as exc:
                out["errors"].append({"stage": "scheda", "item": iid, "attempt": attempt, "error": str(exc)[:200]})
                continue
            src = norm((it.get("title") or "") + " " + it["text"][:TEXT_CHARS])
            for x in note["facts"] + note["theses"]:
                q = norm(x.get("quote"))
                x["quote_verified"] = bool(q) and q in src
            out["schede"][iid] = note
            break
        save()

    # 2. composition, N runs
    notes = out["schede"]
    listing = [{"item_id": iid, "source": items[iid]["source_id"], "origin": items[iid]["origin"], "kind_hint": items[iid]["kind"],
                "published": (items[iid].get("published") or "")[:10], "title": items[iid].get("title") or "",
                "note": {k: v for k, v in n.items() if k != "item_id"} | {
                    "facts": [{k: f[k] for k in ("id", "type", "statement", "date", "reported_as_new", "according_to") if k in f} for f in n["facts"]],
                    "theses": [{k: t[k] for k in ("id", "claim", "about_fact") if k in t} for t in n["theses"]]}}
               for iid, n in notes.items()]
    previous = []
    if previous_path and Path(previous_path).exists():
        prevd = json.loads(Path(previous_path).read_text())
        acc = next((p for p in prevd.get("pages", []) if p.get("accepted")), None)
        if acc:
            wk = (prevd.get("window") or ["?"])[0]
            previous = [{"id": f"{wk}:{f.get('id')}", "statement": f.get("statement"), "date": f.get("date")} for f in acc["facts"]]
            out["previous_page"] = {"file": Path(previous_path).name, "facts": len(previous)}
    payload = {"week": sel.get("window"), "notes": listing}
    if previous:
        payload["previous_facts"] = previous
    for run in range(1, compose_runs + 1):
        for attempt in range(1, GATE["attempts"] + 1):
            page = None
            try:
                # Sonnet spends mandatory reasoning tokens inside max_tokens: keep reasoning low and allow a long page
                raw, cost, secs = call(model, p_compose, payload, max_tokens=20000,
                                       extra={"reasoning": {"effort": "low"}} if arm == "sonnet" else None)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, KeyError) as exc:
                body = exc.read(500).decode("utf-8", "replace") if isinstance(exc, urllib.error.HTTPError) else ""
                out["errors"].append({"stage": "compose", "run": run, "attempt": attempt, "error": f"{type(exc).__name__}: {exc} {body}"[:400]})
                save()
                continue
            u = raw.get("usage") or {}
            spend("compose", cost, {"run": run, "attempt": attempt, "seconds": secs, "completion_tokens": u.get("completion_tokens"),
                                    "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                                    "finish_reason": raw["choices"][0].get("finish_reason")})
            try:
                page = parse_json(raw["choices"][0]["message"]["content"])
                assert all(isinstance(page.get(k), list) for k in ("facts", "comments", "analyses", "excluded"))
            except Exception as exc:
                content = raw["choices"][0]["message"].get("content") or ""
                out["errors"].append({"stage": "compose", "run": run, "attempt": attempt, "error": str(exc)[:200],
                                      "finish_reason": raw["choices"][0].get("finish_reason"), "content_len": len(content),
                                      "content_tail": content[-300:]})
                continue
            normalise(page)
            page["controls_before_repair"] = None
            try:
                page["controls_before_repair"] = controls(json.loads(json.dumps(page)), out["schede"], items)["summary"]
                repair(page, out["schede"], items)
                page["controls"] = controls(page, out["schede"], items)
                page["controls"].update(date_and_duplicate_checks(page, out["schede"], items))
            except Exception as exc:  # a control bug must not lose a paid page
                import traceback
                page["controls"] = {"error": traceback.format_exc()[-1500:], "summary": {"control_error": str(exc)[:200]}}
            if previous:
                ids = {p["id"] for p in previous}
                for f in page["facts"]:
                    if f.get("continues") and f["continues"] not in ids:
                        page["controls"].setdefault("bad_continues", []).append([f.get("id"), f["continues"]])
                        f["continues"] = None
            page["run"], page["attempt"] = run, attempt
            page["rejected_by_gate"] = gate(page)
            page["accepted"] = not page["rejected_by_gate"]
            if "error" not in page["controls"]:
                rank_facts(page, (sel.get("window") or [None])[0])
            out["pages"].append(page)
            save()
            if page["accepted"]:
                break
    out["total_cost_usd"] = sum(out["cost"].values())
    out["status"] = "completed"
    save()
    suffix = "" if variant == "base" else f"-{variant}"
    stem = f"v6-{arm}{suffix}" + (f"-{(sel.get('window') or ['x'])[0]}" if previous_path is not None else "")
    for page in out["pages"]:
        if page.get("accepted"):
            (out_dir / f"{stem}-page{page['run']}.md").write_text(render(page, items, arm, page["run"]))
    print(json.dumps({"arm": arm, "notes": len(out["schede"]), "pages": len(out["pages"]), "cost": out["cost"],
                      "controls": [p["controls"]["summary"] for p in out["pages"]]}))


def normalise(page):
    """Tolerate small shape deviations from the model without changing content."""
    for f in page.get("facts", []):
        f["items"] = [r if isinstance(r, dict) else {"item_id": str(r), "fact_ref": None} for r in (f.get("items") or [])]
        for k in ("statement", "what_sources_add"):
            f[k] = f.get(k) or ""
    for key in ("comments", "analyses", "excluded"):
        page[key] = [c for c in page.get(key, []) if isinstance(c, dict)]


def controls(page, schede, items):
    refs_bad, accounted = [], set()
    for f in page["facts"]:
        origins = set()
        for r in f.get("items", []):
            iid, ref = r.get("item_id"), r.get("fact_ref")
            accounted.add(iid)
            note = schede.get(iid)
            match = note and next((x for x in note["facts"] if x.get("id") == ref), None)
            if not match:
                refs_bad.append({"where": f.get("id"), "item": iid, "ref": ref})
            if iid in items:
                origins.add(items[iid]["origin"])
        # Independent confirmations are outlets (origins). Outlets that attribute the fact to the same original
        # source, or one that cites another outlet of the page as its source, collapse into one. Several sources
        # quoted inside ONE outlet never count as several confirmations.
        attrib = {}
        for r in f.get("items", []):
            iid = r.get("item_id")
            nf = next((x for x in schede.get(iid, {}).get("facts", []) if x.get("id") == r.get("fact_ref")), {})
            acc = (nf.get("according_to") or "").strip().lower()
            o = items.get(iid, {}).get("origin", iid)
            attrib.setdefault(o, set())
            if acc and acc not in ("own reporting", "unspecified", "unknown", "none"):
                attrib[o].add(acc)
        parent = {o: o for o in attrib}
        def find(o):
            while parent[o] != o:
                o = parent[o]
            return o
        def tokens(o):
            return {t for t in re.split(r"[-_ ]", o) if len(t) >= 4 and t not in ("policy", "tech", "news", "press", "europe", "digital")}
        olist = sorted(attrib)
        for a in olist:
            for b in olist:
                if a < b and (attrib[a] & attrib[b] or any(t in acc for t in tokens(a) for acc in attrib[b])
                              or any(t in acc for t in tokens(b) for acc in attrib[a])):
                    parent[find(b)] = find(a)
        originals = sorted({acc for v in attrib.values() for acc in v})
        f["official"] = any(re.search(r"gazzetta|official|council|commission|parliament|court|filing|press release|federal register|ministry|government|regulator|garante|cnil|ftc", o) for o in originals) or \
            any(items.get(r.get("item_id"), {}).get("source_type") == "primary_official" for r in f.get("items", []))
        f["original_sources"] = originals
        if not f.get("date"):
            pubs = sorted((items[r["item_id"]].get("published") or "")[:10] for r in f.get("items", []) if r.get("item_id") in items)
            pubs = [x for x in pubs if x]
            if pubs:
                f["date"], f["date_source"] = pubs[0], "pubblicazione"
        f["independent_origins"] = sorted(origins)
        f["verified_quotes"] = sum(1 for r in f.get("items", []) for x in (schede.get(r.get("item_id"), {}).get("facts", []))
                                   if x.get("id") == r.get("fact_ref") and x.get("quote_verified"))
        independent = len({find(o) for o in attrib}) if attrib else len(origins)
        f["independent_count"] = independent
        per_item = {}
        for r in f.get("items", []):
            per_item[r.get("item_id")] = per_item.get(r.get("item_id"), 0) + 1
        f["note_dates"] = sorted({nf.get("date") for r in f.get("items", []) for nf in schede.get(r.get("item_id"), {}).get("facts", [])
                                  if nf.get("id") == r.get("fact_ref") and nf.get("date")})
        f["bundled_note_facts"] = max(per_item.values(), default=0)  # >2: one outlet's several facts merged into one
        f["status"] = "più origini" if len(origins) >= 2 and independent >= 2 else ("fonte originale unica" if len(origins) >= 2 else "origine unica")
    for key in ("comments", "analyses"):
        for c in page[key]:
            iid, ref = c.get("item_id"), c.get("thesis_ref")
            accounted.add(iid)
            note = schede.get(iid)
            match = note and next((x for x in note["theses"] if x.get("id") == ref), None)
            c["quote_verified"] = bool(match and match.get("quote_verified"))
            if key == "comments" and match and match.get("about_fact"):
                fact = next((f for f in page["facts"] if f.get("id") == c.get("fact")), None)
                if not fact or not any(r.get("item_id") == iid and r.get("fact_ref") == match["about_fact"] for r in fact.get("items", [])):
                    c["linkage_check"] = "mismatch"
            if not match:
                refs_bad.append({"where": key, "item": iid, "ref": ref})
    for e in page["excluded"]:
        accounted.add(e.get("item_id"))
    missing = sorted(set(schede) - accounted)
    unknown = sorted(accounted - set(schede) - {None})
    return {"missing_items": missing, "unknown_items": unknown, "bad_references": refs_bad,
            "summary": {"facts": len(page["facts"]), "multi_origin_facts": sum(f["status"] == "più origini" for f in page["facts"]),
                        "comments": len(page["comments"]), "analyses": len(page["analyses"]), "excluded": len(page["excluded"]),
                        "missing": len(missing), "unknown": len(unknown), "bad_refs": len(refs_bad),
                        "comment_quotes_verified": sum(c["quote_verified"] for c in page["comments"] + page["analyses"]),
                        "comment_linkage_mismatch": sum(c.get("linkage_check") == "mismatch" for c in page["comments"]),
                        "report_facts": sum(f.get("type") == "report" for f in page["facts"])}}


def date_and_duplicate_checks(page, schede, items):
    unsupported, dup = [], []
    for f in page["facts"]:
        cited = list(dict.fromkeys(r.get("item_id") for r in f.get("items", [])))
        texts = " ".join(norm(items[i]["text"]) for i in cited if i in items)
        note_dates = {x.get("date") for i in cited for x in schede.get(i, {}).get("facts", [])}
        if f.get("date") and not f.get("date_source") and f["date"] not in note_dates:
            unsupported.append({"fact": f.get("id"), "date": f["date"], "where": "date"})
        for day, month in re.findall(r"\b(\d{1,2})\s+([a-zà-ü]+)", norm(f.get("what_sources_add", "") + " " + f.get("statement", ""))):
            if month in MONTHS:
                names = [m for m, i in MONTHS.items() if i == MONTHS[month]]
                if not any(re.search(rf"\b{day}\.?\s+(de\s+)?{m}\b|\b{m}\s+{day}\b", texts) for m in names):
                    unsupported.append({"fact": f.get("id"), "date": f"{day} {month}", "where": "text"})
    sets = [(f.get("id"), {(r.get("item_id"), r.get("fact_ref")) for r in f.get("items", [])},
             {items[r.get("item_id")]["origin"] for r in f.get("items", []) if r.get("item_id") in items}) for f in page["facts"]]
    for a in range(len(sets)):
        for b in range(a + 1, len(sets)):
            ia, ib = {i for i, _ in sets[a][1]}, {i for i, _ in sets[b][1]}
            if sets[a][1] & sets[b][1] or (ia and ib and (ia <= ib or ib <= ia)):
                dup.append([sets[a][0], sets[b][0]])
    return {"unsupported_dates": unsupported, "possible_duplicate_facts": dup}


def render(page, items, arm, k):
    def src(iid):
        it = items.get(iid, {})
        return f"[{it.get('source_id', iid)}]({it.get('url', '')})"
    lines = [f"# Pagina v6 — {arm}, composizione {k}", ""]
    hl = [f for f in page["facts"] if f.get("highlight", True)]
    rest = [f for f in page["facts"] if not f.get("highlight", True)]
    for title, group in (("## Fatti in evidenza", hl), ("## Altri fatti della settimana", rest)):
      if not group:
        continue
      lines += [title, ""]
      for f in group:
        kind = "rapporto o inchiesta" if f.get("type") == "report" else "evento"
        orig = f"; fonte originale: {', '.join(f['original_sources'])}" if f.get("original_sources") else ""
        dsrc = " (data di pubblicazione)" if f.get("date_source") else ""
        cont = f"; prosegue {f['continues']}" if f.get("continues") else ""
        lines += [f"**{f.get('id')} — {f.get('statement')}** ({kind}; {f.get('date') or 's.d.'}{dsrc}; {f['status']}{orig}{cont})", "",
                  "Fonti: " + ", ".join(src(i) for i in dict.fromkeys(r.get("item_id") for r in f.get("items", []))), "", f.get("what_sources_add", ""), ""]
    lines += ["## Commenti ai fatti", ""] + [f"- **{c.get('fact')} — {src(c.get('item_id'))}.** {c.get('point')}" for c in page["comments"]]
    lines += ["", "## Analisi", ""] + [f"- **{src(a.get('item_id'))}.** {a.get('point')}" for a in page["analyses"]]
    lines += ["", "## Escluse", ""] + [f"- {src(e.get('item_id'))}: {e.get('reason')}" + (f" (come {e.get('redundant_with')})" if e.get("redundant_with") else "")
                                       for e in page["excluded"]]
    c = page["controls"]["summary"]
    lines += ["", "## Controlli", "", json.dumps(c, ensure_ascii=False)]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2,
         sys.argv[5] if len(sys.argv) > 5 else "base", sys.argv[6] if len(sys.argv) > 6 else None)
