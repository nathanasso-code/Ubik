# Ubik — dossier di continuità GitHub e verifica delle fonti
_Data: 10 ottobre 2026 · Ramo: `develop/ubik-core` · Nessuna modifica autorizzata a `main`_

## 0. Sintesi e criterio di lettura

Questo documento ricostruisce i **filoni di sviluppo verificabili nei commit del repository**, non la trascrizione letterale delle conversazioni. I commit sono raggruppati per funzione anziché ripetuti uno per uno. La storia Git consultata include almeno tre pagine di commit del ramo; i riferimenti ai test live derivano dai rapporti conservati in `docs/INGESTION_LIVE_VERIFICATION_2026-10-10.md`. **Implementato**, **testato offline**, **provato con API reali** e **pronto per produzione** sono quattro affermazioni differenti.

L'architettura di prodotto da preservare è **argomenti-matrice → nuvola di tag → fonti, card e, quando giustificati, nuclei**. La raccolta è indipendente dalla successiva selezione: non filtrare anticipatamente le notizie in funzione delle card o dei nuclei. Conservare osservazioni originali e provenienza, compresi i singleton. La selezione editoriale (fase 4) resta fuori dall'attuale ciclo di verifica.

## 1. Sviluppo precedente e fondamenta del repository

- **Interfaccia e modello informativo**: `index.html`, `assets/`, `docs/CORE_ARCHITECTURE.md`, `docs/EPISTEMIC_CARDS_AND_NUCLEI.md`, `docs/KNOWLEDGE_PIPELINE.md`. La pagina esiste; l'esistenza dell'interfaccia non prova che il flusso di acquisizione sia collegato alla pubblicazione.
- **Dati strutturati, provenienza, mappa e viste**: `api/`, `data/`, `scripts/`, `supabase/`; contratti, importazioni, tracciabilità e test JS. Il percorso UCDP/ACLED e la mappa sono distinti dall'esperimento sulle fonti giornalistiche e scientifiche.
- **Diversificazione del catalogo**: `config/source-registry.ai-models.json`, `config/rss-atlas-discovery.ai-models.json`, `config/italian-cross-disciplinary-candidates.json`. RSS di laboratori, ricercatori, newsletter e fonti interdisciplinari; candidati italiani; esplorazione multilingue. Una voce nel registro non equivale a feed funzionante.
- **RSS/Atom**: `scripts/discover_ai_sources.py` legge feed configurati, normalizza URL, preserva osservazioni per fonte, titolo, data, descrizione e attribuzione. Distingue autore dichiarato nel feed, editore e attribuzione non verificata. Conserva i report di errore per fonte; una raccolta storica accumulata non misura il rendimento dell'ultima esecuzione.
- **Ricerca di feed e autori**: `scripts/discover_candidate_feeds.py`, `scripts/discover_ai_authors.py`, `scripts/discover_social_authors.py`, audit attribuzione e recupero metadati. Autodiscovery e candidature sono **code di revisione**, non iscrizioni automatiche a tutte le fonti.
- **Diagnostica**: `scripts/diagnose_source_coverage.py`, `scripts/report_ai_discovery.py`, `scripts/review_ai_relevance.py`. Copertura, firme editoriali, descrizioni e candidati pertinenti, senza promuovere automaticamente i contenuti.

## 2. Epistemologia, card, nuclei e valutazione

- **Pilot deterministico**: card epistemiche e nuclei su fixture offline; `docs/EPISTEMIC_CARDS_AND_NUCLEI.md`, `scripts/` e `tests/`. Un nucleo non coincide con il mero gruppo di articoli sullo stesso argomento.
- **Coppie di articoli e clustering prudente**: proposte di coppie simili, valutazione di falsi accorpamenti e mancati accorpamenti, astensione quando le evidenze sono insufficienti. `scripts/mine_epistemic_pairs.py`, `scripts/build_epistemic_review_queue.py`, `scripts/evaluate_verified_event_pairs.py`.
- **Eventi verificati e controesempi**: esempi con provenienza, identificatori stabili, vincoli temporali e identità del prodotto, controllo dei casi negativi. `scripts/build_event_anchor_review.py`, `scripts/audit_event_reference.py`, `docs/EPISTEMIC_LABELING_PROTOCOL.md`.
- **Dipendenza delle fonti**: `scripts/infer_source_dependencies.py`, `docs/SOURCE_DIVERSITY.md`, `docs/FEED_CLUSTER_CORROBORATION.md`. Una URL condivisa o molte ripubblicazioni non dimostrano conferme indipendenti. **Questo filone non deve diventare un filtro in ingresso**.

