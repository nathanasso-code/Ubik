"""Topic-led, bounded public social discovery. No issue-specific seed terms.

This is a manual experiment runner; automatic triggering on topic creation
requires integration with the topic creation backend and approved rate budgets.
"""
import re
from html import unescape
from html.parser import HTMLParser
from urllib.parse import quote, urlencode, urlsplit
from .contracts import observation, canonical_url_hint
from .mastodon_discovery import discovery_url
from .transport import get_json
from .topic_query_expansion import propose_expansion

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls=[]
    def handle_starttag(self, tag, attrs):
        if tag=="a":
            url=dict(attrs).get("href")
            if url:
                self.urls.append(url)

def topic_queries(name, aliases=()):
    if not isinstance(name,str) or not name.strip() or len(name)>120:
        raise ValueError("Invalid topic name")
    terms=[name.strip(), *aliases]
    if len(terms)>9:
        raise ValueError("Maximum 10 topic terms")
    out=[]
    for term in terms:
        if not isinstance(term,str) or not term.strip() or len(term)>120:
            raise ValueError("Invalid alias")
        term=" ".join(term.split())
        if term.casefold() not in {x.casefold() for x in out}:
            out.append(term)
    return out

def bluesky_search_url(query, limit=30):
    if not isinstance(query,str) or not query.strip() or type(limit) is not int or not 1<=limit<=100:
        raise ValueError("Invalid search query")
    return "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?"+urlencode(
        {"q":query,"limit":limit,"sort":"latest"})

def _external_urls(text, facets=(), embed=None):
    found=[]
    for item in facets or []:
        for feature in item.get("features",[]) if isinstance(item,dict) else []:
            if isinstance(feature,dict) and feature.get("$type")=="app.bsky.richtext.facet#link":
                found.append(feature.get("uri"))
    if isinstance(embed,dict):
        external=embed.get("external") or {}
        if isinstance(external,dict):
            found.append(external.get("uri"))
    found.extend(re.findall(r'https?://[^\s<>"]+',text or ""))
    urls=[]
    for url in found:
        try:
            parsed=urlsplit(url)
            if parsed.scheme!="https" or not parsed.hostname or parsed.hostname in ("bsky.app",):
                continue
            key=canonical_url_hint(url.rstrip(".,);"))
            if key not in urls:
                urls.append(key)
        except (ValueError,TypeError):
            pass
    return urls

def collect_bluesky(query,limit=30,fetch=get_json):
    endpoint=bluesky_search_url(query,limit)
    payload=fetch(endpoint)
    posts=payload.get("posts") or []
    if not isinstance(posts,list) or len(posts)>limit:
        raise ValueError("Invalid Bluesky response")
    results=[]
    for post in posts:
        try:
            uri=post["uri"]
            author=post["author"]["did"]
            record=post.get("record") or {}
            text=record.get("text") or ""
            urls=_external_urls(text,record.get("facets"),post.get("embed") or record.get("embed"))
            results.append(observation(connector="bluesky",source_id=author,external_id=uri,
                title=" ".join(text.split())[:500] or "Public Bluesky post",
                url="https://bsky.app/profile/"+author+"/post/"+uri.rsplit("/",1)[-1],
                discovered_from=endpoint,published_raw=record.get("createdAt"),
                metadata={"topic_query":query,"linked_documents":urls,
                          "like_count":post.get("likeCount"),"repost_count":post.get("repostCount"),
                          "reply_count":post.get("replyCount"),"text_preview":text[:800],"hashtags":[tag for tag in re.findall(r"(?<!\\w)#([\\w]{3,48})",text)]}))
        except (KeyError,TypeError,ValueError):
            continue
    return results

