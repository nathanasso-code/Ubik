"""Run core-first DeepSeek and derive the embedding-only arm from identical embeddings."""
import argparse,json,sys
from pathlib import Path
from ingestion.frozen_qwen_passages_two_track import main as pipeline
def main():
 p=argparse.ArgumentParser();p.add_argument("grounded");p.add_argument("texts");p.add_argument("--output",required=True);a=p.parse_args()
 path=Path(a.output)
 sys.argv=[sys.argv[0],a.grounded,a.texts,"--output",str(path),"--review-mode","core-first"]
 pipeline()
 result=json.loads(path.read_text())
 result["experiment"]="paired_full_component_core_first_vs_embedding_only"
 result["arms"]={"embedding_only":"Unmodified embedding connected components","core_first":"Same embeddings, full-component nucleus-first DeepSeek"}
 for variant,record in result["variants"].items():
  for ctx in record["contexts"]:
   lookup={n["news_id"]:n for card in ctx["cards"] for n in card["source_summaries"]}
   embedding_cards=[]
   for index,component in enumerate(ctx.get("embedding_baseline",{}).get("components",[])):
    ids=component["ids"]
    sources=[lookup[n] for n in ids]
    embedding_cards.append({"id":f"embedding-{variant}-{ctx['context']}-{index}","news_ids":ids,"title":sources[0]["additional_title"],"summary":" ".join(s["summary"] for s in sources),"source_ids":list(dict.fromkeys(s["source_id"] for s in sources)),"source_summaries":sources,"synthesis_status":"unreviewed_embedding_group"})
   ctx["embedding_only_cards"]=embedding_cards
   assert sorted(x for c in embedding_cards for x in c["news_ids"])==sorted(x for c in ctx["cards"] for x in c["news_ids"])
  record["totals"]["embedding_only_cards"]=sum(len(c["embedding_only_cards"]) for c in record["contexts"])
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({k:v["totals"] for k,v in result["variants"].items()}))
if __name__=="__main__":main()
