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
