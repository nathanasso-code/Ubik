# Extraction cost pilot (preregistered 2026-10-29)

Exploratory, on the AI corpus. Question: can extraction become about ten times cheaper without losing the
events that make cards and links?

## Inputs

- 14 articles from `ubik-corpus`, selected by `tools/select_extraction_pilot.py`:
  - window 2026-10-22 to 2026-10-28;
  - full text, rough in-perimeter triage, at least 300 words;
  - ordered by SHA-256 with seed `ubik-extraction-pilot-2026-10-29`;
  - at most 2 per origin.
- Rough triage lets some off-topic articles through. They stay in: the real pipeline will see them too.
- Frozen v5.1 extraction prompt (sha 22a63958…), one news item per article.

## Arms

| Arm | Model | Input |
|---|---|---|
| S-full | Sonnet 5.5 | title + text up to 6000 characters (current configuration) |
| D-full | DeepSeek V4.1 Flash (Nebius FP8, reasoning off) | same |
| D-lede | DeepSeek V4.1 Flash | title + first ~1500 characters, cut at a sentence end |

- One retry on an invalid answer.
- Cost ceiling 0.45 USD; the preflight estimate is about 0.40 USD.

## Blind reference (before any extraction)

An independent agent reads the 14 articles and writes, for each one:
- the main fact (who did what);
- whether it is in the perimeter "AI rules in Europe and the US";
- up to 3 earlier events the article cites that a reader would need to connect it to other coverage.

The agent writes this before any extraction exists. After the run, the same procedure, with arms anonymised
and shuffled, judges:
- for each arm, whether the primary event matches the main fact;
- whether each reference event appears among the arm's events.

## Measures

- Cost per arm and per article.
- Valid answers.
- Events per article (narrated, referenced).
- Primary event correct against the reference.
- Recall of the reference context events.
- E5 coverage of S-full events in each DeepSeek arm (best cosine ≥ 0.90).

## Predictions

1. D-lede costs at most 1/10 of S-full per article.
2. D-full costs at most 1/8 of S-full.
3. D-lede yields at most 60% of S-full's events (median per article).
4. Primary event correct:
   - S-full at least 12/14;
   - D-full at least 11/14;
   - D-lede at least 11/14.
5. Reference context events recalled:
   - S-full at least 70%;
   - D-full within 15 points of S-full;
   - D-lede at least 20 points below S-full.
6. DeepSeek arms: at most 2 invalid answers after retry, per arm.

## Decision rule (stated in advance)

- If D-full meets predictions 4–6 within the stated margins, it becomes the candidate extractor for the
  corpus pipeline. It is then confirmed on a larger sample with judges before adoption.
- If D-lede keeps primary events but loses context events, the lede alone is not enough. A hybrid is the next
  candidate: lede for the primary event, plus a cheap pass for cited events.
- If both DeepSeek arms miss primary events, extraction stays on Sonnet. Savings then come only from the
  judging cascade.
