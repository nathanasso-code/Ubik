#!/usr/bin/env python3
"""Deterministic first-pass source genealogy inference for Ubik.

This module never declares sources independent from text similarity alone.
It emits explicit dependency candidates plus reasons and confidence so a
later verifier (rules, model, or human) can inspect the decision.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import re

AGENCIES = {"reuters","associated press","ap","afp","ansa","dpa","bloomberg"}
DEPENDENCY_PHRASES = [
    (re.compile(r"\b(?:according to|reported by|citing)\s+(reuters|associated press|ap|afp|ansa|dpa|bloomberg)\b", re.I), "explicit_agency_attribution"),
    (re.compile(r"\b(?:secondo|riporta|citando)\s+(reuters|associated press|ap|afp|ansa|dpa|bloomberg)\b", re.I), "explicit_agency_attribution"),
]

@dataclass
class DependencyCandidate:
    child: str
    parent: str
    relation: str
    confidence: str
    reason: str

def host(url: str) -> str:
    try: return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception: return ""

def normalized_name(source: dict) -> str:
    return str(source.get("publisher") or source.get("label") or "").strip().lower()

def infer(sources: list[dict]) -> list[dict]:
    out=[]
    by_name={normalized_name(s):s for s in sources if normalized_name(s)}
    for child in sources:
        cid=str(child.get("id") or child.get("url") or normalized_name(child))
        text=" ".join(str(child.get(k) or "") for k in ("title","text","excerpt","underlying_citation"))
        for rx,relation in DEPENDENCY_PHRASES:
            for match in rx.finditer(text):
                agency=match.group(1).lower()
                agency="associated press" if agency=="ap" else agency
                parent=by_name.get(agency)
                if parent:
                    pid=str(parent.get("id") or parent.get("url") or normalized_name(parent))
                    if pid!=cid:
                        out.append(asdict(DependencyCandidate(cid,pid,relation,"high","explicit attribution in source text")))
        upstream=child.get("upstream_url") or child.get("cites_url")
        if upstream:
            uh=host(str(upstream))
            for parent in sources:
                if parent is child: continue
                if uh and uh==host(str(parent.get("url") or "")):
                    pid=str(parent.get("id") or parent.get("url") or normalized_name(parent))
                    out.append(asdict(DependencyCandidate(cid,pid,"links_to_source","high","explicit upstream URL")))
    unique={(x["child"],x["parent"],x["relation"]):x for x in out}
    return list(unique.values())

def independence_state(sources: list[dict], dependencies: list[dict]) -> dict:
    nodes={str(s.get("id") or s.get("url") or normalized_name(s)) for s in sources}
    children={d["child"] for d in dependencies}
    roots=nodes-children
    return {
        "source_count":len(nodes),
        "dependency_count":len(dependencies),
        "root_count_min":len(roots),
        "independence":"not_established" if len(nodes)>1 and not dependencies else ("single_line" if len(nodes)<=1 else "partially_reconstructed"),
        "note":"Absence of a detected dependency is not evidence of independence."
    }
