"""Free Ukraine v4-source near-duplicate screen. Generated titles/summaries are NOT provenance proof."""
import json,re,sys
from collections import Counter
from itertools import combinations
from pathlib import Path
def tokens(s):return re.findall(r"\w+",s.lower(),flags=re.UNICODE)
def shingles(s,n=5):
 t=tokens(s);return {" ".join(t[i:i+n]) for i in range(max(0,len(t)-n+1))}
def main():
 src=json.loads(Path(sys.argv[1]).read_text())
 news=[{"source_id":s["source_id"],**n} for s in src["sources"] for n in s["news"]]
 result={"model":src.get("model"),"news_count":len(news),"source_count":len(src["sources"]),
 "basis":"archived_v4_generated_titles_and_summaries_only",
 "original_text_provenance_verified":False,"pairs":[]}
 for a,b in combinations(news,2):
  if a["source_id"]==b["source_id"]:continue
  ta,tb=a.get("title",""),b.get("title","")
  shared=sorted(shingles(ta+" "+a.get("summary","")) & shingles(tb+" "+b.get("summary","")))
  if ta.strip().lower()==tb.strip().lower() or shared:
   result["pairs"].append({"left":a["key"],"right":b["key"],
    "left_source":a["source_id"],"right_source":b["source_id"],
    "same_title":ta.strip().lower()==tb.strip().lower(),
    "shared_fivegrams":len(shared),"examples":shared[:12],
    "shared_origin":"unknown_requires_original_excerpts"})
 result["pairs"].sort(key=lambda x:(-int(x["same_title"]),-x["shared_fivegrams"],x["left"],x["right"]))
 out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({"news":len(news),"pairs_with_overlap":len(result["pairs"]),
 "top_pairs":result["pairs"][:6]},ensure_ascii=False))
if __name__=="__main__":main()
