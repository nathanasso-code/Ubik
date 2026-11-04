"""Ubik daily matrici v4 (prototype): the model proposes, the code confirms.
Each note describes the item's main event in structured form (actor, action, object, date; canonical English names).
The model proposes matrici and cards over whole items; the code keeps only the links it can confirm:
  same event   = event dates, when both known, at most 10 days apart, and one of:
                 (a) the objects share a significant word AND (the actors share one OR the objects share two);
                 (b) actor and object share a proper name (Delaware, Anthropic, Reddit), not a generic institution;
                 (c) title, main referent and object share a two-word phrase ("data center", "Kids Act").
                 Each confirmed link records which evidence was used.
  cards        = one card per matrice by default; the model opens a separate card only for a distinct fact or for
                 something the other items contradict or lack ("distinct": "fact" / "adds"), never for angle or kind of
                 piece. The code then fuses two cards when their items share actor AND object of the event and neither
                 card was marked distinct (same test as the unions, applied to the splits).
  twin matrici = in the merge pass, two matrici of the same week about the same object are fused when the model
                 proposes it and the code confirms one item pair, or, unasked, when at least half of the items of each
                 matrice share two object words (besides the actors' names) with an item of the other.
A matrice is a connected group of confirmed items with at least two independent outlets; anything not confirmed is
shown as a single card. Titles are written only from the summaries.

Usage: python -m ingestion.ubik_daily4 SELECTION.json OUT_DIR
"""
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.error
from pathlib import Path

from ingestion import ubik_daily2 as v2
from ingestion import ubik_daily3 as v3
from ingestion.ubik_cost_guard import OverBudget, preflight
from ingestion.ubik_extraction_pilot import call
from ingestion.ubik_ukraine_v51_judge import DEEPSEEK
from ingestion.ubik_v6_editorial import PERIMETER, norm, parse_json

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "daily-v4"
TEXT_CHARS = 8000
GENERIC = {"the", "and", "for", "with", "from", "into", "over", "about", "regulation", "regulations", "rules", "rule", "law",
           "laws", "policy", "policies", "proposal", "proposals", "act", "data", "european", "union", "state", "states",
           "united", "court", "case", "plan", "bill", "report", "study", "new", "national", "federal", "government",
           "artificial", "intelligence", "model", "models", "system", "systems", "company", "companies", "industry",
           "center", "centers", "centre", "centres", "public", "digital", "online", "global", "framework", "package",
           "use", "uses", "using", "access", "content", "contents", "work", "works", "art", "news", "media", "journal",
           "inside", "generated", "ai-generated", "knowledge", "tool", "tools", "launch", "release", "results", "strategy",
           "deal", "deals", "market", "markets", "service", "services", "product", "products", "people", "users", "trend"}
NAME_GENERIC = {"news", "media", "journal", "inside", "times", "post", "institute", "report", "new", "world", "global",
                "state", "states", "united", "european", "union", "court", "district", "department", "government", "council",
                "commission", "eu", "us", "usa", "ai", "the", "and", "for", "congress", "parliament", "senate", "house", "foundation",
                "university", "universities", "institute", "institution", "group", "democracy", "democratic", "security", "appeal",
                "appeals", "electronic", "frontier", "agency", "authority", "ministry", "office", "association", "observatory",
                "network", "committee", "center", "centre", "researchers", "national", "federal"}
STOP = set("""the and for of a an in on to is are was this that with by at from it its how why what who will would
il lo la i gli le di da del della dei delle degli un una e ed in su per con tra fra che non sul sulla sui nel nella nei negli
al alla alle ai agli dal dalla dalle come perché cosa chi
der die das und von zu im mit auf den des ein eine ist wie
el los las de y en por con para se lo que como
le les du et à au aux pour sur est des une""".split())
PHRASE_GENERIC = {"artifi intell", "intell artifi", "europe commis", "commis europe", "united states", "stati uniti",
                  "europe union", "unione europe", "big tech", "social media", "ai act", "elezio midter"}
