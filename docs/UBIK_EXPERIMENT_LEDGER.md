# Ubik — registro sperimentale continuativo

Questo documento è la fonte di continuità degli esperimenti: non confondere discovery, accessibilità, completezza, diritti, analisi semantica e accuratezza. Ogni run deve conservare commit, configurazione, campione, risultati, limiti e prossimo esperimento.

## Principi invarianti
- Feed generalista; topic curati e limitati; card per stesso evento; nuclei rari.
- Acquisizione RSS/API/social/archivi; conservare URL e provenienza; rispettare robots, sicurezza di rete e diritti.
- Soglia di riferimento: 800 caratteri di testo sostanziale o abstract esteso; lunghezza da sola non dimostra qualità né integralità.
- Selezione preliminare locale/economica (embedding, similarità lessicale, deduplica); LLM solo su casi informativi/incerti. Valutare insieme recall dei candidati, accuratezza semantica e costo. Una soglia rigida non validata può perdere parafrasi.
- Non chiamare «accuratezza» la percentuale di risposte accettate da un validatore di citazioni; non chiamare «fallimento di acquisizione» l'assenza di uno snapshot persistito.
- Le analisi di accessibilità non autorizzano a ripubblicare contenuti.

## Run A — primo pilot accessibilità
- Run: https://github.com/nathanasso-code/Ubik/actions/runs/38962196813
- 36 feed, 34 riusciti; 1.165 osservazioni RSS, 1.091 URL distinti, 15 domini.
- 24 URL selezionati **in ordine feed**, massimo 5 per host: non casuali né rappresentativi.
- 19 GET riusciti; 10 con testo sostanziale in elemento article; 7 con testo pagina non verificato; 2 abstract metadata estesi; 5 GET falliti; zero testi integrali verificati.

## Run B — campionamento corretto
- Commit correzione sintassi: c2fc94b42d2f4a38fea445b953644f999adbba1e.
- Run: https://github.com/nathanasso-code/Ubik/actions/runs/38963366209 — **successo**.
- Campione pseudocasuale riproducibile, seed 42, stratificato per host; 90 URL, 6 per ciascuno dei 15 domini (limite 7).
- 72 GET riusciti; 40 con testo sostanziale in elemento article; 29 testo pagina non verificato; 3 abstract metadata estesi; 18 fallimenti; zero testi integrali verificati.
- Campione bilanciato per host, **non ponderato** rispetto alla distribuzione del corpus.

## Run C — diagnostica per editore
- Run: https://github.com/nathanasso-code/Ubik/actions/runs/38964497312 — **successo**.
- Sei URL per host. Testo article sostanziale: Ars Technica, ABC Australia, DW, Euronews, The Verge 6/6; BBC e Guardian 5/6.
- Testo pagina non verificato: arXiv, TechCrunch, France24, ScienceDaily 6/6; Al Jazeera 4/6 (+2 abstract metadata estesi).
- GET falliti: Phys.org, NPR, NYT 6/6. Non inferire la causa senza diagnosi.
- Modulo: ingestion/acquisition_quality_report.py.

## Stato semantico pregresso
- Smoke OpenRouter: https://github.com/nathanasso-code/Ubik/actions/runs/38874914586 — HTTP 200.
- Esperimento Qwen 3 32B: https://github.com/nathanasso-code/Ubik/actions/runs/38877451363. 24 testi Europe PMC con licenza compatibile, 20 inviati al modello, 6/20 accettati dal validatore delle citazioni, 14/20 respinti; costo segnalato $0.00323699. Il 30% **non è** accuratezza delle relazioni.
- Pilot locale TF-IDF e coda embedding→LLM presenti, non ancora validati end-to-end sul corpus RSS.

## Protocollo obbligatorio per i prossimi run
1. Registrare input, versione del codice, seed, stratificazione, editori, URL tentati e motivi di errore.
2. Confrontare **sugli stessi URL** estrattore HTML attuale vs recupero di metadati strutturati e parser alternativo; niente bypass o persistenza non autorizzata di corpi protetti.
3. Distinguere testo article, testo pagina incerto, abstract esteso e testo integrale **verificato**; misurare rumore con campione annotato.
4. Su testi sostanziali legalmente analizzabili, costruire coppie positive e negative annotate; confrontare preselezione locale vs baseline, con recall@k, falsi negativi, chiamate LLM e costo.
5. Riportare solo risultati di workflow completati e verificati. Aggiungere run e risultati qui, non sovrascrivere lo storico.

## Run D — HTML versus JSON-LD structured signal
- Run https://github.com/nathanasso-code/Ubik/actions/runs/38965510012 — **success** (including three new unit tests).
- Same sampling configuration (90, seed 42, stratified across 15 hosts); 40 substantial HTML article elements; 12 URLs with JSON-LD articleBody >=800 characters. **Overlap not measured yet**: 12 is not a verified increment in acquired documents.
- 66 successful GETs, 18 GET failures, 6 robots_unavailable (arXiv), 23 substantial unverified page text, 3 long abstract metadata. Prior run had 72 GET successes, 29 unverified page texts, no robots_unavailable. Do not interpret these transient access differences as parser regression.
- Next: compute JSON-LD/HTML overlap and incremental yield on matched URLs, including host-level breakdown; then manually assess content relevance and completeness before any semantic claims.

