"""Bounded no-key research discovery: OpenAlex, Bluesky, Mastodon.

Public endpoints only. Results are *observed* evidence, not exhaustive counts.
"""
import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCES = [
("Gemini 4 Argon: our next era of frontier intelligence","https://deepmind.google/blog/gemini-4-argon-our-next-era-of-frontier-intelligence/"),
("Rogue Anthropic AI agent gave police fake tip in unsolved murder case","https://www.bbc.co.uk/news/articles/cqkg50j1yd5lo"),
("Financing the AI Buildout","https://www.nber.org/papers/w35865"),
("Asana cuts model costs 76x in browser tests with GPT-6.1 Sol","https://openai.com/index/asana-browser-agent/"),
("Caught in the Act: Probes Effectively Detect Sabotage and Catch Unverbalized Deception","https://arxiv.org/abs/2610.12445v1"),
("SpaceCast-Bench: Evaluating Predictive Spatial Reasoning in Vision-Language Models","https://arxiv.org/abs/2610.12402v1"),
("On the estimation and validity of AI time horizons---a statistical look at the METR plot","https://arxiv.org/abs/2610.12466v1"),
("AI existential risk probabilities are (still) too unreliable to inform policy","https://www.normaltech.ai/p/p-doom"),
("I expect rapid progress but not towards general superintelligence","https://www.interconnects.ai/p/i-expect-rapid-progress-but-not-towards"),
("From Reactive Containment to Proactive Assurance","https://arxiv.org/abs/2610.12463v1"),
("FastBench: Can Streaming VLMs Perceive High-Dynamic Real-World Streams?","https://arxiv.org/abs/2610.12427v1"),
("A big-tent or small-tent AI safety movement?","https://www.normaltech.ai/p/a-big-tent-or-small-tent-ai-safety"),
("Sophos cuts threat investigation time by 96% with OpenAI Daybreak","https://openai.com/index/sophos"),
("Why AlphaFold Didn't Solve Protein Folding","https://www.latent.space/p/biohub-deepmind"),
("Validity Without Ground Truth: What Stated-Preference Economics Offers the Evaluation of Language Models","https://arxiv.org/abs/2610.10506v1"),
("Focusing on Post-Training","https://sebastianraschka.com/blog/2026/focusing-on-llm-post-training.html"),
("Language Models for Text Classification: From Bag-of-Words to Jev","https://magazine.sebastianraschka.com/p/classifier-history-and-jev"),
("WOVEN: Weaving Visual World Modeling into Multimodal LLMs","https://arxiv.org/abs/2610.12417v1"),
("Rounding in Preconditioner Space","https://arxiv.org/abs/2610.12444v1"),
("OuroWorld: Bringing Any 3D World Alive","https://arxiv.org/abs/2610.12461v1"),
("OmniCapBench: A Deep-Structured Evaluation Framework","https://arxiv.org/abs/2610.12458v1"),
("Building AI for Reliable Execution: Lessons From Industrial Robotics","https://www.latent.space/p/standard-bots"),
("One Block, Multiple Depths: Recurrent Vision Transformers","https://arxiv.org/abs/2610.12448v1"),
("Marformer: A Transformer for Predicting Missing Data Distributions","https://arxiv.org/abs/2610.12379v1"),
("Credal Machine Learning for Risk-Averse Decision Making","https://arxiv.org/abs/2610.12115v1"),
("Composite Online-to-Nonconvex Conversion with Optimal Oracle Complexity","https://arxiv.org/abs/2610.12328v1"),
("Bilevel optimization for data-driven learning of Koopman embeddings","https://arxiv.org/abs/2610.12370v1"),
("Verification with Transfer: Exact Information Frontiers","https://arxiv.org/abs/2610.12211v1"),
("Quoting The New York Times","https://simonwillison.net/2026/Oct/10/the-new-york-times/"),
("Python 3.15.0 added to actions/python-versions","https://simonwillison.net/2026/Oct/10/python-actions/"),
]

def fetch(url):
    request=urllib.request.Request(url,headers={"User-Agent":"UbikResearchPilot/0.1 (public metadata only)","Accept":"application/json"})
    try:
        with urllib.request.urlopen(request,timeout=12) as response:
            return json.load(response),None
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError) as exc:
        return None,str(exc)[:180]

def qurl(base,params):
    return base+"?"+urllib.parse.urlencode(params)

def bluesky_fetch(params):
    """Try the alternate AppView; avoid hammering blocked hosts."""
    failures=[]
    for host in ("https://api.bsky.app", "https://public.api.bsky.app"):
        data,err=fetch(qurl(host+"/xrpc/app.bsky.feed.searchPosts",params))
        if data is not None:
            return data,[]
        failures.append(host+": "+str(err))
        if err and ("403" in err or "429" in err):
            continue
    return None,failures


