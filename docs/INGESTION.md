# Ubik ingestion pipeline v1

## Principle
Contributors submit raw material; Ubik creates canonical events. UI cards and map points are projections of canonical events, never independently authored copies.

## Accepted batch inputs
- Ubik JSON
- generic JSON arrays / {data:[...]} / {events:[...]}
- CSV
- ACLED exports (field aliases supported: event_id_cnty, event_date, admin1, location, latitude, longitude, event_type, sub_event_type, civilian_targeting, source, notes, fatalities)

## Pipeline
raw -> adapter -> normalize -> geographic guardrail -> deduplicate -> merge provenance -> canonical corpus -> map/feed

## Status
Imported records default to `signal`. Import is not validation.

## Deduplication v1
Same date + ~100m coordinates + event type is treated as a candidate duplicate and source provenance is merged. This is intentionally conservative and will later be replaced by scored entity resolution using time, location, weapon, target and semantic similarity.

## Scale
The browser must not eventually load tens of thousands of full source records at once. The next backend phase should store canonical events in PostgreSQL/Supabase and expose paginated/viewport queries. The JSON corpus is an intermediate portable format.

## ACLED adapter
ACLED programmatic access requires authenticated API access. API responses are paginated for large result sets. Credentials must remain server-side; never commit them to this repository.


## Source genealogy and independence

Ubik counts information lines, not article volume. The first deterministic pass lives in `scripts/infer_source_dependencies.py`.

Rules:
- explicit agency attribution and explicit upstream URLs create inspectable dependency candidates;
- textual similarity alone never proves dependency or independence;
- absence of a detected dependency never upgrades sources to independent;
- shared official statements, documents, datasets, papers, images, video, wire copy, or eyewitnesses should become common upstream nodes;
- a later model may propose ambiguous relations, but must return evidence for review rather than silently changing independence;
- publication surfaces should report unknown/partial reconstruction when genealogy is incomplete.

Target graph: `event -> claim -> evidence line -> origin -> dependency/republication -> revision`. Validation operates at claim level, not publisher-count level.
