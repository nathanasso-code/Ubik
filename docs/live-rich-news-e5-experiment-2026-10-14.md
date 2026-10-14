# Ubik — confronto empirico tra metadati e testi sostanziali (14 ottobre 2026)

## Stato verificato
Ramo: `develop/ubik-core`. La CI «Ubik Core checks» relativa al commit `17ac66a5` è **verde**. Il workflow «Global topic-agnostic discovery pilot» run **38632610923** è **in esecuzione** al momento di questo aggiornamento: non attribuire al nuovo esperimento risultati non ancora pubblicati.

## Motivazione
Negli esperimenti iniziali il sistema E5/NLI analizzava titoli e descrizioni anche quando erano stati estratti testi molto più lunghi. Era dunque scorretto attribuire la debolezza delle relazioni al solo classificatore.

## Corpus verificato prima della nuova esecuzione
- Archivio precedente: 4.286 documenti, 181 con almeno un segnale di accesso a testo sostanziale o abstract esteso.
- Esperimento giornalistico precedente: 24 coppie candidate, 16 articoli con corpo sostanziale, 6 coppie con due corpi sostanziali.
- Sono **esiti osservati nel workflow precedente**, non garanzia che lo stesso numero venga recuperato nella nuova esecuzione live.

## Esperimento implementato
`ingestion/live_rich_pair_experiment.py` recupera temporaneamente articoli pubblici nel rispetto dei controlli robots, seleziona corpi di almeno 2.000 caratteri e confronta le **stesse coppie**:
1. coseno lessicale dei titoli;
2. coseno lessicale di titoli e descrizioni;
3. massimo e media top-3 delle similarità lessicali tra segmenti del corpo;
4. con `--semantic-e5`, similarità E5 dei metadati, massimo e media top-3 dei segmenti testuali.

`ingestion/rich_pair_semantic.py::semantic_scores` calcola embeddings normalizzati dei segmenti con il modello E5 multilingue già usato da Ubik. Non persiste il corpo giornalistico e produce esclusivamente metriche, URL e lunghezze.

Il workflow esegue il comando:
```bash
python -m ingestion.live_rich_pair_experiment \
  --snapshot data/discovery/global-rss-pilot.json \
  --hybrid data/discovery/hybrid-event-review.json \
  --output data/discovery/live-rich-pair-experiment.json \
  --limit 24 --semantic-e5
```

## Criteri di interpretazione
- Un aumento della similarità non è automaticamente un miglioramento: segmenti generici e boilerplate possono gonfiare i valori.
- Le coppie sono selezionate a partire da metadati; il campione non è casuale.
- Non esistono ancora etichette indipendenti sufficienti per misurare precisione/recall o qualità delle contraddizioni.
- Il confronto non esegue ancora NLI su frasi candidate tratte dal corpo.
- Un esito verde della CI non dimostra che siano state acquisite due fonti sostanziali per ciascuna coppia.

## Decisione operativa successiva
Dopo il completamento del run, esaminare `data/discovery/live-rich-pair-experiment.json`: contare coppie con due corpi, confrontare per coppia `semantic.metadata_e5` e `semantic.mean_top_3_chunk_e5`, e ispezionare i casi divergenti. Solo dopo costruire una revisione manuale indipendente delle relazioni e l'NLI su passaggi selezionati, senza dichiarare verificati eventi o affermazioni non controllati.

Workflow: https://github.com/nathanasso-code/Ubik/actions/runs/38632610923
