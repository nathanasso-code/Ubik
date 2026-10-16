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
