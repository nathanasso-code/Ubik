# Ubik — Politica di adeguatezza dell'evidenza e relazioni documentali
Data: 13 ottobre 2026. Ramo di sviluppo: `develop/ubik-core`.

## Principio
Ubik valuta la **densità e la specificità dell'informazione**, non la lunghezza del documento. Testi integrali, estratti sostanziali, abstract scientifici e descrizioni editoriali entrano in un'unica analisi con **provenienza e grado di completezza espliciti**. Una descrizione RSS non viene automaticamente trattata come abstract scientifico.

## Livelli di adeguatezza
- **A — evidenza sostanziale:** il passaggio contiene almeno due frasi sufficientemente articolate, un risultato riconoscibile e un riferimento metodologico o quantitativo; candidato a estrazione di affermazioni, con revisione.
- **B — evidenza parziale:** contesto e segnali informativi presenti ma insufficienti per il confronto specifico; categorizzazione e ricerca di relazioni solo preliminari.
- **C — insufficiente:** titolo, teaser, rumore o testo povero; indicizzazione senza inferenze fattuali.
- Il livello **non misura la veridicità** della fonte. Le euristiche attuali IT/EN sono un prototipo, con possibili falsi positivi e negativi; richiedono un dataset annotato e metriche di precisione/recall.

## Moduli implementati
1. `ingestion/abstract_evidence_adequacy.py`: valuta tutti i documenti del nuovo snapshot RSS+API, restituisce A/B/C, indicatori di metodo/risultato/numeri/incertezza, brevi passaggi candidati (massimo 160 caratteri) con URL. **Non è ancora un estrattore semantico LLM né un verificatore fattuale.**
2. `ingestion/cross_source_evidence_review.py`: confronta brevi passaggi da fonti diverse e propone tre etichette **solo per revisione**: `possible_redundancy_review`, `possible_polarity_difference_review`, `related_claims_review`. Si astiene se la sovrapposizione è insufficiente. Una differenza di negazione non prova una contraddizione.
3. `ingestion/public_text_transient_analysis.py`: lettura in memoria di pagine accessibili nel rispetto di robots, senza conservare il corpo protetto; attualmente genera frequenze lessicali e misure, **non** affermazioni strutturate. Questo è un debito tecnico prioritario.
4. `ingestion/europe_pmc_licensed_texts.py`: testi scientifici XML conservati per verifica delle licenze; il testo scientifico non è ancora collegato all'estrazione delle affermazioni.
5. `.github/workflows/global-discovery-pilot.yml`: esegue automaticamente test, adeguatezza degli abstract, confronto interfonte, raccolta globale e revisione semantica. Gli artefatti sono conservati 14 giorni; il registro persistente dipende dalla cache GitHub Actions e richiede storage durevole.

## Risultati empirici e limiti
- Esecuzione **38379718302** (precedente): 1.673 URL distinti nel corpus, 150 tentativi GET, 108 pagine analizzate in memoria, 105 con almeno 1.200 caratteri. Non sono 108 articoli di cui sia verificata la completezza.
- Esecuzione **38465549058**: **fallita** nel test `test_informative_abstract` (livello B invece di A). Nessun nuovo conteggio A/B/C affidabile da quella esecuzione. Soglia corretta in commit `f01a0aea`; verificare la nuova CI prima di considerarla risolta.
- Nuovi conteggi A/B/C e relazioni interfonte: **non ancora verificati**; dipendono dagli artefatti della nuova esecuzione.
- arXiv: endpoint/API e RSS hanno precedentemente prodotto zero risultati. Richiede diagnosi del codice HTTP, contenuto della risposta e fallback, non una dichiarazione di accesso riuscito.

## Prossimi passi obbligatori
1. Verificare CI, artefatti A/B/C e relazioni, controllare precisione su campione annotato; **non** interpretare conteggi euristici come affermazioni corrette.
2. Estrarre e confrontare affermazioni dai **corpi di testo effettivamente letti**, in memoria, conservando solo evidenze/relazioni compatibili con i diritti; integrare anche gli XML Europe PMC.
3. Identificare stesso evento solo dopo controllo di entità, data, luogo, tesi e contesto; distinguere convergenza da ripetizione della stessa agenzia.
4. Categorizzare con classificazione multilabel e categorie emergenti; pubblicazione sempre distinta da proposte non validate.
5. Migliorare API arXiv, provider social/GNews, logging dei fallimenti e monitoraggio obbligatorio di ogni canale.

