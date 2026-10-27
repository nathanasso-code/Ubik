"""Deterministic, read-only bridge-edge diagnostic for part_of incident components."""
def bridge_part_of_edges(cards,relations):
    nodes={c["id"] for c in cards}
    edges=[(i,r) for i,r in enumerate(relations) if r["type"]=="part_of"]
    graph={n:[] for n in nodes}
    for i,r in edges:
        a,b=r["source"],r["target"]
        if a not in nodes or b not in nodes:raise ValueError("Unknown card")
        graph[a].append((b,i));graph[b].append((a,i))
    def component(start,excluded=None):
        found=set();stack=[start]
        while stack:
            n=stack.pop()
            if n in found:continue
            found.add(n)
            stack.extend(v for v,i in graph[n] if i!=excluded and v not in found)
        return found
    result=[]
    for i,r in edges:
        a,b=r["source"],r["target"]
        whole=component(a)
        left=component(a,i)
        if b in left:continue
        right=component(b,i)
        if len(left)<2 or len(right)<2:continue
        result.append({"relation_index":i,"edge":r,"component_cards":sorted(whole),
                       "side_a_cards":sorted(left),"side_b_cards":sorted(right),
                       "diagnostic_only":True})
    return result
