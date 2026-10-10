# Ubik — estensione verifica fonti e canali (2026-10-11)

## Perimetro del lavoro

Continuazione dei punti 1–3 della verifica delle fonti. Nessuna attivazione di produzione, scheduling permanente, credenziali, migrazione PostgreSQL o selezione di articoli per card/nuclei.

## Inventario espanso

`ingestion/cross_topic_inventory.py` aggrega **32** voci del registro pilota `ai-models` e **12** candidati italiani da `config/italian-cross-disciplinary-candidates.json`: **44 voci catalogate**, non necessariamente 44 editori indipendenti. Tutti i 12 candidati italiani restano **disabilitati**. Il report non pretende di rappresentare l'intero universo di testate e autori concordati. `ingestion/channel_readiness.py` distingue l'esistenza di un adapter da un test live e da una copertura continua; include esplicitamente i canali non rappresentati (Reddit, YouTube, transcript, stream Bluesky, Mastodon globale, sitemaps e registro testate generaliste).

## Diagnosi dei cinque feed problematici

`ingestion/feed_triage.py` assegna un problema e un prossimo controllo a ogni feed con errore o upstream vuoto. Dalle verifiche RSS reali del 10 ottobre 2026:

| Fonte | Osservazione reale | Prossima verifica |
| --- | --- | --- |
| The Batch | HTTP 403 | Consultare policy e endpoint pubblici ufficiali, senza bypass |
| Jack Clark / Import AI | HTTP 403 | Come sopra |
| Economics of AI | HTTP 403 | Come sopra |
| Frankly the Counterfactual | HTTP 403 | Come sopra |
| Dan Luu | Feed oltre il limite di 3 MB | Valutare parser incrementale con limite totale e sicurezza invariati |
| arXiv cs.AI e cs.CL | 0 elementi grezzi, 0 normalizzati | Controllare endpoint, pubblicazione e feed alternativo ufficiale |

**Nessuno di questi problemi è stato ancora risolto.** Non confondere la diagnosi automatica con la riparazione o la prova di una sorgente alternativa. Le richieste 403 non devono essere aggirate.

## Metriche senza selezione

`ingestion/source_quality.py` produce distribuzioni per fonte di freschezza (RSS RFC 2822 e ISO 8601), identificatori duplicati, identificatori mancanti e dati autore mancanti; **recall globale e per fonte sono null** perché non conosciamo l'universo atteso. Il tempo dalla pubblicazione non è automaticamente la latenza d'ingestione: servono timestamp di acquisizione confrontabili.

## Utilizzo e verifiche

```sh
python -m unittest discover -s tests
python -m ingestion.coverage_cli --output data/discovery/source-inventory-quality.json
python -m ingestion.coverage_cli --discovery data/discovery/ai-models.json --federated data/discovery/unselected-rss-federated.json --output data/discovery/source-inventory-quality.json
```

La pipeline `.github/workflows/ai-discovery-pilot.yml` raccoglie realmente i 24 feed RSS configurati in risposta a modifiche esplicite, conserva osservazioni federate e report di copertura in un artefatto temporaneo. Le esecuzioni del 10 ottobre hanno restituito 19 feed riusciti, 5 falliti e 2.638 osservazioni normalizzate. Non esiste un job di raccolta ricorrente avviato da questa modifica.

## Stato dei canali aggiuntivi

- **Hacker News**: script e test offline esistono, ma nessuna nuova prova live documentata in questa fase.
- **GDELT**: adapter a query limitate, non un flusso completo; nessuna nuova prova live documentata.
- **Bluesky**: una prova reale precedente su un singolo autore; non rappresenta la rete.
- **Mastodon**: HTTP 422 nella prova precedente; causa irrisolta, nessuna elusione dei limiti.
- **OpenAlex e Crossref**: prove reali precedenti riuscite su finestre ridotte; non rappresentano l'intero archivio scientifico.
- **Reddit, YouTube e trascrizioni**: non implementati come flussi di acquisizione equivalenti; prima servono verifica delle API, licenze e condizioni d'uso.

## Passi successivi non ancora completati

1. Inventario documentato di testate generaliste e feed diretti per argomenti-matrice, con verifiche HTTP e diritti d'uso.
2. Verifica mirata di endpoint RSS alternativi ufficiali per i 403, senza bypass.
3. Esperimenti live limitati per HN/GDELT e successivamente social/scienza, con log e artefatti temporanei, senza retention indebita.
4. Report per finestre temporali ripetute, con timestamp acquisizione, costo e copertura relativa per singola fonte.
5. **Fase editoriale 4 rinviata**: nessun ranking o clustering attivato.