## Contratto di trasparenza
Distinguere sempre **configurato**, **interrogato**, **documenti restituiti**, **testo letto**, **testo sostanziale**, **affermazioni candidate**, **affermazioni verificate**, **relazioni candidate**, **relazioni validate**. Mai sommare metriche di fasi diverse.

## Rappresentazione delle affermazioni v1 (implementata successivamente)
Il modulo `ingestion/claim_representation.py` costruisce candidati strutturati dai passaggi A degli abstract: ID stabile, URL, fonte, tipo di evidenza, posizione della frase, hash, breve estratto, predicato lessicale candidato, quantità non ancora associate a una misura, indicatori di negazione e incertezza. I campi `subject`, `object`, `population`, `timeframe`, `location` e `study_id` restano esplicitamente `null` finché non sono inferiti e verificati con strumenti più adatti. Il modulo si astiene su frasi senza relazione riconoscibile. La CI salva `structured-claim-candidates.json` e registra separatamente candidati e affermazioni verificate (inizialmente zero). Questo **non** costituisce ancora estrazione fattuale completa né verifica di contraddizioni.

## Audit sperimentale aggiunto
- `ingestion/claim_pair_benchmark.py`: tre casi sintetici di regressione; la corrispondenza con etichette attese **non** è una misura di precisione su notizie reali.
- `ingestion/claim_relation_audit.py`: conteggia le proposte di relazione tra documenti reali, URL distinti e tipologie; registra esplicitamente zero supporti/contraddizioni verificati.
- Artefatti CI: `synthetic-claim-relation-benchmark.json` e `real-claim-relation-audit.json`.
- Riferimento esterno per la successiva valutazione supervisionata: SciFact (Allen Institute for AI), con etichette SUPPORT/CONTRADICT e frasi-evidenza negli abstract: https://github.com/allenai/scifact/blob/master/doc/data.md . L'integrazione con SciFact e la valutazione su etichette indipendenti **non sono ancora implementate**.

## Valutazione gold SciFact (13 ottobre 2026)
`ingestion/scifact_gold_baseline.py` scarica l'archivio pubblico SciFact, carica **solo** lo split development annotato e il corpus, e confronta una baseline lessicale con gli indici di frase gold. Registra hit/recall@1 e @3 di evidenze **condizionate alla conoscenza del documento gold** (oracle document retrieval). Questa misura non valuta l'individuazione del documento corretto, né l'inferenza SUPPORT/CONTRADICT. Il verificatore che si astiene sempre ottiene zero recall positivo; non si attribuisce una precisione indefinita. Il job è `continue-on-error` perché la dipendenza esterna può essere indisponibile: controllare che `scifact-dev-baseline.json` sia realmente presente nell'artefatto prima di citare valori. Nessun risultato numerico è dichiarato finché la CI non termina.

