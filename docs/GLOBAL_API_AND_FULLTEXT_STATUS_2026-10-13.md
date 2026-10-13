# Global acquisition: API integration and full text — 13 October 2026

## Empirical failure that triggered this change
Run 38376857116, `discover` success, artifact 11801098756: 36 RSS feeds configured, 34 reported `ok`, 992 observations, 920 distinct URLs. Yet **arXiv cs.AI, cs.LG, econ and Wikinews en/it all reported `ok` with 0 items**; EEA RSS returned HTTPError. Wikinews text pilot: **0 attempts, 0 texts**. Therefore "feed succeeded" was not a useful coverage indicator. Do not cite this run as proof of arXiv or Wikinews ingestion.

## Implemented in branch develop/ubik-core
- `ingestion/global_api_discovery.py`: first-class public metadata APIs: arXiv Atom search, Europe PMC open access search, MediaWiki allpages EN/IT; per-provider status and item counts.
- `ingestion/merge_global_discovery.py`: appends API-discovered records to the existing global RSS snapshot **before** subsequent social discovery, persistent ledger, semantic review, and candidate cards. Distinguishes `empty` from `ok` with actual documents.
- `ingestion/europe_pmc_licensed_texts.py`: requests fullTextXML for Europe PMC PMCID, parses article body, checks CC BY 4.0 / CC BY-SA 4.0 / CC0 URLs and excludes NC/ND; stores candidate permitted texts in the GitHub Actions artifact under `licensed-papers` for **rights review**, not production publication. It does not yet perform complete rights review of third-party material, figures, and attribution.
- `ingestion/wikinews_text_pilot.py`: API fallback and temporary text extraction, no permanent storage.
- Existing GNews, RSS, Bluesky, Mastodon, access GET and semantic components remain in repository. **GNews is not automatically guaranteed to run on this workflow**: confirm active job and credentials separately. Do not equate existence of a connector with an enabled provider.
- Workflow `global-discovery-pilot.yml` now calls all newly integrated API and Europe PMC text stages.

## Verification status
**Code committed and Actions triggered, but new API and full-text outcomes are not verified until latest artifacts are inspected.** The run 38377426298 was in progress when this note was authored. Counts of acquired full texts: **unknown**, not zero and not claimed successful. A configured provider may fail due to rate limits, HTTP access, response format or licensing.

## Critical next steps
1. Read `global-api-discovery.json`, `europe-pmc-text-results.json`, `licensed-papers` and `wikinews-text-pilot.json` from the newest artifact. Fix errors until actual full text is acquired.
2. Feed permitted full article text into semantic document-level routing, calibrate on labeled samples and generate candidate same-event groups only with entity/date/location/claim verification.
3. Create permanent provider inventory including **active/inactive**, credential requirements, successful observations, zero-result alarms and freshness. Extend coverage beyond the current explicit 4 APIs; "all public APIs worldwide" is not a finite discoverable or verifiable list.
4. Store licensed texts in controlled application storage with revision, license evidence, author attribution and withdrawal support. GitHub artifact is **not** production storage.
5. Do not modify `main` or production without compatibility validation.
