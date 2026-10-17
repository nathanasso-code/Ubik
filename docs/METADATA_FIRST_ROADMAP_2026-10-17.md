# Ubik — Piano operativo metadata-first (17 ottobre 2026)

**Stato: direzione approvata; primo modulo di candidate retrieval implementato, valutazione empirica e integrazione nel feed ancora da eseguire.** Ramo `develop/ubik-core`. Questo documento integra, non cancella, `UBIK_DECISION_RECORD_2026-10-16.md` e `EPISTEMIC_CARDS_AND_NUCLEI.md`.

## Decisione di prodotto

Ubik punta a superare la sola aggregazione di Ground News in **precisione degli accorpamenti, spiegabilità delle differenze, tracciabilità delle evidenze e contributo umano/IA alla conoscenza**. L'audit esplorativo su 20 card Ground News suggerisce che l'aggregazione di titoli/metadati può essere efficace, ma il campione visibile non permette di stimare il tasso di errore sull'intero servizio né di dedurne l'algoritmo interno.

**Card:** stessa notizia/specifico sviluppo con sovrapposizione quasi totale dei fatti centrali, anche quando le fonti differiscono per dettagli, taglio o commento. **Nucleo:** questione circoscritta e persistente con più sviluppi solo parzialmente sovrapposti, raro e utile alla comunità. **Topic:** dominio ampio curato e relativamente raro. **Tag:** metadati ricercabili trasversali. **Fonte autonoma:** valida anche fuori topic o senza card. Le pubblicazioni in syndication non contano come corroborazioni indipendenti.

## Pipeline ordinata per costo e livello di evidenza

| Fase | Input | Elaborazione | Output | Stato |
| --- | --- | --- | --- | --- |
| 0. Ingestione | RSS/API/arXiv/Wikinews/social; URL e provenienza | Normalizzazione, dedup URL, conservazione metadati e link originali | Archivio fonti, anche paywall | Parziale, da consolidare |
| 1. Discovery economica | Titolo, descrizione, data, publisher, URL | Blocking temporale, TF-IDF/embedding, candidati top-k; non forzare topic | Coppie candidate e contesti di revisione | **Modulo nuovo implementato**: `ingestion/metadata_first_candidates.py`; non integrato |
| 2. Identità della notizia | Candidati, metadati, descrizioni; testo quando disponibile | LLM valuta insieme 2+ fonti: evento centrale, data, protagonisti, differenze decisive; split se necessario | Card candidate con motivi e confidenza qualitativa, fonti autonome | Pilot Qwen su 43 fonti; adattamento metadata-first DA FARE |
| 3. Revisione mirata | Solo casi ambigui, card ad alto impatto o ad alto rischio | Acquisizione testi/abstract estesi, confronto fattuale avversariale e citazioni | Conferma/split/relazione, evidenze verificabili | Pilot su 43 fonti, non produzione |
| 4. Organizzazione | Fonti e card | Routing a pochi topic curati, tag consolidati, nuclei solo quando giustificati | Feed generale + topic + nuclei selettivi | Proposte offline: 5 topic, 2 nuclei |
| 5. Sintesi epistemica | Testi disponibili e provenance | Sintesi con riferimenti a fonti/passaggi, differenze, incertezze, contraddizioni | Card consultabile, relazioni fra fonti, audit trail | Da integrare e valutare |
| 6. Pubblicazione e feedback | Candidate verificate e policy editoriali | Controlli, reversibilità split/merge, revisione umana, segnali di qualità e discussione | Feed utilizzabile, senza pubblicazione automatica dei nuclei | Non implementato |

**Separazione cruciale:** raggruppare pubblicazioni ≠ verificarne la verità. I paywall non impediscono necessariamente il clustering su metadati, ma limitano le affermazioni epistemiche e la qualità della sintesi. Non presentare un'assenza di testo come evidenza di conferma.

## Esperimenti effettivi e limiti

- Corpus di discovery: **984 documenti**, embedding multilingue e 100 coppie nuove rispetto alla baseline TF-IDF (run `39016497891`). Non costituisce un gold standard.
- Campione Qwen: **43 fonti / 54 relazioni**; classificazione topic e nuclei: **5 topic / 2 nuclei** (run `39026959251`).
- Controllo Qwen a coppie, con passaggi testuali: **2 card candidate**, 4 fonti coinvolte (run `39033053708`).
- Controllo Qwen multi-fonte con passaggi testuali: **4 card candidate**, **9 fonti**, una card con **3 fonti**; **34 fonti autonome**, 5 topic e 2 nuclei preservati (run `39041792692`). Candidature editoriali, non precisione certificata. Esempi controversi: Albania, Trump/Russia, leap-hour.
- Audit esplorativo Ground News: **20 card**, valutazione di sottoinsiemi pubblicamente visibili: **13 apparentemente coerenti, 6 misti, 1 indeterminato**. Campione intenzionale e non rappresentativo, non misura di accuratezza generale.

## Prossimi step, in ordine operativo

1. **Benchmark riproducibile sul corpus ampio**: usare il nuovo modulo su JSON `{items:[...]}` da 984 fonti; conservare ID, URL, titoli, descrizioni, date, publisher; registrare recall candidate e percentuale fonti non accorpate. Eseguire workflow dedicato, pubblicare artifact; non confondere contesti con card.
2. **Revisione metadata-first a gruppi**: inviare a Qwen i contesti candidati in finestre limitate; non affidare il merge finale alla transitività dei grafi; richiedere esplicitamente separazione di sviluppi collegati. Usare testi solo nei casi ambigui o per sintesi con evidenze.
3. **Campione gold standard cieco**: almeno 100 coppie difficili e 30 gruppi, etichettati con categorie SAME_EVENT / RELATED_DISTINCT / TOPIC_ONLY / INSUFFICIENT; includere date e fonti di editori differenti; misurare false fusioni, mancate fusioni, qualità dei gruppi 3+, costo e latenza.
4. **Routing topic e nuclei dopo le card**: pochi topic, nuclei rari; nessuna proliferazione automatica; preservare ogni fonte fuori topic nel feed generale.
5. **Confronto di modelli**: Qwen baseline; modelli più capaci solo sui casi incerti o ad alto impatto, dopo misurazione dei costi. Un modello più caro può essere più economico nel risultato finale se riduce iterazioni e errori: ipotesi da testare, non scelta già compiuta.
6. **Integrazione nel prodotto**: versionamento decisioni e spiegazioni, archiviazione link originali, UI con card/fonti/differenze e reversibilità; niente pubblicazione automatica basata sui soli score.

## Vincoli di qualità e spesa

- Priorità: **precisione della stessa notizia**, non massimizzazione del numero di card. Una fonte non accorpata è preferibile a una fusione errata.
- La selezione deve restare spiegabile: quale evento condiviso, quali differenze, quali passaggi sostengono la sintesi, quali fonti sono indipendenti.
- Per i modelli a pagamento fissare limite per run, campionamento, cache e arresto controllato; non chiamare modelli costosi su tutte le coppie del corpus.
- Separare `candidate_retrieval`, `semantic_event_identity`, `evidence_grounding`, `editorial_review` nei log e nelle metriche.
- **Non dichiarare implementato ciò che è soltanto pianificato.**
