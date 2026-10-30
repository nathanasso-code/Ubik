# Ubik v6 — editorial composition with mechanical controls (preregistered 2026-10-30)

Exploratory. Question: does a simple pipeline produce, with cheap models, a page close to what an attentive
editor builds? The pipeline is a reading note per item, one editorial composition per week, and controls done
by code, not by the model.

## Inputs (frozen)

- Week 22–28 October 2026, AI corpus: 36 articles passing the strict perimeter score plus 7 social posts.
  - `ubik-corpus/reports/week-run/selection.json`, sha c59bd1c3…
- Reference: the page built by an independent agent (high-end model, subscription) that read the 43 texts.
  - `ubik-corpus/reports/v6/reference-page-agent.md`, sha 67a4733e…
  - Built before any v6 output existed, with the same three levels (facts, comments, analyses).
  - Caveat: it is one model's reading, not a human gold standard; it may favour models of the same family.
- Prompts:
  - `prompts/v6/scheda.txt` (sha 089ab0bb5dd2d9f30a837053215c614dd4e49feed79372ce32348a56b5eefdfc)
  - `prompts/v6/compose.txt` (sha f81401373c279e2558c9072aa74aae8e4ad0de113b3983185abd22c716cf3e66)

## Arms

| Arm | Model | Note |
|---|---|---|
| deepseek | DeepSeek V4.1 Flash (Nebius FP8, reasoning off) | candidate production model |
| sonnet | Sonnet 5.5 | mid-tier comparison |

- Notes are made once per arm.
- Composition runs twice per arm, to measure stability.
- Cost ceilings: 0.30 USD (deepseek) and 1.20 USD (sonnet), with preflight.

## Mechanical controls (code, no model)

- Every quote is checked verbatim against the item text (normalised whitespace and quotation marks).
- Every item must appear in the page or in the excluded list (coverage).
- Every fact, comment and analysis must reference an existing note id.
- Independent origins are counted per fact: an outlet's site and its social accounts count once. Facts are
  labelled "più origini" or "origine unica".

## Evaluation

An independent agent compares each page (anonymised, shuffled) with the reference:
- fact recall and precision;
- comments and analyses matched;
- important items missed;
- spurious or unfaithful statements;
- wrong exclusions.

Stability: overlap of facts, comments and analyses between the two compositions of the same arm.

## Predictions

1. Coverage: both arms account for at least 95% of items in every composition.
2. Verbatim quotes:
   - Sonnet at least 85% of quotes verified;
   - DeepSeek at least 70%.
3. Fact recall against the reference (6 facts):
   - Sonnet at least 4/6;
   - DeepSeek at least 3/6.
4. Precision: at most 2 facts per page that the evaluator judges outside the perimeter, not of the week or
   unfaithful.
5. Comments plus analyses: at least half of the reference's 15 entries recovered by Sonnet, at least a third by
   DeepSeek.
6. Stability: at least 70% of facts identical between the two compositions of each arm.
7. Cost: DeepSeek at most 0.15 USD for the week; Sonnet at most 1.00 USD.

## Decision rule

- If DeepSeek meets 1, 3, 4 and 6, it becomes the candidate for automatic weekly pages.
- If only Sonnet does, the choice is cost versus quality, decided with the user.
- If neither does, the composition step needs a stronger model or a different instruction before scaling.

## Results of the first run (2026-10-30), before the addendum

Blind evaluation by an independent agent. Pages were anonymised and shuffled; the key is in
`ubik-corpus/reports/v6/eval-key.json`.

| Prediction | DeepSeek (2 runs) | Sonnet (2 runs) |
|---|---|---|
| 1. Coverage ≥95% | confirmed: 100%, 100% | **falsified**: 98%, 88%; also cited non-existent item ids ("masto-dup", "masto-placeholder") |
| 2. Verbatim quotes | confirmed: 240/241 | confirmed: 203/203 |
| 3. Fact recall | confirmed: 5/6, 4/6 | confirmed: 5/6 (two reference facts merged), 4/6 |
| 4. ≤2 bad facts | **falsified**: 5 and 4 (off perimeter, dated, one duplicate) | confirmed: 1 and 2 |
| 5. Comments + analyses | confirmed: 12/15, 12/15 | confirmed: 12/15, 11/15 |
| 6. Stability ≥70% of facts | confirmed: 12/14 matched | confirmed: 5/6 matched |
| 7. Cost | confirmed: 0.07 USD | confirmed on valid runs: 0.74 USD; about 0.93 USD lost on truncated compositions (the reasoning budget cut the output; fixed) |

