# Ubik — verifica empirica e registro degli sviluppi (13 ottobre 2026)

**Ramo:** `develop/ubik-core`. **Non equivale a rilascio su Vercel o produzione.**

## Stato verificato da artefatti reali

GitHub Actions run [38370949846](https://github.com/nathanasso-code/Ubik/actions/runs/38370949846), job `discover` **success**, artifact `global-discovery-pilot` (ID 11799460116), letto il 13 ottobre 2026:

| Metrica | Risultato empirico |
|---|---:|
| URL distinti nel registro persistente | **1.244** |
| URL con segnale di scoperta social | **330** |
| URL con almeno una misurazione GET | **73** |
| URL con evidenza di testo sostanziale nell'elemento article | **34** |
| Documenti con titolo e descrizione sufficienti secondo la soglia euristica attuale | **918** |
| Descrizioni lunghe / corte | **567 / 317** |
| Metadati insufficienti | **326** |
| Documenti con licenza di ripubblicazione verificata nel registro | **0** |

Nota: le 34 pagine con testo sostanziale **non** sono 34 testi completi verificati né 34 permessi di ripubblicazione. I 918 documenti sono **eleggibili per un test di classificazione**, non classificazioni corrette verificate.

Il job `semantic-review` dello stesso run è **fallito**: `FileNotFoundError: data/discovery/topic-evidence-quality.json`, a causa del layout annidato dell'artefatto scaricato. Commit `81ecb0a7` corregge i riferimenti a `data/discovery/discovery/...` per gli input del job. **Correzione implementata, da verificare su nuova esecuzione.**

## Implementato nel codice (non confondere con funzionalità in produzione)

- `ingestion/persistent_discovery_ledger.py`: accumula metadati RSS/social e prove GET tra run; GitHub Actions cache + artefatto JSON. Test di deduplicazione e persistenza eseguiti con successo nel job `discover`.
- `ingestion/live_get_text_probe.py`: GET HTTPS limitati, robots.txt, estrazione HTML e lunghezze/hash; **non** certifica completezza o diritti.
- `ingestion/topic_evidence_qualification.py`: seleziona input con titolo e descrizione; testato sul corpus (918 eleggibili).
- `ingestion/dual_topic_router.py`: proposta per topic manuali (`data/catalog.json`) con embedding multilingue, soglia, margine, ancoraggio lessicale, astensione; termini emergenti dai titoli non assegnati. **Non esistono ancora metriche empiriche di precisione/recall.**
- `ingestion/ephemeral_article_topic_analysis.py`: implementazione di analisi in RAM del testo HTML quando acquisibile, **non ancora verificata in esecuzione end-to-end** e non connessa al job globale.
- `ingestion/document_rights_registry.py`: default-deny; la policy di un dominio è solo un **indizio per revisione**, non una licenza automaticamente assegnata al documento. Coda di revisione generata sul corpus: 0 licenze documentali verificate.
- `ingestion/licensed_text_store.py`: salvataggio del testo condizionato a licenza/URL evidenza verificati e permessi di conservazione e visualizzazione. Test unitari con testo fittizio passati; **nessun testo reale è stato archiviato**.
- `ingestion/global_event_pairs.py`, `ingestion/global_cards.py`: proposte di relazioni e card su evidenze limitate; **non sono cluster di evento verificati**, né sintesi approvate.

## Ricognizione concreta dei diritti di riutilizzo

Il corpus 1.244 URL è dominato da editori di notizie; non è corretto inferire autorizzazioni dai loro RSS o da HTTP 200.

**Fonte promettente presente nel corpus:** un URL EEA condiviso su Bluesky:
`https://eea.europa.eu/en/newsroom/news/building-sustainable-competitiveness-in-an-uncertain-future`.
È un **link di scoperta** senza titolo/descrizione editoriali e senza GET del testo nel corpus: **non ancora acquisito né approvato**.

La [nota legale EEA](https://www.eea.europa.eu/en/legal-notice) dichiara in generale CC-BY per materiali EEA, riutilizzo commerciale e non commerciale con attribuzione e rispetto del significato, **escludendo i contenuti di terzi e le eccezioni indicate nei singoli documenti**. È quindi una **fonte prioritaria per verifica puntuale**, non un via libera automatico. Il modulo rights registry ora segnala il dominio EEA nella coda di revisione.

Altre fonti da integrare in acquisizione mirata, non presenti come documenti verificati nel corpus corrente:
- [Wikinews inglese — copyright](https://en.wikinews.org/wiki/Wikinews:Copyright): licenza del testo dipendente dalla data; verificare eccezioni, attribuzione e singola pagina.
- [Wikinotizie italiano — copyright](https://it.wikinews.org/wiki/Wikinotizie:Copyright): CC BY con condizioni e possibili eccezioni.
- [arXiv — licenze](https://info.arxiv.org/help/license/index.html): verificare **singolo paper**, la licenza predefinita di distribuzione arXiv non equivale a diritto di ripubblicazione su Ubik.

**Non archiviare o mostrare integralmente alcun documento finché non sono verificati:** identità/autore, licenza del singolo testo, eventuali materiali di terzi, attribuzione, permessi di acquisizione, limiti tecnici e modalità di visualizzazione.

## Progettato / da fare (NON completato)

1. **Verifica documentale dei diritti:** identificare documenti riutilizzabili e registrarne URL della licenza, versione, data, eccezioni e decisione con audit.
2. **Acquisizione e archivio reale:** estrarre testi autorizzati e salvarli in uno storage protetto con attribuzione, provenienza e versionamento; attualmente esiste solo il modulo di salvataggio, non il collegamento allo storage applicativo.
3. **Semantica empirica:** completare il workflow, creare un campione manualmente etichettato di pertinenza, misurare precisione/recall e falsi positivi; distinguere topic manuali ed emergenti.
4. **Card multifonte:** raggruppare per evento/questione, non per semplice tema; confrontare entità, luogo, tempo, affermazioni e indipendenza delle fonti prima di presentare accorpamenti come verificati.
5. **UI e deploy:** integrare stato dei diritti, testo autorizzato, filtri di classificazione e card nella UI esistente senza alterare architettura o produzione.
6. **Robustezza:** il ledger su GitHub cache non è ancora un database duraturo; valutare Supabase e gestione delle versioni dei testi e revoche.
7. **Privacy e licenze:** analisi legale del trattamento automatizzato, TDM e condizioni per ogni editore; non interpretare robots.txt come concessione di copyright.

## Prossima sequenza operativa

Prima verificare l'esecuzione corretta del job `semantic-review`; in parallelo estendere la scoperta verso fonti con policy di riutilizzo promettenti e verificare il primo documento EEA. Solo dopo una licenza **specifica** validata, acquisire testo, categorizzare, confrontare candidati di evento e proporre card multifonte, mantenendo evidenza e astensioni.

**Regola di documentazione:** `implementato` significa codice committato; `testato` richiede un test o run riuscito; `empiricamente verificato` richiede dati reali e numeri; `in produzione` richiede deploy confermato. Questi stati non sono intercambiabili.