def search_bluesky(title,url):
    searches=[url]
    arxiv=re.search(r"arxiv.org/abs/(\d{4}\.\d+)",url)
    if arxiv:
        searches.append(arxiv.group(1))
    else:
        searches.append(title[:95])
    found={}
    errors=[]
    for query in searches:
        data,failures=bluesky_fetch({"q":query,"limit":20,"sort":"latest"})
        err="; ".join(failures) if failures else None
        if err:
            errors.append(err)
            continue
        for post in (data or {}).get("posts",[]):
            author=post.get("author") or {}
            uri=post.get("uri","")
            rkey=uri.rsplit("/",1)[-1]
            handle=author.get("handle")
            if not handle or not rkey:
                continue
            link=f"https://bsky.app/profile/{handle}/post/{rkey}"
            record=post.get("record") or {}
            text=record.get("text","")
            # Explicit relation to queried URL/identifier/title, not vague topic overlap.
            if query.casefold() not in (text+" "+json.dumps(record.get("facets",[]))+" "+json.dumps((post.get("embed") or {}))).casefold():
                continue
            found[link]={"url":link,"author":handle,"text":text[:700],"created_at":record.get("createdAt"),"query":query,"relation":"explicit_string_match_unreviewed"}
    return list(found.values()),errors

def search_openalex(title,url):
    arxiv=re.search(r"arxiv.org/abs/(\d{4}\.\d+)",url)
    doi="10.3386/w35865" if "nber.org/papers/w35865" in url else None
    # Search by exact ID in the API where possible; fallback to title, with strict verification.
    params={"search":title,"per-page":5}
    data,err=fetch(qurl("https://api.openalex.org/works",params))
    if err:
        return None,err
    target=re.sub(r"[^a-z0-9]+"," ",title.lower()).strip()
    matches=[]
    for work in (data or {}).get("results",[]):
        worktitle=re.sub(r"[^a-z0-9]+"," ",(work.get("display_name") or "").lower()).strip()
        workdoi=(work.get("doi") or "").lower()
        locations=work.get("locations") or []
        linked_arxiv=any(arxiv and arxiv.group(1) in str(loc.get("landing_page_url","")) for loc in locations)
        if not (worktitle==target or (doi and doi in workdoi) or linked_arxiv):
            continue
        matches.append({"openalex_id":work.get("id"),"title":work.get("display_name"),
                        "doi":work.get("doi"),"cited_by_count":work.get("cited_by_count"),
                        "referenced_works_count":len(work.get("referenced_works") or []),
                        "cited_by_api_url":work.get("cited_by_api_url"),
                        "open_access":work.get("open_access"),
                        "matched_by":"exact_normalized_title_or_identifier"})
    return matches,None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("output",type=Path)
    p.add_argument("--limit",type=int,default=30)
    args=p.parse_args()
    rows=[]
    for title,url in SOURCES[:args.limit]:
        posts,bsky_errors=search_bluesky(title,url)
        scholarly,openalex_error=search_openalex(title,url) if ("arxiv.org" in url or "nber.org" in url) else (None,None)
        row={"title":title,"source_url":url,"bluesky_posts":posts,"bluesky_errors":bsky_errors,
             "openalex_matches":scholarly,"openalex_error":openalex_error,
             "mastodon_posts":[],"mastodon_status":"not_queried_federated_fulltext_requires_instance_access",
             "web_mentions":None,"web_mentions_status":"not_measured",
             "note":"Observed API matches only; zero results is not proof of zero citations"}
        rows.append(row)
        print(json.dumps({"title":title[:55],"bluesky_posts":len(posts),
                          "openalex_matches":len(scholarly or []),
                          "errors":bsky_errors[:1]+([openalex_error] if openalex_error else [])}),flush=True)
        time.sleep(0.15)
    result={"schema_version":1,"source_count":len(rows),"sources":rows,
            "bluesky_total_posts":sum(len(r["bluesky_posts"]) for r in rows),
            "openalex_matched_works":sum(len(r["openalex_matches"] or []) for r in rows),
            "method":"public API searches with strict explicit-match filters; no paid services",
            "limitations":["No Mastodon full-text federation-wide search","No exhaustive social coverage",
                           "OpenAlex cited_by_count may lag; title match may be ambiguous",
                           "Missing records are unknown, not zero"]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("UBIK_PUBLIC_API_SUMMARY "+json.dumps({"source_count":len(rows),"bluesky_total_posts":result["bluesky_total_posts"],"openalex_matched_works":result["openalex_matched_works"]}),flush=True)

if __name__=="__main__":
    main()
