# Live general-news acquisition pilot — observed results (2026-10-16)

Run: https://github.com/nathanasso-code/Ubik/actions/runs/38962196813 (success). Artifact: https://github.com/nathanasso-code/Ubik/actions/runs/38962196813/artifacts/12072983054

## Observed

- 36 configured feeds, 34 successfully parsed; Nature failed with ParseError and EEA feed with HTTPError.
- 1,165 RSS observations, 1,091 unique URL hints, 74 duplicate observations, 15 URL hostnames. Multiple feeds on one host are not independent publishers.
- 24 article URLs probed (2.2% of distinct discovered URLs), 19 GET successes, 5 GET failures.
- Outcomes: 10 `substantial_article_text_accessible`, 7 `substantial_page_text_unverified_article`, 2 `long_abstract_metadata`, 5 `get_failed`.
- 0 full-article completeness verifications. No copyrighted article body persisted, no republication rights verified.

## Interpretation and cautions

This demonstrates broad feed-based discovery and some direct article-text accessibility, **not** complete daily-news coverage or full-text acquisition. The 7 page-text cases may contain boilerplate; 2 descriptions are not full articles. The discovery-only audit printed 0 acquired bodies because no persisted acquired-document snapshot was supplied; **that is not evidence of 1,091 extraction failures**. The probe separately attempted 24 URLs. The sample was bounded and ordered, not statistically random or representative across all publishers. Report stratified outcomes before drawing cross-domain conclusions.

## Next actions

1. Add attempted-fetch status to canonical acquisition ledger and join it to discovery; distinguish never attempted, robots denied, HTTP error, parser failure, short extract and substantial text.
2. Stratify sampling by publisher/domain and subject; increase sample to 100–200 URLs, with per-domain budgets.
3. Compare article parser against metadata, JSON-LD and a tested main-content extraction library without retaining unauthorized bodies.
4. Build an independently annotated set of same-event/different-event/contradiction/update pairs from sources with substantial or licensed text; evaluate embedding shortlist vs LLM adjudication.
5. Only after measuring baseline, compare external search/extraction providers and their marginal cost and novel independent sources.

No public feed publication, automatic merge, nucleus creation or validated synthesis follows from this run.