def collect_mastodon(instance,tag,limit=30,fetch=get_json):
    endpoint=discovery_url(instance,"tag",tag=tag,limit=limit)
    statuses=fetch(endpoint)
    if not isinstance(statuses,list) or len(statuses)>limit:
        raise ValueError("Invalid Mastodon response")
    results=[]
    for status in statuses:
        try:
            if status.get("visibility")!="public" or status.get("reblog"):
                continue
            author=status["account"]["url"]
            html=status.get("content") or ""
            parser=Links()
            parser.feed(html)
            urls=[]
            for url in parser.urls:
                try:
                    parsed=urlsplit(url)
                    if parsed.scheme!="https" or not parsed.hostname:
                        continue
                    if parsed.hostname in (urlsplit(author).hostname,urlsplit(instance if "://" in instance else "https://"+instance).hostname):
                        continue
                    key=canonical_url_hint(url)
                    if key not in urls:
                        urls.append(key)
                except (TypeError,ValueError):
                    continue
            results.append(observation(connector="mastodon",source_id=author,
                external_id=status.get("uri") or status["url"],
                title=" ".join(re.sub(r"<[^>]*>"," ",unescape(html)).split())[:500] or "Public Mastodon post",
                url=status["url"],discovered_from=endpoint,published_raw=status.get("created_at"),
                metadata={"topic_query":tag,"linked_documents":urls,
                          "hashtags":[t.get("name") for t in status.get("tags",[]) if isinstance(t,dict) and isinstance(t.get("name"),str)],
                          "like_count":status.get("favourites_count"),
                          "repost_count":status.get("reblogs_count"),
                          "reply_count":status.get("replies_count")}))
        except (KeyError,TypeError,ValueError):
            continue
    return results

def discover(name,aliases=(),*,instances=("mastodon.social",),limit=30,fetch=get_json,expand=False,max_expansion_terms=8):
    terms=topic_queries(name,aliases)
    records=[]; errors=[]
    for term in terms:
        try:
            records.extend(collect_bluesky(term,limit,fetch))
        except (ValueError,RuntimeError,OSError) as exc:
            errors.append({"provider":"bluesky","term":term,"error_type":type(exc).__name__})
        tag=re.sub(r"[^\w]","",term,flags=re.UNICODE)
        if not tag:
            continue
        for instance in instances:
            try:
                records.extend(collect_mastodon(instance,tag,limit,fetch))
            except (ValueError,RuntimeError,OSError) as exc:
                errors.append({"provider":"mastodon","term":tag,"instance":instance,
                               "error_type":type(exc).__name__})
    seed_records=list({x["id"]:x for x in records}.values())
    expansion=propose_expansion(seed_records,terms,max_terms=max_expansion_terms) if expand else []
    for item in expansion:
        term=item["term"]
        try:
            records.extend(collect_bluesky("#"+term,limit,fetch))
        except (ValueError,RuntimeError,OSError) as exc:
            errors.append({"provider":"bluesky","term":term,"phase":"expansion","error_type":type(exc).__name__})
        for instance in instances:
            try:
                records.extend(collect_mastodon(instance,term,limit,fetch))
            except (ValueError,RuntimeError,OSError) as exc:
                errors.append({"provider":"mastodon","term":term,"phase":"expansion","instance":instance,"error_type":type(exc).__name__})
    unique={x["id"]:x for x in records}
    documents={}
    for record in unique.values():
        for url in record["metadata"].get("linked_documents",[]):
            row=documents.setdefault(url,{"url":url,"accounts":set(),"posts":set(),"providers":set()})
            row["accounts"].add(record["source_id"])
            row["posts"].add(record["url"])
            row["providers"].add(record["connector"])
    ranked=sorted(({"url":x["url"],"distinct_accounts_observed":len(x["accounts"]),
                    "post_count":len(x["posts"]),"providers":sorted(x["providers"]),
                    "post_urls":sorted(x["posts"])} for x in documents.values()),
                  key=lambda x:(-x["distinct_accounts_observed"],-x["post_count"],x["url"]))
    return {"topic":name,"queries":terms,"posts":len(unique),"documents":ranked,
            "errors":errors,"expansion":expansion,"seed_posts":len(seed_records),
            "coverage":"Bounded public search; handles not verified as independent; no automatic claims or summaries."}