## 3. Modulo indipendente di acquisizione

- **Confine di dipendenza**: `ingestion/contracts.py` e `ingestion/README.md`. Il motore acquisisce osservazioni e provenienza senza importare ranking, UI o algoritmi di clustering.
- **Adattatori**: RSS e Hacker News legacy (`ingestion/legacy_adapters.py`, `scripts/discover_hacker_news.py`), GDELT DOC (`ingestion/gdelt_doc.py`), Bluesky, Mastodon, OpenAlex, Crossref (`ingestion/public_adapters.py`). GDELT è ricerca limitata a query, Bluesky un feed di autore, Mastodon una timeline locale di istanza; nessuno è automaticamente una raccolta universale.
- **Trasporto**: `ingestion/transport.py`, retry e backoff limitati, payload limitati, controllo degli URL di istanze Mastodon e vincoli di richieste. Le protezioni SSRF e le policy delle piattaforme richiedono ulteriore revisione prima della produzione.
- **Federazione**: `ingestion/federate.py`, `scripts/merge_discovery_observations.py`. Accorpa osservazioni eterogenee senza cancellare la provenienza o confondere identità dei documenti e corroborazione.
- **Budget e piano**: `ingestion/budgets.py`, `ingestion/experiment_plan.py`, `ingestion/experiment.py`, `config/ingestion-experiment.example.json`. Validazione offline, budget di pagine, `--live` esplicito, isolamento dei guasti per fonte. Il piano di esempio copre **quattro sorgenti**, non tutto il catalogo.

## 4. Persistenza, integrità e ripresa

- **Archivi locali immutabili**: `ingestion/archive.py`, SHA-256, snapshot append-only. `ingestion/checkpoints.py` usa checkpoint atomici collegati all'archivio e verifica la corrispondenza prima della ripresa.
- **Paginazione**: `ingestion/run_batch.py`, raccolta limitata e riprendibile per fonte. Cursori anche su pagine vuote dopo normalizzazione; arresto su cursore ripetuto. Correzione successiva: una pagina Crossref corta **dopo normalizzazione** non prova la fine dei risultati upstream.
- **Concorrenza locale**: `ingestion/locks.py`, lock POSIX per fonte; protegge i worker cooperanti sullo stesso filesystem, non più macchine indipendenti.
- **Audit e duplicati**: `ingestion/audit.py`, `ingestion/audit_archive.py`, `ingestion/duplicates.py`. Conteggi, freschezza, sovrapposizioni, identità ripetute, alterazioni dei file. Nessuna deduplicazione distruttiva.
- **SQLite**: `ingestion/sqlite_ledger.py`, `ingestion/sqlite_store.py`, `ingestion/storage_contract.py`. Pagine e cursori atomici, lease con epoca crescente, adapter opzionale per runner ed esperimenti, ripresa fra connessioni. Audit `ingestion/audit_sqlite.py` e CLI read-only. `ingestion/payload_codec.py` unifica il JSON canonico e SHA-256 fra file e SQLite. La modalità SQLite non è un deployment Supabase.
- **Test**: suite Python e JS in `tests/` e GitHub Actions; copertura di collisioni di lease, ripresa, rollback, integrità e comportamento del cursore. Un CI verde attesta i test eseguiti, non completezza o disponibilità continuativa delle fonti.

## 5. Prove reali già eseguite

Rapporto: `docs/INGESTION_LIVE_VERIFICATION_2026-10-10.md`.

| Fonte | Esito di un singolo smoke test | Osservazioni |
| --- | --- | ---: |
| Crossref | API reale riuscita | 4 |
| OpenAlex | API reale riuscita | 5 |
| Bluesky (account `bsky.app`) | API reale riuscita | 3 |
| Mastodon (`mastodon.social`) | HTTP 422, causa sconosciuta | 0 |

