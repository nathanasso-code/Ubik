"""Deterministic part_of validation: quarantine cycles, never silently invent hierarchy."""
def resolve_part_of(relations):
    accepted=[];rejected=[];parents={}
    def reaches(start,target):
        todo=[start];seen=set()
        while todo:
            n=todo.pop()
            if n==target:return True
            if n in seen:continue
            seen.add(n);todo.extend(parents.get(n,()))
        return False
    for r in sorted(relations,key=lambda r:(r["source"],r["target"],r.get("origin",""))):
        if r["type"]!="part_of":
            accepted.append(r);continue
        a,b=r["source"],r["target"]
        if a==b or reaches(b,a):
            rejected.append({"relation":r,"reason":"self_or_cycle","resolution":"quarantined_pending_evidence_review"})
            continue
        accepted.append(r);parents.setdefault(a,set()).add(b)
    return accepted,rejected
