# Ubik — Next empirical phase: discovery, acquisition and semantic discrimination

Status: development plan + newly committed offline audit, **not a completed live experiment**. 2026-10-16. Read with `UBIK_DECISION_RECORD_2026-10-16.md`.

## Immediate implementation

`ingestion/discovery_acquisition_gap_audit.py` compares an existing discovery snapshot (`items`) with a supplied acquired-document snapshot (`documents`). It measures unique URL hints, duplicate observations, domains, matched documents, missing acquired records, short texts, and texts >=800 chars. Tests: `tests/test_discovery_acquisition_gap_audit.py`.

Example:
```sh
python -m ingestion.discovery_acquisition_gap_audit --discovery data/discovery/global-rss-pilot.json --acquired /path/to/acquired.json --output /tmp/ubik-gap-audit.json
python -m unittest tests.test_discovery_acquisition_gap_audit
```
Use the **actual artifact paths** from the relevant run; the example is not a claim that the acquired snapshot exists at the placeholder path. An absent acquired snapshot yields a discovery-only report, **not** a measured extraction failure rate.

## First instrument the acquisition funnel

Per URL record: discovery channel, timestamp, canonical hint, fetch attempted yes/no, HTTP outcome, extraction method, extracted characters, text quality tier (complete / substantial / partial / inaccessible), license/rights assessment, original URL, and error category. Count *attempted and successful* extraction separately. Character count alone is not full-text validation.

## Discovery extension priorities

1. RSS/Atom plus site feed autodiscovery; XML sitemaps, news sitemaps, category/archive pages; bounded per-domain exploration.
2. Original links surfaced on Bluesky/Mastodon, with attribution and distinction between primary social contribution and link-only discovery. Deduplicate syndication and track independent publishers.
3. Fallback extraction: HTTP + main-content parser (e.g. Trafilatura), JSON-LD/structured content, documented site APIs; only selectively use rendering or external extractors after failure.
4. Official papers/repositories/primary sources; Wikinews and Europe PMC where relevant. Common Crawl is archival, **not a live news feed**.
5. Compare optional Exa/Tavily or other search providers *only after* baseline coverage and per-100-URL cost are measured; no assumption of comprehensive daily-news coverage or guaranteed full text.
6. Future gap-guided research: retrieve original studies, sources of conflicting claims, updates and independent coverage with depth/cost limits and marginal-utility stopping. This is **not implemented**.

Never bypass paywalls, authentication or access restrictions; respect robots/terms, crawl budgets, licensing, SSRF controls, and prompt-injection boundaries. Public availability does not automatically grant republication rights.

## Semantic experiment to run

Use substantial texts or extended abstracts and an independently reviewed reference set including:
- same news event with different language/terminology (must merge),
- superficially similar topic but distinct event (must separate),
- same event with complementary facts (merge + preserve differences),
- conflicting statements on same issue (link as disagreement; do not silently collapse),
- sequential update/correction (temporal relation),
- paraphrase, syndication, near-duplicates and distinct original sources.

Compare lexical/embedding baseline vs embedding shortlist + affordable LLM adjudication, on identical held-out pairs. Record event identity, claim relation, evidence spans, correct/incorrect merges, missed merges, abstentions, synopsis faithfulness, omission, token spend and latency. Model-generated evidence quotes must match supplied text; diagnose quote errors independently of semantic relation quality.

**Do not infer semantic accuracy from the hierarchical classification pilot.** The latest OpenRouter run `38877451363` had 20 responses, 6 accepted hierarchical classifications and 14 rejected for verbatim evidence mismatch, at $0.00323699 reported cost. This does not measure pairwise event recognition.

## Product boundaries

Sources outside initial curated topics remain in the general feed with normalized descriptive tags; cards group the **same news event**. Nuclei are rare persistent community spaces, not auto-generated taxonomy levels. The experimental corpus is not published automatically.

## Next proof points

A. Audit real RSS snapshot against real attempted extraction records; quantify unattempted vs HTTP failure vs parser failure vs insufficient text.  
B. Run 100–200 diverse current-news URLs across multiple domains and topics, measure substantial-text coverage and cost, preserving provenance.  
C. Run blind, annotated semantic-pair benchmark on real substantial texts.  
D. Only then decide whether paid search/extraction providers materially improve coverage.
