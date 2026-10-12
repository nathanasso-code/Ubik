# UBIK — CONTINUITÀ OPERATIVA (aggiornato 2026-10-12)

> **Leggere questo documento per primo in una nuova chat.** Repository: `nathanasso-code/Ubik`. Branch di lavoro: `develop/ubik-core`. `main` può alimentare la produzione: non modificarlo né distribuire migrazioni senza verifiche. Questa nota distingue intenzioni, codice committato e funzionalità realmente operative.

## Obiettivo e prodotto

Ubik è una piattaforma di informazione per topic, selezione delle fonti, evidenze tracciabili, confronto documentato e discernimento assistito. I topic sono il centro del prodotto: matrice tematica, tag cloud, fonti, card e nuclei epistemici opzionali. Il precedente lessico Pulse/Press/Insights descrive alcune funzioni storiche, **ma non va reintrodotto come navigazione obbligatoria**: il vincolo più recente in `docs/START_HERE_UBIK.md` è topic-first. Non trasformare ogni articolo in un nucleo epistemico, né ogni discussione in una notizia.

## Principio acquisizione — scoperta — autonomia

Mastodon è prioritario come **segnale di scoperta**, non come archivio proprietario né come unico ingresso. RSS diretti, GDELT, Hacker News, Bluesky, Crossref/OpenAlex e altre fonti già integrate restano complementari. Da ogni post sociale individuare gli **URL esterni**, ricondurli per quanto verificabile al documento originale e al sito editore, mantenere tutte le osservazioni e registrare eventuali feed ufficiali per acquisizione diretta futura. La stessa pubblicazione scoperta via RSS e Mastodon resta un unico documento con più segnalazioni, **solo quando l'identità documentale è confermata**. La somiglianza tra titoli non prova identità o indipendenza delle fonti.

L'archivio permanente deve essere indipendente da Mastodon: editori/domini e feed, documenti/DOI/URL canonici, segnalazioni con provenienza, associazioni ai topic, cronologia delle revisioni. Conservare metadati e collegamenti rispettando termini e diritti; non assumere autorizzazione a copiare full text. Scoprire un sito tramite Mastodon non autorizza crawling illimitato. SSRF, redirect, rate limit e 403/429 vanno trattati esplicitamente.

## Quattro segnali cardine di attenzione

1. Condivisioni da più account **indipendenti**.
2. Condivisione anche singola da account molto seguito (follower normalizzati, non dominanti).
3. Condivisione da account con identità/competenza **verificabili**; il linked-domain verification di Mastodon NON certifica automaticamente competenza.
4. Discussione sostanziale e documentata, non semplice numero di risposte.

I segnali determinano **priorità di revisione**, non verità o credibilità. Penalizzare bot, sindacazione e copie coordinate; valori non disponibili restano *unknown*, non zero. Consentire accesso a revisione anche a contributi specialistici poco popolari. Validazione distinta: origine, evidenze, corroborazione indipendente, contraddizioni e stabilità.

## Tre viste progressive per ogni topic

- **Esplora**: selezione blanda, ampia, scoperte pertinenti non necessariamente validate.
- **Rilevanti**: selezione intermedia, attenzione documentata, interesse editoriale o segnalazioni qualificate.
- **Essenziali**: poche fonti di valore documentale approvate dopo revisione, persistenti nel tempo, non semplicemente le più recenti o popolari.

Sono viste dello **stesso catalogo**, non tre copie dei dati. Essenziali è sottoinsieme logico di Rilevanti, che è sottoinsieme di Esplora; i limiti di pagina devono rispettare la progressione. La promozione/declassamento richiede ragione tracciabile. Nessuna soglia numerica sperimentale va presentata come validata.

## Stato tecnico verificato nel repository

- `ingestion/contracts.py`: contratto osservazioni, `canonical_url_hint` elimina alcuni tracker ma **non certifica** identità canonica.
- `ingestion/broad_source_catalog.py`: catalogo ampio con provenienza, nessuna esclusione editoriale automatica.
- `ingestion/public_adapters.py`: adattatori pubblici metadata-only per Bluesky, Mastodon, OpenAlex, Crossref.
- `ingestion/mastodon_discovery.py`, `ingestion/mastodon_merge.py`: discovery e dedup ActivityPub URI del pilot, con test dedicati.
- `ingestion/social_source_catalog.py`: **nuovo prototipo offline** di estrazione URL esterni da post Mastodon e fusione preliminare con catalogo esistente; test `tests/test_social_source_catalog.py`. Limiti: non risolve redirect/canonical reali, non fa crawling né persistenza.
- `ingestion/topic_quality_views.py`: **nuovo prototipo offline** delle tre viste con promozione Essenziali subordinata a revisione esplicita; test `tests/test_topic_quality_views.py`. Non è ranking calibrato né UI di produzione.
- `supabase/migrations/002_source_topic_catalog.sql`: **nuovo schema SQL PROPOSTO, NON APPLICATO**, tabelle `ubik_publishers`, `ubik_documents`, `ubik_document_discoveries`, `ubik_topics`, `ubik_topic_documents`, `ubik_topic_review_history`, RLS abilitato senza policy pubbliche. Controllare conflitti, permessi, migrazione e tracciamento storico prima di applicarlo.
- `docs/TOPIC_QUALITY_AND_SOURCE_REGISTRY.md`: contratto sintetico delle viste e del registro.
- `api/feed.js`: feed esistente basato su Vercel Blob (`questions/*/latest.json`), **non** usa il nuovo schema SQL.
- `supabase/migrations/001_event_corpus.sql`: schema eventi precedente, non alterato.
- `.github/workflows/core-checks.yml`: esegue unit test JS/Python su push nel branch di sviluppo; esito dei commit più recenti **non verificato in questa chat**.

