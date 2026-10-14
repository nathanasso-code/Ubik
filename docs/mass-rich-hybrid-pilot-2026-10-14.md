# Esperimento massivo Ubik: corpus sostanziale e pipeline ibrida

## Stato
Implementato nel ramo `develop/ubik-core` il workflow `rich-hybrid-experiment.yml`. Run iniziale: https://github.com/nathanasso-code/Ubik/actions/runs/38637366519 . I numeri finali vanno letti nell'artefatto `rich-hybrid-corpus-results`, non stimati dai parametri.

## Ingressi obbligatori
- Ricerca su Europe PMC di tre domini (ambiente, AI, salute pubblica), fino a 65 risultati per dominio.
- Fino a 100 tentativi di download di XML Open Access.
- Il corpo è conservato solo se la licenza esplicita supera la whitelist conservativa (CC BY 4.0, CC BY-SA 4.0, CC0), poi il corpus finale richiede **almeno 2.000 caratteri effettivi** e provenienza/diritti tracciati.
- Non vengono inseriti nella valutazione titoli isolati, descrizioni brevi o meri segnali di accessibilità.

## Pipeline
1. Discovery e deduplicazione PMCID.
2. Recupero XML, controllo licenza, estrazione testo e registrazione dei fallimenti.
3. Filtro rigoroso di qualità testuale e limiti di troncamento espliciti.
4. Recupero TF-IDF su titolo + corpo sostanziale (fino a 16.000 caratteri), selezione di 40 coppie; massimo quattro coppie per documento.
5. Passaggio di 20 coppie all'adapter LLM esistente; modalità predefinita **dry-run**, con stato `ready_for_llm`. Non equivale a esecuzione di un LLM.
6. Artefatto JSON con conteggi reali, URL, coppie candidate e stati LLM.

## Condizione per una prova LLM reale
Per attivare l'inferenza serve un endpoint HTTPS compatibile OpenAI, un modello e una chiave, passati come `UBIK_LLM_ENDPOINT`, `UBIK_LLM_MODEL`, `UBIK_LLM_API_KEY` e l'opzione `--execute`. Non è configurata nel workflow pubblico, così da non esporre credenziali o avviare costi non autorizzati.

## Limiti
Il corpus scientifico open access non è rappresentativo delle notizie generaliste. TF-IDF propone somiglianze, non stabilisce identità evento né verifica affermazioni. Le risposte LLM devono passare validazione di citazioni e revisione prima di ogni pubblicazione. Il run iniziale non deve essere presentato come validazione semantica finché l'inferenza non sia stata effettivamente eseguita.

## File
- `ingestion/mass_rich_hybrid_pilot.py`
- `ingestion/europe_pmc_licensed_texts.py`
- `ingestion/rich_text_corpus.py`
- `ingestion/llm_semantic_adapter.py`
- `.github/workflows/rich-hybrid-experiment.yml`
