"""Monarch schema-v5 extraction-only smoke test. No pair judge calls."""
import json,os
from pathlib import Path
from ingestion.ubik_monarch_v5_pilot import ask,ROOT
from ingestion.ubik_v5_extraction_validator import validate_extraction
PROMPT="""Extract ONE source independently. Return valid JSON with events[] and assignments[].
Every event MUST have id, event_nature (EXACTLY container|fact),
text_role (EXACTLY narrated|referenced), actor, action, object, actuality,
event_time, evidence, container_name, context_signal, and event_part_of[].
Each event_part_of item MUST be {event_id: ID OF ANOTHER EVENT IN THIS SOURCE,
evidence: NONEMPTY SOURCE EVIDENCE}. These are directed event-to-event relations,
including secondary facts within a news item. They are NOT inferred from mere
mentions or thematic proximity. Allow multi-level chains: technology part_of
project, detailed test part_of technology, when supported by evidence.
The tracking project must be an explicit container event, without inventing
its formal name, institution or journal. Population decline and regulatory
listing background are not automatically part of the tracking project.
text_role means whether an event is narrated as a main account or referenced
within the text; it is INDEPENDENT from event_nature.
assignments[]: one per news item, {news_key,primary_event_id,
part_of:[event_id],reacts_to:[{event_id,position}],mentions:[event_id],
context_only}. Position MUST be support|criticism|neutral|mixed|unclear.
Do not substitute mentions for part_of. No fabricated evidence.
Do not assume another source exists. Return JSON only."""
def main():
    inp=json.loads((ROOT/"input.json").read_text())
    out={"stage":"extraction_only_schema_v5","sources":[],"usage":[],"errors":[]}
    for source in inp["sources"]:
        try:
            ans,usage=ask(PROMPT,source)
            validate_extraction(ans,source)
            out["sources"].append({"source_id":source["source_id"],"answer":ans})
            out["usage"].append({"source_id":source["source_id"],"usage":usage})
        except Exception as e:out["errors"].append({"source_id":source["source_id"],"error":str(e)[:400]})
        (ROOT/"schema-extraction-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({"sources":len(out["sources"]),"errors":out["errors"],
                      "events":[len(s["answer"]["events"]) for s in out["sources"]]}))
    if out["errors"]:raise RuntimeError("Extraction schema validation failed")
if __name__=="__main__":main()