## Risultati live da non confondere con produzione

- Pilot RSS 2026-10-11: 2.797 osservazioni in un run, 23/28 feed riusciti, 21 con materiale; vedere `docs/START_HERE_UBIK.md` per evoluzione e run successivi. I numeri descrivono campioni, non copertura universale.
- Pilot Mastodon IA: workflow su `main` `.github/workflows/ubik-mastodon-ai-research.yml`, run https://github.com/nathanasso-code/Ubik/actions/runs/38216136515 completato con successo. 640 post raccolti da hashtag, 602 URI unici, 38 duplicati per URI; artifact `mastodon-ai-research` (ZIP, scadenza GitHub Actions). **Non sono 602 articoli esterni né 602 notizie valide**. Necessari estrazione URL, verifica pertinenza, dedup documentale e review.
- Mastodon `@ubik_platform@mastodon.social` e Bluesky `@ubik-platform.bsky.social` sono account del progetto; token Mastodon in GitHub Actions secret `UBIK_MASTODON_TOKEN`. Non chiedere o esporre il token.
- `main` contiene workflow di ricerca Mastodon isolati; `develop/ubik-core` contiene prototipi di integrazione. Non confondere la presenza di workflow con ingestion ricorrente o distribuita.

## Azioni successive — ordine raccomandato

1. **Verificare CI** degli ultimi commit e correggere test, import, normalizzazione URL, casi limite; evitare di affermare che passano senza un run verificato.
2. Confrontare il nuovo catalogo con i contratti di ingestion, le strutture topic già esistenti e il feed Vercel Blob. Evitare duplicazioni di concetti o migrazioni invasive.
3. Costruire pipeline *offline* di estrazione URL dai 602 post (artifact se disponibile), risoluzione controllata dei siti originari, mappatura dominio/feed e import di osservazioni da RSS/GDELT/Bluesky; misurare duplicati e falsi positivi.
4. Implementare un archivio persistente **solo dopo** review dello schema, delle policy RLS, della strategia di upsert e dello storico revisioni.
5. Creare endpoint read-only per topic e UI a tre viste, con dati reali, provenienza e spiegazione delle promozioni; testare su topic IA e un secondo topic non-IA.
6. Calibrare attenzione e validazione su campioni annotati, con fallback per fonti di nicchia e tutela contro bot e segnali mancanti.
7. Eseguire regression test e controlli di sicurezza prima di qualunque merge su `main` o deploy.

## Ipotesi sperimentale successiva — NON approvata come sviluppo

È emersa la possibilità che ricerche web iterative guidate da LLM recuperino controversie, prospettive e fonti primarie meglio della sola raccolta RSS/API, a costi sostenibili con budget e caching. **Non è un risultato dimostrato né una decisione di roadmap.** È stata formalizzata un'ipotesi A/B e ibrida, con criteri di valutazione e vincoli economici in [RESEARCH_HYPOTHESIS_AI_WEB_INVESTIGATION_2026-10-12.md](RESEARCH_HYPOTHESIS_AI_WEB_INVESTIGATION_2026-10-12.md). Una nuova chat deve leggerla come ricerca esplorativa, non attivare automaticamente servizi a pagamento o modificare la produzione.

## Regole per una nuova chat autonoma

- Leggere questo file, `docs/START_HERE_UBIK.md`, `docs/CORE_ARCHITECTURE.md`, `docs/TOPIC_QUALITY_AND_SOURCE_REGISTRY.md`, `ingestion/README.md`, quindi il codice effettivo e le ultime Actions.
- Non dedurre che una funzionalità sia attiva perché è documentata o committata.
- Non alterare il corpus eventi, la navigazione topic-first o il feed di produzione per introdurre i tre livelli.
- Operare su `develop/ubik-core`, preferire incrementi compatibili e verificabili; l'utente desidera autonomia, senza approvazione per ogni passo non distruttivo.
- Documentare a ogni milestone commit, test, dati verificati, limitazioni e prossima azione, distinguendo sempre **fatto / proposto / non verificato**.