KIND_GROUP = {"cronaca": "report", "documento": "report", "reazione": "reaction", "analisi": "reading", "commento": "reading",
              "altro": "report"}


def prompt(name):
    raw = (PROMPTS / f"{name}.txt").read_text()
    return raw.replace("{PERIMETER}", PERIMETER), hashlib.sha256(raw.encode()).hexdigest()


def toks(s, generic=True):
    words = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'\-]{2,}", s or "")
    return {w.lower()[:6] for w in words if not (generic and w.lower() in GENERIC) and w.lower() not in ("the", "and", "for", "of")}


def names(e, field=None):
    s = (e.get("actor") or "") + " " + (e.get("object") or "") if field is None else (e.get(field) or "")
    return {w.lower()[:6] for w in re.findall(r"\b[A-Z][A-Za-zÀ-ÿ'\-]{2,}", s)
            if w.lower() not in GENERIC and w.lower() not in NAME_GENERIC}


def clean_title(title):
    """Drop the outlet name that feeds append to titles ("... - Agenda Digitale", "... | TechCrunch")."""
    return re.sub(r"\s+[-|–]\s+[^-|–]{2,40}$", "", title or "")


def phrases(note, title):
    s = " ".join([clean_title(title), note.get("main_referent") or "", (note.get("event") or {}).get("object") or ""])
    w = [x.lower()[:6] for x in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'\-]+", s) if x.lower() not in STOP]
    return {a + " " + b for a, b in zip(w, w[1:])} - PHRASE_GENERIC


def same_event(a, b, title_a="", title_b=""):
    """Return the evidence ('event', 'names', 'phrase: ...') that a and b are about the same event, or None."""
    ea, eb = a.get("event") or {}, b.get("event") or {}
    try:
        if abs((dt.date.fromisoformat(ea["date"]) - dt.date.fromisoformat(eb["date"])).days) > 10:
            return None
    except Exception:
        pass
    oa, ob = toks(ea.get("object")), toks(eb.get("object"))
    aa, ab = toks(ea.get("actor"), generic=False), toks(eb.get("actor"), generic=False)
    if oa & ob and (aa & ab or len(oa & ob) >= 2):
        return "event"
    # a proper name shared by the actors, or two shared by the objects ("Reddit v. SerpAPI"), not one capitalised word
    common = (names(ea, "actor") & names(eb, "actor")) | ((names(ea, "object") & names(eb, "object"))
                                                          if len(names(ea, "object") & names(eb, "object")) >= 2 else set())
    if common:
        return "names: " + ", ".join(sorted(common))
    common = phrases(a, title_a) & phrases(b, title_b)
    if common:
        return "phrase: " + ", ".join(sorted(common))
    return None


def components(ids, link):
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if link(ids[x], ids[y]):
                parent[find(ids[y])] = find(ids[x])
    groups = {}
    for i in ids:
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def actor_match(ea, eb):
    """The two events have the same actor: same normalised string, or a shared specific (non-institutional) word."""
    a, b = (ea.get("actor") or "").strip().lower(), (eb.get("actor") or "").strip().lower()
    if not a or not b:
        return None
    if a == b:
        return a
    common = toks(ea.get("actor")) & toks(eb.get("actor")) - {w[:6] for w in NAME_GENERIC}
    return ", ".join(sorted(common)) or None


def card_link(a, b):
    """Evidence that two items report the same fact: dates compatible, same actor AND a shared object word."""
    ea, eb = a.get("event") or {}, b.get("event") or {}
    try:
        if abs((dt.date.fromisoformat(ea["date"]) - dt.date.fromisoformat(eb["date"])).days) > 10:
            return None
    except Exception:
        pass
    actor = actor_match(ea, eb)
    # the shared object word must not be the actor's own name ("Anthropic IPO" and "Anthropic" are not the same fact)
    obj = object_words(a, b)
    return f"actor: {actor}; object: {', '.join(sorted(obj))}" if actor and obj else None


def consolidate(m, keep, log):
    """Fuse the cards of a matrice that the code finds to be the same fact (card_link on any pair of their items),
    unless the model marked one of them distinct. Main card (not distinct) first, then by size."""
    cards = m["cards"]
    evidence = {}

    def link(x, y):
        if cards[x].get("distinct") or cards[y].get("distinct"):
            return False
        for a in cards[x]["items"]:
            for b in cards[y]["items"]:
                e = card_link(keep[a], keep[b])
                if e:
                    evidence[f"{x}~{y}"] = f"{a}~{b} {e}"
                    return True
        return False
    groups = components(list(range(len(cards))), link)
    if any(len(g) > 1 for g in groups):
        log.append({"matrice": m["id"], "cards_before": len(cards), "cards_after": len(groups), "evidence": evidence})
    new = []
    for g in groups:
        g.sort()
        c = {"items": [i for k in g for i in cards[k]["items"]], "distinct": cards[g[0]].get("distinct"),
             "why": cards[g[0]].get("why", "")}
        new.append(c)
    new.sort(key=lambda c: (bool(c.get("distinct")), -len(c["items"])))
    m["cards"] = new
    m["kept_distinct"] = [{"items": c["items"], "distinct": c["distinct"], "why": c["why"]} for c in new if c.get("distinct")]


def proposed_cards(comp, cards_in):
    """Cards of a confirmed component, as the model proposed them (no split by kind of piece any more)."""
    card_of = {i: k for k, c in enumerate(cards_in or []) for i in c.get("items") or []}
    parts = components(comp, lambda a, b: card_of.get(a) == card_of.get(b))
    out = []
    for part in parts:
        c = (cards_in or [{}])[card_of.get(part[0], 0)] if card_of.get(part[0]) is not None else {}
        d = c.get("distinct") if c.get("distinct") in ("fact", "adds") else None
        out.append({"items": part, "distinct": d, "why": c.get("why", "") if d else ""})
    return out


def strong(e):
    """Evidence accepted in the merge pass: event fields or proper names, not a shared common phrase like "data center"."""
    return e if e and not e.startswith("phrase") else None


def merge(matrici, used, keep, items, out, previous=None):
    """Second pass: the model proposes unions between single items and matrici; the code confirms with same_event,
    accepting only strong evidence, because this pass invites broader unions. Items whose proposal is rejected but that
    are strongly linked to each other (two outlets at least) form a matrice of their own."""
    p_merge, h_merge = prompt("merge")
    out["prompt_sha256"]["merge"] = h_merge
    singles = [i for i in keep if i not in used and keep[i].get("kind") != "rassegna"]
    payload = {"matrici": [{"id": m["id"], "referent": m["referent"],
                            "items": [{"source": items[i].get("publisher"), "title": items[i].get("title"),
                                       "event": keep[i].get("event")} for i in m["items"]]} for m in matrici],
               "singles": [{"id": i, "source": items[i].get("publisher"), "origin": items[i]["origin"],
                            "date": (items[i].get("published") or "")[:10], "title": clean_title(items[i].get("title")),
                            "event": keep[i].get("event"), "main_referent": keep[i].get("main_referent"),
                            "summary": keep[i].get("summary")} for i in singles]}
    if os.getenv("DAILY_REUSE_MERGE") and previous and previous.get("prompt", h_merge) == h_merge:
        prop = previous["proposed"]
        out["merge_reused"] = True
    else:
        try:
            raw, cost, _ = call(DEEPSEEK, p_merge, payload, max_tokens=4000)
            out["cost"]["merge"] = cost
            prop = parse_json(raw["choices"][0]["message"]["content"])
        except Exception as exc:
            out["errors"].append({"stage": "merge", "error": str(exc)[:200]})
            return
    log = out["merge"] = {"prompt": h_merge, "proposed": prop, "joined": [], "new": [], "rejected": []}
    by_id = {m["id"]: m for m in matrici}

    def ev(a, b):
        return strong(same_event(keep[a], keep[b], items[a].get("title"), items[b].get("title")))
    for j in prop.get("join") or []:
        m = by_id.get(j.get("matrice"))
        for i in j.get("items") or []:
            if not m or i not in keep or i in used:
                continue
            proof = next(((x, ev(i, x)) for x in m["items"] if ev(i, x)), None)
            if not proof:
                log["rejected"].append({"item": i, "to": j.get("matrice"), "why": j.get("why")})
                continue
            used.add(i)
            m["items"].append(i)
            m["cards"].append({"items": [i], "distinct": None, "why": ""})
            m["origins"] = sorted({items[x]["origin"] for x in m["items"]})
            m["date"] = max(m["date"], (items[i].get("published") or "")[:10])
            log["joined"].append({"item": i, "to": m["id"], "evidence": f"{proof[0]}: {proof[1]}", "why": j.get("why")})
    for nm in prop.get("new") or []:
        ids = [i for c in nm.get("cards") or [] for i in c.get("items") or [] if i in keep and i not in used]
        ids = list(dict.fromkeys(ids))
        evidence = {}

        def link(a, b):
            e = ev(a, b)
            if e:
                evidence[f"{a}~{b}"] = e
            return bool(e)
        for comp in components(ids, link):
            origins = {items[i]["origin"] for i in comp}
            if len(comp) < 2 or len(origins) < 2:
                log["rejected"] += [{"item": i, "to": nm.get("referent"), "why": nm.get("why")} for i in comp]
                continue
            used.update(comp)
            matrici.append({"id": f"M{len(matrici) + 1}", "referent": nm.get("referent"), "cards": proposed_cards(comp, nm.get("cards")),
                            "items": comp, "origins": sorted(origins), "from_merge": True,
                            "strong": any(items[i].get("tier", "approved") in v2.STRONG for i in comp),
                            "date": max((items[i].get("published") or "")[:10] for i in comp), "removed": []})
            log["new"].append({"referent": nm.get("referent"), "items": comp, "evidence": evidence, "why": nm.get("why")})
    pool = [r["item"] for r in log["rejected"] if r["item"] not in used]
    evidence = {}

    def link2(a, b):
        e = ev(a, b)
        if e:
            evidence[f"{a}~{b}"] = e
        return bool(e)
    for comp in components(list(dict.fromkeys(pool)), link2):
        origins = {items[i]["origin"] for i in comp}
        if len(comp) < 2 or len(origins) < 2:
            continue
        used.update(comp)
        first = min(comp, key=lambda i: items[i].get("published") or "")
        matrici.append({"id": f"M{len(matrici) + 1}", "referent": keep[first].get("main_referent"),
                        "cards": [{"items": [i], "distinct": None, "why": ""} for i in comp], "items": comp, "origins": sorted(origins), "from_merge": True,
                        "strong": any(items[i].get("tier", "approved") in v2.STRONG for i in comp),
                        "date": max((items[i].get("published") or "")[:10] for i in comp), "removed": []})
        log["new"].append({"referent": matrici[-1]["referent"], "items": comp, "from_rejected": True,
                           "evidence": {k: v for k, v in evidence.items() if k.split("~")[0] in comp}})
    log["rejected"] = [r for r in log["rejected"] if r["item"] not in used]
    fuse(matrici, keep, items, prop.get("fuse") or [], log)


def object_words(a, b):
    """Object words shared by two events, without the actors' own names."""
    ea, eb = a.get("event") or {}, b.get("event") or {}
    return toks(ea.get("object")) & toks(eb.get("object")) - toks(ea.get("actor"), generic=False) - toks(eb.get("actor"), generic=False)


def twin_pairs(m1, m2, keep, items, min_words=1):
    """Item pairs across two matrici with strong evidence of the same event and at least min_words shared object
    words that are not the actors' names (Microsoft's buyouts and Microsoft's quarterly results are not twins)."""
    pairs = []
    for a in m1["items"]:
        for b in m2["items"]:
            e = strong(same_event(keep[a], keep[b], items[a].get("title"), items[b].get("title")))
            obj = object_words(keep[a], keep[b])
            if e and len(obj) >= min_words:
                pairs.append(f"{a}~{b} object: {', '.join(sorted(obj))}")
    return pairs


def fuse(matrici, keep, items, proposals, log):
    """Twin matrici: fused when the model proposes it and at least one item pair is confirmed, or, without a proposal,
    when at least half of the items of each matrice have a pair confirmed with two object words (two pairs at least). The larger matrice absorbs the other; cards are kept as they
    are and checked again by consolidate()."""
    log["fused"], log["fuse_rejected"] = [], []
    proposed = set()
    for f in proposals:
        ids = [x for x in f.get("matrici") or [] if isinstance(x, str)]
        for x in ids:
            for y in ids:
                if x < y:
                    proposed.add((x, y))
    changed = True
    while changed:
        changed = False
        for m1 in matrici:
            for m2 in matrici:
                if m1 is m2 or m1["id"] > m2["id"]:
                    continue
                asked = (m1["id"], m2["id"]) in proposed or (m2["id"], m1["id"]) in proposed
                pairs = twin_pairs(m1, m2, keep, items, 1 if asked else 2)
                total = len(m1["items"]) * len(m2["items"])
                # unasked: at least half of the items of EACH matrice have a confirmed pair
                cover = min(len({p.split("~")[0] for p in pairs}) / len(m1["items"]),
                            len({p.split("~")[1].split()[0] for p in pairs}) / len(m2["items"]))
                if not (asked and pairs or len(pairs) >= 2 and cover >= 0.5):
                    if asked:
                        log["fuse_rejected"].append({"matrici": [m1["id"], m2["id"]]})
                        proposed.discard((m1["id"], m2["id"]))
                        proposed.discard((m2["id"], m1["id"]))
                    continue
                big, small = (m1, m2) if len(m1["items"]) >= len(m2["items"]) else (m2, m1)
                big["items"] += small["items"]
                # the twin's main cards report another fact (the regulator's investigation) unless the code finds them
                # to be the same fact as a card of the absorbing matrice
                for c in small["cards"]:
                    if not c.get("distinct") and not any(card_link(keep[a], keep[b]) for a in c["items"]
                                                         for b in big["items"]):
                        c["distinct"], c["why"] = "fact", f"twin matrice: {small['referent']}"
                big["cards"] += small["cards"]
                big["origins"] = sorted(set(big["origins"]) | set(small["origins"]))
                big["date"] = max(big["date"], small["date"])
                big["strong"] = big["strong"] or small["strong"]
                big.setdefault("fused_from", []).append({"id": small["id"], "referent": small["referent"]})
                log["fused"].append({"into": big["id"], "from": small["id"], "proposed": asked,
                                     "pairs": f"{len(pairs)}/{total}", "cover": round(cover, 2), "evidence": pairs[:5]})
                matrici.remove(small)
                changed = True
                break
            if changed:
                break


def future_dates(keep, items, out):
    """An event date after the item's publication is an announced date (a delay "to 20 November"), not the date of
    the event reported: it is kept as announced_date and left out of the date checks."""
    moved = []
    for iid, n in keep.items():
        e, pub = n.get("event") or {}, (items[iid].get("published") or "")[:10]
        if e.get("date") and pub and e["date"] > pub:
            n["event"] = {**e, "date": None, "announced_date": e["date"]}
            moved.append(iid)
    out["announced_dates"] = moved


def build(keep, items, out, old, p_group, h_group, p_write, admit=None):
    """Group, confirm, merge, write and summarise the matrici of the kept notes (mutates out).

    admit(matrice) -> bool, if given, is applied after the merge pass and before the titles: a matrice it refuses is
    recorded in out["topic_filter"], its items go back to the single cards, and no title is paid for it."""
    future_dates(keep, items, out)
    listing = [{"id": iid, "source": items[iid].get("publisher"), "origin": items[iid]["origin"],
                "date": (items[iid].get("published") or "")[:10], "title": items[iid].get("title") or "", "kind": n.get("kind"),
                "event": n.get("event"), "main_referent": n.get("main_referent"), "summary": n.get("summary")} for iid, n in keep.items()]
    if os.getenv("DAILY_REUSE_GROUP") and old.get("proposed") and old.get("prompt_sha256", {}).get("group") == h_group:
        proposed = old["proposed"]
        out["group_reused"] = True
    else:
        raw, cost, _ = call(DEEPSEEK, p_group, {"items": listing}, max_tokens=10000)
        out["cost"]["group"] = cost
        proposed = parse_json(raw["choices"][0]["message"]["content"]).get("matrici", [])
    out["proposed"] = proposed

    used, matrici = set(), []
    for m in proposed:
        ids = [i for c in m.get("cards") or [] for i in (c.get("items") or [])]
        ids = [i for i in dict.fromkeys(ids) if i in keep and i not in used and keep[i].get("kind") != "rassegna"]
        evidence = {}

        def link(a, b):
            e = same_event(keep[a], keep[b], items[a].get("title"), items[b].get("title"))
            if e:
                evidence[f"{a}~{b}"] = e
            return bool(e)
        comps = components(ids, link)
        rejected = [i for c in comps if len(c) < 2 for i in c]
        for comp in comps:
            origins = {items[i]["origin"] for i in comp}
            if len(comp) < 2 or len(origins) < 2:
                continue
            used.update(comp)
            matrici.append({"id": f"M{len(matrici) + 1}", "referent": m.get("referent"), "cards": proposed_cards(comp, m.get("cards")),
                            "items": comp, "origins": sorted(origins),
                            "strong": any(items[i].get("tier", "approved") in v2.STRONG for i in comp),
                            "date": max((items[i].get("published") or "")[:10] for i in comp), "removed": []})
        out["log"].append({"referent": m.get("referent"), "proposed": len(ids), "confirmed": [len(c) for c in comps if len(c) > 1],
                           "evidence": evidence,
                           "rejected": [{"id": i, "event": keep[i].get("event")} for i in rejected]})
    used_by_group = len(used)
    if os.getenv("DAILY_MERGE", "1") == "1":
        merge(matrici, used, keep, items, out, old.get("merge"))
    out["cards_check"] = []
    for m in matrici:
        consolidate(m, keep, out["cards_check"])
    matrici.sort(key=lambda m: (not m["strong"], -len(m["origins"]), -len(m["items"]), m["date"]))
    out["matrici_before_admit"] = len(matrici)
    if admit:
        refused = [m for m in matrici if not admit(m)]
        out["topic_filter"] = [{"referent": m["referent"], "items": len(m["items"]), "origins": len(m["origins"])} for m in refused]
        for m in refused:
            used.difference_update(m["items"])
        matrici = [m for m in matrici if admit(m)]
    for m in matrici:
        payload = {"referent": m["referent"], "cards": [{"index": k, "items": [{"source": items[i].get("publisher"), "kind": keep[i].get("kind"),
                                                                                 "summary": keep[i].get("summary")} for i in c["items"]],
                                         **({"distinct_fact": c["why"]} if c.get("distinct") and c.get("why") else {})}
                                                        for k, c in enumerate(m["cards"])]}
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
                c["title"], c["text"] = x.get("title", ""), (x.get("text", "") if len(c["items"]) > 1 else "")
        hay = norm(" ".join(keep[i].get("summary", "") for i in m["items"]))
        own = m["title"] + " " + m["essence"] + " " + " ".join(c.get("text", "") for c in m["cards"])
        m["unsupported_numbers"] = sorted({x for x in re.findall(r"\d[\d.,]*\d|\d", own)
                                           if x.replace(".", "").replace(",", "") not in hay.replace(".", "").replace(",", "")})
    # every item in or partly in the perimeter is shown: alone if no matrice confirmed it, central items first
    singles = [iid for iid, n in keep.items() if iid not in used and n.get("kind") != "rassegna"]
    singles.sort(key=lambda i: (keep[i].get("in_perimeter") != "yes", items[i].get("tier", "approved") not in v2.STRONG,
                                items[i].get("published") or ""))
    out.update({"matrici": matrici, "singles": singles})
    proposed_items = sum(o["proposed"] for o in out["log"] if o["proposed"] > 1)
    out["summary"] = {"items_in": len(listing), "proposed_matrici": len(proposed), "proposed_items": proposed_items,
                      "matrici": len(matrici), "items_in_matrici": len(used), "removed_by_check": proposed_items - used_by_group,
                      "multi_source_cards": sum(len(c["items"]) > 1 for m in matrici for c in m["cards"]),
                      "multi_outlet": sum(len(m["origins"]) >= 2 for m in matrici), "singles": len(singles), "singles_partial": sum(keep[i].get("in_perimeter") != "yes" for i in singles),
                      "unsupported_numbers": sum(bool(m["unsupported_numbers"]) for m in matrici),
                      "false_friend_numbers": sorted(i for i in keep if re.search(r"\b(bilion|trilion)[ei]\b", keep[i].get("summary", ""), re.I)),
                      "merge_joined": len((out.get("merge") or {}).get("joined", [])),
                      "merge_new_matrici": len((out.get("merge") or {}).get("new", [])),
                      "merge_rejected": len((out.get("merge") or {}).get("rejected", [])),
                      "merge_fused": len((out.get("merge") or {}).get("fused", [])),
                      "cards_fused_by_code": sum(c["cards_before"] - c["cards_after"] for c in out["cards_check"]),
                      "cards_kept_distinct": sum(len(m.get("kept_distinct", [])) for m in matrici)}


def main(selection_path, out_dir):
    sel = json.loads(Path(selection_path).read_text())
    items = {i["item_id"]: i for i in sel["items"]}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (p_note, h_note), (p_group, h_group), (p_write, h_write) = prompt("nota"), prompt("group"), prompt("write")
    notes_path, path = out_dir / "notes-v4.json", out_dir / "daily-v4.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    notes = {"prompt_sha256": h_note, "notes": {}, "cost": 0.0, "errors": []}
    if notes_path.exists() and json.loads(notes_path.read_text()).get("prompt_sha256") == h_note:
        notes = json.loads(notes_path.read_text())
    out = {"version": "daily-v4", "window": sel.get("window"), "code_commit": os.getenv("UBIK_COMMIT"),
           "prompt_sha256": {"nota": h_note, "group": h_group, "write": h_write}, "preflight": [], "errors": [],
           "cost": {"group": 0.0, "merge": 0.0, "write": 0.0}, "log": []}

    def save():
        notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + "\n")
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    todo = [i for i in items if i not in notes["notes"]]
    try:
        preflight("daily matrici v4", len(todo) * 0.001 + 0.03, 0.40, out["preflight"])
    except OverBudget as exc:
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
    save()
    keep = {iid: n for iid, n in notes["notes"].items() if iid in items and n.get("in_perimeter") in ("yes", "partial")
            and n.get("kind") not in ("rilancio",)}
    build(keep, items, out, old, p_group, h_group, p_write)
    out["cost"]["notes"] = notes["cost"]
    out["total_cost_usd"] = sum(out["cost"].values())
    out["status"] = "completed"
    save()
    html_page = v3.render(out, keep, items).replace("PROTOTIPO V3", "PROTOTIPO V4").replace(
        "Il controllo ha tolto", "Il codice ha escluso").replace("articoli non pertinenti", "articoli che non poteva confermare").replace("Prototipo v3", "Prototipo v4")
    (out_dir / "daily-v4.html").write_text(html_page)
    print(json.dumps({"summary": out["summary"], "cost": out["cost"]}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