## Run E — measured incremental yield, same URL sample
- Run https://github.com/nathanasso-code/Ubik/actions/runs/38965964363 — **success**.
- 90 URL, HTML substantial article signals 40; JSON-LD articleBody >=800 characters 12; **overlap 12; JSON-LD-only 0; union 40**. JSON-LD was observed only for The Verge (6) and Euronews (6), both already HTML-positive.
- This rejects the hypothesis that JSON-LD alone improves the *count* of substantial accessible articles in this sample. It may still corroborate extracted HTML and cannot establish completeness.
- 72 GET successes, 18 GET failures, 30 unverified page-text cases and 2 long abstract cases in this run. Per-run access variation should not be mistaken for parser changes.
- Next priority: extract clean text from uncertain page-text publishers with a distinct bounded paragraph/content heuristic, and benchmark on the exact same URLs; assess contamination before any semantic clustering. Keep JSON-LD as low-cost secondary signal only.

## Run F — independent open-source extractors, empirical coverage
- Run https://github.com/nathanasso-code/Ubik/actions/runs/38967865468 — **success**, including new regression tests. Same 90 sampled URLs and single authorized HTML fetch per URL; no extracted text persisted.
- Baseline HTML article element: **40/90** at >=1200 chars and >=180 words. Trafilatura 2.3.1: **68/90** at >=800 chars and >=100 words; 40 overlap with baseline, **28 additional signals**. Readability-lxml 0.9.0: **65/90**, 39 overlap, **26 additional signals**, union with HTML 66.
- Trafilatura domain positives: Guardian 6, Ars Technica 6, Al Jazeera 5, The Verge 6, arXiv 6, ScienceDaily 6, France24 4, TechCrunch 6, DW 6, BBC 5, ABC 6, Euronews 6; zero phys.org, NPR, NYT (access failures).
- Crucial: **different thresholds** baseline vs library, and library output is not yet manually validated. 68 is a substantial-text *screening signal*, NOT 68 confirmed complete clean articles. Do not report 28 as confirmed article recoveries. Need paired same-threshold quality/boilerplate audit and controlled reference sample before semantic benchmarking.
- JSON-LD remains auxiliary: previous run showed zero incremental URL coverage.

## Run G — equal-threshold comparison (verified)
- https://github.com/nathanasso-code/Ubik/actions/runs/38968334318 **success**. 90 sampled URLs, **same threshold for all methods**: >=1200 characters and >=180 words.
- HTML baseline 40; Trafilatura 64 (39 overlap HTML, 25 additional, union 65); Readability 60 (37 overlap HTML, 23 additional, union 63). HTML + Trafilatura screening coverage +62.5% relative to baseline (65 versus 40).
- Caveat: screening coverage is NOT verified clean article completeness, and 90 publisher-stratified URLs are not representative of the overall source population. Follow up with extraction-quality audit before using this material as ground truth for semantic analysis.

## Run H — automated contamination screening of extractions
- Run https://github.com/nathanasso-code/Ubik/actions/runs/38968901524 — **success**.
- Same 90-URL stratified pilot, HTML baseline 40 at >=1200 characters and >=180 words; Trafilatura 64 (39 baseline overlap, **25 additional**, 65 union). Readability 61 at the same threshold (37 baseline overlap, 24 additional, 64 union). Access outcomes: 72 GET successes, 18 failures.
- For **25 Trafilatura-only candidates**, heuristic checks found **0 with configured boilerplate phrases**, **0 with repeated long sentences**, and **0 without long sentences**. This is only a *weak automated contamination screen*; it is NOT manual validation, semantic correctness, or completeness evidence. The phrase list is narrow and English-only.
- Artifact: `live-coverage-extraction-quality.json` includes URLs and per-URL metrics but no article bodies. Source: acquisition-coverage-live-pilot workflow artifact.
- Decision: Trafilatura primary candidate, Readability fallback candidate, HTML control. Next gate: quality labels against a small human-reviewed reference sample; then local-first semantic benchmark using source-attributed texts.

## Run I — 1,091-source cross-publisher ambiguity shortlist
- Run https://github.com/nathanasso-code/Ubik/actions/runs/38970603252 — **success**. 36 configured feeds, 34 successful, 1,165 observations, 1,091 unique URLs across 15 publisher domains.
- Sparse TF-IDF over RSS titles (double weight) and descriptions: **155,816 nonzero cross-domain candidate pair scores**; 100 highest ranked pairs preserved as source-linked artifact. This is NOT 155,816 validated same-event pairs, nor a semantic accuracy measurement.
- Empirical hard examples: Sally Rooney France24/NPR score 0.7035; Katie Zacharia Al Jazeera/ABC 0.6693; West Bank olive-harvest BBC/France24 0.6365; Pakistan school roof BBC/NYT 0.5514 with headline counts 33 vs 32. Differences need event-time and evidence review, not automatic contradiction labels.
- Added human-readable 40-pair table renderer and regression tests; an initial test incorrectly assumed stable pair ordering and was corrected in commit 55621d47. The **successful run above predates these tests**, so inspect the later Actions runs for their final outcome.
- Next: authorized full/extended text acquisition for selected cross-publisher pairs, explicit same-event vs related-event labels, claim-level numerical comparisons, measured precision and cost. Details: docs/UBIK_CROSS_SOURCE_AMBIGUITY_EXPERIMENT.md.

## Aggiornamento 18 ottobre 2026 — benchmark congelato e Qwen in due fasi
Il riepilogo completo, le metriche con denominatori corretti, gli errori di accorpamento (Ucraina/Euronews), i run 39111933850 e 39114498864, e le istruzioni di continuità sono in [HANDOFF_UBIK_2026-10-18.md](HANDOFF_UBIK_2026-10-18.md). Il secondo run era in corso all'ultima verifica: non attribuire esiti non controllati. Le 58 coppie candidate non sono tutte le relazioni implicite nelle card.