- **Ranking by the evaluator:**
  1. DeepSeek run 2 (7/10): most substance, finest detail.
  2. Sonnet run 2 (6/10): most selective.
  3. DeepSeek run 1 (6/10).
  4. Sonnet run 1 (5/10).
- **Common errors:**
  - A date not found in the source ("29 aprile", DeepSeek, both runs).
  - Exact dates of the week mostly missing.
  - The one-line harmonised-standard fact missed by every page.
- **Decision rule outcome:** neither arm met every criterion. DeepSeek fails on selectivity only; Sonnet fails on
  coverage and integrity.

## Addendum (preregistered before the run): variant v6-pf

Same notes and the same frozen prompts. Two changes, both done by code, not by the model.

**Mechanical prefilter before composition:**
- notes judged off-perimeter carry no facts or theses;
- notes classified as relay or promotion carry no facts or theses;
- facts must be marked reported_as_new;
- facts may not be dated more than 7 days before the week.

**New controls after composition:**
- dates written in a fact must appear in the cited notes or source texts;
- possible duplicate facts are flagged (shared note fact, or item set contained in another).

Arm: DeepSeek only, 2 compositions (expected cost about 0.03 USD).

**Predictions:**
- Bad facts per page ≤2 (prediction 4 now met).
- Fact recall stays ≥4/6.
- Comments and analyses ≥10/15.
- Coverage 100%.
- Stability ≥70%.

## Results of v6-pf (2026-10-30)

Same blind procedure; same evaluator rubric, new evaluator instance.

| Prediction | Run 1 | Run 2 |
|---|---|---|
| Bad facts ≤2 | **falsified**: 6 | **falsified**: 4 |
| Fact recall ≥4/6 | confirmed: 5/6 | confirmed: 5/6 |
| Comments + analyses ≥10/15 | confirmed: 10/15 | **falsified**: 9/15 |
| Coverage 100% | confirmed | confirmed |
| Stability ≥70% | not computed | not computed |

Cost: 0.02 USD. Overall score 6/10 for both pages, against 7 and 6 for the base DeepSeek pages.

**Reading.**
- The prefilter removed the clearly off-topic facts (Siri, election spending) and the invented date, but did
  not make the page more selective. It cost some commentary.
- Most remaining "bad facts" are reports published this week: the Open Rights Group report, the Spotlight on
  Corruption investigation and the EFF documents. The two evaluator instances labelled them differently: "valid
  extra" in the first evaluation, "not a fact of the week" in the second.
- The fact/analysis boundary for published reports is an editorial definition to settle, not a model error.
  Single-evaluator judgments carry visible noise.

**Other systematic issues:**
- dates missing even when the source gives them;
- "più origini" assigned to stories that all derive from one original source (Sveriges Radio);
- comments attached to the wrong fact;
- one misattribution between outlets.

## Addendum v6.2 (preregistered before its run, 2026-10-30)

**User decision:** pertinent reports and investigations published in the week are valid facts, catalogued as such.

**Prompt changes** (`prompts/v6.2/`):
- Notes give each fact a type ("event" or "report") and an according_to field naming the original source.
- The composition keeps two fact types and states the perimeter for facts explicitly: rules, governance or
  public policy on AI, not finance, product launches or adjacent policy.
- A comment must point to a page fact.

**New code controls:**
- The date falls back to the first publication date, marked "data di pubblicazione".
- Items attributing a fact to the same original source collapse into one: label "fonte originale unica" plus
  the source's name.
- Comment-to-fact linkage is checked against the note.

DeepSeek only: new notes plus 2 compositions, expected cost about 0.08 USD. Evaluation uses the same rubric,
with the user's rule: a pertinent report or investigation of the week is a valid fact.

**Predictions:**
- Bad facts ≤2 per page.
- Reference facts ≥5/6.
- Comments plus analyses ≥10/15.
- Coverage 100%.
- The Swedish story labelled "fonte originale unica (Sveriges Radio)".
- No fact without a date.
