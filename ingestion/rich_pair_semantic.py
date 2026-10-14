"""Compare E5 semantic signals on the same metadata and transient rich-news pairs.

No article bodies or excerpts are retained. No inference of event identity.
"""
import argparse,json
from pathlib import Path
from ingestion.live_rich_pair_experiment import chunks,analyze as lexical_analyze
from ingestion.semantic_topic_router import MODEL

def score_pairs(snapshot,hybrid,embed,limit=24,fetch=None):
    # Fetch happens in lexical_analyze; semantic comparison requires access to the
    # same in-memory texts, so we intentionally do not claim semantic scores here.
    # This gate prevents fabricated embedding comparisons from metadata-only output.
    raise NotImplementedError("Semantic scoring requires an in-memory rich-text fetch callback")

def semantic_scores(text_a,text_b,meta_a,meta_b,embed):
    aa=chunks(text_a);bb=chunks(text_b)
    if not aa or not bb:return None
    inputs=["passage: "+meta_a,"passage: "+meta_b]+["passage: "+s for s in aa+bb]
    vectors=embed(inputs)
    def cos(a,b):return sum(x*y for x,y in zip(a,b))
    n=len(aa);body=[cos(vectors[2+i],vectors[2+n+j]) for i in range(n) for j in range(len(bb))]
    body.sort(reverse=True)
    return {"metadata_e5":round(cos(vectors[0],vectors[1]),4),
      "max_chunk_e5":round(body[0],4),"mean_top_3_chunk_e5":round(sum(body[:3])/min(3,len(body)),4),
      "chunks_a":len(aa),"chunks_b":len(bb)}
