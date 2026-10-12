# Ubik — scoperta globale prima dell'assegnazione ai topic (13 ottobre 2026)

## Decisione architetturale

Adottare un **modello ibrido a priorità globale**. L'acquisizione è indipendente dai topic e produce osservazioni immutabili da fonti dirette (RSS, editori, ricerca, bibliografia) e social (come segnale). La scoperta propone documenti, termini ed eventi; **solo in un secondo passaggio** i candidati vengono collegati a uno o più topic. I topic possono chiedere ulteriori approfondimenti motivati da lacune specifiche.

Non interpretare «globale» come «intero web»: il catalogo di fonti determina la copertura; campionamenti, lingua, API, frequenza e filtri delle fonti producono bias osservabili.

## Perché

La ricerca per topic limita il recall di notizie che non menzionano le parole del topic. Espansioni automatiche da hashtag generici possono invece causare drift. La raccolta indipendente dai topic consente di riutilizzare lo stesso documento per più topic e confrontare ciò che emerge senza seed tematici.

## Pipeline target

1. **Acquisizione ampia**: feed e connettori approvati; osservazioni, errori, data/ora, snapshot, fonte e diritti.
2. **Registro documenti**: normalizzazione URL, dedup prudente, genealogia delle segnalazioni, publisher.
3. **Scoperta candidate**: frequenza documentale, copertura editori, variazione temporale, entità e concetti multilingue; conservare esempi e controesempi.
4. **Eventi**: retrieval di coppie candidate e verifica di equivalenza; mai fondere automaticamente sulla sola somiglianza lessicale.
5. **Topic routing**: associazione multi-topic con evidenze e confidence calibrata; categoria non assegnata consentita.
6. **Approfondimento mirato**: query specifiche derivate dai documenti e dalle lacune del topic, tracciate e limitate.
7. **Card e revisione**: sintesi solo da documenti realmente letti; separare fatti, ipotesi, controversie e provenienza.

## Incremento implementato ora

`ingestion/global_discovery.py` accetta snapshot già compatibili con `ingestion/federate.py` e genera termini candidati senza query o filtri per topic. I termini sono estratti dai titoli delle osservazioni; richiedono almeno due documenti e due coppie connector/source osservate. Ogni candidato conserva fino a 15 URL di supporto e conta host distinti. Ripetizioni di un unico URL non bastano a promuovere un termine. **È un prototipo lessicale offline, non NER, non clustering semantico, non ranking editoriale.**

Esempio:
```sh
python -m ingestion.global_discovery data/discovery/ai-models.json data/discovery/hacker-news.json --output global-candidates.json
python -m unittest discover -s tests
```

I file di input sono esempi da verificare nel checkout: non si dichiara un run live né un output globale già acquisito. `tests/test_global_discovery.py` copre la scoperta senza seed e il caso di repost multipli.

## Criteri di accettazione per i prossimi incrementi

- Due finestre temporali successive con acquisizione immutabile, metriche di copertura e crescita di documenti unici.
- Valutazione cieca della pertinenza su topic non usati come seed.
- Misura del recall su eventi documentati a posteriori, **senza usare il caso di controllo nelle query**.
- Precisione degli eventi candidati annotata manualmente, con falsi merge tracciati.
- Misura della deriva e dell'eventuale predominio di pochi editori/lingue.
- Nessuna modifica al feed di produzione finché la pipeline non è verificata e la persistenza non è progettata.

## Confini di sicurezza

Non attivare scraping indiscriminato, bypass di accessi, scheduler non presidiati, credenziali esposte o migrazioni su `main`. Conservare separatamente osservazioni, documenti, eventi, assegnazioni e revisioni. La presenza di un candidato non autorizza una sintesi fattuale.


## Primo pilot live generalista — risultati

Nuovi componenti: `ingestion/global_rss_pilot.py`, `config/source-registry.global-pilot.json`, `tests/test_global_rss_pilot.py`, `.github/workflows/global-discovery-pilot.yml`.

Run di riferimento: https://github.com/nathanasso-code/Ubik/actions/runs/38317573397

**Risultato dei passaggi di acquisizione e analisi nei log:** 10 feed configurati, 9 riusciti, 333 osservazioni, 324 URL distinti; test unitari del workflow superati. Il primo run `38317565952` era fallito per invocazione unittest e la causa è stata corretta nel workflow.

Il catalogo non è ancora bilanciato geograficamente o linguisticamente. Il rapporto osservazioni/URL è diverso da quello dei post social; non comparare i conteggi come se misurassero la stessa cosa. Il ranking dei termini è lessicale: una frequenza alta non identifica automaticamente un evento.

**Prossimo gate:** due snapshot temporali e valutazione della precisione di un campione di candidati; evitare qualsiasi pubblicazione automatica.


## Secondo incremento live: coppie di eventi candidate

Modulo `ingestion/global_event_pairs.py`, test `tests/test_global_event_pairs.py`, workflow `.github/workflows/global-discovery-pilot.yml` aggiornato. Metodo: titoli, weighted Jaccard, almeno due termini condivisi, editori con host differenti, pubblicazione entro 72 ore; nessun merge automatico. È un suggeritore di coppie, non un clustering multilingue o una prova di identità degli eventi.

Run **completato con successo**: https://github.com/nathanasso-code/Ubik/actions/runs/38317808123 — **324 documenti, 4 coppie proposte, 0 fusioni automatiche**. 10 feed configurati, 9 riusciti, 333 osservazioni. I controlli Core checks sul codice correttivo sono riusciti nel run `38317808091`.

La quantità di coppie non è una metrica di qualità: servono annotazioni umane delle 4 coppie, ricerca di coppie vere non rilevate e precision/recall. L'output `global-event-pairs-review.json` è conservato come artifact del run GitHub (scadenza 14 giorni).


## Prime card di scoperta documentale (13 ottobre 2026)

`ingestion/global_cards.py` rende disponibili card non editorializzate da titoli RSS e URL originali. Il risultato è tracciabile e verificabile nei log del run https://github.com/nathanasso-code/Ubik/actions/runs/38318112930 : **24 card (4 coppie di fonti, 20 documenti singoli)**, con `global-cards-preview.json` e `global-cards-preview.md` nell'artifact. Le quattro coppie trattano titoli su Ilhan Omar, RJ Mitte, naufragio presso Gibuti e vicecapo della polizia sudafricana. Tutte restano `unverified`; non sono sintesi fattuali né card pubblicate.

Le card singole sono ordinate per apparizione nel feed, non per importanza. **Non trasformare la dimostrazione in ranking editoriale o prova di indipendenza delle fonti.** Prossimo passaggio: verifica documentale, confronto cross-lingua, valutazione di falsi positivi/negativi, integrazione UI dietro flag di preview.
