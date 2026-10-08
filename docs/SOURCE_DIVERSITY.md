# Source diversity and acquisition adapters — pilot policy

Ubik's source universe includes institutional labs, journals, newsrooms, independent researchers, personal blogs, newsletters, open-source developers, social posts, community forums and video creators. Editorial size is **not** a proxy for epistemic reliability.

## Current enabled pilot inputs
RSS/Atom feeds from labs, arXiv, research/industry blogs and independent authors (initially Simon Willison). The registry entries are **candidates**, not guaranteed working endpoints; validate HTTP status, MIME type, freshness and usage permissions through actual pilot runs. Do not automatically publish discovered entries.

## Additional adapter priorities
1. **Personal sites and newsletters**: prefer author-published RSS/Atom; support feed autodiscovery and manual submission. Do not circumvent subscriptions or paywalls.
2. **Bluesky**: selected-author `app.bsky.feed.getAuthorFeed` can be queried via `https://public.api.bsky.app` without authentication for public reads. Start with explicitly selected authors, avoid network-wide collection. Exclude repost-only duplication or preserve explicit repost provenance.
3. **GitHub**: selected repository releases and research artifacts; identify release authors, version, repository and original release URL. Releases are not independent verification of product claims.
4. **Mastodon**: per-instance API policy and author-specific retrieval; honor local rate limits.
5. **YouTube and podcasts**: public channel/feed metadata when available; transcripts and reuse rights require separate access decisions.
6. **Forums / social networks**: evaluate official APIs, rate limits, privacy and content terms separately. Unsupported access is a documented coverage gap, not permission to scrape around restrictions.

## Identity and independence
Preserve `source_id`, `author_id`, original publication URL, canonical URL, retrieval time, publication time, and any reference to the originating post, research paper, release or press announcement. A syndicated news story, an author's cross-posted blog entry and its social announcement may be three records but only one underlying information lineage.

Differentiate `unavailable`, `not_configured`, `temporarily_failed`, and `access_restricted` in monitoring. Never claim the system captures 'all sources'. The long-term objective is **broad and auditable coverage**, not impossible universal access.

## Operating policy
Use a small initial set of author and institution feeds with low-cost polling; expand via measured coverage and editorial/user suggestions. Ingestion is not verification. Clustering and nucleus promotion are separate downstream stages. Keep original author attribution and direct outbound links even when a synthetic epistemic card represents the story.
