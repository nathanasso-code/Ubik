"""Frozen monarch v5: E5-small role-filtered candidate retrieval and cautious grouping."""
from collections import defaultdict

def role(event):
    return "container" if event.get("role")=="referenced" and (
        event.get("container_name") or "project" in str(event.get("object","")).lower()
        or "study" in str(event.get("object","")).lower()) else "fact"

def candidates(sources,k=5):
    events=[(s["source_id"]+":"+e["id"],s["source_id"],e) for s in sources for e in s["answer"]["events"]]
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer("intfloat/multilingual-e5-small",device="cpu")
    texts=["passage: "+str(e.get("action") or "")+" "+str(e.get("object") or "") for _,_,e in events]
    vec=model.encode(texts,normalize_embeddings=True,convert_to_numpy=True,show_progress_bar=False)
    sims=vec@vec.T
    selected={}
    for i,(eid,sid,event) in enumerate(events):
        options=[j for j,(_,other_sid,other) in enumerate(events)
                 if other_sid!=sid and role(event)==role(other)]
        options.sort(key=lambda j:(-float(sims[i,j]),events[j][0]))
        for j in options[:k]:
            a,b=sorted((eid,events[j][0]))
            selected[(a,b)]=max(selected.get((a,b),-1),float(sims[i,j]))
    return sorted(selected,key=lambda p:(-selected[p],p)),selected,{eid:e for eid,_,e in events}

def cautious_groups(events,judgments,scores):
    """Permanent distinct veto; no duplicate source; competing merges abstain."""
    ids=sorted(events);groups=[frozenset([i]) for i in ids]
    positive=set();negative=set();part_of=[]
    for j in judgments:
        pair=tuple(sorted((j["left"],j["right"])))
        verdict=j["result"]["decision"]
        if verdict=="equivalent":positive.add(pair)
        elif verdict=="distinct":negative.add(pair)
        elif verdict=="part_of":part_of.append(j)
    conflicts=[]
    for pair in sorted(positive,key=lambda p:(-scores.get(p,0),p)):
        ga=next(g for g in groups if pair[0] in g)
        gb=next(g for g in groups if pair[1] in g)
        if ga==gb:continue
        sources=[e.split(":")[0] for e in ga|gb]
        if len(sources)!=len(set(sources)):
            conflicts.append({"pair":pair,"reason":"duplicate_source"});continue
        if any(tuple(sorted((a,b))) in negative for a in ga for b in gb):
            conflicts.append({"pair":pair,"reason":"permanent_distinct_veto"});continue
        cross=sum(tuple(sorted((a,b))) in positive for a in ga for b in gb)
        if (len(ga)==len(gb)==1) or cross>=2:
            groups.remove(ga);groups.remove(gb);groups.append(ga|gb)
        else:conflicts.append({"pair":pair,"reason":"insufficient_group_confirmations"})
    return {"groups":[sorted(g) for g in sorted(groups,key=lambda g:sorted(g))],
            "conflicts":conflicts,"part_of":part_of}
