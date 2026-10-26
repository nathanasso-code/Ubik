"""Monarch v5 independent extraction and conservative cross-source judgment."""
import json,os,sys,urllib.request
from pathlib import Path
from ingestion.ubik_json_response import parse_json_response
from ingestion.ubik_matrix_composer_v5 import compose_v5
from ingestion.ubik_shared_origin_v5 import probable_shared_origin

ROOT=Path("data/monarch-v5")
ROOT.mkdir(parents=True,exist_ok=True)
MODEL=os.getenv("UBIK_LLM_MODEL","deepseek/deepseek-v3.2")
KEY=os.environ["UBIK_LLM_API_KEY"]
EXTRACT="""Extract from ONE source, independently. JSON only. Output events array with
{id,role,actor,action,object,actuality,event_time,evidence,container_name,context_signal},
and assignments array with {news_key,primary_event_id,part_of:[event_id],
reacts_to:[{event_id,position}],mentions:[event_id],context_only}.
Represent a concrete shared study as an event even if only referenced. Distinguish
article date from event date. Background population statistics must not be
automatically part_of a study. Evidence must be grounded in provided excerpts.
Do not invent details. Do not assume any other source exists."""
JUDGE="""Compare two event descriptions from different sources. JSON only:
{decision:'equivalent'|'distinct'|'uncertain',reason,detail_conflicts:[]}.
Only equivalent if same identifiable real-world event or study. Report explicit
contradictory details with supporting evidence; absence of details is not conflict."""

def ask(prompt,payload):
    req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
      data=json.dumps({"model":MODEL,"messages":[{"role":"system","content":prompt},
      {"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
      "response_format":{"type":"json_object"},"max_tokens":4000}).encode(),
      headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=200) as response:
        obj=json.load(response)
    return parse_json_response(obj["choices"][0]["message"]["content"]),obj.get("usage",{})

def save(out):
    (ROOT/"result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))

def main():
    inp=json.loads((ROOT/"input.json").read_text())
    out={"model":MODEL,"input_kind":inp.get("input_kind"),"sources":[],
         "judgments":[],"errors":[],"usage":[]}
    out["shared_origin"]=probable_shared_origin(*inp["sources"])
    save(out)
    for source in inp["sources"]:
        try:
            ans,usage=ask(EXTRACT,source)
            assert isinstance(ans["events"],list) and isinstance(ans["assignments"],list)
            ids={e["id"] for e in ans["events"]}
            assert len(ids)==len(ans["events"])
            assert {a["news_key"] for a in ans["assignments"]}=={n["key"] for n in source["news"]}
            for a in ans["assignments"]:
                assert a.get("primary_event_id") is None or a["primary_event_id"] in ids
                assert all(e in ids for e in a.get("part_of",[]))
            out["sources"].append({"source_id":source["source_id"],"answer":ans})
            out["usage"].append({"stage":"extract","source_id":source["source_id"],"usage":usage})
        except Exception as e:
            out["errors"].append({"stage":"extract","source_id":source["source_id"],"error":str(e)[:300]})
        save(out)
    if len(out["sources"])!=2:raise RuntimeError("Two source extractions required")
    left,right=out["sources"]
    for a in left["answer"]["events"]:
        for b in right["answer"]["events"]:
            try:
                decision,usage=ask(JUDGE,{"left":a,"right":b})
                assert decision["decision"] in ("equivalent","distinct","uncertain")
                out["judgments"].append({"left":left["source_id"]+":"+a["id"],
                    "right":right["source_id"]+":"+b["id"],"result":decision})
                out["usage"].append({"stage":"judge","pair":[a["id"],b["id"]],"usage":usage})
            except Exception as e:
                out["errors"].append({"stage":"judge","pair":[a["id"],b["id"]],"error":str(e)[:300]})
            save(out)
    cards=[];lookup={};used=set()
    for j in out["judgments"]:
        if j["result"]["decision"]!="equivalent":continue
        x,y=j["left"],j["right"]
        if x in used or y in used:continue
        used.update([x,y]);cid="card:"+x
        cards.append({"id":cid,"source_ids":[left["source_id"],right["source_id"]]})
        lookup[x]=lookup[y]=cid
    for source in out["sources"]:
        for e in source["answer"]["events"]:
            q=source["source_id"]+":"+e["id"]
            if q not in lookup:
                lookup[q]="card:"+q
                cards.append({"id":lookup[q],"source_ids":[source["source_id"]]})
    relations=[]
    for source in out["sources"]:
        sid=source["source_id"]
        for a in source["answer"]["assignments"]:
            primary=a.get("primary_event_id")
            if not primary:continue
            for parent in a.get("part_of",[]):
                x=lookup[sid+":"+primary];y=lookup[sid+":"+parent]
                if x!=y:
                    rel={"type":"part_of","source":x,"target":y}
                    if rel not in relations:relations.append(rel)
            for reaction in a.get("reacts_to",[]):
                x=lookup[sid+":"+primary];y=lookup[sid+":"+reaction["event_id"]]
                if x!=y:
                    rel={"type":"reacts_to","source":x,"target":y,
                         "position":reaction.get("position","unclear")}
                    if rel not in relations:relations.append(rel)
    if out["shared_origin"]["probable_common_origin"]:
        for card in cards:
            if len(card["source_ids"])>1:
                card["independent_origin_ids"]=["probable-shared-origin:S473:S474"]
    out["composition"]=compose_v5(cards,relations)
    save(out)
    print(json.dumps({"sources":len(out["sources"]),"pairs":len(out["judgments"]),
       "incidents":len(out["composition"]["incidents"]),
       "matrices":len(out["composition"]["matrices"]),"errors":out["errors"],
       "usage":out["usage"]},ensure_ascii=False))
    if out["errors"]:sys.exit(1)

if __name__=="__main__":main()
