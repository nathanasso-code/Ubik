"""Cards: one per matrice by default; the code fuses splits it can confirm and keeps the ones the model justified."""
from ingestion import ubik_daily4 as d4


def note(actor, obj, date=None):
    return {"event": {"actor": actor, "action": "other", "object": obj, "date": date}, "kind": "cronaca"}


KEEP = {
    "ms1": note("Microsoft", "Microsoft voluntary exit offer for 60,000 employees", "2026-10-26"),
    "ms2": note("Microsoft", "Voluntary severance offer to 60,000 employees", "2026-10-26"),
    "ms3": note("Microsoft", "Microsoft fiscal year 2027 first quarter results", "2026-10-29"),
    "kid1": note("European Commission", "EU Kids Act"),
    "kid2": note("European Commission", "EU Kids Act"),
    "oslo": note("Oslo District Court", "Meta AI scraping terms", "2026-10-28"),
    "meta1": note("Meta", "Meta commercial terms for professional users", "2026-10-26"),
    "meta2": note("Meta", "Meta's proposed ads and business terms update", "2026-10-28"),
    "cma1": note("Competition and Markets Authority", "Meta's new commercial terms on use of content for AI", "2026-10-28"),
    "cma2": note("Competition and Markets Authority", "Meta new commercial terms for AI products", "2026-10-30"),
}


def matrice(mid, cards):
    items = [i for c in cards for i in c["items"]]
    return {"id": mid, "referent": mid, "cards": cards, "items": items, "origins": items, "date": "2026-10-30", "strong": False}


def test_split_without_reason_is_fused():
    m = matrice("M1", [{"items": ["ms1"], "distinct": None}, {"items": ["ms2"], "distinct": None}])
    log = []
    d4.consolidate(m, KEEP, log)
    assert [c["items"] for c in m["cards"]] == [["ms1", "ms2"]] and log[0]["cards_after"] == 1


def test_split_marked_distinct_is_kept():
    m = matrice("M2", [{"items": ["kid1"], "distinct": None},
                       {"items": ["kid2"], "distinct": "fact", "why": "request to Austria"}])
    d4.consolidate(m, KEEP, [])
    assert len(m["cards"]) == 2 and m["kept_distinct"][0]["why"] == "request to Austria"


def test_other_actor_stays_apart_and_actor_name_is_not_an_object():
    m = matrice("M3", [{"items": ["meta1"], "distinct": None}, {"items": ["oslo"], "distinct": "fact", "why": "ruling"}])
    assert d4.consolidate(m, KEEP, []) == [] and len(m["cards"]) == 2
    assert d4.card_link(KEEP["ms1"], KEEP["ms3"]) is None


def test_untied_split_and_other_event_go_back_to_singles():
    m = matrice("M5", [{"items": ["ms1", "ms2"], "distinct": None}, {"items": ["ms3"], "distinct": "fact", "why": "results"},
                       {"items": ["oslo"], "distinct": None}])
    gone = d4.consolidate(m, KEEP, [])
    assert sorted(gone) == ["ms3", "oslo"] and [c["items"] for c in m["cards"]] == [["ms1", "ms2"]]
    assert {r["why"] for r in m["removed_by_card_check"]} == {"other event, same actor", "not tied to the main card"}


def test_adds_becomes_a_line_of_the_main_card():
    m = matrice("M6", [{"items": ["kid1"], "distinct": None}, {"items": ["kid2"], "distinct": "adds", "why": "critique"}])
    d4.consolidate(m, KEEP, [])
    assert [c["items"] for c in m["cards"]] == [["kid1", "kid2"]] and m["cards"][0]["adds"][0]["why"] == "critique"


def test_twin_matrici():
    ms = [matrice("M1", [{"items": ["ms1", "ms2"], "distinct": None}]), matrice("M2", [{"items": ["ms3"], "distinct": None}]),
          matrice("M3", [{"items": ["meta1", "meta2"], "distinct": None}]), matrice("M4", [{"items": ["cma1", "cma2"], "distinct": None}])]
    items = {i: {"title": ""} for i in KEEP}
    log = {}
    d4.fuse(ms, KEEP, items, [{"matrici": ["M1", "M2"]}, {"matrici": ["M3", "M4"]}], log)
    assert [m["id"] for m in ms] == ["M1", "M2", "M3"]
    assert log["fused"][0]["into"] == "M3" and log["fuse_rejected"] == [{"matrici": ["M1", "M2"]}]
    assert [c.get("distinct") for c in ms[2]["cards"]] == [None, "fact"]


def test_announced_date_is_not_event_date():
    keep = {"next": note("Meta", "Meta updated commercial terms", "2026-11-20"), "verge": note("Meta", "Meta business terms update", "2026-10-28")}
    items = {"next": {"published": "2026-10-26T10:00:00Z"}, "verge": {"published": "2026-10-28T10:00:00Z"}}
    out = {}
    d4.future_dates(keep, items, out)
    assert out["announced_dates"] == ["next"] and keep["next"]["event"]["announced_date"] == "2026-11-20"
    assert d4.card_link(keep["next"], keep["verge"])
