"""Review-only relationship proposals for real-body corpus cards.

Never equate lexical or semantic similarity with same-event identity.
Propose separate contextual relations for adjacent rounds and election stages.
"""
import re

_ROUND = re.compile(r"\b(?:round|game|match)\s*(\d+)\b", re.I)
_FINAL = re.compile(r"\b(?:mayoral election|general election|presidential election)\b", re.I)
_PRIMARY = re.compile(r"\b(?:primary|primaries)\b", re.I)
_RESULTS = re.compile(r"\b(?:win|wins|won|lose|loses|lost|victory|defeat|concedes|conceded)\b",re.I)

def event_guard(title_a, title_b):
    """Return a cautious, explainable candidate relation, never verification."""
    a, b = title_a or "", title_b or ""
    r1, r2 = _ROUND.search(a), _ROUND.search(b)
    if r1 and r2 and r1.group(1) != r2.group(1):
        return {"same_event_candidate": False, "relation_hypothesis":"related_distinct_events",
                "reason":"Different explicitly numbered sporting rounds",
                "evidence":{"left_round":int(r1.group(1)),"right_round":int(r2.group(1))},
                "verified":False}
    if (_PRIMARY.search(a) and _FINAL.search(b)) or (_PRIMARY.search(b) and _FINAL.search(a)):
        return {"same_event_candidate":False,"relation_hypothesis":"related_distinct_events",
                "reason":"Primary and general elections are different voting events",
                "verified":False}
    return {"same_event_candidate":None,"relation_hypothesis":"insufficient_evidence",
            "reason":"Article bodies, named entities, event time and scope require review",
            "verified":False}

def annotate_cards(cards):
    """Preserve sources/cards while making potential false merges visible."""
    result=[]
    for card in cards:
        copy=dict(card)
        titles=copy.get("source_titles") or [copy.get("title","")]
        guards=[event_guard(titles[i],titles[j]) for i in range(len(titles)) for j in range(i+1,len(titles))]
        copy["event_pair_review"]=guards
        copy["same_event_candidate_blocked"]=any(g["same_event_candidate"] is False for g in guards)
        copy["source_independence_verified"]=False
        result.append(copy)
    return result
