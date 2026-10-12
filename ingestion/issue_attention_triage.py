"""Conservative issue-attention triage with provenance, not truth or virality score.

Priority gates: independently reviewed sharing convergence and reviewed
substantive debate. Raw counts are diagnostic, not verified independence.
"""
def triage(documents):
    results = []
    for doc in documents:
        mentions = doc.get("social_mentions") or []
        authors = {m.get("author") for m in mentions if isinstance(m, dict) and m.get("author")}
        # Independence must be asserted by review with provenance, not guessed
        # from distinct account handles.
        reviewed_groups = set()
        for mention in mentions:
            if not isinstance(mention, dict):
                continue
            group = mention.get("independent_origin_group")
            if mention.get("independence_reviewed") is True and isinstance(group, str) and group.strip():
                reviewed_groups.add(group.strip())
        debate = doc.get("debate_evidence") or []
        substantive = [d for d in debate if isinstance(d, dict)
                       and d.get("reviewed") is True
                       and d.get("substantive") is True
                       and d.get("url") and d.get("reason")]
        convergence = len(reviewed_groups) >= 2
        discussion = bool(substantive)
        if convergence and discussion:
            priority = "high_review"
        elif convergence or discussion:
            priority = "review"
        else:
            priority = "unassessed"
        results.append({"url": doc.get("url"), "priority": priority,
            "convergence_verified": convergence, "substantive_debate_verified": discussion,
            "distinct_handles_observed": len(authors),
            "independent_groups_reviewed": len(reviewed_groups),
            "substantive_contributions_reviewed": len(substantive),
            "needs_independence_review": bool(authors) and not convergence,
            "attention_is_not_validation": True,
            "evidence_urls": sorted({d["url"] for d in substantive})})
    results.sort(key=lambda x: ({"high_review": 0, "review": 1, "unassessed": 2}[x["priority"]],
                                -x["independent_groups_reviewed"],
                                -x["substantive_contributions_reviewed"], x["url"] or ""))
    return {"schema_version": 1, "items": results,
            "policy": "Reviewed independent convergence and documented substantive debate prioritize investigation; neither verifies a claim."}
