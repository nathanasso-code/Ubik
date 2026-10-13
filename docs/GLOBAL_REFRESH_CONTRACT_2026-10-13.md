# Ubik — contratto operativo della ricerca globale

**Aggiornato:** 13 ottobre 2026. **Branch:** `develop/ubik-core`.

## Comando operativo

GitHub Actions → `Global topic-agnostic discovery pilot` → `Run workflow` sul ramo `develop/ubik-core`.

La pipeline esegue RSS, ricerca dei termini senza topic seed, scoperta social, deduplicazione RSS/social, GET di accessibilità, registro persistente, verifica input semantici, coda diritti e proposta semantica. Gli artefatti JSON distinguono successi, errori e tentativi.

## Copertura obbligatoria

Il registro `config/source-registry.global-pilot.json` ora include 36 feed, fra cui arXiv AI/ML/economia, Wikinews inglese, Wikinotizie italiano ed EEA. `ingestion/global_coverage_contract.py` verifica esplicitamente che siano configurati e tentati i gruppi editoriale, preprint scientifici, notizie collaborative e istituzioni. **Una sorgente tentata può comunque fallire; il report non la conta come acquisita.**

**Limite reale:** il contratto evita dimenticanze dei gruppi dichiarati, ma non rende il corpus esaustivo. Per una copertura globale completa occorre continuare ad aggiungere registri geografici, linguistici e disciplinari, e monitorare feed inattivi. L'API arXiv è Atom e offre anche OAI-PMH per grandi volumi; il pilota usa feed RSS di categorie, non l'intero archivio.

## Testo integrale e licenze

`ingestion/wikinews_text_pilot.py` interroga MediaWiki API per pagine scoperte dal feed Wikinews, estrae il testo in memoria e registra **solo** conteggi, hash ed esiti. L'acquisizione effettiva va confermata dai report del workflow. **Non archivia testo integrale** in assenza di revisione puntuale dei diritti.

`ingestion/licensed_text_store.py` consente salvataggio solo con autorizzazione per documento già verificata; manca ancora la verifica documentale reale di licenze, autori, attribuzione ed eccezioni, e l'integrazione con storage dell'applicazione.

## Semantica e accorpamenti

`ingestion/dual_topic_router.py` produce proposte verso topic manuali, astensioni e termini emergenti. Non misura ancora precisione o recall. `global_event_pairs.py` e `global_cards.py` generano **candidati**, non conferme di stessa notizia. Il passo successivo richiede analisi dei testi acquisiti legalmente, entità/tempo/luogo e confronto di affermazioni, seguiti da verifica empirica di precisione.

## Cosa è implementato e cosa no

- **Implementato:** 36 feed configurati; audit obbligatorio dei canali; tentativo MediaWiki GET; ledger; rights default-deny; routing semantico; GitHub Actions.
- **Da verificare empiricamente:** quanti dei nuovi feed rispondono, quanti testi MediaWiki sono effettivamente letti, esito end-to-end del job semantico.
- **Non implementato:** archivio in produzione di testi riutilizzabili, verifica automatica affidabile della licenza del singolo articolo, estrazione integrale arXiv PDF/HTML, clustering fattuale validato, precisione misurata e pubblicazione UI.

Le nuove fonti non vanno mai date per acquisite soltanto perché sono nel registro.