## Confronto semantico controllato
`ingestion/scifact_semantic_comparison.py` valuta sul medesimo SciFact dev e sulle medesime frasi-evidenza due ranking: Jaccard lessicale e cosine similarity su embedding normalizzati del modello `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Registra hit/recall@1 e @3. L'esperimento conosce a priori il documento corretto, non classifica SUPPORT/CONTRADICT, e non prova affidabilità su notizie reali. Il job è non bloccante in caso di indisponibilità della rete/modello; verificare l'artefatto `scifact-semantic-comparison.json` prima di dichiarare risultati.

## Decisione di prodotto: priorità informativa (14 ottobre 2026)

**PRIORITÀ ATTIVA — Organizzazione informativa.** Acquisire documenti con provenienza, attribuire categorie gerarchiche (generali e specifiche), identificare concetti e conclusioni rilevanti, proporre relazioni tra documenti, distinguendo stesso tema, stesso evento/studio e contributi complementari. Costruire sintesi fedeli e collegate alle fonti. Non accorpare automaticamente in base alla sola cosine similarity; richiedere un controllo di identità dell'evento/studio e una valutazione editoriale.

**IN STANDBY — Grafo e confronto delle evidenze.** La rappresentazione di singole affermazioni, supporti, contraddizioni e livelli di consenso rimane una possibile fase successiva, non un prerequisito del motore informativo. Mantenere gli esperimenti esistenti riproducibili, senza dedicarvi nuove priorità di sviluppo finché categorizzazione, accorpamento e sintesi non saranno valutati empiricamente. Nessuna pretesa di verificare autonomamente la verità.

### Primo pilota gerarchico/embedding
Il run GitHub Actions 38473835541 ha elaborato 400 documenti, valutato 17 percorsi tassonomici e restituito 100 coppie candidate (limite configurato, non numero di accorpamenti corretti). La revisione dei risultati evidenzia errori macroscopici di tassonomia: diversi articoli sulla sentenza nel caso Tupac Shakur sono classificati «technology > computing > cybersecurity». I collegamenti fra titoli relativi allo stesso fatto appaiono promettenti, ma non sono ancora stati misurati precision, recall o accuratezza delle categorie. Perciò non pubblicare categorie o merge come verificati. Prima di qualsiasi sintesi, verificare anche la provenienza e la disponibilità del testo originale.

### Iterazione tassonomia e astensione
Il pilota ora include una branca cronaca/giustizia (processi penali, tribunali, indagini), affari internazionali e sport, prima assenti. Una categoria può essere proposta soltanto se la somiglianza supera 0,70 e il distacco dalla seconda scelta è almeno 0,015; in caso contrario il sistema si astiene. Queste soglie sono **provvisorie e non calibrate**, e i risultati sono proposte da revisionare, non etichette convalidate. Prossimi passi: annotazione manuale stratificata e misura degli errori, poi distinzione esplicita tra affinità tematica e identità di evento/studio. Le 100 coppie del pilota precedente erano un limite di output, non una misura di precisione.

## Pilota ibrido per categorizzazione e accorpamento (14 ottobre 2026)

**Implementato:** ampliamento tassonomia con cronaca giudiziaria, esteri e sport; astensione in caso di bassa similarità o margine ambiguo. Il modulo `ingestion/semantic_topic_neighbor_pilot.py` preserva ora anche la data di pubblicazione, quando disponibile. Il modulo `ingestion/hybrid_event_review.py` usa le stesse coppie candidate del ranking embedding e aggiunge confronto lessicale dei titoli, sovrapposizione euristica di espressioni con iniziali maiuscole e distanza temporale. Restituisce `same_event_review_candidate` oppure `related_topic_or_unresolved`. Non modifica gruppi pubblicati, non verifica eventi, non produce sintesi.

**Limiti metodologici:** le prime 100 coppie semantiche costituiscono un campione troncato, non un benchmark completo; le entità ricavate dalle maiuscole non sono NER; gli articoli in lingue differenti possono non condividere token; le date possono mancare; le soglie non sono calibrate. La similarità ibrida è un punteggio di ordinamento, non una probabilità. Per la categorizzazione, un punteggio elevato in una tassonomia incompleta non garantisce la pertinenza. Per l'accorpamento, manca ancora la prova di identità dell'evento e la gestione degli aggiornamenti temporali.

**Valutazione obbligatoria prima della produzione:** campione stratificato di categorie con gold label indipendenti, macro-F1 per livello, coverage/accuracy su casi non astenuti e matrice di confusione; per gli accorpamenti, annotazioni indipendenti di `same_event`, `related_event`, `same_topic_only`, `unrelated`, con precision@K, recall e analisi degli errori fra embedding puro e punteggio ibrido. Confrontare anche casi multilingue e hard negatives (stesso soggetto, evento diverso). Nessun risultato numerico di miglioramento va dichiarato prima di un run e di annotazioni gold.

**Riferimenti metodologici:** Saravanakumar et al., EACL 2021, https://aclanthology.org/2021.eacl-main.198/ (rappresentazioni sparse e dense con entità); Jiang et al., LREC-COLING 2024, https://aclanthology.org/2024.lrec-main.1416/ (embedding sensibili al tempo).

## Dalla relazione fra fonti alle anteprime estrattive

Run 38475814894: 400 documenti classificati, **347 astensioni (86,75%)**, 53 proposte (13,25%). Questo dimostra una copertura troppo bassa con le soglie attuali, non una precisione alta: non esistono gold label per confermarla. Priorità successiva: separare l'assegnazione macro-categoria da quella fine e calibrare soglie per livello su campione annotato, evitando l'abbassamento arbitrario di soglie.

Aggiunto `ingestion/grounded_extractive_briefs.py`: per le sole coppie proposte come stesso evento dal pilota ibrido seleziona frasi già presenti nelle descrizioni dei feed, mantenendo URL e identificativo della fonte. Elimina estratti quasi duplicati e segnala che identità dell'evento e testo completo non sono verificati. Output `data/discovery/grounded-extractive-briefs.json`, artefatto CI di sola revisione. Non è una sintesi generativa, non si pubblica automaticamente e gli estratti vanno sottoposti a verifica dei diritti di riuso prima di un'eventuale visualizzazione pubblica. Passaggio successivo: selezione di passaggi su testi autorizzati, identificazione di informazioni complementari, sintesi generativa con citazioni e controllo della fedeltà.

## Iterazione sperimentale: separazione macro/fine e campionamento gold

Nel run 38476550232 (job discover concluso con successo) il pilota ha prodotto 400 documenti, 29 percorsi tassonomici, **345 astensioni a livello fine**; sulle 100 coppie semanticamente più vicine, l'euristica ibrida ha segnalato **32 same_event_review_candidate** e **68 related_topic_or_unresolved**. Queste sono uscite del modello, non precisione né recall.

Correzione: `semantic_topic_neighbor_pilot.py` ora emette indipendentemente `macro_category_candidate`, punteggio e margine macro; la mancata scelta della sottocategoria non obbliga più a perdere la proposta generale. Rimane necessaria una verifica delle soglie su dati etichettati.

Aggiunto `ingestion/information_review_sample.py` per campionare in modo deterministico categorie proposte/astenute e coppie same-event/unresolved, con campi gold inizialmente null. Le etichette delle coppie sono `same_event`, `related_event`, `same_topic_only`, `unrelated`. Non confondere accuratezza su campione stratificato con accuratezza del corpus; occorre pesare gli strati e includere negativi difficili. La revisione umana precede qualsiasi affermazione di accuratezza o attivazione di merge automatici.

## Valutazione con etichette editoriali

Aggiunto `ingestion/evaluate_information_review.py`, integrato nel workflow discovery. Legge `information-review-sample.json` e restituisce `information-review-evaluation.json` con copertura delle annotazioni, precision/recall per i candidati stesso evento e accuratezza macro/fine sui casi etichettati. **Se le etichette gold non esistono, le metriche restano null**; il programma non trasforma previsioni in verità di riferimento. I risultati su campione stratificato non rappresentano automaticamente la popolazione, e il recall esclude coppie non proposte fuori campione. La valutazione va estesa a negativi difficili e coppie fuori dal top-100 per misurare il recupero.

## Decisione architetturale: due percorsi complementari (14 ottobre 2026)

Il confronto delle evidenze esce dallo standby come **analisi semantica delle affermazioni**, senza diventare un servizio di certificazione della verità. L'organizzazione informativa resta obiettivo prioritario; categorizzazione, identità di evento e relazioni tra affermazioni sono tre proiezioni dello stesso documento, con criteri distinti.

Pipeline proposta: (1) normalizzazione e provenienza del documento; (2) recupero candidati con embedding e ricerca lessicale; (3) estrazione di eventi, attori, date, luoghi e proposizioni attribuite alla fonte, con ancoraggio al passaggio testuale; (4) confronto fra proposizioni: equivalenti, compatibili/complementari, in tensione, contraddittorie, non confrontabili, con possibilità di astensione; (5) classificazione gerarchica tramite tema, evento e proposizioni; (6) formazione gruppi evitando la chiusura transitiva indiscriminata; (7) sintesi che esplicita convergenze e divergenze e cita le fonti.

Distinzioni indispensabili: **stesso tema != stesso evento != stessa affermazione**; due fonti possono trattare il medesimo evento e trarre conclusioni differenti; una contraddizione apparente può dipendere da periodo, popolazione, misura o modalità diversa. Un punteggio embedding non è una probabilità di entailment, né una verifica di verità.

Modello dati sperimentale: `document` (URL, fonte, lingua, timestamp), `event_candidate` (attori, azione, oggetto, tempo, luogo), `statement` (testo originale, span e URL, soggetto, predicato, oggetto, qualificatori, attribuzione), `relation` (tipo, evidenza, modello, stato di revisione), `topic_path` (livello, confidenza, astensione). Ogni relazione mantiene gli ID delle fonti e può essere rivista. Il grafo è una vista di queste strutture, non una fonte autonoma di fatti.

Sequenza empirica: annotare un campione del corpus reale con etichette evento e proposizione; confrontare baseline embedding, ibrido lessicale/temporale e confronto di proposizioni sugli stessi esempi; misurare precision/recall evento, classificazione per livello, qualità del riconoscimento delle divergenze e fedeltà delle sintesi. Integrare testi completi solo quando acquisiti legittimamente e non pubblicare estratti protetti senza autorizzazione. Non dichiarare miglioramenti finché le metriche non sono misurate.
