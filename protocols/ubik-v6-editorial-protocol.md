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
