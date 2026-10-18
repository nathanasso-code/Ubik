# UBIK — Handoff operativo e benchmark semantico (18 ottobre 2026)

> Stato verificato al momento della redazione. Ramo di lavoro: `develop/ubik-core`; non confondere esperimenti GitHub Actions con pipeline di produzione o deploy Vercel. Questo documento integra, non sostituisce, gli storici in `UBIK_EXPERIMENT_LEDGER.md` e `FROZEN_BENCHMARK_AUDIT_2026-10-17.md`.

## Visione e vincoli
Ubik organizza informazione verificabile: pochi topic-matrice curati, tag semantici, fonti originali con URL/provenienza, card per **medesimo sviluppo informativo specifico**, relazioni fra eventi distinti e nuclei epistemici futuri. Pulse/Press/Insights sospesi. La pipeline di discovery non deve automaticamente creare topic o pubblicare card. Distinguere duplicazione di contenuti, stesso evento, sviluppo successivo, reazione, analisi e semplice somiglianza tematica. Ogni fonte compare al massimo una volta nel raggruppamento finale di un contesto; deduplicare globalmente anche fra contesti prima della pubblicazione.

## Acquisizione, corpus e recupero
- Pilot RSS: run [38962196813](https://github.com/nathanasso-code/Ubik/actions/runs/38962196813): 36 feed, 34 riusciti, 1.165 osservazioni, 1.091 URL distinti, 15 domini. Campionamento stratificato run [38963366209](https://github.com/nathanasso-code/Ubik/actions/runs/38963366209): 90 URL, 72 GET riusciti, nessun testo integrale verificato. Consultare il ledger per classificazioni.
- Corpus RSS congelato successivo: **1.052 osservazioni, 979 URL unici**. TF-IDF metadati: 107 coppie candidate; embedding multilingue aggiunge 195 coppie; unione **302 candidate**, **82 contesti connessi**, 260 fonti collegate e 719 isolate. Run [39075100154](https://github.com/nathanasso-code/Ubik/actions/runs/39075100154), artifact `frozen-neural-expanded-candidates`. Retrieval propone candidati, non card definitive; non abbiamo recall globale verificato.
- Revisione Qwen su metadati: run [39076957811](https://github.com/nathanasso-code/Ubik/actions/runs/39076957811): 20 contesti, 25 card provvisorie; 62 contesti non esaminati. Accordi/disaccordi con Qwen non sono gold standard.
- Acquisizione testi originali: run [39107689997](https://github.com/nathanasso-code/Ubik/actions/runs/39107689997): 97 ID nei 20 contesti, tentati 50, estratti non verificati 41, non disponibili 9, 40 testi >=800 caratteri. Lunghezza non implica testo originale pulito o informativo; nessun bypass di paywall.
- Qwen testi con obbligo di citazioni letterali: run [39109209778](https://github.com/nathanasso-code/Ubik/actions/runs/39109209778): 8 contesti valutabili, 3 card; il validatore letterale ha introdotto un veto molto restrittivo, non interpretabile come misura della qualità del modello.
- Qwen testi **senza** veto letterale: run [39111933850](https://github.com/nathanasso-code/Ubik/actions/runs/39111933850): 8 contesti, 9 card, 12 contesti saltati, 40 testi sostanziali. Nelle 58 coppie candidate comparabili, Qwen metadati accorpa 46, Qwen testi accorpa 46, con 6 divergenze (3 solo metadati e 3 solo testi). Il confronto HTML `ingestion/three_way_comparison_page.py` converte le card in coppie **solo per valutazione**; non confondere le coppie con le card o con tutte le relazioni implicite in un gruppo.

## Revisione editoriale dei soli testi forniti a Qwen
Revisione ragionata su 39 fonti appartenenti agli 8 contesti con testo, basata sugli estratti HTML disponibili; **non è un gold standard esterno certificato**. Giudizio per contesto:
1. Farfalle monarca NPR, 2 fonti: stesso reportage in due trasmissioni, card corretta; non due conferme indipendenti.
2. Deforestazione Amazzonia, 4 fonti: stessi nuovi dati governativi, card corretta.
3. Bollettini Euronews, 4 fonti: tre edizioni del 17 ottobre impropriamente unite; testo estratto è una descrizione generica, non il contenuto dei bollettini.
4. Trump/Russia/Ucraina, 13 fonti: Qwen ha unito 11 fonti su decisione sanzioni, reazioni, presunto cessate il fuoco energetico, summit, interviste, Starlink e editoriale. **Falso accorpamento massivo**: correlazione geopolitica non significa identità dello sviluppo.
5. Selma Blair, 2 fonti: stessa dichiarazione dei rappresentanti, card corretta.
6. Condanna per omicidio surfisti in Messico, 4 fonti: stessa sentenza, card corretta.
7. Guardian podcast/video su sorveglianza IA al lavoro, 2 fonti: stesso contenuto in formati diversi, card corretta.
8. Papa Leone XIV, 8 fonti: separazione corretta fra dimissioni dall'ospedale (6) e prime immagini/Messa durante la convalescenza (2).

Su tutte le combinazioni implicite nei gruppi, una classificazione editoriale preliminare stimava **37 TP, 52 FP, 1 FN**, precisione 41,6% e richiamo 97,4% sulle relazioni positive. Questi numeri non sono confrontabili direttamente con la precedente precisione 76,1% calcolata sulle sole 58 coppie **candidate**: denominatori e universi differenti. Verificare etichette, fonte per fonte, prima di pubblicare una metrica definitiva. La causa principale è la fusione eccessiva del gruppo Ucraina.

## Nuovo esperimento: fingerprint per fonte prima delle card
Codice `ingestion/frozen_text_qwen_review.py` aggiornato per richiedere in due stadi: (1) estrarre indipendentemente per ogni fonte `subject, action, object, event_date, place, result_or_consequence, central_development, information_quality, ambiguity`; (2) confrontare i fatti e accorpare **solo lo stesso sviluppo**, lasciando separati reazioni, interviste, annunci e contesti genericamente simili. Output JSON `source_facts`, `cards`, `related_events`, `uncertainties`. Non richiedere citazioni letterali; non inventare campi mancanti.
- Run [39114071951](https://github.com/nathanasso-code/Ubik/actions/runs/39114071951) **fallito** per SyntaxError introdotto dal codice, senza chiamare Qwen.
- Run [39114277357](https://github.com/nathanasso-code/Ubik/actions/runs/39114277357) **fallito** per un secondo carattere letterale `\\n` nel medesimo blocco.
- Fix completo: commit [d83cc6f](https://github.com/nathanasso-code/Ubik/commit/d83cc6f9e23b462967bfc948565920292375f46b); nuovo run [39114498864](https://github.com/nathanasso-code/Ubik/actions/runs/39114498864). **Verificare conclusione e artifact prima di dichiarare risultati.** CI core ha avuto esito positivo, ma ciò non dimostra l'esecuzione LLM.

## Prossimi passi rigorosi
1. Verificare run 39114498864, log, artifact e presenza di `source_facts`. Se fallisce, correggere il problema reale e aggiungere controllo `python -m py_compile ingestion/frozen_text_qwen_review.py` in CI **prima** delle chiamate API.
2. Riesaminare le card sui medesimi 39 testi, confrontando soprattutto Ucraina, Euronews e Papa; distinguere errore di estrazione dal confronto. Non cambiare campione fra baseline e test.
3. Valutare **card complete e tutte le relazioni implicite**, non soltanto coppie retrieval; usare metriche pairwise e di partizione, includendo falsi accorpamenti e separazioni, con revisione editoriale indipendente e incertezze.
4. Introdurre astensione su testo HTML generico/rumoroso, riconoscimento di contenuti audio/video senza trascrizione e distinzione fra stessa notizia e medesima fonte ripubblicata.
5. Verificare unicità delle fonti fra contesti, URL canonici, assegnazione globale, e rappresentazione UI di card vs relazioni. Conservare fonti isolate.
6. Misurare token, chiamate e **costo per card corretta**. Valutare modello più capace soltanto su casi complessi. Budget orientativo poche decine di euro al mese (~1 €/giorno).
7. Nessuna modifica automatica a `main`, nessun deploy o pubblicazione di contenuti non verificati. Aggiornare questo handoff e il ledger con ogni run completato.

## Punti di ingresso
- [Architettura corrente](ARCHITECTURE_CURRENT.md)
- [Registro esperimenti](UBIK_EXPERIMENT_LEDGER.md)
- [Audit benchmark precedente](FROZEN_BENCHMARK_AUDIT_2026-10-17.md)
- [Workflow nuovo esperimento](../.github/workflows/frozen-text-qwen-three-way.yml)
- [Revisore Qwen](../ingestion/frozen_text_qwen_review.py)
- [Confronto HTML](../ingestion/three_way_comparison_page.py)
