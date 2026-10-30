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

## Results of v6.2 (2026-10-30)

Cost: 0.07 USD (new notes 0.046 plus two compositions 0.025).

Controls, run 2 recomputed locally after a KeyError in the control code (the pages are unchanged):

| | Run 1 | Run 2 |
|---|---|---|
| Facts (reports) | 11 (4) | 14 (5) |
| Comments / analyses / excluded | 6 / 13 / 19 | 40 / 38 / 42 (degenerate: repeated entries) |
| Missing, unknown, bad references | 0, 0, 0 | 1, 2, 9 |
| Comments linked to the wrong fact | 3 | 13 |

**Predictions, checked mechanically.** No blind evaluation: run 2 fails the controls and run 1 shows no gain in
selectivity.
- Coverage 100%: confirmed for run 1; falsified for run 2.
- No fact without a date: confirmed, through the publication-date fallback.
- Swedish story labelled "fonte originale unica": **falsified**. according_to correctly names Sveriges Radio
  for two items, but one item says "own reporting", so the code still counts two groups.
- Bad facts ≤2: not evaluated blind. Both pages keep at least the German energy law; run 2 adds more.

**Reading.**
- The v6.2 instructions did not make DeepSeek more selective: 11 and 14 facts, against 12–14 in the base runs.
- Composition variance is high: one composition in four so far is degenerate.
- Two things did work:
  - the controls flag the bad page by themselves;
  - according_to names the original source in most cases (Gazzetta Ufficiale, Sveriges Radio, Open Rights
    Group, Spotlight on Corruption, Freedom House).

**Proposed next steps** (to discuss with the user before more prompt changes):
1. An acceptance gate. A page with missing or unknown items, bad references or many wrong links is rejected
   and recomposed automatically (about 0.01 USD per attempt).
2. Selectivity as an explicit, visible rule rather than an instruction the model ignores. The code orders facts
   by independent origins and type and shows the first N; the others go to "altri fatti della settimana",
   collapsed. Nothing is lost.
3. Fields stay only if a measure shows they help. The prefilter (pf) is removed; the fact type and according_to
   stay for now, because they feed the labels the user asked for.

## v6.3 (preregistered 2026-10-30): user decisions applied, plus weekly continuity

**User decisions:**
- Keep the fields that work almost always: fact type (event, report) and according_to.
- Drop the problematic ones: the prefilter is removed.
- Highlight a fixed number of facts: 5.

**Changes:**
- **Acceptance gate (code).** A page is rejected and recomposed, up to 3 attempts, when it has missing or unknown
  items, bad references, more than 2 comments linked to the wrong fact, possible duplicate facts or repeated
  entries.
- **Highlight rule (code).** Facts of type event or report come first. They are ordered by independent original
  sources, then official origin, then distinct outlets, then number of items. The first 5 are "Fatti in
  evidenza"; the rest go to "Altri fatti della settimana".
- **Continuity.** The composition receives the facts of the previous accepted page and may set "continues" on a
  later step of the same story (`prompts/v6.3/compose.txt`, sha c85b5d0e683689e9011fc0190cb8abfe9ea789ce96a8baa2d7df47e5703e0548; the notes prompt is unchanged from v6.2).
  Invalid ids are dropped by code. `ingestion/ubik_v6_matrices.py` chains the links into vicende (matrices).

**Run.** DeepSeek on week 15–21 October (22 items, new notes, 1 composition), then week 22–28 October (frozen
selection, v6.2 notes reused, 2 compositions) with the previous week as memory. Expected cost about 0.06 USD.

**Predictions:**
- Every published page passes the gate within 3 attempts.
- At least one valid "continues" link: a fact of week 22–28 that is a later step of a week 15–21 story.
- No continues link that an evaluator judges merely thematic.

## Results of v6.3 (2026-10-30)

Cost: 0.093 USD, of which 0.023 for new notes for week 15–21 and 0.07 for 7 compositions.

**Week 15–21:** 1 composition, accepted at once. 7 facts, 6 comments, 6 analyses; no repairs.

**Week 22–28:** the strict gate rejected all 6 compositions, mostly for 1–4 references to note ids that do not
exist. Prediction "every published page passes the gate within 3 attempts" is **falsified**.

**Change applied after the run** (code, applied locally to the same paid pages, content unchanged except the
logged removals):
- References that cannot be verified are removed.
- Entries for unknown items are dropped.
- Items the composition forgot are listed as excluded "non_valutato".
- Every repair is logged; a page with more than 5 repairs is still rejected.

With this repair-by-removal, the first acceptable composition is attempt 2 in run 1 (4 repairs) and attempt 1 in
run 2 (3 repairs).

**Continuity.** The model set "continues" on 2 facts in every composition of week 22–28, always the same two:
- **Texas sues OpenAI → the suits by other states on 14 October.** A genuine later step of the same story
  (prediction confirmed).
- **Italian decree in force on 23 October → the same decree, announced the previous week.** The same fact seen
  in two weeks: card continuity rather than a new step. It is not thematic, so the prediction on thematic links
  holds. The matrix builder should distinguish "same fact, updated" from "next step".

No invalid continues ids.

**Quality note.** One week 15–21 fact bundles three distinct events: the state lawsuits, AI Office requests and
FTC subpoenas. This is a composition fault the controls do not catch.

## Addendum, 30 ottobre: correzioni nel codice (nessuna chiamata al modello)

Riscontrate rileggendo la settimana 22–28 ottobre e ricalcolate sulle pagine già pagate con `ingestion/ubik_v6_recheck.py`.

1. **Conferme indipendenti gonfiate.** Le fonti citate dentro un solo articolo (un op-ed, un portavoce, il rapporto) contavano come conferme separate: Delaware risultava a 4, Home Office a 3, entrambi da un solo articolo ed entrambi in evidenza. Ora le conferme sono le testate (origini); due testate si fondono se attribuiscono il fatto alla stessa fonte originale o se una cita l'altra come fonte. Settimana 22: i fatti con più conferme reali sono 2 su 10 (Svezia 3, Digital Omnibus 2).
2. **Riferimento sbagliato.** Un fatto (Spotlight on Corruption) puntava alla nota di un altro articolo (Germania e Nvidia). Ora un fatto deve condividere almeno un nome proprio (prefisso di 5 lettere, così da reggere la traduzione) con la nota e il testo che cita; altrimenti il riferimento si toglie, con registro.
3. **Spareggio.** A parità di conferme contava il numero di riferimenti, che premiava i fatti accorpati; ora conta gli articoli distinti. Il numero di note fuse in un fatto è registrato (`bundled_note_facts`) ma non cambia l'ordine.
4. **Provato e scartato:** escludere dall'evidenza i fatti con note datate oltre due settimane prima. Le schede sbagliano l'anno (Texas e Nvidia, entrambi della settimana, datati 2025): il filtro nascondeva fatti veri.

Effetto sulla settimana 22: in evidenza Svezia, Digital Omnibus, Germania–Nvidia, decreto italiano, Texas; escono Delaware e Home Office, che restavano lì per il conteggio gonfiato. Settimana 15: invariata.
