"""Recompose frozen Ukraine v5 judge artifact with no LLM calls."""
import json
from pathlib import Path
from ingestion.ubik_matrix_composer_v5 import compose_connected_v5
from ingestion.ubik_part_of_bridge_diagnostic import bridge_part_of_edges
root=Path("data/ukraine-v5")
data=json.loads((root/"v5-judge.json").read_text())
if len(data["judgments"])!=data["candidate_pairs"] or data["errors"]:
 raise RuntimeError("Incomplete frozen judgment")
cards=data["composition"]["cards"]
relations=data["relations"]
before=data["composition"]
after=compose_connected_v5(cards,relations,conflicts=data.get("quarantined_relations",[]))
report={"stage":"deterministic-recomposition","model_calls":0,
 "frozen_judgments":len(data["judgments"]),
 "original":{"incidents":len(before["incidents"]),"matrices":len(before["matrices"])},
 "corrected":{"incidents":len(after["incidents"]),"matrices":len(after["matrices"]),
              "topic_cards":len(after["topic_cards"])},
 "bridge_diagnostic":bridge_part_of_edges(cards,relations),
 "composition":after,"cost_audit_original":data.get("cost_audit"),
 "unmodified_judgment_hash":__import__("hashlib").sha256(json.dumps(data["judgments"],sort_keys=True).encode()).hexdigest()}
(root/"v5-recomposed.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ("composition","bridge_diagnostic")},ensure_ascii=False))
