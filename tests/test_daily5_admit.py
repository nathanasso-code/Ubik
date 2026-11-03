"""The sub-topic filter runs before the titles: a refused matrice pays no write call and its items become single cards."""
import json

from ingestion import ubik_daily4 as d4
from ingestion import ubik_daily5 as d5


def note(kind, topic_flag, iid):
    return {"item_id": iid, "kind": kind, "in_perimeter": topic_flag, "summary": f"Sintesi {iid} su Texas Stargate.",
            "main_referent": "Data center Stargate in Texas",
            "event": {"actor": "OpenAI Stargate", "action": "decision", "object": "Stargate Abilene data center", "date": "2026-11-03"}}


def setup(flags):
    keep = {f"i{k}": note("cronaca", f, f"i{k}") for k, f in enumerate(flags)}
    items = {iid: {"publisher": f"Testata {k}", "origin": f"o{k}", "published": "2026-11-03", "title": "Stargate Abilene data center",
                   "tier": "approved"} for k, iid in enumerate(keep)}
    return keep, items


def run(flags, monkeypatch):
    keep, items = setup(flags)
    calls = []

    def fake_call(model, prompt, payload, max_tokens=0):
        calls.append(prompt)
        if prompt == "GROUP":
            body = {"matrici": [{"referent": "Stargate", "cards": [{"items": list(keep)}]}]}
        else:
            body = {"title": "Titolo", "essence": "Essenza.", "cards": []}
        return {"choices": [{"message": {"content": json.dumps(body)}}]}, 0.001, {}

    monkeypatch.setattr(d4, "call", fake_call)
    monkeypatch.setenv("DAILY_MERGE", "0")
    out = {"cost": {"group": 0.0, "merge": 0.0, "write": 0.0}, "log": [], "errors": []}
    d4.build(keep, items, out, {}, "GROUP", "h", "WRITE", admit=d5.admits(keep))
    d5.topic_filter(out, keep, items)
    return out, calls


def test_refused_matrice_pays_no_title(monkeypatch):
    out, calls = run(["yes", "partial", "partial"], monkeypatch)
    assert calls == ["GROUP"]
    assert out["matrici"] == [] and len(out["topic_filter"]) == 1
    assert sorted(out["singles"]) == ["i0", "i1", "i2"]
    assert out["summary"]["matrici_before_topic_filter"] == 1 and out["summary"]["matrici"] == 0


def test_admitted_matrice_gets_title(monkeypatch):
    out, calls = run(["yes", "yes", "partial"], monkeypatch)
    assert calls == ["GROUP", "WRITE"]
    assert len(out["matrici"]) == 1 and out["matrici"][0]["title"] == "Titolo" and out["singles"] == []