Totale **12 osservazioni riuscite**, in campioni piccoli e non rappresentativi. Run: [scholarly](https://github.com/nathanasso-code/Ubik/actions/runs/38087169646), [social](https://github.com/nathanasso-code/Ubik/actions/runs/38087200025). Ulteriore [prova Crossref di ripresa](https://github.com/nathanasso-code/Ubik/actions/runs/38087520133): due snapshot e tre osservazioni attraverso due invocazioni successive. I workflow temporanei sono stati rimossi dopo l'uso. **Non** dimostrano raccolta continuativa, copertura completa, assenza di dati mancanti o disponibilità Mastodon.

## 6. Preparazione infrastrutturale, non produzione

- `ingestion/postgres/schema.sql` e `transaction_templates.sql`: schema isolato e modelli di transazione con fencing; **non sono migrazioni applicate**. Un tentativo successivo di scrivere un adapter PostgreSQL non è andato a buon fine; non dichiararlo implementato.
- `ingestion/social_lifecycle.py`: decisioni offline su età, revisione e potenziali cancellazioni; non elimina dati né verifica autonomamente i segnali di rimozione.
- `ingestion/readiness.py` e `docs/INGESTION_PRODUCTION_READINESS.md`: readiness esplicitamente negativa finché mancano PostgreSQL testato, lease distribuiti, gestione cancellazioni e approvazioni.
- Nessuna attivazione di scheduler permanenti, credenziali, modifiche a `main` o migrazioni di produzione.

## 7. Nuova fase: verifica delle fonti, senza selezione editoriale

**Punto 1 — Inventario**: `ingestion/source_inventory.py` produce un catalogo offline delle voci del registro pilota e degli adattatori, distinguendo feed abilitati, candidati disabilitati, implementazioni presenti ed evidenza live documentata. **Il registro `ai-models` non è necessariamente l'elenco esaustivo di tutte le fonti concordate nelle conversazioni.** Non confondere il catalogo con la copertura globale di Ubik.

**Punto 2 — Prove di acquisizione**: mantenere separati i test deterministici con fetcher fittizi dalle verifiche HTTP reali. I test live documentati sono solo quelli del paragrafo 5; il nuovo inventario non contatta alcuna fonte. Le fonti RSS vanno verificate singolarmente in una successiva esecuzione controllata, conservando il report per ogni URL, inclusi gli errori. Un HTTP 422 non è uno zero editoriale.

**Punto 3 — Qualità**: `ingestion/coverage_report.py` e `ingestion/coverage_cli.py` misurano, da dati già acquisiti, esiti per feed, volumi, date mancanti, freschezza, identità ripetute e differenza tra `seen` della singola chiamata e `stored` cumulativo. Nessun giudizio su verità o qualità editoriale; nessuna selezione delle card.

Comando di audit senza rete:

```sh
python -m ingestion.coverage_cli --output data/discovery/source-coverage-report.json
```

Se sono disponibili i dati delle precedenti acquisizioni, usare anche `--discovery <rss.json> --federated <federated.json>`. Senza questi file, il report deve dire **non testato**, non inventare conteggi o successi.

## 8. Rischi, limiti e prossima evidenza richiesta

1. Verificare l'inventario complessivo di RSS, testate, autori, forum, social, ricerca e video; alcune voci sono soltanto candidate e non tutte sono registrate nello stesso file.
2. Eseguire un test reale **per ciascun feed abilitato**, con data, codice/esito, conteggio di voci grezze e normalizzate, identificatore del run e budget esplicito. Conservare artefatti e statistiche, senza escludere preventivamente fonti per pertinenza.
3. Diagnosticare Mastodon 422 senza eludere limiti di accesso; verificare anche gli altri connettori nel loro reale ambito di copertura.
4. Misurare giornalmente freschezza, ritardi, errori, duplicazioni, lingue e lacune di provenienza; confrontare gli intervalli con la cadenza di aggiornamento dei feed, senza stimare un recall globale quando l'universo delle pubblicazioni è ignoto.
5. **Non avviare la fase 4**: assegnazione alle fonti esposte, card e nuclei resta una decisione successiva, informata dalle misure e non incorporata nella raccolta.
