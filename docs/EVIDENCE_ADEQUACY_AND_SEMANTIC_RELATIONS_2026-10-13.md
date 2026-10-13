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
