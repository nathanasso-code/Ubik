"""Recover the two-source monarch evidence from archived joint-results.json."""
import json
from pathlib import Path
src=json.loads(Path("data/monarch-v5/joint-results.json").read_text())
matrices=src["arms"]["A_qwen"]["contexts"][0]["matrices"]
by_source={"S473":{},"S474":{}}
for matrix in matrices:
    for card in matrix["cards"]:
        for s in card["sources"]:
            sid=s.get("source_id")
            if sid not in by_source:continue
            key=s["news_id"]
            if key not in by_source[sid]:
                by_source[sid][key]={"key":key,"title":s.get("original_title",""),
                  "summary":s.get("summary",""),
                  "evidence_excerpts":[p["text"] for p in s.get("passages",[])]}
assert set(by_source["S473"])=={"n0","n1","n2"},by_source
assert set(by_source["S474"])=={"n3","n4","n5","n6"},by_source
out={"input_kind":"archived_excerpts_not_full_article","source_artifact_id":12572749808,
 "sources":[{"source_id":sid,"article_published_at":None,"source_type":"unknown",
 "provenance":{"publisher_id":sid,"publisher_name":None,"editorial_group_id":None,
 "content_origin":{"type":"unknown","name":None},"reliability_level":"unrated"},
 "news":list(news.values())} for sid,news in by_source.items()]}
Path("data/monarch-v5/input.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
print("Recovered",[(s["source_id"],len(s["news"])) for s in out["sources"]])
